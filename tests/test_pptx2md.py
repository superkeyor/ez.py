import ast
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
import warnings
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pptx import Presentation
from pptx.util import Inches


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

    def add_image_to_first_slide(self):
        from PIL import Image

        image_path = self.source.with_suffix(".png")
        Image.new("RGB", (32, 32), "white").save(image_path)
        self.presentation.slides[0].shapes.add_picture(
            str(image_path), Inches(1), Inches(1)
        )
        self.presentation.save(self.source)

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

    def test_ocr_is_opt_in_and_text_is_added_to_its_slide(self):
        self.add_image_to_first_slide()
        recognize = Mock(return_value="Recognized picture text")
        failed_dir = self.source.parent / "failed-images"
        with patch.dict(self.namespace, {
                "_md_require_vision": Mock(),
                "_md_vision_ocr": recognize,
        }):
            default_markdown = self.convert()
            self.assertNotIn("Recognized picture text", default_markdown)
            recognize.assert_not_called()

            markdown = self.convert(ocr=True, ocr_failed_dir=failed_dir)

        self.assertIn("<!-- Slide number: 1 -->", markdown)
        self.assertIn("*[Image OCR]*\n\nRecognized picture text\n\n*[End OCR]*", markdown)
        recognize.assert_called_once()
        self.assertEqual(recognize.call_args.args[1], "accurate")
        self.assertEqual(recognize.call_args.args[2], "english")
        self.assertEqual(recognize.call_args.kwargs["failed_dir"], str(failed_dir))
        self.assertIn(str(self.source), recognize.call_args.args[3])
        self.assertFalse(failed_dir.exists())

    def test_ocr_cli_uses_requested_mode(self):
        self.add_image_to_first_slide()
        recognize = Mock(return_value="Fast recognized text")
        failed_dir = self.source.parent / "failed-images"
        with (patch.dict(self.namespace, {
                "_md_require_vision": Mock(),
                "_md_vision_ocr": recognize,
        }), redirect_stdout(io.StringIO()) as output):
            status = self.namespace["_cli"](
                [str(self.source), "--ocr", "--ocr-mode", "fast",
                 "--ocr-failed-dir", str(failed_dir)],
                command="pptx2md",
            )
        self.assertEqual(status, 0)
        self.assertIn("Fast recognized text", output.getvalue())
        self.assertEqual(recognize.call_args.args[1], "fast")
        self.assertEqual(recognize.call_args.kwargs["failed_dir"], str(failed_dir))

    def test_ocr_cli_uses_requested_language(self):
        self.add_image_to_first_slide()
        recognize = Mock(return_value="Chinese recognized text")
        with (patch.dict(self.namespace, {
                "_md_require_vision": Mock(),
                "_md_vision_ocr": recognize,
        }), redirect_stdout(io.StringIO())):
            status = self.namespace["_cli"](
                [str(self.source), "--ocr", "--ocr-language", "chinese"],
                command="pptx2md",
            )
        self.assertEqual(status, 0)
        self.assertEqual(recognize.call_args.args[2], "chinese")

    def test_ocr_mode_requires_ocr_on_cli(self):
        with redirect_stderr(io.StringIO()) as errors:
            with self.assertRaises(SystemExit) as result:
                self.namespace["_cli"](
                    [str(self.source), "--ocr-mode", "fast"], command="pptx2md"
                )
        self.assertEqual(result.exception.code, 2)
        self.assertIn("require --ocr", errors.getvalue())

    def test_ocr_language_requires_ocr_on_cli(self):
        with redirect_stderr(io.StringIO()) as errors:
            with self.assertRaises(SystemExit) as result:
                self.namespace["_cli"](
                    [str(self.source), "--ocr-language", "chinese"],
                    command="pptx2md",
                )
        self.assertEqual(result.exception.code, 2)
        self.assertIn("--ocr-language", errors.getvalue())

    def test_ocr_failed_dir_requires_ocr_on_cli(self):
        with redirect_stderr(io.StringIO()) as errors:
            with self.assertRaises(SystemExit) as result:
                self.namespace["_cli"](
                    [str(self.source), "--ocr-failed-dir", "failed-images"],
                    command="pptx2md",
                )
        self.assertEqual(result.exception.code, 2)
        self.assertIn("--ocr-failed-dir", errors.getvalue())

    def test_ocr_failed_dir_requires_ocr_in_python_api(self):
        with self.assertRaisesRegex(ValueError, "requires ocr=True"):
            self.convert(ocr_failed_dir=self.source.parent / "failed-images")

    def test_vision_ocr_rejects_non_macos(self):
        with patch.object(sys, "platform", "linux"):
            with self.assertRaisesRegex(OSError, "only on macOS"):
                self.namespace["_md_require_vision"]()

    def test_vision_ocr_uses_requested_level_and_languages(self):
        from PIL import Image

        image = io.BytesIO()
        Image.new("RGB", (4, 4), "white").save(image, format="PNG")
        image_data = image.getvalue()
        for mode, level in (("accurate", 1), ("fast", 2)):
            for language, languages in (
                    ("english", ["en-US"]),
                    ("chinese", ["zh-Hans"]),
                    ("both", ["zh-Hans", "en-US"])):
                request = Mock()
                request.results.return_value = []
                handler = Mock()
                handler.performRequests_error_.return_value = (True, None)
                vision = SimpleNamespace(
                    VNRecognizeTextRequest=Mock(),
                    VNRequestTextRecognitionLevelAccurate=1,
                    VNRequestTextRecognitionLevelFast=2,
                    VNImageRequestHandler=Mock(),
                )
                vision.VNRecognizeTextRequest.alloc.return_value.init.return_value = request
                vision.VNImageRequestHandler.alloc.return_value.initWithData_options_.return_value = handler
                foundation = SimpleNamespace(
                    NSData=SimpleNamespace(
                        dataWithBytes_length_=Mock(return_value=object())
                    )
                )
                with (patch.object(sys, "platform", "darwin"),
                      patch.dict(sys.modules, {
                          "Vision": vision, "Foundation": foundation
                      })):
                    self.assertEqual(
                        self.namespace["_md_vision_ocr"](image_data, mode, language),
                        "",
                    )
                request.setRecognitionLevel_.assert_called_once_with(level)
                request.setRecognitionLanguages_.assert_called_once_with(languages)

    def test_vision_ocr_reports_missing_binding(self):
        with (patch.object(sys, "platform", "darwin"),
              patch.dict(sys.modules, {"Vision": None})):
            with self.assertRaisesRegex(ImportError, "pyobjc-framework-Vision"):
                self.namespace["_md_require_vision"]()

    def test_vision_ocr_skips_invalid_image_with_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = self.namespace["_md_vision_ocr"](
                b"not an image", context="PowerPoint slide 2"
            )
        self.assertEqual(result, "")
        self.assertEqual(len(caught), 1)
        self.assertIn("PowerPoint slide 2", str(caught[0].message))

    def test_vision_zero_dimension_error_skips_only_that_image(self):
        request = Mock()
        request.results.return_value = []
        handler = Mock()
        handler.performRequests_error_.return_value = (
            False, "Error: zero-dimensioned image (0 x 0)"
        )
        vision = SimpleNamespace(
            VNRecognizeTextRequest=Mock(),
            VNRequestTextRecognitionLevelAccurate=1,
            VNRequestTextRecognitionLevelFast=2,
            VNImageRequestHandler=Mock(),
        )
        vision.VNRecognizeTextRequest.alloc.return_value.init.return_value = request
        vision.VNImageRequestHandler.alloc.return_value.initWithData_options_.return_value = handler
        foundation = SimpleNamespace(
            NSData=SimpleNamespace(dataWithBytes_length_=Mock(return_value=object()))
        )
        image = io.BytesIO()
        from PIL import Image

        Image.new("RGB", (4, 4), "white").save(image, format="PNG")
        failed_dir = self.source.parent / "failed-images"
        with (patch.object(sys, "platform", "darwin"),
              patch.dict(sys.modules, {"Vision": vision, "Foundation": foundation}),
              warnings.catch_warnings(record=True) as caught):
            warnings.simplefilter("always")
            result = self.namespace["_md_vision_ocr"](
                image.getvalue(), context="PowerPoint slide 3",
                failed_dir=failed_dir,
                failed_name="deck-slide-3-Graphic 1",
                image_extension=".png",
            )
        self.assertEqual(result, "")
        self.assertEqual(len(caught), 1)
        self.assertIn("zero-dimensioned", str(caught[0].message))
        saved_image = failed_dir / "deck-slide-3-Graphic_1.png"
        self.assertEqual(saved_image.read_bytes(), image.getvalue())
        self.assertIn(str(saved_image), str(caught[0].message))

    def test_vision_failure_saves_image_before_raising(self):
        from PIL import Image

        request = Mock()
        handler = Mock()
        handler.performRequests_error_.return_value = (
            False, "Vision processing failed"
        )
        vision = SimpleNamespace(
            VNRecognizeTextRequest=Mock(),
            VNRequestTextRecognitionLevelAccurate=1,
            VNRequestTextRecognitionLevelFast=2,
            VNImageRequestHandler=Mock(),
        )
        vision.VNRecognizeTextRequest.alloc.return_value.init.return_value = request
        vision.VNImageRequestHandler.alloc.return_value.initWithData_options_.return_value = handler
        foundation = SimpleNamespace(
            NSData=SimpleNamespace(dataWithBytes_length_=Mock(return_value=object()))
        )
        image = io.BytesIO()
        Image.new("RGB", (4, 4), "white").save(image, format="PNG")
        image_data = image.getvalue()
        failed_dir = self.source.parent / "failed-images"
        with (patch.object(sys, "platform", "darwin"),
              patch.dict(sys.modules, {"Vision": vision, "Foundation": foundation})):
            with self.assertRaisesRegex(OSError, "Apple Vision OCR failed"):
                self.namespace["_md_vision_ocr"](
                    image_data,
                    context="PowerPoint slide 4, picture 'Graphic 1'",
                    failed_dir=failed_dir,
                    failed_name="deck-slide-4-Graphic 1",
                    image_extension=".png",
                )

        saved_image = failed_dir / "deck-slide-4-Graphic_1.png"
        self.assertEqual(saved_image.read_bytes(), image_data)

    def test_failed_ocr_image_saves_without_overwriting_existing_files(self):
        failed_dir = self.source.parent / "failed-images"
        save_failed = self.namespace["_md_save_failed_ocr_image"]

        first = save_failed(b"first", failed_dir, "slide/1", ".PNG")
        second = save_failed(b"second", failed_dir, "slide/1", ".PNG")

        self.assertEqual(first.name, "slide_1.png")
        self.assertEqual(second.name, "slide_1-2.png")
        self.assertEqual(first.read_bytes(), b"first")
        self.assertEqual(second.read_bytes(), b"second")

    def test_pptx_with_no_embedded_images_still_converts(self):
        with (patch.dict(self.namespace, {"_md_check_ocr_platform": Mock()}),
              redirect_stdout(io.StringIO()) as output):
            markdown = self.namespace["pptx2md"](self.source, ocr=True)
        self.assertEqual(output.getvalue(), markdown)
        self.assertIn("Visible first", markdown)
        self.assertNotIn("Image OCR", markdown)

    def test_pptx_linked_picture_is_silently_skipped(self):
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        class LinkedPicture:
            shape_type = MSO_SHAPE_TYPE.PICTURE
            name = "Linked Picture"

            @property
            def image(self):
                raise ValueError("no embedded image")

        slide = SimpleNamespace(shapes=[LinkedPicture()])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            blobs = list(self.namespace["_md_pptx_image_blobs"](slide))
        self.assertEqual(blobs, [])
        self.assertEqual(caught, [])

    def test_pptx_linked_picture_does_not_fail_conversion(self):
        from pptx.oxml.ns import qn
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        self.add_image_to_first_slide()
        picture = next(
            shape for shape in self.presentation.slides[0].shapes
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE
        )
        picture._pic.blipFill.blip.attrib.pop(qn("r:embed"))
        self.presentation.save(self.source)
        recognize = Mock()
        with (patch.dict(self.namespace, {
                "_md_check_ocr_platform": Mock(),
                "_md_vision_ocr": recognize,
        }), warnings.catch_warnings(record=True) as caught):
            warnings.simplefilter("always")
            markdown = self.convert(ocr=True)
        self.assertIn("Visible first", markdown)
        self.assertEqual(caught, [])
        recognize.assert_not_called()

    def test_cli_pptx_linked_picture_produces_no_warning(self):
        from pptx.oxml.ns import qn
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        self.add_image_to_first_slide()
        picture = next(
            shape for shape in self.presentation.slides[0].shapes
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE
        )
        picture._pic.blipFill.blip.attrib.pop(qn("r:embed"))
        self.presentation.save(self.source)
        errors = io.StringIO()
        recognize = Mock()
        with (patch.dict(self.namespace, {
                "_md_check_ocr_platform": Mock(),
                "_md_vision_ocr": recognize,
        }),
              redirect_stderr(errors), redirect_stdout(io.StringIO())):
            status = self.namespace["_cli"](
                [str(self.source), "--ocr"], command="pptx2md"
            )

        self.assertEqual(status, 0)
        self.assertEqual(errors.getvalue(), "")
        recognize.assert_not_called()

    def test_cli_pptx_vision_warning_names_file_slide_and_picture(self):
        self.add_image_to_first_slide()
        self.presentation.save(self.source)

        def skip_vision(image_data, mode, language, context, **kwargs):
            return skip_vision_with_warning(context)

        def skip_vision_with_warning(context):
            warnings.warn(
                f"Skipping OCR for {context}: Vision reports a zero-dimensioned image.",
                UserWarning,
            )
            return ""

        errors = io.StringIO()
        with (patch.dict(self.namespace, {
                "_md_check_ocr_platform": Mock(),
                "_md_vision_ocr": skip_vision,
        }), redirect_stderr(errors), redirect_stdout(io.StringIO())):
            status = self.namespace["_cli"](
                [str(self.source), "--ocr"], command="pptx2md"
            )

        self.assertEqual(status, 0)
        warning = errors.getvalue()
        self.assertIn("pptx2md: warning:", warning)
        self.assertIn(str(self.source), warning)
        self.assertIn("slide 1", warning)
        self.assertIn("picture 'Picture 3'", warning)
        self.assertIn("zero-dimensioned image", warning)
        self.assertNotRegex(warning, r"ez\.py:\d+")

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
                    if command in ("pptx2md", "docx2md", "xlsx2md"):
                        self.assertIn("--ocr", help_text)
                        self.assertIn("--ocr-mode", help_text)
                        self.assertIn("--ocr-language", help_text)
                        self.assertIn("--ocr-failed-dir", help_text)

    def test_cli_without_arguments_shows_help(self):
        for command in self.namespace["_CLI_COMMANDS"]:
            with self.subTest(command=command), redirect_stdout(io.StringIO()) as output:
                status = self.namespace["_cli"]([], command=command)
            self.assertEqual(status, 0)
            self.assertIn(f"Usage:\n    {command} ", output.getvalue())


class OfficeOcrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.namespace = load_cli()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        from PIL import Image

        self.image_path = self.root / "image.png"
        Image.new("RGB", (32, 32), "white").save(self.image_path)

    def test_docx_ocr_is_inserted_after_embedded_image(self):
        from docx import Document
        from docx.shared import Inches

        source = self.root / "document.docx"
        document = Document()
        document.add_paragraph().add_run().add_picture(str(self.image_path), width=Inches(1))
        document.save(source)
        recognize = Mock(return_value="Word image text")
        failed_dir = self.root / "failed-images"
        with patch.dict(self.namespace, {
                "_md_require_vision": Mock(),
                "_md_vision_ocr": recognize,
        }), redirect_stdout(io.StringIO()) as output:
            markdown = self.namespace["docx2md"](
                source, ocr=True, ocr_failed_dir=failed_dir
            )
        self.assertEqual(output.getvalue(), markdown)
        self.assertIn("Word image text", markdown)
        self.assertIn("\n[Image OCR]", markdown)
        recognize.assert_called_once()
        self.assertIn(str(source), recognize.call_args.args[3])
        self.assertEqual(recognize.call_args.kwargs["failed_dir"], str(failed_dir))

    def test_xlsx_ocr_includes_image_anchor_and_sheet_context(self):
        from openpyxl import Workbook
        from openpyxl.drawing.image import Image as SpreadsheetImage

        source = self.root / "workbook.xlsx"
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Summary"
        worksheet["A1"] = "Report"
        worksheet.add_image(SpreadsheetImage(str(self.image_path)), "B2")
        workbook.save(source)
        recognize = Mock(return_value="Spreadsheet image text")
        failed_dir = self.root / "failed-images"
        with patch.dict(self.namespace, {
                "_md_require_vision": Mock(),
                "_md_vision_ocr": recognize,
        }), redirect_stdout(io.StringIO()) as output:
            markdown = self.namespace["xlsx2md"](
                source, ocr=True, ocr_failed_dir=failed_dir
            )
        self.assertEqual(output.getvalue(), markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("### OCR from image near B2", markdown)
        self.assertIn("Spreadsheet image text", markdown)
        recognize.assert_called_once()
        self.assertIn(str(source), recognize.call_args.args[3])
        self.assertEqual(recognize.call_args.kwargs["failed_dir"], str(failed_dir))

    def test_xlsx_ocr_skips_unreadable_image_with_warning(self):
        from openpyxl import Workbook
        from openpyxl.drawing.image import Image as SpreadsheetImage
        from zipfile import ZIP_DEFLATED, ZipFile
        from PIL import Image

        image_path = self.root / "image.bmp"
        Image.new("RGB", (32, 32), "white").save(image_path)
        source = self.root / "workbook.xlsx"
        workbook = Workbook()
        workbook.active.add_image(SpreadsheetImage(str(image_path)), "B2")
        workbook.save(source)

        broken_source = self.root / "broken.xlsx"
        with ZipFile(source) as original, ZipFile(
                broken_source, "w", ZIP_DEFLATED) as broken:
            for item in original.infolist():
                data = original.read(item.filename)
                if item.filename == "xl/media/image1.bmp":
                    data = image_path.read_bytes()[:60]
                broken.writestr(item, data)

        recognize = Mock()
        failed_dir = self.root / "failed-images"
        with (patch.dict(self.namespace, {
                "_md_check_ocr_platform": Mock(),
                "_md_vision_ocr": recognize,
        }), warnings.catch_warnings(record=True) as caught,
                redirect_stdout(io.StringIO())):
            warnings.simplefilter("always")
            markdown = self.namespace["xlsx2md"](
                broken_source, ocr=True, ocr_failed_dir=failed_dir
            )
        self.assertIn("## Sheet", markdown)
        self.assertEqual(len(caught), 1)
        self.assertIn(str(broken_source), str(caught[0].message))
        self.assertIn("worksheet 'Sheet', image near B2", str(caught[0].message))
        self.assertIn("invalid or unreadable", str(caught[0].message))
        saved_image = failed_dir / "broken-Sheet-B2.bmp"
        self.assertEqual(saved_image.read_bytes(), image_path.read_bytes()[:60])
        self.assertIn(str(saved_image), str(caught[0].message))
        recognize.assert_not_called()


if __name__ == "__main__":
    unittest.main()
