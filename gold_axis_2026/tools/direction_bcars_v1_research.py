from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import beta as beta_dist

MODEL_ID = "DIRECTION_BCARS_V1_RESEARCH"
MIN_MODEL_WEEK = date(2022, 3, 7)
INITIAL_WINDOW = 52
EPS = 1e-12

STARTS = [
    ((0.25, 0.25, 0.25, 0.25), 1.0),
    ((0.10, 0.70, 0.10, 0.10), 0.5),
    ((0.05, 0.85, 0.05, 0.05), 1.0),
    ((0.10, 0.20, 0.60, 0.10), 0.5),
    ((0.20, 0.30, 0.30, 0.20), 2.0),
]


@dataclass(frozen=True)
class Row:
    week_start: date
    ur: float
    ret: float


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path: Path) -> list[Row]:
    out = []
    with path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        needed = {"week_start", "up_ratio", "return_log", "identity_abs_error"}
        if not needed.issubset(rd.fieldnames or []):
            raise ValueError(f"INPUT_SCHEMA_MISSING:{sorted(needed - set(rd.fieldnames or []))}")
        for r in rd:
            d = date.fromisoformat(r["week_start"])
            if d < MIN_MODEL_WEEK:
                continue
            ur = float(r["up_ratio"])
            ret = float(r["return_log"])
            err = float(r["identity_abs_error"])
            if not math.isfinite(ur) or not (0.0 < ur < 1.0):
                raise RuntimeError(f"BCARS_BOUNDARY_OR_INVALID_UP_RATIO:{d}:{ur}")
            if not math.isfinite(ret):
                raise RuntimeError(f"INVALID_RETURN:{d}")
            if err > 1e-10:
                raise RuntimeError(f"DECOMPOSITION_IDENTITY_FAIL:{d}:{err}")
            # Direction identity audit.
            if (ret > 0) != (ur > 0.5):
                raise RuntimeError(f"DIRECTION_IDENTITY_FAIL:{d}:{ret}:{ur}")
            out.append(Row(d, ur, ret))
    out.sort(key=lambda x: x.week_start)
    if len(out) < INITIAL_WINDOW + 1:
        raise RuntimeError(f"INSUFFICIENT_WEEKLY_ROWS:{len(out)}")
    if len({r.week_start for r in out}) != len(out):
        raise RuntimeError("DUPLICATE_WEEK_START")
    return out


def unpack(theta):
    a, b, c, log_beta = [float(x) for x in theta]
    logits = np.array([a, b, c, 0.0], dtype=float)
    logits -= logits.max()
    weights = np.exp(logits)
    weights /= weights.sum()
    omega, gamma, tau, slack = [float(x) for x in weights]
    beta = float(math.exp(log_beta))
    return omega, gamma, tau, slack, beta


def theta_from_start(weights, beta):
    omega, gamma, tau, slack = weights
    return np.array([
        math.log(omega / slack),
        math.log(gamma / slack),
        math.log(tau / slack),
        math.log(beta),
    ], dtype=float)


def k_path(y: np.ndarray, theta) -> tuple[np.ndarray, tuple[float, float, float, float, float]]:
    omega, gamma, tau, slack, beta = unpack(theta)
    denom = 1.0 - gamma - tau
    if denom <= 0:
        raise FloatingPointError("INVALID_UNCONDITIONAL_MEAN_DENOM")
    k = np.empty(len(y), dtype=float)
    k[0] = omega / denom
    if not (0.0 < k[0] < 1.0):
        raise FloatingPointError("INVALID_INITIAL_K")
    for t in range(1, len(y)):
        k[t] = omega + gamma * k[t - 1] + tau * y[t - 1]
        if not (0.0 < k[t] < 1.0):
            raise FloatingPointError("INVALID_K_RECURSION")
    return k, (omega, gamma, tau, slack, beta)


def neg_loglik(theta, y):
    try:
        k, (_, _, _, _, beta) = k_path(y, theta)
        alpha = k * beta / (1.0 - k)
        if np.any(alpha <= 0) or not np.all(np.isfinite(alpha)):
            return 1e100
        ll = (
            gammaln(alpha + beta)
            - gammaln(alpha)
            - gammaln(beta)
            + (alpha - 1.0) * np.log(y)
            + (beta - 1.0) * np.log1p(-y)
        )
        total = float(np.sum(ll))
        return -total if math.isfinite(total) else 1e100
    except Exception:
        return 1e100


