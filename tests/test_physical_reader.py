"""Regression checks for complete, in-site Physical AI reading.

Build first, then run:
PHYSICAL_READER_SITE=/path/to/site python -m unittest discover -s tests -p test_physical_reader.py
"""

from html.parser import HTMLParser
import os
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = Path(os.environ.get("PHYSICAL_READER_SITE", ROOT / "_site"))
BASE = "/learning-wiki"
BOOKS = {
    "knowledge": ("Physical_AI_知识全景与学习指南.md", "十五、练习与掌握程度检查"),
    "industry": ("industry/Physical_AI_业界产品与端到端方案.md", "12 把产品接起来：交付接口与原理对照"),
    "advanced": ("advanced/Physical_AI_底层原理与实现细节.md", "14 数值练习与系统贯通：把公式变成可检查的计算"),
    "gtc": ("conferences/gtc-berlin-2026/GTC_Berlin_2026_Physical_AI_深度调研报告.md", "八、相关会议场次"),
}


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.books = {}
        self.ids = []
        self.targets = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if attrs.get("data-reading-book"):
            self.books[attrs["data-reading-book"]] = attrs
        if tag in {"a", "img", "source"}:
            for attribute in ("href", "src", "srcset"):
                if attrs.get(attribute):
                    self.targets.append(attrs[attribute])

    def handle_data(self, data):
        self.text.append(data)


@unittest.skipUnless(SITE.is_dir() or "PHYSICAL_READER_SITE" in os.environ,
                     "Build the site or set PHYSICAL_READER_SITE for integration checks")
class PhysicalReaderTests(unittest.TestCase):
    def read_page(self, relative):
        file = SITE / relative
        self.assertTrue(file.is_file(), "Build the site before testing: " + str(file))
        return Page(file.read_text(encoding="utf-8"))

    def test_topic_page_contains_all_four_complete_books_without_navigation(self):
        page = self.read_page("wiki/topics/physical-ai/index.html")
        self.assertEqual(set(page.books), set(BOOKS),
                         "Physical AI currently only links to the books; their bodies must be in this page")
        text = "".join(page.text)
        self.assertGreater(len(text), 60000, "The reading page must contain the actual books, not short previews")
        for key, (_, final_chapter) in BOOKS.items():
            with self.subTest(book=key):
                self.assertIn(final_chapter, text)

    def test_subtopic_entries_render_their_actual_text_not_just_download_links(self):
        for key, route in (
            ("industry", "wiki/topics/physical-ai/industry/index.html"),
            ("advanced", "wiki/topics/physical-ai/advanced/index.html"),
            ("gtc", "wiki/topics/physical-ai/conferences/gtc-berlin-2026/index.html"),
        ):
            with self.subTest(book=key):
                page = self.read_page(route)
                self.assertIn(key, page.books)
                self.assertIn(BOOKS[key][1], "".join(page.text))

    def test_inlined_heading_ids_are_unique_and_anchors_exist(self):
        page = self.read_page("wiki/topics/physical-ai/index.html")
        self.assertTrue(page.books, "No in-page books to validate")
        self.assertEqual(len(page.ids), len(set(page.ids)), "Colliding IDs across books")
        for target in page.targets:
            if target.startswith("#"):
                self.assertIn(unquote(target[1:]), page.ids, "Broken in-page anchor: " + target)

    def test_reader_links_and_images_stay_in_project_and_resolve(self):
        page = self.read_page("wiki/topics/physical-ai/index.html")
        self.assertTrue(page.books, "No in-page books to validate")
        for target in page.targets:
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            self.assertTrue(parts.path.startswith(BASE + "/"), "Wrong base URL: " + target)
            file = SITE / unquote(parts.path[len(BASE) + 1:])
            if parts.path.endswith("/"):
                file /= "index.html"
            self.assertTrue(file.is_file(), "Broken local reader resource: " + target)

    def test_generated_fragments_track_the_archival_source_files(self):
        import hashlib
        # YAML itself is tested by the build; source digests can be checked
        # dependency-free here without adding another Python package.
        metadata = (ROOT / "_data/physical_ai_books.yml").read_text(encoding="utf-8")
        for source, _ in BOOKS.values():
            file = ROOT / "wiki/topics/physical-ai" / source
            self.assertIn(hashlib.sha256(file.read_bytes()).hexdigest(), metadata)

    def test_book_text_is_available_without_javascript(self):
        page = self.read_page("wiki/topics/physical-ai/index.html")
        self.assertEqual(set(page.books), set(BOOKS))
        for attrs in page.books.values():
            self.assertNotIn("hidden", attrs)
            self.assertNotIn("reader-inactive", attrs.get("class", ""))


if __name__ == "__main__":
    unittest.main()
