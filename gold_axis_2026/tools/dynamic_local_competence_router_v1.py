from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

IDENTITY = "GOLD_CONTROL_DYNAMIC_LOCAL_COMPETENCE_ROUTER_V1_RESEARCH"
EXPERTS = [
    "TTSM_S2",
    "TTSM_S1",
    "BONATO_AR1_RM_QBOOST_H1",
    "AR1_RM_LOGIT",
    "RM_LOGIT",
]
K_GRID = [20, 30, 40, 60, 90, 120]
MIN_HISTORY = 120


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def robust_scale(hist_X: np.ndarray, x: np.ndarray):
    med = np.median(hist_X, axis=0)
    mad = np.median(np.abs(hist_X - med), axis=0)
    scale = 1.4826 * mad
    std = np.std(hist_X, axis=0, ddof=0)
    scale = np.where(scale > 1e-12, scale, np.where(std > 1e-12, std, 1.0))
    return (hist_X - med) / scale, (x - med) / scale


def build_rows(base):
    base.CUTOFF = "2026-09-01T04:00:00Z"
    days = base.load_days()
    tdays, bdays, ldays, daily = base.transformed(days)
    trows = base.ttsm_mod.build_signal_rows(tdays)
    bmaps = base.bonato_maps(bdays)
    lmaps = base.logit_maps(ldays)
    contexts = base.legacy_context(daily)

    # Origin-safe state features indexed by completed origin day.
    state = {}
    closes = np.array([float(x.close) for x in days], dtype=float)
    logc = np.log(closes)
    for i, x in enumerate(days):
        if i < 20:
            continue
        lag1 = float(logc[i] - logc[i-1])
        mom5 = float(logc[i] - logc[i-5])
        mom20 = float(logc[i] - logc[i-20])
        logrv = float(math.log(max(x.rv, 1e-12)))
        logrv5 = float(np.mean([math.log(max(days[j].rv, 1e-12)) for j in range(i-4, i+1)]))
        rsk = 0.0
        if x.rv > 0 and x.m_returns > 0:
            rsk = float(math.sqrt(x.m_returns) * x.r3 / (x.rv ** 1.5))
            if not math.isfinite(rsk):
                rsk = 0.0
        downside_share = float(x.rs_minus / x.rv) if x.rv > 0 else 0.5
        ctx = contexts[x.d.isoformat()]
        state[x.d.isoformat()] = [
            lag1,
            mom5,
            mom20,
            logrv,
            logrv5,
            rsk,
            downside_share,
            float(ctx["FAST_UP"]),
            float(ctx["SLOW_UP"]),
            float(ctx["MONTHLY_UP"]),
        ]

    tmap = {r["target_date"]: r for r in trows}
    common = sorted(
        set(tmap)
        & set(bmaps["BONATO_AR1_RM_QBOOST_H1"])
        & set(lmaps["AR1_RM_LOGIT"])
        & set(lmaps["RM_LOGIT"])
    )
    out = []
    for td in common:
        t = tmap[td]
        b = bmaps["BONATO_AR1_RM_QBOOST_H1"][td]
        ar = lmaps["AR1_RM_LOGIT"][td]
        rm = lmaps["RM_LOGIT"][td]
        od = t["origin_date"]
        if od not in state:
            continue
        if not (od == b["origin_date"] == ar["origin_date"] == rm["origin_date"]):
            raise RuntimeError(f"ORIGIN_MISMATCH:{td}")
        vals = [int(t["actual_up"]), int(b["actual_up"]), int(ar["actual_up"]), int(rm["actual_up"])]
        if len(set(vals)) != 1:
            raise RuntimeError(f"ACTUAL_MISMATCH:{td}:{vals}")
        ctx = contexts[od]
        out.append({
            "origin_date": od,
            "target_date": td,
            "year": int(td[:4]),
            "actual_up": vals[0],
            "state": state[od],
            "TTSM_S2": int(t["ttsm_s2_signal"] == 1),
            "TTSM_S1": int(t["ttsm_s1_signal"] == 1),
            "BONATO_AR1_RM_QBOOST_H1": int(b["up"]),
            "AR1_RM_LOGIT": int(ar["up"]),
            "RM_LOGIT": int(rm["up"]),
            **ctx,
        })
    return out


