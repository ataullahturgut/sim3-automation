from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v170_research/contracts/v170a_free_public_data_acquisition_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v170a_research"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V170_FORECAST_SCORING":
        raise RuntimeError("V170A_CONTRACT_NOT_FROZEN")
    forbidden = set(c["forbidden_in_v170a"])
    required = {"forecast_target_join", "forecast_model_fit", "forecast_scoring", "feature_selection_using_outcomes", "2025_2026_performance_inspection", "production_writes"}
    if not required.issubset(forbidden):
        raise RuntimeError("V170A_GOVERNANCE_LOCK_FAIL")
    return c


def fetch_dataset(spec: dict, start: str, end: str) -> pd.DataFrame:
    params = {
        "cftc_contract_market_code": spec["contract_market_code"],
        "$where": f"report_date_as_yyyy_mm_dd between '{start}T00:00:00.000' and '{end}T23:59:59.999'",
        "$order": "report_date_as_yyyy_mm_dd ASC",
        "$limit": "1000",
    }
    r = requests.get(spec["endpoint"], params=params, timeout=60, headers={"User-Agent": "Gold-Control-research/1.0"})
    r.raise_for_status()
    payload = r.json()
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"V170A_EMPTY_DATASET:{spec['dataset_id']}")
    df = pd.DataFrame(payload)
    if "report_date_as_yyyy_mm_dd" not in df.columns:
        raise RuntimeError(f"V170A_REPORT_DATE_MISSING:{spec['dataset_id']}")
    if "cftc_contract_market_code" not in df.columns:
        raise RuntimeError(f"V170A_MARKET_CODE_MISSING:{spec['dataset_id']}")
    df["report_date_as_yyyy_mm_dd"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"], errors="raise")
    df = df.sort_values("report_date_as_yyyy_mm_dd").reset_index(drop=True)
    if not (df["cftc_contract_market_code"].astype(str) == str(spec["contract_market_code"])).all():
        raise RuntimeError(f"V170A_MARKET_CODE_CONTAMINATION:{spec['dataset_id']}")
    if df["report_date_as_yyyy_mm_dd"].duplicated().any():
        raise RuntimeError(f"V170A_DUPLICATE_REPORT_DATE:{spec['dataset_id']}")
    # Weekly COT should yield far more than monthly support over 3.5 years.
    if len(df) < 150:
        raise RuntimeError(f"V170A_WEEKLY_SUPPORT_TOO_SMALL:{spec['dataset_id']}:{len(df)}")
    df["available_date_conservative"] = df["report_date_as_yyyy_mm_dd"] + pd.Timedelta(days=6)
    return df


def main() -> None:
    c = load_contract()
    OUT.mkdir(parents=True, exist_ok=True)
    start, end = c["capture_window"]
    manifest = {
        "contract_id": c["contract_id"],
        "status": "SUCCESS_DATA_CAPTURE_ONLY_NO_FORECAST_SCORING",
        "capture_window": [start, end],
        "pit_clock_rule": c["pit_clock_rule_for_later_modeling"],
        "datasets": {},
        "forecast_scoring_performed": False,
    }
    for name, spec in c["sources"].items():
        df = fetch_dataset(spec, start, end)
        path = OUT / f"v170a_{name}_gold_weekly_raw.csv"
        # Stable column order makes the captured snapshot hash reproducible.
        cols = ["report_date_as_yyyy_mm_dd", "available_date_conservative"] + sorted([x for x in df.columns if x not in {"report_date_as_yyyy_mm_dd", "available_date_conservative"}])
        df[cols].to_csv(path, index=False, date_format="%Y-%m-%d")
        manifest["datasets"][name] = {
            "dataset_id": spec["dataset_id"],
            "endpoint": spec["endpoint"],
            "rows": int(len(df)),
            "min_report_date": df["report_date_as_yyyy_mm_dd"].min().strftime("%Y-%m-%d"),
            "max_report_date": df["report_date_as_yyyy_mm_dd"].max().strftime("%Y-%m-%d"),
            "columns": list(df.columns),
            "csv_file": path.name,
            "csv_sha256": sha256_file(path),
        }
    (OUT / "v170a_free_public_cftc_capture_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
