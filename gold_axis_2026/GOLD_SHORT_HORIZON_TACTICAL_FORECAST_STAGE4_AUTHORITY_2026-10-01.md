# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 4 TFT Multi-Horizon Challenger Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Test whether a constrained **Temporal Fusion Transformer (TFT)** can extract useful joint H1/H3/H5 structure that is not captured by the frozen tabular boosting models or by the rejected TCN/GRU/BiGRU challengers.

This is the final deep-learning challenger stage before forecast-head reconciliation.

## 2. Library / implementation authority

Implementation:
- PyTorch Forecasting **v1.8.0**
- official `TemporalFusionTransformer`
- Lightning **v2.6.6**
- CPU execution.

The project uses the stable v1 model API, not the WIP v2 model API.

## 3. Targets

At each Gold origin t:

Continuous:
- H1 = log(P[t+1]/P[t])
- H3 = log(P[t+3]/P[t])
- H5 = log(P[t+5]/P[t]).

Categorical:
- UP1 = 1 iff H1 > 0
- UP3 = 1 iff H3 > 0
- UP5 = 1 iff H5 > 0.

The TFT program consists of two joint multi-target models per refit:

### TFT-CLASS
Jointly predicts:
- UP1
- UP3
- UP5

using three CrossEntropy targets.

### TFT-QUANT
Jointly predicts:
- H1 Q10/Q50/Q90
- H3 Q10/Q50/Q90
- H5 Q10/Q50/Q90

using three QuantileLoss targets.

Point-return prediction for each horizon is the TFT Q50 output.

This separation avoids mixing classification logits and quantile regression in one heterogeneous loss while still testing joint H1/H3/H5 learning.

## 4. Data authority

Input panel:
- governed Stage-0 readiness panel
- artifact 11166972412.

Sequence feature contract:
- **CORE3 only**
  - Gold r1/r3/r5/r10/r21/sigma20
  - Silver r1/r5/r21/age_days
  - Platinum r1/r5/r21/age_days.

Excluded:
- Palladium
- raw external levels
- transformed external blocks

because Stage 2 did not promote them.

## 5. Chronology

- background/train: 2011-2021
- DEV selection: 2022-2024
- 2025: frozen / forbidden
- 2026: no selection.

Joint training row eligibility:
- because H1/H3/H5 are learned together, a training row may enter only after its **H5 target is fully matured**.

No random split.

## 6. Encoder / refit contract

Encoder lookback:
- **L60 only**

Reason:
- Stage 3 already tested L20/L60 compact sequence encoders;
- TFT is allowed one constrained lookback only to avoid multiplying selection degrees of freedom.

Refit cadence:
- every **63 DEV Gold origins** (approximately quarterly)
- expanding matured history
- up to 12 refits across 2022-2024.

This slower cadence is computationally required and is conservative versus the frozen classical 5-origin benchmark.

## 7. TFT architecture

Frozen constrained architecture:

- hidden_size = **8**
- hidden_continuous_size = **4**
- attention_head_size = **1**
- lstm_layers = **1**
- dropout = **0.10**
- causal_attention = True
- share_single_variable_networks = False
- optimizer = AdamW
- learning_rate = **0.001**
- weight_decay = **0.0001**
- max encoder length = 60
- max prediction length = 1.

The model treats H1/H3/H5 as three joint targets at the same forecast origin. Decoder length is one because the three horizons are explicit target heads rather than decoder positions.

Parameter count must be reported.
If either TFT model exceeds **30,000 trainable parameters**, the run is invalid and Stage 4 must stop.

## 8. Training

For each refit:

- chronological matured training pool
- final 15% of matured rows used as validation
- no shuffling across chronology for validation split
- training dataloader may shuffle training windows
- batch size = 64
- max epochs = **20**
- early stopping patience = **4**
- minimum improvement = 1e-4
- gradient clip = 0.1
- fixed seed = 20261001
- deterministic execution where supported
- no learning-rate finder
- no Optuna / hyperparameter tuning.

The best validation checkpoint is used for the next DEV block.

## 9. Input timing

All CORE3 features on decoder/origin row are known at origin t.

No t+1 or later feature enters the decoder.

Targets are stored for supervised evaluation but never included as input features.

## 10. Classical references

### H3 frozen references — binding

Direction:
- CORE3 / XGB_CLASS
- Brier **0.246458**
- log loss from Stage 2 frozen result.

Return:
- GOLD_ONLY / LGBM_REG
- MAE **0.013384**
- RMSE from Stage 2 frozen result.

Quantile:
- GOLD_ONLY / LGBM_QUANT
- mean pinball **0.004295**.

### H1 / H5

Use authoritative Stage-1 aggregate artifact 11167138282.

For direction:
- compare against both strongest Stage-1 model and strongest frozen probability baseline;
- H1/H5 cannot be called promoted unless the original Stage-1 direction gate is cleared.

For return and quantile:
- compare against Stage-1 best classical candidate and baseline.

## 11. Promotion gates

### H3 direction
TFT replaces XGB only if:
- Brier improves >=0.5% relative
- log loss not worse
- no DEV year Brier deteriorates >3%.

### H3 point return
TFT Q50 replaces LightGBM only if:
- MAE improves >=0.5%
- RMSE not worse
- no DEV year MAE deteriorates >3%.

### H3 quantile
TFT replaces LightGBM Quantile only if:
- mean Q10/Q50/Q90 pinball improves >=0.5%
- no DEV year mean pinball deteriorates >3%
- quantile crossing rate after output = 0
- report pre-repair crossing rate if any repair is required.

### H1/H5
Supporting challenger status:
- apply the same metric family;
- direction must additionally clear the original Stage-1 baseline PASS gate.

## 12. Robustness views

Report:
- aggregate DEV
- 2022 / 2023 / 2024
- pre-2022 sigma20 LOW/MID/HIGH buckets
- refit diagnostics
- parameter count
- mean epochs
- prediction dispersion
- quantile coverage.

No post-hoc volatility gate.

## 13. Decision logic

If TFT promotes no H3 head:
- deep-learning challenger program is **CLOSED**
- retain classical boosting engine
- move to forecast-head reconciliation / tactical allocation design.

If TFT promotes one or more H3 heads:
- promote only those specific heads
- retain classical model for non-winning heads
- then proceed to head reconciliation.

2025 remains frozen until Stage 4 is fully frozen.

## 14. Required artifacts

- TFT classification OOS predictions
- TFT quantile OOS predictions
- aggregate metrics
- annual metrics
- volatility metrics
- training diagnostics
- H1/H3/H5 promotion decisions
- immutable hashes.
