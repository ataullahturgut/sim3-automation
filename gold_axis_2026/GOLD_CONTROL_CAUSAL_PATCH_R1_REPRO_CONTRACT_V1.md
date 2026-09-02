# GOLD CONTROL — CAUSAL PATCH R1 REPRODUCIBILITY CONTRACT V1

**Date:** 2026-09-02  
**Status:** `FROZEN_BEFORE_LOCKED_REPLAY_SCORE`  
**Candidate ID:** `CAUSAL_PATCH_R1_REPRO_V1`

## 1. Objective

Build one deterministic, causal, reproducible implementation of the retained Causal Patch/PatchTST-style H=1 architecture. This contract restores the agreed forecast-development path and does not claim exact executable identity with the archived Patch artifact.

## 2. H=1 target and origin

- Target: next calendar month's average XAU/USD price.
- Historical target for locked replay: canonical CORE5 monthly gold series; World Bank Pink Sheet is accepted as materially identical historical data-plane lineage but is not relabelled as CORE5.
- Forecast origin: end of the previous completed calendar month.
- Locked score window: 2023-01 through 2026-07, N=43.
- No September-2026 prospective backfill.

## 3. Frozen role registry

- `CAUSAL_PATCH_R1_REPRO_V1`: production-primary candidate, not yet approved.
- `VW_AUDITED_SHADOW_V2`: audited shadow/reference only.
- `MOMENTUM_3M_R1`: direction challenger/context.
- `RW_R1`: mandatory naive benchmark.
- `AUTO_SELECTOR=OFF`.
- `AUTO_ENSEMBLE_PRIMARY=OFF`.

The three-seed median inside one Patch model is stochastic stabilization, not a selector across different model families.

## 4. Source locks

### Monthly canonical block

Locked CORE5 local artifact:

`gold_axis_2026/core5_monthly.csv.gz.b64`

Required variables:

- `gold_monthly`
- `fedfunds`
- `nasdaq`
- `usdcny`
- `gpr`

### Daily precious-metals block

Source:

`github:lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

Required daily metals:

- Gold
- Silver
- Platinum
- Palladium

The exact commit is mandatory. `master`/unversioned fetch is prohibited.

## 5. Origin-safe transformations

For target month `t`, origin month is `p=t-1`, with `pp=t-2`.

Daily block:

1. compute daily log returns using observations no later than origin date;
2. build a trailing lookback tensor;
3. causal decomposition uses only a trailing 21-observation moving mean and residual; no centered filter and no future decomposition information.

Macro block:

- Fed funds: level available at `p` under the locked CORE5 historical contract;
- Nasdaq: log change `p/pp`;
- USD/CNY: log change `p/pp`;
- GPR: conservative publication rule uses period `pp` (`t-2`) rather than target-adjacent current-period GPR;
- GPR normalization must use only GPR history available through `pp`.

All scaler/statistical normalization fits occur inside the training sample for each outer origin.

## 6. Architecture family

Retained causal Patch family:

- input channels: causal trend + residual for four daily metal-return series;
- patch embedding;
- Transformer encoder;
- local Conv1D aggregation;
- concatenated five-element macro block;
- single next-month return output;
- Huber training loss;
- AdamW optimization;
- gradient clipping;
- median of three deterministic seed runs.

No new model family may be introduced inside this contract.

## 7. Architecture selection without locked-window leakage

Candidate geometry is inherited from the retained Axis-3 implementation:

- lookback `L ∈ {126, 252}`;
- patch length `P ∈ {7, 14, 21}` only where present in the retained candidate grid;
- hidden dimension `D ∈ {24, 32}` according to the retained grid.

Architecture selection is performed only on a pre-2023 development block. The 2023-01→2026-07 locked score window may not select `L`, `P`, `D`, training epochs, seed set, loss, macro features, or causal-decomposition rule.

The selected geometry must be printed and frozen in the replay evidence before reporting the 43-month score.

## 8. Locked replay acceptance gates

Hard gates:

1. `SOURCE_PIN_PASS=true`.
2. `TARGET_RECONCILIATION=43/43`.
3. `RW_RECONCILIATION=43/43`.
4. `FUTURE_INFORMATION_USED=false`.
5. second deterministic run produces max absolute prediction difference `<=1e-8`.
6. no forecast-state/decision-store database writes during historical replay.

Performance gates for production-primary candidacy:

- Patch replay MAPE must be lower than RW MAPE on the same 43 months;
- Patch replay MAE must be lower than RW MAE on the same 43 months;
- archived Patch and VW scores are references, not tuning targets;
- failure to reproduce archived Patch forecast values exactly does not permit relabelling the new candidate as the archived executable identity.

If all hard gates pass but the performance gates fail, status is:

`REPRODUCIBLE_PATCH_IMPLEMENTATION_PASS; PRODUCTION_PRIMARY_NOT_APPROVED`

If hard gates and performance gates pass, status is:

`PATCH_R1_REPRO_V1_HISTORICAL_REPLAY_ELIGIBLE`

This is still historical replay, not prospective proof.

## 9. Output evidence

The runner must emit only research/replay artifacts containing:

- selected pre-2023 architecture;
- code/input/source hashes;
- 43 monthly forecasts and actuals;
- RW comparison;
- archived Patch/VW references clearly labelled;
- deterministic rerun check;
- gate result;
- `evidence_class=HISTORICAL_REPLAY`;
- `prospective_claim=false`.

No forecast contract or production decision row may be issued by this replay.