def fit_bcars(y: np.ndarray):
    fits = []
    for weights, beta0 in STARTS:
        x0 = theta_from_start(weights, beta0)
        res = minimize(
            neg_loglik,
            x0,
            args=(y,),
            method="L-BFGS-B",
            bounds=[(-12, 12), (-12, 12), (-12, 12), (-8, 8)],
            options={"maxiter": 3000, "ftol": 1e-12, "gtol": 1e-8, "maxls": 50},
        )
        if res.success and math.isfinite(float(res.fun)):
            fits.append(res)
    if not fits:
        raise RuntimeError("MODEL_FIT_BLOCKED:NO_CONVERGED_START")
    best = min(fits, key=lambda r: float(r.fun))
    k, pars = k_path(y, best.x)
    omega, gamma, tau, slack, beta = pars
    k_next = omega + gamma * k[-1] + tau * y[-1]
    if not (0.0 < k_next < 1.0):
        raise RuntimeError(f"INVALID_FORECAST_K:{k_next}")
    alpha_next = k_next * beta / (1.0 - k_next)
    p_ext_up = float(1.0 - beta_dist.cdf(0.5, alpha_next, beta))
    return {
        "loglik": -float(best.fun),
        "omega": omega,
        "gamma": gamma,
        "tau": tau,
        "slack": slack,
        "beta": beta,
        "k_last": float(k[-1]),
        "k_forecast": float(k_next),
        "alpha_forecast": float(alpha_next),
        "p_ext_up": p_ext_up,
        "converged_starts": len(fits),
        "optimizer_nit": int(best.nit),
    }


def forecasts(rows: list[Row]):
    out = []
    for target_idx in range(INITIAL_WINDOW, len(rows)):
        train = rows[:target_idx]
        target = rows[target_idx]
        y = np.array([r.ur for r in train], dtype=float)
        fit = fit_bcars(y)
        hist_mean = float(np.mean(y))
        pred_up = 1 if fit["k_forecast"] > 0.5 else 0
        actual_up = 1 if target.ret > 0 else 0
        previous_up = 1 if train[-1].ret > 0 else 0
        out.append({
            "origin_week": train[-1].week_start.isoformat(),
            "target_week": target.week_start.isoformat(),
            "n_train": len(train),
            **fit,
            "historical_mean_ur": hist_mean,
            "forecast_direction": "UP" if pred_up else "DOWN",
            "actual_direction": "UP" if actual_up else "DOWN",
            "previous_week_direction": "UP" if previous_up else "DOWN",
            "actual_up_ratio": target.ur,
            "actual_return_log": target.ret,
        })
    return out


def metric_block(rows):
    if not rows:
        return {"n": 0}
    n = len(rows)
    actual_up = sum(r["actual_direction"] == "UP" for r in rows)
    actual_down = n - actual_up
    tp = sum(r["forecast_direction"] == "UP" and r["actual_direction"] == "UP" for r in rows)
    tn = sum(r["forecast_direction"] == "DOWN" and r["actual_direction"] == "DOWN" for r in rows)
    fp = sum(r["forecast_direction"] == "UP" and r["actual_direction"] == "DOWN" for r in rows)
    fn = sum(r["forecast_direction"] == "DOWN" and r["actual_direction"] == "UP" for r in rows)

    brier = sum((r["p_ext_up"] - (1 if r["actual_direction"] == "UP" else 0)) ** 2 for r in rows) / n
    ll = 0.0
    for r in rows:
        y = 1 if r["actual_direction"] == "UP" else 0
        p = min(max(r["p_ext_up"], EPS), 1 - EPS)
        ll += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    ll /= n

    sse_bcars = sum((r["actual_up_ratio"] - r["k_forecast"]) ** 2 for r in rows)
    sse_mean = sum((r["actual_up_ratio"] - r["historical_mean_ur"]) ** 2 for r in rows)
    r2_oos = 1.0 - sse_bcars / sse_mean if sse_mean > 0 else None

    return {
        "n": n,
        "accuracy": (tp + tn) / n,
        "balanced_accuracy": ((tp / actual_up) + (tn / actual_down)) / 2 if actual_up and actual_down else None,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "forecast_up": tp + fp,
        "forecast_down": tn + fn,
        "up_sensitivity": tp / actual_up if actual_up else None,
        "down_sensitivity": tn / actual_down if actual_down else None,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "always_up_accuracy": actual_up / n,
        "previous_sign_accuracy": sum(r["forecast_direction"] == r["previous_week_direction"] and r["previous_week_direction"] == r["actual_direction"] for r in []) if False else sum(r["previous_week_direction"] == r["actual_direction"] for r in rows) / n,
        "mse_up_ratio_bcars": sse_bcars / n,
        "mse_up_ratio_historical_mean": sse_mean / n,
        "r2_oos_up_ratio": r2_oos,
        "brier_p_ext": brier,
        "log_loss_p_ext": ll,
        "mean_k_forecast": sum(r["k_forecast"] for r in rows) / n,
        "min_k_forecast": min(r["k_forecast"] for r in rows),
        "max_k_forecast": max(r["k_forecast"] for r in rows),
        "mean_p_ext_up": sum(r["p_ext_up"] for r in rows) / n,
        "min_p_ext_up": min(r["p_ext_up"] for r in rows),
        "max_p_ext_up": max(r["p_ext_up"] for r in rows),
    }


