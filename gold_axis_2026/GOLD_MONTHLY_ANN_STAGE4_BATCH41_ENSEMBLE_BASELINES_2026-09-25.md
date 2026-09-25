# GOLD MONTHLY ANN — Stage 4 Batch 4.1 Ensemble Baselines

Date: 2026-09-25

## ELM ensemble recovery status
**NOT_FOUND.**

The original ELM ledger commit and the current repository were searched for a prediction-level ELM ensemble definition, component set, learned weight vector, or ensemble result. None is verifiably present.

Therefore this stage is documented as a **new ANN ensemble stage**, not as exact ELM ensemble parity. No ELM ensemble component or weight value was invented.

## Frozen ANN ensemble component pool
Seven components were selected from the already-frozen Stage 2/3 evidence roles:

1. Vanilla ANN — baseline anchor
2. MPA-ANN — primary price leader
3. SCA-ANN — direction leader
4. DE-ABC-ANN — complementarity / hybrid benchmark
5. Adaptive TLBO-ANN — strongest refinement price profile
6. TLBO-tuned PSO-ANN — strong price+direction refinement
7. MPA+SCA Hybrid ANN — balance/stability hybrid

All predictions were loaded from the original successful GitHub Actions artifacts. No component model was re-trained in Stage 4.1.

## Meta-evaluation protocol
DEV = 2022-04..2024-12, n=33.

Three ensemble variants:

### 1. SIMPLE_AVERAGE
- fixed 1/7 weight for each component;
- no learned weights;
- serves as the ensemble benchmark.

### 2. PERFORMANCE_WEIGHTED
- for each DEV target, weights are calculated only from earlier DEV origins;
- weight_j proportional to inverse prior MAE_j;
- first 6 DEV origins use equal weights because meta-history is insufficient;
- external 2025/2026 weights are frozen after fitting on all DEV only.

### 3. OPTIMIZED_SIMPLEX
- SLSQP minimizes MAPE on earlier DEV origins only;
- non-negative weights;
- weights sum to 1;
- first 6 DEV origins use equal weights;
- external 2025/2026 weights are frozen from all DEV only.

Important: the full-DEV optimized fit is recorded only to show the final frozen external weight vector. Its in-sample DEV metric is **not** used as honest DEV performance evidence.

## Results

| Ensemble | Honest prequential DEV MAPE % | DEV MAE | DEV RMSE | DEV Direction % | DEV win vs RW | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|---:|---:|---:|
| SIMPLE_AVERAGE | **2.10665** | **43.299** | **55.634** | **66.67** | **60.61%** | 2.46790 | 4.35551 |
| PERFORMANCE_WEIGHTED | 2.11411 | 43.454 | 55.752 | 66.67 | 60.61% | 2.46539 | **4.35001** |
| OPTIMIZED_SIMPLEX | 2.33779 | 47.715 | 58.532 | 60.61 | 51.52% | **2.39450** | 4.40192 |

Reference DEV:
- Vanilla ANN: 2.18895%
- MPA-ANN: 2.19947%
- MPA+SCA Hybrid: 2.23957%
- Adaptive TLBO-ANN: 2.24090%
- SCA-ANN direction: 72.73%

## Main finding
The **simple 7-model average is the strongest honest DEV ensemble in Batch 4.1**.

Compared with the best individual DEV model:
- Vanilla ANN: 2.18895%
- Simple average: 2.10665%

This is about a **3.76% relative MAPE reduction** versus Vanilla.

Compared with MPA:
- MPA ANN: 2.19947%
- Simple average: 2.10665%

This is about a **4.22% relative MAPE reduction**.

The ensemble also raises DEV direction accuracy to 66.67%, substantially above Vanilla (54.55%) and MPA (57.58%), although still below SCA's specialist 72.73%.

## Performance-weighted finding
The inverse-MAE performance-weighted variant remains close to equal weight:
- DEV MAPE 2.11411% vs simple average 2.10665%.
- Final all-DEV weights are nearly uniform:
  - Vanilla 14.71%
  - MPA 14.80%
  - SCA 13.71%
  - DE-ABC 14.19%
  - Adaptive TLBO 14.33%
  - TLBO-tuned PSO 13.90%
  - MPA+SCA 14.35%

This supports the interpretation that the gain comes primarily from diversified error averaging rather than aggressive performance weighting.

## Optimized simplex finding — meta-overfit warning
The final all-DEV optimized weights are:
- MPA+SCA: 34.14%
- Vanilla: 25.13%
- DE-ABC: 21.10%
- MPA: 19.63%
- SCA: ~0%
- Adaptive TLBO: ~0%
- TLBO-tuned PSO: ~0%

If these weights are evaluated on the same full DEV period used to fit them, MAPE is **2.05363%**.

However, this is in-sample meta-fit and is not valid as honest DEV evidence.

Under expanding prequential DEV evaluation, the optimized simplex degrades to **2.33779%**, clearly worse than simple average and performance weighting.

This is direct evidence of **ensemble-weight overfitting** in the small n=33 meta-sample.

## External reporting only
2025/2026 were not used to choose components, tune weights, choose variants, or judge success.

External observations:
- all three ensemble variants have 2025 direction accuracy 91.67%;
- simple/performance-weighted 2026 MAPE is around 4.35%;
- optimized simplex 2025 MAPE is lower at 2.39450%, but this cannot override its weak prequential DEV evidence.

## Decision
- **SIMPLE_AVERAGE: retain as current leading ANN ensemble benchmark.**
- **PERFORMANCE_WEIGHTED: retain as a near-equivalent robust challenger.**
- **OPTIMIZED_SIMPLEX: do not promote in unregularized form; prequential evidence shows meta-overfit.**
- Stage 4.2 should test only a small, controlled remedy for optimized-weight overfit:
  1. shrinkage/regularized simplex weights toward equal weights;
  2. optionally one predeclared reduced role-diverse component pool.
- No large component-subset search or arbitrary weight search is permitted.
- 2025/2026 remain outside model-selection authority.
