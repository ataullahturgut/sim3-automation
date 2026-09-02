from __future__ import annotations

import re
import unicodedata
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
    "POZİSYONU KORU", "AL", "SAT",
}


@dataclass(frozen=True)
class ViewState:
    title: str
    subtitle: str
    tone: str
    evidence_class: str | None = None


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
        title=classification.replace("_", " "),
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


def _guard_normalize(value: str) -> str:
    """Normalize Turkish/Unicode spelling for policy-term comparison only."""
    value = str(value or "").replace("ı", "i").replace("İ", "I")
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_like = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return ascii_like.upper()


def assert_no_action_mapping(text: str) -> None:
    normalized = _guard_normalize(text)
    for term in PROHIBITED_ACTION_TERMS:
        normalized_term = _guard_normalize(term)
        pattern = rf"(?<![A-Z0-9]){re.escape(normalized_term)}(?![A-Z0-9])"
        if re.search(pattern, normalized):
            raise RuntimeError(f"NOT_PROVEN_POSITION_MAPPING_UI_VIOLATION:{term}")


def deterministic_explanation(decision: dict[str, Any] | None) -> str:
    if not decision:
        return "Görünüm, display-eligible Decision Store kaydı oluşana kadar karar üretmez."
    parts: list[str] = []
    monthly = decision.get("monthly_direction_3m")
    fast = decision.get("fast_state")
    slow = decision.get("slow_state")
    bocpd = decision.get("bocpd_context")
    emergency = decision.get("level_emergency") or decision.get("reversal_emergency")
    gvz = decision.get("gvz_cap")
    if monthly not in (None, "N/A"):
        parts.append(f"Aylık bağlam: {monthly}")
    if fast not in (None, "N/A") or slow not in (None, "N/A"):
        parts.append(f"Fast/Slow: {fast or 'N/A'} / {slow or 'N/A'}")
    if bocpd not in (None, "N/A"):
        parts.append(f"Rejim: {bocpd}")
    if emergency not in (None, "N/A"):
        parts.append(f"Emergency: {emergency}")
    if gvz not in (None, "N/A"):
        parts.append(f"Risk katmanı: {gvz}")
    result = ". ".join(parts) + ("." if parts else "Kayıtlı alt katman ayrıntısı mevcut değil.")
    assert_no_action_mapping(result)
    return result
