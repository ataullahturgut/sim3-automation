#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import vw_midas_msvr_successor_v1 as base
import gold_monthly_challenger_b_pls1_v1 as pls

MODEL_ID = "GOLD_MONTHLY_ADPRR_V1"
FREEZE_FILE = "GOLD_MONTHLY_ADPRR_V1_AUTHORITY_2026-10-02.md"

FEATURE_START = "2010-05"
PRED_START = "2016-04"
DEV_START, DEV_END = "2022-04", "2024-12"
HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

REL_WINDOW = 36
CAL_WINDOW = 36
RECENT_N = 60
ANALOG_K = 15
ANALOG_PSEUDO = 10.0
BETA_A = 3.0
BETA_B = 3.0
STRONG_RECALL_TOL = 0.05
PRICE_AE_TOL = 0.02
THRESHOLDS = (0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.25)
SEED = 20261001

REFS = {
    "ChHHO_ANFIS": {"dev_sumae": 1413.0297794084559, "dev_direction_correct": 23},
    "DE_ABC_RBFNN": {"dev_sumae": 1415.8371290308862, "dev_direction_correct": 25},
    "FULL7_ANN": {"dev_sumae": 1428.8589858125417, "dev_direction_correct": 22},
    "REDUCED4_ANN": {"dev_sumae": 1431.4587, "dev_direction_correct": 24},
    "PLS1_V1": {"dev_sumae": 1420.0291, "dev_direction_correct": 20},
}

def read_invariants(dsn: str) -> dict:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def build_pit_feature_table(bundle, end_month: str) -> pd.DataFrame:
    rows = []
    for target in base.month_range(FEATURE_START, end_month):
        origin = base.month_shift(target, -1)
        gh = bundle.gpr_vintages.get(origin)
        if gh is None or target not in bundle.core_gold or origin not in bundle.core_gold:
            continue
        try:
            x = pls.current8_x_only(bundle, target, gh)
        except Exception:
            continue
        actual = float(bundle.core_gold[target])
        rw = float(bundle.core_gold[origin])
        y_up = int(actual > rw)
        rec = {
            "target": target,
            "origin": origin,
            "actual": actual,
            "rw": rw,
            "actual_log_return": float(math.log(actual / rw)),
            "y_up": y_up,
        }
        for i, v in enumerate(x):
            rec[f"x{i}"] = float(v)
        rows.append(rec)
    df = pd.DataFrame(rows).sort_values("target").reset_index(drop=True)
    if len(df) < 100:
        raise RuntimeError(f"PIT_FEATURE_TABLE_TOO_SMALL n={len(df)}")
    return df

def long_en_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=0.30,
            penalty="elasticnet",
            l1_ratio=0.50,
            solver="saga",
            class_weight="balanced",
            max_iter=5000,
            tol=1e-4,
            random_state=SEED,
        )),
    ])

def recent_l2_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            penalty="l2",
            solver="lbfgs",
            class_weight="balanced",
            max_iter=3000,
            random_state=SEED,
        )),
    ])

def arrays(df: pd.DataFrame):
    feat = [f"x{i}" for i in range(8)]
    return df[feat].to_numpy(float), df["y_up"].to_numpy(int)

def analog_prob(train: pd.DataFrame, test_row: pd.Series) -> float:
    feat = [f"x{i}" for i in range(8)]
    A = train[feat].to_numpy(float)
    x = test_row[feat].to_numpy(float)
    mu = A.mean(axis=0)
    sd = A.std(axis=0)
    sd = np.where(sd > 1e-12, sd, 1.0)
    Z = (A - mu) / sd
    z = (x - mu) / sd
    d = np.sqrt(np.mean((Z - z) ** 2, axis=1))
    k = min(ANALOG_K, len(train))
    idx = np.argpartition(d, k - 1)[:k]
    dd = d[idx]
    pos = dd[dd > 0]
    scale = float(np.median(pos)) if len(pos) else 1.0
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    w = np.exp(-dd / scale)
    y = train["y_up"].to_numpy(float)[idx]
    prior = float(train["y_up"].mean())
    local = float(np.sum(w * y) / np.sum(w)) if float(np.sum(w)) > 0 else prior
    eff = float(np.sum(w))
    return float((eff * local + ANALOG_PSEUDO * prior) / (eff + ANALOG_PSEUDO))

