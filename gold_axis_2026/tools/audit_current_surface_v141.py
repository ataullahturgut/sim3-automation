from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GC = ROOT / "gold_axis_2026"
SNAPSHOT = GC / "apps" / "production_display_snapshot.json"

CURRENT_RUNTIME_FILES = [
    GC / "GOLD_CONTROL_PROJECT_MANIFEST.md",
    GC / "apps" / "gold_control.py",
    GC / "apps" / "gold_control_mobile.py",
    GC / "apps" / "engine_observability_contract.py",
    GC / "apps" / "runtime_source.py",
    GC / "apps" / "production_display_snapshot.py",
    SNAPSHOT,
    GC / "apps" / "live_sources.py",
    GC / "data_pipeline" / "data_evidence_spine_runtime_bootstrap.py",
    GC / "data_pipeline" / "multi_expert_forecast.py",
    GC / "tools" / "export_production_display_snapshot.py",
]

FORBIDDEN_CURRENT_PATTERNS = {
    "superseded_vw_identity": re.compile(r"(?<!SUCCESSOR_)\bVW_MIDAS_MSVR\b(?!_SUCCESSOR)"),
    "stale_waiting_promotion": re.compile(r"WAITING_RUNTIME_PROMOTION_RECORD"),
    "stale_missed_origin_status": re.compile(r"NOT_ISSUED_MISSED_2026_08_31_ORIGIN|SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED"),
    "superseded_snapshot_contract": re.compile(r"LEGACY_SNAPSHOT_CONTRACT|FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V[123]"),
    "old_manifest_runtime_scope": re.compile(r"MANIFEST_V1_(?:2[0-9]|3[0-9]|40)"),
    "date_specific_replay_dependency": re.compile(r"aug31_state_replay|aug31_replay_expansion", re.IGNORECASE),
    "old_mobile_entrypoint": re.compile(r"gold_control_mobile_v1"),
    "old_stage_contract": re.compile(r"GOLD_CONTROL_STAGE4|GOLD_CONTROL_STAGE_4"),
    "old_context_evidence": re.compile(r"LATE_BOOTSTRAP_SHADOW_CONTEXT"),
    "old_macro_identity": re.compile(r"MACRO_EVENT_SUCCESSOR_V1"),
}

LEGACY_PATH_TOKENS = (
    "v126", "v127", "v128", "v129", "v130", "v131", "v132", "v139", "v140",
    "aug31_state_replay", "aug31_replay_expansion", "stage4b", "stage4_",
    "vw_midas_svr_xau_successor_v2", "macro_event_successor_v1",
    "gold_control_mobile_v1", "mobile_ui_contract",
)

EXPECTED_ENGINES = {
    "CAUSAL_PATCH",
    "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "MACRO_EVENT_SUCCESSOR_V2",
    "BOCPD_RETURN_SUCCESSOR_V1",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "GVZ_RISK",
}
EXPECTED_FEATURES = {
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
}


def scan_current_runtime() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in CURRENT_RUNTIME_FILES:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            findings.append({"kind": "missing_current_file", "path": rel, "match": ""})
            continue
        text = path.read_text(encoding="utf-8")
        for name, pattern in FORBIDDEN_CURRENT_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append({"kind": name, "path": rel, "match": f"line {line}: {match.group(0)}"})
    return findings


def validate_snapshot() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not SNAPSHOT.exists():
        return [{"kind": "snapshot_missing", "path": str(SNAPSHOT.relative_to(ROOT)), "match": ""}]
    try:
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    except Exception as exc:
        return [{"kind": "snapshot_json_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": type(exc).__name__}]

    if snapshot.get("snapshot_contract") != "GOLD_CONTROL_CURRENT_PRODUCTION_DISPLAY_SNAPSHOT_V141":
        findings.append({"kind": "snapshot_contract_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": str(snapshot.get("snapshot_contract"))})

    runtime = snapshot.get("runtime") or []
    ids = {str(row.get("engine_id") or "") for row in runtime if isinstance(row, dict)}
    if len(runtime) != 12 or ids != EXPECTED_ENGINES:
        findings.append({"kind": "snapshot_runtime_inventory_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": f"count={len(runtime)} ids={sorted(ids)}"})
    if any(str(row.get("runtime_status") or "").upper() != "ACTIVE" for row in runtime if isinstance(row, dict)):
        findings.append({"kind": "snapshot_runtime_not_all_active", "path": str(SNAPSHOT.relative_to(ROOT)), "match": ""})
    for row in runtime:
        if not isinstance(row, dict):
            continue
        metadata = row.get("metadata") or {}
        if metadata.get("current_surface_contract") != "GOLD_CONTROL_CURRENT_SURFACE_V141":
            findings.append({"kind": "snapshot_runtime_contract_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": str(row.get("engine_id"))})

    features = snapshot.get("features") or []
    names = {str(row.get("feature_name") or "") for row in features if isinstance(row, dict)}
    if len(features) != 7 or names != EXPECTED_FEATURES:
        findings.append({"kind": "snapshot_feature_inventory_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": f"count={len(features)} names={sorted(names)}"})
    for row in features:
        if not isinstance(row, dict):
            continue
        metadata = row.get("metadata") or {}
        if row.get("quality_status") != "HISTORICAL_REPLAY_CONTEXT":
            findings.append({"kind": "snapshot_feature_evidence_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": str(row.get("feature_name"))})
        if metadata.get("current_surface_contract") != "GOLD_CONTROL_CURRENT_SURFACE_V141":
            findings.append({"kind": "snapshot_feature_contract_invalid", "path": str(SNAPSHOT.relative_to(ROOT)), "match": str(row.get("feature_name"))})

    authority = snapshot.get("authority_store_counts") or {}
    if any(int(authority.get(key) or 0) != 0 for key in ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events")):
        findings.append({"kind": "snapshot_authority_store_nonzero", "path": str(SNAPSHOT.relative_to(ROOT)), "match": json.dumps(authority, sort_keys=True)})
    return findings


def legacy_paths() -> list[str]:
    result: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        low = rel.lower()
        if rel.startswith(".git/"):
            continue
        if any(token in low for token in LEGACY_PATH_TOKENS):
            result.append(rel)
    return sorted(result)


def main() -> int:
    findings = scan_current_runtime() + validate_snapshot()
    legacy = legacy_paths()
    report = {
        "contract": "GOLD_CONTROL_CURRENT_SURFACE_AUDIT_V141",
        "current_runtime_findings": findings,
        "legacy_path_count": len(legacy),
        "legacy_paths": legacy,
        "pass": not findings and not legacy,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    Path("current_surface_audit_v141.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
