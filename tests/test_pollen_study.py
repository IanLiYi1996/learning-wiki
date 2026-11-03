"""Additive checks for the Pollen study; do not rewrite archived Physical AI."""

from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from test_payments import ILLUSTRATION, Page, PaymentsChecks, markdown_links, normalized
from test_deep_learning import readable_samples


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "wiki/topics/physical-ai"
STUDY = TOPIC / "pollen-robotics"
SITE = Path(os.environ.get("POLLEN_SITE", ROOT / "_site")).resolve()
FILES = ("README.md", "robots-and-sdk.md", "teleoperation-and-logging.md",
         "perception-and-simulation.md", "data-and-policy-learning.md",
         "microduck-and-rl.md", "hands-and-actuators.md", "lab.md", "sources.md")
ROUTES = {name: "wiki/topics/physical-ai/pollen-robotics/" +
          name.replace("README.md", "index.html").replace(".md", ".html") for name in FILES}
COUNTS = (2, 1, 1, 2, 1, 1, 1, 1, 0)
# Inspected public snapshots, allowed only within their exact repository URLs.
VERSIONS = {
    "eb42d1f08cf32244443dc46930ff2e17cf5852da": "pollen-robotics/reachy2-sdk",
    "b7000c1255f322826f4d0ad1f1e54d424e55c051": "pollen-robotics/reachy2_core",
    "2bb56b676f235a8d6774474cf053ef4bd8585476": "pollen-robotics/reachy2_sdk_server",
    "6a7cbdd463200fef3a20c2742255ee5089d89561": "pollen-robotics/reachy2-sdk-api",
    "9934da67628c0b41398d0a2fd33316494ada39db": "pollen-robotics/ReachyTeleoperation",
    "1612347e3b1b06a612f5dd79c333090c1d0bd335": "pollen-robotics/Reachy2Teleoperation",
    "e26c6c30e723d80b1ecdaa3ace80f7e84f4d15f2": "pollen-robotics/reachy_mini",
    "feead2b81acdc92ab632f9dc53badf7a450ba19e": "pollen-robotics/reachy2_hdf5_recorder",
    "538b296209cc91d114b8e923c43df9912f5d0559": "pollen-robotics/reachy2-sdk-rerun",
    "e82d31b772c99efbf35f16e8634844ab22e73c1b": "pollen-robotics/grabette",
    "c0e997b15b7b50a485577fa6d059875cfc62e849": "pollen-robotics/grabette-policy",
    "39116d865065a7b8db946f6845ecf6c07042df5f": "pollen-robotics/grabette-slam",
    "997808c1d71056d31bd6f05fc5fde848c849d2bc": "pollen-robotics/microduck",
    "bae39f5900b318f7e87fc485c30a31213cfa14eb": "pollen-robotics/microduck_rl",
    "2d7cfab7c0c1090741e43ba5e3aab5acefb110f7": "pollen-robotics/pollen-vision",
    "f6d8284e812d3b96b557e2e844d55bd09d6e3ee6": "pollen-robotics/reachy2_mujoco",
    "a304471a9685d6a30e45f8bdb552d8db0c91ac32": "pollen-robotics/reachy2_mujoco_server",
    "149948db13b108b9f4a940a5bb94f50422eadd27": "pollen-robotics/reachy2_qpik",
    "3e8241074df3436a3044ced4881e3bb2133aa725": "pollen-robotics/AmazingHand",
    "31bfc548270a306829c7a3acdad19f643f53f618": "pollen-robotics/AmazingHand",
    "1b5a3dc83cb4eae042d535bda3765b9e12a9b8a7": "pollen-robotics/PincOpen",
    "9e547d616af8487c52c5aff68792a74fbc023d79": "pollen-robotics/orbita3d_control",
    "dc54f7ee24b54407d584ebee15bdb35894c206d0": "pollen-robotics/orbita2d_control",
    "19d6c06c17572dafcb31ad5110a902006b58d944": "mujocolab/mjlab",
    "62bd8ce12154340be97e06f7f41a0ca8f116d967": "Rhoban/bam",
}


