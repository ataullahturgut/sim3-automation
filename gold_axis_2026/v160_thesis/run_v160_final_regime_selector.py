from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import psycopg
from sklearn.metrics import balanced_accuracy_score

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157
from gold_axis_2026.v158_thesis import run_v158_trend_reversal_router as v158
from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as v159
from gold_axis_2026.v159_thesis import run_v159r1_entry as v159r1

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "v160_thesis/contracts/v160_final_regime_selector_freeze_v1.json"
V157_CONTRACT_PATH = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v160_thesis"


def load_contract() -> dict[str, Any]:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_V160_RETROSPECTIVE_SCORING":
        raise RuntimeError("V160_CONTRACT_NOT_FROZEN")
    if c.get("stopping_rule") != "FINAL_NORMAL_DAY_RETROSPECTIVE_ARCHITECTURE_EXPERIMENT_V151_V160_SEQUENCE":
        raise RuntimeError("V160_STOPPING_RULE_MISSING")
    g = c["governance"]
    if g.get("AUTO_SELECTOR") != "OFF" or g.get("AUTO_ENSEMBLE") != "OFF":
        raise RuntimeError("V160_GOVERNANCE_LOCK_FAIL")
    if g.get("production_authority") is not False or g.get("production_writes") != "NONE":
        raise RuntimeError("V160_PRODUCTION_AUTHORITY_FORBIDDEN")
    if set(c["experts"]) != {"LEGACY_RTQ_R126", "DRIVER_RTQ_R126"}:
        raise RuntimeError("V160_EXPERT_SET_CHANGED")
    return c


