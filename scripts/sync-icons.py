"""Generate a small local sprite from the official Lucide static package."""

from copy import deepcopy
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.63.0"
ICONS = [
    "arrow-left", "arrow-right", "arrow-up", "arrow-up-right", "book-open",
    "bookmark", "check", "chevron-right", "copy", "file-text", "flask-conical",
    "external-link", "house", "inbox", "library", "menu", "moon", "search", "sun", "x",
]
SVG = "http://www.w3.org/2000/svg"


def generate():
    ET.register_namespace("", SVG)
    sprite = ET.Element(f"{{{SVG}}}svg")
    sprite.append(ET.Comment(f" Lucide {VERSION}, ISC license; see lucide-LICENSE.txt "))
    for name in ICONS:
        url = f"https://cdn.jsdelivr.net/npm/lucide-static@{VERSION}/icons/{name}.svg"
        with urlopen(url, timeout=30) as response:
            raw = response.read()
        icon = ET.fromstring(raw)
        symbol = ET.SubElement(sprite, f"{{{SVG}}}symbol", {
            "id": name, "viewBox": icon.get("viewBox", "0 0 24 24"),
            "fill": "none", "stroke": "currentColor", "stroke-width": "1.8",
            "stroke-linecap": "round", "stroke-linejoin": "round",
        })
        for child in icon:
            symbol.append(deepcopy(child))
        if name == "book-open":
            (ROOT / "assets/book-open.svg").write_bytes(raw)
    ET.ElementTree(sprite).write(
        ROOT / "assets/icons.svg", encoding="utf-8", xml_declaration=True)
    with urlopen(
            f"https://cdn.jsdelivr.net/npm/lucide-static@{VERSION}/LICENSE",
            timeout=30) as response:
        (ROOT / "assets/lucide-LICENSE.txt").write_bytes(response.read())
    print(f"Generated {len(ICONS)} Lucide icons")


if __name__ == "__main__":
    generate()
