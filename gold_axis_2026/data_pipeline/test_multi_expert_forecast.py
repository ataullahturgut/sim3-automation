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
    momentum_3m_r2_source_bound,
    rw_r1,
    rw_r2_source_bound,
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


def test_patch_rw_and_momentum_are_forward_executable_after_frozen_v2_source_pass():
    assert executable_experts() == (PATCH_EXPERT, MOMENTUM_EXPERT, RW_EXPERT)
    assert EXPERT_REGISTRY[VW_EXPERT].execution_status == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert EXPERT_REGISTRY[MOMENTUM_EXPERT].execution_status == "EXECUTABLE_FORWARD_EXPERT"
    assert EXPERT_REGISTRY[RW_EXPERT].execution_status == "EXECUTABLE_FORWARD_EXPERT"
    assert EXPERT_REGISTRY[MOMENTUM_EXPERT].model_version == "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
    assert EXPERT_REGISTRY[RW_EXPERT].model_version == "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"


def test_rw_and_momentum_formulas_preserve_r1_math_under_explicit_v2_source_binding():
    levels = [100.0, 110.0, 121.0, 133.1]
    assert rw_r1(levels) == pytest.approx(133.1)
    assert momentum_3m_r1(levels) == pytest.approx(146.41)
    assert rw_r2_source_bound(levels) == pytest.approx(rw_r1(levels))
    assert momentum_3m_r2_source_bound(levels) == pytest.approx(momentum_3m_r1(levels))


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
