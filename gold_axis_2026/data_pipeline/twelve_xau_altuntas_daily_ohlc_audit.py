from __future__ import annotations
import hashlib, json, math, os, time
from datetime import date, datetime
from pathlib import Path
import requests

API_URL="https://api.twelvedata.com/time_series"
SYMBOL="XAU/USD"
INTERVAL="1day"
START="2017-10-01"
END="2025-12-31"
OUT=Path("altuntas_ohlc_audit_artifact")
YEARS=range(2017,2026)
MIN_COUNTS={"train":1000,"dev":200,"validation":200,"challenge":200}

def request_year(session,key,y):
    s=f"{y}-01-01" if y>2017 else START
    e=f"{y}-12-31"
    params={"symbol":SYMBOL,"interval":INTERVAL,"start_date":s,"end_date":e,"order":"ASC","outputsize":5000,"format":"JSON"}
    last=None
    for a in range(4):
        try:
            r=session.get(API_URL,params=params,headers={"Authorization":f"apikey {key}","User-Agent":"GoldControl-Altuntas-Audit/1.0"},timeout=(10,90))
            p=r.json()
            if isinstance(p,dict) and p.get("status")=="error":
                msg=str(p.get("message",""))
                if a<3 and ("credit" in msg.lower() or "rate" in msg.lower() or str(p.get("code","")) in {"429","4290"}):
                    time.sleep(61); continue
                raise RuntimeError(f"TWELVE_ERROR:{p.get('code')}:{msg[:180]}")
            r.raise_for_status()
            vals=p.get("values") if isinstance(p,dict) else None
            if not isinstance(vals,list) or not vals: raise RuntimeError(f"NO_VALUES:{y}")
            return vals, hashlib.sha256(r.content).hexdigest()
        except Exception as exc:
            last=exc
            if a==3: raise
            time.sleep(5*(a+1))
    raise RuntimeError(str(last))

def parse(row):
    d=datetime.fromisoformat(str(row["datetime"])).date()
    v={k:float(row[k]) for k in ("open","high","low","close")}
    if any((not math.isfinite(x) or x<=0) for x in v.values()): raise RuntimeError(f"INVALID_PRICE:{d}")
    if v["low"]>v["high"] or not(v["low"]<=v["open"]<=v["high"]) or not(v["low"]<=v["close"]<=v["high"]):
        raise RuntimeError(f"INVALID_OHLC:{d}")
    return d,v

def split_name(d):
    if date(2018,1,1)<=d<=date(2022,12,31): return "train"
    if d.year==2023: return "dev"
    if d.year==2024: return "validation"
    if d.year==2025: return "challenge"
    return None

def main():
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key: raise SystemExit("TWELVE_DATA_API_KEY_MISSING")
    sess=requests.Session(); rows={}; audits=[]
    for y in YEARS:
        vals,h=request_year(sess,key,y)
        accepted=0
        for raw in vals:
            d,v=parse(raw)
            if d.weekday()>=5: continue
            old=rows.get(d)
            if old is not None and old!=v: raise RuntimeError(f"DUPLICATE_CONFLICT:{d}")
            rows[d]=v; accepted+=1
        audits.append({"year":y,"provider_rows":len(vals),"accepted_weekdays":accepted,"payload_sha256":h})
        print(json.dumps({"year":y,"accepted_weekdays":accepted,"raw_values_logged":False},sort_keys=True))
        time.sleep(2)
    ds=sorted(rows)
    if not ds: raise RuntimeError("NO_DAILY_ROWS")
    digest_src="\n".join(f"{d.isoformat()}|{rows[d]['open']:.10f}|{rows[d]['high']:.10f}|{rows[d]['low']:.10f}|{rows[d]['close']:.10f}" for d in ds)
    panel_sha=hashlib.sha256(digest_src.encode()).hexdigest()

    # Eligibility: need 50 completed closes and an 11-day image ending at t; label uses next retained weekday.
    counts={k:0 for k in MIN_COUNTS}
    equal_labels={k:0 for k in MIN_COUNTS}
    for i,d in enumerate(ds[:-1]):
        sp=split_name(d)
        if sp is None or i<49 or i<10: continue
        nxt=ds[i+1]
        if split_name(nxt) is None and d.year==2025: continue
        c0=rows[d]["close"]; c1=rows[nxt]["close"]
        if c1==c0:
            equal_labels[sp]+=1; continue
        counts[sp]+=1
    ready=all(counts[k]>=MIN_COUNTS[k] for k in MIN_COUNTS)
    summary={
        "identity":"DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH",
        "status":"SOURCE_AUDIT_READY" if ready else "BLOCKED_INSUFFICIENT_IMAGE_SUPPORT",
        "provider":"Twelve Data","symbol":SYMBOL,"interval":INTERVAL,
        "requested_start":START,"requested_end":END,
        "first_accepted_date":ds[0].isoformat(),"last_accepted_date":ds[-1].isoformat(),
        "unique_weekday_daily_ohlc_rows":len(ds),
        "normalized_panel_sha256":panel_sha,
        "eligible_labelled_images":counts,
        "equal_close_labels_omitted":equal_labels,
        "minimum_support":MIN_COUNTS,
        "support_gate_passed":ready,
        "production_database_write":"NONE",
        "raw_vendor_values_persisted":False,
        "year_audit":audits,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"altuntas_daily_ohlc_source_audit_2026-09-21.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"counts":counts,"panel_sha256":panel_sha,"production_database_write":"NONE"},sort_keys=True))

if __name__=="__main__":
    main()
