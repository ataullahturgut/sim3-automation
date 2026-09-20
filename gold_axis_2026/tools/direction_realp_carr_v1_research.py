from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

IDENTITY = "DIRECTION_REALP_CARR_V1_RESEARCH"
INITIAL_WINDOW = 52

# Fixed optimizer starts: (omega multiplier vs mean CAR, a, b, g, slack)
STARTS = [
    (0.05, 0.60, 0.20, 0.05, 0.15),
    (0.10, 0.40, 0.35, 0.05, 0.20),
    (0.05, 0.75, 0.10, 0.02, 0.13),
    (0.15, 0.25, 0.45, 0.10, 0.20),
    (0.10, 0.50, 0.15, 0.15, 0.20),
]


@dataclass(frozen=True)
class Row:
    week_start: date
    car: float
    realp: float
    ret: float


def read_rows(path: Path) -> list[Row]:
    out = []
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        needed = {"week_start", "car", "realp", "return_log", "identity_abs_error"}
        if not needed.issubset(set(rd.fieldnames or [])):
            raise ValueError(f"INPUT_SCHEMA_MISSING:{sorted(needed-set(rd.fieldnames or []))}")
        for r in rd:
            d = date.fromisoformat(r["week_start"])
            car = float(r["car"])
            realp = float(r["realp"])
            ret = float(r["return_log"])
            err = float(r["identity_abs_error"])
            if not (math.isfinite(car) and car > 0):
                raise RuntimeError(f"INVALID_CAR:{d}:{car}")
            if not (math.isfinite(realp) and 0 <= realp <= 1):
                raise RuntimeError(f"INVALID_REALP:{d}:{realp}")
            if not math.isfinite(ret):
                raise RuntimeError(f"INVALID_RETURN:{d}")
            if err > 1e-10:
                raise RuntimeError(f"IDENTITY_FAIL:{d}:{err}")
            if abs(ret) > 1e-14 and ((ret > 0) != (realp > 0.5)):
                raise RuntimeError(f"DIRECTION_IDENTITY_FAIL:{d}:{ret}:{realp}")
            out.append(Row(d, car, realp, ret))
    out.sort(key=lambda x: x.week_start)
    if len(out) < INITIAL_WINDOW + 1:
        raise RuntimeError(f"INSUFFICIENT_ROWS:{len(out)}")
    if len({r.week_start for r in out}) != len(out):
        raise RuntimeError("DUPLICATE_WEEK_START")
    return out


def coeffs_from_theta(theta):
    log_omega, x1, x2, x3 = [float(x) for x in theta]
    logits = np.array([x1, x2, x3, 0.0], dtype=float)
    logits -= logits.max()
    w = np.exp(logits)
    w /= w.sum()
    a, b, g, slack = [float(x) for x in w]
    omega = math.exp(log_omega)
    return omega, a, b, g, slack


def theta_from_start(mean_car, spec):
    omega_mult, a, b, g, slack = spec
    total = a + b + g + slack
    a, b, g, slack = a/total, b/total, g/total, slack/total
    return np.array(
        [
            math.log(max(mean_car * omega_mult, 1e-12)),
            math.log(a/slack),
            math.log(b/slack),
            math.log(g/slack),
        ],
        dtype=float,
    )


def lambda_path(car, ret, theta):
    omega, a, b, g, slack = coeffs_from_theta(theta)
    n = len(car)
    lam = np.empty(n, dtype=float)
    lam[0] = float(np.mean(car))
    if not math.isfinite(lam[0]) or lam[0] <= 0:
        raise FloatingPointError("INVALID_INITIAL_LAMBDA")
    for t in range(1, n):
        neg = 1.0 if ret[t-1] < 0 else 0.0
        lam[t] = omega + a*lam[t-1] + b*car[t-1] + g*car[t-1]*neg
        if not math.isfinite(lam[t]) or lam[t] <= 0:
            raise FloatingPointError("INVALID_LAMBDA")
    return lam, (omega, a, b, g, slack)


def nll(theta, car, ret):
    try:
        lam, _ = lambda_path(car, ret, theta)
        val = float(np.sum(np.log(lam) + car/lam))
        return val if math.isfinite(val) else 1e100
    except Exception:
        return 1e100


