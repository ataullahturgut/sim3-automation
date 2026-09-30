from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

SIGNALS = ["A","B","C","D","E","G","H","I1","I2","T1_WGC"]
T0_SIGNALS = {"A","B","C","D","H"}
MODELS = ["M0_SIGNAL_ONLY","M1_SIGNAL_REGIME","M2_SIGNAL_REGIME_V2"]

DEV_START = "2022-04"
DEV_END = "2024-12"
OPEN_START = "2025-01"
OPEN_END = "2026-08"

K_SIGNAL = 4.0
K_REGIME = 4.0
K_STATUS = 4.0
K_CELL = 6.0
GATE = 0.50
EPS = 1e-12


def load_json(path: str):
    return json.loads(Path(path).read_text())


def useful_outcome(outcome: str) -> int:
    if outcome in ("HIGH_HIT","MEDIUM_HIT"):
        return 1
    if outcome == "FALSE_CALL":
        return 0
    raise ValueError(outcome)


def iter_events(rows):
    for r in rows:
        for s in SIGNALS:
            if bool(r[s]):
                yield {
                    "signal": s,
                    "useful": useful_outcome(r[f"{s}_outcome"]),
                    "origin": r["origin"],
                    "target": r["target"],
                    "severity": r["severity"],
                    "regime": r["v2_semantic_state"],
                    "regime_probability": float(r["v2_semantic_probability"]),
                    "status": r["v2_transition_status"],
                    "live_cell": r["live_cell"],
                }


def fit_counts(rows):
    evs = list(iter_events(rows))
    total_n = len(evs)
    total_u = sum(e["useful"] for e in evs)
    global_mean = (total_u + 1.0) / (total_n + 2.0)

    signal = defaultdict(lambda: [0,0])
    signal_regime = defaultdict(lambda: [0,0])
    signal_status = defaultdict(lambda: [0,0])
    cell = defaultdict(lambda: [0,0])

    for e in evs:
        s=e["signal"]; r=e["regime"]; z=e["status"]; y=e["useful"]
        signal[s][0] += y; signal[s][1] += 1
        signal_regime[(s,r)][0] += y; signal_regime[(s,r)][1] += 1
        signal_status[(s,z)][0] += y; signal_status[(s,z)][1] += 1
        cell[(s,r,z)][0] += y; cell[(s,r,z)][1] += 1

    return {
        "n_events": total_n,
        "n_useful": total_u,
        "global_mean": global_mean,
        "signal": dict(signal),
        "signal_regime": dict(signal_regime),
        "signal_status": dict(signal_status),
        "cell": dict(cell),
    }


def cnt(d, key):
    return d.get(key, [0,0])


def estimates(fit, signal, regime, status, p):
    u_s,n_s = cnt(fit["signal"], signal)
    m_s = (u_s + K_SIGNAL*fit["global_mean"]) / (n_s + K_SIGNAL)

    u_sr,n_sr = cnt(fit["signal_regime"], (signal,regime))
    m_sr = (u_sr + K_REGIME*m_s) / (n_sr + K_REGIME)

    u_sz,n_sz = cnt(fit["signal_status"], (signal,status))
    m_sz = (u_sz + K_STATUS*m_s) / (n_sz + K_STATUS)

    u_c,n_c = cnt(fit["cell"], (signal,regime,status))
    parent = 0.5*(m_sr+m_sz)
    m_c = (u_c + K_CELL*parent) / (n_c + K_CELL)

    p = min(1.0,max(0.0,float(p)))
    m0 = m_s
    m1 = p*m_sr + (1.0-p)*m_s
    m2 = p*m_c + (1.0-p)*m_sz
    return {
        "M0_SIGNAL_ONLY": float(m0),
        "M1_SIGNAL_REGIME": float(m1),
        "M2_SIGNAL_REGIME_V2": float(m2),
        "components": {
            "m_global": float(fit["global_mean"]),
            "m_signal": float(m_s),
            "m_signal_regime": float(m_sr),
            "m_signal_status": float(m_sz),
            "m_cell": float(m_c),
            "regime_probability": p,
            "n_signal": n_s,
            "n_signal_regime": n_sr,
            "n_signal_status": n_sz,
            "n_cell": n_c,
        },
    }


