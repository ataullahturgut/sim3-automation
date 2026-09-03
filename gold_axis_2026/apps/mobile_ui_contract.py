from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_CLASSIFICATIONS = {
    "MACRO_DOWN_RISK",
    "REVERSAL_RISK_DOWN",
    "REVERSAL_RISK_UP",
    "ALIGNED_UP",
    "ALIGNED_DOWN",
    "CONFLICT",
    "UNRESOLVED_MIXED",
}

PROHIBITED_ACTION_TERMS = {
    "BUY", "SELL", "HOLD", "HOLD_LONG", "EXIT", "REDUCE",
    "POZİSYONU KORU", "POZISYONU KORU", " AL ", " SAT ",
}

GORUNUM_SECTION_ORDER = (
    "SİNYAL ÖZETİ",
    "MODEL YÖNÜ (AYLIK)",
    "FAST / SLOW TEYİDİ",
    "RİSK SEVİYESİ",
    "SİNYAL ZAMAN ÇİZELGESİ",
    "EMERGENCY DURUMU",
    "SİSTEM YORUMU",
)

TAHMIN_SECTION_ORDER = (
    "GELECEK AY TAHMİNİ",
    "GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI",
    "SENARYOLAR",
    "MEVCUT FİYATA GÖRE FARK",
    "MODEL PERFORMANSI",
)

GECMIS_SECTION_ORDER = (
    "ÖZET METRİKLER",
    "TAHMİN PERFORMANSI",
    "HATA / KARAR ZAMAN ÇİZELGESİ",
    "SEÇİLMİŞ GEÇMİŞ KAYITLAR",
)

FINAL_MOCKUP_CONTRACT = "APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2"
SCENARIO_STATUS = "BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT"
POSITION_STATUS = "NOT_PROVEN_POSITION_MAPPING"

EXPERT_SELECTION_STATUS = "NOT_PROVEN_EXPERT_SELECTION_RULE"
AUTO_SELECTOR_STATUS = "OFF"
AUTO_ENSEMBLE_STATUS = "OFF"
MONTH_END_TRACK = "MONTH_END_EXPERT"
EARLY_INDICATIVE_TRACK = "EARLY_INDICATIVE"
CONTEXT_EVIDENCE_CLASS = "LATE_BOOTSTRAP_SHADOW_CONTEXT"
INTRAMONTH_PENDING_LABEL = "INTRAMONTH TEYİT HENÜZ YAYIMLANMADI"
EXPERT_DISPLAY_ORDER = (
    "CAUSAL_PATCH",
    "VW_MIDAS_MSVR",
    "MOMENTUM_3M",
    "RANDOM_WALK",
)
EXPERT_DISPLAY = {
    "CAUSAL_PATCH": {
        "label": "Causal Patch",
        "model_version": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "role": "Forward issuer candidate / expert",
        "empty_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",
    },
    "VW_MIDAS_MSVR": {
        "label": "VW-MIDAS-MSVR",
        "model_version": "VW_AUDITED_SHADOW_V2",
        "role": "Audited analytical shadow/reference",
        "empty_status": "BLOCKED_NOT_PROVEN_EXECUTABLE",
    },
    "MOMENTUM_3M": {
        "label": "3M Momentum",
        "model_version": "MOMENTUM_3M_R1",
        "role": "Direction challenger / context expert",
        "empty_status": "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",
    },
    "RANDOM_WALK": {
        "label": "Random Walk",
        "model_version": "RW_R1",
        "role": "Mandatory naive benchmark",
        "empty_status": "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",
    },
}


@dataclass(frozen=True)
class ViewState:
    title: str
    subtitle: str
    tone: str
    evidence_class: str | None = None


def normalize_search_text(text: str) -> str:
    return str(text or "").upper().replace("İ", "I").replace("ı", "I")


def assert_no_action_mapping(text: str) -> None:
    normalized = f" {normalize_search_text(text)} "
    for term in PROHIBITED_ACTION_TERMS:
        t = normalize_search_text(term)
        if t.strip() in normalized:
            raise RuntimeError(f"NOT_PROVEN_POSITION_MAPPING_UI_VIOLATION:{term}")


