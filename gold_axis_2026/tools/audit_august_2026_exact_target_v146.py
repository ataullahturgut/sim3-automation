from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

import bocpd_return_successor_v1 as bocpd

ROOT = Path(__file__).resolve().parents[1]
ROLE_REPLAY = ROOT / "data_pipeline/audits/component_role_replays_v145/component_role_replays_v145.json"
WB_URL = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_world_bank_gold(path: Path) -> pd.Series:
    frame = pd.read_excel(path, sheet_name="Monthly Prices", skiprows=4)
    if "Unnamed: 0" not in frame or "Gold" not in frame:
        raise RuntimeError("World Bank monthly Gold columns not found")
    labels = frame["Unnamed: 0"].astype(str)
    valid = labels.str.fullmatch(r"\d{4}M\d{2}")
    dates = pd.to_datetime(labels[valid].str.replace("M", "-", regex=False) + "-01", format="%Y-%m-%d")
    values = pd.to_numeric(frame.loc[valid, "Gold"], errors="coerce")
    out = pd.Series(values.to_numpy(), index=dates, name="gold_monthly").dropna().sort_index()
    if out.index.has_duplicates or (out <= 0).any():
        raise RuntimeError("invalid World Bank Gold series")
    return out


def exact_prefix_check(core: pd.DataFrame, upstream: pd.Series) -> dict:
    joined = core[["gold_monthly"]].join(upstream.rename("upstream"), how="left")
    checked = joined.loc["2016-01-01":"2026-07-01"]
    if checked["upstream"].isna().any():
        raise RuntimeError("upstream prefix incomplete")
    differences = (checked["gold_monthly"].astype(float) - checked["upstream"].astype(float)).abs()
    # The current Pink Sheet workbook displays some older values rounded to whole
    # dollars.  The frozen artifact retains the originally retrieved precision.
    # A bounded display-precision check proves semantic identity without claiming
    # byte-for-byte numeric identity across mutable official workbook editions.
    mismatch = checked[differences > 0.50]
    return {
        "checked_rows": int(len(checked)),
        "exact_equal_rows": int((differences == 0).sum()),
        "within_display_precision_rows": int((differences <= 0.50).sum()),
        "max_abs_difference_usd": float(differences.max()),
        "mismatch_rows": int(len(mismatch)),
        "status": "PASS" if mismatch.empty else "FAIL",
        "claim": "SEMANTIC_IDENTITY_WITH_OFFICIAL_WORKBOOK_DISPLAY_PRECISION",
    }


def direction(value: float) -> int:
    return (value > 0) - (value < 0)


def build_evidence(workbook: Path, retrieved_at: str) -> dict:
    core = bocpd.load_core_monthly()
    wb = load_world_bank_gold(workbook)
    prefix = exact_prefix_check(core, wb)
    if prefix["status"] != "PASS":
        raise RuntimeError("frozen CORE5 and official World Bank identity mismatch")
    month = pd.Timestamp("2026-08-01")
    if month not in wb.index:
        raise RuntimeError("WORLD_BANK_GOLD_2026_08_NOT_FOUND")
    actual = float(wb.loc[month])

    extended = core.copy()
    extended.loc[month, "gold_monthly"] = actual
    extended = extended.sort_index()
    contract = bocpd.load_contract()
    returns = bocpd.monthly_log_returns(extended)
    prior = bocpd.fit_development_prior(returns, contract)
    expected = int(contract["hazard"]["expected_run_length_months"])
    replay_returns = returns.loc[pd.Timestamp(contract["windows"]["development_start"]):month]
    first = bocpd.run_bocpd(replay_returns, prior, expected, contract)
    second = bocpd.run_bocpd(replay_returns, prior, expected, contract)
    hash1 = bocpd.canonical_hash(first, prior, expected)
    hash2 = bocpd.canonical_hash(second, prior, expected)
    bocpd.assert_prefix_invariance(replay_returns, prior, expected, contract, [pd.Timestamp("2026-07-01"), month])
    if hash1 != hash2:
        raise RuntimeError("BOCPD_DETERMINISM_FAIL")

    replay = json.loads(ROLE_REPLAY.read_text(encoding="utf-8"))
    july_actual = float(core.loc[pd.Timestamp("2026-07-01"), "gold_monthly"])
    realized_change = actual - july_actual
    h1 = {}
    for engine, row in sorted(replay["h1_2026_08"].items()):
        forecast = float(row["forecast"])
        h1[engine] = {
            "forecast": forecast,
            "actual": actual,
            "absolute_error": abs(forecast - actual),
            "ape_percent": abs(forecast - actual) / actual * 100.0,
            "direction_hit": direction(forecast - july_actual) == direction(realized_change),
            "origin_month": row["origin_month"],
            "target_month": row["target_month"],
            "future_information_violations": int(row["future_information_violations"]),
        }

    last = first.loc[month]
    return {
        "audit_id": "GOLD_CONTROL_AUGUST_2026_EXACT_TARGET_V146",
        "status": "PASS",
        "source_identity": "WORLD_BANK_PINK_SHEET_MONTHLY_GOLD_USD_PER_TROY_OUNCE",
        "source_url": WB_URL,
        "source_payload_sha256": sha256(workbook),
        "retrieved_at": retrieved_at,
        "available_as_of": retrieved_at,
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "prospective_claim": False,
        "target_month": "2026-08",
        "actual_value": actual,
        "unit": "USD_PER_TROY_OUNCE",
        "aggregation": "WORLD_BANK_PINK_SHEET_MONTHLY_GOLD",
        "frozen_core5_prefix_identity": prefix,
        "frozen_source_overwritten": False,
        "database_writes": "NONE",
        "bocpd": {
            "engine_id": bocpd.SUCCESSOR_ID,
            "status": "PASS",
            "state": str(last["state"]),
            "log_return": float(last["log_return"]),
            "map_run": int(last["map_run"]),
            "p_run0": float(last["p_run0"]),
            "determinism_sha256": hash1,
            "deterministic_rerun": "PASS",
            "prefix_invariance": "PASS",
            "model_or_threshold_change": "NONE",
            "future_information_violations": 0,
        },
        "h1_2026_08": h1,
        "no_tuning_confirmation": True,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "canonical_forecast_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True, type=Path)
    parser.add_argument("--retrieved-at", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    evidence = build_evidence(args.workbook, args.retrieved_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STATUS={evidence['status']}")
    print(f"ACTUAL_2026_08={evidence['actual_value']}")
    print(f"BOCPD_STATE={evidence['bocpd']['state']}")
    print(f"DETERMINISM_SHA256={evidence['bocpd']['determinism_sha256']}")


if __name__ == "__main__":
    main()
