import ast
import configparser
from contextlib import redirect_stdout
from email import message_from_bytes
import io
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import types
import unittest
from unittest.mock import patch
import warnings
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        cls.metadata = cls.config["project"]

    def test_identity_and_source_version(self):
        self.assertEqual(self.metadata["name"], "ez")
        self.assertEqual(
            self.metadata["version"], runpy.run_path(str(ROOT / "ez/version.py"))["__version__"],
        )

    def test_native_backend_and_package_layout(self):
        self.assertEqual(self.config["build-system"]["build-backend"], "uv_build")
        self.assertEqual(self.config["tool"]["uv"]["build-backend"]["module-root"], "")
        self.assertFalse((ROOT / "setup.py").exists())
        self.assertFalse((ROOT / "MANIFEST.in").exists())

    def test_python_requirement_matches_documentation(self):
        self.assertEqual(self.metadata["requires-python"], ">=3.11")
        self.assertIn("Requires Python 3.11+.", (ROOT / "README.md").read_text())

    def test_console_scripts_follow_the_source_registry(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            tree = ast.parse((ROOT / "ez/ez.py").read_text())
        commands = ast.literal_eval(next(
            node.value for node in tree.body if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "_CLI_COMMANDS"
                    for target in node.targets)
        ))
        self.assertEqual(self.metadata["scripts"], {name: "ez.ez:_cli" for name in commands})

    def test_requirements_preserve_platform_markers_without_release_tools(self):
        requirements = self.metadata["dependencies"]
        self.assertEqual(len(requirements), len(set(requirements)))
        self.assertFalse({"twine", "setuptools", "uv", "uv_build"} & set(requirements))
        for requirement in (
            'psutil; sys_platform != "linux"',
            'pynput; sys_platform != "linux"',
            'docx2pdf; sys_platform != "linux"',
            'imessage_reader; sys_platform == "darwin"',
        ):
            self.assertIn(requirement, requirements)

    def test_readme_and_license(self):
        self.assertEqual(self.metadata["readme"], "README.md")
        self.assertEqual(self.metadata["license"], "AGPL-3.0-or-later")

    def test_installed_version_uses_distribution_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "ez/version.py"
            target.parent.mkdir()
            target.write_bytes((ROOT / "ez/version.py").read_bytes())
            with patch("importlib.metadata.version", return_value="12.0.0") as version:
                self.assertEqual(runpy.run_path(str(target))["__version__"], "12.0.0")
            version.assert_called_once_with("ez")

    def test_ver_reads_the_version_module_instead_of_parsing_its_source(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            tree = ast.parse((ROOT / "ez/ez.py").read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == "ver")
        namespace = {
            "__file__": str(ROOT / "ez/ez.py"), "__package__": "ez", "os": os, "sys": sys,
        }
        exec(compile(ast.Module(body=[function], type_ignores=[]), "ver", "exec"), namespace)
        package = types.ModuleType("ez")
        package.__path__ = []
        module = types.ModuleType("ez.version")
        module.__version__ = "12.0.0"
        output = io.StringIO()
        with patch.dict(sys.modules, {"ez": package, "ez.version": module}), redirect_stdout(output):
            namespace["ver"]("ez")
        self.assertIn("ez: 12.0.0", output.getvalue())


@unittest.skipUnless(shutil.which("uv"), "uv is required for real artifact checks")
class BuiltArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="ez-artifact-tests-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.output = Path(cls.directory.name)
        cls.project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        cls.version = cls.project["version"]
        subprocess.run(
            ["uv", "build", "--out-dir", str(cls.output)], cwd=ROOT,
            capture_output=True, text=True, check=True,
        )
        cls.sdist = cls.output / f"ez-{cls.version}.tar.gz"
        cls.wheel_name = f"ez-{cls.version}-py3-none-any.whl"
        cls.wheel = zipfile.ZipFile(cls.output / cls.wheel_name)
        cls.addClassCleanup(cls.wheel.close)
        cls.info = f"ez-{cls.version}.dist-info"
        cls.metadata = message_from_bytes(cls.wheel.read(f"{cls.info}/METADATA"))

    def test_metadata_and_readme(self):
        self.assertEqual(self.metadata["Name"], "ez")
        self.assertEqual(self.metadata["Version"], self.version)
        self.assertEqual(self.metadata["Requires-Python"], ">=3.11")
        self.assertEqual(self.metadata["License-Expression"], "AGPL-3.0-or-later")
        self.assertEqual(
            self.metadata.get_payload(decode=True), (ROOT / "README.md").read_bytes(),
        )

    def test_dependency_metadata_matches_project(self):
        def normalized(requirement):
            name, marker = (requirement.split(";", 1) + [""])[:2]
            match = re.fullmatch(r"([^\[]+)(?:\[([^\]]+)\])?", name.strip())
            base, extras = match.groups()
            return (
                base.lower().replace("_", "-"), tuple(sorted((extras or "").split(","))),
                re.sub(r"\s+", "", marker).replace("'", '"'),
            )

        self.assertEqual(
            {normalized(item) for item in self.metadata.get_all("Requires-Dist")},
            {normalized(item) for item in self.project["dependencies"]},
        )

    def test_wheel_is_universal_and_contains_only_package_and_metadata(self):
        self.assertIn(b"Tag: py3-none-any", self.wheel.read(f"{self.info}/WHEEL"))
        names = self.wheel.namelist()
        self.assertTrue(all(name.startswith(("ez/", self.info + "/")) for name in names))
        self.assertFalse(any(
            ".DS_Store" in name or "__pycache__" in name or name.endswith(".pyc")
            for name in names
        ))
        for name in ("ez/__init__.py", "ez/ez.py", "ez/version.py", "ez/prepublish.py"):
            self.assertIn(name, names)
        entries = configparser.ConfigParser()
        entries.read_string(self.wheel.read(f"{self.info}/entry_points.txt").decode())
        self.assertEqual(dict(entries["console_scripts"]), self.project["scripts"])

    def test_sdist_contents_and_wheel_rebuild(self):
        with tarfile.open(self.sdist) as archive:
            names = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
        self.assertTrue({
            "pyproject.toml", "README.md", "scripts/publish.py", "publish.sh",
            "tests/test_publish.py", "Publish.app/Contents/Resources/script",
        } <= names)
        self.assertNotIn("setup.py", names)
        self.assertNotIn("MANIFEST.in", names)
        self.assertFalse(any("Contents/MacOS" in name for name in names))
        output = self.output / "rebuilt"
        subprocess.run(
            ["uv", "build", str(self.sdist), "--wheel", "--out-dir", str(output)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        with zipfile.ZipFile(output / self.wheel_name) as rebuilt:
            self.assertEqual(set(self.wheel.namelist()), set(rebuilt.namelist()))
            for name in self.wheel.namelist():
                self.assertEqual(self.wheel.read(name), rebuilt.read(name), name)

    def test_installed_version_without_runtime_dependencies(self):
        installed = self.output / "installed"
        self.wheel.extractall(installed)
        sys.path.insert(0, str(installed))
        try:
            self.assertEqual(
                runpy.run_path(str(installed / "ez/version.py"))["__version__"], self.version,
            )
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
