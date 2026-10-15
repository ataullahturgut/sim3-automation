#!/usr/bin/env python3
"""Event-anchor analog portfolio protection V0. Research-only. No live trading.

Inputs (all UTF-8 CSV):
--library: OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv
--outcomes: case_id,low96,high96,ct; forward 96h price extrema measured
            from historical M15 bars, strictly for historical anchors.
--checkpoints: tt,p,c,r4,r1,r3,rv,ds,eff,loc,dd,nq1,nq6,zn1
               Only completed, origin-safe prices. Do not include future outcomes.
Use --year 2025 or 2026 to exclude contemporary/future archive cases.
Decision: co-sell confirmation PLUS analog risk >=0.20 OR unknown-extreme
(distance>=1 AND 4h realized volatility>=0.8 percentage points).
This is an *unvalidated* research hypothesis, NOT an automatic trading recommendation.
"""
import argparse
import csv
import json
import math
from datetime import datetime, timezone

FEATURES = (
    ("r4", 1.2, 1.0), ("rv", 0.65, 1.0),
    ("ds", 0.45, 0.5), ("eff", 0.55, 0.5),
    ("loc", 0.55, 0.4), ("dd", 1.5, 1.0),
    ("nq1", 0.65, 0.5), ("zn1", 0.15, 0.25),
)

def f(x):
    try:
        z = float(x)
        return z if math.isfinite(z) else None
    except (TypeError, ValueError):
        return None

