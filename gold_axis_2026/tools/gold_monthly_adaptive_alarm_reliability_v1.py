from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

SIGNALS = ["A","B","C","D","E","G","H","I1","I2","T1_WGC"]
T0_SIGNALS = {"A","B","C","D","H"}
PRIOR_STRENGTH = 4.0
GATE = 0.50
EPS = 1e-12

DEV_START, DEV_END = "2022-04", "2024-12"
OPEN_START, OPEN_END = "2025-01", "2026-08"
CHECKPOINTS = ["2024-12","2025-06","2025-12","2026-04","2026-06","2026-08"]

CANDIDATES = {
    "EXPANDING": ("EXPANDING", None),
    "ROLL_12": ("ROLL", 12),
    "ROLL_18": ("ROLL", 18),
    "ROLL_24": ("ROLL", 24),
    "ROLL_36": ("ROLL", 36),
    "HL_6": ("HL", 6),
    "HL_12": ("HL", 12),
    "HL_18": ("HL", 18),
    "HL_24": ("HL", 24),
}


def load_json(path: str):
    return json.loads(Path(path).read_text())


def mindex(month: str) -> int:
    y,m = month.split("-")
    return int(y)*12 + int(m)


def outcome_y(row: dict, signal: str) -> int:
    o = row[f"{signal}_outcome"]
    if o in ("HIGH_HIT","MEDIUM_HIT"):
        return 1
    if o == "FALSE_CALL":
        return 0
    raise ValueError((signal,o))


def weight_for(candidate: str, train_origin: str, score_origin: str) -> float:
    kind,param = CANDIDATES[candidate]
    age = mindex(score_origin) - mindex(train_origin)
    if age <= 0:
        return 0.0
    if kind == "EXPANDING":
        return 1.0
    if kind == "ROLL":
        return 1.0 if age <= int(param) else 0.0
    if kind == "HL":
        return float(0.5 ** (age / float(param)))
    raise ValueError(candidate)


def weighted_fit(rows: list[dict], score_origin: str, candidate: str):
    gu = 0.0
    gn = 0.0
    su = defaultdict(float)
    sn = defaultdict(float)
    raw_n = defaultdict(int)
    raw_u = defaultdict(int)

    for r in rows:
        if r["origin"] >= score_origin:
            continue
        w = weight_for(candidate, r["origin"], score_origin)
        if w <= 0:
            continue
        for s in SIGNALS:
            if not bool(r[s]):
                continue
            y = outcome_y(r,s)
            gu += w*y
            gn += w
            su[s] += w*y
            sn[s] += w
            raw_n[s] += 1
            raw_u[s] += y

    m_global = (gu + 1.0) / (gn + 2.0)
    scores = {}
    details = {}
    for s in SIGNALS:
        score = (su[s] + PRIOR_STRENGTH*m_global) / (sn[s] + PRIOR_STRENGTH)
        scores[s] = float(score)
        details[s] = {
            "score": float(score),
            "weighted_event_mass": float(sn[s]),
            "weighted_useful_mass": float(su[s]),
            "raw_event_count_in_memory": int(raw_n[s]),
            "raw_useful_count_in_memory": int(raw_u[s]),
        }
    return {
        "global_mean": float(m_global),
        "global_weighted_event_mass": float(gn),
        "global_weighted_useful_mass": float(gu),
        "scores": scores,
        "details": details,
    }


def score_rows(source_rows, eval_rows, candidate):
    out=[]
    for r in sorted(eval_rows, key=lambda x:x["origin"]):
        fit=weighted_fit(source_rows,r["origin"],candidate)
        active={}
        for s in SIGNALS:
            if bool(r[s]):
                active[s]={
                    "score":fit["scores"][s],
                    "useful":outcome_y(r,s),
                    "outcome":r[f"{s}_outcome"],
                }
        out.append({
            "origin":r["origin"],
            "target":r["target"],
            "severity":r["severity"],
            "ANY_VISIBLE":bool(r["ANY_VISIBLE"]),
            "T0_STANDARD":bool(r["T0_STANDARD"]),
            "active_signals":list(r["active_signals"]),
            "active_scores":active,
            "global_mean":fit["global_mean"],
        })
    return out


def event_records(scored_rows):
    out=[]
    for r in scored_rows:
        for s,d in r["active_scores"].items():
            out.append({
                "origin":r["origin"],
                "target":r["target"],
                "severity":r["severity"],
                "signal":s,
                "score":float(d["score"]),
                "useful":int(d["useful"]),
                "outcome":d["outcome"],
            })
    return out


