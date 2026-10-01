# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 3 Sequence Challenger Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Test whether compact origin-safe sequence models improve the frozen H3 classical forecast heads without using 2025.

Sequence challengers:
1. TCN
2. GRU
3. BiGRU.

TFT remains blocked until Stage 3 is resolved.

## 2. Frozen target and evaluation population

Horizon:
- **H3 only**

Target:
- `r3f = log(P[t+3]/P[t])`
- direction = 1 iff r3f > 0
- quantiles = Q10 / Q50 / Q90.

Evaluation:
- DEV 2022-2024
- same 749 H3 origins as Stages 1-2
- 2025 forbidden for selection.

## 3. Frozen classical references

Direction:
- CORE3 / XGB_CLASS
- Stage-2 corrected Brier 0.246458.

Point return:
- GOLD_ONLY / LGBM_REG
- Stage-2 corrected MAE 0.013384.

Quantiles:
- GOLD_ONLY / LGBM_QUANT
- Stage-2 corrected mean pinball 0.004295
- stability caution: aggregate edge concentrated in 2024/high-volatility DEV.

Classical references come from authoritative corrected Stage-2 artifact 11167744845.

## 4. Sequence input contract

All Stage-3 sequence challengers use **CORE3** history:

Gold:
- r1/r3/r5/r10/r21
- sigma20.

Silver:
- r1/r5/r21
- age_days.

Platinum:
- r1/r5/r21
- age_days.

Reason:
- CORE3 is the frozen H3 direction contract;
- it preserves full 2011-2024 history;
- Palladium is excluded after Stage 2 rejection;
- external transformed blocks are excluded after Stage 2 rejection.

Using CORE3 for all sequence heads is a preregistered challenger design. If a sequence head wins, later ablation may separate architecture gain from cross-metal input gain.

## 5. Lookback screen

Preregistered lookbacks:
- **L20** = 20 Gold origins
- **L60** = 60 Gold origins.

No other lookback may be inserted after seeing DEV results.

## 6. Refit protocol

To make compact neural evaluation computationally feasible while retaining chronology:

- refit every **20 DEV Gold origins**
- expanding matured training history
- full H3 label maturity required
- each sequence ends at the forecast origin t
- no sequence contains t+1 or later observations.

The classical reference is the frozen 5-origin-refit benchmark from Stage 2.

This makes challenger comparison conservative with respect to refit frequency; classical metrics are not weakened or recomputed to match the slower neural cadence.

## 7. Feature preprocessing

At each neural refit:
- compute feature medians from training sequences only;
- fill missing feature values using training medians only;
- standardize each feature using training mean/std only;
- apply the same frozen transform to the next DEV block.

No future/global scaler.

Age fields are treated as ordinary standardized numeric inputs.

## 8. Compact architectures

### TCN
- input channels = CORE3 features
- Conv1d 14 -> 16, kernel 3, dilation 1, causal padding/cropping
- ReLU
- dropout 0.10
- Conv1d 16 -> 16, kernel 3, dilation 2, causal padding/cropping
- ReLU
- dropout 0.10
- last-time-step representation.

### GRU
- one GRU layer
- hidden size 16
- unidirectional
- last hidden state
- no recurrent stack.

### BiGRU
- one bidirectional GRU layer
- hidden size 12 per direction
- concatenate final forward/backward hidden states.

BiGRU is allowed because both directions operate only inside the fully observed past lookback window. It never reads data after forecast origin t.

## 9. Multi-head outputs

Each architecture/lookback produces jointly:

1. direction logit
2. standardized point-return estimate
3. Q10 standardized return
4. Q50 standardized return
5. Q90 standardized return.

Quantile order is enforced at inference by sorting the three predicted quantiles; crossing frequency before sorting is reported.

## 10. Loss

Training target return is standardized using training-only mean/std.

Joint loss:

- BCE(direction)
- + 0.50 * MSE(standardized point return)
- + 0.50 * mean pinball(Q10,Q50,Q90 on standardized return).

No loss-weight search.

## 11. Optimizer / training

- Adam
- learning rate = 0.001
- weight decay = 0.0001
- batch size = 64
- maximum epochs = 30
- chronological validation = last 15% of matured training sequences
- early stopping patience = 5
- minimum 5 epochs
- restore best validation-loss weights
- fixed seed = 20261001
- CPU deterministic execution where supported.

No hyperparameter tuning.

## 12. Promotion gates

A sequence challenger may replace a classical head only if:

### Direction
- Brier improves >=0.5% relative to 0.246458
- log loss not worse than classical
- no DEV year Brier deterioration >3% relative to classical.

### Point return
- MAE improves >=0.5% relative to 0.013384
- RMSE not worse than classical
- no DEV year MAE deterioration >3%.

### Quantile
- mean Q10/Q50/Q90 pinball improves >=0.5% relative to 0.004295
- no DEV year mean pinball deterioration >3%
- Q10/Q50/Q90 ordered after inference repair
- pre-repair crossing rate reported.

If multiple challenger configurations pass one head:
- select best primary-metric improvement;
- if within 0.25 percentage points, select the simpler architecture in order:
  GRU -> TCN -> BiGRU, then shorter L20 over L60.

Different heads may select different sequence configurations.

## 13. Robustness reporting

Mandatory:
- aggregate DEV
- 2022 / 2023 / 2024
- pre-2022 sigma20 LOW/MID/HIGH diagnostic
- parameter count
- mean epochs used
- convergence/failure count.

No post-hoc volatility gate.

## 14. Decision logic

- If no sequence head passes: retain all classical Stage-2 heads and proceed to TFT only if justified as a distinct multi-horizon/distribution architecture.
- If one or more heads pass: freeze only the winning head replacements; non-winning heads remain classical.
- 2025 stays frozen until sequence/TFT challenger program is complete.

## 15. Required outputs

- prediction-level OOS table per architecture/lookback
- head metrics
- annual metrics
- volatility metrics
- training diagnostics
- promotion decisions
- immutable hashes.