def display_state(value: Any, fallback: str = "KULLANILAMIYOR") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    if not text or text.upper() in {"NONE", "NAN", "N/A"}:
        return fallback
    return text


def arrow_state(value: Any) -> tuple[str, str]:
    text = display_state(value, "NÖTR").upper()
    if "UP" in text or "YUKARI" in text:
        return "↑", "positive"
    if "DOWN" in text or "AŞAĞI" in text or "ASAGI" in normalize_search_text(text):
        return "↓", "negative"
    return "•", "neutral"


def classification_label(value: Any) -> str:
    mapping = {
        "ALIGNED_UP": "YUKARI UYUMLU",
        "ALIGNED_DOWN": "AŞAĞI UYUMLU",
        "CONFLICT": "ÇELİŞKİ",
        "UNRESOLVED_MIXED": "KARMA / ÇÖZÜMLENMEDİ",
        "MACRO_DOWN_RISK": "MAKRO AŞAĞI RİSKİ",
        "REVERSAL_RISK_DOWN": "AŞAĞI DÖNÜŞ RİSKİ",
        "REVERSAL_RISK_UP": "YUKARI DÖNÜŞ RİSKİ",
    }
    raw = display_state(value, "KANONİK KARAR YOK")
    label = mapping.get(raw, raw.replace("_", " "))
    assert_no_action_mapping(label)
    return label


def decision_view_state(decision: dict[str, Any] | None) -> ViewState:
    if not decision:
        return ViewState(
            title="KANONİK KARAR YOK",
            subtitle="Display-eligible Decision Store kaydı oluşmadı.",
            tone="neutral",
            evidence_class=None,
        )
    if decision.get("context_only") is True:
        return ViewState(
            title="KANONİK KARAR YOK",
            subtitle="Kısmi SHADOW CONTEXT mevcut; tam Decision Store snapshot henüz yok.",
            tone="neutral",
            evidence_class=CONTEXT_EVIDENCE_CLASS,
        )
    classification = str(decision.get("classification") or "UNRESOLVED_MIXED")
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise RuntimeError(f"UNAPPROVED_UI_CLASSIFICATION:{classification}")
    tone = "positive" if classification == "ALIGNED_UP" else "negative" if classification in {
        "ALIGNED_DOWN", "MACRO_DOWN_RISK", "REVERSAL_RISK_DOWN"
    } else "warning" if classification in {"CONFLICT", "REVERSAL_RISK_UP"} else "neutral"
    return ViewState(
        title=classification_label(classification),
        subtitle="Kayıtlı karar durumu — canlı spottan türetilmez.",
        tone=tone,
        evidence_class=decision.get("evidence_class"),
    )


