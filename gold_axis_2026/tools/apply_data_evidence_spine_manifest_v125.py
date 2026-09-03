from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{count}:{old[:120]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    text = MANIFEST.read_text(encoding="utf-8")
    if "**Manifest version:** 1.25" in text and "FROZEN_DATA_EVIDENCE_SPINE_V1" in text:
        print("MANIFEST_V125_DATA_EVIDENCE_SPINE_ALREADY_APPLIED")
        return 0

    text = replace_once(text, "**Manifest version:** 1.24", "**Manifest version:** 1.25")

    old_state = """Current forecast-state database reconciliation on 2026-09-01:

- `forecast_input_snapshots`: **0 rows**;
- `derived_feature_snapshots`: **1 row** — `MONTHLY_DIRECTION_3M`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`;
- `monthly_forecast_contracts`: **0 rows**;
- append-only UPDATE/DELETE guard coverage: **3/3 tables**;
- no historical file-backed forecast may be backfilled and relabeled as if it had existed prospectively in Neon.

Evidence: read-only reconcile run `33518909613`, plus the guarded monthly-direction bootstrap issuance run `33516396253`. The first future H=1 `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast must still be stored before outcome realization with immutable inputs and provenance.
"""
    new_state = """Current production data-plane reconciliation on 2026-09-03 before Data Evidence Spine V1 production migration:

- `forecast_input_snapshots`: **0 rows**;
- `monthly_expert_forecasts`: **0 rows**;
- `monthly_forecast_contracts`: **0 rows**;
- `decision_signal_snapshots`: **0 rows**;
- `decision_runs`: **0 rows**;
- `decision_events`: **0 rows**;
- `derived_feature_snapshots`: **7 immutable component-context rows** — `MONTHLY_DIRECTION_3M`, `FAST_STATE`, `SLOW_STATE`, `GVZ_VALUE`, `GVZ_CAP`, `GVZ_PANIC`, `GVZ_REGIME`;
- no historical file-backed forecast or decision may be backfilled and relabeled as if it had existed prospectively in Neon.

The first future H=1 `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` expert forecast must still be stored before outcome realization with immutable inputs and provenance. Data Evidence Spine V1 migration status at this manifest candidate is `PREPARED_TEMP_BRANCH_PASS_PRODUCTION_NOT_APPLIED`; canonical production status must not be changed to APPLIED until the guarded Neon migration and post-migration audit both pass.
"""
    text = replace_once(text, old_state, new_state)

    anchor = """---

# 17. FRONTEND INFORMATION ARCHITECTURE
"""
    section = """## 16.1 Data Evidence Spine V1 — normalized production evidence chain

Frozen contract:

`gold_axis_2026/GOLD_CONTROL_DATA_EVIDENCE_SPINE_CONTRACT_2026-09-03.md`

Frozen marker:

`FROZEN_DATA_EVIDENCE_SPINE_V1`

Authoritative production migration:

`gold_axis_2026/data_pipeline/schema_patch_data_evidence_spine_neon_v1.sql`

Required production evidence chain:

```text
retrieval/source lineage
        ↓
observations / observations_as_of(as_of)
        ↓
forecast_input_sets
        ↓
forecast_input_snapshots + forecast_input_set_members
        ↓
monthly_expert_forecasts
        ↓
engine_execution_runs + normalized output links
        ↓
future governed selector / canonical forecast
        ↓
Decision Store
        ↓
read-only application
```

Binding rules:

1. Every future expert forecast must have a non-null `input_set_id`.
2. Expert/input-set identity is enforced by composite foreign key across target, origin, as-of, track, expert, model, evidence class and input fingerprint.
3. Snapshot membership is normalized in `forecast_input_set_members`; the existing `input_snapshot_ids[]` field remains audit-readable but is not the only lineage representation.
4. The application/store must verify that every member snapshot matches input-set origin/target/model identity and that `available_as_of <= as_of` and `retrieved_at <= as_of` before commit.
5. Every issued expert output must be linked to exactly one `engine_execution_runs` row in the same database transaction.
6. All 12 governed motors have a runtime ledger state even when the legitimate state is `WAITING`, `BLOCKED` or `NOT_PROVEN`; status-only rows must never fabricate outputs.
7. `latest_engine_runtime_state` and `data_evidence_spine_health_v1` are read-only observability surfaces; neither is a selector or final-decision authority.
8. `forecast_input_sets`, membership and engine runtime/output-link tables are append-only using the existing proven Gold Control mutation-rejection function.
9. `canonical_latest` and `usable_observations` remain current-state convenience surfaces only; historical/forward reconstruction must use `observations_as_of(as_of)` or a sealed immutable input set.
10. Existing `derived_feature_snapshots` rows must not be edited or prospectively relabeled during runtime-ledger bootstrap.
11. Decision Store V1 is retained but remains empty while expert selection and position mapping are not proven. Future Decision Store V2 normalized binding status is `BLOCKED_DECISION_STORE_V2_SELECTION_CONTRACT`.
12. UI continues to use `SET TRANSACTION READ ONLY`. A dedicated least-privilege DB reader role is desirable defense-in-depth but is `NOT_PROVEN_PROVISIONED` until separately created and tested.

Migration acceptance is fail-closed: production application is forbidden unless the temporary Neon migration branch preserves existing rows, accepts a valid synthetic evidence chain, rejects identity/FK/immutability violations, and the production preflight still confirms zero pre-existing expert/input rows that would require reconciliation.

Migration status for this candidate:

`PREPARED_TEMP_BRANCH_PASS_PRODUCTION_NOT_APPLIED`

---

# 17. FRONTEND INFORMATION ARCHITECTURE
"""
    text = replace_once(text, anchor, section)
    MANIFEST.write_text(text, encoding="utf-8")
    print("MANIFEST_V125_DATA_EVIDENCE_SPINE_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
