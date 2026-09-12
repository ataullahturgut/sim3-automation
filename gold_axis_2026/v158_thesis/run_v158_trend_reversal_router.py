from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "v158_thesis/contracts/v158_trend_reversal_router_freeze_v1.json"
V157_CONTRACT_PATH = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
PATCH_REF_PATH = ROOT / "patch_repro_v1/locked_replay_v7_daily_feature_pit_43.csv"
OUT = ROOT / "data_pipeline/audits/v158_thesis"


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_V158_RETROSPECTIVE_SCORING":
        raise RuntimeError("V158_CONTRACT_NOT_FROZEN")
    if c["governance"].get("AUTO_SELECTOR") != "OFF" or c["governance"].get("AUTO_ENSEMBLE") != "OFF":
        raise RuntimeError("V158_GOVERNANCE_LOCK_FAIL")
    if c["governance"].get("production_authority") is not False:
        raise RuntimeError("V158_PRODUCTION_AUTHORITY_FORBIDDEN")
    return c


def load_patch_references() -> dict[str, float]:
    # Deliberately read only the two preregistered columns. Actuals and historical
    # error fields in the source artifact are not consumed by the router.
    d = pd.read_csv(PATCH_REF_PATH, usecols=["month", "patch_v7"])
    d["month"] = d["month"].astype(str)
    d["patch_v7"] = pd.to_numeric(d["patch_v7"], errors="raise")
    if d["month"].duplicated().any() or (~np.isfinite(d["patch_v7"])).any() or (d["patch_v7"] <= 0).any():
        raise RuntimeError("V158_MONTHLY_REFERENCE_INVALID")
    return dict(zip(d["month"], d["patch_v7"].astype(float)))


def emergency_research_context(panel: pd.DataFrame, refs: dict[str, float], contract: dict) -> pd.DataFrame:
    cfg = contract["emergency_research_context"]
    level_thr = float(cfg["level_threshold_abs"])
    reversal_thr = float(cfg["reversal_threshold_abs"])
    d = panel.copy().sort_values("date").reset_index(drop=True)
    d["month_key"] = d["date"].dt.strftime("%Y-%m")
    d["monthly_reference_v7"] = d["month_key"].map(refs)
    if d["monthly_reference_v7"].isna().any():
        missing = sorted(d.loc[d["monthly_reference_v7"].isna(), "month_key"].unique().tolist())
        raise RuntimeError(f"V158_MONTHLY_REFERENCE_COVERAGE_FAIL:{missing}")

    levels: list[int] = []
    alerts: list[int] = []
    onsets: list[int] = []
    ages: list[int] = []
    disps: list[float] = []

    current_month: str | None = None
    shock_direction = 0
    running_peak: float | None = None
    running_trough: float | None = None
    previous_alert = 0
    alert_age = 0

    for row in d.itertuples(index=False):
        month = str(row.month_key)
        close = float(row.close)
        ref = float(row.monthly_reference_v7)
        if month != current_month:
            current_month = month
            shock_direction = 0
            running_peak = None
            running_trough = None
            previous_alert = 0
            alert_age = 0

        displacement = close / ref - 1.0
        level = 1 if displacement >= level_thr else (-1 if displacement <= -level_thr else 0)
        if level == 1 and shock_direction != 1:
            shock_direction = 1
            running_peak = close
            running_trough = None
        elif level == -1 and shock_direction != -1:
            shock_direction = -1
            running_trough = close
            running_peak = None

        alert = 0
        if shock_direction == 1:
            running_peak = max(running_peak if running_peak is not None else close, close)
            if close / running_peak - 1.0 <= -reversal_thr:
                alert = -1
        elif shock_direction == -1:
            running_trough = min(running_trough if running_trough is not None else close, close)
            if close / running_trough - 1.0 >= reversal_thr:
                alert = 1

        onset = alert if alert != 0 and alert != previous_alert else 0
        if alert == 0:
            alert_age = 0
        elif alert == previous_alert:
            alert_age += 1
        else:
            alert_age = 1

        disps.append(displacement)
        levels.append(level)
        alerts.append(alert)
        onsets.append(onset)
        ages.append(alert_age)
        previous_alert = alert

    d["emergency_displacement"] = disps
    d["emergency_level"] = levels
    d["emergency_reversal"] = alerts
    d["emergency_alert_onset"] = onsets
    d["emergency_alert_age"] = ages
    return d


