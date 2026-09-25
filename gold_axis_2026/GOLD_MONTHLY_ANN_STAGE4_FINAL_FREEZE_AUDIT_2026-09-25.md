# GOLD MONTHLY ANN — Stage 4 Final Robustness / Freeze Audit

Date: 2026-09-25

## Purpose
This audit is diagnostic only. It does **not** open a new ensemble search.

Frozen candidates entering the audit:
- PRIMARY: FULL7 equal-weight ANN ensemble.
- CHALLENGER: REDUCED4 equal-weight ANN ensemble.

All calculations use original successful GitHub Actions artifact predictions. No base model is retrained.

## Authority
- DEV: 2022-04..2024-12, n=33.
- 2025/2026: reporting only.
- Random split: none.
- Database access: none.
- Leave-one-component-out is explicitly **diagnostic only** and is not used to choose a new subset.
- No post-hoc subset is promoted from this audit.

## Frozen ensembles

### FULL7
Vanilla + MPA + SCA + DE-ABC + Adaptive TLBO + TLBO-tuned PSO + MPA+SCA, all equal 1/7.

DEV:
- MAPE 2.10665%
- MAE 43.299
- RMSE 55.634
- Direction 66.67%
- Relative MAE vs RW 0.8128
- Worst APE 6.763%

### REDUCED4
Vanilla + MPA + SCA + DE-ABC, all equal 1/4.

DEV:
- MAPE 2.12123%
- MAE 43.378
- RMSE 54.966
- Direction 72.73%
- Relative MAE vs RW 0.8143
- Worst APE 6.822%

## Year-by-year DEV robustness

### FULL7
| Year | n | MAPE % | Direction % | Rel MAE vs RW | Worst APE % |
|---|---:|---:|---:|---:|---:|
| 2022 | 9 | 2.19485 | 88.89 | 0.7193 | 4.292 |
| 2023 | 12 | 1.89276 | 50.00 | 0.8757 | 5.153 |
| 2024 | 12 | 2.25439 | 66.67 | 0.8304 | 6.763 |

FULL7 beats RW on MAE in every DEV year (relative MAE < 1), but direction performance is clearly weaker in 2023.

### REDUCED4
| Year | n | MAPE % | Direction % | Rel MAE vs RW | Worst APE % |
|---|---:|---:|---:|---:|---:|
| 2022 | 9 | 2.29902 | 88.89 | 0.7565 | 4.272 |
| 2023 | 12 | 1.88397 | 58.33 | 0.8731 | 4.939 |
| 2024 | 12 | 2.22516 | 75.00 | 0.8123 | 6.822 |

REDUCED4 also beats RW on MAE in every DEV year and is directionally stronger than FULL7 in 2023 and 2024.

## Leave-one-origin sensitivity

### FULL7
When each DEV origin is removed one at a time:
- MAPE min: 1.96114%
- MAPE max: 2.17153%
- range: 0.21039 percentage points
- direction range: 65.625% to 68.75%

No single DEV origin causes a catastrophic collapse. The aggregate MAPE advantage is not produced by one isolated month.

### REDUCED4
- MAPE min: 1.97434%
- MAPE max: 2.18489%
- range: 0.21055 points
- direction range: 71.875% to 75.00%

Likewise, no single DEV origin drives the REDUCED4 result.

## Pairwise origin-level comparison

### FULL7 vs Vanilla
- FULL7 lower APE: 17/33 origins
- Vanilla lower APE: 16/33
- mean APE delta FULL7 - Vanilla: -0.0823 percentage points
- median delta: -0.1147 points
- largest FULL7 improvement: 2.1445 points
- largest FULL7 deterioration: 1.4308 points

### FULL7 vs MPA
- FULL7 lower APE: 17/33
- MPA lower APE: 16/33
- mean APE delta: -0.0928 points
- median delta: -0.0240 points

Interpretation: FULL7 does **not** win more often by a large count margin. Its aggregate gain comes from the magnitude/asymmetry of error improvements on the months it helps. Therefore the ensemble advantage is real on aggregate DEV error but should not be described as universal month-by-month dominance.

### REDUCED4 vs Vanilla/MPA
REDUCED4 is better on only 16/33 origins against each anchor and worse on 17/33, despite better aggregate mean MAPE. This reinforces the same point: its advantage is driven by error magnitude rather than frequent wins.

## Leave-one-component-out diagnostic — FULL7

This is a robustness diagnostic, **not subset selection**.

| Removed component | Resulting DEV MAPE % | Delta vs FULL7 | Direction % |
|---|---:|---:|---:|
| none (FULL7) | 2.10665 | — | 66.67 |
| Vanilla | 2.11284 | +0.00619 | 66.67 |
| MPA | 2.11936 | +0.01271 | 63.64 |
| SCA | **2.09504** | **-0.01161** | 66.67 |
| DE-ABC | 2.13407 | +0.02742 | 66.67 |
| Adaptive TLBO | 2.11877 | +0.01212 | 69.70 |
| TLBO-tuned PSO | **2.08292** | **-0.02373** | 66.67 |
| MPA+SCA | 2.12927 | +0.02262 | 66.67 |

### Interpretation
- Removing Vanilla, MPA, DE-ABC, Adaptive TLBO or MPA+SCA worsens DEV MAPE; these components provide positive ensemble support under this diagnostic.
- Removing SCA or TLBO-tuned PSO improves aggregate DEV MAPE slightly.
- This means FULL7 contains some redundancy / negative price-MAPE contribution.
- However promoting FULL6/FULL5 from this table would be a **post-hoc component subset search** performed on the same DEV sample. That would violate the Stage 4 anti-overfit rule established after optimized-weight failure.
- Therefore these removal results are retained as diagnostic evidence only. FULL7 composition is not changed retroactively.

## External reporting only
Previously frozen external behavior remains:
- FULL7: 2025 MAPE 2.46790%, direction 91.67%; 2026 MAPE 4.35551%, direction 71.43%.
- REDUCED4: 2025 MAPE 2.47331%, direction 91.67%; 2026 MAPE 4.46679%, direction 71.43%.

These values do not alter the freeze.

## Final Stage 4 freeze

### PRIMARY ANN ENSEMBLE — FROZEN
**FULL7 equal-weight ensemble**
- selection rationale: best predeclared honest DEV MAPE among tested Stage 4 protocols;
- weight-learning audit independently returned alpha=0 / equal weights;
- stable to leave-one-origin perturbation;
- beats RW MAE in every DEV year;
- caveat: component-removal diagnostic shows modest redundancy, so FULL7 should not be described as a uniquely optimal subset.

### SECONDARY CHALLENGER — FROZEN
**REDUCED4 equal-weight ensemble**
- slightly worse aggregate DEV MAPE;
- better DEV RMSE and direction accuracy;
- retains 72.73% DEV direction accuracy.

### CLOSED
- performance-specific learned weights as primary: closed;
- optimized simplex: closed;
- shrinkage simplex: closed (DEV selects alpha=0);
- generic stacking/meta-learner: closed;
- arbitrary subset search: closed;
- further ANN optimizer hybrids: closed.

## Stage status
**AŞAMA 4/5: COMPLETE AND FROZEN.**

Next: **AŞAMA 5/5 — final ELM vs ANN comparison and research-family freeze.**
