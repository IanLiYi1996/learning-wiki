"""Additive content/build contracts, not a scanner or an AWS security assessment."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from test_payments import ILLUSTRATION, Page, PaymentsChecks, markdown_links, normalized
from test_deep_learning import readable_samples


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/security"
STUDY = TOPIC / "aws-continuum"
SITE = Path(os.environ.get("SECURITY_SITE", ROOT / "_site")).resolve()
FILES = ("README.md", "security-foundations.md", "continuum-l200.md",
         "permissions-and-data.md", "validation-and-remediation.md",
         "customer-solutions.md", "learning-roadmap.md", "lab.md", "sources.md")
ROUTES = {name: "wiki/topics/security/aws-continuum/" +
          name.replace("README.md", "index.html").replace(".md", ".html") for name in FILES}
COUNTS = (1, 1, 2, 1, 1, 2, 1, 1, 0)
NATIVE = TOPIC / "images/sec-aws-governance.svg"


def documents():
    return {name: (STUDY / name).read_text() for name in FILES}


def manifest():
    return json.loads((ROOT / "scripts/figures/security-continuum.json").read_text())


def samples(source):
    source = re.sub(r"(?m)^\[[^\]]+\]:\s+\S+.*\n?", "", source)
    source = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]+\]", r"\1", source)
    # The native SVG's caption is italic Markdown; compare its actual prose.
    source = re.sub(r"(?m)^\*([^*\n]+)\*$", r"\1", source)
    return readable_samples(source)


class SecuritySourceTests(PaymentsChecks):
    def test_exact_pages_and_public_scope(self):
        self.assertEqual({path.name for path in STUDY.iterdir()}, set(FILES) | {"sources.json"})
        for name, source in documents().items():
            self.assertRegex(source, r"\A# ")
            self.assertIn("2026-11-03", source)
            self.assertGreater(len(ILLUSTRATION.sub("", source)), 1800, name)
            self.assert_public(source, name)
            self.assertNotRegex(source, r"TODO|TBD|待主代理|由主代理|(?:上午|下午)\s*\d+:\d+")
        for path in [TOPIC / "README.md", STUDY / "sources.json",
                     ROOT / "scripts/figures/security-continuum.json", *TOPIC.glob("images/*.svg")]:
            self.assert_public(path.read_text(), path.name)

    def test_ga_status_and_scope_discrepancy_remain_explicit(self):
        docs = documents()
        for name in ("README.md", "continuum-l200.md", "permissions-and-data.md",
                     "validation-and-remediation.md", "customer-solutions.md", "sources.md"):
            self.assertIn("2026-10-22", docs[name])
            self.assertIn("GA", docs[name])
            self.assertIn("preview", docs[name].lower())
        self.assertIn("| Code vulnerabilities | 2026-10-22 GA", docs["continuum-l200.md"])
        self.assertIn("overview", docs["sources.md"])
        self.assertIn("未来", docs["validation-and-remediation.md"])
        self.assertIn("不覆盖", docs["sources.md"])
        self.assertIn("fail-open", docs["continuum-l200.md"])
        self.assertIn("Manual only", docs["continuum-l200.md"])
        self.assertIn("PR** code reviews", docs["continuum-l200.md"])
        self.assertIn("不是 AWS 认证", docs["learning-roadmap.md"])
        self.assertNotRegex(ILLUSTRATION.sub("", docs["continuum-l200.md"]), r"\$\d")
        self.assertEqual(docs["lab.md"].splitlines().count("$$"), 4)

    def test_source_ledger_is_mutable_not_claimed_snapshot_or_live_scan(self):
        ledger = json.loads((STUDY / "sources.json").read_text())
        self.assertEqual(ledger["research_date"], "2026-11-03")
        self.assertFalse(ledger["account_accessed"])
        self.assertFalse(ledger["assessments_executed"])
        self.assertIn("mutable", ledger["source_type"])
        self.assertEqual(len(ledger["sources"]), 25)
        self.assertEqual(len({row["id"] for row in ledger["sources"]}), 25)
        self.assertEqual(len(ledger["discrepancies"]), 5)
        urls = {target for _, target in markdown_links(documents()["sources.md"])}
        urls.update(target for _, target in markdown_links(documents()["security-foundations.md"]))
        for row in ledger["sources"]:
            self.assertEqual(urlsplit(row["url"]).scheme, "https")
            self.assertIn(row["url"], urls, row["id"])
            self.assertTrue(row["scope"])
        ga = next(row for row in ledger["sources"] if row["id"] == "ga")
        self.assertEqual(ga["event_date"], "2026-10-22")
        self.assertIn("human approval", ga["scope"])

    def test_local_links_and_existing_explicit_fragments(self):
        for path in [TOPIC / "README.md", *(STUDY / name for name in FILES)]:
            source = path.read_text()
            for target in [target for _, target in markdown_links(source)] + Page(source).links:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    self.assertNotEqual(parts.scheme, "http")
                    continue
                file = (path.parent / unquote(parts.path)).resolve() if parts.path else path
                self.assertTrue(file.is_relative_to(ROOT))
                self.assertTrue(file.is_file(), f"{path.name}: {target}")
                if parts.fragment:
                    self.assertIn(unquote(parts.fragment), Page(file.read_text()).ids)

    def test_nine_pairs_placements_and_one_native_aws_svg(self):
        figures = manifest()
        self.assertEqual(len(figures), 9)
        self.assertEqual(sum(len(row["placements"]) for row in figures), 9)
        from test_figures import FIGURES
        actual = Counter()
        for figure in figures:
            self.assertEqual(figure["topic"], "security")
            self.assertRegex(figure["id"], r"^sec-[a-z0-9-]+$")
            svg = TOPIC / "images" / (figure["id"] + ".svg")
            self.assertEqual(svg.read_text(), FIGURES.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            if figure["kind"] == "compare":
                self.assertEqual(figure["footer_gap"], 64)
                tree = ET.fromstring(svg.read_text())
                ns = {"svg": "http://www.w3.org/2000/svg"}
                cells = [node for node in tree.findall(".//svg:rect", ns) if "x" in node.attrib]
                bottom = max(float(node.get("y")) + float(node.get("height")) for node in cells)
                footer = tree.findall(".//svg:line", ns)[-1]
                self.assertGreaterEqual(float(footer.get("y1")), bottom + 32)
            for placement in figure["placements"]:
                name = Path(placement["file"]).name
                self.assertIn(name, FILES)
                self.assertEqual(documents()[name].splitlines().count(placement["after"]), 1)
                identity = figure["id"] + "-" + hashlib.sha256(placement["after"].encode()).hexdigest()[:10]
                self.assertEqual(len([body for marker, body in ILLUSTRATION.findall(documents()[name])
                                      if marker == identity]), 1)
                actual[name] += 1
        self.assertEqual(sum(actual.values()), 9)
        tree = ET.fromstring(NATIVE.read_text())
        self.assertIn("mxGraphModel", tree.attrib["content"])
        model = ET.fromstring(tree.attrib["content"])
        cells = model.findall(".//mxCell")
        self.assertEqual(len([cell for cell in cells if cell.get("edge") == "1"]), 4)
        self.assertNotRegex(NATIVE.read_text(), r"<script|<foreignObject|file://|/home/|/tmp/")
        for service in ("AWS IAM Identity Center", "AWS Secrets Manager",
                        "AWS Key Management Service", "AWS Step Functions", "Amazon S3",
                        "AWS CloudTrail", "Amazon CloudWatch"):
            self.assertIn(service, NATIVE.read_text())
        self.assertFalse(NATIVE.with_suffix(".png").exists())
        expected = {row["id"] + "." + ext for row in figures for ext in ("svg", "png")} | {NATIVE.name}
        self.assertEqual({path.name for path in (TOPIC / "images").iterdir()}, expected)

    def test_compare_clearance_is_opt_in_and_rejects_invalid_gap(self):
        from test_figures import FIGURES
        fixture = {"title": "Test", "subtitle": "fixture", "columns": ["A", "B"],
                   "rows": [["X", "Y"]], "note": "note"}
        original = FIGURES.render_compare(fixture)
        self.assertEqual(original, FIGURES.render_compare({**fixture, "footer_gap": 0}))
        tall = ET.fromstring(FIGURES.render_compare({**fixture, "footer_gap": 64}))
        short = ET.fromstring(original)
        self.assertEqual(int(tall.get("height")), int(short.get("height")) + 64)
        for value in (-1, float("inf"), float("nan"), True, "64"):
            with self.assertRaises(ValueError):
                FIGURES.render_compare({**fixture, "footer_gap": value})

    def test_customer_contracts_and_execution_exclusions(self):
        source = documents()["customer-solutions.md"]
        for label in ("### A.", "### B.", "### C.", "### D.", "no-go",
                      "PoC 验收", "stop／人审批", "双方责任", "成本／替代", "2—4 周",
                      "不是 Continuum 内部架构", "客户自建", "diagrams.net"):
            self.assertIn(label, source)
        for label in ("未登录 AWS", "未执行", "无网络"):
            self.assertIn(label, "\n".join(documents().values()))
        lab = documents()["lab.md"]
        for label in ("不扫描目标", "不是复制 AWS", "RELEASE_REVIEW", "不是安全证明",
                      "0.5", "480", "第一档"):
            self.assertIn(label, lab)
        for filename in ("scripts/security_tabletop_lab.py", "tests/test_security_tabletop_lab.py"):
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + filename, lab)
            self.assertTrue((ROOT / filename).is_file())


class SecurityBuildTests(PaymentsChecks):
    @classmethod
    def setUpClass(cls):
        if not (SITE / "search.json").is_file():
            raise AssertionError("Build Jekyll before testing security pages")

    def local(self, route, target):
        resolved = urlsplit(urljoin("https://local.invalid" + self.base + "/" + route, target))
        if resolved.netloc != "local.invalid":
            return None
        file = SITE / unquote(resolved.path[len(self.base):]).lstrip("/")
        if not file.suffix:
            file /= "index.html"
        self.assertTrue(file.resolve().is_relative_to(SITE))
        self.assertTrue(file.is_file(), target)
        if resolved.fragment and file.suffix == ".html":
            self.assertIn(unquote(resolved.fragment), Page(file.read_text()).ids)
        return file

    def test_exact_search_routes_titles_prose_and_navigation(self):
        records = json.loads((SITE / "search.json").read_text())
        self.base = Page((SITE / ROUTES["README.md"]).read_text()).base
        selected = [row for row in records if urlsplit(row["url"]).path.startswith(
            self.base + "/wiki/topics/security/")]
        routes = list(ROUTES.values()) + ["wiki/topics/security/index.html"]
        self.assertEqual(Counter(row["url"] for row in selected),
                         Counter(self.base + "/" + route.replace("index.html", "") for route in routes))
        for name, route in ROUTES.items():
            source = documents()[name]
            html = (SITE / route).read_text()
            page = Page(html)
            self.assertEqual(page.article_count, 1)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assert_public(html, route)
            record = next(row for row in selected if row["url"] ==
                          self.base + "/" + route.replace("index.html", ""))
            self.assertEqual(record["title"], re.search(r"(?m)^# (.+)$", source)[1])
            for sample in samples(source):
                self.assertIn(sample, normalized("".join(page.text)), name)
                self.assertIn(sample, normalized(record["text"]), name)
            for target in page.article_links:
                file = self.local(route, target)
                if file:
                    self.assertNotEqual(file.suffix, ".md")
            for expected in routes:
                self.assertIn(self.base + "/" + expected.replace("index.html", ""), page.sidebar_links)

    def test_built_images_and_native_svg_are_exact(self):
        for name, count in zip(FILES, COUNTS):
            route = ROUTES[name]
            page = Page((SITE / route).read_text())
            self.base = page.base
            self.assertEqual(len(page.images), count, name)
            for image in page.images:
                file = self.local(route, image["src"])
                relative = file.relative_to(SITE)
                self.assertTrue(image["alt"])
                self.assertEqual(file.read_bytes(), (ROOT / relative).read_bytes())
        self.assertEqual((SITE / NATIVE.relative_to(ROOT)).read_bytes(), NATIVE.read_bytes())

    def test_no_extra_study_files_and_roots_expose_topic(self):
        expected = set(FILES) | {file.replace(".md", ".html") for file in FILES} | {
            "index.html", "README.html", "sources.json"}
        actual = SITE / "wiki/topics/security/aws-continuum"
        self.assertEqual({path.name for path in actual.iterdir()}, expected)
        for route in ("index.html", "wiki/topics/index.html"):
            self.assertIn("/wiki/topics/security/", (SITE / route).read_text())
        navigation = (ROOT / "_data/navigation.yml").read_text()
        security = navigation.split("  - label: 云与应用安全\n", 1)[1].split(
            "  - label: 深度学习专题\n", 1)[0]
        self.assertNotIn("group:", security)
        self.assertEqual(set(re.findall(r"url: (/wiki/topics/security/\S*)", security)),
                         {"/wiki/topics/security/"} |
                         {"/" + route.replace("index.html", "") for route in ROUTES.values()})


if __name__ == "__main__":
    unittest.main()