def add_router_target(panel: pd.DataFrame, h: int) -> pd.DataFrame:
    d = panel.copy().sort_values("date").reset_index(drop=True)
    d["target_close"] = d["close"].shift(-h)
    d["target_date"] = d["date"].shift(-h)
    d["target_return"] = np.log(d["target_close"] / d["close"])
    d["future_direction"] = np.where(d["target_return"].notna(), np.where(d["target_return"] > 0, 1, -1), np.nan)
    d["trend_sign"] = np.where(d["mom20"] > 0, 1, np.where(d["mom20"] < 0, -1, 0))
    valid = d["target_return"].notna() & d["trend_sign"].ne(0)
    d["reversal_y"] = np.nan
    d.loc[valid, "reversal_y"] = (d.loc[valid, "future_direction"] != d.loc[valid, "trend_sign"]).astype(int)
    d["origin_index"] = np.arange(len(d), dtype=int)

    for role, out in [("fast_role", "trend_fast_agree"), ("slow_role", "trend_slow_agree"), ("monthly_direction_3m", "trend_monthly_agree")]:
        r = pd.to_numeric(d[role], errors="coerce").fillna(0.0)
        d[out] = np.where(r == 0, 0, np.where(r == d["trend_sign"], 1, -1))
    agree_cols = ["trend_fast_agree", "trend_slow_agree", "trend_monthly_agree"]
    d["role_disagreement_count"] = (d[agree_cols] == -1).sum(axis=1).astype(float)
    return d


def mature_training_indices(d: pd.DataFrame, t: int, h: int, contract: dict) -> list[int]:
    cfg = contract["models"]["training"]
    idx = [j for j in range(t) if j + h <= t and pd.notna(d.loc[j, "reversal_y"]) and int(d.loc[j, "trend_sign"]) != 0]
    cap = int(cfg["rolling_cap"])
    if len(idx) < int(cfg["minimum_mature_targets"]):
        return []
    return idx[-cap:]


def make_model(model_id: str, features: list[str], contract: dict):
    if model_id == contract["models"]["primary"]["id"]:
        c = contract["models"]["primary"]
        return HistGradientBoostingClassifier(
            max_depth=int(c["max_depth"]),
            max_iter=int(c["max_iter"]),
            learning_rate=float(c["learning_rate"]),
            l2_regularization=float(c["l2_regularization"]),
            random_state=int(c["random_state"]),
        )
    if model_id == contract["models"]["diagnostic"]["id"]:
        c = contract["models"]["diagnostic"]
        numeric = list(features)
        preprocess = ColumnTransformer([
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric)
        ], remainder="drop")
        return Pipeline([
            ("prep", preprocess),
            ("clf", LogisticRegression(C=float(c["C"]), class_weight=str(c["class_weight"]), max_iter=int(c["max_iter"]), random_state=int(c["random_state"])))
        ])
    raise KeyError(model_id)


def sequential_reversal_probabilities(d: pd.DataFrame, model_id: str, contract: dict) -> pd.DataFrame:
    h = int(contract["target"]["primary_horizon_sessions"])
    features = list(contract["router_features"])
    start = pd.Timestamp(contract["windows"]["formation_score_start"])
    rows: list[dict] = []
    for t in range(len(d) - h):
        if pd.Timestamp(d.loc[t, "date"]) < start or int(d.loc[t, "trend_sign"]) == 0:
            continue
        train = mature_training_indices(d, t, h, contract)
        if not train:
            continue
        ytrain = d.loc[train, "reversal_y"].astype(int)
        if ytrain.nunique() < 2:
            continue
        model = make_model(model_id, features, contract)
        model.fit(d.loc[train, features], ytrain)
        p = float(model.predict_proba(d.loc[[t], features])[0, 1])
        if not math.isfinite(p) or not (0.0 <= p <= 1.0):
            raise RuntimeError("V158_INVALID_REVERSAL_PROBABILITY")
        freq = float(ytrain.mean())
        rows.append({
            "origin_index": int(t),
            "origin_date": d.loc[t, "date"],
            "target_date": d.loc[t, "target_date"],
            "target_return": float(d.loc[t, "target_return"]),
            "future_direction": int(d.loc[t, "future_direction"]),
            "trend_sign": int(d.loc[t, "trend_sign"]),
            "reversal_y": int(d.loc[t, "reversal_y"]),
            "model_id": model_id,
            "p_reversal": p,
            "expanding_frequency_benchmark": freq,
            "train_n": int(len(train)),
            "emergency_level": int(d.loc[t, "emergency_level"]),
            "emergency_reversal": int(d.loc[t, "emergency_reversal"]),
            "emergency_alert_onset": int(d.loc[t, "emergency_alert_onset"]),
            "emergency_alert_age": int(d.loc[t, "emergency_alert_age"]),
            "fast_role": float(d.loc[t, "fast_role"]) if pd.notna(d.loc[t, "fast_role"]) else np.nan,
            "slow_role": float(d.loc[t, "slow_role"]) if pd.notna(d.loc[t, "slow_role"]) else np.nan,
            "monthly_direction_3m": float(d.loc[t, "monthly_direction_3m"]) if pd.notna(d.loc[t, "monthly_direction_3m"]) else np.nan,
        })
    return pd.DataFrame(rows)


