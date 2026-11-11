"""Offline memory/flow teaching examples, source contracts and built-site checks."""

from collections import Counter
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from test_payments import Page, PRIVATE, markdown_links, normalized, prose_samples


ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "wiki/topics/agent-memory"
CONTINUOUS = ROOT / "wiki/topics/deep-learning/continuous-language-models"
MEMORY_CHAPTERS = (
    "01-memory-and-state.md", "02-write-manage-read.md",
    "03-representations-and-retrieval.md", "04-evaluation-and-ablation.md",
    "05-safety-and-governance.md", "06-anthropic-components.md",
)
CONTINUOUS_CHAPTERS = (
    "01-discrete-text-continuous-state.md", "02-representations-and-decoders.md",
    "03-diffusion-and-flow-matching.md", "04-training-schedules-and-self-conditioning.md",
    "05-sampling-guidance-and-commitment.md", "06-flow-maps-and-few-step-generation.md",
    "07-scaling-and-evaluation.md", "08-safety-and-research-roadmap.md",
)
MEMORY_FILES = ("README.md",) + MEMORY_CHAPTERS + ("glossary.md", "lab.md", "sources.md")
CONTINUOUS_FILES = ("README.md",) + CONTINUOUS_CHAPTERS + ("glossary.md", "lab.md", "sources.md")
MEMORY_ROUTES = {name: "wiki/topics/agent-memory/" +
                 name.replace("README.md", "index.html").replace(".md", ".html")
                 for name in MEMORY_FILES}
CONTINUOUS_ROUTES = {name: "wiki/topics/deep-learning/continuous-language-models/" +
                     name.replace("README.md", "index.html").replace(".md", ".html")
                     for name in CONTINUOUS_FILES}
SITE = Path(os.environ.get("MEMORY_FLOW_SITE", ROOT / "_site")).resolve()
SURVEY_ID = "2611.continuous-diffusion-flow-language-models"
PUBLIC_REVISION = "bbe5f932364c8f9097516979ddc0e69bb2a99709"
PUBLIC_REPOSITORY = "github.com/sophtang/Awesome-Continuous-Language-Models"
PUBLIC_CONFERENCE_URLS = (
    "https://proceedings.neurips.cc/paper_files/paper/2025/hash/"
    "42a97bbd9844d2bf68596730af80bcdf-Abstract-Conference.html",
    "https://papers.neurips.cc/paper_files/paper/2025/file/"
    "42a97bbd9844d2bf68596730af80bcdf-Paper-Conference.pdf",
)
spec = importlib.util.spec_from_file_location("memory_and_flow_lab",
                                            ROOT / "scripts/memory_and_flow_lab.py")
LAB = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = LAB
spec.loader.exec_module(LAB)


def public_study_text(text):
    readme = f"https://{PUBLIC_REPOSITORY}/blob/{PUBLIC_REVISION}/README.md"
    text = re.sub(re.escape(readme) + r'(?=[)\s"<>]|$)',
                  f"https://{PUBLIC_REPOSITORY}/blob/public-revision/README.md", text)
    for url in PUBLIC_CONFERENCE_URLS:
        text = text.replace(url, "https://proceedings.neurips.cc/public-paper")
    return text


def readable_samples(text):
    text = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]*\]", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)
    lines, math_block = [], False
    for line in text.splitlines():
        if line.strip() == "$$":
            math_block = not math_block
            continue
        if not math_block and "$" not in line and not re.match(r"^\[[^\]]+\]:", line):
            lines.append(line)
    return prose_samples("\n".join(lines))


