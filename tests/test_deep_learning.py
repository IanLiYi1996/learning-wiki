"""Offline document/build regressions for the weight-space study."""

from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit

# Reuse the repo's HTML/link/prose parser, not its payment-specific expectations.
from test_payments import ILLUSTRATION, Page, PaymentsChecks, markdown_links, normalized, prose_samples


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/deep-learning"
SITE = Path(os.environ.get("DEEP_LEARNING_SITE", ROOT / "_site")).resolve()
FILES = ("README.md", "weight-space-programming.md", "weight-space-programming-lab.md",
         "glossary.md", "weight-space-programming-sources.md")
DIFFUSION_FILES = tuple("diffusion/" + name for name in (
    "README.md", "01-dpo-and-preference-pairs.md", "02-rl-through-denoising.md",
    "03-rewards-judges-and-advantages.md", "04-autoresearch-and-oracles.md",
    "05-gpu-and-memory-roofline.md", "06-realtime-video-estimates.md", "lab.md"))
TRAINING_FILES = ("training/README.md",) + tuple("training/rufus-air/" + name for name in (
    "README.md", "data-sft-and-rlvr.md", "agentic-environments.md",
    "reward-and-stability.md", "infrastructure-and-evaluation.md", "lab.md", "sources.md"))
AGENTIC_FILES = tuple("training/agentic-rl-lab/" + name for name in (
    "README.md", "policy-objectives.md", "tools-and-environments.md",
    "on-policy-distillation.md", "credit-assignment.md", "multimodal-and-judges.md",
    "evaluation-and-reproduction.md", "lab.md", "sources.md"))
ROUTES = {name: "wiki/topics/deep-learning/" +
          ("index.html" if name == "README.md" else name.replace(".md", ".html"))
          for name in FILES}
DIFFUSION_ROUTES = {name: "wiki/topics/deep-learning/" +
                    ("diffusion/index.html" if name.endswith("README.md") else
                     name.replace(".md", ".html")) for name in DIFFUSION_FILES}
TRAINING_ROUTES = {name: "wiki/topics/deep-learning/" +
                   name.replace("README.md", "index.html").replace(".md", ".html")
                   for name in TRAINING_FILES}
AGENTIC_ROUTES = {name: "wiki/topics/deep-learning/" +
                  name.replace("README.md", "index.html").replace(".md", ".html")
                  for name in AGENTIC_FILES}
LESSONS = [f"wsp-{number:02d}" for number in range(1, 11)]
SOURCE_IDS = {"blog", "logs", "experiments", "qwen", "qwen-results",
              "checkpoint-release", "gemma", "transformer-circuits", "tracr",
              "hypernetworks", "rome", "refusal-direction"}
