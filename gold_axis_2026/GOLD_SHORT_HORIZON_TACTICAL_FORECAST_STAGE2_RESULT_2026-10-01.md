# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 2 H3 Robustness & Feature Representation Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PASS / ALL STAGE-1 HEAD CONTRACTS RETAINED**  
**Authoritative workflow:** Gold Short Horizon Stage2 H3 Robustness  
**Authoritative run:** **36874561989**  
**Artifact:** **11167744845**  
**Artifact digest:** `sha256:63e70127447ec23531f59ff6dd589933085905260adcfb3b9c558b253d9cdadb`  
**Runner commit:** `63c4de8eabc97ae757031889f9f56e4b50ab95dd`  
**Authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE2_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

No Stage-2 feature challenger earns promotion.

Frozen H3 contracts remain:

- **Direction:** CORE3 / XGB_CLASS
- **Point return:** GOLD_ONLY / LGBM_REG
- **Quantile distribution:** GOLD_ONLY / LGBM_QUANT.

Therefore:

> The Stage-1 H3 signal survives the robustness/representation audit without requiring Palladium or transformed macro/market external blocks.

The signal remains modest.

2025 is still unopened for model selection.

## 2. Critical preprocessing correction

Two earlier Stage-2 runs are **superseded / non-authoritative**:

- run 36873375235
- run 36873744569.

Reason:

Those executions dropped the first 21 historical rows with incomplete lag history, while frozen Stage 1 had training-median imputed those early lag gaps.

That changed the supposedly frozen comparator.

The authoritative run 36874561989 restores exact Stage-1 preprocessing:

- early lag-history gaps: training-median imputation
- DEV rows: no missing features
- **Palladium exception:** no backfill; CORE4 uses only genuinely observed Palladium-history rows.

Comparator verification after correction:

- H3 direction CORE3/XGB Brier = **0.246458**, matching Stage 1
- H3 return Gold-only/LightGBM MAE = **0.013384**, matching Stage 1
- H3 quantile Gold-only/LightGBM mean pinball = **0.004295**, matching Stage 1.

## 3. Feature-block decisions

| Head | Current | Best challenger | Challenger relative improvement | Gate | Decision |
|---|---|---|---:|---|---|
| Direction | **CORE3** | CORE3 + VIX transformed | **-0.02%** | FAIL | **RETAIN CORE3** |
| Return | **GOLD_ONLY** | CORE3 | **-0.02%** | FAIL | **RETAIN GOLD_ONLY** |
| Quantile | **GOLD_ONLY** | CORE3 | **-0.25%** | FAIL | **RETAIN GOLD_ONLY** |

No challenger reaches the frozen +0.5% promotion requirement.

## 4. Aggregate H3 direction

Frozen model:
**CORE3 / XGB_CLASS**

| Feature block | Brier |
|---|---:|
| **CORE3** | **0.246458** |
| CORE3 + VIX transforms | 0.246519 |
| GOLD_ONLY | 0.247045 |
| CORE3 + Rates transforms | 0.248785 |
| CORE3 + FX transforms | 0.248974 |
| CORE3 + NDX transforms | 0.249318 |
| CORE3 + ALL transformed | 0.252051 |
| CORE4 / Palladium | 0.253098 |

Interpretation:
- Silver + Platinum retain a small useful contribution to H3 direction.
- VIX transform comes very close but does not improve the frozen CORE3 model.
- Palladium materially worsens the result under its shorter genuine history.
- stacking all transformed external families worsens the probability forecast.

## 5. Aggregate H3 point return

Frozen model:
**GOLD_ONLY / LGBM_REG**

| Feature block | MAE |
|---|---:|
| **GOLD_ONLY** | **0.013384** |
| CORE3 | 0.013388 |
| CORE3 + VIX transforms | 0.013448 |
| CORE3 + NDX transforms | 0.013483 |
| CORE3 + Rates transforms | 0.013536 |
| CORE4 / Palladium | 0.013581 |
| CORE3 + FX transforms | 0.013603 |
| CORE3 + ALL transformed | 0.013638 |

CORE3 is extremely close but not better.

The Stage-1 choice to keep the point-return head Gold-only is therefore retained.

