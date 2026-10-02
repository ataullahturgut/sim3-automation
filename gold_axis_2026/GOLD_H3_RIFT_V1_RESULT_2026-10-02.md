# RIFT-H3 V1 — REVERSAL IMBALANCE & FAT-TAIL TRIGGER RESULT

**Status:** **NOT_PROMOTED_CONFIRM_FAIL**  
**Evidence class:** retrospective mechanism validation; architecture was motivated after inspecting historical errors including 2026.  
**Fixed reversal threshold:** **0.70**

## Period metrics

| Period | AURORA Acc | RIFT Acc | AURORA BA | RIFT BA | AURORA Brier | RIFT Brier | Overrides | Rescued | Broken |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022_H2 | 57.58% | 63.64% | 58.27% | 64.62% | 0.2567 | 0.2389 | 2 | 2 | 0 |
| 2023 | 71.23% | 70.32% | 71.83% | 70.82% | 0.2118 | 0.2165 | 6 | 2 | 4 |
| 2024 | 70.83% | 71.25% | 69.97% | 70.11% | 0.2006 | 0.1999 | 7 | 4 | 3 |
| 2025 | 64.52% | 64.92% | 62.93% | 63.45% | 0.2276 | 0.2297 | 15 | 8 | 7 |
| 2026 | 60.73% | 61.78% | 61.12% | 62.16% | 0.2477 | 0.2434 | 4 | 3 | 1 |
| 2023-2024 | 71.02% | 70.81% | 71.24% | 70.84% | 0.2059 | 0.2079 | 13 | 6 | 7 |
| 2025-2026 | 62.87% | 63.55% | 62.07% | 62.79% | 0.2363 | 0.2356 | 19 | 11 | 8 |

## 2026 changed calls

| Issue | H3 end | AURORA | P(reversal) | RIFT | Actual | H3 return | Effect |
|---|---|---|---:|---|---|---:|---|
| 2026-02-03 | 2026-02-05 | DOWN | 70.1% | UP | UP | +3.64% | RESCUED |
| 2026-04-20 | 2026-04-22 | UP | 74.2% | DOWN | DOWN | -1.53% | RESCUED |
| 2026-04-22 | 2026-04-24 | DOWN | 70.7% | UP | DOWN | -1.36% | BROKEN |
| 2026-05-11 | 2026-05-13 | UP | 70.1% | DOWN | DOWN | -0.45% | RESCUED |

## Governance

No feature, threshold or model hyperparameter was searched after this authority was written. Because the architecture itself was discovered from historical error anatomy, these results cannot be called pristine prospective validation. A passed RIFT must be frozen separately and judged only on future origins.
