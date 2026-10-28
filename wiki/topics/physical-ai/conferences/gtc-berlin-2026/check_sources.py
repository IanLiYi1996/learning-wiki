"""Check cited first-party endpoints without changing remote state."""

import concurrent.futures
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
text = (ROOT / "GTC_Berlin_2026_Physical_AI_深度调研报告.md").read_text(
    encoding="utf-8"
)
definitions = re.findall(r"^\[(\d+)\]:\s+(\S+)", text, re.M)
urls = sorted({url for _, url in definitions})


def check(url):
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "Research source verification"}
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            snippet = response.read(600_000) if "html" in content_type else b""
            html = snippet.decode("utf-8", errors="replace")
            match = re.search(r"<title\b[^>]*>(.*?)</title>", html, re.I | re.S)
            return {
                "url": url, "status": response.status,
                "final_url": response.url, "content_type": content_type,
                "page_title": re.sub(r"\s+", " ", match[1]).strip()
                if match else None,
            }
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"url": url, "error": str(error)}


with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(check, urls))
(ROOT / "qa" / "source-endpoint-check.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
issues = [r for r in results if "error" in r]
print(json.dumps({"unique_endpoints": len(results),
                  "readable": len(results) - len(issues), "issues": issues},
                 ensure_ascii=False, indent=2))
