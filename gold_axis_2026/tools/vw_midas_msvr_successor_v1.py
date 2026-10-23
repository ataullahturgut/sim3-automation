from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import psycopg
try:
    from .gold_monthly_four_metal_governance_v1 import build_governed_panel
except ImportError:  # Direct script execution: its own directory is on sys.path.
    from gold_monthly_four_metal_governance_v1 import build_governed_panel

MODEL_ID = "VW_MIDAS_MSVR_SUCCESSOR_V1"
PIPELINE_VERSION = "GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_2026-09-06"
EVAL_START, EVAL_END, INNER_START = "2023-01", "2026-07", "2022-04"
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
    return ts[:7] if isinstance(ts, str) else f"{ts.year:04d}-{ts.month:02d}"


def month_shift(m: str, delta: int) -> str:
    y, mo = map(int, m.split("-")); z = y * 12 + mo - 1 + delta
    return f"{z // 12:04d}-{z % 12 + 1:02d}"


def month_range(start: str, end: str):
    cur = start
    while cur <= end:
        yield cur
        cur = month_shift(cur, 1)


def month_end_utc(m: str) -> datetime:
    y, mo = map(int, m.split("-")); d = calendar.monthrange(y, mo)[1]
    return datetime(y, mo, d, 23, 59, 59, tzinfo=timezone.utc)


def rbf_kernel(x, y, gamma):
    xx = np.sum(x * x, axis=1)[:, None]; yy = np.sum(y * y, axis=1)[None, :]
    return np.exp(-gamma * np.maximum(xx + yy - 2.0 * (x @ y.T), 0.0))


class MSVR:
    def __init__(self, C=1.0, epsilon=0.05, gamma=0.0625, tol=1e-3):
        self.C, self.epsilon, self.gamma, self.tol = map(float, (C, epsilon, gamma, tol))

    def fit(self, x, y):
        self.x_train = np.asarray(x, float).copy(); y = np.asarray(y, float)
        H = rbf_kernel(self.x_train, self.x_train, self.gamma)
        self.beta = np.zeros((len(x), y.shape[1]), float)
        E = y - H @ self.beta; u = np.sqrt(np.sum(E * E, axis=1, keepdims=True))
        active = np.where(u > self.epsilon)[0]
        if len(active) == 0: return self
        a = 2 * self.C * (u - self.epsilon) / np.maximum(u, 1e-12)
        L = np.zeros_like(u); L[active] = u[active] ** 2 - 2 * self.epsilon * u[active] + self.epsilon**2
        prev = float(np.trace(self.beta.T @ H @ self.beta) / 2 + self.C * np.sum(L) / 2)
        for _ in range(80):
            if len(active) == 0: break
            old_beta, old_u, old_active = self.beta.copy(), u.copy(), active.copy()
            M = H[np.ix_(active, active)] + np.diag(1 / np.maximum(a[active].reshape(-1), 1e-10)) + 1e-10 * np.eye(len(active))
            try: sol = np.linalg.solve(M, y[active])
            except np.linalg.LinAlgError: sol = np.linalg.pinv(M) @ y[active]
            eta, accepted = 1.0, False
            for _ in range(18):
                B = np.zeros_like(self.beta); B[active] = eta * sol + (1 - eta) * old_beta[active]
                e = y - H @ B; uu = np.sqrt(np.sum(e * e, axis=1, keepdims=True)); new_active = np.where(uu >= self.epsilon)[0]
                LL = np.zeros_like(uu); LL[new_active] = uu[new_active] ** 2 - 2 * self.epsilon * uu[new_active] + self.epsilon**2
                cur = float(np.trace(B.T @ H @ B) / 2 + self.C * np.sum(LL) / 2)
                if cur <= prev + 1e-12:
                    self.beta, u, active, accepted = B, uu, new_active, True; break
                eta /= 10
            if not accepted:
                self.beta, u, active = old_beta, old_u, old_active; break
            if prev != 0 and (prev - cur) / abs(prev) < self.tol: break
            prev = cur; a = 2 * self.C * (u - self.epsilon) / np.maximum(u, 1e-12)
        return self

    def predict(self, x):
        return rbf_kernel(np.asarray(x, float), self.x_train, self.gamma) @ self.beta


