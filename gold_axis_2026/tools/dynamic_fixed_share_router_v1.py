from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

IDENTITY = "GOLD_CONTROL_DYNAMIC_FIXED_SHARE_ROUTER_V1_RESEARCH"
EXPERTS = [
    "TTSM_S2",
    "TTSM_S1",
    "BONATO_AR1_RM_QBOOST_H1",
    "AR1_RM_LOGIT",
    "RM_LOGIT",
]
ALPHAS = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10]
ETAS = [0.25, 0.50, 1.00, 2.00]
THRESHOLD = 0.50


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def build_rows(base):
    base.CUTOFF = "2026-09-01T04:00:00Z"
    days = base.load_days()
    tdays, bdays, ldays, daily = base.transformed(days)
    trows = base.ttsm_mod.build_signal_rows(tdays)
    bmaps = base.bonato_maps(bdays)
    lmaps = base.logit_maps(ldays)
    contexts = base.legacy_context(daily)

    close = {x.d.isoformat(): float(x.close) for x in days}
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
        if not (od == b["origin_date"] == ar["origin_date"] == rm["origin_date"]):
            raise RuntimeError(f"ORIGIN_MISMATCH:{td}")
        vals = [int(t["actual_up"]), int(b["actual_up"]), int(ar["actual_up"]), int(rm["actual_up"])]
        if len(set(vals)) != 1:
            raise RuntimeError(f"ACTUAL_MISMATCH:{td}:{vals}")
        if od not in close or td not in close:
            raise RuntimeError(f"CLOSE_MISSING:{od}:{td}")
        ret = math.log(close[td] / close[od])
        ctx = contexts[od]
        out.append({
            "origin_date": od,
            "target_date": td,
            "year": int(td[:4]),
            "actual_up": vals[0],
            "target_log_return": float(ret),
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
    au = tp + fn
    ad = tn + fp
    pu = tp + fp
    precision = tp / pu if pu else None
    recall = tp / au if au else None
    fpr = fp / ad if ad else None
    down_recall = tn / ad if ad else None
    bal = None if recall is None or down_recall is None else (recall + down_recall) / 2.0
    wealth = 100.0
    for r in rows:
        if r["pred_up"] == 1:
            wealth *= math.exp(r["target_log_return"])
    return {
        "n": n,
        "actual_up": au,
        "actual_down": ad,
        "predicted_up": pu,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "up_precision": precision,
        "up_recall": recall,
        "false_up_fpr": fpr,
        "down_recall": down_recall,
        "balanced_accuracy": bal,
        "accuracy": (tp + tn) / n if n else None,
        "coverage": pu / n if n else None,
        "strategy_100usd_no_cost": wealth,
        "strategy_return_pct_no_cost": (wealth / 100.0 - 1.0) * 100.0,
    }


def fixed_share_run(rows, alpha: float, eta: float, end_year: int | None = None):
    k = len(EXPERTS)
    w = np.ones(k, dtype=float) / k
    scored = []
    for r in rows:
        if end_year is not None and r["year"] > end_year:
            break
        x = np.array([float(r[e]) for e in EXPERTS], dtype=float)
        score = float(np.dot(w, x) / np.sum(w))
        pred = int(score >= THRESHOLD)
        z = dict(r)
        z["score"] = score
        z["pred_up"] = pred
        z["weights_before"] = {e: float(v) for e, v in zip(EXPERTS, w / np.sum(w))}
        scored.append(z)

        y = int(r["actual_up"])
        loss = (x != y).astype(float)
        post = w * np.exp(-eta * loss)
        total = float(np.sum(post))
        if not math.isfinite(total) or total <= 0:
            raise RuntimeError("BAD_WEIGHT_TOTAL")
        # Herbster-Warmuth style fixed share: retain (1-alpha) own mass and
        # redistribute alpha of total mass uniformly across all experts.
        w = (1.0 - alpha) * post + (alpha / k) * total
        w = w / np.sum(w)
    return scored


def score_router_year(base, eval_rows, history):
    out = []
    hist = [dict(r) for r in history]
    for br in eval_rows:
        row = dict(br)
        eligible = []
        for ex in base.DIRECT_UP_EXPERTS:
            if row[ex] != 1:
                continue
            st = base.router_stats(hist, ex, row["legacy_bucket"])
            if st is None:
                continue
            if st["n_up"] < 30 or st["precision"] <= 0.50 or st["fpr"] >= 0.50:
                continue
            eligible.append((ex, st))
        if eligible:
            eligible.sort(key=lambda x: (
                -x[1]["lcb"], x[1]["fpr"], -x[1]["precision"], base.ROUTER_TIE_ORDER[x[0]]
            ))
            ex, st = eligible[0]
            row["pred_up"] = 1
            row["selected_expert"] = ex
        else:
            row["pred_up"] = 0
            row["selected_expert"] = ""
        out.append(row)
        hist.append(dict(br))
    return out, hist


def baseline_router(base, rows):
    by = defaultdict(list)
    for r in rows:
        by[r["year"]].append(r)

    s24, h24 = score_router_year(base, by[2024], by[2023])
    s25, h25 = score_router_year(base, by[2025], h24)
    s26, _ = score_router_year(base, by[2026], h25)

    m24 = metrics(s24)
    m25 = metrics(s25)
    m26 = metrics(s26)
    if (m24["predicted_up"], m24["tp"], m24["fp"]) != (42, 26, 16):
        raise RuntimeError(f"ROUTER_2024_AUTHORITY_MISMATCH:{m24}")
    if (m25["predicted_up"], m25["tp"], m25["fp"]) != (37, 27, 10):
        raise RuntimeError(f"ROUTER_2025_AUTHORITY_MISMATCH:{m25}")
    return {"2024": m24, "2025": m25, "2026": m26}


def subset(scored, years):
    ys = set(years)
    return [r for r in scored if r["year"] in ys]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    base = load_module("router_authority", args.base)
    rows = build_rows(base)
    years = sorted(set(r["year"] for r in rows))

    # Development selection uses ONLY 2022-2023. 2024 is untouched validation.
    grid = []
    for alpha in ALPHAS:
        for eta in ETAS:
            s = fixed_share_run(rows, alpha, eta, end_year=2023)
            dev = subset(s, [2022, 2023])
            m = metrics(dev)
            grid.append({"alpha": alpha, "eta": eta, "threshold": THRESHOLD, "dev_2022_2023": m})

    def key(g):
        m = g["dev_2022_2023"]
        return (
            -(m["balanced_accuracy"] if m["balanced_accuracy"] is not None else -1.0),
            -(m["up_recall"] if m["up_recall"] is not None else -1.0),
            -(m["up_precision"] if m["up_precision"] is not None else -1.0),
            g["alpha"],
            g["eta"],
        )
    grid_sorted = sorted(grid, key=key)
    selected = grid_sorted[0]
    alpha = selected["alpha"]
    eta = selected["eta"]

    # Freeze selected hyperparameters before any 2024/2025/2026 metric is read.
    full = fixed_share_run(rows, alpha, eta)
    annual = {}
    for y in [2022, 2023, 2024, 2025, 2026]:
        annual[str(y)] = metrics(subset(full, [y]))

    validation_2024 = annual["2024"]
    locked_2025 = annual["2025"]
    stress_2026 = annual["2026"]

    baseline = baseline_router(base, rows)

    # Diagnostics: end-of-year weights from the frozen online path.
    weight_snapshots = {}
    for y in [2023, 2024, 2025, 2026]:
        yr = subset(full, [y])
        if yr:
            last = yr[-1]
            weight_snapshots[str(y)] = last["weights_before"]

    result = {
        "identity": IDENTITY,
        "status": "RESEARCH_ONLY_NO_PROMOTION",
        "data_years_available": years,
        "protocol": {
            "experts": EXPERTS,
            "online_update": "predict first, observe outcome, multiplicative loss update, fixed-share redistribution",
            "expert_loss": "0-1 directional loss",
            "threshold": THRESHOLD,
            "candidate_alphas": ALPHAS,
            "candidate_etas": ETAS,
            "hyperparameter_selection": "highest balanced accuracy on 2022-2023 only; tie higher UP recall, higher precision, then smaller alpha/eta",
            "validation": "2024 untouched during selection",
            "locked_test": "2025 untouched during selection",
            "stress_only": "2026 through 2026-08-31",
            "no_2025_tuning": True,
            "no_2026_tuning": True,
        },
        "selected": selected,
        "top_grid": grid_sorted[:10],
        "fixed_share": {
            "2022": annual["2022"],
            "2023": annual["2023"],
            "2024_validation": validation_2024,
            "2025_locked": locked_2025,
            "2026_stress": stress_2026,
            "weight_snapshots": weight_snapshots,
        },
        "router_v2_baseline": baseline,
        "governance": {
            "random_split": False,
            "future_leakage": False,
            "canonical_branch_modified": False,
            "production_writes": False,
            "runtime_promotion": False,
        },
    }

    out = args.out / "GOLD_CONTROL_DYNAMIC_FIXED_SHARE_ROUTER_V1_RESULT_2026-09-24.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
