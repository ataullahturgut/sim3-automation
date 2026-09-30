# GOLD MONTHLY — Unified Alarm Matrix V2 False-Call Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Rows:** 58
**Scope:** false-call accounting only; no new alarm threshold, no forecast correction, no routing/model switching.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_AUTHORITY_2026-09-30.md`
- authority commit: `76beeaaeec3d833e78f8a0df6431ed9369eba66a`

Execution:
- workflow: **Gold Monthly Unified Alarm Matrix V2 False Call**
- run: **36711349670**
- artifact: **11093903747**
- code commit: `37994b3f08676c6bc20e5d9fd81ac07a16051132`
- workflow commit: `028ddbd75bf5c19f321d54b4ad9d2bc09d1b1a14`
- artifact digest: `sha256:995f216b3a44d4903b214cfcb7f64335dda70f73e2f6e56f67e7a821744eb949`
- scientific gate: **PASS**

## 2. False-call definition

APE remains binding:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

When a signal is ON:
- HIGH -> HIGH HIT
- MEDIUM -> MEDIUM HIT
- NORMAL -> FALSE CALL

MEDIUM is not counted as a false alarm.

## 3. Individual signal quality

| Signal | Events | HIGH hits | MEDIUM hits | FALSE calls | Useful-call rate | False-call rate |
|---|---:|---:|---:|---:|---:|---:|
| A | 5 | 3 | 0 | 2 | 60.0% | 40.0% |
| B | 4 | 2 | 0 | 2 | 50.0% | 50.0% |
| C | 1 | 0 | 1 | 0 | 100.0% | 0.0% |
| D | 1 | 1 | 0 | 0 | 100.0% | 0.0% |
| E | 4 | 2 | 2 | 0 | 100.0% | 0.0% |
| G | 3 | 1 | 0 | 2 | 33.3% | 66.7% |
| H | 9 | 3 | 3 | 3 | 66.7% | 33.3% |
| I1 | 2 | 1 | 0 | 1 | 50.0% | 50.0% |
| I2 | 12 | 5 | 0 | 7 | 41.7% | 58.3% |
| T1_WGC | 23 | 6 | 2 | 15 | 34.8% | 65.2% |

## 4. Exact individual false calls

### A
- 2021-11 — APE 0.462%
- 2025-12 — APE 2.166%

### B
- 2023-02 — APE 1.566%
- 2023-05 — APE 0.973%

### C
- none

### D
- none

### E
- none in the current 58-row sample
- caution: E is still discovery-period / unvalidated; zero observed false calls does not independently validate it.

### G
- 2022-08 — APE 2.031%
- 2026-07 — APE 2.030%

### H
- 2023-03 — APE 2.199%
- 2023-09 — APE 0.281%
- 2024-08 — APE 1.796%

### I1
- 2026-04 — APE 0.608%

### I2
- 2022-08 — APE 2.031%
- 2022-10 — APE 0.193%
- 2022-12 — APE 1.755%
- 2023-09 — APE 0.281%
- 2023-10 — APE 1.853%
- 2023-11 — APE 0.624%
- 2026-07 — APE 2.030%

### T1_WGC
- 2021-11 — APE 0.462%
- 2022-08 — APE 2.031%
- 2022-10 — APE 0.193%
- 2022-12 — APE 1.755%
- 2023-02 — APE 1.566%
- 2023-03 — APE 2.199%
- 2023-04 — APE 2.201%
- 2023-09 — APE 0.281%
- 2023-10 — APE 1.853%
- 2023-11 — APE 0.624%
- 2023-12 — APE 0.363%
- 2024-01 — APE 2.407%
- 2024-02 — APE 1.546%
- 2024-05 — APE 1.223%
- 2026-07 — APE 2.030%

## 5. Union false-call burden

### T0_STANDARD = A OR B OR C OR D OR H
- events: **19**
- HIGH hits: **9**
- MEDIUM hits: **3**
- NORMAL false calls: **7**
- useful-call rate: **63.2%**
- false-call rate: **36.8%**
- HIGH recall: **52.9%**

False-call months:
- 2021-11
- 2023-02
- 2023-03
- 2023-05
- 2023-09
- 2024-08
- 2025-12

### T0_ALL_VISIBLE = A/B/C/D/E/G/H/I1/I2
- events: **34**
- HIGH hits: **16**
- MEDIUM hits: **4**
- NORMAL false calls: **14**
- useful-call rate: **58.8%**
- false-call rate: **41.2%**
- HIGH recall: **94.1%**

Important:
The 94.1% HIGH visibility is bought at the cost of **14 normal-month alarms**. Therefore this union is descriptive and must not be used as a single production alarm.

### T0_PLUS_T1_STANDARD
- events: **34**
- HIGH hits: **12**
- MEDIUM hits: **4**
- NORMAL false calls: **18**
- useful-call rate: **47.1%**
- false-call rate: **52.9%**
- HIGH recall: **70.6%**

T1 improves HIGH coverage but materially worsens false-call burden if treated as an equal hard alarm.

### ANY_VISIBLE = all T0 signals OR T1_WGC
- events: **40**
- HIGH hits: **16**
- MEDIUM hits: **5**
- NORMAL false calls: **19**
- useful-call rate: **52.5%**
- false-call rate: **47.5%**
- HIGH recall: **94.1%**

Binding conclusion:
**ANY_VISIBLE must not be interpreted as one alarm.**
It is a research visibility map only.

## 6. Multi-signal false calls

Normal months where 2+ independent signal channels fired:

- 2021-11 — A + T1_WGC — APE 0.462%
- 2022-08 — G + I2 + T1_WGC — APE 2.031%
- 2022-10 — I2 + T1_WGC — APE 0.193%
- 2022-12 — I2 + T1_WGC — APE 1.755%
- 2023-02 — B + T1_WGC — APE 1.566%
- 2023-03 — H + T1_WGC — APE 2.199%
- 2023-09 — H + I2 + T1_WGC — APE 0.281%
- 2023-10 — I2 + T1_WGC — APE 1.853%
- 2023-11 — I2 + T1_WGC — APE 0.624%
- 2026-07 — G + I2 + T1_WGC — APE 2.030%

This is especially important: even multiple simultaneous warnings do not guarantee a HIGH or MEDIUM error.

## 7. Binding interpretation

1. Every future alarm report must show HIGH hits, MEDIUM hits and NORMAL false calls together.
2. False-call rate is mandatory alongside recall.
3. E's zero false calls are descriptive only and do not override its discovery-period status.
4. G, I2 and T1_WGC are useful regime warnings but have substantial false-call burdens.
5. T0_STANDARD is materially cleaner than adding every visible signal indiscriminately.
6. No all-signals OR should be promoted to a production alarm.
7. The next stage should optimize/select alarm confidence only after preserving an untouched validation segment; no threshold retuning is authorized here.