class MemoryLabTests(unittest.TestCase):
    def test_admission_examples_and_declared_boundary(self):
        rows = LAB.memory_examples()["admission"]
        self.assertEqual([row["gate"] for row in rows],
                         ["admit", "wrong-version", "unverified", "expired", "wrong-scope"])
        note = LAB.MemoryNote("m", "t", "p", "s", "v", 1, 2)
        self.assertEqual(LAB.memory_gate(note, "t", "p", {"s": "v"}, 1), "admit")
        self.assertEqual(LAB.memory_gate(note, "t", "p", {"s": "v"}, 2), "expired")
        self.assertEqual(LAB.memory_gate(note, "t", "p", {}, 1), "unknown-source")
        revoked = LAB.MemoryNote("m", "t", "p", "s", "v", 1, 2, "revoked")
        self.assertEqual(LAB.memory_gate(revoked, "t", "p", {"s": "v"}, 1), "revoked")

    def test_note_fields_and_context_reject_invalid_inputs(self):
        base = ["m", "t", "p", "s", "v", 1, 2]
        for index, values in (
            (0, ["", False]), (5, [-1, True, float("nan"), 10**1000]),
            (6, [.5, float("inf")]),
        ):
            for value in values:
                args = base.copy()
                args[index] = value
                with self.assertRaises(ValueError):
                    LAB.MemoryNote(*args)
        with self.assertRaises(ValueError):
            LAB.MemoryNote(*base, "unchecked-state")
        note = LAB.MemoryNote(*base)
        for args in ((None, "t", "p", {}, 1), (note, "", "p", {}, 1),
                     (note, "t", "p", None, 1), (note, "t", "p", {"s": True}, 1),
                     (note, "t", "p", {}, .5), (note, "t", "p", {}, True)):
            with self.assertRaises(ValueError):
                LAB.memory_gate(*args)

    def test_invalidation_marks_descendants_and_does_not_mutate_graph(self):
        graph = {"source": [], "note": ["source"], "report": ["note"], "other": []}
        before = json.dumps(graph, sort_keys=True)
        self.assertEqual(LAB.invalidate(["source"], graph), ("note", "report", "source"))
        self.assertEqual(LAB.invalidate(["note"], graph), ("note", "report"))
        self.assertEqual(json.dumps(graph, sort_keys=True), before)

    def test_invalidation_rejects_cycles_dangling_and_ambiguous_records(self):
        for changed, graph in (
            (["a"], {"a": ["a"]}), (["a"], {"a": ["b"], "b": ["a"]}),
            (["a"], {"a": ["missing"]}), (["a"], {"a": (), "b": ["a", "a"]}),
            (["unknown"], {"a": ()}), ([], {"a": ()}), ("a", {"a": ()}),
            ([False], {"a": ()}), (["a"], {"a": "not-a-parent-list"}),
        ):
            with self.assertRaises(ValueError):
                LAB.invalidate(changed, graph)
        # No recursive DFS limit for a long, still synthetic, acyclic chain.
        graph = {str(i): [str(i - 1)] if i else [] for i in range(1100)}
        self.assertEqual(len(LAB.invalidate(["0"], graph)), 1100)

    def test_cas_preserves_facts_and_rejects_stale_replacement(self):
        example = LAB.memory_examples()["concurrency"]
        self.assertFalse(example["stale_write"]["accepted"])
        self.assertEqual(set(example["naive_last_write_facts"]), {"alpha", "gamma"})
        self.assertEqual(set(example["retry"]["facts"]), {"alpha", "beta", "gamma"})
        facts = {"x": "old"}
        result = LAB.cas_write(0, facts, 0, {"x": "new"})
        result["facts"]["x"] = "external mutation"
        self.assertEqual(facts, {"x": "old"})

    def test_cas_rejects_wrong_types_without_real_storage(self):
        for args in ((True, {}, 0, {}), (0, {}, -1, {}), (0, [], 0, {}),
                     (0, {"": "v"}, 0, {}), (0, {}, 0, {"k": None})):
            with self.assertRaises(ValueError):
                LAB.cas_write(*args)

    def test_break_even_and_no_finite_payback(self):
        self.assertEqual(LAB.break_even(120, 10, 7, 1),
                         {"net_saving_per_query": 2, "break_even_queries": 60})
        self.assertIsNone(LAB.break_even(120, 8, 7, 1)["break_even_queries"])
        self.assertIsNone(LAB.break_even(0, 7, 7, 1)["break_even_queries"])
        self.assertEqual(LAB.break_even(0, 8, 7, 1)["break_even_queries"], 1)
        self.assertEqual(LAB.break_even(1, 3, 1, 0)["break_even_queries"], 1)

    def test_cost_validation_and_overflow(self):
        for args in ((-1, 10, 7, 1), (120, True, 7, 1), (120, 10, float("nan"), 1),
                     (120, 10, 1e308, 1e308), (1e308, 1e-308, 0, 0)):
            with self.assertRaises(ValueError):
                LAB.break_even(*args)


