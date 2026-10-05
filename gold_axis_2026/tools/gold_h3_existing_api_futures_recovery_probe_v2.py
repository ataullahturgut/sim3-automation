from __future__ import annotations

import io
import json
import math
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUTJ = AX / "GOLD_H3_EXISTING_API_FUTURES_RECOVERY_PROBE_V2_2026-10-05.json"
OUTM = AX / "GOLD_H3_EXISTING_API_FUTURES_RECOVERY_PROBE_V2_2026-10-05.md"

KEY = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
if not KEY:
    raise RuntimeError("TWELVE_DATA_API_KEY missing")

TD = "https://api.twelvedata.com"
S = requests.Session()
S.headers.update({"User-Agent": "gold-h3-existing-api-recovery-v2/1.0"})
LAST_CALL = 0.0
MIN_GAP = 8.2  # current project entitlement was observed at 8 credits/minute

TARGETS = {
    "GC": {
        "name": "COMEX Gold futures",
        "exchange_primary": "COMEX",
        "exchange_alt": "CME",
        "direct_symbols": ["GC", "GC=F", "GC1!"],
        "searches": ["COMEX Gold Futures", "Gold Futures CME"],
        "proxy_terms": ["gold"],
    },
    "SI": {
        "name": "COMEX Silver futures",
        "exchange_primary": "COMEX",
        "exchange_alt": "CME",
        "direct_symbols": ["SI", "SI=F", "SI1!"],
        "searches": ["COMEX Silver Futures", "Silver Futures CME"],
        "proxy_terms": ["silver"],
    },
    "NQ": {
        "name": "E-mini Nasdaq-100 futures",
        "exchange_primary": "CME",
        "exchange_alt": "CME",
        "direct_symbols": ["NQ", "NQ=F", "NQ1!"],
        "searches": ["E-mini Nasdaq 100 Futures", "Nasdaq 100 Futures CME"],
        "proxy_terms": ["nasdaq"],
    },
    "ZN": {
        "name": "10-Year U.S. Treasury Note futures",
        "exchange_primary": "CBOT",
        "exchange_alt": "CME",
        "direct_symbols": ["ZN", "ZN=F", "ZN1!"],
        "searches": ["10 Year Treasury Note Futures", "10Y Treasury Futures CBOT"],
        "proxy_terms": ["treasury", "10 year"],
    },
    "CL": {
        "name": "NYMEX WTI Crude Oil futures",
        "exchange_primary": "NYMEX",
        "exchange_alt": "CME",
        "direct_symbols": ["CL", "CL=F", "CL1!"],
        "searches": ["NYMEX WTI Crude Oil Futures", "Crude Oil Futures CME"],
        "proxy_terms": ["wti", "crude oil"],
    },
}

def td_get(endpoint: str, params: dict) -> tuple[int, dict]:
    global LAST_CALL
    wait = MIN_GAP - (time.monotonic() - LAST_CALL)
    if wait > 0:
        time.sleep(wait)
    p = dict(params)
    p["apikey"] = KEY
    r = S.get(f"{TD}/{endpoint}", params=p, timeout=45)
    LAST_CALL = time.monotonic()
    try:
        j = r.json()
    except Exception:
        j = {"status": "error", "message": f"NON_JSON_HTTP_{r.status_code}"}
    return r.status_code, j

def safe_meta(j):
    m = (j or {}).get("meta") or {}
    keys = ["symbol","name","exchange","mic_code","currency","type","instrument_type","exchange_timezone","interval"]
    return {k:m.get(k) for k in keys if m.get(k) is not None}

def classify_meta(meta: dict, target: str) -> str:
    text = " ".join(str(v) for v in meta.values()).lower()
    if any(k in text for k in ["future", "futures"]):
        if target=="GC" and any(k in text for k in ["gold","gc"]): return "POSSIBLE_EXACT_FUTURES"
        if target=="SI" and any(k in text for k in ["silver","si"]): return "POSSIBLE_EXACT_FUTURES"
        if target=="NQ" and any(k in text for k in ["nasdaq","nq"]): return "POSSIBLE_EXACT_FUTURES"
        if target=="ZN" and any(k in text for k in ["treasury","10-year","10 year","zn"]): return "POSSIBLE_EXACT_FUTURES"
        if target=="CL" and any(k in text for k in ["crude","wti","cl"]): return "POSSIBLE_EXACT_FUTURES"
    return "NOT_PROVEN_EXACT"

