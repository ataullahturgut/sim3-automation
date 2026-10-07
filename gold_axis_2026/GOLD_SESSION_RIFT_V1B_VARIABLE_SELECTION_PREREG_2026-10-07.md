# SESSION RIFT V1B — VARIABLE-SELECTION CHALLENGER — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline

Canonical RIFT V1 remains unchanged:
- reversal target = actual session direction differs from pre-target 12h XAU momentum;
- StandardScaler + LogisticRegression(C=1.0, class_weight=balanced);
- reversal threshold = 0.70;
- same fixed correction rule;
- same upstream baselines audited separately.

## Objective

Test whether RIFT correction becomes more stable when its own reversal variables are selected separately by session.

This is a within-RIFT feature analysis. No new data family is added.

## Candidate universe

Only the nine canonical RIFT variables:
- trend_strength
- opposite_semivar_share
- deceleration_6h
- path_consistency
- trend_close_location
- opposite_extreme_recency
- jump_concentration_24
- trend_to_range
- adverse_excursion

No SAGE, A1, PATH_GLOBAL probability, COT, macro, GVZ, cross-metal, target-window or downstream model-state feature may enter the RIFT classifier.

## Clock contract

Unchanged:
- all features are generated from governed XAU15;
- `anchor_available < target_start`;
- maximum governed reference staleness <= 60 minutes;
- no target-window data.

## Chronology

- 2022: warm-up only
- 2023–2024: nested variable selection and downstream correction evaluation
- 2025: closed until representation and eligible baseline/window pairs are frozen
- 2026: unopened

## Outer chronology

Preserve RIFT's monthly expanding causal structure.

For each session and each scored month in 2023–2024:
1. training contains only reversal labels matured before the first target start in that month;
2. current month is untouched outer test data;
3. minimum outer training rows = 80.

## Inner variable selection

Within each outer training history:

1. Use up to three chronological inner validation months.
2. Use StandardScaler + L1 LogisticRegression(class_weight=balanced) as selector only.
3. Selector C grid:
   - 0.03
   - 0.10
   - 0.30
   - 1.00
   - 3.00
4. Evaluate each selected subset with the unchanged final RIFT estimator:
   - StandardScaler
   - LogisticRegression(C=1.0, class_weight=balanced)
5. Primary selector metric = reversal Balanced Accuracy.
6. Within 1 percentage point of best reversal BA, prefer:
   - lower reversal Brier;
   - fewer variables;
   - smaller selector C.
7. Keep at least 2 RIFT variables.
8. Outer month never selects its own variables.

## Development correction evaluation

The fold-local selected RIFT probability is then applied to each governed upstream baseline using the unchanged correction rule:

- if baseline already opposes 12h momentum: keep;
- if baseline follows momentum and p_reversal >= 0.70: flip;
- otherwise keep.

Evaluate separately against:
- A0 CORE3
- A1 ARCR
- PATH_GLOBAL 1H
- STRUCTURAL_IRIS A1+1H

## Selected-RIFT development pass rule

For a window/baseline pair to open selected-RIFT 2025 transport:

- 2023 corrected accuracy >= baseline accuracy - 1 pp;
- 2024 corrected accuracy >= baseline accuracy - 1 pp;
- 2023 corrected Brier <= baseline Brier + 0.003;
- 2024 corrected Brier <= baseline Brier + 0.003;
- combined corrected BA >= baseline BA;
- combined net rescue > 0;
- min(corrected UP recall, corrected DOWN recall) >= 30%.

Exactly the canonical RIFT V1 downstream gate is reused.

## Final frozen RIFT subset

After all 2023–2024 outer months are complete:

- rank variables by outer-month selection frequency;
- prefer variables selected in both 2023 and 2024;
- freeze 2–6 variables per session;
- no 2025 outcome may alter the subset.

## 2025

After development closes, transport may compare:
- canonical full RIFT V1;
- frozen selected RIFT V1B;
- unchanged upstream baseline;

but only for baseline/window pairs eligible under their respective pre-2025 gates.

No 2025 threshold tuning, feature reselection or rescue search is allowed.
