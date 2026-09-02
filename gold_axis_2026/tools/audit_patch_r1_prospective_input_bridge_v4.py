from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"patch_repro_v1"
CONTRACT=ROOT/"GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V4.md"
CC=ROOT/"GOLD_CONTROL_CAUSAL_PATCH_R1_INPUT_SOURCE_CHANGE_CONTROL_V4_2026-09-02.md"
V1=OUT/"prospective_input_bridge_v1_evidence.json"
V3=OUT/"prospective_input_bridge_v3_source_evidence.json"
URL="https://api.twelvedata.com/time_series"


def key():
    v=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not v: raise RuntimeError("TWELVE_DATA_API_KEY_NOT_SET")
    return v


def inherit():
    a=json.loads(V1.read_text(encoding="utf-8"))
    b=json.loads(V3.read_text(encoding="utf-8"))
    fed=a["macro_audit"]["series"]["fedfunds"]
    fx=a["macro_audit"]["series"]["usdcny"]
    nas=b["nasdaq_source_identity_availability"]
    return {
      "fedfunds_pass":bool(fed.get("pass")),
      "usdcny_pass":bool(fx.get("pass")),
      "nasdaq_v3_pass":bool(nas.get("pass")),
      "nasdaq_common_months":nas.get("common_months"),
      "nasdaq_locked_inputs_checked":nas.get("locked_completed_month_inputs_checked"),
      "nasdaq_availability_violations":len(nas.get("availability_violations") or []),
    }


def xau_audit():
    r=requests.get(URL,params={"symbol":"XAU/USD","interval":"1day","start_date":"2010-01-01","end_date":"2026-08-31","outputsize":5000,"order":"ASC","format":"JSON"},headers={"Authorization":f"apikey {key()}","User-Agent":"Gold-Control-Patch-V4-XAU-Source-Audit/1.0"},timeout=(20,150))
    r.raise_for_status()
    p=r.json()
    if isinstance(p,dict) and p.get("status")=="error": raise RuntimeError(f"TWELVE_ERROR:{p.get('code')}:{p.get('message')}")
    meta=p.get("meta") or {}
    vals=p.get("values") or []
    rows=[]
    for z in vals:
        try:
            d=pd.Timestamp(str(z.get("datetime"))).normalize(); v=float(z.get("close"))
        except Exception: continue
        if np.isfinite(v) and v>0: rows.append((d,v))
    d=pd.DataFrame(rows,columns=["date","close"]).sort_values("date")
    dup=int(d.duplicated("date").sum()) if not d.empty else 0
    total=int(len(d)); pre=int((d.date<=pd.Timestamp("2011-02-28")).sum()) if total else 0
    first=None if not total else d.date.min().date().isoformat(); last=None if not total else d.date.max().date().isoformat()
    passed=bool(meta.get("symbol")=="XAU/USD" and meta.get("interval")=="1day" and dup==0 and pre>=253 and total>=3500 and d.date.max()>=pd.Timestamp("2026-08-28"))
    return {"lineage":"PATCH_XAU_TWELVE_DAILY_FULL_HISTORY_V4","symbol":meta.get("symbol"),"interval":meta.get("interval"),"type":meta.get("type"),"rows":total,"first_date":first,"last_date":last,"rows_through_2011_02_28":pre,"pre_origin_gate":253,"total_rows_gate":3500,"recent_gate_date":"2026-08-28","duplicates":dup,"pass":passed,"raw_values_logged":False}


def main():
    if "FROZEN_BEFORE_V4_SOURCE_RESULT" not in CONTRACT.read_text(encoding="utf-8"): raise RuntimeError("V4_CONTRACT_NOT_FROZEN")
    if "FROZEN_BEFORE_V4_SOURCE_RESULT" not in CC.read_text(encoding="utf-8"): raise RuntimeError("V4_CHANGE_CONTROL_NOT_FROZEN")
    inh=inherit(); x=xau_audit()
    passed=bool(x["pass"] and inh["fedfunds_pass"] and inh["usdcny_pass"] and inh["nasdaq_v3_pass"] and inh["nasdaq_locked_inputs_checked"]==86 and inh["nasdaq_availability_violations"]==0)
    decision="PATCH_PROSPECTIVE_INPUT_BRIDGE_V4_SOURCE_PASS" if passed else "BLOCKED_PATCH_PROSPECTIVE_INPUT_V4_SOURCE_NOT_PROVEN"
    e={"contract":CONTRACT.name,"change_control":CC.name,"candidate_architecture":"CAUSAL_PATCH_R1_REPRO_V1","reserved_identity_after_model_impact_only":"CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE","evidence_class":"INPUT_SOURCE_READINESS_AUDIT","prospective_claim":False,"geometry_changed":False,"geometry":{"L":252,"P":21,"D":32},"daily_channels":["XAU"],"omitted_not_imputed":["XAG","XPT","XPD"],"inherited_source_proof":inh,"xau_source":x,"source_bridge_pass":passed,"decision":decision,"forecast_ledger_write":"NONE","decision_store_write":"NONE","database_write":"NONE","raw_vendor_market_values_logged":False}
    OUT.mkdir(exist_ok=True)
    (OUT/"prospective_input_bridge_v4_source_evidence.json").write_text(json.dumps(e,indent=2),encoding="utf-8")
    print(f"V4_XAU_ROWS={x['rows']}"); print(f"V4_XAU_PRE_ORIGIN_ROWS={x['rows_through_2011_02_28']}"); print(f"V4_XAU_FIRST_DATE={x['first_date']}"); print(f"V4_XAU_LAST_DATE={x['last_date']}"); print(f"V4_XAU_SOURCE_PASS={str(x['pass']).lower()}")
    print(f"V4_NASDAQ_V3_INHERITED_PASS={str(inh['nasdaq_v3_pass']).lower()}"); print(f"V4_FEDFUNDS_INHERITED_PASS={str(inh['fedfunds_pass']).lower()}"); print(f"V4_USDCNY_INHERITED_PASS={str(inh['usdcny_pass']).lower()}")
    print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V4_SOURCE_PASS={str(passed).lower()}"); print(f"PATCH_PROSPECTIVE_INPUT_BRIDGE_V4_DECISION={decision}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO"); print("DATABASE_WRITES=NONE"); print("FORECAST_LEDGER_WRITE=NONE"); print("DECISION_STORE_WRITE=NONE")

if __name__=="__main__": main()