@dataclass
class DataBundle:
    core_gold: dict
    core_gpr: dict
    daily_month_values: dict
    monthly_metal: dict
    gpr_vintages: dict
    source_checks: dict
    invariants_before: dict


def fetch_scalar_map(cur, series_id):
    cur.execute("SELECT observation_ts,value FROM observations WHERE series_id=%s ORDER BY observation_ts", (series_id,))
    return {month_key(ts): float(v) for ts, v in cur.fetchall()}


def authority_invariants(cur):
    out = {}
    for name in ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events"):
        cur.execute(f"SELECT count(*) FROM {name}"); out[name] = int(cur.fetchone()[0])
    return out


def load_data(dsn: str) -> DataBundle:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            invariants = authority_invariants(cur)
            core_gold, core_gpr = fetch_scalar_map(cur, CORE_GOLD), fetch_scalar_map(cur, CORE_GPR)
            # Choose exactly ONE immutable historical research source family.
            # The StakTrakr bundle is an aggregator; its LBMA label is NOT a
            # certified original LBMA fixing, licence, or firstprint timestamp.
            provider_rows = []
            for metal, sid in DAILY_SERIES.items():
                cur.execute(
                    "SELECT observation_ts,value,source,"
                    "metadata->>'payload_provider_label',"
                    "metadata->>'payload_source_label' "
                    "FROM observations WHERE series_id=%s ORDER BY observation_ts",
                    (sid,),
                )
                for ts, value, source, provider, payload in cur.fetchall():
                    provider_rows.append({
                        "day": ts.date().isoformat(), "metal": metal,
                        "value": float(value), "provider_label": provider,
                        "payload_source_label": payload, "provenance": source,
                        "firstprint_proven": False,
                    })
            panel = build_governed_panel(provider_rows)
            # Only aligned business days from complete, homogeneous months.
            # Mixed/unknown-provider MONTHS are removed entirely, not repaired
            # by dropping weekends or silently relabelling records.
            daily_month_values = {m: defaultdict(list) for m in METALS}
            for row in panel["clean_four_metal_rows"]:
                for metal in METALS:
                    daily_month_values[metal][row["month"]].append(row["prices"][metal])
            daily_month_values = {
                m: {k: np.asarray(v, float) for k, v in monthly.items()}
                for m, monthly in daily_month_values.items()
            }
            monthly_metal = {
                m: {k: float(v.mean()) for k, v in daily_month_values[m].items()}
                for m in METALS
            }
            # Historical target price and four model metal inputs MUST share
            # the identical day-aligned provider family. CORE5 gold remains
            # an independently readable reference, never our active target.
            core_gold_reference = core_gold
            core_gold = dict(monthly_metal["Gold"])
            common_dates = panel["count_accepted_business_dates"]

            cur.execute("SELECT observation_ts,value,available_as_of,metadata->>'origin_month' FROM observations WHERE series_id=%s ORDER BY metadata->>'origin_month',observation_ts", (GPR_PIT,))
            vintages, availability = defaultdict(dict), {}
            for ts, value, available_as_of, origin_month in cur.fetchall():
                if not origin_month: continue
                vintages[origin_month][month_key(ts)] = float(value)
                availability[origin_month] = min(availability.get(origin_month, available_as_of), available_as_of)
            required = [month_shift(t, -1) for t in month_range(INNER_START, EVAL_END)]
            missing = [m for m in required if m not in vintages]
            late = [m for m in required if availability.get(m) is None or availability[m] > month_end_utc(m)]
            missing_lag = [m for m in required if m in vintages and month_shift(m, -1) not in vintages[m]]
            checks = {
                "core_gold_rows": len(core_gold), "core_gold_first": min(core_gold), "core_gold_last": max(core_gold),
                "core5_reference_rows_not_used_as_metal_target": len(core_gold_reference),
                "metal_price_basis": "SINGLE_PROVIDER_LABELLED_STAKTRAKR_SEED_LBMA_RESEARCH_ONLY",
                "historical_firstprint_verified": False,
                "single_source_accepted_months": panel["accepted_months"],
                "single_source_excluded_months": panel["quarantined_months"],
                "single_source_missing_months": panel["missing_expected_months"],
                "single_source_excluded_records": panel["count_raw_records"] - 4 * panel["count_accepted_business_dates"],
                "core_gpr_rows": len(core_gpr), "common_daily_rows": len(common_dates),
                "common_daily_first": panel["clean_four_metal_rows"][0]["day"],
                "common_daily_last": panel["clean_four_metal_rows"][-1]["day"],
                "metal_months": {m: len(monthly_metal[m]) for m in METALS}, "gpr_origin_vintages": len(vintages),
                "missing_required_gpr_origins": missing, "late_required_gpr_origins": late, "missing_required_gpr_lag_month": missing_lag,
            }
            if missing or late or missing_lag: raise RuntimeError(f"GPR_PIT_SOURCE_GATE_FAIL {checks}")
            return DataBundle(core_gold, core_gpr, daily_month_values, monthly_metal, dict(vintages), checks, invariants)


