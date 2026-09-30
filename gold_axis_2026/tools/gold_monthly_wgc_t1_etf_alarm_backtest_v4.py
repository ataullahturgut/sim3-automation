from __future__ import annotations
import argparse, json, time
from pathlib import Path
import pandas as pd

import gold_monthly_wgc_t1_etf_alarm_backtest_v3 as v3

EVAL_START="2021-11"
EVAL_END="2026-08"
FETCH_START="2021-10"
FETCH_END="2026-08"

MANUAL_OVERRIDES={
    "2021-12":{
        "page_month":"2021-12",
        "data_month":"2021-11",
        "url":"https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2021/12",
        "status":200,
        "publication_date":"2021-12-07",
        "global_direction":1,
        "direction_confidence":1.0,
        "direction_detail":{
            "kind":"manual_authority_override",
            "snippet":"Gold-backed ETFs experienced net inflows of 13.6 tonnes in November, the first month of positive flows since July.",
            "reason":"Official WGC page is unambiguous; automatic parser did not extract this historical template."
        },
        "slowdown_note":False,
        "slowdown_detail":None,
        "manual_override":True,
    }
}

def load_severity(path):
    j=json.loads(Path(path).read_text())
    if j.get("schema")!="GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30":
        raise RuntimeError(("BAD_SEVERITY_SCHEMA",j.get("schema")))
    return {r["target"]:r for r in j["rows"]}

