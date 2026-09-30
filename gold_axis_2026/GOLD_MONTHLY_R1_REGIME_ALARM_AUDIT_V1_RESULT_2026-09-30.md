# GOLD MONTHLY — R1 Regime Alarm Audit V1 Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Scope:** descriptive alarm audit inside independently discovered R1 only.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_R1_REGIME_ALARM_AUDIT_V1_AUTHORITY_2026-09-30.md`
- authority commit: `206d55a724a693aa3b1dca230f12e145d5e5fd1e`

Execution:
- workflow: **Gold Monthly R1 Regime Alarm Audit V1**
- run: **36718441330**
- code commit: `adcc0efbf62490248e770ddbba1010ea544ac5e0`
- workflow commit: `6ae89b7b051bd9a3abf8c5e7bc61396681bfbb50`
- scientific gate: **PASS**

## 2. Regime conditioning

Regime is taken from the forecast **origin month**, not the target month.

Primary R1:
- state = R1
- filtered posterior >= 60%
- not OOD.

This yields:
- **19 target months**
- HIGH: **4**
- MEDIUM: **3**
- NORMAL: **12**

HIGH targets arising from confident R1 origins:
- 2021-12
- 2023-08
- 2024-03
- 2026-08

MEDIUM:
- 2022-01
- 2022-02
- 2024-04

## 3. Signal performance inside confident R1

| Signal | Events | HIGH | MEDIUM | False calls | False-call rate | HIGH recall |
|---|---:|---:|---:|---:|---:|---:|
| A | 2 | 1 | 0 | 1 | 50.0% | 25.0% |
| B | 2 | 0 | 0 | 2 | **100.0%** | 0.0% |
| C | 0 | 0 | 0 | 0 | — | 0.0% |
| D | 0 | 0 | 0 | 0 | — | 0.0% |
| E | 0 | 0 | 0 | 0 | — | 0.0% |
| G | 1 | 1 | 0 | 0 | **0.0%** | 25.0% |
| H | 4 | 1 | 1 | 2 | 50.0% | 25.0% |
| I1 | 0 | 0 | 0 | 0 | — | 0.0% |
| I2 | 4 | 2 | 0 | 2 | 50.0% | 50.0% |
| T1_WGC | 13 | 2 | 2 | 9 | **69.2%** | 50.0% |

## 4. Exact false calls inside confident R1

### A
- 2021-11 — APE 0.462%

### B
- 2023-02 — 1.566%
- 2023-05 — 0.973%

### H
- 2023-03 — 2.199%
- 2023-09 — 0.281%

### I2
- 2023-09 — 0.281%
- 2023-10 — 1.853%

### T1_WGC
- 2021-11 — 0.462%
- 2023-02 — 1.566%
- 2023-03 — 2.199%
- 2023-04 — 2.201%
- 2023-09 — 0.281%
- 2023-10 — 1.853%
- 2023-12 — 0.363%
- 2024-01 — 2.407%
- 2024-02 — 1.546%

## 5. Union behavior inside R1

### T0_STANDARD = A/B/C/D/H
- events 8
- HIGH hits 2/4
- MEDIUM hits 1
- false calls 5
- false-call rate **62.5%**
- useful-call rate 37.5%

### ANY_VISIBLE
- events 16
- HIGH hits **4/4**
- MEDIUM hits 2
- false calls **10**
- false-call rate **62.5%**
- useful-call rate 37.5%

Important:
All four HIGH R1-origin targets had at least one visible alarm, but the union is extremely noisy.

## 6. Main descriptive conclusions

1. R1 does not mean “safe/no model risk.”
   - 4 HIGH-error targets occur from confident R1 origins.

2. B is poor in R1 in this sample.
   - 2 events, both false calls.

3. T1_WGC is very noisy in R1.
   - 13 events, 9 false calls.
   - false-call rate 69.2%.

4. I2 is mixed in R1.
   - 4 events, 2 HIGH hits and 2 false calls.

5. H is mixed.
   - 1 HIGH + 1 MEDIUM + 2 false calls.

6. G has one R1 event and it is a true HIGH hit (2026-08), but n=1 is too small for inference.

7. Any-visible achieves 4/4 HIGH coverage in R1, but only by producing 10 false calls in 16 alarm events.

## 7. Sensitivity

If all raw R1 assignments are included even when posterior <60%:
- R1-origin targets = 22
- HIGH = 6
- ANY_VISIBLE catches 5/6
- remaining blind HIGH = **2026-06**
- false calls = 11/18 alarm events.

The difference is driven by ambiguous-regime origins such as 2026-05 before target 2026-06.

## 8. Governance

No alarm selection, weighting, threshold tuning, forecast correction, or routing was performed.

This audit only measures existing alarm behavior conditional on independently discovered R1.