def expert_probs_for_target(feature_df: pd.DataFrame, target: str) -> dict:
    pos = feature_df.index[feature_df["target"] == target].tolist()
    if len(pos) != 1:
        raise RuntimeError(f"TARGET_FEATURE_ROW_NOT_UNIQUE {target} {len(pos)}")
    i = pos[0]
    te = feature_df.loc[i]
    tr = feature_df[feature_df["target"] < target].copy()
    if len(tr) < 60:
        raise RuntimeError(f"EXPERT_HISTORY_TOO_SMALL target={target} n={len(tr)}")
    Xtr, ytr = arrays(tr)
    Xte = te[[f"x{i}" for i in range(8)]].to_numpy(float).reshape(1, -1)

    m1 = long_en_model()
    m1.fit(Xtr, ytr)
    p1 = float(m1.predict_proba(Xte)[0, 1])

    rr = tr.tail(RECENT_N).copy()
    Xr, yr = arrays(rr)
    m2 = recent_l2_model()
    m2.fit(Xr, yr)
    p2 = float(m2.predict_proba(Xte)[0, 1])

    p3 = analog_prob(tr, te)
    return {
        "p_LONG_EN": p1,
        "p_RECENT60_L2": p2,
        "p_LOCAL_ANALOG": p3,
    }

def precompute_pls_rows(bundle, targets: list[str]) -> dict[str, dict]:
    out = {}
    for j, target in enumerate(targets, 1):
        row = pls.forecast_one(bundle, target)
        out[target] = row
        if j % 12 == 0 or j == len(targets):
            print(f"PLS_PRECOMPUTE {j}/{len(targets)} target={target}", flush=True)
    return out

def build_prequential_expert_ledger(feature_df: pd.DataFrame, pls_rows: dict[str, dict]) -> pd.DataFrame:
    rows = []
    targets = [t for t in feature_df["target"].tolist() if t >= PRED_START and t in pls_rows]
    for j, target in enumerate(targets, 1):
        te = feature_df[feature_df.target == target].iloc[0]
        probs = expert_probs_for_target(feature_df, target)
        prow = pls_rows[target]
        r_anchor = float(prow["pred_log_return_gold"])
        rec = {
            "target": target,
            "origin": prow["origin"],
            "actual": float(prow["actual"]),
            "rw": float(prow["rw"]),
            "y_up": int(float(prow["actual"]) > float(prow["rw"])),
            "r_anchor": r_anchor,
            "pls_forecast": float(prow["forecast"]),
            "pls_pred_up": int(r_anchor >= 0.0),
            **probs,
        }
        rows.append(rec)
        if j % 12 == 0 or j == len(targets):
            print(f"EXPERT_PRECOMPUTE {j}/{len(targets)} target={target}", flush=True)
    led = pd.DataFrame(rows).sort_values("target").reset_index(drop=True)
    return led

def side_reliability(history: pd.DataFrame, pcol: str, current_p: float) -> tuple[float, int, int]:
    side = int(current_p >= 0.5)
    h = history.tail(REL_WINDOW).copy()
    if h.empty:
        return 0.5, 0, 0
    pred = (h[pcol].to_numpy(float) >= 0.5).astype(int)
    y = h["y_up"].to_numpy(int)
    mask = pred == side
    calls = int(mask.sum())
    correct = int(np.sum(pred[mask] == y[mask])) if calls else 0
    rel = float((correct + BETA_A) / (calls + BETA_A + BETA_B))
    return rel, calls, correct

