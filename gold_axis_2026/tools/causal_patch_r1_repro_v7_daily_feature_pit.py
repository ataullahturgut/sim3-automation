from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import causal_patch_r1_repro_v6_monthly_level as v6

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1"
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_DAILY_FEATURE_PIT_CHANGE_CONTROL_V7_2026-09-02.md"
V6_EVIDENCE = OUT / "locked_replay_v6_monthly_level_evidence.json"
IDENTITY = "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE"
PASS_ID = "PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS"
FAIL_ID = "PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_FAIL_NO_RETUNE"
LOCKED_START = pd.Timestamp("2023-01-01")
LOCKED_END = pd.Timestamp("2026-07-01")
L = 252


def feature_sample_v7(target: pd.Timestamp, xau_daily: pd.DataFrame, core: pd.DataFrame, nas_monthly: pd.Series):
    daily_returns = np.log(xau_daily[["Gold"]]).diff().dropna()
    p = target - pd.offsets.MonthBegin(1)
    pp = p - pd.offsets.MonthBegin(1)
    ppp = p - pd.offsets.MonthBegin(2)
    if any(q not in core.index for q in [p, pp]) or pp not in nas_monthly.index or ppp not in nas_monthly.index:
        raise RuntimeError(f"V7_FEATURE_MONTH_MISSING:{target.date()}")

    origin_date = target - pd.Timedelta(days=1)
    # Gold Data R2.7 completed-session rule: same-origin-date vendor 1day
    # observations are ineligible because the bar may still be in progress.
    history = daily_returns.loc[daily_returns.index < origin_date]
    if len(history) < L:
        raise RuntimeError(f"V7_DAILY_FEATURE_HISTORY_TOO_SHORT:{target.date()}:{len(history)}")
    if history.index.max() >= origin_date:
        raise RuntimeError(f"V7_SAME_ORIGIN_DATE_FEATURE_USE:{target.date()}:{history.index.max().date()}")

    x = v6.causal_decomp(history.iloc[-L:].values.astype(np.float32), 21).astype(np.float32)
    nasdaq = float(np.log(float(nas_monthly.loc[pp]) / float(nas_monthly.loc[ppp])))
    fx = float(np.log(float(core.loc[p, "usdcny"]) / float(core.loc[pp, "usdcny"])))
    gpr = float(core.loc[pp, "gpr"])
    macro = np.array(
        [float(core.loc[p, "fedfunds"]), nasdaq, fx, np.log1p(gpr), v6.gpr_z_asof(core, pp)],
        dtype=np.float32,
    )
    return target, x, macro


def pit_audit(xau_daily: pd.DataFrame) -> dict:
    daily_returns = np.log(xau_daily[["Gold"]]).diff().dropna()
    rows = []
    for target in pd.date_range(LOCKED_START, LOCKED_END, freq="MS"):
        origin_date = target - pd.Timedelta(days=1)
        eligible = daily_returns.loc[daily_returns.index < origin_date]
        if len(eligible) < L:
            raise RuntimeError(f"V7_PIT_HISTORY_TOO_SHORT:{target.date()}:{len(eligible)}")
        selected = eligible.iloc[-L:]
        rows.append(
            {
                "target": target.strftime("%Y-%m"),
                "origin_date": origin_date.date().isoformat(),
                "eligible_return_count": int(len(eligible)),
                "selected_return_count": int(len(selected)),
                "selected_max_date": selected.index.max().date().isoformat(),
                "strictly_before_origin": bool(selected.index.max() < origin_date),
                "same_origin_date_use": int(np.sum(selected.index == origin_date)),
            }
        )
    return {
        "locked_origins": len(rows),
        "min_eligible_return_count": min(r["eligible_return_count"] for r in rows),
        "min_selected_return_count": min(r["selected_return_count"] for r in rows),
        "same_origin_date_feature_uses": sum(r["same_origin_date_use"] for r in rows),
        "strict_before_origin_count": sum(int(r["strictly_before_origin"]) for r in rows),
        "pass": bool(
            len(rows) == 43
            and min(r["selected_return_count"] for r in rows) == L
            and sum(r["same_origin_date_use"] for r in rows) == 0
            and all(r["strictly_before_origin"] for r in rows)
        ),
    }


