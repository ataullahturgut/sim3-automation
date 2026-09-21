from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import warnings
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import psycopg
from statsmodels.tsa.arima.model import ARIMA

IDENTITY = "DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESEARCH"
XAU_SERIES = "XAU_STAKTRAKR_RESEARCH_DAILY_R1"
DJIA_SERIES = "DJIA_FRED"

WINDOWS = (50, 75, 100, 125, 150, 175, 200, 225, 250)
SEED = 2008
N_GAUSS = 10
N_GCOMP = 11
N_HIDDEN = N_GAUSS + N_GCOMP
LEARNING_RATE = 0.05
MOMENTUM = 0.50
MAX_EPOCHS = 1500
PATIENCE = 200
MIN_DELTA = 1e-10
INIT_BOUND = 0.30
BOOT_REPS = 500
BOOT_BLOCK = 4


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
    gold_level: float
    prev_gold_level: float


def database_url() -> str:
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
        and observation_ts >= '2016-08-01'::timestamptz
        and observation_ts <  '2026-01-03'::timestamptz
      order by observation_ts::date, retrieved_at desc, id desc
    ),
    j as (
      select distinct on (observation_ts::date)
             observation_ts::date as d, value
      from observations
      where series_id = %s
        and observation_ts >= '2016-08-01'::timestamptz
        and observation_ts <  '2026-01-03'::timestamptz
      order by observation_ts::date, retrieved_at desc, id desc
    )
    select x.d, x.value, j.value
    from x join j using(d)
    order by x.d
    """
    with psycopg.connect(database_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(sql, (XAU_SERIES, DJIA_SERIES))
            rows = cur.fetchall()

    out: list[tuple[date, float, float]] = []
    for d, gold, djia in rows:
        g = float(gold)
        j = float(djia)
        if not (math.isfinite(g) and g > 0 and math.isfinite(j) and j > 0):
            raise RuntimeError(f"INVALID_SOURCE_VALUE:{d}")
        out.append((d, g, j))
    if not out:
        raise RuntimeError("NO_COMMON_DAILY_ROWS")
    return out


def build_weekly(daily: list[tuple[date, float, float]]) -> list[WeekRow]:
    buckets: dict[date, list[tuple[date, float, float]]] = {}
    for d, gold, djia in daily:
        if d.weekday() > 4:
            continue
        ws = d - timedelta(days=d.weekday())
        buckets.setdefault(ws, []).append((d, gold, djia))

    out: list[WeekRow] = []
    for ws in sorted(buckets):
        arr = sorted(buckets[ws], key=lambda z: z[0])
        d, gold, djia = arr[-1]
        we = ws + timedelta(days=4)
        if d > we:
            raise RuntimeError(f"COMMON_DATE_AFTER_NOMINAL_FRIDAY:{ws}:{d}")
        out.append(WeekRow(ws, we, d, gold, djia))
    if len(out) < 400:
        raise RuntimeError(f"LONG_HISTORY_WEEKLY_PANEL_TOO_SHORT:{len(out)}")
    return out


def weekly_hash(rows: list[WeekRow]) -> str:
    raw = "\n".join(
        f"{r.week_start.isoformat()}|{r.week_end.isoformat()}|{r.common_date.isoformat()}|"
        f"{r.gold:.12f}|{r.djia:.12f}"
        for r in rows
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def make_samples(rows: list[WeekRow]) -> list[Sample]:
    gold = np.array([r.gold for r in rows], dtype=float)
    djia = np.array([r.djia for r in rows], dtype=float)
    dg = np.full(len(rows), np.nan)
    dd = np.full(len(rows), np.nan)
    dg[1:] = np.diff(gold)
    dd[1:] = np.diff(djia)

    out: list[Sample] = []
    for t in range(5, len(rows)):
        feats = tuple(
            [float(dg[t-k]) for k in range(1, 5)]
            + [float(dd[t-k]) for k in range(1, 5)]
        )
        if not all(math.isfinite(v) for v in feats):
            continue
        y = float(dg[t])
        prev_y = float(dg[t-1])
        if not (math.isfinite(y) and math.isfinite(prev_y)):
            continue
        out.append(
            Sample(
                week_end=rows[t].week_end,
                x=feats,
                y=y,
                prev_y=prev_y,
                gold_level=float(rows[t].gold),
                prev_gold_level=float(rows[t-1].gold),
            )
        )
    return out


def scale_x_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lo = np.min(x, axis=0)
    hi = np.max(x, axis=0)
    return lo, hi - lo


def scale_x_apply(x: np.ndarray, lo: np.ndarray, span: np.ndarray) -> np.ndarray:
    out = np.zeros_like(x, dtype=float)
    mask = span > 0
    out[:, mask] = -1.0 + 2.0 * (x[:, mask] - lo[mask]) / span[mask]
    return out


def scale_y_fit(y: np.ndarray) -> tuple[float, float]:
    lo, hi = float(np.min(y)), float(np.max(y))
    if not hi > lo:
        raise RuntimeError("CONSTANT_TARGET_WINDOW")
    return lo, hi


def scale_y_apply(y: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return 0.1 + 0.8 * (y - lo) / (hi - lo)


def inverse_y(v: float, lo: float, hi: float) -> float:
    return lo + ((v - 0.1) / 0.8) * (hi - lo)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def hidden_and_grad(zg: np.ndarray, zc: np.ndarray):
    hg = np.exp(-(zg * zg))
    hc_base = np.exp(-(zc * zc))
    hc = 1.0 - hc_base
    dg = -2.0 * zg * hg
    dc = 2.0 * zc * hc_base
    return hg, hc, dg, dc


def init_params(n_in: int):
    rng = np.random.default_rng(SEED)
    Wg = rng.uniform(-INIT_BOUND, INIT_BOUND, size=(n_in, N_GAUSS))
    bg = rng.uniform(-INIT_BOUND, INIT_BOUND, size=N_GAUSS)
    Wc = rng.uniform(-INIT_BOUND, INIT_BOUND, size=(n_in, N_GCOMP))
    bc = rng.uniform(-INIT_BOUND, INIT_BOUND, size=N_GCOMP)
    v = rng.uniform(-INIT_BOUND, INIT_BOUND, size=N_HIDDEN)
    b = np.array(rng.uniform(-INIT_BOUND, INIT_BOUND))
    return [Wg, bg, Wc, bc, v, b]


def forward(xs: np.ndarray, params):
    Wg, bg, Wc, bc, v, b = params
    zg = xs @ Wg + bg
    zc = xs @ Wc + bc
    hg, hc, dg, dc = hidden_and_grad(zg, zc)
    H = np.concatenate([hg, hc], axis=1)
    s = H @ v + b
    out = sigmoid(s)
    return out, (hg, hc, dg, dc)


def train_ward(xs: np.ndarray, ys: np.ndarray):
    params = init_params(xs.shape[1])
    velocities = [np.zeros_like(p) for p in params]
    best_loss = float("inf")
    best = None
    bad = 0
    epochs = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        epochs = epoch
        out, cache = forward(xs, params)
        err = out - ys
        loss = float(np.mean(err * err))
        if not math.isfinite(loss):
            raise RuntimeError("WARD_TRAIN_NONFINITE_LOSS")

        if loss < best_loss - MIN_DELTA:
            best_loss = loss
            best = [p.copy() for p in params]
            bad = 0
        else:
            bad += 1
            if bad >= PATIENCE:
                break

        hg, hc, dg, dc = cache
        Wg, bg, Wc, bc, v, b = params
        n = len(ys)
        ds = (2.0 / n) * err * out * (1.0 - out)

        H = np.concatenate([hg, hc], axis=1)
        gv = H.T @ ds
        gb_out = np.array(np.sum(ds))

        dh = ds[:, None] * v[None, :]
        dzg = dh[:, :N_GAUSS] * dg
        dzc = dh[:, N_GAUSS:] * dc

        gWg = xs.T @ dzg
        gbg = np.sum(dzg, axis=0)
        gWc = xs.T @ dzc
        gbc = np.sum(dzc, axis=0)
        grads = [gWg, gbg, gWc, gbc, gv, gb_out]

        for i, (p, g) in enumerate(zip(params, grads)):
            velocities[i] = MOMENTUM * velocities[i] - LEARNING_RATE * g
            p += velocities[i]

    if best is None:
        raise RuntimeError("WARD_TRAIN_NO_BEST_STATE")
    return best_loss, epochs, best


def ward_forecast(train: list[Sample], target: Sample, window: int):
    if len(train) < window:
        return None
    tw = train[-window:]
    X = np.array([s.x for s in tw], dtype=float)
    y = np.array([s.y for s in tw], dtype=float)
    x0 = np.array(target.x, dtype=float).reshape(1, -1)

    xlo, xspan = scale_x_fit(X)
    Xs = scale_x_apply(X, xlo, xspan)
    x0s = scale_x_apply(x0, xlo, xspan)
    ylo, yhi = scale_y_fit(y)
    ys = scale_y_apply(y, ylo, yhi)

    loss, epochs, params = train_ward(Xs, ys)
    pred_scaled, _ = forward(x0s, params)
    pred = inverse_y(float(pred_scaled[0]), ylo, yhi)

    return {
        "target_week_end": target.week_end.isoformat(),
        "rolling_window": window,
        "predicted_delta_gold": pred,
        "actual_delta_gold": target.y,
        "forecast_direction": "UP" if pred > 0.0 else "DOWN",
        "actual_direction": "UP" if target.y > 0.0 else "DOWN",
        "previous_direction": "UP" if target.prev_y > 0.0 else "DOWN",
        "training_mse_scaled": loss,
        "training_epochs": epochs,
        "train_start_week_end": tw[0].week_end.isoformat(),
        "train_end_week_end": tw[-1].week_end.isoformat(),
    }


def arima_forecast(train: list[Sample], window: int):
    if len(train) < window:
        return None
    tw = train[-window:]
    levels = np.array([tw[0].prev_gold_level] + [s.gold_level for s in tw], dtype=float)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit = ARIMA(
                levels,
                order=(4, 1, 2),
                trend=None,
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit()
        next_level = float(np.asarray(fit.forecast(steps=1))[0])
        delta = next_level - float(levels[-1])
        return delta if math.isfinite(delta) else None
    except Exception:
        return None


def forecasts_for_year(samples: list[Sample], window: int, year: int, include_arima: bool):
    rows = []
    for i, target in enumerate(samples):
        if target.week_end.year != year:
            continue
        train = samples[:i]
        f = ward_forecast(train, target, window)
        if f is None:
            continue
        if include_arima:
            ap = arima_forecast(train, window)
            f["arima_predicted_delta_gold"] = ap
            f["arima_direction"] = None if ap is None else ("UP" if ap > 0 else "DOWN")
        rows.append(f)
    return rows


def pt_test(rows, forecast_key="forecast_direction"):
    n = len(rows)
    if n < 2:
        return {"statistic": None, "pvalue_two_sided": None}
    y = np.array([r["actual_direction"] == "UP" for r in rows], dtype=float)
    p = np.array([r[forecast_key] == "UP" for r in rows], dtype=float)
    hit = float(np.mean(y == p))
    py, pp = float(np.mean(y)), float(np.mean(p))
    pstar = py * pp + (1.0 - py) * (1.0 - pp)
    v = pstar * (1.0 - pstar) / n
    w = (
        ((2.0 * py - 1.0) ** 2) * pp * (1.0 - pp)
        + ((2.0 * pp - 1.0) ** 2) * py * (1.0 - py)
    ) / n
    den = v - w
    if den <= 0:
        return {"statistic": None, "pvalue_two_sided": None, "expected_accuracy": pstar}
    stat = (hit - pstar) / math.sqrt(den)
    pval = math.erfc(abs(stat) / math.sqrt(2.0))
    return {"statistic": stat, "pvalue_two_sided": pval, "expected_accuracy": pstar}


def direction_metrics(rows, forecast_key="forecast_direction"):
    usable = [r for r in rows if r.get(forecast_key) in {"UP", "DOWN"}]
    if not usable:
        return {"n": 0}
    n = len(usable)
    au = sum(r["actual_direction"] == "UP" for r in usable)
    ad = n - au
    tp = sum(r[forecast_key] == "UP" and r["actual_direction"] == "UP" for r in usable)
    tn = sum(r[forecast_key] == "DOWN" and r["actual_direction"] == "DOWN" for r in usable)
    fp = sum(r[forecast_key] == "UP" and r["actual_direction"] == "DOWN" for r in usable)
    fn = sum(r[forecast_key] == "DOWN" and r["actual_direction"] == "UP" for r in usable)
    return {
        "n": n,
        "accuracy": (tp + tn) / n,
        "balanced_accuracy": ((tp / au) + (tn / ad)) / 2 if au and ad else None,
        "actual_up": au,
        "actual_down": ad,
        "forecast_up": tp + fp,
        "forecast_down": tn + fn,
        "up_sensitivity": tp / au if au else None,
        "down_sensitivity": tn / ad if ad else None,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "always_up_accuracy": au / n,
        "always_down_accuracy": ad / n,
        "previous_sign_accuracy": sum(r["previous_direction"] == r["actual_direction"] for r in usable) / n,
        "pt_test": pt_test(usable, forecast_key),
    }


def ward_metrics(rows):
    m = direction_metrics(rows)
    if not rows:
        return m
    e = np.array([r["predicted_delta_gold"] - r["actual_delta_gold"] for r in rows], dtype=float)
    m["rmse_delta_gold"] = float(np.sqrt(np.mean(e * e)))
    m["mae_delta_gold"] = float(np.mean(np.abs(e)))
    m["mean_predicted_delta_gold"] = float(np.mean([r["predicted_delta_gold"] for r in rows]))
    return m


def bootstrap_accuracy(rows):
    if not rows:
        return {"reps": 0}
    hits = np.array([r["forecast_direction"] == r["actual_direction"] for r in rows], dtype=float)
    n = len(hits)
    starts = np.arange(max(1, n - BOOT_BLOCK + 1))
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(BOOT_REPS):
        parts = []
        count = 0
        while count < n:
            s = int(rng.choice(starts))
            part = hits[s:s + BOOT_BLOCK]
            parts.append(part)
            count += len(part)
        sample = np.concatenate(parts)[:n]
        vals.append(float(np.mean(sample)))
    return {
        "reps": BOOT_REPS,
        "block_length_weeks": BOOT_BLOCK,
        "seed": SEED,
        "mean_accuracy": float(np.mean(vals)),
        "std_accuracy": float(np.std(vals, ddof=1)),
        "p05_accuracy": float(np.quantile(vals, 0.05)),
        "p95_accuracy": float(np.quantile(vals, 0.95)),
    }


def source_audit(panel: list[WeekRow], samples: list[Sample]):
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
        "y2023_samples": sum(s.week_end.year == 2023 for s in samples),
        "y2024_samples": sum(s.week_end.year == 2024 for s in samples),
        "y2025_samples": sum(s.week_end.year == 2025 for s in samples),
        "pre2025_samples": sum(s.week_end.year <= 2024 for s in samples),
        "panel_sha256": weekly_hash(panel),
        "xau_data_class": "APPROVED_RESEARCH_ONLY_NOT_PIT",
        "evidence_class": "RETROSPECTIVE_RECONSTRUCTION",
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
    }


def write_json(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows):
    if not rows:
        raise RuntimeError(f"NO_ROWS_TO_WRITE:{path}")
    fields = []
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


def selection_key(item):
    m = item["metrics_common_2023"]
    pt = m["pt_test"]["statistic"]
    ptv = -1e99 if pt is None else float(pt)
    bal = -1e99 if m["balanced_accuracy"] is None else float(m["balanced_accuracy"])
    return (-m["accuracy"], -bal, -ptv, item["rolling_window"])


def stage_pre2025(outdir: Path):
    daily = load_daily_common()
    panel = build_weekly(daily)
    samples = make_samples(panel)
    audit = source_audit(panel, samples)
    outdir.mkdir(parents=True, exist_ok=True)

    by_window = {}
    for w in WINDOWS:
        by_window[w] = forecasts_for_year(samples, w, 2023, include_arima=False)
        if not by_window[w]:
            raise RuntimeError(f"NO_2023_FORECASTS_WINDOW:{w}")

    common = set(r["target_week_end"] for r in by_window[WINDOWS[0]])
    for w in WINDOWS[1:]:
        common &= {r["target_week_end"] for r in by_window[w]}
    common = sorted(common)
    if len(common) < 45:
        raise RuntimeError(f"COMMON_2023_SUPPORT_TOO_SMALL:{len(common)}")

    ranking = []
    for w in WINDOWS:
        rows = [r for r in by_window[w] if r["target_week_end"] in common]
        ranking.append({"rolling_window": w, "metrics_common_2023": ward_metrics(rows)})
    ranking.sort(key=selection_key)
    selected = int(ranking[0]["rolling_window"])

    y2023 = [r for r in by_window[selected] if r["target_week_end"] in common]
    y2024 = forecasts_for_year(samples, selected, 2024, include_arima=True)
    if len(y2024) < 50:
        raise RuntimeError(f"2024_FORECAST_COUNT_UNEXPECTED:{len(y2024)}")

    m23 = ward_metrics(y2023)
    m24 = ward_metrics(y2024)
    ar24 = direction_metrics(y2024, "arima_direction")
    b23 = bootstrap_accuracy(y2023)
    b24 = bootstrap_accuracy(y2024)

    config = {
        "identity": IDENTITY,
        "selected_window": selected,
        "selection_year": 2023,
        "validation_year": 2024,
        "candidate_windows": list(WINDOWS),
        "selection_rule": "MAX_PPS_THEN_BALANCED_THEN_PT_STAT_THEN_SMALLER_WINDOW",
        "architecture": {
            "inputs": 8,
            "ward_hidden_slabs": [
                {"activation": "gaussian", "neurons": N_GAUSS},
                {"activation": "gaussian_complement", "neurons": N_GCOMP},
            ],
            "hidden_total": N_HIDDEN,
            "output": "logistic_inverse_scaled_to_delta_gold",
        },
        "scaling": {"inputs": "rolling_minmax_-1_1", "target": "rolling_minmax_0.1_0.9"},
        "training": {
            "algorithm": "full_batch_backprop_gradient_descent_with_momentum",
            "learning_rate": LEARNING_RATE,
            "momentum": MOMENTUM,
            "max_epochs": MAX_EPOCHS,
            "patience": PATIENCE,
            "min_delta": MIN_DELTA,
            "weight_init": f"uniform[-{INIT_BOUND},{INIT_BOUND}]",
            "seed": SEED,
        },
        "panel_sha256": audit["panel_sha256"],
        "direction_rule": "UP_IFF_PREDICTED_DELTA_GOLD_GT_0",
        "frozen_before_2025": True,
        "exact_parisi_2008_replication_claim": False,
    }

    result = {
        "identity": IDENTITY,
        "stage": "PRE2025_CONFIG_AND_2024_VALIDATION_FROZEN",
        "source_audit": audit,
        "selection_support_2023": {
            "n": len(common),
            "first_target_week_end": common[0],
            "last_target_week_end": common[-1],
        },
        "ranking_2023": ranking,
        "selected_window": selected,
        "selected_2023_metrics": m23,
        "selected_2023_bootstrap": b23,
        "unchanged_2024_metrics": m24,
        "unchanged_2024_arima_412_metrics": ar24,
        "unchanged_2024_bootstrap": b24,
        "post_2024_retune": False,
        "post_result_retune": False,
    }

    write_json(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_SOURCE_AUDIT_2026-09-21.json", audit)
    write_json(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_FROZEN_CONFIG_2026-09-21.json", config)
    write_json(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_PRE2025_RESULT_2026-09-21.json", result)
    write_csv(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_2023_SELECTED_FORECASTS_2026-09-21.csv", y2023)
    write_csv(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_2024_FORECASTS_2026-09-21.csv", y2024)


def stage_2025(config_path: Path, pre_path: Path, outdir: Path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    pre = json.loads(pre_path.read_text(encoding="utf-8"))

    daily = load_daily_common()
    panel = build_weekly(daily)
    samples = make_samples(panel)
    audit = source_audit(panel, samples)

    if audit["panel_sha256"] != config["panel_sha256"]:
        raise RuntimeError("PANEL_HASH_CHANGED_AFTER_PRE2025_FREEZE")
    if pre["selected_window"] != config["selected_window"]:
        raise RuntimeError("FROZEN_WINDOW_MISMATCH")

    w = int(config["selected_window"])
    rows = forecasts_for_year(samples, w, 2025, include_arima=True)
    if len(rows) < 50:
        raise RuntimeError(f"2025_FORECAST_COUNT_UNEXPECTED:{len(rows)}")

    m = ward_metrics(rows)
    ar = direction_metrics(rows, "arima_direction")
    boot = bootstrap_accuracy(rows)

    result = {
        "identity": IDENTITY,
        "stage": "LOCKED_2025_RETROSPECTIVE_CHALLENGE",
        "selected_window_pre2025": w,
        "unchanged_2024_metrics": pre["unchanged_2024_metrics"],
        "2025_metrics": m,
        "2025_arima_412_metrics": ar,
        "2025_block_bootstrap": boot,
        "panel_sha256_verified": True,
        "post_result_retune": False,
        "exact_parisi_2008_replication_claim": False,
    }

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_2025_FORECASTS_2026-09-21.csv", rows)
    write_json(outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_2025_RESULT_2026-09-21.json", result)

    m24 = pre["unchanged_2024_metrics"]
    ar24 = pre["unchanged_2024_arima_412_metrics"]
    lines = [
        "# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESEARCH RESULT",
        "",
        "**Date:** 2026-09-21",
        f"**Identity:** {IDENTITY}",
        "**Evidence class:** SOURCE_CONSTRAINED_RECONSTRUCTION / NOT_EXACT_PROPRIETARY_REPLICATION",
        "",
        "## Source boundary",
        "",
        "This V2 corrects the removed first adaptation by using the published 4+4 first-difference signal, a genuine two-slab Ward-1 reconstruction, long Gold/DJIA history and period-by-period fixed-window rolling retraining. Exact Parisi-2008 proprietary neuron allocation, activation/scaling selection, rolling-size grid and training internals remain unproven; no exact-replication claim is made.",
        "",
        "## Pre-2025 frozen selection",
        "",
        f"- selected rolling window = {w} weeks, selected on 2023 only",
        f"- 2023 selected PPS/accuracy = {pre['selected_2023_metrics']['accuracy']:.10f}",
        f"- 2023 selected balanced accuracy = {pre['selected_2023_metrics']['balanced_accuracy']:.10f}",
        "",
        "## Unchanged 2024 validation",
        "",
        f"- n = {m24['n']}",
        f"- accuracy/PPS = {m24['accuracy']:.10f}",
        f"- balanced accuracy = {m24['balanced_accuracy']:.10f}",
        f"- UP sensitivity = {m24['up_sensitivity']:.10f}",
        f"- DOWN sensitivity = {m24['down_sensitivity']:.10f}",
        f"- TP/TN/FP/FN = {m24['tp']}/{m24['tn']}/{m24['fp']}/{m24['fn']}",
        f"- always-UP = {m24['always_up_accuracy']:.10f}",
        f"- previous-sign = {m24['previous_sign_accuracy']:.10f}",
        f"- PT statistic = {m24['pt_test']['statistic']}",
        f"- PT p = {m24['pt_test']['pvalue_two_sided']}",
        f"- ARIMA(4,1,2) n = {ar24['n']}",
        f"- ARIMA(4,1,2) accuracy = {ar24.get('accuracy')}",
        "",
        "No retuning was performed after this 2024 checkpoint.",
        "",
        "## Locked 2025 retrospective challenge",
        "",
        f"- n = {m['n']}",
        f"- actual UP/DOWN = {m['actual_up']}/{m['actual_down']}",
        f"- forecast UP/DOWN = {m['forecast_up']}/{m['forecast_down']}",
        f"- accuracy/PPS = {m['accuracy']:.10f}",
        f"- balanced accuracy = {m['balanced_accuracy']:.10f}",
        f"- UP sensitivity = {m['up_sensitivity']:.10f}",
        f"- DOWN sensitivity = {m['down_sensitivity']:.10f}",
        f"- TP/TN/FP/FN = {m['tp']}/{m['tn']}/{m['fp']}/{m['fn']}",
        f"- always-UP = {m['always_up_accuracy']:.10f}",
        f"- always-DOWN = {m['always_down_accuracy']:.10f}",
        f"- previous-sign = {m['previous_sign_accuracy']:.10f}",
        f"- DeltaGold RMSE = {m['rmse_delta_gold']:.10f}",
        f"- DeltaGold MAE = {m['mae_delta_gold']:.10f}",
        f"- PT statistic = {m['pt_test']['statistic']}",
        f"- PT p = {m['pt_test']['pvalue_two_sided']}",
        f"- block-bootstrap mean accuracy = {boot['mean_accuracy']:.10f}",
        f"- block-bootstrap sd accuracy = {boot['std_accuracy']:.10f}",
        f"- bootstrap 5-95% = {boot['p05_accuracy']:.10f} .. {boot['p95_accuracy']:.10f}",
        f"- ARIMA(4,1,2) n = {ar['n']}",
        f"- ARIMA(4,1,2) accuracy = {ar.get('accuracy')}",
        "",
        "## Governance",
        "",
        "- rolling-window selection used 2023 only;",
        "- 2024 was replayed unchanged and frozen before 2025 scoring;",
        "- 2025 did not select/tune any parameter;",
        "- database writes NONE;",
        "- forecast-ledger writes NONE;",
        "- decision-store writes NONE;",
        "- no runtime promotion and no PR merge are authorized by this result.",
    ]
    (outdir / "GOLD_CONTROL_DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESULT_2026-09-21.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


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
            raise SystemExit("--config and --pre-result required for stage=2025")
        stage_2025(args.config, args.pre_result, args.outdir)


if __name__ == "__main__":
    main()
