"""Offline source, worked-example, navigation and build checks for MoE/RLCR."""

from collections import Counter
import json
import math
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

import test_deep_learning as dl
from test_agentic_study import study_samples
from test_payments import Page, markdown_links, normalized
from test_training_recipes import GROUPS, GroupedPage


def documents():
    return {
        name: (dl.TOPIC / name).read_text(encoding="utf-8")
        for name in dl.MOE_SWARM_FILES
    }


class MoESwarmSourceTests(dl.DeepLearningChecks):
    def test_five_dated_public_pages_and_complete_navigation(self):
        docs = documents()
        self.assertEqual(len(docs), 5)
        nav = (dl.ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        hub = docs[dl.MOE_SWARM_FILES[0]]
        for name, text in docs.items():
            with self.subTest(name=name):
                self.assertRegex(text, r"\A# ")
                self.assertIn("2026-11-09", text)
                self.assertGreater(len(text), 1400)
                self.assertNotRegex(text, r"TODO|TBD|待主任务|待主 agent")
                self.assert_public_study(text, name)
                route = "/" + dl.MOE_SWARM_ROUTES[name].replace("index.html", "")
                self.assertEqual(nav.count("url: " + route + "\n"), 1)
                if not name.endswith("README.md"):
                    self.assertIn(Path(name).name, hub)
        for filename in ("README.md", "wiki/topics/README.md",
                         "wiki/topics/deep-learning/README.md",
                         "wiki/topics/deep-learning/training/README.md"):
            self.assertIn("moe-and-swarms/README.md",
                          (dl.ROOT / filename).read_text(encoding="utf-8"))

    def test_local_links_unique_anchors_and_https_sources(self):
        for name, text in documents().items():
            with self.subTest(name=name):
                self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
                for _, target in markdown_links(text):
                    parts = urlsplit(target)
                    if parts.scheme or parts.netloc:
                        self.assertEqual(parts.scheme, "https", target)
                        continue
                    path = ((dl.TOPIC / name).parent / unquote(parts.path)).resolve() \
                        if parts.path else dl.TOPIC / name
                    self.assertTrue(path.is_relative_to(dl.ROOT), target)
                    self.assertTrue(path.is_file(), f"{name}: {target}")
                    if parts.fragment:
                        self.assertIn(unquote(parts.fragment),
                                      Page(path.read_text(encoding="utf-8")).ids)

    def test_mechanisms_and_explicit_evidence_boundaries(self):
        docs = documents()
        moe = docs[dl.MOE_SWARM_FILES[1]]
        for phrase in ("Top-1", "总参数", "激活参数", "MaxVio",
                       "capacity factor", "z-loss", "dropless",
                       "EP", "R3", "GSPO", "不是完整 FLOPs 公式"):
            self.assertIn(phrase, moe)
        swarm = docs[dl.MOE_SWARM_FILES[2]]
        for phrase in ("共享 policy", "flat collective advantage", "Anytime-return",
                       "不是技术报告训练 loss 的完整复刻", "截止时间不是连续的提速奖励",
                       "4 倍", "2.4 小时", "1.7 小时", "1.8 小时", "CISPO",
                       "derived latency", "不是已经在本地实测"):
            self.assertIn(phrase, swarm)
        comparison = docs[dl.MOE_SWARM_FILES[3]]
        for phrase in ("matched", "通信", "关键路径", "总计算", "prompt",
                       "消融", "不是两个源文的 benchmark 公式", "尚未运行真实模型",
                       "冻结 router", "expert assignments"):
            self.assertIn(phrase, comparison)
        for name in dl.MOE_SWARM_FILES[1:4]:
            self.assertIn("## 自测", docs[name])
            questions = docs[name].split("## 自测\n", 1)[1]
            self.assertEqual(re.findall(r"(?m)^([123])\. ", questions), ["1", "2", "3"])

    def test_sources_and_narrow_public_revision_exemptions(self):
        source = documents()[dl.MOE_SWARM_FILES[-1]]
        for target in ("huggingface.co/spaces/huggingface/moe-blogpost",
                       "gr.inc/blog/how-to-train-a-swarm", "gr.inc/avalonm1.pdf",
                       "2101.03961", "2401.06066", "2408.15664",
                       "2412.19437", "2510.11370", "2507.18071"):
            self.assertIn(target, source)
        for revision, repository in dl.MOE_SWARM_VERSIONS.items():
            self.assertIn(f"https://{repository}/blob/{revision}/", source)
            self.assert_public_study(
                f"https://{repository}/blob/{revision}/README.md", "public URL")
            for fixture in (revision, f"https://example.com/blob/{revision}/README.md",
                            f"https://{repository}/blob/{revision}/private.docx"):
                with self.subTest(fixture=fixture), self.assertRaises(AssertionError):
                    self.assert_public_study(fixture, "negative revision fixture")


class WorkedExampleTests(unittest.TestCase):
    def test_parameter_example_is_not_a_memory_estimate(self):
        common, layers, experts, expert_width, topk = 1, 10, 8, 0.1, 2
        total = common + layers * experts * expert_width
        active = common + layers * topk * expert_width
        self.assertAlmostEqual(total, 9)
        self.assertAlmostEqual(active, 3)
        text = documents()[dl.MOE_SWARM_FILES[1]]
        self.assertIn("总参数为 9 B", text)
        self.assertIn("约 3 B", text)

    def test_capacity_and_maxvio_use_assignment_counts(self):
        assignments = [8, 4, 2, 2]
        mean = sum(assignments) / len(assignments)
        self.assertEqual((max(assignments) - mean) / mean, 1)
        capacity = math.ceil(16 * 1 * 1 / 4)
        dropped = sum(max(0, count - capacity) for count in assignments)
        self.assertEqual(capacity, 4)
        self.assertEqual(dropped / sum(assignments), 0.25)
        self.assertIn("25\\%", documents()[dl.MOE_SWARM_FILES[1]])

    def test_top1_postselection_softmax_is_constant(self):
        for logit in (-8, 0, 8):
            weight = math.exp(logit) / math.exp(logit)
            self.assertEqual(weight, 1)

    def test_deadline_does_not_reward_equal_returns_before_cap(self):
        def score_at_deadline(completed_tests, finished_at, cap=20):
            return completed_tests if finished_at <= cap else 0

        self.assertEqual(score_at_deadline(10, 10), score_at_deadline(10, 18))
        self.assertEqual(score_at_deadline(6, 20), 6)
        self.assertEqual(score_at_deadline(8, 20), 8)

    def test_parallelism_does_not_remove_serial_work(self):
        speedup = 1 / (0.2 + 0.8 / 8)
        self.assertAlmostEqual(speedup, 10 / 3)
        self.assertLess(speedup, 8)
        self.assertIn("3.33", documents()[dl.MOE_SWARM_FILES[3]])


@unittest.skipUnless(dl.SITE.is_dir(), "Build Jekyll first")
class MoESwarmSiteTests(dl.DeepLearningChecks):
    page = dl.DeepLearningSiteTests.page
    local_target = dl.DeepLearningSiteTests.local_target

    def test_searchable_pages_prose_math_and_active_training_group(self):
        records = json.loads((dl.SITE / "search.json").read_text(encoding="utf-8"))
        docs = documents()
        base = self.page(dl.MOE_SWARM_ROUTES[dl.MOE_SWARM_FILES[0]]).base
        selected = [record for record in records if urlsplit(record["url"]).path.startswith(
            base + "/wiki/topics/deep-learning/training/moe-and-swarms/")]
        self.assertEqual(Counter(record["url"] for record in selected),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in dl.MOE_SWARM_ROUTES.values()))
        for name, route in dl.MOE_SWARM_ROUTES.items():
            with self.subTest(name=name):
                built = (dl.SITE / route).read_text(encoding="utf-8")
                page = self.page(route)
                self.assertEqual(page.article_count, 1)
                self.assertEqual(len(page.ids), len(set(page.ids)))
                record = next(record for record in selected if record["url"] ==
                              base + "/" + route.replace("index.html", ""))
                self.assertEqual(record["title"], docs[name].splitlines()[0][2:])
                for sample in study_samples(docs[name]):
                    self.assertIn(sample, normalized("".join(page.text)), name)
                    self.assertIn(sample, normalized(record["text"]), name)
                self.assert_public_study(built, route)
                for target in page.article_links:
                    local = self.local_target(route, target)
                    if local:
                        self.assertNotEqual(local.suffix, ".md", target)
                grouped = GroupedPage(built)
                navigation = (dl.ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
                topic = navigation.split("  - label: 深度学习专题\n", 1)[1].split(
                    "\n  - label:", 1)[0]
                expected_groups = list(dict.fromkeys(
                    re.findall(r"(?m)^\s+group: (.+)$", topic)))
                self.assertEqual([group["name"] for group in grouped.groups], expected_groups)
                self.assertEqual([group["name"] for group in grouped.groups if group["open"]],
                                 [GROUPS[0]])
                self.assertEqual(Counter(grouped.groups[0]["links"]),
                                 Counter(base + "/" + relative.replace("index.html", "")
                                         for relative in [*dl.TRAINING_ROUTES.values(),
                                                          *dl.AGENTIC_ROUTES.values(),
                                                          *dl.UNIFIED_ROUTES.values(),
                                                          *dl.MOE_SWARM_ROUTES.values()]))
                math_blocks = docs[name].splitlines().count("$$") // 2
                if math_blocks:
                    article = re.search(r"<article\b[^>]*>(.*?)</article>", built, re.S)[1]
                    # The site's MathJax 3 converter emits \[...\], not the
                    # legacy MathJax 2 script[type=math/tex] representation.
                    self.assertEqual(article.count(r"\["), math_blocks, name)
                    self.assertEqual(article.count(r"\]"), math_blocks, name)
                    self.assertTrue('id="MathJax-script"' in built, name)


if __name__ == "__main__":
    unittest.main()
