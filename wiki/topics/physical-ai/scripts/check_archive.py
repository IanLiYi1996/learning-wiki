"""Check this archive offline. Reads only; no dependencies or hardware."""

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {"node_modules", "__pycache__"}
TEXT_SUFFIXES = {".md", ".json", ".html", ".csv"}
LOCAL_PATH = re.compile(r"file://|(?<![\w/])/(?:home|Users)/[^/\s]+/")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", re.M)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", re.S)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def archive_path(root, relative):
    """Reject absolute paths and traversal, including symlink escapes."""
    root = root.resolve()
    target = (root / relative).resolve()
    require(not Path(relative).is_absolute() and target.is_relative_to(root),
            f"Path outside archive: {relative}")
    return target


def closing_bracket(text, start, opening, closing):
    depth = 0
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == opening:
            depth += 1
        elif character == closing:
            depth -= 1
            if depth == 0:
                return index
    return None


def inline_targets(text):
    targets = []
    position = 0
    while position < len(text):
        start = text.find("[", position)
        if start < 0:
            break
        end = closing_bracket(text, start, "[", "]")
        if end is None:
            break
        position = end + 1
        if text[position:position + 1] != "(":
            continue
        close = closing_bracket(text, position, "(", ")")
        if close is None:
            continue
        destination = text[position + 1:close].strip()
        if destination.startswith("<"):
            angle_end = destination.find(">")
            if angle_end >= 0:
                targets.append(destination[1:angle_end])
        elif destination:
            targets.append(destination.split()[0])
        position = close + 1
    return targets


def markdown_targets(text):
    """Check the archive's link forms, not the full CommonMark grammar or anchors."""
    prose = []
    fence = None
    for line in text.splitlines():
        marker = FENCE.match(line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) \
                    and not marker.group(2).strip():
                fence = None
            continue
        if fence is None and not line.startswith(("    ", "\t")):
            prose.append(line)
    text = INLINE_CODE.sub("", "\n".join(prose))
    return inline_targets(text) + [
        match.group(1).strip("<>") for match in REFERENCE_LINK.finditer(text)]


def missing_local_links(path, text):
    missing = []
    for target in markdown_targets(text):
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        require(not Path(unquote(parts.path)).is_absolute(),
                f"Absolute local link in {path.name}: {target}")
        if not (path.parent / unquote(parts.path)).exists():
            missing.append(target)
    return missing


def verify_hashes(root, records):
    require(len({row["path"] for row in records}) == len(records),
            "Duplicate manifest paths")
    for row in records:
        path = archive_path(root, row["path"])
        require(path.is_file(), f"Missing deliverable: {row['path']}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == row["sha256"], f"SHA-256 mismatch: {row['path']}")


def verify_supporting_files(root, paths):
    require(len(set(paths)) == len(paths), "Duplicate supporting paths")
    for relative in paths:
        require(archive_path(root, relative).is_file(),
                f"Missing supporting file: {relative}")


def compare_catalogue(products, rows):
    require(len(products) == len(rows), "CSV/JSON product count differs")
    require(len({item["id"] for item in products}) == len(products),
            "Duplicate product IDs")
    for product, row in zip(products, rows):
        require(set(product) == set(row), f"CSV fields differ: {product['id']}")
        for field, expected in product.items():
            actual = json.loads(row[field]) if isinstance(expected, (list, dict)) \
                else row[field]
            require(actual == expected,
                    f"CSV/JSON mismatch: {product['id']}:{field}")


def check_archive(root=ROOT):
    files = sorted(path for path in root.rglob("*") if path.is_file()
                   and not set(path.relative_to(root).parts) & IGNORED_DIRECTORIES)
    json_files = [path for path in files if path.suffix == ".json"]
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8-sig"))
    local_links = 0
    for path in files:
        if path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8-sig")
        require(not LOCAL_PATH.search(text),
                f"Host-specific path: {path.relative_to(root)}")
        if path.suffix == ".md":
            missing = missing_local_links(path, text)
            require(not missing,
                    f"Broken local links in {path.relative_to(root)}: {missing}")
            local_links += sum(not urlsplit(target).scheme
                               and not urlsplit(target).netloc
                               and bool(urlsplit(target).path)
                               for target in markdown_targets(text))
    manifest = json.loads((root / "archive-manifest.json").read_text(encoding="utf-8"))
    verify_supporting_files(root, manifest["required_supporting_files"])
    verify_hashes(root, manifest["deliverables"])
    products = json.loads((root / "industry/products.json").read_text(encoding="utf-8"))
    with (root / "industry/products.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    compare_catalogue(products, rows)
    counts = {
        "deliverables": len(manifest["deliverables"]),
        "supporting_files": len(manifest["required_supporting_files"]),
        "products": len(products),
        "industry_chapters": len(list((root / "industry/chapters").glob("*.md"))),
        "principle_chapters": len(list((root / "advanced/chapters").glob("*.md"))),
        "principle_papers": len(json.loads(
            (root / "advanced/papers.json").read_text(encoding="utf-8"))),
    }
    for key, expected in manifest["expected"].items():
        require(counts[key] == expected, f"Count mismatch: {key}")
    return {"status": "passed", **counts, "json_files": len(json_files),
            "markdown_local_links": local_links,
            "scope": "Offline archive integrity, not product or model validation."}


def main():
    try:
        print(json.dumps(check_archive(), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Archive check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
