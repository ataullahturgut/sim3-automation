# GOLD H3 CLEAN REVERSAL CHAIN — 2026-10-03

**Status:** full fixed-rule clean rerun from corrected AURORA through V5-DCE.

No threshold was retuned. Original frozen/prospective artifacts were not overwritten.

## Model metrics

| Model | Period | Accuracy | BA | Brier | Logloss |
|---|---|---:|---:|---:|---:|
| AURORA | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| OPAL | 2023 | 67.12% | 67.41% | 0.2303 | 0.6561 |
| V2 | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| V3 | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| V4 | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| V5 | 2023 | 71.23% | 71.83% | 0.2118 | 0.6149 |
| AURORA | 2024 | 70.83% | 69.97% | 0.2006 | 0.5847 |
| OPAL | 2024 | 70.00% | 67.99% | 0.2070 | 0.5993 |
| V2 | 2024 | 71.25% | 70.22% | 0.1988 | 0.5806 |
| V3 | 2024 | 70.83% | 69.74% | 0.1988 | 0.5804 |
| V4 | 2024 | 71.25% | 70.22% | 0.1988 | 0.5806 |
| V5 | 2024 | 71.25% | 70.22% | 0.1988 | 0.5806 |
| AURORA | 2025 | 64.52% | 62.93% | 0.2276 | 0.6585 |
| OPAL | 2025 | 64.92% | 61.42% | 0.2330 | 0.6716 |
| V2 | 2025 | 66.13% | 64.26% | 0.2244 | 0.6520 |
| V3 | 2025 | 64.92% | 62.34% | 0.2280 | 0.6590 |
| V4 | 2025 | 66.13% | 64.26% | 0.2244 | 0.6520 |
| V5 | 2025 | 66.53% | 64.59% | 0.2243 | 0.6518 |
| AURORA | 2026 | 58.64% | 59.02% | 0.2532 | 0.7207 |
| OPAL | 2026 | 63.35% | 63.71% | 0.2467 | 0.7100 |
| V2 | 2026 | 60.73% | 61.16% | 0.2477 | 0.7089 |
| V3 | 2026 | 63.35% | 63.76% | 0.2455 | 0.7045 |
| V4 | 2026 | 62.30% | 62.71% | 0.2447 | 0.7029 |
| V5 | 2026 | 63.35% | 63.76% | 0.2425 | 0.6976 |
| AURORA | 2025-2026 | 61.96% | 61.15% | 0.2388 | 0.6856 |
| OPAL | 2025-2026 | 64.24% | 62.98% | 0.2389 | 0.6883 |
| V2 | 2025-2026 | 63.78% | 62.85% | 0.2346 | 0.6767 |
| V3 | 2025-2026 | 64.24% | 63.17% | 0.2357 | 0.6788 |
| V4 | 2025-2026 | 64.46% | 63.57% | 0.2332 | 0.6741 |
| V5 | 2025-2026 | 65.15% | 64.24% | 0.2322 | 0.6717 |

## Clean V5 routing

| Year | Routed | Rescue | Broken | Net | DCE exceptions |
|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 6 | 1 | +5 | 1 |
| 2026 | 19 | 14 | 5 | +9 | 4 |

## Clean reversal experts

| Expert | Year | Accuracy | AURORA | Overrides | Rescue | Broken |
|---|---:|---:|---:|---:|---:|---:|
| RIFT | 2025 | 64.92% | 64.52% | 15 | 8 | 7 |
| RIFT | 2026 | 59.16% | 58.64% | 3 | 2 | 1 |
| TURN | 2025 | 62.90% | 64.52% | 10 | 3 | 7 |
| TURN | 2026 | 57.59% | 58.64% | 6 | 2 | 4 |
| VEGA | 2025 | 64.11% | 64.52% | 9 | 4 | 5 |
| VEGA | 2026 | 59.16% | 58.64% | 13 | 7 | 6 |
| OPAL | 2025 | 64.92% | 64.52% | 23 | 12 | 11 |
| OPAL | 2026 | 63.35% | 58.64% | 25 | 17 | 8 |

## 2026 clean-refit vs old probabilities on clean labels

| Model | Old probability / clean labels | Clean refit | Delta | Clean Brier |
|---|---:|---:|---:|---:|
| AURORA | 59.69% | 58.64% | -1.05 pp | 0.2532 |
| V2 | 60.73% | 60.73% | +0.00 pp | 0.2477 |
| V3 | 64.40% | 63.35% | -1.05 pp | 0.2455 |
| V4 | 63.35% | 62.30% | -1.05 pp | 0.2447 |
| V5 | 64.40% | 63.35% | -1.05 pp | 0.2425 |

## Governance

All values in the previous pre-clean HELIOS V2/V3/V4/V5 2026 reports must be treated as historical/provisional. This clean chain is the valid retrospective integrity rerun, but remains post-hoc research rather than prospective confirmation.
