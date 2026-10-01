# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 4 TFT Multi-Horizon Probabilistic Challenger Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / NO_TFT_PROMOTION / DEEP-LEARNING CHALLENGER PROGRAM CLOSED**  

**Primary TFT workflow:** Gold Short Horizon Stage4 TFT Challenger  
**Primary run:** **36889006614**

Scientific task artifacts:
- TFT-CLASS: **11176206620**
  - digest: `sha256:15e50e711be88c552dd970eaf59440cb85ce73a79a346592ab89098597f9dba2`
- TFT-QUANT: **11176830553**
  - digest: `sha256:115cc80bf1fdcde9eac3c8cfb6a96371f11f914067e74d0b4d39e1723c00079c`

**Authoritative aggregate V2 workflow:** Gold Short Horizon Stage4 TFT Aggregate V2  
**Aggregate V2 run:** **36890974544**  
**Aggregate V2 artifact:** **11176262943**  
**Aggregate digest:** `sha256:93de732490a5cddebe842089e89cd03056f5c09ed2ef13c473d1ff3d3090d245`

**Authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE4_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

The constrained official PyTorch Forecasting Temporal Fusion Transformer does **not** improve any frozen H3 forecast head enough to earn promotion.

Retain H3 classical engine:

- **Direction:** CORE3 / XGB_CLASS
- **Point return:** GOLD_ONLY / LGBM_REG
- **Quantile distribution:** GOLD_ONLY / LGBM_QUANT.

Therefore:

> **The deep-learning challenger program is closed for the current data/target contract.**

Already rejected:
- TCN
- GRU
- BiGRU
- TFT.

No further deep architecture should be added without materially new data, target design, or explicit project reopening.

2025 remains frozen.

## 2. TFT design actually tested

This was not a generic transformer approximation.

Implementation:
- PyTorch Forecasting v1.8.0
- official `TemporalFusionTransformer`
- Lightning v2.6.6.

Two joint H1/H3/H5 TFTs were fit:

### TFT-CLASS
Joint targets:
- UP1
- UP3
- UP5.

### TFT-QUANT
Joint targets:
- H1 Q10/Q50/Q90
- H3 Q10/Q50/Q90
- H5 Q10/Q50/Q90.

Point return:
- Q50 of the corresponding horizon.

Input:
- CORE3 only.

Encoder:
- 60 Gold origins.

Refit:
- every 63 DEV origins
- 12 expanding chronological refits.

2025 was not used.

## 3. Architecture scale

Frozen architecture:
- hidden_size = 8
- hidden_continuous_size = 4
- attention heads = 1
- LSTM layers = 1
- dropout = 0.10.

Trainable parameters:
- TFT-CLASS: **10,712**
- TFT-QUANT: **10,739**.

Both are well below the frozen 30,000-parameter ceiling.

Training:
- TFT-CLASS mean epochs: **8.3**
- TFT-QUANT mean epochs: **14.9**.

Thus rejection is not due to an oversized transformer.

## 4. H3 binding comparison

| Head | TFT | Frozen classical | Relative vs classical | Gate | Decision |
|---|---:|---:|---:|---|---|
| Direction Brier | 0.252751 | **0.246458** | **-2.55%** | FAIL | **RETAIN XGB** |
| Point-return MAE | 0.013360 | **0.013384** | **+0.18%** | FAIL | **RETAIN LightGBM** |
| Quantile mean pinball | 0.004345 | **0.004295** | **-1.16%** | FAIL | **RETAIN Quantile LightGBM** |

H3 point-return is numerically slightly better in MAE, but the frozen promotion requirement is +0.5%.

The gain is only **+0.18%**, therefore it is not promotable.

## 5. H3 direction details

TFT-CLASS:
- Brier: **0.252751**
- log loss: **0.698990**
- accuracy: **50.87%**
- prediction SD: 0.0481.

Frozen XGBoost:
- Brier: **0.246458**.

Annual TFT Brier:
- 2022: 0.252587
- 2023: **0.262078**
- 2024: 0.243475.

Relative to frozen classical by year:
- 2022: **-2.41%**
- 2023: **-4.88%**
- 2024: **-0.28%**.

Therefore H3 direction fails:
- aggregate gate
- log-loss co-primary
- annual >3% deterioration guard in 2023.

No direction promotion.

## 6. H3 point-return details

TFT Q50:
- MAE: **0.0133596**
- RMSE: **0.0173594**.

Frozen classical:
- MAE: **0.0133844**
- TFT relative MAE improvement: **+0.18%** only.

Annual relative MAE change versus classical:
- 2022: **-1.90%**
- 2023: **+0.67%**
- 2024: **+1.33%**.

Annual guard passes, and RMSE is not worse.

However the primary +0.5% promotion gate does not pass.

Therefore:
**retain Gold-only LightGBM point-return head.**

## 7. H3 quantile details

