import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_figures", ROOT / "scripts/render_figures.py")
FIGURES = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FIGURES)


class FigureTests(unittest.TestCase):
    def test_every_curated_asset_and_placement(self):
        figures = FIGURES.load_figures()
        result = FIGURES.validate(figures)
        self.assertGreaterEqual(result["notes"], 67)
        self.assertGreaterEqual(result["figures"], 83)
        self.assertEqual(set(f["topic"] for f in figures),
                         {"rendering", "blockchain", "physical-ai", "big-data"})

    def test_all_diagrams_are_valid_self_contained_svg(self):
        for figure in FIGURES.load_figures():
            with self.subTest(id=figure["id"]):
                svg = FIGURES.RENDERERS[figure["kind"]](figure)
                tree = ET.fromstring(svg)
                self.assertEqual(tree.tag, f"{{{FIGURES.SVG_NS}}}svg")
                self.assertIn("<title ", svg)
                self.assertIn("<desc ", svg)
                self.assertNotRegex(svg, r"@import|<script|<foreignObject|href=")
                self.assertNotIn("https://", svg.replace(FIGURES.SVG_NS, ""))
                self.assertNotIn("file://", svg)

    def test_png_fallbacks_have_correct_retina_dimensions(self):
        for figure in FIGURES.load_figures():
            with self.subTest(id=figure["id"]):
                data = FIGURES.figure_path(figure).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", data[16:24])
                svg = ET.parse(FIGURES.figure_path(figure, "svg")).getroot()
                self.assertEqual(width, int(svg.attrib["width"]) * 2)
                self.assertEqual(height, int(svg.attrib["height"]) * 2)

    def test_no_text_overflow_is_silently_accepted(self):
        canvas = FIGURES.Canvas("标题", "说明")
        with self.assertRaisesRegex(ValueError, "Text does not fit"):
            canvas.box(40, 100, 80, 60, "过长文字" * 12)

    def test_text_measurement_accounts_for_chinese(self):
        self.assertGreater(FIGURES.text_width("汉字", 18), FIGURES.text_width("ab", 18))
        wrapped = FIGURES.wrap("中文标签和英文 label 都需要换行", 100)
        self.assertTrue(all(FIGURES.text_width(line, 18) <= 100 for line in wrapped))

    def test_xml_sensitive_text_is_escaped(self):
        canvas = FIGURES.Canvas("A < B & C", 'desc "quoted"')
        canvas.box(40, 120, 300, 120, "x < y", "a & b")
        ET.fromstring(canvas.finish())

    def test_embedding_is_idempotent_and_recovers_original_prose(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "note.md"
            original = "# 标题\n\n原始正文。\n\n## 机制\n\n更多原文。\n"
            file.write_text(original, encoding="utf-8")
            figure = {"id": "sample", "topic": "rendering", "title": "测试图",
                      "subtitle": "测试说明", "placements": [{"file": "note.md", "after": "## 机制"}]}
            with patch.object(FIGURES, "ROOT", root):
                FIGURES.embed(figure)
                first = file.read_bytes()
                FIGURES.embed(figure)
                self.assertEqual(file.read_bytes(), first)
                self.assertIn(b"wiki/topics/rendering/images/sample.png", first)
            cleaned = re.sub(
                rb"\n<!-- illustration: ([a-z0-9-]+) -->\n.*?<!-- /illustration: \1 -->\n",
                b"", first, flags=re.S,
            )
            self.assertEqual(cleaned, original.encode("utf-8"))

    def test_missing_or_duplicate_heading_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "note.md"
            original = "## 重复\n\n内容\n\n## 重复\n"
            file.write_text(original, encoding="utf-8")
            figure = {"id": "sample", "topic": "rendering", "title": "测试",
                      "subtitle": "说明", "placements": [{"file": "note.md", "after": "## 重复"}]}
            with patch.object(FIGURES, "ROOT", root), self.assertRaises(ValueError):
                FIGURES.embed(figure)
            self.assertEqual(file.read_text(encoding="utf-8"), original)

    def test_same_figure_at_two_headings_in_one_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "note.md"
            file.write_text("## 一\n\n甲\n\n## 二\n\n乙\n", encoding="utf-8")
            figure = {"id": "sample", "topic": "rendering", "title": "测试图",
                      "subtitle": "说明", "placements": [
                          {"file": "note.md", "after": "## 一"},
                          {"file": "note.md", "after": "## 二"}]}
            with patch.object(FIGURES, "ROOT", root):
                FIGURES.embed(figure)
                original = file.read_bytes()
                FIGURES.embed(figure)
                self.assertEqual(original, file.read_bytes())
            self.assertEqual(original.count(b"<!-- illustration: sample-"), 2)

    def test_all_principle_and_industry_chapters_are_illustrated(self):
        figures = FIGURES.load_figures()
        placed = {p["file"] for f in figures for p in f["placements"]}
        for folder in ("advanced", "industry"):
            for chapter in (ROOT / f"wiki/topics/physical-ai/{folder}/chapters").glob("*.md"):
                self.assertIn(chapter.relative_to(ROOT).as_posix(), placed)

    def test_archival_originals_survive_additive_illustrations(self):
        root = ROOT / "wiki/topics/physical-ai"
        manifest = json.loads((root / "archive-manifest.json").read_text(encoding="utf-8"))
        for entry in manifest["deliverables"]:
            data = (root / entry["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
            if "original_sha256" in entry:
                stripped = re.sub(
                    rb"\n<!-- illustration: ([a-z0-9-]+) -->\n.*?<!-- /illustration: \1 -->\n",
                    b"", data, flags=re.S,
                )
                self.assertEqual(hashlib.sha256(stripped).hexdigest(), entry["original_sha256"])

    def test_archived_html_cannot_overwrite_markdown_routes(self):
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        for figure in FIGURES.load_figures():
            for placement in figure["placements"]:
                file = ROOT / placement["file"]
                if file.with_suffix(".html").exists():
                    self.assertIn(f"  - {file.relative_to(ROOT).with_suffix('.html').as_posix()}", config)


if __name__ == "__main__":
    unittest.main()
