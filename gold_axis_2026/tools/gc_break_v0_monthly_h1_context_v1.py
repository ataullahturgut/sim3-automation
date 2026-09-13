from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_monthly_h1_context_contract_v1.json"
H1_PATH = ROOT / "data_pipeline" / "audits" / "pilot_validation_v145" / "pilot_h1_monthly_evidence_v145.csv"
DIAG_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_diagnostic_v1"
OUT_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_monthly_h1_context_v1"
ENGINES = ["CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK"]
NON_RW = ["CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M"]


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_MONTHLY_CONTEXT_DIAGNOSTIC":
        raise RuntimeError("MONTHLY_CONTEXT_CONTRACT_NOT_FROZEN")
    if c["role_lock"]["may_trigger_break_alert"] is not False:
        raise RuntimeError("MONTHLY_TRIGGER_GUARD_FAIL")
    if c["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_WRITE_GUARD_FAIL")
    return c


def build_month_context() -> pd.DataFrame:
    h = pd.read_csv(H1_PATH)
    h = h[h["engine_id"].isin(ENGINES)].copy()
    h["target_month"] = h["target_month"].astype(str)
    h["origin_month"] = h["origin_month"].astype(str)
    h["forecast"] = pd.to_numeric(h["forecast"], errors="raise")
    if h.duplicated(["engine_id", "target_month"]).any():
        raise RuntimeError("DUPLICATE_H1_ENGINE_TARGET")
    piv = h.pivot(index="target_month", columns="engine_id", values="forecast")
    if not set(ENGINES).issubset(piv.columns):
        raise RuntimeError("H1_ENGINE_MISSING")
    origins = h.groupby("target_month")["origin_month"].nunique()
    if (origins != 1).any():
        raise RuntimeError("MULTIPLE_H1_ORIGINS_PER_TARGET")
    out = piv[ENGINES].copy()
    out["rw_anchor"] = out["RANDOM_WALK"]
    for e in NON_RW:
        out[f"gap_{e.lower()}_vs_rw"] = (out[e] - out["rw_anchor"]) / out["rw_anchor"]
    out["up_votes"] = sum((out[e] > out["rw_anchor"]).astype(int) for e in NON_RW)
    out["down_votes"] = sum((out[e] < out["rw_anchor"]).astype(int) for e in NON_RW)
    out["consensus_direction"] = np.select(
        [out["up_votes"].ge(2), out["down_votes"].ge(2)], ["UP", "DOWN"], default="MIXED"
    )
    vals = out[ENGINES].to_numpy(float)
    out["dispersion"] = np.std(vals, axis=1, ddof=0) / np.mean(vals, axis=1)
    out["range_dispersion"] = (np.max(vals, axis=1) - np.min(vals, axis=1)) / out["rw_anchor"]
    out["forecast_median"] = np.median(vals, axis=1)
    out["forecast_mean"] = np.mean(vals, axis=1)
    out["origin_month"] = h.groupby("target_month")["origin_month"].first()
    out = out.reset_index()
    return out


def main() -> int:
    contract = load_contract()
    if not (DIAG_DIR / "gc_break_v0_origin_panel.csv").exists():
        raise RuntimeError("RUN_GOVERNED_DIAGNOSTIC_FIRST")
    panel = pd.read_csv(DIAG_DIR / "gc_break_v0_origin_panel.csv", parse_dates=["date"])
    events = pd.read_csv(DIAG_DIR / "gc_break_v0_break_events.csv", parse_dates=["break_date"])
    ctx = build_month_context()

    panel["target_month"] = panel["date"].dt.strftime("%Y-%m")
    aug = panel.merge(ctx, on="target_month", how="left", validate="many_to_one", suffixes=("", "_h1"))
    aug["monthly_h1_consensus_vs_regime"] = np.select(
        [
            aug["consensus_direction"].eq(aug["regime_pre"]),
            aug["consensus_direction"].isin(["UP", "DOWN"]) & aug["regime_pre"].isin(["UP", "DOWN"]) & aug["consensus_direction"].ne(aug["regime_pre"]),
        ],
        ["ALIGNED", "OPPOSITE"],
        default="MIXED_OR_UNAVAILABLE",
    )

    ev = events.merge(
        aug[["date", "target_month", "consensus_direction", "monthly_h1_consensus_vs_regime", "dispersion", "range_dispersion", "forecast_median", "rw_anchor"]],
        left_on="break_date", right_on="date", how="left", validate="one_to_one",
    )
    nonbreak = aug[aug["event_id"].isna() & aug["dispersion"].notna()].copy()
    break_rows = aug[aug["event_id"].notna() & aug["dispersion"].notna()].copy()

    relation_counts = ev["monthly_h1_consensus_vs_regime"].value_counts(dropna=False).to_dict()
    summary = {
        "audit_id": "GC_BREAK_V0_MONTHLY_H1_CONTEXT_V1",
        "contract_id": contract["contract_id"],
        "contract_status": contract["status"],
        "production_authority": False,
        "production_database_write": "NONE",
        "prospective_claim": False,
        "daily_origins": int(len(aug)),
        "months_with_h1_context": int(ctx["target_month"].nunique()),
        "origins_with_h1_context": int(aug["consensus_direction"].notna().sum()),
        "objective_breaks": int(len(events)),
        "breaks_with_h1_context": int(ev["consensus_direction"].notna().sum()),
        "break_consensus_vs_prebreak_regime": {str(k): int(v) for k, v in relation_counts.items()},
        "dispersion_descriptive": {
            "break_origin_mean": float(break_rows["dispersion"].mean()) if len(break_rows) else None,
            "break_origin_median": float(break_rows["dispersion"].median()) if len(break_rows) else None,
            "nonbreak_origin_mean": float(nonbreak["dispersion"].mean()) if len(nonbreak) else None,
            "nonbreak_origin_median": float(nonbreak["dispersion"].median()) if len(nonbreak) else None,
            "range_break_origin_mean": float(break_rows["range_dispersion"].mean()) if len(break_rows) else None,
            "range_nonbreak_origin_mean": float(nonbreak["range_dispersion"].mean()) if len(nonbreak) else None,
        },
        "role_lock": "MONTHLY_H1_REMAINS_STANDALONE_FORECAST_AND_STRATEGIC_CONTEXT_ONLY; NOT_A_BREAK_TRIGGER",
        "interpretation_lock": "DESCRIPTIVE_RETROSPECTIVE_CONTEXT_ONLY; no threshold, trigger or weight may be selected from this diagnostic.",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ctx.to_csv(OUT_DIR / "gc_break_monthly_h1_context_by_month.csv", index=False)
    aug.to_csv(OUT_DIR / "gc_break_monthly_h1_augmented_origin_panel.csv", index=False)
    ev.to_csv(OUT_DIR / "gc_break_monthly_h1_break_context.csv", index=False)
    (OUT_DIR / "gc_break_v0_monthly_h1_context_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
