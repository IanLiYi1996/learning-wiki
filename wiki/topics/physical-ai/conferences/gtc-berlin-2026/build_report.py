"""Render the sourced report to HTML/PDF and check the resulting layout."""

import json
import re
from pathlib import Path

import markdown
import pymupdf
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

ROOT = Path(__file__).resolve().parent
STEM = "GTC_Berlin_2026_Physical_AI_深度调研报告"


def main():
    source = (ROOT / f"{STEM}.md").read_text(encoding="utf-8")
    definitions = dict(re.findall(r"^\[(\d+)\]:\s+(\S+)", source, re.M))
    prose = re.sub(r"^\[\d+\]:.*$", "", source, flags=re.M)
    cited = set(re.findall(r"\[(\d+)\]", prose))
    if cited - definitions.keys():
        raise ValueError(f"Missing sources: {cited - definitions.keys()}")
    if "[TOC]" not in source:
        raise ValueError("Missing contents marker")
    _, body_source = source.split("[TOC]", 1)
    # Python-Markdown permits whitespace between full reference labels.
    # Resolve numbered citations explicitly so "[1] [2]" never binds 1 to 2.
    body_source = re.sub(r"^\[\d+\]:.*$", "", body_source, flags=re.M)
    body_source = re.sub(
        r"\[(\d+)\]",
        lambda match: f"[{match[1]}]({definitions[match[1]]})",
        body_source,
    )
    editor = markdown.Markdown(
        extensions=["tables", "sane_lists", "toc", "fenced_code"],
        extension_configs={"toc": {"toc_depth": "2", "permalink": False}},
    )
    rendered = editor.convert("[TOC]\n\n" + body_source)
    citation_count = 0
    for match in re.finditer(r'<a href="([^"]+)">(\d+)</a>', rendered):
        if match[1] != definitions[match[2]]:
            raise ValueError(f"Misbound citation {match[2]}: {match[1]}")
        citation_count += 1
    if not citation_count:
        raise ValueError("No numbered citations checked")
    contents_match = re.match(r'<div class="toc">.*?</div>\s*', rendered, re.S)
    if not contents_match:
        raise ValueError("Contents generation failed")
    contents = contents_match.group(0)
    body = rendered[contents_match.end():]
    chapters = []
    for part in re.split(r"(?=<h2\b)", body):
        if not part.strip():
            continue
        match = re.search(r"<h2\b[^>]*>(.*?)</h2>", part, re.S)
        title = match.group(1) if match else ""
        is_sources = title.startswith("附录 C")
        if not is_sources:
            part = re.sub(
                r'(<a\b[^>]*>)(\d+)(</a>)',
                lambda m: '<sup class="citation">' + m[1] + "[" + m[2] +
                "]" + m[3] + "</sup>",
                part,
            )
        classes = ["chapter"]
        if title.startswith("一、"):
            classes.append("start-section")
        if is_sources:
            classes.append("sources")
        if title.startswith("八、"):
            classes.append("sessions")
        chapters.append(f'<section class="{" ".join(classes)}">{part}</section>')
    cover = """
    <section class="cover">
      <p class="eyebrow">会议内容整理 · 2026 / BERLIN</p>
      <h1>GTC Berlin 2026<br>Physical AI</h1>
      <p class="subtitle">机器人、工厂与自动驾驶<br>技术、产品和案例说明</p>
      <div class="cover-rule"></div>
      <p class="cover-message">世界模型怎样生成场景，<br>
      机器人怎样学习动作。</p>
      <p class="cover-topics">Cosmos · GR00T · Isaac · Omniverse<br>
      工厂应用 · 汽车合作 · Physical AI 技术栈</p>
      <p class="cover-date">会议：2026 年 10 月 20–22 日 · 德国柏林<br>
      资料整理：2026 年 10 月 26 日 · 版本 1.2</p>
      <p class="cover-note">根据 NVIDIA 和合作方的公开资料整理。<br>
      介绍工具用途、技术栈、会议案例及发布信息。</p>
    </section>
    """
    reading = """
    <section class="contents-page">
    <h2 class="contents-title">阅读目录</h2>
    <p class="reading-note">正文按世界模型、机器人、工厂和自动驾驶归类。<br>
    第六章说明 Physical AI 技术栈，第七章汇总发布信息。<br>
    后面附会议场次、名词对照及原始资料。</p>
    """
    html = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<title>GTC Berlin 2026 · Physical AI 内容整理</title>'
        '<link rel="stylesheet" href="print.css"></head><body>' +
        cover + reading + contents + "</section>" +
        "\n".join(chapters) + "</body></html>"
    )
    (ROOT / f"{STEM}.html").write_text(html, encoding="utf-8")
    fonts = FontConfiguration()
    HTML(string=html, base_url=str(ROOT)).write_pdf(
        ROOT / f"{STEM}.pdf",
        stylesheets=[CSS(filename=str(ROOT / "print.css"), font_config=fonts)],
        font_config=fonts,
        pdf_tags=True,
    )
    pdf = pymupdf.open(ROOT / f"{STEM}.pdf")
    pages = []
    for number, page in enumerate(pdf, 1):
        text = page.get_text()
        blocks = [b for b in page.get_text("blocks") if b[4].strip()]
        pages.append({
            "page": number,
            "characters": len(text),
            "bounds": [
                round(min(b[0] for b in blocks), 1),
                round(min(b[1] for b in blocks), 1),
                round(max(b[2] for b in blocks), 1),
                round(max(b[3] for b in blocks), 1),
            ] if blocks else None,
        })
    report = {
        "pdf_pages": len(pdf),
        "source_entries": len(definitions),
        "unique_source_urls": len(set(definitions.values())),
        "chinese_characters": len(re.findall(r"[\u4e00-\u9fff]", source)),
        "chapters_and_appendices": len(chapters),
        "bookmarks": len(pdf.get_toc()),
        "pdf_links": sum(len(p.get_links()) for p in pdf),
        "citations_checked": citation_count,
        "misbound_citations": 0,
        "missing_references": [],
        "pages": pages,
    }
    qa = ROOT / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "layout-check.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    columns = 4
    thumb_width = 260
    thumb_height = 380
    rows = (len(pdf) + columns - 1) // columns
    montage = pymupdf.open()
    sheet = montage.new_page(width=columns * thumb_width, height=rows * thumb_height)
    for index, page in enumerate(pdf):
        column, row = index % columns, index // columns
        rect = pymupdf.Rect(
            column * thumb_width + 6, row * thumb_height + 17,
            (column + 1) * thumb_width - 6, (row + 1) * thumb_height - 6
        )
        sheet.show_pdf_page(rect, pdf, index)
        sheet.insert_text(
            (column * thumb_width + 8, row * thumb_height + 12),
            f"Page {index + 1}", fontsize=9, color=(0.25, 0.3, 0.35)
        )
    sheet.get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save(qa / "contact-sheet.png")
    for number in (1, 2, 4, len(pdf)):
        pdf[number - 1].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(
            qa / f"page-{number}.png"
        )
    print(json.dumps({k: v for k, v in report.items() if k != "pages"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
