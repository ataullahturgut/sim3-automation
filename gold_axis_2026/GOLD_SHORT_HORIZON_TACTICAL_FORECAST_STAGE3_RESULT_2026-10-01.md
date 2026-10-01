# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 3 Sequence Challenger Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / NO_SEQUENCE_PROMOTION**  
**Workflow:** Gold Short Horizon Stage3 Sequence Challengers  
**Run:** **36877156753**  
**Aggregate artifact:** **11169543476**  
**Aggregate artifact digest:** `sha256:a23e21682a6dc4db14c69c33b806f151f9842a9a19cbf0958379611aacd24392`  
**Authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE3_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

Compact sequence models do **not** improve the frozen H3 classical forecast heads.

Retain:

- **Direction:** CORE3 / XGB_CLASS
- **Point return:** GOLD_ONLY / LGBM_REG
- **Quantile distribution:** GOLD_ONLY / LGBM_QUANT.

Rejected as replacements:

- TCN L20
- TCN L60
- GRU L20
- GRU L60
- BiGRU L20
- BiGRU L60.

2025 remains frozen.

## 2. Protocol

Frozen:
- H3 target only
- DEV 2022-2024, n=749
- CORE3 sequence inputs
- lookbacks L20 and L60
- refit every 20 DEV Gold origins
- expanding matured history
- full H3 label-maturity purge
- no 2025 selection
- compact architectures
- fixed seed / training contract.

Each configuration jointly predicted:
- H3 UP probability
- H3 point return
- Q10/Q50/Q90 H3 return distribution.

Total:
- 6 sequence configurations
- 38 chronological refits per configuration
- 228 compact neural fits.

All six matrix jobs completed successfully.

## 3. Frozen classical references

| Head | Classical contract | Primary metric |
|---|---|---:|
| Direction | CORE3 / XGB_CLASS | Brier **0.246458** |
| Return | GOLD_ONLY / LGBM_REG | MAE **0.013384** |
| Quantile | GOLD_ONLY / LGBM_QUANT | Mean pinball **0.004295** |

## 4. Promotion decisions

| Head | Decision | Best sequence | Sequence primary | Classical primary | Relative change |
|---|---|---|---:|---:|---:|
| Direction | **RETAIN CLASSICAL** | GRU-L60 | 0.250025 | 0.246458 | **-1.45%** |
| Return | **RETAIN CLASSICAL** | GRU-L60 | 0.013531 | 0.013384 | **-1.10%** |
| Quantile | **RETAIN CLASSICAL** | TCN-L20 | 0.004422 | 0.004295 | **-2.95%** |

Negative relative change means the sequence challenger is worse than the frozen classical reference.

No head passes the +0.5% sequence promotion gate.

## 5. Direction comparison

Brier, lower is better:

| Configuration | Brier | Relative vs classical | Year gate |
|---|---:|---:|---|
| **Classical CORE3/XGB** | **0.246458** | — | frozen |
| GRU-L60 | 0.250025 | -1.45% | FAIL |
| GRU-L20 | 0.250025 | -1.45% | FAIL |
| TCN-L60 | 0.250735 | -1.74% | FAIL |
| BiGRU-L60 | 0.251115 | -1.89% | PASS yearly only |
| BiGRU-L20 | 0.251984 | -2.24% | FAIL |
| TCN-L20 | 0.252682 | -2.53% | FAIL |

Even the best sequence probability model is materially worse than XGBoost.

Important:
- BiGRU-L60 passes the annual-deterioration guard but still fails because aggregate Brier is worse.
- sequence complexity does not create a superior direction probability.

## 6. Point-return comparison

MAE, lower is better:

| Configuration | MAE | Relative vs classical | Year gate |
|---|---:|---:|---|
| **Classical Gold-only/LightGBM** | **0.013384** | — | frozen |
| GRU-L60 | 0.013531 | -1.10% | PASS yearly only |
| GRU-L20 | 0.013541 | -1.17% | FAIL |
| TCN-L60 | 0.013663 | -2.08% | FAIL |
| TCN-L20 | 0.013706 | -2.41% | FAIL |
| BiGRU-L20 | 0.013752 | -2.75% | FAIL |
| BiGRU-L60 | 0.013756 | -2.78% | FAIL |

GRU-L60 is the closest sequence challenger, but still worse on aggregate MAE and therefore cannot replace LightGBM.

## 7. Quantile comparison

Mean Q10/Q50/Q90 pinball, lower is better:

| Configuration | Mean pinball | Relative vs classical |
|---|---:|---:|
| **Classical Gold-only/LightGBM Quantile** | **0.004295** | — |
| TCN-L20 | 0.004422 | -2.95% |
| GRU-L60 | 0.004442 | -3.42% |
| BiGRU-L20 | 0.004458 | -3.79% |
| BiGRU-L60 | 0.004463 | -3.92% |
| GRU-L20 | 0.004476 | -4.20% |
| TCN-L60 | 0.004488 | -4.50% |

All sequence quantile heads are worse than the classical quantile benchmark.

Pre-repair quantile crossing:
- **0%** in the reported sequence configurations.

Thus failure is not caused by quantile-order pathology; the distribution forecasts are simply less accurate.

## 8. Architecture scale

Trainable parameters:

- TCN: **1,557**
- GRU: **1,621**
- BiGRU: **2,141**.

Mean epochs to early stopping:

- TCN-L20: 10.9
- TCN-L60: 10.8
- GRU-L20: 16.0
- GRU-L60: 14.9
- BiGRU-L20: 14.6
- BiGRU-L60: 11.7.

Therefore the rejection is not the result of uncontrolled oversized neural networks. Even compact, regularized architectures do not beat boosting on this dataset.

## 9. Representative annual behavior

### TCN-L20
Direction Brier:
- 2022: 0.24807
- 2023: 0.25715
- 2024: 0.25281.

Return MAE:
- 2022: 0.01184
- 2023: 0.01244
- 2024: 0.01687.

### GRU-L60
Direction Brier:
- 2022: 0.24823
- 2023: 0.25153
- 2024: 0.25031.

Return MAE:
- 2022: 0.01169
- 2023: 0.01221
- 2024: 0.01672.

### BiGRU-L60
Direction Brier:
- 2022: 0.25040
- 2023: 0.25404
- 2024: 0.24888.

Return MAE:
- 2022: 0.01205
- 2023: 0.01237
- 2024: 0.01688.

No sequence architecture demonstrates a stable advantage sufficient for promotion.

## 10. Scientific interpretation

Current evidence favors **tabular boosting over compact sequence recurrence/convolution** for this H3 daily Gold dataset.

This is consistent with the project’s modest sample size:
- about 2,722 pre-DEV daily origins
- 749 DEV origins.

The useful short-horizon signal appears to be captured more efficiently by:
- current multi-lag Gold features
- Silver/Platinum context for direction
- boosted trees

than by learning a latent 20- or 60-day sequence representation.

This does **not** prove that all deep temporal architectures are useless.

It does show that:
- TCN
- GRU
- BiGRU

do not justify replacing the simpler classical H3 models under the frozen protocol.

## 11. Stage-3 artifact hashes

Aggregate:
- `stage3_decisions.csv`: `96ba6f0cbb5ac6059e81ceae1ab432f0a69168194c5119bc3edd2d38bd850b2c`
- `stage3_sequence_comparison.csv`: `66987b055c14520b2b841f4a96c14720ae081cdcf7b1fece039c4ccf29ebb02b`
- `stage3_all_summaries.json`: `dead2ada0e8816fc13a3160649b375b3ecc7e425a1d0e5b287141a23353b8c95`
- `STAGE3_RESULT.md`: `84448c80e01b56a03bea803825291cb24e36d9e6156c6967bba14a8c32414b0f`.

## 12. Decision

**Stage 3 = COMPLETE / NO_SEQUENCE_PROMOTION.**

Frozen H3 classical benchmark remains unchanged.

## 13. Exact next stage

**Stage 4 — TFT Multi-Horizon Probabilistic Challenger**

Rationale:
- TFT is not just another recurrent encoder;
- it directly models multiple horizons and quantiles with variable selection / temporal attention;
- therefore it tests a materially different hypothesis from the rejected TCN/GRU/BiGRU family.

Stage 4 should:
1. retain H1/H3/H5 targets simultaneously;
2. produce direction / point-return / Q10-Q50-Q90 where technically coherent;
3. use a tightly constrained TFT due modest sample size;
4. pre-register lookback and architecture before execution;
5. compare H3 directly to the frozen classical benchmark;
6. additionally test whether joint H1/H3/H5 training creates value not seen in separate classical models;
7. keep 2025 frozen.

If TFT also fails to add value:
- close the deep-learning challenger program;
- retain boosting as the forecast engine;
- move to forecast-head reconciliation and tactical allocation/utility research.