def test_timeseries(symbol: str, exchange: str | None, start: str, end: str):
    p = {
        "symbol": symbol,
        "interval": "1h",
        "start_date": start,
        "end_date": end,
        "timezone": "UTC",
        "outputsize": 5000,
        "format": "JSON",
    }
    if exchange:
        p["exchange"] = exchange
    st,j = td_get("time_series",p)
    vals = j.get("values") or [] if isinstance(j,dict) else []
    rows=[]
    for x in vals:
        dt=pd.to_datetime(x.get("datetime"),utc=True,errors="coerce")
        close=pd.to_numeric(x.get("close"),errors="coerce")
        if pd.notna(dt) and pd.notna(close) and float(close)>0:
            rows.append((dt,float(close),x.get("volume")))
    d=pd.DataFrame(rows,columns=["ts","close","volume"]) if rows else pd.DataFrame(columns=["ts","close","volume"])
    if not d.empty:
        d=d.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    return {
        "http":st,
        "status":j.get("status") if isinstance(j,dict) else None,
        "code":j.get("code") if isinstance(j,dict) else None,
        "message":j.get("message") if isinstance(j,dict) else None,
        "meta":safe_meta(j) if isinstance(j,dict) else {},
        "n":int(len(d)),
        "first":None if d.empty else str(d.ts.min()),
        "last":None if d.empty else str(d.ts.max()),
        "has_volume":False if d.empty else bool(pd.Series(d.volume).notna().any()),
        "_df":d,
    }

def search(q: str):
    st,j=td_get("symbol_search",{"symbol":q,"outputsize":100})
    rows=j.get("data") or [] if isinstance(j,dict) else []
    keep=[]
    for x in rows:
        y={k:x.get(k) for k in ["symbol","instrument_name","name","exchange","mic_code","exchange_timezone","instrument_type","type","country","currency"] if x.get(k) is not None}
        keep.append(y)
    return {"http":st,"status":j.get("status") if isinstance(j,dict) else None,
            "code":j.get("code") if isinstance(j,dict) else None,
            "message":j.get("message") if isinstance(j,dict) else None,
            "rows":keep}

def commodities():
    st,j=td_get("commodities",{"outputsize":5000})
    rows=j.get("data") or [] if isinstance(j,dict) else []
    keep=[]
    for x in rows:
        y={k:x.get(k) for k in ["symbol","name","currency","currency_base","currency_quote","type"] if x.get(k) is not None}
        keep.append(y)
    return {"http":st,"status":j.get("status") if isinstance(j,dict) else None,
            "code":j.get("code") if isinstance(j,dict) else None,
            "message":j.get("message") if isinstance(j,dict) else None,
            "rows":keep}

def load_frozen_panel():
    ref="origin/gold-h3-llrs-v1-20261004"
    path="gold_axis_2026/GOLD_H3_LLRS_V1_HOURLY_PANEL_2026-10-04.csv"
    try:
        subprocess.run(["git","fetch","origin","gold-h3-llrs-v1-20261004:refs/remotes/origin/gold-h3-llrs-v1-20261004"],
                       cwd=ROOT,check=True,capture_output=True,text=True,timeout=90)
        p=subprocess.run(["git","show",f"{ref}:{path}"],cwd=ROOT,check=True,capture_output=True,text=True,timeout=90)
        d=pd.read_csv(io.StringIO(p.stdout))
        d["ts"]=pd.to_datetime(d["ts"],utc=True)
        return d
    except Exception:
        return None

