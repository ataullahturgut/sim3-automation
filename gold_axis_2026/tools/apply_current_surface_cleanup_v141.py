from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GC = ROOT / "gold_axis_2026"

DELETIONS = {
    # Version/date-specific application replay and verification surface.
    "gold_axis_2026/apps/V126_POST_RECOVERY_VERIFICATION.md",
    "gold_axis_2026/apps/V127_DEPLOYMENT_SNAPSHOT_VERIFICATION.md",
    "gold_axis_2026/apps/V129_REPLAY_FALLBACK_VERIFICATION.md",
    "gold_axis_2026/apps/V130_FINAL_VERIFICATION.md",
    "gold_axis_2026/apps/aug31_replay_expansion_display.py",
    "gold_axis_2026/apps/aug31_replay_expansion_snapshot.json",
    "gold_axis_2026/apps/aug31_replay_expansion_source.py",
    "gold_axis_2026/apps/aug31_state_replay_snapshot.json",
    "gold_axis_2026/apps/aug31_state_replay_source.py",
    "gold_axis_2026/apps/test_aug31_replay_expansion_display.py",
    "gold_axis_2026/apps/test_aug31_state_replay_source.py",
    "gold_axis_2026/apps/test_replay_snapshot_fallback_v129.py",
    "gold_axis_2026/apps/test_ui_manifest_consistency_v126.py",
    "gold_axis_2026/apps/test_v132_monthly_origin_contract.py",
    "gold_axis_2026/apps/mobile_ui_contract.py",
    "gold_axis_2026/apps/test_mobile_ui_contract.py",
    # Superseded replay/stage writers.
    "gold_axis_2026/data_pipeline/aug31_replay_expansion_v2.py",
    "gold_axis_2026/data_pipeline/aug31_replay_expansion_v2_persist.py",
    "gold_axis_2026/data_pipeline/aug31_replay_expansion_v2_persist_fixed.py",
    "gold_axis_2026/data_pipeline/stage4_gvz_risk_context_issue.py",
    "gold_axis_2026/data_pipeline/stage4_input_readiness_audit.py",
    "gold_axis_2026/data_pipeline/stage4_monthly_direction_issue.py",
    "gold_axis_2026/data_pipeline/stage4_monthly_direction_rehearsal.py",
    "gold_axis_2026/data_pipeline/stage4_tactical_context_issue.py",
    "gold_axis_2026/data_pipeline/stage4_tactical_rehearsal.py",
    "gold_axis_2026/data_pipeline/stage4b_forecast_state_readiness.py",
    "gold_axis_2026/data_pipeline/stage4b_forecast_writer_schema_audit.py",
    "gold_axis_2026/data_pipeline/stage4b_multi_expert_patch_v7_month_end_issuer.py",
    "gold_axis_2026/data_pipeline/stage4b_patch_v7_first_shadow_issuer.py",
    "gold_axis_2026/data_pipeline/stage4b_patch_v7_runner_core.py",
    "gold_axis_2026/data_pipeline/stage4b_patch_v7_writer_rehearsal.py",
    "gold_axis_2026/data_pipeline/verify_ops_integrity_v130.py",
    # Superseded Macro Event V1 implementation. V2 reads the persisted frozen data directly.
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_alfred_construction_audit.py",
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_consensus_provider_audit.py",
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_investing_coverage_audit.py",
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_machine_preflight.py",
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_research_neon_ingest.py",
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_score_replay.py",
    "gold_axis_2026/data_pipeline/macro_event_successor_v1_sources.py",
    "gold_axis_2026/data_pipeline/source_contract_macro_event_successor_v1.json",
    "gold_axis_2026/tests/test_macro_event_successor_v1_consensus_provider_audit.py",
    "gold_axis_2026/tests/test_macro_event_successor_v1_investing_coverage_audit.py",
    "gold_axis_2026/tests/test_macro_event_successor_v1_research_neon_ingest.py",
    "gold_axis_2026/tests/test_macro_event_successor_v1_score_replay.py",
    "gold_axis_2026/tests/test_macro_event_successor_v1_sources.py",
    "gold_axis_2026/tests/test_replay_macro_event_successor_v1_score.py",
    # Superseded apply/reconcile helpers.
    "gold_axis_2026/tools/apply_historical_replay_data_contract_v128.py",
    "gold_axis_2026/tools/apply_mobile_db_read_cache_v128.py",
    "gold_axis_2026/tools/apply_replay_snapshot_fallback_v129.py",
    "gold_axis_2026/tools/apply_september_replay_ui_v128.py",
    "gold_axis_2026/tools/apply_stage4_forecast_audit_v1_8.py",
    "gold_axis_2026/tools/apply_v127_deployment_snapshot_recovery.py",
    "gold_axis_2026/tools/apply_v130_aug31_state_replay_ui.py",
    "gold_axis_2026/tools/reconcile_stage4_prospective_origin_v1_9.py",
    "gold_axis_2026/tools/reconcile_stage4_xau_pipeline_v1_7.py",
    "gold_axis_2026/tools/replay_macro_event_successor_v1_score.py",
}

