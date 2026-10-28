"""Store metadata for the two scoped primary technical reports."""

import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NS = {"a": "http://www.w3.org/2005/Atom"}
with urllib.request.urlopen(
    "https://export.arxiv.org/api/query?id_list=2606.02800", timeout=30
) as response:
    entry = ET.fromstring(response.read()).find("a:entry", NS)
if entry is None:
    raise ValueError("Missing arXiv entry")
title = " ".join(entry.findtext("a:title", namespaces=NS).split())
if "Cosmos 3" not in title:
    raise ValueError("Unexpected arXiv report")
published = entry.findtext("a:published", namespaces=NS)[:10]
authors = [e.text.strip() for e in entry.findall("a:author/a:name", NS)]
reports = [
    {
        "title": title,
        "authors": authors,
        "year": int(published[:4]),
        "publication_date": published,
        "publication_type": "preprint",
        "venue": "arXiv technical report",
        "doi": None,
        "arxiv_id": "2606.02800",
        "citation_count": None,
        "open_access_status": "green",
        "license": "OpenMDW-1.1 (project code/models; check report-specific terms)",
        "full_text_status": "open_pdf",
        "pdf_url": "https://arxiv.org/pdf/2606.02800",
        "code_url": "https://github.com/NVIDIA/cosmos",
        "source_platforms": ["arxiv", "NVIDIA Research", "official GitHub"],
        "fetched_at": "2026-10-26",
        "role": "pre-conference architecture background",
    },
    {
        "title": "Interactive World Simulation with Cosmos for Physical AI",
        "authors": ["NVIDIA"],
        "year": 2026,
        "publication_date": None,
        "publication_type": "technical-report",
        "venue": "NVIDIA Research technical report",
        "doi": None,
        "arxiv_id": None,
        "citation_count": None,
        "open_access_status": "unknown",
        "license": None,
        "full_text_status": "open_pdf",
        "pdf_url": "https://research.nvidia.com/labs/cosmos-lab/cosmos-simulation/technical-report.pdf",
        "code_url": "https://github.com/NVIDIA/cosmos-framework",
        "source_platforms": ["NVIDIA Research", "official GitHub"],
        "fetched_at": "2026-10-26",
        "role": "conference-related interactive simulation research",
    },
]
for report in reports:
    request = urllib.request.Request(report["pdf_url"], method="HEAD")
    with urllib.request.urlopen(request, timeout=30) as response:
        report["pdf_http_status"] = response.status
        report["pdf_content_type"] = response.headers.get("Content-Type")
        if "pdf" not in report["pdf_content_type"].lower():
            raise ValueError(f"PDF endpoint is not PDF: {report['title']}")
(ROOT / "notes" / "paper-metadata.json").write_text(
    json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({"reports": len(reports), "citation_counts": "not retrieved",
                  "pdf_endpoints_verified": True}, ensure_ascii=False))