def score(rows,timely=False):
    z=[r for r in rows if r.get("severity") is not None]
    ev=[r for r in z if r["R2_WGC"] and (not timely or r["TIMELY_T1"])]
    hi=[r for r in z if r["severity"]=="HIGH"]
    elev=[r for r in z if r["severity"] in ("MEDIUM","HIGH")]
    hh=[r for r in ev if r["severity"]=="HIGH"]
    eh=[r for r in ev if r["severity"] in ("MEDIUM","HIGH")]
    return {
        "events":len(ev),
        "event_targets":[r["page_month"] for r in ev],
        "event_publication_dates":{r["page_month"]:r["publication_date"] for r in ev},
        "high_n":len(hi),
        "high_hits":len(hh),
        "high_hit_targets":[r["page_month"] for r in hh],
        "high_precision":None if not ev else len(hh)/len(ev),
        "high_recall":None if not hi else len(hh)/len(hi),
        "elevated_n":len(elev),
        "elevated_hits":len(eh),
        "elevated_hit_targets":[r["page_month"] for r in eh],
        "elevated_precision":None if not ev else len(eh)/len(ev),
        "elevated_recall":None if not elev else len(eh)/len(elev),
        "normal_false_alarm_targets":[r["page_month"] for r in ev if r["severity"]=="NORMAL"],
        "medium_hit_targets":[r["page_month"] for r in ev if r["severity"]=="MEDIUM"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--severity",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    sev=load_severity(a.severity)

    raw=[]
    for ym in v3.mrange(FETCH_START,FETCH_END):
        r=v3.fetch(ym)
        if ym in MANUAL_OVERRIDES:
            auto=dict(r)
            r=dict(MANUAL_OVERRIDES[ym])
            r["automatic_parse_before_override"]=auto
        else:
            r["manual_override"]=False
        raw.append(r)
        time.sleep(.03)

    parsed=[r for r in raw if r.get("publication_date") and r.get("global_direction") in (-1,1)]
    by_data={r["data_month"]:r for r in parsed}
    rows=sorted(parsed,key=lambda r:r["publication_date"])

    for r in rows:
        prev=by_data.get(v3.mshift(r["data_month"],-1))
        r["prev_global_direction"]=None if prev is None else prev.get("global_direction")
        r["R2_WGC"]=bool(r["global_direction"]==-1 and r["prev_global_direction"]==-1)
        ts=pd.Timestamp(r["publication_date"])
        r["publication_matches_target_month"]=bool(ts.strftime("%Y-%m")==r["page_month"])
        r["publish_day"]=int(ts.day)
        r["TIMELY_T1"]=bool(r["publication_matches_target_month"] and r["publish_day"]<=10)
        s=sev.get(r["page_month"])
        if s:
            r["ape_pct"]=float(s["ape_pct"])
            r["severity"]=s["ape_severity"]
            r["ABCDH"]=bool(s["ABCDH"])
        else:
            r["ape_pct"]=None
            r["severity"]=None
            r["ABCDH"]=None

    expected=v3.mrange(EVAL_START,EVAL_END)
    eval_rows=[r for r in rows if EVAL_START<=r["page_month"]<=EVAL_END and r.get("severity") is not None]
    have={r["page_month"] for r in eval_rows}
    missing=[m for m in expected if m not in have]

    manual_eval=[r for r in eval_rows if r.get("manual_override")]
    if [r["page_month"] for r in manual_eval] != ["2021-12"]:
        raise RuntimeError(("MANUAL_OVERRIDE_REGISTRY_MISMATCH",[r["page_month"] for r in manual_eval]))

    bad_pub=[r["page_month"] for r in eval_rows if not r["publication_matches_target_month"]]
    bad_data=[r["page_month"] for r in eval_rows if r["data_month"]!=v3.mshift(r["page_month"],-1)]

    met=score(eval_rows,False)
    timely=score(eval_rows,True)

    high=[r for r in eval_rows if r["severity"]=="HIGH"]
    t0_hits=[r for r in high if r["ABCDH"]]
    t1_hits=[r for r in high if r["R2_WGC"]]
    incremental=[r for r in high if (not r["ABCDH"]) and r["R2_WGC"]]
    union=[r for r in high if r["ABCDH"] or r["R2_WGC"]]
    remaining=[r for r in high if not (r["ABCDH"] or r["R2_WGC"])]

    core_targets=["2022-05","2022-07","2022-09","2024-03"]
    core=[]
    for t in core_targets:
        r=next(x for x in eval_rows if x["page_month"]==t)
        core.append({k:r.get(k) for k in [
            "page_month","data_month","publication_date","publish_day",
            "global_direction","prev_global_direction","R2_WGC","TIMELY_T1",
            "slowdown_note","slowdown_detail","ape_pct","severity","ABCDH",
            "direction_detail","manual_override"
        ]})

    status="COMPLETE" if (
        len(eval_rows)==58 and not missing and not bad_pub and not bad_data and
        len(manual_eval)==1 and manual_eval[0]["page_month"]=="2021-12"
    ) else "INCOMPLETE"

    out={
        "schema":"GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V4_2026-09-30",
        "status":status,
        "evaluation_window":[EVAL_START,EVAL_END],
        "evaluation_authority":{
            "expected_rows":58,
            "available_rows":len(eval_rows),
            "coverage":len(eval_rows)/58.0,
            "missing":missing,
            "bad_publication_month":bad_pub,
            "bad_data_month":bad_data,
            "manual_override_targets":[r["page_month"] for r in manual_eval],
        },
        "manual_override_registry":MANUAL_OVERRIDES,
        "rows":rows,
        "raw_page_status":raw,
        "metrics_all":met,
        "metrics_timely":timely,
        "core_rows":core,
        "t0_t1_high_coverage":{
            "high_n":len(high),
            "t0_ABCDH_hits":len(t0_hits),
            "t0_ABCDH_hit_targets":[r["page_month"] for r in t0_hits],
            "t0_ABCDH_recall":len(t0_hits)/len(high),
            "t1_R2_hits":len(t1_hits),
            "t1_R2_hit_targets":[r["page_month"] for r in t1_hits],
            "t1_incremental_hits_over_T0":len(incremental),
            "t1_incremental_hit_targets":[r["page_month"] for r in incremental],
            "union_hits":len(union),
            "union_hit_targets":[r["page_month"] for r in union],
            "union_recall":len(union)/len(high),
            "remaining_high_misses":[r["page_month"] for r in remaining],
        },
        "governance":{
            "forecast_modified":False,
            "routing_tested":False,
            "numeric_threshold_used":False,
            "r2_fixed_two_consecutive_outflow_reports":True,
            "severity_ape_v3":True,
            "target_month_market_data_used":False,
            "evaluation_complete_58_of_58":len(eval_rows)==58 and not missing,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE="+("PASS" if status=="COMPLETE" else "FAIL"))
    print(json.dumps({
        "authority":out["evaluation_authority"],
        "metrics_all":met,
        "metrics_timely":timely,
        "coverage":out["t0_t1_high_coverage"],
        "core":core,
    },sort_keys=True))

if __name__=="__main__":
    main()
