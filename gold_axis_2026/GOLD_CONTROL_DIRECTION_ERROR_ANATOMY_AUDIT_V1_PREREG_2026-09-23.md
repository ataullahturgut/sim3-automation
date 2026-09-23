# GOLD CONTROL — DIRECTION ERROR ANATOMY AUDIT V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `DIRECTION_ERROR_ANATOMY_AUDIT_V1_RESEARCH`  
**Purpose:** descriptive failure-mode analysis of the current residual UP-2 direction layer  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Question

Within the exact residual route

`SQRT HIGH RISK + Frozen Primary UP Verifier V2 ABSTAIN`

compare the origin-safe state patterns of:

1. **CAPTURED_UP** = One-Sided UP-2 Logit emits UP2 and realized next close is UP.
2. **MISSED_UP** = UP-2 abstains and realized next close is UP.
3. **FALSE_UP_ACTUAL_DOWN** = UP-2 emits UP2 but realized next close is DOWN. This is the direction-layer analogue of a missed DOWN.
4. **REJECTED_DOWN** = UP-2 abstains and realized next close is DOWN.

Important semantic guardrail: the current architecture has no validated positive-DOWN authority. Therefore `REJECTED_DOWN` is **not** called a predicted DOWN. It is a correctly rejected UP that remains available to the downstream direction lane.

## 2. Primary evidence versus transport

Primary descriptive anatomy:
- governed 2022–2024 residual population only.

Locked transport check:
- governed 2025 residual population, evaluated separately.
- 2025 must not select features, contrasts, or thresholds.

2026 excluded.

## 3. Frozen source artifacts

Join by exact `(origin_date,target_date)`:

- One-Sided UP-2 frozen ledger:
  `GOLD_CONTROL_RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_LEDGER_2026-09-23.csv`
  at commit `eb928b2d5be6250227d8e14dea2d58abe494f762`.

- Trajectory morphology frozen ledger:
  `GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_LEDGER_2026-09-23.csv`
  at commit `cee7fadff9490a667716520ed0c9479932e5c41e`.

- Frozen SQRT parent returns:
  `GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv`
  at commit `2926796b6a7e9048d2c091c9c571cb928b773e02`.

Expected joined counts:
- 2022–2024 n=26 = 8 CAPTURED_UP + 5 MISSED_UP + 3 FALSE_UP_ACTUAL_DOWN + 10 REJECTED_DOWN.
- locked 2025 n=74 = 13 CAPTURED_UP + 22 MISSED_UP + 12 FALSE_UP_ACTUAL_DOWN + 27 REJECTED_DOWN.

Any mismatch blocks interpretation.

## 4. Frozen origin-safe feature set

### Risk/context
1. `sqrt_score`
2. `lag1_close_return`
3. `direct_up_fraction`
4. `legacy_up_fraction`

### Intraday pressure / terminal state
5. `downside_share`
6. `intraday_end_norm`
7. `close_location`
8. `last_quarter_return_norm`

### Intraday stress / rebound morphology
9. `max_drawdown_norm`
10. `trough_position`
11. `recovery_to_close_ratio`
12. `post_trough_return_norm`
13. `post_trough_positive_fraction`

The model score `p_up` is reported separately as a **diagnostic score**, not as a market-state feature.

The target-day realized simple return and absolute return are reported separately as **ex-post outcome severity**, not as predictors.

## 5. Frozen contrasts

A. **Why are some UPs captured and some missed?**  
`CAPTURED_UP - MISSED_UP`

B. **Why are some DOWNs safely rejected and some mistaken for UP?**  
`REJECTED_DOWN - FALSE_UP_ACTUAL_DOWN`

C. **Inside UP-2 abstentions, what distinguishes the unresolved UP from unresolved DOWN?**  
`MISSED_UP - REJECTED_DOWN`

D. **Easy-direction benchmark**  
`CAPTURED_UP - REJECTED_DOWN`

No other pairwise contrast is added after seeing the data.

## 6. Descriptive statistics and effect sizes

For every group/feature:
- n;
- mean;
- median;
- IQR.

For every frozen contrast:
- Cliff's delta, defined positive when the first group tends to have larger values than the second;
- median difference;
- exact permutation p-value for the absolute median-difference statistic;
- Benjamini-Hochberg q-value across the 13 market-state features within each contrast.

Because the primary samples are small, inference remains exploratory. No feature is declared causal.

## 7. Cross-period stability labels

To avoid choosing patterns from 2025 retrospectively, pattern strength is frozen before scoring:

- **STRONG_STABLE**: pre-2025 |Cliff delta| >=0.474 AND locked-2025 same sign with |delta| >=0.33.
- **MODERATE_STABLE**: pre-2025 |delta| >=0.33 AND locked-2025 same sign with |delta| >=0.20.
- **PRE2025_ONLY**: pre-2025 |delta| >=0.33 but 2025 fails sign/magnitude stability.
- **WEAK_OR_INCONSISTENT**: otherwise.

These labels are descriptive effect-size stability labels, not hypothesis-test acceptance rules.

## 8. Output interpretation

The audit should answer:

- whether missed UPs look like weaker versions of captured UPs or a qualitatively different state;
- whether false-UP actual-DOWN cases have a distinct precursor pattern from safely rejected DOWNs;
- whether unresolved UP versus unresolved DOWN has stable separable structure suitable for a future downstream resolver;
- whether 2025 suggests conditional drift / regime instability.

No model is trained, retuned, promoted, or combined from this audit.

## 9. Governance

- no random split;
- no new classifier;
- no feature mining beyond the frozen list;
- no result-dependent contrast selection;
- no 2025 tuning;
- no 2026 use;
- no production writes;
- no runtime promotion.
