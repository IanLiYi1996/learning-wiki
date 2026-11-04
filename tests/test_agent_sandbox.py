"""Offline teaching/book contracts; optional AGENT_SANDBOX_SITE build checks."""

from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from test_payments import ILLUSTRATION, Page, markdown_links


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/agent-sandbox"
PREFIX = "wiki/topics/agent-sandbox/"
CHAPTERS = (
    "01-system-model-and-threats.md", "02-linux-and-containers.md", "03-gvisor.md",
    "04-microvm-and-kata.md", "05-wasm-and-confidential-computing.md",
    "06-lifecycle-and-orchestration.md", "07-platform-landscape.md",
    "08-selection-and-architectures.md", "09-network-identity-and-data.md",
    "10-production-and-benchmarks.md",
)
FILES = ("README.md",) + CHAPTERS + (
    "learning-roadmap.md", "glossary.md", "lab.md", "sources.md",
)
ROUTES = {name: PREFIX + ("index.html" if name == "README.md" else
                         name.replace(".md", ".html")) for name in FILES}
SITE = Path(os.environ.get("AGENT_SANDBOX_SITE", ROOT / "_site")).resolve()
spec = importlib.util.spec_from_file_location(
    "agent_sandbox_lab", ROOT / "scripts/agent_sandbox_lab.py")
LAB = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = LAB
spec.loader.exec_module(LAB)


def documents():
    return {name: (TOPIC / name).read_text(encoding="utf-8") for name in FILES}


def manifest():
    return json.loads((ROOT / "scripts/figures/agent-sandbox.json").read_text())


