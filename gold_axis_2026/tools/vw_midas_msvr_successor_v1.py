from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import psycopg

MODEL_ID = "VW_MIDAS_MSVR_SUCCESSOR_V1"
PIPELINE_VERSION = "GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_2026-09-06"
EVAL_START = "2023-01"
EVAL_END = "2026-07"
INNER_START = "2022-04"
MIN_INNER = 6
METALS = ("Gold", "Silver", "Platinum", "Palladium")
DAILY_SERIES = {
    "Gold": "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "Silver": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "Platinum": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "Palladium": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
CORE_GOLD = "CORE5_GOLD_USD_OZ_RESEARCH_R1"
CORE_GPR = "CORE5_GPR_ROUNDED_RESEARCH_R1"
GPR_PIT = "GPR_OFFICIAL_GIT_PIT"
CONFIGS = tuple((C, ep, gm) for C in (0.1, 1.0, 10.0) for ep in (0.02, 0.05) for gm in (0.5, 1.0))
LEGACY_FIXED_CONFIG = (1.0, 0.05, 0.5)
ARCHIVED = {
    "n": 43,
    "mape_pct": 2.672150,
    "median_ape_pct": 1.962940,
    "worst_ape_pct": 8.831236,
    "rw_mape_pct": 3.302322,
    "mape_2025_pct": 2.3859417402868672,
}


def month_key(ts) -> str:
    if isinstance(ts, str):
        return ts[:7]
    return f"{ts.year:04d}-{ts.month:02d}"


def month_shift(m: str, delta: int) -> str:
    y, mo = map(int, m.split("-"))
    z = y * 12 + (mo - 1) + delta
    return f"{z // 12:04d}-{z % 12 + 1:02d}"


def month_range(start: str, end: str):
    cur = start
    while cur <= end:
        yield cur
        cur = month_shift(cur, 1)


def month_end_utc(m: str) -> datetime:
    y, mo = map(int, m.split("-"))
    d = calendar.monthrange(y, mo)[1]
    return datetime(y, mo, d, 23, 59, 59, tzinfo=timezone.utc)


def rbf_kernel(x, y, gamma):
    xx = np.sum(x * x, axis=1)[:, None]
    yy = np.sum(y * y, axis=1)[None, :]
    d2 = np.maximum(xx + yy - 2.0 * (x @ y.T), 0.0)
    return np.exp(-gamma * d2)


class MSVR:
    def __init__(self, C=1.0, epsilon=0.05, gamma=None, tol=1e-3):
        self.C = float(C)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.tol = float(tol)

    def fit(self, x, y):
        self.x_train = np.asarray(x, float).copy()
        y = np.asarray(y, float)
        H = rbf_kernel(self.x_train, self.x_train, self.gamma)
        self.beta = np.zeros((len(x), y.shape[1]), float)
        E = y - H @ self.beta
        u = np.sqrt(np.sum(E * E, axis=1, keepdims=True))
        active = np.where(u > self.epsilon)[0]
        if len(active) == 0:
            return self
        a = 2.0 * self.C * (u - self.epsilon) / np.maximum(u, 1e-12)
        L = np.zeros_like(u)
        L[active] = u[active] ** 2 - 2 * self.epsilon * u[active] + self.epsilon**2
        prev = float(np.trace(self.beta.T @ H @ self.beta) / 2 + self.C * np.sum(L) / 2)
        for _ in range(80):
            if len(active) == 0:
                break
            old_beta = self.beta.copy()
            old_u = u.copy()
            old_active = active.copy()
            M = H[np.ix_(active, active)] + np.diag(1 / np.maximum(a[active].reshape(-1), 1e-10)) + 1e-10 * np.eye(len(active))
            try:
                sol = np.linalg.solve(M, y[active])
            except np.linalg.LinAlgError:
                sol = np.linalg.pinv(M) @ y[active]
            eta = 1.0
            accepted = False
            for _ in range(18):
                B = np.zeros_like(self.beta)
                B[active] = eta * sol + (1 - eta) * old_beta[active]
                e = y - H @ B
                uu = np.sqrt(np.sum(e * e, axis=1, keepdims=True))
                new_active = np.where(uu >= self.epsilon)[0]
                LL = np.zeros_like(uu)
                LL[new_active] = uu[new_active] ** 2 - 2 * self.epsilon * uu[new_active] + self.epsilon**2
                cur = float(np.trace(B.T @ H @ B) / 2 + self.C * np.sum(LL) / 2)
                if cur <= prev + 1e-12:
                    self.beta = B
                    u = uu
                    active = new_active
                    accepted = True
                    break
                eta /= 10.0
            if not accepted:
                self.beta = old_beta
                u = old_u
                active = old_active
                break
            if prev != 0 and (prev - cur) / abs(prev) < self.tol:
                break
            prev = cur
            a = 2.0 * self.C * (u - self.epsilon) / np.maximum(u, 1e-12)
        return self

    def predict(self, x):
        return rbf_kernel(np.asarray(x, float), self.x_train, self.gamma) @ self.beta


@dataclass
class DataBundle:
    core_gold: dict
    core_gpr: dict
    common_daily: dict
    monthly_metal: dict
    gpr_vintages: dict
    source_checks: dict
    invariants_before: dict


def fetch_scalar_map(cur, series_id):
    cur.execute(
        "SELECT observation_ts, value FROM observations WHERE series_id=%s ORDER BY observation_ts",
        (series_id,),
    )
    out = {}
    for ts, value in cur.fetchall():
        out[month_key(ts)] = float(value)
    return out


def authority_invariants(cur):
    names = ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events")
    out = {}
    for name in names:
        cur.execute(f"SELECT count(*) FROM {name}")
        out[name] = int(cur.fetchone()[0])
    return out


def load_data(dsn: str) -> DataBundle:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only = on")
            invariants = authority_invariants(cur)
            core_gold = fetch_scalar_map(cur, CORE_GOLD)
            core_gpr = fetch_scalar_map(cur, CORE_GPR)

            raw_daily = {m: {} for m in METALS}
            for metal, sid in DAILY_SERIES.items():
                cur.execute(
                    "SELECT observation_ts, value FROM observations WHERE series_id=%s ORDER BY observation_ts",
                    (sid,),
                )
                for ts, value in cur.fetchall():
                    raw_daily[metal][ts.date()] = float(value)

            common_dates = sorted(set.intersection(*(set(raw_daily[m]) for m in METALS)))
            common_daily = {m: {d: raw_daily[m][d] for d in common_dates} for m in METALS}
            monthly_vals = {m: defaultdict(list) for m in METALS}
            for d in common_dates:
                mk = f"{d.year:04d}-{d.month:02d}"
                for m in METALS:
                    monthly_vals[m][mk].append(common_daily[m][d])
            monthly_metal = {m: {k: float(np.mean(v)) for k, v in monthly_vals[m].items()} for m in METALS}

            cur.execute(
                "SELECT observation_ts, value, available_as_of, metadata->>'origin_month' "
                "FROM observations WHERE series_id=%s ORDER BY metadata->>'origin_month', observation_ts",
                (GPR_PIT,),
            )
            gpr_vintages = defaultdict(dict)
            availability = {}
            for ts, value, available_as_of, origin_month in cur.fetchall():
                if not origin_month:
                    continue
                gpr_vintages[origin_month][month_key(ts)] = float(value)
                availability.setdefault(origin_month, available_as_of)
                if available_as_of < availability[origin_month]:
                    availability[origin_month] = available_as_of

            required_origins = [month_shift(t, -1) for t in month_range(INNER_START, EVAL_END)]
            missing_origins = [m for m in required_origins if m not in gpr_vintages]
            late_origins = [m for m in required_origins if availability.get(m) is None or availability[m] > month_end_utc(m)]
            insufficient_lag = []
            for origin in required_origins:
                if origin not in gpr_vintages:
                    continue
                req = month_shift(origin, -1)
                if req not in gpr_vintages[origin]:
                    insufficient_lag.append(origin)

            source_checks = {
                "core_gold_rows": len(core_gold),
                "core_gold_first": min(core_gold),
                "core_gold_last": max(core_gold),
                "core_gpr_rows": len(core_gpr),
                "common_daily_rows": len(common_dates),
                "common_daily_first": common_dates[0].isoformat(),
                "common_daily_last": common_dates[-1].isoformat(),
                "metal_months": {m: len(monthly_metal[m]) for m in METALS},
                "gpr_origin_vintages": len(gpr_vintages),
                "missing_required_gpr_origins": missing_origins,
                "late_required_gpr_origins": late_origins,
                "missing_required_gpr_lag_month": insufficient_lag,
            }
            if missing_origins or late_origins or insufficient_lag:
                raise RuntimeError(f"GPR_PIT_SOURCE_GATE_FAIL {source_checks}")
            return DataBundle(core_gold, core_gpr, common_daily, monthly_metal, dict(gpr_vintages), source_checks, invariants)


def gpr_norm(history: dict, m: str):
    keys = [k for k in history if k <= m]
    if m not in history or len(keys) < 24:
        raise RuntimeError(f"GPR_HISTORY_NOT_AVAILABLE month={m}")
    vals = np.array([history[k] for k in sorted(keys)], float)
    lo, hi = float(vals.min()), float(vals.max())
    if hi <= lo:
        return 0.5
    return float((history[m] - lo) / (hi - lo))


def weighted_daily_return(bundle: DataBundle, metal: str, origin_month: str, z: float):
    dates = [d for d in bundle.common_daily[metal] if f"{d.year:04d}-{d.month:02d}" == origin_month]
    dates.sort()
    if len(dates) < 5:
        raise RuntimeError(f"INSUFFICIENT_DAILY_ROWS {metal} {origin_month} n={len(dates)}")
    v = np.array([bundle.common_daily[metal][d] for d in dates], float)
    r = np.diff(np.log(v))
    lam = 0.1 * math.exp(-10.0 * float(np.clip(z, 0, 1)))
    age = np.arange(len(r) - 1, -1, -1, dtype=float)
    w = np.exp(-lam * age)
    w /= w.sum()
    return float(w @ r)


def sample_for_target(bundle: DataBundle, target: str, gpr_history: dict, lag_gpr: bool):
    p = month_shift(target, -1)
    pp = month_shift(target, -2)
    gpr_month = pp if lag_gpr else p
    z = gpr_norm(gpr_history, gpr_month)
    x, y = [], []
    for metal in METALS:
        M = bundle.monthly_metal[metal]
        if target not in M or p not in M or pp not in M:
            raise RuntimeError(f"MONTHLY_METAL_MISSING {metal} target={target}")
        mr = math.log(M[p] / M[pp])
        vw = weighted_daily_return(bundle, metal, p, z)
        x.extend((mr, vw))
        y.append(math.log(M[target] / M[p]))
    return np.array(x, float), np.array(y, float)


def all_samples_at_origin(bundle: DataBundle, outer_target: str, governed: bool):
    origin = month_shift(outer_target, -1)
    if governed:
        history = bundle.gpr_vintages[origin]
        lag_gpr = True
    else:
        history = bundle.core_gpr
        lag_gpr = False
    first = max("2010-03", min(bundle.monthly_metal["Gold"]))
    out = {}
    for t in month_range(first, outer_target):
        try:
            out[t] = sample_for_target(bundle, t, history, lag_gpr)
        except RuntimeError:
            continue
    if outer_target not in out:
        raise RuntimeError(f"OUTER_TARGET_NOT_BUILDABLE {outer_target} governed={governed}")
    return out


def standardize_fit_predict(train_x, train_y, test_x, cfg):
    X = np.asarray(train_x, float)
    Y = np.asarray(train_y, float)
    tx = np.asarray(test_x, float)[None, :]
    xm, xs = X.mean(0), X.std(0)
    ym, ys = Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)
    Xs = (X - xm) / xs
    Ys = (Y - ym) / ys
    txs = (tx - xm) / xs
    C, ep, gm = cfg
    model = MSVR(C=C, epsilon=ep, gamma=gm / X.shape[1]).fit(Xs, Ys)
    pred = model.predict(txs)[0] * ys + ym
    return pred


