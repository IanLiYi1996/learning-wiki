"""Offline source/build checks for the illustrated six-article collection."""

from collections import Counter
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

import test_deep_learning as wsp
from test_deep_learning import (
    ROOT, SITE, TOPIC, DIFFUSION_FILES, DIFFUSION_ROUTES, DIFFUSION_VERSIONS,
    DeepLearningChecks, diffusion_figures, readable_samples,
)
from test_payments import ILLUSTRATION, Page, markdown_links, normalized


ORIGINALS = ("preference-optimization", "rl-for-diffusion-part-1",
             "rl-for-diffusion-part-2", "autoresearch", "gpu-story",
             "realtime-video-calculator")
EXPECTED_COUNTS = (1, 1, 2, 2, 2, 2, 3, 0)


def documents():
    return {name: (TOPIC / name).read_text(encoding="utf-8") for name in DIFFUSION_FILES}


def samples(source):
    # Resolve reference-link notation before reusing the repo's prose sampler.
    refs = dict(re.findall(r"(?m)^\[([^\]]+)\]:\s*(\S+)\s*$", source))
    source = re.sub(r"(?m)^\[[^\]]+\]:\s*\S+\s*$", "", source)
    source = re.sub(r"\[([^\]]+)\]\[([^\]]+)\]",
                    lambda match: f"[{match[1]}]({refs[match[2]]})", source)
    return readable_samples(source)