# Exact, inspected public-source version identifiers. Never exempt arbitrary hashes.
PUBLIC_VERSIONS = {
    "4d09ba6d6a7e891dd8063974dfe81b3d78e3494f": "github.com/RikiyaT/lm_understand-logs",
    "2fc06364715b967f1860aea9cf38778875588b17": "huggingface.co/Qwen/Qwen3.5-0.8B",
    "d1671a178705bcab7644806d23c535517f35723b":
        "huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming",
    "ac82b4e820549b854eebf28ce6dedaf9fdfa17b3": "huggingface.co/google/gemma-3-270m-it",
}
# Exact code snapshots inspected during the new study. These public hashes are
# permitted only when paired with their specific source repository in prose.
DIFFUSION_VERSIONS = {
    "f8b8c0f49dc92a430bae41585f9d467d3618fe2f": "github.com/eric-mitchell/direct-preference-optimization",
    "9bc5f3d5f0f3aa09f384238b73196826e24508eb": "github.com/SalesforceAIResearch/DiffusionDPO",
    "1249c845e4502ceca3efcb49d2135d533a449b20": "github.com/YangYongJin/FiFA-Official-Repo",
    "879042cf5707f8b90daa98d147d7deac2317c5da": "github.com/yifan123/flow_grpo",
    "cbb14f84b8312b620390dfcbe2fab69c1383b104": "github.com/NVlabs/DiffusionNFT",
    "f386d1190a9918a20705837a963380c1a21d9960": "github.com/xiefan-guo/shortft",
    "78f8051059b34fef8e0032ccb40561c23a2ddbbb": "github.com/THUDM/ImageReward",
    "335e4c2c3452df52e32fe3c583d9458235e7d9e1": "github.com/linzhiqiu/t2v_metrics",
    "511960d61a777b2008cd486a85a090ba96792a32": "github.com/THUDM/VisionReward",
    "4ad86b4fbfc5db594f3a2750ff9c39fdc8ee6115": "github.com/NVlabs/GDPO",
    "f1ad765bc9a330e6cf387f95e9c1e5a6c4bb2d02": "github.com/Qwen-Applications/GD2PO",
    "8b33abd84f360473f05e5a750aef36e974340cce": "github.com/verl-project/verl",
}
TRAINING_VERSIONS = {
    "74e23eb6f830fef4a9e96a92f6f6262214cbb9a8":
        "huggingface.co/datasets/nvidia/Nemotron-Post-Training-Dataset-v1",
    "0df3cf37f2abefb380370cfb02eabea2a35ae782":
        "huggingface.co/datasets/Agent-Ark/Toucan-1.5M",
    "ba3d3aaff23b3f4cac7a14672b4f6e293d97c98b": "github.com/huggingface/Math-Verify",
    "49b07130b3fcd12f2d064bba7c43869543a0e7e7": "github.com/open-thought/reasoning-gym",
    "28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24": "github.com/LiveCodeBench/LiveCodeBench",
    "24c91001cf99ba642be791e099d358f4dfe955f5": "github.com/sgl-project/sglang",
    "540ea919e45b8b929198abce008a103be9cfc779": "github.com/THUDM/slime",
}
AGENTIC_VERSIONS = {
    "8493321013c02eef6cf79ca2594811f53c6fdac1": "github.com/datawhalechina/agentic-rl-lab",
}


def documents():
    return {name: (TOPIC / name).read_text(encoding="utf-8") for name in FILES}


def figures():
    return json.loads((ROOT / "scripts/figures/deep-learning.json").read_text(encoding="utf-8"))


def diffusion_figures():
    return json.loads((ROOT / "scripts/figures/diffusion.json").read_text(encoding="utf-8"))


def training_figures():
    return json.loads((ROOT / "scripts/figures/training-recipes.json").read_text(encoding="utf-8"))


def agentic_figures():
    return json.loads((ROOT / "scripts/figures/agentic-rl-lab.json").read_text(encoding="utf-8"))


def readable_samples(source):
    # Display math and inline TeX are tested in a real browser. Typography in
    # script[type=math/tex] is intentionally different from Markdown delimiters.
    math_block = False
    lines = []
    for line in source.splitlines():
        if line.strip() == "$$":
            math_block = not math_block
            continue
        if not math_block and "$" not in line:
            lines.append(line)
    return prose_samples("\n".join(lines))


class DeepLearningChecks(PaymentsChecks):
    def assert_public_study(self, text, label):
        for version in PUBLIC_VERSIONS:
            text = text.replace(version, "")
        for version, repository in {**DIFFUSION_VERSIONS, **TRAINING_VERSIONS,
                                    **AGENTIC_VERSIONS}.items():
            # Exempt only the exact revision in its verified repository URL.
            # Keep the rest of the path visible to all other privacy checks.
            text = re.sub("(" + re.escape("https://" + repository) + r"/(?:blob|tree)/)" +
                          re.escape(version) + r'(?=/|[)\s"<>]|$)', r"\1public-revision", text)
        self.assert_public(text, label)


