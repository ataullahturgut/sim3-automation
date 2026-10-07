# SESSION MODEL-02 — SHALLOW CART — VARIABLE-SELECTION PREREGISTRATION

**Date:** 2026-10-07  
**Status:** **BINDING BEFORE MODEL-02 OUTCOME REVIEW**

## Objective

Run Shallow CART on the corrected V5 session targets using the **most useful leakage-safe variables for each session**, rather than forcing one global feature list.

Feature selection is part of Model-02 and must be completed inside development chronology before 2025 is opened.

## Fixed model identity

- estimator: `DecisionTreeClassifier`
- criterion: `log_loss`
- max_depth: **3**
- min_samples_leaf: **60**
- decision threshold: **0.50**
- no pruning/hyperparameter search from 2025/2026
- random split: prohibited

These are inherited from the legacy raw-source Shallow CART identity. The experiment changes the target/clock and adds governed variable selection; it does not tune tree depth or leaf size.

## Candidate variable universe

The candidate universe preserves the legacy raw-source CART information families.

### Gold
- gold_r1
- gold_r5
- gold_r21
- sigma20

### Other precious metals
- silver_r1 / silver_r5 / silver_r21
- platinum_r1 / platinum_r5 / platinum_r21
- palladium_r1 / palladium_r5 / palladium_r21

### Equity / risk-on
- nasdaq_r1 / nasdaq_r5 / nasdaq_r21
- sp500_r1 / sp500_r5 / sp500_r21
- djia_r1 / djia_r5 / djia_r21

No model-output state, archived prediction, target-derived variable, 2025-selected variable, or 2026-selected variable may enter this candidate universe.

Rates/FX/VIX/GVZ/COT/event variables are **not silently appended to Model-02**. They belong to other legacy model/specialist lineages unless separately preregistered. This keeps Shallow CART comparable to its historical raw-source identity.

## Source-ready rule

Every daily candidate must be known before the session target starts.

For this conservative Model-02 replay, the usable observation is the latest candidate observation from a **strictly earlier America/New_York calendar date** than the target start. Same-NY-date daily values are not used.

Rows with daily source age > 7 calendar days are ineligible.

Targets are the binding V5 session start-OPEN -> final-15m-CLOSE labels. DAILY/H3 labels are prohibited.

## Chronology

- 2022: governed warm-up/training only; no performance claim
- 2023–2024: development + variable selection
- 2025: one-time frozen-specification causal transport
- 2026: unopened for selection

Only matured same-window outcomes may enter training.

## Fold-local variable analysis

For every session and every 5-row outer development block:

1. Build the training set using only outcomes matured before the first target start in the block.
2. Require at least 240 matured rows.
3. Inside that training history, create 2–3 chronological inner validation folds of 30 rows, each with at least 180 earlier training rows.
4. Fit the **fixed Shallow CART** on the complete candidate pool in each inner fold.
5. Measure held-out permutation contribution for each variable using:
   - change in Balanced Accuracy;
   - change in Brier score;
   - split-use stability.
6. A variable is considered stable when it is used by the tree in at least half of available inner folds and has positive held-out contribution to Balanced Accuracy or Brier in the inner validation evidence.
7. Rank stable variables by:
   - fold stability;
   - median held-out Balanced-Accuracy contribution;
   - median held-out Brier contribution;
   - split-use frequency.
8. Keep at most **6 variables** per outer block. If fewer than 3 pass the stability rule, fill to 3 using the highest-ranked split-used variables from the same inner evidence.

The outer block is then scored using only the variables selected without seeing that block's outcome.

## Development comparators

On the exact same scored outer rows, compare:

1. **SELECTED_CART** — fold-local selected variables
2. **GOLD_ONLY_CART** — gold_r1, gold_r5, gold_r21, sigma20
3. **FULL_LEGACY_CART** — all candidate variables

Primary metric: **Balanced Accuracy**.

Guardrail:
- minimum of UP recall and DOWN recall must be >= **30%**.

Tie rule:
- candidates within 1.0 percentage point of the best Balanced Accuracy are compared by lower Brier;
- if still effectively tied, prefer fewer variables.

## Final per-session feature freeze

After all 2023–2024 development outer predictions are complete:

- if SELECTED_CART is the admissible development winner, freeze a session-specific subset from fold-local selection frequencies;
- a feature should preferably appear in both scored development years;
- target subset size: 3–6 variables;
- if SELECTED_CART does not beat the fixed alternatives under the development rule, freeze the winning fixed representation instead.

No 2025 outcome may alter the frozen feature set.

## 2025 transport

Replay the frozen representation through the continuous five-row causal chronology and report only 2025 rows.

Required metrics for every session:
- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- log loss
- selected/frozen feature list
- coverage

2025 is evidence only; no rescue retuning is permitted.

## Historical H3 CART evidence

The old DAILY/H3 raw-source CART screen may be reported only as historical context. Its result that GOLD_ONLY had the best H3 Brier does **not** select the session variables.

The corrected V5 session variable analysis is the only selection authority for SESSION Model-02.
