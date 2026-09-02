from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1" / "prospective_monthly_level_v5_source_evidence.json"
URL = "https://api.twelvedata.com/time_series"
CONTRACT = ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_MONTHLY_LEVEL_INPUT_CHANGE_CONTROL_V5_2026-09-02.md"

PROBES = [
    ("2011-01", "2011-01-03 00:00:00", "2011-01-31 23:59:59"),
    ("2016-01", "2016-01-04 00:00:00", "2016-01-31 23:59:59"),
    ("2020-01", "2020-01-02 00:00:00", "2020-01-31 23:59:59"),
    ("2023-01", "2023-01-03 00:00:00", "2023-01-31 23:59:59"),
    ("2026-01", "2026-01-02 00:00:00", "2026-01-31 23:59:59"),
]


def main() -> int:
    contract = CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_V5_SOURCE_RESULT" not in contract:
        raise RuntimeError("V5_CONTRACT_NOT_FROZEN")
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY_NOT_SET")

    session = requests.Session()
    results = []
    for label, start, end in PROBES:
        status = None
        api_code = None
        accessible = False
        row_count = 0
        error_class = None
        try:
            response = session.get(
                URL,
                params={
                    "symbol": "XAU/USD",
                    "interval": "1h",
                    "start_date": start,
                    "end_date": end,
                    "timezone": "America/New_York",
                    "outputsize": 1000,
                    "order": "ASC",
                    "format": "JSON",
                },
                headers={
                    "Authorization": f"apikey {key}",
                    "User-Agent": "Gold-Control-Patch-V5-Entitlement-Audit/1.0",
                },
                timeout=(20, 180),
            )
            status = int(response.status_code)
            try:
                payload = response.json()
            except Exception:
                payload = None
            if isinstance(payload, dict):
                api_code = payload.get("code")
                values = payload.get("values") or []
                row_count = int(len(values)) if isinstance(values, list) else 0
                accessible = bool(
                    response.status_code == 200
                    and payload.get("status") != "error"
                    and row_count > 0
                )
            else:
                error_class = "NON_JSON_RESPONSE"
        except Exception as exc:
            error_class = type(exc).__name__
        results.append(
            {
                "probe_month": label,
                "http_status": status,
                "api_code": api_code,
                "accessible": accessible,
                "returned_rows": row_count,
                "error_class": error_class,
            }
        )

    required_start_accessible = bool(results[0]["accessible"])
    evidence = {
        "candidate_id": "CAUSAL_PATCH_R1_REPRO_V1_4_XAU_MONTHLY_LEVEL_ORIGIN_SAFE",
        "candidate_series_id": "PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V5",
        "evidence_class": "SOURCE_INPUT_SEMANTIC_AUDIT",
        "prospective_claim": False,
        "parent_failed_workflow_run": 33617695639,
        "required_history_start": "2011-02",
        "provider_access_probes": results,
        "required_start_accessible": required_start_accessible,
        "source_bridge_pass": False,
        "model_impact_run": "SKIPPED_SOURCE_GATE_NOT_PROVEN",
        "decision": "BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_NOT_PROVEN",
        "failure_semantic": (
            "REQUIRED_HOURLY_HISTORY_NOT_ACCESSIBLE_UNDER_CURRENT_PROVIDER_ENTITLEMENT"
            if not required_start_accessible
            else "V5_FULL_HISTORY_FETCH_NOT_PROVEN"
        ),
        "thresholds_relaxed": False,
        "source_substituted": False,
        "raw_vendor_market_values_logged": False,
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "audited_at": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    model_evidence = {
        "candidate_id": evidence["candidate_id"],
        "evidence_class": "HISTORICAL_REPLAY_MODEL_IMPACT",
        "prospective_claim": False,
        "source_gate": evidence["decision"],
        "model_impact_run": "SKIPPED_SOURCE_GATE_NOT_PROVEN",
        "model_impact_pass": False,
        "decision": "PATCH_R1_V5_MONTHLY_LEVEL_MODEL_IMPACT_FAIL_NO_RETUNE",
        "post_result_retune": False,
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
        "database_write": "NONE",
        "raw_vendor_market_values_logged": False,
    }
    (OUT.parent / "locked_replay_v5_monthly_level_evidence.json").write_text(
        json.dumps(model_evidence, indent=2), encoding="utf-8"
    )

    print(f"V5_REQUIRED_START_ACCESSIBLE={str(required_start_accessible).lower()}")
    for row in results:
        print(
            "V5_PROBE=" + row["probe_month"]
            + " HTTP=" + str(row["http_status"])
            + " API_CODE=" + str(row["api_code"])
            + " ACCESSIBLE=" + str(row["accessible"]).lower()
            + " ROWS=" + str(row["returned_rows"])
        )
    print("V5_SOURCE_DECISION=BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_NOT_PROVEN")
    print("V5_MODEL_IMPACT=SKIPPED_SOURCE_GATE_NOT_PROVEN")
    print("THRESHOLDS_RELAXED=NO")
    print("SOURCE_SUBSTITUTED=NO")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
