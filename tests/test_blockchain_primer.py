"""Guard the readable primer's coverage, illustration group, and scene renderer."""

from copy import deepcopy
import importlib.util
import math
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("primer_figures", ROOT / "scripts/render_figures.py")
FIGURES = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FIGURES)


def scene():
    return {
        "title": "A < B & C", "subtitle": "金额与控制分开", "height": 560,
        "nodes": [
            {"id": "a", "x": 60, "y": 160, "w": 240, "h": 120, "label": "左边"},
            {"id": "b", "x": 740, "y": 160, "w": 240, "h": 120, "label": "右边"},
        ],
        "edges": [{"points": [[300, 220], [740, 220]], "label": "请求"}],
    }


class PrimerCoverageTests(unittest.TestCase):
    def test_complete_book_is_directly_readable(self):
        text = (ROOT / "wiki/topics/blockchain/beginner-guide.md").read_text(encoding="utf-8")
        topics = [int(value) for value in re.findall(r"^## (\d+)\.", text, re.M)]
        self.assertEqual(topics, list(range(1, 35)))
        for concept in ("FDV", "市值", "期货", "永续", "资金费", "ETF", "RWA",
                        "DID", "IPFS", "Filecoin", "DePIN", "KYC", "清算",
                        "目标值", "助记词", "nonce", "DAO", "Lightning", "x402"):
            self.assertIn(concept, text)
        self.assertEqual(len(re.findall(r"^\| \d+\. ", text, re.M)), 30)
        self.assertIn("beginner-reference.md", text)

    def test_thirty_local_original_figures_have_unique_ids_and_placements(self):
        group = [item for item in FIGURES.load_figures() if item["id"].startswith("primer-")]
        self.assertEqual(len(group), 30)
        self.assertEqual(len({item["id"] for item in group}), 30)
        self.assertEqual(sum(len(item["placements"]) for item in group), 31)
        self.assertGreaterEqual(sum(item["kind"] == "scene" for item in group), 10)
        FIGURES.validate(group)
        for item in group:
            svg = FIGURES.figure_path(item, "svg").read_text(encoding="utf-8")
            self.assertNotRegex(svg, r"<script|<foreignObject|@import|href=")

    def test_prefix_check_does_not_touch_the_physical_ai_manifest(self):
        figures = [{"id": "other"}, {"id": "primer-test"}]
        with patch.object(FIGURES, "load_figures", return_value=figures), \
                patch.object(FIGURES, "validate", return_value={}) as validate, \
                patch.object(FIGURES, "asset_manifest") as manifest, \
                patch("sys.argv", ["render_figures.py", "--check", "--id-prefix", "primer-"]), \
                patch("builtins.print"):
            FIGURES.main()
        validate.assert_called_once_with([{"id": "primer-test"}])
        manifest.assert_not_called()

    def test_unknown_prefix_is_rejected(self):
        with patch.object(FIGURES, "load_figures", return_value=[{"id": "other"}]), \
                patch("sys.argv", ["render_figures.py", "--check", "--id-prefix", "primer-"]), \
                patch("sys.stderr"), self.assertRaises(SystemExit):
            FIGURES.main()

    def test_filtered_generation_refreshes_only_an_affected_manifest(self):
        figures = [
            {**scene(), "id": "physical-test", "topic": "physical-ai", "kind": "scene"},
            {**scene(), "id": "primer-test", "topic": "blockchain", "kind": "scene"},
        ]
        for prefix, refresh in (("physical-", True), ("primer-", False)):
            with self.subTest(prefix=prefix), tempfile.TemporaryDirectory() as directory, \
                    patch.object(FIGURES, "ROOT", Path(directory)), \
                    patch.object(FIGURES, "load_figures", return_value=figures), \
                    patch.object(FIGURES, "validate", return_value={}), \
                    patch.object(FIGURES, "asset_manifest") as manifest, \
                    patch.dict("sys.modules", {"cairosvg": SimpleNamespace(svg2png=Mock())}), \
                    patch("sys.argv", ["render_figures.py", "--id-prefix", prefix]), \
                    patch("builtins.print"):
                FIGURES.main()
                if refresh:
                    manifest.assert_called_once_with(figures)
                else:
                    manifest.assert_not_called()


class SceneSafetyTests(unittest.TestCase):
    def test_valid_scene_is_xml_and_escapes_text(self):
        svg = FIGURES.render_scene(scene())
        ET.fromstring(svg)
        self.assertIn("A &lt; B &amp; C", svg)

    def test_duplicate_nodes_are_rejected(self):
        data = scene()
        data["nodes"][1]["id"] = "a"
        with self.assertRaisesRegex(ValueError, "unique"):
            FIGURES.render_scene(data)

    def test_bounds_and_nonfinite_dimensions_are_rejected(self):
        for key, value in (("x", 0), ("y", 100), ("w", 0), ("h", 800), ("x", math.nan)):
            with self.subTest(key=key, value=value):
                data = scene()
                data["nodes"][0][key] = value
                with self.assertRaises(ValueError):
                    FIGURES.render_scene(data)
        with self.assertRaises(ValueError):
            FIGURES.render_scene({**scene(), "height": math.inf})

    def test_crossing_a_card_is_rejected(self):
        data = scene()
        data["edges"] = [{"points": [[40, 220], [350, 220]]}]
        with self.assertRaisesRegex(ValueError, "crosses node"):
            FIGURES.render_scene(data)

    def test_bad_edges_are_rejected(self):
        for points in ([[300, 220]], [[300, 220], [400, 240]],
                       [[300, 220], [300, 220]], [[300, 220], [1050, 220]]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                FIGURES.render_scene({**scene(), "edges": [{"points": points}]})

    def test_bad_bars_and_labels_are_rejected(self):
        for bar in ({"x": 40, "y": 130, "w": 900, "h": 600},
                    {"x": 40, "y": 130, "w": 40, "h": 40, "label": "放不下的长标签"}):
            with self.subTest(bar=bar), self.assertRaises(ValueError):
                FIGURES.render_scene({**scene(), "bars": [bar]})
        valid = {"x": 520, "y": 400, "text": "说明", "anchor": "middle"}
        for invalid in ({"anchor": "end"}, {"x": math.nan}, {"size": 1},
                        {"color": '" /><script/>'}, {"weight": "bold"}, {"x": 0}):
            label = {**deepcopy(valid), **invalid}
            with self.subTest(label=label), self.assertRaises(ValueError):
                FIGURES.render_scene({**scene(), "labels": [label]})


if __name__ == "__main__":
    unittest.main()
