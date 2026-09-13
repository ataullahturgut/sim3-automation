# Gold Control V1.62 — Context-Aware Meta-Forecast Result Checkpoint

Date: 2026-09-13  
Branch: `gold-v162-context-aware-meta-forecast-research`  
Draft PR: #53  
Parent research head: `1dfbc77a3aebdc96cf6b28af188aac04776f3262` (V1.61)  
Pre-score freeze commit: `10c1c11a43d7dc61ffb7a0eb7afb4e08d7a60f3e`  
Workflow run: `34751425868` — SUCCESS  
Artifact: `10315921341`  
Artifact digest: `sha256:ce618700531a6f06eccd9bfa81ab0e9888f3da95b0ce4507d11fa485f67bd560`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Question

Can a small pool of horizon-specific probabilistic forecasters be improved by recent-loss weighting, soft state-local competence weighting, or CRASE-style local reliability, while legacy Gold Control engines remain role-preserving context rather than flat direction votes?

The expert pool and all meta-layer constants were frozen before scoring. V1.62 may not be retuned after this result.

## Governance / reproducibility

- Tests: PASS.
- Maturity: only forecasts satisfying `j+h<=t` can update expert/meta competence.
- Random split: none.
- Legacy engines: context only; no equal direction vote.
- `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`.
- Production/trading writes: NONE.

## Main results

### 1D — all available meta-evaluation origins (N=384)

| Method | Brier | Log loss | Balanced accuracy | MCC | UP / DOWN |
|---|---:|---:|---:|---:|---:|
| P50 | 0.250000 | 0.693147 | 0.5000 | 0.0000 | 384 / 0 |
| Expanding frequency | 0.251128 | 0.695447 | 0.5000 | 0.0000 | 384 / 0 |
| Best prior single | 0.258399 | 0.711550 | 0.4658 | -0.0710 | 243 / 141 |
| Equal mean | 0.257576 | 0.709070 | 0.4614 | -0.0791 | 235 / 149 |
| Recent exponential | 0.257567 | 0.709073 | 0.4589 | -0.0841 | 234 / 150 |
| Local soft | 0.257595 | 0.709138 | 0.4639 | -0.0741 | 236 / 148 |
| CRASE_V0 | NO_SIGNAL | — | — | — | coverage 0% |

### 3D — all available meta-evaluation origins (N=378)

| Method | Brier | Log loss | Balanced accuracy | MCC | UP / DOWN |
|---|---:|---:|---:|---:|---:|
| P50 | 0.250000 | 0.693147 | 0.5000 | 0.0000 | 378 / 0 |
| Expanding frequency | 0.245485 | 0.684467 | 0.5000 | 0.0000 | 378 / 0 |
| Best prior single | 0.259974 | 0.716386 | 0.4927 | -0.0228 | 336 / 42 |
| Equal mean | 0.256297 | 0.707591 | 0.4854 | -0.0479 | 340 / 38 |
| Recent exponential | 0.256606 | 0.708408 | 0.4831 | -0.0547 | 339 / 39 |
| Local soft | 0.256727 | 0.708685 | 0.4831 | -0.0547 | 339 / 39 |
| CRASE_V0 | NO_SIGNAL | — | — | — | coverage 0% |

2025 and 2026 subperiods tell the same qualitative story: none of the expert/meta methods establishes a two-direction predictive advantage over the mandatory anchors.

## Why CRASE_V0 produced 0% coverage

Post-run diagnostic inspection of the immutable artifact shows that the failure is **not** lack of local sample support:

- 1D local effective N: min ~54, median ~193.
- 3D local effective N: min ~55, median ~192.
- Probability-edge gate passes about 66.7% of 1D origins and 89.4% of 3D origins.
- The frozen weight-confidence gate passes **0%** of origins.
- Maximum entropy-derived expert-weight confidence is only ~0.0134 (1D) and ~0.0179 (3D), far below the frozen 0.10 gate.

This means the local competence layer cannot identify a meaningfully superior expert. The experts remain near-uniform in estimated competence.

Standalone expert diagnostics reinforce this conclusion:

- 1D expert Brier is roughly 0.2584–0.2614; balanced accuracy roughly 0.466–0.493.
- 3D expert Brier is roughly 0.2536–0.2653; balanced accuracy roughly 0.489–0.497.
- The two logistic experts are highly correlated (~0.99 at 1D, ~0.98 at 3D).

Therefore this is primarily a **weak / insufficiently complementary expert-pool problem**, not a selector-threshold problem.

## Scientific decision

`V1.62 = FAIL / NEGATIVE METHOD-DEVELOPMENT RESULT`.

Do **not** lower the V1.62 confidence threshold, change the state vector, alter eta/lambda, add experts, or change horizons inside V1.62 after seeing these scores.

The result answers an important question: a state-local meta-selector cannot rescue a pool whose constituent forecasters do not themselves carry stable incremental predictive information.

## Next legitimate hypothesis

A new frozen version must target the **true forecasters**, not retune V1.62 selection. The next research question should be whether richer, genuinely heterogeneous information can create stronger horizon-specific experts before dynamic selection is attempted again. Candidate directions must preserve role semantics and may include:

1. richer lagged price-discovery / realized-moment / corrected macro-driver information already available in V1.61,
2. state-local or mixture-of-experts learning inside the new horizon-specific forecaster (not inside legacy FAST/SLOW/BOCPD/GVZ engines),
3. explicit expert-diversity/complementarity audit before any new selector is eligible,
4. only after competent/diverse experts exist, re-test dynamic/local combination under a new pre-score freeze.

No prospective or production claim is made.
