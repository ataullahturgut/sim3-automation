from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
MULTI_EXPERT = ROOT / "data_pipeline" / "multi_expert_forecast.py"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{count}:{old[:120]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    text = MANIFEST.read_text(encoding="utf-8")
    if "**Manifest version:** 1.25" in text and "FROZEN_DATA_EVIDENCE_SPINE_V1" in text:
        print("MANIFEST_V125_DATA_EVIDENCE_SPINE_ALREADY_APPLIED")
    else:
        text = replace_once(text, "**Manifest version:** 1.24", "**Manifest version:** 1.25")

        old_state = """Current forecast-state database reconciliation on 2026-09-01:

- `forecast_input_snapshots`: **0 rows**;
- `derived_feature_snapshots`: **1 row** — `MONTHLY_DIRECTION_3M`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`;
- `monthly_forecast_contracts`: **0 rows**;
- append-only UPDATE/DELETE guard coverage: **3/3 tables**;
- no historical file-backed forecast may be backfilled and relabeled as if it had existed prospectively in Neon.

Evidence: read-only reconcile run `33518909613`, plus the guarded monthly-direction bootstrap issuance run `33516396253`. The first future H=1 `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast must still be stored before outcome realization with immutable inputs and provenance.
"""
        new_state = """Current production data-plane reconciliation on 2026-09-03 after Data Evidence Spine V1 schema migration:

- `forecast_input_snapshots`: **0 rows**;
- `forecast_input_sets`: **0 rows**;
- `forecast_input_set_members`: **0 rows**;
- `monthly_expert_forecasts`: **0 rows**;
- `monthly_forecast_contracts`: **0 rows**;
- `decision_signal_snapshots`: **0 rows**;
- `decision_runs`: **0 rows**;
- `decision_events`: **0 rows**;
- `derived_feature_snapshots`: **7 immutable component-context rows** — `MONTHLY_DIRECTION_3M`, `FAST_STATE`, `SLOW_STATE`, `GVZ_VALUE`, `GVZ_CAP`, `GVZ_PANIC`, `GVZ_REGIME`;
- `engine_execution_runs`: **0 rows pending canonical runtime bootstrap**;
- Data Evidence Spine immutable guard names: **6/6**;
- expert/input-set composite identity FK: **1/1**;
- orphan input snapshots / expert rows without input set / fingerprint mismatches: **0 / 0 / 0**;
- no historical file-backed forecast or decision was backfilled or prospectively relabeled.

Production Neon migration `5281e7d0-8335-41c5-bff2-a15e2b91b017` was applied successfully to branch `production` (`br-gentle-mouse-b22dzkr1`) after a temporary-branch positive chain test and negative FK/immutability tests. The first future H=1 `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` expert forecast must still be stored before outcome realization with immutable inputs and provenance. Runtime bootstrap is an observability/provenance operation only and remains `PENDING_CANONICAL_BOOTSTRAP` until the canonical code SHA is promoted and the 12-engine post-write audit passes.
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
3. Snapshot membership is normalized in `forecast_input_set_members`; the existing `input_snapshot_ids[]` remains audit-readable but is not the only lineage representation.
4. The application/store must verify that every member snapshot matches input-set origin/target/model identity and that `available_as_of <= as_of` and `retrieved_at <= as_of` before commit.
5. Every issued expert output must be linked to exactly one `engine_execution_runs` row in the same database transaction.
6. All 12 governed motors must have a runtime ledger state even when the legitimate state is `WAITING`, `BLOCKED` or `NOT_PROVEN`; status-only rows must never fabricate outputs.
7. `latest_engine_runtime_state` and `data_evidence_spine_health_v1` are read-only observability surfaces; neither is a selector or final-decision authority.
8. `forecast_input_sets`, membership and engine runtime/output-link tables are append-only using the existing proven Gold Control mutation-rejection function.
9. `canonical_latest` and `usable_observations` remain current-state convenience surfaces only; historical/forward reconstruction must use `observations_as_of(as_of)` or a sealed immutable input set.
10. Existing `derived_feature_snapshots` rows must not be edited or prospectively relabeled during runtime-ledger bootstrap.
11. Decision Store V1 is retained but remains empty while expert selection and position mapping are not proven. Future Decision Store V2 normalized binding status is `BLOCKED_DECISION_STORE_V2_SELECTION_CONTRACT`.
12. UI continues to use `SET TRANSACTION READ ONLY`. A dedicated least-privilege DB reader role is desirable defense-in-depth but remains `NOT_PROVEN_PROVISIONED` until separately created and tested.
13. Production schema migration status is `APPLIED_PRODUCTION_PASS`; migration ID is `5281e7d0-8335-41c5-bff2-a15e2b91b017`.
14. Runtime-ledger bootstrap status at this manifest issue point is `PENDING_CANONICAL_BOOTSTRAP`; it may only link the existing seven persisted context rows and status-only WAITING/BLOCKED engines, with no recalculation or prospective relabeling.
15. Selector, ensemble, canonical forecast issuance and position mapping locks are unchanged: `NOT_PROVEN_EXPERT_SELECTION_RULE`, `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_POSITION_MAPPING`.

Migration acceptance was fail-closed: the temporary Neon migration preserved existing production rows, accepted a valid synthetic evidence chain, rejected expert/input-set identity violations, rejected append-only mutation, and production post-migration integrity remained clean.

Schema migration status:

`APPLIED_PRODUCTION_PASS`

Runtime bootstrap status:

`PENDING_CANONICAL_BOOTSTRAP`

---

# 17. FRONTEND INFORMATION ARCHITECTURE
"""
        text = replace_once(text, anchor, section)
        MANIFEST.write_text(text, encoding="utf-8")
        print("MANIFEST_V125_DATA_EVIDENCE_SPINE_PATCH_PASS")

    model_text = MULTI_EXPERT.read_text(encoding="utf-8")
    if 'MANIFEST_VERSION = "1.25"' not in model_text:
        model_text = replace_once(model_text, 'MANIFEST_VERSION = "1.24"', 'MANIFEST_VERSION = "1.25"')
        MULTI_EXPERT.write_text(model_text, encoding="utf-8")
        print("MULTI_EXPERT_MANIFEST_VERSION_V125_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