def documents():
    return {name: (STUDY / name).read_text(encoding="utf-8") for name in FILES}


def figures():
    return json.loads((ROOT / "scripts/figures/pollen-robotics.json").read_text())


def samples(source):
    source = re.sub(r"(?m)^\[[^\]]+\]:\s+\S+.*\n?", "", source)
    source = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]+\]", r"\1", source)
    return readable_samples(source)


class PublicStudyChecks(PaymentsChecks):
    def assert_study_public(self, text, label):
        for revision, repository in VERSIONS.items():
            text = re.sub(
                "(" + re.escape("https://github.com/" + repository) + r"/(?:blob|tree)/)" +
                revision + r'(?=/|[)\s"<>]|$)', r"\1public-revision", text)
        self.assert_public(text, label)


class PollenSourceTests(PublicStudyChecks):
    def test_only_nine_complete_public_pages_and_snapshot_metadata(self):
        self.assertEqual({file.relative_to(STUDY).as_posix()
                          for file in STUDY.rglob("*") if file.is_file()},
                         set(FILES) | {"sources.json"})
        for name, source in documents().items():
            self.assertRegex(source, r"\A# ")
            self.assertIn("2026-11-03", source)
            self.assertGreater(len(ILLUSTRATION.sub("", source)), 1800, name)
            self.assert_study_public(source, name)
            self.assertNotRegex(source, r"TODO|TBD|待主代理|由主代理另行")
        for file in (STUDY / "sources.json", ROOT / "scripts/figures/pollen-robotics.json"):
            self.assert_study_public(file.read_text(), file.name)
        for file in (TOPIC / "images").glob("pollen-*.svg"):
            self.assert_study_public(file.read_text(), file.name)

    def test_snapshot_lock_exact_scope_and_narrow_privacy_exemptions(self):
        lock = json.loads((STUDY / "sources.json").read_text())
        self.assertEqual(lock["research_date"], "2026-11-03")
        self.assertEqual(len(lock["snapshots"]), 23)
        self.assertEqual(len({row["repository"] for row in lock["snapshots"]}), 22)
        self.assertEqual(len(lock["upstream_dependencies"]), 2)
        rows = lock["snapshots"] + lock["upstream_dependencies"]
        versions = {urlsplit(row["url"]).path.split("/")[4]:
                    "/".join(urlsplit(row["url"]).path.split("/")[1:3]) for row in rows}
        self.assertEqual(versions, VERSIONS)
        self.assertEqual({item["parent"] for item in lock["metadata_only"]},
                         {"MarkFzp/act-plus-plus", "octo-models/octo", "ChaoningZhang/MobileSAM"})
        for item in lock["metadata_only"]:
            self.assertTrue(item["fork"])
            self.assertFalse(item["code_audited"])
        for revision, repository in VERSIONS.items():
            self.assert_study_public(f"https://github.com/{repository}/blob/{revision}/file.py", "valid")
            for text in (revision, f"https://github.com/other/repo/tree/{revision}",
                         f"https://github.com/{repository}/blob/{revision}/secret.docx"):
                with self.assertRaises(AssertionError):
                    self.assert_study_public(text, "negative control")

    def test_local_links_and_explicit_fragments(self):
        for name, source in documents().items():
            self.assertEqual(len(Page(source).ids), len(set(Page(source).ids)))
            for target in [url for _, url in markdown_links(source)] + Page(source).links:
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    self.assertNotEqual(parts.scheme, "http")
                    continue
                path = ((STUDY / name).parent / unquote(parts.path)).resolve() \
                    if parts.path else STUDY / name
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(), f"{name}: {target}")
                if parts.fragment:
                    self.assertIn(unquote(parts.fragment), Page(path.read_text()).ids)

    def test_ten_original_diagrams_placement_and_retina_bytes(self):
        manifest = figures()
        self.assertEqual(len(manifest), 10)
        self.assertEqual(sum(len(fig["placements"]) for fig in manifest), 10)
        self.assertEqual(len({fig["id"] for fig in manifest}), 10)
        spec = importlib.util.spec_from_file_location("pollen_figures", ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        placed = Counter()
        for suffix in ("svg", "png"):
            self.assertEqual({path.stem for path in (TOPIC / "images").glob(f"pollen-*.{suffix}")},
                             {fig["id"] for fig in manifest})
        for figure in manifest:
            self.assertEqual(figure["topic"], "physical-ai")
            self.assertIs(figure["archive_assets"], False)
            self.assertRegex(figure["id"], r"^pollen-[a-z0-9-]+$")
            svg = TOPIC / "images" / (figure["id"] + ".svg")
            self.assertEqual(svg.read_text(), renderer.RENDERERS[figure["kind"]](figure))
            self.assert_asset_pair(svg, svg.with_suffix(".png"), figure)
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(STUDY.relative_to(ROOT)).as_posix()
                self.assertIn(name, FILES)
                placed[name] += 1
                identity = figure["id"] + "-" + hashlib.sha256(placement["after"].encode()).hexdigest()[:10]
                source = documents()[name]
                self.assertEqual(source.splitlines().count(placement["after"]), 1)
                blocks = [body for marker, body in ILLUSTRATION.findall(source) if marker == identity]
                self.assertEqual(len(blocks), 1)
                target = os.path.relpath(svg.with_suffix(".png"), (STUDY / name).parent)
                self.assertIn(f"]({target})", blocks[0])
                self.assertIn(f"*图：{figure['title']}。", blocks[0])
        for name, count in zip(FILES, COUNTS):
            self.assertEqual(placed[name], count)
            self.assertEqual(len(ILLUSTRATION.findall(documents()[name])), count)

    def test_additive_navigation_and_execution_boundaries(self):
        navigation = (ROOT / "_data/navigation.yml").read_text()
        actual = set(re.findall(r"(?m)^\s+url: (/wiki/topics/physical-ai/pollen-robotics/\S*)\s*$",
                                navigation))
        self.assertEqual(actual, {"/" + rel.replace("index.html", "") for rel in ROUTES.values()})
        source = documents()["sources.md"]
        for phrase in ("22 个仓库", "23 份快照", "第一级", "第三级", "未执行", "归档"):
            self.assertIn(phrase, source)
        lab = documents()["lab.md"]
        for phrase in ("0.088", "单位", "不执行动作", "不是 Pollen 的硬件测试"):
            self.assertIn(phrase, lab)
        for filename in ("scripts/pollen_contract_lab.py", "tests/test_pollen_contract_lab.py"):
            self.assertIn("https://github.com/IanLiYi1996/learning-wiki/blob/main/" + filename, lab)
            self.assertTrue((ROOT / filename).is_file())

    def test_new_diagrams_do_not_rewrite_the_old_archive_manifest(self):
        import tempfile
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location("archive_pollen_figures", ROOT / "scripts/render_figures.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        old = json.loads((TOPIC / "illustrations-manifest.json").read_text())
        self.assertEqual(old["date"], "2026-10-29")
        self.assertEqual(len(old["assets"]), 56)
        self.assertFalse(any("/pollen-" in row["path"] for row in old["assets"]))
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            (temporary_root / "wiki/topics/physical-ai").mkdir(parents=True)
            # New supplement figures are intentionally absent on disk here.
            # Exclusion must occur before trying to hash archived resources.
            with patch.object(renderer, "ROOT", temporary_root):
                renderer.asset_manifest(figures())
            result = json.loads((temporary_root / "wiki/topics/physical-ai/illustrations-manifest.json").read_text())
            self.assertEqual(result["assets"], [])


@unittest.skipUnless(SITE.is_dir(), "Build Jekyll first")
class PollenSiteTests(PublicStudyChecks):
    def page(self, route):
        self.assertTrue((SITE / route).is_file(), route)
        return Page((SITE / route).read_text())

    def local_target(self, route, target):
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            return None
        base = self.page(route).base
        resolved = urlsplit(urljoin(base + "/" + route, target))
        self.assertTrue(resolved.path.startswith(base + "/"))
        file = SITE / unquote(resolved.path[len(base) + 1:])
        if resolved.path.endswith("/"):
            file /= "index.html"
        self.assertTrue(file.resolve().is_relative_to(SITE))
        self.assertTrue(file.is_file(), target)
        if resolved.fragment and file.suffix == ".html":
            self.assertIn(unquote(resolved.fragment), Page(file.read_text()).ids)
        return file

    def test_exact_search_routes_titles_prose_and_links(self):
        base = self.page(ROUTES["README.md"]).base
        records = json.loads((SITE / "search.json").read_text())
        selected = [record for record in records if urlsplit(record["url"]).path.startswith(
            base + "/wiki/topics/physical-ai/pollen-robotics/")]
        self.assertEqual(Counter(record["url"] for record in selected),
                         Counter(base + "/" + route.replace("index.html", "") for route in ROUTES.values()))
        for name, route in ROUTES.items():
            page, source = self.page(route), documents()[name]
            self.assertEqual(page.article_count, 1)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            self.assertTrue(set(Page(source).ids).issubset(page.article_ids))
            record = next(item for item in selected if item["url"] ==
                          base + "/" + route.replace("index.html", ""))
            self.assertEqual(record["title"], re.search(r"(?m)^# (.+)$", source)[1])
            self.assert_study_public((SITE / route).read_text(), route)
            for sample in samples(source):
                self.assertIn(sample, normalized("".join(page.text)), name)
                self.assertIn(sample, normalized(record["text"]), name)
            for target in page.article_links:
                local = self.local_target(route, target)
                if local:
                    self.assertNotEqual(local.suffix, ".md")
            for relative in ROUTES.values():
                self.assertIn(base + "/" + relative.replace("index.html", ""), page.sidebar_links)

    def test_built_assets_caption_and_section(self):
        actual = {}
        for (name, route), count in zip(ROUTES.items(), COUNTS):
            page = self.page(route)
            self.assertEqual(len(page.images), count)
            heading = None
            for kind, value in page.events:
                if kind == "heading":
                    heading = value[1]
                elif kind == "image":
                    file = self.local_target(route, value["src"])
                    self.assertTrue(value["alt"])
                    actual[(name, file.stem)] = heading
        for figure in figures():
            for suffix in ("svg", "png"):
                relative = f"wiki/topics/physical-ai/images/{figure['id']}.{suffix}"
                self.assertEqual((SITE / relative).read_bytes(), (ROOT / relative).read_bytes())
            for placement in figure["placements"]:
                name = Path(placement["file"]).relative_to(STUDY.relative_to(ROOT)).as_posix()
                self.assertEqual(actual[(name, figure["id"])], placement["after"].lstrip("# "))

    def test_no_extra_study_files_and_root_reader_exposes_new_entry(self):
        expected = set(FILES) | {file.replace(".md", ".html") for file in FILES} | {
            "index.html", "README.html", "sources.json"}
        published = SITE / "wiki/topics/physical-ai/pollen-robotics"
        self.assertEqual({file.relative_to(published).as_posix()
                          for file in published.rglob("*") if file.is_file()}, expected)
        root = (SITE / "wiki/topics/physical-ai/index.html").read_text()
        self.assertIn('data-physical-supplement', root)
        self.assertIn("/wiki/topics/physical-ai/pollen-robotics/", root)
        self.assertEqual(root.count("data-reading-book="), 4)
        for route in ("industry", "advanced", "conferences/gtc-berlin-2026"):
            self.assertNotIn('data-physical-supplement',
                             (SITE / f"wiki/topics/physical-ai/{route}/index.html").read_text())
        self.assertFalse((SITE / "scripts").exists())
        self.assertFalse((SITE / "tests").exists())
