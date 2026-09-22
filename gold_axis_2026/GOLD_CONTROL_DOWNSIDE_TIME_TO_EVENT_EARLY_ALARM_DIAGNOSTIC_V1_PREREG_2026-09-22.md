# GOLD CONTROL — TIME-TO-EVENT / EARLY-ALARM DIAGNOSTIC V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** DOWNSIDE_TIME_TO_EVENT_EARLY_ALARM_DIAGNOSTIC_V1_RESEARCH  
**Parent risk model:** DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH / SQRT_HAR_DR  
**Branch:** gold-downside-time-to-event-diagnostic-v1-20260922  
**Runtime / production authority:** NONE  
**Manifest update:** DEFERRED UNTIL RESULTS ARE FROZEN  
**Production DB writes:** FORBIDDEN

## 1. Scientific question

The parent SQRT-HAR-DR model is a downside-risk sensor, not a direction model. In 2025, interpreting every parent high-risk alarm as a next-day DOWN call produced 45 true DOWN hits and 45 false DOWN alarms.

V1 asks a narrower diagnostic question:

> Are some alarms that are false at t+1 actually early warnings of a downside event that occurs at t+2, t+3 or t+5?

This experiment does **not** fit a new predictive model. It only measures event delay / first-passage behavior after frozen parent alarms.

## 2. Methodological authority scan

The diagnostic is motivated by three established methodological ideas:

1. **Discrete-time survival / time-to-event prediction:** event risk may be represented over prespecified future intervals rather than collapsed into one binary next-step label. Suresh, Severn & Ghosh (2022), *Survival prediction models: an introduction to discrete-time modeling*, BMC Medical Research Methodology 22:207, DOI 10.1186/s12874-022-01679-6.
2. **Early-warning evaluation with prediction horizons:** alarm correctness depends on whether an event occurs inside a prespecified future window and on alarm lead time, rather than only at the immediately following time point. This is standard in predictive monitoring / early-event evaluation.
3. **Financial early-warning windows:** Gresnigt, Kole & Franses (2015), *Interpreting financial market crashes as earthquakes: A new Early Warning System for medium term crashes*, Journal of Banking & Finance 56, 123–139, DOI 10.1016/j.jbankfin.2015.03.003, explicitly predicts crash occurrence over a future multi-day window.

These sources justify testing a time window. They do **not** prove that SQRT-HAR-DR is an early-warning model; that is the empirical question here.

## 3. Frozen parent alarm

Use the exact frozen annual-origin SQRT_HAR_DR forecast surface from:

DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH.

A primary alarm at origin t is exactly the frozen parent field:

sqrt_high_risk_alert == 1

No parent refit, threshold change, re-normalization or reconstruction from target-period outcomes is permitted.

## 4. Data / clock

Parent Gold source remains:

public.xau_intraday_research_cache_5m

Daily clock:
- America/New_York;
- retained weekdays only;
- daily close = final retained 5-minute close;
- future horizons are counted in retained trading days, not calendar days.

No overnight return is inserted into realized semivariance construction.

For the event-delay diagnostic only, future daily closes from the same retained Gold daily sequence are used to determine what happened after each already-issued historical alarm.

## 5. Evidence periods

- 2022, 2023, 2024: primary retrospective falsification panel.
- 2025: retrospective stress description only; known 45/45 next-day diagnostic cannot be used to select rules.
- 2026 YTD: retrospective transport/stress description only.
- No period is pristine prospective confirmation for this hypothesis.

No random split.

## 6. Definition of a t+1 false direction interpretation

For an origin t:

- parent alarm = 1;
- one-trading-day origin-anchored cumulative close return:
  R1 = log(C_(t+1) / C_t).

A **t+1 false direction interpretation** is:

parent alarm == 1 AND R1 >= 0.

This does not mean the parent risk model itself is false; it means only that treating the risk alarm as an immediate DOWN call would be false.

## 7. Primary event: origin-anchored downside first passage

For k in {1,2,3,5}:

Rk = log(C_(t+k) / C_t).

A sign-level downside event has occurred by horizon h if any retained trading day k<=h satisfies:

Rk < 0.

For t+1 false interpretations, the first possible delayed conversion is k=2.

