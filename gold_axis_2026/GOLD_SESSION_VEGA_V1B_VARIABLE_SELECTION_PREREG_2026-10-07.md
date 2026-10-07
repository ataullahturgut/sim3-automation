# SESSION VEGA V1B — VARIABLE-SELECTION CHALLENGER — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline

Canonical VEGA V1 remains unchanged:
- reversal target against pre-target 12h XAU momentum;
- StandardScaler + LogisticRegression(C=1.0, class_weight=balanced);
- threshold = 0.70;
- D-1-or-earlier GVZ information rule;
- same correction rule;
- same upstream baseline separation.

## Candidate universe

Only the nine canonical VEGA variables:
- gvz_z252
- gvz_r1
- gvz_r3
- gvz_r5
- gvz_vs_med20
- iv_rv24_gap
- iv_rv48_gap
- trend_strength
- gvz_shock_x_trend

No new data family may enter.

## Information-time contract

- GVZ observation date <= New York origin date D-1;
- same-day GVZ prohibited;
- XAU state pre-target only;
- no target-window information.

## Chronology

- 2022 warm-up
- 2023–2024 nested variable selection / development
- 2025 closed until representation and pair eligibility are frozen
- 2026 unopened

## Outer / inner design

Preserve monthly expanding VEGA chronology.

For each scored 2023–2024 month:
- train only on matured prior rows;
- select features inside training history only;
- current month is untouched outer test.

Inner selector:
- chronological last up-to-three validation months;
- L1 balanced logistic selector;
- C grid = 0.03, 0.10, 0.30, 1.00, 3.00;
- evaluate subsets with unchanged final balanced Logistic C=1.0;
- primary metric = reversal Balanced Accuracy;
- within 1pp prefer lower Brier, fewer variables, smaller selector C;
- retain at least 2 VEGA variables.

## Downstream correction gate

Apply fold-local selected VEGA probabilities using the unchanged 0.70 rule against each upstream baseline separately.

Reuse canonical VEGA development pass rule exactly:
- annual accuracy no worse than baseline by >1pp;
- annual Brier no worse than baseline by >0.003;
- combined BA >= baseline;
- combined net rescue > 0;
- corrected min class recall >=30%.

## Frozen subset

After 2023–2024:
- rank by outer-month selection frequency;
- prefer cross-year stable variables;
- freeze 2–6 variables per session;
- 2025 cannot alter the subset.

## 2025

Only pairs pre-eligible under full VEGA V1 or selected VEGA V1B may be transported.
No 2025 threshold/feature/session/baseline rescue is permitted.