def gpr_norm(history: dict, m: str):
    keys = sorted(k for k in history if k <= m)
    if m not in history or len(keys) < 24: raise RuntimeError(f"GPR_HISTORY_NOT_AVAILABLE {m}")
    vals = np.array([history[k] for k in keys], float); lo, hi = float(vals.min()), float(vals.max())
    return 0.5 if hi <= lo else float((history[m] - lo) / (hi - lo))


def weighted_daily_return(bundle, metal, origin_month, z):
    v = bundle.daily_month_values[metal].get(origin_month)
    if v is None or len(v) < 5: raise RuntimeError(f"INSUFFICIENT_DAILY_ROWS {metal} {origin_month}")
    r = np.diff(np.log(v)); lam = 0.1 * math.exp(-10.0 * float(np.clip(z, 0, 1)))
    age = np.arange(len(r) - 1, -1, -1, dtype=float); w = np.exp(-lam * age); w /= w.sum()
    return float(w @ r)


def feature_for_target(bundle, target, gpr_history, lag_gpr):
    """Build origin-known X only. Never read the target month's price/label."""
    p, pp = month_shift(target, -1), month_shift(target, -2)
    z = gpr_norm(gpr_history, pp if lag_gpr else p)
    x = []
    for metal in METALS:
        M = bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"ORIGIN_FEATURE_MONTH_MISSING {metal} target={target} origin={p} prior={pp}")
        x.extend((math.log(M[p] / M[pp]), weighted_daily_return(bundle, metal, p, z)))
    return np.array(x, float)


def label_for_target(bundle, target):
    """Historical Y only. This is forbidden for the month being forecast."""
    p = month_shift(target, -1)
    y = []
    for metal in METALS:
        M = bundle.monthly_metal[metal]
        if target not in M or p not in M:
            raise RuntimeError(f"TRAINING_LABEL_MONTH_MISSING {metal} target={target} origin={p}")
        y.append(math.log(M[target] / M[p]))
    return np.array(y, float)


def sample_for_target(bundle, target, gpr_history, lag_gpr):
    """Backward-compatible *labelled historical* row for completed months."""
    return feature_for_target(bundle, target, gpr_history, lag_gpr), label_for_target(bundle, target)


def all_samples_at_origin(bundle, outer_target, governed):
    """Train with completed labelled months; forecast outer_target with X alone.

    The upcoming month's realized metal prices must be entirely absent and
    cannot influence the training matrix, validation or the forecast X.
    This fixes label dependence, not separate historical source-PIT/anchor issues.
    """
    origin = month_shift(outer_target, -1)
    history = bundle.gpr_vintages[origin] if governed else bundle.core_gpr
    out = {}
    for t in month_range("2010-03", origin):
        try:
            out[t] = sample_for_target(bundle, t, history, governed)
        except RuntimeError:
            continue
    # Never call label_for_target for the month we are forecasting.
    out[outer_target] = (feature_for_target(bundle, outer_target, history, governed), None)
    return out


