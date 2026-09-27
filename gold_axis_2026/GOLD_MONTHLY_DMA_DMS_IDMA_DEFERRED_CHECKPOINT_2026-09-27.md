# GOLD MONTHLY — DMA / DMS / IDMA DEFERRED CHECKPOINT

Date: 2026-09-27  
Status: **DEFERRED — REVISIT LAST**  
Project: GOLD MONTHLY FORECAST  
Target: H=1 next-calendar-month average XAU/USD  
Selection authority: DEV 2022-04..2024-12 only  
2025/2026: reporting-only; never tuning/selection

## 1. Decision

The DMA / DMS / IDMA family is **not rejected**. It is parked for later review because:

1. Under the current frozen 8-feature VW-MIDAS information set, the family does not beat the project's strongest nonlinear families.
2. Additional history does not produce a stable monotonic improvement, so simple sample shortage is not supported as the main explanation.
3. A small literature-aligned market augmentation (Fed funds, Nasdaq, USD/CNY) does not materially improve DMS and worsens DMA.
4. The direct gold DMA/IDMA literature uses a broader and more heterogeneous macro-financial information set than the current frozen 8 metal-derived features.
5. Therefore, the unresolved hypothesis is **predictor-set / information-set mismatch and model-form mismatch**, not merely insufficient sample size.
6. The family should be revisited **after the other planned high-authority model families are completed**, using a dedicated literature-replication track.

## 2. Binding authority correction discovered during audit

The pre-outcome authority plan was committed before the first DMA execution:

- Authority plan commit: `9af2868f5390e5778f096531f32ac3f7cf5a276e`
- Commit time: 2026-09-26T21:46:56Z

That plan requires the canonical first-pass structure to be:

- Gold-only target;
- all 2^8 = 256 subsets of the frozen 8 predictors;
- intercept always included;
- canonical alpha=0.99, lambda=0.99;
- no custom multi-output DMA before canonical Gold evidence.

Some earlier exploratory runs instead:
- forced GOLD_MR into every model, yielding 128 subsets;
- opened a custom GOVERNED_MULTI4 lane.

Those runs remain useful exploratory evidence but **must not be treated as canonical authority results**.

## 3. Corrected canonical Gold-only 256-subset results

Canonical alpha=0.99, lambda=0.99, DEV 2022-04..2024-12:

| Model | DEV SigmaAE (USD) | MAE | RMSE | Direction |
|---|---:|---:|---:|---:|
| Canonical DMA | **1486.2561** | 45.0381 | 57.2129 | 19/33 = 57.58% |
| Canonical DMS | 1489.8247 | 45.1462 | 57.1733 | 20/33 = 60.61% |

Canonical DMA is the current corrected price-error reference for this family.

## 4. Sample-size diagnostic

Canonical Gold-only DMS was rerun with fixed recent-history lengths:

| Training history | DEV SigmaAE | Direction |
|---|---:|---:|
| 60 months | 1489.0965 | 19/33 |
| 84 months | 1497.7098 | 19/33 |
| **108 months** | **1483.8794** | **20/33** |
| 132 months | 1488.0163 | 20/33 |
| Maximum available | 1489.8247 | 20/33 |

Interpretation:
- error does **not** decline monotonically as history increases;
- maximum history is not best;
- the best 108-month window improves only about 5.95 USD versus maximum-history DMS;
- therefore, **simple data shortage is not supported as the dominant cause**.

## 5. Information-set diagnostic

A diagnostic-only literature-aligned market set was tested using:
- Fed funds: one-month change;
- Nasdaq: one-month log return;
- USD/CNY: one-month log return.

GPR was deliberately excluded because full-DEV origin-safe PIT coverage is not proven by the available snapshot.

Results:

| Predictor space | Method | DEV SigmaAE | Direction |
|---|---|---:|---:|
| GOLD2_ONLY | DMA | 1489.9335 | 20/33 |
| GOLD2_ONLY | DMS | **1489.8247** | **20/33** |
| MARKET3_ONLY | DMA | 1774.8885 | 15/33 |
| MARKET3_ONLY | DMS | 1757.1890 | 17/33 |
| GOLD2 + MARKET3 | DMA | 1509.1210 | 19/33 |
| GOLD2 + MARKET3 | DMS | **1489.8247** | **20/33** |

Interpretation:
- adding only Fed + Nasdaq + USD/CNY does not rescue the family;
- DMS effectively falls back to the Gold-only solution;
- this diagnostic does **not** prove that a broader literature-faithful information set would fail.

## 6. Exploratory IDMA evidence already obtained

These results are retained for method development history, but they are not a substitute for a future literature-faithful replication because the earlier IDMA implementation used the 128-subset/GOLD_MR-mandatory search space and also evaluated a custom Multi4 lane.

### Stage 4 — IDMA core
Best exploratory result:
- Authority Gold IDMA, expanding, MSFE-log-return selector
- DEV SigmaAE: **1495.6721**
- Direction: **20/33 = 60.61%**