def metrics(rows):
    n = len(rows)
    tp = sum(r["pred_up"] == 1 and r["actual_up"] == 1 for r in rows)
    fp = sum(r["pred_up"] == 1 and r["actual_up"] == 0 for r in rows)
    tn = sum(r["pred_up"] == 0 and r["actual_up"] == 0 for r in rows)
    fn = sum(r["pred_up"] == 0 and r["actual_up"] == 1 for r in rows)
    au, ad, pu = tp + fn, tn + fp, tp + fp
    prec = tp / pu if pu else None
    rec = tp / au if au else None
    fpr = fp / ad if ad else None
    spec = tn / ad if ad else None
    bal = None if rec is None or spec is None else (rec + spec) / 2.0
    return {
        "n": n, "actual_up": au, "actual_down": ad, "predicted_up": pu,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "up_precision": prec, "up_recall": rec, "false_up_fpr": fpr,
        "down_recall": spec, "balanced_accuracy": bal,
        "accuracy": (tp + tn) / n if n else None,
        "coverage": pu / n if n else None,
    }


def local_competence_run(rows, k):
    scored = []
    hist = []
    for r in rows:
        if len(hist) < MIN_HISTORY:
            hist.append(r)
            continue
        HX = np.array([h["state"] for h in hist], dtype=float)
        x = np.array(r["state"], dtype=float)
        Z, zx = robust_scale(HX, x)
        dist = np.sqrt(np.sum((Z - zx) ** 2, axis=1))
        order = np.argsort(dist, kind="mergesort")
        kk = min(k, len(hist))
        idx = order[:kk]
        neigh = [hist[int(i)] for i in idx]
        nd = np.array([dist[int(i)] for i in idx], dtype=float)
        dw = 1.0 / (nd + 1e-6)
        dw = dw / np.sum(dw)

        comps = {}
        for ex in EXPERTS:
            correct = np.array([1.0 if int(h[ex]) == int(h["actual_up"]) else 0.0 for h in neigh], dtype=float)
            local_acc = float(np.sum(dw * correct))
            local_up_precision_num = sum(float(dw[j]) for j,h in enumerate(neigh) if h[ex] == 1 and h["actual_up"] == 1)
            local_up_precision_den = sum(float(dw[j]) for j,h in enumerate(neigh) if h[ex] == 1)
            local_up_precision = local_up_precision_num / local_up_precision_den if local_up_precision_den > 0 else 0.5
            comps[ex] = {
                "local_accuracy": local_acc,
                "local_up_precision": float(local_up_precision),
                "current_signal": int(r[ex]),
            }

        # Canonical DCS-style decision: choose the locally most accurate expert.
        # Tie-break: higher local UP precision, then fixed expert order.
        selected = sorted(
            EXPERTS,
            key=lambda ex: (-comps[ex]["local_accuracy"], -comps[ex]["local_up_precision"], EXPERTS.index(ex))
        )[0]
        pred = int(r[selected])

        z = dict(r)
        z["pred_up"] = pred
        z["selected_expert"] = selected
        z["local_competence"] = comps
        z["nearest_distance_mean"] = float(np.mean(nd))
        z["nearest_distance_max"] = float(np.max(nd))
        scored.append(z)
        hist.append(r)
    return scored


def score_router_year(base, eval_rows, history):
    out=[]; hist=[dict(r) for r in history]
    for br in eval_rows:
        row=dict(br); elig=[]
        for ex in base.DIRECT_UP_EXPERTS:
            if row[ex] != 1: continue
            st=base.router_stats(hist,ex,row["legacy_bucket"])
            if st is None or st["n_up"]<30 or st["precision"]<=.50 or st["fpr"]>=.50: continue
            elig.append((ex,st))
        if elig:
            elig.sort(key=lambda x:(-x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]))
            ex,_=elig[0]; row["pred_up"]=1; row["selected_expert"]=ex
        else:
            row["pred_up"]=0; row["selected_expert"]=""
        out.append(row); hist.append(dict(br))
    return out,hist


