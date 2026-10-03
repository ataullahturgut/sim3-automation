from __future__ import annotations

import json, math, os, time
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_price_integrity_audit_out"))
OUT.mkdir(parents=True, exist_ok=True)

API="https://api.twelvedata.com/time_series"
KEY=os.environ["TWELVE_DATA_API_KEY"]
TZ="America/New_York"
START="2026-01-27 00:00:00"
END="2026-03-25 23:59:59"
FROZEN=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"

SYMS={
 "gold":"XAU/USD",
 "silver":"XAG/USD",
 "platinum":"XPT/USD",
 "palladium":"XPD/USD",
}

def fetch(sym):
    params={
      "symbol":sym,"interval":"1h","start_date":START,"end_date":END,
      "timezone":TZ,"order":"ASC","outputsize":5000,"apikey":KEY,
    }
    for a in range(4):
        r=requests.get(API,params=params,timeout=60)
        try: p=r.json()
        except Exception: p={"status":"error","code":f"HTTP_{r.status_code}_NONJSON"}
        if r.status_code==429 or (isinstance(p,dict) and p.get("code")==429):
            if a==3: return pd.DataFrame(),{"symbol":sym,"error":"RATE_LIMIT"}
            time.sleep(65); continue
        if r.status_code!=200 or not isinstance(p,dict) or not p.get("values"):
            return pd.DataFrame(),{"symbol":sym,"error":str(p)[:500]}
        rows=[]
        for z in p["values"]:
            try:
                ts=pd.Timestamp(z["datetime"])
                close=float(z["close"])
            except Exception:
                continue
            rows.append((ts,close))
        x=pd.DataFrame(rows,columns=["ts","close"]).sort_values("ts").drop_duplicates("ts",keep="last")
        return x,{"symbol":sym,"rows":len(x),"first":str(x.ts.min()),"last":str(x.ts.max())}
    raise AssertionError

def main():
    frozen=pd.read_csv(FROZEN)
    frozen["date"]=pd.to_datetime(frozen.date)
    frozen=frozen[(frozen.date>=pd.Timestamp("2026-01-27"))&(frozen.date<=pd.Timestamp("2026-03-25"))].copy()

    details=[]
    status={}
    for metal,sym in SYMS.items():
        x,st=fetch(sym); status[metal]=st
        if x.empty: continue
        x["date"]=x.ts.dt.normalize()
        for hour in [12,16]:
            q=x[x.ts.dt.hour==hour][["date","close"]].rename(columns={"close":f"twelve_{hour}"})
            z=frozen[["date",metal]].merge(q,on="date",how="left")
            z["metal"]=metal
            z["hour"]=hour
            z["frozen"]=z[metal].astype(float)
            z["twelve"]=z[f"twelve_{hour}"].astype(float)
            z["log_ratio"]=z.apply(lambda r: math.log(r.frozen/r.twelve) if pd.notna(r.twelve) and r.twelve>0 else float("nan"),axis=1)
            details.append(z[["date","metal","hour","frozen","twelve","log_ratio"]])
        time.sleep(8)

    d=pd.concat(details,ignore_index=True) if details else pd.DataFrame()
    d.to_csv(OUT/"price_integrity_compare.csv",index=False)

    flagged=d[d.log_ratio.abs()>=0.03].copy()
    flagged.to_csv(OUT/"price_integrity_flagged.csv",index=False)

    lines=[
      "# GOLD H3 DAILY PRICE INTEGRITY AUDIT — 2026-10-03","",
      "**Scope:** frozen StakTrakr daily panel vs Twelve Data hourly closes, 2026-01-27..2026-03-25.","",
      "## Source status",""
    ]
    for k,v in status.items(): lines.append(f"- {k}: `{json.dumps(v,sort_keys=True)}`")
    lines += ["","## >=3% level discrepancies","",
      "| Date | Metal | Hour NY | Frozen | Twelve | log ratio |",
      "|---|---|---:|---:|---:|---:|"]
    for r in flagged.sort_values(["date","metal","hour"]).itertuples():
        lines.append(f"| {pd.Timestamp(r.date).date()} | {r.metal} | {r.hour}:00 | {r.frozen:.4f} | {r.twelve:.4f} | {100*r.log_ratio:+.2f}% |")

    focus=d[(d.date>=pd.Timestamp("2026-02-24"))&(d.date<=pd.Timestamp("2026-03-03"))].copy()
    lines += ["","## Feb 24–Mar 03 focus","",
      "| Date | Metal | Hour | Frozen | Twelve | log ratio |",
      "|---|---|---:|---:|---:|---:|"]
    for r in focus.sort_values(["date","metal","hour"]).itertuples():
        if pd.isna(r.twelve): continue
        lines.append(f"| {pd.Timestamp(r.date).date()} | {r.metal} | {r.hour}:00 | {r.frozen:.4f} | {r.twelve:.4f} | {100*r.log_ratio:+.2f}% |")

    (OUT/"PRICE_INTEGRITY_AUDIT.md").write_text("\n".join(lines)+"\n")
    (OUT/"price_integrity_summary.json").write_text(json.dumps({
      "schema":"GOLD_H3_PRICE_INTEGRITY_AUDIT",
      "status":status,
      "flagged_n":int(len(flagged)),
      "flagged":flagged.assign(date=flagged.date.astype(str)).to_dict(orient="records"),
    },indent=2,default=str)+"\n")
    print((OUT/"PRICE_INTEGRITY_AUDIT.md").read_text())

if __name__=="__main__":
    main()
