"""Offline migration, public-source and built-page checks; no model execution."""

import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from test_payments import Page, PaymentsChecks, markdown_links, normalized


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "wiki/topics/deep-learning/openmoss"
SITE = Path(os.environ.get("OPENMOSS_SITE", ROOT / "_site")).resolve()
CHAPTERS = (
    "01-audio-representation-and-generation.md",
    "02-streaming-video-time-and-cache.md",
    "03-audiovisual-latents-and-joint-denoising.md",
    "04-image-layout-supervision-and-specification.md",
    "05-world-action-and-embodied-agent.md",
    "06-agent-memory-and-executable-evaluation.md",
    "07-long-context-and-diffusion-optimization.md",
    "08-mechanistic-interpretability.md",
    "09-foundation-and-omni-models.md",
    "10-audio-understanding-and-transcription.md",
    "11-robotics-policy-and-control.md",
    "12-honesty-and-long-context-safety.md",
    "13-diffusion-language-models.md",
    "14-post-training-and-rl.md",
)
FILES = ("README.md", "learning-roadmap.md", *CHAPTERS, "sources.md")
OPENMOSS_FILES = tuple("openmoss/" + name for name in FILES) + ("openmoss/sources.json",)
REGISTRY = json.loads((STUDY / "sources.json").read_text())
# Whitelist from the frozen registry, itself locked below. Do not exempt a
# revision in another repository, bare prose, or an unpublished attachment.
OPENMOSS_VERSIONS = {}
for snapshot in REGISTRY["snapshots"]:
    match = re.fullmatch(r"https://([^/]+/[^/]+/[^/]+)/tree/([a-f0-9]{40})",
                         snapshot["url"])
    if not match:
        raise ValueError("Invalid public snapshot URL")
    OPENMOSS_VERSIONS[match[2]] = match[1]
OPENMOSS_PUBLIC_PDFS = (
    "https://proceedings.iclr.cc/paper_files/paper/2026/file/"
    "20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf",
    "https://proceedings.iclr.cc/paper_files/paper/2026/file/"
    "7e57d4c3bb2bd2396a551e7aeea19aed-Paper-Conference.pdf",
)
REGISTRY_SHA = "54a287cd985677b2f9e9870671d6aca7cff8ebd853a4c76398684d5fcd287077"
ROUTES = {name: "wiki/topics/deep-learning/openmoss/" +
          name.replace("README.md", "index.html").replace(".md", ".html")
          for name in FILES}
MATH_COUNTS = (9, 0, 0, 0, 2, 8, 4, 10, 1, 3, 1, 6, 3, 8)
CONTRACTS = {
    CHAPTERS[0]: ("RVQ", "Delay", "MOSS-Speech", "TTSD"),
    CHAPTERS[1]: ("XRoPE", "49,152", "Realtime-SFT", "未来"),
    CHAPTERS[2]: ("OmniVAE", "MOVA", "sigma", "CFG"),
    CHAPTERS[3]: ("MOSS-Image", "OCR", "Elo", "布局"),
    CHAPTERS[4]: ("D2PO", "WAP", "EasyWAM", "ETA"),
    CHAPTERS[5]: ("UnifiedToolHub", "AgentHPOBench", "ContextWeave", "过期"),
    CHAPTERS[6]: ("RoPE++", "LongLLaDA", "ReAttention", "PPL"),
    CHAPTERS[7]: ("Lorsa", "CRM", "JumpReLU", "因果"),
    CHAPTERS[8]: ("700B", "110", "AnyGPT", "SoundStorm"),
    CHAPTERS[9]: ("DeepStack", "cpCER", "MOSS-Music", "12.5"),
    CHAPTERS[10]: ("FAST+", "DAgger", "H-GPT", "实机"),
    CHAPTERS[11]: ("p_q^{10}", "45.42", "Coverage", "LongSafety"),
    CHAPTERS[12]: ("Sparse-dLLM", "cached", "31.72", "近似"),
    CHAPTERS[13]: ("top-k=50", "step_map", "BandPO", "Planner-R1"),
}


def public_source_text(text):
    for revision, repository in OPENMOSS_VERSIONS.items():
        text = re.sub(
            "(" + re.escape("https://" + repository) + r"/(?:blob|tree|raw)/)" +
            revision + r'(?=/|[)\s"<>]|$)', r"\1public-revision", text)
    for url in OPENMOSS_PUBLIC_PDFS:
        text = text.replace(url, "https://proceedings.iclr.cc/public-paper.pdf")
    return text


