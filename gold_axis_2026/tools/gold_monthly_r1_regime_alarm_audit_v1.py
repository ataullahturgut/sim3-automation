from __future__ import annotations
import argparse,json
from pathlib import Path

SIGNALS=["A","B","C","D","E","G","H","I1","I2","T1_WGC"]
UNIONS=["T0_STANDARD","ANY_VISIBLE"]

def load(p):
    return json.loads(Path(p).read_text())

def summarize(rows,flag):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in ev if r["severity"]=="HIGH"]
    med=[r for r in ev if r["severity"]=="MEDIUM"]
    norm=[r for r in ev if r["severity"]=="NORMAL"]
    allhi=[r for r in rows if r["severity"]=="HIGH"]
    return {
        "events":len(ev),
        "high_hits":len(hi),
        "medium_hits":len(med),
        "false_calls":len(norm),
        "false_call_rate":None if not ev else len(norm)/len(ev),
        "useful_call_rate":None if not ev else (len(hi)+len(med))/len(ev),
        "high_recall":None if not allhi else len(hi)/len(allhi),
        "high_hit_targets":[r["target"] for r in hi],
        "medium_hit_targets":[r["target"] for r in med],
        "false_call_targets":[r["target"] for r in norm],
        "false_call_detail":[{"target":r["target"],"ape_pct":r["ape_pct"],"active_signals":r["active_signals"]} for r in norm],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--regime",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    mat=load(a.matrix)
    reg=load(a.regime)
    if mat.get("schema")!="GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_2026-09-30":
        raise RuntimeError(("BAD_MATRIX_SCHEMA",mat.get("schema")))
    if reg.get("schema")!="GOLD_MONTHLY_MARKET_REGIME_DISCOVERY_V1_2026-09-30":
        raise RuntimeError(("BAD_REGIME_SCHEMA",reg.get("schema")))

    rm={r["month"]:r for r in reg["monthly_regimes"]}
    rows=[]
    for r0 in mat["rows"]:
        r=dict(r0)
        origin=str(r["origin"])
        rr=rm.get(origin)
        if rr is None:
            r["origin_regime_available"]=False
            continue
        r["origin_regime_available"]=True
        r["origin_regime_state"]=rr["state"]
        r["origin_regime_probability"]=float(rr["state_probability"])
        r["origin_regime_ood"]=bool(rr["ood_below_train_p05"])
        r["origin_regime_confident_r1"]=bool(
            rr["state"]=="R1" and
            rr["state_probability"]>=0.60 and
            not rr["ood_below_train_p05"]
        )
        r["origin_regime_raw_r1"]=bool(rr["state"]=="R1")
        rows.append(r)

    if len(rows)!=58:
        raise RuntimeError(("JOINED_ROWS",len(rows)))

    confident=[r for r in rows if r["origin_regime_confident_r1"]]
    raw=[r for r in rows if r["origin_regime_raw_r1"]]

    def pack(subset):
        stats={s:summarize(subset,s) for s in SIGNALS+UNIONS}
        return {
            "n_targets":len(subset),
            "targets":[r["target"] for r in subset],
            "origin_months":[r["origin"] for r in subset],
            "high_targets":[r["target"] for r in subset if r["severity"]=="HIGH"],
            "medium_targets":[r["target"] for r in subset if r["severity"]=="MEDIUM"],
            "normal_targets":[r["target"] for r in subset if r["severity"]=="NORMAL"],
            "high_no_visible_alarm":[r["target"] for r in subset if r["severity"]=="HIGH" and not r["ANY_VISIBLE"]],
            "stats":stats,
        }

    out={
        "schema":"GOLD_MONTHLY_R1_REGIME_ALARM_AUDIT_V1_2026-09-30",
        "status":"COMPLETE",
        "primary_confident_r1":pack(confident),
        "sensitivity_raw_r1":pack(raw),
        "rows":rows,
        "governance":{
            "regime_conditioned_on_origin_month":True,
            "r1_probability_floor":0.60,
            "ood_excluded_from_primary":True,
            "alarm_definitions_changed":False,
            "alarm_selection_performed":False,
            "threshold_tuning_performed":False,
            "forecast_modified":False,
            "routing_tested":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "primary_confident_r1":out["primary_confident_r1"],
        "sensitivity_raw_r1":out["sensitivity_raw_r1"],
    },sort_keys=True))

if __name__=="__main__":
    main()
