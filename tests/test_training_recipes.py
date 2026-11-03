"""Training collection, opt-in subgroup navigation and public-build checks."""

from collections import Counter
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

import test_deep_learning as dl
from test_deep_learning import (
    ROOT, SITE, TOPIC, TRAINING_FILES, TRAINING_ROUTES, TRAINING_VERSIONS,
    DeepLearningChecks, training_figures, readable_samples,
)
from test_payments import ILLUSTRATION, Page, markdown_links, normalized


GROUPS = ("LLM 训练与后训练", "扩散与视觉生成", "推理与硬件",
          "自动研究与评测", "权重编辑与解释")
COUNTS = (0, 1, 1, 2, 1, 2, 1, 0)


def documents():
    return {name: (TOPIC / name).read_text(encoding="utf-8") for name in TRAINING_FILES}


def samples(source):
    # The shared sampler handles bold/code/links; this collection also uses
    # normal single-star emphasis for paper titles. Preserve the title text.
    source = re.sub(r"(?<![\w*`])\*([^*\n]+)\*(?![\w*`])", r"\1", source)
    return readable_samples(source)


class GroupedPage(Page):
    def __init__(self, source):
        self.groups = []
        self.detail_stack = []
        super().__init__(source)

    def handle_starttag(self, tag, attributes):
        super().handle_starttag(tag, attributes)
        attrs = dict(attributes)
        if tag == "details":
            group = None
            if "nav-subtopic" in attrs.get("class", "").split():
                group = {"name": attrs["data-subtopic"], "open": "open" in attrs, "links": []}
                self.groups.append(group)
            self.detail_stack.append(group)
        if tag == "a" and "nav-leaf" in attrs.get("class", "").split():
            group = next((item for item in reversed(self.detail_stack) if item), None)
            if group is not None:
                group["links"].append(attrs["href"])

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if tag == "details":
            self.detail_stack.pop()