class TopicState(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.topics = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "details" and "nav-topic" in attrs.get("class", "").split():
            self.topics.append((attrs["data-topic"], "open" in attrs))


class OpenMOSSSourceTests(PaymentsChecks):
    def test_exact_migration_scope_and_original_research_date(self):
        self.assertEqual({p.relative_to(STUDY).as_posix()
                          for p in STUDY.rglob("*") if p.is_file()},
                         set(FILES) | {"sources.json"})
        for name in FILES:
            text = (STUDY / name).read_text()
            self.assertTrue(text.startswith("# "), name)
            self.assertIn("2026-10-17", text)
            self.assertGreater(len(text), 1200, name)
            self.assert_public(public_source_text(text), name)
            self.assertNotRegex(text, r"/research-notes/|personal-research-journal|"
                                     r"/home/|/tmp/|主会处理|本文只编辑")
        for name in ("README.md", "learning-roadmap.md", "sources.md"):
            self.assertIn("2026-11-04", (STUDY / name).read_text())
        for name, phrases in CONTRACTS.items():
            text = (STUDY / name).read_text()
            for phrase in phrases:
                self.assertIn(phrase, text, name)

    def test_math_and_reference_adaptation_is_complete(self):
        total = 0
        for name, expected in zip(CHAPTERS, MATH_COUNTS):
            text = (STUDY / name).read_text()
            prose = re.sub(r"```[\s\S]*?```", "", text)
            self.assertNotRegex(prose, r"\\[\[\]()]")
            self.assertNotIn("$$\n$$", prose)
            count = len(re.findall(r"(?m)^\$\$$", prose))
            self.assertEqual(count, 2 * expected, name)
            total += count // 2
            self.assertEqual(len(re.findall(r"(?m)^```", text)) % 2, 0)
            definitions = set(re.findall(r"(?m)^\[([^\]]+)\]:", text))
            prose = re.sub(r"`[^`\n]*`", "", prose)
            for label in re.findall(r"\[[^\]\n]+\]\[([^\]\n]+)\]", prose):
                self.assertIn(label, definitions, name)
        self.assertEqual(total, 55)

    def test_local_links_and_public_index_are_portable(self):
        for name in FILES:
            source = (STUDY / name).read_text()
            link_text = re.sub(r"(?m)^(\[\^[^\]]+\]):", r"\1 —", source)
            for _, target in markdown_links(link_text):
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    self.assertEqual(parts.scheme, "https", name)
                    continue
                self.assertFalse(parts.path.startswith("/"), (name, target))
                file = (STUDY / unquote(parts.path)).resolve() if parts.path else STUDY / name
                self.assertTrue(file.is_relative_to(ROOT))
                self.assertTrue(file.is_file(), (name, target))
                if parts.fragment:
                    self.assertIn(unquote(parts.fragment), Page(file.read_text()).ids)
        index = (STUDY / "README.md").read_text()
        for name in CHAPTERS:
            self.assertIn(f"]({name})", index)
        for entry in ("README.md", "wiki/topics/README.md",
                      "wiki/topics/deep-learning/README.md",
                      "wiki/topics/physical-ai/README.md"):
            self.assertIn("openmoss/README.md", (ROOT / entry).read_text())

    def test_registry_is_frozen_and_exemptions_stay_narrow(self):
        self.assertEqual(hashlib.sha256((STUDY / "sources.json").read_bytes()).hexdigest(),
                         REGISTRY_SHA)
        self.assertEqual(REGISTRY["research_date"], "2026-10-17")
        self.assertEqual(REGISTRY["wiki_adapted_date"], "2026-11-04")
        self.assertFalse(REGISTRY["model_experiments_rerun"])
        self.assertEqual(len(OPENMOSS_VERSIONS), 44)
        self.assertEqual(len(REGISTRY["papers"]), 36)
        self.assert_public(public_source_text((STUDY / "sources.json").read_text()), "registry")
        for revision, repository in OPENMOSS_VERSIONS.items():
            self.assert_public(public_source_text(
                f"https://{repository}/blob/{revision}/file.py"), "public fixture")
            for bad in (revision, f"https://unknown.invalid/blob/{revision}/file.py",
                        f"https://{repository}/blob/{revision}/private.docx"):
                with self.assertRaises(AssertionError):
                    self.assert_public(public_source_text(bad), "negative fixture")

    def test_navigation_routes_and_topic_boundaries(self):
        navigation = (ROOT / "_data/navigation.yml").read_text()
        segment = navigation.split("  - label: OpenMOSS 综合研究\n", 1)[1].split(
            "  - label: 支付行业 101\n", 1)[0]
        actual = re.findall(r"(?m)^\s+url: (/wiki/topics/deep-learning/openmoss/\S*)\s*$",
                            segment)
        expected = {"/" + route.replace("index.html", "") for route in ROUTES.values()}
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), len(expected) + 1)  # topic URL plus overview item
        self.assertNotIn("group:", segment)  # leave the existing six DL groups unchanged
        self.assertNotIn("p_q^{10}", (STUDY / CHAPTERS[5]).read_text())
        self.assertNotIn("step_map", (STUDY / CHAPTERS[6]).read_text())

    def test_tagged_equations_keep_local_scrolling_not_document_overflow(self):
        css = (ROOT / "assets/css/style.scss").read_text()
        self.assertRegex(css, r'mjx-container\[display="true"\]\[width="full"\]\s*'
                              r'\{\s*min-width:\s*0\s*!important;')
        self.assertRegex(css, r'mjx-container\[display="true"\]\s*\{[^}]*overflow-x:\s*auto')
        self.assertRegex(css, r'body\.openmoss-study mjx-container:not\(\[display="true"\]\)'
                              r'\s*\{[^}]*display:\s*inline-block;[^}]*max-width:\s*100%;')


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll first")
class OpenMOSSSiteTests(PaymentsChecks):
    def test_full_pages_search_math_and_child_navigation(self):
        records = json.loads((SITE / "search.json").read_text())
        selected = [r for r in records if "/wiki/topics/deep-learning/openmoss/" in r["url"]]
        self.assertEqual(len(selected), len(FILES))
        for name, route in ROUTES.items():
            html = (SITE / route).read_text()
            page = Page(html)
            self.assertEqual(page.article_count, 1, name)
            self.assertEqual(len(page.ids), len(set(page.ids)), name)
            self.assert_public(public_source_text(html), route)
            active = [topic for topic, opened in TopicState(html).topics if opened]
            self.assertEqual(active, [page.base + "/wiki/topics/deep-learning/openmoss/"])
            title = (STUDY / name).read_text().splitlines()[0][2:]
            record = next(r for r in selected
                          if r["url"] == page.base + "/" + route.replace("index.html", ""))
            self.assertEqual(record["title"], title)
            if name in CHAPTERS:
                expected = MATH_COUNTS[CHAPTERS.index(name)]
                self.assertEqual(len(re.findall(r"(?m)^\\\[", html)), expected, name)
                for phrase in CONTRACTS[name]:
                    if phrase != "p_q^{10}":
                        self.assertIn(phrase, html, name)
            for target in page.article_links:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    continue
                url = urlsplit(urljoin(page.base + "/" + route, target))
                self.assertTrue(url.path.startswith(page.base + "/"))
                file = SITE / unquote(url.path[len(page.base) + 1:])
                if url.path.endswith("/"):
                    file /= "index.html"
                self.assertTrue(file.is_file(), (name, target))
                self.assertNotEqual(file.suffix, ".md", (name, target))

    def test_only_public_topic_files_and_root_entrypoints_publish(self):
        published = {p.relative_to(SITE / "wiki/topics/deep-learning/openmoss").as_posix()
                     for p in (SITE / "wiki/topics/deep-learning/openmoss").rglob("*")
                     if p.is_file()}
        expected = set(FILES) | {name.replace(".md", ".html") for name in FILES} | {
            "index.html", "sources.json"}
        self.assertEqual(published, expected)
        for route in ("index.html", "wiki/topics/index.html",
                      "wiki/topics/deep-learning/index.html",
                      "wiki/topics/physical-ai/index.html"):
            self.assertIn("/wiki/topics/deep-learning/openmoss/", (SITE / route).read_text())
        self.assertFalse((SITE / "scripts").exists())
        self.assertFalse((SITE / "tests").exists())


if __name__ == "__main__":
    unittest.main()