def score_row(row, fit):
    scores={}
    for s in SIGNALS:
        if not bool(row[s]):
            continue
        e=estimates(
            fit, s, row["v2_semantic_state"], row["v2_transition_status"],
            float(row["v2_semantic_probability"])
        )
        scores[s]=e
    return scores


def oof_dev_scores(rows):
    dev=[r for r in rows if DEV_START <= r["target"] <= DEV_END]
    out=[]
    for r in sorted(dev,key=lambda x:x["origin"]):
        train=[x for x in rows if x["origin"] < r["origin"]]
        fit=fit_counts(train)
        out.append({**r,"reliability_scores":score_row(r,fit),"fit_event_count":fit["n_events"]})
    return out


def frozen_open_scores(rows):
    train=[r for r in rows if r["target"] <= DEV_END]
    fit=fit_counts(train)
    opened=[r for r in rows if OPEN_START <= r["target"] <= OPEN_END]
    out=[]
    for r in opened:
        out.append({**r,"reliability_scores":score_row(r,fit),"fit_event_count":fit["n_events"]})
    return out,fit


def event_records(scored_rows, model):
    out=[]
    for r in scored_rows:
        for s,e in r["reliability_scores"].items():
            y=useful_outcome(r[f"{s}_outcome"])
            out.append({
                "origin":r["origin"],
                "target":r["target"],
                "signal":s,
                "severity":r["severity"],
                "outcome":r[f"{s}_outcome"],
                "useful":y,
                "score":float(e[model]),
                "regime":r["v2_semantic_state"],
                "regime_probability":float(r["v2_semantic_probability"]),
                "status":r["v2_transition_status"],
                "live_cell":r["live_cell"],
                "components":e["components"],
            })
    return out


def score_metrics(records):
    n=len(records)
    if n==0:
        return {"n":0,"brier":None,"log_loss":None,"mean_score_useful":None,"mean_score_false":None}
    b=sum((r["score"]-r["useful"])**2 for r in records)/n
    ll=0.0
    for r in records:
        p=min(1-EPS,max(EPS,r["score"]))
        y=r["useful"]
        ll += -(y*math.log(p)+(1-y)*math.log(1-p))
    ll/=n
    useful=[r["score"] for r in records if r["useful"]==1]
    false=[r["score"] for r in records if r["useful"]==0]
    return {
        "n":n,
        "useful_n":len(useful),
        "false_n":len(false),
        "brier":float(b),
        "log_loss":float(ll),
        "mean_score_useful":None if not useful else float(sum(useful)/len(useful)),
        "mean_score_false":None if not false else float(sum(false)/len(false)),
    }


def signal_score_metrics(records):
    out={}
    for s in SIGNALS:
        rr=[r for r in records if r["signal"]==s]
        q=score_metrics(rr)
        q["evidence_label"]="NO_EVENTS" if not rr else ("SMALL_N" if len(rr)<3 else "REPORTABLE")
        out[s]=q
    return out


def gate_event_metrics(records):
    kept=[r for r in records if r["score"]>=GATE]
    useful_all=sum(r["useful"] for r in records)
    false_all=len(records)-useful_all
    useful_kept=sum(r["useful"] for r in kept)
    false_kept=len(kept)-useful_kept
    return {
        "n_events":len(records),
        "kept_events":len(kept),
        "useful_events":useful_all,
        "false_events":false_all,
        "useful_kept":useful_kept,
        "false_kept":false_kept,
        "useful_event_recall":None if useful_all==0 else float(useful_kept/useful_all),
        "false_call_suppression":None if false_all==0 else float((false_all-false_kept)/false_all),
    }


def raw_union_metrics(rows, union_name):
    ev=[r for r in rows if bool(r[union_name])]
    high=[r for r in rows if r["severity"]=="HIGH"]
    elev=[r for r in rows if r["severity"] in ("HIGH","MEDIUM")]
    hh=sum(r["severity"]=="HIGH" for r in ev)
    mh=sum(r["severity"]=="MEDIUM" for r in ev)
    fc=sum(r["severity"]=="NORMAL" for r in ev)
    return {
        "events":len(ev),
        "high_hits":int(hh),
        "medium_hits":int(mh),
        "false_calls":int(fc),
        "high_recall":None if not high else float(hh/len(high)),
        "elevated_recall":None if not elev else float((hh+mh)/len(elev)),
        "false_call_rate":None if not ev else float(fc/len(ev)),
        "useful_call_rate":None if not ev else float((hh+mh)/len(ev)),
    }