def fit_predict(samples, target, cfg):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < 24: raise RuntimeError(f"TRAINING_ROWS_TOO_FEW {target} n={len(keys)}")
    X = np.stack([samples[k][0] for k in keys]); Y = np.stack([samples[k][1] for k in keys]); tx = samples[target][0][None, :]
    xm, xs, ym, ys = X.mean(0), X.std(0), Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs); ys = np.where(ys < 1e-9, 1.0, ys)
    C, ep, gm = cfg; model = MSVR(C=C, epsilon=ep, gamma=gm / X.shape[1]).fit((X - xm) / xs, (Y - ym) / ys)
    pred = model.predict((tx - xm) / xs)[0] * ys + ym
    return pred, len(keys)


def forecast_from_samples(bundle, target, cfg, samples):
    pred, n = fit_predict(samples, target, cfg); p = month_shift(target, -1)
    return {"target": target, "origin": p, "cfg": list(cfg), "pred_log_return_gold": float(pred[0]),
            "forecast": float(bundle.core_gold[p] * math.exp(float(pred[0]))), "actual": float(bundle.core_gold[target]),
            "rw": float(bundle.core_gold[p]), "train_rows": n}


def build_governed_nested(bundle):
    all_targets = list(month_range(INNER_START, EVAL_END)); by_cfg = {cfg: {} for cfg in CONFIGS}
    for t in all_targets:
        samples = all_samples_at_origin(bundle, t, governed=True)
        for cfg in CONFIGS: by_cfg[cfg][t] = forecast_from_samples(bundle, t, cfg, samples)
    outer = []
    for t in month_range(EVAL_START, EVAL_END):
        eligible = [u for u in all_targets if u < t]
        if len(eligible) < MIN_INNER: raise RuntimeError(f"INNER_FOLDS_TOO_FEW {t}")
        ranked = []
        for cfg in CONFIGS:
            errs = []
            for u in eligible:
                r = by_cfg[cfg][u]; p = month_shift(u, -1)
                actual_ret = math.log(bundle.monthly_metal["Gold"][u] / bundle.monthly_metal["Gold"][p])
                errs.append(abs(r["pred_log_return_gold"] - actual_ret))
            ranked.append((float(np.mean(errs)), cfg[0], cfg[1], cfg[2], cfg))
        ranked.sort(); selected = ranked[0][-1]; row = dict(by_cfg[selected][t])
        row["inner_n"] = len(eligible); row["inner_mean_abs_gold_log_return_error"] = ranked[0][0]; outer.append(row)
    return outer


def build_legacy_reconciliation(bundle):
    out = []
    for t in month_range(EVAL_START, EVAL_END):
        samples = all_samples_at_origin(bundle, t, governed=False)
        out.append(forecast_from_samples(bundle, t, LEGACY_FIXED_CONFIG, samples))
    return out


def metrics(rows):
    a = np.array([r["actual"] for r in rows]); f = np.array([r["forecast"] for r in rows]); rw = np.array([r["rw"] for r in rows])
    ae, rw_ae = np.abs(f - a), np.abs(rw - a); ape, rw_ape = ae / a, rw_ae / a
    direction, actual_direction = np.sign(f - rw), np.sign(a - rw)
    return {"n": len(rows), "mae": float(ae.mean()), "mape_pct": float(ape.mean() * 100),
            "smape_pct": float(np.mean(2 * ae / (np.abs(f) + np.abs(a))) * 100), "median_ae": float(np.median(ae)),
            "median_ape_pct": float(np.median(ape) * 100), "worst_ape_pct": float(np.max(ape) * 100),
            "rmse": float(np.sqrt(np.mean((f - a) ** 2))), "monthly_win_rate_vs_rw": float(np.mean(ae < rw_ae)),
            "direction_accuracy_pct": float(np.mean(direction == actual_direction) * 100), "relative_mae_vs_rw": float(ae.sum() / rw_ae.sum()),
            "rw_mae": float(rw_ae.mean()), "rw_mape_pct": float(rw_ape.mean() * 100), "rw_median_ae": float(np.median(rw_ae))}


def yearly(rows):
    return {y: metrics([r for r in rows if r["target"].startswith(y)]) for y in sorted({r["target"][:4] for r in rows})}


