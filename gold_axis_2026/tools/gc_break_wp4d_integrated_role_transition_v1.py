from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "gc_break_v0" / "gc_break_wp4d_integrated_role_transition_prereg_v1.json"


def as_bool(s: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False).astype(bool)
    return s.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def finite_float(x: object) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def load_contract() -> dict:
    c = json.loads(PREREG.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_WP4D_FORMATION_SCORING":
        raise RuntimeError("WP4D_PREREG_NOT_FROZEN")
    g = c.get("governance", {})
    required_true = [
        "no_equal_weight_voting", "no_random_split", "no_hindsight_threshold_tuning",
        "no_2025_challenge_access_during_formation", "no_2026_stress_access_during_selection",
        "no_database_writes", "no_position_mapping", "no_production_promotion",
        "same_origin_optional_comparison",
    ]
    if not all(g.get(k) is True for k in required_true):
        raise RuntimeError("WP4D_GOVERNANCE_GUARD_FAIL")
    if g.get("auto_selector") != "OFF" or g.get("auto_ensemble") != "OFF":
        raise RuntimeError("WP4D_AUTO_GUARD_FAIL")
    return c


def validate_inputs(panel: pd.DataFrame, events: pd.DataFrame) -> None:
    need = {
        "date", "regime_pre", "regime_post", "wp2_break_flag", "path_half",
        "fast_conflict", "fast_opposite", "fast_state", "slow_state",
        "monthly_direction_3m", "bocpd_state", "macro_strong_event_count",
        "macro_adverse_event_count", "emergency_level", "emergency_reversal",
        "emergency_status", "h1_random_walk", "h1_momentum_3m", "h1_vw_midas",
        "h1_causal_patch", "h1_context_status",
    }
    missing = sorted(need - set(panel.columns))
    if missing:
        raise RuntimeError(f"WP4D_PANEL_COLUMNS_MISSING:{missing}")
    if panel["date"].duplicated().any():
        raise RuntimeError("WP4D_DUPLICATE_PANEL_DATE")
    if panel["date"].min() < pd.Timestamp("2022-01-01") or panel["date"].max() > pd.Timestamp("2024-12-31"):
        raise RuntimeError("WP4D_FORMATION_BOUNDARY_FAIL")
    if len(panel) != 351:
        raise RuntimeError(f"WP4D_FORMATION_ORIGIN_COUNT_FAIL:{len(panel)}")
    if len(events) != 21:
        raise RuntimeError(f"WP4D_PRIMARY_EVENT_COUNT_FAIL:{len(events)}")


def add_role_features(p: pd.DataFrame) -> pd.DataFrame:
    p = p.sort_values("date").reset_index(drop=True).copy()
    p["wp2_break_flag"] = as_bool(p["wp2_break_flag"])
    p["path_half"] = as_bool(p["path_half"])
    p["fast_conflict"] = as_bool(p["fast_conflict"])
    p["fast_opposite"] = as_bool(p["fast_opposite"])
    p["wp4d_episode_opener"] = p["path_half"] | p["fast_conflict"]

    # Regime sojourn is causal: number of governed origins since the previous observed primary break.
    ages: list[int] = []
    age = 0
    prev_break = False
    for cur_break in p["wp2_break_flag"].tolist():
        age = 1 if prev_break or age == 0 else age + 1
        ages.append(age)
        prev_break = bool(cur_break)
    p["regime_sojourn_age"] = ages
    p["log1p_regime_sojourn_age"] = np.log1p(p["regime_sojourn_age"].astype(float))

    valid_regime = p["regime_pre"].isin(["UP", "DOWN"])
    p["monthly_direction_conflict_wp4d"] = np.where(
        valid_regime,
        ((p["regime_pre"] == "UP") & (p["monthly_direction_3m"] == "DOWN"))
        | ((p["regime_pre"] == "DOWN") & (p["monthly_direction_3m"] == "UP")),
        np.nan,
    )
    if "monthly_direction_missing_reason" in p.columns:
        p.loc[p["monthly_direction_missing_reason"].notna(), "monthly_direction_conflict_wp4d"] = np.nan

    # BOCPD has a frozen downside-only interpretation. It is never converted into a symmetric direction vote.
    p["bocpd_downside_adverse_context_wp4d"] = np.where(
        p["bocpd_state"].notna(),
        ((p["regime_pre"] == "UP") & (p["bocpd_state"] == "ADVERSE_BREAK_CANDIDATE")).astype(float),
        np.nan,
    )

    strong = pd.to_numeric(p["macro_strong_event_count"], errors="coerce")
    adverse = pd.to_numeric(p["macro_adverse_event_count"], errors="coerce")
    supportive = strong - adverse
    p["macro_break_pressure_wp4d"] = np.where(
        p["regime_pre"] == "UP", (adverse > 0).astype(float),
        np.where(p["regime_pre"] == "DOWN", (supportive > 0).astype(float), np.nan),
    )

    p["emergency_level_opposite_wp4d"] = np.where(
        p["emergency_status"].eq("AVAILABLE_FROZEN_REFERENCE"),
        (((p["regime_pre"] == "UP") & (p["emergency_level"] == "DOWN"))
         | ((p["regime_pre"] == "DOWN") & (p["emergency_level"] == "UP"))).astype(float),
        np.nan,
    )
    p["emergency_reversal_opposite_wp4d"] = np.where(
        p["emergency_status"].eq("AVAILABLE_FROZEN_REFERENCE"),
        (((p["regime_pre"] == "UP") & (p["emergency_reversal"] == "DOWN_ALERT"))
         | ((p["regime_pre"] == "DOWN") & (p["emergency_reversal"] == "UP_ALERT"))).astype(float),
        np.nan,
    )

    hcols = ["h1_random_walk", "h1_momentum_3m", "h1_vw_midas", "h1_causal_patch"]
    h = p[hcols].apply(pd.to_numeric, errors="coerce")
    h1_ok = p["h1_context_status"].eq("AVAILABLE_FOUR_FROZEN_REPLAY_EXPERTS") & h.notna().all(axis=1)
    up_votes = (h[["h1_momentum_3m", "h1_vw_midas", "h1_causal_patch"]].gt(h["h1_random_walk"], axis=0)).sum(axis=1)
    down_votes = (h[["h1_momentum_3m", "h1_vw_midas", "h1_causal_patch"]].lt(h["h1_random_walk"], axis=0)).sum(axis=1)
    consensus = pd.Series("MIXED", index=p.index, dtype="object")
    consensus.loc[up_votes >= 2] = "UP"
    consensus.loc[down_votes >= 2] = "DOWN"
    p["h1_consensus_direction_wp4d"] = np.where(h1_ok, consensus, None)
    p["h1_consensus_conflict_wp4d"] = np.where(
        h1_ok,
        (((p["regime_pre"] == "UP") & (consensus == "DOWN"))
         | ((p["regime_pre"] == "DOWN") & (consensus == "UP"))).astype(float),
        np.nan,
    )
    mean_h = h.mean(axis=1)
    p["h1_dispersion_ratio_wp4d"] = np.where(h1_ok, h.std(axis=1, ddof=0) / mean_h, np.nan)
    return p


def episode_snapshot(p: pd.DataFrame, start_i: int, terminal_i: int, outcome: int, episode_id: int) -> dict:
    r = p.iloc[start_i]
    return {
        "episode_id": episode_id,
        "start_i": int(start_i),
        "terminal_i": int(terminal_i),
        "start_date": pd.Timestamp(r["date"]),
        "terminal_date": pd.Timestamp(p.iloc[terminal_i]["date"]),
        "outcome_break": int(outcome),
        "terminal_type": "BREAK" if outcome else "RECOVERY",
        "lead_observations_if_break": int(terminal_i - start_i) if outcome else np.nan,
        "lead_calendar_days_if_break": int((pd.Timestamp(p.iloc[terminal_i]["date"]) - pd.Timestamp(r["date"])).days) if outcome else np.nan,
        "regime_pre": r["regime_pre"],
        "log1p_regime_sojourn_age": finite_float(r["log1p_regime_sojourn_age"]),
        "fast_opposite_at_episode_start": float(bool(r["fast_opposite"])),
        "monthly_direction_conflict_at_episode_start": finite_float(r["monthly_direction_conflict_wp4d"]),
        "bocpd_downside_adverse_context_at_episode_start": finite_float(r["bocpd_downside_adverse_context_wp4d"]),
        "macro_break_pressure_at_episode_start": finite_float(r["macro_break_pressure_wp4d"]),
        "h1_consensus_conflict_at_episode_start": finite_float(r["h1_consensus_conflict_wp4d"]),
        "h1_dispersion_ratio_at_episode_start": finite_float(r["h1_dispersion_ratio_wp4d"]),
        "emergency_level_opposite_at_episode_start": finite_float(r["emergency_level_opposite_wp4d"]),
        "emergency_reversal_opposite_at_episode_start": finite_float(r["emergency_reversal_opposite_wp4d"]),
        "h1_context_status_at_episode_start": r["h1_context_status"],
        "emergency_status_at_episode_start": r["emergency_status"],
    }


def build_predictive_episodes(p: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []
    active_start: int | None = None
    same_origin_break_openers = 0
    censored = 0
    eid = 0

    for i, r in p.iterrows():
        opener = bool(r["wp4d_episode_opener"])
        is_break = bool(r["wp2_break_flag"])

        if active_start is None:
            if opener and is_break:
                same_origin_break_openers += 1
                continue
            if opener:
                active_start = i
            continue

        if is_break:
            eid += 1
            rows.append(episode_snapshot(p, active_start, i, 1, eid))
            active_start = None
            continue

        if not opener:
            eid += 1
            rows.append(episode_snapshot(p, active_start, i, 0, eid))
            active_start = None

    if active_start is not None:
        censored = 1

    episodes = pd.DataFrame(rows)
    audit = {
        "terminal_predictive_episodes": int(len(episodes)),
        "break_conversions": int(episodes["outcome_break"].sum()) if len(episodes) else 0,
        "recoveries": int((1 - episodes["outcome_break"]).sum()) if len(episodes) else 0,
        "same_origin_break_openers_excluded": int(same_origin_break_openers),
        "right_censored_open_episode": int(censored),
    }
    return episodes, audit


def core_eligibility(e: pd.DataFrame) -> pd.Series:
    cols = [
        "log1p_regime_sojourn_age",
        "fast_opposite_at_episode_start",
        "monthly_direction_conflict_at_episode_start",
        "bocpd_downside_adverse_context_at_episode_start",
        "macro_break_pressure_at_episode_start",
    ]
    return e[cols].notna().all(axis=1)


def make_estimator(c_value: float = 0.25) -> Pipeline:
    return Pipeline([
        ("scale", StandardScaler()),
        ("logit", LogisticRegression(
            penalty="l2", C=c_value, solver="liblinear", class_weight=None,
            fit_intercept=True, max_iter=1000, random_state=0,
        )),
    ])


def prequential_predict(
    episodes: pd.DataFrame,
    features: list[str],
    eligible: pd.Series,
    contract: dict,
    label: str,
) -> pd.DataFrame:
    proto = contract["prequential_protocol"]
    min_n = int(proto["minimum_past_completed_episodes"])
    min_pos = int(proto["minimum_past_break_conversions"])
    min_neg = int(proto["minimum_past_recoveries"])
    c_value = 0.25
    out = []
    eligible = eligible.astype(bool)

    for idx, row in episodes.iterrows():
        if not bool(eligible.loc[idx]):
            continue
        prior_mask = eligible & (episodes["terminal_i"] < int(row["start_i"]))
        train = episodes.loc[prior_mask].copy()
        y = train["outcome_break"].astype(int)
        n_pos = int(y.sum())
        n_neg = int(len(y) - n_pos)
        if len(train) < min_n or n_pos < min_pos or n_neg < min_neg:
            continue
        prior_prob = float((n_pos + 0.5) / (len(train) + 1.0))
        rec = {
            "episode_id": int(row["episode_id"]),
            "start_date": row["start_date"],
            "outcome_break": int(row["outcome_break"]),
            "train_episodes": int(len(train)),
            "train_breaks": n_pos,
            "train_recoveries": n_neg,
            "model_id": label,
            "p_empirical_prior": prior_prob,
        }
        if features:
            X = train[features].astype(float)
            x = pd.DataFrame([row[features].astype(float).to_dict()], columns=features)
            model = make_estimator(c_value)
            model.fit(X, y)
            prob = float(model.predict_proba(x)[0, 1])
            rec["probability"] = float(np.clip(prob, 1e-6, 1 - 1e-6))
        else:
            rec["probability"] = float(np.clip(prior_prob, 1e-6, 1 - 1e-6))
        out.append(rec)
    return pd.DataFrame(out)


def score_predictions(df: pd.DataFrame, probability_col: str = "probability") -> dict:
    if df.empty:
        return {"n": 0, "breaks": 0, "recoveries": 0, "brier_score": None, "log_loss": None,
                "average_precision_descriptive": None, "roc_auc_descriptive": None}
    y = df["outcome_break"].astype(int).to_numpy()
    p = np.clip(df[probability_col].astype(float).to_numpy(), 1e-6, 1 - 1e-6)
    both = len(set(y.tolist())) == 2
    return {
        "n": int(len(df)),
        "breaks": int(y.sum()),
        "recoveries": int(len(y) - y.sum()),
        "brier_score": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "average_precision_descriptive": float(average_precision_score(y, p)) if both else None,
        "roc_auc_descriptive": float(roc_auc_score(y, p)) if both else None,
    }


def aligned_metrics(preds: dict[str, pd.DataFrame], ids: Iterable[str]) -> tuple[dict, pd.DataFrame]:
    ids = list(ids)
    common: set[int] | None = None
    for mid in ids:
        s = set(preds[mid]["episode_id"].astype(int).tolist()) if not preds[mid].empty else set()
        common = s if common is None else common & s
    common = common or set()
    merged = pd.DataFrame({"episode_id": sorted(common)})
    metrics = {}
    for mid in ids:
        d = preds[mid][preds[mid]["episode_id"].isin(common)].copy().sort_values("episode_id")
        metrics[mid] = score_predictions(d)
        if not d.empty:
            x = d[["episode_id", "outcome_break", "probability", "train_episodes", "train_breaks", "train_recoveries"]].copy()
            x = x.rename(columns={"probability": f"p_{mid}", "train_episodes": f"train_n_{mid}",
                                  "train_breaks": f"train_breaks_{mid}", "train_recoveries": f"train_recoveries_{mid}"})
            if "outcome_break" in merged.columns:
                x = x.drop(columns=["outcome_break"])
            merged = merged.merge(x, on="episode_id", how="left")
    return metrics, merged


def extension_test(episodes: pd.DataFrame, base_features: list[str], extra_features: list[str], eligible: pd.Series, contract: dict, label: str) -> dict:
    p_base = prequential_predict(episodes, base_features, eligible, contract, f"{label}_CORE_COMMON_SUPPORT")
    p_ext = prequential_predict(episodes, base_features + extra_features, eligible, contract, f"{label}_EXTENSION")
    if p_base.empty or p_ext.empty:
        return {"id": label, "status": "NOT_TESTABLE_INSUFFICIENT_PREQUENTIAL_SUPPORT", "common_metrics": None}
    common = sorted(set(p_base["episode_id"]).intersection(set(p_ext["episode_id"])))
    b = p_base[p_base["episode_id"].isin(common)].sort_values("episode_id")
    x = p_ext[p_ext["episode_id"].isin(common)].sort_values("episode_id")
    bm = score_predictions(b)
    xm = score_predictions(x)
    min_eval = contract["formation_support_gate"]
    enough = (xm["n"] >= int(min_eval["minimum_common_prequential_scored_episodes"])
              and xm["breaks"] >= int(min_eval["minimum_common_scored_break_conversions"])
              and xm["recoveries"] >= int(min_eval["minimum_common_scored_recoveries"]))
    if not enough:
        status = "NOT_TESTABLE_INSUFFICIENT_COMMON_SUPPORT"
        supported = False
    else:
        tol = 1e-12
        no_worse = (xm["brier_score"] <= bm["brier_score"] + tol and xm["log_loss"] <= bm["log_loss"] + tol)
        strict = (xm["brier_score"] < bm["brier_score"] - tol or xm["log_loss"] < bm["log_loss"] - tol)
        supported = bool(no_worse and strict)
        status = "SUPPORTED_MODIFIER" if supported else "NOT_SUPPORTED_AS_INCREMENTAL_MODIFIER"
    return {
        "id": label,
        "status": status,
        "supported": supported,
        "common_episode_ids": common,
        "core_same_support": bm,
        "extension_same_support": xm,
    }


def slow_confirmation_summary(p: pd.DataFrame) -> dict:
    break_idx = p.index[p["wp2_break_flag"]].tolist()
    confirmed = []
    delays = []
    cal = []
    for k, i in enumerate(break_idx):
        new_regime = p.loc[i, "regime_post"]
        target = "ROBUST_UP" if new_regime == "UP" else "ROBUST_DOWN"
        stop = break_idx[k + 1] if k + 1 < len(break_idx) else len(p)
        found = None
        for j in range(i, stop):
            if p.loc[j, "slow_state"] == target:
                found = j
                break
        if found is not None:
            confirmed.append(i)
            delays.append(found - i)
            cal.append((pd.Timestamp(p.loc[found, "date"]) - pd.Timestamp(p.loc[i, "date"])).days)
    return {
        "events": int(len(break_idx)),
        "confirmed_before_next_break": int(len(confirmed)),
        "confirmation_rate_before_next_break": float(len(confirmed) / len(break_idx)) if break_idx else None,
        "median_delay_observations": float(np.median(delays)) if delays else None,
        "median_delay_calendar_days": float(np.median(cal)) if cal else None,
        "role": "POST_BREAK_CONFIRMATION_NEW_REGIME_ONLY",
    }


def role_ledger(contract: dict, p: pd.DataFrame, episodes: pd.DataFrame) -> list[dict]:
    entries = []
    roles = contract["governed_identity_role_ledger"]
    h1_episode_support = int(episodes["h1_consensus_conflict_at_episode_start"].notna().sum()) if len(episodes) else 0
    em_episode_support = int(episodes["emergency_level_opposite_at_episode_start"].notna().sum()) if len(episodes) else 0
    for engine, role in roles.items():
        if engine in {"CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK"}:
            status = "SAME_ORIGIN_H1_EXTENSION" if h1_episode_support else "NOT_TESTABLE"
            support = h1_episode_support
        elif engine == "GVZ_RISK":
            status = "NOT_TESTABLE_FORMATION_PIT_NOT_PROVEN"
            support = 0
        elif engine in {"EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"}:
            status = "SAME_ORIGIN_EMERGENCY_EXTENSION"
            support = em_episode_support
        elif engine == "SLOW":
            status = "CONFIRMATION_LANE"
            support = int(len(p))
        elif engine == "FAST":
            status = "TACTICAL_OPENER_AND_CORE_FEATURE"
            support = int(len(episodes))
        elif engine == "MONTHLY_DIRECTION_3M":
            status = "CORE_STRATEGIC_CONTEXT"
            support = int(episodes["monthly_direction_conflict_at_episode_start"].notna().sum()) if len(episodes) else 0
        elif engine == "BOCPD_RETURN_SUCCESSOR_V1":
            status = "CORE_REGIME_CONTEXT_NATIVE_MONTHLY"
            support = int(episodes["bocpd_downside_adverse_context_at_episode_start"].notna().sum()) if len(episodes) else 0
        elif engine == "MACRO_EVENT_SUCCESSOR_V2":
            status = "CORE_EVENT_CLOCK_MODIFIER_FROM_FROZEN_MAPPED_MACRO_CONTEXT"
            support = int(episodes["macro_break_pressure_at_episode_start"].notna().sum()) if len(episodes) else 0
        else:
            status = "UNRESOLVED"
            support = 0
        entries.append({"engine": engine, "role": role, "formation_handling": status, "terminal_episode_support": support})
    return entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, required=True)
    ap.add_argument("--events", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)

    contract = load_contract()
    p = pd.read_csv(a.panel)
    p["date"] = pd.to_datetime(p["date"]).dt.normalize()
    events = pd.read_csv(a.events)
    event_date_col = "trade_date" if "trade_date" in events.columns else "break_date"
    events[event_date_col] = pd.to_datetime(events[event_date_col]).dt.normalize()
    validate_inputs(p, events)
    p = add_role_features(p)

    episodes, episode_audit = build_predictive_episodes(p)
    if episodes.empty:
        raise RuntimeError("WP4D_NO_TERMINAL_PREDICTIVE_EPISODES")
    core_ok = core_eligibility(episodes)
    episodes["core_eligible"] = core_ok
    episodes["h1_extension_eligible"] = core_ok & episodes["h1_consensus_conflict_at_episode_start"].notna()
    episodes["emergency_extension_eligible"] = core_ok & episodes[[
        "emergency_level_opposite_at_episode_start", "emergency_reversal_opposite_at_episode_start"
    ]].notna().all(axis=1)

    base_features = ["log1p_regime_sojourn_age", "fast_opposite_at_episode_start"]
    core_features = base_features + [
        "monthly_direction_conflict_at_episode_start",
        "bocpd_downside_adverse_context_at_episode_start",
        "macro_break_pressure_at_episode_start",
    ]

    pred = {
        "M0_EPISODE_EMPIRICAL_PRIOR": prequential_predict(episodes, [], core_ok, contract, "M0_EPISODE_EMPIRICAL_PRIOR"),
        "M1_TACTICAL_DURATION_RIDGE": prequential_predict(episodes, base_features, core_ok, contract, "M1_TACTICAL_DURATION_RIDGE"),
        "M2_INTEGRATED_ROLE_CORE_RIDGE": prequential_predict(episodes, core_features, core_ok, contract, "M2_INTEGRATED_ROLE_CORE_RIDGE"),
    }
    metrics, common_predictions = aligned_metrics(pred, [
        "M0_EPISODE_EMPIRICAL_PRIOR", "M1_TACTICAL_DURATION_RIDGE", "M2_INTEGRATED_ROLE_CORE_RIDGE"
    ])

    h1_ext = extension_test(
        episodes, core_features, ["h1_consensus_conflict_at_episode_start"], episodes["h1_extension_eligible"], contract,
        "E1_MONTHLY_H1_STRATEGIC_CONTEXT",
    )
    emergency_ext = extension_test(
        episodes, core_features,
        ["emergency_level_opposite_at_episode_start", "emergency_reversal_opposite_at_episode_start"],
        episodes["emergency_extension_eligible"], contract, "E2_EMERGENCY_CONTEXT",
    )
    gvz_ext = {
        "id": "E3_GVZ_RISK",
        "status": "NOT_TESTABLE_FORMATION_PIT_NOT_PROVEN",
        "supported": False,
        "reason": "Canonical 2022-2024 GVZ PIT history is not proven; preregistration forbids imputation or core-window shortening.",
    }

    gate = contract["formation_support_gate"]
    eligible_eps = episodes.loc[core_ok]
    total_n = int(len(eligible_eps))
    total_pos = int(eligible_eps["outcome_break"].sum())
    total_neg = int(total_n - total_pos)
    m2 = metrics.get("M2_INTEGRATED_ROLE_CORE_RIDGE", {})
    common_support_ok = (
        int(m2.get("n") or 0) >= int(gate["minimum_common_prequential_scored_episodes"])
        and int(m2.get("breaks") or 0) >= int(gate["minimum_common_scored_break_conversions"])
        and int(m2.get("recoveries") or 0) >= int(gate["minimum_common_scored_recoveries"])
    )
    total_support_ok = (
        total_n >= int(gate["minimum_terminal_predictive_episodes"])
        and total_pos >= int(gate["minimum_break_conversions"])
        and total_neg >= int(gate["minimum_recoveries"])
    )
    support_ok = bool(total_support_ok and common_support_ok)

    if not support_ok:
        status = contract["formation_decision_rule"]["insufficient_status"]
        gate_detail = {"support_gate_pass": False, "vs_null_pass": None, "vs_minimal_pass": None}
    else:
        m0 = metrics["M0_EPISODE_EMPIRICAL_PRIOR"]
        m1 = metrics["M1_TACTICAL_DURATION_RIDGE"]
        tol = 1e-12
        vs_null = (m2["brier_score"] < m0["brier_score"] - tol and m2["log_loss"] < m0["log_loss"] - tol)
        vs_minimal_no_worse = (m2["brier_score"] <= m1["brier_score"] + tol and m2["log_loss"] <= m1["log_loss"] + tol)
        vs_minimal_strict = (m2["brier_score"] < m1["brier_score"] - tol or m2["log_loss"] < m1["log_loss"] - tol)
        vs_minimal = bool(vs_minimal_no_worse and vs_minimal_strict)
        passed = bool(vs_null and vs_minimal)
        status = contract["formation_decision_rule"]["pass_status"] if passed else contract["formation_decision_rule"]["fail_status"]
        gate_detail = {"support_gate_pass": True, "vs_null_pass": bool(vs_null), "vs_minimal_pass": bool(vs_minimal)}

    slow = slow_confirmation_summary(p)
    ledger = role_ledger(contract, p, episodes)
    all_12 = len(ledger) == 12 and {x["engine"] for x in ledger} == set(contract["governed_identity_role_ledger"])

    for d in pred.values():
        if not d.empty:
            d.to_csv(a.output_dir / f"gc_break_wp4d_{d.iloc[0]['model_id'].lower()}_predictions_v1.csv", index=False)
    episodes.to_csv(a.output_dir / "gc_break_wp4d_formation_episodes_v1.csv", index=False)
    common_predictions.to_csv(a.output_dir / "gc_break_wp4d_common_prequential_predictions_v1.csv", index=False)
    (a.output_dir / "gc_break_wp4d_engine_role_ledger_v1.json").write_text(json.dumps(ledger, indent=2, default=str) + "\n")

    metrics_payload = {
        "primary_common_support_metrics": metrics,
        "extensions": [h1_ext, emergency_ext, gvz_ext],
        "slow_confirmation_lane": slow,
    }
    (a.output_dir / "gc_break_wp4d_formation_metrics_v1.json").write_text(
        json.dumps(metrics_payload, indent=2, sort_keys=True, default=str) + "\n"
    )

    summary = {
        "audit_id": "GC_BREAK_WP4D_INTEGRATED_ROLE_TRANSITION_FORMATION_V1",
        "contract_id": contract["contract_id"],
        "contract_status": contract["status"],
        "status": status,
        "formation_window": contract["formation_window"],
        "formation_origins": int(len(p)),
        "primary_break_events": int(p["wp2_break_flag"].sum()),
        "episode_audit": episode_audit,
        "core_eligible_terminal_episodes": total_n,
        "core_eligible_break_conversions": total_pos,
        "core_eligible_recoveries": total_neg,
        "gate": gate_detail,
        "primary_common_support_metrics": metrics,
        "extensions": [h1_ext, emergency_ext, gvz_ext],
        "slow_confirmation_lane": slow,
        "all_12_governed_identities_accounted_for": bool(all_12),
        "structural_health_used_as_independent_predictor": False,
        "path_half_or_adverse_fraction_in_probability_features": False,
        "random_split": False,
        "hyperparameter_search": False,
        "threshold_search": False,
        "post_score_tuning": False,
        "challenge_2025_accessed": False,
        "stress_2026_accessed": False,
        "production_database_write": "NONE",
        "production_authority": False,
        "next_action": (
            "FREEZE_WP4D_CHALLENGE_PARAMETERS_AND_RUN_2025_ONCE" if status == "FORMATION_SUPPORT_CHALLENGE_REQUIRED"
            else "STOP_WP4D_WITHOUT_2025_CHALLENGE"
        ),
    }
    (a.output_dir / "gc_break_wp4d_formation_summary_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
