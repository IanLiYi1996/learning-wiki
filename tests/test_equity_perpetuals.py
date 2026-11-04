"""Source, asset and built-site contracts for the equity-perpetuals primer."""

from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from test_payments import ILLUSTRATION, Page, markdown_links, normalized

ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/blockchain/equity-perpetuals"
SITE = Path(os.environ.get("EQUITY_PERPETUALS_SITE", ROOT / "_site")).resolve()
PREFIX = "wiki/topics/blockchain/equity-perpetuals/"
CHAPTERS = (
    "01-products-and-rights.md", "02-market-and-positions.md",
    "03-prices-and-anchoring.md", "04-funding-and-arbitrage.md",
    "05-margin-and-liquidation.md", "06-hours-and-corporate-actions.md",
    "07-risk-and-protection.md", "08-reading-a-contract.md",
)
FILES = ("README.md", *CHAPTERS, "learning-roadmap.md", "glossary.md", "lab.md", "sources.md")
ROUTES = {
    name: PREFIX + ("index.html" if name == "README.md" else name.replace(".md", ".html"))
    for name in FILES
}


def documents():
    return {name: (TOPIC / name).read_text(encoding="utf-8") for name in FILES}


def manifest():
    return json.loads((ROOT / "scripts/figures/equity-perpetuals.json").read_text())


