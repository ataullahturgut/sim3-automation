# GOLD MONTHLY — ETF I1/I2 Historical Recurrence V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING HISTORICAL RECURRENCE TEST
**Scope:** model-free validation of ETF dynamic mechanisms I1/I2. No ChHHO backcast, no routing/model switching.

## 1. Question

Do the previously frozen ETF dynamics recur in 2010-2020 and precede unusually large next-month Gold moves?

Mechanisms are frozen from the prior authority and are not changed:

### I1 — ETF FLOW DETERIORATION
Combined GLD/IAU monthly flow deterioration:
FLOW_DELTA1 <= the 2010-2020 calibration Q10 threshold already frozen at approximately -4.2816 percentage points.

### I2 — ETF REDEMPTION PERSISTENCE
GLD and IAU both contract for at least the historical Q90 consecutive-month persistence length, frozen at 2 months.

This test is model-free. It does not claim ChHHO would have made an error in 2010-2020.

## 2. Data

Use the same official daily ETF sources:
- GLD official Historical Archive
- IAU official Historical data download

Gold movement proxy for historical recurrence:
- GLD month-end closing price return, because it is contained in the same official historical archive and is available continuously over 2010-2020.
- Report both simple and log next-month returns.
- This is used only for mechanism recurrence, not for the forecasting target definition.

## 3. Event timing

For origin month m:
- compute I1/I2 using ETF data observed through the last available trading day of month m;
- evaluate Gold/GLD movement in month m+1.

No target-month ETF information is used in the signal.

## 4. Fixed outcome definitions

Do not fit outcome thresholds to events.

For next-month absolute GLD log return:
- MOVE_3 = abs(next-month log return) >= 3 percentage points
- MOVE_5 = abs(next-month log return) >= 5 percentage points
- MOVE_8 = abs(next-month log return) >= 8 percentage points

Also report:
- mean absolute next-month return
- median absolute next-month return
- downside rate
- upside rate
- sign-reversal rate versus origin-month GLD return.

## 5. Baselines

Compare I1 and I2 event months to:
- all eligible 2010-2020 origins;
- non-event origins in 2010-2020.

Report:
- event count
- outcome rates
- baseline rates
- relative-risk / uplift ratios
- Fisher exact p-value for MOVE_3 and MOVE_5 where computable
- bootstrap 95% CI for mean absolute-return uplift with deterministic seed.

No multiple-testing-based threshold selection will be performed.

## 6. Secondary untouched-period recurrence

After the 2010-2020 historical recurrence calculation, report the same descriptive statistics for:
- 2021-01..2024-12
- 2025-01..2026-08

This is descriptive only because later periods were already inspected during alarm research.

## 7. Interpretation

A mechanism may be called historically recurrent if:
- it has multiple 2010-2020 events; and
- next-month absolute movement is materially elevated versus baseline on at least one fixed outcome or continuous movement statistic.

Statistical significance is supportive, not mandatory, due to small event counts.

No I1/I2 combination rule is authorized by this test.
No production hard alarm is authorized.
