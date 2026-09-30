# GOLD MONTHLY — Within-Regime Extreme / Stress Detector V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / MARKET-ONLY WITHIN-REGIME EXTREMENESS  
**Parents:** Regime Discovery V1; Prototype Alignment V1; Transition Detector V1/V2

## 1. Scientific question

Can we identify months in which the market remains inside the same latent regime but is behaving unusually/extremely relative to that regime's own historical training distribution?

This is explicitly different from TRANSITION.

The detector does **not** ask:
- which regime comes next;
- whether ChHHO will fail;
- whether an alarm should be trusted.

Output:
- `EXTREME`
- `NORMAL`
- `DEFER` when the month is not a confident same-regime observation.

## 2. Independence from the transition detector

V1 Extreme does **not** use Transition V1/V2 as an input.

Transition V2 is not operationally promoted, so Extreme V1 must be measured independently.

After both layers are computed, their overlap is reported descriptively.

## 3. Underlying HMM schedules

Evaluate both:
- EXPANDING_REFIT
- ANNUAL_ANCHORED

Use the exact same scaler/PCA/HMM fitting schedules already governed in the regime project.

Prototype semantic labels may be attached for reporting, but **semantic prototypes are not used by the Extreme decision rule**.

This avoids using the frozen 2010-2024 semantic prototypes as a historical extremeness threshold.

## 4. Eligibility: "within-regime"

A month t is eligible for NORMAL/EXTREME classification only if, under the HMM fit available at t:

- the best raw latent state at t-1 equals the best raw latent state at t;
- posterior of that raw state at t-1 >= 0.60;
- posterior of that raw state at t >= 0.60.

Otherwise:
- `DEFER`.

This is a same-latent-state stability requirement and uses no future month.

## 5. Frozen anomaly signals

For each eligible month t, compute four origin-safe signals from that fit's training history only.

### E1 — state emission tail
Current observation's emission log-density under the persistent raw latent state is at or below the **10th percentile** of training emission log-densities for months whose hard filtered state equals that latent state.

Minimum state-pool size: 8.

### E2 — predictive surprise
Current one-step predictive log score is at or below the **10th percentile** of sequential one-step predictive log scores on the fit's training history.

### E3 — within-state 13D distance
In the fit's own 13-feature standardized space:
- estimate each raw latent state's center as the filtered-posterior-weighted mean of training observations;
- calculate Euclidean distance from current month to the persistent state's center.

EXTREME signal if this distance is at or above the **90th percentile** of distances for training months whose hard filtered state equals that same state.

Minimum state-pool size: 8.

### E4 — one-month market-state jump
Euclidean norm of the change in the fit-standardized 13D market-state vector from t-1 to t.

Signal if at or above the **90th percentile** of historical training month-to-month jump norms.

## 6. Frozen V1 rule

For eligible months:

- `EXTREME` if at least **2 of E1..E4** are TRUE.
- otherwise `NORMAL`.

For ineligible months:
- `DEFER`.

Also report anomaly count 0..4 and active signal names.

No threshold search is allowed in V1.

## 7. No-outcome governance

Forbidden from detector construction:
- ChHHO forecast;
- ChHHO error / APE / AE;
- HIGH/MEDIUM/NORMAL forecast-error labels;
- alarm A/B/C/D/E/G/H/I/T information;
- routing/model-switch information;
- future market observations.

The detector is unsupervised relative to forecast performance.

## 8. Reporting periods

Report separately:
- historical: 2015-07..2021-12
- later validation: 2022-01..2024-12
- opened transport/inspection: 2025-01..2026-08
- full replay: 2015-07..2026-08

For each schedule:
- total months;
- eligible months;
- DEFER count/rate;
- EXTREME count;
- EXTREME rate among eligible;
- NORMAL count;
- anomaly-count distribution;
- extreme run lengths;
- semantic-regime distribution for reporting only;
- overlap with frozen Transition V2 flags.

## 9. Distinctness diagnostic

Extreme and Transition are intended to measure different phenomena.

On the 2022-2024 later-validation period, report:
- EXTREME only;
- TRANSITION-V2 only;
- both;
- neither.

A useful Extreme layer should not merely duplicate Transition V2.

Descriptive distinctness target:
- fewer than 50% of EXTREME months also flagged by Transition V2.

This target is a diagnostic, not a threshold-tuning target.

## 10. Selectivity diagnostic

Without using forecast outcomes, the layer should remain selective.

For EXPANDING_REFIT:
- historical EXTREME rate among eligible should be between 5% and 30%;
- 2022-2024 validation EXTREME rate among eligible should be between 5% and 30%;
- DEFER rate may be reported but is not optimized.

If the rate falls outside this range, V1 is considered poorly calibrated as a descriptive extreme layer.

## 11. Mandatory checkpoints

Report month-level status/signals for:
- 2024-03..2024-06
- 2026-01..2026-08

The 2026 months are already inspected and do not affect the frozen rule.

## 12. Stage boundary

This stage does not:
- retune Transition V2;
- select/weight/suppress alarms;
- modify the gold forecast;
- route between forecast models.

After this stage, decide whether the combined market-state engine is sufficiently informative to justify:
- a structurally different transition model, or
- freezing Transition as descriptive only and proceeding with regime/extreme reliability analysis.
