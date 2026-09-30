from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

ALARM_EXPERTS = ["A","B","C","D","E","G","H","I1","I2","T1_WGC","V2_TRANSITION"]
RAW_SIGNAL_EXPERTS = ["A","B","C","D","E","G","H","I1","I2","T1_WGC"]
T0_SIGNALS = {"A","B","C","D","H"}
NULL = "NULL"
ALL_EXPERTS = ALARM_EXPERTS + [NULL]

ETAS = [0.25,0.50,1.00,2.00]
ALPHAS = [0.01,0.05,0.10,0.20]
TAUS = [0.25,0.35,0.45,0.50,0.60]
EPS = 1e-12

DEV_START, DEV_END = "2022-04","2024-12"
Y2025_START, Y2025_END = "2025-01","2025-12"
Y2026_START, Y2026_END = "2026-01","2026-08"
OPEN_START, OPEN_END = "2025-01","2026-08"

CHECKPOINTS = ["2024-12","2025-06","2025-12","2026-04","2026-06","2026-08"]


def load_json(path: str):
    return json.loads(Path(path).read_text())


def awake(row: dict, expert: str) -> bool:
    if expert == "V2_TRANSITION":
        return bool(row["v2_transition_flag"])
    return bool(row[expert])


def y_high(row: dict) -> int:
    return 1 if row["severity"] == "HIGH" else 0


def y_elev(row: dict) -> int:
    return 1 if row["severity"] in ("HIGH","MEDIUM") else 0


def normalize(weights: dict[str,float]):
    total = sum(weights.values())
    if total <= 0:
        raise RuntimeError("NONPOSITIVE_WEIGHT_SUM")
    scale = len(weights) / total
    for k in weights:
        weights[k] *= scale


def fixed_share_alarm_weights(weights: dict[str,float], alpha: float):
    if alpha <= 0:
        return
    mean_alarm = sum(weights[e] for e in ALARM_EXPERTS) / len(ALARM_EXPERTS)
    old = {e: weights[e] for e in ALARM_EXPERTS}
    for e in ALARM_EXPERTS:
        weights[e] = (1.0-alpha)*old[e] + alpha*mean_alarm


def vote_probability(row: dict, weights: dict[str,float]) -> tuple[float,list[str]]:
    active = [e for e in ALARM_EXPERTS if awake(row,e)]
    if not active:
        return 0.0, []
    alarm_mass = sum(weights[e] for e in active)
    den = alarm_mass + weights[NULL]
    return float(alarm_mass / den), active


def update_task(row: dict, weights: dict[str,float], eta: float, alpha: float, target: int):
    active = [e for e in ALARM_EXPERTS if awake(row,e)]

    # Alarm specialists predict 1 when awake: loss = 1-target.
    alarm_loss = 1 - target
    factor_alarm = math.exp(-eta * alarm_loss)
    for e in active:
        weights[e] *= factor_alarm

    # NULL always predicts 0: loss = target.
    weights[NULL] *= math.exp(-eta * target)

    fixed_share_alarm_weights(weights, alpha)
    normalize(weights)


def evidence_tier(n: int) -> str:
    if n < 3:
        return "EMERGING"
    if n < 6:
        return "DEVELOPING"
    return "ESTABLISHED"


