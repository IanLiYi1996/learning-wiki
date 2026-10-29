"""Publication checks run against isolated synthetic notes, never real secrets."""

from contextlib import redirect_stdout
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

CHECKER_PATH = Path(__file__).resolve().parents[1] / "check_topic.py"
SPEC = importlib.util.spec_from_file_location("topic_checker", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class PublicationChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.topic = self.repo / "wiki/topics/blockchain"
        self.topic.mkdir(parents=True)
        self.previous_root = CHECKER.ROOT
        CHECKER.ROOT = self.topic
        for folder in ("chapters", "upgrades"):
            (self.topic / folder).mkdir()
        for number in range(1, 8):
            (self.topic / "chapters" / f"{number:02d}.md").write_text(
                "# Chapter\n\n[E01]\n", encoding="utf-8"
            )
        for filename in CHECKER.EXPECTED_UPGRADES:
            (self.topic / "upgrades" / filename).write_text("# Upgrade\n", encoding="utf-8")
        (self.topic / "upgrades/README.md").write_text(
            "\n".join(f"[Read]({name})" for name in sorted(CHECKER.EXPECTED_UPGRADES)),
            encoding="utf-8",
        )
        (self.topic / "slide-map.md").write_text(
            "\n".join(f"| {page} | Topic |" for page in range(1, 61)), encoding="utf-8"
        )
        (self.topic / "sources.md").write_text("| E01 | Source | Fact |\n", encoding="utf-8")
        for filename in ("corrections.md", "glossary.md", "README.md"):
            (self.topic / filename).write_text("# Notes\n", encoding="utf-8")
        (self.repo / "README.md").write_text("blockchain/README.md\n", encoding="utf-8")
        (self.repo / "wiki/topics/README.md").write_text("blockchain/README.md\n", encoding="utf-8")

    def tearDown(self):
        CHECKER.ROOT = self.previous_root
        self.temporary.cleanup()

    def run_check(self, source=False):
        output = io.StringIO()
        with redirect_stdout(output):
            failed = CHECKER.check(check_source=source)
        return failed, json.loads(output.getvalue())

    def make_local_archive(self):
        archive = self.topic / "source"
        archive.mkdir()
        ppt_bytes = b"synthetic attachment, not a real PPT"
        (archive / "fixture.pptx").write_bytes(ppt_bytes)
        slides = [
            {"page": page, "text": ["fixture"], "images": []}
            for page in range(1, 61)
        ]
        for page in (58, 59):
            filename = f"image-{page}.png"
            data = f"synthetic image {page}".encode()
            (archive / filename).write_bytes(data)
            slides[page - 1]["images"] = [
                {"path": filename, "sha256": sha256(data).hexdigest()}
            ]
        record = {
            "source_filename": "fixture.pptx",
            "source_sha256": sha256(ppt_bytes).hexdigest(),
            "slide_count": 60,
            "slides": slides,
        }
        (archive / "slides.json").write_text(json.dumps(record), encoding="utf-8")
        (archive / "slides.md").write_text(
            "\n".join(f"## 第 {page} 页：fixture" for page in range(1, 61)),
            encoding="utf-8",
        )
        return archive

    def test_public_clone_requires_no_attachment(self):
        failed, result = self.run_check()
        self.assertFalse(failed)
        self.assertFalse(result["local_source_checked"])
        self.assertIsNone(result["local_archive"])
        self.assertEqual(result["slides_indexed"], 60)
        self.assertEqual(result["upgrade_tutorials"], 6)

    def test_private_markdown_is_not_published_or_checked(self):
        failed, before = self.run_check()
        self.assertFalse(failed)
        archive = self.topic / "source"
        archive.mkdir()
        (archive / "private.md").write_text("[Private](missing) ```", encoding="utf-8")
        failed, after = self.run_check()
        self.assertFalse(failed)
        self.assertEqual(before["markdown_files"], after["markdown_files"])

    def test_private_attachment_link_is_rejected_even_if_file_exists(self):
        archive = self.make_local_archive()
        (self.topic / "README.md").write_text("[PPT](source/fixture.pptx)", encoding="utf-8")
        failed, result = self.run_check()
        self.assertTrue(failed)
        self.assertTrue((archive / "fixture.pptx").exists())
        self.assertTrue(any("private attachment" in error for error in result["errors"]))

    def test_private_link_with_parent_segments_is_rejected(self):
        self.make_local_archive()
        (self.topic / "chapters/01.md").write_text(
            "[PPT](../source/fixture.pptx)", encoding="utf-8"
        )
        failed, result = self.run_check()
        self.assertTrue(failed)
        self.assertTrue(any("private attachment" in error for error in result["errors"]))

    def test_broken_public_link_is_rejected(self):
        (self.topic / "README.md").write_text("[Read](missing.md)", encoding="utf-8")
        failed, result = self.run_check()
        self.assertTrue(failed)
        self.assertTrue(any("Broken internal" in error for error in result["errors"]))

    def test_missing_upgrade_is_rejected(self):
        (self.topic / "upgrades/01-ethereum.md").unlink()
        failed, result = self.run_check()
        self.assertTrue(failed)
        self.assertIn("Expected six named upgrade tutorials", result["errors"])

    def test_unknown_source_id_is_rejected(self):
        (self.topic / "chapters/01.md").write_text("[E99]", encoding="utf-8")
        failed, result = self.run_check()
        self.assertTrue(failed)
        self.assertTrue(any("Unknown source E99" in error for error in result["errors"]))

    def test_explicit_archive_check_succeeds(self):
        self.make_local_archive()
        failed, result = self.run_check(source=True)
        self.assertFalse(failed)
        self.assertTrue(result["local_source_checked"])
        self.assertEqual(result["local_archive"]["pictures"], 2)

    def test_explicit_missing_archive_is_a_failure(self):
        failed, result = self.run_check(source=True)
        self.assertTrue(failed)
        self.assertTrue(any("Local archive check failed" in error for error in result["errors"]))

    def test_tampered_attachment_is_a_failure(self):
        archive = self.make_local_archive()
        (archive / "fixture.pptx").write_bytes(b"tampered")
        failed, result = self.run_check(source=True)
        self.assertTrue(failed)
        self.assertIn("PPT SHA-256 mismatch", result["errors"])

    def test_attachment_path_escape_is_rejected(self):
        archive = self.make_local_archive()
        record_path = archive / "slides.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["source_filename"] = "../README.md"
        record_path.write_text(json.dumps(record), encoding="utf-8")
        failed, result = self.run_check(source=True)
        self.assertTrue(failed)
        self.assertTrue(any("single filename" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
