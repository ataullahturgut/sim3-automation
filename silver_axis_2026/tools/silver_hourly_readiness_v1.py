from __future__ import annotations
import json, os, time
from pathlib import Path

import requests
import psycopg

OUT=Path("silver_axis_2026/SILVER_HOURLY_READINESS_OUT")
OUT.mkdir(parents=True,exist_ok=True)

API="https://api.twelvedata.com/time_series"
SYMBOLS=["XAG/USD"]
DATES=["2018-06-15","2020-03-16","2022-06-15","2023-06-15","2024-06-17","2025-06-16","2026-08-31"]

def probe(symbol,date):
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key:return {"symbol":symbol,"date":date,"status":"NO_API_KEY"}
    params={"symbol":symbol,"interval":"1h","start_date":f"{date} 15:00:00","end_date":f"{date} 18:00:00",
            "timezone":"America/New_York","order":"ASC","outputsize":100,"apikey":key}
    r=requests.get(API,params=params,timeout=45)
    try:p=r.json()
    except Exception:p={"status":"error","message":"non-json"}
    vals=p.get("values") or [] if isinstance(p,dict) else []
    found=[x for x in vals if str(x.get("datetime"))==f"{date} 16:00:00"]
    return {"symbol":symbol,"date":date,"http":r.status_code,"api_status":p.get("status") if isinstance(p,dict) else None,
            "n_values":len(vals),"anchor_16_present":bool(found),"code":p.get("code") if isinstance(p,dict) else None}

def neon_inventory():
    dsn=os.environ.get("NEON_DATABASE_URL","").strip()
    if not dsn:return {"status":"NO_DSN","series":[]}
    try:
        with psycopg.connect(dsn,autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
                cur.execute("""
                    SELECT series_id, count(*) AS n, min(observation_ts), max(observation_ts)
                    FROM observations
                    WHERE upper(series_id) LIKE '%XAG%'
                       OR upper(series_id) LIKE '%SILVER%'
                       OR upper(series_id) LIKE 'SI_%'
                       OR upper(series_id) = 'SI'
                    GROUP BY series_id
                    ORDER BY n DESC
                    LIMIT 100
                """)
                rows=cur.fetchall()
            conn.rollback()
        return {"status":"OK","series":[{"series_id":r[0],"n":int(r[1]),"first":str(r[2]),"last":str(r[3])} for r in rows]}
    except Exception as e:
        return {"status":"ERROR","error":f"{type(e).__name__}:{e}","series":[]}

def main():
    results=[]
    for s in SYMBOLS:
        for d in DATES:
            results.append(probe(s,d))
            time.sleep(3)
    inv=neon_inventory()
    out={"identity":"SILVER_HOURLY_READINESS_V1","twelve_probes":results,"neon_inventory":inv}
    (OUT/"SILVER_HOURLY_READINESS_V1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    available=[r["date"] for r in results if r.get("anchor_16_present")]
    lines=["# SILVER HOURLY READINESS V1","",
           f"TwelveData symbol: **XAG/USD**","",
           "| Date | 16:00 NY 1H bar | API status |",
           "|---|---|---|"]
    for r in results:
        lines.append(f"| {r['date']} | {'YES' if r.get('anchor_16_present') else 'NO'} | {r.get('api_status') or r.get('status') or r.get('http')} |")
    lines += ["",f"Earliest sampled proven 1H date: **{min(available) if available else 'NOT_PROVEN'}**","",
              "## Existing database inventory","",f"Status: **{inv['status']}**"]
    for x in inv.get("series",[]):lines.append(f"- {x['series_id']}: n={x['n']}, {x['first']} .. {x['last']}")
    (OUT/"SILVER_HOURLY_READINESS_V1.md").write_text("\n".join(lines)+"\n")
    print((OUT/"SILVER_HOURLY_READINESS_V1.md").read_text())

if __name__=="__main__":main()

# workflow trigger 2026-10-05
