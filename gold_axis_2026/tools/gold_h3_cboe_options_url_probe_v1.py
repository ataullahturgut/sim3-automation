from __future__ import annotations
import json,re,requests
from pathlib import Path

URL="https://www.cboe.com/_cache/js/4d8e75a5572cebd5d9bda2c068d4556e.js"
OUT=Path("gold_h3_cboe_options_url_probe_out"); OUT.mkdir(exist_ok=True)
r=requests.get(URL,timeout=60,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
res={"url":URL,"status":r.status_code,"bytes":len(r.content),"snippets":[]}
txt=r.text if r.status_code==200 else ""
patterns=[
    "/us/options/market_statistics/historical_data/download",
    "URLSearchParams","toISODate","toFormat","encodeURIComponent",
    "volumeAggType","volumeType","symbolType","exchanges","startDate","endDate",
    "reportType"
]
for pat in patterns:
    for m in list(re.finditer(re.escape(pat),txt,re.I))[:20]:
        res["snippets"].append({"pattern":pat,"start":m.start(),"text":txt[max(0,m.start()-1200):m.end()+3500]})
(OUT/"probe.json").write_text(json.dumps(res,indent=2))
lines=["# CBOE OPTIONS DOWNLOAD URL CONSTRUCTION PROBE","",f"- status: {r.status_code}",f"- bytes: {len(r.content)}",""]
for s in res["snippets"]:
    lines += [f"## {s['pattern']} @ {s['start']}","SNIPPET_START",s["text"],"SNIPPET_END",""]
(OUT/"RESULT.md").write_text("\n".join(lines))
print((OUT/"RESULT.md").read_text())

# trigger: url-probe-ready