def bridge_stats(candidate: pd.DataFrame, frozen: pd.DataFrame | None, col: str):
    if candidate is None or candidate.empty or frozen is None or col not in frozen.columns:
        return {"overlap_n":0,"return_corr":None,"sign_agreement":None,"median_abs_return_diff_bps":None}
    a=candidate[["ts","close"]].copy().sort_values("ts")
    f=frozen[["ts",col]].copy().dropna().sort_values("ts")
    z=f.merge(a,on="ts",how="inner")
    if len(z)<3:
        return {"overlap_n":int(len(z)),"return_corr":None,"sign_agreement":None,"median_abs_return_diff_bps":None}
    z["rf"]=np.log(z[col].astype(float)).diff()
    z["rc"]=np.log(z.close.astype(float)).diff()
    q=z.dropna(subset=["rf","rc"])
    if len(q)<2:
        return {"overlap_n":int(len(z)),"return_corr":None,"sign_agreement":None,"median_abs_return_diff_bps":None}
    return {
        "overlap_n":int(len(q)),
        "return_corr":float(q.rf.corr(q.rc)),
        "sign_agreement":float((np.sign(q.rf)==np.sign(q.rc)).mean()),
        "median_abs_return_diff_bps":float(np.median(np.abs(q.rf-q.rc))*10000.0),
    }

def public_dict(x):
    return {k:v for k,v in x.items() if k!="_df"}

