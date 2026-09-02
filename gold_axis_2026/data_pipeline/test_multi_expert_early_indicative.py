from datetime import datetime, timezone

from multi_expert_early_indicative import (
    LEVEL_SOURCE_BLOCK,
    OVERALL_BLOCK,
    PATCH_BLOCK,
    VW_BLOCK,
    overall_status,
    readiness,
    report,
)
from multi_expert_forecast import (
    AUTO_ENSEMBLE,
    AUTO_SELECTOR,
    EXPERT_ORDER,
    MOMENTUM_EXPERT,
    PATCH_EXPERT,
    RW_EXPERT,
    SELECTOR_STATUS,
    TRACK_EARLY_INDICATIVE,
    VW_EXPERT,
)


def test_all_four_experts_are_present_and_fail_closed():
    rows = readiness(datetime(2026, 9, 2, 16, 0, tzinfo=timezone.utc))
    assert tuple(x.expert_id for x in rows) == EXPERT_ORDER
    assert all(x.forecast_track == TRACK_EARLY_INDICATIVE for x in rows)
    assert all(x.executable is False for x in rows)
    assert all(x.write_allowed is False for x in rows)
    status = {x.expert_id: x.status for x in rows}
    assert status[PATCH_EXPERT] == PATCH_BLOCK
    assert status[VW_EXPERT] == VW_BLOCK
    assert status[MOMENTUM_EXPERT] == LEVEL_SOURCE_BLOCK
    assert status[RW_EXPERT] == LEVEL_SOURCE_BLOCK
    assert overall_status(rows) == OVERALL_BLOCK


def test_report_never_claims_canonical_or_database_write():
    payload = report(datetime(2026, 9, 2, 16, 0, tzinfo=timezone.utc))
    assert payload["overall_status"] == OVERALL_BLOCK
    assert payload["forecast_track"] == TRACK_EARLY_INDICATIVE
    assert payload["selector_status"] == SELECTOR_STATUS
    assert payload["auto_selector"] == AUTO_SELECTOR == "OFF"
    assert payload["auto_ensemble"] == AUTO_ENSEMBLE == "OFF"
    assert payload["database_writes"] == "NONE"
    assert payload["canonical_forecast_contract_write"] == "NONE"
