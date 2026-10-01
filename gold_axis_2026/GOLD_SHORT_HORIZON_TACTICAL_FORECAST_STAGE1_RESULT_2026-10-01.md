# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 1 First Multi-Horizon Model Screen Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PASS**  
**Primary workflow:** Gold Short Horizon Stage1 Model Screen  
**Primary run:** **36870914575**  
**Frozen horizon artifacts:**  
- H1: **11166394641**
- H3: **11166279606**
- H5: **11166224706**

**Authoritative aggregate workflow:** Gold Short Horizon Stage1 Aggregate V2  
**Aggregate run:** **36871668075**  
**Aggregate artifact:** **11167138282**  
**Aggregate digest:** `sha256:e4e80b3c6bb0ced359752b2b951ac9867f0a004d1915a6732ab3a5aade3296aa`

**Stage 0 authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE0_SCIENTIFIC_CONTRACT_2026-10-01.md`

## 1. Main conclusion

The first pre-2025 multi-horizon screen finds **modest but real predictive signal**.

The strongest overall horizon is currently **H3**, because it is the only horizon where all three forecast heads pass their frozen baseline gates:

- direction probability: PASS
- point return: PASS
- quantile distribution: PASS.

H1 and H5 each pass point-return and quantile heads but **do not pass the direction-probability gate**.

This is evidence for continued H3-focused research, not yet a final trading-horizon selection.

## 2. Frozen DEV protocol

- DEV: 2022-2024
- n = **749 origins** per horizon
- 2025: not inspected for model selection
- 2026: not used
- chronological expanding training
- refit every 5 Gold origins
- horizon-specific label-maturity purge
- no random split.

Feature blocks:
- GOLD_ONLY
- CORE3 = Gold + Silver + Platinum
- CORE3_SAFE_EXTERNAL = CORE3 + Rates + FX + VIX + Nasdaq-100.

Models:
- direction: Logistic L2, LightGBM, XGBoost
- point return: Elastic Net, LightGBM, XGBoost
- quantiles: LightGBM Q10/Q50/Q90.

## 3. Head decisions

| Horizon | Head | Decision | Best feature | Best model | Primary score | Best baseline | Relative improvement |
|---|---|---|---|---|---:|---:|---:|
| H1 | Direction | **NO PASS** | GOLD_ONLY | XGB_CLASS | Brier 0.248528 | 0.250282 | **+0.70%** |
| H1 | Return | **PASS** | CORE3 | XGB_REG | MAE 0.008596 | 0.008728 | **+1.51%** |
| H1 | Quantile | **PASS** | GOLD_ONLY | LGBM_QUANT | Pinball 0.002869 | 0.002907 | **+1.30%** |
| **H3** | **Direction** | **PASS** | **CORE3** | **XGB_CLASS** | **Brier 0.246458** | 0.249270 | **+1.13%** |
| **H3** | **Return** | **PASS** | **GOLD_ONLY** | **LGBM_REG** | **MAE 0.013384** | 0.013529 | **+1.07%** |
| **H3** | **Quantile** | **PASS** | **GOLD_ONLY** | **LGBM_QUANT** | **Pinball 0.004295** | 0.004374 | **+1.81%** |
| H5 | Direction | **NO PASS** | GOLD_ONLY | XGB_CLASS | Brier 0.248081 | 0.249215 | **+0.45%** |
| H5 | Return | **PASS** | CORE3 | LGBM_REG | MAE 0.016833 | 0.017007 | **+1.03%** |
| H5 | Quantile | **PASS** | GOLD_ONLY | LGBM_QUANT | Pinball 0.005407 | 0.005493 | **+1.57%** |

## 4. Horizon comparison

- H1: **2/3 heads PASS**, mean relative primary-metric improvement **+1.17%**
- **H3: 3/3 heads PASS**, mean improvement **+1.34%**
- H5: **2/3 heads PASS**, mean improvement **+1.02%**.

Current research priority:
**H3**

But H1/H5 remain active because their return-distribution heads pass and may be useful in later tactical horizon selection.

## 5. H3 direction head

Frozen first-screen leader:

**CORE3 / XGB_CLASS**

Metrics:
- Brier: **0.24646**
- baseline Brier: 0.24927
- relative improvement: **+1.13%**
- log loss: **0.68609**
- baseline log loss: 0.69169
- accuracy: **55.14%**
- balanced accuracy: **54.61%**
- UP precision: **57.81%**
- UP recall: **61.54%**
- ROC-AUC: **0.5598**
- PR-AUC: **0.5763**.

Interpretation:
- the edge is real under the pre-registered gate;
- the edge is **modest**, not strong;
- accuracy alone would overstate confidence.

## 6. H3 point-return head

Leader:

**GOLD_ONLY / LGBM_REG**

- MAE: **0.013384**
- baseline MAE: 0.013529
- relative MAE improvement: **+1.07%**
- RMSE: **0.017486**
- baseline RMSE: 0.017544
- return-sign accuracy from point forecast: **54.61%**
- Spearman: **0.0835**.

Close CORE3 alternative:
- MAE 0.013388
- direction accuracy **56.07%**
- Spearman **0.1191**.

The CORE3 alternative deserves robustness comparison before point-return head freeze.

## 7. H3 quantile head

Leader:

**GOLD_ONLY / LightGBM Quantile**

- mean Q10/Q50/Q90 pinball: **0.004295**
- baseline: 0.004374
- improvement: **+1.81%**.

Empirical coverage:
- Q10: **11.88%**
- Q50: **48.73%**
- Q90: **87.18%**.

The distribution is reasonably ordered/calibrated for a first screen, although upper-tail coverage is modestly below nominal 90%.

CORE3 quantile:
- mean pinball 0.004306
- very close to GOLD_ONLY.

## 8. H1 result

### Direction
Best XGB Gold-only:
- accuracy **53.27%**
- Brier improvement only **+0.70%**
- **NO PASS** under the frozen 1% Brier gate.

This illustrates why direction accuracy alone is not sufficient.

### Point return
CORE3 / XGB:
- MAE improvement **+1.51%**
- RMSE improves
- point-forecast direction accuracy **56.07%**
- PASS.

### Quantiles
Gold-only LightGBM:
- pinball improvement **+1.30%**
- PASS.

## 9. H5 result

### Direction
Gold-only XGB:
- accuracy **56.07%**
- Brier improvement **+0.45%**
- **NO PASS**.

Again, accuracy appears attractive but probabilistic improvement is below the pre-registered gate.

### Point return
CORE3 / LightGBM:
- MAE improvement **+1.03%**
- direction accuracy **55.14%**
- Spearman **0.1321**
- PASS.

### Quantiles
Gold-only LightGBM:
- pinball improvement **+1.57%**
- PASS.

## 10. Feature-family finding

No winning head in Stage 1 uses **CORE3_SAFE_EXTERNAL**.

The first-screen winners use:
- Gold-only, or
- Gold + Silver + Platinum.

Therefore the current raw/as-of representation of:
- Rates
- FX
- VIX
- Nasdaq-100

does **not** earn promotion in the first batch.

This is not evidence that these market variables contain no information.

It only means:
> their current raw-level/as-of representation does not improve the tested first-screen models enough to beat the simpler blocks.

Future external work, if authorized, should test better causal transformations such as:
- changes
- returns
- momentum
- volatility
- surprise/acceleration
rather than simply adding raw levels.

## 11. Model-family finding

First-screen winners:

- XGBoost:
  - H1 point return
  - H3 direction.

- LightGBM:
  - H3 point return
  - H5 point return
  - quantile head at H1/H3/H5.

- Elastic Net:
  - no winning head.

This supports keeping boosting models as the classical benchmark before moving to TCN/GRU/TFT.

## 12. Aggregate artifact hashes

- `stage1_metrics_all.csv`: `37c70595c846005e69abd1a152792016baf4b4c5a55f9471ab952ac11eee5f0d`
- `stage1_quantile_metrics_all.csv`: `930004137d8b105239a972bbdc62f75ff5a25ff82abf36ffeaab03aecdec9974`
- `stage1_quantile_summary_all.csv`: `9ce74579f6056730e7112ddb4201c09dde09a765088d4c08f2297d9918ca7f43`
- `stage1_decisions.csv`: `13ae7a5bf8127da7e69072012c6386b81078443461b3c016b3a752857878e61c`
- `stage1_horizon_summary.csv`: `b3c04b8d6aec596d2efa12841ef82020b8b47c7a82b7aed409098ae4584bfa36`
- `STAGE1_RESULT.md`: `9183ceb7ebd405614dc41069d87b4a9267e584fa2f71057cbe436b407bca5061`.

## 13. Technical supersession note

The aggregate step inside primary run 36870914575 failed only because the reporting script used the pandas method name `head` as if it were a column accessor.

All three horizon model jobs completed successfully and produced the authoritative frozen horizon artifacts.

Aggregate V2:
- run **36871668075**
- artifact **11167138282**
- successfully combines those exact frozen artifacts.

No horizon model was rerun or changed for the V2 aggregation.

## 14. Decision

**Stage 1 = PASS.**

Current strongest research horizon:
**H3**

Frozen Stage-1 evidence:
- H3 direction: CORE3 / XGB
- H3 return: Gold-only / LightGBM, with CORE3 close challenger
- H3 quantile: Gold-only / LightGBM quantile.

No tactical trading rule is authorized yet.

## 15. Exact next stage

**Stage 2 — H3 Robustness + Feature Representation Audit**

Before deep models or 2025 transport:

1. test H3 winners by DEV year 2022/2023/2024;
2. test rolling market-volatility buckets;
3. compare Gold-only vs CORE3 consistently across all H3 heads;
4. test CORE4/Palladium incrementally without changing target/model hyperparameters;
5. test causal transformed external blocks:
   - Rates changes
   - FX returns/momentum
   - VIX change/level-normalized stress
   - NDX returns/momentum
   rather than raw external levels;
6. retain 2025 fully frozen.

Only after H3 robustness is established should TCN/GRU/BiGRU/TFT challengers begin.
