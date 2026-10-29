"""Rebuild the wiki's curated, local illustrations; no network or AI API calls.

SVG is editable source; PNG is the portable Markdown/export fallback.
Content and placement are authored in figures/*.json, not inferred from headings.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
FONT = "Noto Sans CJK SC"
PALETTE = [
    ("#eff6ff", "#2563eb"), ("#f0fdf4", "#15803d"),
    ("#faf5ff", "#7c3aed"), ("#fff7ed", "#c2410c"),
]
SVG_NS = "http://www.w3.org/2000/svg"


def text_width(value, size):
    return sum(size if unicodedata.east_asian_width(c) in "WF"
               else size * 0.58 for c in value)


def wrap(value, width, size=18):
    result = []
    for line in str(value).split("\n"):
        current = ""
        # Preserve short Latin identifiers/words rather than splitting "pixel"
        # into "p" and "ixel"; Chinese still wraps at character boundaries.
        for token in re.findall(r"[A-Za-z0-9_]+|.", line):
            if text_width(token, size) > width:
                pieces = list(token)
            else:
                pieces = [token]
            for piece in pieces:
                if current and text_width(current + piece, size) > width:
                    result.append(current.rstrip())
                    current = ""
                current += piece if current else piece.lstrip()
        result.append(current.rstrip())
    return result


class Canvas:
    """Append complete XML elements to a list, then validate the resulting SVG."""

    def __init__(self, title, subtitle, height=540):
        self.height = height
        self.lines = [
            f'<svg xmlns="{SVG_NS}" width="1040" height="{height}" '
            f'viewBox="0 0 1040 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(subtitle)}</desc>',
            "<defs>",
        ]
        for name, color in (("main", "#2563eb"), ("feedback", "#7c3aed")):
            self.lines.append(
                f'<marker id="{name}" markerWidth="10" markerHeight="7" '
                f'refX="9" refY="3.5" orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0 0 L10 3.5 L0 7 Z" fill="{color}"/></marker>'
            )
        self.lines.extend([
            "</defs>",
            f'<g font-family="{FONT}, PingFang SC, Microsoft YaHei, sans-serif">',
            f'<rect width="1040" height="{height}" rx="12" fill="#ffffff"/>',
        ])
        self.text(40, 47, title, 25, weight=700)
        for i, line in enumerate(wrap(subtitle, 960, 16)):
            self.text(40, 78 + i * 23, line, 16, "#63736a")

    def text(self, x, y, value, size=18, color="#23312b", weight=400, anchor="start"):
        self.lines.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'
        )

    def box(self, x, y, w, h, label, detail="", color=0):
        fill, stroke = PALETTE[color % len(PALETTE)]
        self.lines.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{fill}" stroke="{stroke}" stroke-opacity=".4" stroke-width="1.5"/>'
        )
        labels = wrap(label, w - 28, 20)
        details = wrap(detail, w - 28, 16) if detail else []
        needed = len(labels) * 27 + len(details) * 23 + (8 if details else 0)
        if needed > h - 16:
            raise ValueError(f"Text does not fit: {label!r}: {needed} > {h-16}")
        baseline = y + (h - needed) / 2 + 22
        for i, line in enumerate(labels):
            self.text(x + w / 2, baseline + i * 27, line, 20, weight=600, anchor="middle")
        for i, line in enumerate(details):
            self.text(x + w / 2, baseline + len(labels) * 27 + 8 + i * 23,
                      line, 16, "#52645a", anchor="middle")

    def arrow(self, points, label="", feedback=False, label_segment=None):
        color, marker = ("#7c3aed", "feedback") if feedback else ("#2563eb", "main")
        path = "M " + " L ".join(f"{x},{y}" for x, y in points)
        self.lines.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.2" '
            f'marker-end="url(#{marker})" stroke-linejoin="round"/>'
        )
        if label:
            # The longest segment has a clear corridor; label background masks its line.
            segments = list(zip(points, points[1:]))
            a, b = (segments[label_segment] if label_segment is not None else
                    max(segments, key=lambda p: abs(p[0][0]-p[1][0])+abs(p[0][1]-p[1][1])))
            x, y = (a[0]+b[0])/2, (a[1]+b[1])/2
            w = text_width(label, 15) + 16
            self.lines.append(
                f'<rect x="{x-w/2}" y="{y-13}" width="{w}" height="25" fill="#fff"/>'
            )
            self.text(x, y + 5, label, 15, color, anchor="middle")

    def footer(self, note, feedback=False):
        y = self.height - 44
        self.lines.append(f'<line x1="40" y1="{y-20}" x2="1000" y2="{y-20}" stroke="#e0e7e2"/>')
        if feedback:
            self.text(40, y + 3, "蓝色：前向信息　紫色：反馈／再执行", 14, "#63736a")
            self.text(40, y + 25, note, 14, "#63736a")
        else:
            for i, line in enumerate(wrap(note, 960, 15)):
                self.text(40, y + 4 + i * 21, line, 15, "#63736a")

    def finish(self):
        self.lines.extend(["</g>", "</svg>", ""])
        svg = "\n".join(self.lines)
        ET.fromstring(svg)
        return svg


def render_flow(figure):
    nodes = figure["nodes"]
    rows = math.ceil(len(nodes) / 3)
    height = 180 + rows * 180 + (50 if figure.get("loop") else 0)
    c = Canvas(figure["title"], figure["subtitle"], height)
    positions = []
    for i, node in enumerate(nodes):
        row, col = divmod(i, 3)
        # Serpentine routing keeps every connector out of component interiors.
        if row % 2:
            col = 2 - col
        x, y = 56 + col * 336, 128 + row * 180
        positions.append((x, y))
        c.box(x, y, 256, 120, node[0], node[1] if len(node) > 1 else "", i)
    for i, ((x, y), (nx, ny)) in enumerate(zip(positions, positions[1:])):
        if y == ny:
            if nx > x:
                points = [(x+256, y+60), (nx, ny+60)]
            else:
                points = [(x, y+60), (nx+256, ny+60)]
        else:
            points = [(x+128, y+120), (nx+128, ny)]
        c.arrow(points)
    if figure.get("loop"):
        x, y = positions[-1]
        # Use external left rail for a loop; no crossing with forward edges.
        rail_y = y + 147
        c.arrow([(x+128, y+120), (x+128, rail_y), (24, rail_y),
                 (24, 188), (56, 188)], figure["loop"], True, label_segment=1)
    c.footer(figure.get("note", "按正文机制绘制；示意图不代表实际部署或测量。"),
             bool(figure.get("loop")))
    return c.finish()


def render_compare(figure):
    rows = figure["rows"]
    columns = figure["columns"]
    if not 2 <= len(columns) <= 4:
        raise ValueError("Comparison requires 2–4 columns")
    widths = [180] + [780 / (len(columns)-1)] * (len(columns)-1)
    row_heights = [
        max(68, 28 + max(len(wrap(str(cell), w-26, 17)) for cell, w
                        in zip(row, widths)) * 25)
        for row in rows
    ]
    c = Canvas(figure["title"], figure["subtitle"], 222 + sum(row_heights))
    y = 126
    for index, row in enumerate([columns] + rows):
        h = 54 if index == 0 else row_heights[index-1]
        x = 40
        for j, (cell, w) in enumerate(zip(row, widths)):
            fill = "#e5f1eb" if index == 0 else ("#f7f9f8" if index % 2 else "#fff")
            c.lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
                           'stroke="#e0e7e2"/>')
            for line_index, line in enumerate(wrap(cell, w-26, 17)):
                c.text(x+13, y+29+line_index*25, line, 17,
                       weight=600 if index == 0 or j == 0 else 400)
            x += w
        y += h
    c.footer(figure.get("note", "对照的是职责与条件，不是性能排名。"))
    return c.finish()


def render_layers(figure):
    rows = figure["layers"]
    c = Canvas(figure["title"], figure["subtitle"], 198 + len(rows)*116)
    for i, row in enumerate(rows):
        y = 125 + i * 116
        fill, stroke = PALETTE[i % 4]
        c.lines.append(f'<rect x="56" y="{y}" width="928" height="84" rx="8" '
                       f'fill="{fill}" stroke="{stroke}" stroke-opacity=".3"/>')
        c.text(76, y+36, row[0], 20, weight=600)
        for j, line in enumerate(wrap(row[1], 680, 17)):
            c.text(292, y+32+j*25, line, 17, "#52645a")
        if figure.get("connect") and i < len(rows)-1:
            c.arrow([(520, y+84), (520, y+116)])
    c.footer(figure.get("note", "分层表示责任边界，不要求每层独立部署。"))
    return c.finish()


def render_geometry(figure):
    c = Canvas(figure["title"], figure["subtitle"], 560)
    # Two exact solutions for l1=l2=1, target=(1,1), in an orthographic diagram.
    ox, oy, scale = 200, 400, 210
    c.arrow([(ox-25, oy), (ox+320, oy)])
    c.arrow([(ox, oy+25), (ox, oy-290)])
    c.text(ox+327, oy+5, "x", 18)
    c.text(ox-4, oy-300, "y", 18)
    for mid, color in (((ox+scale, oy), "#2563eb"), ((ox, oy-scale), "#7c3aed")):
        ex, ey = ox+scale, oy-scale
        c.lines.append(f'<path d="M{ox},{oy} L{mid[0]},{mid[1]} L{ex},{ey}" '
                       f'fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round"/>')
        c.lines.append(f'<circle cx="{mid[0]}" cy="{mid[1]}" r="9" fill="#fff" stroke="{color}" stroke-width="3"/>')
    c.lines.append(f'<circle cx="{ox+scale}" cy="{oy-scale}" r="9" fill="#15803d"/>')
    c.text(ox+scale+18, oy-scale-14, "目标 (1, 1)", 20, "#15803d")
    c.box(580, 145, 380, 116, "解 A：q = (0, π/2)", "先向右，再向上；l₁ = l₂ = 1", 0)
    c.box(580, 297, 380, 116, "解 B：q = (π/2, −π/2)", "先向上，再向右；相同末端位置", 2)
    c.footer("原创数值例：仅说明 FK／IK 多解；未加入限位、碰撞或真实设备。")
    return c.finish()


def render_intervals(figure):
    c = Canvas(figure["title"], figure["subtitle"], 465)
    x0, x1 = 220, 952
    y0, y1 = 167, 283
    for y, label, low, high in ((y0, "9 / 10", .596, .982),
                                (y1, "90 / 100", .826, .945)):
        c.text(56, y+6, label, 23, weight=600)
        c.lines.append(f'<line x1="{x0+low*(x1-x0)}" y1="{y}" '
                       f'x2="{x0+high*(x1-x0)}" y2="{y}" stroke="#2563eb" stroke-width="6"/>')
        for value in (low, high):
            x = x0+value*(x1-x0)
            c.lines.append(f'<line x1="{x}" y1="{y-14}" x2="{x}" y2="{y+14}" stroke="#2563eb" stroke-width="3"/>')
            c.text(x, y+42, f"{value*100:.1f}%", 17, anchor="middle")
        c.lines.append(f'<circle cx="{x0+.9*(x1-x0)}" cy="{y}" r="8" fill="#15803d"/>')
    c.lines.append(f'<line x1="{x0}" y1="360" x2="{x1}" y2="360" stroke="#63736a"/>')
    for value in (0, .25, .5, .75, 1):
        c.text(x0+value*(x1-x0), 386, f"{value*100:g}%", 16, anchor="middle")
    c.footer("绿色点：经验比例 90%；蓝线：正文 95% Wilson 区间，需独立同分布二项假设。")
    return c.finish()


RENDERERS = {"flow": render_flow, "compare": render_compare, "layers": render_layers,
             "geometry": render_geometry, "intervals": render_intervals}


def load_figures():
    figures = []
    for path in sorted((ROOT / "scripts/figures").glob("*.json")):
        figures.extend(json.loads(path.read_text(encoding="utf-8")))
    for figure in figures:
        expanded = []
        for placement in figure.get("placements", []):
            expanded.append({"file": placement["file"], "after": placement["after"]})
            for mirror in placement.get("mirrors", []):
                expanded.append({"file": mirror, "after": placement["after"]})
        figure["placements"] = expanded
    ids = [f["id"] for f in figures]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate illustration IDs")
    return figures


def figure_path(figure, suffix="png"):
    return ROOT / "wiki/topics" / figure["topic"] / "images" / f'{figure["id"]}.{suffix}'


def placement_id(figure, placement):
    # The same diagram can appear at two different headings in a long note.
    suffix = hashlib.sha256(placement["after"].encode("utf-8")).hexdigest()[:10]
    return f'{figure["id"]}-{suffix}'


def embed(figure):
    """Mechanical insertion of explicitly curated placements, idempotently."""
    for placement in figure.get("placements", []):
        file = ROOT / placement["file"]
        text = file.read_text(encoding="utf-8")
        identity = placement_id(figure, placement)
        marker = f'<!-- illustration: {identity} -->'
        old_marker = f'<!-- illustration: {figure["id"]} -->'
        src = os.path.relpath(figure_path(figure), file.parent).replace(os.sep, "/")
        block = (
            f'\n{marker}\n'
            f'![{figure["title"]}。{figure["subtitle"]}]({src})\n\n'
            f'*图：{figure["title"]}。{figure.get("caption", figure["subtitle"])}*\n'
            f'<!-- /illustration: {identity} -->\n'
        )
        if marker in text or old_marker in text:
            existing = identity if marker in text else figure["id"]
            pattern = re.compile(re.escape(f'<!-- illustration: {existing} -->') + r".*?"
                                 + re.escape(f'<!-- /illustration: {existing} -->'), re.S)
            text = pattern.sub(lambda _: block.strip("\n"), text)
        else:
            heading = placement["after"]
            if text.splitlines().count(heading) != 1:
                raise ValueError(f"Placement must be a unique whole heading: {file}: {heading}")
            text = text.replace(heading + "\n", heading + "\n" + block, 1)
        file.write_text(text, encoding="utf-8")


def validate(figures):
    errors = []
    references = 0
    for figure in figures:
        for suffix in ("svg", "png"):
            path = figure_path(figure, suffix)
            if not path.is_file():
                errors.append(f"Missing: {path.relative_to(ROOT)}")
        if figure_path(figure, "svg").exists():
            svg = ET.parse(figure_path(figure, "svg")).getroot()
            if svg.find(f"{{{SVG_NS}}}title") is None or svg.find(f"{{{SVG_NS}}}desc") is None:
                errors.append(f"Missing SVG accessibility metadata: {figure['id']}")
        for placement in figure.get("placements", []):
            path = ROOT / placement["file"]
            text = path.read_text(encoding="utf-8")
            marker = f'<!-- illustration: {placement_id(figure, placement)} -->'
            if text.count(marker) != 1:
                errors.append(f"Missing/duplicate placement: {figure['id']}: {path}")
            src = os.path.relpath(figure_path(figure), path.parent).replace(os.sep, "/")
            if f"]({src})" not in text:
                errors.append(f"Wrong image path: {figure['id']}: {path}")
            references += 1
    if errors:
        raise ValueError("\n".join(errors))
    return {"figures": len(figures), "placements": references,
            "notes": len({p["file"] for f in figures for p in f.get("placements", [])})}


def asset_manifest(figures):
    root = ROOT / "wiki/topics/physical-ai"
    assets = []
    for figure in figures:
        if figure["topic"] != "physical-ai":
            continue
        for suffix in ("svg", "png"):
            path = figure_path(figure, suffix)
            assets.append({"path": path.relative_to(root).as_posix(),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    data = {"date": "2026-10-29", "scope": "Original local teaching illustrations.",
            "assets": assets}
    (root / "illustrations-manifest.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def contact_sheet(figures, output):
    from PIL import Image, ImageDraw, ImageFont
    columns, cell_w, cell_h = 4, 520, 460
    sheet = Image.new("RGB", (columns*cell_w, math.ceil(len(figures)/columns)*cell_h), "#eef2ef")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc", 16)
    for i, figure in enumerate(figures):
        x, y = (i % columns)*cell_w, (i // columns)*cell_h
        with Image.open(figure_path(figure)) as image:
            thumbnail = image.convert("RGB")
            thumbnail.thumbnail((cell_w-20, cell_h-56))
            sheet.paste(thumbnail, (x+(cell_w-thumbnail.width)//2, y+40))
        draw.text((x+10, y+10), f'{i+1:02}. {figure["id"]}', fill="#23312b", font=font)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embed", action="store_true", help="Insert/update curated figures in notes")
    parser.add_argument("--check", action="store_true", help="Validate assets and placements without writing")
    parser.add_argument("--contact-sheet", type=Path, help="Save a visual review PNG to this path")
    args = parser.parse_args()
    figures = load_figures()
    if not args.check:
        import cairosvg
        # Fail before writing any note if an authored heading no longer exists.
        for figure in figures:
            RENDERERS[figure["kind"]](figure)
            for placement in figure.get("placements", []):
                text = (ROOT / placement["file"]).read_text(encoding="utf-8")
                if text.splitlines().count(placement["after"]) != 1:
                    raise ValueError(f"Ambiguous/missing heading: {placement}")
        for figure in figures:
            svg = RENDERERS[figure["kind"]](figure)
            path = figure_path(figure, "svg")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(svg, encoding="utf-8")
            cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                            write_to=str(path.with_suffix(".png")), scale=2)
            if args.embed:
                embed(figure)
        asset_manifest(figures)
    if args.contact_sheet:
        contact_sheet(figures, args.contact_sheet)
    print(json.dumps(validate(figures), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
