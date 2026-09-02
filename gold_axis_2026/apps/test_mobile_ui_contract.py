from mobile_ui_contract import (
    FINAL_MOCKUP_CONTRACT,
    GECMIS_SECTION_ORDER,
    GORUNUM_SECTION_ORDER,
    SCENARIO_STATUS,
    TAHMIN_SECTION_ORDER,
    assert_no_action_mapping,
    classification_label,
    decision_view_state,
    evidence_badge,
    forecast_view_state,
    v2_layout_contract,
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


def test_final_v2_mockup_contract_is_frozen():
    contract = v2_layout_contract()
    assert contract["contract"] == FINAL_MOCKUP_CONTRACT == "APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2"
    assert contract["gorunum"] == GORUNUM_SECTION_ORDER
    assert contract["tahmin"] == TAHMIN_SECTION_ORDER
    assert contract["gecmis"] == GECMIS_SECTION_ORDER
    assert contract["scenario_status"] == SCENARIO_STATUS == "BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT"


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
