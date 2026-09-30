# GOLD MONTHLY — Missing-9 Frozen Transport Reconstruction + Exact-16 SAFE-Veto V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / FROZEN-CONTRACT TRANSPORT RECONSTRUCTION

## 1. Objective

The original cross-model SAFE-veto used a frozen **16-model competitive pool** and improved DEV false-call suppression without losing HIGH/MEDIUM alarms.

A 7-model transport approximation was rejected because the reduced pool materially changed the SAFE signal.

This stage reconstructs transport forecasts for the **9 missing members of the original 16-model pool under their exact frozen model contracts**, then transports the original 16-model SAFE-veto apples-to-apples.

No model selection, alarm tuning, router tuning, or SAFE-veto threshold tuning is allowed.

## 2. Frozen original 16-model competitive pool

Original competitive pool:

1. AOA_ELM
2. BOOST_CATBOOST_ORDERED
3. BOOST_RANDOM_FOREST_ANCHOR
4. ChHHO_ANFIS
5. DE_ABC_RBFNN
6. FULL7_ANN
7. LMC2_RBF_M32
8. PLS1_V1
9. REDUCED4_ANN
10. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1
11. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1
12. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1
13. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1
14. SVR_CURRENT8
15. SVR_DAILY_SUMMARY12
16. SVR_MIXED20

Seven members already have frozen 2025 and 2026 Jan-Jul forecasts.

Nine members require transport reconstruction.

## 3. Missing nine models

### Boosting Stage-1 canonical
- BOOST_CATBOOST_ORDERED
- BOOST_RANDOM_FOREST_ANCHOR

Frozen source artifact:
- **10929616178**
- `gold_monthly_boosting_stage1_canonical_v1_result.json`

Frozen package/environment contract follows the original Stage-1 workflow.

### SVR Stage-2B representation
- SVR_CURRENT8
- SVR_DAILY_SUMMARY12
- SVR_MIXED20

Frozen source artifact:
- **10958140025**
- `gold_monthly_svr_dwt_stage2b_representation_v1_result.json`

Frozen RBF-SVR:
- C=1.0
- epsilon=0.1
- gamma=scale
- train-only X/Y standardization
- common train start 2010-05
- representation definitions unchanged.

### Sequence Stage-1A
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1

Frozen source artifacts:
- CNN_LSTM LB3: **10978660065**
- CNN_LSTM LB6: **10979300075**
- LSTM LB3: **10978271647**
- LSTM LB6: **10978391582**

Frozen architecture/training/seed-selection contract is exactly Stage-1A.

## 4. Reproduction gate before transport use

Every reconstructed model must first reproduce its frozen 33-row DEV behavior.

### Boost/SVR
Require for every DEV target:
- same target/origin;
- same train row count;
- abs(predicted log-return difference) <= **1e-10**;
- abs(price forecast difference) <= **1e-7 USD**.

### Sequence models
Require for every DEV target:
- same target/origin;
- same selected seed;
- same selected best epoch;
- same training sequence count;
- abs(predicted log-return difference) <= **5e-5**;
- abs(price forecast difference) <= **0.10 USD**.

Additionally for every sequence model:
- DEV total ΣAE absolute difference <= **1.0 USD**;
- DEV direction-correct count exactly equal to frozen artifact.

If any reproduction gate fails:
- that model is **NOT TRANSPORT-AUTHORIZED**;
- the exact-16 SAFE-veto transport is not run.

No tolerance may be widened after results.

## 5. Transport target period

Generate origin-safe forecasts for:

- 2025-01..2025-12
- 2026-01..2026-07

Total:
- **19 transport targets per missing model**.

Why stop at 2026-07:
- the seven already-frozen transport-capable members of the original pool are available through 2026-07;
- exact-16 comparability ends there.

Target 2026-08 remains NO_FEATURE for exact-16 SAFE-veto and the frozen Specialist Router passes through unchanged.

## 6. Origin safety

At every target t:
- train only on labels strictly before t;
- use only origin-known features through t-1;
- use the PIT GPR vintage available at the origin;
- target t actual is evaluation only;
- DB remains READ_ONLY.

No 2025/2026 outcome is used to select hyperparameters, model family, representation, lookback, seed grid, SAFE threshold, or router threshold.

## 7. Existing seven frozen transport members

Use exact previously frozen rows for:

- AOA_ELM
- ChHHO_ANFIS
- FULL7_ANN
- REDUCED4_ANN
- DE_ABC_RBFNN
- LMC2_RBF_M32
- PLS1_V1

No retraining or rewriting is required for these seven in this stage.

## 8. Exact-16 SAFE-veto transport

Frozen DEV veto:
- `V2_STRONG_DIRECTION_CONSENSUS`
- ChHHO direction agreement >= **0.80**
- forecast dispersion <= expanding prior-history median
- minimum prior history = **6**.

For DEV:
- use the exact previously frozen 16-model veto rows from artifact **11095060918**.

For 2025..2026-07:
- compute consensus using the exact original 16 model identities;
- seed the expanding dispersion history with the exact frozen DEV feature history from artifact 11095060918;
- update the dispersion history sequentially using only forecast-state features, never outcomes;
- apply the same 80% + prior-median rule unchanged.

## 9. Frozen Specialist Router

Overlay onto exact frozen router V1:
- Specialist Hedge
- eta=0.25
- alpha=0
- tau=0.50
- A/B/C/D/E/G/H/I1/I2/T1_WGC/V2_TRANSITION experts.

Source artifact:
- **11124892942**.

No router recomputation/tuning from transport outcomes.

## 10. Exact transport evaluation

Report separately:

### 2025
- router alone
- router + exact-16 SAFE-veto

### 2026 Jan-Jul
- router alone
- router + exact-16 SAFE-veto

### 2025 + 2026 Jan-Jul
- combined.

Target 2026-08:
- exact-16 SAFE feature = unavailable;
- router decision passes through and is reported separately.

Metrics:
- events
- HIGH hits
- MEDIUM hits
- false calls
- HIGH recall
- elevated recall
- useful-call rate
- false-call rate
- exact rows vetoed.

## 11. Critical preservation checks

The exact-16 transport overlay must report explicitly whether it preserves:

- 2025-02 HIGH (H)
- 2025-09 HIGH (A + V2)
- 2026-06 HIGH (V2-only)
- 2026-08 HIGH (G + V2; pass-through because no exact-16 feature).

These are critical because the rejected 7-model shadow suppressed some of them.

## 12. Transport interpretation

This stage does **not** select/tune the veto on opened outcomes.

Possible transport interpretations:

### EXACT16_TRANSPORT_SUPPORTIVE
- no HIGH is removed in 2025..2026-07; and
- at least one false call is removed.

### EXACT16_TRANSPORT_NEUTRAL
- no HIGH is removed; and
- no false call is removed.

### EXACT16_TRANSPORT_HARMFUL
- any HIGH is removed.

MEDIUM losses are also reported and prevent operational promotion even if no HIGH is lost.

No production authorization is automatic in this stage.

## 13. Governance

Forbidden:
- changing any missing-model frozen contract;
- substituting another model for a failed reconstruction;
- widening reproduction tolerances;
- changing the 16-model pool;
- changing SAFE-veto 80%;
- changing prior-median dispersion rule;
- changing minimum prior history;
- changing Specialist Router eta/tau;
- using 2025/2026 outcomes for selection;
- forecast correction/model switching.

This stage is an apples-to-apples frozen transport reconstruction only.