def write_forecast_csv(path: Path, rows, include_actual_ur=False):
    fields = [
        "origin_week","target_week","n_train","omega","gamma","tau","slack","beta",
        "k_last","k_forecast","alpha_forecast","p_ext_up","historical_mean_ur",
        "forecast_direction","actual_direction","previous_week_direction",
        "loglik","converged_starts","optimizer_nit",
    ]
    if include_actual_ur:
        fields += ["actual_up_ratio","actual_return_log"]
    with path.open("w",encoding="utf-8",newline="") as fh:
        wr=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n")
        wr.writeheader()
        for row in rows:
            wr.writerow({k:row[k] for k in fields})


def fmt(x):
    if x is None:
        return "NA"
    if isinstance(x, int):
        return str(x)
    return f"{x:.10f}"


def pre2025_markdown(data_sha, m23, m24, mall):
    return f"""# GOLD CONTROL — DIRECTION_BCARS_V1_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `{MODEL_ID}`  
**Status:** `PRE2025_CHECKPOINT_COMPLETE / FROZEN_BEFORE_BCARS_V1_2025_REPLAY`  
**Evidence:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_RESEARCH`  
**Input artifact SHA-256:** `{data_sha}`

## Frozen method

- true Twelve Data XAU/USD 1h HIGH/CLOSE-derived weekly up-ratio;
- weekly modeled sample begins 2022-03-07;
- B-CARS(1,1);
- expanding-window MLE;
- initial 52 valid weekly up-ratios;
- source high adjustment `H_t^a=max(H_t,C_(t-1))`;
- source-grounded unconditional-mean recursion initialization;
- fixed deterministic five-start L-BFGS-B numerical contract;
- native direction UP iff forecast `k_(t+1)>0.5`;
- no exogenous variables and no 2025-driven tuning.

## 2023 development/audit

- n = {m23['n']}
- accuracy = {fmt(m23['accuracy'])}
- balanced accuracy = {fmt(m23['balanced_accuracy'])}
- actual UP / DOWN = {m23['actual_up']} / {m23['actual_down']}
- forecast UP / DOWN = {m23['forecast_up']} / {m23['forecast_down']}
- UP sensitivity = {fmt(m23['up_sensitivity'])}
- DOWN sensitivity = {fmt(m23['down_sensitivity'])}
- TP / TN / FP / FN = {m23['tp']} / {m23['tn']} / {m23['fp']} / {m23['fn']}
- always-UP accuracy = {fmt(m23['always_up_accuracy'])}
- previous-week-sign accuracy = {fmt(m23['previous_sign_accuracy'])}
- up-ratio MSE B-CARS = {fmt(m23['mse_up_ratio_bcars'])}
- up-ratio MSE historical mean = {fmt(m23['mse_up_ratio_historical_mean'])}
- source-style up-ratio R2_oos = {fmt(m23['r2_oos_up_ratio'])}
- derived P(UP) Brier = {fmt(m23['brier_p_ext'])}
- derived P(UP) log loss = {fmt(m23['log_loss_p_ext'])}

## 2024 fixed validation

- n = {m24['n']}
- accuracy = {fmt(m24['accuracy'])}
- balanced accuracy = {fmt(m24['balanced_accuracy'])}
- actual UP / DOWN = {m24['actual_up']} / {m24['actual_down']}
- forecast UP / DOWN = {m24['forecast_up']} / {m24['forecast_down']}
- UP sensitivity = {fmt(m24['up_sensitivity'])}
- DOWN sensitivity = {fmt(m24['down_sensitivity'])}
- TP / TN / FP / FN = {m24['tp']} / {m24['tn']} / {m24['fp']} / {m24['fn']}
- always-UP accuracy = {fmt(m24['always_up_accuracy'])}
- previous-week-sign accuracy = {fmt(m24['previous_sign_accuracy'])}
- up-ratio MSE B-CARS = {fmt(m24['mse_up_ratio_bcars'])}
- up-ratio MSE historical mean = {fmt(m24['mse_up_ratio_historical_mean'])}
- source-style up-ratio R2_oos = {fmt(m24['r2_oos_up_ratio'])}
- derived P(UP) Brier = {fmt(m24['brier_p_ext'])}
- derived P(UP) log loss = {fmt(m24['log_loss_p_ext'])}

## Combined pre-2025

- n = {mall['n']}
- accuracy = {fmt(mall['accuracy'])}
- balanced accuracy = {fmt(mall['balanced_accuracy'])}
- source-style up-ratio R2_oos = {fmt(mall['r2_oos_up_ratio'])}
- native k forecast range = {fmt(mall['min_k_forecast'])} .. {fmt(mall['max_k_forecast'])}
- derived P(UP) range = {fmt(mall['min_p_ext_up'])} .. {fmt(mall['max_p_ext_up'])}

## Lock

No B-CARS V1 parameter, optimizer rule, order, window, threshold, source semantic or boundary treatment may be changed after this checkpoint based on 2025 outcomes.
"""