def fail(reason: str) -> int:
    evidence = {
        "candidate_id": IDENTITY,
        "parent_candidate_id": v6.IDENTITY,
        "evidence_class": "HISTORICAL_REPLAY_MODEL_IMPACT",
        "prospective_claim": False,
        "model_impact_pass": False,
        "decision": FAIL_ID,
        "failure_reason": reason[:500],
        "post_result_retune": False,
        "raw_vendor_market_values_logged": False,
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
    }
    (OUT / "locked_replay_v7_daily_feature_pit_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"V7_DECISION={FAIL_ID}")
    print("POST_RESULT_RETUNE=NO")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    return 2


def main() -> int:
    text = CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_V7_MODEL_RESULT" not in text or IDENTITY not in text:
        raise RuntimeError("V7_CONTRACT_NOT_FROZEN")

    v6e = json.loads(V6_EVIDENCE.read_text(encoding="utf-8"))
    if not v6e.get("model_impact_pass") or v6e.get("decision") != "PATCH_R1_V6_MONTHLY_LEVEL_MODEL_IMPACT_PASS":
        raise RuntimeError("V6_PARENT_NOT_PASS")
    geometry = json.loads((OUT / "frozen_geometry.json").read_text(encoding="utf-8"))["selected_pre_2023_geometry"]
    if (int(geometry["L"]), int(geometry["P"]), int(geometry["D"])) != (252, 21, 32):
        raise RuntimeError("V7_GEOMETRY_MISMATCH")

    core = v6.load_core()
    session = v6.requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-Patch-V7-PIT/1.0"})
    try:
        xau_daily = v6.fetch_xau_daily(session)
        daily_level, _ = v6.daily_monthly_levels(xau_daily)
        hourly_anchor, _, _ = v6.fetch_hourly_anchor_levels(session)
        nas_monthly = v6.fetch_nasdaq_monthly(session)
        pit = pit_audit(xau_daily)
        if not pit["pass"]:
            return fail(f"PIT_GATE_FAIL:{pit}")

        # One and only one implementation change from V6: replace the feature
        # cutoff helper with the frozen completed-session rule above.
        v6.feature_sample = feature_sample_v7
        first, fv1 = v6.locked_predictions(core, xau_daily, nas_monthly, daily_level, hourly_anchor)
        second, fv2 = v6.locked_predictions(core, xau_daily, nas_monthly, daily_level, hourly_anchor)
    except Exception as exc:
        return fail(str(exc))

    first = first.rename(columns={"patch_v6": "patch_v7"})
    second = second.rename(columns={"patch_v6": "patch_v7"})
    maxdiff = float(np.max(np.abs(first["patch_v7"].to_numpy() - second["patch_v7"].to_numpy())))

    ref = pd.read_csv(ROOT / "production_closure" / "production_history_43.csv")
    joined = ref.merge(first, on="month", how="inner")
    if len(joined) != 43:
        return fail(f"COMMON_N_NOT_43:{len(joined)}")

    target_ok = 0
    rw_ok = 0
    for _, row in joined.iterrows():
        target = pd.Timestamp(str(row["month"]) + "-01")
        p = target - pd.offsets.MonthBegin(1)
        target_ok += int(abs(float(core.loc[target, "gold_monthly"]) - float(row["actual"])) <= 1e-9)
        rw_ok += int(abs(float(core.loc[p, "gold_monthly"]) - float(row["rw"])) <= 1e-9)

    candidate = v6.error_metrics(joined["actual"], joined["patch_v7"])
    rw = v6.error_metrics(joined["actual"], joined["rw"])
    hard = bool(
        pit["pass"]
        and target_ok == 43
        and rw_ok == 43
        and int(fv1 + fv2) == 0
        and maxdiff <= 1e-8
    )
    performance = bool(
        candidate["MAPE_pct"] < rw["MAPE_pct"]
        and candidate["MAE"] < rw["MAE"]
        and candidate["worst_APE_pct"] <= 1.25 * rw["worst_APE_pct"]
    )
    passed = bool(hard and performance)
    decision = PASS_ID if passed else FAIL_ID

    joined["patch_v7_ape"] = np.abs(joined["patch_v7"] - joined["actual"]) / joined["actual"] * 100.0
    joined.to_csv(OUT / "locked_replay_v7_daily_feature_pit_43.csv", index=False)
    evidence = {
        "candidate_id": IDENTITY,
        "parent_candidate_id": v6.IDENTITY,
        "evidence_class": "HISTORICAL_REPLAY_MODEL_IMPACT",
        "prospective_claim": False,
        "daily_feature_rule": "TWELVE_XAU_USD_1DAY_OBSERVATION_DATE_STRICTLY_BEFORE_ORIGIN_DATE",
        "geometry": {"L": 252, "P": 21, "D": 32},
        "geometry_reselected": False,
        "locked_window": "2023-01..2026-07",
        "N": 43,
        "pit_gate": pit,
        "target_reconciliation": f"{target_ok}/43",
        "rw_reconciliation": f"{rw_ok}/43",
        "future_information_violations": int(fv1 + fv2),
        "deterministic_max_abs_diff": maxdiff,
        "candidate_metrics": candidate,
        "rw_metrics": rw,
        "worst_ape_ratio_vs_rw": float(candidate["worst_APE_pct"] / rw["worst_APE_pct"]),
        "hard_gate_pass": hard,
        "performance_gate_pass": performance,
        "model_impact_pass": passed,
        "decision": decision,
        "post_result_retune": False,
        "raw_vendor_market_values_logged": False,
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
    }
    (OUT / "locked_replay_v7_daily_feature_pit_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"V7_PIT_GATE_PASS={str(pit['pass']).lower()}")
    print(f"V7_SAME_ORIGIN_DATE_FEATURE_USES={pit['same_origin_date_feature_uses']}")
    print(f"V7_TARGET_RECONCILIATION={target_ok}/43")
    print(f"V7_RW_RECONCILIATION={rw_ok}/43")
    print(f"V7_FUTURE_INFORMATION_VIOLATIONS={fv1 + fv2}")
    print(f"V7_DETERMINISTIC_MAX_ABS_DIFF={maxdiff:.12g}")
    print(f"V7_MAPE_PCT={candidate['MAPE_pct']:.9f}")
    print(f"RW_MAPE_PCT={rw['MAPE_pct']:.9f}")
    print(f"V7_MAE={candidate['MAE']:.9f}")
    print(f"RW_MAE={rw['MAE']:.9f}")
    print(f"V7_WORST_APE_PCT={candidate['worst_APE_pct']:.9f}")
    print(f"RW_WORST_APE_PCT={rw['worst_APE_pct']:.9f}")
    print(f"V7_HARD_GATE_PASS={str(hard).lower()}")
    print(f"V7_PERFORMANCE_GATE_PASS={str(performance).lower()}")
    print(f"V7_MODEL_IMPACT_PASS={str(passed).lower()}")
    print(f"V7_DECISION={decision}")
    print("POST_RESULT_RETUNE=NO")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