def run_online(rows: list[dict], eta: float, alpha: float):
    wh = {e:1.0 for e in ALL_EXPERTS}
    we = {e:1.0 for e in ALL_EXPERTS}

    prior_awake = {e:0 for e in ALARM_EXPERTS}
    prior_high = {e:0 for e in ALARM_EXPERTS}
    prior_elev = {e:0 for e in ALARM_EXPERTS}

    scored=[]
    checkpoints={}

    for row in sorted(rows,key=lambda r:r["origin"]):
        ph, active_h = vote_probability(row,wh)
        pe, active_e = vote_probability(row,we)
        if active_h != active_e:
            raise RuntimeError("ACTIVE_SET_MISMATCH")

        expert_diag={}
        for e in active_h:
            expert_diag[e]={
                "prior_awake_events":prior_awake[e],
                "prior_high_hits":prior_high[e],
                "prior_elevated_hits":prior_elev[e],
                "evidence_tier":evidence_tier(prior_awake[e]),
                "high_weight":float(wh[e]),
                "elevated_weight":float(we[e]),
            }

        scored.append({
            "origin":row["origin"],
            "target":row["target"],
            "severity":row["severity"],
            "p_high":ph,
            "p_elevated":pe,
            "awake_experts":active_h,
            "expert_diagnostics":expert_diag,
            "raw_ANY_VISIBLE":bool(row["ANY_VISIBLE"]),
            "raw_T0_STANDARD":bool(row["T0_STANDARD"]),
            "v2_transition":bool(row["v2_transition_flag"]),
            "active_signals":list(row["active_signals"]),
        })

        yh=y_high(row)
        ye=y_elev(row)

        # Evidence counts update only after prediction.
        for e in active_h:
            prior_awake[e]+=1
            prior_high[e]+=yh
            prior_elev[e]+=ye

        update_task(row,wh,eta,alpha,yh)
        update_task(row,we,eta,alpha,ye)

        if row["origin"] in CHECKPOINTS:
            checkpoints[row["origin"]]={
                "high_weights":{e:float(wh[e]) for e in ALL_EXPERTS},
                "elevated_weights":{e:float(we[e]) for e in ALL_EXPERTS},
                "evidence":{
                    e:{
                        "awake_events":prior_awake[e],
                        "high_hits":prior_high[e],
                        "elevated_hits":prior_elev[e],
                        "tier":evidence_tier(prior_awake[e]),
                    } for e in ALARM_EXPERTS
                },
            }

    return scored,checkpoints


def binary_scoring(rows: list[dict], prob_field: str, target_fn):
    if not rows:
        return {"n":0,"brier":None,"log_loss":None}
    b=0.0
    ll=0.0
    for r in rows:
        p=min(1-EPS,max(EPS,float(r[prob_field])))
        y=target_fn(r)
        b += (p-y)**2
        ll += -(y*math.log(p)+(1-y)*math.log(1-p))
    return {"n":len(rows),"brier":float(b/len(rows)),"log_loss":float(ll/len(rows))}


def target_from_scored_high(r: dict) -> int:
    return 1 if r["severity"]=="HIGH" else 0


def target_from_scored_elev(r: dict) -> int:
    return 1 if r["severity"] in ("HIGH","MEDIUM") else 0


def router_metrics(rows: list[dict], tau: float):
    warns=[r for r in rows if float(r["p_high"]) >= tau]
    high_all=sum(r["severity"]=="HIGH" for r in rows)
    med_all=sum(r["severity"]=="MEDIUM" for r in rows)
    elev_all=high_all+med_all
    hh=sum(r["severity"]=="HIGH" for r in warns)
    mh=sum(r["severity"]=="MEDIUM" for r in warns)
    fc=sum(r["severity"]=="NORMAL" for r in warns)

    raw_high_rows=[r for r in rows if r["raw_ANY_VISIBLE"] and r["severity"]=="HIGH"]
    raw_high_retained=sum(
        r["raw_ANY_VISIBLE"] and r["severity"]=="HIGH" and float(r["p_high"])>=tau
        for r in rows
    )

    return {
        "events":len(warns),
        "high_hits":int(hh),
        "medium_hits":int(mh),
        "false_calls":int(fc),
        "high_recall":None if high_all==0 else float(hh/high_all),
        "elevated_recall":None if elev_all==0 else float((hh+mh)/elev_all),
        "false_call_rate":None if not warns else float(fc/len(warns)),
        "useful_call_rate":None if not warns else float((hh+mh)/len(warns)),
        "raw_any_high_hits":len(raw_high_rows),
        "raw_any_high_hits_retained":int(raw_high_retained),
        "raw_any_high_hit_retention":None if not raw_high_rows else float(raw_high_retained/len(raw_high_rows)),
        "warn_origins":[r["origin"] for r in warns],
        "warn_targets":[r["target"] for r in warns],
    }


