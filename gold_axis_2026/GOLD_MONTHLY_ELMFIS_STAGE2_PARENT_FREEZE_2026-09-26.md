# GOLD MONTHLY FORECAST — ELMFIS STAGE 2 DEV-ONLY PARENT FREEZE

**Date:** 2026-09-26  
**Authority:** DEV 2022-04..2024-12 only (n=33)  
**Status:** STAGE 2 COMPLETE — PARENT ROLES FROZEN

## Source and governance
Stage 2 used the original Stage-1 GitHub Actions JSON artifacts from runs:
36169448338, 36170049225, 36170874292, 36171748270, 36173141852, 36174033508, 36175116272, 36175779813, 36177121360.

No Stage-1 model was re-run. 2025 transport and 2026 stress results were excluded from all Stage-2 selection, Pareto and parent-role decisions.

Active selection plane:
1. DEV cumulative absolute error (ΣAE), lower is better.
2. DEV monthly direction accuracy, higher is better.

Supporting DEV-only diagnostics:
- year-by-year ΣAE and direction;
- maximum monthly AE and worst APE;
- relative MAE vs random walk;
- signed forecast-error bias;
- repeat-validation fitness CV;
- signed-error correlation and direction-rescue counts.

## Final Stage-1 Pareto frontier

| Model | DEV ΣAE USD | Direction | Role |
|---|---:|---:|---|
| **ABC-ELMFIS** | **1,524.89** | 21/33 = 63.64% | price-error frontier |
| **SMA-ELMFIS** | **1,651.45** | **25/33 = 75.76%** | direction/trade-off frontier |

No other Stage-1 model is nondominated on the active two-objective plane.

## Robustness diagnostics

| Model | ΣAE | Direction | Year-MAE SD | Max monthly AE | Worst APE | Repeat CV med |
|---|---:|---:|---:|---:|---:|---:|
| ABC | 1,524.89 | 21/33 | 11.59 | 145.09 | 6.72% | 0.0605 |
| SMA | 1,651.45 | 25/33 | 14.53 | 174.87 | 9.03% | 0.0240 |
| HHO | 1,857.89 | 22/33 | 5.72 | 141.32 | 6.55% | 0.0653 |
| DE | 1,665.47 | 21/33 | 9.28 | 152.28 | 8.15% | 0.0555 |
| HGSO | 1,594.65 | 18/33 | 13.75 | 191.01 | 7.21% | 0.0453 |
| CS | 1,809.39 | 25/33 | 15.48 | 251.74 | 9.79% | 0.0554 |
| ACO | 1,942.87 | 19/33 | 2.51 | 150.10 | 6.96% | 0.0543 |
| FA-FPA | 1,820.45 | 25/33 | 13.33 | 165.88 | 7.69% | 0.0586 |
| Vanilla | 1,996.29 | 20/33 | 5.28 | 180.36 | 6.80% | n/a |

## Complementarity diagnostics

These are DEV-only diagnostic proxies, not Stage-4 ensemble selection.

| Pair | Signed-error corr. | 50/50 proxy ΣAE | Proxy direction | Second model beats first AE | Direction rescues/losses |
|---|---:|---:|---:|---:|---:|
| ABC + SMA | 0.6299 | 1,428.49 | 26/33 | 17/33 | 7 / 3 |
| ABC + HHO | 0.6687 | 1,479.86 | 24/33 | 14/33 | 5 / 4 |
| SMA + HHO | 0.5667 | 1,568.21 | 24/33 | 15/33 | 1 / 4 |
| ABC + DE | 0.8518 | 1,445.87 | 22/33 | 14/33 | 5 / 5 |
| SMA + CS | 0.3938 | 1,518.50 | 24/33 | 15/33 | 4 / 4 |

ABC and SMA therefore carry useful complementary DEV error information. The 50/50 numbers above are not frozen ensemble results and may not be promoted until Stage 4.

## Frozen Stage-3 structure

### Baseline anchor
**Vanilla ELMFIS** — canonical implementation anchor only; not an active metaheuristic parent.

### Active evidence-driven parents
1. **ABC-ELMFIS — primary price parent**
   - Best DEV ΣAE: 1,524.89 USD.
   - Direction: 21/33.
   - Relative MAE vs RW: 0.8674.

2. **SMA-ELMFIS — direction + complementarity parent**
   - Direction: 25/33.
   - DEV ΣAE: 1,651.45 USD.
   - Strong active trade-off and useful complementarity with ABC.

3. **HHO-ELMFIS — year/tail-stability parent**
   - DEV ΣAE: 1,857.89 USD.
   - Direction: 22/33.
   - Year-MAE SD: 5.72.
   - Max monthly AE: 141.32 USD.

### Existing hybrid/parity benchmarks
- **FA-FPA-ELMFIS:** 1,820.45 USD / 25/33. Existing Stage-1 hybrid benchmark only.
- **DE-ABC-ELMFIS:** 2,317.34 USD / 17/33. Weak DEV result; retained only for parity/audit reference.

### Reserve challengers
- **DE-ELMFIS:** strong price reserve, 1,665.47 USD / 21/33.
- **HGSO-ELMFIS:** price reserve, 1,594.65 USD but 18/33 direction.
- **CS-ELMFIS:** direction reserve, 25/33 but higher tail error.
- **ACO-ELMFIS:** year-stability reserve; lowest optimized-model year-MAE SD (2.51) but only 19/33 direction.

Reserves do not enter Stage 3 by default.

## Stage-3 governance
Binding checklist remains unchanged:
- Stage 3A: Adaptive PSO, TLBO-tuned PSO, DE-tuned PSO, Adaptive/Improved TLBO, Adaptive Crow Search, PSO-TLBO Hybrid.
- Stage 3B: MPA+SCA, MPA+GA, MPA+CPA.
- Stage 3C: CQCSA-ELMFIS.
- No new optimizer cross-product is added from Stage-2 results.
- All tuning/promotion remains DEV-only.
- 2025 and 2026 remain reporting-only.

## Control and compliance summary
- DB READ_ONLY: PASS.
- Random split: PASS — none.
- Chronological origin: PASS.
- Target-month leakage: PASS.
- Frozen 8-feature contract: PASS.
- DEV-only selection: PASS.
- 2025 selection exclusion: PASS.
- 2026 selection exclusion: PASS.
- Stage-1 models re-run in Stage 2: NO.
- Active metric contract ΣAE + direction: PASS.
- Pareto calculation: PASS — ABC + SMA only.
- Stage 2: COMPLETE.
- Next stage: Stage 3A after explicit user approval.