## 6. Aggregate H3 quantile distribution

Frozen model:
**GOLD_ONLY / LGBM_QUANT**

| Feature block | Mean Q10/Q50/Q90 pinball |
|---|---:|
| **GOLD_ONLY** | **0.004295** |
| CORE3 | 0.004306 |
| CORE3 + VIX transforms | 0.004312 |
| CORE3 + FX transforms | 0.004316 |
| CORE3 + Rates transforms | 0.004316 |
| CORE3 + ALL transformed | 0.004329 |
| CORE3 + NDX transforms | 0.004332 |
| CORE4 / Palladium | 0.004334 |

No distribution challenger improves the Gold-only quantile head.

## 7. H3 robustness by DEV year

The following compares each retained H3 head against its own strongest frozen Stage-1 baseline.

### Direction — CORE3 / XGB

| Year | Relative Brier improvement vs baseline |
|---|---:|
| 2022 | **+1.29%** |
| 2023 | **-0.07%** |
| 2024 | **+2.19%** |

Interpretation:
- positive in 2022 and 2024
- effectively flat/slightly worse in 2023
- no material annual collapse.

Direction is **robust enough to retain**, but its aggregate edge is modest.

### Point return — GOLD_ONLY / LightGBM

| Year | Relative MAE improvement vs baseline |
|---|---:|
| 2022 | **+0.94%** |
| 2023 | **-0.85%** |
| 2024 | **+2.57%** |

Interpretation:
- useful in 2022 and 2024
- modestly worse in 2023
- no >3% annual deterioration.

Return head is **retained with moderate stability caution**.

### Quantile — GOLD_ONLY / LightGBM

| Year | Relative mean-pinball improvement vs baseline |
|---|---:|
| 2022 | **-0.47%** |
| 2023 | **-0.08%** |
| 2024 | **+4.82%** |

Interpretation:
- aggregate Stage-1 PASS is driven mainly by 2024
- 2022/2023 are approximately flat/slightly worse, not materially worse
- no formal robustness rejection, but **year-concentration warning is binding**.

Quantile head remains frozen but must not be described as uniformly stable across DEV years.

## 8. H3 robustness by pre-DEV volatility bucket

Volatility bucket cutoffs were fixed from pre-2022 Gold sigma20 history:

- LOW <= **0.006486**
- MID <= **0.008498**
- HIGH > **0.008498**.

Relative retained-head improvement versus frozen baseline:

| Volatility | Direction | Return | Quantile |
|---|---:|---:|---:|
| LOW | -0.29% | +0.64% | +1.57% |
| MID | -0.36% | -1.12% | -1.81% |
| HIGH | **+2.06%** | **+1.74%** | **+2.81%** |

The H3 edge is clearly strongest in **HIGH volatility** conditions.

Important:
- this is diagnostic only;
- no volatility gate is created in Stage 2;
- a post-hoc HIGH-vol-only trading rule is forbidden.

## 9. Palladium / CORE4 audit

Strict genuine CORE4 history:

- pre-DEV complete rows: **1,965**
- first complete signal: **2014-02-10**
- DEV complete rows: 749.

CORE3:
- pre-DEV rows: **2,722**
- first complete signal: 2011-02-03.

CORE4 loses roughly 757 pre-DEV training observations and does not compensate with predictive improvement:

- direction Brier: 0.253098
- return MAE: 0.013581
- quantile pinball: 0.004334.

Decision:
**Palladium not promoted into H3 core.**

## 10. External transformed representation audit

Tested causally:

### Rates
- DGS10 Δ1 / Δ5
- DFII10 Δ1 / Δ5
- breakeven Δ1 / Δ5
- nominal-real spread level / Δ5.

### FX
For Broad USD, EUR, GBP, JPY, CHF, CNY:
- 1-origin log change
- 5-origin log change.

### VIX
- log change 1
- log change 5
- rolling 20-origin z-score.

### Nasdaq-100
- log return 1
- log return 5
- log return 21.

Result:

**No transformed external block earns promotion in any H3 head.**

VIX is the closest:
- direction Brier 0.246519 vs CORE3 0.246458
- still slightly worse.

