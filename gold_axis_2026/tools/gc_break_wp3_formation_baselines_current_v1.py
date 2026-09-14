from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "gc_break_v0" / "gc_break_wp3_baseline_contract_v1.json").exists():
            return parent
    raise RuntimeError("PROJECT_ROOT_NOT_FOUND")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def event_num(x: object) -> float:
    if pd.isna(x) or str(x).strip() == "":
        return np.nan
    s = str(x).strip()
    if not (s.startswith("B") and s[1:].isdigit()):
        raise RuntimeError(f"EVENT_ID_FORMAT_FAIL:{s}")
    return float(int(s[1:]))


def same_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_UP")) | ((regime == "DOWN") & (state == "ROBUST_DOWN"))


def opposite_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_DOWN")) | ((regime == "DOWN") & (state == "ROBUST_UP"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, required=True)
    ap.add_argument("--wp1-closure-audit", type=Path, required=True)
    ap.add_argument("--wp2-origin-labels", type=Path, required=True)
    ap.add_argument("--wp2-events", type=Path, required=True)
    ap.add_argument("--wp2-audit", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)

    root = project_root()
    contract = json.loads((root / "gc_break_v0" / "gc_break_wp3_baseline_contract_v1.json").read_text())
    prereg = json.loads((root / "gc_break_v0" / "gc_break_wp3_baseline_prereg_v1.json").read_text())
    if contract.get("status") != "FROZEN_BEFORE_FORMATION_BASELINE_SCORING":
        raise RuntimeError("WP3_BASELINE_CONTRACT_NOT_FROZEN")
    if contract.get("event_contract") != "GC_BREAK_EVENT_CONTRACT_V1":
        raise RuntimeError("WP3_EVENT_CONTRACT_MISMATCH")
    guards = contract.get("governance", {})
    must_true = ["no_random_split", "no_post_score_threshold_tuning", "no_equal_weight_voting",
                 "no_winner_promotion_from_2025_2026", "no_database_writes"]
    if not all(guards.get(k) is True for k in must_true):
        raise RuntimeError("WP3_GOVERNANCE_GUARD_FAIL")
    if guards.get("auto_selector") != "OFF" or guards.get("auto_ensemble") != "OFF":
        raise RuntimeError("WP3_AUTO_GUARD_FAIL")
    if prereg.get("status") != "FROZEN_BEFORE_FULL_FORMATION_CHALLENGE_SCORING":
        raise RuntimeError("WP3_EARLIER_PREREG_NOT_FROZEN")

    wp1 = json.loads(a.wp1_closure_audit.read_text())
    wp2 = json.loads(a.wp2_audit.read_text())
    if wp1.get("audit_id") != "GC_BREAK_WP1_MANIFEST_CLOSURE_AUDIT_V1" or wp1.get("status") != "PASS" or int(wp1.get("unresolved_rows", -1)) != 0:
        raise RuntimeError("WP1_CLOSURE_GATE_FAIL")
    if wp2.get("audit_id") != "GC_BREAK_WP2_LABEL_AUDIT_V1" or wp2.get("status") not in {"PASS", "PASS_WITH_DATA_DENSITY_WARNING"}:
        raise RuntimeError("WP2_GATE_FAIL")
    if wp2.get("engine_independence_test", {}).get("passed") is not True or float(wp2.get("primary_contract", {}).get("k_sigma", -1)) != 3.0:
        raise RuntimeError("WP2_ENGINE_OR_K_GATE_FAIL")

    panel = pd.read_csv(a.panel)
    labels = pd.read_csv(a.wp2_origin_labels)
    events = pd.read_csv(a.wp2_events)
    for d, c in ((panel, "date"), (labels, "trade_date"), (events, "trade_date")):
        d[c] = pd.to_datetime(d[c]).dt.normalize()
        if d[c].duplicated().any(): raise RuntimeError(f"DUPLICATE_DATE:{c}")
    if list(panel["date"]) != list(labels["trade_date"]): raise RuntimeError("WP1_WP2_ORIGIN_DATE_MISMATCH")
    if panel["date"].min() < pd.Timestamp("2022-01-01") or panel["date"].max() > pd.Timestamp("2024-12-31"):
        raise RuntimeError("FORMATION_BOUNDARY_FAIL")
    if len(panel) != int(wp2.get("formation_governed_origins", -1)) or len(events) != int(wp2.get("primary_events", {}).get("count", -1)):
        raise RuntimeError("WP2_COUNT_MISMATCH")
    if not np.allclose(pd.to_numeric(panel["close"]), pd.to_numeric(labels["close"]), rtol=0, atol=1e-8):
        raise RuntimeError("WP1_WP2_CLOSE_MISMATCH")
    if pd.to_numeric(labels["k_sigma"], errors="raise").ne(3.0).any() or pd.to_numeric(events["k_sigma"], errors="raise").ne(3.0).any():
        raise RuntimeError("NONPRIMARY_K_PRESENT")
    if labels["prospective_claim"].astype(str).str.lower().ne("false").any() or events["prospective_claim"].astype(str).str.lower().ne("false").any():
        raise RuntimeError("PROSPECTIVE_CLAIM_FAIL")
    needed = {"fast_state", "slow_state", "emergency_reversal", "emergency_status", "bocpd_state"}
    if not needed <= set(panel.columns): raise RuntimeError(f"WP1_COLUMNS_MISSING:{sorted(needed-set(panel.columns))}")

    p = panel.sort_values("date").reset_index(drop=True).copy()
    l = labels.sort_values("trade_date").reset_index(drop=True)
    p["regime_pre"] = l["regime_before"].astype(str)
    p["regime_post"] = l["regime_after"].astype(str)
    p["threshold_log_move"] = pd.to_numeric(l["threshold"], errors="coerce")
    p["adverse_log_move"] = pd.to_numeric(l["adverse_move"], errors="coerce").clip(lower=0)
    p["adverse_fraction"] = p["adverse_log_move"] / p["threshold_log_move"]
    p["event_id"] = l["event_id"].map(event_num)
    p["wp2_break_flag"] = l["is_break"].astype(str).str.lower().eq("true")

    ev = events.sort_values("trade_date").reset_index(drop=True).copy()
    ev["event_id"] = ev["event_id"].map(event_num).astype(int)
    ev = ev.rename(columns={"trade_date": "break_date", "pre_regime": "old_regime", "post_regime": "new_regime"})
    if set(ev["break_date"]) != set(p.loc[p["wp2_break_flag"], "date"]): raise RuntimeError("WP2_EVENT_DATE_MISMATCH")
    if set(ev["event_id"]) != set(p["event_id"].dropna().astype(int)): raise RuntimeError("WP2_EVENT_ID_MISMATCH")

    valid = p["regime_pre"].isin(["UP", "DOWN"])
    p["no_warning"] = False
    p["path_half"] = valid & p["adverse_fraction"].ge(0.50)
    p["fast_conflict"] = valid & ~same_robust(p["fast_state"], p["regime_pre"])
    p["fast_opposite"] = valid & opposite_robust(p["fast_state"], p["regime_pre"])
    p["slow_conflict"] = valid & ~same_robust(p["slow_state"], p["regime_pre"])
    p["slow_opposite"] = valid & opposite_robust(p["slow_state"], p["regime_pre"])
    p["emergency_supported"] = p["emergency_status"].eq("AVAILABLE_FROZEN_REFERENCE")
    p["emergency_reversal_opposite"] = pd.Series(pd.NA, index=p.index, dtype="boolean")
    em = p["emergency_supported"]
    p.loc[em, "emergency_reversal_opposite"] = (
        ((p.loc[em, "regime_pre"] == "UP") & (p.loc[em, "emergency_reversal"] == "DOWN_ALERT")) |
        ((p.loc[em, "regime_pre"] == "DOWN") & (p.loc[em, "emergency_reversal"] == "UP_ALERT"))
    )
    p["core_weakening_native"] = pd.Series(pd.NA, index=p.index, dtype="boolean")
    p.loc[em, "core_weakening_native"] = p.loc[em, "fast_conflict"].astype(bool) | p.loc[em, "emergency_reversal_opposite"].astype(bool)
    p["bocpd_native_monthly_prereg"] = p["bocpd_state"].eq("ADVERSE_BREAK_CANDIDATE")

    diag = load_module(root / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_wp3_diag_current")
    primary = {
        "NO_WARNING": ("no_warning", pd.Series(True, index=p.index)),
        "PATH_HALF": ("path_half", pd.Series(True, index=p.index)),
        "FAST_CONFLICT": ("fast_conflict", pd.Series(True, index=p.index)),
        "FAST_OPPOSITE": ("fast_opposite", pd.Series(True, index=p.index)),
        "SLOW_CONFLICT": ("slow_conflict", pd.Series(True, index=p.index)),
        "EMERGENCY_REVERSAL_OPPOSITE": ("emergency_reversal_opposite", em),
        "CORE_WEAKENING_NATIVE": ("core_weakening_native", em),
    }
    metrics, episode_frames = [], []
    for bid, (col, mask) in primary.items():
        support = p.loc[mask.astype(bool)].copy().reset_index(drop=True)
        if support[col].isna().any(): raise RuntimeError(f"SIGNAL_MISSING_ON_SUPPORT:{bid}")
        eligible = ev[ev["break_date"].isin(set(support["date"]))].copy().reset_index(drop=True)
        m, e = diag.evaluate_signal(support, eligible, col)
        m.update({"baseline_id": bid, "scope": "PRIMARY_CURRENT_CONTRACT", "available_origins": len(support),
                  "missing_origins": len(p)-len(support), "support_start": support["date"].min().date().isoformat(),
                  "support_end": support["date"].max().date().isoformat()})
        metrics.append(m)
        if not e.empty:
            e = e.copy(); e["baseline_id"] = bid; e["scope"] = m["scope"]; episode_frames.append(e)

    bs = p[p["bocpd_state"].notna()].copy().reset_index(drop=True)
    bev = ev[ev["break_date"].isin(set(bs["date"]))].copy().reset_index(drop=True)
    m, e = diag.evaluate_signal(bs, bev, "bocpd_native_monthly_prereg")
    m.update({"baseline_id": "B5_BOCPD_NATIVE_MONTHLY_PREREG_SUPPLEMENT", "scope": "SUPPLEMENTARY_EARLIER_PREREG_NOT_CURRENT_CONTRACT",
              "available_origins": len(bs), "missing_origins": len(p)-len(bs), "support_start": bs["date"].min().date().isoformat(),
              "support_end": bs["date"].max().date().isoformat()})
    metrics.append(m)
    if not e.empty:
        e = e.copy(); e["baseline_id"] = m["baseline_id"]; e["scope"] = m["scope"]; episode_frames.append(e)

    metrics_df = pd.DataFrame(metrics)
    expected = [x["id"] for x in contract["warning_baselines"]]
    got = metrics_df.loc[metrics_df["scope"].eq("PRIMARY_CURRENT_CONTRACT"), "baseline_id"].tolist()
    if got != expected: raise RuntimeError(f"CONTRACT_BASELINE_SET_FAIL:{expected}:{got}")
    episodes_df = pd.concat(episode_frames, ignore_index=True) if episode_frames else pd.DataFrame()
    conf = diag.confirmation_delays(p, ev)
    conf_ok = conf.dropna(subset=["delay_observations"])
    conf_summary = {"events": len(conf), "confirmed_before_next_break": len(conf_ok),
                    "confirmation_rate_before_next_break": float(len(conf_ok)/len(conf)) if len(conf) else None,
                    "median_confirmation_delay_observations": float(conf_ok["delay_observations"].median()) if len(conf_ok) else None,
                    "median_confirmation_delay_calendar_days": float(conf_ok["delay_calendar_days"].median()) if len(conf_ok) else None}

    reconciliation = {
        "audit_id": "GC_BREAK_WP3_PREREG_GOVERNANCE_RECONCILIATION_V1",
        "primary_scoring_authority": contract["contract_id"], "primary_contract_status": contract["status"],
        "earlier_prereg_id": prereg["prereg_id"], "earlier_prereg_status": prereg["status"],
        "current_contract_baselines": expected, "earlier_prereg_baselines": [x["id"] for x in prereg["baselines"]],
        "difference_handling": "Current executable contract is primary. Earlier prereg BOCPD B5 is retained only as supplementary historical prereg evidence; no artifact is rewritten.",
        "threshold_changes_after_scoring": "NONE", "production_authority": False
    }
    support = {"formation_origins": len(p), "emergency_available_origins": int(em.sum()), "emergency_unavailable_origins": int((~em).sum()),
               "emergency_unavailable_by_year": {str(int(y)): int(n) for y,n in p.loc[~em].groupby(p.loc[~em,"date"].dt.year).size().items()},
               "emergency_no_imputation_policy": "Emergency and CORE are scored only on AVAILABLE_FROZEN_REFERENCE origins; unavailable origins are excluded from origin and event denominators."}

    p.to_csv(a.output_dir / "gc_break_wp3_current_formation_baseline_panel_v1.csv", index=False)
    metrics_df.to_csv(a.output_dir / "gc_break_wp3_current_formation_baseline_metrics_v1.csv", index=False)
    episodes_df.to_csv(a.output_dir / "gc_break_wp3_current_formation_baseline_episodes_v1.csv", index=False)
    conf.to_csv(a.output_dir / "gc_break_wp3_current_slow_confirmation_v1.csv", index=False)
    (a.output_dir / "gc_break_wp3_prereg_governance_reconciliation_v1.json").write_text(json.dumps(reconciliation, indent=2, sort_keys=True)+"\n")
    clean = metrics_df.replace({np.nan: None}).set_index("baseline_id").to_dict(orient="index")
    summary = {
        "audit_id": "GC_BREAK_WP3_CURRENT_FORMATION_BASELINES_V1", "status": "EVIDENCE_GENERATED_NOT_YET_CLOSED",
        "contract_id": contract["contract_id"], "contract_status": contract["status"], "formation_window": contract["formation_window"],
        "formation_origins": len(p), "primary_break_events": len(ev), "wp1_closure_status": wp1["status"], "wp2_status": wp2["status"],
        "wp2_data_density_warning_inherited": wp2.get("data_density_diagnostics"), "primary_metrics": clean,
        "slow_confirmation": conf_summary, "support": support, "prereg_reconciliation": reconciliation,
        "model_learning_performed": False, "threshold_tuning_performed": False, "random_split_used": False,
        "database_write": "NONE", "challenge_2025_accessed": False, "stress_2026_accessed": False, "prospective_claim": False,
        "next_gate": "Inspect WP3 evidence under manifest. Do not begin WP4 or promote a baseline before explicit evidence review."
    }
    (a.output_dir / "gc_break_wp3_current_formation_baselines_v1_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)+"\n")
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