def fit_carr(car, ret):
    mean_car = float(np.mean(car))
    fits = []
    # omega scale spans many price levels, so use broad finite bounds around observed CAR.
    lo_omega = math.log(max(mean_car*1e-6, 1e-12))
    hi_omega = math.log(max(mean_car*10.0, 1e-8))
    bounds = [(lo_omega, hi_omega), (-12, 12), (-12, 12), (-12, 12)]
    for spec in STARTS:
        x0 = theta_from_start(mean_car, spec)
        res = minimize(
            nll,
            x0,
            args=(car, ret),
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 4000, "ftol": 1e-12, "gtol": 1e-8, "maxls": 50},
        )
        if res.success and math.isfinite(float(res.fun)):
            fits.append(res)
    if not fits:
        raise RuntimeError("CARR_FIT_BLOCKED:NO_CONVERGED_START")
    best = min(fits, key=lambda r: float(r.fun))
    lam, pars = lambda_path(car, ret, best.x)
    omega, a, b, g, slack = pars
    neg = 1.0 if ret[-1] < 0 else 0.0
    lam_next = omega + a*lam[-1] + b*car[-1] + g*car[-1]*neg
    if not math.isfinite(lam_next) or lam_next <= 0:
        raise RuntimeError(f"INVALID_LAMBDA_FORECAST:{lam_next}")
    return {
        "nll": float(best.fun),
        "omega": omega,
        "a": a,
        "b": b,
        "g": g,
        "slack": slack,
        "lambda_last": float(lam[-1]),
        "lambda_next": float(lam_next),
        "lambda_path": lam,
        "converged_starts": len(fits),
        "optimizer_nit": int(best.nit),
    }


def ols_realp(realp, lam):
    X = np.column_stack([np.ones(len(lam)), lam])
    coef, *_ = np.linalg.lstsq(X, realp, rcond=None)
    theta, psi = [float(x) for x in coef]
    fitted = X @ coef
    return theta, psi, fitted


def forecasts(rows: list[Row]):
    out = []
    for idx in range(INITIAL_WINDOW, len(rows)):
        train = rows[:idx]
        target = rows[idx]
        car = np.array([r.car for r in train], dtype=float)
        realp = np.array([r.realp for r in train], dtype=float)
        ret = np.array([r.ret for r in train], dtype=float)

        fit = fit_carr(car, ret)
        theta, psi, fitted = ols_realp(realp, fit["lambda_path"])
        realp_hat = theta + psi*fit["lambda_next"]

        historical_mean = float(np.mean(realp))
        previous_realp = float(realp[-1])
        forecast_up = int(realp_hat > 0.5)
        actual_up = int(target.ret > 0)
        previous_up = int(train[-1].ret > 0)
        histmean_up = int(historical_mean > 0.5)
        previous_realp_up = int(previous_realp > 0.5)

        out.append(
            {
                "origin_week": train[-1].week_start.isoformat(),
                "target_week": target.week_start.isoformat(),
                "n_train": len(train),
                "omega": fit["omega"],
                "a": fit["a"],
                "b": fit["b"],
                "g": fit["g"],
                "slack": fit["slack"],
                "lambda_last": fit["lambda_last"],
                "lambda_forecast": fit["lambda_next"],
                "theta": theta,
                "psi": psi,
                "realp_forecast": realp_hat,
                "historical_mean_realp": historical_mean,
                "previous_realp": previous_realp,
                "forecast_direction": "UP" if forecast_up else "DOWN",
                "actual_direction": "UP" if actual_up else "DOWN",
                "previous_week_direction": "UP" if previous_up else "DOWN",
                "historical_mean_realp_direction": "UP" if histmean_up else "DOWN",
                "previous_realp_direction": "UP" if previous_realp_up else "DOWN",
                "actual_realp": target.realp,
                "actual_return_log": target.ret,
                "converged_starts": fit["converged_starts"],
                "optimizer_nit": fit["optimizer_nit"],
            }
        )
    return out


