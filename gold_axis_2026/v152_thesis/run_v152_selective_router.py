from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import binomtest

from gold_axis_2026.v151_thesis import run_v151_locked_audit as v151

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v152_thesis/contracts/v152_selective_event_router_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v152_thesis"


def event_metric(g: pd.DataFrame, horizon: str) -> dict:
    z = g[g[horizon].notna() & g["score"].notna() & (g["score"] != 0)].copy()
    if z.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    signed = np.sign(z["score"].astype(float)) * z[horizon].astype(float)
    hits = int((signed > 0).sum())
    n = int(len(z))
    return {
        "n": n,
        "hits": hits,
        "hit_rate": float(hits / n),
        "median_signed_log_return": float(np.median(signed)),
        "exact_binomial_one_sided_p": float(binomtest(hits, n, p=0.5, alternative="greater").pvalue),
    }


def primary_router_mask(d: pd.DataFrame, contract: dict) -> pd.Series:
    fam = set(contract["event_router"]["primary_families"])
    return d["family"].isin(fam) & d["score"].notna() & d["score"].ne(0)


def high_confidence_mask(d: pd.DataFrame, contract: dict) -> pd.Series:
    strong = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
    return primary_router_mask(d, contract) & d["state"].isin(strong)


def gate(metric: dict, cfg: dict, require_p: bool) -> bool:
    if metric.get("n", 0) < int(cfg["minimum_n"]):
        return False
    if metric.get("hit_rate", 0.0) < float(cfg["minimum_hit_rate"]):
        return False
    if bool(cfg.get("median_signed_log_return_must_be_positive", False)) and metric.get("median_signed_log_return", 0.0) <= 0:
        return False
    if require_p and metric.get("exact_binomial_one_sided_p", 1.0) > float(cfg["maximum_one_sided_binomial_p"]):
        return False
    return True


def summarize(events: pd.DataFrame, contract: dict) -> dict:
    d = events.copy()
    d["year"] = d["event_ts"].dt.year
    horizons = [contract["event_router"]["primary_horizon"], *contract["event_router"]["secondary_horizons"]]
    periods = {
        "FORMATION_2023_2024": [2023, 2024],
        "RETROSPECTIVE_VALIDATION_2025": [2025],
        "RETROSPECTIVE_TEST_2026": [2026],
    }
    out = {"periods": {}, "router_policy": contract["event_router"]}
    for label, years in periods.items():
        g = d[d["year"].isin(years)]
        routed = g[primary_router_mask(g, contract)]
        high = g[high_confidence_mask(g, contract)]
        fomc = g[g["family"].isin(contract["event_router"]["separate_diagnostic_family"])]
        out["periods"][label] = {
            "pooled_all_events": {h: event_metric(g, h) for h in horizons},
            "primary_employment_inflation_router": {h: event_metric(routed, h) for h in horizons},
            "high_confidence_primary": {h: event_metric(high, h) for h in horizons},
            "fomc_diagnostic_only": {h: event_metric(fomc, h) for h in horizons},
            "coverage": {
                "all_event_rows": int(len(g)),
                "primary_router_rows": int(len(routed)),
                "high_confidence_rows": int(len(high)),
            },
        }
    formation = out["periods"]["FORMATION_2023_2024"]
    r15 = formation["primary_employment_inflation_router"][contract["event_router"]["primary_horizon"]]
    hi = formation["high_confidence_primary"][contract["event_router"]["primary_horizon"]]
    out["formation_gates"] = {
        "primary_router_r15_pass": gate(r15, contract["success_gates"]["primary_router_r15"], True),
        "high_confidence_tier_pass": gate(hi, contract["success_gates"]["high_confidence_tier"], False),
    }
    out["interpretation"] = (
        "Selective router: Employment/Inflation are primary short-horizon event specialists; "
        "FOMC remains separate diagnostic; general 1D/3D remains NO_SIGNAL unless separately proven."
    )
    return out


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V152_SUCCESSOR_SCORING":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    OUT.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(db) as conn:
        events = v151.load_event_rows(conn, "2023-01-01", "2026-09-11")
        current = v151.load_current_master_state(conn)
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "selective_event_router": summarize(events, contract),
        "current_master_state": current,
        "master_short_horizon_policy": {
            "normal_day_general_1d_3d": "NO_SIGNAL_NOT_PROVEN",
            "employment_inflation_event": "MACRO_EVENT_DIRECTION_ELIGIBLE",
            "fomc_event": "SEPARATE_DIAGNOSTIC_SPECIALIST",
            "market_shock": "POST_RELEASE_CONFIRMATION_ONLY",
        },
        "AUTO_SELECTOR": "OFF",
        "AUTO_ENSEMBLE": "OFF",
        "production_authority": False,
        "production_writes": "NONE",
        "future_prospective_shadow_required": True,
    }
    events.drop(columns=["metadata"], errors="ignore").to_csv(OUT / "v152_event_router_rows.csv", index=False)
    (OUT / "v152_selective_router_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
