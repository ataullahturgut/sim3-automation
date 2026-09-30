# GOLD MONTHLY — E/G Historical Signal Validation Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / BINDING HISTORICAL VALIDATION SPEC  
**Purpose:** test whether E and G represent recurring historical risk states, and where scientifically possible test whether the frozen ChHHO main model actually incurs elevated error at those historical signals.

## 1. Two-layer design

This validation deliberately separates two questions.

### Layer 1 — market-state validation
Use canonical monthly Gold only. No ChHHO prediction is required.

- E market-state precursor: Gold monthly price > 20% above the trailing prior-12-month mean.
- G: trailing 3-month Gold monthly log return <= -10%.

For 2010-01..2021-12 report:
- every signal origin;
- next-month Gold log return and absolute move;
- signal-group mean and median next-month absolute move;
- baseline mean and median next-month absolute move;
- uplift ratio;
- count above the unconditional 2010-2021 next-month absolute-return Q3.

The Q3 threshold is descriptive only and is not used to tune E or G.

### Layer 2 — ChHHO historical stress replay
For each historical E/G origin, run the unchanged canonical ChHHO-ANFIS model only if the frozen CURRENT8 training contract can be built.

The goal is to ask:
> Under the same current-method GPR definition, would ChHHO have shown elevated error at the historical signal?

This layer is explicitly a **counterfactual same-methodology stress replay**, not point-in-time production validation.

## 2. GPR authority for stress replay

Use the earliest proven current-method GPR snapshot:

- official repo: `iacoviel/iacoviel.github.io`
- file: `gpr_files/data_gpr_export.xls`
- snapshot commit: `5e4dfbfda5a89aceff9b30f5454fb36ab33c3baf`
- commit time: 2021-10-18T15:19:48Z

For each historical target:
- truncate GPR history to the required lag month;
- do not use later monthly observations;
- use the unchanged canonical CURRENT8 sample builder and unchanged ChHHO optimizer.

Important limitation:
The current GPR methodology did not exist at the old historical origin dates. Therefore this replay must never be labeled PIT or out-of-sample validation. It is a controlled same-methodology historical stress test only.

No old-method GPR source is permitted.

## 3. Model/data invariants

- Model: unchanged canonical ChHHO-ANFIS.
- Model features: unchanged frozen CURRENT8/VW-MIDAS contract.
- Database access: READ_ONLY.
- No target month in training.
- No alarm threshold retuning.
- No optimizer retuning.
- Historical signal selection depends only on canonical Gold data, not model errors.
- Origins with insufficient training history must be reported as unbuildable, not filled with another model.

## 4. Alarm definitions

### E full ChHHO alarm
Only for buildable ChHHO origins:
- E market-state precursor is true; and
- |ChHHO predicted Gold log return − current canonical Gold 1m log return| > 5 percentage points.

### G full alarm
- canonical Gold 3m log return <= -10%.

G does not require ChHHO prediction to fire; ChHHO is run only to evaluate model error conditional on the signal.

## 5. Error labels

Report all three frozen model-error labels:

- HIGH_AE: AE > 63.06 USD
- HIGH_APE: APE > 2.96117%
- HIGH_RETURN_ERROR: absolute Gold log-return forecast error > 3.00590 percentage points

For historical cross-price-level comparison, HIGH_RETURN_ERROR and HIGH_APE are the primary robustness checks; HIGH_AE is retained because it is the project's main nominal error threshold.

## 6. Interpretation rules

- Strong market-state recurrence does not by itself prove ChHHO failure.
- ChHHO counterfactual stress results do not count as PIT validation.
- A signal is strengthened if it shows both:
  1. materially elevated historical next-month movement versus baseline; and
  2. repeated elevated ChHHO error in buildable historical stress cases.
- A weak/contradictory historical record must be reported even if 2025/2026 looked strong.