def build_rtq_baseline(panel: pd.DataFrame, base_features: list[str]) -> pd.DataFrame:
    c = json.loads(V157_CONTRACT_PATH.read_text(encoding="utf-8"))
    h = 20
    z = v157.add_target(panel, h)
    f = v157.sequential_quantiles(z, base_features, "H20_BASE_RTQ_R126", "ROLLING126", False, h, c)
    if f.empty:
        raise RuntimeError("V158_RTQ_BASELINE_EMPTY")
    f["rtq_signal"] = np.where(f["q25"] > 0, 1, np.where(f["q75"] < 0, -1, 0))
    return f[["origin_index", "origin_date", "target_date", "rtq_signal", "q25", "q50", "q75"]]


def period_name(date: pd.Timestamp, contract: dict) -> str:
    w = contract["windows"]
    if pd.Timestamp(w["formation_score_start"]) <= date <= pd.Timestamp(w["formation_score_end"]):
        return "FORMATION_2024"
    if pd.Timestamp(w["validation_start"]) <= date <= pd.Timestamp(w["validation_end"]):
        return "VALIDATION_2025"
    if pd.Timestamp(w["test_start"]) <= date <= pd.Timestamp(w["test_end"]):
        return "TEST_2026_AVAILABLE"
    return "OUTSIDE"


def apply_router(f: pd.DataFrame, contract: dict) -> pd.DataFrame:
    d = f.copy()
    hi = float(contract["router"]["reversal_probability_high"])
    lo = float(contract["router"]["reversal_probability_low"])
    trend_up = d["trend_sign"].eq(1)
    continuation_dir = np.where(trend_up, 1, -1)
    reversal_dir = -continuation_dir

    d["router_primary_dir"] = 0
    d.loc[d["p_reversal"] >= hi, "router_primary_dir"] = reversal_dir[d["p_reversal"] >= hi]
    d.loc[d["p_reversal"] <= lo, "router_primary_dir"] = continuation_dir[d["p_reversal"] <= lo]

    d["router_confirmed_dir"] = 0
    rev_mask = d["p_reversal"] >= hi
    cont_mask = (d["p_reversal"] <= lo) & d["rtq_signal"].eq(d["trend_sign"])
    d.loc[rev_mask, "router_confirmed_dir"] = reversal_dir[rev_mask]
    d.loc[cont_mask, "router_confirmed_dir"] = continuation_dir[cont_mask]
    return d


def direction_metrics(f: pd.DataFrame, column: str) -> dict:
    sig = f[column].astype(int)
    mask = sig.ne(0)
    g = f.loc[mask]
    if g.empty:
        return {"n": int(len(f)), "selective_n": 0, "coverage": 0.0}
    pred = (g[column].astype(int) > 0).astype(int)
    y = (g["future_direction"].astype(int) > 0).astype(int)
    return {
        "n": int(len(f)),
        "selective_n": int(len(g)),
        "coverage": float(len(g) / len(f)),
        "selective_accuracy": float(accuracy_score(y, pred)),
        "selective_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "up_signals": int((g[column] > 0).sum()),
        "down_signals": int((g[column] < 0).sum()),
        "actual_up_rate_on_signals": float(y.mean()),
    }


def reversal_metrics(f: pd.DataFrame) -> dict:
    y = f["reversal_y"].astype(int).to_numpy()
    p = f["p_reversal"].astype(float).to_numpy()
    b = f["expanding_frequency_benchmark"].astype(float).clip(1e-6, 1 - 1e-6).to_numpy()
    pred = (p >= 0.5).astype(int)
    return {
        "n": int(len(f)),
        "reversal_rate": float(np.mean(y)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.column_stack([1-p, p]), labels=[0, 1])),
        "balanced_accuracy_at_0_5": float(balanced_accuracy_score(y, pred)),
        "mcc_at_0_5": float(matthews_corrcoef(y, pred)),
        "frequency_brier": float(brier_score_loss(y, b)),
        "frequency_log_loss": float(log_loss(y, np.column_stack([1-b, b]), labels=[0, 1])),
    }


def rtq_direction_metrics(f: pd.DataFrame) -> dict:
    return direction_metrics(f.rename(columns={"rtq_signal": "_rtq"}), "_rtq")