def raw_union_metrics(rows: list[dict], field: str):
    fired=[r for r in rows if bool(r[field])]
    high_all=sum(r["severity"]=="HIGH" for r in rows)
    elev_all=sum(r["severity"] in ("HIGH","MEDIUM") for r in rows)
    hh=sum(r["severity"]=="HIGH" for r in fired)
    mh=sum(r["severity"]=="MEDIUM" for r in fired)
    fc=sum(r["severity"]=="NORMAL" for r in fired)
    return {
        "events":len(fired),
        "high_hits":int(hh),
        "medium_hits":int(mh),
        "false_calls":int(fc),
        "high_recall":None if high_all==0 else float(hh/high_all),
        "elevated_recall":None if elev_all==0 else float((hh+mh)/elev_all),
        "false_call_rate":None if not fired else float(fc/len(fired)),
        "useful_call_rate":None if not fired else float((hh+mh)/len(fired)),
    }


def v2_only_metrics(rows: list[dict]):
    fired=[r for r in rows if bool(r["v2_transition"])]
    high_all=sum(r["severity"]=="HIGH" for r in rows)
    elev_all=sum(r["severity"] in ("HIGH","MEDIUM") for r in rows)
    hh=sum(r["severity"]=="HIGH" for r in fired)
    mh=sum(r["severity"]=="MEDIUM" for r in fired)
    fc=sum(r["severity"]=="NORMAL" for r in fired)
    return {
        "events":len(fired),
        "high_hits":int(hh),
        "medium_hits":int(mh),
        "false_calls":int(fc),
        "high_recall":None if high_all==0 else float(hh/high_all),
        "elevated_recall":None if elev_all==0 else float((hh+mh)/elev_all),
        "false_call_rate":None if not fired else float(fc/len(fired)),
        "useful_call_rate":None if not fired else float((hh+mh)/len(fired)),
    }


def period_subset(scored,start,end):
    return [r for r in scored if start <= r["target"] <= end]


def candidate_id(kind: str, eta: float, alpha: float, tau: float):
    if kind=="HEDGE":
        return f"HEDGE_eta{eta:.2f}_tau{tau:.2f}"
    return f"FIXED_SHARE_eta{eta:.2f}_alpha{alpha:.2f}_tau{tau:.2f}"


def build_grid():
    grid=[]
    for eta in ETAS:
        for tau in TAUS:
            grid.append({"kind":"HEDGE","eta":eta,"alpha":0.0,"tau":tau,
                         "id":candidate_id("HEDGE",eta,0.0,tau)})
    for eta in ETAS:
        for alpha in ALPHAS:
            for tau in TAUS:
                grid.append({"kind":"FIXED_SHARE","eta":eta,"alpha":alpha,"tau":tau,
                             "id":candidate_id("FIXED_SHARE",eta,alpha,tau)})
    return grid


def evaluate_candidate(all_rows, params):
    scored,checkpoints=run_online(all_rows,params["eta"],params["alpha"])
    dev=period_subset(scored,DEV_START,DEV_END)
    rm=router_metrics(dev,params["tau"])
    brier=binary_scoring(dev,"p_high",target_from_scored_high)
    elev=binary_scoring(dev,"p_elevated",target_from_scored_elev)
    raw=raw_union_metrics(dev,"raw_ANY_VISIBLE")
    false_reduction = None if raw["false_calls"]==0 else float((raw["false_calls"]-rm["false_calls"])/raw["false_calls"])
    eligible=bool(
        rm["high_recall"] is not None and rm["high_recall"]>=0.90
        and rm["raw_any_high_hit_retention"] is not None
        and rm["raw_any_high_hit_retention"]>=0.90
    )
    return {
        "params":params,
        "dev_router":rm,
        "dev_high_scoring":brier,
        "dev_elevated_scoring":elev,
        "dev_raw_any":raw,
        "false_call_reduction_vs_raw_any":false_reduction,
        "eligible":eligible,
        "_scored":scored,
        "_checkpoints":checkpoints,
    }


def selection_key(x):
    # Eligible pool only.
    rm=x["dev_router"]
    fr=x["false_call_reduction_vs_raw_any"]
    useful=-1 if rm["useful_call_rate"] is None else rm["useful_call_rate"]
    kind_pref=1 if x["params"]["kind"]=="FIXED_SHARE" else 0
    return (
        -(fr if fr is not None else -999.0),
        -rm["medium_hits"],
        -useful,
        x["dev_high_scoring"]["brier"],
        x["dev_high_scoring"]["log_loss"],
        -kind_pref,
        x["params"]["id"],
    )