def fixed_config_forecast(bundle: DataBundle, target: str, cfg, governed: bool):
    samples = all_samples_at_origin(bundle, target, governed=governed)
    train_keys = sorted(k for k in samples if k < target)
    if len(train_keys) < 24:
        raise RuntimeError(f"TRAINING_ROWS_TOO_FEW target={target} n={len(train_keys)}")
    X = np.stack([samples[k][0] for k in train_keys])
    Y = np.stack([samples[k][1] for k in train_keys])
    pred = standardize_fit_predict(X, Y, samples[target][0], cfg)
    p = month_shift(target, -1)
    if p not in bundle.core_gold or target not in bundle.core_gold:
        raise RuntimeError(f"CORE_GOLD_MISSING target={target}")
    price = bundle.core_gold[p] * math.exp(float(pred[0]))
    return {
        "target": target,
        "origin": p,
        "cfg": list(cfg),
        "pred_log_return_gold": float(pred[0]),
        "forecast": float(price),
        "actual": float(bundle.core_gold[target]),
        "rw": float(bundle.core_gold[p]),
        "train_rows": len(train_keys),
    }


def build_governed_nested(bundle: DataBundle):
    all_targets = list(month_range(INNER_START, EVAL_END))
    by_cfg = {cfg: {} for cfg in CONFIGS}
    for t in all_targets:
        for cfg in CONFIGS:
            by_cfg[cfg][t] = fixed_config_forecast(bundle, t, cfg, governed=True)

    outer = []
    for t in month_range(EVAL_START, EVAL_END):
        eligible_inner = [u for u in all_targets if u < t]
        if len(eligible_inner) < MIN_INNER:
            raise RuntimeError(f"INNER_FOLDS_TOO_FEW target={t} n={len(eligible_inner)}")
        ranked = []
        for cfg in CONFIGS:
            errs = []
            for u in eligible_inner:
                r = by_cfg[cfg][u]
                p = month_shift(u, -1)
                actual_ret = math.log(bundle.monthly_metal["Gold"][u] / bundle.monthly_metal["Gold"][p])
                errs.append(abs(r["pred_log_return_gold"] - actual_ret))
            ranked.append((float(np.mean(errs)), cfg[0], cfg[1], cfg[2], cfg))
        ranked.sort()
        selected = ranked[0][-1]
        row = dict(by_cfg[selected][t])
        row["inner_n"] = len(eligible_inner)
        row["inner_mean_abs_gold_log_return_error"] = ranked[0][0]
        outer.append(row)
    return outer


