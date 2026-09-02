# GOLD CONTROL — CAUSAL PATCH R1 REPRO V1 MODEL FREEZE

**Date:** 2026-09-02  
**Model ID:** `CAUSAL_PATCH_R1_REPRO_V1`  
**Evidence status:** `HISTORICAL_REPLAY_ELIGIBLE; PROSPECTIVE_ISSUER_NOT_YET_READY`

## 1. Identity

This model is a new deterministic, causal, reproducible implementation in the retained Causal Patch/PatchTST family. It is **not** the archived `Causal PatchTST Gold R1` executable identity and must never be relabelled as that historical executable unless exact identity is independently proven.

Frozen code/artifact lineage:

- implementation path: `gold_axis_2026/tools/causal_patch_r1_repro_v1.py`;
- implementation Git blob SHA: `c4d2fd507b2621d8ad7dac41f10410b46747d478`;
- implementation introduction commit: `6e72ae690022a264c226597c69776518fe27c3a8`;
- pre-2023 geometry freeze commit: `a12e83a3e26b3c69220af4025405b747b9fc8aec`;
- locked replay evidence commit: `f9274a1`;
- geometry artifact blob SHA: `c65fa295d5ce5ac669ee7b444bd2e19a650bcb6b`;
- locked replay evidence blob SHA: `b57986f356389ec5cb2afbdfc58aca2d13470f45`;
- CORE5 historical artifact SHA256: `48678809e6506b049a2c6b215929a807e5b88fd21126a1d51703387376efcebb`;
- pinned historical daily-metal source commit: `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`.

## 2. Frozen geometry

Selected without the locked 2023–2026 score window:

- daily lookback `L=252`;
- patch length `P=21`;
- hidden dimension `D=32`;
- development train end `2020-12`;
- development validation `2021-01→2022-12`;
- development return MAE `0.024503217715495115`.

The locked 2023-01→2026-07 window was not used for geometry selection.

## 3. Locked replay evidence

GitHub Actions:

- geometry selection run `33600168927`, job `100151896585`, `SUCCESS`;
- locked replay run `33600343405`, job `100152429384`, `SUCCESS`.

Locked replay:

- N = 43;
- target reconciliation = `43/43`;
- Random Walk reconciliation = `43/43`;
- future information used = `false`;
- deterministic second full rerun max absolute difference = `0`;
- forecast-ledger writes = `NONE`;
- decision-store writes = `NONE`.

Performance:

| Model/evidence | MAPE % | MAE |
|---|---:|---:|
| `CAUSAL_PATCH_R1_REPRO_V1` | 3.1082537220 | 101.6606604402 |
| `RW_R1` | 3.3023220233 | 107.4651162791 |
| archived Patch reference | 3.0746698377 | 101.6591968894 |
| audited VW reference | 2.6721495778 | 85.1347018619 |

The new model passes its pre-frozen historical performance gate because both MAPE and MAE are lower than RW on the same 43 months.

Decision:

`PATCH_R1_REPRO_V1_HISTORICAL_REPLAY_ELIGIBLE`

## 4. What this freeze does not prove

This freeze does not yet authorize a prospective forecast because historical replay used locked historical inputs whose **future operational continuation semantics must still be proven**.

Before an immutable forecast input snapshot can be issued at an eligible future origin, the operational input bridge must prove a reproducible continuation for:

1. monthly macro block semantics corresponding to historical `fedfunds`, `nasdaq`, `usdcny`, `gpr`;
2. daily Gold/Silver/Platinum/Palladium price/return block beyond the pinned historical source commit;
3. exact origin cut-off and availability rules;
4. source/version hashes inside the future immutable snapshot.

Until that bridge passes:

`PROSPECTIVE_ISSUER_NOT_YET_READY`

No September 2026 forecast may be backdated.
