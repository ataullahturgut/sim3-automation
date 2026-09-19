#!/usr/bin/env python3
"""DIRECTION_BCTX_AR_V1_RESEARCH

Preregistered BCT-AR successor for Gold weekly returns.

Authority:
  GOLD_CONTROL_DIRECTION_BCTX_AR_V1_PREREG_2026-09-19.md

Method basis:
  Papageorgiou & Kontoyiannis, BCT-X / BCT-AR.
  Exact local AR marginal likelihood + GCTW evidence + GBCT MAP tree.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

IDENTITY = "DIRECTION_BCTX_AR_V1_RESEARCH"
D = 10
M = 3
BETA = 1.0 - 2.0 ** (-M + 1)  # 0.75
TAU = 1.0
LAMBDA = 1.0
P_CANDIDATES = (1, 2, 3, 4, 5)
QUANTILE_LEVELS = tuple(i / 10.0 for i in range(1, 10))
DEV_END = date(2023, 12, 31)
EPS_TIE = 1e-10


@dataclass(frozen=True)
class Row:
    week_start: date
    weekly_return: float


@dataclass
class NodeStats:
    n: int
    s1: float
    s2: np.ndarray
    s3: np.ndarray


def read_rows(path: Path) -> list[Row]:
    out: list[Row] = []
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        required = {"week_start", "weekly_return"}
        if not required.issubset(set(rd.fieldnames or [])):
            raise ValueError(f"Missing columns: {sorted(required)}")
        for r in rd:
            w = date.fromisoformat(r["week_start"])
            x = float(r["weekly_return"])
            if not math.isfinite(x):
                raise ValueError(f"Nonfinite return at {w}")
            out.append(Row(w, x))
    if not out:
        raise ValueError("No rows")
    if any(out[i].week_start >= out[i + 1].week_start for i in range(len(out) - 1)):
        raise ValueError("week_start must be strictly increasing")
    return out


def quantize_value(x: float, c1: float, c2: float) -> int:
    if x < c1:
        return 0
    if x < c2:
        return 1
    return 2


def quantize_series(x: np.ndarray, c1: float, c2: float) -> np.ndarray:
    q = np.empty(len(x), dtype=np.int8)
    q[x < c1] = 0
    q[(x >= c1) & (x < c2)] = 1
    q[x >= c2] = 2
    return q


def empty_stats(k: int) -> NodeStats:
    return NodeStats(0, 0.0, np.zeros(k), np.zeros((k, k)))


def build_stats(
    x: np.ndarray, c1: float, c2: float, p: int
) -> tuple[Dict[Tuple[int, ...], NodeStats], set[Tuple[int, ...]]]:
    if len(x) <= max(D, p):
        raise ValueError("Insufficient series length")

    k = p + 1  # intercept + p lags
    q = quantize_series(x, c1, c2)
    stats: Dict[Tuple[int, ...], NodeStats] = {}
    observed: set[Tuple[int, ...]] = set()

    start = max(D, p)
    for i in range(start, len(x)):
        ctx_full = tuple(int(q[i - j - 1]) for j in range(D))
        reg = np.array([1.0] + [float(x[i - j - 1]) for j in range(p)], dtype=float)
        y = float(x[i])

        for depth in range(D + 1):
            ctx = ctx_full[:depth]
            observed.add(ctx)
            s = stats.get(ctx)
            if s is None:
                s = empty_stats(k)
                stats[ctx] = s
            s.n += 1
            s.s1 += y * y
            s.s2 += y * reg
            s.s3 += np.outer(reg, reg)

    return stats, observed


def log_pe(s: NodeStats | None, p: int) -> float:
    k = p + 1
    if s is None or s.n == 0:
        return 0.0

    ident = np.eye(k)
    a = s.s3 + ident
    sign, logdet_a = np.linalg.slogdet(a)
    if sign <= 0:
        raise RuntimeError("Non-positive determinant in AR evidence")

    # Sigma0 = I and mu0 = 0.
    sol = np.linalg.solve(a, s.s2)
    ds = float(s.s1 - s.s2 @ sol)
    if ds < 0 and abs(ds) < 1e-10:
        ds = 0.0
    if ds < 0:
        raise RuntimeError(f"Negative D_s: {ds}")

    log_c = 0.5 * (s.n * math.log(2.0 * math.pi) + logdet_a)
    return (
        -log_c
        + math.lgamma(TAU + s.n / 2.0)
        + TAU * math.log(LAMBDA)
        - math.lgamma(TAU)
        - (TAU + s.n / 2.0) * math.log(LAMBDA + ds / 2.0)
    )


def logsumexp2(a: float, b: float) -> float:
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


def has_observed_child(ctx: Tuple[int, ...], observed: set[Tuple[int, ...]]) -> bool:
    if len(ctx) >= D:
        return False
    return any(ctx + (j,) in observed for j in range(M))


def gctw_log_evidence(
    stats: Dict[Tuple[int, ...], NodeStats],
    observed: set[Tuple[int, ...]],
    p: int,
) -> float:
    memo: Dict[Tuple[int, ...], float] = {}

    def rec(ctx: Tuple[int, ...]) -> float:
        if ctx in memo:
            return memo[ctx]
        local = log_pe(stats.get(ctx), p)

        if len(ctx) == D or not has_observed_child(ctx, observed):
            memo[ctx] = local
            return local

        split = sum(rec(ctx + (j,)) for j in range(M))
        val = logsumexp2(
            math.log(BETA) + local,
            math.log(1.0 - BETA) + split,
        )
        memo[ctx] = val
        return val

    return rec(())


def map_tree(
    stats: Dict[Tuple[int, ...], NodeStats],
    observed: set[Tuple[int, ...]],
    p: int,
) -> tuple[set[Tuple[int, ...]], float]:
    memo: Dict[Tuple[int, ...], float] = {}
    choose_leaf: Dict[Tuple[int, ...], bool] = {}

    def rec(ctx: Tuple[int, ...]) -> float:
        if ctx in memo:
            return memo[ctx]

        local = log_pe(stats.get(ctx), p)

        if len(ctx) == D:
            choose_leaf[ctx] = True
            memo[ctx] = local
            return local

        if not has_observed_child(ctx, observed):
            # T_MAX leaf at depth < D. Here Pe=1 for the absent sibling
            # closure used by the proper m-ary tree.
            choose_leaf[ctx] = True
            memo[ctx] = math.log(BETA) + local
            return memo[ctx]

        leaf_score = math.log(BETA) + local
        branch_score = math.log(1.0 - BETA) + sum(
            rec(ctx + (j,)) for j in range(M)
        )

        # Source MAP recursion. Favor pruning at exact numerical ties.
        if leaf_score >= branch_score:
            choose_leaf[ctx] = True
            memo[ctx] = leaf_score
        else:
            choose_leaf[ctx] = False
            memo[ctx] = branch_score
        return memo[ctx]

    root_score = rec(())

    leaves: set[Tuple[int, ...]] = set()

    def collect(ctx: Tuple[int, ...]) -> None:
        if len(ctx) == D or choose_leaf.get(ctx, True):
            leaves.add(ctx)
            return
        for j in range(M):
            collect(ctx + (j,))

    collect(())
    return leaves, root_score


def leaf_for_context(
    leaves: set[Tuple[int, ...]], ctx_full: Tuple[int, ...]
) -> Tuple[int, ...]:
    if () in leaves:
        return ()
    for depth in range(1, D + 1):
        ctx = ctx_full[:depth]
        if ctx in leaves:
            return ctx
    raise RuntimeError("No MAP leaf matched current context")


def map_coefficients(s: NodeStats | None, p: int) -> np.ndarray:
    k = p + 1
    if s is None or s.n == 0:
        return np.zeros(k)
    return np.linalg.solve(s.s3 + np.eye(k), s.s2)


def evidence_grid(
    x_dev: np.ndarray, threshold_values: list[float]
) -> tuple[list[dict], dict]:
    pairs = [
        (float(threshold_values[i]), float(threshold_values[j]))
        for i in range(len(threshold_values))
        for j in range(i + 1, len(threshold_values))
        if threshold_values[i] < threshold_values[j]
    ]
    if not pairs:
        raise RuntimeError("No distinct threshold pairs")

    grid: list[dict] = []
    for p in P_CANDIDATES:
        for c1, c2 in pairs:
            stats, observed = build_stats(x_dev, c1, c2, p)
            ev = gctw_log_evidence(stats, observed, p)
            grid.append(
                {
                    "p": p,
                    "c1_z": c1,
                    "c2_z": c2,
                    "log_evidence": ev,
                }
            )

    grid.sort(key=lambda z: (-z["log_evidence"], z["p"], z["c1_z"], z["c2_z"]))
    best_ev = grid[0]["log_evidence"]
    ties = [g for g in grid if abs(g["log_evidence"] - best_ev) <= EPS_TIE]
    ties.sort(key=lambda z: (z["p"], z["c1_z"], z["c2_z"]))
    return grid, ties[0]


def forecast_one(
    x_seen: np.ndarray,
    mu_train: float,
    sd_train: float,
    c1: float,
    c2: float,
    p: int,
) -> dict:
    z = (x_seen - mu_train) / sd_train
    stats, observed = build_stats(z, c1, c2, p)
    leaves, map_score = map_tree(stats, observed, p)
    q = quantize_series(z, c1, c2)
    ctx_full = tuple(int(q[len(z) - j - 1]) for j in range(D))
    leaf = leaf_for_context(leaves, ctx_full)
    coef = map_coefficients(stats.get(leaf), p)
    reg = np.array([1.0] + [float(z[len(z) - j - 1]) for j in range(p)])
    pred_z = float(coef @ reg)
    pred_return = mu_train + sd_train * pred_z

    depths = [len(s) for s in leaves]
    return {
        "pred_z": pred_z,
        "pred_return": pred_return,
        "state": "ROOT" if not leaf else "".join(str(v) for v in leaf),
        "state_depth": len(leaf),
        "state_support": 0 if stats.get(leaf) is None else stats[leaf].n,
        "tree_leaves": len(leaves),
        "tree_max_depth": max(depths) if depths else 0,
        "map_log_score": float(map_score),
    }


def metrics(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}

    n = len(rows)
    au = sum(r["actual_up"] for r in rows)
    ad = n - au
    tp = sum(r["forecast_up"] == 1 and r["actual_up"] == 1 for r in rows)
    tn = sum(r["forecast_up"] == 0 and r["actual_up"] == 0 for r in rows)
    fp = sum(r["forecast_up"] == 1 and r["actual_up"] == 0 for r in rows)
    fn = sum(r["forecast_up"] == 0 and r["actual_up"] == 1 for r in rows)

    errors = np.array([r["pred_return"] - r["actual_return"] for r in rows], dtype=float)
    tree_leaves = np.array([r["tree_leaves"] for r in rows], dtype=float)
    tree_depths = np.array([r["tree_max_depth"] for r in rows], dtype=float)

    return {
        "n": n,
        "accuracy": (tp + tn) / n,
        "balanced_accuracy": ((tp / au) + (tn / ad)) / 2.0 if au and ad else None,
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
        "previous_sign_accuracy": sum(
            r["previous_up"] == r["actual_up"] for r in rows
        ) / n,
        "rmse_return": float(np.sqrt(np.mean(errors ** 2))),
        "mae_return": float(np.mean(np.abs(errors))),
        "mean_pred_return": float(np.mean([r["pred_return"] for r in rows])),
        "median_tree_leaves": float(np.median(tree_leaves)),
        "max_tree_leaves": int(np.max(tree_leaves)),
        "median_tree_max_depth": float(np.median(tree_depths)),
        "max_tree_max_depth": int(np.max(tree_depths)),
    }


def gate(m: dict) -> dict:
    passed = bool(
        m["balanced_accuracy"] is not None
        and m["balanced_accuracy"] >= 0.55
        and m["up_sensitivity"] is not None
        and m["up_sensitivity"] >= 0.40
        and m["down_sensitivity"] is not None
        and m["down_sensitivity"] >= 0.40
        and m["accuracy"] > m["always_up_accuracy"]
        and m["accuracy"] > m["previous_sign_accuracy"]
    )
    return {
        "passed": passed,
        "criteria": {
            "balanced_accuracy_gte_0_55": m["balanced_accuracy"] >= 0.55,
            "up_sensitivity_gte_0_40": m["up_sensitivity"] >= 0.40,
            "down_sensitivity_gte_0_40": m["down_sensitivity"] >= 0.40,
            "accuracy_gt_always_up": m["accuracy"] > m["always_up_accuracy"],
            "accuracy_gt_previous_sign": m["accuracy"] > m["previous_sign_accuracy"],
        },
    }


def forecast_year(
    rows: list[Row],
    year: int,
    config: dict,
) -> list[dict]:
    raw = np.array([r.weekly_return for r in rows], dtype=float)
    mu = float(config["mu_train"])
    sd = float(config["sd_train"])
    c1 = float(config["selected"]["c1_z"])
    c2 = float(config["selected"]["c2_z"])
    p = int(config["selected"]["p"])

    out: list[dict] = []
    for t, r in enumerate(rows):
        if r.week_start.year != year:
            continue
        if t <= max(D, p):
            continue

        f = forecast_one(raw[:t], mu, sd, c1, c2, p)
        actual = float(raw[t])
        previous = float(raw[t - 1])
        out.append(
            {
                "origin_week": rows[t - 1].week_start.isoformat(),
                "target_week": r.week_start.isoformat(),
                "pred_return": f["pred_return"],
                "actual_return": actual,
                "forecast_up": int(f["pred_return"] > 0.0),
                "actual_up": int(actual > 0.0),
                "previous_up": int(previous > 0.0),
                "pred_z": f["pred_z"],
                "state": f["state"],
                "state_depth": f["state_depth"],
                "state_support": f["state_support"],
                "tree_leaves": f["tree_leaves"],
                "tree_max_depth": f["tree_max_depth"],
                "map_log_score": f["map_log_score"],
            }
        )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def select_and_pre2025(input_path: Path, outdir: Path) -> None:
    rows = read_rows(input_path)
    dev = [r for r in rows if r.week_start <= DEV_END]
    if len(dev) < 30:
        raise RuntimeError("Development sample unexpectedly short")

    x_dev_raw = np.array([r.weekly_return for r in dev], dtype=float)
    mu = float(np.mean(x_dev_raw))
    sd = float(np.std(x_dev_raw, ddof=1))
    if not math.isfinite(sd) or sd <= 0:
        raise RuntimeError("Invalid development sample sd")

    x_dev = (x_dev_raw - mu) / sd
    qvals = [float(np.quantile(x_dev, q)) for q in QUANTILE_LEVELS]
    qvals = sorted(set(qvals))
    if len(qvals) < 3:
        raise RuntimeError("Too few distinct quantile candidate values")

    grid, selected = evidence_grid(x_dev, qvals)
    config = {
        "identity": IDENTITY,
        "method": "BCT-AR / BCT-X",
        "reference_repo": "IoannisPapageorgiou/Replication_BCTX",
        "reference_commit": "8e34c5fe74797bfaad7583dae1aa46c5d01bf21d",
        "m": M,
        "D": D,
        "beta": BETA,
        "tau": TAU,
        "lambda": LAMBDA,
        "mu0": "zero vector",
        "Sigma0": "identity",
        "p_candidates": list(P_CANDIDATES),
        "quantile_levels": list(QUANTILE_LEVELS),
        "threshold_candidate_values_z": qvals,
        "development_start": dev[0].week_start.isoformat(),
        "development_end": dev[-1].week_start.isoformat(),
        "development_n": len(dev),
        "mu_train": mu,
        "sd_train": sd,
        "selected": selected,
        "direction_rule": "UP iff predicted original-scale weekly_return > 0",
    }

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_EVIDENCE_GRID_2026-09-19.csv", grid)
    write_json(outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_FROZEN_CONFIG_2026-09-19.json", config)

    fc = forecast_year(rows, 2024, config)
    m = metrics(fc)
    g = gate(m)
    summary = {
        "identity": IDENTITY,
        "stage": "pre2025_2024_fixed_validation",
        "selected": selected,
        "metrics": m,
        "gate": g,
    }
    write_csv(outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_PRE2025_FORECASTS_2026-09-19.csv", fc)
    write_json(outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_PRE2025_RESULT_2026-09-19.json", summary)


def run_2025(input_path: Path, config_path: Path, pre_result_path: Path, outdir: Path) -> None:
    rows = read_rows(input_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    pre = json.loads(pre_result_path.read_text(encoding="utf-8"))

    fc = forecast_year(rows, 2025, config)
    m = metrics(fc)
    result = {
        "identity": IDENTITY,
        "stage": "2025_post_diagnostic_unchanged_replay",
        "selected": config["selected"],
        "pre2025_gate": pre["gate"],
        "metrics": m,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_2025_FORECASTS_2026-09-19.csv", fc)
    write_json(outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_2025_RESULT_2026-09-19.json", result)

    pm = pre["metrics"]
    g = pre["gate"]
    status = (
        "EVALUATED / PRE2025_GATE_PASSED / POST_DIAGNOSTIC_2025_COMPLETE / NOT_RUNTIME"
        if g["passed"]
        else "EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / BCT_FAMILY_CLOSE_CURRENT_SEQUENCE / NOT_RUNTIME"
    )

    lines = [
        "# GOLD CONTROL — DIRECTION_BCTX_AR_V1_RESEARCH RESULT",
        "",
        "**Date:** 2026-09-19  ",
        f"**Identity:** `{IDENTITY}`  ",
        f"**Status:** `{status}`",
        "",
        "## Frozen selected configuration",
        "",
        f"- m = {M}",
        f"- D = {D}",
        f"- beta = {BETA:.12g}",
        f"- p = {config['selected']['p']}",
        f"- c1_z = {config['selected']['c1_z']:.12g}",
        f"- c2_z = {config['selected']['c2_z']:.12g}",
        f"- selected development log evidence = {config['selected']['log_evidence']:.12g}",
        f"- development scaling mean = {config['mu_train']:.12g}",
        f"- development scaling sd = {config['sd_train']:.12g}",
        "",
        "Hyperparameter/quantiser selection used only the development sample through 2023-12-25 and exact GCTW evidence. No 2024 or 2025 direction score entered selection.",
        "",
        "## 2024 fixed validation",
        "",
        f"- n = {pm['n']}",
        f"- accuracy = {pm['accuracy']:.10f}",
        f"- balanced accuracy = {pm['balanced_accuracy']:.10f}",
        f"- UP sensitivity = {pm['up_sensitivity']:.10f}",
        f"- DOWN sensitivity = {pm['down_sensitivity']:.10f}",
        f"- TP/TN/FP/FN = {pm['tp']}/{pm['tn']}/{pm['fp']}/{pm['fn']}",
        f"- forecast UP/DOWN = {pm['forecast_up']}/{pm['forecast_down']}",
        f"- always-UP accuracy = {pm['always_up_accuracy']:.10f}",
        f"- previous-sign accuracy = {pm['previous_sign_accuracy']:.10f}",
        f"- return RMSE = {pm['rmse_return']:.10f}",
        f"- return MAE = {pm['mae_return']:.10f}",
        f"- pre-registered gate passed = {str(g['passed']).upper()}",
        "",
        "Gate components:",
    ]
    for k, v in g["criteria"].items():
        lines.append(f"- {k} = {str(v).upper()}")

    lines += [
        "",
        "## Unchanged 2025 post-diagnostic replay",
        "",
        f"- n = {m['n']}",
        f"- accuracy = {m['accuracy']:.10f}",
        f"- balanced accuracy = {m['balanced_accuracy']:.10f}",
        f"- UP sensitivity = {m['up_sensitivity']:.10f}",
        f"- DOWN sensitivity = {m['down_sensitivity']:.10f}",
        f"- TP/TN/FP/FN = {m['tp']}/{m['tn']}/{m['fp']}/{m['fn']}",
        f"- forecast UP/DOWN = {m['forecast_up']}/{m['forecast_down']}",
        f"- always-UP accuracy = {m['always_up_accuracy']:.10f}",
        f"- previous-sign accuracy = {m['previous_sign_accuracy']:.10f}",
        f"- return RMSE = {m['rmse_return']:.10f}",
        f"- return MAE = {m['mae_return']:.10f}",
        "",
        "## Binding interpretation",
        "",
    ]

    if g["passed"]:
        lines += [
            "BCT-AR passed the preregistered 2024 direction gate. The 2025 replay remains post-diagnostic historical evidence and does not authorize tuning.",
            "",
            "No runtime or production promotion is automatic; a separate project decision is required.",
        ]
    else:
        lines += [
            "BCT-AR failed the preregistered 2024 direction gate. The unchanged 2025 replay cannot rescue the failed pre-2025 validation.",
            "",
            "Binding current-sequence decision: close the BCT direction family after BCT/CTW V1 and this BCT-AR successor. No D/beta/window/threshold/quantiser rescue is authorized unless the user explicitly reopens the family.",
        ]

    (outdir / "GOLD_CONTROL_DIRECTION_BCTX_AR_V1_RESULT_2026-09-19.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--stage", choices=["pre2025", "2025"], required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--pre-result", type=Path)
    args = ap.parse_args()

    if args.stage == "pre2025":
        select_and_pre2025(args.input_csv, args.outdir)
    else:
        if args.config is None or args.pre_result is None:
            raise SystemExit("--config and --pre-result are required for 2025 stage")
        run_2025(args.input_csv, args.config, args.pre_result, args.outdir)


if __name__ == "__main__":
    main()