class TeachingTests(unittest.TestCase):
    def test_unknown_and_false_do_not_pass_gates(self):
        for value in (None, False, 0, 1, "true", "false", [], {}):
            with self.subTest(value=value):
                evidence = dict.fromkeys(LAB.REQUIRED, True)
                evidence["runtime"] = value
                self.assertEqual(LAB.admit(evidence),
                                 {"admitted": False, "failed_gates": ["runtime"]})
        self.assertEqual(LAB.admit({})["failed_gates"], list(LAB.REQUIRED))

    def test_latency_only_compares_admitted_records(self):
        result = LAB.admission_demo()
        self.assertEqual(result["winner"], "vetted_example")
        self.assertEqual([row["admitted"] for row in result["checks"]],
                         [False, False, True, True])
        self.assertIsNone(LAB.select([])["winner"])
        self.assertIsNone(LAB.select([
            {"name": "none", "first_command_ms": 1, "evidence": {}}])["winner"])

    def test_selection_validates_names_and_latency(self):
        base = {"name": "a", "first_command_ms": 100,
                "evidence": dict.fromkeys(LAB.REQUIRED, True)}
        for value in (True, 0, -1, float("inf"), float("nan"), "10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                LAB.select([{**base, "first_command_ms": value}])
        for name in ("", " ", None):
            with self.assertRaises(ValueError):
                LAB.select([{**base, "name": name}])
        with self.assertRaises(ValueError):
            LAB.select([base, base])

    def test_capacity_matches_documented_arithmetic(self):
        result = LAB.capacity(2, 30, 0.7, 10, 512)
        self.assertEqual(result["mean_in_service"], 60)
        self.assertEqual(result["online_slots"], 86)
        self.assertEqual(result["total_slots"], 96)
        self.assertEqual(result["slot_memory_mib"], 48 * 1024)
        self.assertEqual(LAB.capacity(0, 30, 1, 0, 512)["total_slots"], 0)

    def test_capacity_rejects_invalid_and_nonfinite_inputs(self):
        for index, values in (
            (0, (-1, True, float("inf"), float("nan"), "2", 10 ** 1000)),
            (1, (-1, False, float("inf"), float("nan"))),
            (2, (0, -1, 1.01, True, float("nan"))),
            (3, (-1, 1.5, True)),
            (4, (0, -1, 1.5, True)),
        ):
            for value in values:
                args = [2, 30, 0.7, 10, 512]
                args[index] = value
                with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                    LAB.capacity(*args)
        with self.assertRaises(ValueError):
            LAB.capacity(1e308, 1e308, 0.7, 10, 512)
        with self.assertRaises(ValueError):
            LAB.capacity(1e308, 1, 1e-308, 10, 512)

    def test_lifecycle_denies_stale_wrong_and_terminal_contexts(self):
        result = LAB.lifecycle_demo()
        self.assertEqual(result["checks"], {
            "before_ready": False, "correct_context": True, "wrong_tenant": False,
            "wrong_policy": False, "while_paused": False, "stale_generation": False,
            "new_generation": True, "after_termination": False,
        })
        self.assertEqual(result["generation"], 2)
        self.assertEqual(result["final_state"], "terminated")
        ready = LAB.Session("a", "p", state="ready")
        self.assertFalse(ready.allows("a", True, "p"))
        self.assertFalse(ready.allows("a", 1.0, "p"))

    def test_state_transitions_and_record_validation(self):
        session = LAB.Session("a", "p")
        with self.assertRaises(ValueError):
            session.advance("running")
        session.advance("terminated")
        for state in LAB.TRANSITIONS:
            with self.subTest(state=state), self.assertRaises(ValueError):
                session.advance(state)
        for kwargs in (
            {"tenant": ""}, {"policy": ""}, {"generation": 0},
            {"generation": True}, {"state": "unknown"},
        ):
            args = {"tenant": "a", "policy": "p", **kwargs}
            with self.assertRaises(ValueError):
                LAB.Session(**args)

    def test_deterministic_json_and_no_external_execution(self):
        encoded = json.dumps(LAB.demos(), allow_nan=False)
        self.assertEqual(encoded, json.dumps(LAB.demos(), allow_nan=False))
        self.assertIn("synthetic", json.loads(encoded)["scope"])
        source = (ROOT / "scripts/agent_sandbox_lab.py").read_text()
        self.assertNotRegex(source, r"\b(?:subprocess|socket|urllib|requests|exec|eval)\s*[.(]")


class DocumentTests(unittest.TestCase):
    def test_fifteen_complete_public_pages(self):
        docs = documents()
        self.assertEqual({path.name for path in TOPIC.glob("*.md")}, set(FILES))
        for name, text in docs.items():
            with self.subTest(page=name):
                self.assertTrue(text.startswith("# "))
                self.assertIn("2026-11-04", text)
                self.assertGreater(len(ILLUSTRATION.sub("", text)), 1000)
                self.assertNotRegex(text, r"TODO|TBD|待主代理|由主代理|```mermaid")
                self.assertNotRegex(text, r"/home/|/Users/|file://|research-internal")
        for name in CHAPTERS:
            self.assertGreater(len(ILLUSTRATION.sub("", docs[name])), 2000, name)
            self.assertGreaterEqual(len({url for _, url in markdown_links(docs[name])
                                        if urlsplit(url).scheme == "https"}), 2, name)

    def test_relative_links_and_reference_definitions(self):
        for name, text in documents().items():
            definitions = set(re.findall(r"(?m)^\[([^\]]+)\]:", text))
            references = set(re.findall(r"(?<!!)\[[^\]\n]+\]\[([^\]\n]+)\]", text))
            self.assertTrue(references <= definitions, name)
            for image, target in markdown_links(text):
                part = urlsplit(target)
                if part.scheme or part.netloc:
                    self.assertEqual(part.scheme, "https", target)
                    self.assertFalse(image, "Remote diagram")
                    continue
                if not part.path:
                    continue
                path = (TOPIC / unquote(part.path)).resolve()
                self.assertTrue(path.is_relative_to(ROOT), target)
                self.assertTrue(path.is_file(), f"{name}: {target}")

    def test_sources_cover_all_external_fact_links(self):
        docs = documents()
        ledger = {url for _, url in markdown_links(docs["sources.md"])}
        urls = {url for name, text in docs.items() if name != "lab.md"
                for _, url in markdown_links(text) if urlsplit(url).scheme == "https"}
        self.assertTrue(urls <= ledger, sorted(urls - ledger))
        self.assertGreaterEqual(len(urls), 80)
        for phrase in ("未做", "固定提交", "Deep Research", "v0.1.7", "v0.227",
                       "Preview", "未知", "51.0.0-dev"):
            self.assertIn(phrase, docs["sources.md"])
        self.assertIn("调用方自报字段不能作为信任根", docs["lab.md"])
        self.assertIn("共享 host kernel", docs["07-platform-landscape.md"])
        self.assertIn("已移除", docs["09-network-identity-and-data.md"])
        self.assertIn("不执行网络流量过滤", docs["04-microvm-and-kata.md"])

    def test_four_distinct_figures_and_eight_local_placements(self):
        rows = manifest()
        self.assertEqual(len(rows), 4)
        self.assertEqual(len({row["id"] for row in rows}), 4)
        self.assertEqual(sum(len(row["placements"]) for row in rows), 8)
        for row in rows:
            stem = TOPIC / "images" / row["id"]
            tree = ET.parse(stem.with_suffix(".svg")).getroot()
            self.assertIsNotNone(tree.find("{http://www.w3.org/2000/svg}title"))
            self.assertIsNotNone(tree.find("{http://www.w3.org/2000/svg}desc"))
            width, height = struct.unpack(">II", stem.with_suffix(".png").read_bytes()[16:24])
            self.assertEqual((width, height),
                             (int(tree.attrib["width"]) * 2, int(tree.attrib["height"]) * 2))
            for placement in row["placements"]:
                text = (ROOT / placement["file"]).read_text()
                self.assertEqual(text.splitlines().count(placement["after"]), 1)
                self.assertIn("<!-- illustration: " + row["id"] + "-", text)
                self.assertIn(f"images/{row['id']}.png)", text)

    def test_navigation_and_existing_topic_connections(self):
        self.assertIn(PREFIX + "README.md", (ROOT / "README.md").read_text())
        self.assertIn("agent-sandbox/README.md", (ROOT / "wiki/topics/README.md").read_text())
        self.assertIn("../agent-sandbox/README.md",
                      (ROOT / "wiki/topics/security/README.md").read_text())
        nav = (ROOT / "_data/navigation.yml").read_text()
        for route in ROUTES.values():
            self.assertIn("url: /" + route.replace("index.html", ""), nav)


@unittest.skipUnless(os.environ.get("AGENT_SANDBOX_SITE"), "Set an actual Jekyll build path")
class BuiltSiteTests(unittest.TestCase):
    def test_all_routes_links_images_and_sidebar(self):
        for name, route in ROUTES.items():
            with self.subTest(page=name):
                page = Page((SITE / route).read_text())
                self.assertEqual(page.article_count, 1)
                self.assertFalse([key for key, count in Counter(page.ids).items() if count > 1])
                self.assertTrue(any(level == "h1" for level, _ in page.headings))
                for wanted in ROUTES.values():
                    self.assertIn(page.base + "/" + wanted.replace("index.html", ""),
                                  page.sidebar_links)
                for target in page.article_links + [image["src"] for image in page.images]:
                    part = urlsplit(target)
                    if part.scheme or part.netloc:
                        continue
                    joined = urlsplit(urljoin(page.base + "/" + route, target))
                    candidate = SITE / unquote(joined.path).removeprefix(page.base + "/")
                    if candidate.is_dir():
                        candidate /= "index.html"
                    self.assertTrue(candidate.resolve().is_relative_to(SITE))
                    self.assertTrue(candidate.is_file(), f"{name}: {target}")
                    self.assertNotEqual(candidate.suffix, ".md", target)
                    if joined.fragment:
                        self.assertIn(unquote(joined.fragment),
                                      Page(candidate.read_text()).ids)

    def test_fifteen_unique_search_routes(self):
        records = json.loads((SITE / "search.json").read_text())
        selected = [row for row in records if "/" + PREFIX in row["url"]]
        self.assertEqual(len(selected), len(FILES))
        self.assertEqual(len({row["url"] for row in selected}), len(FILES))
        page = Page((SITE / ROUTES["README.md"]).read_text())
        self.assertEqual({row["url"] for row in selected},
                         {page.base + "/" + route.replace("index.html", "")
                          for route in ROUTES.values()})
        for row in selected:
            self.assertTrue(row["title"] and row["text"])


if __name__ == "__main__":
    unittest.main()
