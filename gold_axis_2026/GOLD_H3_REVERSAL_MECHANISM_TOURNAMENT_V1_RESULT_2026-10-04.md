# GOLD H3 — Reversal Mechanism Tournament V1 Result

**Status:** WINNER_FROZEN_2026_STRESSED

## Design

- 2023-2024: mechanism construction / fitting
- 2025: eligibility and threshold selection
- 2026: frozen retrospective stress
- No 2026 label enters fitting or selection.

## 2025 fixed-grid results

| Family | Q | Handoff | Actions | Rescue | Broken | Net | Precision | Eligible |
|---|---:|---|---:|---:|---:|---:|---:|---|
| ANALOG | 0.95 | True | 3 | 1 | 2 | -1 | 33.3% | False |
| ANALOG | 0.95 | False | 10 | 4 | 6 | -2 | 40.0% | False |
| ANALOG | 0.90 | True | 4 | 1 | 3 | -2 | 25.0% | False |
| ANALOG | 0.85 | True | 5 | 1 | 4 | -3 | 20.0% | False |
| ANALOG | 0.80 | True | 6 | 1 | 5 | -4 | 16.7% | False |
| ANALOG | 0.90 | False | 17 | 6 | 11 | -5 | 35.3% | False |
| ANALOG | 0.80 | False | 47 | 18 | 29 | -11 | 38.3% | False |
| ANALOG | 0.85 | False | 29 | 9 | 20 | -11 | 31.0% | False |
| HAZ | 0.90 | False | 14 | 8 | 6 | +2 | 57.1% | False |
| HAZ | 0.95 | False | 5 | 3 | 2 | +1 | 60.0% | False |
| HAZ | 0.80 | False | 25 | 13 | 12 | +1 | 52.0% | False |
| HAZ | 0.95 | True | 0 | 0 | 0 | +0 | 0.0% | False |
| HAZ | 0.85 | False | 23 | 11 | 12 | -1 | 47.8% | False |
| HAZ | 0.80 | True | 4 | 1 | 3 | -2 | 25.0% | False |
| HAZ | 0.85 | True | 4 | 1 | 3 | -2 | 25.0% | False |
| HAZ | 0.90 | True | 3 | 0 | 3 | -3 | 0.0% | False |
| MCP | 0.90 | True | 1 | 1 | 0 | +1 | 100.0% | False |
| MCP | 0.85 | True | 2 | 1 | 1 | +0 | 50.0% | False |
| MCP | 0.95 | True | 0 | 0 | 0 | +0 | 0.0% | False |
| MCP | 0.80 | True | 3 | 1 | 2 | -1 | 33.3% | False |
| MCP | 0.95 | False | 14 | 5 | 9 | -4 | 35.7% | False |
| MCP | 0.90 | False | 34 | 11 | 23 | -12 | 32.4% | False |
| MCP | 0.85 | False | 47 | 12 | 35 | -23 | 25.5% | False |
| MCP | 0.80 | False | 52 | 12 | 40 | -28 | 23.1% | False |
| SELLR | 0.95 | False | 9 | 6 | 3 | +3 | 66.7% | True |
| SELLR | 0.90 | False | 15 | 8 | 7 | +1 | 53.3% | False |
| SELLR | 0.90 | True | 2 | 1 | 1 | +0 | 50.0% | False |
| SELLR | 0.95 | True | 0 | 0 | 0 | +0 | 0.0% | False |
| SELLR | 0.85 | True | 3 | 1 | 2 | -1 | 33.3% | False |
| SELLR | 0.80 | True | 4 | 1 | 3 | -2 | 25.0% | False |
| SELLR | 0.85 | False | 25 | 9 | 16 | -7 | 36.0% | False |
| SELLR | 0.80 | False | 34 | 13 | 21 | -8 | 38.2% | False |

## 2025 selected finalists

| Finalist | Net | Precision | Actions |
|---|---:|---:|---:|
| SELLR | +3 | 66.7% | 9 |

Frozen tournament winner: **SELLR**

## Frozen 2026 stress

| Family | Actions | Rescue | Broken | Net | Precision | Remaining-53 rescued | Episode starts | Accuracy | BA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SELLR | 1 | 1 | 0 | +1 | 100.0% | 1 | 0 | 66.49% | 66.81% |

### Winner — SELLR

- combined baseline: **126/191 = 65.97%**, BA **66.31%**
- assisted: **127/191 = 66.49%**, BA **66.81%**
- net rescue: **+1**
- remaining-53 rescued: **1**
- episode-first rescues: **0**

## Hazard coefficients (standardized features)

| Feature | Coefficient |
|---|---:|
| abs_h_ret_12 | -0.644 |
| core_confirmation | -0.309 |
| log_trend_age | +0.228 |
| trend_strength | -0.226 |
| opt_total_z20 | +0.089 |
| signed_opt_pressure | +0.066 |
| adverse_excursion | -0.042 |
| cross_dispersion | +0.019 |
| mcp_score | +0.010 |
| path_consistency | -0.009 |

## Interpretation discipline

- This tournament deliberately tests multiple causal/statistical stories rather than repeatedly retuning one gate.
- 2025 determines eligibility; 2026 is not used to rescue a failed mechanism.
- Because the project focus arose from retrospective 2026 errors, even a positive 2026 stress remains retrospective evidence, not pristine prospective validation.