def support(primary: dict[str, dict], base: dict[str, dict], rev: dict[str, dict], contract: dict) -> dict:
    rule = contract["evaluation"]["support_rule"]
    checks = {}
    for period in ["VALIDATION_2025", "TEST_2026_AVAILABLE"]:
        m = primary[period]
        r = rev[period]
        bm = base[period]
        checks[f"{period}:coverage"] = m.get("coverage", 0) >= float(rule["coverage_each_2025_2026_min"])
        checks[f"{period}:balanced"] = m.get("selective_balanced_accuracy", 0) > float(rule["balanced_accuracy_each_2025_2026_strictly_above"])
        checks[f"{period}:mcc"] = m.get("mcc", 0) > float(rule["mcc_each_2025_2026_strictly_above"])
        checks[f"{period}:both_directions"] = m.get("up_signals", 0) > 0 and m.get("down_signals", 0) > 0
        nonworse = r["brier"] <= r["frequency_brier"] and r["log_loss"] <= r["frequency_log_loss"]
        strict = r["brier"] < r["frequency_brier"] or r["log_loss"] < r["frequency_log_loss"]
        checks[f"{period}:proper_scores"] = bool(nonworse and strict)
        if period == "VALIDATION_2025":
            checks[f"{period}:beats_rtq_balanced"] = m.get("selective_balanced_accuracy", -1) > bm.get("selective_balanced_accuracy", -1)
        else:
            checks[f"{period}:not_below_rtq_balanced"] = m.get("selective_balanced_accuracy", -1) >= bm.get("selective_balanced_accuracy", 2)
    return {"pass": bool(all(checks.values())), "checks": checks}


def main() -> int:
    contract = load_contract()
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")
    v157_contract = json.loads(V157_CONTRACT_PATH.read_text(encoding="utf-8"))

    with psycopg.connect(url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, base_features, _, _ = v157.build_panel(conn, v157_contract)

    panel = emergency_research_context(panel, load_patch_references(), contract)
    routed = add_router_target(panel, int(contract["target"]["primary_horizon_sessions"]))
    rtq = build_rtq_baseline(panel, base_features)

    model_ids = [contract["models"]["primary"]["id"], contract["models"]["diagnostic"]["id"]]
    all_predictions = []
    results: dict = {
        "contract_id": contract["contract_id"],
        "status": "RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "production_authority": False,
        "models": {},
    }

    for model_id in model_ids:
        f = sequential_reversal_probabilities(routed, model_id, contract)
        f = f.merge(rtq, on=["origin_index", "origin_date", "target_date"], how="left", validate="one_to_one")
        if f["rtq_signal"].isna().any():
            raise RuntimeError("V158_RTQ_ALIGNMENT_FAIL")
        f = apply_router(f, contract)
        f["period"] = f["origin_date"].map(lambda x: period_name(pd.Timestamp(x), contract))
        f = f[f["period"].ne("OUTSIDE")].copy()
        all_predictions.append(f)

        model_result = {"periods": {}}
        primary_m, confirmed_m, rtq_m, rev_m = {}, {}, {}, {}
        for period in ["FORMATION_2024", "VALIDATION_2025", "TEST_2026_AVAILABLE"]:
            g = f[f["period"].eq(period)].copy()
            if g.empty:
                model_result["periods"][period] = {"status": "BLOCKED_EMPTY"}
                continue
            pm = direction_metrics(g, "router_primary_dir")
            cm = direction_metrics(g, "router_confirmed_dir")
            bm = rtq_direction_metrics(g)
            rm = reversal_metrics(g)
            primary_m[period], confirmed_m[period], rtq_m[period], rev_m[period] = pm, cm, bm, rm
            model_result["periods"][period] = {
                "router_primary": pm,
                "router_confirmed": cm,
                "rtq_baseline": bm,
                "reversal_probability": rm,
            }
        if all(p in primary_m for p in ["VALIDATION_2025", "TEST_2026_AVAILABLE"]):
            model_result["support_gate_primary_router"] = support(primary_m, rtq_m, rev_m, contract)
        results["models"][model_id] = model_result

    results["interpretation_lock"] = {
        "h20_is_primary": True,
        "emergency_is_context_not_vote": True,
        "realized_semivariance_is_used_for_reversal_router_not_generic_return_regression": True,
        "2025_2026_are_researcher_visible": True,
        "future_prospective_shadow_required": True,
        "post_score_changes_forbidden": True,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v158_trend_reversal_router_panel.csv", index=False)
    pd.concat(all_predictions, ignore_index=True).to_csv(OUT / "v158_trend_reversal_router_predictions.csv", index=False)
    (OUT / "v158_trend_reversal_router_results.json").write_text(json.dumps(results, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(results, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