def attach_rescue_scores(ledger: pd.DataFrame) -> pd.DataFrame:
    q = ledger.copy()
    pcols = ["p_LONG_EN", "p_RECENT60_L2", "p_LOCAL_ANALOG"]
    scores = []
    detail = []
    for i, r in q.iterrows():
        hist = q.iloc[max(0, i - REL_WINDOW):i].copy()
        num = 0.0
        den = 0.0
        d = {}
        for pc in pcols:
            p = float(r[pc])
            rel, calls, correct = side_reliability(hist, pc, p)
            edge = max(2.0 * rel - 1.0, 0.0)
            conf = 2.0 * p - 1.0
            num += edge * conf
            den += edge
            key = pc.replace("p_", "")
            d[f"rel_{key}"] = rel
            d[f"rel_calls_{key}"] = calls
            d[f"rel_correct_{key}"] = correct
            d[f"edge_{key}"] = edge
        score = float(num / den) if den > 1e-12 else 0.0
        scores.append(score)
        detail.append(d)
    q["rescue_score"] = scores
    dd = pd.DataFrame(detail)
    return pd.concat([q.reset_index(drop=True), dd.reset_index(drop=True)], axis=1)

def direction_recall(y: np.ndarray, pred: np.ndarray, side: int) -> float:
    mask = y == side
    if not np.any(mask):
        return 0.0
    return float(np.mean(pred[mask] == side))

def apply_threshold(g: pd.DataFrame, threshold: float | None) -> dict:
    y = g["y_up"].to_numpy(int)
    anchor_r = g["r_anchor"].to_numpy(float)
    anchor_pred = (anchor_r >= 0.0).astype(int)
    score = g["rescue_score"].to_numpy(float)
    final_pred = anchor_pred.copy()
    overridden = np.zeros(len(g), dtype=bool)

    if threshold is not None and np.isfinite(threshold):
        rescue_pred = (score >= 0.0).astype(int)
        cand = (np.abs(score) >= threshold) & (rescue_pred != anchor_pred)
        final_pred[cand] = rescue_pred[cand]
        overridden[cand] = True

    final_r = np.where(final_pred == anchor_pred, anchor_r, np.where(final_pred == 1, np.abs(anchor_r), -np.abs(anchor_r)))
    rw = g["rw"].to_numpy(float)
    actual = g["actual"].to_numpy(float)
    fc = rw * np.exp(final_r)
    ae = np.abs(fc - actual)

    up_rec = direction_recall(y, final_pred, 1)
    down_rec = direction_recall(y, final_pred, 0)
    bal = float(balanced_accuracy_score(y, final_pred))
    acc = float(np.mean(y == final_pred))
    return {
        "n": int(len(g)),
        "sum_abs_error": float(ae.sum()),
        "mae": float(ae.mean()),
        "rmse": float(np.sqrt(np.mean((fc - actual) ** 2))),
        "direction_correct": int(np.sum(y == final_pred)),
        "direction_accuracy_pct": float(acc * 100.0),
        "balanced_accuracy_pct": float(bal * 100.0),
        "up_recall_pct": float(up_rec * 100.0),
        "down_recall_pct": float(down_rec * 100.0),
        "min_side_recall_pct": float(min(up_rec, down_rec) * 100.0),
        "override_count": int(overridden.sum()),
        "_final_pred": final_pred,
        "_final_r": final_r,
        "_forecast": fc,
        "_ae": ae,
        "_overridden": overridden,
    }