def forecast_view_state(forecast: dict[str, Any] | None) -> ViewState:
    if not forecast:
        return ViewState(
            title="TAHMİN HENÜZ YAYIMLANMADI",
            subtitle="NOT_ISSUED_IN_CANONICAL_LEDGER",
            tone="neutral",
            evidence_class=None,
        )
    evidence = str(forecast.get("evidence_class") or "")
    if evidence not in {"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}:
        raise RuntimeError(f"FORECAST_UI_EVIDENCE_NOT_DISPLAY_ELIGIBLE:{evidence}")
    if forecast.get("canonical_authority") is not True:
        raise RuntimeError("FORECAST_UI_NONCANONICAL_EXPERT_AS_CANONICAL_VIOLATION")
    selector = str(forecast.get("selector_status") or "")
    if not selector or selector == EXPERT_SELECTION_STATUS:
        raise RuntimeError("FORECAST_UI_SELECTOR_RULE_NOT_GOVERNED")
    return ViewState(
        title="GELECEK AY TAHMİNİ",
        subtitle=str(forecast.get("target_month") or "Hedef ay mevcut değil"),
        tone="positive" if evidence == "LIVE_PRODUCTION" else "shadow",
        evidence_class=evidence,
    )


def evidence_badge(evidence_class: str | None) -> tuple[str, str]:
    mapping = {
        "HISTORICAL_REPLAY": ("HISTORICAL REPLAY", "research"),
        "PROSPECTIVE_SHADOW": ("PROSPECTIVE SHADOW", "shadow"),
        "LIVE_PRODUCTION": ("LIVE PRODUCTION", "production"),
        CONTEXT_EVIDENCE_CLASS: ("SHADOW CONTEXT", "shadow"),
    }
    if evidence_class is None:
        return ("YAYIMLANMADI", "neutral")
    if evidence_class not in mapping:
        raise RuntimeError(f"UNKNOWN_EVIDENCE_BADGE:{evidence_class}")
    return mapping[evidence_class]


def expert_state_map(rows: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows or []:
        expert_id = str(row.get("expert_id") or "")
        if expert_id not in EXPERT_DISPLAY:
            continue
        if row.get("canonical_authority") is True:
            raise RuntimeError("INDIVIDUAL_EXPERT_CANONICAL_AUTHORITY_UI_VIOLATION")
        if str(row.get("selector_status") or EXPERT_SELECTION_STATUS) != EXPERT_SELECTION_STATUS:
            raise RuntimeError("EXPERT_SELECTOR_STATUS_UI_VIOLATION")
        if str(row.get("auto_selector") or "OFF").upper() != "OFF":
            raise RuntimeError("EXPERT_AUTO_SELECTOR_UI_VIOLATION")
        if str(row.get("auto_ensemble") or "OFF").upper() != "OFF":
            raise RuntimeError("EXPERT_AUTO_ENSEMBLE_UI_VIOLATION")
        result[expert_id] = dict(row)
    return result


def expert_display_state(expert_id: str, rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    if expert_id not in EXPERT_DISPLAY:
        raise KeyError(expert_id)
    base = dict(EXPERT_DISPLAY[expert_id])
    row = expert_state_map(rows).get(expert_id)
    if row:
        base.update({
            "issued": True,
            "forecast_value": row.get("forecast_value"),
            "target_month": row.get("target_month"),
            "as_of": row.get("as_of"),
            "forecast_track": row.get("forecast_track"),
            "evidence_class": row.get("evidence_class"),
            "status": "ISSUED_SEPARATE_EXPERT_OUTPUT",
        })
    else:
        base.update({
            "issued": False,
            "forecast_value": None,
            "target_month": None,
            "as_of": None,
            "forecast_track": None,
            "evidence_class": None,
            "status": base["empty_status"],
        })
    return base


def _component_is_available(value: Any) -> bool:
    text = display_state(value, "YAYIMLANMADI").upper()
    return text not in {
        "YAYIMLANMADI",
        "KULLANILAMIYOR",
        "UNRESOLVED",
        "NONE",
        "N/A",
        "NAN",
    }


def monthly_intramonth_relation(decision: dict[str, Any] | None) -> str:
    if not decision:
        return "KARAR HENÜZ YAYIMLANMADI"
    monthly = display_state(decision.get("monthly_direction_3m"), "YAYIMLANMADI")
    fast = display_state(decision.get("fast_state"), "YAYIMLANMADI")
    slow = display_state(decision.get("slow_state"), "YAYIMLANMADI")
    monthly_ok = _component_is_available(monthly)
    fast_ok = _component_is_available(fast)
    slow_ok = _component_is_available(slow)

    if decision.get("context_only") is True:
        if not monthly_ok and (fast_ok or slow_ok):
            return "MONTHLY_PRIOR_NOT_ISSUED_TACTICAL_CONTEXT_AVAILABLE"
        if monthly_ok and not (fast_ok or slow_ok):
            return INTRAMONTH_PENDING_LABEL
        if not monthly_ok and not (fast_ok or slow_ok):
            return "UNRESOLVED_INSUFFICIENT_STORED_STATE"
    elif not monthly_ok or not (fast_ok or slow_ok):
        return "UNRESOLVED_INSUFFICIENT_STORED_STATE"

    ma, _ = arrow_state(monthly)
    fa, _ = arrow_state(fast)
    sa, _ = arrow_state(slow)
    if fast_ok and slow_ok:
        intramonth = fa if fa == sa and fa in {"↑", "↓"} else "•"
    elif fast_ok:
        intramonth = fa
    elif slow_ok:
        intramonth = sa
    else:
        intramonth = "•"
    if ma in {"↑", "↓"} and intramonth in {"↑", "↓"} and ma != intramonth:
        return "MONTHLY_PRIOR_INTRAMONTH_CONFLICT_ALLOWED"
    if ma in {"↑", "↓"} and intramonth == ma:
        return "MONTHLY_PRIOR_INTRAMONTH_CONFIRMATION"
    return "MONTHLY_PRIOR_INTRAMONTH_MIXED"


def deterministic_explanation(decision: dict[str, Any] | None) -> str:
    if not decision:
        return (
            "Aylık prior stratejik anchor'dır; günlük işlem emri değildir. "
            "Fast/Slow, Macro Event, Emergency, BOCPD ve GVZ yalnız kendi dondurulmuş rolleriyle "
            "yeni uygun veri geldikçe intramonth durumu günceller. Kayıtlı final karar henüz yok."
        )

    monthly = display_state(decision.get("monthly_direction_3m"), "YAYIMLANMADI")
    fast = display_state(decision.get("fast_state"), "YAYIMLANMADI")
    slow = display_state(decision.get("slow_state"), "YAYIMLANMADI")
    macro = display_state(decision.get("macro_event_state"), "BLOCKED_NOT_FULLY_RECOVERED")
    level = display_state(decision.get("level_emergency"), "YAYIMLANMADI")
    reversal = display_state(decision.get("reversal_emergency"), "YAYIMLANMADI")
    bocpd = display_state(decision.get("bocpd_context"), "YAYIMLANMADI")
    gvz = display_state(decision.get("gvz_cap"), "YAYIMLANMADI")

    if decision.get("context_only") is True:
        parts = [
            f"Aylık prior: {monthly}",
            f"Fast/Slow: {fast} / {slow}",
            f"Macro Event: {macro}",
            f"Emergency Level/Reversal: {level} / {reversal}",
            f"BOCPD: {bocpd}",
            f"GVZ stored risk cap: {gvz}",
            f"Prior/intramonth: {monthly_intramonth_relation(decision)}",
            "Bu kayıtlar kısmi immutable shadow context'tir; final Decision Store kararı değildir",
        ]
        result = ". ".join(parts) + "."
        assert_no_action_mapping(result)
        return result

    parts: list[str] = []
    if _component_is_available(monthly):
        parts.append(f"Aylık prior: {monthly}")
    if _component_is_available(fast) or _component_is_available(slow):
        parts.append(f"Fast/Slow: {fast} / {slow}")
    parts.append(f"Macro Event: {macro}")
    if _component_is_available(level) or _component_is_available(reversal):
        parts.append(f"Emergency: {level} / {reversal}")
    if _component_is_available(bocpd):
        parts.append(f"BOCPD: {bocpd}")
    if _component_is_available(gvz):
        parts.append(f"GVZ risk cap: {gvz}")
    parts.append(f"Prior/intramonth: {monthly_intramonth_relation(decision)}")
    result = ". ".join(parts) + "."
    assert_no_action_mapping(result)
    return result


def v2_layout_contract() -> dict[str, tuple[str, ...] | str]:
    return {
        "contract": FINAL_MOCKUP_CONTRACT,
        "gorunum": GORUNUM_SECTION_ORDER,
        "tahmin": TAHMIN_SECTION_ORDER,
        "gecmis": GECMIS_SECTION_ORDER,
        "scenario_status": SCENARIO_STATUS,
        "position_status": POSITION_STATUS,
        "expert_selection_status": EXPERT_SELECTION_STATUS,
        "auto_selector": AUTO_SELECTOR_STATUS,
        "auto_ensemble": AUTO_ENSEMBLE_STATUS,
        "expert_order": EXPERT_DISPLAY_ORDER,
        "month_end_track": MONTH_END_TRACK,
        "early_indicative_track": EARLY_INDICATIVE_TRACK,
    }
