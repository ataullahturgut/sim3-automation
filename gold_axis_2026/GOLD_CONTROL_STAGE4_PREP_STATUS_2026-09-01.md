# GOLD CONTROL — STAGE 4 PREPARATION STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.1  
**Stage:** 4 — Deterministic R4.1 Decision Engine  
**Current status:** `PREPARATION_TESTS_PASS; NOT_COMPLETE_AHEAD_OF_STAGE3`

## 1. Scope

This file records non-mutating Stage 4 preparation only.

The manifest exit criterion for Stage 4 is:

> same frozen input snapshot → same decision state; version and config recorded.

Because Stage 3 production persistence is still blocked, this document does **not** promote Stage 4 to complete.

## 2. Determinism test suite

Added:

`gold_axis_2026/r4_1/tests/test_determinism.py`

Canonical passing commit:

`655d5e6b3ab1d53097e070536197900193bd4ece`

Workflow run:

`33492826842`

Job:

`99808068109`

Result:

`11 passed in 1.17s`

The new tests verify:

- exact repeatability of a full sequential replay;
- prefix state invariance when future rows are appended;
- prefix state invariance when future prices are perturbed;
- frozen classification precedence;
- Emergency month-boundary reset;
- current implementation defaults remain aligned with `frozen_r4_1.json` for Emergency, Tactical and GVZ parameters.

These tests are causal/deterministic safeguards. They are not a performance backtest and do not create prospective evidence.

## 3. Deterministic persistence bridge

Added:

- `gold_axis_2026/data_pipeline/r4_1_decision_adapter.py`
- `gold_axis_2026/data_pipeline/test_r4_1_decision_adapter.py`

The adapter preserves the already-emitted R4.1 descriptive state and binds:

- engine version;
- config version;
- config hash;
- code SHA;
- input snapshot reference;
- forecast contract reference;
- evidence class.

It maps classification to the frozen audit reason vocabulary only. It does **not** recompute the engine state and does **not** infer a trading action.

Latest rollback-only integration run:

- commit: `cba353cd53ec87ba9b1ca8d1d86b51af3b3d5e98`
- workflow run: `33493261858`
- job: `99809509661`

Exact marker:

```text
R4_1_DECISION_ADAPTER_SMOKE_PASS engine_repeatability=PASS state_to_payload=PASS provenance_binding=PASS store_roundtrip=PASS idempotency=PASS action_mapping_guard=PASS rollback=PASS
```

This demonstrates that a deterministic R4.1 emitted state can be converted into the candidate Decision Store contract and read back without changing the classification or inventing an action.

## 4. What is still missing before Stage 4 PASS

Stage 4 is not complete because the production chain does not yet have:

1. the Stage 3 schema permanently installed in Neon;
2. a real immutable production input snapshot used by the R4.1 run;
3. an actual persisted prospective/shadow decision created before outcome realization;
4. post-migration proof that the engine/config/code lineage recorded in the permanent store matches the actual run;
5. operational scheduled decision execution under the frozen production contract.

Therefore:

`STAGE_4 = PREPARATION_TESTS_PASS; NOT_COMPLETE_AHEAD_OF_STAGE3`

Historical deterministic tests remain `HISTORICAL_REPLAY / TEST EVIDENCE`, not `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`.