class FlowLabTests(unittest.TestCase):
    def test_correct_marginals_still_lose_joint_dependencies(self):
        result = LAB.factorization_error(((.5, 0), (0, .5)))
        self.assertEqual(result["first_marginal"], (.5, .5))
        self.assertEqual(result["product"], ((.25, .25), (.25, .25)))
        self.assertEqual(result["invalid_mass"], .5)
        self.assertEqual(result["total_variation"], .5)
        independent = LAB.factorization_error(((.25, .25), (.25, .25)))
        self.assertEqual(independent["total_variation"], 0)

    def test_joint_shape_normalization_and_numerical_validation(self):
        for joint in (None, (), ((.5,), (.25, .25)), ((1.1, -.1),),
                      ((.2, .2),), ((True, 0),), ((float("inf"),),), (.5, .5)):
            with self.assertRaises(ValueError):
                LAB.factorization_error(joint)

    def test_solver_results_and_same_nfe_comparison(self):
        values = [LAB.integrate_linear(n) for n in (1, 2, 4)]
        self.assertEqual([row["approximation"] for row in values], [2, 2.25, 2.44140625])
        heun = LAB.integrate_linear(1, "heun")
        self.assertEqual(heun["approximation"], 2.5)
        self.assertEqual(heun["nfe"], values[1]["nfe"])
        self.assertLess(heun["absolute_error"], values[1]["absolute_error"])
        self.assertEqual(LAB.integrate_linear(1, duration=0)["approximation"], 1)

    def test_solver_declared_budget_invalid_modes_and_overflow(self):
        for args in ((0,), (True,), (10001,), (1, "unknown"),
                     (1, "euler", True), (1, "euler", 1, float("nan")),
                     (1, "euler", 1, -1), (1, "euler", 1, 1000),
                     (1, "heun", 1e308, 1)):
            with self.assertRaises(ValueError):
                LAB.integrate_linear(*args)

    def test_semigroup_alone_accepts_wrong_identity_map(self):
        result = LAB.map_contract()
        self.assertLess(result["exact_semigroup_error"], 1e-12)
        self.assertEqual(result["euler_semigroup_error"], .25)
        self.assertEqual(result["identity_semigroup_error"], 0)
        self.assertEqual(result["identity_velocity_error"], 1)
        for args in ((0, .7, .5), (-1, .5, 1), (0, .5, 2),
                     (True, .5, 1), (0, .5, 1, 1e308)):
            with self.assertRaises(ValueError):
                LAB.map_contract(*args)

    def test_probability_guidance_may_leave_simplex(self):
        result = LAB.guidance_targets((.9, .1), (.4, .6), 2)
        self.assertAlmostEqual(result["raw"][0], -.1)
        self.assertFalse(result["valid_probability_target"])
        self.assertTrue(LAB.guidance_targets((.9, .1), (.4, .6), 1)
                        ["valid_probability_target"])
        for args in ((None, (.4, .6), 1), ((.9, .1), (.4, .3), 1),
                     ((1,), (.4, .6), 1), ((.9, .1), (.4, .6), True),
                     ((.9, .1), (.4, .6), -1)):
            with self.assertRaises(ValueError):
                LAB.guidance_targets(*args)

    def test_reference_gppl_and_entropy_are_different(self):
        repeat = LAB.binary_reference_stats("AAAAAA")
        alternate = LAB.binary_reference_stats("ABABAB")
        self.assertAlmostEqual(repeat["conditional_gppl"], 1 / .9)
        self.assertEqual(repeat["unigram_entropy"], 0)
        self.assertAlmostEqual(alternate["conditional_gppl"], 10)
        self.assertAlmostEqual(alternate["unigram_entropy"], math.log(2))
        for args in ((None,), ("A",), ("ABC",), ("AA", 0), ("AA", 1),
                     ("AA", True), ("AA", float("nan"))):
            with self.assertRaises(ValueError):
                LAB.binary_reference_stats(*args)

    def test_declared_dense_state_and_all_evaluation_counts(self):
        result = LAB.dense_state_budget(128, 50000, 64)
        self.assertEqual(result, {"one_hot_bytes": 25600000, "embedding_bytes": 32768,
                                  "binary_coordinates": 16, "binary_float_state_bytes": 8192})
        self.assertEqual(LAB.dense_state_budget(1, 1, 1)["binary_coordinates"], 0)
        self.assertEqual(LAB.evaluation_count(8, 2, 1), 17)
        for args in ((0, 2, 1), (1, True, 1), (1, 2, -1)):
            with self.assertRaises(ValueError):
                LAB.evaluation_count(*args)
        with self.assertRaises(ValueError):
            LAB.dense_state_budget(True, 50000, 64)

    def test_all_nine_demos_export_finite_json(self):
        result = {"memory": LAB.memory_examples(), "flow": LAB.flow_examples()}
        self.assertEqual(len(result["memory"]), 4)
        self.assertEqual(len(result["flow"]), 5)
        self.assertIsInstance(json.loads(json.dumps(result, allow_nan=False)), dict)