Therefore:
- Rates: not promoted
- FX: not promoted
- VIX: not promoted
- NDX: not promoted
- ALL transformed: not promoted.

This resolves the first external representation question without claiming the variables are universally useless.

## 11. Feature availability

| Block | Features | Pre-DEV complete rows | First complete signal | DEV complete |
|---|---:|---:|---|---:|
| GOLD_ONLY | 6 | 2,722 | 2011-02-03 | 749 |
| CORE3 | 14 | 2,722 | 2011-02-03 | 749 |
| CORE4 | 18 | 1,965 | 2014-02-10 | 749 |
| CORE3 + Rates X | 22 | 2,722 | 2011-02-03 | 749 |
| CORE3 + FX X | 26 | 2,722 | 2011-02-03 | 749 |
| CORE3 + VIX X | 17 | 2,722 | 2011-02-03 | 749 |
| CORE3 + NDX X | 17 | 2,722 | 2011-02-03 | 749 |
| CORE3 + ALL X | 40 | 2,722 | 2011-02-03 | 749 |

## 12. Scientific interpretation

The cleanest current architecture is asymmetric by forecast head:

### Direction
Cross-metal information helps:
**Gold + Silver + Platinum**

### Expected H3 return
Gold's own path is sufficient:
**Gold-only**

### H3 return distribution
Gold-only also remains best:
**Gold-only quantiles**

Adding more variables does not improve the first classical architecture.

This argues against building a giant all-feature model by default.

## 13. Artifact hashes

- `stage2_aggregate_metrics.csv`: `73eed9b105947484446f1c776cdcf4232de8c8fa9967f10d2ff110a770da7d27`
- `stage2_year_metrics.csv`: `3c22471bf0503f745891335a134f26e1b21a96169fbfa6c066ba74a2f5307196`
- `stage2_volatility_metrics.csv`: `13435141879fbdcdfd677c63d0eabf2c709dd0702f99055df210e4cdb903460b`
- `stage2_quantile_summary.csv`: `5f0cb892806697f7eabd789bd107eb676381eb972b79bb80caa2ec2c057484ce`
- `stage2_quantile_year_summary.csv`: `ef6e7834a2306a19b48d30afcf6884fe1cb80803962c208fdf64fa19f9b5e55f`
- `stage2_quantile_volatility_summary.csv`: `d86503dfab4f22f22ede8a9e62b2b008027b15021c1b3b2548f12e6dd1da5f2f`
- `stage2_decisions.csv`: `de7dedfe30c666840248859a1346bc71792f9ab3ef88360dbc6f3d37ac1846e3`
- `stage2_feature_availability.csv`: `5fe2ba03c2018e6445edcb9ca998c1bbda847b41199a29a8a09d898925403ddf`
- `stage2_h3_predictions.csv`: `d859831f4caabe6b42a0cdad5efca2bd17f71cfcfcebc283c4aa561c1814f351`
- `stage2_h3_quantile_predictions.csv`: `6b0ca96a1951676f468689b8fffff56a1ba03354af3d5991a90b9b1b3b672a37`
- `STAGE2_RESULT.md`: `0226d1d401d53e96b78d8d5a9ed5d88ad816a4b6e50ab79d421cc91b99cbf437`.

## 14. Decision

**Stage 2 = PASS.**

Retain H3 as the strongest current short-horizon research horizon.

Frozen H3 classical benchmark contracts:

- direction = CORE3 / XGB_CLASS
- return = GOLD_ONLY / LGBM_REG
- quantile = GOLD_ONLY / LGBM_QUANT.

2025 remains frozen.

## 15. Exact next stage

**Stage 3 — Sequence Model Challengers**

Run compact, origin-safe sequence challengers on H3 only:

1. TCN
2. GRU
3. BiGRU

Rules:
- same 2022-2024 DEV authority
- same H3 target
- no 2025 selection
- compact architectures only
- input windows preregistered before run
- compare direction / return / quantile heads to the frozen Stage-2 classical contracts
- no TFT until compact sequence models are resolved.

The quantile head carries a binding stability caution because its aggregate gain is concentrated in 2024/high-volatility conditions.