def metrics(rows):
    if not rows:
        return {"n": 0}
    n = len(rows)
    actual_up = sum(r["actual_direction"] == "UP" for r in rows)
    actual_down = n - actual_up
    tp = sum(r["forecast_direction"] == "UP" and r["actual_direction"] == "UP" for r in rows)
    tn = sum(r["forecast_direction"] == "DOWN" and r["actual_direction"] == "DOWN" for r in rows)
    fp = sum(r["forecast_direction"] == "UP" and r["actual_direction"] == "DOWN" for r in rows)
    fn = sum(r["forecast_direction"] == "DOWN" and r["actual_direction"] == "UP" for r in rows)

    sse = sum((r["actual_realp"]-r["realp_forecast"])**2 for r in rows)
    sse_mean = sum((r["actual_realp"]-r["historical_mean_realp"])**2 for r in rows)

    return {
        "n": n,
        "accuracy": (tp+tn)/n,
        "balanced_accuracy": ((tp/actual_up)+(tn/actual_down))/2 if actual_up and actual_down else None,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "forecast_up": tp+fp,
        "forecast_down": tn+fn,
        "up_sensitivity": tp/actual_up if actual_up else None,
        "down_sensitivity": tn/actual_down if actual_down else None,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "always_up_accuracy": actual_up/n,
        "previous_sign_accuracy": sum(r["previous_week_direction"]==r["actual_direction"] for r in rows)/n,
        "historical_mean_realp_direction_accuracy": sum(r["historical_mean_realp_direction"]==r["actual_direction"] for r in rows)/n,
        "previous_realp_direction_accuracy": sum(r["previous_realp_direction"]==r["actual_direction"] for r in rows)/n,
        "mse_realp_model": sse/n,
        "mse_realp_historical_mean": sse_mean/n,
        "r2_oos_realp": 1.0-sse/sse_mean if sse_mean > 0 else None,
        "mean_realp_forecast": sum(r["realp_forecast"] for r in rows)/n,
        "min_realp_forecast": min(r["realp_forecast"] for r in rows),
        "max_realp_forecast": max(r["realp_forecast"] for r in rows),
        "min_lambda_forecast": min(r["lambda_forecast"] for r in rows),
        "max_lambda_forecast": max(r["lambda_forecast"] for r in rows),
        "min_psi": min(r["psi"] for r in rows),
        "max_psi": max(r["psi"] for r in rows),
        "mean_psi": sum(r["psi"] for r in rows)/n,
        "all_origins_converged": all(r["converged_starts"] >= 1 for r in rows),
    }


def gate(m):
    crit = {
        "balanced_accuracy_gte_0_55": m["balanced_accuracy"] is not None and m["balanced_accuracy"] >= 0.55,
        "up_sensitivity_gte_0_40": m["up_sensitivity"] is not None and m["up_sensitivity"] >= 0.40,
        "down_sensitivity_gte_0_40": m["down_sensitivity"] is not None and m["down_sensitivity"] >= 0.40,
        "accuracy_gt_always_up": m["accuracy"] > m["always_up_accuracy"],
        "accuracy_gt_previous_sign": m["accuracy"] > m["previous_sign_accuracy"],
        "r2_oos_realp_gt_0": m["r2_oos_realp"] is not None and m["r2_oos_realp"] > 0.0,
    }
    return {"passed": all(crit.values()), "criteria": crit}


def write_csv(path, rows):
    if not rows:
        raise RuntimeError("NO_ROWS_TO_WRITE")
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n", encoding="utf-8")


def fmt(x):
    if x is None:
        return "NA"
    if isinstance(x, bool):
        return str(x).upper()
    if isinstance(x, int):
        return str(x)
    return f"{x:.10f}"


def stage_pre2025(input_csv: Path, outdir: Path):
    rows = read_rows(input_csv)
    fc = forecasts(rows)
    pre = [r for r in fc if r["target_week"] < "2025-01-01"]
    y23 = [r for r in pre if r["target_week"].startswith("2023-")]
    y24 = [r for r in pre if r["target_week"].startswith("2024-")]
    m23, m24, mall = metrics(y23), metrics(y24), metrics(pre)
    g = gate(m24)

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir/"GOLD_CONTROL_DIRECTION_REALP_CARR_V1_PRE2025_FORECASTS_2026-09-20.csv", pre)
    result = {
        "identity": IDENTITY,
        "stage": "pre2025",
        "2023": m23,
        "2024": m24,
        "combined": mall,
        "gate_2024": g,
    }
    write_json(outdir/"GOLD_CONTROL_DIRECTION_REALP_CARR_V1_PRE2025_RESULT_2026-09-20.json", result)