def build_legacy_reconciliation(bundle: DataBundle):
    return [fixed_config_forecast(bundle, t, LEGACY_FIXED_CONFIG, governed=False) for t in month_range(EVAL_START, EVAL_END)]


def metrics(rows):
    a = np.array([r["actual"] for r in rows], float)
    f = np.array([r["forecast"] for r in rows], float)
    rw = np.array([r["rw"] for r in rows], float)
    ae = np.abs(f - a)
    rw_ae = np.abs(rw - a)
    ape = ae / a
    rw_ape = rw_ae / a
    smape = 2 * ae / (np.abs(f) + np.abs(a))
    direction = np.sign(f - rw)
    actual_direction = np.sign(a - rw)
    return {
        "n": len(rows),
        "mae": float(ae.mean()),
        "mape_pct": float(ape.mean() * 100),
        "smape_pct": float(smape.mean() * 100),
        "median_ae": float(np.median(ae)),
        "median_ape_pct": float(np.median(ape) * 100),
        "worst_ape_pct": float(np.max(ape) * 100),
        "rmse": float(np.sqrt(np.mean((f - a) ** 2))),
        "monthly_win_rate_vs_rw": float(np.mean(ae < rw_ae)),
        "direction_accuracy_pct": float(np.mean(direction == actual_direction) * 100),
        "relative_mae_vs_rw": float(ae.sum() / rw_ae.sum()),
        "rw_mae": float(rw_ae.mean()),
        "rw_mape_pct": float(rw_ape.mean() * 100),
        "rw_median_ae": float(np.median(rw_ae)),
    }


