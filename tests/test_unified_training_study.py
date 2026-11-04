"""Offline public-content, figure, reading, and publication-scope regressions."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

import test_deep_learning as dl
from test_deep_learning import ROOT, SITE, TOPIC, DeepLearningChecks
from test_figures import FIGURES
from test_payments import ILLUSTRATION, Page, markdown_links, normalized
from test_training_recipes import GROUPS, GroupedPage, samples


COUNTS = (1, 1, 2, 1, 2, 1, 1, 1, 0)


def docs():
    return {name: (TOPIC / name).read_text() for name in dl.UNIFIED_FILES}


class UnifiedSourceTests(DeepLearningChecks):
    def test_nine_complete_public_pages_and_self_tests(self):
        self.assertEqual(len(dl.UNIFIED_FILES), 9)
        self.assertEqual({p.relative_to(TOPIC).as_posix()
                          for p in (TOPIC / "training/unified-training").rglob("*") if p.is_file()},
                         set(dl.UNIFIED_FILES))
        for name, text in docs().items():
            self.assertRegex(text, r"\A# ")
            self.assertIn("2026-11-04", text)
            self.assertGreater(len(ILLUSTRATION.sub("", text)), 1000, name)
            self.assert_public_study(text, name)
            self.assertNotRegex(text, r"TODO|TBD|主代理|待主任务|后续插入|```mermaid")
            self.assertGreaterEqual(len(re.findall(r"(?m)^## ", text)), 4, name)
            self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
        for name in dl.UNIFIED_FILES[1:6]:
            self.assertIn("自测与答案", docs()[name])

    def test_local_links_and_explicit_anchors(self):
        for name, text in docs().items():
            for target in [url for _, url in markdown_links(text)] + Page(text).links:
                part = urlsplit(target)
                if part.scheme or part.netloc:
                    self.assertNotEqual(part.scheme, "http")
                    continue
                path = ((TOPIC / name).parent / unquote(part.path)).resolve() \
                    if part.path else TOPIC / name
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(), f"{name}: {target}")
                if part.fragment:
                    self.assertIn(unquote(part.fragment), Page(path.read_text()).ids)

    def test_fixed_revision_exemption_does_not_allow_unattributed_hashes(self):
        revision = next(iter(dl.UNIFIED_VERSIONS))
        self.assertIn(revision, docs()["training/unified-training/sources.md"])
        self.assert_public_study(
            f"https://github.com/yudasong/unified-training/blob/{revision}/README.md", "source")
        for value in (revision, f"https://unknown.invalid/blob/{revision}/README.md",
                      f"https://github.com/yudasong/unified-training/blob/{revision}/secret.docx"):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                self.assert_public_study(value, "fixture")

    def test_targets_finite_samples_masks_async_and_budget_boundaries(self):
        required = {
            "likelihood-and-targets.md": ("保持固定", "0.75", "另一生成器", "不等于当前策略"),
            "maxrl-and-finite-sampling.md": ("1/\\hat p", "REINFORCE", "N=1",
                                            "0.68359375", "0.99609375", "TailRL"),
            "weighted-loss-and-masks.md": ("3.2", "归约", "分母", "response_tokens",
                                           "8", "错误回答", "默认"),
            "asynchronous-system.md": ("v10", "v14", "strict", "full-vocabulary",
                                       "top-k", "policy", "复用"),
            "mixing-and-schedules.md": ("80%", "0.005", "1,020,000", "420,000",
                                        "省略", "不等总计算", "更新"),
            "evidence-and-limits.md": ("两颗", "20B", "0.76B", "240M", "10%",
                                      "描述", "冲突", "事后", "未下载"),
            "sources.md": ("release", "默认", "固定", "未下载", "未执行"),
            "lab.md": ("3.2", "16", "80%", "1,020,000", "不是作者 trainer"),
        }
        for name, phrases in required.items():
            for phrase in phrases:
                self.assertIn(phrase, docs()["training/unified-training/" + name], name)
        for path in ("scripts/unified_training_lab.py", "tests/test_unified_training_lab.py"):
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + path,
                          docs()["training/unified-training/lab.md"])
            self.assertTrue((ROOT / path).is_file())

    def test_ten_original_diagrams_exact_bytes_retina_and_spacing(self):
        manifest = dl.unified_figures()
        self.assertEqual(len(manifest), 10)
        self.assertEqual(len({f["id"] for f in manifest}), 10)
        self.assertEqual(sum(len(f["placements"]) for f in manifest), 10)
        placed = Counter()
        for f in manifest:
            self.assertEqual(f["topic"], "deep-learning")
            self.assertTrue(f["id"].startswith("uni-"))
            svg = TOPIC / "images" / (f["id"] + ".svg")
            self.assertEqual(svg.read_text(), FIGURES.RENDERERS[f["kind"]](f))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), f)
            self.assert_public_study(svg.read_text(), svg.name)
            if f["kind"] == "compare":
                self.assertEqual(f["footer_gap"], 64)
                tree = ET.fromstring(svg.read_text())
                ns = {"s": FIGURES.SVG_NS}
                bottom = max(float(r.get("y")) + float(r.get("height"))
                             for r in tree.findall(".//s:rect", ns) if r.get("x"))
                self.assertGreaterEqual(float(tree.findall(".//s:line", ns)[-1].get("y1")),
                                        bottom + 32)
            for p in f["placements"]:
                name = Path(p["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                text = docs()[name]
                self.assertEqual(text.splitlines().count(p["after"]), 1)
                identity = f["id"] + "-" + hashlib.sha256(p["after"].encode()).hexdigest()[:10]
                blocks = [body for key, body in ILLUSTRATION.findall(text) if key == identity]
                self.assertEqual(len(blocks), 1)
                expected = os.path.relpath(svg.with_suffix(".png"), (TOPIC / name).parent)
                self.assertIn("](" + expected + ")", blocks[0])
                placed[name] += 1
        for name, count in zip(dl.UNIFIED_FILES, COUNTS):
            self.assertEqual(placed[name], count, name)
            self.assertEqual(len(ILLUSTRATION.findall(docs()[name])), count)
        expected = {f["id"] + "." + ext for f in manifest for ext in ("svg", "png")}
        self.assertEqual({p.name for p in (TOPIC / "images").glob("uni-*")}, expected)


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll before checking the study")
class UnifiedBuildTests(DeepLearningChecks):
    page = dl.DeepLearningSiteTests.page
    local_target = dl.DeepLearningSiteTests.local_target

    def test_exact_search_routes_titles_prose_links_and_training_group(self):
        records = json.loads((SITE / "search.json").read_text())
        base = self.page(next(iter(dl.UNIFIED_ROUTES.values()))).base
        selected = [row for row in records if urlsplit(row["url"]).path.startswith(
            base + "/wiki/topics/deep-learning/training/unified-training/")]
        self.assertEqual(Counter(row["url"] for row in selected),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in dl.UNIFIED_ROUTES.values()))
        for name, route in dl.UNIFIED_ROUTES.items():
            source, html = docs()[name], (SITE / route).read_text()
            page = self.page(route)
            self.assertEqual(page.article_count, 1)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assert_public_study(html, route)
            record = next(row for row in selected
                          if row["url"] == base + "/" + route.replace("index.html", ""))
            self.assertEqual(record["title"], re.search(r"(?m)^# (.+)$", source)[1])
            for sample in samples(source):
                self.assertIn(sample, normalized("".join(page.text)), name)
                self.assertIn(sample, normalized(record["text"]), name)
            for target in page.article_links:
                local = self.local_target(route, target)
                if local:
                    self.assertNotEqual(local.suffix, ".md")
            grouped = GroupedPage(html)
            self.assertEqual([g["name"] for g in grouped.groups], list(GROUPS))
            self.assertEqual([g["name"] for g in grouped.groups if g["open"]],
                             ["LLM 训练与后训练"])
            self.assertEqual(Counter(grouped.groups[0]["links"]),
                             Counter(base + "/" + r.replace("index.html", "")
                                     for r in [*dl.TRAINING_ROUTES.values(), *dl.AGENTIC_ROUTES.values(),
                                               *dl.UNIFIED_ROUTES.values()]))

    def test_built_images_and_actual_placement_headings(self):
        actual = {}
        for (name, route), count in zip(dl.UNIFIED_ROUTES.items(), COUNTS):
            page = self.page(route)
            self.assertEqual(len(page.images), count, name)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    path = self.local_target(route, value["src"])
                    self.assertTrue(value["alt"])
                    self.assertEqual(path.read_bytes(), (ROOT / path.relative_to(SITE)).read_bytes())
                    actual[(name, path.stem)] = heading
        for f in dl.unified_figures():
            for ext in ("svg", "png"):
                path = Path("wiki/topics/deep-learning/images") / (f["id"] + "." + ext)
                self.assertEqual((SITE / path).read_bytes(), (ROOT / path).read_bytes())
            for p in f["placements"]:
                name = Path(p["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertEqual(actual[(name, f["id"])], p["after"].lstrip("# "))

    def test_publication_scope_and_entrypoints(self):
        book = SITE / "wiki/topics/deep-learning/training/unified-training"
        names = {Path(name).name for name in dl.UNIFIED_FILES}
        expected = names | {name.replace(".md", ".html") for name in names} | {"index.html", "README.html"}
        self.assertEqual({p.name for p in book.iterdir()}, expected)
        for route in ("index.html", "wiki/topics/index.html", "wiki/topics/deep-learning/index.html",
                      "wiki/topics/deep-learning/training/index.html"):
            self.assertIn("unified-training/", (SITE / route).read_text())
        self.assertFalse((SITE / "scripts").exists())
        self.assertFalse((SITE / "tests").exists())


if __name__ == "__main__":
    unittest.main()
