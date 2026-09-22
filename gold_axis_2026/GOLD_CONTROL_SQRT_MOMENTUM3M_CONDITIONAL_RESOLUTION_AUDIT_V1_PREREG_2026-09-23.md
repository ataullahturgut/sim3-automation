# GOLD CONTROL — SQRT × MOMENTUM_3M CONDITIONAL-RESOLUTION AUDIT V1

**Date:** 2026-09-23  
**Identity:** `SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_RESEARCH`  
**Parent risk motor:** frozen `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`  
**Directional prior:** frozen `MOMENTUM_3M` monthly H=1 price/momentum expert  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Question

The user proposed a deliberately simple architecture:

> SQRT tells us whether next-day downside risk is high. If the already-frozen strong MOMENTUM_3M direction prior says UP, interpret the high-risk day as more likely to resolve UP; if MOMENTUM_3M says DOWN, interpret it as more likely to resolve DOWN.

This audit tests that proposition directly.

MOMENTUM_3M is **not** re-labelled as a next-day classifier. It remains a monthly H=1 direction prior whose forecast is already available before the target month begins. The audit asks only whether that slower prior conditions the direction of SQRT alarm days.

## 2. Frozen inputs

### SQRT parent

Use the exact frozen forecast ledger from commit:

`2926796b6a7e9048d2c091c9c571cb928b773e02`

Artifact:

`gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv`

No SQRT refit or threshold change is allowed.

### MOMENTUM_3M

Use the canonical locked replay artifact:

`gold_axis_2026/patch_repro_v1/locked_replay_v7_daily_feature_pit_43.csv`

For each target month:
- frozen monthly reference = `rw`;
- frozen MOMENTUM_3M price forecast = `mom`;
- `MOMENTUM_3M_DIRECTION = UP` iff `mom > rw`;
- `DOWN` iff `mom < rw`;
- `NEUTRAL` iff equal.

The forecast origin is the previous month. Therefore the target-month MOMENTUM_3M state is available before every SQRT daily origin whose target date lies inside that month.

No re-estimation or daily updating is allowed.

## 3. Frozen daily composition rule

On a frozen SQRT alarm row:

- MOMENTUM_3M = UP -> emit `UP`;
- MOMENTUM_3M = DOWN -> emit `DOWN`;
- MOMENTUM_3M = NEUTRAL -> emit `ABSTAIN`.

This is the entire rule. No Router, RV_LOGIT, TTSM, threshold, confidence score, persistence gate or post-result rescue is used.

## 4. Populations

Report separately:

1. **All SQRT alarms**.
2. **Realized-high-risk SQRT alarms only**, where the frozen parent ledger has `actual_high_risk=1`.

Evaluation windows:

- 2023–2024: primary common-clock retrospective characterization.
- 2025: locked retrospective transport/stress only. It may not alter the rule or select parameters.
- 2026: excluded from this V1.

2020–2022 are not scored because the retained canonical MOMENTUM_3M locked replay begins in 2023. No historical MOMENTUM_3M reconstruction is invented for missing years.

## 5. Metrics

For each year, pooled 2023–2024, and pooled 2023–2025 descriptive support, report:

- SQRT alarm count;
- realized-risk-hit alarm count;
- unique target months represented;
- MOMENTUM UP / DOWN / NEUTRAL alarm counts;
- actual UP / DOWN counts;
- TP / FP / TN / FN under the exact composition rule;
- UP precision / recall;
- DOWN precision / recall;
- ordinary accuracy;
- balanced accuracy;
- conditional `P(actual UP | MOMENTUM_UP, SQRT alarm)`;
- conditional `P(actual DOWN | MOMENTUM_DOWN, SQRT alarm)`.

Repeat the same metrics on realized-high-risk alarm rows only.

Because MOMENTUM_3M is constant within a target month, daily alarm rows are clustered. Therefore daily counts are not treated as independent statistical trials. Also report month-level anatomy:
- target month;
- frozen MOMENTUM direction;
- SQRT alarms in month;
- actual UP / DOWN alarm days;
- risk-hit UP / DOWN alarm days.

## 6. Integrity

Mandatory checks:

- 2023 SQRT alarms = 2;
- 2024 SQRT alarms = 17;
- 2025 SQRT alarms = 90;
- 2023–2024 pooled = 19;
- 2025 frozen parent risk alarms reproduce the parent artifact exactly;
- target return sign is non-zero on scored alarm rows;
- each scored target month has exactly one frozen MOMENTUM_3M row;
- no target month uses a forecast formed after that month began.

Any failure => `BLOCKED_INTEGRITY_MISMATCH`.

## 7. Interpretation

This is a cross-clock conditional-resolution audit, not a claim that MOMENTUM_3M itself predicts next-day direction.

A useful result would mean the monthly directional prior materially separates the daily high-risk alarms into different UP/DOWN resolution tendencies. A weak result would mean that monthly trend direction does not sufficiently resolve the next-day high-risk direction problem.

No promotion gate is introduced in V1. Exact empirical results are reported without threshold search.

## 8. Governance

- random split: forbidden;
- no post-result threshold tuning;
- 2025 cannot tune or rescue the rule;
- 2026 excluded;
- no production writes;
- no runtime promotion;
- no automatic trade mapping.