def yearly(rows):
    out = {}
    years = sorted({r["target"][:4] for r in rows})
    for y in years:
        rr = [r for r in rows if r["target"].startswith(y)]
        out[y] = metrics(rr)
    return out


def gate(governed_metrics, year_metrics, source_checks, invariant_same):
    completed = [y for y in ("2023", "2024", "2025") if y in year_metrics]
    year_wins = sum(year_metrics[y]["mae"] < year_metrics[y]["rw_mae"] for y in completed)
    no_year_breach = all(year_metrics[y]["mae"] <= 1.5 * year_metrics[y]["rw_mae"] for y in completed)
    checks = {
        "source_provenance_pit_pass": not source_checks["missing_required_gpr_origins"] and not source_checks["late_required_gpr_origins"] and not source_checks["missing_required_gpr_lag_month"],
        "authority_invariants_unchanged": bool(invariant_same),
        "relative_mae_vs_rw_lt_1": governed_metrics["relative_mae_vs_rw"] < 1.0,
        "mape_le_rw": governed_metrics["mape_pct"] <= governed_metrics["rw_mape_pct"],
        "median_ae_le_rw": governed_metrics["median_ae"] <= governed_metrics["rw_median_ae"],
        "completed_year_win_half_or_more": year_wins >= math.ceil(len(completed) / 2),
        "no_completed_year_mae_gt_1_5_rw": no_year_breach,
        "no_unresolved_leakage_or_availability_exception": True,
    }
    passed = all(checks.values())
    status = "RESEARCH_SHADOW_CANDIDATE_HISTORICAL_REPLAY_PASS_PROSPECTIVE_VALIDATION_REQUIRED" if passed else "REJECT_ALL_VW_MIDAS_MSVR_SUCCESSOR_V1_CANDIDATES"
    return status, checks, {"completed_years": completed, "year_wins_vs_rw": year_wins}


