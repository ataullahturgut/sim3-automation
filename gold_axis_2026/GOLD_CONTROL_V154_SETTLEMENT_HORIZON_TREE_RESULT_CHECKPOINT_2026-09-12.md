# Gold Control V1.54 — Settlement-Window Multi-Horizon Result Checkpoint

**Workflow:** `34704495965`  
**Artifact:** `10300712776`  
**Artifact digest:** `sha256:8799b427d1f91620435647ed7470727888beea55432a5ef3ed4e355118681926`  
**Status:** `NOT_PROVEN_DYNAMIC_DIRECTION`; research-only; no production authority.

## Frozen-rule result

The preregistered 13:29 ET XAU/USD spot endpoint aligned to the CME GC settlement window improved historical endpoint density, but the fixed annual tree models did **not** satisfy the frozen research-interest gate on both 2025 and 2026.

### Primary 20-settlement-session horizon

| Model | 2025 accuracy | 2025 balanced accuracy | 2026 accuracy | 2026 balanced accuracy | Gate |
|---|---:|---:|---:|---:|---|
| RF500 (primary) | 58.51% | 49.67% | 45.27% | 49.58% | FAIL |
| BAG300 | 67.22% | 59.30% | 44.59% | 49.26% | FAIL |
| SGB300 | 55.60% | 59.86% | 45.27% | 48.98% | FAIL |
| LOGIT | 55.19% | 40.78% | 46.62% | 51.24% | FAIL |

At 10 sessions the strongest 2026 result was BAG300 at about 56.96% ordinary accuracy and 59.23% balanced accuracy, but its 2025 balanced accuracy was only about 48.57%. The five-session horizon also failed the frozen gate.

## Structural-change diagnostic

The 20-session target class distribution changed sharply: the 2025 evaluation cells were overwhelmingly UP (about 81.3%), whereas the 2026 available-cache cells were only about 44.6% UP. Fixed annual models trained through 2025 consequently produced strongly UP-skewed 2026 predictions and lost balanced skill.

This is consistent with the structural-break and dynamic-model-averaging literature: the relevant gold predictor/model may change through time, and a fixed annual winner can fail when the return regime shifts.

## Decision

V1.54 is **not promoted** and will not be post-hoc retuned against the observed 2025/2026 cells. The next successor must be frozen before scoring and should directly address parameter/model instability through rolling/recency-weighted estimation and/or dynamic model averaging, while preserving horizon-specific treatment and explicit majority-class skill controls.

Governance remains `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, production authority `false`, production writes `NONE`.
