import ast
from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
import warnings

from pptx import Presentation


ROOT = Path(__file__).resolve().parents[1]


def load_cli():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse((ROOT / "ez/ez.py").read_text(encoding="utf-8"))
    nodes = [
        node for node in tree.body
        if (isinstance(node, ast.FunctionDef)
            and (node.name.startswith(("_md_", "_output_", "_cli", "_pdfannot_"))
                 or node.name in ("_parse_ranges", "pptx2md", "docx2md", "xlsx2md",
                                  "pdf2md", "pdfannot")))
        or (isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name)
                    and target.id in ("_CLI_COMMANDS", "_CLI_ARGUMENT_GROUPS", "_CLI_OUTPUT_FORMATS")
                    for target in node.targets))
    ]
    import glob
    namespace = {"os": os, "re": re, "sys": sys, "glob": glob}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "ez/ez.py", "exec"), namespace)
    return namespace


class Pptx2mdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.namespace = load_cli()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.source = Path(temporary.name) / "slides.pptx"
        self.presentation = Presentation()
        for title, visibility in (
            ("Visible first", None),
            ("Hidden zero", "0"),
            ("Hidden false", "false"),
            ("Visible one", "1"),
            ("Visible true", "true"),
        ):
            slide = self.presentation.slides.add_slide(self.presentation.slide_layouts[0])
            slide.shapes.title.text = title
            slide.notes_slide.notes_text_frame.text = "Speaker note " + title
            if visibility is not None:
                slide._element.set("show", visibility)
        self.presentation.save(self.source)

    def convert(self, **kwargs):
        with redirect_stdout(io.StringIO()) as output:
            markdown = self.namespace["pptx2md"](self.source, **kwargs)
        self.assertEqual(output.getvalue(), markdown)
        return markdown

    def test_default_skips_hidden_and_preserves_original_numbers(self):
        markdown = self.convert()
        self.assertEqual(re.findall(r"Slide number: (\d+)", markdown), ["1", "4", "5"])
        self.assertNotIn("Hidden", markdown)
        self.assertNotIn("Speaker note", markdown)
        self.assertIn("Visible first", markdown)
        self.assertIn("Visible one", markdown)
        self.assertIn("Visible true", markdown)

    def test_include_hidden_with_notes(self):
        markdown = self.convert(skip_hidden=False, note=True)
        self.assertEqual(re.findall(r"Slide number: (\d+)", markdown),
                         ["1", "2", "3", "4", "5"])
        self.assertIn("Hidden zero", markdown)
        self.assertIn("Hidden false", markdown)
        self.assertIn("Speaker note Hidden zero", markdown)

    def test_selection_uses_original_numbers_and_skips_hidden(self):
        markdown = self.convert(slides="4,2,1,4")
        self.assertEqual(re.findall(r"Slide number: (\d+)", markdown), ["1", "4"])
        self.assertNotIn("Hidden", markdown)
        markdown = self.convert(slides="2-3", skip_hidden=False)
        self.assertEqual(re.findall(r"Slide number: (\d+)", markdown), ["2", "3"])

    def test_hidden_only_selection_is_empty(self):
        self.assertEqual(self.convert(slides="2-3"), "")

    def test_all_hidden_presentation_is_empty(self):
        for slide in self.presentation.slides:
            slide._element.set("show", "0")
        self.presentation.save(self.source)
        self.assertEqual(self.convert(), "")

    def test_without_markers(self):
        markdown = self.convert(markers=False)
        self.assertNotIn("Slide number:", markdown)
        self.assertNotIn("Hidden", markdown)
        self.assertEqual(markdown.count("\n\n---\n\n"), 2)

    def test_cli_default_and_include_hidden(self):
        for flags, expected in (([], ["1", "4", "5"]),
                                (["--include-hidden"], ["1", "2", "3", "4", "5"])):
            with self.subTest(flags=flags), redirect_stdout(io.StringIO()) as output:
                status = self.namespace["_cli"]([str(self.source), *flags], command="pptx2md")
            self.assertEqual(status, 0)
            self.assertEqual(re.findall(r"Slide number: (\d+)", output.getvalue()), expected)

    def test_cli_help_for_all_converters(self):
        for command in self.namespace["_CLI_COMMANDS"]:
            for flag in ("-h", "--help"):
                with self.subTest(command=command, flag=flag):
                    with redirect_stdout(io.StringIO()) as output:
                        with self.assertRaises(SystemExit) as result:
                            self.namespace["_cli"]([flag], command=command)
                    self.assertEqual(result.exception.code, 0)
                    help_text = output.getvalue()
                    self.assertIn(f"Usage:\n    {command} ", help_text)
                    for section in ("Notes:", "Example:", "See also:"):
                        self.assertIn(section, help_text)
                    if command == "pptx2md":
                        self.assertIn("--include-hidden", help_text)
                        self.assertIn("skipped by default", help_text)
                        self.assertIn("Slides are 1-based", help_text)
                        self.assertIn("original order and numbering", help_text)
                        self.assertIn("even when selected", help_text)

    def test_cli_without_arguments_shows_help(self):
        for command in self.namespace["_CLI_COMMANDS"]:
            with self.subTest(command=command), redirect_stdout(io.StringIO()) as output:
                status = self.namespace["_cli"]([], command=command)
            self.assertEqual(status, 0)
            self.assertIn(f"Usage:\n    {command} ", output.getvalue())


if __name__ == "__main__":
    unittest.main()
