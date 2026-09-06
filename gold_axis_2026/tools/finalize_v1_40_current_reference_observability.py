from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_one(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{marker}:expected=1:found={count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_runtime_bootstrap() -> None:
    path = ROOT / "data_pipeline" / "data_evidence_spine_runtime_bootstrap.py"
    replace_one(
        path,
        '                "input_fingerprint": None,\n                "derived_feature_snapshot_ids": [],',
        '                "input_fingerprint": (CURRENT_MONTH_REFERENCES.get(engine_id) or {}).get("input_fingerprint"),\n                "derived_feature_snapshot_ids": [],',
        "RUNTIME_REFERENCE_FINGERPRINT_PATCH",
    )


def patch_observability() -> None:
    path = ROOT / "apps" / "engine_observability_contract.py"
    replace_one(
        path,
        '    if _text(ref.get("reference_kind")) != "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE":\n        return None',
        '    if _text(ref.get("reference_kind")) not in {\n        "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",\n        "HISTORICAL_REPLAY_MONTH_OPEN_STATE",\n    }:\n        return None',
        "OBSERVABILITY_REFERENCE_KIND_PATCH",
    )
    replace_one(
        path,
        '            if ref and not _available(row.get("output")):',
        '            if ref and (\n                not _available(row.get("output"))\n                or _text(row.get("status")).startswith(("WAITING_", "BLOCKED_", "NOT_PROVEN_", "ACTIVE_HISTORICAL_REPLAY_"))\n            ):',
        "OBSERVABILITY_STALE_PLACEHOLDER_OVERRIDE_PATCH",
    )


def patch_snapshot_exporter() -> None:
    path = ROOT / "tools" / "export_production_display_snapshot.py"
    replace_one(
        path,
        'SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2"',
        'SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V3_CURRENT_MONTH_REFERENCES"',
        "EXPORTER_SNAPSHOT_CONTRACT_PATCH",
    )
    replace_one(
        path,
        '                       git_commit\n                FROM latest_engine_runtime_state',
        '                       git_commit,metadata\n                FROM latest_engine_runtime_state',
        "EXPORTER_RUNTIME_METADATA_PATCH",
    )


def patch_snapshot_validator() -> None:
    path = ROOT / "apps" / "production_display_snapshot.py"
    replace_one(
        path,
        'SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2"\nLEGACY_SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1"',
        'SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V3_CURRENT_MONTH_REFERENCES"\nPREVIOUS_SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2"\nLEGACY_SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1"',
        "VALIDATOR_SNAPSHOT_CONTRACT_PATCH",
    )
    replace_one(
        path,
        '    if snapshot.get("snapshot_contract") not in {SNAPSHOT_CONTRACT, LEGACY_SNAPSHOT_CONTRACT}:',
        '    if snapshot.get("snapshot_contract") not in {SNAPSHOT_CONTRACT, PREVIOUS_SNAPSHOT_CONTRACT, LEGACY_SNAPSHOT_CONTRACT}:',
        "VALIDATOR_ALLOWED_CONTRACT_PATCH",
    )


def main() -> int:
    patch_runtime_bootstrap()
    patch_observability()
    patch_snapshot_exporter()
    patch_snapshot_validator()
    print("GOLD_CONTROL_V140_FINAL_OBSERVABILITY_RECONCILE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
