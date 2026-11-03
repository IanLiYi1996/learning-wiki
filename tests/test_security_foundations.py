"""Additive security reader contracts; do not replace existing product study tests."""
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
from test_security_study import samples

ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/security"
BOOK = TOPIC / "security-101"
SITE = Path(os.environ.get("SECURITY_FOUNDATIONS_SITE", ROOT / "_site")).resolve()
FILES = ("README.md", "01-risk-and-governance.md", "02-identity-and-organization.md",
         "03-network-and-zero-trust.md", "04-data-keys-and-privacy.md",
         "05-app-and-api-security.md", "06-devsecops-and-supply-chain.md",
         "07-workload-and-container-security.md", "08-detection-and-incident-response.md",
         "09-ai-and-agent-security.md", "10-resilience-and-recovery.md",
         "learning-roadmap.md", "lab.md", "sources.md")
COUNTS = (1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1, 1, 1, 0)
ROUTES = {name: "wiki/topics/security/security-101/" +
          name.replace("README.md", "index.html").replace(".md", ".html") for name in FILES}


def docs():
    return {name: (BOOK / name).read_text() for name in FILES}


def figures():
    return json.loads((ROOT / "scripts/figures/security-foundations.json").read_text())


class FoundationsSourceTests(PaymentsChecks):
    def test_fourteen_complete_pages_and_public_sources(self):
        self.assertEqual({path.name for path in BOOK.iterdir()}, set(FILES) | {"sources.json"})
        for name, source in docs().items():
            self.assertRegex(source, r"\A# ")
            self.assertIn("2026-11-03", source)
            self.assertGreater(len(ILLUSTRATION.sub("", source)), 1800, name)
            self.assert_public(source, name)
            self.assertNotRegex(source, r"TODO|TBD|```mermaid|待主代理|由主代理|(?:上午|下午)\s*\d+:\d+")
            if re.match(r"\d\d-", name):
                self.assertRegex(source, r"自测|自测与答案|三题")
                self.assertGreaterEqual(len({target for _, target in markdown_links(source)
                                             if urlsplit(target).scheme == "https"}), 8)
        for path in [BOOK / "sources.json", ROOT / "scripts/figures/security-foundations.json",
                     *TOPIC.glob("images/safe-*.svg")]:
            self.assert_public(path.read_text(), path.name)

    def test_baselines_are_not_claimed_latest_or_live_operations(self):
        ledger = json.loads((BOOK / "sources.json").read_text())
        self.assertEqual(ledger["research_date"], "2026-11-03")
        self.assertFalse(ledger["account_accessed"])
        self.assertFalse(ledger["real_security_operations_executed"])
        self.assertIn("not_latest_guarantees", ledger["scope"])
        self.assertEqual(len(ledger["selected_baselines"]), 9)
        self.assertEqual(len(ledger["key_sources"]), 25)
        self.assertEqual(len({row["id"] for row in ledger["key_sources"]}), 25)
        urls = {target for source in docs().values() for _, target in markdown_links(source)}
        for row in ledger["key_sources"]:
            self.assertIn(row["url"], urls, row["id"])
            self.assertEqual(urlsplit(row["url"]).scheme, "https")
            self.assertTrue(row["scope"])
        for phrase in ("不宣称", "未执行", "不是 IAM", "不是密码学审批",
                       "MATCH_FOR_REVIEW", "None", "0.5"):
            self.assertIn(phrase, "\n".join(docs().values()))

    def test_boundary_conditions_remain_explicit(self):
        required = {
            "01-risk-and-governance.md": ("Profiles", "Tiers", "合规", "不是"),
            "02-identity-and-organization.md": ("角色会话", "隐式拒绝", "管理账户", "OIDC", "RCP"),
            "03-network-and-zero-trust.md": ("无状态", "IMDS", "NAT", "逐资源授权"),
            "04-data-keys-and-privacy.md": ("一律双重 Allow", "预签名 URL", "副本", "撤销"),
            "05-app-and-api-security.md": ("BOLA", "BFLA", "BOPLA", "未触发异步副作用"),
            "06-devsecops-and-supply-chain.md": ("SSDF 1.1", "SLSA v1.2", "fork", "skipped"),
            "07-workload-and-container-security.md": ("不支持 EKS on Fargate", "audit", "IMDS", "RBAC"),
            "08-detection-and-incident-response.md": ("90 天", "OCSF", "证据", "不一定"),
            "09-ai-and-agent-security.md": ("toolResult", "toolSpec", "版本", "不是 IAM"),
            "10-resilience-and-recovery.md": ("30 分钟", "70 分钟", "validation", "宽限期"),
        }
        for name, phrases in required.items():
            for phrase in phrases:
                self.assertIn(phrase, docs()[name], name)

    def test_all_local_links_resolve_without_new_fragment_guessing(self):
        for path in [TOPIC / "README.md", *(BOOK / name for name in FILES)]:
            source = path.read_text()
            for target in [target for _, target in markdown_links(source)] + Page(source).links:
                part = urlsplit(target)
                if part.scheme or part.netloc:
                    self.assertNotEqual(part.scheme, "http")
                    continue
                file = (path.parent / unquote(part.path)).resolve() if part.path else path
                self.assertTrue(file.is_relative_to(ROOT))
                self.assertTrue(file.is_file(), f"{path.name}: {target}")
                if part.fragment:
                    self.assertIn(unquote(part.fragment), Page(file.read_text()).ids)

    def test_sixteen_distinct_asset_pairs_and_exact_placements(self):
        from test_figures import FIGURES
        manifest = figures()
        self.assertEqual(len(manifest), 16)
        self.assertEqual(len({row["id"] for row in manifest}), 16)
        self.assertEqual(sum(len(row["placements"]) for row in manifest), 16)
        placed = Counter()
        for figure in manifest:
            self.assertEqual(figure["topic"], "security")
            self.assertRegex(figure["id"], r"^safe-[a-z0-9-]+$")
            svg = TOPIC / "images" / (figure["id"] + ".svg")
            self.assertEqual(svg.read_text(), FIGURES.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            if figure["kind"] == "compare":
                self.assertEqual(figure["footer_gap"], 64)
                tree = ET.fromstring(svg.read_text())
                ns = {"s": "http://www.w3.org/2000/svg"}
                cells = [row for row in tree.findall(".//s:rect", ns) if row.get("x")]
                bottom = max(float(row.get("y")) + float(row.get("height")) for row in cells)
                line = tree.findall(".//s:line", ns)[-1]
                self.assertGreaterEqual(float(line.get("y1")), bottom + 32)
            for placement in figure["placements"]:
                path = ROOT / placement["file"]
                self.assertEqual(path.parent, BOOK)
                source = docs()[path.name]
                self.assertEqual(source.splitlines().count(placement["after"]), 1)
                marker = figure["id"] + "-" + hashlib.sha256(placement["after"].encode()).hexdigest()[:10]
                body = [body for key, body in ILLUSTRATION.findall(source) if key == marker]
                self.assertEqual(len(body), 1)
                self.assertIn(f"../images/{figure['id']}.png", body[0])
                placed[path.name] += 1
        for name, count in zip(FILES, COUNTS):
            self.assertEqual(placed[name], count)
            self.assertEqual(len(ILLUSTRATION.findall(docs()[name])), count)
        expected = {row["id"] + "." + ext for row in manifest for ext in ("svg", "png")}
        self.assertEqual({path.name for path in TOPIC.glob("images/safe-*")}, expected)

    def test_lab_links_and_existing_product_reader_retained(self):
        for filename in ("scripts/security_foundations_lab.py", "tests/test_security_foundations_lab.py"):
            self.assertTrue((ROOT / filename).is_file())
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + filename,
                          docs()["lab.md"])
        self.assertNotIn("认证课程", docs()["learning-roadmap.md"])
        self.assertIn("四张客户候选", docs()["learning-roadmap.md"])
        self.assertIn("aws-continuum/README.md", docs()["README.md"])
        self.assertTrue((TOPIC / "aws-continuum/sources.json").is_file())


