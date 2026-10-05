from __future__ import annotations
import json, os, tempfile
from pathlib import Path
import requests
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"OCT5_DIAGNOSTIC_NOWCAST_OUT"
OUT.mkdir(exist_ok=True)

# Required before importing the frozen prospective harness.
os.environ.setdefault("STAK_LIVE_REF","54fdf1c8d39b7b6c7b874d0f30f784296e886044")

import gold_h3_aurora_prospective_v1 as base
import gold_h3_clean_aurora_prospective_v1 as clean
import gold_h3_clean_v5_prospective_v1 as cv5

START=pd.Timestamp("2026-09-30")
END=pd.Timestamp("2026-10-02")
ORIGIN=pd.Timestamp("2026-10-02")
SYMS={"gold":"XAU/USD","silver":"XAG/USD","platinum":"XPT/USD","palladium":"XPD/USD"}

def td_daily(symbol):
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key: raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    params={"symbol":symbol,"interval":"1day","start_date":str(START.date()),"end_date":"2026-10-03",
            "timezone":"America/New_York","apikey":key,"outputsize":20,"format":"JSON"}
    r=requests.get("https://api.twelvedata.com/time_series",params=params,timeout=60)
    r.raise_for_status()
    j=r.json()
    if "values" not in j:
        raise RuntimeError(f"TWELVE_{symbol}_FAIL {j}")
    rows=[]
    for x in j["values"]:
        d=pd.to_datetime(x.get("datetime"),errors="coerce")
        try: c=float(x.get("close"))
        except Exception: continue
        if pd.notna(d) and np.isfinite(c) and c>0:
            rows.append((d.normalize(),c))
    return dict(rows)

def build_alt_prices():
    maps={k:td_daily(v) for k,v in SYMS.items()}
    common=sorted(set.intersection(*(set(m.keys()) for m in maps.values())))
    common=[d for d in common if START<=d<=END]
    if ORIGIN not in common:
        raise RuntimeError(f"NO_COMMON_ORIGIN_{ORIGIN.date()} common={common}")
    rows=[]
    for d in common:
        rows.append({"date":d,**{k:maps[k][d] for k in SYMS},
                     "first_seen_stak_ref":"TWELVE_DATA_DIAGNOSTIC_ONLY",
                     "first_seen_at_utc":pd.Timestamp.now(tz="UTC").isoformat()})
    return pd.DataFrame(rows).sort_values("date")

def run():
    alt=build_alt_prices()
    alt.to_csv(OUT/"ALT_DAILY_PRICES.csv",index=False)

    # Configure the CLEAN frozen model, but permit 2026-10-02 solely for this
    # diagnostic nowcast. This is explicitly NOT prospective evidence.
    clean.OUT=OUT
    clean.configure()
    base.OUT=OUT
    base.PROSPECTIVE_MIN_FEATURE=ORIGIN

    price_path=OUT/"DIAG_PRICE_LEDGER.csv"
    forecast_path=OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_LEDGER.csv"
    miss_path=OUT/"DIAG_AURORA_MISSES.csv"
    integ_path=OUT/"DIAG_INTEGRITY.csv"
    alt.to_csv(price_path,index=False)

    base.PRICE_LEDGER_FILE=price_path
    base.FORECAST_LEDGER_FILE=forecast_path
    base.MISS_LEDGER_FILE=miss_path
    base.INTEGRITY_LEDGER_FILE=integ_path

    base.main()
    a=pd.read_csv(forecast_path)
    a["feature_cutoff_date"]=pd.to_datetime(a.feature_cutoff_date,errors="coerce")
    ar=a[a.feature_cutoff_date==ORIGIN]
    if len(ar)!=1:
        raise RuntimeError(f"AURORA_ORIGIN_ROW_FAIL n={len(ar)}")
    ar=ar.iloc[0]

    # Run the frozen CLEAN V5-DCE chain on the same diagnostic AURORA row.
    cv5.OUT=OUT
    cv5.AURORA_LEDGER=forecast_path
    cv5.V5_LEDGER=OUT/"DIAG_V5_LEDGER.csv"
    cv5.V5_MISSES=OUT/"DIAG_V5_MISSES.csv"
    cv5.FIRST_FEATURE=ORIGIN
    cv5.main()
    v=pd.read_csv(OUT/"DIAG_V5_LEDGER.csv")
    v["feature_cutoff_date"]=pd.to_datetime(v.feature_cutoff_date,errors="coerce")
    vr=v[v.feature_cutoff_date==ORIGIN]
    if len(vr)!=1:
        raise RuntimeError(f"V5_ORIGIN_ROW_FAIL n={len(vr)}")
    vr=vr.iloc[0]

    out={
      "status":"DIAGNOSTIC_ONLY_NOT_PROSPECTIVE_EVIDENCE",
      "feature_cutoff_date":"2026-10-02",
      "planned_issue_date":"2026-10-05",
      "alt_source":"TwelveData daily spot for 2026-09-30..2026-10-02",
      "alt_prices":alt.assign(date=alt.date.dt.strftime("%Y-%m-%d")).to_dict("records"),
      "aurora":{
        "p_up":float(ar.p_aurora),
        "direction":str(ar.direction),
        "active_expert":str(ar.active_expert),
        "p_structural":float(ar.p_structural),
        "p_path_global":float(ar.p_path_global),
        "h_ret_12":float(ar.h_ret_12),
        "h_ret_24":float(ar.h_ret_24),
        "h_ret_48":float(ar.h_ret_48),
      },
      "v5":{
        "p_up":float(vr.p_clean_v5),
        "direction":str(vr.v5_direction),
        "aurora_direction":str(vr.aurora_direction),
        "changed_from_aurora":bool(vr.changed_from_aurora),
        "candidate_reversal":bool(vr.candidate_reversal),
        "opal_override":bool(vr.opal_override),
        "p_opal_reversal":float(vr.p_opal_reversal),
        "gt_flip_share":float(vr.gt_flip_share),
        "v4_route":bool(vr.v4_route),
        "rge_active":bool(vr.rge_active),
        "dce_exception":bool(vr.dce_exception),
      }
    }
    (OUT/"OCT5_DIAGNOSTIC_NOWCAST.json").write_text(json.dumps(out,indent=2,default=str)+"\n")
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__":
    run()