def rows(path):
    with open(path, encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def library(archive, outcomes, evaluation_year):
    future = {r["case_id"]: r for r in rows(outcomes)}
    events = []
    for r in rows(archive):
        if r["asof_price_quality"] != "COMPLETE":
            continue
        year = utc(r["checkpoint_utc"]).year
        if year >= evaluation_year:
            continue  # Prevent future-year event knowledge.
        result = future.get(r["case_id"])
        if not result or f(result.get("low96")) is None or (f(result.get("ct")) or 0) < 40:
            continue
        events.append({
            "id": r["case_id"], "year": year,
            "org": r.get("org_plot_candidate", "UNMAPPED"),
            "dna": r.get("candidate_DNA", "UNRESOLVED"),
            "source_grade": r["evidence_grade"],
            "news_verified": r.get("onset_firstprint_verified", "NO"),
            "low96": float(result["low96"]),
            "high96": f(result.get("high96")),
            "features": {
                "r4": f(r.get("asof_ret4h_pct")),
                "rv": f(r.get("asof_rv4h_pct")),
                "ds": f(r.get("asof_downside_var_share4h")),
                "eff": f(r.get("asof_path_efficiency4h")),
                "loc": f(r.get("asof_close_location4h")),
                "dd": f(r.get("asof_from_high_dd4h_pct")),
                "nq1": f(r.get("asof_nq_return_h1_pct")),
                "zn1": f(r.get("asof_zn_futures_price_return_h1_pct")),
            }
        })
    if len(events) < 9:
        raise ValueError("Insufficient historical cases before evaluation year")
    return events

def analog_score(market, events, k=9):
    scored = []
    for event in events:
        distance, weight_sum = 0.0, 0.0
        for key, scale, weight in FEATURES:
            a, b = f(market.get(key)), event["features"][key]
            if a is None or b is None:
                continue
            distance += weight * ((a - b) / scale) ** 2
            weight_sum += weight
        if weight_sum <= 0:
            continue
        scored.append((math.sqrt(distance / weight_sum), event))
    if len(scored) < k:
        raise ValueError("Too few comparable archive cases")
    scored.sort(key=lambda x: x[0])
    nearest = scored[:k]
    values = [1.0 / (dist + 0.35) ** 2 for dist, _ in nearest]
    denominator = sum(values)
    score = sum(w for w, (_, case) in zip(values, nearest) if case["low96"] <= -3.0) / denominator
    return {
        "analog_risk_score": score,  # NOT a calibrated probability.
        "nearest_distance": nearest[0][0],
        "nearest_ids": [event["id"] for _, event in nearest[:3]],
        "nearest_orgs": [event["org"] for _, event in nearest[:3]],
    }

def replay(checkpoints, events, mode="hybrid", fee=0.008):
    if not checkpoints:
        raise ValueError("No checkpoint data")
    if any(utc(checkpoints[i]["tt"]) >= utc(checkpoints[i+1]["tt"]) for i in range(len(checkpoints)-1)):
        raise ValueError("Checkpoints must be strictly chronological")
    first_price = f(checkpoints[0].get("p"))
    if not first_price or first_price <= 0:
        raise ValueError("Missing first executable price")
    ounces = 100.0 * (1-fee) / first_price
    cash, holding, last_exit = 0.0, True, None
    high_nav, maximum_drawdown = 100.0, 0.0
    logs = []
    for row in checkpoints:
        t = utc(row["tt"])
        p, c = f(row.get("p")), f(row.get("c"))
        r4, r1, r3, nq6, rv = (f(row.get(z)) for z in ("r4", "r1", "r3", "nq6", "rv"))
        if p is None or c is None or r4 is None or r1 is None or r3 is None:
            raise ValueError("Incomplete checkpoint price/returns at " + row["tt"])
        analog = analog_score(row, events)
        co_sell = nq6 is not None and r4 <= -1 and nq6 <= -1
        novelty = analog["nearest_distance"] >= 1 and rv is not None and rv >= 0.8
        if mode == "hold":
            protect = False
        elif mode == "cosell":
            protect = co_sell
        elif mode == "hybrid":
            protect = co_sell and (analog["analog_risk_score"] >= 0.20 or novelty)
        else:
            raise ValueError("Unknown mode")
        action = "HOLD_GOLD" if holding else "HOLD_CASH"
        if holding and protect:
            cash = ounces * p * (1-fee)
            ounces = 0.0
            holding, last_exit, action = False, t, "PROTECT_TO_CASH"
        elif (not holding and last_exit is not None and
              (t-last_exit).total_seconds() >= 72*3600 and r1 >= 2 and r3 >= 0.5):
            ounces = cash * (1-fee) / p
            cash = 0.0
            holding, action = True, "RESTORE_GOLD"
        nav = ounces*c*(1-fee) + cash
        high_nav = max(high_nav, nav)
        maximum_drawdown = max(maximum_drawdown, 100*(1-nav/high_nav))
        logs.append({
            "utc": row["tt"], "action": action,
            "price": p, "nav_if_liquidated": round(nav, 6),
            "phase_hypothesis": (
                "BREAK_OR_LIQUIDATION_CANDIDATE" if co_sell
                else "RECOVERY_CANDIDATE" if r1 >= 2 and r3 >= 0.5
                else "UNRESOLVED_OR_NORMAL"
            ),
            "cross_asset_co_sell": co_sell,
            "out_of_archive_domain": novelty,
            "risk_score_not_calibrated": round(analog["analog_risk_score"], 6),
            "nearest_distance": round(analog["nearest_distance"], 6),
            "nearest_case_ids": analog["nearest_ids"],
            "nearest_org_candidates_NOT_CAUSAL": analog["nearest_orgs"],
            "firstprint_proven": False
        })
    end = ounces*f(checkpoints[-1]["c"])*(1-fee)+cash
    return {"initial_usd": 100, "final_usd": round(end, 6),
            "net_return_pct": round(end-100, 6),
            "max_drawdown_pct": round(maximum_drawdown, 4),
            "protective_exits": sum(x["action"] == "PROTECT_TO_CASH" for x in logs),
            "decisions": logs}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", required=True)
    ap.add_argument("--outcomes", required=True)
    ap.add_argument("--checkpoints", required=True)
    ap.add_argument("--year", type=int, required=True, choices=(2025, 2026))
    ap.add_argument("--mode", choices=("hold", "cosell", "hybrid"), default="hybrid")
    ap.add_argument("--fee", type=float, default=0.008)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    checks = [r for r in rows(args.checkpoints) if utc(r["tt"]).year == args.year]
    events = library(args.library, args.outcomes, args.year)
    result = replay(checks, events, args.mode, args.fee)
    result["model_status"] = "RESEARCH_ONLY_NOT_VALIDATED"
    result["archive_cases_used"] = len(events)
    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
    print(json.dumps({k:v for k,v in result.items() if k!="decisions"},ensure_ascii=False))

if __name__ == "__main__":
    main()
