"""Build and verify a sourced Chinese research document."""

import argparse
import base64
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEM = "Physical_AI_底层原理与实现细节"
TITLE = "Physical AI：底层原理与实现细节"
FONT = "Noto Sans CJK SC"
ACCENT = "245478"
QA = ROOT / "qa"
PROTECTED = re.compile(
    r"```[\s\S]*?```|`[^`\n]*`|\$\$[\s\S]*?\$\$|\$(?:\\.|[^$\\\n])+\$"
)
WEB_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)")


def read_source():
    text = (ROOT / f"{STEM}.md").read_text(encoding="utf-8")
    references = dict(re.findall(r"^\[(S\d+)\]:\s+(\S+)", text, re.M))
    body = re.sub(r"^\[S\d+\]:.*$", "", text, flags=re.M)
    missing = set(re.findall(r"\[(S\d+)\]", body)) - references.keys()
    if missing:
        raise ValueError(f"Undefined citations: {missing}")
    if "[TOC]" not in text:
        raise ValueError("Missing contents marker")
    return text, references


def save_json(name, value):
    (QA / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def rewrite_prose_links(text, callback):
    """Do not let a bracket in TeX or code consume a following source link."""
    pieces = []
    previous = 0
    for match in PROTECTED.finditer(text):
        pieces.append(WEB_LINK.sub(callback, text[previous:match.start()]))
        pieces.append(match.group())
        previous = match.end()
    pieces.append(WEB_LINK.sub(callback, text[previous:]))
    return "".join(pieces)


def assemble():
    files = sorted((ROOT / "chapters").glob("[0-9][0-9]_*.md"))
    prefixes = {file.name[:2] for file in files}
    expected = {f"{n:02}" for n in range(1, 15)}
    if prefixes != expected:
        raise ValueError(f"Missing/extra chapters: {expected ^ prefixes}")
    source_map = {}
    records = []

    def citation(match):
        label, url = match.group(1), match.group(2)
        if len(label) > 180 or "$" in label:
            raise ValueError(f"Source label consumed prose/math: {label}")
        if url not in source_map:
            key = f"S{len(records) + 1}"
            source_map[url] = key
            records.append({"key": key, "title": label, "url": url})
        return f"[{source_map[url]}]"

    chapters = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        # Modern font commands also parse into native Word OMML via Pandoc.
        text = re.sub(r"\{\\rm\s+([^{}]+)\}", r"{\\mathrm{\1}}", text)
        text = re.split(
            r"^###\s+(?:本章.*来源|参考来源|实际读取来源|Sources|参考文献)",
            text, maxsplit=1, flags=re.M,
        )[0]
        text = rewrite_prose_links(text, citation)
        text = re.sub(r"(\[S\d+\])(?=\[S\d+\])", r"\1、", text)
        # Chapter notes are one directory deeper than the assembled manuscript.
        text = text.replace("](../../images/", "](../images/")
        chapters.append(text.strip())
    appendices = (ROOT / "appendices.md").read_text(encoding="utf-8")
    front = (ROOT / "frontmatter.md").read_text(encoding="utf-8")
    sources = [
        "## 附录 C 一手来源与实现入口",
        "引用按正文首次出现排序。S 编号专用于来源，避免与代码中的数组索引混淆。"
        "教材、论文和官方实现分别提供推导背景与接口事实；本书算例、数值验证和系统组合为教学编写。"
        "软件复现应固定版本，访问日期为 2026-10-27。",
    ]
    for record in records:
        sources.append(
            f"- [{record['key']}] {record['title']}。"
            f"[访问来源]({record['url']})"
        )
    definitions = [f"[{r['key']}]: {r['url']}" for r in records]
    document = "\n\n".join([front.strip(), *chapters, appendices.strip(),
                            *sources, "\n".join(definitions)]) + "\n"
    (ROOT / f"{STEM}.md").write_text(document, encoding="utf-8")
    (ROOT / "sources.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    save_json("assembly-check.json", {
        "chapters": len(files), "chapter_files": [f.name for f in files],
        "sources": len(records), "source_urls_unique": len(source_map),
    })


def bibliography():
    fields = set()
    papers = []
    inputs = [ROOT.parent / "papers.json", *(ROOT / "notes").glob("*papers.json")]
    for path in inputs:
        records = json.loads(path.read_text(encoding="utf-8"))
        for paper in records:
            fields.update(paper.keys())
            if not all(paper.get(key) for key in ("title", "authors", "year")):
                raise ValueError(f"Incomplete paper identity: {paper}")
            papers.append(paper)
    seen = set()
    combined = []
    for paper in papers:
        key = paper.get("arxiv_id") or paper.get("doi") or paper["title"].lower()
        key = key.split("v")[0] if paper.get("arxiv_id") else key
        if key in seen:
            continue
        seen.add(key)
        combined.append({field: paper.get(field) for field in sorted(fields)})
    (ROOT / "papers.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    save_json("bibliography-check.json", {
        "papers": len(combined), "unique_paper_keys": len(seen),
        "unknown_values": "null; original metadata and version notes retained",
    })


