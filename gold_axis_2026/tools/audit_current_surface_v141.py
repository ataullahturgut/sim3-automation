from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GC = ROOT / "gold_axis_2026"

CURRENT_RUNTIME_FILES = [
    GC / "GOLD_CONTROL_PROJECT_MANIFEST.md",
    GC / "apps" / "gold_control.py",
    GC / "apps" / "gold_control_mobile.py",
    GC / "apps" / "engine_observability_contract.py",
    GC / "apps" / "runtime_source.py",
    GC / "apps" / "production_display_snapshot.py",
    GC / "apps" / "production_display_snapshot.json",
    GC / "apps" / "forecast_source.py",
    GC / "data_pipeline" / "data_evidence_spine_runtime_bootstrap.py",
    GC / "data_pipeline" / "multi_expert_forecast.py",
    GC / "tools" / "export_production_display_snapshot.py",
]

FORBIDDEN_CURRENT_PATTERNS = {
    "superseded_vw_identity": re.compile(r"(?<!SUCCESSOR_)\bVW_MIDAS_MSVR\b(?!_SUCCESSOR)"),
    "stale_waiting_promotion": re.compile(r"WAITING_RUNTIME_PROMOTION_RECORD"),
    "stale_missed_origin_status": re.compile(r"NOT_ISSUED_MISSED_2026_08_31_ORIGIN"),
    "superseded_snapshot_contract": re.compile(r"LEGACY_SNAPSHOT_CONTRACT|FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V[12]"),
    "old_manifest_runtime_scope": re.compile(r"MANIFEST_V1_(?:2[0-9]|3[0-9]|40)"),
    "date_specific_replay_dependency": re.compile(r"aug31_state_replay|aug31_replay_expansion", re.IGNORECASE),
    "old_mobile_entrypoint": re.compile(r"gold_control_mobile_v1"),
}

LEGACY_PATH_TOKENS = (
    "v126", "v127", "v128", "v129", "v130", "v131", "v132", "v139", "v140",
    "aug31_state_replay", "aug31_replay_expansion", "stage4b", "stage4_",
    "VW_MIDAS_SVR_XAU_SUCCESSOR_V2", "MACRO_EVENT_SUCCESSOR_V1",
    "gold_control_mobile_v1", "mobile_ui_contract",
)


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


def legacy_paths() -> list[str]:
    result: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        low = rel.lower()
        if rel.startswith(".git/"):
            continue
        if any(token.lower() in low for token in LEGACY_PATH_TOKENS):
            result.append(rel)
    return sorted(result)


def main() -> int:
    current_findings = scan_current_runtime()
    legacy = legacy_paths()
    report = {
        "contract": "GOLD_CONTROL_CURRENT_SURFACE_AUDIT_V141",
        "current_runtime_findings": current_findings,
        "legacy_path_count": len(legacy),
        "legacy_paths": legacy,
        "pass": not current_findings and not legacy,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    Path("current_surface_audit_v141.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
