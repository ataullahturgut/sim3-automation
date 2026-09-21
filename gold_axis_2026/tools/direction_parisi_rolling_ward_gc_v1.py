from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import psycopg

IDENTITY = "DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH"
XAU_SERIES = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
DJIA_SERIES = "DJIA_FRED"
WINDOWS = (50, 75, 100)
SEEDS = (11, 29, 47, 71, 101)
HIDDEN = 21
SLAB = 7
LR = 0.01
MAX_EPOCHS = 2000
PATIENCE = 200
MIN_DELTA = 1e-10


@dataclass(frozen=True)
class WeekRow:
    week_start: date
    week_end: date
    common_date: date
    gold: float
    djia: float


@dataclass(frozen=True)
class Sample:
    week_end: date
    x: tuple[float, ...]
    y: float
    prev_y: float


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return value


def load_daily_common() -> list[tuple[date, float, float]]:
    sql = """
    with x as (
      select distinct on (observation_ts::date)
             observation_ts::date as d, value
      from observations
      where series_id = %s
        and observation_ts >= '2022-02-01'::timestamptz
        and observation_ts <  '2026-01-01'::timestamptz
      order by observation_ts::date, retrieved_at desc, id desc
    ),
    j as (
      select distinct on (observation_ts::date)
             observation_ts::date as d, value
      from observations
      where series_id = %s
        and observation_ts >= '2022-02-01'::timestamptz
        and observation_ts <  '2026-01-01'::timestamptz
      order by observation_ts::date, retrieved_at desc, id desc
    )
    select x.d, x.value, j.value
    from x join j using(d)
    order by x.d
    """
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(sql, (XAU_SERIES, DJIA_SERIES))
            rows = cur.fetchall()
    out = []
    for d, g, j in rows:
        gf, jf = float(g), float(j)
        if not (math.isfinite(gf) and gf > 0 and math.isfinite(jf) and jf > 0):
            raise RuntimeError(f"NONFINITE_OR_NONPOSITIVE_SOURCE:{d}")
        out.append((d, gf, jf))
    if not out:
        raise RuntimeError("NO_COMMON_DAILY_ROWS")
    return out


def weekly_panel(daily: list[tuple[date, float, float]]) -> list[WeekRow]:
    by_week: dict[date, list[tuple[date, float, float]]] = {}
    for d, g, j in daily:
        if d.weekday() > 4:
            continue
        ws = d - timedelta(days=d.weekday())
        by_week.setdefault(ws, []).append((d, g, j))

    out = []
    for ws in sorted(by_week):
        arr = sorted(by_week[ws], key=lambda z: z[0])
        d, g, j = arr[-1]
        we = ws + timedelta(days=4)
        if d > we:
            raise RuntimeError(f"COMMON_DATE_AFTER_FRIDAY:{ws}:{d}")
        out.append(WeekRow(ws, we, d, g, j))

    if len(out) < 120:
        raise RuntimeError(f"WEEKLY_PANEL_TOO_SHORT:{len(out)}")
    return out