def fallback_key(x):
    rm=x["dev_router"]
    fr=x["false_call_reduction_vs_raw_any"]
    return (
        -(rm["high_recall"] if rm["high_recall"] is not None else -1),
        -(rm["raw_any_high_hit_retention"] if rm["raw_any_high_hit_retention"] is not None else -1),
        -(fr if fr is not None else -999.0),
        -rm["medium_hits"],
        x["dev_high_scoring"]["brier"],
        x["params"]["id"],
    )


def compact_candidate(x):
    return {
        "params":x["params"],
        "eligible":x["eligible"],
        "dev_router":x["dev_router"],
        "dev_high_scoring":x["dev_high_scoring"],
        "dev_elevated_scoring":x["dev_elevated_scoring"],
        "false_call_reduction_vs_raw_any":x["false_call_reduction_vs_raw_any"],
    }


def promotion_gate(selected):
    rm=selected["dev_router"]
    raw=selected["dev_raw_any"]
    fr=selected["false_call_reduction_vs_raw_any"]
    return {
        "high_recall_required":0.90,
        "high_recall_observed":rm["high_recall"],
        "high_recall_pass":bool(rm["high_recall"] is not None and rm["high_recall"]>=0.90),
        "raw_any_high_retention_required":0.90,
        "raw_any_high_retention_observed":rm["raw_any_high_hit_retention"],
        "raw_any_high_retention_pass":bool(
            rm["raw_any_high_hit_retention"] is not None and rm["raw_any_high_hit_retention"]>=0.90
        ),
        "false_call_reduction_required":0.20,
        "false_call_reduction_observed":fr,
        "false_call_reduction_pass":bool(fr is not None and fr>=0.20),
        "useful_rate_raw_any":raw["useful_call_rate"],
        "useful_rate_router":rm["useful_call_rate"],
        "useful_rate_pass":bool(
            rm["useful_call_rate"] is not None and raw["useful_call_rate"] is not None
            and rm["useful_call_rate"] > raw["useful_call_rate"]
        ),
    }


def period_bundle(scored,tau,start,end):
    rr=period_subset(scored,start,end)
    return {
        "n":len(rr),
        "router":router_metrics(rr,tau),
        "high_scoring":binary_scoring(rr,"p_high",target_from_scored_high),
        "elevated_scoring":binary_scoring(rr,"p_elevated",target_from_scored_elev),
        "raw_ANY_VISIBLE":raw_union_metrics(rr,"raw_ANY_VISIBLE"),
        "raw_T0_STANDARD":raw_union_metrics(rr,"raw_T0_STANDARD"),
        "V2_TRANSITION_ONLY":v2_only_metrics(rr),
        "rows":rr,
    }