def main():
    result={
        "schema":"GOLD_H3_EXISTING_API_FUTURES_RECOVERY_PROBE_V2",
        "date":"2026-10-05",
        "purpose":"Test existing API stack for exact 1h historical GC/SI/NQ/ZN/CL recovery before licensed-source purchase.",
        "raw_market_values_logged":False,
        "database_writes":False,
        "frozen_model_changed":False,
        "targets":{},
    }

    frozen=load_frozen_panel()
    result["frozen_panel_loaded"]=bool(frozen is not None)
    if frozen is not None:
        result["frozen_panel_first"]=str(frozen.ts.min())
        result["frozen_panel_last"]=str(frozen.ts.max())
        result["frozen_panel_rows"]=int(len(frozen))

    # One reference-data pull: useful for spot/commodity alternatives, but never mislabeled futures.
    comm=commodities()
    result["commodities_catalog"]={k:v for k,v in comm.items() if k!="rows"}
    comm_rows=comm["rows"]

    for target,spec in TARGETS.items():
        t={"name":spec["name"],"searches":[],"direct_tests":[],"commodity_proxy_candidates":[]}

        # Search by full instrument name, then retain every row carrying futures/CME-family evidence.
        discovered=[]
        for q in spec["searches"]:
            sr=search(q)
            compact=[]
            for row in sr["rows"]:
                txt=" ".join(str(v) for v in row.values()).lower()
                if any(w in txt for w in ["future","futures","cme","comex","nymex","cbot"]):
                    compact.append(row)
                    discovered.append(row)
            t["searches"].append({
                "query":q,"http":sr["http"],"status":sr["status"],"code":sr["code"],
                "message":sr["message"],"matching_rows":compact[:30],
                "total_rows":len(sr["rows"]),
            })

        # Direct symbol probes. Root symbol is tried with both expected exchange labels;
        # Yahoo and TradingView spellings are also tried without pretending they are valid Twelve identifiers.
        candidates=[]
        for sym in spec["direct_symbols"]:
            if sym==spec["direct_symbols"][0]:
                for ex in dict.fromkeys([spec["exchange_primary"],spec["exchange_alt"]]):
                    candidates.append((sym,ex))
            else:
                candidates.append((sym,None))
        # add any discovered futures-like identifiers, capped
        for row in discovered[:3]:
            pair=(row.get("symbol"),row.get("exchange"))
            if pair[0] and pair not in candidates:
                candidates.append(pair)

        successful_exact=[]
        for sym,ex in candidates[:6]:
            p25=test_timeseries(sym,ex,"2025-07-01","2025-07-15")
            rec={
                "symbol":sym,"exchange_request":ex,
                "classification":classify_meta(p25["meta"],target),
                "test_2025":public_dict(p25),
            }
            if p25["n"]>0:
                p23=test_timeseries(sym,ex,"2023-06-01","2023-06-08")
                rec["test_2023"]=public_dict(p23)
                rec["bridge_2025"]=bridge_stats(p25["_df"],frozen,target)
                if rec["classification"]=="POSSIBLE_EXACT_FUTURES":
                    successful_exact.append(rec)
            t["direct_tests"].append(rec)

        # Commodity catalog analogs: recorded as PROXY ONLY.
        terms=spec["proxy_terms"]
        prox=[]
        for row in comm_rows:
            txt=" ".join(str(v) for v in row.values()).lower()
            if any(term in txt for term in terms):
                prox.append(row)
        t["commodity_proxy_candidates"]=prox[:20]

        # At most one likely commodity proxy per target is tested to establish 2023 1h depth.
        proxy_test=None
        if prox:
            row=prox[0]
            psym=row.get("symbol")
            if psym:
                p23=test_timeseries(psym,"Commodity","2023-06-01","2023-06-08")
                proxy_test={"catalog_row":row,"test_2023":public_dict(p23),"status":"PROXY_ONLY_NOT_DPTC_EXACT"}
        t["commodity_proxy_test"]=proxy_test

        exact_2023=[x for x in t["direct_tests"]
                    if x.get("classification")=="POSSIBLE_EXACT_FUTURES"
                    and (x.get("test_2023") or {}).get("n",0)>0]
        t["exact_2023_available"]=bool(exact_2023)
        result["targets"][target]=t

    exact=[k for k,v in result["targets"].items() if v["exact_2023_available"]]
    result["exact_2023_channels"]=exact
    result["exact_2023_complete_five_channel_panel"]=len(exact)==5
    result["conclusion"]=(
        "EXACT_2023_FIVE_CHANNEL_RECOVERY_AVAILABLE"
        if len(exact)==5 else
        "EXACT_2023_FIVE_CHANNEL_RECOVERY_NOT_ESTABLISHED_FROM_EXISTING_TWELVE_API"
    )

    # strip any private dfs
    OUTJ.write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")

    lines=[
        "# GOLD H3 — Existing API Futures Recovery Probe V2","",
        f"**Conclusion:** **{result['conclusion']}**  ",
        f"Frozen Yahoo LLRS panel loaded for bridge check: **{result['frozen_panel_loaded']}**.  ",
        "**Governance:** no model rules changed; no database writes; raw vendor market values are not logged.","",
        "## Exact futures recovery","",
        "| Channel | 2023 exact 1h established? | Best direct 2025 result | 2023 result | Bridge evidence |",
        "|---|---|---|---|---|"
    ]
    for target,t in result["targets"].items():
        best=None
        for x in t["direct_tests"]:
            if x["test_2025"]["n"]>0:
                best=x; break
        if best is None:
            a="No successful direct 1h identity"
            b="—"; c="—"
        else:
            m=best["test_2025"].get("meta") or {}
            a=f"{best['symbol']} @ {best.get('exchange_request') or '-'}; n={best['test_2025']['n']}; meta={m}"
            b=f"n={(best.get('test_2023') or {}).get('n',0)}"
            bs=best.get("bridge_2025") or {}
            c=f"overlap={bs.get('overlap_n',0)}, corr={bs.get('return_corr')}, sign={bs.get('sign_agreement')}"
        lines.append(f"| {target} | **{t['exact_2023_available']}** | {a} | {b} | {c} |")

    lines += ["","## Commodity alternatives (not exact futures)","",
              "| Channel | Catalog candidates found | 2023 1h proxy test | Status |",
              "|---|---:|---|---|"]
    for target,t in result["targets"].items():
        pt=t.get("commodity_proxy_test")
        if pt:
            p=pt["test_2023"]
            desc=f"{pt['catalog_row'].get('symbol')} n={p.get('n',0)} meta={p.get('meta')}"
        else:
            desc="—"
        lines.append(f"| {target} | {len(t['commodity_proxy_candidates'])} | {desc} | PROXY ONLY |")

    lines += ["","## Interpretation","",
              "- A Twelve Data series is called **exact futures** only if returned metadata itself identifies the intended futures instrument; a similarly named equity/ETF/commodity is rejected.",
              "- Commodity/index proxies may have deep 1h history, but they are not allowed to silently replace GC/SI/NQ/ZN/CL in the frozen DPTC lineage.",
              "- If all five exact channels are not established, the next step is to audit other already-connected/public source routes rather than retune DPTC on proxy data."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