def panel_hash(rows: list[WeekRow]) -> str:
    raw = "\n".join(
        f"{r.week_start.isoformat()}|{r.week_end.isoformat()}|{r.common_date.isoformat()}|{r.gold:.12f}|{r.djia:.12f}"
        for r in rows
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def make_samples(rows: list[WeekRow]) -> list[Sample]:
    g = np.array([r.gold for r in rows], dtype=float)
    j = np.array([r.djia for r in rows], dtype=float)
    dg = np.full(len(rows), np.nan)
    dj = np.full(len(rows), np.nan)
    dg[1:] = np.diff(g)
    dj[1:] = np.diff(j)

    out = []
    for t in range(5, len(rows)):
        feats = tuple(
            [float(dg[t-k]) for k in range(1, 5)]
            + [float(dj[t-k]) for k in range(1, 5)]
        )
        if not all(math.isfinite(v) for v in feats):
            continue
        y = float(dg[t])
        prev = float(dg[t-1])
        if not (math.isfinite(y) and math.isfinite(prev)):
            continue
        out.append(Sample(rows[t].week_end, feats, y, prev))
    return out


def scale_x_fit(x: np.ndarray):
    lo = np.min(x, axis=0)
    hi = np.max(x, axis=0)
    span = hi - lo
    return lo, hi, span


def scale_x_apply(x: np.ndarray, lo: np.ndarray, span: np.ndarray):
    out = np.zeros_like(x, dtype=float)
    mask = span > 0
    out[:, mask] = -1.0 + 2.0 * (x[:, mask] - lo[mask]) / span[mask]
    return out


def scale_y_fit(y: np.ndarray):
    lo, hi = float(np.min(y)), float(np.max(y))
    if not hi > lo:
        raise RuntimeError("CONSTANT_TARGET_WINDOW")
    return lo, hi


def scale_y_apply(y: np.ndarray, lo: float, hi: float):
    return 0.1 + 0.8 * (y - lo) / (hi - lo)


def inverse_y(v: float, lo: float, hi: float):
    return lo + ((v - 0.1) / 0.8) * (hi - lo)


def sigmoid(z):
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def act_and_grad(z):
    h = np.empty_like(z)
    d = np.empty_like(z)

    g1 = np.exp(-(z[:, :SLAB] ** 2))
    h[:, :SLAB] = g1
    d[:, :SLAB] = -2.0 * z[:, :SLAB] * g1

    g2 = np.exp(-(z[:, SLAB:2*SLAB] ** 2))
    h[:, SLAB:2*SLAB] = 1.0 - g2
    d[:, SLAB:2*SLAB] = 2.0 * z[:, SLAB:2*SLAB] * g2

    t = np.tanh(z[:, 2*SLAB:])
    h[:, 2*SLAB:] = t
    d[:, 2*SLAB:] = 1.0 - t*t
    return h, d


def fit_one(xs: np.ndarray, ys: np.ndarray, seed: int):
    rng = np.random.default_rng(seed)
    n_in = xs.shape[1]
    bnd = math.sqrt(6.0 / (n_in + HIDDEN))
    W = rng.uniform(-bnd, bnd, size=(n_in, HIDDEN))
    b = np.zeros(HIDDEN)
    vbnd = math.sqrt(6.0 / (HIDDEN + 1))
    v = rng.uniform(-vbnd, vbnd, size=HIDDEN)
    c = np.array(0.0)

    params = [W, b, v, c]
    m = [np.zeros_like(p) for p in params]
    vv = [np.zeros_like(p) for p in params]
    best_loss = float("inf")
    best = None
    bad = 0
    beta1, beta2, eps = 0.9, 0.999, 1e-8

    for epoch in range(1, MAX_EPOCHS + 1):
        z = xs @ W + b
        h, dhdz = act_and_grad(z)
        s = h @ v + c
        o = sigmoid(s)
        e = o - ys
        loss = float(np.mean(e*e))
        if not math.isfinite(loss):
            break

        if loss < best_loss - MIN_DELTA:
            best_loss = loss
            best = [p.copy() for p in params]
            bad = 0
        else:
            bad += 1
            if bad >= PATIENCE:
                break

        ds = (2.0 / len(ys)) * e * o * (1.0 - o)
        gv = h.T @ ds
        gc = np.array(np.sum(ds))
        dz = (ds[:, None] * v[None, :]) * dhdz
        gW = xs.T @ dz
        gb = np.sum(dz, axis=0)
        grads = [gW, gb, gv, gc]

        for k, (p, g) in enumerate(zip(params, grads)):
            m[k] = beta1*m[k] + (1-beta1)*g
            vv[k] = beta2*vv[k] + (1-beta2)*(g*g)
            mh = m[k] / (1-beta1**epoch)
            vh = vv[k] / (1-beta2**epoch)
            p -= LR * mh / (np.sqrt(vh) + eps)

    if best is None:
        raise RuntimeError(f"TRAINING_FAILED_SEED:{seed}")
    return best_loss, best


def predict_scaled(xrow: np.ndarray, pars):
    W, b, v, c = pars
    z = xrow @ W + b
    h, _ = act_and_grad(z.reshape(1, -1))
    return float(sigmoid(h[0] @ v + c))


def forecast_origin(train: list[Sample], target: Sample, window: int):
    if len(train) < window:
        return None
    tw = train[-window:]
    X = np.array([s.x for s in tw], dtype=float)
    y = np.array([s.y for s in tw], dtype=float)
    x0 = np.array(target.x, dtype=float).reshape(1, -1)

    xlo, xhi, xspan = scale_x_fit(X)
    Xs = scale_x_apply(X, xlo, xspan)
    x0s = scale_x_apply(x0, xlo, xspan)
    ylo, yhi = scale_y_fit(y)
    ys = scale_y_apply(y, ylo, yhi)

    fits = []
    for seed in SEEDS:
        loss, pars = fit_one(Xs, ys, seed)
        fits.append((loss, seed, pars))
    fits.sort(key=lambda z: (z[0], z[1]))
    loss, seed, pars = fits[0]
    scaled_pred = predict_scaled(x0s[0], pars)
    pred = inverse_y(scaled_pred, ylo, yhi)

    return {
        "target_week_end": target.week_end.isoformat(),
        "rolling_window": window,
        "predicted_delta_gold": pred,
        "actual_delta_gold": target.y,
        "forecast_direction": "UP" if pred > 0 else "DOWN",
        "actual_direction": "UP" if target.y > 0 else "DOWN",
        "previous_direction": "UP" if target.prev_y > 0 else "DOWN",
        "selected_seed": seed,
        "training_mse_scaled": loss,
        "train_start_week_end": tw[0].week_end.isoformat(),
        "train_end_week_end": tw[-1].week_end.isoformat(),
    }


def forecasts_for_year(samples: list[Sample], window: int, year: int):
    out = []
    for i, s in enumerate(samples):
        if s.week_end.year != year:
            continue
        f = forecast_origin(samples[:i], s, window)
        if f is not None:
            out.append(f)
    return out


def pt_test(rows):
    n = len(rows)
    if n < 2:
        return {"statistic": None, "pvalue_two_sided": None}
    y = np.array([r["actual_delta_gold"] > 0 for r in rows], dtype=float)
    p = np.array([r["predicted_delta_gold"] > 0 for r in rows], dtype=float)
    hit = float(np.mean(y == p))
    py, px = float(np.mean(y)), float(np.mean(p))
    pstar = py*px + (1-py)*(1-px)
    v = pstar*(1-pstar)/n
    w = (((2*py-1)**2)*px*(1-px) + ((2*px-1)**2)*py*(1-py))/n
    den = v-w
    if not den > 0:
        return {"statistic": None, "pvalue_two_sided": None, "expected_accuracy": pstar}
    stat = (hit-pstar)/math.sqrt(den)
    pval = math.erfc(abs(stat)/math.sqrt(2.0))
    return {"statistic": stat, "pvalue_two_sided": pval, "expected_accuracy": pstar}


def metrics(rows):
    if not rows:
        return {"n": 0}
    n = len(rows)
    au = sum(r["actual_direction"] == "UP" for r in rows)
    ad = n-au
    tp = sum(r["forecast_direction"] == "UP" and r["actual_direction"] == "UP" for r in rows)
    tn = sum(r["forecast_direction"] == "DOWN" and r["actual_direction"] == "DOWN" for r in rows)
    fp = sum(r["forecast_direction"] == "UP" and r["actual_direction"] == "DOWN" for r in rows)
    fn = sum(r["forecast_direction"] == "DOWN" and r["actual_direction"] == "UP" for r in rows)
    err = np.array([r["predicted_delta_gold"]-r["actual_delta_gold"] for r in rows])
    return {
        "n": n,
        "accuracy": (tp+tn)/n,
        "balanced_accuracy": ((tp/au)+(tn/ad))/2 if au and ad else None,
        "actual_up": au,
        "actual_down": ad,
        "forecast_up": tp+fp,
        "forecast_down": tn+fn,
        "up_sensitivity": tp/au if au else None,
        "down_sensitivity": tn/ad if ad else None,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "always_up_accuracy": au/n,
        "always_down_accuracy": ad/n,
        "previous_sign_accuracy": sum(r["previous_direction"] == r["actual_direction"] for r in rows)/n,
        "rmse_delta_gold": float(np.sqrt(np.mean(err*err))),
        "mae_delta_gold": float(np.mean(np.abs(err))),
        "mean_predicted_delta_gold": float(np.mean([r["predicted_delta_gold"] for r in rows])),
        "pt_test": pt_test(rows),
    }


def write_csv(path: Path, rows):
    if not rows:
        raise RuntimeError(f"NO_ROWS:{path}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


def write_json(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n", encoding="utf-8")


def source_audit(panel, samples):
    return {
        "identity": IDENTITY,
        "xau_series": XAU_SERIES,
        "djia_series": DJIA_SERIES,
        "weekly_bridge": "LATEST_COMMON_COMPLETED_DATE_IN_MONDAY_START_FRIDAY_ENDING_WEEK",
        "target_year_semantic": "NOMINAL_FRIDAY_WEEK_END_YEAR",
        "weekly_rows": len(panel),
        "first_week_end": panel[0].week_end.isoformat(),
        "last_week_end": panel[-1].week_end.isoformat(),
        "sample_rows": len(samples),
        "pre2025_samples": sum(s.week_end.year <= 2024 for s in samples),
        "y2025_samples": sum(s.week_end.year == 2025 for s in samples),
        "panel_sha256": panel_hash(panel),
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
    }


def stage_pre2025(outdir: Path):
    daily = load_daily_common()
    panel = weekly_panel(daily)
    samples = make_samples(panel)
    audit = source_audit(panel, samples)
    outdir.mkdir(parents=True, exist_ok=True)

    by_window = {}
    rows_by_window = {}
    for w in WINDOWS:
        rows = forecasts_for_year(samples, w, 2024)
        if not rows:
            raise RuntimeError(f"NO_2024_FORECASTS_WINDOW:{w}")
        rows_by_window[w] = rows

    common = set(r["target_week_end"] for r in rows_by_window[WINDOWS[0]])
    for w in WINDOWS[1:]:
        common &= set(r["target_week_end"] for r in rows_by_window[w])
    common = sorted(common)
    if len(common) < 20:
        raise RuntimeError(f"COMMON_2024_SUPPORT_TOO_SMALL:{len(common)}")

    ranking = []
    common_rows_by_window = {}
    for w in WINDOWS:
        rows = [r for r in rows_by_window[w] if r["target_week_end"] in common]
        common_rows_by_window[w] = rows
        m = metrics(rows)
        ranking.append({"rolling_window": w, "metrics_common_2024": m})

    def key(item):
        m = item["metrics_common_2024"]
        return (
            -(m["balanced_accuracy"] if m["balanced_accuracy"] is not None else -1),
            -m["accuracy"],
            m["rmse_delta_gold"],
            item["rolling_window"],
        )
    ranking.sort(key=key)
    selected = int(ranking[0]["rolling_window"])
    selected_rows = common_rows_by_window[selected]

    result = {
        "identity": IDENTITY,
        "stage": "PRE2025_WINDOW_SELECTION_FROZEN",
        "source_audit": audit,
        "candidate_windows": list(WINDOWS),
        "selection_support_2024": {
            "n": len(common),
            "first_target_week_end": common[0],
            "last_target_week_end": common[-1],
        },
        "selection_rule": "MAX_BALANCED_ACC_THEN_ACC_THEN_MIN_RMSE_THEN_SMALLER_WINDOW",
        "ranking": ranking,
        "selected_window": selected,
        "selected_metrics_common_2024": metrics(selected_rows),
        "post_result_retune": False,
    }
    config = {
        "identity": IDENTITY,
        "selected_window": selected,
        "panel_sha256": audit["panel_sha256"],
        "architecture": {
            "inputs": 8,
            "hidden_total": 21,
            "slabs": {"gaussian": 7, "gaussian_complement": 7, "tanh": 7},
            "output": "logistic_then_inverse_delta_gold_scale",
        },
        "training": {
            "optimizer": "full_batch_adam",
            "learning_rate": LR,
            "max_epochs": MAX_EPOCHS,
            "patience": PATIENCE,
            "min_delta": MIN_DELTA,
            "seeds": list(SEEDS),
            "seed_selection": "lowest_training_mse_at_each_origin",
        },
        "direction_rule": "UP_IFF_PREDICTED_DELTA_GOLD_GT_0",
        "weekly_bridge": audit["weekly_bridge"],
        "target_year_semantic": audit["target_year_semantic"],
        "frozen_before_2025": True,
    }

    write_json(outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_SOURCE_AUDIT_2026-09-21.json", audit)
    write_json(outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_PRE2025_RESULT_2026-09-21.json", result)
    write_json(outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_FROZEN_CONFIG_2026-09-21.json", config)
    write_csv(outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_PRE2025_SELECTED_FORECASTS_2026-09-21.csv", selected_rows)


def stage_2025(config_path: Path, pre_path: Path, outdir: Path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    daily = load_daily_common()
    panel = weekly_panel(daily)
    samples = make_samples(panel)
    audit = source_audit(panel, samples)
    if audit["panel_sha256"] != config["panel_sha256"]:
        raise RuntimeError("WEEKLY_PANEL_HASH_CHANGED_AFTER_PRE2025_FREEZE")
    w = int(config["selected_window"])
    rows = forecasts_for_year(samples, w, 2025)
    if len(rows) < 50:
        raise RuntimeError(f"2025_WEEKLY_FORECAST_COUNT_UNEXPECTED:{len(rows)}")
    m = metrics(rows)

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_2025_FORECASTS_2026-09-21.csv", rows)
    write_json(
        outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_2025_RESULT_2026-09-21.json",
        {
            "identity": IDENTITY,
            "stage": "LOCKED_2025_RETROSPECTIVE_CHALLENGE",
            "selected_window_pre2025": w,
            "pre2025_selected_metrics_common_2024": pre["selected_metrics_common_2024"],
            "2025_metrics": m,
            "panel_sha256_verified": True,
            "post_result_retune": False,
        },
    )

    pm = pre["selected_metrics_common_2024"]
    lines = [
        "# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH RESULT",
        "",
        "**Date:** 2026-09-21  ",
        f"**Identity:** `{IDENTITY}`  ",
        "**Status:** `EVALUATED / LOCKED_2025_RETROSPECTIVE_COMPLETE / SOURCE_GROUNDED_ADAPTATION / NOT_EXACT_REPLICATION / NOT_RUNTIME`",
        "",
        "## Method identity",
        "",
        "This is the preregistered Gold-Control adaptation of Parisi, Parisi & Díaz (2008), not an exact reproduction of the proprietary 2008 Ward implementation. The source-proven eight-lag first-difference signal and rolling period-by-period retraining are preserved; unrecovered Ward implementation details are explicitly resolved by the frozen GC_V1 adaptation contract.",
        "",
        "## Frozen pre-2025 selection",
        "",
        f"- selected rolling window = {w} weeks",
        f"- common 2024 selection n = {pm['n']}",
        f"- 2024 accuracy = {pm['accuracy']:.10f}",
        f"- 2024 balanced accuracy = {pm['balanced_accuracy']:.10f}",
        f"- 2024 UP sensitivity = {pm['up_sensitivity']:.10f}",
        f"- 2024 DOWN sensitivity = {pm['down_sensitivity']:.10f}",
        f"- 2024 TP/TN/FP/FN = {pm['tp']}/{pm['tn']}/{pm['fp']}/{pm['fn']}",
        f"- 2024 previous-sign accuracy = {pm['previous_sign_accuracy']:.10f}",
        "",
        "The rolling-window choice was frozen from common 2024 support before any 2025 model score was computed.",
        "",
        "## Locked 2025 retrospective challenge",
        "",
        f"- n = {m['n']}",
        f"- accuracy = {m['accuracy']:.10f}",
        f"- balanced accuracy = {m['balanced_accuracy']:.10f}",
        f"- UP sensitivity = {m['up_sensitivity']:.10f}",
        f"- DOWN sensitivity = {m['down_sensitivity']:.10f}",
        f"- TP/TN/FP/FN = {m['tp']}/{m['tn']}/{m['fp']}/{m['fn']}",
        f"- forecasts UP/DOWN = {m['forecast_up']}/{m['forecast_down']}",
        f"- actual UP/DOWN = {m['actual_up']}/{m['actual_down']}",
        f"- always-UP accuracy = {m['always_up_accuracy']:.10f}",
        f"- always-DOWN accuracy = {m['always_down_accuracy']:.10f}",
        f"- previous-sign accuracy = {m['previous_sign_accuracy']:.10f}",
        f"- ΔGold RMSE = {m['rmse_delta_gold']:.10f}",
        f"- ΔGold MAE = {m['mae_delta_gold']:.10f}",
        f"- Pesaran-Timmermann statistic = {m['pt_test']['statistic']}",
        f"- Pesaran-Timmermann two-sided p = {m['pt_test']['pvalue_two_sided']}",
        "",
        "## Governance",
        "",
        "- 2025 was not used for feature, architecture, rolling-window, seed, scaling or sign-threshold selection.",
        "- no post-result retuning was performed.",
        "- no database, forecast-ledger or decision-store writes were performed.",
        "- no automatic runtime promotion is authorized by this retrospective result.",
    ]
    (outdir/"GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESULT_2026-09-21.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["pre2025", "2025"], required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--pre-result", type=Path)
    args = ap.parse_args()

    if args.stage == "pre2025":
        stage_pre2025(args.outdir)
    else:
        if args.config is None or args.pre_result is None:
            raise SystemExit("--config and --pre-result are required for stage=2025")
        stage_2025(args.config, args.pre_result, args.outdir)


if __name__ == "__main__":
    main()
