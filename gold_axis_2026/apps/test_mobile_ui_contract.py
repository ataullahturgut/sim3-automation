from mobile_ui_contract import (
    AUTO_ENSEMBLE_STATUS,
    AUTO_SELECTOR_STATUS,
    EARLY_INDICATIVE_TRACK,
    EXPERT_DISPLAY_ORDER,
    EXPERT_SELECTION_STATUS,
    FINAL_MOCKUP_CONTRACT,
    GECMIS_SECTION_ORDER,
    GORUNUM_SECTION_ORDER,
    MONTH_END_TRACK,
    SCENARIO_STATUS,
    TAHMIN_SECTION_ORDER,
    assert_no_action_mapping,
    classification_label,
    decision_view_state,
    evidence_badge,
    expert_display_state,
    forecast_view_state,
    monthly_intramonth_relation,
    v2_layout_contract,
)


def test_empty_decision_is_fail_closed():
    state = decision_view_state(None)
    assert state.title == "KANONİK KARAR YOK"


def test_monthly_shadow_context_is_visible_but_not_promoted_to_decision():
    context = {
        "context_only": True,
        "evidence_class": "LATE_BOOTSTRAP_SHADOW_CONTEXT",
        "monthly_direction_3m": "UP",
        "fast_state": "YAYIMLANMADI",
        "slow_state": "YAYIMLANMADI",
    }
    state = decision_view_state(context)
    assert state.title == "KANONİK KARAR YOK"
    assert "SHADOW CONTEXT" in state.subtitle
    assert evidence_badge(context["evidence_class"]) == ("SHADOW CONTEXT", "shadow")
    assert monthly_intramonth_relation(context) == "INTRAMONTH TEYİT HENÜZ YAYIMLANMADI"


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


def test_noncanonical_expert_cannot_fill_canonical_hero():
    try:
        forecast_view_state({
            "evidence_class": "PROSPECTIVE_SHADOW",
            "target_month": "2026-10",
            "canonical_authority": False,
        })
    except RuntimeError as exc:
        assert "NONCANONICAL_EXPERT" in str(exc)
    else:
        raise AssertionError("individual expert must not become canonical hero")


def test_unproven_position_language_is_rejected():
    for text in ["Pozisyonu koru", "POZİSYONU KORU", "BUY", "SELL", "HOLD_LONG"]:
        try:
            assert_no_action_mapping(text)
        except RuntimeError as exc:
            assert "NOT_PROVEN_POSITION_MAPPING_UI_VIOLATION" in str(exc)
        else:
            raise AssertionError(f"position action must be rejected: {text}")


def test_classification_labels_are_descriptive_not_actions():
    assert classification_label("ALIGNED_UP") == "YUKARI UYUMLU"
    assert classification_label("ALIGNED_DOWN") == "AŞAĞI UYUMLU"
    assert classification_label("CONFLICT") == "ÇELİŞKİ"


def test_final_v2_mockup_contract_is_frozen_with_v122_expert_policy():
    contract = v2_layout_contract()
    assert contract["contract"] == FINAL_MOCKUP_CONTRACT == "APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2"
    assert contract["gorunum"] == GORUNUM_SECTION_ORDER
    assert contract["tahmin"] == TAHMIN_SECTION_ORDER
    assert contract["gecmis"] == GECMIS_SECTION_ORDER
    assert contract["scenario_status"] == SCENARIO_STATUS == "BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT"
    assert contract["expert_selection_status"] == EXPERT_SELECTION_STATUS == "NOT_PROVEN_EXPERT_SELECTION_RULE"
    assert contract["auto_selector"] == AUTO_SELECTOR_STATUS == "OFF"
    assert contract["auto_ensemble"] == AUTO_ENSEMBLE_STATUS == "OFF"
    assert contract["expert_order"] == EXPERT_DISPLAY_ORDER == (
        "CAUSAL_PATCH", "VW_MIDAS_MSVR", "MOMENTUM_3M", "RANDOM_WALK"
    )
    assert contract["month_end_track"] == MONTH_END_TRACK == "MONTH_END_EXPERT"
    assert contract["early_indicative_track"] == EARLY_INDICATIVE_TRACK == "EARLY_INDICATIVE"


def test_empty_expert_states_do_not_invent_forecasts_or_winner():
    patch = expert_display_state("CAUSAL_PATCH", [])
    vw = expert_display_state("VW_MIDAS_MSVR", [])
    mom = expert_display_state("MOMENTUM_3M", [])
    rw = expert_display_state("RANDOM_WALK", [])
    assert patch["forecast_value"] is None
    assert patch["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert vw["status"] == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert mom["status"] == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"
    assert rw["status"] == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"


def test_monthly_prior_intramonth_conflict_is_allowed_state():
    d = {"monthly_direction_3m": "UP", "fast_state": "DOWN", "slow_state": "DOWN"}
    assert monthly_intramonth_relation(d) == "MONTHLY_PRIOR_INTRAMONTH_CONFLICT_ALLOWED"


def test_gorunum_final_section_order():
    assert GORUNUM_SECTION_ORDER == (
        "SİNYAL ÖZETİ",
        "MODEL YÖNÜ (AYLIK)",
        "FAST / SLOW TEYİDİ",
        "RİSK SEVİYESİ",
        "SİNYAL ZAMAN ÇİZELGESİ",
        "EMERGENCY DURUMU",
        "SİSTEM YORUMU",
    )


def test_tahmin_and_gecmis_final_section_order():
    assert TAHMIN_SECTION_ORDER[0] == "GELECEK AY TAHMİNİ"
    assert TAHMIN_SECTION_ORDER[1] == "GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI"
    assert "SENARYOLAR" in TAHMIN_SECTION_ORDER
    assert GECMIS_SECTION_ORDER == (
        "ÖZET METRİKLER",
        "TAHMİN PERFORMANSI",
        "HATA / KARAR ZAMAN ÇİZELGESİ",
        "SEÇİLMİŞ GEÇMİŞ KAYITLAR",
    )
