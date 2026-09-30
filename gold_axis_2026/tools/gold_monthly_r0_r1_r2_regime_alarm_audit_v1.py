from __future__ import annotations
import argparse,json
from pathlib import Path

SIGNALS=["A","B","C","D","E","G","H","I1","I2","T1_WGC"]
UNIONS=["T0_STANDARD","ANY_VISIBLE"]
REGIMES=["R0","R1","R2"]

def load(p):
    return json.loads(Path(p).read_text())

def summarize(rows,flag):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in ev if r["severity"]=="HIGH"]
    med=[r for r in ev if r["severity"]=="MEDIUM"]
    norm=[r for r in ev if r["severity"]=="NORMAL"]
    allhi=[r for r in rows if r["severity"]=="HIGH"]
    allelev=[r for r in rows if r["severity"] in ("HIGH","MEDIUM")]
    return {
        "events":len(ev),
        "high_hits":len(hi),
        "medium_hits":len(med),
        "false_calls":len(norm),
        "false_call_rate":None if not ev else len(norm)/len(ev),
        "useful_call_rate":None if not ev else (len(hi)+len(med))/len(ev),
        "high_recall":None if not allhi else len(hi)/len(allhi),
        "elevated_recall":None if not allelev else (len(hi)+len(med))/len(allelev),
        "high_hit_targets":[r["target"] for r in hi],
        "medium_hit_targets":[r["target"] for r in med],
        "false_call_targets":[r["target"] for r in norm],
        "false_call_detail":[
            {"target":r["target"],"ape_pct":r["ape_pct"],"active_signals":r["active_signals"]}
            for r in norm
        ],
    }

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
        rr=rm.get(str(r["origin"]))
        if rr is None:
            raise RuntimeError(("REGIME_MISSING_FOR_ORIGIN",r["target"],r["origin"]))
        r["origin_regime_state"]=rr["state"]
        r["origin_regime_probability"]=float(rr["state_probability"])
        r["origin_regime_ood"]=bool(rr["ood_below_train_p05"])
        r["origin_regime_confident"]=bool(
            rr["state_probability"]>=0.60 and not rr["ood_below_train_p05"]
        )
        rows.append(r)
    if len(rows)!=58:
        raise RuntimeError(("JOINED_ROWS",len(rows)))

    primary={}
    sensitivity={}
    for rg in REGIMES:
        conf=[r for r in rows if r["origin_regime_state"]==rg and r["origin_regime_confident"]]
        raw=[r for r in rows if r["origin_regime_state"]==rg]
        primary[rg]=pack(conf)
        sensitivity[rg]=pack(raw)

    comparison={}
    for rg in REGIMES:
        p=primary[rg]
        comparison[rg]={
            "n_targets":p["n_targets"],
            "high_n":len(p["high_targets"]),
            "medium_n":len(p["medium_targets"]),
            "normal_n":len(p["normal_targets"]),
            "any_visible_high_recall":p["stats"]["ANY_VISIBLE"]["high_recall"],
            "any_visible_false_call_rate":p["stats"]["ANY_VISIBLE"]["false_call_rate"],
            "any_visible_events":p["stats"]["ANY_VISIBLE"]["events"],
            "any_visible_false_calls":p["stats"]["ANY_VISIBLE"]["false_calls"],
            "t0_standard_high_recall":p["stats"]["T0_STANDARD"]["high_recall"],
            "t0_standard_false_call_rate":p["stats"]["T0_STANDARD"]["false_call_rate"],
            "t0_standard_events":p["stats"]["T0_STANDARD"]["events"],
            "t0_standard_false_calls":p["stats"]["T0_STANDARD"]["false_calls"],
        }

    per_signal_compare={}
    for s in SIGNALS:
        per_signal_compare[s]={}
        for rg in REGIMES:
            q=primary[rg]["stats"][s]
            per_signal_compare[s][rg]={
                "events":q["events"],
                "high_hits":q["high_hits"],
                "medium_hits":q["medium_hits"],
                "false_calls":q["false_calls"],
                "false_call_rate":q["false_call_rate"],
                "useful_call_rate":q["useful_call_rate"],
                "high_recall":q["high_recall"],
            }

    out={
        "schema":"GOLD_MONTHLY_R0_R1_R2_REGIME_ALARM_AUDIT_V1_2026-09-30",
        "status":"COMPLETE",
        "primary_confident_regimes":primary,
        "sensitivity_raw_regimes":sensitivity,
        "comparison":comparison,
        "per_signal_comparison":per_signal_compare,
        "rows":rows,
        "governance":{
            "regime_conditioned_on_origin_month":True,
            "posterior_floor":0.60,
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
        "comparison":comparison,
        "R0":primary["R0"],
        "R1":primary["R1"],
        "R2":primary["R2"],
        "per_signal_comparison":per_signal_compare,
        "sensitivity_R2":sensitivity["R2"],
    },sort_keys=True))

if __name__=="__main__":
    main()
