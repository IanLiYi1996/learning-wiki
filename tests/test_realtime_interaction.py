"""Offline teaching, document and optional Jekyll regressions."""

from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from test_payments import Page, PRIVATE, markdown_links, normalized, prose_samples


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/deep-learning/realtime-interaction"
PREFIX = "wiki/topics/deep-learning/realtime-interaction/"
CHAPTERS = (
    "01-duplex-and-turn-taking.md", "02-streaming-codecs-and-rendering.md",
    "03-background-reasoning-and-tools.md", "04-training-and-distillation.md",
    "05-evaluation-and-safety.md", "06-higgs-realtime-duplex.md",
)
FILES = ("README.md",) + CHAPTERS + ("lab.md", "glossary.md", "sources.md")
ROUTES = {name: PREFIX + name.replace("README.md", "index.html").replace(".md", ".html")
          for name in FILES}
SITE = Path(os.environ.get("REALTIME_SITE", ROOT / "_site")).resolve()
# Exact public snapshots inspected during source research, never arbitrary hashes.
PUBLIC_VERSIONS = {
    "e6a55d2722a65870ef52a6c9f6ecfc0e90f38362": "github.com/kyutai-labs/moshi",
    "3e799c45a045256f47d5f1c9cda90157e2d2ec9e":
        "github.com/DanielLin94144/Full-Duplex-Bench",
    "033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f":
        "github.com/sierra-research/tau2-bench",
}
spec = importlib.util.spec_from_file_location(
    "realtime_interaction_lab", ROOT / "scripts/realtime_interaction_lab.py")
LAB = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = LAB
spec.loader.exec_module(LAB)


def without_verified_revisions(text):
    """Permit only the inspected public provenance, not unknown digests."""
    for revision, repository in PUBLIC_VERSIONS.items():
        text = text.replace(f"`{revision}`", "`public-revision`")
        text = text.replace(f"https://{repository}/blob/{revision}/",
                            f"https://{repository}/blob/public-revision/")
        api_repository = repository.removeprefix("github.com/")
        text = text.replace(f"https://api.github.com/repos/{api_repository}/commits/{revision}",
                            f"https://api.github.com/repos/{api_repository}/commits/public-revision")
    return text


def readable_samples(text):
    text = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]*\]", r"\1", text)
    lines = []
    math = False
    for line in text.splitlines():
        if line.strip() == "$$":
            math = not math
            continue
        if not math and "$" not in line and not re.match(r"^\[[^\]]+\]:", line):
            lines.append(line)
    return prose_samples("\n".join(lines))


