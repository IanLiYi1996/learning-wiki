"""Offline payments regressions; use PAYMENTS_SITE to select an existing build.

python -B -m unittest discover -s tests -p test_payments.py -v
"""

from collections import Counter
import hashlib
from html import unescape
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/payments"
SITE = Path(os.environ.get("PAYMENTS_SITE", ROOT / "_site")).resolve()
CORE_FILES = ("README.md", "payment-industry-101.md", "glossary.md",
              "learning-roadmap.md", "sources.md")
CHAPTERS = (
    "13-card-products-and-operations",
    "14-in-person-and-offline-payments",
    "15-recurring-payments",
    "16-merchant-lifecycle",
    "17-treasury-and-liquidity",
    "18-messages-and-payment-security",
    "19-ledgers-and-reliable-payment-engineering",
    "20-china-and-regulatory-maps",
    "21-cash-mobile-money-and-local-methods",
    "22-cbdc-tokenised-deposits-and-stablecoins",
)
EXTENSION_FILES = tuple(f"chapters/{name}.md" for name in CHAPTERS)
FILES = CORE_FILES + EXTENSION_FILES
ROUTES = {name: "wiki/topics/payments/" +
          ("index.html" if name == "README.md" else name.replace(".md", ".html"))
          for name in FILES}
LESSONS = [f"lesson-{number:02d}" for number in range(1, 13)]
EXTENSION_LESSONS = [f"lesson-{number}" for number in range(13, 23)]
MANIFESTS = tuple(ROOT / f"scripts/figures/{name}.json" for name in (
    "payments", "payments-foundations", "payments-operations",
    "payments-engineering-regions", "payments-digital-money",
))
LINK = re.compile(r'(!?)\[[^\]\n]*\]\(\s*(?:<([^>]+)>|([^\s)]+))[^)]*\)')
ILLUSTRATION = re.compile(
    r"<!-- illustration: ([a-z0-9-]+) -->\n(.*?)<!-- /illustration: \1 -->",
    re.S,
)
# Generic rules cover unpublished attachments and provenance without copying
# private source identifiers into a public regression file.
PRIVATE = {
    "email": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|mailto:",
    "private document host": r"\b(?:[a-z0-9-]+\.)*(?:sharepoint|onedrive)\.com\b",
    "local path": r"file:/{2,}|/(?:home|Users|Volumes|private|tmp)/|\b[a-z]:[\\/]|~/",
    "attachment": r"\.(?:pptx?|docx?|xlsx?|mp4|mov|mkv|m4a|wav|zip)\b",
    "attachment digest": r"(?<![a-f0-9])[a-f0-9]{20,64}(?![a-f0-9])",
    "private provenance map": r"\b(?:[a-z]+[-_])?source[-_]map\b",
    "internal workspace": r"\bresearch[-_/ ]+internal\b",
    "confidential session": r"\b(?:internal|confidential)[-_ ]+(?:meeting|session|briefing)\b",
    "meeting recording": r"会议录屏|会议录像|(?:meeting|session)[-_ ]+recording",
}


def markdown_links(text):
    links = [(bool(match[1]), match[2] or match[3]) for match in LINK.finditer(text)]
    links.extend((False, match[1]) for match in re.finditer(
        r"(?m)^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?", text))
    return links


def normalized(text):
    return " ".join(unescape(text).split())