class SourceTests(unittest.TestCase):
    def test_thirteen_complete_pages_and_eight_chapters(self):
        self.assertEqual({path.name for path in TOPIC.iterdir()}, set(FILES))
        for name, text in documents().items():
            self.assertRegex(text, r"\A# ")
            self.assertIn("2026-11-04", text)
            self.assertGreater(len(ILLUSTRATION.sub("", text)), 1500, name)
            self.assertNotRegex(text, r"TODO|TBD|待主代理|由主代理|/home/|file://")
        for name in CHAPTERS:
            self.assertIn("自测与答案", documents()[name])
            self.assertGreaterEqual(len(re.findall(r"(?m)^[123]\. ", documents()[name])), 3)
            self.assertIn("sources.md#s", documents()[name])

    def test_local_links_and_explicit_source_anchors_resolve(self):
        for name, text in documents().items():
            path = TOPIC / name
            for _, target in markdown_links(text):
                part = urlsplit(target)
                if part.scheme or part.netloc:
                    self.assertEqual(part.scheme, "https", f"{name}: {target}")
                    continue
                dest = (path.parent / unquote(part.path)).resolve() if part.path else path
                self.assertTrue(dest.is_relative_to(ROOT), target)
                self.assertTrue(dest.is_file(), f"{name}: {target}")
                if part.fragment:
                    self.assertIn(
                        unquote(part.fragment), Page(dest.read_text()).ids,
                        f"{name}: {target}",
                    )

    def test_twenty_primary_source_groups_and_version_limits(self):
        source = documents()["sources.md"]
        ids = re.findall(r'<a id="(s\d\d)"></a>', source)
        self.assertEqual(ids, [f"s{number:02d}" for number in range(1, 21)])
        urls = {target for _, target in markdown_links(source) if urlsplit(target).scheme == "https"}
        self.assertGreaterEqual(len(urls), 50)
        allowed = {
            "docs.trade.xyz", "hyperliquid.gitbook.io", "www.investor.gov",
            "www.sec.gov", "www.finra.org", "www.sipc.org",
            "docs.xstocks.fi", "assets.backed.fi",
        }
        for url in urls:
            self.assertIn(urlsplit(url).netloc, allowed, url)
        for phrase in (
            "0.0003", "0.0005", "未查询", "历史", "unified", "销毁",
            "未核验", "不是固定股息", "没有标的的所有权", "不是对 XYZ 作法律裁决",
        ):
            self.assertIn(phrase, source)

    def test_critical_corrections_and_teaching_boundaries_are_retained(self):
        texts = documents()
        required = {
            "README.md": ("软", "没有连接钱包", "教学算例"),
            "03-prices-and-anchoring.md": ("中位数", "Oracle 错误", "150 秒", "软锚定"),
            "04-funding-and-arbitrage.md": ("0.00001", "8.76%", "87.6%", "不是已执行", "clamp"),
            "05-margin-and-liquidation.md": ("Unified", "Standard", "Portfolio", "不是", "ADL"),
            "06-hours-and-corporate-actions.md": ("20:05", "ET", "夏令时", "重新开仓", "不是固定股息"),
            "07-risk-and-protection.md": ("销毁", "SIPC", "不等于", "不是"),
            "08-reading-a-contract.md": ("十四问", "未知", "教学假设"),
            "lab.md": ("不是实盘监控工具", "13 个单元测试", "0.08760", "AT_OR_ABOVE"),
            "learning-roadmap.md": ("0.1 USDC", "0.001%=0.00001", "未知"),
        }
        for name, phrases in required.items():
            for phrase in phrases:
                self.assertIn(phrase, texts[name], f"{name}: {phrase}")
        script = (ROOT / "scripts/equity_perpetuals_lab.py").read_text()
        self.assertNotRegex(script, r"requests|urllib|httpx|socket|subprocess")
        self.assertIn("not a real liquidation estimator", script)

    def test_four_generated_asset_pairs_and_scoped_placements(self):
        spec = importlib.util.spec_from_file_location(
            "equity_figures", ROOT / "scripts/render_figures.py"
        )
        figures = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(figures)
        group = manifest()
        self.assertEqual(len(group), 4)
        self.assertEqual({row["id"] for row in group}, {
            "eq-products", "eq-anchor", "eq-liquidation", "eq-risk",
        })
        figures.validate(group)
        for row in group:
            svg = figures.figure_path(row, "svg")
            png = figures.figure_path(row, "png")
            self.assertEqual(svg.read_text(), figures.RENDERERS[row["kind"]](row))
            ET.fromstring(svg.read_text())
            self.assertNotRegex(svg.read_text(), r"<script|<foreignObject|@import|href=")
            self.assertEqual(png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(len(row["placements"]), 1)
            for placement in row["placements"]:
                self.assertEqual((ROOT / placement["file"]).parent, TOPIC)
                self.assertEqual(
                    documents()[Path(placement["file"]).name].splitlines().count(placement["after"]),
                    1,
                )

    def test_topic_is_linked_from_three_existing_indexes_and_navigation(self):
        for name, target in (
            ("README.md", "wiki/topics/blockchain/equity-perpetuals/README.md"),
            ("wiki/topics/README.md", "blockchain/equity-perpetuals/README.md"),
            ("wiki/topics/blockchain/README.md", "equity-perpetuals/README.md"),
        ):
            self.assertIn(target, (ROOT / name).read_text())
        nav = (ROOT / "_data/navigation.yml").read_text()
        for route in ROUTES.values():
            self.assertIn("/" + route.replace("index.html", ""), nav)


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (SITE / "search.json").is_file():
            raise AssertionError("Build Jekyll before running the equity primer checks")

    def test_thirteen_routes_search_content_and_topic_sidebar(self):
        records = json.loads((SITE / "search.json").read_text())
        base = Page((SITE / ROUTES["README.md"]).read_text()).base
        selected = [row for row in records if urlsplit(row["url"]).path.startswith(
            base + "/" + PREFIX
        )]
        self.assertEqual(
            Counter(row["url"] for row in selected),
            Counter(base + "/" + route.replace("index.html", "") for route in ROUTES.values()),
        )
        content_markers = {
            "README.md": "股价永续的连接机制可理解为",
            "01-products-and-rights.md": "正确的比较至少有四个轴",
            "02-market-and-positions.md": "在 XYZ，USD 参考价格与 USDC",
            "03-prices-and-anchoring.md": "前两项由 relayer 提交",
            "04-funding-and-arbitrage.md": "没有把未核实的配置与封顶顺序",
            "05-margin-and-liquidation.md": "当前 Standard / Manual 模式分开 DEX 余额",
            "06-hours-and-corporate-actions.md": "XYZ 当前的一般拆股 / 反向拆股政策是",
            "07-risk-and-protection.md": "当前 HIP-3 说明中",
            "08-reading-a-contract.md": "未知 / 不一致",
            "learning-roadmap.md": "费用被放大了十倍",
            "glossary.md": "某小时费率 × 8",
            "lab.md": "不是实盘监控工具",
            "sources.md": "ETF 份额代表基金组合",
        }
        for name, route in ROUTES.items():
            html = (SITE / route).read_text()
            page = Page(html)
            self.assertEqual(page.article_count, 1)
            self.assertIn(
                documents()[name].splitlines()[0][2:],
                [value for tag, value in page.headings if tag == "h1"],
            )
            self.assertIn(base + "/" + PREFIX, page.sidebar_links)
            for chapter in CHAPTERS:
                self.assertIn(base + "/" + ROUTES[chapter], page.sidebar_links)
            prose = normalized("".join(page.text))
            self.assertIn("2026-11-04", prose)
            self.assertIn(content_markers[name], prose, name)

    def test_built_article_links_images_and_source_fragments(self):
        for name, route in ROUTES.items():
            page = Page((SITE / route).read_text())
            targets = page.article_links + [image["src"] for image in page.images]
            for target in targets:
                resolved = urlsplit(urljoin("https://local.invalid" + page.base + "/" + route, target))
                if resolved.netloc != "local.invalid":
                    continue
                self.assertTrue(resolved.path.startswith(page.base + "/"), target)
                dest = SITE / unquote(resolved.path[len(page.base):]).lstrip("/")
                if not dest.suffix:
                    dest /= "index.html"
                self.assertTrue(dest.resolve().is_relative_to(SITE))
                self.assertTrue(dest.is_file(), f"{name}: {target}")
                if resolved.fragment and dest.suffix == ".html":
                    self.assertIn(unquote(resolved.fragment), Page(dest.read_text()).ids)
                if dest.suffix in (".png", ".svg"):
                    source_asset = ROOT / dest.relative_to(SITE)
                    self.assertEqual(dest.read_bytes(), source_asset.read_bytes())
            for link in page.article_links:
                if not urlsplit(link).netloc:
                    self.assertFalse(urlsplit(link).path.endswith(".md"), link)
        expected = sum(len(row["placements"]) for row in manifest())
        actual = sum(len(Page((SITE / route).read_text()).images) for route in ROUTES.values())
        self.assertEqual(actual, expected)

    def test_homepage_has_a_direct_topic_card(self):
        home = Page((SITE / "index.html").read_text())
        self.assertIn(home.base + "/" + PREFIX, home.catalogue_links)


if __name__ == "__main__":
    unittest.main()
