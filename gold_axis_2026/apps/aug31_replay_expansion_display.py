from __future__ import annotations

from typing import Any


TARGET_CONTEXT = "2026-09"
REPLAY_EVIDENCE = "HISTORICAL_REPLAY"


def attach_aug31_replay_expansion(
    rows: list[dict[str, Any]],
    replay: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Attach immutable 31-Aug replay references without changing operational status.

    This function is presentation-only. It never changes runtime_status,
    status/status_code, direction-vote permission, selector/ensemble locks, or
    canonical authority. The UI renders replay fields as a second evidence layer.
    """
    out = [dict(row) for row in rows]
    if not replay:
        return out
    if replay.get("target_context") != TARGET_CONTEXT:
        return out
    if replay.get("evidence_class") != REPLAY_EVIDENCE:
        return out
    if replay.get("prospective_claim") is not False:
        return out
    if replay.get("current_runtime_authority") is not False:
        return out
    if replay.get("canonical_authority") is not False:
        return out
    if replay.get("direction_vote_permitted") is not False:
        return out
    if replay.get("auto_selector") != "OFF" or replay.get("auto_ensemble") != "OFF":
        return out

    by_engine = {str(row.get("engine_id") or ""): row for row in out}

    patch = by_engine.get("CAUSAL_PATCH")
    if patch is not None:
        patch["replay_reference"] = {
            "label": "31 AĞUSTOS REPLAY",
            "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
            "output": replay.get("causal_patch_forecast"),
            "unit": "USD/oz",
            "status": "REPLAY_REFERENCE_AVAILABLE",
            "evidence_class": REPLAY_EVIDENCE,
            "version": replay.get("causal_patch_version"),
            "target_context": TARGET_CONTEXT,
            "forecast_origin": replay.get("causal_patch_forecast_origin"),
            "as_of": replay.get("source_state_at"),
            "prospective_claim": False,
            "canonical_authority": False,
            "direction_vote_permitted": False,
            "note": "Eylül 2026 H=1 historical reference; 31 Ağustos information boundary. Prospective issuance değildir.",
        }

    for engine_id, key, version in (
        ("EMERGENCY_LEVEL", "emergency_level", "R4_1_EMERGENCY_LEVEL_REPLAY_V1"),
        ("EMERGENCY_REVERSAL", "emergency_reversal", "R4_1_EMERGENCY_REVERSAL_REPLAY_V1"),
    ):
        row = by_engine.get(engine_id)
        if row is not None:
            row["replay_reference"] = {
                "label": "31 AĞUSTOS AY-AÇILIŞ REPLAY",
                "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE",
                "output": replay.get(key),
                "unit": None,
                "status": "REPLAY_STATE_AVAILABLE",
                "evidence_class": REPLAY_EVIDENCE,
                "version": version,
                "target_context": TARGET_CONTEXT,
                "forecast_origin": replay.get("state_as_of"),
                "as_of": replay.get("source_state_at"),
                "prospective_claim": False,
                "canonical_authority": False,
                "direction_vote_permitted": False,
                "note": "Eylül EOD gözlemi henüz yokken frozen month-open initialization; 31 Ağustos close Eylül close değildir.",
            }

    bocpd = by_engine.get("BOCPD")
    if bocpd is not None:
        bocpd["replay_reference"] = {
            "label": "SUCCESSOR V1 · 31 AĞUSTOS REPLAY",
            "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",
            "output": replay.get("bocpd_successor_state"),
            "unit": None,
            "status": "RESEARCH_REPLAY_CONTEXT_AVAILABLE",
            "evidence_class": REPLAY_EVIDENCE,
            "version": replay.get("bocpd_successor_id"),
            "target_context": TARGET_CONTEXT,
            "forecast_origin": replay.get("state_as_of"),
            "as_of": replay.get("source_state_at"),
            "prospective_claim": False,
            "canonical_authority": False,
            "direction_vote_permitted": False,
            "archived_engine_status": replay.get("bocpd_archived_engine_status"),
            "context_identity": replay.get("bocpd_context_identity"),
            "note": "Archived BOCPD BLOCKED kalır; successor yalnız out-of-lock research/historical replay context'tir.",
        }

    return out
