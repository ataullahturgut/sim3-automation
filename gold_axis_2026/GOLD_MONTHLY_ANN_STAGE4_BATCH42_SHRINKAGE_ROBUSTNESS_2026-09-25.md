# GOLD MONTHLY ANN — Stage 4 Batch 4.2 Shrinkage / Reduced-Pool Robustness

Date: 2026-09-25

## Purpose
Batch 4.1 showed that:
- the 7-model simple average was the strongest honest prequential DEV ensemble;
- performance weighting stayed close to uniform;
- unregularized optimized simplex overfit the small n=33 meta-sample.

Batch 4.2 therefore tested a controlled remedy:
1. exact simplex MAPE optimization solved by linear programming;
2. shrink optimized weights toward equal weights by alpha;
3. one single predeclared role-diverse reduced pool.

No combinatorial subset search was allowed.

## First-run technical failure and correction
The first Batch 4.2 workflow run (36136794458) failed because SLSQP reached its iteration limit for one small-history reduced-pool problem.

No scientific result from that failed run was accepted.

The numerical core was then replaced by an exact linear-programming solution of the MAPE-weighted L1 simplex problem. Shrinkage was implemented as:

w_alpha = (1-alpha) * equal_weight + alpha * w_optimized

with fixed alpha grid:
0.00, 0.10, 0.25, 0.50, 0.75, 1.00.

The corrected run 36137025884 completed successfully with OUTPUT_GATE=PASS.

## Authority
- DEV selection authority only: 2022-04..2024-12, n=33.
- 2025/2026 excluded from alpha and pool selection.
- Random split: none.
- Database access: none; original GitHub Actions artifact predictions only.
- Weights non-negative and sum to one.
- First 6 DEV origins use equal weights because learned meta-history is insufficient.
- No subset search.

## Pools

### FULL7
Vanilla, MPA, SCA, DE-ABC, Adaptive TLBO, TLBO-tuned PSO, MPA+SCA.

### REDUCED4
Single predeclared role-diverse pool:
Vanilla + MPA + SCA + DE-ABC.

This pool represents:
- baseline anchor;
- price leader;
- direction leader;
- complementarity/hybrid benchmark.

## Prequential alpha curves

### FULL7
| Alpha | DEV MAPE % | DEV Direction % | DEV RMSE |
|---:|---:|---:|---:|
| 0.00 | **2.10665** | **66.67** | **55.634** |
| 0.10 | 2.12971 | 66.67 | 55.791 |
| 0.25 | 2.16431 | 66.67 | 56.084 |
| 0.50 | 2.22197 | 66.67 | 56.718 |
| 0.75 | 2.27963 | 66.67 | 57.530 |
| 1.00 | 2.33729 | 60.61 | 58.514 |

**Chosen alpha = 0.00.**

The DEV curve is monotonic: every movement away from equal weights worsens MAPE.

### REDUCED4
| Alpha | DEV MAPE % | DEV Direction % | DEV RMSE |
|---:|---:|---:|---:|
| 0.00 | **2.12123** | **72.73** | **54.966** |
| 0.10 | 2.13516 | 72.73 | 55.042 |
| 0.25 | 2.15605 | 72.73 | 55.194 |
| 0.50 | 2.19086 | 72.73 | 55.551 |
| 0.75 | 2.22568 | 72.73 | 56.033 |
| 1.00 | 2.26049 | 69.70 | 56.640 |

**Chosen alpha = 0.00.**

Again, every movement away from equal weights worsens DEV MAPE.

## Final external weights
Because alpha=0 for both pools, the frozen external weights reduce exactly to equal weights.

### FULL7
Each model = 1/7 = 14.2857%.

### REDUCED4
Each model = 1/4 = 25%.

## External reporting only

| Pool / variant | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| FULL7 equal / chosen shrinkage | **2.10665** | 66.67 | **2.46790** | 91.67 | **4.35551** | 71.43 |
| REDUCED4 equal / chosen shrinkage | 2.12123 | **72.73** | 2.47331 | 91.67 | 4.46679 | 71.43 |

2025/2026 are evidence only and were not used in the choice.

## Interpretation

### 1. Optimized weight fine-tuning is not supported by DEV
The result is stronger than merely saying that one optimizer overfit.

Across both a 7-model and 4-model pool, and across the full shrinkage path, the best honest DEV result occurs at **alpha=0**, meaning:
- use no optimized-weight contribution;
- use equal weights.

This is direct evidence that, with only 33 DEV meta-observations, model-specific weight fitting has insufficient support.

### 2. FULL7 remains the price-error leader
FULL7 equal average:
- MAPE 2.10665%;
- MAE 43.299;
- RMSE 55.634;
- direction 66.67%.

This remains the best honest DEV MAPE observed in the ANN research line.

### 3. REDUCED4 offers a direction/RMSE trade-off
REDUCED4 equal average:
- MAPE 2.12123%, slightly worse than FULL7;
- direction 72.73%, matching the SCA specialist;
- RMSE 54.966, better than FULL7 55.634;
- median APE 1.571%, also better than FULL7.

Thus REDUCED4 is not the primary price-MAPE ensemble, but it is a valid role-diverse directional/large-error robustness challenger.

### 4. Full-DEV optimized weights remain sparse but are not transportable
For reference only, the unshrunk full-DEV optimums are:

FULL7:
- MPA+SCA 34.14%
- Vanilla 25.13%
- DE-ABC 21.10%
- MPA 19.63%
- SCA 0
- Adaptive TLBO 0
- TLBO-tuned PSO 0

REDUCED4:
- Vanilla 61.96%
- DE-ABC 38.04%
- MPA 0
- SCA 0

The prequential alpha curves show that moving toward these sparse optima monotonically worsens honest DEV performance. Therefore these sparse weights are meta-fit artifacts, not reliable ensemble weights.

## Decision
- **FULL7 SIMPLE AVERAGE remains the primary ANN ensemble candidate.**
- **REDUCED4 SIMPLE AVERAGE remains a secondary direction/RMSE challenger.**
- **Optimized/shrunk weights are closed:** DEV itself chooses alpha=0.
- No further weight fine-tuning or arbitrary subset search is scientifically justified at this sample size.
- A generic stacking/meta-learner is not justified: it would add more degrees of freedom after both optimized simplex and shrinkage failed to generalize prequentially.
- Stage 4 can now proceed only to a final robustness/freeze check if desired; no new ensemble family should be opened.
