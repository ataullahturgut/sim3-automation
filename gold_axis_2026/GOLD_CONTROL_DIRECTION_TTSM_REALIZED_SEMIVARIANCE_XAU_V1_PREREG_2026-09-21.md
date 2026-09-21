# GOLD CONTROL — TTSM REALIZED-SEMIVARIANCE DIRECTION V1 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_RESEARCH`  
**Primary authority:** Liu, Lu, Li & Wang (2023), *Time series momentum and reversal: Intraday information from realized semivariance*, Journal of Empirical Finance 72, 54–77, DOI 10.1016/j.jempfin.2023.03.001  
**Runtime authority:** NONE  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS  
**Production writes:** NONE

## 1. Goal

Test the source TTSM rule on governed Spot-XAU data as a standalone direction/reversal model, with special emphasis on DOWN detection and UP-momentum-to-DOWN reversal detection.

This is a source-constrained Spot-XAU adaptation, not an exact commodity-futures replication.

## 2. Frozen data contract

Source: `public.xau_intraday_research_cache_5m`.

Daily grouping:
- timezone: America/New_York;
- Monday–Friday only;
- retain a date only if >=240 five-minute closes;
- daily close = final retained 5m close;
- intraday log returns are consecutive within-date closes only; no cross-date/overnight return is inserted into realized semivariance.

No interpolation, forward fill, alternate-provider substitution, or future information.

## 3. Frozen source rule

Daily close-to-close log return:
`r_t = log(C_t/C_(t-1))`.

Original TSM state:
- lookback J=20 daily returns;
- momentum score = sum of the most recent 20 daily log returns, equivalent to log(C_t/C_(t-20));
- UP momentum if score > 0;
- DOWN momentum otherwise.

Five-day partial realized semivariances:
- compute squared 5m intraday returns;
- `RS+_t` = sum of squared positive 5m returns over retained days t-4..t;
- `RS-_t` = sum of squared negative 5m returns over retained days t-4..t.
Using average instead of sum is scale-equivalent for the percentile rule; V1 freezes the source-form sum.

Reference thresholds:
- fixed rolling history = 250 TTSM daily observations, including current day t, exactly t-249..t;
- marginal 80th-percentile reference for RS+ and RS- separately;
- empirical nearest-rank quantile is frozen as the deterministic reconstruction of the source empirical-CDF percentile:
  sorted value at rank ceil(0.80*n), n=250.

Regions:
- Region 1: RS+ > q80+ AND RS- > q80-;
- Region 2: RS+ <= q80+ AND RS- > q80-;
- Region 3: RS+ <= q80+ AND RS- <= q80-;
- Region 4: RS+ > q80+ AND RS- <= q80-.

Source action mapping:
- Region 1: close out / NEUTRAL for S1 and S2.
- Region 3: retain original TSM signal for S1 and S2.
- Region 2:
  - S1: turn LONG to SHORT and keep SHORT => DOWN regardless of original TSM sign.
  - S2: turn LONG to SHORT; close original SHORT => DOWN if TSM=UP, otherwise NEUTRAL.
- Region 4:
  - S1: turn SHORT to LONG and keep LONG => UP regardless of original TSM sign.
  - S2: turn SHORT to LONG; close original LONG => UP if TSM=DOWN, otherwise NEUTRAL.

Output values:
- +1 = UP;
- -1 = DOWN;
- 0 = NEUTRAL / abstain.

Target:
- next retained trading-day close direction;
- UP iff C_(t+1)>C_t;
- DOWN iff C_(t+1)<C_t;
- equal close omitted.

## 4. Chronology

No fitted parameters and no tuning.

- 2021 and earlier: warm-up / percentile-history formation only.
- 2022–2023: development/audit reporting only.
- 2024: fixed pre-2025 validation.
- 2025: locked retrospective challenge, run only after pre-2025 evidence is frozen.

2025 cannot alter J=20, 5-day semivariance horizon, 250-day reference window, 80th percentile, quantile method, region boundaries, source mapping, clock, or metrics.

## 5. Mandatory evaluation

For TSM, TTSM-S1 and TTSM-S2 by period:
- n;
- coverage;
- accuracy on active signals;
- balanced accuracy on active signals;
- UP sensitivity on full timeline;
- DOWN sensitivity on full timeline;
- UP and DOWN precision;
- DOWN F1 using full-timeline missed/neutral cases as misses;
- false-DOWN rate among actual UP days;
- forecast UP/DOWN/NEUTRAL counts;
- always-UP and always-DOWN raw baselines.

Reversal-specific diagnostics:
- count of actual next-day DOWN cases while TSM state is UP;
- proportion of those captured as DOWN by TTSM (UP->DOWN reversal sensitivity);
- precision of DOWN alerts issued in UP-momentum states;
- false DOWN-alert burden in UP-momentum states;
- Region 2 frequency and next-day DOWN rate;
- Region 3/4/1 frequencies and next-day DOWN rates.

The primary scientific question is whether TTSM improves DOWN and UP->DOWN reversal detection relative to TSM without an unacceptable false-DOWN burden.

## 6. Frozen pre-2025 research gate

TTSM-S1 is the primary source rule. TTSM-S2 is a conservative source comparator.

A model is retained as a promising standalone DOWN/reversal signal only if on 2024:
- full-timeline DOWN sensitivity >= TSM DOWN sensitivity + 0.10;
- UP->DOWN reversal sensitivity >= TSM + 0.10;
- active-signal balanced accuracy >= 0.52;
- DOWN precision >= 0.45;
- active coverage >= 0.50.

This is a research gate, not runtime promotion.

If the 2024 gate fails, unchanged 2025 may still be replayed for audit completeness but cannot rescue the failed pre-2025 decision.

## 7. Interpretation lock

Possible conclusions:
- `PRE2025_DOWN_REVERSAL_SIGNAL_SUPPORTED`
- `PRE2025_DOWN_REVERSAL_SIGNAL_NOT_SUPPORTED`
- `2025_TRANSPORT_SUPPORTED`
- `2025_TRANSPORT_NOT_SUPPORTED`

No threshold rescue, class weighting, alternate lookback, percentile search, feature augmentation, GC-BREAK fusion, FAST/GVZ input, or 2025-driven tuning is allowed under this V1 identity.