class DocumentTests(unittest.TestCase):
    def test_prose_samples_remove_inline_emphasis_not_visible_words(self):
        source = "旧标题 *A Practical Memory Injection Attack against LLM Agents* 与 **当前题名**。"
        self.assertEqual(list(readable_samples(source)),
                         ["旧标题 A Practical Memory Injection Attack against LLM Agents 与 当前题名。"])

    def test_twenty_two_complete_pages_and_no_source_placeholder(self):
        for topic, files in ((MEMORY, MEMORY_FILES), (CONTINUOUS, CONTINUOUS_FILES)):
            self.assertEqual({path.name for path in topic.iterdir()}, set(files))
            for filename in files:
                text = (topic / filename).read_text(encoding="utf-8")
                self.assertTrue(text.startswith("# "), filename)
                self.assertIn("2026-11-11", text, filename)
                self.assertGreater(len(text), 650, filename)
                self.assertNotRegex(text, r"TODO|TBD|待主任务|预期章节名|本侧车")

    def test_all_relative_links_and_explicit_anchors_resolve(self):
        for topic, files in ((MEMORY, MEMORY_FILES), (CONTINUOUS, CONTINUOUS_FILES)):
            for filename in files:
                source = topic / filename
                text = source.read_text(encoding="utf-8")
                self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)), filename)
                for image, target in markdown_links(text):
                    parts = urlsplit(target)
                    if parts.scheme or parts.netloc:
                        self.assertIn(parts.scheme, ("https", "http"))
                        self.assertFalse(image)
                        continue
                    local = (source.parent / unquote(parts.path)).resolve() \
                        if parts.path else source
                    self.assertTrue(local.is_relative_to(ROOT), target)
                    self.assertTrue(local.is_file(), f"{filename}: {target}")
                    if parts.fragment:
                        self.assertIn(unquote(parts.fragment),
                                      Page(local.read_text(encoding="utf-8")).ids)

    def test_sources_and_survey_identity_are_not_misrepresented(self):
        memory = (MEMORY / "sources.md").read_text(encoding="utf-8")
        for term in ("2026-11-06", "Lance Martin", "transcripts", "memory notes",
                     "memory representations", "injected context", "30 题", "40 题",
                     "41/57", "57/57", "mean reward", "不是第五层"):
            self.assertIn(term, memory)
        continuous = (CONTINUOUS / "sources.md").read_text(encoding="utf-8")
        for term in (SURVEY_ID, "alphaXiv", "2026-11-08", "2026-11-09",
                     "2026-11-02", "arxivId", "null", "37 页",
                     "2602.16813v3", "2602.12233v1", "2605.18530v3", "2605.10938v3"):
            self.assertIn(term, continuous)
        self.assertNotIn("https://arxiv.org/abs/" + SURVEY_ID, continuous)
        self.assertIn(PUBLIC_REVISION, continuous)
        self.assertIn("不是模型实验", (CONTINUOUS / CONTINUOUS_CHAPTERS[0])
                      .read_text(encoding="utf-8"))

    def test_no_private_provenance_and_only_exact_public_exemptions(self):
        for topic, files in ((MEMORY, MEMORY_FILES), (CONTINUOUS, CONTINUOUS_FILES)):
            for filename in files:
                text = public_study_text((topic / filename).read_text(encoding="utf-8"))
                for label, pattern in PRIVATE.items():
                    with self.subTest(page=filename, privacy=label):
                        self.assertNotRegex(text, re.compile(pattern, re.I))
        for value in (PUBLIC_REVISION, "https://example.com/" + PUBLIC_REVISION,
                      f"https://{PUBLIC_REPOSITORY}/blob/{PUBLIC_REVISION}/private.docx",
                      f"https://{PUBLIC_REPOSITORY}/blob/{PUBLIC_REVISION}/other.md",
                      f"https://{PUBLIC_REPOSITORY}/blob/{PUBLIC_REVISION}/README.md-private"):
            text = public_study_text(value)
            self.assertTrue(any(re.search(pattern, text, re.I) for pattern in PRIVATE.values()))

    def test_complete_navigation_and_entrypoints(self):
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        item_urls = Counter(re.findall(r"(?m)^ {8}url: (\S+)$", navigation))
        for routes in (MEMORY_ROUTES, CONTINUOUS_ROUTES):
            for route in routes.values():
                self.assertEqual(item_urls["/" + route.replace("index.html", "")], 1)
        for file in (ROOT / "README.md", ROOT / "wiki/topics/README.md"):
            text = file.read_text(encoding="utf-8")
            self.assertIn("agent-memory/README.md", text)
            self.assertIn("continuous-language-models/README.md", text)
        self.assertIn("continuous-language-models/README.md",
                      (ROOT / "wiki/topics/deep-learning/README.md").read_text(encoding="utf-8"))
        self.assertIn("group: 扩散与生成模型", navigation)
        self.assertNotIn("group: 扩散与视觉生成", navigation)

    def test_lab_numeric_claims_and_free_execution_contracts(self):
        memory = (MEMORY / "lab.md").read_text(encoding="utf-8")
        for term in ("60 题", "wrong-version", "CAS", "不会", "合成", "不访问网络"):
            self.assertIn(term, memory)
        flow = (CONTINUOUS / "lab.md").read_text(encoding="utf-8")
        for term in ("2.44140625", "0.25", "(-0.1,1.1)", "17", "25,600,000",
                     "32,768", "8,192", "不是 GPT-2"):
            self.assertIn(term, flow)
        for text in (memory, flow):
            self.assertIn("scripts/memory_and_flow_lab.py", text)
            self.assertIn("tests/test_memory_and_flow_studies.py", text)


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll or set MEMORY_FLOW_SITE")
class SiteTests(unittest.TestCase):
    def test_all_new_pages_render_search_and_link_without_markdown_leaks(self):
        records = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        for topic, routes in ((MEMORY, MEMORY_ROUTES), (CONTINUOUS, CONTINUOUS_ROUTES)):
            for filename, route in routes.items():
                with self.subTest(page=filename):
                    self.assertTrue((SITE / route).is_file(), route)
                    built = (SITE / route).read_text(encoding="utf-8")
                    page = Page(built)
                    self.assertEqual(page.article_count, 1)
                    self.assertEqual(len(page.ids), len(set(page.ids)), route)
                    canonical = page.base + "/" + route.replace("index.html", "")
                    selected = [record for record in records if record["url"] == canonical]
                    self.assertEqual(len(selected), 1, route)
                    source = (topic / filename).read_text(encoding="utf-8")
                    self.assertEqual(selected[0]["title"], source.splitlines()[0][2:])
                    body = normalized("".join(page.text))
                    for sample in readable_samples(source):
                        self.assertTrue(sample in body, f"Missing prose in {filename}: {sample[:80]}")
                        self.assertTrue(sample in normalized(selected[0]["text"]),
                                        f"Missing search prose in {filename}: {sample[:80]}")
                    self.assertIn(f'href="{canonical}" aria-current="page"', built)
                    for target in page.article_links:
                        parts = urlsplit(target)
                        if parts.scheme or parts.netloc:
                            continue
                        resolved = urlsplit(urljoin(canonical, target))
                        self.assertTrue(resolved.path.startswith(page.base + "/"), target)
                        local = (SITE / unquote(resolved.path[len(page.base) + 1:])).resolve()
                        if resolved.path.endswith("/"):
                            local /= "index.html"
                        self.assertTrue(local.is_relative_to(SITE), target)
                        self.assertTrue(local.is_file(), f"{filename}: {target}")
                        self.assertNotEqual(local.suffix, ".md")
                        if resolved.fragment:
                            self.assertIn(unquote(resolved.fragment),
                                          Page(local.read_text(encoding="utf-8")).ids)

    def test_math_and_script_exclusion_in_frozen_build(self):
        for route in (MEMORY_ROUTES[MEMORY_CHAPTERS[3]],
                      CONTINUOUS_ROUTES[CONTINUOUS_CHAPTERS[2]],
                      CONTINUOUS_ROUTES[CONTINUOUS_CHAPTERS[5]]):
            text = (SITE / route).read_text(encoding="utf-8")
            self.assertTrue("\\[" in text or 'type="math/tex; mode=display"' in text)
        self.assertFalse((SITE / "scripts/memory_and_flow_lab.py").exists())
        self.assertFalse((SITE / "tests/test_memory_and_flow_studies.py").exists())


if __name__ == "__main__":
    unittest.main()
