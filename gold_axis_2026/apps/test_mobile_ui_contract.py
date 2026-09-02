from mobile_ui_contract import (
    assert_no_action_mapping,
    decision_view_state,
    evidence_badge,
    forecast_view_state,
)


def test_empty_decision_is_fail_closed():
    state = decision_view_state(None)
    assert state.title == "KANONİK KARAR YOK"


def test_empty_forecast_is_fail_closed():
    state = forecast_view_state(None)
    assert state.title == "TAHMİN HENÜZ YAYIMLANMADI"
    assert state.subtitle == "NOT_ISSUED_IN_CANONICAL_LEDGER"


def test_prospective_shadow_badge_is_explicit():
    label, tone = evidence_badge("PROSPECTIVE_SHADOW")
    assert label == "PROSPECTIVE SHADOW"
    assert tone == "shadow"


def test_historical_replay_cannot_be_current_forecast():
    try:
        forecast_view_state({"evidence_class": "HISTORICAL_REPLAY", "target_month": "2026-10"})
    except RuntimeError as exc:
        assert "NOT_DISPLAY_ELIGIBLE" in str(exc)
    else:
        raise AssertionError("historical replay must not be display-eligible current forecast")


def test_unproven_position_language_is_rejected():
    try:
        assert_no_action_mapping("Pozisyonu koru")
    except RuntimeError as exc:
        assert "NOT_PROVEN_POSITION_MAPPING_UI_VIOLATION" in str(exc)
    else:
        raise AssertionError("position action must be rejected")
