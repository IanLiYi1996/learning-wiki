"""Apply report styles through OfficeCLI and retain its verification output."""

import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILE = ROOT / "GTC_Berlin_2026_Physical_AI_深度调研报告.docx"


def office(*args):
    result = subprocess.run(
        ["officecli", *map(str, args)], check=True,
        capture_output=True, text=True,
    )
    return result.stdout


def operation(path, props):
    return {"command": "set", "path": path, "props": props}


def main():
    office("open", FILE)
    office("add", FILE, "/styles", "--type", "style",
           "--prop", "id=TableNormal", "--prop", "name=Normal Table",
           "--prop", "type=table")
    office("get", FILE, "/styles/TableNormal")
    operations = [
        operation("/", {
            "title": "GTC Berlin 2026：Physical AI 内容整理",
            "author": "研究整理",
            "description": "世界模型、机器人、工厂和自动驾驶的产品、技术与案例说明",
            "pageWidth": "21cm", "pageHeight": "29.7cm",
            "marginTop": "2.3cm", "marginBottom": "2.3cm",
            "marginLeft": "2.54cm", "marginRight": "2.54cm",
            "docDefaults.font": "Noto Sans CJK SC",
            "docDefaults.font.eastAsia": "Noto Sans CJK SC",
            "docDefaults.fontSize": "11pt",
            "updateFields": "true",
        }),
        operation("/styles/Normal", {
            "font": "Noto Sans CJK SC", "font.ea": "Noto Sans CJK SC",
            "size": "11pt", "lineSpacing": "1.3x",
            "spaceAfter": "7pt", "color": "182230",
        }),
        operation("/styles/BodyText", {
            "font": "Noto Sans CJK SC", "font.ea": "Noto Sans CJK SC",
            "size": "11pt", "lineSpacing": "1.3x",
            "spaceAfter": "7pt", "color": "182230",
        }),
        operation("/styles/Title", {
            "font": "Noto Sans CJK SC", "font.ea": "Noto Sans CJK SC",
            "size": "32pt", "bold": "true", "color": "245447",
            "align": "left", "spaceBefore": "45pt", "spaceAfter": "18pt",
        }),
        operation("/styles/Heading1", {
            "font": "Noto Sans CJK SC", "font.ea": "Noto Sans CJK SC",
            "size": "20pt", "bold": "true", "color": "245447",
            "spaceBefore": "16pt", "spaceAfter": "10pt",
            "keepNext": "true", "keepLines": "true",
        }),
        operation("/styles/Heading2", {
            "font": "Noto Sans CJK SC", "font.ea": "Noto Sans CJK SC",
            "size": "14pt", "bold": "true", "color": "182230",
            "spaceBefore": "12pt", "spaceAfter": "6pt", "keepNext": "true",
        }),
        operation("/body/p[2]", {
            "size": "16pt", "color": "344054", "spaceAfter": "16pt",
        }),
    ]
    first_heading = json.loads(office(
        "query", FILE, "paragraph[style=Heading1]", "--json"
    ))["data"]["results"][0]["path"]
    operations.append(operation(first_heading, {"pageBreakBefore": "true"}))
    for index in (3, 4, 5, 6):
        operations.append(operation(
            f"/body/p[{index}]", {"spaceAfter": "12pt", "lineSpacing": "1.4x"}
        ))
    # Discover exact semantic paths instead of relying on shifted indices.
    body_tree = office("get", FILE, "/body", "--depth", "4")
    for line in body_tree.splitlines():
        match = re.match(r"(/body/tbl\[\d+\]) \(table\)", line)
        if match:
            operations.append(operation(match[1], {
                "width": "100%", "layout": "autofit", "padding": "90",
            }))
        match = re.match(r"(/body/tbl\[\d+\]/tr\[(\d+)\]) \(row\)", line)
        if match:
            props = {"cantSplit": "true"}
            if match[2] == "1":
                props["header"] = "true"
            operations.append(operation(match[1], props))
        match = re.match(r"(/body/tbl\[\d+\]/tr\[(\d+)\]/tc\[\d+\]) \(cell\)", line)
        if match:
            props = {
                "font": "Noto Sans CJK SC", "size": "9.3pt", "valign": "top"
            }
            if match[2] == "1":
                props.update({"fill": "EDF4F1", "bold": "true"})
            operations.append(operation(match[1], props))
    batch = json.dumps(operations, ensure_ascii=False)
    office("batch", FILE, "--commands", batch, "--json")
    # Read back structural settings before inserting another structure.
    office("get", FILE, "/styles/Heading1")
    office("get", FILE, "/body/tbl[1]", "--depth", "1")
    office(
        "add", FILE, "/body", "--type", "toc",
        "--prop", "levels=1-1", "--prop", "title=阅读目录",
        "--prop", "hyperlinks=true", "--before", first_heading,
    )
    office("get", FILE, "/toc", "--depth", "2")
    office("set", FILE, "/styles/TOCHeading",
           "--prop", "color=245447", "--prop", "pageBreakBefore=true",
           "--prop", "keepNext=true")
    office(
        "add", FILE, "/", "--type", "header",
        "--prop", "text=GTC Berlin 2026 · Physical AI",
        "--prop", "size=8pt", "--prop", "color=667085",
    )
    office(
        "add", FILE, "/", "--type", "footer",
        "--prop", "type=default", "--prop", "text=第 ",
        "--prop", "size=9pt", "--prop", "align=center",
    )
    office("add", FILE, "/footer[1]/p[1]", "--type", "field",
           "--prop", "fieldType=page")
    office("add", FILE, "/footer[1]/p[1]", "--type", "run", "--prop", "text= / ")
    office("add", FILE, "/footer[1]/p[1]", "--type", "field",
           "--prop", "fieldType=numpages")
    office("get", FILE, "/footer[1]", "--depth", "3")
    # OfficeCLI's table-border setter can append tblBorders after tblLayout.
    # Retain the header shading and remove only that optional border element.
    if "tblBorders" in office("raw", FILE, "/document"):
        office("raw-set", FILE, "/document", "--xpath",
               "//w:tblPr/w:tblBorders", "--action", "remove")
    office("save", FILE)
    qa = ROOT / "qa"
    for mode in ("outline", "issues", "stats"):
        (qa / f"docx-{mode}.txt").write_text(
            office("view", FILE, mode), encoding="utf-8"
        )
    preview = office("view", FILE, "html")
    preview_path = qa / "docx-preview.html"
    preview_path.write_text(preview, encoding="utf-8")
    office("close", FILE)
    validation = office("validate", FILE)
    (qa / "docx-validation.txt").write_text(validation, encoding="utf-8")
    if "no errors found" not in validation.lower():
        raise ValueError(validation)
    text = office("view", FILE, "text")
    if re.search(r"\[TOC\]|<TODO>|\{\{[^}]+\}\}|\\[tn]", text):
        raise ValueError("Placeholder or escape leaked into report")
    (qa / "docx-text.txt").write_text(text, encoding="utf-8")
    fields = office("query", FILE, "field[fieldType=page]", "--json")
    (qa / "docx-page-fields.json").write_text(fields, encoding="utf-8")
    definitions = dict(re.findall(
        r"^\[(\d+)\]:\s+(\S+)",
        (ROOT / "GTC_Berlin_2026_Physical_AI_深度调研报告.md").read_text(
            encoding="utf-8"
        ), re.M
    ))
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    with zipfile.ZipFile(FILE) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        relations = ET.fromstring(package.read("word/_rels/document.xml.rels"))
    targets = {relation.attrib["Id"]: relation.attrib["Target"]
               for relation in relations}
    count = 0
    for link in document.findall(".//w:hyperlink", ns):
        label = "".join(node.text or "" for node in link.findall(".//w:t", ns))
        number = re.fullmatch(r"\[(\d+)\]", label)
        if not number:
            continue
        target = targets.get(link.attrib.get("{" + ns["r"] + "}id"))
        if target != definitions[number[1]]:
            raise ValueError(f"Misbound Word citation: {label}: {target}")
        count += 1
    (qa / "docx-citation-check.json").write_text(
        json.dumps({"citations_checked": count, "misbound": 0}),
        encoding="utf-8"
    )
    print(json.dumps({"docx": str(FILE), "schema": "passed",
                      "dynamic_toc": "recalculate in Word on open",
                      "formatting_operations": len(operations),
                      "citations_checked": count,
                      "html_preview": str(preview_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
