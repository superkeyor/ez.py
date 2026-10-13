import ast
from contextlib import ExitStack, redirect_stdout
import importlib.metadata as md
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch
import warnings


ROOT = Path(__file__).resolve().parents[1]


class RequireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse((ROOT / "ez/ez.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == "require")
        namespace = {"re": re, "subprocess": subprocess, "sys": sys}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "ez/ez.py", "exec"), namespace)
        cls.require = staticmethod(namespace["require"])

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.output = io.StringIO()
        self.stack.enter_context(redirect_stdout(self.output))
        self.metadata = self.stack.enter_context(patch("importlib.metadata.version"))
        self.metadata.side_effect = [md.PackageNotFoundError(), "2.0"]
        self.network = self.stack.enter_context(patch("urllib.request.urlopen"))
        self.pip = self.stack.enter_context(patch("subprocess.call", return_value=0))
        self.prompt = self.stack.enter_context(patch("builtins.input", return_value=""))
        self.invalidate = self.stack.enter_context(patch("importlib.invalidate_caches"))
        self.stack.enter_context(patch.dict("os.environ", {"CONDA_EXE": "/mock/conda"}))
        self.conda_environment = self.stack.enter_context(patch("os.path.isdir", return_value=True))
        self.conda_path = self.stack.enter_context(patch("shutil.which", return_value="/path/conda"))
        self.conda_list = self.stack.enter_context(patch("subprocess.run"))
        self.conda_list.side_effect = [
            subprocess.CompletedProcess([], 0, stdout="[]"),
            subprocess.CompletedProcess([], 0, stdout='[{"name": "ffmpeg", "version": "2.0"}]'),
        ]

    def conda_record(self, version):
        return subprocess.CompletedProcess(
            [], 0, stdout=json.dumps([{"name": "ffmpeg", "version": version}])
        )

    def test_missing_latest_installs_and_verifies(self):
        self.assertTrue(self.require("demo"))
        self.pip.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "demo"]
        )
        self.assertEqual(self.metadata.call_count, 2)
        self.invalidate.assert_called_once()
        self.network.assert_not_called()

    def test_latest_already_current_lets_pip_resolve(self):
        self.metadata.side_effect = None
        self.metadata.return_value = "2.0"
        self.assertTrue(self.require("demo"))
        self.pip.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "demo"]
        )
        self.prompt.assert_called_once()

    def test_pinned_version_changes_without_network(self):
        self.metadata.side_effect = ["3.0", "1.0"]
        self.assertTrue(self.require("demo", "1.0", confirm=False))
        self.network.assert_not_called()
        self.prompt.assert_not_called()
        self.assertEqual(self.pip.call_args.args[0][-1], "demo==1.0")

    def test_already_pinned_skips_pip(self):
        self.metadata.side_effect = None
        self.metadata.return_value = "1.0"
        self.assertTrue(self.require("demo", "1.0"))
        self.network.assert_not_called()
        self.pip.assert_not_called()

    def test_extras_are_resolved_even_when_version_matches(self):
        self.metadata.side_effect = ["2.0", "2.0"]
        self.assertTrue(self.require("demo[extra, other]", "2.0"))
        self.assertEqual(self.pip.call_args.args[0][-1], "demo[extra, other]==2.0")

    def test_decline_missing_returns_false(self):
        self.prompt.return_value = "n"
        self.assertFalse(self.require("demo", "2.0"))
        self.pip.assert_not_called()
        self.assertIn("declined", self.output.getvalue())

    def test_decline_installed_returns_true(self):
        self.metadata.side_effect = ["1.0"]
        self.prompt.return_value = "no"
        self.assertTrue(self.require("demo", "2.0"))
        self.pip.assert_not_called()

    def test_eof_declines(self):
        self.prompt.side_effect = EOFError
        self.assertFalse(self.require("demo", "2.0"))
        self.pip.assert_not_called()

    def test_latest_python_311_keeps_compatible_pysubs2_without_pin(self):
        self.metadata.side_effect = ["1.8.1", "1.8.1"]
        with patch.object(sys, "version_info", (3, 11, 0)):
            self.assertTrue(self.require("pysubs2", confirm=False))
        self.pip.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pysubs2"]
        )
        self.network.assert_not_called()
        self.assertNotIn("1.9.0", self.output.getvalue())

    def test_latest_accepts_new_compatible_resolved_version(self):
        self.metadata.side_effect = ["1.8.1", "1.9.0"]
        self.assertTrue(self.require("pysubs2", confirm=False))
        self.assertEqual(self.pip.call_args.args[0][-1], "pysubs2")

    def test_incompatible_explicit_pin_fails_without_fallback(self):
        self.metadata.side_effect = ["1.8.1"]
        self.pip.return_value = 1
        self.assertFalse(self.require("pysubs2", "1.9.0", confirm=False))
        self.pip.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pysubs2==1.9.0"]
        )

    def test_pip_failure_returns_false(self):
        self.pip.return_value = 1
        self.assertFalse(self.require("demo", "2.0", confirm=False))
        self.assertIn("pip failed", self.output.getvalue())
        self.invalidate.assert_not_called()

    def test_pip_launch_failure_returns_false(self):
        self.pip.side_effect = OSError("cannot launch")
        self.assertFalse(self.require("demo", "2.0", confirm=False))
        self.assertIn("couldn't run pip", self.output.getvalue())

    def test_pip_success_without_package_returns_false(self):
        self.metadata.side_effect = [md.PackageNotFoundError(), md.PackageNotFoundError()]
        self.assertFalse(self.require("demo", "2.0", confirm=False))
        self.assertIn("still not installed", self.output.getvalue())

    def test_pip_success_with_wrong_version_returns_false(self):
        self.metadata.side_effect = ["1.0", "1.0"]
        self.assertFalse(self.require("demo", "2.0", confirm=False))
        self.assertIn("expected demo==2.0", self.output.getvalue())

    def test_invalid_arguments_raise_before_side_effects(self):
        for pkg, version in (
            ("", "latest"), ("demo==2.0", "latest"), ("-r file", "latest"),
            ("https://example.com/demo.whl", "latest"), (None, "latest"),
            ("demo", 2), ("demo", ">=2.0"), ("demo", "2.0 --other"),
        ):
            with self.subTest(pkg=pkg, version=version), self.assertRaises(ValueError):
                self.require(pkg, version)
        self.metadata.assert_not_called()
        self.network.assert_not_called()
        self.pip.assert_not_called()

    def test_none_and_empty_version_use_latest(self):
        for version in (None, ""):
            with self.subTest(version=version):
                self.metadata.side_effect = [md.PackageNotFoundError(), "2.0"]
                self.assertTrue(self.require("demo", version, confirm=False))
                self.assertEqual(self.pip.call_args.args[0][-1], "demo")

    def test_pypi_alias_preserves_pip_behavior(self):
        self.assertTrue(self.require("demo", "2.0", confirm=False, channel="pypi"))
        self.assertEqual(self.pip.call_args.args[0][0:3], [sys.executable, "-m", "pip"])
        self.conda_list.assert_not_called()

    def test_invalid_channel_and_conda_extras_fail_before_side_effects(self):
        for channel, pkg in (("apt", "demo"), (None, "demo"), ("conda", "demo[extra]")):
            with self.subTest(channel=channel, pkg=pkg), self.assertRaises(ValueError):
                self.require(pkg, channel=channel)
        self.metadata.assert_not_called()
        self.network.assert_not_called()
        self.conda_list.assert_not_called()
        self.pip.assert_not_called()

    def test_conda_missing_latest_installs_in_current_prefix(self):
        self.assertTrue(self.require("ffmpeg", confirm=False, channel="conda"))
        self.pip.assert_called_once_with(
            ["/mock/conda", "install", "--yes", "--prefix", sys.prefix, "ffmpeg"]
        )
        self.conda_list.assert_called_with(
            ["/mock/conda", "list", "--prefix", sys.prefix, "--json", "--no-pip"],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(self.conda_list.call_count, 2)
        self.metadata.assert_not_called()
        self.network.assert_not_called()
        self.prompt.assert_not_called()

    def test_conda_existing_latest_uses_update(self):
        self.conda_list.side_effect = [self.conda_record("1.0"), self.conda_record("2.0")]
        self.assertTrue(self.require("ffmpeg", channel="conda"))
        self.pip.assert_called_once_with(
            ["/mock/conda", "update", "--yes", "--prefix", sys.prefix, "ffmpeg"]
        )
        self.prompt.assert_called_once()

    def test_conda_pin_uses_install_with_exact_version(self):
        self.conda_list.side_effect = [self.conda_record("3.0"), self.conda_record("2.0")]
        self.assertTrue(self.require("ffmpeg", "2.0", confirm=False, channel="conda"))
        self.pip.assert_called_once_with(
            ["/mock/conda", "install", "--yes", "--prefix", sys.prefix, "ffmpeg==2.0"]
        )

    def test_conda_current_pin_skips_install_and_prompt(self):
        self.conda_list.side_effect = [self.conda_record("2.0")]
        self.assertTrue(self.require("ffmpeg", "2.0", channel="conda"))
        self.assertEqual(self.conda_list.call_count, 1)
        self.pip.assert_not_called()
        self.prompt.assert_not_called()

    def test_conda_decline_missing_does_not_install(self):
        self.prompt.return_value = "n"
        self.assertFalse(self.require("ffmpeg", channel="conda"))
        self.assertEqual(self.conda_list.call_count, 1)
        self.pip.assert_not_called()

    def test_conda_decline_installed_returns_true(self):
        self.conda_list.side_effect = [self.conda_record("1.0")]
        self.prompt.return_value = "no"
        self.assertTrue(self.require("ffmpeg", channel="conda"))
        self.pip.assert_not_called()

    def test_conda_requires_current_interpreter_to_be_conda(self):
        self.conda_environment.return_value = False
        self.assertFalse(self.require("ffmpeg", confirm=False, channel="conda"))
        self.assertIn("not in a Conda environment", self.output.getvalue())
        self.conda_list.assert_not_called()
        self.pip.assert_not_called()

    def test_conda_path_fallback_ignores_other_active_environment(self):
        with patch.dict("os.environ", {"CONDA_EXE": "", "CONDA_PREFIX": "/other/environment"}):
            self.assertTrue(self.require("ffmpeg", confirm=False, channel="CONDA"))
        self.pip.assert_called_once_with(
            ["/path/conda", "install", "--yes", "--prefix", sys.prefix, "ffmpeg"]
        )
        self.conda_path.assert_called_once_with("conda")

    def test_conda_missing_executable_is_reported(self):
        self.conda_path.return_value = None
        with patch.dict("os.environ", {"CONDA_EXE": ""}):
            self.assertFalse(self.require("ffmpeg", confirm=False, channel="conda"))
        self.assertIn("executable not found", self.output.getvalue())
        self.conda_list.assert_not_called()
        self.pip.assert_not_called()

    def test_conda_list_errors_prevent_install(self):
        for error in (OSError("cannot launch"), subprocess.CalledProcessError(1, ["conda", "list"])):
            with self.subTest(error=error):
                self.conda_list.side_effect = error
                self.assertFalse(self.require("ffmpeg", confirm=False, channel="conda"))
        self.assertIn("couldn't read installed conda packages", self.output.getvalue())
        self.pip.assert_not_called()

    def test_conda_malformed_records_prevent_install(self):
        for output in ("invalid JSON", "{}", "[null]", '[{"name": "ffmpeg"}]',
                       '[{"name": "ffmpeg", "version": 2}]'):
            with self.subTest(output=output):
                self.conda_list.side_effect = None
                self.conda_list.return_value = subprocess.CompletedProcess([], 0, stdout=output)
                self.assertFalse(self.require("ffmpeg", confirm=False, channel="conda"))
        self.pip.assert_not_called()

    def test_conda_installer_failure_is_reported(self):
        self.pip.return_value = 1
        self.assertFalse(self.require("ffmpeg", confirm=False, channel="conda"))
        self.assertIn("conda failed", self.output.getvalue())
        self.assertEqual(self.conda_list.call_count, 1)

    def test_conda_post_install_missing_or_wrong_version_fails(self):
        for after in (subprocess.CompletedProcess([], 0, stdout="[]"), self.conda_record("1.0")):
            with self.subTest(after=after):
                self.conda_list.side_effect = [self.conda_record("3.0"), after]
                self.assertFalse(self.require("ffmpeg", "2.0", confirm=False, channel="conda"))

    def test_conda_post_install_query_error_is_reported(self):
        self.conda_list.side_effect = [self.conda_record("1.0"), OSError("cannot launch")]
        self.assertFalse(self.require("ffmpeg", confirm=False, channel="conda"))
        self.assertIn("couldn't verify installed conda packages", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
