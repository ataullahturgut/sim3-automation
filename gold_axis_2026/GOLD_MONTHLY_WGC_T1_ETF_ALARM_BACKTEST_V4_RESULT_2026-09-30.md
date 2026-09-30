# GOLD MONTHLY — WGC T1 Early-Month ETF Alarm Backtest V4 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Scope:** alarm detection only. Forecast unchanged; no routing/model switching.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V4_AUTHORITY_2026-09-30.md`
- authority commit: `b57e602f2717143dd633fdb0300c98d64024eb8a`

Execution:
- workflow: **Gold Monthly WGC T1 ETF Alarm Backtest V4**
- run: **36708826992**
- artifact: **11093192454**
- code commit: `32489decb6f33bff14b33fd0d9770617da9a0bf5`
- workflow commit: `75f31ba6cfc1814a80376bb1924ba7c68ec8fa72`
- scientific gate: **PASS**
- artifact digest: `sha256:58f418f5dbb60202810f1da19f9fc79aea31c2db892d566fb9a01dbdb8f1d984`

Supersession:
- V1-V3 WGC parser performance claims are non-binding because their scientific completeness gates failed.
- V4 is the first binding T1 performance result.

## 2. Complete evaluation authority

Binding APE-severity evaluation:
- 2021-11..2026-08
- expected rows: **58**
- available authoritative WGC rows: **58**
- coverage: **100%**
- missing: **0**
- bad publication month: **0**
- bad data month: **0**

Exactly one pre-authorized official-source override:
- target 2021-12 / data month 2021-11
- WGC report published 7 December 2021
- global ETF direction = INFLOW
- previous October report = OUTFLOW
- therefore R2_WGC = FALSE.

## 3. Standardized T1 alarm

**R2_WGC = two consecutive official WGC monthly reports with global gold-ETF OUTFLOW.**

No numeric tonnage threshold is used.

T1 report is published after T0 forecast, during the target month. The forecast is not changed.

TIMELY_T1:
- publication day <=10 of target month.

All R2_WGC events in this evaluation are timely.

## 4. R2_WGC performance

Across 58 targets:

- R2_WGC events: **23**
- HIGH APE months: **17**
- HIGH hits: **6**
- HIGH precision: **26.1%**
- HIGH recall: **35.3%**

HIGH hit targets:
- **2022-07**
- **2022-09**
- 2022-11
- 2023-01
- 2023-08
- **2024-03**

MEDIUM hits:
- 2022-02
- 2024-04

MEDIUM+HIGH:
- elevated months: **24**
- R2 hits: **8**
- precision: **34.8%**
- recall: **33.3%**

Normal-event false alarms:
- 2021-11
- 2022-08
- 2022-10
- 2022-12
- 2023-02
- 2023-03
- 2023-04
- 2023-09
- 2023-10
- 2023-11
- 2023-12
- 2024-01
- 2024-02
- 2024-05
- 2026-07

Interpretation:
R2_WGC is too noisy to be a hard alarm by itself, but it has meaningful incremental coverage of T0 misses.

## 5. Timeliness

Every standardized R2 event in the evaluation was published by calendar day 10.

Therefore timely-event metrics are identical to all-event metrics.

Examples:
- target 2022-07: report published **7 July 2022**
- target 2022-09: report published **7 September 2022**
- target 2024-03: report published **7 March 2024**

Thus the useful incremental information arrives during the first week / first ten days of the target month.

## 6. T0 + T1 incremental coverage

### T0 A/B/C/D/H
HIGH APE:
- total HIGH: **17**
- T0 hits: **9**
- T0 recall: **52.9%**

T0 hit targets:
- 2021-12
- 2022-11
- 2023-01
- 2023-08
- 2024-11
- 2025-02
- 2025-03
- 2025-09
- 2025-10

### T1 R2_WGC
HIGH hits: **6**

Three overlap with T0:
- 2022-11
- 2023-01
- 2023-08

Three are genuinely incremental T1 detections:
- **2022-07**
- **2022-09**
- **2024-03**

### T0 + T1 union

- HIGH hits: **12/17**
- recall: **70.6%**

Union hit targets:
- 2021-12
- 2022-07
- 2022-09
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- 2024-11
- 2025-02
- 2025-03
- 2025-09
- 2025-10

Remaining HIGH misses:
- **2022-05**
- **2025-11**
- **2026-01**
- **2026-06**
- **2026-08**

## 7. Four core previously unexplained HIGH months

### 2022-05
- APE: **4.324% HIGH**
- WGC report: **6 May 2022**
- April global ETF direction: INFLOW
- March global ETF direction: INFLOW
- R2_WGC: **FALSE**
- T0 A/B/C/D/H: FALSE

However the official report explicitly states April inflows were **77% lower than the previous month**.

This is real T1 warning information, but it is not counted as a standardized hit because no pre-registered slowdown magnitude rule exists.

Status:
**visible qualitative T1 deterioration, not a standardized R2 detection.**

### 2022-07
- APE: **3.748% HIGH**
- report: **7 July 2022**
- June global ETF direction: OUTFLOW
- May direction: OUTFLOW
- R2_WGC: **TRUE**
- T0 A/B/C/D/H: FALSE

Status:
**standardized T1 incremental hit.**

### 2022-09
- APE: **3.509% HIGH**
- report: **7 September 2022**
- August direction: OUTFLOW
- July direction: OUTFLOW
- R2_WGC: **TRUE**
- T0 A/B/C/D/H: FALSE

Status:
**standardized T1 incremental hit.**

### 2024-03
- APE: **6.098% HIGH**
- report: **7 March 2024**
- February direction: OUTFLOW
- January direction: OUTFLOW
- R2_WGC: **TRUE**
- T0 A/B/C/D/H: FALSE

Status:
**standardized T1 incremental hit.**

## 8. Binding interpretation

1. **Yes, early-month official ETF reports add alarm information after the month-end forecast.**
2. The standardized WGC two-consecutive-outflow warning adds **3 HIGH detections that T0 missed**.
3. T0 HIGH coverage rises from **9/17 (52.9%)** to **12/17 (70.6%)** when T1 R2 is added as a separate warning channel.
4. The signal is noisy: R2 alone has only **26.1% HIGH precision**, so it is a warning, not a hard alarm.
5. 2022-05 contains visible T1 deterioration information (77% slowdown) but remains outside the standardized R2 rule.
6. Remaining HIGH misses after standardized T0+T1:
   - 2022-05
   - 2025-11
   - 2026-01
   - 2026-06
   - 2026-08
7. No forecast correction was tested or authorized.
8. No routing/model switching was tested or authorized.