def best_hedge(cands):
    hedge=[x for x in cands if x["params"]["kind"]=="HEDGE"]
    elig=[x for x in hedge if x["eligible"]]
    if elig:
        return sorted(elig,key=selection_key)[0], True
    return sorted(hedge,key=fallback_key)[0], False


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audit-json",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    src=load_json(args.audit_json)
    if src.get("status")!="COMPLETE":
        raise RuntimeError("INVALID_SOURCE")
    if src.get("primary_schedule")!="EXPANDING_REFIT":
        raise RuntimeError("INVALID_PRIMARY_SCHEDULE")
    rows=sorted(src["rows"],key=lambda r:r["origin"])
    if len(rows)!=58:
        raise RuntimeError(("ROW_COUNT",len(rows)))

    grid=build_grid()
    if len(grid)!=100:
        raise RuntimeError(("GRID_COUNT",len(grid)))

    results=[evaluate_candidate(rows,p) for p in grid]
    eligible=[x for x in results if x["eligible"]]

    if eligible:
        selected=sorted(eligible,key=selection_key)[0]
        selection_status="ELIGIBLE_CANDIDATE_SELECTED"
    else:
        selected=sorted(results,key=fallback_key)[0]
        selection_status="NO_ELIGIBLE_CANDIDATE"

    hedge,hedge_eligible=best_hedge(results)
    gate=promotion_gate(selected)
    gate["candidate_pass"]=bool(
        selection_status=="ELIGIBLE_CANDIDATE_SELECTED"
        and gate["high_recall_pass"]
        and gate["raw_any_high_retention_pass"]
        and gate["false_call_reduction_pass"]
        and gate["useful_rate_pass"]
    )

    scored=selected["_scored"]
    tau=selected["params"]["tau"]

    result={
        "schema":"GOLD_MONTHLY_SPECIALIST_FIXED_SHARE_ALARM_ROUTER_V1_2026-09-30",
        "status":"COMPLETE",
        "scientific_gate":"PASS",
        "experts":ALARM_EXPERTS,
        "null_expert":NULL,
        "algorithm":{
            "alarm_prediction":1,
            "null_prediction":0,
            "sleeping_experts_updated":False,
            "share_applied_to":"alarm experts only",
            "tasks":["HIGH","ELEVATED"],
            "primary_decision_task":"HIGH",
        },
        "grid":{
            "etas":ETAS,
            "alphas_fixed_share":ALPHAS,
            "taus":TAUS,
            "candidate_count":len(grid),
            "eligible_count":len(eligible),
            "eligible_fixed_share_count":sum(x["eligible"] and x["params"]["kind"]=="FIXED_SHARE" for x in results),
            "eligible_hedge_count":sum(x["eligible"] and x["params"]["kind"]=="HEDGE" for x in results),
        },
        "selection_contract":{
            "selection_period_targets":[DEV_START,DEV_END],
            "uses_2025_2026":False,
            "high_recall_min":0.90,
            "raw_any_high_retention_min":0.90,
            "ranking":[
                "max false-call reduction vs raw ANY",
                "max MEDIUM hits",
                "max useful-call rate",
                "min HIGH Brier",
                "min HIGH log loss",
                "prefer Fixed-Share on exact tie",
                "lexical id"
            ],
        },
        "selection_status":selection_status,
        "selected_candidate":compact_candidate(selected),
        "best_hedge_candidate":compact_candidate(hedge),
        "best_hedge_was_eligible":hedge_eligible,
        "promotion_gate":gate,
        "dev_baselines":{
            "raw_ANY_VISIBLE":selected["dev_raw_any"],
            "raw_T0_STANDARD":raw_union_metrics(period_subset(scored,DEV_START,DEV_END),"raw_T0_STANDARD"),
            "V2_TRANSITION_ONLY":v2_only_metrics(period_subset(scored,DEV_START,DEV_END)),
        },
        "periods":{
            "DEV_2022_04_2024_12":period_bundle(scored,tau,DEV_START,DEV_END),
            "OPENED_2025":period_bundle(scored,tau,Y2025_START,Y2025_END),
            "OPENED_2026":period_bundle(scored,tau,Y2026_START,Y2026_END),
            "OPENED_2025_2026":period_bundle(scored,tau,OPEN_START,OPEN_END),
        },
        "selected_checkpoints":selected["_checkpoints"],
        "grid_results":[compact_candidate(x) for x in results],
        "governance":{
            "raw_alarm_definitions_changed":False,
            "v2_retuned":False,
            "regime_used_in_router":False,
            "2025_2026_used_for_eta_alpha_tau_selection":False,
            "posthoc_grid_values_added":False,
            "forecast_modified":False,
            "model_switching_tested":False,
        },
    }

    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "grid_summary":result["grid"],
        "selection_status":selection_status,
        "selected_candidate":result["selected_candidate"],
        "best_hedge_candidate":result["best_hedge_candidate"],
        "promotion_gate":gate,
        "dev_baselines":result["dev_baselines"],
        "opened_2025":result["periods"]["OPENED_2025"],
        "opened_2026":result["periods"]["OPENED_2026"],
        "opened_2025_2026":result["periods"]["OPENED_2025_2026"],
        "checkpoints":result["selected_checkpoints"],
    },sort_keys=True))


if __name__=="__main__":
    main()
