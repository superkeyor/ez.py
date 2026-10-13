import ast
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "ez/prepublish.py"
spec = importlib.util.spec_from_file_location("ez_prepublish", HOOK)
prepublish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepublish)

SOURCE = '''__doc__ = "Old catalog."
#region Helpers
#region useful
def useful(value=1):
    """Return the supplied value.

    Detailed usage remains here.
    """
    return value
shortcut = useful
#endregion useful
#endregion Helpers
'''


def module_doc(source):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        return ast.literal_eval(prepublish._literal_assignment(ast.parse(source), "__doc__"))


class CatalogTests(unittest.TestCase):
    def test_generated_names_aliases_and_summary(self):
        updated = prepublish.generate_doc(SOURCE)
        doc = module_doc(updated)
        self.assertIn("Helpers:", doc)
        self.assertIn("useful (aliases: shortcut) - Return the supplied value.", doc)
        self.assertNotIn("Old catalog.", doc)

    def test_only_module_documentation_changes(self):
        updated = prepublish.generate_doc(SOURCE)
        self.assertEqual(SOURCE.split("#region", 1)[1], updated.split("#region", 1)[1])

    def test_idempotent(self):
        updated = prepublish.generate_doc(SOURCE)
        self.assertEqual(updated, prepublish.generate_doc(updated))

    def test_imported_shortcuts_and_chained_aliases(self):
        source = SOURCE + (
            "#region Waiting\nfrom time import sleep\nwait = sleep\n"
            "rest = wait\n#endregion Waiting\n"
        )
        self.assertIn(
            "sleep (aliases: wait, rest) - Imported from time.sleep.",
            module_doc(prepublish.generate_doc(source)),
        )

    def test_import_aliases_share_one_entry(self):
        source = SOURCE + (
            "#region Paths\nfrom os import getcwd as pwd\n"
            "from os import getcwd as cwd\n#endregion Paths\n"
        )
        self.assertIn(
            "pwd (aliases: cwd) - Imported from os.getcwd.",
            module_doc(prepublish.generate_doc(source)),
        )

    def test_repeated_topic_blocks_are_merged(self):
        source = SOURCE + (
            "#region Helpers\n#region another\n"
            'def another():\n    """Return None."""\n    return None\n'
            "#endregion another\n#endregion Helpers\n"
        )
        doc = module_doc(prepublish.generate_doc(source))
        self.assertEqual(doc.count("Helpers:"), 1)
        self.assertIn("another - Return None.", doc)

    def test_region_looking_text_inside_strings_is_ignored(self):
        source = SOURCE + 'example = """\n#region fake\n#endregion wrong\n"""\n'
        updated = prepublish.generate_doc(source)
        self.assertTrue(updated.endswith(source[source.index("example ="):]))

    def test_nested_functions_and_methods_are_not_cataloged(self):
        source = SOURCE.replace(
            "    return value",
            "    def inner():\n        return value\n    return inner()",
        ) + 'class Thing:\n    def method(self):\n        return None\n'
        doc = module_doc(prepublish.generate_doc(source))
        self.assertNotIn("inner -", doc)
        self.assertNotIn("method -", doc)

    def test_decorators_are_inside_the_function_region(self):
        source = SOURCE.replace("def useful", "@decorator\ndef useful")
        prepublish.generate_doc(source)
        source = source.replace("#region useful\n@decorator", "@decorator\n#region useful")
        with self.assertRaisesRegex(ValueError, "enclose"):
            prepublish.generate_doc(source)

    def test_unicode_offsets_and_safe_literal_escaping(self):
        source = SOURCE.replace(
            '__doc__ = "Old catalog."',
            'title = "café"; __doc__ = "Old catalog."; tail = "untouched"',
        ).replace(
            "Return the supplied value.",
            "Return café, quotes \\\"\\\"\\\", and a path C:\\\\tmp.",
        )
        updated = prepublish.generate_doc(source)
        self.assertIn('title = "café"; __doc__ = ', updated)
        self.assertIn('; tail = "untouched"', updated)
        self.assertIn('café, quotes """', module_doc(updated))
        self.assertEqual(updated, prepublish.generate_doc(updated))

    def test_missing_docstring_is_an_error(self):
        source = SOURCE.replace(
            '    """Return the supplied value.\n\n    Detailed usage remains here.\n    """\n', "",
        )
        with self.assertRaisesRegex(ValueError, "docstring"):
            prepublish.generate_doc(source)

    def test_empty_docstring_is_an_error(self):
        source = SOURCE.replace(
            '"""Return the supplied value.\n\n    Detailed usage remains here.\n    """', '""" """',
        )
        with self.assertRaisesRegex(ValueError, "docstring"):
            prepublish.generate_doc(source)

    def test_missing_function_region_is_an_error(self):
        source = SOURCE.replace("#region useful\n", "").replace("#endregion useful\n", "")
        with self.assertRaisesRegex(ValueError, "own region"):
            prepublish.generate_doc(source)

    def test_alias_outside_topic_is_an_error(self):
        source = SOURCE.replace("shortcut = useful\n", "") + "shortcut = useful\n"
        with self.assertRaisesRegex(ValueError, "outside"):
            prepublish.generate_doc(source)

    def test_malformed_regions_are_errors(self):
        sources = [
            SOURCE + "#endregion\n",
            SOURCE.replace("#endregion Helpers\n", ""),
            SOURCE.replace("#endregion Helpers", "#endregion Wrong"),
            SOURCE.replace("#region Helpers", "#region"),
        ]
        for source in sources:
            with self.subTest(source=source), self.assertRaises(ValueError):
                prepublish.generate_doc(source)

    def test_doc_assignment_must_be_one_literal(self):
        for source in (
            SOURCE.replace('__doc__ = "Old catalog."', '__doc__ = str("old")'),
            SOURCE + '__doc__ = "duplicate"\n',
            SOURCE.replace('__doc__ = "Old catalog."\n', ""),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                prepublish.generate_doc(source)

    def test_wildcard_import_inside_topic_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Wildcard"):
            prepublish.generate_doc(SOURCE + "#region Other\nfrom other import *\n#endregion Other\n")

    def test_no_module_functions_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "No module-level"):
            prepublish.generate_doc('__doc__ = "Nothing."\n')

    def test_live_catalog_and_region_layout(self):
        source = (ROOT / "ez/ez.py").read_text(encoding="utf-8")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertEqual(source, prepublish.generate_doc(source))
            tree = ast.parse(source)
        regions = prepublish._regions(source)
        lines = source.splitlines()
        separator = "# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><"
        for start, end, labels in regions:
            if len(labels) == 1:
                self.assertEqual(lines[start - 2], separator)
                self.assertEqual(lines[end - 1], "#endregion " + labels[0])
            else:
                self.assertNotEqual(lines[start - 2], separator)
        doc = module_doc(source)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                matches = [
                    line for line in doc.splitlines()
                    if line.startswith(f"    {node.name} -") or line.startswith(f"    {node.name} (aliases:")
                ]
                self.assertEqual(len(matches), 1, node.name)
                self.assertTrue(ast.get_docstring(node))
        for shortcut in ("pwd", "cwd", "Randomize", "randomize", "sleep", "wait", "ppprint", "which"):
            self.assertIn(shortcut, doc)


class PrepublishTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="ez prepublish tests ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "ez.py"
        self.version = self.root / "version.py"
        self.source.write_text(SOURCE, encoding="utf-8")
        self.original_version = "__version__ = '11.7.4'"
        self.version.write_text(self.original_version, encoding="utf-8")

    def invoke(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(prepublish, "HERE", self.root), redirect_stdout(stdout), redirect_stderr(stderr):
            status = prepublish.main(args)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_check_is_read_only_and_stale_fails(self):
        status, _, error = self.invoke(["--check-docs"])
        self.assertEqual(status, 1)
        self.assertIn("stale", error)
        self.assertEqual(self.source.read_text(), SOURCE)
        self.assertEqual(self.version.read_text(), self.original_version)

    def test_docs_only_does_not_increment(self):
        self.assertEqual(self.invoke(["--docs-only"])[0], 0)
        self.assertEqual(self.version.read_text(), self.original_version)
        self.assertEqual(self.invoke(["--check-docs"])[0], 0)

    def test_no_argument_flow_updates_docs_before_increment(self):
        original_bump = prepublish.bump_version

        def checked_bump(path):
            self.assertTrue(prepublish.update_doc(self.source, check=True))
            return original_bump(path)

        with patch.object(prepublish, "bump_version", side_effect=checked_bump):
            self.assertEqual(self.invoke([])[0], 0)
        self.assertEqual(self.version.read_text(), "__version__ = '11.7.5'")

    def test_bad_docs_do_not_increment(self):
        self.source.write_text(SOURCE.replace("#endregion Helpers\n", ""), encoding="utf-8")
        before = self.source.read_text()
        status, _, error = self.invoke([])
        self.assertEqual(status, 1)
        self.assertIn("Unclosed region", error)
        self.assertEqual(self.source.read_text(), before)
        self.assertEqual(self.version.read_text(), self.original_version)

    def test_version_rollover_preserves_numbering_scheme(self):
        for old, new in (("11.7.9", "11.8.0"), ("11.9.9", "12.0.0")):
            with self.subTest(old=old):
                self.version.write_text(f"__version__ = '{old}'")
                self.assertEqual(prepublish.bump_version(self.version), new)

    def test_invalid_version_does_not_overwrite_it(self):
        self.version.write_text("__version__ = 'broken'")
        with self.assertRaises(ValueError):
            prepublish.bump_version(self.version)
        self.assertEqual(self.version.read_text(), "__version__ = 'broken'")

    def test_help_has_no_side_effects(self):
        with self.assertRaises(SystemExit) as result:
            self.invoke(["--help"])
        self.assertEqual(result.exception.code, 0)
        self.assertEqual(self.source.read_text(), SOURCE)
        self.assertEqual(self.version.read_text(), self.original_version)

    def test_cli_resolves_paths_from_hook_and_import_is_safe(self):
        hook = self.root / "prepublish.py"
        hook.write_bytes(HOOK.read_bytes())
        imported = subprocess.run(
            [sys.executable, "-c",
             "import importlib.util; "
             f"s=importlib.util.spec_from_file_location('hook', {str(hook)!r}); "
             "m=importlib.util.module_from_spec(s); s.loader.exec_module(m)"],
            cwd=self.root.parent, capture_output=True, text=True,
        )
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertEqual(self.source.read_text(), SOURCE)
        self.assertEqual(self.version.read_text(), self.original_version)
        result = subprocess.run(
            [sys.executable, str(hook), "--docs-only"],
            cwd=self.root.parent, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(prepublish.update_doc(self.source, check=True))
        self.assertEqual(self.version.read_text(), self.original_version)


if __name__ == "__main__":
    unittest.main()