def prose_samples(text):
    """Plain prose/table cells, not navigation, image alt text, or code blocks."""
    fenced = False
    for line in ILLUSTRATION.sub("", text).splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.strip() or line.startswith(("#", "<", "![")):
            continue
        cells = line.strip("|").split("|") if line.startswith("|") else [line]
        for cell in cells:
            cell = re.sub(r"^\s*>\s?", "", cell)
            cell = LINK.sub(lambda match: match[0].split("](", 1)[0].lstrip("!["), cell)
            cell = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", cell)
            cell = normalized(cell.replace("**", "").replace("`", ""))
            if len(cell) >= 12 and not re.fullmatch(r"[-: ]+", cell):
                yield cell


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.article_ids = []
        self.links = []
        self.article_links = []
        self.sidebar_links = []
        self.images = []
        self.scripts = []
        self.catalogue_links = []
        self.headings = []
        self.events = []
        self.text = []
        self.base = None
        self.article = False
        self.sidebar = False
        self.article_count = 0
        self.heading = None
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "body":
            self.base = attrs.get("data-baseurl", "").rstrip("/")
        if tag == "article" and "article-content" in attrs.get("class", "").split():
            self.article = True
            self.article_count += 1
        if tag == "aside" and "site-sidebar" in attrs.get("class", "").split():
            self.sidebar = True
        if attrs.get("id"):
            self.ids.append(attrs["id"])
            if self.article:
                self.article_ids.append(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
            if self.article:
                self.article_links.append(attrs["href"])
            if self.sidebar:
                self.sidebar_links.append(attrs["href"])
            if "topic-row" in attrs.get("class", "").split():
                self.catalogue_links.append(attrs["href"])
        if tag == "img" and self.article:
            self.images.append(attrs)
            self.events.append(("image", attrs))
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        if self.article and tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading = (tag, [])
        if self.article and tag in {"p", "li", "td", "th", "br"}:
            self.text.append(" ")

    def handle_endtag(self, tag):
        if self.heading and tag == self.heading[0]:
            heading = (tag, normalized("".join(self.heading[1])))
            self.headings.append(heading)
            self.events.append(("heading", heading))
            self.heading = None
        if tag == "article":
            self.article = False
        if tag == "aside":
            self.sidebar = False
        if self.article and tag in {"p", "li", "td", "th"}:
            self.text.append(" ")

    def handle_data(self, data):
        if self.article:
            self.text.append(data)
        if self.heading:
            self.heading[1].append(data)


class PaymentsChecks(unittest.TestCase):
    def assert_public(self, text, label):
        decoded = unquote(unescape(text))
        if label.endswith(".html"):
            # The shared layout emits a Git revision in these two exact places.
            # Do not exempt hashes in prose, downloads, or arbitrary URLs.
            decoded = re.sub(
                r'(/assets/(?:css|js)/[a-z0-9._/-]+\?v=)[a-f0-9]{40}(?=["\'])',
                r"\1", decoded, flags=re.I)
            decoded = re.sub(
                r'(\bdata-index-version=["\'])[a-f0-9]{40}(["\'])',
                r"\1\2", decoded, flags=re.I)
        for kind, pattern in PRIVATE.items():
            # Do not echo potentially private contents in assertion output.
            self.assertFalse(bool(re.search(pattern, decoded, re.I)),
                             f"Nonpublic {kind} in {label}")

    def documents(self):
        return {name: (TOPIC / name).read_text(encoding="utf-8") for name in FILES}

    def figures(self):
        return [figure for manifest in MANIFESTS
                for figure in json.loads(manifest.read_text(encoding="utf-8"))]

    def require_figures(self):
        if not any((TOPIC / "images").glob("payment-*")):
            self.skipTest("Payments figure generation has not completed yet")

    def assert_asset_pair(self, svg_path, png_path, figure):
        self.assertTrue(svg_path.is_file(), f"Missing SVG: {svg_path}")
        self.assertTrue(png_path.is_file(), f"Missing PNG: {png_path}")
        svg_text = svg_path.read_text(encoding="utf-8")
        svg = ET.fromstring(svg_text)
        namespace = "{http://www.w3.org/2000/svg}"
        self.assertEqual(svg.tag, namespace + "svg")
        self.assertEqual(svg.findtext(namespace + "title"), figure["title"])
        self.assertEqual(svg.findtext(namespace + "desc"), figure["subtitle"])
        self.assertNotRegex(svg_text, r"(?i)<script|<foreignObject|@import|\bhref\s*=")
        self.assertNotIn("https://", svg_text)
        self.assertNotIn("file://", svg_text)
        data = png_path.read_bytes()
        self.assertGreater(len(data), 24)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(data[12:16], b"IHDR")
        self.assertEqual(struct.unpack(">II", data[16:24]),
                         (int(svg.attrib["width"]) * 2, int(svg.attrib["height"]) * 2))


class PaymentsSourceTests(PaymentsChecks):
    def test_privacy_rules_reject_generic_private_material_and_encoded_paths(self):
        for value in ("person@example.invalid", "https://team.sharepoint.com/document",
                      "file:///Users/example/notes", "%2Fhome%2Fexample%2Fnotes",
                      "original.pptx", "0123456789abcdef0123456789abcdef",
                      "private-source-map.md", "research_internal/notes",
                      "internal meeting", "meeting recording"):
            with self.subTest(example=value), self.assertRaises(AssertionError):
                self.assert_public(value, "synthetic fixture")

    def test_privacy_rules_allow_only_template_revision_hashes_not_body_hashes(self):
        revision = "0123456789abcdef" * 2 + "01234567"
        template = (f'<script src="/assets/js/wiki.js?v={revision}"></script>'
                    f'<body data-index-version="{revision}">公开教学内容</body>')
        self.assert_public(template, "fixture.html")
        self.assert_public("https://www.bis.org/publications/example.pdf", "fixture.md")
        for value in (f"<p>{revision}</p>", f'<a href="attachment?v={revision}">文件</a>'):
            with self.subTest(location=value[:12]), self.assertRaises(AssertionError):
                self.assert_public(value, "fixture.html")

    def test_fifteen_public_documents_and_no_unpublished_attachments(self):
        self.assertEqual({path.relative_to(TOPIC).as_posix()
                          for path in TOPIC.rglob("*.md")}, set(FILES))
        allowed = set(FILES) | {
            f"images/{figure['id']}.{suffix}"
            for figure in self.figures() for suffix in ("svg", "png")
        }
        for path in TOPIC.rglob("*"):
            if path.is_file():
                self.assertIn(path.relative_to(TOPIC).as_posix(), allowed)

    def test_twelve_complete_lessons_with_unique_explicit_anchors(self):
        book = self.documents()["payment-industry-101.md"]
        headings = list(re.finditer(r"(?m)^## (\d{2}) (.+)$", book))
        self.assertEqual([int(match[1]) for match in headings], list(range(1, 13)))
        self.assertEqual(Page(book).ids, LESSONS)
        self.assertEqual(re.findall(r"\]\(#(lesson-\d{2})\)", book), LESSONS)
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index < 11 else len(book)
            section = ILLUSTRATION.sub("", book[heading.end():end])
            with self.subTest(lesson=index + 1):
                self.assertGreater(len(section.strip()), 300, "Lesson is only a stub")
                self.assertGreaterEqual(len(re.findall(r"(?m)^### ", section)), 3)
                if index < 11:
                    self.assertIn(f"检查理解 {index + 1}", section)
        self.assertIn("故障恢复能证明不丢账、不重账", book)
        self.assertIn("最后，把领域压缩成八句话", book)

    def test_ten_substantive_extension_lessons_with_sources_and_self_tests(self):
        expected_terms = (
            ("借记", "信用", "预付", "三方", "四方", "换卡"),
            ("EMV", "NFC", "SoftPOS", "L1", "L2", "L3", "离线"),
            ("CIT", "MIT", "SCA", "重试", "取消"),
            ("KYB", "MCC", "准备金", "退出"),
            ("流动性", "预注资", "FX", "净额"),
            ("8583", "20022", "HSM", "PIN", "密钥"),
            ("可用", "冻结", "并发", "Outbox", "Inbox", "恢复"),
            ("银联", "网联", "备付金", "CIPS", "美国", "新加坡"),
            ("现金", "Mobile Money", "e-float", "ATM", "支票"),
            ("CBDC", "代币化存款", "稳定币", "赎回", "最终性"),
        )
        for number, name, terms in zip(range(13, 23), EXTENSION_FILES, expected_terms):
            text = self.documents()[name]
            with self.subTest(lesson=number):
                self.assertRegex(text, rf"(?m)^# {number} .+$")
                self.assertIn(f"lesson-{number}", Page(text).ids)
                self.assertEqual(Page(text).ids.count(f"lesson-{number}"), 1)
                self.assertIn("public-sources", Page(text).ids)
                body, bibliography = text.split('<a id="public-sources"></a>', 1)
                plain_body = ILLUSTRATION.sub("", LINK.sub("", body))
                self.assertGreater(len(plain_body), 1800, "Extension is only a stub")
                self.assertGreaterEqual(len(re.findall(r"(?m)^## ", text)), 7)
                self.assertIn("自测", body)
                self.assertIn("参考答案", body)
                self.assertRegex(body, r"(?m)^1\. ")
                self.assertRegex(body, r"(?m)^2\. ")
                self.assertRegex(body, r"(?m)^3\. ")
                self.assertIn("边界", text)
                for term in terms:
                    self.assertIn(term, body)
                urls = {target for _, target in markdown_links(bibliography)
                        if urlsplit(target).scheme in {"http", "https"}}
                self.assertGreaterEqual(len(urls), 5, "Missing primary evidence")
                if "读取日均为 2026-11-02" not in bibliography and \
                        "读取日为 2026-11-02" not in bibliography:
                    self.assertGreaterEqual(bibliography.count("2026-11-02"), len(urls))
                self.assertGreaterEqual(len(
                    [target for _, target in markdown_links(body)
                     if urlsplit(target).scheme in {"http", "https"}]), 4)

    def test_all_local_markdown_links_and_explicit_fragments_resolve(self):
        for name, text in self.documents().items():
            ids = Page(text).ids
            self.assertEqual(len(ids), len(set(ids)), f"Duplicate IDs in {name}")
            targets = [target for _, target in markdown_links(text)] + Page(text).links
            for target in targets:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    continue
                if parts.path and not parts.path.lower().endswith(".md"):
                    continue
                with self.subTest(document=name, target=target):
                    path = ((TOPIC / name).parent / unquote(parts.path)).resolve()
                    if not parts.path:
                        path = TOPIC / name
                    self.assertTrue(path.is_relative_to(ROOT), "Link escapes repository")
                    self.assertTrue(path.is_file(), f"Missing Markdown: {target}")
                    if parts.fragment:
                        self.assertIn(unquote(parts.fragment),
                                      Page(path.read_text(encoding="utf-8")).ids)

    def test_course_and_source_catalogues_are_real_not_empty_anchor_lists(self):
        docs = self.documents()
        links = [target for _, target in markdown_links(docs["README.md"])]
        self.assertTrue({f"payment-industry-101.md#{lesson}" for lesson in LESSONS}
                        .issubset(links))
        self.assertTrue(set(EXTENSION_FILES).issubset(links))
        self.assertIn("22 课", docs["README.md"])
        self.assertIn("32 张", docs["README.md"])
        self.assertIn("第二周", docs["learning-roadmap.md"])
        for name in EXTENSION_FILES:
            self.assertIn(f"{name}#public-sources", docs["sources.md"])
        sources = docs["sources.md"]
        ids = Page(sources).ids
        self.assertGreaterEqual(len(ids), 30)
        cited = {urlsplit(target).fragment for text in docs.values()
                 for _, target in markdown_links(text)
                 if urlsplit(target).path == "sources.md" and urlsplit(target).fragment}
        self.assertGreaterEqual(len(cited), 30)
        self.assertTrue(cited.issubset(ids))
        entries = list(re.finditer(r'<a id="([^"]+)"></a>', sources))
        for index, entry in enumerate(entries):
            end = entries[index + 1].start() if index + 1 < len(entries) else len(sources)
            with self.subTest(source=entry[1]):
                self.assertRegex(sources[entry.end():end], r"\]\(https://")

    def test_thirty_two_manifest_figures_have_unique_local_heading_placements(self):
        figures = self.figures()
        self.assertEqual(len(figures), 32)
        self.assertEqual(len({figure["id"] for figure in figures}), 32)
        self.assertEqual(sum(len(figure["placements"]) for figure in figures), 32)
        counts = Counter(Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                         for figure in figures for placement in figure["placements"])
        self.assertEqual(counts["payment-industry-101.md"], 14)
        self.assertEqual([counts[name] for name in EXTENSION_FILES],
                         [2, 2, 1, 2, 2, 2, 2, 2, 1, 2])
        for figure in figures:
            with self.subTest(figure=figure["id"]):
                self.assertRegex(figure["id"], r"^payment-[a-z0-9-]+$")
                self.assertEqual(figure["topic"], "payments")
                for placement in figure["placements"]:
                    name = Path(placement["file"]).relative_to(
                        TOPIC.relative_to(ROOT)).as_posix()
                    self.assertIn(name, ("payment-industry-101.md", *EXTENSION_FILES))
                    text = (ROOT / placement["file"]).read_text(encoding="utf-8")
                    self.assertEqual(text.splitlines().count(placement["after"]), 1)
                    self.assertTrue(placement["after"].startswith(
                        "## " if name in EXTENSION_FILES else "### "))

    def test_assets_and_body_placements_match_the_renderer_and_manifest(self):
        self.require_figures()
        figures = self.figures()
        for suffix in ("svg", "png"):
            self.assertEqual({path.stem for path in (TOPIC / "images").glob(f"*.{suffix}")},
                             {figure["id"] for figure in figures})
        spec = importlib.util.spec_from_file_location(
            "payments_figures", ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        expected_markers = {name: [] for name in FILES}
        expected_images = {name: [] for name in FILES}
        docs = self.documents()
        for figure in figures:
            with self.subTest(figure=figure["id"]):
                svg = TOPIC / "images" / (figure["id"] + ".svg")
                self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
                self.assertEqual(svg.read_text(encoding="utf-8"),
                                 renderer.RENDERERS[figure["kind"]](figure))
                for placement in figure["placements"]:
                    name = Path(placement["file"]).relative_to(
                        TOPIC.relative_to(ROOT)).as_posix()
                    book = docs[name]
                    image_path = os.path.relpath(
                        svg.with_suffix(".png"), (TOPIC / name).parent)
                    suffix = hashlib.sha256(placement["after"].encode("utf-8")).hexdigest()[:10]
                    marker = figure["id"] + "-" + suffix
                    expected_markers[name].append(marker)
                    expected_images[name].append(image_path)
                    blocks = [body for identity, body in ILLUSTRATION.findall(book)
                              if identity == marker]
                    self.assertEqual(len(blocks), 1, "Missing or duplicate illustration")
                    self.assertIn(f']({image_path})', blocks[0])
                    self.assertIn(figure["title"], blocks[0])
                    self.assertIn(f"*图：{figure['title']}。", blocks[0])
                    self.assertRegex(book, re.escape(placement["after"]) +
                                     r"\n\s*<!-- illustration: " + re.escape(marker) + " -->")
        for name, book in docs.items():
            with self.subTest(document=name):
                self.assertEqual(Counter(identity for identity, _ in ILLUSTRATION.findall(book)),
                                 Counter(expected_markers[name]))
                images = [target for image, target in markdown_links(book) if image]
                self.assertEqual(Counter(images), Counter(expected_images[name]))

    def test_public_source_files_do_not_leak_private_provenance(self):
        shared = [ROOT / "README.md", ROOT / "wiki/topics/README.md",
                  ROOT / "_data/navigation.yml", ROOT / "_includes/sidebar.html", *MANIFESTS]
        for path in shared + [path for path in TOPIC.rglob("*") if path.is_file()]:
            label = path.relative_to(ROOT).as_posix()
            self.assert_public(label, "published filename")
            if path.suffix != ".png":
                self.assert_public(path.read_text(encoding="utf-8"), label)

    def test_home_topic_index_and_sidebar_navigation_include_all_lessons(self):
        self.assertIn("](wiki/topics/payments/README.md)",
                      (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("](payments/README.md)",
                      (ROOT / "wiki/topics/README.md").read_text(encoding="utf-8"))
        navigation = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        urls = re.findall(r"(?m)^\s+url:\s*(/wiki/topics/payments/\S*)\s*$", navigation)
        required = {"/wiki/topics/payments/"} | {
            "/wiki/topics/payments/" + name.replace(".md", ".html")
            for name in FILES if name != "README.md"
        } | {"/wiki/topics/payments/payment-industry-101.html#" + lesson for lesson in LESSONS}
        self.assertEqual(set(urls), required)
        sidebar = (ROOT / "_includes/sidebar.html").read_text(encoding="utf-8")
        self.assertIn("site.data.navigation.topics", sidebar)
        self.assertIn("topic.items", sidebar)
        self.assertIn("item.url | relative_url", sidebar)
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        excluded = config.split("\nexclude:", 1)[1]
        self.assertRegex(excluded, r"(?m)^  - tests\s*$")
        self.assertRegex(excluded, r"(?m)^  - scripts\s*$")


@unittest.skipUnless(SITE.is_dir(), "Build the site or set PAYMENTS_SITE for integration checks")
class PaymentsSiteTests(PaymentsChecks):
    def setUp(self):
        self.pages = {}

    def read_page(self, relative):
        path = SITE / relative
        self.assertTrue(path.is_file(), f"Missing built page: {relative}")
        if relative not in self.pages:
            self.pages[relative] = Page(path.read_text(encoding="utf-8"))
        return self.pages[relative]

    def local_target(self, relative, target):
        page = self.read_page(relative)
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            return None
        route = page.base + "/" + relative
        if route.endswith("index.html"):
            route = route[:-len("index.html")]
        parts = urlsplit(urljoin(route, target))
        path = unquote(parts.path)
        self.assertTrue(path.startswith(page.base + "/"), f"Wrong base URL: {target}")
        file = (SITE / path[len(page.base) + 1:]).resolve()
        if path.endswith("/"):
            file /= "index.html"
        self.assertTrue(file.is_relative_to(SITE), f"Resource escapes build: {target}")
        self.assertTrue(file.is_file(), f"Broken local resource: {target}")
        if parts.fragment and file.suffix == ".html":
            self.assertIn(unquote(parts.fragment),
                          self.read_page(file.relative_to(SITE).as_posix()).ids,
                          f"Broken built anchor: {target}")
        return file

    def test_all_fifteen_pages_render_the_actual_body_without_javascript(self):
        for name, source in self.documents().items():
            with self.subTest(document=name):
                page = self.read_page(ROUTES[name])
                self.assertEqual(page.article_count, 1)
                self.assertEqual(len(page.ids), len(set(page.ids)), "Duplicate built IDs")
                self.assertTrue(set(Page(source).ids).issubset(page.article_ids))
                headings = [("h" + str(len(match[1])), normalized(match[2]))
                            for match in re.finditer(r"(?m)^(#{1,6}) (.+)$", source)]
                self.assertEqual(page.headings, headings)
                body = normalized("".join(page.text))
                samples = list(prose_samples(source))
                self.assertGreater(len(samples), 5, "No meaningful source-body checks")
                for sample in samples:
                    self.assertTrue(sample in body, f"Missing built prose in {name}: {sample}")
        reader = self.read_page(ROUTES["payment-industry-101.md"])
        self.assertEqual([identity for identity in reader.article_ids if identity in LESSONS],
                         LESSONS)

    def test_local_body_links_and_source_anchors_resolve_in_the_build(self):
        for name, relative in ROUTES.items():
            page = self.read_page(relative)
            for target in page.article_links:
                with self.subTest(document=name, target=target):
                    file = self.local_target(relative, target)
                    if file is not None:
                        self.assertNotEqual(file.suffix, ".md", "Unconverted Markdown link")
            source_links = [target for target in page.article_links
                            if urlsplit(target).path.endswith("/sources.html")
                            and urlsplit(target).fragment]
            if name in {"payment-industry-101.md", "learning-roadmap.md"}:
                self.assertTrue(source_links, "Missing built source citations")

    def test_thirty_two_built_png_svg_pairs_and_their_heading_placements(self):
        placed = {}
        for name, relative in ROUTES.items():
            page = self.read_page(relative)
            expected_count = sum(placement["file"] == "wiki/topics/payments/" + name
                                 for figure in self.figures() for placement in figure["placements"])
            self.assertEqual(len(page.images), expected_count)
            self.assertTrue(any(urlsplit(src).path.endswith("/assets/js/wiki-figures.js")
                                for src in page.scripts), "Missing SVG/modal enhancement")
            current_heading = None
            for kind, value in page.events:
                if kind == "heading":
                    current_heading = value[1]
                elif kind == "image":
                    self.assertTrue(value.get("alt"), "Missing image description")
                    target = value.get("src", "")
                    self.assertFalse(urlsplit(target).scheme or urlsplit(target).netloc,
                                     "Payments illustrations must be local")
                    png = self.local_target(relative, target)
                    self.assertEqual(png.suffix, ".png")
                    self.assertNotIn(png.stem, placed, "Duplicate built figure")
                    placed[png.stem] = (name, current_heading)
        self.assertEqual(set(placed), {figure["id"] for figure in self.figures()})
        for figure in self.figures():
            with self.subTest(figure=figure["id"]):
                png = SITE / "wiki/topics/payments/images" / (figure["id"] + ".png")
                self.assert_asset_pair(png.with_suffix(".svg"), png, figure)
                for suffix in ("png", "svg"):
                    self.assertEqual(png.with_suffix("." + suffix).read_bytes(),
                                     (TOPIC / "images" / (figure["id"] + "." + suffix)).read_bytes())
                placement = figure["placements"][0]
                name = Path(placement["file"]).relative_to(TOPIC.relative_to(ROOT)).as_posix()
                self.assertEqual(placed[figure["id"]],
                                 (name, placement["after"].lstrip("# ")))

    def test_home_index_sidebar_and_search_have_working_payments_entries(self):
        reader = self.read_page(ROUTES["payment-industry-101.md"])
        topic_url = reader.base + "/wiki/topics/payments/"
        home = self.read_page("index.html")
        self.assertIn(topic_url, home.catalogue_links)
        index = self.read_page("wiki/topics/index.html")
        # jekyll-readme-index keeps README.html as a valid alias when
        # remove_originals is false; either route is a working topic entry.
        entries = {topic_url, topic_url + "README.html"}
        self.assertTrue(entries.intersection(index.article_links), "Missing topic-index entry")
        for target in entries.intersection(index.article_links):
            self.local_target("wiki/topics/index.html", target)
        required = {reader.base + "/" + relative.replace("index.html", "")
                    for relative in ROUTES.values()}
        required |= {reader.base + "/wiki/topics/payments/payment-industry-101.html#" + lesson
                     for lesson in LESSONS}
        for relative in ("index.html", "wiki/topics/index.html", *ROUTES.values()):
            page = self.read_page(relative)
            self.assertTrue(required.issubset(page.sidebar_links), "Incomplete payments sidebar")
            for target in required:
                self.local_target(relative, target)
        records = json.loads((SITE / "search.json").read_text(encoding="utf-8"))
        payments = [record for record in records
                    if urlsplit(record["url"]).path.startswith(topic_url)]
        self.assertEqual(Counter(record["url"] for record in payments),
                         Counter(reader.base + "/" + relative.replace("index.html", "")
                                 for relative in ROUTES.values()))
        for record in payments:
            self.assertTrue(record["title"].strip())
            self.local_target("index.html", record["url"])
            self.assert_public(json.dumps(record, ensure_ascii=False), "payments search record")
            name = next(name for name, relative in ROUTES.items()
                        if record["url"] == reader.base + "/" + relative.replace("index.html", ""))
            for sample in prose_samples(self.documents()[name]):
                self.assertTrue(sample in normalized(record["text"]),
                                f"Unsearchable prose in {name}: {sample}")

    def test_published_files_exclude_private_material_and_test_sources(self):
        self.assertFalse((SITE / "tests").exists(), "Tests must not be published")
        self.assertFalse((SITE / "scripts").exists(), "Figure scripts must not be published")
        allowed = set(FILES) | {"README.html", "index.html"} | {
            name.replace(".md", ".html") for name in FILES
        } | {f"images/{figure['id']}.{suffix}"
             for figure in self.figures() for suffix in ("png", "svg")}
        for path in (SITE / "wiki/topics/payments").rglob("*"):
            if path.is_file():
                self.assertIn(path.relative_to(SITE / "wiki/topics/payments").as_posix(), allowed)
                if path.suffix != ".png":
                    self.assert_public(path.read_text(encoding="utf-8"),
                                       path.relative_to(SITE).as_posix())
        for relative in ("index.html", "wiki/topics/index.html"):
            self.assert_public((SITE / relative).read_text(encoding="utf-8"), relative)
        for path in SITE.rglob("*"):
            self.assertFalse(re.search(PRIVATE["private provenance map"], path.name, re.I),
                             "A private provenance map must not be published")


if __name__ == "__main__":
    unittest.main()
