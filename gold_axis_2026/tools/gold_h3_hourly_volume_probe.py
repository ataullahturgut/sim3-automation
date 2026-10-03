from pathlib import Path
import json
import pandas as pd
import requests, numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUTJ=AX/"GOLD_H3_HOURLY_VOLUME_PROBE_2026-10-04.json"
OUTM=AX/"GOLD_H3_HOURLY_VOLUME_PROBE_2026-10-04.md"

SYMS={"GC":"GC=F","SI":"SI=F"}
START=int(pd.Timestamp("2025-01-01",tz="UTC").timestamp())
END=int(pd.Timestamp("2026-10-04",tz="UTC").timestamp())
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def fetch(sym):
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(sym,safe='')}"
        params={"period1":START,"period2":END,"interval":"1h","events":"history"}
        try:
            r=S.get(url,params=params,timeout=60)
            if r.status_code!=200:
                last=f"HTTP {r.status_code}"; continue
            z=r.json()["chart"]["result"][0]
            q=z["indicators"]["quote"][0]
            rows=[]
            for i,t in enumerate(z["timestamp"]):
                c=q["close"][i]; v=q["volume"][i]
                if c is None: continue
                rows.append((pd.to_datetime(t,unit="s",utc=True),float(c),np.nan if v is None else float(v)))
            return pd.DataFrame(rows,columns=["ts","close","volume"])
        except Exception as e: last=repr(e)
    raise RuntimeError(last)

out={}
for name,sym in SYMS.items():
    try:
        d=fetch(sym)
        nz=d.volume.fillna(0)>0
        et=d.ts.dt.tz_convert("America/New_York")
        out[name]={
            "symbol":sym,"rows":len(d),
            "volume_nonnull":int(d.volume.notna().sum()),
            "volume_positive":int(nz.sum()),
            "positive_rate":float(nz.mean()),
            "volume_median_positive":float(d.loc[nz,"volume"].median()) if nz.any() else None,
            "volume_p95_positive":float(d.loc[nz,"volume"].quantile(.95)) if nz.any() else None,
            "first_et":str(et.min()),"last_et":str(et.max())
        }
    except Exception as e:
        out[name]={"symbol":sym,"error":repr(e)}
OUTJ.write_text(json.dumps(out,indent=2)+"\n")
lines=["# H3 HOURLY VOLUME PROBE","",
"| Channel | Rows | Positive volume | Rate | Median positive | P95 |",
"|---|---:|---:|---:|---:|---:|"]
for k,x in out.items():
    lines.append(f"| {k} | {x.get('rows','')} | {x.get('volume_positive','')} | {100*x.get('positive_rate',0):.2f}% | {x.get('volume_median_positive','')} | {x.get('volume_p95_positive','')} |")
OUTM.write_text("\n".join(lines)+"\n")
print(OUTM.read_text())

# trigger: hourly-volume-probe-ready
