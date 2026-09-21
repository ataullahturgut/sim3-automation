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

IDENTITY = "DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_RESEARCH"
PARENT = "DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH"
TABLE = "public.xau_intraday_research_cache_5m"
TZ = "America/New_York"
MIN_BARS = 240
MIN_TRAIN = 250
RIDGE = 1e-6
MAX_ITER = 100
TOL = 1e-10
MODELS = {
    "AR1_LOGIT": ("lag1_return",),
    "RV_LOGIT": ("log_rv",),
    "RSK_LOGIT": ("rsk",),
    "RM_LOGIT": ("log_rv", "rsk"),
    "AR1_RM_LOGIT": ("lag1_return", "log_rv", "rsk"),
}
PRIMARY = "AR1_RM_LOGIT"
BASELINE = "AR1_LOGIT"


@dataclass(frozen=True)
class DayRow:
    d: date
    close: float
    n_bars: int
    rv: float
    log_rv: float
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
        log_rv = math.log(max(v, 1e-12))
        base.append((d, c, int(n_bars), v, log_rv, rsk))

    if len(base) < 1000:
        raise RuntimeError(f"INSUFFICIENT_RETAINED_DAYS:{len(base)}")

    out: list[DayRow] = []
    prev_close = None
    for d, c, n, rv, log_rv, rsk in base:
        lag1 = float("nan") if prev_close is None else math.log(c / prev_close)
        out.append(DayRow(d, c, n, rv, log_rv, rsk, lag1))
        prev_close = c
    return out


def panel_hash(days: list[DayRow]) -> str:
    s = "\n".join(
        f"{r.d.isoformat()}|{r.close:.12f}|{r.n_bars}|{r.rv:.16g}|{r.log_rv:.16g}|{r.rsk:.16g}|{r.lag1_return:.16g}"
        for r in days[1:]
    )
    return hashlib.sha256(s.encode()).hexdigest()


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def fit_logit_predict(X: np.ndarray, y: np.ndarray, x_new: np.ndarray) -> tuple[float, list[float]]:
    if X.ndim != 2 or len(y) != X.shape[0] or X.shape[0] < MIN_TRAIN:
        raise RuntimeError("BAD_LOGIT_TRAIN_SHAPE")
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd = np.where(sd <= 1e-12, 1.0, sd)
    Xs = (X - mu) / sd
    xn = (x_new - mu) / sd

    Z = np.column_stack([np.ones(len(Xs)), Xs])
    zn = np.concatenate([[1.0], xn])
    beta = np.zeros(Z.shape[1], dtype=float)

    for _ in range(MAX_ITER):
        p = sigmoid(Z @ beta)
        w = np.clip(p * (1.0 - p), 1e-9, None)
        grad = Z.T @ (p - y)
        grad[1:] += RIDGE * beta[1:]
        H = Z.T @ (Z * w[:, None])
        H[1:, 1:] += RIDGE * np.eye(Z.shape[1] - 1)
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, grad, rcond=None)[0]
        beta_new = beta - step
        if float(np.max(np.abs(beta_new - beta))) < TOL:
            beta = beta_new
            break
        beta = beta_new

    pnew = float(sigmoid(np.array([float(zn @ beta)]))[0])
    pnew = min(max(pnew, 1e-12), 1.0 - 1e-12)
    return pnew, beta.tolist()


def fv(r: DayRow, name: str) -> float:
    return float(getattr(r, name))


def make_forecasts(days: list[DayRow], target_years: set[int]) -> list[dict]:
    out = []
    for i in range(1, len(days) - 1):
        target_i = i + 1
        target_date = days[target_i].d
        if target_date.year not in target_years:
            continue
        origin = days[i]
        if not math.isfinite(origin.lag1_return):
            continue

        train_idx = list(range(1, i))
        if len(train_idx) < MIN_TRAIN:
            continue

        y = np.array(
            [1.0 if math.log(days[j+1].close / days[j].close) > 0 else 0.0 for j in train_idx],
            dtype=float,
        )
        actual_return = math.log(days[target_i].close / origin.close)
        actual_up = int(actual_return > 0)
        freq = float(np.mean(y))

        row = {
            "origin_date": origin.d.isoformat(),
            "target_date": target_date.isoformat(),
            "actual_return": actual_return,
            "actual_up": actual_up,
            "freq_p_up": freq,
            "lag1_return": origin.lag1_return,
            "log_rv": origin.log_rv,
            "rsk": origin.rsk,
        }

        for model, feats in MODELS.items():
            X = np.array([[fv(days[j], f) for f in feats] for j in train_idx], dtype=float)
            xn = np.array([fv(origin, f) for f in feats], dtype=float)
            p, beta = fit_logit_predict(X, y, xn)
            row[f"{model}_p_up"] = p
            row[f"{model}_pred_up"] = int(p >= 0.5)
            row[f"{model}_beta"] = json.dumps(beta, separators=(",", ":"))
        out.append(row)
    return out