### Stage 5 — adaptive selector window
Pareto observations:
- Expanding Authority IDMA: SigmaAE **1495.6721**, direction 20/33
- W12 Authority IDMA: SigmaAE **1537.3872**, direction **21/33**

W24 did not improve price error.

### Stage 6 — project H=1 price-loss alignment
Best exploratory result:
- Authority Gold IDMA, expanding, AE_PRICE selector
- DEV SigmaAE: **1495.5268**
- Direction: **20/33**

Conclusion from exploratory IDMA:
- the refinements did not materially improve on canonical DMA/DMS;
- Stage 4 to Stage 6 improvement was negligible;
- current evidence does not justify further blind tuning.

## 7. Why published studies can still report strong DMA/IDMA results

The direct gold literature uses a materially different information set and evaluation design.

### Aye et al. (2015)
Uses broad macro-financial blocks including:
- business-cycle factors;
- nominal factors;
- interest-rate factors;
- commodity factors;
- exchange-rate factors;
- stock-market factors;
- stress / uncertainty variables.

The model can therefore switch among economically distinct regimes.

### Baur, Beckmann & Czudaj (2016)
Uses a much broader candidate determinant set and a large model space, while DMA often ends up selecting parsimonious subsets dynamically.

### Chen, Yang & Lan (2026)
Uses monthly gold data with a larger predictor universe spanning macroeconomic, other-asset and risk variables. Reported horizon-dependent drivers include Nasdaq, interest rates / Fed funds, USD/CNY and lagged GPR.

Therefore, our current frozen 8 metal-derived feature set is not a close replication of those published information environments.

## 8. Requirements before reopening this family

The family should be reopened only when the following are available:

1. **Exact literature predictor matrix**
   - extract every predictor used in Aye 2015 and Chen 2026;
   - record transformation, lag, release timing and horizon role.

2. **Origin-safe PIT data map**
   - for every literature predictor, classify:
     - AVAILABLE_PIT
     - DERIVABLE_PIT
     - NOT_FOUND
     - NOT_PROVEN
     - BLOCKED
   - no final-vintage substitution.

3. **Broader heterogeneous macro-financial panel**
   Candidate categories should include, where origin-safe evidence exists:
   - activity/business cycle;
   - inflation/nominal;
   - rates/yields;
   - FX / USD;
   - equities / Nasdaq;
   - commodities;
   - financial stress / volatility;
   - uncertainty / GPR.

4. **GPR full-DEV PIT coverage**
   - current available PIT macro snapshot begins at 2022-12 and does not cover the whole DEV period;
   - do not backfill with final-vintage values.

5. **Paper-faithful replication lane**
   - reproduce paper target/return-domain scoring as closely as possible;
   - keep this separate from the project H=1 average-price primary score.

6. **Project-target lane**
   - same origin-safe predictor panel;
   - H=1 next-month average XAU/USD;
   - primary score SigmaAE + direction.

7. **Canonical model-space governance**
   - Gold-only first;
   - no forced GOLD_MR unless the cited paper explicitly requires lagged dependent variable;
   - use the authority-prescribed model space;
   - if model space becomes very large, use literature-backed DOW / IDMA rather than arbitrary pruning.

8. **True IDMA replication audit**
   - distinguish an exact/paper-faithful iterative IDMA implementation from the current exhaustive small-space adaptation;
   - document Stepsize, Thres, ThresPara, TrainWin, TestWin, MaxIter and objective from the primary paper.

9. **No 2025/2026 tuning**
   - DEV-only nested selection remains binding.

## 9. Reopen criterion

Reopen DMA/DMS/IDMA only:
- after the planned higher-priority model families have been tested, **or**
- when a substantially more literature-faithful origin-safe predictor panel becomes available.

Until then:

**STATUS = DEFERRED_REVISIT_LAST**

Do not spend further compute on small alpha/lambda/window tweaks under the current frozen 8-feature information set.

## 10. Provenance

Relevant successful runs/artifacts:
- Stage 4 IDMA core: run `36277936108`, artifact `10918640413`
- Stage 5 window: run `36303383254`, artifact `10926108909`
- Stage 6 H=1 loss alignment: run `36306335110`, artifact `10927618455`
- Cause diagnostics / canonical 256-subset audit: run `36308156035`, artifact `10928147352`

Earlier exploratory DMA/DMS Batch 1:
- run `36274932872`, artifact `10917351143`

## Kontrol ve Uyum Özeti

- Current family decision: **DEFERRED, NOT REJECTED**
- Revisit order: **LAST, after other planned families**
- Canonical 256-subset Gold-only audit: **PASS**
- Sample-shortage hypothesis: **NOT SUPPORTED as dominant cause**
- 3-variable market augmentation rescue hypothesis: **NOT SUPPORTED**
- Broad literature-faithful predictor mismatch: **OPEN / HIGH-PRIORITY REVISIT HYPOTHESIS**
- DB writes: **NONE**
- Random split: **NONE**
- 2025/2026 selection: **NONE**
- Non-PIT GPR substitution: **NONE**
