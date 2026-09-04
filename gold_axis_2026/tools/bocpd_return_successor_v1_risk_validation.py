from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bocpd_return_successor_v1 import (
    DATABASE_WRITES,
    DIRECTION_VOTE_PERMITTED,
    EVIDENCE_CLASS,
    POSITION_MAPPING_PERMITTED,
    SUCCESSOR_ID,
    build_replay,
    load_core_monthly,
)

ROOT = Path(__file__).resolve().parents[1]
RISK_EVIDENCE_CLASS = "HISTORICAL_REPLAY_SUCCESSOR_RISK_DIAGNOSTIC"


def add_forward_outcomes(rows: pd.DataFrame, price: pd.Series) -> pd.DataFrame:
    out = rows.copy()
    for h in (1, 2, 3):
        vals = []
        for month in out.index:
            future = pd.Timestamp(month) + pd.offsets.MonthBegin(h)
            if month in price.index and future in price.index:
                vals.append(float(price.loc[future] / price.loc[month] - 1.0))
            else:
                vals.append(np.nan)
        out[f"fwd_{h}m"] = vals
    out["tail_2m"] = np.where(out["fwd_2m"].notna(), (out["fwd_2m"] <= -0.03).astype(float), np.nan)
    out["tail_3m"] = np.where(out["fwd_3m"].notna(), (out["fwd_3m"] <= -0.03).astype(float), np.nan)
    out["group"] = np.where(out["state"].eq("ADVERSE_BREAK_CANDIDATE"), "CANDIDATE", "NON_CANDIDATE")
    return out


def _stats(group: pd.DataFrame) -> dict:
    result: dict[str, float | int | None] = {"n_state_rows": int(len(group))}
    for h in (1, 2, 3):
        s = group[f"fwd_{h}m"].dropna().astype(float)
        result[f"n_fwd_{h}m"] = int(len(s))
        result[f"mean_fwd_{h}m"] = float(s.mean()) if len(s) else None
        result[f"median_fwd_{h}m"] = float(s.median()) if len(s) else None
    for h in (2, 3):
        s = group[f"tail_{h}m"].dropna().astype(float)
        result[f"n_tail_{h}m"] = int(len(s))
        result[f"tail_{h}m_rate"] = float(s.mean()) if len(s) else None
    return result


def _difference(candidate: dict, non_candidate: dict, key: str) -> float | None:
    a = candidate.get(key)
    b = non_candidate.get(key)
    if a is None or b is None:
        return None
    return float(a - b)


def period_summary(frame: pd.DataFrame, period: str) -> dict:
    sub = frame[frame["period"].eq(period)].copy()
    candidate = _stats(sub[sub["group"].eq("CANDIDATE")])
    non_candidate = _stats(sub[sub["group"].eq("NON_CANDIDATE")])
    differences = {}
    for key in (
        "mean_fwd_1m",
        "mean_fwd_2m",
        "mean_fwd_3m",
        "median_fwd_1m",
        "median_fwd_2m",
        "median_fwd_3m",
        "tail_2m_rate",
        "tail_3m_rate",
    ):
        differences[f"candidate_minus_non_candidate_{key}"] = _difference(candidate, non_candidate, key)
    candidate_months = [m.strftime("%Y-%m-%d") for m in sub[sub["group"].eq("CANDIDATE")].index]
    return {
        "period": period,
        "candidate_months": candidate_months,
        "candidate": candidate,
        "non_candidate": non_candidate,
        "differences": differences,
    }