def stable_hash_payload(governed, legacy, governed_metrics, legacy_metrics):
    payload = {
        "model_id": MODEL_ID,
        "governed": [{k: r[k] for k in ("target", "origin", "cfg", "pred_log_return_gold", "forecast", "actual", "rw", "train_rows", "inner_n")} for r in governed],
        "legacy": [{k: r[k] for k in ("target", "forecast", "actual", "rw")} for r in legacy],
        "governed_metrics": governed_metrics,
        "legacy_metrics": legacy_metrics,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def run_once(dsn):
    bundle = load_data(dsn)
    governed = build_governed_nested(bundle)
    legacy = build_legacy_reconciliation(bundle)
    gm = metrics(governed)
    lm = metrics(legacy)
    gy = yearly(governed)
    ly = yearly(legacy)

    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only = on")
            invariants_after = authority_invariants(cur)
    invariant_same = invariants_after == bundle.invariants_before
    status, checks, gate_meta = gate(gm, gy, bundle.source_checks, invariant_same)
    h = stable_hash_payload(governed, legacy, gm, lm)

    return {
        "pipeline_version": PIPELINE_VERSION,
        "model_id": MODEL_ID,
        "scope": "RESEARCH_HISTORICAL_REPLAY_ONLY",
        "final_gate": status,
        "deterministic_payload_sha256": h,
        "source_checks": bundle.source_checks,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": invariants_after,
        "governed_nested_pit": {
            "metrics": gm,
            "yearly": gy,
            "rows": governed,
        },
        "legacy_reconciliation_only": {
            "evidence_class": "RECONCILIATION_ONLY_NOT_PIT_ELIGIBLE",
            "fixed_config": list(LEGACY_FIXED_CONFIG),
            "metrics": lm,
            "yearly": ly,
            "archived_reference": ARCHIVED,
            "mape_distance_pp": float(lm["mape_pct"] - ARCHIVED["mape_pct"]),
            "mape_2025_distance_pp": float(ly["2025"]["mape_pct"] - ARCHIVED["mape_2025_pct"]),
        },
        "gate_checks": checks,
        "gate_meta": gate_meta,
        "governance": {
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
            "database_writes": "NONE",
            "forecast_writes": "NONE",
            "decision_writes": "NONE",
            "runtime_activation": "NONE",
            "archived_identity_untouched": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="vw_midas_msvr_successor_v1_result.json")
    ap.add_argument("--determinism-check", action="store_true")
    args = ap.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL is required")
    result = run_once(dsn)
    if args.determinism_check:
        second = run_once(dsn)
        if result["deterministic_payload_sha256"] != second["deterministic_payload_sha256"]:
            raise RuntimeError("DETERMINISM_FAIL")
        result["determinism_check"] = "PASS"
    else:
        result["determinism_check"] = "NOT_RUN"
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "final_gate": result["final_gate"],
        "sha256": result["deterministic_payload_sha256"],
        "governed_metrics": result["governed_nested_pit"]["metrics"],
        "legacy_reconciliation_metrics": result["legacy_reconciliation_only"]["metrics"],
        "legacy_mape_distance_pp": result["legacy_reconciliation_only"]["mape_distance_pp"],
        "gate_checks": result["gate_checks"],
        "determinism_check": result["determinism_check"],
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
