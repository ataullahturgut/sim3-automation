from datetime import datetime, timezone

import pytest

from multi_expert_forecast import (
    AUTO_ENSEMBLE,
    AUTO_SELECTOR,
    EXPERT_ORDER,
    EXPERT_REGISTRY,
    MOMENTUM_EXPERT,
    PATCH_EXPERT,
    RW_EXPERT,
    SELECTOR_STATUS,
    TRACK_EARLY_INDICATIVE,
    TRACK_MONTH_END,
    VW_EXPERT,
    ExpertForecastRecord,
    executable_experts,
    momentum_3m_r1,
    rw_r1,
    selector_contract,
)


def test_manifest_v122_expert_set_is_exact_and_ordered():
    assert EXPERT_ORDER == (PATCH_EXPERT, VW_EXPERT, MOMENTUM_EXPERT, RW_EXPERT)
    assert set(EXPERT_REGISTRY) == set(EXPERT_ORDER)


def test_selector_and_ensemble_are_binding_off():
    assert SELECTOR_STATUS == "NOT_PROVEN_EXPERT_SELECTION_RULE"
    assert AUTO_SELECTOR == "OFF"
    assert AUTO_ENSEMBLE == "OFF"
    assert selector_contract() == {
        "selector_status": SELECTOR_STATUS,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    }


def test_only_patch_is_currently_forward_executable():
    assert executable_experts() == (PATCH_EXPERT,)
    assert EXPERT_REGISTRY[VW_EXPERT].execution_status == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert EXPERT_REGISTRY[MOMENTUM_EXPERT].execution_status == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"
    assert EXPERT_REGISTRY[RW_EXPERT].execution_status == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"


def test_rw_and_momentum_formulas_are_reproducible_but_source_agnostic():
    levels = [100.0, 110.0, 121.0, 133.1]
    assert rw_r1(levels) == pytest.approx(133.1)
    assert momentum_3m_r1(levels) == pytest.approx(146.41)


def _record(track=TRACK_MONTH_END, provenance=None):
    d = EXPERT_REGISTRY[PATCH_EXPERT]
    return ExpertForecastRecord(
        target_month="2026-10",
        forecast_origin=datetime(2026, 9, 30, 21, 20, tzinfo=timezone.utc),
        as_of=datetime(2026, 9, 30, 21, 21, tzinfo=timezone.utc),
        forecast_track=track,
        expert_id=d.expert_id,
        model_name=d.model_name,
        model_version=d.model_version,
        expert_role=d.expert_role,
        forecast_value=3500.0,
        unit="USD/oz",
        evidence_class="PROSPECTIVE_SHADOW",
        git_commit="abc",
        input_snapshot_ids=(1, 2),
        input_fingerprint="fingerprint",
        provenance={
            "canonical_authority": False,
            "selector_status": SELECTOR_STATUS,
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
            **(provenance or {}),
        },
    )


def test_month_end_and_early_indicative_are_separate_tracks():
    _record(TRACK_MONTH_END).validate()
    _record(TRACK_EARLY_INDICATIVE).validate()


def test_individual_expert_cannot_self_promote_to_canonical():
    with pytest.raises(ValueError, match="INDIVIDUAL_EXPERT_CANNOT_SELF_PROMOTE"):
        _record(provenance={"canonical_authority": True}).validate()


def test_selector_or_ensemble_cannot_be_enabled_in_record():
    with pytest.raises(ValueError, match="AUTO_SELECTOR_MUST_REMAIN_OFF"):
        _record(provenance={"auto_selector": "ON"}).validate()
    with pytest.raises(ValueError, match="AUTO_ENSEMBLE_MUST_REMAIN_OFF"):
        _record(provenance={"auto_ensemble": "ON"}).validate()
