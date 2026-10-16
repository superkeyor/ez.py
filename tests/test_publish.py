import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ez_publish", ROOT / "scripts/publish.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="ez-auth-")
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        self.addCleanup(patch.stopall)
        patch.dict(os.environ, {}, clear=True).start()
        patch.object(Path, "home", return_value=self.home).start()
        self.config = self.home / ".pypirc"

    def test_environment_precedes_file(self):
        os.environ["UV_PUBLISH_TOKEN"] = "environment-token"
        self.config.write_text("[broken\npassword = do-not-print")
        self.assertEqual(publisher.publish_token(), "environment-token")

    def test_token_config_without_interpolation(self):
        self.config.write_text("[pypi]\nusername = __token__\npassword = secret%value\n")
        self.assertEqual(publisher.publish_token(), "secret%value")

    def test_invalid_credentials_have_no_secret_output(self):
        configurations = [
            None,
            "[testpypi]\npassword = do-not-print",
            "[pypi]\nusername = user\npassword = do-not-print",
            "[pypi]\nusername = __token__\n",
            "[pypi]\nusername = __token__\npassword = do-not-print\n"
            "repository = https://other.example/legacy/",
            "[pypi]\npassword = do-not-print\nmalformed do-not-print\n",
        ]
        for config in configurations:
            with self.subTest(config=config):
                if config is not None:
                    self.config.write_text(config)
                with self.assertRaises(ValueError) as result:
                    publisher.publish_token()
                self.assertNotIn("do-not-print", str(result.exception))


class VersionTests(unittest.TestCase):
    def test_rollover_component_selection(self):
        for version, component in (
            ("11.8.8", "patch"), ("11.8.9", "minor"), ("11.9.9", "major"),
            ("0.0.0", "patch"),
        ):
            with self.subTest(version=version):
                self.assertEqual(publisher.bump_component(version), component)

    def test_invalid_versions_fail_explicitly(self):
        for version in ("broken", "11.8.10", "11.10.0", "11.8.2.dev1", None):
            with self.subTest(version=version), self.assertRaises(ValueError):
                publisher.bump_component(version)


