"""Build and verify a sourced Chinese research document."""

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEM = "Physical_AI_知识全景与学习指南"
TITLE = "Physical AI：知识全景与学习指南"
FONT = "Noto Sans CJK SC"
ACCENT = "245478"
QA = ROOT / "qa"


def read_source():
    text = (ROOT / f"{STEM}.md").read_text(encoding="utf-8")
    references = dict(re.findall(r"^\[(\d+)\]:\s+(\S+)", text, re.M))
    body = re.sub(r"^\[\d+\]:.*$", "", text, flags=re.M)
    missing = set(re.findall(r"\[(\d+)\]", body)) - references.keys()
    if missing:
        raise ValueError(f"Undefined citations: {missing}")
    if "[TOC]" not in text:
        raise ValueError("Missing contents marker")
    return text, references


def save_json(name, value):
    (QA / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def bibliography():
    fields = set()
    papers = []
    for name in ("models-papers.json", "evaluation-papers.json", "rl-papers.json"):
        records = json.loads((ROOT / "notes" / name).read_text(encoding="utf-8"))
        for paper in records:
            fields.update(paper.keys())
            if not all(paper.get(key) for key in ("title", "authors", "arxiv_id")):
                raise ValueError(f"Incomplete paper identity: {paper}")
            papers.append(paper)
    seen = set()
    combined = []
    for paper in papers:
        key = paper["arxiv_id"].split("v")[0]
        if key in seen:
            continue
        seen.add(key)
        combined.append({field: paper.get(field) for field in sorted(fields)})
    (ROOT / "papers.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    save_json("bibliography-check.json", {
        "papers": len(combined), "unique_arxiv_ids": len(seen),
        "unknown_values": "null; original metadata and version notes retained",
    })