def choose_threshold(history: pd.DataFrame) -> dict:
    cal = history.tail(CAL_WINDOW).copy()
    if len(cal) < CAL_WINDOW:
        return {
            "threshold": None,
            "reason": "CAL_HISTORY_TOO_SHORT",
            "strong_side": None,
            "weak_side": None,
            "eligible_n": 0,
        }

    base_m = apply_threshold(cal, None)
    y = cal["y_up"].to_numpy(int)
    base_pred = (cal["r_anchor"].to_numpy(float) >= 0.0).astype(int)
    base_up = direction_recall(y, base_pred, 1)
    base_down = direction_recall(y, base_pred, 0)
    strong_side = 1 if base_up >= base_down else 0
    weak_side = 1 - strong_side
    base_strong = base_up if strong_side == 1 else base_down

    scored = []
    for th in THRESHOLDS:
        m = apply_threshold(cal, th)
        pred = m["_final_pred"]
        strong_rec = direction_recall(y, pred, strong_side)
        weak_rec = direction_recall(y, pred, weak_side)
        eligible = (
            strong_rec + 1e-12 >= base_strong - STRONG_RECALL_TOL
            and m["sum_abs_error"] <= base_m["sum_abs_error"] * (1.0 + PRICE_AE_TOL) + 1e-9
        )
        scored.append({
            "threshold": float(th),
            "eligible": bool(eligible),
            "strong_side": "UP" if strong_side == 1 else "DOWN",
            "weak_side": "DOWN" if strong_side == 1 else "UP",
            "strong_recall": float(strong_rec),
            "weak_recall": float(weak_rec),
            "balanced_accuracy": float(m["balanced_accuracy_pct"] / 100.0),
            "direction_accuracy": float(m["direction_accuracy_pct"] / 100.0),
            "sum_abs_error": float(m["sum_abs_error"]),
            "override_count": int(m["override_count"]),
        })

    elig = [r for r in scored if r["eligible"]]
    if not elig:
        return {
            "threshold": None,
            "reason": "NO_ELIGIBLE_THRESHOLD_KEEP_ANCHOR",
            "strong_side": "UP" if strong_side == 1 else "DOWN",
            "weak_side": "DOWN" if strong_side == 1 else "UP",
            "eligible_n": 0,
            "base_sumae": float(base_m["sum_abs_error"]),
            "base_up_recall": float(base_up),
            "base_down_recall": float(base_down),
            "candidates": scored,
        }
    elig.sort(key=lambda r: (
        -r["weak_recall"],
        -r["balanced_accuracy"],
        r["sum_abs_error"],
        -r["threshold"],
    ))
    best = elig[0]
    return {
        "threshold": float(best["threshold"]),
        "reason": "PRESERVATION_CONSTRAINED_SELECTION",
        "strong_side": best["strong_side"],
        "weak_side": best["weak_side"],
        "eligible_n": len(elig),
        "base_sumae": float(base_m["sum_abs_error"]),
        "base_up_recall": float(base_up),
        "base_down_recall": float(base_down),
        "selected": best,
        "candidates": scored,
    }

def run_router(ledger: pd.DataFrame, start: str, end: str, label: str) -> dict:
    rows = []
    targets = [t for t in ledger["target"].tolist() if start <= t <= end]
    for target in targets:
        i = int(ledger.index[ledger.target == target][0])
        hist = ledger.iloc[:i].copy()
        sel = choose_threshold(hist)
        cur = ledger.iloc[[i]].copy()
        m = apply_threshold(cur, sel["threshold"])
        anchor_m = apply_threshold(cur, None)

        r = cur.iloc[0]
        final_pred = int(m["_final_pred"][0])
        pls_pred = int(r["pls_pred_up"])
        actual_dir = int(r["y_up"])
        overridden = bool(m["_overridden"][0])
        final_fc = float(m["_forecast"][0])
        pls_fc = float(r["pls_forecast"])
        actual = float(r["actual"])
        rw = float(r["rw"])
        final_ae = abs(final_fc - actual)
        pls_ae = abs(pls_fc - actual)

        rows.append({
            "target": target,
            "origin": r["origin"],
            "role": label,
            "actual": actual,
            "rw": rw,
            "pls_forecast": pls_fc,
            "adprr_forecast": final_fc,
            "pls_ae": pls_ae,
            "adprr_ae": final_ae,
            "pls_direction": "UP" if pls_pred else "DOWN",
            "adprr_direction": "UP" if final_pred else "DOWN",
            "actual_direction": "UP" if actual_dir else "DOWN",
            "pls_direction_correct": bool(pls_pred == actual_dir),
            "adprr_direction_correct": bool(final_pred == actual_dir),
            "override": overridden,
            "override_beneficial_direction": bool(overridden and pls_pred != actual_dir and final_pred == actual_dir),
            "override_harmful_direction": bool(overridden and pls_pred == actual_dir and final_pred != actual_dir),
            "override_beneficial_ae": bool(overridden and final_ae < pls_ae - 1e-9),
            "override_harmful_ae": bool(overridden and final_ae > pls_ae + 1e-9),
            "rescue_score": float(r["rescue_score"]),
            "selected_threshold": None if sel["threshold"] is None else float(sel["threshold"]),
            "selection_reason": sel["reason"],
            "strong_side_calibration": sel.get("strong_side"),
            "weak_side_calibration": sel.get("weak_side"),
            "p_LONG_EN": float(r["p_LONG_EN"]),
            "p_RECENT60_L2": float(r["p_RECENT60_L2"]),
            "p_LOCAL_ANALOG": float(r["p_LOCAL_ANALOG"]),
        })

    if len(rows) != len(list(base.month_range(start, end))):
        raise RuntimeError(f"PERIOD_ROWS_MISMATCH {label} got={len(rows)} expected={len(list(base.month_range(start,end)))}")
    return {
        "role": label,
        "rows": rows,
        "metrics": metric_rows(rows, "adprr"),
        "anchor_metrics": metric_rows(rows, "pls"),
        "yearly": yearly(rows, "adprr"),
        "anchor_yearly": yearly(rows, "pls"),
        "threshold_counts": dict(sorted(Counter("KEEP" if r["selected_threshold"] is None else f"{r['selected_threshold']:.2f}" for r in rows).items())),
    }

