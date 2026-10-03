from __future__ import annotations
import json, re, urllib.parse
from pathlib import Path
import requests
from bs4 import BeautifulSoup

URL = "https://www.cboe.com/us/options/market_statistics/historical_data/"
OUT = Path("gold_h3_cboe_options_probe_out")
OUT.mkdir(exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

r = requests.get(URL, headers=HEADERS, timeout=60)
result = {
    "url": URL,
    "status": r.status_code,
    "bytes": len(r.content),
    "content_type": r.headers.get("content-type"),
    "forms": [],
    "scripts": [],
    "matches": [],
}

if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    for form in soup.find_all("form"):
        inputs = []
        for x in form.find_all(["input", "select", "button"]):
            inputs.append({
                "name": x.get("name"),
                "type": x.get("type"),
                "value": x.get("value"),
                "id": x.get("id"),
            })
        result["forms"].append({
            "action": form.get("action"),
            "method": form.get("method"),
            "inputs": inputs,
        })

    srcs = []
    for s in soup.find_all("script"):
        src = s.get("src")
        if src:
            srcs.append(urllib.parse.urljoin(URL, src))
    result["scripts"] = srcs

    pats = ["historical_data", "download", "volume", "symbol_type", "begin_date", "end_date", "underlying"]
    for src in srcs:
        try:
            q = requests.get(src, headers={"User-Agent": HEADERS["User-Agent"], "Accept": "*/*"}, timeout=60)
            txt = q.text if q.status_code == 200 and len(q.content) < 8_000_000 else ""
            low = txt.lower()
            if any(p in low for p in pats):
                snippets = []
                for p in pats:
                    for m in list(re.finditer(re.escape(p), low))[:5]:
                        snippets.append(txt[max(0, m.start()-400):m.end()+800])
                result["matches"].append({
                    "src": src,
                    "status": q.status_code,
                    "bytes": len(q.content),
                    "snippets": snippets[:30],
                })
        except Exception as e:
            result["matches"].append({"src": src, "error": repr(e)})
else:
    result["head"] = r.text[:1000]

(OUT / "probe.json").write_text(json.dumps(result, indent=2))
lines = [
    "# CBOE HISTORICAL OPTIONS FORM SOURCE PROBE",
    "",
    "- HTTP: " + str(result["status"]),
    "- bytes: " + str(result["bytes"]),
    "- forms: " + str(len(result["forms"])),
    "- scripts: " + str(len(result["scripts"])),
    "- matched scripts: " + str(len(result["matches"])),
    "",
]
for i, f in enumerate(result["forms"]):
    lines += [
        "## Form " + str(i+1),
        "- action: " + str(f["action"]),
        "- method: " + str(f["method"]),
        "- inputs: " + json.dumps(f["inputs"]),
        "",
    ]
for m in result["matches"]:
    lines += [
        "## Script " + str(m.get("src")),
        "- status: " + str(m.get("status")),
        "- bytes: " + str(m.get("bytes")),
        "",
    ]
    for sn in m.get("snippets", [])[:20]:
        lines += ["SNIPPET_START", sn[:1800], "SNIPPET_END", ""]

(OUT / "RESULT.md").write_text("\n".join(lines))
print((OUT / "RESULT.md").read_text())

# trigger: workflow-ready