def extract_math(content):
    """Protect code and replace TeX with tokens before Markdown parsing."""
    formulas = []
    def token(match):
        value = match.group()
        if value.startswith("`"):
            return value
        display = value.startswith("$$")
        tex = value[2:-2] if display else value[1:-1]
        checked = re.sub(r"\\(?:text|mathrm|operatorname)\{[^{}]*\}", "", tex)
        if re.search(r"[\u4e00-\u9fff]", checked):
            raise ValueError(f"Prose inside a math expression: {tex}")
        name = f"MATHBLOCKTOKEN{len(formulas):05}Z"
        formulas.append({"tex": tex.strip(), "display": display, "token": name})
        return "\n\n" + name + "\n\n" if display else name

    return PROTECTED.sub(token, content), formulas


def embed_math(rendered, formulas):
    payload = [{"tex": f["tex"], "display": f["display"]} for f in formulas]
    result = subprocess.run(
        ["node", str(ROOT / "render_math.cjs")],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    if result.returncode:
        raise ValueError(result.stderr)
    images = json.loads(result.stdout)
    scales = []
    for formula, image in zip(formulas, images):
        width, height = image["width_ex"] * 5.25, image["height_ex"] * 5.25
        scale = min(1.0, 445 / width)
        if scale < 0.85:
            scales.append({"tex": formula["tex"], "scale": round(scale, 3)})
        data = base64.b64encode(image["svg"].encode()).decode()
        align = image["vertical_ex"] * 5.25
        tag = (
            f'<img class="math-image" alt="{html.escape(formula["tex"], quote=True)}" '
            f'src="data:image/svg+xml;base64,{data}" '
            f'style="width:{width*scale:.3f}pt;height:{height*scale:.3f}pt;'
            f'vertical-align:{align*scale:.3f}pt">'
        )
        if formula["display"]:
            rendered = rendered.replace(
                f'<p>{formula["token"]}</p>', f'<div class="equation">{tag}</div>'
            )
        else:
            rendered = rendered.replace(formula["token"], tag)
    if "MATHBLOCKTOKEN" in rendered:
        raise ValueError("Unresolved formula placeholder")
    save_json("math-check.json", {
        "formulas": len(formulas),
        "display": sum(f["display"] for f in formulas),
        "inline": sum(not f["display"] for f in formulas),
        "rendered": len(images), "parser_errors": 0,
        "substantially_scaled_formulas": scales,
    })
    return rendered


def pdf():
    import markdown
    import pymupdf
    from weasyprint import CSS, HTML
    from weasyprint.text.fonts import FontConfiguration

    source, references = read_source()
    content = source.split("[TOC]", 1)[1]
    content = re.sub(r"^\[S\d+\]:.*$", "", content, flags=re.M)
    content = re.sub(
        r"\[(S\d+)\]", lambda m: f"[{m[1]}]({references[m[1]]})", content
    )
    editor = markdown.Markdown(
        extensions=["tables", "toc", "sane_lists", "fenced_code"],
        extension_configs={"toc": {"toc_depth": "2"}},
    )
    prepared, formulas = extract_math(content)
    rendered = editor.convert("[TOC]\n\n" + prepared)
    rendered = embed_math(rendered, formulas)
    rendered = rendered.replace(
        '<pre><code class="language-json">',
        '<pre class="splittable-code"><code class="language-json">',
    )
    citation_count = 0
    for match in re.finditer(r'<a href="([^"]+)">(S\d+)</a>', rendered):
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
        if title.startswith(("01 ", "附录 C")):
            css += " start-section"
        if not title.startswith("附录 C"):
            part = re.sub(
                r'(<a\b[^>]*>)(S\d+)(</a>)',
                lambda m: '<sup class="citation">' + m[1] +
                "[" + m[2] + "]" + m[3] + "</sup>", part
            )
        chapters.append(f'<section class="{css}">{part}</section>')
    cover = """
    <section class="cover">
      <p class="eyebrow">数学模型 · 算法过程 · 实现接口</p>
      <h1>Physical AI<br>底层原理与实现细节</h1>
      <p class="subtitle">逐层展开机器人、学习模型与运行系统<br>技术手册 · 深化版 2.0</p>
      <div class="cover-rule"></div>
      <p class="cover-message">读公式背后的假设，<br>追踪算法怎样从输入算到输出。</p>
      <p class="cover-topics">SE(3) 与雅可比 · EKF 与 SLAM · 规划与控制<br>
      VLA · 扩散与 Flow Matching · 强化学习 · 世界模型<br>
      数据对齐 · 接触求解 · GPU 时序 · 统计评测</p>
      <p class="cover-date">资料核实：2026 年 10 月 27 日<br>
      版本 2.0 · 原理、公式、伪代码与数值验证</p>
      <p class="cover-note">前版知识地图保留，本册面向逐层理解与实现。<br>
      数学表达均单独渲染；教学程序不连接硬件、不训练模型。</p>
    </section>
    """
    document = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        f"<title>{TITLE}</title>"
        '<link rel="stylesheet" href="print.css"></head><body>' + cover +
        '<section class="contents-page"><h2 class="contents-title">阅读目录</h2>'
        '<p class="reading-note">01—05：系统、身体、估计、规划与控制。<br>'
        '06—09：表示、动作生成、强化学习与世界模型。<br>'
        '10—14：数据、仿真、运行系统、评测和数值练习。</p>' +
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


def repair_pandoc_omml(file):
    """Correct two demonstrated serializer defects without altering equations."""
    namespace = "http://schemas.openxmlformats.org/officeDocument/2006/math"
    ns = {"m": namespace}
    ET.register_namespace("m", namespace)
    with zipfile.ZipFile(file) as package:
        tree = ET.fromstring(package.read("word/document.xml"))
    operations = []
    for index, node in enumerate(tree.findall(".//m:mcPr", ns), 1):
        count = node.find("m:count", ns)
        if count is not None and len(node) and node[0] is not count:
            node.remove(count)
            node.insert(0, count)
            operations.append({
                "command": "raw-set", "part": "/document",
                "xpath": f"(//m:mcPr)[{index}]", "action": "replace",
                "xml": ET.tostring(node, encoding="unicode"),
            })
    normal_styles = 0
    for index, node in enumerate(tree.findall(".//m:rPr", ns), 1):
        if node.find("m:nor", ns) is None:
            continue
        removed = [child for child in node
                   if child.tag in {f"{{{namespace}}}sty", f"{{{namespace}}}scr"}]
        if removed:
            for child in removed:
                node.remove(child)
            normal_styles += 1
            operations.append({
                "command": "raw-set", "part": "/document",
                "xpath": f"(//m:rPr)[{index}]", "action": "replace",
                "xml": ET.tostring(node, encoding="unicode"),
            })
    if operations:
        office("batch", file, "--commands",
               json.dumps(operations, ensure_ascii=False), "--json")
    save_json("omml-repair.json", {
        "matrix_property_order_fixed": len(operations) - normal_styles,
        "normal_text_style_conflicts_fixed": normal_styles,
        "mathematical_content_changed": False,
    })


def docx():
    source, references = read_source()
    content = re.sub(r"^\[S\d+\]:.*$", "", source, flags=re.M)
    content = re.sub(
        r"\[(S\d+)\]", lambda m: f"[{m[1]}]({references[m[1]]})", content
    )
    file = ROOT / f"{STEM}.docx"
    if file.exists():
        office("close", file)
    conversion = subprocess.run([
        "pandoc", "--from", "markdown", "--to", "docx",
        "--standalone", "--lua-filter", str(ROOT / "docx_filter.lua"),
        "--metadata", "lang=zh-CN", "--output", str(file),
    ], input=content, text=True, capture_output=True, check=True)
    (QA / "pandoc-warnings.txt").write_text(conversion.stderr, encoding="utf-8")
    if "Could not convert TeX math" in conversion.stderr:
        raise ValueError("Word math conversion failed; inspect pandoc-warnings.txt")
    office("open", file)
    repair_pandoc_omml(file)
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
           "--prop", "text=Physical AI · 底层原理与实现细节",
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
        match = re.fullmatch(r"\[(S\d+)\]", label)
        if match:
            target = targets.get(link.attrib.get("{" + ns["r"] + "}id"))
            if target != references[match[1]]:
                raise ValueError(f"Misbound Word citation: {label} -> {target}")
            count += 1
    math_ns = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
    math_count = len(document.findall(".//m:oMath", math_ns))
    expected_math_count = len(extract_math(content)[1])
    if math_count != expected_math_count:
        raise ValueError(
            f"Word math mismatch: {math_count} native vs {expected_math_count} source"
        )
    result = {"schema": "passed", "citations_checked": count,
              "native_math_expressions": math_count,
              "source_math_expressions": expected_math_count,
              "misbound_citations": 0, "live_page_fields": len(page_fields),
              "dynamic_toc": "recalculate on open in Word"}
    save_json("docx-check.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("assemble", "pdf", "docx", "all"),
                        default="all")
    args = parser.parse_args()
    QA.mkdir(exist_ok=True)
    assemble()
    bibliography()
    if args.format in ("pdf", "all"):
        pdf()
    if args.format in ("docx", "all"):
        docx()