def metric_rows(rows: list[dict], prefix: str) -> dict:
    fkey = "adprr_forecast" if prefix == "adprr" else "pls_forecast"
    dkey = "adprr_direction_correct" if prefix == "adprr" else "pls_direction_correct"
    a = np.asarray([r["actual"] for r in rows], float)
    f = np.asarray([r[fkey] for r in rows], float)
    rw = np.asarray([r["rw"] for r in rows], float)
    pred = np.asarray([1 if f[i] >= rw[i] else 0 for i in range(len(rows))], int)
    y = np.asarray([1 if a[i] > rw[i] else 0 for i in range(len(rows))], int)
    ae = np.abs(f - a)
    rwae = np.abs(rw - a)
    wi = int(np.argmax(ae))
    up = direction_recall(y, pred, 1)
    down = direction_recall(y, pred, 0)
    return {
        "n": len(rows),
        "sum_abs_error": float(ae.sum()),
        "mae": float(ae.mean()),
        "rmse": float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct": float(np.mean(ae / np.maximum(np.abs(a), 1e-12)) * 100),
        "wape_pct": float(ae.sum() / np.maximum(np.abs(a).sum(), 1e-12) * 100),
        "worst_ae": float(ae[wi]),
        "worst_month": rows[wi]["target"],
        "relative_mae_vs_rw": float(ae.sum() / max(float(rwae.sum()), 1e-12)),
        "direction_correct": int(np.sum(pred == y)),
        "direction_accuracy_pct": float(np.mean(pred == y) * 100),
        "balanced_accuracy_pct": float(balanced_accuracy_score(y, pred) * 100),
        "up_recall_pct": float(up * 100),
        "down_recall_pct": float(down * 100),
        "min_side_recall_pct": float(min(up,down) * 100),
        "override_count": int(sum(bool(r["override"]) for r in rows)) if prefix == "adprr" else 0,
        "direction_rescues": int(sum(bool(r["override_beneficial_direction"]) for r in rows)) if prefix == "adprr" else 0,
        "direction_damages": int(sum(bool(r["override_harmful_direction"]) for r in rows)) if prefix == "adprr" else 0,
        "ae_beneficial_overrides": int(sum(bool(r["override_beneficial_ae"]) for r in rows)) if prefix == "adprr" else 0,
        "ae_harmful_overrides": int(sum(bool(r["override_harmful_ae"]) for r in rows)) if prefix == "adprr" else 0,
    }

