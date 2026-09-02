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
    }
    if evidence_class is None:
        return ("YAYIMLANMADI", "neutral")
    if evidence_class not in mapping:
        raise RuntimeError(f"UNKNOWN_EVIDENCE_BADGE:{evidence_class}")
    return mapping[evidence_class]


def deterministic_explanation(decision: dict[str, Any] | None) -> str:
    if not decision:
        return "Görünüm, display-eligible Decision Store kaydı oluşana kadar karar üretmez."
    parts: list[str] = []
    monthly = decision.get("monthly_direction_3m")
    fast = decision.get("fast_state")
    slow = decision.get("slow_state")
    bocpd = decision.get("bocpd_context")
    level = decision.get("level_emergency")
    reversal = decision.get("reversal_emergency")
    gvz = decision.get("gvz_cap")
    if monthly not in (None, "N/A"):
        parts.append(f"Aylık bağlam: {monthly}")
    if fast not in (None, "N/A") or slow not in (None, "N/A"):
        parts.append(f"Fast/Slow: {fast or 'N/A'} / {slow or 'N/A'}")
    if bocpd not in (None, "N/A"):
        parts.append(f"Rejim: {bocpd}")
    if level not in (None, "N/A") or reversal not in (None, "N/A"):
        parts.append(f"Emergency: {level or 'N/A'} / {reversal or 'N/A'}")
    if gvz not in (None, "N/A"):
        parts.append(f"Risk katmanı: {gvz}")
    result = ". ".join(parts) + ("." if parts else "Kayıtlı alt katman ayrıntısı mevcut değil.")
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
    }
