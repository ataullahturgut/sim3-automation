# GOLD SHORT-HORIZON GLOBAL XAU — Stage 1 Classical / Boosting Screen Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PARTIAL SIGNAL / H3 DIRECTION ONLY**  
**Workflow:** Gold Short Horizon Global XAU Stage1 Screen  
**Authoritative run:** **36901409925**

Artifacts:
- H1: **11182016410**
- H3: **11181384613**
- H5: **11182181130**
- aggregate: **11181622889**
- aggregate digest: `sha256:20d0a7a3bcf0358d3482d066b66e4d4f191b5383027602217ed01aa6c472dc47`

Authority:
`GOLD_SHORT_HORIZON_GLOBAL_XAU_STAGE1_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

The corrected global-XAU target does **not** reproduce the prior BIST result structure.

Only one head clears its frozen baseline gate:

> **H3 direction — CORE3 / Logistic L2**

H1:
- 0/3 heads PASS.

H3:
- **1/3 heads PASS**.

H5:
- 0/3 heads PASS.

Therefore H3 remains the only horizon with statistically meaningful first-screen evidence, but there is **not yet a complete short-horizon investment forecast engine** because the H3 point-return and quantile heads do not beat their baselines.

2025 remains unopened.

## 2. Target / sample

Target:
- global XAU/USD daily spot-average research series
- StakTrakr / MetalPriceAPI lineage
- NOT Borsa İstanbul Metal Price.

DEV:
- 2022-2024
- **755 origins**.

Pre-DEV safe-panel history:
- **3,011 origins**.

Frozen 2025 coverage:
- **253 observations** available, not inspected for model selection.

## 3. H1

### Direction
Best:
- GOLD_ONLY / LightGBM
- Brier: **0.249533**
- baseline: 0.249736
- relative improvement: **+0.08%**
- FAIL versus +1.0% gate.

### Point return
Best:
- GOLD_ONLY / XGBoost
- MAE: **0.006588**
- baseline: 0.006599
- relative improvement: **+0.16%**
- FAIL.

### Quantile
Best:
- GOLD_ONLY / LightGBM Quantile
- mean pinball: **0.002180**
- baseline: 0.002182
- relative improvement: **+0.08%**
- FAIL.

Decision:
**H1 = 0/3 PASS.**

## 4. H3

### Direction — PASS
Best:
- **CORE3 / Logistic L2**

CORE3:
- Gold
- Silver
- Platinum.

Metrics:
- Brier: **0.246731**
- baseline: **0.249712**
- relative improvement: **+1.19%**
- log loss: **0.686634**
- baseline log loss: **0.692572**
- PASS.

This is the only head in the first global-XAU screen that clears the frozen gate.

### Point return — FAIL
Best:
- GOLD_ONLY / Elastic Net
- MAE: **0.011857**
- baseline: **0.011841**
- relative improvement: **-0.13%**
- RMSE: 0.015084
- baseline RMSE: 0.015062
- FAIL.

The learned point-return model is slightly worse than the simple historical baseline.

### Quantile — FAIL
Best:
- GOLD_ONLY / LightGBM Quantile
- mean pinball: **0.003785**
- baseline: **0.003774**
- relative improvement: **-0.29%**
- FAIL.

Decision:
**H3 = 1/3 PASS.**

## 5. H5

### Direction
Best:
- CORE3 / Logistic L2
- Brier: **0.247880**
- baseline: 0.249444
- relative improvement: **+0.63%**
- FAIL.

This is suggestive but does not clear the frozen +1% gate.

### Point return
Best:
- GOLD_ONLY / Elastic Net
- MAE: **0.015428**
- baseline: **0.015419**
- relative improvement: **-0.05%**
- FAIL.

### Quantile
Best:
- CORE4 / LightGBM Quantile
- mean pinball: **0.004940**
- baseline: 0.004927
- relative improvement: **-0.28%**
- FAIL.

Decision:
**H5 = 0/3 PASS.**

## 6. Horizon summary

| Horizon | Direction | Return | Quantile | Complete heads passing |
|---|---|---|---|---:|
| H1 | FAIL | FAIL | FAIL | 0/3 |
| **H3** | **PASS** | FAIL | FAIL | **1/3** |
| H5 | FAIL | FAIL | FAIL | 0/3 |

Mean primary-metric relative improvement:
- H1: +0.11%
- H3: +0.26%
- H5: +0.10%.

H3 is the only horizon justified for robustness work.

## 7. Comparison with archived BIST-target project

Archived BIST first screen had H3 passing all three heads.

The corrected global-XAU target passes only H3 direction.

Therefore:

> the previous BIST H3 return/distribution success must not be carried into the global-XAU project.

The target change materially changes the empirical result.

This validates the user's objection that the tactical target identity matters.

## 8. Model-family implication

Direction:
- the best global-XAU H3 model is **Logistic L2**, not XGBoost.

This is important:
- a low-capacity linear probability model beats the frozen baseline;
- more complex boosting is not automatically better.

Return/distribution:
- none of Elastic Net / LightGBM / XGBoost / Quantile LightGBM provides a meaningful gain over simple historical baselines in the first screen.

Therefore do not proceed directly to trading utility or deep models.

## 9. Scientific interpretation

The current evidence supports a narrower statement:

> There is modest pre-2025 predictive information for the **direction of the next 3 global-XAU daily observations**, especially when Gold is combined with Silver and Platinum history.

It does **not** yet support:
- reliable H3 return magnitude forecasting
- superior H3 conditional quantile forecasting
- a complete tactical allocation rule.

## 10. Next stage

**Stage 2 — H3 Direction Robustness & Representation Audit**

Before expanding model complexity:

1. test H3 CORE3 / Logistic L2 by 2022, 2023, 2024;
2. test LOW/MID/HIGH volatility buckets;
3. inspect coefficient stability / sign changes across expanding refits;
4. compare GOLD_ONLY / CORE3 / CORE4 / transformed external representations under the same Logistic L2 contract;
5. test whether H5's +0.63% Brier improvement is stable enough to remain a secondary horizon;
6. keep 2025 frozen.

Do not reopen BIST as tactical target.
Do not start P&L optimization.
