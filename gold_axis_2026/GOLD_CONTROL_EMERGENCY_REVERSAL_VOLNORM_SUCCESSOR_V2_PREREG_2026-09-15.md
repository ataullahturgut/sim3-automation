# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM SUCCESSOR V2 PREREGISTRATION

**Date frozen:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V2`  
**Status:** `FROZEN_BEFORE_2025_REPLAY`  
**Parent:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V1` = `BLOCKED_DATA_COVERAGE_NO_2025_REPLAY`  
**Production authority:** NONE  
**Database writes:** NONE

## 1. Scope of the V2 change

V2 changes **only the historical research source clock** required to obtain adequate, reproducible pre-2025 coverage. The volatility-normalized reversal mathematics, state semantics, thresholds and evaluation protocol remain unchanged from V1.

No 2025 observation, 2025 volatility event or 2025 detector result was inspected in selecting the V2 source.

## 2. Pre-2025 source discovery

A source probe restricted to calendar years 2022–2024 compared fixed Twelve Data `XAU/USD` 1-hour bars opened at 13:00, 14:00, 15:00 and 16:00 America/New_York.

The frozen V1 16:00 source failed its predeclared 90% formation coverage gate in 2023 (224/260 = 86.15%).

The 14:00 source was selected for V2 because it is the closest earlier fixed hour that simultaneously provides high coverage in every formation year and remains highly concordant with 16:00 on overlapping dates:

| Metric | 14:00 ET result |
|---|---:|
| 2022 coverage | 257 / 260 = 98.85% |
| 2023 coverage | 256 / 260 = 98.46% |
| 2024 coverage | 258 / 262 = 98.47% |
| overlap with 16:00 | 707 dates |
| level correlation with 16:00 | 0.9999335 |
| median absolute level gap | 6.79 bp |
| p95 absolute level gap | 31.23 bp |

13:00 also had adequate coverage but is farther from the intended late-session reference and showed larger level gaps. 15:00 remained below 90% coverage in 2023 (232/260 = 89.23%).

This source choice is a **pre-2025 measurement decision**, not a detector-performance optimization.

## 3. Frozen V2 source contract

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1h`;
- requested timezone: `America/New_York`;
- selected bar: exact hourly bar opened at `14:00:00`;
- selected value: positive finite `close`, representing the end of the 14:00–15:00 ET hourly bar;
- no fallback hour;
- no interpolation;
- no forward fill;
- no provider substitution;
- evidence class: `HISTORICAL_RESEARCH_RECONSTRUCTION`;
- no official settlement/fixing claim.

Coverage gate for every complete calendar year used in formation or challenge execution:

`selected_weekday_closes / calendar_weekdays >= 0.95`.

Failure -> `BLOCKED_DATA_COVERAGE`. The gate may not be relaxed after observing 2025.

## 4. Frozen mathematics

Exactly as V1:

- `r_t = ln(P_t/P_{t-1})`;
- `sigma20_t` = sample standard deviation of the 20 immediately preceding observed returns, current return excluded;
- accumulated path scale from running extreme `e` to `t` = `sqrt(sum(sigma20_j^2))` over the observed path after the extreme;
- initial `UP_LEG` or `DOWN_LEG` requires absolute path score >= `2.0`;
- a reversal from the running peak/trough requires an opposite path score >= `2.0` in absolute value;
- `MAJOR`: absolute reversal score >=2 and <3;
- `EXTREME`: absolute reversal score >=3;
- one alert only on the state transition date;
- no monthly forecast input;
- no fixed raw-percentage reversal threshold.

Thresholds are not optimized on formation or challenge outcomes under this identity.

## 5. Formation gate

Formation: `2022-01-01 .. 2024-12-31` only.

Before 2025 may run:

- V2 source coverage >=95% in 2022, 2023 and 2024;
- deterministic repeat equality;
- prefix invariance;
- current observation excluded from its own volatility scale;
- no monthly forecast input;
- no 2025 observation is read;
- no production/database write;
- at least 3 reversal alerts across formation;
- alert count <20% of eligible post-warmup observations.

Failure -> `REJECTED_OR_BLOCKED_NO_2025_REPLAY`.

## 6. 2025 engine-first challenge

After formation PASS and implementation/config hash freeze only:

1. reconstruct the full eligible source path needed to initialize the detector through 2024 and run all 2025 origins;
2. run the frozen V2 detector without loading the 19-event volatility inventory;
3. retain every 2025 daily state, score and transition alert;
4. hash/freeze the complete 2025 engine timeline;
5. only then overlay the independently frozen 19 volatility event-days.

Primary comparison: same governed date.

Required accounting:

- total 2025 alerts;
- UP/DOWN and MAJOR/EXTREME alert counts;
- same-day volatility overlaps;
- same-day direction-aligned overlaps;
- same-day direction-opposed overlaps;
- volatility event-days with no reversal alert;
- alerts with no same-day volatility event, labelled `NO_SAME_DAY_VOLATILITY_OVERLAY` rather than automatically called universal false alarms.

±1 and ±3 observed-day proximity may be reported only as descriptive secondary diagnostics.

No 2025 result may alter V2 source, window, threshold or state rule.