DOC_PREFIXES = (
    "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_",
    "GOLD_CONTROL_AUG31_STATE_REPLAY_DISPLAY_",
    "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V1_",
    "GOLD_CONTROL_STAGE4_",
    "GOLD_CONTROL_STAGE4B_",
    "GOLD_CONTROL_V130_",
    "GOLD_CONTROL_V131_",
    "GOLD_CONTROL_V132_",
    "GOLD_CONTROL_VW_MIDAS_SVR_XAU_SUCCESSOR_V2_",
)

WORKFLOW_TOKENS = (
    "aug31-state-replay-v130",
    "historical-replay-data-layer-v128",
    "mobile-db-cache-v128",
    "september-replay-v128",
    "stage4b-",
    "v126-",
    "v127-",
    "v130-",
    "v139-",
    "v140-",
)


def rm(path: Path, removed: list[str]) -> None:
    if not path.exists() or path.is_dir():
        return
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    subprocess.run(["git", "rm", "-f", "--", rel], cwd=ROOT, check=True)
    removed.append(rel)


def patch(path: Path, replacements: list[tuple[str, str]], changed: list[str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = text
    for old, repl in replacements:
        new = new.replace(old, repl)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)).replace("\\", "/"))


def main() -> int:
    removed: list[str] = []
    changed: list[str] = []

    for rel in sorted(DELETIONS):
        rm(ROOT / rel, removed)

    for path in GC.glob("*.md"):
        if path.name.startswith(DOC_PREFIXES):
            rm(path, removed)

    workflows = ROOT / ".github" / "workflows"
    if workflows.exists():
        for path in workflows.glob("*.yml"):
            if any(token in path.name for token in WORKFLOW_TOKENS):
                rm(path, removed)

    stage4b = GC / "stage4b"
    if stage4b.exists():
        for path in sorted(stage4b.rglob("*"), reverse=True):
            if path.is_file():
                rm(path, removed)

    for pyc in GC.rglob("*.pyc"):
        rm(pyc, removed)

    patch(
        GC / "data_pipeline" / "data_evidence_spine_runtime_bootstrap.py",
        [
            ("# v1.39 current governed inventory.", "# v1.41 current governed inventory."),
            ("CANONICAL_MANIFEST_RUNTIME_STATUS_V140", "CANONICAL_MANIFEST_RUNTIME_STATUS_V141"),
            ("DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_V140_PASS", "DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_V141_PASS"),
        ],
        changed,
    )
    patch(
        GC / "data_pipeline" / "multi_expert_forecast.py",
        [
            ('MANIFEST_VERSION = "1.40"', 'MANIFEST_VERSION = "1.41"'),
            (
                'status_reason="Source-bound V2 passed the frozen 43-origin source/materiality/non-inferiority audit; issuance waits for an eligible prospective month-end origin.",',
                'status_reason="Current September H=1 historical-replay reference is available; the executable remains eligible for later origin-time issuance under its frozen source contract.",',
            ),
        ],
        changed,
    )

    report = {"removed": removed, "changed": changed, "removed_count": len(removed), "changed_count": len(changed)}
    Path("current_surface_cleanup_v141.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
