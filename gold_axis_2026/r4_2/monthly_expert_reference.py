from __future__ import annotations

from typing import Any, Mapping

from .contracts import MonthlyPriceReference


PATCH_EXPERT_ID = "CAUSAL_PATCH"
ALLOWED_TRACK = "MONTH_END_EXPERT"
ALLOWED_EVIDENCE = {"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}
SELECTOR_LOCK = "NOT_PROVEN_EXPERT_SELECTION_RULE"


def patch_expert_monthly_reference(row: Mapping[str, Any]) -> MonthlyPriceReference:
    """Convert one persisted Patch expert row into an Emergency reference.

    This adapter is deliberately expert-specific. It does not choose among
    experts, rank experts, average them, or promote Patch to canonical forecast
    authority. It merely states that the frozen operational Patch issuer may be
    used as the reference for a *Patch-referenced Emergency context* when its
    own persisted expert identity is complete and all selection locks remain
    closed.
    """

    expert_id = str(row.get("expert_id") or "").strip()
    if expert_id != PATCH_EXPERT_ID:
        raise ValueError(f"unsupported emergency expert reference: {expert_id or 'MISSING'}")

    track = str(row.get("forecast_track") or "").strip()
    if track != ALLOWED_TRACK:
        raise ValueError(f"Patch emergency reference requires {ALLOWED_TRACK}, got {track or 'MISSING'}")

    evidence = str(row.get("evidence_class") or "").strip()
    if evidence not in ALLOWED_EVIDENCE:
        raise ValueError(f"Patch emergency reference requires prospective evidence, got {evidence or 'MISSING'}")

    if row.get("canonical_authority") is not False:
        raise ValueError("Patch expert reference must retain canonical_authority=false")
    if str(row.get("auto_selector") or "").strip() != "OFF":
        raise ValueError("Patch expert reference requires AUTO_SELECTOR=OFF")
    if str(row.get("auto_ensemble") or "").strip() != "OFF":
        raise ValueError("Patch expert reference requires AUTO_ENSEMBLE=OFF")
    if str(row.get("selector_status") or "").strip() != SELECTOR_LOCK:
        raise ValueError(f"Patch expert reference requires selector_status={SELECTOR_LOCK}")

    forecast_id = row.get("id")
    input_set_id = row.get("input_set_id")
    if forecast_id is None or not str(input_set_id or "").strip():
        raise ValueError("Patch expert reference requires persisted id and input_set_id")

    target = row.get("target_month")
    target_month = str(target or "")[:7]
    forecast_origin = str(row.get("forecast_origin") or "").strip()
    model_id = str(row.get("model_version") or row.get("model_name") or expert_id).strip()

    reference = MonthlyPriceReference(
        value=float(row["forecast_value"]),
        model_id=model_id,
        target_month=target_month,
        forecast_origin=forecast_origin,
        evidence_class=evidence,
        input_set_id=str(input_set_id),
        expert_forecast_id=str(forecast_id),
    )
    reference.validate(require_persisted_ids=True)
    return reference
