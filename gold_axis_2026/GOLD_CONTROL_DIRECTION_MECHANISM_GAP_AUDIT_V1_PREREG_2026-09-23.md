# GOLD CONTROL — DIRECTION MECHANISM-GAP AUDIT V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH`  
**Purpose:** derive concrete model-improvement hypotheses from the failure anatomy of the current residual direction layer  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

Within the exact governed residual route

`SQRT HIGH RISK + Frozen Primary UP Verifier V2 ABSTAIN`

and using the frozen One-Sided UP-2 V1 output, identify whether the model is missing **specific path-dynamic mechanisms** that are not represented by the current aggregate state variables.

The audit addresses three frozen questions:

1. **Captured-UP vs Missed-UP:** what path dynamics characterize the UP mechanism that UP-2 currently misses?
2. **Captured-UP vs False-UP actual-DOWN:** what path dynamics distinguish true rebound from continuation-mimic hard negatives?
3. **Missed-UP vs Rejected-DOWN:** is there any stable path-dynamic structure left in the abstained hard residual population?

No classifier is trained in this audit.

## 2. Error-cell semantics

- `CAPTURED_UP`: UP2 call=1 and realized target UP.
- `MISSED_UP`: UP2 call=0 and realized target UP.
- `FALSE_UP_ACTUAL_DOWN`: UP2 call=1 and realized target DOWN.
- `REJECTED_DOWN`: UP2 call=0 and realized target DOWN.

`REJECTED_DOWN` is not a validated positive-DOWN prediction.

Expected counts:
- governed 2022–2024: 8 / 5 / 3 / 10;
- locked 2025: 13 / 22 / 12 / 27.

Any mismatch blocks interpretation.

## 3. Data

Primary anatomy:
- governed 5-minute research cache;
- target years 2022–2024.

Locked transport:
- governed 2025;
- used only to test sign/effect stability.

2026 excluded.

Frozen UP-2 ledger:
`GOLD_CONTROL_RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_LEDGER_2026-09-23.csv`
at commit `eb928b2d5be6250227d8e14dea2d58abe494f762`.

Governed 5-minute table is read-only.

## 4. Frozen path-dynamic feature families

All features are computed only from the completed origin-day 5-minute return path.

Let:
- `r_t` = intraday log returns,
- `C_t` = cumulative intraday return including session start at zero,
- `RV = sum(r_t^2)`,
- `DRV = sum(r_t^2 I(r_t<0))`,
- `t*` = global trough index,
- `Q` = final 25% of intraday returns,
- `H` = final 12 five-minute returns (approximately final hour).

### A. Selling-pressure persistence

1. `late_rv_share` = RV in Q / full-day RV.
2. `late_downside_rv_share` = downside RV in Q / full-day downside RV.
3. `late_downside_intensity` = downside RV in Q / full-day RV.
4. `terminal_negative_run_frac` = consecutive negative-return run ending at close / N.
5. `max_negative_run_frac` = maximum negative-return run length / N.
6. `new_low_rate_last_quarter` = fraction of Q cumulative-path points that set a new running session low.
7. `time_near_low_last_quarter` = fraction of Q cumulative-path points lying within the bottom 20% of the session path range.

### B. Recovery quality after the trough

8. `post_trough_efficiency` = net trough-to-close recovery / total absolute post-trough movement; 0 if no post-trough path.
9. `post_trough_positive_move_share` = total positive post-trough return / total absolute post-trough movement.
10. `post_trough_sign_change_rate` = sign changes among non-zero post-trough returns / available transitions.
11. `recovery_speed_norm` = trough-to-close recovery divided by sqrt(RV), divided by post-trough fraction of the session; 0 if trough at close.
12. `near_trough_revisit_rate` = fraction of post-trough path points that remain within 20% of the trough-to-session-range band.

### C. Terminal trend / acceleration

13. `last_hour_return_norm` = sum(H) / sqrt(RV).
14. `last_hour_slope_norm` = OLS slope of the cumulative path over H, scaled by N/sqrt(RV).
15. `last_hour_trend_r2` = R-squared of that OLS trend.
16. `late_acceleration_norm` = normalized return of final half of H minus first half of H.

### D. Shock concentration

17. `max_negative_shock_share` = largest squared negative 5-minute return / DRV.
18. `top3_negative_shock_share` = sum of the three largest squared negative returns / DRV.

No feature is added after seeing results.

## 5. Frozen contrasts

A. `CAPTURED_UP - MISSED_UP`  
Goal: identify a missing UP mechanism.

B. `CAPTURED_UP - FALSE_UP_ACTUAL_DOWN`  
Goal: identify a true-rebound versus continuation-mimic discriminator.

C. `MISSED_UP - REJECTED_DOWN`  
Goal: test whether the remaining hard residual population has a stable path-dynamic separator.

No other contrast is promoted under V1.

## 6. Statistics

For each group/feature:
- n;
- mean;
- median;
- IQR.

For each contrast/feature:
- Cliff's delta;
- median difference;
- exact permutation p-value for absolute median difference;
- Benjamini-Hochberg q-value across the 18 frozen features within the contrast.

## 7. Frozen stability labels

Across pre-2025 and locked 2025:

- **STRONG_STABLE**: pre-2025 |delta| >=0.474 and locked-2025 same sign with |delta| >=0.33.
- **MODERATE_STABLE**: pre-2025 |delta| >=0.33 and locked-2025 same sign with |delta| >=0.20.
- **PRE2025_ONLY**: pre-2025 |delta| >=0.33 but locked-2025 fails sign/magnitude.
- **WEAK_OR_INCONSISTENT**: otherwise.

## 8. Model-improvement interpretation rules

A feature family may motivate a future model change only when:
- at least one feature is MODERATE_STABLE or STRONG_STABLE in the relevant contrast;
- direction of the effect has an interpretable path mechanism;
- the future model uses a new preregistered identity.

Suggested mappings are frozen conceptually before scoring:

- Stable persistence features in Captured-UP vs Missed-UP -> add a **Recovery/Continuation-UP specialist**.
- Stable persistence/recovery features in Captured-UP vs False-UP actual-DOWN -> add a **continuation-mimic veto/failure detector** behind the rebound specialist.
- Stable features in Missed-UP vs Rejected-DOWN -> candidate inputs for a future downstream conditional resolver.
- If the third contrast remains unstable, do not force a static residual binary classifier; prefer regime-conditioned/defer architecture research.

## 9. Governance

- no random split;
- no new predictive model;
- no feature mining beyond the frozen 18;
- no result-dependent threshold changes;
- 2025 not used to design or tune;
- 2026 excluded;
- DB read-only;
- no runtime/production promotion.