def yearly(rows: list[dict], prefix: str) -> dict:
    years = sorted({r["target"][:4] for r in rows})
    return {y: metric_rows([r for r in rows if r["target"].startswith(y)], prefix) for y in years}

def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    source_gate = (
        not bundle.source_checks["missing_required_gpr_origins"]
        and not bundle.source_checks["late_required_gpr_origins"]
        and not bundle.source_checks["missing_required_gpr_lag_month"]
    )
    if not source_gate:
        raise RuntimeError(f"SOURCE_GATE_FAIL {bundle.source_checks}")

    feature_df = build_pit_feature_table(bundle, STRESS_END)
    pls_targets = [t for t in feature_df["target"].tolist() if t >= PRED_START and t <= STRESS_END]
    pls_rows = precompute_pls_rows(bundle, pls_targets)
    ledger = build_prequential_expert_ledger(feature_df, pls_rows)
    ledger = attach_rescue_scores(ledger)

    if ledger[ledger.target < DEV_START].shape[0] < 60:
        raise RuntimeError("PREDEV_LEDGER_TOO_SMALL")

    dev = run_router(ledger, DEV_START, DEV_END, "DEV_SELECTION_AUTHORITY")
    hold = run_router(ledger, HOLDOUT_START, HOLDOUT_END, "LOCKED_REPORT_ONLY")
    stress = run_router(ledger, STRESS_START, STRESS_END, "QUARANTINED_REPORT_ONLY")

    after = read_invariants(dsn)
    same = after == bundle.invariants_before
    if not same:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    comparison = [
        {"model":"ADPRR_V1","sum_abs_error":dev["metrics"]["sum_abs_error"],"direction_correct":dev["metrics"]["direction_correct"]},
        {"model":"PLS1_ANCHOR_REPLAY","sum_abs_error":dev["anchor_metrics"]["sum_abs_error"],"direction_correct":dev["anchor_metrics"]["direction_correct"]},
        *[
            {"model":k,"sum_abs_error":float(v["dev_sumae"]),"direction_correct":int(v["dev_direction_correct"])}
            for k,v in REFS.items() if k!="PLS1_V1"
        ],
    ]
    comparison = sorted(comparison, key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))

    payload = {
        "dev": dev["rows"],
        "holdout_2025": hold["rows"],
        "stress_2026": stress["rows"],
    }
    digest = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

    out = {
        "model_id": MODEL_ID,
        "freeze_file": FREEZE_FILE,
        "scientific_gate": "PASS",
        "contract": {
            "target":"H=1 next-calendar-month average XAU/USD",
            "representation":"CURRENT8",
            "base_anchor":"PLS1 V1 magnitude/sign",
            "direction_experts":["LONG_EN","RECENT60_L2","LOCAL_ANALOG"],
            "side_reliability_window":REL_WINDOW,
            "calibration_window":CAL_WINDOW,
            "beta_prior":[BETA_A,BETA_B],
            "threshold_grid":list(THRESHOLDS),
            "strong_side_recall_tolerance":STRONG_RECALL_TOL,
            "price_ae_tolerance":PRICE_AE_TOL,
            "magnitude_policy":"ABS_PLS1_LOG_RETURN_PRESERVED",
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"LOCKED_REPORT_ONLY",
            "2026_role":"QUARANTINED_REPORT_ONLY",
        },
        "source_checks":bundle.source_checks,
        "feature_table_n":int(len(feature_df)),
        "expert_ledger_n":int(len(ledger)),
        "dev":dev,
        "holdout_2025":hold,
        "stress_2026":stress,
        "frozen_reference_comparison":comparison,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "authority_invariants_unchanged":same,
        "software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},
        "result_payload_sha256":digest,
    }
    Path("GOLD_MONTHLY_ADPRR_V1_RESULT_2026-10-02.json").write_text(
        json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8"
    )

    def metric_line(name,m):
        return (
            f"| {name} | {m['sum_abs_error']:.2f} | {m['direction_correct']}/{m['n']} "
            f"({m['direction_accuracy_pct']:.2f}%) | {m['balanced_accuracy_pct']:.2f}% | "
            f"{m['up_recall_pct']:.2f}% | {m['down_recall_pct']:.2f}% | "
            f"{m['min_side_recall_pct']:.2f}% | {m['override_count']} |"
        )

    lines = [
        "# GOLD MONTHLY — ADPRR-v1 RESULT","",
        "Asymmetric Direction-Preserving Reliability Router: PLS1 price-magnitude anchor + three origin-safe direction experts + side-conditional reliability + preservation-constrained overrides.","",
        "## DEV 2022-04..2024-12","",
        "| Model | ΣAE USD | Direction | Balanced acc | UP recall | DOWN recall | Min-side recall | Overrides |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        metric_line("PLS1 anchor replay",dev["anchor_metrics"]),
        metric_line("ADPRR-v1",dev["metrics"]),
        "",
        f"DEV direction rescues / damages: **{dev['metrics']['direction_rescues']} / {dev['metrics']['direction_damages']}**.",
        f"DEV AE-beneficial / AE-harmful overrides: **{dev['metrics']['ae_beneficial_overrides']} / {dev['metrics']['ae_harmful_overrides']}**.",
        f"DEV threshold counts: \`{json.dumps(dev['threshold_counts'],sort_keys=True)}\`.","",
        "## Reporting only","",
        "| Period | Model | ΣAE USD | Direction | Balanced acc | UP recall | DOWN recall | Overrides |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
        f"| 2025 | PLS1 anchor | {hold['anchor_metrics']['sum_abs_error']:.2f} | {hold['anchor_metrics']['direction_correct']}/12 | {hold['anchor_metrics']['balanced_accuracy_pct']:.2f}% | {hold['anchor_metrics']['up_recall_pct']:.2f}% | {hold['anchor_metrics']['down_recall_pct']:.2f}% | 0 |",
        f"| 2025 | ADPRR-v1 | {hold['metrics']['sum_abs_error']:.2f} | {hold['metrics']['direction_correct']}/12 | {hold['metrics']['balanced_accuracy_pct']:.2f}% | {hold['metrics']['up_recall_pct']:.2f}% | {hold['metrics']['down_recall_pct']:.2f}% | {hold['metrics']['override_count']} |",
        f"| 2026 Jan-Jul | PLS1 anchor | {stress['anchor_metrics']['sum_abs_error']:.2f} | {stress['anchor_metrics']['direction_correct']}/7 | {stress['anchor_metrics']['balanced_accuracy_pct']:.2f}% | {stress['anchor_metrics']['up_recall_pct']:.2f}% | {stress['anchor_metrics']['down_recall_pct']:.2f}% | 0 |",
        f"| 2026 Jan-Jul | ADPRR-v1 | {stress['metrics']['sum_abs_error']:.2f} | {stress['metrics']['direction_correct']}/7 | {stress['metrics']['balanced_accuracy_pct']:.2f}% | {stress['metrics']['up_recall_pct']:.2f}% | {stress['metrics']['down_recall_pct']:.2f}% | {stress['metrics']['override_count']} |",
        "",
        "## Frozen reference frontier (context only)","",
        "| Model | DEV ΣAE | Direction |",
        "|---|---:|---:|",
    ]
    for r in comparison:
        lines.append(f"| {r['model']} | {r['sum_abs_error']:.2f} | {r['direction_correct']}/33 |")
    lines += ["","2025/2026 were not used to alter the frozen ADPRR-v1 specification."]
    Path("GOLD_MONTHLY_ADPRR_V1_RESULT_2026-10-02.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

    pd.DataFrame(dev["rows"]+hold["rows"]+stress["rows"]).to_csv(
        "GOLD_MONTHLY_ADPRR_V1_PREDICTIONS_2026-10-02.csv",index=False
    )

    print("ADPRR_V1_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "dev":dev["metrics"],
        "dev_anchor":dev["anchor_metrics"],
        "holdout_2025":hold["metrics"],
        "stress_2026":stress["metrics"],
        "comparison":comparison,
        "result_payload_sha256":digest,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