def stage_2025(input_csv: Path, pre_result: Path, outdir: Path):
    rows = read_rows(input_csv)
    pre = json.loads(pre_result.read_text(encoding="utf-8"))
    fc = forecasts(rows)
    y25 = [r for r in fc if r["target_week"].startswith("2025-")]
    m25 = metrics(y25)

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir/"GOLD_CONTROL_DIRECTION_REALP_CARR_V1_2025_FORECASTS_2026-09-20.csv", y25)
    write_json(
        outdir/"GOLD_CONTROL_DIRECTION_REALP_CARR_V1_2025_RESULT_2026-09-20.json",
        {
            "identity": IDENTITY,
            "stage": "2025_post_diagnostic_unchanged",
            "pre2025_gate": pre["gate_2024"],
            "2025": m25,
        },
    )

    m24 = pre["2024"]
    g = pre["gate_2024"]
    status = (
        "EVALUATED / PRE2025_GATE_PASSED / 2025_POST_DIAGNOSTIC_COMPLETE / NOT_RUNTIME"
        if g["passed"]
        else "EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / REALP_BCARS_FAMILY_CLOSE_CURRENT_SEQUENCE / NOT_RUNTIME"
    )

    lines = [
        "# GOLD CONTROL — DIRECTION_REALP_CARR_V1_RESEARCH RESULT",
        "",
        "**Date:** 2026-09-20  ",
        f"**Identity:** `{IDENTITY}`  ",
        f"**Status:** `{status}`",
        "",
        "## Authority boundary",
        "",
        "This experiment is NOT represented as CARB. The exact CARB mathematical specification was not proven from an accessible primary source. This experiment uses the source-verifiable Realized Probability construction plus the published CARR-filter / linear-regression predictability mechanism.",
        "",
        "## 2024 fixed validation",
        "",
        f"- n = {m24['n']}",
        f"- accuracy = {fmt(m24['accuracy'])}",
        f"- balanced accuracy = {fmt(m24['balanced_accuracy'])}",
        f"- UP sensitivity = {fmt(m24['up_sensitivity'])}",
        f"- DOWN sensitivity = {fmt(m24['down_sensitivity'])}",
        f"- TP/TN/FP/FN = {m24['tp']}/{m24['tn']}/{m24['fp']}/{m24['fn']}",
        f"- forecast UP/DOWN = {m24['forecast_up']}/{m24['forecast_down']}",
        f"- always-UP accuracy = {fmt(m24['always_up_accuracy'])}",
        f"- previous-sign accuracy = {fmt(m24['previous_sign_accuracy'])}",
        f"- historical-mean-RealP direction accuracy = {fmt(m24['historical_mean_realp_direction_accuracy'])}",
        f"- previous-RealP direction accuracy = {fmt(m24['previous_realp_direction_accuracy'])}",
        f"- RealP R2_oos vs expanding historical mean = {fmt(m24['r2_oos_realp'])}",
        f"- RealP forecast range = {fmt(m24['min_realp_forecast'])} .. {fmt(m24['max_realp_forecast'])}",
        f"- preregistered gate passed = {str(g['passed']).upper()}",
        "",
        "Gate components:",
    ]
    for k, v in g["criteria"].items():
        lines.append(f"- {k} = {str(v).upper()}")

    lines += [
        "",
        "## Unchanged 2025 post-diagnostic replay",
        "",
        f"- n = {m25['n']}",
        f"- accuracy = {fmt(m25['accuracy'])}",
        f"- balanced accuracy = {fmt(m25['balanced_accuracy'])}",
        f"- UP sensitivity = {fmt(m25['up_sensitivity'])}",
        f"- DOWN sensitivity = {fmt(m25['down_sensitivity'])}",
        f"- TP/TN/FP/FN = {m25['tp']}/{m25['tn']}/{m25['fp']}/{m25['fn']}",
        f"- forecast UP/DOWN = {m25['forecast_up']}/{m25['forecast_down']}",
        f"- always-UP accuracy = {fmt(m25['always_up_accuracy'])}",
        f"- previous-sign accuracy = {fmt(m25['previous_sign_accuracy'])}",
        f"- RealP R2_oos = {fmt(m25['r2_oos_realp'])}",
        f"- RealP forecast range = {fmt(m25['min_realp_forecast'])} .. {fmt(m25['max_realp_forecast'])}",
        "",
        "## Binding interpretation",
        "",
    ]
    if g["passed"]:
        lines += [
            "The model passed the frozen 2024 gate. The 2025 replay is interpreted only as unchanged historical generalisation evidence. No automatic runtime promotion is authorized.",
        ]
    else:
        lines += [
            "The model failed the frozen 2024 gate. The unchanged 2025 replay cannot rescue the failed pre-2025 validation.",
            "",
            "Binding current-sequence decision: close the B-CARS / Realized-Probability direction family unless the user explicitly reopens it. No CARB invention, threshold rescue, alternate CARR order, exogenous augmentation, or 2025-driven tuning is authorized.",
        ]

    (outdir/"GOLD_CONTROL_DIRECTION_REALP_CARR_V1_RESULT_2026-09-20.md").write_text(
        "\n".join(lines)+"\n", encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--stage", choices=["pre2025", "2025"], required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--pre-result", type=Path)
    args = ap.parse_args()

    if args.stage == "pre2025":
        stage_pre2025(args.input_csv, args.outdir)
    else:
        if args.pre_result is None:
            raise SystemExit("--pre-result required for 2025")
        stage_2025(args.input_csv, args.pre_result, args.outdir)


if __name__ == "__main__":
    main()
