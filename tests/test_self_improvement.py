"""Offline RSI document, teaching-code, figure, and optional built-site checks."""

from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from test_payments import Page, PRIVATE, markdown_links


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/deep-learning/self-improvement"
PREFIX = "wiki/topics/deep-learning/self-improvement/"
CHAPTERS = (
    "concepts-and-foundations.md", "agent-evolution.md", "learning-and-weights.md",
    "algorithms-and-infrastructure.md", "ai-scientists.md", "industry-and-autoresearch.md",
    "evaluation-and-safety.md", "research-roadmap.md",
)
FILES = ("README.md",) + CHAPTERS + ("glossary.md", "lab.md", "sources.md")
ROUTES = {name: PREFIX + name.replace("README.md", "index.html").replace(".md", ".html")
          for name in FILES}
SITE = Path(os.environ.get("RSI_SITE", ROOT / "_site")).resolve()
spec = importlib.util.spec_from_file_location("self_improvement_lab",
                                            ROOT / "scripts/self_improvement_lab.py")
LAB = importlib.util.module_from_spec(spec)
# dataclasses resolves the defining module through sys.modules.
import sys
sys.modules[spec.name] = LAB
spec.loader.exec_module(LAB)


def manifests():
    return json.loads((ROOT / "scripts/figures/self-improvement.json").read_text(encoding="utf-8"))


class TeachingTests(unittest.TestCase):
    def test_more_candidates_do_not_change_generator(self):
        self.assertEqual(LAB.sampling_demo(), [
            {"budget": 2, "best_score": 0.2},
            {"budget": 4, "best_score": 0.4},
            {"budget": 8, "best_score": 0.8},
        ])

    def test_budget_and_score_contracts(self):
        for budget in (0, -1, 9, 1.5, True):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                LAB.best_of(LAB.SCORES, budget)
        for value in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                LAB.best_of((value,), 1)

    def test_four_way_values_and_equal_opportunity_budget(self):
        rows = LAB.transfer_demo()
        self.assertEqual([row["final_mean"] for row in rows], [8, 10, 7, 9])
        self.assertEqual([row["mean_gain"] for row in rows], [2, 4, 1, 3])
        self.assertTrue(all(row["candidate_evaluations_per_target"] == 4 for row in rows))
        self.assertTrue(all(row["final_mean"] >= row["initial_mean"] for row in rows))
        with self.assertRaises(ValueError):
            LAB.compare_improver(0, "forward", ())

    def test_invented_fast_scores_do_not_bypass_admission(self):
        result = LAB.gates_demo()
        self.assertEqual(result["winner"], "valid_fast")
        self.assertEqual([row["accepted"] for row in result["checks"]],
                         [True, False, False, False, False])

    def test_nonfinite_shape_latency_and_evaluator_contracts(self):
        bad = [
            LAB.Candidate("inf", (0.2, float("inf")), 1),
            LAB.Candidate("shape", (0.2,), 1),
            LAB.Candidate("zero", LAB.REFERENCE, 0),
            LAB.Candidate("negative", LAB.REFERENCE, -1),
            LAB.Candidate("time_nan", LAB.REFERENCE, float("nan")),
            LAB.Candidate("judge", LAB.REFERENCE, 1, evaluator="other"),
        ]
        self.assertTrue(all(not LAB.admission(candidate)[0] for candidate in bad))
        self.assertIsNone(LAB.select_candidate(bad)["winner"])
        self.assertIsNone(LAB.select_candidate([])["winner"])
        self.assertTrue(LAB.admission(
            LAB.Candidate("within_tolerance", (0.2000000001, 0.3999999999), 80))[0])

    def test_json_export_has_only_finite_serializable_records(self):
        self.assertTrue(json.loads(json.dumps(LAB.all_demos(), allow_nan=False)))