def full2025_markdown(data_sha, m25):
    return f"""# GOLD CONTROL — DIRECTION_BCARS_V1_RESEARCH LOCKED 2025 TEST

**Date:** 2026-09-18  
**Identity:** `{MODEL_ID}`  
**Status:** `LOCKED_2025_HISTORICAL_REPLAY_COMPLETE / EVENT_OVERLAY_NOT_YET_APPLIED`  
**Input artifact SHA-256:** `{data_sha}`

The 2025 replay uses the unchanged preregistered expanding-window B-CARS(1,1) specification.

## Locked 2025 result

- n = {m25['n']}
- accuracy = {fmt(m25['accuracy'])}
- balanced accuracy = {fmt(m25['balanced_accuracy'])}
- actual UP / DOWN = {m25['actual_up']} / {m25['actual_down']}
- forecast UP / DOWN = {m25['forecast_up']} / {m25['forecast_down']}
- UP sensitivity = {fmt(m25['up_sensitivity'])}
- DOWN sensitivity = {fmt(m25['down_sensitivity'])}
- TP / TN / FP / FN = {m25['tp']} / {m25['tn']} / {m25['fp']} / {m25['fn']}
- always-UP accuracy = {fmt(m25['always_up_accuracy'])}
- previous-week-sign accuracy = {fmt(m25['previous_sign_accuracy'])}
- up-ratio MSE B-CARS = {fmt(m25['mse_up_ratio_bcars'])}
- up-ratio MSE historical mean = {fmt(m25['mse_up_ratio_historical_mean'])}
- source-style up-ratio R2_oos = {fmt(m25['r2_oos_up_ratio'])}
- native k forecast range = {fmt(m25['min_k_forecast'])} .. {fmt(m25['max_k_forecast'])}
- derived P(UP) Brier = {fmt(m25['brier_p_ext'])}
- derived P(UP) log loss = {fmt(m25['log_loss_p_ext'])}
- derived P(UP) range = {fmt(m25['min_p_ext_up'])} .. {fmt(m25['max_p_ext_up'])}

The complete 2025 forecast table is frozen before the volatility-event overlay.
"""


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def parse_events(path: Path):
    events=[]
    pat=re.compile(r"^\|\s*\d+\s*\|\s*(2025-\d\d-\d\d)\s*\|\s*([+-][\d.]+)%\s*\|\s*([+-][\d.]+)\s*\|\s*(UP|DOWN)\s*\|\s*(MAJOR|EXTREME)\s*\|$")
    for line in path.read_text(encoding="utf-8").splitlines():
        m=pat.match(line)
        if m:
            events.append({
                "event_date":m.group(1),"simple_return_pct":float(m.group(2)),
                "z":float(m.group(3)),"event_direction":m.group(4),"tier":m.group(5)
            })
    if len(events)!=19:
        raise RuntimeError(f"EVENT_COUNT_MISMATCH:{len(events)}")
    return events