class TrainingSourceTests(DeepLearningChecks):
    def test_complete_pages_metadata_boundaries_and_self_tests(self):
        docs = documents()
        self.assertEqual(len(docs), 8)
        for name, text in docs.items():
            self.assertRegex(text, r"\A# ")
            self.assertIn("2026-11-03", text)
            self.assert_public_study(text, name)
            self.assertNotRegex(text, r"TODO|TBD|待主任务|待主 agent")
            self.assertGreater(len(ILLUSTRATION.sub("", text)), 1400)
        for name in TRAINING_FILES[2:6]:
            text = docs[name]
            self.assertIn('id="public-sources"', text)
            self.assertGreaterEqual(len(re.findall(r"(?m)^## ", text)), 7)
            self.assertEqual(re.findall(r"(?m)^([123])\. ", text), ["1", "2", "3"])
            self.assertGreaterEqual(len(list(samples(text))), 15)
        source = docs["training/rufus-air/sources.md"]
        for phrase in ("2609.29421v2", "2026-09-24", "2026-09-25", "22 位", "预印本",
                       "未查询", "不转载", "专用 Rufus-Air", "第一级", "第三级"):
            self.assertIn(phrase, source)

    def test_explicit_taxonomy_and_old_source_files_preserved(self):
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        segment = navigation.split("  - label: 深度学习专题\n", 1)[1].split(
            "  - label: 支付行业 101\n", 1)[0]
        self.assertEqual(set(re.findall(r"(?m)^\s+group: (.+)$", segment)), set(GROUPS))
        for name in ("category-training", "category-diffusion", "category-inference",
                     "category-research", "category-weights"):
            self.assertIn(name, Page((TOPIC / "README.md").read_text(encoding="utf-8")).ids)
        for name in (*dl.FILES, *dl.DIFFUSION_FILES):
            self.assertTrue((TOPIC / name).is_file())
        home = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("五个方向细分", home)

    def test_local_links_anchors_and_exact_source_revision_exemptions(self):
        all_text = "\n".join(documents().values())
        for name, text in documents().items():
            self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
            for target in [url for _, url in markdown_links(text)] + Page(text).links:
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
        for revision, repository in TRAINING_VERSIONS.items():
            self.assertIn(revision, all_text)
            self.assertIn(repository, all_text)
            for bad in ("unattributed " + revision,
                        f"https://{repository}/blob/{revision}/private.docx"):
                with self.assertRaises(AssertionError):
                    self.assert_public_study(bad, "negative fixture")

    def test_eight_diagrams_exact_assets_retina_and_nested_relative_paths(self):
        manifest = training_figures()
        self.assertEqual(len(manifest), 8)
        self.assertEqual(len({figure["id"] for figure in manifest}), 8)
        self.assertEqual(sum(len(figure["placements"]) for figure in manifest), 8)
        spec = importlib.util.spec_from_file_location("recipe_figures", ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        for suffix in ("svg", "png"):
            self.assertEqual({path.stem for path in (TOPIC / "images").glob(f"ruf-*.{suffix}")},
                             {figure["id"] for figure in manifest})
        placed = Counter()
        for figure in manifest:
            self.assertEqual(figure["topic"], "deep-learning")
            self.assertRegex(figure["id"], r"^ruf-[a-z0-9-]+$")
            svg = TOPIC / "images" / (figure["id"] + ".svg")
            self.assertEqual(svg.read_text(encoding="utf-8"),
                             renderer.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                placed[name] += 1
                text = documents()[name]
                identity = figure["id"] + "-" + hashlib.sha256(
                    placement["after"].encode()).hexdigest()[:10]
                blocks = [body for key, body in ILLUSTRATION.findall(text) if key == identity]
                self.assertEqual(len(blocks), 1)
                self.assertIn(f"](../../images/{figure['id']}.png)", blocks[0])
                self.assertIn(f"*图：{figure['title']}。", blocks[0])
                self.assertRegex(text, re.escape(placement["after"]) +
                                 r"\n\s*<!-- illustration: " + identity + " -->")
        for name, expected in zip(TRAINING_FILES, COUNTS):
            self.assertEqual(placed[name], expected)
            self.assertEqual(len(ILLUSTRATION.findall(documents()[name])), expected)

    def test_lab_results_scope_and_code_are_recorded(self):
        text = documents()["training/rufus-air/lab.md"]
        for number in ("4096", "380", "0.4401267", "0.6561", "2.5", "1.325", "832", "6656"):
            self.assertIn(number, text)
        for filename in ("scripts/training_recipe_lab.py", "tests/test_training_recipe_lab.py"):
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + filename, text)
            self.assertTrue((ROOT / filename).is_file())
        for phrase in ("标准库", "不是 Rufus-Air trainer", "没有真实训练"):
            self.assertIn(phrase, text)


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll first")
class TrainingSiteTests(DeepLearningChecks):
    page = dl.DeepLearningSiteTests.page
    local_target = dl.DeepLearningSiteTests.local_target

    def test_eight_searchable_pages_titles_prose_links_and_groups(self):
        base = self.page(next(iter(TRAINING_ROUTES.values()))).base
        records = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        selected = [item for item in records if urlsplit(item["url"]).path.startswith(
            base + "/wiki/topics/deep-learning/training/")]
        self.assertEqual(Counter(item["url"] for item in selected),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in [*TRAINING_ROUTES.values(), *dl.AGENTIC_ROUTES.values()]))
        for name, route in TRAINING_ROUTES.items():
            page = self.page(route)
            source = documents()[name]
            record = next(item for item in selected
                          if item["url"] == base + "/" + route.replace("index.html", ""))
            title = re.search(r"(?m)^# (.+)$", source)[1]
            self.assertEqual(record["title"], title)
            self.assertIn("<title>" + html.escape(title) + " |",
                          (SITE / route).read_text(encoding="utf-8"))
            self.assertEqual(page.article_count, 1)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assertTrue(set(Page(source).ids).issubset(page.article_ids))
            self.assert_public_study((SITE / route).read_text(encoding="utf-8"), route)
            for sample in samples(source):
                self.assertIn(sample, normalized("".join(page.text)), name)
                self.assertIn(sample, normalized(record["text"]), name)
            for target in page.article_links:
                local = self.local_target(route, target)
                if local:
                    self.assertNotEqual(local.suffix, ".md")
            grouped = GroupedPage((SITE / route).read_text(encoding="utf-8"))
            self.assertEqual([group["name"] for group in grouped.groups], list(GROUPS))
            self.assertEqual([group["name"] for group in grouped.groups if group["open"]],
                             [GROUPS[0]])
            self.assertEqual(Counter(grouped.groups[0]["links"]),
                             Counter(base + "/" + relative.replace("index.html", "")
                                     for relative in [*TRAINING_ROUTES.values(), *dl.AGENTIC_ROUTES.values()]))

    def test_built_assets_captions_and_placement_heading(self):
        actual = {}
        for (name, route), count in zip(TRAINING_ROUTES.items(), COUNTS):
            page = self.page(route)
            self.assertEqual(len(page.images), count)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    path = self.local_target(route, value["src"])
                    self.assertTrue(value["alt"])
                    actual[(name, path.stem)] = heading
        for figure in training_figures():
            for suffix in ("svg", "png"):
                relative = f"wiki/topics/deep-learning/images/{figure['id']}.{suffix}"
                self.assertEqual((SITE / relative).read_bytes(), (ROOT / relative).read_bytes())
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertEqual(actual[(name, figure["id"])], placement["after"].lstrip("# "))

    def test_grouping_is_opt_in_and_old_topic_links_remain_ungrouped(self):
        for route in ("wiki/topics/payments/index.html", "wiki/topics/physical-ai/index.html"):
            grouped = GroupedPage((SITE / route).read_text(encoding="utf-8"))
            # The shared sidebar includes DL groups, but other topic blocks do not.
            text = (SITE / route).read_text(encoding="utf-8")
            segment = text.split('data-topic="' + grouped.base + "/" +
                                 route.replace("index.html", "") + '"', 1)[1].split(
                                     '</details>', 1)[0]
            self.assertNotIn("nav-subtopic", segment)
        for name, route in {**dl.ROUTES, **dl.DIFFUSION_ROUTES}.items():
            grouped = GroupedPage((SITE / route).read_text(encoding="utf-8"))
            self.assertEqual(len(grouped.groups), 5)
            self.assertEqual(sum(len(group["links"]) for group in grouped.groups),
                             len(TRAINING_ROUTES) + len(dl.AGENTIC_ROUTES) + len(dl.DIFFUSION_ROUTES) +
                             len(dl.ROUTES) - 1 + len(dl.LESSONS))


if __name__ == "__main__":
    unittest.main()