def router_baseline(base, rows):
    by=defaultdict(list)
    for r in rows: by[r["year"]].append(r)
    s24,h24=score_router_year(base,by[2024],by[2023])
    s25,h25=score_router_year(base,by[2025],h24)
    s26,_=score_router_year(base,by[2026],h25)
    m24,m25,m26=metrics(s24),metrics(s25),metrics(s26)
    if (m24["predicted_up"],m24["tp"],m24["fp"]) != (42,26,16):
        raise RuntimeError("ROUTER_2024_AUTHORITY_MISMATCH")
    if (m25["predicted_up"],m25["tp"],m25["fp"]) != (37,27,10):
        raise RuntimeError("ROUTER_2025_AUTHORITY_MISMATCH")
    return {"2024":m24,"2025":m25,"2026":m26}


def subset(rows, years):
    ys=set(years)
    return [r for r in rows if r["year"] in ys]


def expert_selection_counts(rows):
    return {ex:sum(r["selected_expert"]==ex for r in rows) for ex in EXPERTS}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)

    base=load_module("router_authority_local",args.base)
    rows=build_rows(base)

    # k selected ONLY on 2022-2023. 2024/2025/2026 untouched.
    grid=[]
    for k in K_GRID:
        s=local_competence_run(rows,k)
        dev=subset(s,[2022,2023])
        m=metrics(dev)
        grid.append({"k":k,"dev_2022_2023":m})
    grid=sorted(grid,key=lambda g:(
        -(g["dev_2022_2023"]["balanced_accuracy"] or -1),
        -(g["dev_2022_2023"]["up_recall"] or -1),
        -(g["dev_2022_2023"]["up_precision"] or -1),
        g["k"],
    ))
    selected_k=grid[0]["k"]

    full=local_competence_run(rows,selected_k)
    annual={}
    selections={}
    for y in [2022,2023,2024,2025,2026]:
        rr=subset(full,[y])
        annual[str(y)]=metrics(rr)
        selections[str(y)]=expert_selection_counts(rr)

    # Validation gate is descriptive only: no retuning after seeing 2024.
    baseline=router_baseline(base,rows)
    result={
        "identity":IDENTITY,
        "status":"RESEARCH_ONLY_NO_PROMOTION",
        "protocol":{
            "state_features":[
                "lag1_return","momentum_5d","momentum_20d","log_rv","mean_log_rv_5d",
                "realized_skewness","downside_share","FAST_UP","SLOW_UP","MONTHLY_UP"
            ],
            "distance":"robust-scaled Euclidean using only prior history; inverse-distance neighbor weights",
            "competence":"inverse-distance weighted local classification accuracy over k nearest prior states",
            "decision":"select single locally most accurate expert; tie higher local UP precision then fixed expert order",
            "candidate_k":K_GRID,
            "k_selection":"highest balanced accuracy on 2022-2023 only; ties higher UP recall/precision then smaller k",
            "validation":"2024 untouched during selection",
            "locked_test":"2025 untouched during selection",
            "stress_only":"2026 through 2026-08-31",
            "min_history":MIN_HISTORY,
            "no_2025_tuning":True,
            "no_2026_tuning":True,
        },
        "selected_k":selected_k,
        "development_grid":grid,
        "local_competence":{
            "2022":annual["2022"],"2023":annual["2023"],
            "2024_validation":annual["2024"],
            "2025_locked":annual["2025"],
            "2026_stress":annual["2026"],
            "selected_expert_counts":selections,
        },
        "router_v2_baseline":baseline,
        "governance":{
            "random_split":False,"future_leakage":False,"canonical_branch_modified":False,
            "production_writes":False,"runtime_promotion":False
        }
    }
    (args.out/"GOLD_CONTROL_DYNAMIC_LOCAL_COMPETENCE_ROUTER_V1_RESULT_2026-09-24.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8"
    )
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