def metrics(rows: list[dict], model: str) -> dict:
    if not rows:
        return {"n": 0}
    y = np.array([int(r["actual_up"]) for r in rows], dtype=int)
    p = np.array([float(r[f"{model}_p_up"]) for r in rows], dtype=float)
    pred = p >= 0.5
    up = y == 1
    dn = y == 0
    tp = int(np.sum(up & pred))
    tn = int(np.sum(dn & (~pred)))
    fp = int(np.sum(dn & pred))
    fn = int(np.sum(up & (~pred)))
    up_s = tp / int(np.sum(up)) if np.sum(up) else None
    dn_s = tn / int(np.sum(dn)) if np.sum(dn) else None
    bal = (up_s + dn_s) / 2 if up_s is not None and dn_s is not None else None
    eps = 1e-12
    brier = float(np.mean((p - y) ** 2))
    logloss = float(-np.mean(y*np.log(np.clip(p,eps,1-eps)) + (1-y)*np.log(np.clip(1-p,eps,1-eps))))
    freq = np.array([float(r["freq_p_up"]) for r in rows], dtype=float)
    freq_brier = float(np.mean((freq - y) ** 2))
    return {
        "n": int(len(rows)),
        "accuracy": float(np.mean(pred == up)),
        "balanced_accuracy": bal,
        "up_sensitivity": up_s,
        "down_sensitivity": dn_s,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "actual_up": int(np.sum(up)),
        "actual_down": int(np.sum(dn)),
        "forecast_up": int(np.sum(pred)),
        "forecast_down": int(np.sum(~pred)),
        "forecast_down_share": float(np.mean(~pred)),
        "always_up_accuracy": float(np.mean(up)),
        "always_down_accuracy": float(np.mean(dn)),
        "brier": brier,
        "log_loss": logloss,
        "expanding_frequency_brier": freq_brier,
    }


def exact_two_sided_sign_p(a: int, b: int) -> float:
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    lower = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * lower)


def primary_comparison(rows: list[dict]) -> dict:
    ar = metrics(rows, BASELINE)
    rm = metrics(rows, PRIMARY)
    down_rows = [r for r in rows if int(r["actual_up"]) == 0]
    both = rm_only = ar_only = wrong = 0
    for r in down_rows:
        a = int(r[f"{BASELINE}_pred_up"]) == 0
        m = int(r[f"{PRIMARY}_pred_up"]) == 0
        if a and m:
            both += 1
        elif m and not a:
            rm_only += 1
        elif a and not m:
            ar_only += 1
        else:
            wrong += 1
    return {
        "delta_down_sensitivity": rm["down_sensitivity"] - ar["down_sensitivity"],
        "delta_balanced_accuracy": rm["balanced_accuracy"] - ar["balanced_accuracy"],
        "delta_brier_rm_minus_ar1": rm["brier"] - ar["brier"],
        "actual_down_paired": {
            "both_correct": both,
            "rm_only_correct": rm_only,
            "ar1_only_correct": ar_only,
            "both_wrong": wrong,
            "discordant_exact_two_sided_sign_p": exact_two_sided_sign_p(rm_only, ar_only),
        },
    }


def summarize(rows: list[dict], years: list[int]) -> dict:
    return {
        "identity": IDENTITY,
        "years": years,
        "models": {m: metrics(rows, m) for m in MODELS},
        "primary_comparison": primary_comparison(rows),
    }


def feature_gate(summary: dict) -> bool:
    p = summary["models"][PRIMARY]
    c = summary["primary_comparison"]
    return (
        c["delta_down_sensitivity"] >= 0.10
        and c["delta_balanced_accuracy"] >= 0.02
        and p["balanced_accuracy"] >= 0.52
        and p["up_sensitivity"] >= 0.35
        and p["down_sensitivity"] >= 0.35
        and 0.10 <= p["forecast_down_share"] <= 0.90
    )


def strong_gate(summary: dict) -> bool:
    p = summary["models"][PRIMARY]
    return (
        p["balanced_accuracy"] >= 0.55
        and p["up_sensitivity"] >= 0.40
        and p["down_sensitivity"] >= 0.40
        and p["accuracy"] > p["always_up_accuracy"]
        and p["accuracy"] > p["always_down_accuracy"]
        and p["brier"] <= p["expanding_frequency_brier"]
    )


