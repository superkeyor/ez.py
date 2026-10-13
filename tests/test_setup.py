import ast
from pathlib import Path
import types
import unittest
from unittest.mock import patch
import warnings


ROOT = Path(__file__).resolve().parents[1]


def literal(source, name):
    tree = ast.parse(source)
    value = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
    )
    return ast.literal_eval(value)


class SetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = {}
        setuptools = types.ModuleType("setuptools")
        setuptools.setup = lambda **kwargs: cls.metadata.update(kwargs)
        setuptools.find_packages = lambda: ["ez"]
        namespace = {"__file__": str(ROOT / "setup.py"), "__name__": "__main__"}
        with patch.dict("sys.modules", {"setuptools": setuptools}), warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            exec(compile((ROOT / "setup.py").read_text(), str(ROOT / "setup.py"), "exec"), namespace)

    def test_identity_and_literal_version(self):
        self.assertEqual(self.metadata["name"], "ez")
        self.assertEqual(
            self.metadata["version"], literal((ROOT / "ez/version.py").read_text(), "__version__"),
        )

    def test_python_requirement_matches_documentation(self):
        self.assertEqual(self.metadata["python_requires"], ">=3.11")
        self.assertNotIn("Programming Language :: Python :: 2.7", self.metadata["classifiers"])
        self.assertIn("Requires Python 3.11+.", (ROOT / "README.md").read_text())

    def test_console_scripts_follow_the_source_registry(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            commands = literal((ROOT / "ez/ez.py").read_text(), "_CLI_COMMANDS")
        self.assertEqual(
            self.metadata["entry_points"]["console_scripts"],
            [f"{command}=ez.ez:_cli" for command in commands],
        )

    def test_requirements_have_no_duplicates(self):
        requirements = self.metadata["install_requires"]
        self.assertTrue(all(isinstance(requirement, str) for requirement in requirements))
        self.assertEqual(len(requirements), len(set(requirements)))

    def test_readme_and_package_data_are_included(self):
        self.assertEqual(
            self.metadata["long_description"], (ROOT / "README.md").read_text(),
        )
        self.assertEqual(self.metadata["long_description_content_type"], "text/markdown")
        self.assertTrue(self.metadata["include_package_data"])
        self.assertIn("include README.md", (ROOT / "MANIFEST.in").read_text())


if __name__ == "__main__":
    unittest.main()