class DiffusionSourceTests(DeepLearningChecks):
    def test_eight_complete_public_documents_and_six_original_entries(self):
        docs = documents()
        self.assertEqual(len(docs), 8)
        overview = docs["diffusion/README.md"]
        for original in ORIGINALS:
            self.assertIn(f"https://anvilarth.github.io/{original}.html", overview)
        for index, (name, text) in enumerate(docs.items()):
            self.assert_public_study(text, name)
            self.assertIn("2026-11-03", text)
            self.assertIn('id="public-sources"', text)
            self.assertNotRegex(text, r"TODO|TBD|待主 agent|主 agent 唯一")
            self.assertGreater(len(ILLUSTRATION.sub("", text)), 2000)
            if 1 <= index <= 6:
                self.assertIn(f'id="diffusion-{index:02d}"', text)
                self.assertIn(f"https://anvilarth.github.io/{ORIGINALS[index - 1]}.html", text)
                self.assertIn("自测", text)
                self.assertRegex(text, r"答案|答：")
                self.assertEqual(re.findall(r"(?m)^([123])\. ", text), ["1", "2", "3"])
                self.assertGreaterEqual(len(re.findall(r"(?m)^## ", text)), 7)
                self.assertGreaterEqual(len(list(samples(text))), 15)

    def test_local_links_fragments_and_versioned_sources(self):
        texts = documents()
        all_text = "\n".join(texts.values())
        for name, text in texts.items():
            self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
            for target in [target for _, target in markdown_links(text)] + Page(text).links:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    self.assertNotEqual(parts.scheme, "http")
                    continue
                path = (TOPIC / name).parent / unquote(parts.path) if parts.path else TOPIC / name
                path = path.resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(), f"{name}: {target}")
                if parts.fragment:
                    self.assertIn(unquote(parts.fragment), Page(path.read_text(encoding="utf-8")).ids)
        for version, repository in DIFFUSION_VERSIONS.items():
            self.assertIn(f"https://{repository}/blob/{version}/", all_text)
            with self.assertRaises(AssertionError):
                self.assert_public_study("unattributed digest: " + version, "negative fixture")
            with self.assertRaises(AssertionError):
                self.assert_public_study(
                    f"https://{repository}/blob/{version}/unpublished.docx",
                    "known revision must not exempt a whole URL")

    def test_thirteen_figures_exact_bytes_retina_and_relative_embedding(self):
        manifest = diffusion_figures()
        self.assertEqual(len(manifest), 13)
        self.assertEqual(len({figure["id"] for figure in manifest}), 13)
        self.assertEqual(sum(len(figure["placements"]) for figure in manifest), 13)
        spec = importlib.util.spec_from_file_location("dif_figures", ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        for suffix in ("svg", "png"):
            self.assertEqual({path.stem for path in (TOPIC / "images").glob(f"dif-*.{suffix}")},
                             {figure["id"] for figure in manifest})
        placements = Counter()
        for figure in manifest:
            self.assertEqual(figure["topic"], "deep-learning")
            self.assertRegex(figure["id"], r"^dif-[a-z0-9-]+$")
            svg = TOPIC / "images" / (figure["id"] + ".svg")
            self.assertEqual(svg.read_text(encoding="utf-8"),
                             renderer.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertIn(name, DIFFUSION_FILES)
                placements[name] += 1
                text = documents()[name]
                marker = figure["id"] + "-" + hashlib.sha256(
                    placement["after"].encode()).hexdigest()[:10]
                blocks = [body for identity, body in ILLUSTRATION.findall(text) if identity == marker]
                self.assertEqual(len(blocks), 1)
                self.assertIn(f"](../images/{figure['id']}.png)", blocks[0])
                self.assertIn(f"*图：{figure['title']}。", blocks[0])
                self.assertRegex(text, re.escape(placement["after"]) +
                                 r"\n\s*<!-- illustration: " + marker + " -->")
        for name, expected in zip(DIFFUSION_FILES, EXPECTED_COUNTS):
            self.assertEqual(placements[name], expected)
            self.assertEqual(len(ILLUSTRATION.findall(documents()[name])), expected)

    def test_teaching_results_and_source_boundaries_remain_explicit(self):
        docs = documents()
        lab = docs["diffusion/lab.md"]
        for number in ("3520", "3680", "4600", "180000", "120000", "26.077"):
            self.assertIn(number, lab)
        for file in ("scripts/diffusion_lab.py", "tests/test_diffusion_lab.py"):
            self.assertTrue((ROOT / file).is_file())
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + file, lab)
        for phrase in ("不运行图像生成模型", "不使用 GPU", "不是任何论文的实验成绩"):
            self.assertIn(phrase, lab)
        video = docs["diffusion/06-realtime-video-estimates.md"]
        for phrase in ("整体", "0.4", "0.7", "0.15", "首帧", "不是实测基准", "INT8", "FP8"):
            self.assertIn(phrase, video)
        self.assertIn("有偏", docs["diffusion/02-rl-through-denoising.md"])
        self.assertIn("sample std", docs["diffusion/03-rewards-judges-and-advantages.md"])
        self.assertIn("NaN", docs["diffusion/04-autoresearch-and-oracles.md"])


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll or set DEEP_LEARNING_SITE")
class DiffusionSiteTests(DeepLearningChecks):
    # Reuse only helpers, not inherited WSP test methods.
    page = wsp.DeepLearningSiteTests.page
    local_target = wsp.DeepLearningSiteTests.local_target

    def test_eight_searchable_pages_full_prose_and_links(self):
        records = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        base = self.page(DIFFUSION_ROUTES["diffusion/README.md"]).base
        selected = [item for item in records if urlsplit(item["url"]).path.startswith(
            base + "/wiki/topics/deep-learning/diffusion/")]
        self.assertEqual(Counter(item["url"] for item in selected),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in DIFFUSION_ROUTES.values()))
        for name, route in DIFFUSION_ROUTES.items():
            page = self.page(route)
            self.assertEqual(page.article_count, 1)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assertTrue(set(Page(documents()[name]).ids).issubset(page.article_ids))
            self.assert_public_study((SITE / route).read_text(encoding="utf-8"), route)
            record = next(item for item in selected
                          if item["url"] == base + "/" + route.replace("index.html", ""))
            expected_title = re.search(r"(?m)^# (.+)$", documents()[name])[1]
            self.assertEqual(record["title"], expected_title)
            self.assertIn("<title>" + html.escape(expected_title) + " |",
                          (SITE / route).read_text(encoding="utf-8"))
            body = normalized("".join(page.text))
            for sample in samples(documents()[name]):
                self.assertIn(sample, body, f"Missing article prose in {name}")
                self.assertIn(sample, normalized(record["text"]), f"Missing search prose in {name}")
            for target in page.article_links:
                local = self.local_target(route, target)
                if local:
                    self.assertNotEqual(local.suffix, ".md")
            for chapter in DIFFUSION_ROUTES.values():
                self.assertIn(base + "/" + chapter.replace("index.html", ""), page.sidebar_links)

    def test_all_built_illustrations_are_local_match_assets_and_heading(self):
        actual = {}
        for (name, route), expected in zip(DIFFUSION_ROUTES.items(), EXPECTED_COUNTS):
            page = self.page(route)
            self.assertEqual(len(page.images), expected)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    path = self.local_target(route, value["src"])
                    self.assertTrue(value["alt"])
                    actual[(name, path.stem)] = heading
        for figure in diffusion_figures():
            for suffix in ("svg", "png"):
                relative = f"wiki/topics/deep-learning/images/{figure['id']}.{suffix}"
                self.assertEqual((SITE / relative).read_bytes(), (ROOT / relative).read_bytes())
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertEqual(actual[(name, figure["id"])], placement["after"].lstrip("# "))


if __name__ == "__main__":
    unittest.main()