def gated_union_metrics(scored_rows, model, union):
    out=[]
    suppressed=[]
    allowed=T0_SIGNALS if union=="T0_STANDARD" else set(SIGNALS)

    for r in scored_rows:
        active=[s for s in SIGNALS if bool(r[s]) and s in allowed]
        accepted=[
            s for s in active
            if s in r["reliability_scores"] and r["reliability_scores"][s][model]>=GATE
        ]
        fired=bool(accepted)
        if fired:
            out.append(r)
        if active and not fired:
            suppressed.append({
                "origin":r["origin"],"target":r["target"],"severity":r["severity"],
                "active_signals":active,
                "scores":{s:float(r["reliability_scores"][s][model]) for s in active},
            })

    high=[r for r in scored_rows if r["severity"]=="HIGH"]
    elev=[r for r in scored_rows if r["severity"] in ("HIGH","MEDIUM")]
    hh=sum(r["severity"]=="HIGH" for r in out)
    mh=sum(r["severity"]=="MEDIUM" for r in out)
    fc=sum(r["severity"]=="NORMAL" for r in out)
    return {
        "events":len(out),
        "high_hits":int(hh),
        "medium_hits":int(mh),
        "false_calls":int(fc),
        "high_recall":None if not high else float(hh/len(high)),
        "elevated_recall":None if not elev else float((hh+mh)/len(elev)),
        "false_call_rate":None if not out else float(fc/len(out)),
        "useful_call_rate":None if not out else float((hh+mh)/len(out)),
        "suppressed_rows":suppressed,
    }


def union_comparison(scored_rows, model):
    plain=[{k:v for k,v in r.items() if k!="reliability_scores"} for r in scored_rows]
    out={}
    for union in ["T0_STANDARD","ANY_VISIBLE"]:
        raw=raw_union_metrics(plain,union)
        gated=gated_union_metrics(scored_rows,model,union)
        out[union]={
            "raw":raw,
            "gated":gated,
            "high_hit_retention_vs_raw":None if raw["high_hits"]==0 else float(gated["high_hits"]/raw["high_hits"]),
            "false_call_reduction_vs_raw":None if raw["false_calls"]==0 else float((raw["false_calls"]-gated["false_calls"])/raw["false_calls"]),
        }
    return out


def by_status(records):
    out={}
    for z in ["STABLE","TRANSITION"]:
        rr=[r for r in records if r["status"]==z]
        out[z]=score_metrics(rr)
    return out


def by_regime(records):
    out={}
    for rg in ["R0","R1","R2"]:
        rr=[r for r in records if r["regime"]==rg]
        out[rg]=score_metrics(rr)
    return out


def evaluate(scored_rows):
    result={}
    for model in MODELS:
        rec=event_records(scored_rows,model)
        result[model]={
            "event_scoring":score_metrics(rec),
            "gate_event_metrics":gate_event_metrics(rec),
            "per_signal":signal_score_metrics(rec),
            "by_status":by_status(rec),
            "by_regime":by_regime(rec),
            "unions":union_comparison(scored_rows,model),
        }
    return result


