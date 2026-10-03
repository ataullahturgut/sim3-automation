from pathlib import Path
import json, time
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT_JSON=AX/"GOLD_H3_LLRS_HOURLY_PROXY_PROBE_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_LLRS_HOURLY_PROXY_PROBE_2026-10-04.md"

SYMBOLS={
    "GC":"GC=F",
    "USD":"DX=F",
    "UST10":"ZN=F",
    "NASDAQ":"NQ=F",
    "VIXF":"VX=F",
    "SILVER":"SI=F",
    "WTI":"CL=F",
}
START=pd.Timestamp("2025-01-01",tz="UTC")
END=pd.Timestamp("2026-10-04",tz="UTC")
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def fetch(symbol):
    p1=int(START.timestamp()); p2=int(END.timestamp())
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(symbol,safe='')}"
        params={"period1":p1,"period2":p2,"interval":"1h","events":"history","includeAdjustedClose":"true"}
        try:
            r=S.get(url,params=params,timeout=60)
            if r.status_code!=200:
                last=f"HTTP {r.status_code}: {r.text[:200]}"
                continue
            j=r.json()
            err=j.get("chart",{}).get("error")
            result=j.get("chart",{}).get("result")
            if err or not result:
                last=f"chart_error={err}"
                continue
            z=result[0]
            ts=z.get("timestamp",[])
            q=z.get("indicators",{}).get("quote",[{}])[0]
            close=q.get("close",[])
            rows=[]
            for t,c in zip(ts,close):
                if c is None: continue
                rows.append((pd.to_datetime(t,unit="s",utc=True),float(c)))
            df=pd.DataFrame(rows,columns=["ts","close"]).drop_duplicates("ts").sort_values("ts")
            return df,{"host":host,"url":r.url,"meta":z.get("meta",{})}
        except Exception as e:
            last=repr(e)
    raise RuntimeError(last or "fetch failed")

def main():
    out={}
    lines=["# LLRS-H3 — HOURLY CROSS-ASSET PROXY PROBE","",
           "**Evidence class:** retrospective transport/coverage probe only.",""]
    for name,sym in SYMBOLS.items():
        try:
            df,meta=fetch(sym)
            et=df.ts.dt.tz_convert("America/New_York")
            years=et.dt.year.value_counts().sort_index().to_dict()
            out[name]={
                "symbol":sym,"status":"PASS","rows":len(df),
                "min_utc":str(df.ts.min()),"max_utc":str(df.ts.max()),
                "min_et":str(et.min()),"max_et":str(et.max()),
                "year_rows":{str(k):int(v) for k,v in years.items()},
                "exchange_tz":meta["meta"].get("exchangeTimezoneName"),
                "gmtoffset":meta["meta"].get("gmtoffset")
            }
        except Exception as e:
            out[name]={"symbol":sym,"status":"FAIL","error":repr(e)}

    lines += ["| Channel | Symbol | Status | Rows | First ET | Last ET |",
              "|---|---|---|---:|---|---|"]
    for name,x in out.items():
        lines.append(f"| {name} | {x['symbol']} | {x['status']} | {x.get('rows','')} | {x.get('min_et','')} | {x.get('max_et','')} |")
    OUT_JSON.write_text(json.dumps(out,indent=2,default=str)+"\n")
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: llrs-hourly-proxy-workflow-ready