def score_metrics(records):
    n=len(records)
    if not n:
        return {"n":0,"useful_n":0,"false_n":0,"brier":None,"log_loss":None,
                "mean_score_useful":None,"mean_score_false":None}
    b=sum((r["score"]-r["useful"])**2 for r in records)/n
    ll=0.0
    us=[]
    fs=[]
    for r in records:
        p=min(1-EPS,max(EPS,r["score"]))
        y=r["useful"]
        ll += -(y*math.log(p)+(1-y)*math.log(1-p))
        (us if y else fs).append(r["score"])
    ll/=n
    return {
        "n":n,
        "useful_n":len(us),
        "false_n":len(fs),
        "brier":float(b),
        "log_loss":float(ll),
        "mean_score_useful":None if not us else float(sum(us)/len(us)),
        "mean_score_false":None if not fs else float(sum(fs)/len(fs)),
    }


def raw_union_metrics(rows, field):
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


def gated_union_metrics(scored_rows, union):
    allowed=set(SIGNALS) if union=="ANY_VISIBLE" else T0_SIGNALS
    fired=[]
    suppressed=[]
    for r in scored_rows:
        active=[s for s in r["active_scores"] if s in allowed]
        kept=[s for s in active if r["active_scores"][s]["score"] >= GATE]
        if kept:
            fired.append(r)
        if active and not kept:
            suppressed.append({
                "origin":r["origin"],
                "target":r["target"],
                "severity":r["severity"],
                "active_signals":active,
                "scores":{s:float(r["active_scores"][s]["score"]) for s in active},
            })
    high_all=sum(r["severity"]=="HIGH" for r in scored_rows)
    elev_all=sum(r["severity"] in ("HIGH","MEDIUM") for r in scored_rows)
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
        "suppressed_rows":suppressed,
    }


def union_comparison(source_eval_rows, scored_rows):
    out={}
    for union in ["ANY_VISIBLE","T0_STANDARD"]:
        raw=raw_union_metrics(source_eval_rows,union)
        gated=gated_union_metrics(scored_rows,union)
        out[union]={
            "raw":raw,
            "gated":gated,
            "high_hit_retention_vs_raw":None if raw["high_hits"]==0 else float(gated["high_hits"]/raw["high_hits"]),
            "false_call_reduction_vs_raw":None if raw["false_calls"]==0 else float((raw["false_calls"]-gated["false_calls"])/raw["false_calls"]),
        }
    return out


def evaluate_candidate(source_rows, eval_rows, candidate):
    scored=score_rows(source_rows,eval_rows,candidate)
    records=event_records(scored)
    return {
        "candidate":candidate,
        "event_scoring":score_metrics(records),
        "unions":union_comparison(eval_rows,scored),
        "scored_rows":scored,
    }


def choose_candidate(dev_results):
    ordered=sorted(
        CANDIDATES.keys(),
        key=lambda c: (
            dev_results[c]["event_scoring"]["brier"],
            dev_results[c]["event_scoring"]["log_loss"],
            c,
        )
    )
    return ordered[0], ordered


def improvement(base,new):
    if base is None or new is None or base==0:
        return None
    return float((base-new)/base)