class DocumentTests(unittest.TestCase):
    def test_complete_readable_book_and_date_separation(self):
        for name in FILES:
            with self.subTest(name=name):
                text = (TOPIC / name).read_text(encoding="utf-8")
                self.assertTrue(text.startswith("# "))
                self.assertIn("2026-11-04", text)
                if name != "lab.md":
                    self.assertIn("2026-10-17", text)
                self.assertNotIn("```json", text)
        body = "".join((TOPIC / name).read_text(encoding="utf-8").split("\n[^", 1)[0]
                       for name in CHAPTERS)
        self.assertGreater(len(re.findall(r"[\u3400-\u9fff]", body)), 18000)

    def test_private_provenance_not_published(self):
        for name in FILES:
            text = (TOPIC / name).read_text(encoding="utf-8")
            for label, pattern in PRIVATE.items():
                with self.subTest(page=name, kind=label):
                    self.assertNotRegex(text.lower(), re.compile(pattern, re.I))

    def test_all_relative_markdown_links_resolve(self):
        for name in FILES:
            file = TOPIC / name
            # Footnote prose is not an ordinary [label]: URL definition.
            text = re.sub(r"(?m)^\[\^\d+\]:\s*", "",
                          file.read_text(encoding="utf-8"))
            for is_image, target in markdown_links(text):
                url = urlsplit(target)
                if url.scheme:
                    self.assertIn(url.scheme, ("https", "http"))
                    if is_image:
                        self.fail("Diagram hotlink")
                    continue
                if not url.path:
                    continue
                path = (file.parent / unquote(url.path)).resolve()
                self.assertTrue(path.is_relative_to(ROOT), target)
                self.assertTrue(path.is_file(), f"{name}: {target}")
        self.assertNotRegex("".join((TOPIC / name).read_text(encoding="utf-8")
                                   for name in FILES), r"\]\([^)]*rsi-detailed")

    def test_all_snapshot_reference_groups_remain_available(self):
        used = set()
        for name in CHAPTERS:
            text = (TOPIC / name).read_text(encoding="utf-8")
            body = re.sub(r"(?m)^\[\^\d+\]: .+$", "", text)
            references = set(re.findall(r"(?m)^\[\^(\d+)\]:", text))
            citations = set(re.findall(r"\[\^(\d+)\]", body))
            self.assertEqual(citations, references, name)
            used |= citations
        self.assertEqual(used, {str(n) for n in range(1, 50)})
        source = (TOPIC / "sources.md").read_text(encoding="utf-8")
        ids = re.findall(r'id="source-(\d+)"', source)
        self.assertEqual(set(ids), used)
        self.assertEqual(len(ids), 49)

    def test_mechanism_figures_are_local_retina_and_cover_all_chapters(self):
        figures = manifests()
        self.assertEqual(len(figures), 6)
        placements = [p for figure in figures for p in figure["placements"]]
        self.assertEqual(len(placements), 12)
        placed = {p["file"] for p in placements}
        self.assertTrue({PREFIX + name for name in CHAPTERS}.issubset(placed))
        for figure in figures:
            stem = ROOT / "wiki/topics/deep-learning/images" / figure["id"]
            tree = ET.parse(stem.with_suffix(".svg")).getroot()
            self.assertIsNotNone(tree.find("{http://www.w3.org/2000/svg}title"))
            self.assertIsNotNone(tree.find("{http://www.w3.org/2000/svg}desc"))
            width, height = struct.unpack(">II", stem.with_suffix(".png").read_bytes()[16:24])
            self.assertEqual((width, height),
                             (int(tree.attrib["width"]) * 2, int(tree.attrib["height"]) * 2))
            for placement in figure["placements"]:
                text = (ROOT / placement["file"]).read_text(encoding="utf-8")
                self.assertIn(f"/images/{figure['id']}.png)", text)
                self.assertIn("<!-- illustration: " + figure["id"] + "-", text)

    def test_entry_points_and_navigation_discoverability(self):
        self.assertIn(PREFIX + "README.md", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("deep-learning/self-improvement/README.md",
                      (ROOT / "wiki/topics/README.md").read_text(encoding="utf-8"))
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        for route in ROUTES.values():
            route = "/" + route.replace("/index.html", "/")
            self.assertIn("url: " + route, navigation)


@unittest.skipUnless(os.environ.get("RSI_SITE"), "Set RSI_SITE to an actual Jekyll build")
class BuiltSiteTests(unittest.TestCase):
    def test_all_pages_have_unique_ids_and_local_article_links(self):
        for name, route in ROUTES.items():
            with self.subTest(page=name):
                html = (SITE / route).read_text(encoding="utf-8")
                page = Page(html)
                self.assertEqual(page.article_count, 1)
                self.assertFalse([key for key, count in Counter(page.ids).items() if count > 1])
                self.assertTrue(any(level == "h1" for level, _ in page.headings))
                self.assertNotRegex(html, r"\[\^\d+\]|\]\([^)]*\.md")
                for target in page.article_links + [image["src"] for image in page.images]:
                    url = urlsplit(target)
                    if url.scheme or url.netloc:
                        continue
                    joined = urlsplit(urljoin("/learning-wiki/" + route, target))
                    path = unquote(joined.path).removeprefix("/learning-wiki/").lstrip("/")
                    candidate = SITE / path
                    if candidate.is_dir():
                        candidate /= "index.html"
                    self.assertTrue(candidate.is_file(), f"{route}: {target}")
                    if joined.fragment:
                        target_page = Page(candidate.read_text(encoding="utf-8"))
                        self.assertIn(unquote(joined.fragment), target_page.ids)

    def test_search_contains_exactly_twelve_study_routes(self):
        records = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        study = [row for row in records if "/"+PREFIX in row["url"]]
        self.assertEqual(len(study), len(FILES))
        self.assertEqual(len({row["url"] for row in study}), len(FILES))
        for row in study:
            self.assertTrue(row["title"] and row["text"])


if __name__ == "__main__":
    unittest.main()