def build_frozen_parents(contract: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    parent_contract = v159r1.merged_contract()
    h = int(contract["target"]["primary_horizon_sessions"])
    if h != int(parent_contract["target"]["primary_horizon_sessions"]):
        raise RuntimeError("V160_HORIZON_PARENT_MISMATCH")

    driver_frames: dict[str, pd.DataFrame] = {}
    driver_evidence: dict[str, Any] = {}
    for sid in ["DTWEXBGS", "DFII10"]:
        d, e = v159r1.fedboard_fetch(sid, "2022-01-01", contract["windows"]["test_end"])
        driver_frames[sid] = d
        driver_evidence[sid] = e

    v157_contract = json.loads(V157_CONTRACT_PATH.read_text(encoding="utf-8"))
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, base_features, _, _ = v157.build_panel(conn, v157_contract)

    panel = v159.add_corrected_drivers(panel, driver_frames, parent_contract)
    panel = v158.emergency_research_context(panel, v158.load_patch_references(), v158.load_contract())
    routed = v158.add_router_target(panel, h)

    legacy_raw = v159.legacy_rtq_parent(panel, base_features)
    corrected_features = v159.corrected_parent_features(base_features, parent_contract)
    driver_raw = v159.corrected_rtq_parent(panel, corrected_features, parent_contract)

    legacy = v159.prepare_parent_frame(legacy_raw, routed, parent_contract)
    driver = v159.prepare_parent_frame(driver_raw, routed, parent_contract)
    legacy["expert_id"] = "LEGACY_RTQ_R126"
    driver["expert_id"] = "DRIVER_RTQ_R126"
    return legacy, driver, driver_evidence


def _sign(v: Any) -> int:
    try:
        x = float(v)
    except Exception:
        return 0
    if not math.isfinite(x) or x == 0:
        return 0
    return 1 if x > 0 else -1


def role_consensus(row: pd.Series) -> str:
    signs = [_sign(row.get(c)) for c in ["fast_role", "slow_role", "monthly_direction_3m"]]
    nz = [x for x in signs if x != 0]
    if nz.count(1) >= 2 or nz.count(-1) >= 2:
        return "CONSENSUS"
    return "MIXED"


def add_causal_regime(frame: pd.DataFrame, contract: dict[str, Any]) -> pd.DataFrame:
    cfg = contract["regime"]
    lookback = int(cfg["lookback_for_state_thresholds"])
    min_hist = int(cfg["minimum_state_history"])
    d = frame.sort_values("origin_index").reset_index(drop=True).copy()

    keys: list[str] = []
    vol_refs: list[float | None] = []
    break_refs: list[float | None] = []
    for i, row in d.iterrows():
        hist = d.iloc[max(0, i - lookback):i]
        hv = pd.to_numeric(hist.get("vol20"), errors="coerce").dropna()
        hb = pd.to_numeric(hist.get("bocpd_reset_fraction"), errors="coerce").dropna()
        if len(hist) < min_hist or len(hv) < min_hist // 2 or len(hb) < min_hist // 2:
            keys.append("UNKNOWN")
            vol_refs.append(None)
            break_refs.append(None)
            continue
        vol_ref = float(hv.median())
        break_ref = float(hb.quantile(0.75))
        vol_state = "HIGH" if float(row["vol20"]) > vol_ref else "LOW"
        emergency = int(row.get("emergency_alert_onset", 0) or 0) == 1 or _sign(row.get("emergency_reversal", 0)) != 0
        bocpd = float(row.get("bocpd_reset_fraction", 0.0) or 0.0)
        structural = "RISK" if emergency or bocpd > break_ref else "CALM"
        roles = role_consensus(row)
        keys.append(f"VOL_{vol_state}|STRUCT_{structural}|ROLE_{roles}")
        vol_refs.append(vol_ref)
        break_refs.append(break_ref)

    d["regime_key"] = keys
    d["causal_vol_median_ref"] = vol_refs
    d["causal_bocpd_q75_ref"] = break_refs
    return d


def reliability_snapshot(expert: pd.DataFrame, row_pos: int, contract: dict[str, Any]) -> dict[str, Any]:
    cfg = contract["selector"]
    h = int(contract["target"]["primary_horizon_sessions"])
    current = expert.iloc[row_pos]
    current_origin = int(current["origin_index"])
    current_regime = str(current["regime_key"])
    if current_regime == "UNKNOWN":
        return {"eligible": False, "reason": "REGIME_UNKNOWN", "n": 0}

    hist = expert.iloc[:row_pos].copy()
    hist = hist[
        hist["parent_signal"].astype(int).ne(0)
        & hist["future_direction"].notna()
        & hist["regime_key"].eq(current_regime)
        & ((hist["origin_index"].astype(int) + h) <= current_origin)
    ]
    hist = hist.tail(int(cfg["rolling_cap"]))
    n = int(len(hist))
    if n < int(cfg["minimum_signal_history"]):
        return {"eligible": False, "reason": "INSUFFICIENT_SIGNAL_HISTORY", "n": n}

    actual = hist["future_direction"].astype(int)
    pred = hist["parent_signal"].astype(int)
    a_up = int((actual > 0).sum())
    a_down = int((actual < 0).sum())
    p_up = int((pred > 0).sum())
    p_down = int((pred < 0).sum())
    support = {
        "actual_up": a_up,
        "actual_down": a_down,
        "predicted_up": p_up,
        "predicted_down": p_down,
    }
    if a_up < int(cfg["minimum_realized_up"]) or a_down < int(cfg["minimum_realized_down"]):
        return {"eligible": False, "reason": "INSUFFICIENT_REALIZED_CLASS_SUPPORT", "n": n, **support}
    if p_up < int(cfg["minimum_predicted_up"]) or p_down < int(cfg["minimum_predicted_down"]):
        return {"eligible": False, "reason": "DEGENERATE_PREDICTED_CLASS_SUPPORT", "n": n, **support}

    y = (actual > 0).astype(int)
    yhat = (pred > 0).astype(int)
    ba = float(balanced_accuracy_score(y, yhat))
    eligible = ba >= float(cfg["minimum_balanced_reliability"])
    return {
        "eligible": bool(eligible),
        "reason": "ELIGIBLE" if eligible else "BALANCED_RELIABILITY_BELOW_FLOOR",
        "n": n,
        "balanced_reliability": ba,
        **support,
    }


def align_experts(legacy: pd.DataFrame, driver: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    common = sorted(set(legacy["origin_index"].astype(int)) & set(driver["origin_index"].astype(int)))
    l = legacy[legacy["origin_index"].isin(common)].sort_values("origin_index").reset_index(drop=True)
    d = driver[driver["origin_index"].isin(common)].sort_values("origin_index").reset_index(drop=True)
    if not np.array_equal(l["origin_index"].to_numpy(), d["origin_index"].to_numpy()):
        raise RuntimeError("V160_EXPERT_ALIGNMENT_FAIL")
    if not np.array_equal(l["future_direction"].astype(int).to_numpy(), d["future_direction"].astype(int).to_numpy()):
        raise RuntimeError("V160_ACTUAL_ALIGNMENT_FAIL")
    if not np.array_equal(l["regime_key"].astype(str).to_numpy(), d["regime_key"].astype(str).to_numpy()):
        raise RuntimeError("V160_REGIME_ALIGNMENT_FAIL")
    return l, d


def run_selector(legacy: pd.DataFrame, driver: pd.DataFrame, contract: dict[str, Any]) -> pd.DataFrame:
    legacy, driver = align_experts(legacy, driver)
    rows: list[dict[str, Any]] = []
    tie_order = {"LEGACY_RTQ_R126": 0, "DRIVER_RTQ_R126": 1}

    for i in range(len(legacy)):
        lr = legacy.iloc[i]
        dr = driver.iloc[i]
        snapshots = {
            "LEGACY_RTQ_R126": reliability_snapshot(legacy, i, contract),
            "DRIVER_RTQ_R126": reliability_snapshot(driver, i, contract),
        }
        current_signals = {
            "LEGACY_RTQ_R126": int(lr["parent_signal"]),
            "DRIVER_RTQ_R126": int(dr["parent_signal"]),
        }
        eligible = []
        for eid, snap in snapshots.items():
            if current_signals[eid] != 0 and snap.get("eligible") and math.isfinite(float(snap.get("balanced_reliability", np.nan))):
                eligible.append((float(snap["balanced_reliability"]), -tie_order[eid], eid))
        if eligible:
            eligible.sort(reverse=True)
            selected = eligible[0][2]
            final_direction = int(current_signals[selected])
            selected_reliability = float(snapshots[selected]["balanced_reliability"])
        else:
            selected = "NO_SIGNAL"
            final_direction = 0
            selected_reliability = np.nan

        rows.append({
            "origin_index": int(lr["origin_index"]),
            "origin_date": lr["origin_date"],
            "target_date": lr["target_date"],
            "future_direction": int(lr["future_direction"]),
            "target_return": float(lr["target_return"]),
            "regime_key": str(lr["regime_key"]),
            "legacy_signal": int(lr["parent_signal"]),
            "driver_signal": int(dr["parent_signal"]),
            "legacy_reliability": snapshots["LEGACY_RTQ_R126"].get("balanced_reliability"),
            "driver_reliability": snapshots["DRIVER_RTQ_R126"].get("balanced_reliability"),
            "legacy_eligible": bool(snapshots["LEGACY_RTQ_R126"].get("eligible", False)),
            "driver_eligible": bool(snapshots["DRIVER_RTQ_R126"].get("eligible", False)),
            "legacy_reason": snapshots["LEGACY_RTQ_R126"].get("reason"),
            "driver_reason": snapshots["DRIVER_RTQ_R126"].get("reason"),
            "selected_expert": selected,
            "selected_reliability": None if not math.isfinite(selected_reliability) else selected_reliability,
            "final_direction": final_direction,
        })
    return pd.DataFrame(rows)


def period_label(origin_date: Any, target_date: Any, contract: dict[str, Any]) -> str:
    o = pd.Timestamp(origin_date)
    t = pd.Timestamp(target_date)
    w = contract["windows"]
    periods = [
        ("FORMATION_2024", w["formation_start"], w["formation_end"]),
        ("VALIDATION_2025", w["validation_start"], w["validation_end"]),
        ("TEST_2026_AVAILABLE", w["test_start"], w["test_end"]),
    ]
    for label, a, b in periods:
        if pd.Timestamp(a) <= o <= pd.Timestamp(b) and t <= pd.Timestamp(b):
            return label
    return "OUTSIDE"


def score_frame(frame: pd.DataFrame, signal_col: str, contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    d = frame.copy()
    d["period"] = [period_label(o, t, contract) for o, t in zip(d["origin_date"], d["target_date"])]
    out = {}
    for p in ["FORMATION_2024", "VALIDATION_2025", "TEST_2026_AVAILABLE"]:
        out[p] = v159.direction_metrics(d[d["period"].eq(p)], signal_col)
    return out


def support_gate(selector: dict[str, dict[str, Any]], legacy: dict[str, dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    r = contract["evaluation"]["support_gate"]
    v = selector["VALIDATION_2025"]
    t = selector["TEST_2026_AVAILABLE"]
    lv = legacy["VALIDATION_2025"]
    lt = legacy["TEST_2026_AVAILABLE"]
    checks = {
        "validation_coverage": v.get("coverage", 0) >= float(r["validation_2025_coverage_min"]),
        "validation_balanced_beats_legacy": v.get("selective_balanced_accuracy", -1) > lv.get("selective_balanced_accuracy", 2),
        "validation_mcc_positive": v.get("mcc", 0) > 0,
        "validation_both_directions": v.get("up_signals", 0) > 0 and v.get("down_signals", 0) > 0,
        "test_coverage": t.get("coverage", 0) >= float(r["test_2026_coverage_min"]),
        "test_balanced_min": t.get("selective_balanced_accuracy", 0) >= float(r["test_2026_balanced_min"]),
        "test_not_more_than_003_below_legacy": t.get("selective_balanced_accuracy", -1) >= lt.get("selective_balanced_accuracy", 2) - 0.03,
        "test_mcc_positive": t.get("mcc", 0) > 0,
        "test_both_directions": t.get("up_signals", 0) > 0 and t.get("down_signals", 0) > 0,
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def main() -> int:
    contract = load_contract()
    legacy, driver, source_evidence = build_frozen_parents(contract)
    legacy = add_causal_regime(legacy, contract)
    driver = add_causal_regime(driver, contract)
    legacy, driver = align_experts(legacy, driver)
    selector = run_selector(legacy, driver, contract)

    legacy_scores = score_frame(legacy, "parent_signal", contract)
    driver_scores = score_frame(driver, "parent_signal", contract)
    selector_scores = score_frame(selector, "final_direction", contract)
    gate = support_gate(selector_scores, legacy_scores, contract)

    regime_counts = selector.groupby(["regime_key", "selected_expert"], dropna=False).size().reset_index(name="n")
    results = {
        "contract_id": contract["contract_id"],
        "status": "RETROSPECTIVE_FINAL_ARCHITECTURE_DIAGNOSTIC_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "production_authority": False,
        "stopping_rule": contract["stopping_rule"],
        "source_evidence": source_evidence,
        "experts": {
            "LEGACY_RTQ_R126": legacy_scores,
            "DRIVER_RTQ_R126": driver_scores,
        },
        "selector": selector_scores,
        "support_gate": gate,
        "interpretation_lock": {
            "selector_is_not_a_new_direction_model": True,
            "context_engines_are_not_equal_votes": True,
            "reversal_never_flips_direction": True,
            "NO_SIGNAL_is_not_NEUTRAL": True,
            "2025_2026_are_researcher_visible": True,
            "future_prospective_shadow_required_for_any_promotion": True,
            "post_score_repair_forbidden": True,
            "normal_day_retrospective_model_search_stops_after_V160": True,
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    legacy.assign(expert_id="LEGACY_RTQ_R126").to_csv(OUT / "v160_legacy_regime_expert.csv", index=False)
    driver.assign(expert_id="DRIVER_RTQ_R126").to_csv(OUT / "v160_driver_regime_expert.csv", index=False)
    selector.to_csv(OUT / "v160_selector_predictions.csv", index=False)
    regime_counts.to_csv(OUT / "v160_regime_selection_counts.csv", index=False)
    (OUT / "v160_results.json").write_text(json.dumps(results, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(results, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
