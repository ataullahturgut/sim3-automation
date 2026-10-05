# SILVER SHORT-HORIZON V7 — BARRIER / HIGH-MOVE TARGET RESULT

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_BARRIER_TARGET_V7`  
**Selection universe:** 2022-2024 DEV only.  
**Transport status:** NOT OPENED because no DEV candidate passes the preregistered directional gate.

## DEV results

Frozen SILVER_PATH features and multinomial Logistic were used.

| H | k | Accuracy | Balanced acc | Macro F1 | Multiclass Brier | Pred directional coverage | Selective directional accuracy | Actual NO_MOVE share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H5 | 0.50 | 48.87% | 32.60% | 0.3190 | 0.5140 | 100.00% | **48.87%** | 1.19% |
| H5 | 0.75 | 47.81% | 33.13% | 0.3206 | 0.5421 | 100.00% | **47.81%** | 4.24% |
| H5 | 1.00 | 46.49% | 34.77% | 0.3227 | 0.5904 | 100.00% | **46.49%** | 11.26% |
| H3 | 0.50 | 44.90% | 31.78% | 0.3033 | 0.5643 | 100.00% | **44.90%** | 6.89% |
| H3 | 0.75 | 41.06% | 32.28% | 0.2917 | 0.6211 | 100.00% | **41.06%** | 15.63% |
| H3 | 1.00 | 36.69% | 34.57% | 0.3378 | 0.6544 | 90.20% | **36.12%** | 26.09% |

## Decision

No candidate satisfies the preregistered requirement:
- directional coverage >=30%;
- selective directional accuracy >50%;
- multiclass balanced accuracy above the 1/3 chance reference.

The barrier formulation does not create a useful Silver direction/abstention target under the current daily feature set.

**Status: V7_FAIL_DEV — 2025/2026 NOT OPENED.**

## Interpretation

The present Silver problem is not repaired by:
- changing forced binary H5 into first-hit barrier labels;
- increasing NO_MOVE share through larger volatility-normalized barriers.

The model still lacks a stable directional information source.

The next research step must therefore add a genuinely new source family rather than target engineering alone.
