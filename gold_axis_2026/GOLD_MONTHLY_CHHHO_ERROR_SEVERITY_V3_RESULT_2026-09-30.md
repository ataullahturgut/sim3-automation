# GOLD MONTHLY — ChHHO Error Severity V3 Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Workflow:** Gold Monthly ChHHO Error Severity V3
**Run:** **36702767607**
**Artifact:** **11090497943**
**Authority commit:** `4b005a86c1dbfdae5f3e6979d097b1a7ffdc650d`
**Code commit:** `bcbcc59eedd5f5583dd482916c5c87b600c01a1f`
**Workflow commit:** `9f9e7dd903cf1ae0635bec6f6e8e8e09a95162e8`

## 1. Binding primary severity metric

Primary alarm-severity metric = **APE**.

- NORMAL: APE < 2.50%
- MEDIUM: 2.50% <= APE < 3.00%
- HIGH: APE >= 3.00%

Absolute log-return forecast error remains a robustness metric only.

ΣAE and direction metrics for the forecasting project remain unchanged.

## 2. Counts

Across 58 usable ChHHO targets:
- NORMAL: **34**
- MEDIUM: **7**
- HIGH: **17**

### HIGH targets
- 2021-12
- 2022-05
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
- 2025-11
- 2026-01
- 2026-06
- 2026-08

### MEDIUM targets
- 2022-01
- 2022-02
- 2024-04
- 2024-07
- 2025-01
- 2025-05
- 2026-03

## 3. Return-error robustness disagreements

Only two targets change band when the same 2.5/3.0 cutoffs are applied to log-return error:

- **2024-07**
  - APE = 2.96117% -> MEDIUM
  - return error = 3.00590pp -> HIGH

- **2026-03**
  - APE = 2.99874% -> MEDIUM
  - return error = 3.04462pp -> HIGH

Because the requested concept is percentage price error, APE classification is binding.

## 4. A/B/C/D/H performance on APE HIGH

### DEV
- HIGH = **8**
- A/B/C/D/H hits = **4**
- recall = **50%**

Hits:
- 2022-11 — A
- 2023-01 — B
- 2023-08 — A
- 2024-11 — D

Misses:
- 2022-05
- 2022-07
- 2022-09
- 2024-03

### 2025
- HIGH = **5**
- hits = **4**
- recall = **80%**
- miss = 2025-11

### 2026 Jan-Aug
- HIGH = **3**
- A/B/C/D/H hits = **0**
- recall = **0%**
- misses:
  - 2026-01
  - 2026-06
  - 2026-08

### All usable
- HIGH = **17**
- hits = **9**
- misses = **8**
- alarm events = 19
- false alarms relative to HIGH = 10
- precision = **47.4%**
- recall = **52.9%**

These are descriptive mechanism-coverage figures, not production performance.

## 5. Mechanism status under APE HIGH

### A
HIGH hits:
- 2022-11
- 2023-08
- 2025-09

Events 5; HIGH precision 60%.

### B
HIGH hits:
- 2023-01
- 2025-03

Events 4; HIGH precision 50%.

### C
Only event:
- 2024-07

APE = **2.96117%**, therefore **MEDIUM**, not HIGH.

Binding status:
**C is a medium-error mechanism descriptor / warning, not a HIGH-error hit.**

### D
2024-11 remains a HIGH hit.

### H — CFTC POSITIONING SHIFT
HIGH hits:
- 2021-12
- 2025-02
- 2025-10

Events 9; HIGH hits 3; false alarms relative to HIGH 6; HIGH precision 33.3%.

2024-07 and 2026-03 are MEDIUM under APE, so they are no longer counted as H HIGH hits.

H remains a repeated warning candidate, not a hard alarm.

## 6. MEDIUM targets and coverage

MEDIUM:
- 2022-01
- 2022-02
- 2024-04
- 2024-07
- 2025-01
- 2025-05
- 2026-03

A/B/C/D/H identifies:
- 2024-04
- 2024-07
- 2026-03

The remaining MEDIUM misses:
- 2022-01
- 2022-02
- 2025-01
- 2025-05

## 7. MEDIUM + HIGH ("elevated error")

Across all usable targets:
- elevated = **24**
- A/B/C/D/H hits = **12**
- recall = **50%**
- precision = **63.2%**

By period:
- pre-DEV: 1/3
- DEV: 6/10
- 2025: 4/7
- 2026 Jan-Aug: 1/4

## 8. HIGH misses after A/B/C/D/H

Eight:
- 2022-05
- 2022-07
- 2022-09
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

Descriptor coverage:
- 2025-11: E + GVZ
- 2026-01: E + GVZ
- 2026-06: GVZ + OI compression + FLOW_2OF4
- 2026-08: G + GVZ + OI compression + FLOW_2OF4

No fixed candidate descriptor:
- 2022-05
- 2022-07
- 2022-09
- 2024-03

## 9. Binding decision

1. Alarm severity uses APE:
   - NORMAL <2.5%
   - MEDIUM 2.5–<3.0%
   - HIGH >=3.0%
2. Log-return error is a robustness check.
3. C is MEDIUM, not HIGH.
4. 2026-03 is MEDIUM, not HIGH.
5. H remains warning-only.
6. No alarm-rule retuning.
7. No routing/model switching.
