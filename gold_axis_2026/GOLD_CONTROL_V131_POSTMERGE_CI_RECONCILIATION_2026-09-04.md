# GOLD CONTROL — V1.31 POST-MERGE CI RECONCILIATION

**Freeze date:** 2026-09-04  
**Status:** `FROZEN_V131_POSTMERGE_CI_RECONCILIATION`  
**Authority:** live canonical GitHub + production Neon > project manifest v1.31 > frozen subordinate contracts.

## Purpose

After canonical promotion of `BOCPD_RETURN_SUCCESSOR_V1`, five pre-existing validation/bootstrap/presentation surfaces were stale without indicating a model or production-data failure:

1. `Gold Control Data Evidence Spine V1` still treated any existing forecast input/expert rows as a pre-migration blocker even though the production evidence-spine schema is already migrated and governed historical-replay expert rows now legitimately exist.
2. `Gold Control Mobile UI V1.30 Compatibility Final` still hard-coded manifest version 1.30 and the superseded operational distribution `4 ACTIVE / 3 WAITING / 5 BLOCKED`.
3. `data_evidence_spine_runtime_bootstrap.py` still carried the superseded seed map `4/3/5`; if invoked with `--persist`, it could append stale runtime governance state and therefore had to be reconciled before any future use.
4. `mobile_ui_contract.py` still used the superseded VW empty-state code `BLOCKED_NOT_PROVEN_EXECUTABLE`, while the governed registry and production runtime use `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`.
5. `test_mobile_ui_contract.py` independently pinned that superseded VW empty-state code and therefore had to be updated without weakening the no-forecast/no-winner assertion.

This change-control updates validation/bootstrap/presentation governance semantics only. It does not change model formulas, data-source contracts, model outputs, Decision Store, selector/ensemble locks, position mapping, or current production evidence. No production write is authorized by this reconciliation itself.

## Data Evidence Spine preflight rule

The preflight must distinguish three modes:

- `PRE_MIGRATION`: none of the V1 evidence-spine objects exists. Existing input/expert rows remain a migration blocker because they require reconciliation before first schema application.
- `ALREADY_MIGRATED`: all V1 evidence-spine objects exist. Existing governed rows are allowed at preflight; their referential/PIT/immutability correctness is proved by the immediately following read-only `data_evidence_spine_audit.py` gate.
- `PARTIAL_MIGRATION`: only some V1 objects exist. Fail closed.

In all modes, legacy PIT availability and immutability guards remain mandatory. Decision authority rows remain disallowed by this preflight. No database writes are authorized by preflight.

## Runtime bootstrap rule

The 12-engine bootstrap must reproduce the current governed operational state, not an obsolete recovery snapshot.

Required dry-run/persist target distribution:

- `ACTIVE = 4`: `MONTHLY_DIRECTION_3M`, `FAST`, `SLOW`, `GVZ_RISK`;
- `WAITING = 5`: `CAUSAL_PATCH`, `MOMENTUM_3M`, `RANDOM_WALK`, `EMERGENCY_LEVEL`, `EMERGENCY_REVERSAL`;
- `BLOCKED = 3`: archived `VW_MIDAS_MSVR`, `MACRO_EVENT`, `BOCPD`.

Required recovery semantics include:

- Emergency engines: `WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE`;
- VW: `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`;
- Macro: `BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED`;
- archived BOCPD: `BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`.

The new `BOCPD_RETURN_SUCCESSOR_V1` is **not** a thirteenth current runtime engine and must not replace archived BOCPD in production authority until a separate prospective-promotion contract is satisfied.

## Mobile UI v1.31 rule

The compatibility workflow and UI fallback contract must validate/expose:

- manifest version `1.31`;
- existing frozen display/replay/data-spine/engine-visibility contracts;
- `NOT_PROVEN_EXPERT_SELECTION_RULE`;
- auto selector `OFF`;
- auto ensemble `OFF`;
- `NOT_PROVEN_POSITION_MAPPING`;
- production operational distribution `4 ACTIVE / 5 WAITING / 3 BLOCKED`;
- `CAUSAL_PATCH`, `MOMENTUM_3M`, `RANDOM_WALK`, `EMERGENCY_LEVEL`, `EMERGENCY_REVERSAL` are `WAITING` in current operational authority;
- archived `VW_MIDAS_MSVR`, `MACRO_EVENT`, `BOCPD` remain the three `BLOCKED` operational identities;
- the VW expert-display empty state and its deterministic test fixture equal the governed registry code `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`;
- the new `BOCPD_RETURN_SUCCESSOR_V1` remains research-only and is not inserted into current runtime authority by this CI reconciliation.

## Locks retained

- archived `BOCPD` remains blocked;
- `BOCPD_RETURN_SUCCESSOR_V1` remains research-shadow candidate only;
- no production/ACTIVE promotion;
- direction vote is not added;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- `NOT_PROVEN_POSITION_MAPPING`;
- no BUY/SELL/HOLD/EXIT/REDUCE;
- no Neon mutation.

## Acceptance

Acceptance requires, on the exact feature head and again after canonical promotion:

1. Data Evidence Spine deterministic tests pass, including preflight-mode and runtime-bootstrap status-map tests;
2. read-only production preflight reports `ALREADY_MIGRATED` and passes;
3. read-only production integrity audit passes;
4. 12-engine dry-run bootstrap reports `4/5/3` and `database_writes=NONE`;
5. Mobile UI deterministic tests pass, including expert-display/registry consistency and no-invented-forecast/no-winner behavior;
6. production runtime assertions pass at `4/5/3` with exact blocked/waiting identities;
7. production-backed 390x844 browser QA passes;
8. selector/ensemble/action locks remain intact.