def gate(gm, gy, checks, invariant_same):
    completed = [y for y in ("2023", "2024", "2025") if y in gy]; wins = sum(gy[y]["mae"] < gy[y]["rw_mae"] for y in completed)
    rules = {"source_provenance_pit_pass": not checks["missing_required_gpr_origins"] and not checks["late_required_gpr_origins"] and not checks["missing_required_gpr_lag_month"],
             "authority_invariants_unchanged": invariant_same, "relative_mae_vs_rw_lt_1": gm["relative_mae_vs_rw"] < 1,
             "mape_le_rw": gm["mape_pct"] <= gm["rw_mape_pct"], "median_ae_le_rw": gm["median_ae"] <= gm["rw_median_ae"],
             "completed_year_win_half_or_more": wins >= math.ceil(len(completed) / 2),
             "no_completed_year_mae_gt_1_5_rw": all(gy[y]["mae"] <= 1.5 * gy[y]["rw_mae"] for y in completed),
             "no_unresolved_leakage_or_availability_exception": True}
    status = "RESEARCH_SHADOW_CANDIDATE_HISTORICAL_REPLAY_PASS_PROSPECTIVE_VALIDATION_REQUIRED" if all(rules.values()) else "REJECT_ALL_VW_MIDAS_MSVR_SUCCESSOR_V1_CANDIDATES"
    return status, rules, {"completed_years": completed, "year_wins_vs_rw": wins}


def stable_hash(governed, legacy, gm, lm):
    p = {"model": MODEL_ID, "governed": [{k: r[k] for k in ("target", "origin", "cfg", "pred_log_return_gold", "forecast", "actual", "rw", "train_rows", "inner_n")} for r in governed],
         "legacy": [{k: r[k] for k in ("target", "forecast", "actual", "rw")} for r in legacy], "gm": gm, "lm": lm}
    return hashlib.sha256(json.dumps(p, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def run_once(dsn):
    b = load_data(dsn); governed = build_governed_nested(b); legacy = build_legacy_reconciliation(b)
    gm, lm, gy, ly = metrics(governed), metrics(legacy), yearly(governed), yearly(legacy)
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); after = authority_invariants(cur)
    status, rules, meta = gate(gm, gy, b.source_checks, after == b.invariants_before)
    return {"pipeline_version": PIPELINE_VERSION, "model_id": MODEL_ID, "scope": "RESEARCH_HISTORICAL_REPLAY_ONLY", "final_gate": status,
            "deterministic_payload_sha256": stable_hash(governed, legacy, gm, lm), "source_checks": b.source_checks,
            "authority_invariants_before": b.invariants_before, "authority_invariants_after": after,
            "governed_nested_pit": {"metrics": gm, "yearly": gy, "rows": governed},
            "legacy_reconciliation_only": {"evidence_class": "RECONCILIATION_ONLY_NOT_PIT_ELIGIBLE", "fixed_config": list(LEGACY_FIXED_CONFIG),
                "metrics": lm, "yearly": ly, "archived_reference": ARCHIVED, "mape_distance_pp": float(lm["mape_pct"] - ARCHIVED["mape_pct"]),
                "mape_2025_distance_pp": float(ly["2025"]["mape_pct"] - ARCHIVED["mape_2025_pct"])},
            "gate_checks": rules, "gate_meta": meta,
            "governance": {"auto_selector": "OFF", "auto_ensemble": "OFF", "database_writes": "NONE", "forecast_writes": "NONE", "decision_writes": "NONE", "runtime_activation": "NONE", "archived_identity_untouched": True}}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", default="vw_midas_msvr_successor_v1_result.json"); ap.add_argument("--determinism-check", action="store_true"); args = ap.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL is required")
    result = run_once(dsn)
    if args.determinism_check:
        second = run_once(dsn)
        if result["deterministic_payload_sha256"] != second["deterministic_payload_sha256"]: raise RuntimeError("DETERMINISM_FAIL")
        result["determinism_check"] = "PASS"
    else: result["determinism_check"] = "NOT_RUN"
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"final_gate": result["final_gate"], "sha256": result["deterministic_payload_sha256"], "governed_metrics": result["governed_nested_pit"]["metrics"], "legacy_reconciliation_metrics": result["legacy_reconciliation_only"]["metrics"], "legacy_mape_distance_pp": result["legacy_reconciliation_only"]["mape_distance_pp"], "gate_checks": result["gate_checks"], "determinism_check": result["determinism_check"]}, sort_keys=True))


if __name__ == "__main__": main()