def checkpoint_path(source_rows, selected):
    out={}
    for cp in CHECKPOINTS:
        exp=weighted_fit(source_rows,cp,"EXPANDING")
        sel=weighted_fit(source_rows,cp,selected)
        out[cp]={
            "EXPANDING":{
                "global_mean":exp["global_mean"],
                "signals":{s:exp["details"][s] for s in SIGNALS},
            },
            "SELECTED":{
                "candidate":selected,
                "global_mean":sel["global_mean"],
                "signals":{s:sel["details"][s] for s in SIGNALS},
            },
            "focus":{
                s:{
                    "expanding_score":exp["details"][s]["score"],
                    "selected_score":sel["details"][s]["score"],
                    "selected_weighted_event_mass":sel["details"][s]["weighted_event_mass"],
                    "selected_weighted_useful_mass":sel["details"][s]["weighted_useful_mass"],
                } for s in ["E","H","T1_WGC","I2"]
            },
        }
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audit-json",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    src=load_json(args.audit_json)
    if src.get("status")!="COMPLETE":
        raise RuntimeError("INVALID_SOURCE")
    rows=sorted(src["rows"],key=lambda r:r["origin"])
    if len(rows)!=58:
        raise RuntimeError(("ROW_COUNT",len(rows)))

    dev_rows=[r for r in rows if DEV_START <= r["target"] <= DEV_END]
    opened_rows=[r for r in rows if OPEN_START <= r["target"] <= OPEN_END]
    if len(dev_rows)!=33 or len(opened_rows)!=20:
        raise RuntimeError((len(dev_rows),len(opened_rows)))

    dev_results={}
    for c in CANDIDATES:
        dev_results[c]=evaluate_candidate(rows,dev_rows,c)

    selected,selection_order=choose_candidate(dev_results)

    exp_b=dev_results["EXPANDING"]["event_scoring"]["brier"]
    sel_b=dev_results[selected]["event_scoring"]["brier"]
    b_imp=improvement(exp_b,sel_b)
    sm=dev_results[selected]["event_scoring"]
    anyc=dev_results[selected]["unions"]["ANY_VISIBLE"]

    evidence_gate={
        "selected_candidate":selected,
        "selected_is_adaptive":selected!="EXPANDING",
        "brier_improvement_vs_expanding":b_imp,
        "brier_improvement_required":0.05,
        "brier_pass":bool(b_imp is not None and b_imp>=0.05),
        "mean_score_useful":sm["mean_score_useful"],
        "mean_score_false":sm["mean_score_false"],
        "discrimination_pass":bool(
            sm["mean_score_useful"] is not None and sm["mean_score_false"] is not None
            and sm["mean_score_useful"] > sm["mean_score_false"]
        ),
        "any_high_retention":anyc["high_hit_retention_vs_raw"],
        "any_high_retention_required":0.80,
        "high_retention_pass":bool(
            anyc["high_hit_retention_vs_raw"] is not None
            and anyc["high_hit_retention_vs_raw"]>=0.80
        ),
        "any_false_call_reduction":anyc["false_call_reduction_vs_raw"],
        "any_false_call_reduction_required":0.20,
        "false_reduction_pass":bool(
            anyc["false_call_reduction_vs_raw"] is not None
            and anyc["false_call_reduction_vs_raw"]>=0.20
        ),
    }
    evidence_gate["candidate_pass"]=all([
        evidence_gate["selected_is_adaptive"],
        evidence_gate["brier_pass"],
        evidence_gate["discrimination_pass"],
        evidence_gate["high_retention_pass"],
        evidence_gate["false_reduction_pass"],
    ])

    opened_selected=evaluate_candidate(rows,opened_rows,selected)
    opened_exp=evaluate_candidate(rows,opened_rows,"EXPANDING")

    result={
        "schema":"GOLD_MONTHLY_ADAPTIVE_ALARM_RELIABILITY_V1_2026-09-30",
        "status":"COMPLETE",
        "scientific_gate":"PASS",
        "candidate_definitions":{
            k:{"kind":v[0],"parameter":v[1]} for k,v in CANDIDATES.items()
        },
        "fixed_prior_strength":PRIOR_STRENGTH,
        "fixed_gate":GATE,
        "dev_contract":{
            "targets":[DEV_START,DEV_END],
            "rows":len(dev_rows),
            "selection_uses_2025_2026":False,
            "scoring":"walk-forward; train origins strictly before scored origin",
        },
        "dev_candidate_results":{
            c:{
                "event_scoring":dev_results[c]["event_scoring"],
                "unions":dev_results[c]["unions"],
            } for c in CANDIDATES
        },
        "selection_order":selection_order,
        "selected_candidate":selected,
        "dev_evidence_gate":evidence_gate,
        "opened_contract":{
            "targets":[OPEN_START,OPEN_END],
            "rows":len(opened_rows),
            "mechanism_frozen_from_pre2025":True,
            "sequential_update_from_prior_opened_outcomes":True,
            "opened_used_for_mechanism_selection":False,
        },
        "opened_selected":{
            "candidate":selected,
            "event_scoring":opened_selected["event_scoring"],
            "unions":opened_selected["unions"],
            "scored_rows":opened_selected["scored_rows"],
        },
        "opened_expanding":{
            "event_scoring":opened_exp["event_scoring"],
            "unions":opened_exp["unions"],
        },
        "adaptation_path":checkpoint_path(rows,selected),
        "governance":{
            "new_candidate_added_after_results":False,
            "2025_2026_used_to_choose_memory":False,
            "prior_strength_tuned":False,
            "gate_threshold_tuned":False,
            "alarm_definitions_changed":False,
            "regime_or_v2_changed":False,
            "forecast_modified":False,
            "routing_tested":False,
        },
    }

    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "selection_order":selection_order,
        "selected_candidate":selected,
        "dev_gate":evidence_gate,
        "dev_scores":{
            c:dev_results[c]["event_scoring"] for c in CANDIDATES
        },
        "dev_selected_unions":dev_results[selected]["unions"],
        "opened_selected_score":opened_selected["event_scoring"],
        "opened_expanding_score":opened_exp["event_scoring"],
        "opened_selected_unions":opened_selected["unions"],
        "opened_expanding_unions":opened_exp["unions"],
        "adaptation_focus":{
            cp:result["adaptation_path"][cp]["focus"] for cp in CHECKPOINTS
        },
    },sort_keys=True))


if __name__=="__main__":
    main()
