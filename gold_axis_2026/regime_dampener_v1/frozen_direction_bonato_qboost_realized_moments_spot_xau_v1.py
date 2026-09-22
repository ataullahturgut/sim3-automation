from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import psycopg

IDENTITY = "DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH"
TABLE = "public.xau_intraday_research_cache_5m"
TZ = "America/New_York"
MIN_BARS = 240
HORIZONS = (1, 5, 10)
QUANTILES = tuple(round(0.10 + 0.05 * i, 2) for i in range(17))
STEP_SIZE = 0.1
M_BREAK_INITIAL = 10
M_MAX = 500
MODELS = {
    "AR1_QBOOST": ("lag1_return",),
    "AR1_RM_QBOOST": ("lag1_return", "rv", "rsk"),
}


@dataclass(frozen=True)
class DayRow:
    d: date
    close: float
    n_bars: int
    rv: float
    rsk: float
    lag1_return: float


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v


def load_days() -> list[DayRow]:
    sql = f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
        and observation_ts >= '2020-01-01'::timestamptz
        and observation_ts <  '2026-01-15'::timestamptz
    ),
    intr as (
      select d, observation_ts, close,
             case when prev_close is not null and prev_close > 0
                  then ln(close/prev_close) end as r
      from b
    ),
    daily as (
      select d,
             count(*)::int as n_bars,
             (array_agg(close order by observation_ts desc))[1]::double precision as close,
             coalesce(sum(r*r),0)::double precision as rv,
             coalesce(sum(r*r*r),0)::double precision as r3,
             count(r)::int as m
      from intr
      group by d
    )
    select d, n_bars, close, rv, r3, m
    from daily
    where n_bars >= {MIN_BARS}
    order by d
    """
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(sql)
            raw = cur.fetchall()

    base = []
    for d, n_bars, close, rv, r3, m in raw:
        c = float(close)
        v = float(rv)
        if not (math.isfinite(c) and c > 0 and math.isfinite(v) and v >= 0):
            raise RuntimeError(f"INVALID_DAILY_ROW:{d}")
        if v > 0 and int(m) > 0:
            rsk = math.sqrt(int(m)) * float(r3) / (v ** 1.5)
        else:
            rsk = 0.0
        if not math.isfinite(rsk):
            raise RuntimeError(f"INVALID_RSK:{d}")
        base.append((d, c, int(n_bars), v, rsk))

    if len(base) < 1000:
        raise RuntimeError(f"INSUFFICIENT_RETAINED_DAYS:{len(base)}")

    out: list[DayRow] = []
    prev_close = None
    for d, c, n, rv, rsk in base:
        if prev_close is None:
            lag1 = float("nan")
        else:
            lag1 = math.log(c / prev_close)
        out.append(DayRow(d, c, n, rv, rsk, lag1))
        prev_close = c
    return out


def panel_hash(days: list[DayRow]) -> str:
    s = "\n".join(
        f"{r.d.isoformat()}|{r.close:.12f}|{r.n_bars}|{r.rv:.16g}|{r.rsk:.16g}|{r.lag1_return:.16g}"
        for r in days[1:]
    )
    return hashlib.sha256(s.encode()).hexdigest()


def pinball(y: np.ndarray, pred: np.ndarray, alpha: float) -> float:
    u = y - pred
    return float(np.mean(np.where(u >= 0.0, alpha * u, (alpha - 1.0) * u)))


def fit_qboost(X: np.ndarray, y: np.ndarray, x_new: np.ndarray, alpha: float) -> tuple[float, int]:
    if X.ndim != 2 or len(y) != X.shape[0] or X.shape[0] < 50:
        raise RuntimeError("BAD_QBOOST_TRAIN_SHAPE")
    xm = X.mean(axis=0)
    ym = float(y.mean())
    xc = X - xm
    yd = y - ym
    xnewc = x_new - xm

    init = float(np.median(yd))
    pred = np.full(len(yd), init, dtype=float)
    beta = np.zeros(X.shape[1], dtype=float)

    best_loss = float("inf")
    best_beta = beta.copy()
    best_m = 1
    m_break = M_BREAK_INITIAL

    den = np.sum(xc * xc, axis=0)
    den = np.where(den <= 1e-18, np.nan, den)

    for m in range(1, M_MAX + 1):
        resid = yd - pred
        grad = np.where(resid >= 0.0, alpha, alpha - 1.0)

        gammas = np.zeros(X.shape[1], dtype=float)
        sses = np.full(X.shape[1], np.inf, dtype=float)
        for k in range(X.shape[1]):
            if not math.isfinite(float(den[k])):
                continue
            g = float(np.dot(xc[:, k], grad) / den[k])
            gammas[k] = g
            e = grad - g * xc[:, k]
            sses[k] = float(np.dot(e, e))
        kbest = int(np.argmin(sses))
        if not math.isfinite(float(sses[kbest])):
            break
        inc = STEP_SIZE * gammas[kbest]
        beta[kbest] += inc
        pred += inc * xc[:, kbest]

        loss = pinball(yd, pred, alpha)
        if loss < best_loss - 1e-15:
            best_loss = loss
            best_beta = beta.copy()
            best_m = m

        if m == m_break:
            if best_m <= 0.75 * m_break:
                break
            m_break = min(M_MAX, m_break + 10)

    fc = ym + init + float(np.dot(xnewc, best_beta))
    return fc, best_m


def confusion(y: np.ndarray, pred: np.ndarray) -> dict:
    ay = y > 0
    py = pred > 0
    tp = int(np.sum(ay & py))
    tn = int(np.sum((~ay) & (~py)))
    fp = int(np.sum((~ay) & py))
    fn = int(np.sum(ay & (~py)))
    up_n = int(np.sum(ay))
    dn_n = int(np.sum(~ay))
    up_s = tp / up_n if up_n else None
    dn_s = tn / dn_n if dn_n else None
    bal = (up_s + dn_s) / 2 if up_s is not None and dn_s is not None else None
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(ay == py)),
        "balanced_accuracy": bal,
        "up_sensitivity": up_s,
        "down_sensitivity": dn_s,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "actual_up": up_n, "actual_down": dn_n,
        "forecast_up": int(np.sum(py)), "forecast_down": int(np.sum(~py)),
        "always_up_accuracy": float(np.mean(ay)),
        "always_down_accuracy": float(np.mean(~ay)),
    }


def feature_value(r: DayRow, name: str) -> float:
    return float(getattr(r, name))


def make_forecasts(days: list[DayRow], target_years: set[int]) -> list[dict]:
    out = []
    for h in HORIZONS:
        for i in range(1, len(days) - h):
            target_i = i + h
            target_date = days[target_i].d
            if target_date.year not in target_years:
                continue
            origin = days[i]
            if not math.isfinite(origin.lag1_return):
                continue

            train_idx = [j for j in range(1, i - h + 1) if j + h <= i]
            if len(train_idx) < 250:
                continue

            y_train = np.array(
                [math.log(days[j+h].close / days[j].close) for j in train_idx],
                dtype=float,
            )
            actual = math.log(days[target_i].close / origin.close)

            row = {
                "origin_date": origin.d.isoformat(),
                "target_date": target_date.isoformat(),
                "horizon": h,
                "actual_return": actual,
                "previous_sign_return": origin.lag1_return,
            }

            for model, feats in MODELS.items():
                X = np.array(
                    [[feature_value(days[j], f) for f in feats] for j in train_idx],
                    dtype=float,
                )
                xn = np.array([feature_value(origin, f) for f in feats], dtype=float)
                for a in QUANTILES:
                    fc, mstar = fit_qboost(X, y_train, xn, a)
                    row[f"{model}_q{a:.2f}"] = fc
                    row[f"{model}_m{a:.2f}"] = mstar
            out.append(row)
    return out


def model_metrics(rows: list[dict], model: str, h: int) -> dict:
    rr = [r for r in rows if int(r["horizon"]) == h]
    if not rr:
        return {"n": 0}
    y = np.array([float(r["actual_return"]) for r in rr])
    med = np.array([float(r[f"{model}_q0.50"]) for r in rr])
    c = confusion(y, med)
    c["mae_median"] = float(np.mean(np.abs(y-med)))
    c["rmse_median"] = float(np.sqrt(np.mean((y-med)**2)))
    c["previous_sign_accuracy"] = float(np.mean((y > 0) == (np.array([r["previous_sign_return"] for r in rr]) > 0)))
    c["pinball"] = {
        f"{a:.2f}": pinball(y, np.array([float(r[f"{model}_q{a:.2f}"]) for r in rr]), a)
        for a in QUANTILES
    }
    # Non-overlapping origins diagnostic for h>1; deterministic first-origin phase.
    if h > 1:
        sub = rr[::h]
        ys = np.array([float(r["actual_return"]) for r in sub])
        ps = np.array([float(r[f"{model}_q0.50"]) for r in sub])
        c["non_overlapping"] = confusion(ys, ps)
    return c


def summarize(rows: list[dict], years: list[int]) -> dict:
    result = {"identity": IDENTITY, "years": years, "horizons": {}}
    for h in HORIZONS:
        result["horizons"][str(h)] = {}
        for model in MODELS:
            result["horizons"][str(h)][model] = model_metrics(rows, model, h)
    return result


def write_forecasts(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError("NO_FORECAST_ROWS")
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def viability(summary: dict, h: int, model: str) -> bool:
    m = summary["horizons"][str(h)][model]
    if not m or m.get("n", 0) == 0:
        return False
    return (
        m["balanced_accuracy"] is not None and m["balanced_accuracy"] >= 0.55
        and m["up_sensitivity"] is not None and m["up_sensitivity"] >= 0.40
        and m["down_sensitivity"] is not None and m["down_sensitivity"] >= 0.40
        and m["accuracy"] > m["always_up_accuracy"]
        and m["accuracy"] > m["always_down_accuracy"]
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("pre2025", "2025"), required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--config")
    ap.add_argument("--pre-result")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    days = load_days()
    ph = panel_hash(days)

    audit = {
        "identity": IDENTITY,
        "source_table": TABLE,
        "timezone": TZ,
        "minimum_bars_per_retained_day": MIN_BARS,
        "retained_days": len(days),
        "first_day": days[0].d.isoformat(),
        "last_day": days[-1].d.isoformat(),
        "panel_sha256": ph,
        "production_database_write": "NONE",
        "exact_futures_replication": False,
        "broader_source_control_panel": "BLOCKED_INCOMPLETE_CONTROL_PANEL",
    }

    if args.stage == "pre2025":
        rows23 = make_forecasts(days, {2023})
        rows24 = make_forecasts(days, {2024})
        s23 = summarize(rows23, [2023])
        s24 = summarize(rows24, [2024])
        config = {
            "identity": IDENTITY,
            "source_table": TABLE,
            "timezone": TZ,
            "minimum_bars": MIN_BARS,
            "horizons": list(HORIZONS),
            "quantiles": list(QUANTILES),
            "step_size": STEP_SIZE,
            "m_break_initial_reconstruction_choice": M_BREAK_INITIAL,
            "m_max": M_MAX,
            "models": {k:list(v) for k,v in MODELS.items()},
            "primary_direction_quantile": 0.50,
            "panel_sha256": ph,
            "frozen_before_2025": True,
        }
        pre = {
            "identity": IDENTITY,
            "status": "PRE2025_FROZEN",
            "2023_development": s23,
            "2024_validation": s24,
            "2024_viability": {
                str(h): {m: viability(s24, h, m) for m in MODELS} for h in HORIZONS
            },
        }
        (outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_SOURCE_AUDIT_2026-09-21.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        (outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_FROZEN_CONFIG_2026-09-21.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        (outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_PRE2025_RESULT_2026-09-21.json").write_text(json.dumps(pre, indent=2), encoding="utf-8")
        write_forecasts(outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_2023_FORECASTS_2026-09-21.csv", rows23)
        write_forecasts(outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_2024_FORECASTS_2026-09-21.csv", rows24)
        print("BONATO_QBOOST_PRE2025_FREEZE_SUCCESS")
        return

    if not args.config or not args.pre_result:
        raise RuntimeError("FROZEN_CONFIG_AND_PRE_RESULT_REQUIRED")
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    pre = json.loads(Path(args.pre_result).read_text(encoding="utf-8"))
    if config.get("identity") != IDENTITY or pre.get("identity") != IDENTITY:
        raise RuntimeError("FROZEN_IDENTITY_MISMATCH")
    if config.get("panel_sha256") != ph:
        raise RuntimeError("FROZEN_PANEL_HASH_MISMATCH")

    rows25 = make_forecasts(days, {2025})
    s25 = summarize(rows25, [2025])
    result = {
        "identity": IDENTITY,
        "status": "LOCKED_2025_REPLAY_COMPLETE",
        "2025": s25,
        "pre2025_validation_gate": pre.get("2024_viability"),
    }
    write_forecasts(outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_2025_FORECASTS_2026-09-21.csv", rows25)
    (outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_2025_RESULT_2026-09-21.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# GOLD CONTROL — BONATO QBOOST REALIZED-MOMENTS SPOT-XAU V1 RESULT",
        "",
        f"**Identity:** `{IDENTITY}`  ",
        "**Evidence:** source-constrained Spot-XAU adaptation; not exact gold-futures replication.  ",
        "",
        "## 2024 fixed validation and locked 2025 replay",
        "",
        "| h | model | 2024 acc | 2024 bal | 2024 DOWN | 2025 acc | 2025 bal | 2025 DOWN |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    v24 = pre["2024_validation"]["horizons"]
    v25 = s25["horizons"]
    for h in HORIZONS:
        for model in MODELS:
            a = v24[str(h)][model]
            b = v25[str(h)][model]
            lines.append(
                f"| {h} | {model} | {a['accuracy']:.4f} | {a['balanced_accuracy']:.4f} | {a['down_sensitivity']:.4f} | "
                f"{b['accuracy']:.4f} | {b['balanced_accuracy']:.4f} | {b['down_sensitivity']:.4f} |"
            )
    lines += [
        "",
        "## Binding interpretation",
        "",
        "Promotion cannot be based on 2025. The pre-2025 gate frozen in the preregistration controls the decision.",
        "The broader Bonato futures+controls replication remains BLOCKED_INCOMPLETE_CONTROL_PANEL.",
    ]
    (outdir/"GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESULT_2026-09-21.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("BONATO_QBOOST_2025_REPLAY_SUCCESS")


if __name__ == "__main__":
    main()