def write_forecasts(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError("NO_FORECAST_ROWS")
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


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
        "parent_observation": PARENT,
        "source_table": TABLE,
        "timezone": TZ,
        "minimum_bars_per_retained_day": MIN_BARS,
        "retained_days": len(days),
        "first_day": days[0].d.isoformat(),
        "last_day": days[-1].d.isoformat(),
        "panel_sha256": ph,
        "production_database_write": "NONE",
    }

    if args.stage == "pre2025":
        rows23 = make_forecasts(days, {2023})
        rows24 = make_forecasts(days, {2024})
        s23 = summarize(rows23, [2023])
        s24 = summarize(rows24, [2024])
        fg = feature_gate(s24)
        sg = strong_gate(s24)
        config = {
            "identity": IDENTITY,
            "primary_model": PRIMARY,
            "baseline_model": BASELINE,
            "models": {k:list(v) for k,v in MODELS.items()},
            "horizon": 1,
            "minimum_training_rows": MIN_TRAIN,
            "ridge_numerical_stabilizer": RIDGE,
            "max_iter": MAX_ITER,
            "tolerance": TOL,
            "direction_threshold": 0.5,
            "panel_sha256": ph,
            "frozen_before_2025": True,
        }
        pre = {
            "identity": IDENTITY,
            "status": "PRE2025_FROZEN",
            "2023_development": s23,
            "2024_validation": s24,
            "pre2025_feature_signal_supported": fg,
            "strong_direction_gate_passed": sg,
            "binding_pre2025_decision": (
                "PRE2025_FEATURE_SIGNAL_SUPPORTED" if fg else "PRE2025_FEATURE_SIGNAL_NOT_SUPPORTED"
            ),
            "binding_strong_decision": (
                "STRONG_DIRECTION_GATE_PASSED" if sg else "STRONG_DIRECTION_GATE_FAILED"
            ),
        }
        (outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_SOURCE_AUDIT_2026-09-21.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        (outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_FROZEN_CONFIG_2026-09-21.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        (outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_PRE2025_RESULT_2026-09-21.json").write_text(json.dumps(pre, indent=2), encoding="utf-8")
        write_forecasts(outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_2023_FORECASTS_2026-09-21.csv", rows23)
        write_forecasts(outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_2024_FORECASTS_2026-09-21.csv", rows24)
        print("DOWNSIDE_RM_LOGIT_V2_PRE2025_FREEZE_SUCCESS")
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
        "pre2025_feature_signal_supported": pre["pre2025_feature_signal_supported"],
        "strong_direction_gate_passed": pre["strong_direction_gate_passed"],
        "2025": s25,
    }
    write_forecasts(outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_2025_FORECASTS_2026-09-21.csv", rows25)
    (outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_2025_RESULT_2026-09-21.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    s23 = pre["2023_development"]
    s24 = pre["2024_validation"]
    lines = [
        "# GOLD CONTROL — DOWNSIDE REALIZED-MOMENTS LOGIT V2 RESULT",
        "",
        f"**Identity:** `{IDENTITY}`  ",
        f"**Parent observation:** `{PARENT}`  ",
        "**Evidence:** preregistered cross-model realized-moment feature confirmation; research-only.  ",
        "",
        "## Main model metrics",
        "",
        "| period | model | acc | BA | UP sens | DOWN sens | DOWN forecasts | Brier | freq Brier |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, ss in [("2023", s23), ("2024", s24), ("2025", s25)]:
        for model in MODELS:
            m = ss["models"][model]
            lines.append(
                f"| {label} | {model} | {m['accuracy']:.4f} | {m['balanced_accuracy']:.4f} | "
                f"{m['up_sensitivity']:.4f} | {m['down_sensitivity']:.4f} | {m['forecast_down']} | "
                f"{m['brier']:.4f} | {m['expanding_frequency_brier']:.4f} |"
            )

    lines += [
        "",
        "## Primary AR1+RM versus AR1 comparison",
        "",
        "| period | delta DOWN | delta BA | delta Brier (RM-AR1) | RM-only DOWN correct | AR1-only DOWN correct | sign-test p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label, ss in [("2023", s23), ("2024", s24), ("2025", s25)]:
        c = ss["primary_comparison"]
        d = c["actual_down_paired"]
        lines.append(
            f"| {label} | {c['delta_down_sensitivity']:+.4f} | {c['delta_balanced_accuracy']:+.4f} | "
            f"{c['delta_brier_rm_minus_ar1']:+.4f} | {d['rm_only_correct']} | {d['ar1_only_correct']} | "
            f"{d['discordant_exact_two_sided_sign_p']:.4f} |"
        )

    lines += [
        "",
        "## Frozen decisions",
        "",
        f"- Pre-2025 feature-contribution gate: **{'PASS' if pre['pre2025_feature_signal_supported'] else 'FAIL'}**.",
        f"- Strong standalone direction gate: **{'PASS' if pre['strong_direction_gate_passed'] else 'FAIL'}**.",
        "- 2025 is challenge evidence only and cannot change either pre-2025 decision.",
        "- No runtime, production or trading authority is created by this experiment.",
    ]
    (outdir/"GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_RESULT_2026-09-21.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("DOWNSIDE_RM_LOGIT_V2_2025_REPLAY_SUCCESS")


if __name__ == "__main__":
    main()
