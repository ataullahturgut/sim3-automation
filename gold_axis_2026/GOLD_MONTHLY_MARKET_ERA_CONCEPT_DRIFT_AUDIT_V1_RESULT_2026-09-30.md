# GOLD MONTHLY — Market Era / Concept Drift Audit V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Structural interpretation:** **LATE-R2 CONCEPT DRIFT — suggestive, not independently confirmed**  
**Operational decision:** no new alarm/routing rule is authorized.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_ERA_CONCEPT_DRIFT_AUDIT_V1_AUTHORITY_2026-09-30.md`
- authority commit: `9411d48ebad42344dba298660559f413f03b0971`

Code:
- `gold_axis_2026/tools/gold_monthly_market_era_concept_drift_audit_v1.py`
- code commit: `9ec60909f9c6f6d9d668e5399be25caa5a9cfc67`

Workflow:
- `.github/workflows/gold-monthly-market-era-concept-drift-audit-v1.yml`
- workflow commit: `6da2f4b76137a306c1ee4480fff3c0e49b00a3f1`

Execution:
- run: **36772562100**
- artifact: **11123618480**
- digest: `sha256:a17b7815df568124146db0bfbe040732e4cbf518db7db54208c2440bb5dd5aeb`
- scientific gate: **PASS**

## 2. Frozen era split

Era boundary was not searched from forecast errors.

- PRE_R2_ERA: origin <= 2024-03
- R2_EARLY: origin 2024-04..2024-12
- R2_LATE: origin 2025-01..2026-04
- R2_BREAK: origin 2026-05..2026-07

Counts:
- PRE_R2_ERA: n=30
- R2_EARLY: n=9
- R2_LATE: n=16
- R2_BREAK: n=3

## 3. Main monthly error-severity pattern

### PRE_R2_ERA
- HIGH: **8/30 = 26.7%**
- ELEVATED: 11/30 = 36.7%

### R2_EARLY
- HIGH: **1/9 = 11.1%**
- ELEVATED: 3/9 = 33.3%

### R2_LATE
- HIGH: **6/16 = 37.5%**
- ELEVATED: 8/16 = 50.0%

### R2_BREAK
- HIGH: **2/3 = 66.7%**
- ELEVATED: 2/3 = 66.7%

Interpretation:
- the April-2024 R2 onset does **not** immediately create a high-error era;
- early R2 is actually quieter by HIGH rate;
- HIGH/ELEVATED severity rises later, especially in R2_LATE and the R2_BREAK episode.

Diagnostic Fisher tests for HIGH vs non-HIGH are not statistically decisive:
- PRE vs R2_EARLY: p=0.654
- PRE vs R2_LATE: p=0.512
- R2_EARLY vs R2_LATE: p=0.355.

Small samples remain a major limitation.

## 4. ANY_VISIBLE changes materially late in R2

### PRE_R2_ERA
- 24 alarm events
- 10 useful
- 14 false
- useful-call rate **41.7%**
- false-call rate **58.3%**

### R2_EARLY
- 4 events
- 2 useful
- 2 false
- useful-call rate **50.0%**
- false-call rate **50.0%**

### R2_LATE
- 10 events
- **8 useful**
- **2 false**
- useful-call rate **80.0%**
- false-call rate **20.0%**
- HIGH recall 100%
- elevated recall 100%

Thus the large improvement is not present at the initial 2024 R2 onset. It appears mainly in the later R2 period.

Diagnostic Fisher:
- PRE vs R2_EARLY useful/false: p=1.000
- PRE vs R2_LATE: p=**0.063**
- R2_EARLY vs R2_LATE: p=0.520.

PRE vs late is suggestive but does not cross a conventional 0.05 threshold.

## 5. T0_STANDARD also improves progressively

Useful-call rate:
- PRE: **50.0%**
- R2_EARLY: **66.7%**
- R2_LATE: **83.3%**

False-call rate:
- PRE: 50.0%
- R2_EARLY: 33.3%
- R2_LATE: 16.7%

But event counts are small and Fisher comparisons are not significant.

## 6. Same-R2 control

To avoid simply comparing older R0/R1 mixtures with R2, the analysis was repeated using only rows whose live V2 semantic state was R2.

Counts:
- PRE_R2_ERA live-R2: n=5
- R2_EARLY live-R2: n=9
- R2_LATE live-R2: n=16

### ANY_VISIBLE useful-call rate, live-R2 only
- PRE: **66.7%** (2 useful / 3 events)
- R2_EARLY: **50.0%** (2/4)
- R2_LATE: **80.0%** (8/10)

### T0 useful-call rate, live-R2 only
- PRE: 50.0%
- R2_EARLY: 66.7%
- R2_LATE: 83.3%

This control weakens a simple “R2 itself causes the improvement” explanation:
- there were already R2-like live states before April 2024;
- early R2 is not better than all prior R2 observations on ANY_VISIBLE;
- the strongest improvement appears **late within R2**.

## 7. Signal composition changes strongly

### PRE_R2_ERA
Dominant event flow:
- T1_WGC: **21 events**, 8 useful / 13 false
- I2: **11 events**, 5 useful / 6 false
- H: 4 events, 2 useful / 2 false
- B: 3 events, 1 useful / 2 false
- E: 0 events.

### R2_EARLY
- H: 2 events, 1 useful / 1 false
- T1_WGC: 1 event, false
- C: 1 useful
- D: 1 useful
- E: 0
- I2: 0.

### R2_LATE
- **E: 4/4 useful**
- **H: 3/3 useful**
- B: 1/1 useful
- A: 1 useful / 1 false
- I1: 1 false
- **T1_WGC: 0 events**
- **I2: 0 events**

This is a major structural change in which alarms fire:
- older history is dominated by T1/I2;
- late R2 is dominated by E/H;
- E did not exist as an observed event in PRE or R2_EARLY, then appears 4 times and is useful 4/4 in R2_LATE.

That explains why stationary pooled reliability performed poorly: it averages across materially different signal populations.

## 8. H is a concrete within-signal example

H:
- PRE: 2 useful / 4 events = **50%**
- R2_EARLY: 1/2 = **50%**
- R2_LATE: **3/3 = 100%**

The direction is consistent with late improvement, but n is too small to promote a rule.

## 9. V2 behavior changes late, not at R2 onset

### PRE
V2 TRANSITION:
- n=12
- HIGH rate **16.7%**
- ELEVATED rate 33.3%
- relative to STABLE, HIGH rate is lower by 16.7 percentage points.

### R2_EARLY
V2 TRANSITION:
- n=1
- HIGH=0
- ELEVATED=0
- still not a high-risk warning.

### R2_LATE
V2 TRANSITION:
- n=1
- **HIGH=1/1**
- ELEVATED=1/1.

### R2_BREAK
V2 TRANSITION:
- n=2
- **2/2 HIGH**.

Therefore the recent 3/3 V2-transition-to-HIGH pattern is composed of:
- one late-R2 case;
- two break-era cases.

It did **not** begin simply because R2 started in April 2024.

## 10. Independent no-alarm V2 case

The critical independent catch remains in R2_BREAK:
- origin 2026-05
- V2 = R2_TRANSITION
- ANY_VISIBLE = OFF
- target 2026-06 = HIGH
- APE about 8.57%.

There is no analogous HIGH catch from V2_TRANSITION + NO_ANY_VISIBLE in PRE, R2_EARLY, or R2_LATE.

Thus the strongest independent V2 value is currently specific to the break episode, not the whole R2 era.

## 11. Structural conclusion

The data do **not** support the simple claim:

> “R2 began in April 2024, therefore alarm/V2 behavior changed immediately.”

Instead the observed sequence is:

1. PRE era: noisy, T1/I2-heavy alarm ecology.
2. R2_EARLY: still broadly similar; no V2 high-risk reversal.
3. R2_LATE: alarm mix becomes much cleaner, especially E/H.
4. R2_BREAK: V2 transition becomes strongly associated with HIGH errors and produces the important 2026-05 independent warning.

The best current interpretation is therefore:

> **Late-R2 / within-regime concept drift is more plausible than a simple R2-versus-pre-R2 effect.**

But this is **suggestive, not confirmatory**, because:
- R2_EARLY has only 9 months;
- V2 transition counts by sub-era are tiny;
- exact tests are mostly non-significant;
- 2025-2026 is already opened evidence.

## 12. Binding decision

Do not:
- reweight all R2 alarms;
- promote E/H as universal 100% alarms;
- deploy V2 as a global R2 warning;
- search post-hoc for a better drift date.

Retain:
- the evidence that alarm ecology changes over time;
- E/H as late-R2 research signals;
- V2 as a possible break-state warning, especially around the 2026 transition.

## 13. Next defensible stage

The next test should distinguish **persistent era adaptation** from a coincidental late sample.

A defensible design is:
- rolling/recency-window alarm reliability with window length chosen from historical pre-2025 data only, or
- online change-detection on alarm outcome/process statistics, without using 2025-2026 to choose the change date.

The goal is not to find the best recent window post hoc. It is to test whether a chronology-safe adaptive reliability process would have naturally shifted weight away from T1/I2 and toward E/H before the 2025-2026 outcomes were known.