def pdf():
    import markdown
    import pymupdf
    from weasyprint import CSS, HTML
    from weasyprint.text.fonts import FontConfiguration

    source, references = read_source()
    content = source.split("[TOC]", 1)[1]
    content = re.sub(r"^\[\d+\]:.*$", "", content, flags=re.M)
    content = re.sub(
        r"\[(\d+)\]", lambda m: f"[{m[1]}]({references[m[1]]})", content
    )
    editor = markdown.Markdown(
        extensions=["tables", "toc", "sane_lists", "fenced_code"],
        extension_configs={"toc": {"toc_depth": "2"}},
    )
    rendered = editor.convert("[TOC]\n\n" + content)
    citation_count = 0
    for match in re.finditer(r'<a href="([^"]+)">(\d+)</a>', rendered):
        if match[1] != references[match[2]]:
            raise ValueError(f"Misbound citation: {match[2]}")
        citation_count += 1
    if not citation_count:
        raise ValueError("No numbered citations were checked")
    toc = re.match(r'<div class="toc">.*?</div>\s*', rendered, re.S)
    if not toc:
        raise ValueError("Contents not rendered")
    body = rendered[toc.end():]
    chapters = []
    for part in re.split(r"(?=<h2\b)", body):
        if not part.strip():
            continue
        heading = re.search(r"<h2\b[^>]*>(.*?)</h2>", part, re.S)
        title = heading[1] if heading else ""
        css = "chapter sources" if title.startswith("附录 C") else "chapter"
        if title.startswith("附录 A"):
            css += " glossary"
        if title.startswith(("一、", "附录 C")):
            css += " start-section"
        if not title.startswith("附录 C"):
            part = re.sub(
                r'(<a\b[^>]*>)(\d+)(</a>)',
                lambda m: '<sup class="citation">' + m[1] +
                "[" + m[2] + "]" + m[3] + "</sup>", part
            )
        chapters.append(f'<section class="{css}">{part}</section>')
    cover = """
    <section class="cover">
      <p class="eyebrow">从概念到系统 · Physical AI 学习资料</p>
      <h1>Physical AI<br>知识全景与学习指南</h1>
      <p class="subtitle">看懂数据、模型、仿真与机器人<br>怎样一起完成现实任务</p>
      <div class="cover-rule"></div>
      <p class="cover-message">用“拿起杯子”串起整套系统，<br>理解每一层的输入、输出和反馈。</p>
      <p class="cover-topics">机器人基础 · 感知与控制 · VLA 与世界模型<br>
      数据与训练 · 仿真与部署 · 评测与学习练习</p>
      <p class="cover-date">资料核实：2026 年 10 月 27 日<br>
      版本 1.0 · 以机制和原始资料为主</p>
      <p class="cover-note">覆盖整个领域的主要知识模块，不限于 NVIDIA 或 GTC。<br>
      配有阅读顺序、自测答案和不连接硬件的反馈实验。</p>
    </section>
    """
    document = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        f"<title>{TITLE}</title>"
        '<link rel="stylesheet" href="print.css"></head><body>' + cover +
        '<section class="contents-page"><h2 class="contents-title">阅读目录</h2>'
        '<p class="reading-note">先读第 1—2 章，建立概念和系统地图。<br>'
        '再按第 14 章的顺序学习；第 15 章提供练习和自测答案。<br>'
        '术语速查和一手来源在附录。</p>' +
        toc[0] + "</section>" + "".join(chapters) + "</body></html>"
    )
    (ROOT / f"{STEM}.html").write_text(document, encoding="utf-8")
    fonts = FontConfiguration()
    HTML(string=document, base_url=str(ROOT)).write_pdf(
        ROOT / f"{STEM}.pdf",
        stylesheets=[CSS(filename=str(ROOT / "print.css"), font_config=fonts)],
        font_config=fonts, pdf_tags=True,
    )
    output = pymupdf.open(ROOT / f"{STEM}.pdf")
    pages = []
    for index, page in enumerate(output, 1):
        blocks = [
            b for b in page.get_text("blocks")
            if b[4].strip() and b[1] > 55 and b[3] < page.rect.height - 55
        ]
        pages.append({
            "page": index, "characters": len(page.get_text()),
            "content_bottom": round(max((b[3] for b in blocks), default=0), 1),
            "empty": not blocks,
        })
    if any(p["empty"] for p in pages):
        raise ValueError("Empty PDF page")
    report = {
        "pdf_pages": len(output), "source_entries": len(references),
        "unique_source_urls": len(set(references.values())),
        "chinese_characters": len(re.findall(r"[\u4e00-\u9fff]", source)),
        "bookmarks": len(output.get_toc()),
        "pdf_links": sum(len(p.get_links()) for p in output),
        "citations_checked": citation_count,
        "misbound_citations": 0, "pages": pages,
    }
    save_json("pdf-check.json", report)
    montage = pymupdf.open()
    width, height, columns = 260, 380, 4
    sheet = montage.new_page(
        width=width * columns,
        height=height * ((len(output) + columns - 1) // columns),
    )
    for index in range(len(output)):
        col, row = index % columns, index // columns
        sheet.show_pdf_page(
            pymupdf.Rect(col * width + 6, row * height + 18,
                         (col + 1) * width - 6, (row + 1) * height - 6),
            output, index,
        )
        sheet.insert_text((col * width + 8, row * height + 12),
                          f"Page {index + 1}", fontsize=9)
    sheet.get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save(QA / "contact-sheet.png")
    for number in {1, 2, 4, len(output)}:
        output[number - 1].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(
            QA / f"page-{number}.png"
        )
    print(json.dumps({k: v for k, v in report.items() if k != "pages"},
                     ensure_ascii=False))


def office(*args):
    result = subprocess.run(["officecli", *map(str, args)],
                            check=True, capture_output=True, text=True)
    return result.stdout


def docx():
    source, references = read_source()
    content = re.sub(r"^\[\d+\]:.*$", "", source, flags=re.M)
    content = re.sub(
        r"\[(\d+)\]", lambda m: f"[{m[1]}]({references[m[1]]})", content
    )
    file = ROOT / f"{STEM}.docx"
    if file.exists():
        office("close", file)
    subprocess.run([
        "pandoc", "--from", "markdown", "--to", "docx",
        "--standalone", "--lua-filter", str(ROOT / "docx_filter.lua"),
        "--metadata", "lang=zh-CN", "--output", str(file),
    ], input=content, text=True, check=True)
    office("open", file)
    office("add", file, "/styles", "--type", "style", "--prop", "id=TableNormal",
           "--prop", "type=table", "--prop", "name=Normal Table")
    office("get", file, "/styles/TableNormal")
    operations = []

    def set_op(path, **props):
        operations.append({"command": "set", "path": path, "props": props})

    set_op("/", **{
        "title": TITLE, "author": "研究整理", "pageWidth": "21cm",
        "pageHeight": "29.7cm", "marginTop": "2.3cm", "marginBottom": "2.3cm",
        "marginLeft": "2.54cm", "marginRight": "2.54cm",
        "docDefaults.font": FONT, "docDefaults.font.eastAsia": FONT,
        "docDefaults.fontSize": "11pt", "updateFields": "true",
    })
    for style, size in (("Normal", "11pt"), ("BodyText", "11pt"),
                        ("Title", "32pt"), ("Heading1", "20pt"),
                        ("Heading2", "14pt")):
        props = {"font": FONT, "font.ea": FONT, "size": size,
                 "lineSpacing": "1.3x", "spaceAfter": "7pt"}
        if style in {"Title", "Heading1", "Heading2"}:
            props.update({"bold": "true", "color": ACCENT, "keepNext": "true",
                          "spaceBefore": "14pt", "spaceAfter": "10pt"})
        if style == "Title":
            props.update({"align": "left", "spaceBefore": "40pt",
                          "spaceAfter": "18pt"})
        set_op(f"/styles/{style}", **props)
    set_op("/body/p[2]", size="16pt", color="344054", spaceAfter="16pt")
    tree = office("get", file, "/body", "--depth", "4")
    for line in tree.splitlines():
        table = re.match(r"(/body/tbl\[\d+\]) \(table\)", line)
        row = re.match(r"(/body/tbl\[\d+\]/tr\[(\d+)\]) \(row\)", line)
        cell = re.match(r"(/body/tbl\[\d+\]/tr\[(\d+)\]/tc\[\d+\]) \(cell\)", line)
        if table:
            set_op(table[1], width="100%", layout="autofit", padding="90")
        if row:
            props = {"cantSplit": "true"}
            if row[2] == "1":
                props["header"] = "true"
            set_op(row[1], **props)
        if cell:
            props = {"font": FONT, "size": "9.5pt", "valign": "top"}
            if cell[2] == "1":
                props.update({"fill": "EDF3F8", "bold": "true"})
            set_op(cell[1], **props)
    first_heading = json.loads(office(
        "query", file, "paragraph[style=Heading1]", "--json"
    ))["data"]["results"][0]["path"]
    set_op(first_heading, pageBreakBefore="true")
    office("batch", file, "--commands", json.dumps(operations, ensure_ascii=False),
           "--json")
    office("get", file, "/styles/Heading1")
    office("add", file, "/body", "--type", "toc", "--prop", "levels=1-1",
           "--prop", "title=阅读目录", "--prop", "hyperlinks=true",
           "--before", first_heading)
    office("get", file, "/toc", "--depth", "2")
    office("set", file, "/styles/TOCHeading", "--prop", f"color={ACCENT}",
           "--prop", "pageBreakBefore=true", "--prop", "keepNext=true")
    office("add", file, "/", "--type", "header",
           "--prop", "text=Physical AI · 知识全景与学习指南",
           "--prop", "size=8pt", "--prop", "color=667085")
    office("add", file, "/", "--type", "footer", "--prop", "text=第 ",
           "--prop", "align=center", "--prop", "size=9pt")
    office("add", file, "/footer[1]/p[1]", "--type", "field",
           "--prop", "fieldType=page")
    office("add", file, "/footer[1]/p[1]", "--type", "run", "--prop", "text= / ")
    office("add", file, "/footer[1]/p[1]", "--type", "field",
           "--prop", "fieldType=numpages")
    office("get", file, "/footer[1]", "--depth", "3")
    office("save", file)
    for mode in ("outline", "stats", "issues", "text", "html"):
        suffix = "html" if mode == "html" else "txt"
        (QA / f"docx-{mode}.{suffix}").write_text(
            office("view", file, mode), encoding="utf-8"
        )
    office("close", file)
    validation = office("validate", file)
    (QA / "docx-validation.txt").write_text(validation, encoding="utf-8")
    if "no errors found" not in validation.lower():
        raise ValueError(validation)
    plain = (QA / "docx-text.txt").read_text(encoding="utf-8")
    if re.search(r"\[TOC\]|<TODO>|\{\{[^}]+\}\}|\\[tn]", plain):
        raise ValueError("Leaked placeholder or escape")
    page_fields = json.loads(office(
        "query", file, "field[fieldType=page]", "--json"
    ))["data"]["results"]
    if not page_fields:
        raise ValueError("Missing live PAGE field")
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    with zipfile.ZipFile(file) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        relationships = ET.fromstring(package.read("word/_rels/document.xml.rels"))
    targets = {r.attrib["Id"]: r.attrib["Target"] for r in relationships}
    count = 0
    for link in document.findall(".//w:hyperlink", ns):
        label = "".join(n.text or "" for n in link.findall(".//w:t", ns))
        match = re.fullmatch(r"\[(\d+)\]", label)
        if match:
            target = targets.get(link.attrib.get("{" + ns["r"] + "}id"))
            if target != references[match[1]]:
                raise ValueError(f"Misbound Word citation: {label} -> {target}")
            count += 1
    result = {"schema": "passed", "citations_checked": count,
              "misbound_citations": 0, "live_page_fields": len(page_fields),
              "dynamic_toc": "recalculate on open in Word"}
    save_json("docx-check.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("pdf", "docx", "all"), default="all")
    args = parser.parse_args()
    QA.mkdir(exist_ok=True)
    bibliography()
    if args.format in ("pdf", "all"):
        pdf()
    if args.format in ("docx", "all"):
        docx()
