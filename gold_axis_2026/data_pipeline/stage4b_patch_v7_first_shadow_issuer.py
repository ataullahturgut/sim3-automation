from __future__ import annotations

"""Manifest v1.22 compatibility shim for the retired single-Patch issuer.

The original executable/model-building implementation is preserved in
``stage4b_patch_v7_runner_core.py`` solely so the governed Multi-Expert Patch
issuer can reuse the proven PIT-safe forecast construction and snapshot helper.

This legacy entry point MUST NOT issue a canonical monthly forecast. Manifest
v1.22 requires separate expert outputs first and leaves expert selection as
NOT_PROVEN_EXPERT_SELECTION_RULE. Consequently ``issue-if-eligible`` fails
closed before reading credentials, touching the database, or building a model.
"""

import argparse
from datetime import datetime, timezone

import stage4b_patch_v7_runner_core as core


LEGACY_CANONICAL_ISSUER_STATUS = (
    "BLOCKED_MANIFEST_V1_22_USE_MULTI_EXPERT_MONTH_END_ISSUER"
)
REPLACEMENT_ISSUER = "stage4b_multi_expert_patch_v7_month_end_issuer.py"
ARCHITECTURE_CONTRACT = "MANIFEST_V1_22_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER"
SELECTOR_STATUS = "NOT_PROVEN_EXPERT_SELECTION_RULE"
AUTO_SELECTOR = "OFF"
AUTO_ENSEMBLE = "OFF"

# Read-only / model-construction compatibility exports used by the governed
# Multi-Expert Patch issuer. Deliberately do NOT re-export persist_shadow().
CONTRACT = core.CONTRACT
V7_EVIDENCE = core.V7_EVIDENCE
SCHEMA_EVIDENCE = core.SCHEMA_EVIDENCE
WRITER_EVIDENCE = core.WRITER_EVIDENCE
MODEL_NAME = core.MODEL_NAME
MODEL_VERSION = core.MODEL_VERSION
MODEL_ROLE = core.MODEL_ROLE
EVIDENCE_CLASS = core.EVIDENCE_CLASS
FIRST_ORIGIN_DATE = core.FIRST_ORIGIN_DATE
FIRST_TARGET = core.FIRST_TARGET
NY = core.NY

env = core.env
git_sha = core.git_sha
static_gates = core.static_gates
eligibility = core.eligibility
request_json = core.request_json
fetch_xau_daily = core.fetch_xau_daily
fetch_hourly_anchor = core.fetch_hourly_anchor
fred_month_mean_asof = core.fred_month_mean_asof
fetch_nasdaq_monthly = core.fetch_nasdaq_monthly
fetch_gpr_august = core.fetch_gpr_august
training_samples_forward = core.training_samples_forward
pack_npz = core.pack_npz
build_forecast = core.build_forecast
insert_snapshot = core.insert_snapshot


def preflight(now_utc: datetime) -> int:
    """Prove the retired path is blocked without making persistent writes."""
    static_gates()
    _eligible, eligibility_state = eligibility(now_utc)
    print(f"LEGACY_CANONICAL_ISSUER_STATUS={LEGACY_CANONICAL_ISSUER_STATUS}")
    print(f"REPLACEMENT_ISSUER={REPLACEMENT_ISSUER}")
    print(f"ARCHITECTURE_CONTRACT={ARCHITECTURE_CONTRACT}")
    print(f"SELECTOR_STATUS={SELECTOR_STATUS}")
    print(f"AUTO_SELECTOR={AUTO_SELECTOR}")
    print(f"AUTO_ENSEMBLE={AUTO_ENSEMBLE}")
    print(f"ELIGIBILITY_STATE={eligibility_state}")
    print("CANONICAL_FORECAST_CONTRACT_WRITE=FORBIDDEN")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_VALUE_LOGGED=NO")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    return 0


def issue_if_eligible(now_utc: datetime) -> int:
    """Fail closed before credentials, DB access, model build, or snapshot writes."""
    del now_utc
    raise RuntimeError(
        f"{LEGACY_CANONICAL_ISSUER_STATUS}: direct single-Patch issuance into "
        "monthly_forecast_contracts is forbidden by manifest v1.22; use "
        f"{REPLACEMENT_ISSUER}, which writes Patch only as MONTH_END_EXPERT."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["preflight", "issue-if-eligible"],
        required=True,
    )
    args = parser.parse_args()
    now_utc = datetime.now(timezone.utc)
    return preflight(now_utc) if args.mode == "preflight" else issue_if_eligible(now_utc)


if __name__ == "__main__":
    raise SystemExit(main())
