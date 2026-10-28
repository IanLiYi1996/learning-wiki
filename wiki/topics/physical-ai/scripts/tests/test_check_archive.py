"""Integrity-check behavior, including missing files and changed records."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "check_archive", Path(__file__).resolve().parents[1] / "check_archive.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ArchiveCheckTests(unittest.TestCase):
    def create_archive(self, root):
        """Write only disposable fixtures, never the real archived material."""
        contents = {
            "sample.md": "原始资料\n",
            "README.md": "[正文](sample.md)",
            "industry/products.json": json.dumps([{"id": "p", "sources": []}]),
            "industry/products.csv": 'id,sources\np,[]\n',
            "advanced/papers.json": "[]",
            "industry/chapters/01.md": "# 产品阶段",
            "advanced/chapters/01.md": "# 底层原理",
            "notes/learning-papers.json": "[]",
            "conferences/gtc-berlin-2026/notes/paper-metadata.json": "[]",
            "advanced/frontmatter.md": "# 原理篇前言",
            "industry/frontmatter.md": "# 行业篇前言",
        }
        for relative, text in contents.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        manifest = {
            "required_supporting_files": [
                relative for relative in contents if relative != "sample.md"],
            "deliverables": [{"path": "sample.md", "sha256": hashlib.sha256(
                contents["sample.md"].encode("utf-8")).hexdigest()}],
            "expected": {"deliverables": 1, "products": 1, "industry_chapters": 1,
                         "principle_chapters": 1, "principle_papers": 0},
        }
        (root / "archive-manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_fenced_and_inline_code_are_not_links(self):
        text = "[a](one.md)\n~~~\n[bad](missing.md)\n~~~\n`[code](x.md)`\n[r]: two.md"
        self.assertEqual(CHECK.markdown_targets(text), ["one.md", "two.md"])

    def test_nonmatching_fence_does_not_end_block(self):
        text = "````\n```\n[hidden](missing.md)\n````\n[real](present.md)"
        self.assertEqual(CHECK.markdown_targets(text), ["present.md"])

    def test_nested_labels_and_parenthesized_destinations(self):
        text = "[report [draft]](missing.md)\n[report](report(2026).md)"
        self.assertEqual(CHECK.markdown_targets(text),
                         ["missing.md", "report(2026).md"])

    def test_code_spans_indented_code_and_trailing_fence_text(self):
        text = ("    [indented](absent.md)\n"
                "``a ` [example](absent.md)``\n"
                "```\n```not-a-closer\n[hidden](absent.md)\n```\n"
                "[real](present.md)")
        self.assertEqual(CHECK.markdown_targets(text), ["present.md"])

    def test_external_and_anchor_links_do_not_require_local_files(self):
        text = "[a](https://example.com/a)\n[b](#section)\n[c](//example.com/a)"
        self.assertEqual(CHECK.missing_local_links(Path("README.md"), text), [])

    def test_missing_local_link_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            self.assertEqual(CHECK.missing_local_links(path, "[x](absent.md)"),
                             ["absent.md"])

    def test_utf8_relative_link_resolves(self):
        with tempfile.TemporaryDirectory() as directory:
            # Fixture creation is isolated to a temporary directory.
            (Path(directory) / "中文.md").touch()
            path = Path(directory) / "README.md"
            text = "[x](%E4%B8%AD%E6%96%87.md#section)"
            self.assertEqual(CHECK.missing_local_links(path, text), [])

    def test_angle_destinations_and_absolute_links(self):
        self.assertEqual(CHECK.markdown_targets("[x](<with space.md>)"),
                         ["with space.md"])
        with self.assertRaisesRegex(ValueError, "Absolute local link"):
            CHECK.missing_local_links(Path("README.md"), "[x](%2Ftmp%2Fx.md)")

    def test_absolute_and_traversal_manifest_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (str(root / "x.md"), "../x.md"):
                with self.subTest(relative=relative), self.assertRaises(ValueError):
                    CHECK.archive_path(root, relative)

    def test_symlink_manifest_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "archive"
            root.mkdir()
            (root / "escape").symlink_to(root.parent, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "outside archive"):
                CHECK.archive_path(root, "escape/sample.md")

    def test_manifest_valid_empty_file_and_tamper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").touch()
            records = [{"path": "sample.md",
                        "sha256": hashlib.sha256(b"").hexdigest()}]
            CHECK.verify_hashes(root, records)
            with self.assertRaises(ValueError):
                CHECK.verify_hashes(root, [{"path": "sample.md", "sha256": "bad"}])
            with self.assertRaises(ValueError):
                CHECK.verify_hashes(root, [{"path": "missing.md", "sha256": "bad"}])
            with self.assertRaises(ValueError):
                CHECK.verify_hashes(root, records + records)
            (root / "sample.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                CHECK.verify_hashes(root, records)

    def test_csv_compound_fields_match_and_changes_fail(self):
        products = [{"id": "p", "sources": [{"url": "https://example.com"}]}]
        rows = [{"id": "p", "sources": '[{"url":"https://example.com"}]'}]
        CHECK.compare_catalogue(products, rows)
        with self.assertRaises(ValueError):
            CHECK.compare_catalogue(products, [{"id": "p", "sources": "[]"}])
        with self.assertRaises(ValueError):
            CHECK.compare_catalogue(products, [])
        with self.assertRaises(ValueError):
            CHECK.compare_catalogue(products, [{"id": "p"}])
        with self.assertRaises(ValueError):
            CHECK.compare_catalogue(products, [{"id": "p", "sources": "{bad"}])
        with self.assertRaisesRegex(ValueError, "CSV/JSON mismatch"):
            CHECK.compare_catalogue([{"id": "p"}], [{"id": "changed"}])

    def test_duplicate_products_are_rejected(self):
        products = [{"id": "p"}, {"id": "p"}]
        with self.assertRaises(ValueError):
            CHECK.compare_catalogue(products, products)

    def test_full_archive_success_without_implicit_text_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_archive(root)
            original = Path.read_text

            def read_without_default_encoding(path, encoding=None, errors=None):
                self.assertIsNotNone(encoding)
                return original(path, encoding=encoding, errors=errors)

            with patch.object(Path, "read_text", read_without_default_encoding):
                result = CHECK.check_archive(root)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["products"], 1)
            self.assertEqual(result["markdown_local_links"], 1)

    def test_count_mismatch_and_bad_json_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.create_archive(root)
            manifest["expected"]["products"] = 2
            (root / "archive-manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Count mismatch: products"):
                CHECK.check_archive(root)
            (root / "advanced/papers.json").write_text("{bad", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                CHECK.check_archive(root)

    def test_host_paths_rejected_and_dependency_json_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_archive(root)
            excluded = root / "node_modules/pkg/bad.json"
            excluded.parent.mkdir(parents=True)
            excluded.write_text("{bad", encoding="utf-8")
            self.assertEqual(CHECK.check_archive(root)["status"], "passed")
            (root / "README.md").write_text("/Users/example/report.md", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Host-specific path"):
                CHECK.check_archive(root)

    def test_cli_success_and_failure_diagnostics(self):
        with patch.object(CHECK, "check_archive", return_value={"status": "passed"}):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(CHECK.main(), 0)
            self.assertEqual(json.loads(output.getvalue()), {"status": "passed"})
        with patch.object(CHECK, "check_archive", side_effect=ValueError("bad hash")):
            output = io.StringIO()
            with redirect_stderr(output):
                self.assertEqual(CHECK.main(), 1)
            self.assertIn("Archive check failed: bad hash", output.getvalue())

    def test_missing_unlinked_metadata_and_frontmatter_are_rejected(self):
        paths = ("notes/learning-papers.json",
                 "conferences/gtc-berlin-2026/notes/paper-metadata.json",
                 "advanced/frontmatter.md", "industry/frontmatter.md")
        for relative in paths:
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.create_archive(root)
                (root / relative).unlink()
                with self.assertRaisesRegex(ValueError, "Missing supporting file"):
                    CHECK.check_archive(root)

    def test_supporting_inventory_duplicates_and_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").touch()
            with self.assertRaisesRegex(ValueError, "Duplicate supporting paths"):
                CHECK.verify_supporting_files(root, ["sample.md", "sample.md"])
            with self.assertRaisesRegex(ValueError, "outside archive"):
                CHECK.verify_supporting_files(root, ["../sample.md"])


if __name__ == "__main__":
    unittest.main()
