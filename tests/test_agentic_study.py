"""Additive source/build regressions for the Datawhale study."""

from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

import test_deep_learning as dl
from test_payments import ILLUSTRATION, Page, markdown_links, normalized
from test_training_recipes import GROUPS, GroupedPage, samples


COUNTS = (2, 2, 1, 1, 1, 1, 1, 1, 0)


def documents():
    return {name: (dl.TOPIC / name).read_text(encoding="utf-8") for name in dl.AGENTIC_FILES}


def study_samples(source):
    # Reference definitions are metadata, while the visible reference label is
    # still substantive prose that must survive both build and search indexing.
    source = re.sub(r"(?m)^\[[^\]]+\]:\s+\S+.*\n?", "", source)
    source = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]+\]", r"\1", source)
    return samples(source)


class AgenticSourceTests(dl.DeepLearningChecks):
    def test_nine_complete_dated_public_pages(self):
        self.assertEqual(len(documents()), 9)
        for name, text in documents().items():
            self.assertRegex(text, r"\A# ")
            self.assertIn("2026-11-03", text)
            self.assertNotRegex(text, r"TODO|TBD|待主 agent|待主任务")
            self.assertGreater(len(ILLUSTRATION.sub("", text)), 1700, name)
            self.assert_public_study(text, name)
        self.assertEqual(sum(COUNTS), 10)

    def test_complete_upstream_mapping_and_explicit_boundaries(self):
        hub = documents()[dl.AGENTIC_FILES[0]]
        for directory in ("loss-functions", "grpo", "vision-grpo", "pytrio-jev",
                          "general-opd", "medical-opd", "dapo", "gspo", "opsd",
                          "agentopsd", "search-r1", "retool", "alfworld", "tempo",
                          "spec-o3", "tournament-grpo"):
            self.assertIn(f"`{directory}`", hub)
        for phrase in ("远程", "不等于", "不是", "标准库"):
            self.assertIn(phrase, hub)
        source = documents()[dl.AGENTIC_FILES[-1]]
        for phrase in ("Apache-2.0", "16 个入口", "2402.03300v3",
                       "2503.14476v2", "2507.18071v2", "未执行", "未核验"):
            self.assertIn(phrase, source)
        for revision, repository in dl.AGENTIC_VERSIONS.items():
            self.assertIn(f"https://{repository}/tree/{revision}", source)
            for fixture in (revision, f"https://{repository}/blob/{revision}/secret.docx",
                            f"https://github.com/another/repo/blob/{revision}/file.py"):
                with self.assertRaises(AssertionError):
                    self.assert_public_study(fixture, "revision negative control")

    def test_local_links_and_fragments(self):
        for name, text in documents().items():
            self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
            # Include reference-style targets as well as inline links.
            references = re.findall(r"(?m)^\[[^\]]+\]:\s+(\S+)", text)
            for target in [url for _, url in markdown_links(text)] + references + Page(text).links:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    self.assertNotEqual(parts.scheme, "http")
                    continue
                path = ((dl.TOPIC / name).parent / unquote(parts.path)).resolve() \
                    if parts.path else dl.TOPIC / name
                self.assertTrue(path.is_relative_to(dl.ROOT))
                self.assertTrue(path.is_file(), f"{name}: {target}")
                if parts.fragment:
                    self.assertIn(unquote(parts.fragment), Page(path.read_text()).ids)

    def test_ten_figures_exact_placements_and_retina_assets(self):
        manifest = dl.agentic_figures()
        self.assertEqual(len(manifest), 10)
        self.assertEqual(sum(len(fig["placements"]) for fig in manifest), 10)
        self.assertEqual(len({fig["id"] for fig in manifest}), 10)
        spec = importlib.util.spec_from_file_location("agentic_figures", dl.ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        placed = Counter()
        for suffix in ("svg", "png"):
            self.assertEqual({path.stem for path in (dl.TOPIC / "images").glob(f"arl-*.{suffix}")},
                             {fig["id"] for fig in manifest})
        for figure in manifest:
            self.assertEqual(figure["topic"], "deep-learning")
            self.assertRegex(figure["id"], r"^arl-[a-z0-9-]+$")
            svg = dl.TOPIC / "images" / (figure["id"] + ".svg")
            self.assertEqual(svg.read_text(), renderer.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(dl.TOPIC.relative_to(dl.ROOT)).as_posix()
                self.assertIn(name, dl.AGENTIC_FILES)
                placed[name] += 1
                identity = figure["id"] + "-" + hashlib.sha256(placement["after"].encode()).hexdigest()[:10]
                text = documents()[name]
                self.assertEqual(text.splitlines().count(placement["after"]), 1)
                blocks = [body for marker, body in ILLUSTRATION.findall(text) if marker == identity]
                self.assertEqual(len(blocks), 1)
                target = os.path.relpath(svg.with_suffix(".png"), (dl.TOPIC / name).parent)
                self.assertIn(f"]({target})", blocks[0])
        for name, count in zip(dl.AGENTIC_FILES, COUNTS):
            self.assertEqual(placed[name], count)
            self.assertEqual(len(ILLUSTRATION.findall(documents()[name])), count)

    def test_original_lab_results_and_safety_are_recorded(self):
        text = documents()[dl.AGENTIC_FILES[-2]]
        for phrase in ("0.8660254", "0.9797959", "0.125", "0.3333333",
                       "不是上游模型训练复现", "固定权重"):
            self.assertIn(phrase, text)
        for path in ("scripts/agentic_rl_lab.py", "tests/test_agentic_rl_lab.py"):
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + path, text)
            self.assertTrue((dl.ROOT / path).is_file())


@unittest.skipUnless(dl.SITE.is_dir(), "Build Jekyll first")
class AgenticSiteTests(dl.DeepLearningChecks):
    page = dl.DeepLearningSiteTests.page
    local_target = dl.DeepLearningSiteTests.local_target

    def test_search_prose_links_and_group_routes(self):
        base = self.page(dl.AGENTIC_ROUTES[dl.AGENTIC_FILES[0]]).base
        records = json.loads((dl.SITE / "search.json").read_text())
        selected = [item for item in records if urlsplit(item["url"]).path.startswith(
            base + "/wiki/topics/deep-learning/training/agentic-rl-lab/")]
        self.assertEqual(Counter(item["url"] for item in selected),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in dl.AGENTIC_ROUTES.values()))
        for name, route in dl.AGENTIC_ROUTES.items():
            page, source = self.page(route), documents()[name]
            self.assertEqual(page.article_count, 1)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assertTrue(set(Page(source).ids).issubset(page.article_ids))
            record = next(item for item in selected if item["url"] ==
                          base + "/" + route.replace("index.html", ""))
            self.assertEqual(record["title"], re.search(r"(?m)^# (.+)$", source)[1])
            for sample in study_samples(source):
                self.assertIn(sample, normalized("".join(page.text)), name)
                self.assertIn(sample, normalized(record["text"]), name)
            self.assert_public_study((dl.SITE / route).read_text(), route)
            for target in page.article_links:
                local = self.local_target(route, target)
                if local:
                    self.assertNotEqual(local.suffix, ".md")
            grouped = GroupedPage((dl.SITE / route).read_text())
            self.assertEqual([group["name"] for group in grouped.groups], list(GROUPS))
            self.assertEqual([group["name"] for group in grouped.groups if group["open"]], [GROUPS[0]])
            self.assertEqual(Counter(grouped.groups[0]["links"]),
                             Counter(base + "/" + rel.replace("index.html", "")
                                     for rel in [*dl.TRAINING_ROUTES.values(), *dl.AGENTIC_ROUTES.values(),
                                                 *dl.UNIFIED_ROUTES.values(), *dl.MOE_SWARM_ROUTES.values()]))

    def test_built_assets_headings_and_local_fallbacks(self):
        actual = {}
        for (name, route), count in zip(dl.AGENTIC_ROUTES.items(), COUNTS):
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
        for figure in dl.agentic_figures():
            for suffix in ("svg", "png"):
                relative = f"wiki/topics/deep-learning/images/{figure['id']}.{suffix}"
                self.assertEqual((dl.SITE / relative).read_bytes(), (dl.ROOT / relative).read_bytes())
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(dl.TOPIC.relative_to(dl.ROOT)).as_posix()
                self.assertEqual(actual[(name, figure["id"])], placement["after"].lstrip("# "))
