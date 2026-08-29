# GOLD H1 R1 — Pre-2023 Monthly Reversal Model Audit R1

Date: 2026-08-29

## Purpose
Test whether a reversal-risk discriminator can be learned using only information available before 2023, then frozen and applied to 2023 without hindsight.

## Construction
Target: whether the next calendar month's realized direction is opposite the canonical 3M Momentum prior (`reversal=1`).

Primary feature universe was deliberately restricted to origin-safe GOLD history only:
- latest completed monthly return (`ret1`)
- 3M mean monthly return (`mom3`)
- 6M mean monthly return (`mom6`)
- 6M return volatility (`vol6`)
- acceleration / deceleration (`ret1 - mean(ret2,ret3)`)
- 1M-vs-3M direction disagreement (`mom1_conflict`)
- absolute 3M trend strength (`strength3`)

GPR/current-history variables were deliberately excluded from the primary discriminator because point-in-time vintage safety is not proven.

## Split
- DEV: 2010-01 through 2020-12
- PRE-2023 VALIDATION: 2021-01 through 2022-12
- TEST: 2023-01 through 2023-12
- October 2023 exact-flat monthly-average observation is excluded from economic directional accuracy but retained as a scoring-artifact note.
- No 2023–2026 outcome was used for feature/rule/hyperparameter selection.

## Candidate search discipline
Only small interpretable models were allowed:
- regularized logistic regression
- depth-1 / depth-2 decision tree
- feature subsets of at most 3 variables

DEV time-series cross-validation was used first. A candidate could proceed only if its DEV CV balanced accuracy was at least 0.55 and its 2021–2022 validation balanced accuracy and accuracy were both at least about 0.58. 2023 was not used to choose candidates.

## Pre-2023 qualified candidates
| Model | Features | DEV CV BA | 2021–22 BA | 2021–22 Acc | 2023 BA | 2023 Acc |
|---|---|---:|---:|---:|---:|---:|
| Logistic | mom3 + vol6 + mom1_conflict | 0.5977 | 0.6357 | 0.6250 | 0.4107 | 0.4545 |
| Tree depth 2 | mom1_conflict + strength3 | 0.5924 | 0.6000 | 0.5833 | 0.5357 | 0.5455 |
| Tree depth 2 | mom3 + mom1_conflict + strength3 | 0.5615 | 0.6000 | 0.5833 | 0.5357 | 0.5455 |
| Logistic | mom6 + vol6 + mom1_conflict | 0.5706 | 0.5857 | 0.5833 | 0.3393 | 0.3636 |
| Logistic | ret1 + mom1_conflict + strength3 | 0.5528 | 0.5857 | 0.5833 | 0.4107 | 0.4545 |

## Frozen top-candidate 2023 test
Top pre-2023 candidate: logistic `mom3 + vol6 + mom1_conflict`.

Economically directional 2023 months (excluding exact-flat October):
- canonical 3M baseline: 7/11 = 63.64%
- frozen reversal model: 5/11 = 45.45%

The model:
- corrected June 2023,
- but damaged March, July and August,
- did not fix February,
- did not fix May,
- did not fix November.

Thus the net effect is materially negative.

## Interpretation
A monthly GOLD-only discriminator that appears plausible on 2010–2022 does **not** generalize to the 2023 turning-point pattern. This is evidence against adding another monthly classifier merely to repair 2023.

November 2023 is particularly informative: the monthly 1M-vs-3M signal was not enough to trigger the frozen model, while the independently reconstructed weekly Tactical state was already in conflict. Therefore the remaining potentially useful information is genuinely higher-frequency/event-level, not another monthly momentum transformation.

## Important limitation
The archived Tactical workbook preserves historical Tactical performance mainly in aggregate cells, not a full month-by-month 2010–2022 event table with weekly gap magnitude/persistence. The exact pinned W1 source is identified, but a complete event-level feature panel is not yet stored as a canonical artifact. Therefore a stronger claim that all weekly conflict discriminators have been exhausted would be false.

Status:
- `MONTHLY_REVERSAL_DISCRIMINATOR = REJECT`
- `PRE2023_GENERALIZATION = FAIL_ON_2023`
- `WEEKLY_EVENT_LEVEL_DISCRIMINATOR = UNRESOLVED_NEEDS_CANONICAL_EVENT_PANEL`

## Auto-control
- target leakage: PASS
- 2023 used for candidate selection: NO
- 2024–2026 used for candidate selection: NO
- random split: NO
- GPR vintage leakage risk admitted/excluded: PASS
- October flat-month handling: PASS
- false-flip damage counted: PASS