class LabTests(unittest.TestCase):
    def test_example_budget_has_distinct_streams(self):
        budget = LAB.examples()["budget"]
        self.assertEqual(budget["chunks_per_minute"], 375)
        self.assertEqual(budget["units_per_minute"],
                         {"audio_in": 750, "audio_out": 1125,
                          "video_in": 750, "face_out": 750})
        self.assertEqual(budget["total_units_per_minute"], 3375)
        self.assertEqual(budget["recent_window_units"], 13500)

    def test_budget_supports_disabled_streams_and_fractional_rates(self):
        budget = LAB.stream_budget(170, 1, 0, 6, 0, 0, 2.5)
        self.assertAlmostEqual(budget["total_units_per_minute"], 60000 / 170)
        self.assertAlmostEqual(budget["recent_window_units"], 150000 / 170)
        self.assertEqual(LAB.stream_budget(160, 0, 0, 1, 0, 0, 1)
                         ["total_units_per_minute"], 0)

    def test_budget_rejects_invalid_and_overflowing_inputs(self):
        arguments = [160, 2, 3, 5, 10, 2, 4]
        bad = {
            0: [0, -1, True, "160", float("nan"), float("inf"), 10**1000],
            1: [-1, True, float("nan")],
            2: [-1, False, float("inf")],
            3: [0, -1, 1.5, True, 10**1000],
            4: [-1, True, float("inf")],
            5: [-1, False],
            6: [0, -1, True, float("inf")],
        }
        for index, values in bad.items():
            for value in values:
                args = arguments.copy()
                args[index] = value
                with self.subTest(index=index, value=str(value)[:16]):
                    with self.assertRaises(ValueError):
                        LAB.stream_budget(*args)
        for args in ([5e-324, 2, 3, 5, 10, 2, 4],
                     [160, 1e308, 3, 5, 10, 2, 4],
                     [160, 2, 3, 5, 10, 2, 1e308]):
            with self.assertRaises(ValueError):
                LAB.stream_budget(*args)

    def test_latency_and_conditional_block_wait_are_separate(self):
        output = LAB.examples()
        self.assertEqual(output["latency"]["serial_total_ms"], 250)
        self.assertEqual(output["alignment"],
                         {"mean_wait_ms": 80, "supremum_wait_ms": 160})
        self.assertEqual(LAB.serial_latency({"disabled": 0})["serial_total_ms"], 0)

    def test_latency_requires_named_finite_nonnegative_components(self):
        for bad in ({}, [], {"": 1}, {1: 1}, {"x": True}, {"x": -1},
                    {"x": float("nan")}, {"x": 1e308, "y": 1e308}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                LAB.serial_latency(bad)
        for bad in (0, -1, True, float("inf")):
            with self.assertRaises(ValueError):
                LAB.block_alignment(bad)

    def test_result_admission_matches_documented_examples(self):
        self.assertEqual([row["gate"] for row in LAB.examples()["results"]],
                         ["old-intent", "not-final", "admit", "wrong-task", "expired"])

    def test_result_age_boundary_and_failed_status(self):
        result = LAB.ToolResult("x", 1, "final", 1, "ok")
        self.assertEqual(LAB.result_gate(result, "x", 1, 2, 1), "admit")
        self.assertEqual(LAB.result_gate(result, "x", 1, 2.001, 1), "expired")
        failed = LAB.ToolResult("x", 1, "failed", 1, "")
        self.assertEqual(LAB.result_gate(failed, "x", 1, 2, 1), "not-final")
        self.assertEqual(LAB.result_gate(result, "x", 1, 1, 0), "admit")
        self.assertEqual(result.payload, "ok")  # admission never mutates the record

    def test_tool_records_and_current_context_are_typed(self):
        for args in (("", 1, "final", 1, "x"), ("x", True, "final", 1, "x"),
                     ("x", 0, "final", 1, "x"), ("x", 1, "unknown", 1, "x"),
                     ("x", 1, "final", -1, "x"), ("x", 1, "final", 1, None),
                     ("x", 1, "final", float("nan"), "x")):
            with self.assertRaises(ValueError):
                LAB.ToolResult(*args)
        result = LAB.ToolResult("x", 1, "final", 1, "")
        for args in ((None, "x", 1, 2, 1), (result, "", 1, 2, 1),
                     (result, "x", True, 2, 1), (result, "x", 1, .5, 1),
                     (result, "x", 1, 2, -1), (result, "x", 1, True, 1)):
            with self.assertRaises(ValueError):
                LAB.result_gate(*args)

    def test_one_to_one_timing_penalizes_duplicates_and_extra_output(self):
        score = LAB.examples()["timing"]
        self.assertEqual([score[key] for key in ("true_positives", "false_positives",
                                                "false_negatives")], [2, 2, 1])
        self.assertEqual(score["precision"], .5)
        self.assertEqual(score["recall"], 2 / 3)
        self.assertEqual(score["f1"], 4 / 7)
        self.assertEqual(LAB.timing_score([(1, 2), (5, 6), (9, 10)],
                                         [12, 5.5, 1.6, 1.5]), score)

    def test_timing_closed_boundaries_empty_output_and_invalid_inputs(self):
        self.assertEqual(LAB.timing_score([(1, 2)], [1, 2])["false_positives"], 1)
        self.assertEqual(LAB.timing_score([(1, 2)], [])["f1"], 0)
        self.assertEqual(LAB.timing_score([(1, 1)], [1])["f1"], 1)
        for windows, predictions in (
            ([], []), ([(2, 1)], []), ([(1, 2), (2, 3)], []),
            ([(1, 3), (2, 4)], []), ([(0, float("inf"))], []),
            ([(True, 2)], []), ([(1,)], []), ([(1, 2)], [-1]),
            ([(1, 2)], [float("nan")]), ([(1, 2)], [True]),
        ):
            with self.assertRaises(ValueError):
                LAB.timing_score(windows, predictions)

    def test_all_examples_export_finite_json(self):
        self.assertIsInstance(json.loads(json.dumps(LAB.examples(), allow_nan=False)), dict)


class DocumentTests(unittest.TestCase):
    def test_ten_complete_pages_and_separate_teaching_from_measurement(self):
        self.assertEqual({file.name for file in TOPIC.iterdir()}, set(FILES))
        for name in FILES:
            text = (TOPIC / name).read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# "), name)
            self.assertIn("2026-11-09", text, name)
            self.assertGreater(len(text), 900, name)
        case = (TOPIC / CHAPTERS[-1]).read_text(encoding="utf-8")
        for boundary in ("2026-11-05", "160 ms", "45B", "2T", "waitlist", "设计目标",
                         "未公开", "不是我们测得", "不应直接当作相同"):
            self.assertIn(boundary, case)
        training = (TOPIC / CHAPTERS[3]).read_text(encoding="utf-8")
        self.assertIn("不是 Boson MOPD", training)
        self.assertIn("不自动等于", training)

    def test_relative_links_and_explicit_anchors_resolve(self):
        for name in FILES:
            file = TOPIC / name
            text = file.read_text(encoding="utf-8")
            ids = Page(text).ids
            self.assertEqual(len(ids), len(set(ids)), name)
            for _, target in markdown_links(text):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    self.assertIn(parsed.scheme, ("https", "http"))
                    continue
                local = (file.parent / unquote(parsed.path)).resolve() \
                    if parsed.path else file
                self.assertTrue(local.is_relative_to(ROOT), target)
                self.assertTrue(local.is_file(), f"{name}: {target}")
                if parsed.fragment:
                    self.assertIn(unquote(parsed.fragment),
                                  Page(local.read_text(encoding="utf-8")).ids)

    def test_sources_include_verified_versions_and_no_unrelated_arxiv_links(self):
        source = (TOPIC / "sources.md").read_text(encoding="utf-8")
        for identifier in ("2410.00037v2", "2507.23159v4", "2603.13686v1",
                           "2507.09313v2", "2402.03300v3", "2306.13649v3",
                           "2606.30406v1"):
            self.assertIn(identifier, source)
        for revision, repository in PUBLIC_VERSIONS.items():
            self.assertIn(f"https://{repository}/blob/{revision}/", source)
        for name in FILES:
            text = (TOPIC / name).read_text(encoding="utf-8")
            self.assertNotIn("2503.04721", text)  # unrelated paper, not FDB
        self.assertIn('id="boson"', source)
        self.assertIn('id="mopd"', source)
        self.assertIn("不是 Boson", source)

    def test_public_provenance_without_private_material(self):
        for name in FILES:
            text = without_verified_revisions((TOPIC / name).read_text(encoding="utf-8"))
            for label, pattern in PRIVATE.items():
                with self.subTest(page=name, privacy=label):
                    self.assertNotRegex(text, re.compile(pattern, re.I))
        unknown = "https://github.com/kyutai-labs/moshi/blob/" + "f" * 40 + "/README.md"
        self.assertRegex(without_verified_revisions(unknown),
                         PRIVATE["attachment digest"])

    def test_navigation_and_three_entrypoints_include_new_reader(self):
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        actual = set(re.findall(r"(?m)^\s+url:\s*(/wiki/topics/deep-learning/"
                                r"realtime-interaction/\S*)\s*$", navigation))
        self.assertEqual(actual, {"/" + route.replace("index.html", "")
                                  for route in ROUTES.values()})
        for path, target in (
            (ROOT / "README.md", "wiki/topics/deep-learning/realtime-interaction/README.md"),
            (ROOT / "wiki/topics/README.md", "deep-learning/realtime-interaction/README.md"),
            (ROOT / "wiki/topics/deep-learning/README.md", "realtime-interaction/README.md"),
        ):
            self.assertIn("](" + target + ")", path.read_text(encoding="utf-8"))
        self.assertIn("group: 实时全双工交互", navigation)

    def test_lab_numbers_and_source_code_links_match_script(self):
        text = (TOPIC / "lab.md").read_text(encoding="utf-8")
        for number in ("3375", "13,500", "250 ms", "80 ms", "4/7", "TP=2、FP=2、FN=1"):
            self.assertIn(number, text)
        for path in ("scripts/realtime_interaction_lab.py",
                     "tests/test_realtime_interaction.py"):
            self.assertTrue((ROOT / path).is_file())
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + path, text)
        self.assertIn("不是", text)
        self.assertIn("不采集音视频", text)


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll or set REALTIME_SITE")
class SiteTests(unittest.TestCase):
    def test_all_pages_are_searchable_readable_and_locally_linked(self):
        records = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        for name, route in ROUTES.items():
            with self.subTest(page=name):
                path = SITE / route
                self.assertTrue(path.is_file(), route)
                page = Page(path.read_text(encoding="utf-8"))
                self.assertEqual(page.article_count, 1)
                self.assertEqual(len(page.ids), len(set(page.ids)), route)
                source = (TOPIC / name).read_text(encoding="utf-8")
                self.assertTrue(set(Page(source).ids).issubset(page.article_ids))
                canonical = page.base + "/" + route.replace("index.html", "")
                found = [record for record in records if record["url"] == canonical]
                self.assertEqual(len(found), 1, route)
                body = normalized("".join(page.text))
                samples = list(readable_samples(source))
                self.assertGreater(len(samples), 8, name)
                for sample in samples:
                    self.assertIn(sample, body, f"Missing prose in {name}")
                    self.assertIn(sample, normalized(found[0]["text"]),
                                  f"Missing search prose in {name}")
                self.assertIn(page.base + "/" + PREFIX, page.sidebar_links)
                for target in page.article_links:
                    parsed = urlsplit(target)
                    if parsed.scheme or parsed.netloc:
                        continue
                    resolved = urlsplit(urljoin(canonical, target))
                    self.assertTrue(resolved.path.startswith(page.base + "/"), target)
                    local = (SITE / unquote(resolved.path[len(page.base) + 1:])).resolve()
                    if resolved.path.endswith("/"):
                        local /= "index.html"
                    self.assertTrue(local.is_relative_to(SITE), target)
                    self.assertTrue(local.is_file(), f"{name}: {target}")
                    self.assertNotEqual(local.suffix, ".md", target)
                    if resolved.fragment:
                        self.assertIn(unquote(resolved.fragment),
                                      Page(local.read_text(encoding="utf-8")).ids, target)

    def test_reader_has_one_active_sidebar_leaf_and_math_blocks(self):
        for name, route in ROUTES.items():
            text = (SITE / route).read_text(encoding="utf-8")
            page = Page(text)
            selected = page.base + "/" + route.replace("index.html", "")
            self.assertIn(f'href="{selected}" aria-current="page"', text)
        for name in (CHAPTERS[1], CHAPTERS[2], CHAPTERS[3], CHAPTERS[4], CHAPTERS[5]):
            text = (SITE / ROUTES[name]).read_text(encoding="utf-8")
            self.assertTrue('type="math/tex; mode=display"' in text or "\\[" in text,
                            f"Missing MathJax display-math markup: {name}")
        self.assertFalse((SITE / "scripts/realtime_interaction_lab.py").exists())
        self.assertFalse((SITE / "tests/test_realtime_interaction.py").exists())


if __name__ == "__main__":
    unittest.main()