def improvement(base,new):
    if base is None or new is None or base==0:
        return None
    return float((base-new)/base)


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

    dev_scored=oof_dev_scores(rows)
    opened_scored,pre2025_fit=frozen_open_scores(rows)

    if len(dev_scored)!=33:
        raise RuntimeError(("DEV_ROWS",len(dev_scored)))
    if len(opened_scored)!=20:
        raise RuntimeError(("OPEN_ROWS",len(opened_scored)))

    dev=evaluate(dev_scored)
    opened=evaluate(opened_scored)

    b0=dev["M0_SIGNAL_ONLY"]["event_scoring"]["brier"]
    b1=dev["M1_SIGNAL_REGIME"]["event_scoring"]["brier"]
    b2=dev["M2_SIGNAL_REGIME_V2"]["event_scoring"]["brier"]
    imp0=improvement(b0,b2)
    imp1=improvement(b1,b2)

    any_m2=dev["M2_SIGNAL_REGIME_V2"]["unions"]["ANY_VISIBLE"]
    high_ret=any_m2["high_hit_retention_vs_raw"]
    false_red=any_m2["false_call_reduction_vs_raw"]

    gates={
        "brier_improvement_vs_M0_required":0.05,
        "brier_improvement_vs_M0_observed":imp0,
        "brier_vs_M0_pass":bool(imp0 is not None and imp0>=0.05),
        "brier_improvement_vs_M1_required":0.02,
        "brier_improvement_vs_M1_observed":imp1,
        "brier_vs_M1_pass":bool(imp1 is not None and imp1>=0.02),
        "any_visible_high_hit_retention_required":0.90,
        "any_visible_high_hit_retention_observed":high_ret,
        "high_retention_pass":bool(high_ret is not None and high_ret>=0.90),
        "any_visible_false_call_reduction_required":0.20,
        "any_visible_false_call_reduction_observed":false_red,
        "false_reduction_pass":bool(false_red is not None and false_red>=0.20),
    }
    gates["candidate_pass"]=all([
        gates["brier_vs_M0_pass"],gates["brier_vs_M1_pass"],
        gates["high_retention_pass"],gates["false_reduction_pass"]
    ])

    result={
        "schema":"GOLD_MONTHLY_ALARM_REGIME_V2_SHRINKAGE_RELIABILITY_V1_2026-09-30",
        "status":"COMPLETE",
        "scientific_gate":"PASS",
        "model":{
            "target":"useful alarm = HIGH_HIT or MEDIUM_HIT",
            "pseudo_counts":{
                "signal":K_SIGNAL,"signal_regime":K_REGIME,
                "signal_status":K_STATUS,"cell":K_CELL,
            },
            "gate_threshold":GATE,
            "models":{
                "M0":"signal only",
                "M1":"signal + soft live regime",
                "M2":"signal + soft live regime + V2 status",
            },
        },
        "dev_contract":{
            "targets":[DEV_START,DEV_END],
            "rows":len(dev_scored),
            "scoring":"expanding OOF; only origin rows strictly earlier than scored origin",
        },
        "opened_contract":{
            "targets":[OPEN_START,OPEN_END],
            "rows":len(opened_scored),
            "training":"frozen target<=2024-12",
            "pre2025_fit_event_count":pre2025_fit["n_events"],
            "opened_outcomes_used_for_fit":False,
        },
        "dev":dev,
        "opened_2025_2026":opened,
        "dev_candidate_gate":gates,
        "dev_scored_rows":dev_scored,
        "opened_scored_rows":opened_scored,
        "governance":{
            "raw_alarm_definitions_changed":False,
            "v2_retuned":False,
            "regime_model_changed":False,
            "pseudo_counts_tuned":False,
            "gate_threshold_tuned":False,
            "2025_2026_used_for_model_selection":False,
            "forecast_modified":False,
            "routing_tested":False,
        },
    }

    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    def compact(m):
        return {
            "event_scoring":m["event_scoring"],
            "gate_event_metrics":m["gate_event_metrics"],
            "unions":{
                u:{
                    "raw":m["unions"][u]["raw"],
                    "gated":{k:v for k,v in m["unions"][u]["gated"].items() if k!="suppressed_rows"},
                    "high_hit_retention_vs_raw":m["unions"][u]["high_hit_retention_vs_raw"],
                    "false_call_reduction_vs_raw":m["unions"][u]["false_call_reduction_vs_raw"],
                } for u in ["T0_STANDARD","ANY_VISIBLE"]
            },
            "by_status":m["by_status"],
            "by_regime":m["by_regime"],
        }

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "dev_candidate_gate":gates,
        "dev":{k:compact(v) for k,v in dev.items()},
        "opened":{k:compact(v) for k,v in opened.items()},
        "dev_M2_suppressed_any":dev["M2_SIGNAL_REGIME_V2"]["unions"]["ANY_VISIBLE"]["gated"]["suppressed_rows"],
        "opened_M2_suppressed_any":opened["M2_SIGNAL_REGIME_V2"]["unions"]["ANY_VISIBLE"]["gated"]["suppressed_rows"],
    },sort_keys=True))


if __name__=="__main__":
    main()