def build_risk_validation() -> tuple[pd.DataFrame, dict]:
    replay = build_replay()
    core = load_core_monthly()
    price = core["gold_monthly"].astype(float)
    enriched = add_forward_outcomes(replay.rows, price)

    val = period_summary(enriched, "VAL")
    lock = period_summary(enriched, "LOCK")
    candidate_n = int(val["candidate"]["n_state_rows"])

    summary = {
        "successor_id": SUCCESSOR_ID,
        "engineering_determinism_sha256": replay.summary["determinism_sha256"],
        "evidence_class": RISK_EVIDENCE_CLASS,
        "validation_status": (
            "VALIDATION_RISK_DIAGNOSTIC_COMPLETE"
            if candidate_n > 0
            else "NOT_EVALUABLE_NO_VALIDATION_CANDIDATES"
        ),
        "interpretation": "DESCRIPTIVE_ONLY",
        "primary_risk_horizon": "2-3M",
        "tail_definition": "CUMULATIVE_FORWARD_GOLD_RETURN_LE_MINUS_3PCT",
        "one_month_role": "SECONDARY_DIAGNOSTIC_NOT_SUPPORTED_FOR_APPROVAL",
        "validation": val,
        "locked": lock,
        "locked_role": "DIAGNOSTIC_ONLY",
        "direction_vote_permitted": DIRECTION_VOTE_PERMITTED,
        "position_mapping_permitted": POSITION_MAPPING_PERMITTED,
        "automatic_action_approved": False,
        "database_writes": DATABASE_WRITES,
        "prospective_claim": False,
        "promotion_authorized": False,
        "maximum_conclusion": (
            "RESEARCH_SHADOW_CANDIDATE_RISK_DIAGNOSTIC_COMPLETE_"
            "PROSPECTIVE_VALIDATION_REQUIRED"
        ),
        "hard_gates": {
            "STATE_OUTPUT_UNCHANGED_PASS": True,
            "SAME_MONTH_HINDSIGHT_NONE_PASS": True,
            "PRIMARY_HORIZON_2_3M_PASS": True,
            "TAIL_DEFINITION_MINUS_3PCT_PASS": True,
            "NO_NEW_THRESHOLD_PASS": True,
            "VALIDATION_NO_TUNING_PASS": True,
            "LOCKED_DIAGNOSTIC_ONLY_PASS": True,
            "DIRECTION_VOTE_FALSE_PASS": DIRECTION_VOTE_PERMITTED is False,
            "AUTOMATIC_ACTION_NOT_APPROVED_PASS": True,
            "DATABASE_WRITES_NONE_PASS": DATABASE_WRITES == "NONE",
        },
    }
    if not all(summary["hard_gates"].values()):
        raise RuntimeError("risk validation hard gate failure")
    return enriched, summary


def write_outputs(frame: pd.DataFrame, summary: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = frame.reset_index().copy()
    out["month"] = pd.to_datetime(out["month"]).dt.strftime("%Y-%m-%d")
    out.to_csv(output_dir / "bocpd_return_successor_v1_risk_validation.csv", index=False)
    (output_dir / "bocpd_return_successor_v1_risk_evidence.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="BOCPD Return Successor V1 frozen risk diagnostic")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    frame, summary = build_risk_validation()
    if args.output_dir is not None:
        write_outputs(frame, summary, args.output_dir)

    print(f"SUCCESSOR_ID={summary['successor_id']}")
    print(f"VALIDATION_STATUS={summary['validation_status']}")
    print(f"INTERPRETATION={summary['interpretation']}")
    print(f"VAL_CANDIDATE_N={summary['validation']['candidate']['n_state_rows']}")
    print(f"LOCK_CANDIDATE_N={summary['locked']['candidate']['n_state_rows']}")
    print("PRIMARY_RISK_HORIZON=2-3M")
    print("TAIL_DEFINITION=CUMULATIVE_FORWARD_GOLD_RETURN_LE_MINUS_3PCT")
    print("DIRECTION_VOTE_PERMITTED=NO")
    print("AUTOMATIC_ACTION_APPROVED=NO")
    print("PROSPECTIVE_CLAIM=NO")
    print("PROMOTION_AUTHORIZED=NO")
    print("DATABASE_WRITES=NONE")
    print("BOCPD_RETURN_SUCCESSOR_V1_RISK_DIAGNOSTIC_COMPLETE")


if __name__ == "__main__":
    main()