Record:
- first_down_delay in {2,3,4,5, NONE};
- conversion_by_t2;
- conversion_by_t3;
- conversion_by_t5;
- minimum origin-anchored cumulative return through each horizon.

Primary diagnostic horizon = **t+3**.
t+2 and t+5 are prespecified secondary horizons.

## 8. Severity diagnostics

A trivial tiny sign crossing is not sufficient by itself to establish useful early-warning behavior. Therefore two formation-only severity diagnostics are also frozen.

At each annual origin, using only historical supervised daily close returns completed before the target year:

- Q25_1D = nearest-rank 25th percentile of one-day close returns;
- Q05_1D = nearest-rank 5th percentile of one-day close returns.

For each alarm, calculate the minimum origin-anchored cumulative return over days 1..h.

Report whether the minimum by h is:
- <= Q25_1D: material downside excursion;
- <= Q05_1D: extreme downside excursion.

These are severity diagnostics, not new alarm thresholds.

## 9. Control cohorts

The question is not answered by the raw conversion percentage alone because a DOWN move may occur by chance within several days.

Two prespecified control groups are used within each evaluation year.

### A. CONTEXT_CONTROL — primary comparator

Origins where:
- sqrt_high_risk_alert == 0;
- sqrt_normalized_risk_score >= 0.80;
- R1 >= 0.

This compares false t+1 alarms against elevated-risk non-alarm contexts that also did not fall at t+1.

### B. BROAD_CONTROL — secondary comparator

Origins where:
- sqrt_high_risk_alert == 0;
- R1 >= 0.

No target-year outcome is used to alter the 0.80 boundary.

If CONTEXT_CONTROL support is below 10 observations in a year, that annual comparison is tagged INSUFFICIENT_SUPPORT; pooled analysis remains reportable.

## 10. Mandatory outputs

For alarm false-t+1 cohort and both control cohorts, by year and pooled 2022–2024:

- cohort size;
- conversion rate by t+2, t+3, t+5;
- first-down-delay distribution;
- median / mean first delay among converters;
- Q25 excursion rate by t+3 and t+5;
- Q05 excursion rate by t+3 and t+5;
- minimum cumulative-return distribution.

For ALARM_FALSE_T1 versus CONTEXT_CONTROL:
- absolute conversion-rate lift;
- risk ratio;
- odds ratio;
- same comparison for Q25 and Q05 excursion rates.

BROAD_CONTROL comparison is secondary.

No classifier AUC is relevant because V1 fits no model.

## 11. Frozen interpretation rule

V1 is labeled **EARLY_ALARM_TIMING_SIGNAL_SUPPORTED** only if all of the following hold on pooled 2022–2024 evidence:

1. t+3 sign-conversion rate for ALARM_FALSE_T1 exceeds CONTEXT_CONTROL by at least 0.10 absolute;
2. pooled t+3 risk ratio >= 1.25;
3. annual t+3 conversion lift is positive in at least 2 of 3 years with adequate control support;
4. pooled t+3 Q25 downside-excursion rate is at least 0.05 higher than CONTEXT_CONTROL;
5. the conclusion does not depend solely on 2025 or 2026 stress evidence.

If CONTEXT_CONTROL pooled support is insufficient (<30), condition 1–4 are evaluated against BROAD_CONTROL and the conclusion is downgraded to EARLY_ALARM_TIMING_SIGNAL_WEAK_SUPPORT even if thresholds pass.

If these conditions fail, the timing hypothesis is labeled:

EARLY_ALARM_TIMING_NOT_SUPPORTED

and the next research lane returns to genuinely new direction-resolving sensors.

This is a diagnostic research gate, not runtime promotion.

## 12. Forbidden post-result actions

After any 2022–2024 outcome is inspected under this identity, V1 may not:
- change horizons;
- redefine false alarm;
- replace origin-anchored returns with a different label;
- alter the 0.80 context boundary;
- change Q25/Q05 severity thresholds;
- remove inconvenient years;
- add a predictive model under the same V1 identity;
- use 2025/2026 to rescue a failed pre-2025 gate.

Any predictive survival/hazard successor requires a new identity and new preregistration.
