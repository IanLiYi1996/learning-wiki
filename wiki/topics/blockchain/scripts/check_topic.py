"""Check published notes; opt in to validating the private local attachment."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
SOURCE_ID = re.compile(r"(?<!\w)[BEWCSA]\d{2}\b")
EXPECTED_UPGRADES = {
    "01-ethereum.md",
    "02-solana.md",
    "03-multichain.md",
    "04-stablecoins.md",
    "05-aws-infrastructure.md",
    "06-bitcoin-wallets.md",
}
EXPECTED_SLIDES = 60
EXPECTED_PICTURES = 2


def check_local_archive(errors):
    archive_dir = ROOT / "source"
    record = json.loads((archive_dir / "slides.json").read_text(encoding="utf-8"))
    filename = record["source_filename"]
    if not filename or Path(filename).name != filename:
        raise ValueError("Source filename must be a single filename")
    original = archive_dir / filename
    if hashlib.sha256(original.read_bytes()).hexdigest() != record["source_sha256"]:
        errors.append("PPT SHA-256 mismatch")
    pages = [slide["page"] for slide in record["slides"]]
    if record["slide_count"] != EXPECTED_SLIDES or pages != list(range(1, EXPECTED_SLIDES + 1)):
        errors.append("Expected exactly 60 ordered slides")
    extracted = (archive_dir / "slides.md").read_text(encoding="utf-8")
    if len(re.findall(r"^## 第 \d+ 页：", extracted, flags=re.M)) != EXPECTED_SLIDES:
        errors.append("Extracted Markdown page count differs")
    picture_count = 0
    for slide in record["slides"]:
        if not slide["text"]:
            errors.append(f"Empty text on page {slide['page']}")
        for image in slide["images"]:
            picture_count += 1
            image_path = archive_dir / image["path"]
            if not image_path.resolve().is_relative_to(archive_dir.resolve()):
                errors.append(f"Picture path outside local archive: {image['path']}")
                continue
            if not image_path.is_file():
                errors.append(f"Missing picture {image_path}")
            elif hashlib.sha256(image_path.read_bytes()).hexdigest() != image["sha256"]:
                errors.append(f"Picture hash mismatch {image_path}")
    if picture_count != EXPECTED_PICTURES:
        errors.append("Expected two embedded pictures")
    return {
        "ppt_sha256": record["source_sha256"],
        "slides": len(pages),
        "pictures": picture_count,
    }


def check(check_source=False):
    errors = []
    local_archive = None
    if check_source:
        try:
            local_archive = check_local_archive(errors)
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(f"Local archive check failed: {error}")
    slide_map = (ROOT / "slide-map.md").read_text(encoding="utf-8")
    mapped_pages = [int(page) for page in re.findall(r"^\| (\d+) \|", slide_map, flags=re.M)]
    if mapped_pages != list(range(1, EXPECTED_SLIDES + 1)):
        errors.append("Slide map missing, duplicated, or out of order")
    chapter_files = sorted((ROOT / "chapters").glob("*.md"))
    if len(chapter_files) != 7:
        errors.append("Expected seven chapters")
    upgrade_files = sorted(
        path for path in (ROOT / "upgrades").glob("*.md") if path.name != "README.md"
    )
    if {path.name for path in upgrade_files} != EXPECTED_UPGRADES:
        errors.append("Expected six named upgrade tutorials")
    upgrade_index = ROOT / "upgrades/README.md"
    if not upgrade_index.is_file():
        errors.append("Missing upgrade reading index")
    else:
        index_text = upgrade_index.read_text(encoding="utf-8")
        for filename in EXPECTED_UPGRADES:
            if filename not in index_text:
                errors.append(f"Upgrade index missing {filename}")
    sources = (ROOT / "sources.md").read_text(encoding="utf-8")
    source_rows = re.findall(r"^\| ([BEWCSA]\d{2}) \|", sources, flags=re.M)
    known_sources = set(source_rows)
    if len(source_rows) != len(known_sources):
        errors.append("Duplicate source ID")
    core_files = chapter_files + upgrade_files + [ROOT / "corrections.md", ROOT / "glossary.md"]
    for path in core_files:
        content = path.read_text(encoding="utf-8")
        for source_id in set(SOURCE_ID.findall(content)) - known_sources:
            errors.append(f"Unknown source {source_id} in {path.relative_to(ROOT)}")
    markdown_files = sorted(
        path for path in ROOT.rglob("*.md") if ROOT / "source" not in path.parents
    )
    checked_links = 0
    upgrade_source_urls = set()
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        if content.count("```") % 2:
            errors.append(f"Unbalanced code fences: {path.relative_to(ROOT)}")
        for target in LINK.findall(content):
            target = target.strip().strip("<>")
            parts = urlsplit(target)
            if parts.scheme or target.startswith("#"):
                if parts.scheme in {"https", "http"} and path in upgrade_files:
                    upgrade_source_urls.add(target)
                continue
            destination = path.parent / unquote(parts.path)
            checked_links += 1
            if destination.resolve().is_relative_to((ROOT / "source").resolve()):
                errors.append(f"Public note links to private attachment: {path.relative_to(ROOT)} → {target}")
            elif not destination.exists():
                errors.append(f"Broken internal file link: {path.relative_to(ROOT)} → {target}")
    repo = ROOT.parents[2]
    for navigation in (repo / "README.md", repo / "wiki/topics/README.md"):
        if "blockchain/README.md" not in navigation.read_text(encoding="utf-8"):
            errors.append(f"Missing topic navigation: {navigation}")
    result = {
        "slides_indexed": len(mapped_pages),
        "local_source_checked": check_source,
        "local_archive": local_archive,
        "chapters": len(chapter_files),
        "upgrade_tutorials": len(upgrade_files),
        "markdown_files": len(markdown_files),
        "source_records": len(source_rows),
        "upgrade_external_source_urls": len(upgrade_source_urls),
        "internal_file_links_checked": checked_links,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-local-source", action="store_true",
        help="Also verify the ignored local PPT, verbatim extraction, and pictures",
    )
    args = parser.parse_args()
    sys.exit(check(check_source=args.check_local_source))