TFT:
- Q10 pinball: 0.003017
- Q50 pinball: 0.006680
- Q90 pinball: 0.003337
- mean pinball: **0.004345**.

Frozen classical:
- mean pinball: **0.004295**.

Relative:
- **-1.16%**.

Coverage:
- Q10: 13.35%
- Q50: 47.80%
- Q90: 88.12%.

Quantile crossing:
- after output ordering: **0%**
- pre-repair: **0%**.

Annual relative mean-pinball change:
- 2022: -1.92%
- 2023: -2.11%
- 2024: +0.15%.

The model is technically coherent but less accurate than frozen Quantile LightGBM.

No quantile promotion.

## 8. H1 result

| Head | TFT | Classical | Relative |
|---|---:|---:|---:|
| Direction Brier | 0.254283 | 0.248528 | **-2.32%** |
| Return MAE | 0.008888 | 0.008596 | **-3.39%** |
| Quantile pinball | 0.002948 | 0.002869 | **-2.77%** |

H1:
- no TFT head passes.

## 9. H5 result

| Head | TFT | Classical | Relative | Supporting gate |
|---|---:|---:|---:|---|
| Direction Brier | 0.253825 | 0.248081 | **-2.32%** | FAIL |
| **Return MAE** | **0.016585** | 0.016833 | **+1.47%** | **PASS** |
| Quantile pinball | 0.005440 | 0.005407 | **-0.61%** | FAIL |

Important secondary finding:

> TFT Q50 does improve the H5 point-return MAE by about **1.47%** versus the Stage-1 classical H5 return candidate.

This is retained as **supporting challenger evidence**, but it does not change the main architecture because:
- H5 direction fails;
- H5 quantile fails;
- H3 remains the only horizon with all three classical heads passing;
- Stage 4 authority makes H3 promotion the binding criterion for keeping the deep-learning program open.

The H5 point-return result may be revisited during horizon/head reconciliation, but does not authorize an H5 tactical rule by itself.

## 10. Why joint multi-horizon TFT did not win

The tested hypothesis was materially different from Stage 3:

- Stage 3: single-H3 compact sequence encoders
- Stage 4: joint H1/H3/H5 TFT targets with variable-selection / attention architecture.

Despite joint horizon learning:
- probability calibration deteriorated;
- H3 point-return gain was too small;
- H3 quantiles worsened.

Current evidence therefore continues to favor tabular boosting for the core H3 task.

## 11. Aggregate V2 / technical supersession note

The scientific TFT task jobs in primary run **36889006614** both completed successfully.

The original aggregate job failed only because the artifact-copy shell command encountered the checkpoint subdirectory and used non-recursive `cp`.

No scientific prediction was affected.

Aggregate V2:
- run **36890974544**
- artifact **11176262943**

downloaded the exact frozen CLASS/QUANT artifacts and recomputed the decision without retraining either TFT.

Aggregate V2 is authoritative.

## 12. Aggregate hashes

- `STAGE4_RESULT.md`: `6990e1640b3b5379db7143cedbfbd5a8559e7f15263b1bd21b8e42329aa27524`
- `stage4_tft_comparison.csv`: `1b4258e72dd9e63dec4be3c0de3de267c2a20d63ef24c8195c444d419aad6c18`
- `stage4_all_summaries.json`: `0adef6d6ac39e62f61e3f73261f70c8645f67c82c07d2559210716573bc70a92`.

## 13. Decision

**Stage 4 = COMPLETE / NO_TFT_PROMOTION.**

Deep-learning challenger program:
**CLOSED**.

Frozen current H3 forecast engine:

### Direction
**CORE3 / XGB_CLASS**

### Point return
**GOLD_ONLY / LGBM_REG**

### Distribution
**GOLD_ONLY / LGBM_QUANT**

Supporting non-core evidence:
- H5 TFT Q50 point-return head = aggregate supporting PASS.

No trading rule exists yet.

## 14. Exact next stage

**Stage 5 — Forecast-Head Reconciliation & Tactical Signal Architecture**

Purpose:

Combine the frozen probabilistic direction, point-return and quantile-distribution heads into a coherent origin-level forecast object **without yet optimizing trading P&L**.

Required first questions:
1. Are the three H3 heads mutually consistent at each origin?
2. What does a coherent tactical forecast state look like when:
   - P_UP is high but expected return is weak;
   - expected return is positive but downside Q10 is large;
   - Q50 and direction disagree?
3. Can a preregistered head-consistency rule improve forecast reliability without 2025 tuning?
4. Should H1/H5 remain supporting horizons around the H3 core?
5. How should the H5 TFT return supporting result be represented without allowing it to override failed H5 direction/distribution evidence?

Only after Stage 5 freezes the forecast object may Stage 6 define:
- entry/exit
- transaction costs
- position sizing
- risk-adjusted tactical utility.

2025 remains frozen until the forecast architecture is frozen.