class FoundationsBuildTests(PaymentsChecks):
    @classmethod
    def setUpClass(cls):
        if not (SITE / "search.json").is_file():
            raise AssertionError("Build Jekyll before checking the security foundations")

    def local(self, route, target):
        part = urlsplit(urljoin("https://local.invalid" + self.base + "/" + route, target))
        if part.netloc != "local.invalid":
            return None
        path = SITE / unquote(part.path[len(self.base):]).lstrip("/")
        if not path.suffix:
            path /= "index.html"
        self.assertTrue(path.resolve().is_relative_to(SITE))
        self.assertTrue(path.is_file(), target)
        if part.fragment and path.suffix == ".html":
            self.assertIn(unquote(part.fragment), Page(path.read_text()).ids)
        return path

    def test_fourteen_exact_routes_search_titles_prose_links_and_navigation(self):
        records = json.loads((SITE / "search.json").read_text())
        self.base = Page((SITE / ROUTES["README.md"]).read_text()).base
        selected = [row for row in records if urlsplit(row["url"]).path.startswith(
            self.base + "/wiki/topics/security/security-101/")]
        self.assertEqual(Counter(row["url"] for row in selected),
                         Counter(self.base + "/" + route.replace("index.html", "")
                                 for route in ROUTES.values()))
        for name, route in ROUTES.items():
            source, html = docs()[name], (SITE / route).read_text()
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
                path = self.local(route, target)
                if path:
                    self.assertNotEqual(path.suffix, ".md")
            for expected in ROUTES.values():
                self.assertIn(self.base + "/" + expected.replace("index.html", ""),
                              page.sidebar_links)
            self.assertIn(self.base + "/wiki/topics/security/aws-continuum/", page.sidebar_links)

    def test_built_assets_are_exact_and_in_the_intended_section(self):
        actual = {}
        for name, count in zip(FILES, COUNTS):
            route = ROUTES[name]
            page = Page((SITE / route).read_text())
            self.base = page.base
            self.assertEqual(len(page.images), count, name)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    path = self.local(route, value["src"])
                    self.assertTrue(value["alt"])
                    self.assertEqual(path.read_bytes(), (ROOT / path.relative_to(SITE)).read_bytes())
                    actual[(name, path.stem)] = heading
        for figure in figures():
            for ext in ("svg", "png"):
                path = Path(f"wiki/topics/security/images/{figure['id']}.{ext}")
                self.assertEqual((SITE / path).read_bytes(), (ROOT / path).read_bytes())
            for placement in figure["placements"]:
                self.assertEqual(actual[(Path(placement["file"]).name, figure["id"])],
                                 placement["after"].lstrip("# "))

    def test_scope_files_root_entries_and_old_reader_search_are_retained(self):
        expected = set(FILES) | {name.replace(".md", ".html") for name in FILES} | {
            "index.html", "README.html", "sources.json"}
        self.assertEqual({path.name for path in (SITE / "wiki/topics/security/security-101").iterdir()},
                         expected)
        for route in ("index.html", "wiki/topics/index.html", "wiki/topics/security/index.html"):
            html = (SITE / route).read_text()
            self.assertIn("/wiki/topics/security/security-101/", html)
            self.assertIn("/wiki/topics/security/aws-continuum/", html)
        nav = (ROOT / "_data/navigation.yml").read_text()
        routes = set(re.findall(r"url: (/wiki/topics/security/security-101/\S*)", nav))
        self.assertEqual(routes, {"/" + route.replace("index.html", "") for route in ROUTES.values()})
        records = json.loads((SITE / "search.json").read_text())
        security = [row for row in records if "/wiki/topics/security/" in urlsplit(row["url"]).path]
        self.assertEqual(len(security), 24)
        self.assertEqual(len({row["url"] for row in security}), 24)


if __name__ == "__main__":
    unittest.main()
