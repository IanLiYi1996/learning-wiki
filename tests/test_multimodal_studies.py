"""Content, publication scope, evidence boundaries, figures and reader contracts."""

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
from test_deep_learning import (
    ROOT, SITE, TOPIC, VISION_FILES, VISION_ROUTES, VISION_VERSIONS,
    DeepLearningChecks, vision_figures,
)
from test_figures import FIGURES
from test_payments import ILLUSTRATION, Page, markdown_links, normalized
from test_training_recipes import GROUPS, GroupedPage, samples


COUNTS = (1, 1, 2, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 0)


def docs():
    return {name: (TOPIC / name).read_text() for name in VISION_FILES}


class VisionSourceTests(DeepLearningChecks):
    def test_exact_fourteen_complete_public_pages(self):
        self.assertEqual(len(VISION_FILES), 14)
        self.assertEqual({p.relative_to(TOPIC).as_posix()
                          for p in (TOPIC / "vision").rglob("*") if p.is_file()},
                         set(VISION_FILES))
        for name, text in docs().items():
            self.assertRegex(text, r"\A# ")
            self.assertIn("2026-11-04", text)
            self.assertGreater(len(ILLUSTRATION.sub("", text)), 1000, name)
            self.assert_public_study(text, name)
            self.assertNotRegex(text, r"TODO|TBD|主代理|待主任务|后续插入|```mermaid")
            self.assertGreaterEqual(len(re.findall(r"(?m)^## ", text)), 4, name)
            self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
        for prefix in ("pixelbench", "embeddinggemma-2"):
            source = docs()[f"vision/{prefix}/sources.md"]
            self.assertIn("未", source)
            self.assertIn("权重", source)
            self.assertIn("benchmark", source)

    def test_all_local_links_and_explicit_anchors_resolve(self):
        for name, text in docs().items():
            for target in [target for _, target in markdown_links(text)] + Page(text).links:
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

    def test_exact_public_revision_exemptions_are_narrow(self):
        text = "\n".join(docs().values())
        for revision, repository in VISION_VERSIONS.items():
            self.assertIn(repository, text)
            self.assertIn(revision, text)
            for bad in (revision, "https://unknown.invalid/blob/" + revision + "/README.md",
                        f"https://{repository}/blob/{revision}/private.docx"):
                with self.subTest(bad=bad), self.assertRaises(AssertionError):
                    self.assert_public_study(bad, "negative fixture")
        self.assert_public_study(
            "https://huggingface.co/google/embeddinggemma-2/raw/"
            "f9972ac22e696a105c482202646979e33e4b5a1e/README.md", "verified card")

    def test_pixelbench_claims_keep_tasks_denominators_controls_and_nonexecution(self):
        required = {
            "representation-and-tasks.md": ("2–8", "600", "10%", "视觉编码器", "布尔值", "4×4"),
            "metrics-and-results.md": ("500-way", "100", "MRR", "null", "min–max",
                                      "0.375", "0.75", "0.871", "0.930", "相对"),
            "resolution-and-failure-modes.md": ("4,096", "16×", "token", "机制假说", "重复"),
            "prt-training.md": ("step32000", "500k", "2k", "a–h", "1,047", "61k",
                                "0.6", "3.7", "16 个", "13 个", "不是 PPO"),
            "evidence-and-limitations.md": ("n=7", "n=6", "caption-only", "FLOPs", "未下载"),
            "sources.md": ("没有下载", "模板", "实现", "独立", "format.py"),
            "lab.md": ("0.375", "0.75", "0.9", "0.5", "None", "不是 PixelBench evaluator"),
        }
        for name, phrases in required.items():
            for phrase in phrases:
                self.assertIn(phrase, docs()["vision/pixelbench/" + name], name)
        for path in ("scripts/pixelbench_lab.py", "tests/test_pixelbench_lab.py"):
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + path,
                          docs()["vision/pixelbench/lab.md"])
            self.assertTrue((ROOT / path).is_file())

    def test_embedding_claims_keep_architecture_recipe_and_counterexamples(self):
        required = {
            "architecture.md": ("744M", "271M", "439M", "577M", "24 层", "512→768",
                                "PLE", "GELU", "8192", "5280", "8960", "128", "重新"),
            "training-recipe.md": ("300B", "2T", "600B", "小权重", "冻结",
                                   "false-negative", "same-tower", "1/d",
                                   "同一次", "Q4_C", "W8A8"),
            "evaluation-and-deployment.md": ("68.46", "69.67", "59.01", "49.87",
                                           "69.54", "57.59", "MRR@10", "191 MB",
                                           "harness", "回滚", "未执行"),
            "sources.md": ("v1", "2026-10-27", "固定 revision", "元数据",
                           "未下载", "第一代", "Papers with Code"),
        }
        for name, phrases in required.items():
            for phrase in phrases:
                self.assertIn(phrase, docs()["vision/embeddinggemma-2/" + name], name)
        self.assertIn("不是维修答案", docs()["vision/embeddinggemma-2/README.md"])
        self.assertIn("pixelbench/README.md", docs()["vision/embeddinggemma-2/README.md"])

    def test_fourteen_local_retina_diagrams_and_exact_placements(self):
        manifest = vision_figures()
        self.assertEqual(len(manifest), 14)
        self.assertEqual(Counter(f["id"].split("-")[0] for f in manifest),
                         {"rep": 1, "pxb": 9, "eg2": 4})
        self.assertEqual(sum(len(f["placements"]) for f in manifest), 14)
        placed = Counter()
        for f in manifest:
            self.assertEqual(f["topic"], "deep-learning")
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
                source = docs()[name]
                self.assertEqual(source.splitlines().count(p["after"]), 1)
                marker = f["id"] + "-" + hashlib.sha256(p["after"].encode()).hexdigest()[:10]
                blocks = [body for key, body in ILLUSTRATION.findall(source) if key == marker]
                self.assertEqual(len(blocks), 1)
                expected = os.path.relpath(svg.with_suffix(".png"), (TOPIC / name).parent)
                self.assertIn("](" + expected + ")", blocks[0])
                self.assertIn("*图：" + f["title"], blocks[0])
                placed[name] += 1
        for name, count in zip(VISION_FILES, COUNTS):
            self.assertEqual(placed[name], count, name)
            self.assertEqual(len(ILLUSTRATION.findall(docs()[name])), count)
        expected = {f["id"] + "." + ext for f in manifest for ext in ("svg", "png")}
        actual = {p.name for prefix in ("rep-", "pxb-", "eg2-")
                  for p in (TOPIC / "images").glob(prefix + "*")}
        self.assertEqual(actual, expected)


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll before checking the studies")
class VisionBuildTests(DeepLearningChecks):
    page = dl.DeepLearningSiteTests.page
    local_target = dl.DeepLearningSiteTests.local_target

    def test_exact_search_routes_titles_prose_links_and_groups(self):
        records = json.loads((SITE / "search.json").read_text())
        base = self.page(VISION_ROUTES["vision/README.md"]).base
        selected = [row for row in records
                    if urlsplit(row["url"]).path.startswith(base + "/wiki/topics/deep-learning/vision/")]
        self.assertEqual(Counter(row["url"] for row in selected),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in VISION_ROUTES.values()))
        for name, route in VISION_ROUTES.items():
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
                             ["视觉表征与多模态"])
            self.assertEqual(Counter(grouped.groups[2]["links"]),
                             Counter(base + "/" + r.replace("index.html", "")
                                     for r in VISION_ROUTES.values()))

    def test_image_bytes_alt_caption_and_content_heading(self):
        actual = {}
        for (name, route), count in zip(VISION_ROUTES.items(), COUNTS):
            page = self.page(route)
            self.assertEqual(len(page.images), count, name)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    local = self.local_target(route, value["src"])
                    self.assertTrue(value["alt"])
                    self.assertEqual(local.read_bytes(), (ROOT / local.relative_to(SITE)).read_bytes())
                    actual[(name, local.stem)] = heading
        for f in vision_figures():
            for ext in ("svg", "png"):
                asset = Path("wiki/topics/deep-learning/images") / (f["id"] + "." + ext)
                self.assertEqual((SITE / asset).read_bytes(), (ROOT / asset).read_bytes())
            for p in f["placements"]:
                name = Path(p["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertEqual(actual[(name, f["id"])], p["after"].lstrip("# "))

    def test_exact_published_scope_and_root_entrypoints(self):
        expected = set(VISION_FILES) | {name.replace(".md", ".html") for name in VISION_FILES} | {
            "vision/index.html", "vision/README.html",
            "vision/pixelbench/index.html", "vision/pixelbench/README.html",
            "vision/embeddinggemma-2/index.html", "vision/embeddinggemma-2/README.html"}
        self.assertEqual({p.relative_to(SITE / "wiki/topics/deep-learning").as_posix()
                          for p in (SITE / "wiki/topics/deep-learning/vision").rglob("*")
                          if p.is_file()}, expected)
        for route in ("index.html", "wiki/topics/index.html", "wiki/topics/deep-learning/index.html"):
            source = (SITE / route).read_text()
            self.assertIn("PixelBench", source)
            self.assertIn("EmbeddingGemma 2", source)
            self.assertIn("视觉表征", source)
        self.assertFalse((SITE / "scripts").exists())
        self.assertFalse((SITE / "tests").exists())


if __name__ == "__main__":
    unittest.main()