FAKE_COMMAND = '''#!{python}
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

args = sys.argv[1:]
name = Path(sys.argv[0]).name
stage = args[0] if name == "uv" else name
if name == "git":
    stage = "git-" + args[0]
if name == "uv" and args == ["version", "--short"]:
    stage = "version-report"
if name == "uv" and args[:2] == ["pip", "show"]:
    stage = "pip-show"
with open(os.environ["EZ_COMMAND_LOG"], "a") as stream:
    stream.write(json.dumps({{"stage": stage, "args": args,
                             "has_token": bool(os.environ.get("UV_PUBLISH_TOKEN"))}}) + "\\n")
if stage == os.environ.get("EZ_FAIL_STAGE"):
    sys.exit(7)
if stage == "version-report":
    print(tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"])
if stage == "pip-show":
    print("Name: ez\\nVersion: 0.0.7\\nLocation: /test/local/site-packages")
if stage == "run":
    sys.exit(subprocess.call([sys.executable, args[-1]]))
if stage == "version":
    path = Path("pyproject.toml")
    text = path.read_text()
    version = tomllib.loads(text)["project"]["version"]
    parts = list(map(int, version.split(".")))
    index = {{"major": 0, "minor": 1, "patch": 2}}[args[args.index("--bump") + 1]]
    parts[index] += 1
    for position in range(index + 1, 3):
        parts[position] = 0
    text = text.replace('version = "' + version + '"',
                        'version = "' + ".".join(map(str, parts)) + '"')
    path.write_text(text)
if stage == "build":
    version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    output = Path(args[args.index("--out-dir") + 1])
    for suffix in (".tar.gz", "-py3-none-any.whl"):
        (output / ("ez-" + version + suffix)).write_bytes(b"fresh artifact")
'''


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="ez publisher tests ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve() / "renamed checkout"
        self.root.mkdir()
        for relative in (
            "publish.sh", "scripts/publish.py", "pyproject.toml", "README.md",
            "ez/ez.py", "ez/prepublish.py", "Publish.app/Contents/Resources/script",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.home = self.root.parent / "home"
        self.home.mkdir()
        (self.home / ".pypirc").write_text(
            "[pypi]\nusername = __token__\npassword = do-not-print\n"
        )
        self.bin = self.root.parent / "bin"
        self.bin.mkdir()
        for name in ("uv", "git", "upgrade"):
            command = self.bin / name
            command.write_text(FAKE_COMMAND.format(python=sys.executable))
            command.chmod(0o755)
        (self.home / ".bash_profile").write_text(
            'ezupdate() { "$EZ_FAKE_BIN/upgrade"; }\n'
        )
        self.log = self.root.parent / "commands.jsonl"
        self.environment = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "EZ_FAKE_BIN": str(self.bin),
            "EZ_COMMAND_LOG": str(self.log),
        }
        for variable in ("UV_PUBLISH_TOKEN", "EZ_FAIL_STAGE"):
            self.environment.pop(variable, None)
        self.original_version = self.project_version()

    def project_version(self):
        return tomllib.loads((self.root / "pyproject.toml").read_text())["project"]["version"]

    def invoke(self, entry="publish.sh", args=()):
        result = subprocess.run(
            ["/bin/bash", str(self.root / entry), *args],
            cwd=self.home, env=self.environment, capture_output=True, text=True,
        )
        self.assertNotIn("do-not-print", result.stdout + result.stderr)
        self.assertNotIn("SyntaxWarning", result.stderr)
        return result

    def commands(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_complete_release_keeps_only_current_release_artifacts(self):
        dist = self.root / "dist"
        dist.mkdir()
        stale = dist / "ez-0.0.1.tar.gz"
        stale.write_bytes(b"historical")
        old_wheel = dist / "ez-0.0.1-py3-none-any.whl"
        old_wheel.write_bytes(b"historical wheel")
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.commands()
        self.assertEqual(
            [item["stage"] for item in commands],
            ["run", "version", "build", "publish", "git-add", "git-commit",
             "git-push", "upgrade", "upgrade", "upgrade", "version-report", "pip-show"],
        )
        upload = next(item for item in commands if item["stage"] == "publish")
        self.assertTrue(upload["has_token"])
        self.assertEqual(upload["args"][-2:], [
            str(dist / f"ez-{self.project_version()}.tar.gz"),
            str(dist / f"ez-{self.project_version()}-py3-none-any.whl"),
        ])
        self.assertFalse(stale.exists())
        self.assertFalse(old_wheel.exists())
        self.assertEqual(
            {path.name for path in dist.iterdir()},
            {f"ez-{self.project_version()}.tar.gz", f"ez-{self.project_version()}-py3-none-any.whl"},
        )
        self.assertNotEqual(self.original_version, self.project_version())
        self.assertNotIn("do-not-print", self.log.read_text())
        self.assertIn("--frozen", commands[1]["args"])
        self.assertIn(f"Distribution version: {self.project_version()}", result.stdout)
        self.assertIn("Distribution files:", result.stdout)
        self.assertIn(f"ez-{self.project_version()}-py3-none-any.whl", result.stdout)
        self.assertIn("Locally installed package", result.stdout)
        self.assertIn("Version: 0.0.7", result.stdout)
        self.assertIn("Location: /test/local/site-packages", result.stdout)

    def test_app_runs_without_external_shell_script_from_an_unrelated_directory(self):
        (self.root / "publish.sh").unlink()
        result = self.invoke("Publish.app/Contents/Resources/script")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commands()[-1]["stage"], "pip-show")
        self.assertIn("Version: 0.0.7", result.stdout)

    def test_failed_build_preserves_previous_release_artifacts(self):
        dist = self.root / "dist"
        dist.mkdir()
        previous = dist / "ez-0.0.1.tar.gz"
        previous.write_bytes(b"preserve on build failure")
        self.environment["EZ_FAIL_STAGE"] = "build"
        result = self.invoke()
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(previous.read_bytes(), b"preserve on build failure")

    def test_cleanup_does_not_remove_unrelated_files_or_directories(self):
        dist = self.root / "dist"
        dist.mkdir()
        unrelated = dist / "notes.txt"
        unrelated.write_text("preserve")
        other_package = dist / "other-1.0.0.tar.gz"
        other_package.write_bytes(b"other package")
        directory = dist / "ez-0.0.1.tar.gz"
        directory.mkdir()
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(unrelated.read_text(), "preserve")
        self.assertEqual(other_package.read_bytes(), b"other package")
        self.assertTrue(directory.is_dir())

    def test_bundled_shell_script_matches_current_external_script(self):
        self.assertEqual(
            (ROOT / "publish.sh").read_bytes(),
            (ROOT / "Publish.app/Contents/Resources/script").read_bytes(),
        )

    def test_help_has_no_profile_or_release_side_effects(self):
        (self.home / ".bash_profile").write_text("exit 99\n")
        for entry in ("publish.sh", "Publish.app/Contents/Resources/script"):
            with self.subTest(entry=entry):
                result = self.invoke(entry, ["--help"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Usage:", result.stdout)
        self.assertEqual(self.commands(), [])
        self.assertEqual(self.project_version(), self.original_version)

    def test_unknown_arguments_fail_before_release(self):
        self.assertEqual(self.invoke(args=["--oops"]).returncode, 2)
        self.assertEqual(self.commands(), [])

    def test_auth_failure_precedes_version_and_preparation(self):
        (self.home / ".pypirc").unlink()
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([item["stage"] for item in self.commands()], ["run"])
        self.assertEqual(self.project_version(), self.original_version)

    def test_invalid_catalog_stops_before_bump(self):
        (self.root / "README.md").write_text("No markers")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([item["stage"] for item in self.commands()], ["run"])
        self.assertEqual(self.project_version(), self.original_version)

    def test_each_command_failure_stops_later_stages(self):
        stages = [
            "version", "build", "publish", "git-add", "git-commit", "git-push",
            "upgrade", "version-report", "pip-show",
        ]
        for stage in stages:
            with self.subTest(stage=stage):
                self.environment["EZ_FAIL_STAGE"] = stage
                if self.log.exists():
                    self.log.unlink()
                result = self.invoke()
                self.assertEqual(result.returncode, 7, result.stderr)
                self.assertEqual(self.commands()[-1]["stage"], stage)
                self.assertNotIn("local upgrades completed.", result.stdout)

    def test_missing_upgrade_helper_fails_before_upload(self):
        (self.home / ".bash_profile").write_text("")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ezupdate", result.stderr)
        self.assertEqual(self.commands(), [])

    def test_existing_release_artifacts_are_not_overwritten_or_uploaded(self):
        dist = self.root / "dist"
        dist.mkdir()
        project = self.root / "pyproject.toml"
        project.write_text(project.read_text().replace(
            f'version = "{self.original_version}"', 'version = "11.8.8"',
        ))
        existing = dist / "ez-11.8.9-py3-none-any.whl"
        existing.write_bytes(b"preserve")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(existing.read_bytes(), b"preserve")
        self.assertFalse((dist / "ez-11.8.9.tar.gz").exists())
        self.assertEqual(self.commands()[-1]["stage"], "build")

    def test_invalid_version_precedes_preparation(self):
        project = self.root / "pyproject.toml"
        project.write_text(project.read_text().replace(
            f'version = "{self.original_version}"', 'version = "11.8.10"',
        ))
        readme = (self.root / "README.md").read_bytes()
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / "README.md").read_bytes(), readme)
        self.assertEqual([item["stage"] for item in self.commands()], ["run"])


if __name__ == "__main__":
    unittest.main()