def write_overlay(out_dir: Path, rows2025, event_contract: Path):
    by_week={r["target_week"]:r for r in rows2025}
    events=parse_events(event_contract)
    overlay=[]
    for e in events:
        w=monday_of(date.fromisoformat(e["event_date"])).isoformat()
        r=by_week.get(w)
        if r is None:
            raise RuntimeError(f"NO_FORECAST_FOR_EVENT_WEEK:{e['event_date']}:{w}")
        match=r["forecast_direction"]==e["event_direction"]
        overlay.append({**e,"target_week":w,"k_forecast":r["k_forecast"],"p_ext_up":r["p_ext_up"],
                        "forecast_direction":r["forecast_direction"],"match":match})
    fields=["event_date","tier","z","event_direction","target_week","k_forecast","p_ext_up","forecast_direction","match"]
    with (out_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_2025_VOLATILITY_OVERLAY_2026-09-18.csv").open("w",encoding="utf-8",newline="") as fh:
        wr=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n");wr.writeheader()
        for r in overlay: wr.writerow({k:r[k] for k in fields})
    ups=[r for r in overlay if r["event_direction"]=="UP"]
    downs=[r for r in overlay if r["event_direction"]=="DOWN"]
    ext=[r for r in overlay if r["tier"]=="EXTREME"]
    maj=[r for r in overlay if r["tier"]=="MAJOR"]
    correct=lambda a:sum(r["match"] for r in a)
    bal=((correct(ups)/len(ups))+(correct(downs)/len(downs)))/2
    md=f"""# GOLD CONTROL — DIRECTION_BCARS_V1_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `{MODEL_ID}`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE`

- event-days = {len(overlay)}
- correct event directions = {correct(overlay)}
- raw event-direction agreement = {correct(overlay)/len(overlay):.10f}
- balanced event-direction accuracy = {bal:.10f}
- UP event agreement = {correct(ups)}/{len(ups)}
- DOWN event agreement = {correct(downs)}/{len(downs)}
- EXTREME event agreement = {correct(ext)}/{len(ext)}
- MAJOR-only event agreement = {correct(maj)}/{len(maj)}

B-CARS is a weekly direction model, not a volatility-event detector. This overlay is direction agreement only and is applied after the complete 2025 forecast table is frozen.
"""
    (out_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_2025_VOLATILITY_RESULT_2026-09-18.md").write_text(md,encoding="utf-8")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-csv",type=Path,required=True)
    ap.add_argument("--stage",choices=["pre2025","2025","overlay"],required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--event-contract",type=Path)
    args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)

    data_sha=sha256_file(args.input_csv)
    rows=load_rows(args.input_csv)
    fc=forecasts(rows)

    if args.stage=="pre2025":
        pre=[r for r in fc if r["target_week"] < "2025-01-01"]
        y23=[r for r in pre if r["target_week"].startswith("2023-")]
        y24=[r for r in pre if r["target_week"].startswith("2024-")]
        m23,m24,mall=metric_block(y23),metric_block(y24),metric_block(pre)
        write_forecast_csv(args.output_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_PRE2025_FORECASTS_2026-09-18.csv",pre)
        (args.output_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_PRE2025_RESULT_2026-09-18.md").write_text(
            pre2025_markdown(data_sha,m23,m24,mall),encoding="utf-8")
        (args.output_dir/"bcars_pre2025_metrics.json").write_text(
            json.dumps({"2023":m23,"2024":m24,"combined":mall},indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"stage":"pre2025","2023":m23,"2024":m24,"combined":mall},sort_keys=True))
        return

    if args.stage=="2025":
        y25=[r for r in fc if r["target_week"].startswith("2025-")]
        m25=metric_block(y25)
        write_forecast_csv(args.output_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv",y25)
        (args.output_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_2025_RESULT_2026-09-18.md").write_text(
            full2025_markdown(data_sha,m25),encoding="utf-8")
        (args.output_dir/"bcars_2025_metrics.json").write_text(json.dumps(m25,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"stage":"2025","2025":m25},sort_keys=True))
        return

    if args.event_contract is None:
        raise RuntimeError("EVENT_CONTRACT_REQUIRED_FOR_OVERLAY")
    frozen_path=args.output_dir/"GOLD_CONTROL_DIRECTION_BCARS_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv"
    if not frozen_path.exists():
        raise RuntimeError("FROZEN_2025_FORECAST_TABLE_MISSING")
    frozen=[]
    with frozen_path.open(encoding="utf-8",newline="") as fh:
        rd=csv.DictReader(fh)
        for r in rd:
            frozen.append({
                "target_week":r["target_week"],
                "k_forecast":float(r["k_forecast"]),
                "p_ext_up":float(r["p_ext_up"]),
                "forecast_direction":r["forecast_direction"],
            })
    write_overlay(args.output_dir,frozen,args.event_contract)
    print(json.dumps({"stage":"overlay","frozen_forecast_rows":len(frozen)},sort_keys=True))


if __name__=="__main__":
    main()