class DeepLearningSourceTests(DeepLearningChecks):
    def test_exact_public_files_and_no_unpublished_attachments(self):
        allowed = set(FILES + DIFFUSION_FILES + TRAINING_FILES + AGENTIC_FILES) | {f"images/{figure['id']}.{suffix}"
                               for figure in figures() + diffusion_figures() + training_figures() + agentic_figures()
                               for suffix in ("svg", "png")}
        self.assertEqual({path.relative_to(TOPIC).as_posix()
                          for path in TOPIC.rglob("*") if path.is_file()}, allowed)
        sources = documents()["weight-space-programming-sources.md"]
        for version, repository in PUBLIC_VERSIONS.items():
            self.assertIn(repository, sources)
            self.assertIn(version, sources)
        for path in [ROOT / "scripts/figures/deep-learning.json",
                     ROOT / "scripts/figures/diffusion.json",
                     ROOT / "scripts/figures/training-recipes.json",
                     ROOT / "scripts/figures/agentic-rl-lab.json", *TOPIC.rglob("*")]:
            if path.is_file() and path.suffix != ".png":
                self.assert_public_study(path.read_text(encoding="utf-8"), path.name)
        for value in ("f" * 40, "https://private.sharepoint.com/document",
                      "secret-token.docx", "/home/example/private.md"):
            with self.subTest(value=value[:8]), self.assertRaises(AssertionError):
                self.assert_public_study(value, "synthetic fixture")

    def test_ten_complete_sections_and_twelve_self_test_questions(self):
        docs = documents()
        book = docs["weight-space-programming.md"]
        headings = list(re.finditer(r"(?m)^## (\d{2}) (.+)$", book))
        self.assertEqual([int(match[1]) for match in headings], list(range(1, 11)))
        self.assertEqual(Page(book).ids, LESSONS)
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index < 9 else len(book)
            section = ILLUSTRATION.sub("", book[heading.end():end])
            self.assertGreater(len(section.strip()), 250, f"Stub section {index + 1}")
        lab = docs["weight-space-programming-lab.md"]
        questions, answers = lab.split("## 12 道自测\n", 1)[1].split("## 参考答案\n", 1)
        for text in (questions, answers):
            self.assertEqual([int(number) for number in re.findall(r"(?m)^(\d+)\. ", text)],
                             list(range(1, 13)))
        for term in ("131,072", "130,188", "隐藏状态", "MLP 激活", "Pass@4",
                     "25 题", "不是本课重新测到", "梯度", "置换", "回滚"):
            self.assertIn(term, book)
        for result in ("(11, 121)", "(121, 121)", "0.0", "15", "3.0"):
            self.assertIn(result, lab)

    def test_all_local_links_and_explicit_fragments_resolve(self):
        for name, text in documents().items():
            self.assertEqual(len(Page(text).ids), len(set(Page(text).ids)))
            for target in [target for _, target in markdown_links(text)] + Page(text).links:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    continue
                path = ((TOPIC / name).parent / unquote(parts.path)).resolve() \
                    if parts.path else TOPIC / name
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(), f"Broken local link in {name}: {target}")
                if parts.fragment:
                    self.assertIn(unquote(parts.fragment), Page(path.read_text(encoding="utf-8")).ids)
        sources = documents()["weight-space-programming-sources.md"]
        self.assertTrue(SOURCE_IDS.issubset(Page(sources).ids))
        self.assertIn("2026-11-03", sources)
        self.assertIn("不是重新运行模型", sources)
        self.assertIn("同一题多次生成", sources)
        self.assertIn("基线仅 25 题", sources)
        self.assertIn('<a id="experiments"></a>\n\n## 2. 实验权限矩阵与边界', sources)
        self.assertIn('<a id="qwen-results"></a>\n\n### Qwen：主结论可以对上记录，但要保留协议',
                      sources)
        self.assertGreater(len([target for _, target in markdown_links(sources)
                                if urlsplit(target).scheme == "https"]), 25)

    def test_nine_figures_ten_placements_exact_bytes_and_relative_paths(self):
        manifest = figures()
        self.assertEqual(len(manifest), 9)
        self.assertEqual(len({figure["id"] for figure in manifest}), 9)
        self.assertEqual(sum(len(figure["placements"]) for figure in manifest), 10)
        spec = importlib.util.spec_from_file_location("wsp_figures", ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        markers = {name: [] for name in FILES}
        images = {name: [] for name in FILES}
        for suffix in ("svg", "png"):
            self.assertEqual({path.stem for path in (TOPIC / "images").glob(f"wsp-*.{suffix}")},
                             {figure["id"] for figure in manifest})
        for figure in manifest:
            self.assertEqual(figure["topic"], "deep-learning")
            self.assertRegex(figure["id"], r"^wsp-[a-z0-9-]+$")
            svg = TOPIC / f"images/{figure['id']}.svg"
            self.assertEqual(svg.read_text(encoding="utf-8"),
                             renderer.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertIn(name, FILES)
                text = documents()[name]
                self.assertEqual(text.splitlines().count(placement["after"]), 1)
                marker = (figure["id"] + "-" +
                          hashlib.sha256(placement["after"].encode()).hexdigest()[:10])
                blocks = [body for identity, body in ILLUSTRATION.findall(text) if identity == marker]
                self.assertEqual(len(blocks), 1)
                image_path = os.path.relpath(svg.with_suffix(".png"), (TOPIC / name).parent)
                self.assertIn(f"]({image_path})", blocks[0])
                self.assertIn(f"*图：{figure['title']}。", blocks[0])
                self.assertRegex(text, re.escape(placement["after"]) +
                                 r"\n\s*<!-- illustration: " + marker + " -->")
                markers[name].append(marker)
                images[name].append(image_path)
        for name, text in documents().items():
            self.assertEqual(Counter(identity for identity, _ in ILLUSTRATION.findall(text)),
                             Counter(markers[name]))
            self.assertEqual(Counter(target for image, target in markdown_links(text) if image),
                             Counter(images[name]))

    def test_navigation_and_source_code_links_are_complete(self):
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        urls = set(re.findall(r"(?m)^\s+url:\s*(/wiki/topics/deep-learning/\S*)\s*$", navigation))
        expected = {"/" + relative.replace("index.html", "") for relative in ROUTES.values()}
        expected |= {"/wiki/topics/deep-learning/weight-space-programming.html#" + lesson
                     for lesson in LESSONS}
        expected |= {"/" + relative.replace("index.html", "")
                     for relative in DIFFUSION_ROUTES.values()}
        expected |= {"/" + relative.replace("index.html", "")
                     for relative in TRAINING_ROUTES.values()}
        expected |= {"/" + relative.replace("index.html", "")
                     for relative in AGENTIC_ROUTES.values()}
        self.assertEqual(urls, expected)
        home = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("](wiki/topics/deep-learning/README.md)", home)
        lab = documents()["weight-space-programming-lab.md"]
        for path in ("scripts/weight_space_lab.py", "tests/test_weight_space_lab.py"):
            self.assertTrue((ROOT / path).is_file())
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + path, lab)


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll or set DEEP_LEARNING_SITE")
class DeepLearningSiteTests(DeepLearningChecks):
    def page(self, relative):
        path = SITE / relative
        self.assertTrue(path.is_file(), relative)
        return Page(path.read_text(encoding="utf-8"))

    def local_target(self, relative, target):
        page = self.page(relative)
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            return None
        route = page.base + "/" + relative
        if route.endswith("index.html"):
            route = route[:-10]
        resolved = urlsplit(urljoin(route, target))
        self.assertTrue(resolved.path.startswith(page.base + "/"))
        local = (SITE / unquote(resolved.path[len(page.base) + 1:])).resolve()
        if resolved.path.endswith("/"):
            local /= "index.html"
        self.assertTrue(local.is_relative_to(SITE))
        self.assertTrue(local.is_file(), target)
        if resolved.fragment and local.suffix == ".html":
            self.assertIn(unquote(resolved.fragment),
                          self.page(local.relative_to(SITE).as_posix()).ids)
        return local

    def test_five_static_pages_search_links_sidebar_and_meaningful_prose(self):
        index = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        base = self.page(ROUTES["README.md"]).base
        records = [item for item in index if urlsplit(item["url"]).path.startswith(
            base + "/wiki/topics/deep-learning/")]
        self.assertEqual(Counter(item["url"] for item in records),
                         Counter(base + "/" + route.replace("index.html", "")
                                 for route in [*ROUTES.values(), *DIFFUSION_ROUTES.values(),
                                               *TRAINING_ROUTES.values(), *AGENTIC_ROUTES.values()]))
        for name, relative in ROUTES.items():
            with self.subTest(page=name):
                source = documents()[name]
                page = self.page(relative)
                self.assertEqual(page.article_count, 1)
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertTrue(set(Page(source).ids).issubset(page.article_ids))
                body = normalized("".join(page.text))
                record = next(item for item in records
                              if item["url"] == base + "/" + relative.replace("index.html", ""))
                samples = list(readable_samples(source))
                self.assertGreater(len(samples), 15)
                for sample in samples:
                    self.assertIn(sample, body, f"Missing prose in {name}")
                    self.assertIn(sample, normalized(record["text"]), f"Missing search prose in {name}")
                for target in page.article_links:
                    local = self.local_target(relative, target)
                    if local:
                        self.assertNotEqual(local.suffix, ".md")
                for lesson in LESSONS:
                    self.assertIn(base + "/wiki/topics/deep-learning/weight-space-programming.html#"
                                  + lesson, page.sidebar_links)
                self.assert_public_study((SITE / relative).read_text(encoding="utf-8"), relative)

    def test_ten_built_illustrations_match_source_and_caption_heading(self):
        placed = {}
        for name, relative in ROUTES.items():
            page = self.page(relative)
            self.assertEqual(len(page.images), 9 if name == "weight-space-programming.md"
                             else 1 if name == "weight-space-programming-lab.md" else 0)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    path = self.local_target(relative, value["src"])
                    self.assertTrue(value["alt"])
                    placed[(name, path.stem)] = heading
        for figure in figures():
            for suffix in ("svg", "png"):
                self.assertEqual((SITE / f"wiki/topics/deep-learning/images/{figure['id']}.{suffix}").read_bytes(),
                                 (TOPIC / f"images/{figure['id']}.{suffix}").read_bytes())
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertEqual(placed[(name, figure["id"])], placement["after"].lstrip("# "))

    def test_only_expected_public_files_are_published(self):
        all_files = FILES + DIFFUSION_FILES + TRAINING_FILES + AGENTIC_FILES
        allowed = set(all_files) | {name.replace(".md", ".html") for name in all_files} | {
            "index.html", "README.html", "diffusion/index.html", "diffusion/README.html",
            "training/index.html", "training/README.html",
            "training/rufus-air/index.html", "training/rufus-air/README.html",
            "training/agentic-rl-lab/index.html", "training/agentic-rl-lab/README.html"
        } | {f"images/{figure['id']}.{suffix}"
             for figure in figures() + diffusion_figures() + training_figures() + agentic_figures()
             for suffix in ("svg", "png")}
        for path in (SITE / "wiki/topics/deep-learning").rglob("*"):
            if path.is_file():
                self.assertIn(path.relative_to(SITE / "wiki/topics/deep-learning").as_posix(), allowed)
        self.assertFalse((SITE / "scripts").exists())
        self.assertFalse((SITE / "tests").exists())


if __name__ == "__main__":
    unittest.main()
