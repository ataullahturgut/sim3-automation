from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DP = ROOT / "data_pipeline"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{n}:{old[:120]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_multi_expert() -> None:
    p = DP / "multi_expert_forecast.py"
    replace_once(p, 'MANIFEST_VERSION = "1.25"', 'MANIFEST_VERSION = "1.28"')
    replace_once(
        p,
        'TRACK_MONTH_END = "MONTH_END_EXPERT"\nTRACK_EARLY_INDICATIVE = "EARLY_INDICATIVE"\nFORECAST_TRACKS = frozenset({TRACK_MONTH_END, TRACK_EARLY_INDICATIVE})\nDISPLAY_EVIDENCE_CLASSES = frozenset({"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"})',
        'TRACK_MONTH_END = "MONTH_END_EXPERT"\nTRACK_EARLY_INDICATIVE = "EARLY_INDICATIVE"\nTRACK_HISTORICAL_REPLAY = "HISTORICAL_REPLAY"\nFORECAST_TRACKS = frozenset({TRACK_MONTH_END, TRACK_EARLY_INDICATIVE, TRACK_HISTORICAL_REPLAY})\nDISPLAY_EVIDENCE_CLASSES = frozenset({"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION", "HISTORICAL_REPLAY"})',
    )
    replace_once(
        p,
        '        if self.evidence_class not in DISPLAY_EVIDENCE_CLASSES:\n            raise ValueError(f"INVALID_EVIDENCE_CLASS:{self.evidence_class}")\n        if not self.target_month or len(self.target_month) < 7:',
        '        if self.evidence_class not in DISPLAY_EVIDENCE_CLASSES:\n            raise ValueError(f"INVALID_EVIDENCE_CLASS:{self.evidence_class}")\n        if self.forecast_track == TRACK_HISTORICAL_REPLAY:\n            if self.evidence_class != "HISTORICAL_REPLAY":\n                raise ValueError("HISTORICAL_REPLAY_TRACK_REQUIRES_REPLAY_EVIDENCE")\n        elif self.evidence_class == "HISTORICAL_REPLAY":\n            raise ValueError("HISTORICAL_REPLAY_EVIDENCE_REQUIRES_REPLAY_TRACK")\n        if not self.target_month or len(self.target_month) < 7:',
    )
    replace_once(
        p,
        '        if self.as_of < self.forecast_origin:\n            raise ValueError("AS_OF_BEFORE_FORECAST_ORIGIN")\n        if not isinstance(self.forecast_value, (int, float)) or not (self.forecast_value > 0):',
        '        if self.as_of < self.forecast_origin:\n            raise ValueError("AS_OF_BEFORE_FORECAST_ORIGIN")\n        if self.forecast_track == TRACK_HISTORICAL_REPLAY:\n            if self.as_of <= self.forecast_origin:\n                raise ValueError("HISTORICAL_REPLAY_AS_OF_MUST_BE_AFTER_ORIGIN")\n            if self.provenance.get("historical_replay") is not True:\n                raise ValueError("HISTORICAL_REPLAY_PROVENANCE_REQUIRED")\n            if self.provenance.get("prospective_claim") is not False:\n                raise ValueError("HISTORICAL_REPLAY_PROSPECTIVE_CLAIM_MUST_BE_FALSE")\n            if str(self.provenance.get("information_cutoff")) != self.forecast_origin.isoformat():\n                raise ValueError("HISTORICAL_REPLAY_INFORMATION_CUTOFF_MISMATCH")\n            if str(self.provenance.get("replay_executed_at")) != self.as_of.isoformat():\n                raise ValueError("HISTORICAL_REPLAY_EXECUTION_TIME_MISMATCH")\n        if not isinstance(self.forecast_value, (int, float)) or not (self.forecast_value > 0):',
    )


def patch_spine() -> None:
    p = DP / "data_evidence_spine.py"
    replace_once(
        p,
        '        if self.forecast_track not in {"MONTH_END_EXPERT", "EARLY_INDICATIVE"}:\n            raise ValueError("INVALID_INPUT_SET_FORECAST_TRACK")',
        '        if self.forecast_track not in {"MONTH_END_EXPERT", "EARLY_INDICATIVE", "HISTORICAL_REPLAY"}:\n            raise ValueError("INVALID_INPUT_SET_FORECAST_TRACK")',
    )
    replace_once(
        p,
        '        if self.evidence_class not in {"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}:\n            raise ValueError("INVALID_INPUT_SET_EVIDENCE_CLASS")\n        if not self.input_fingerprint:',
        '        if self.evidence_class not in {"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION", "HISTORICAL_REPLAY"}:\n            raise ValueError("INVALID_INPUT_SET_EVIDENCE_CLASS")\n        if self.forecast_track == "HISTORICAL_REPLAY":\n            if self.evidence_class != "HISTORICAL_REPLAY":\n                raise ValueError("HISTORICAL_REPLAY_INPUT_SET_REQUIRES_REPLAY_EVIDENCE")\n            if self.as_of <= self.forecast_origin:\n                raise ValueError("HISTORICAL_REPLAY_INPUT_SET_AS_OF_MUST_BE_AFTER_ORIGIN")\n            if self.metadata.get("historical_replay") is not True:\n                raise ValueError("HISTORICAL_REPLAY_INPUT_SET_METADATA_REQUIRED")\n            if self.metadata.get("prospective_claim") is not False:\n                raise ValueError("HISTORICAL_REPLAY_INPUT_SET_PROSPECTIVE_CLAIM_MUST_BE_FALSE")\n            if str(self.metadata.get("information_cutoff")) != self.forecast_origin.isoformat():\n                raise ValueError("HISTORICAL_REPLAY_INPUT_SET_CUTOFF_MISMATCH")\n            if str(self.metadata.get("replay_executed_at")) != self.as_of.isoformat():\n                raise ValueError("HISTORICAL_REPLAY_INPUT_SET_EXECUTION_TIME_MISMATCH")\n        elif self.evidence_class == "HISTORICAL_REPLAY":\n            raise ValueError("HISTORICAL_REPLAY_INPUT_SET_EVIDENCE_REQUIRES_REPLAY_TRACK")\n        if not self.input_fingerprint:',
    )


def patch_store() -> None:
    p = DP / "multi_expert_forecast_store.py"
    replace_once(
        p,
        'from __future__ import annotations\n\nimport json\nfrom dataclasses import asdict',
        'from __future__ import annotations\n\nimport json\nfrom dataclasses import asdict\nfrom datetime import datetime',
    )
    replace_once(
        p,
        '        select id,forecast_origin,target_period,model_name,model_version,\n               available_as_of,retrieved_at\n        from forecast_input_snapshots where id=any(%s)',
        '        select id,forecast_origin,target_period,model_name,model_version,\n               observation_ts,available_as_of,retrieved_at,metadata\n        from forecast_input_snapshots where id=any(%s)',
    )
    replace_once(
        p,
        '        if row["available_as_of"] > record.as_of or row["retrieved_at"] > record.as_of:\n            raise RuntimeError("BLOCKED_EXPERT_INPUT_SNAPSHOT_PIT_VIOLATION")\n    return snapshot_ids',
        '        if row["available_as_of"] > record.as_of or row["retrieved_at"] > record.as_of:\n            raise RuntimeError("BLOCKED_EXPERT_INPUT_SNAPSHOT_PIT_VIOLATION")\n        if record.forecast_track == "HISTORICAL_REPLAY":\n            metadata = dict(row.get("metadata") or {})\n            if metadata.get("historical_replay") is not True or metadata.get("prospective_claim") is not False:\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SNAPSHOT_METADATA_INVALID")\n            source_period_end_text = str(metadata.get("source_period_end") or "")\n            if not source_period_end_text:\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_END_MISSING")\n            try:\n                source_period_end = datetime.fromisoformat(source_period_end_text.replace("Z", "+00:00"))\n            except Exception as exc:\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_END_INVALID") from exc\n            if source_period_end.tzinfo is None:\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_END_NAIVE")\n            if source_period_end > record.forecast_origin:\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_AFTER_ORIGIN")\n            if row["observation_ts"] > record.forecast_origin or row["available_as_of"] > record.forecast_origin:\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_INFORMATION_AFTER_ORIGIN")\n            if str(row["target_period"]) == source_period_end.strftime("%Y-%m"):\n                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_TARGET_DATA_AS_INPUT")\n    return snapshot_ids',
    )
    replace_once(
        p,
        '    input_set_id = create_forecast_input_set(\n        cur,\n        ForecastInputSetSpec(',
        '    input_set_metadata = {\n        "contract": "FROZEN_DATA_EVIDENCE_SPINE_V1",\n        "source": "multi_expert_forecast_store.insert_expert_forecast",\n        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",\n        "auto_selector": "OFF",\n        "auto_ensemble": "OFF",\n        "canonical_authority": False,\n    }\n    if record.forecast_track == "HISTORICAL_REPLAY":\n        for key in ("historical_replay", "prospective_claim", "information_cutoff", "replay_executed_at", "official_prospective_status", "source_id"):\n            if key in record.provenance:\n                input_set_metadata[key] = record.provenance[key]\n    input_set_id = create_forecast_input_set(\n        cur,\n        ForecastInputSetSpec(',
    )
    replace_once(
        p,
        '            metadata={\n                "contract": "FROZEN_DATA_EVIDENCE_SPINE_V1",\n                "source": "multi_expert_forecast_store.insert_expert_forecast",\n                "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",\n                "auto_selector": "OFF",\n                "auto_ensemble": "OFF",\n                "canonical_authority": False,\n            },',
        '            metadata=input_set_metadata,',
    )
    replace_once(
        p,
        '        metadata={\n            "forecast_track": record.forecast_track,\n            "input_set_id": input_set_id,\n            "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",\n            "auto_selector": "OFF",\n            "auto_ensemble": "OFF",\n            "canonical_authority": False,\n        },',
        '        metadata={\n            "forecast_track": record.forecast_track,\n            "input_set_id": input_set_id,\n            "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",\n            "auto_selector": "OFF",\n            "auto_ensemble": "OFF",\n            "canonical_authority": False,\n            "historical_replay": record.forecast_track == "HISTORICAL_REPLAY",\n            "prospective_claim": False if record.forecast_track == "HISTORICAL_REPLAY" else record.provenance.get("prospective_claim"),\n            "information_cutoff": record.provenance.get("information_cutoff"),\n            "replay_executed_at": record.provenance.get("replay_executed_at"),\n        },',
    )


def main() -> int:
    patch_multi_expert()
    patch_spine()
    patch_store()
    print("HISTORICAL_REPLAY_DATA_CONTRACT_V128_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
