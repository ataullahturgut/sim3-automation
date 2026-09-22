# GOLD CONTROL — UP COUNTERSIGN VETO V2 FULL-HISTORY PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** DOWNSIDE_UP_COUNTERSIGN_VETO_V2_FULLHISTORY_RESEARCH  
**Parent:** frozen SQRT-HAR-DR next-trading-day downside-risk alert  
**Parent source artifact:** GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Question

When SQRT-HAR-DR raises a high-downside-risk alarm, can an already-existing historical UP-capable engine safely suppress false forced-DOWN interpretations without discarding too many true DOWN alarms?

A veto means NO-DOWN / SUPPRESSED. It is not an UP trading signal.

## 2. Frozen candidate set

The candidate set is fixed before intersection outcomes are computed:

1. FAST_UP
   - source engine: frozen Gold R4 FAST state;
   - frozen rule: FAST state == ROBUST_UP;
   - implementation: SMA20 with 2-day persistence, no parameter changes.

2. RV_LOGIT_UP
   - source: DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_RESEARCH;
   - frozen rule: RV_LOGIT_pred_up == 1.

3. RM_LOGIT_UP
   - same source;
   - frozen rule: RM_LOGIT_pred_up == 1.

4. AR1_RM_LOGIT_UP
   - same source;
   - frozen rule: AR1_RM_LOGIT_pred_up == 1.

5. TTSM_S1_UP
   - source: DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_RESEARCH;
   - frozen rule: ttsm_s1_signal == +1.

6. TTSM_S2_UP
   - same source;
   - frozen rule: ttsm_s2_signal == +1.

No candidate threshold may be changed after intersection results are seen.

## 3. Primary common-support period

Primary ranking uses exact-date common support in **2023–2024** because all six candidates can be constructed there.

Only SQRT parent alarm days are evaluated.

For each exact origin date:
- baseline forced-DOWN call = SQRT alarm;
- actual DOWN iff parent target_close_return < 0;
- actual UP otherwise;
- candidate UP vetoes only when its frozen UP rule is true.

No forward fill, nearest-date matching, weekly carry, or interpolation is allowed.

## 4. FAST construction and clock check

FAST uses the frozen research series:
XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1.

Frozen state rule:
- daily SMA20;
- compare close to SMA on t-1 and t;
- ROBUST_UP iff both comparisons are UP;
- ROBUST_DOWN iff both are DOWN;
- otherwise MIXED.

Before FAST is accepted as a parent-alarm veto candidate:
- exact origin dates must join to parent dates;
- next-day return sign from the FAST daily-close axis and parent target_close_return must match on all primary common-support parent alarm rows, or any mismatches must be disclosed and FAST classified clock-misaligned for those rows.

No FAST rule is refit or tuned.

## 5. Metrics

For every candidate on the 2023–2024 common parent-alarm support:

- overlap alarms;
- baseline TP = actual DOWN;
- baseline FP = actual UP;
- vetoed count;
- GOOD_VETO = veto on actual UP;
- BAD_VETO = veto on actual DOWN;
- veto precision = GOOD_VETO / vetoed;
- false-alarm reduction = GOOD_VETO / baseline FP;
- true-DOWN retention = (baseline TP - BAD_VETO) / baseline TP;
- remaining forced-DOWN precision;
- precision change versus no-veto baseline;
- net veto benefit = GOOD_VETO - BAD_VETO.

## 6. Diagnostic ranking rule

This ranking is descriptive and does not authorize promotion.

Candidates are ordered by:

1. SAFETY-QUALIFIED first: true-DOWN retention >= 0.80 and at least 3 vetoes;
2. among safety-qualified candidates: higher false-alarm reduction;
3. tie-breaker: higher veto precision;
4. tie-breaker: higher remaining forced-DOWN precision.

Candidates with fewer than 3 vetoes are labelled INSUFFICIENT_ACTION_SUPPORT and placed below useful safety-qualified candidates even if retention is 100%.

Candidates with true-DOWN retention < 0.80 are labelled UNSAFE_VETO and placed below safety-qualified / insufficient-action candidates. Their descriptive ordering is by higher net veto benefit, then higher retention.

The do-nothing baseline is retained explicitly.

## 7. 2025 stress

After the 2023–2024 ranking is frozen, apply the same unchanged rules to 2025.

2025 is stress evidence only:
- it cannot change candidate thresholds;
- it cannot alter the pre-2025 ranking rule;
- it cannot rescue an unsafe pre-2025 candidate.

## 8. Forbidden actions

Under V2 do not:
- tune any UP threshold;
- replace ROBUST_UP with another FAST state;
- use FAST episode onset instead of daily state after seeing results;
- combine candidates post hoc;
- add GVZ/SLOW/Macro Event after seeing candidate outcomes;
- optimize Boolean rules;
- tune on 2025;
- reinterpret a veto as an UP trade.

A combined/context-qualified successor requires a new preregistered identity.
