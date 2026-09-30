# GOLD MONTHLY — ChHHO Error Severity V2 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Workflow:** Gold Monthly ChHHO Error Severity V2  
**Run:** **36702363530**  
**Artifact:** **11090178105**  
**Authority commit:** `e08c0cf26d26ab8b47b38d7dc4fb93dc83cbbc37`  
**Code commit:** `db7c60786c872d965be21e5f0c215226334dd8f0`  
**Workflow commit:** `872f816e057e9ffed13a6e6920e87bd339b6860a`

## 1. Binding severity definition

Alarm research now uses fixed normalized return-error bands:

- **NORMAL:** absolute Gold log-return forecast error < **2.50 percentage points**
- **MEDIUM:** **2.50 <= error < 3.00 percentage points**
- **HIGH:** **error >= 3.00 percentage points**

This supersedes the previous DEV-Q3 return-error cutoff as the primary severity interpretation.

The main forecasting project objective remains unchanged:
- cumulative absolute USD error ΣAE;
- direction accuracy;
- supporting MAE/MAPE/WAPE/RMSE.

AE remains an economic/dollar-impact metric, not the alarm severity label.

## 2. Severity counts

Across 58 scientifically usable ChHHO targets:
- NORMAL: **34**
- MEDIUM: **5**
- HIGH: **19**

### Valid pre-DEV
- HIGH: 2021-12
- MEDIUM: 2022-01, 2022-02

### DEV 2022-04..2024-12
HIGH:
- 2022-05
- 2022-07
- 2022-09
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- 2024-07
- 2024-11

MEDIUM:
- 2024-04

### 2025
HIGH:
- 2025-02
- 2025-03
- 2025-09
- 2025-10
- 2025-11

MEDIUM:
- 2025-01
- 2025-05

### 2026 Jan-Aug
HIGH:
- 2026-01
- 2026-03
- 2026-06
- 2026-08

MEDIUM:
- none

## 3. Difference from previous DEV-Q3 label

Previous exact DEV-Q3 threshold:
- 3.0058983302 pp

New HIGH threshold:
- 3.0000000000 pp

The only changed target is:
- **2024-07** — return error **3.00589833pp**

Therefore:
- previous Q3 rule: boundary, not HIGH;
- new fixed 3.0% rule: **HIGH**.

This is the expected consequence of the requested human-readable threshold and not threshold fitting.

## 4. A/B/C/D/H performance on HIGH errors

### DEV
- HIGH months: **9**
- A/B/C/D/H hits: **5**
- misses: **4**
- recall: **55.6%**

Hits:
- 2022-11 — A
- 2023-01 — B
- 2023-08 — A
- 2024-07 — C and H
- 2024-11 — D

Misses:
- 2022-05
- 2022-07
- 2022-09
- 2024-03

### 2025
- HIGH months: **5**
- hits: **4**
- recall: **80%**
- miss: **2025-11**

Hits:
- 2025-02 — H
- 2025-03 — B
- 2025-09 — A
- 2025-10 — H

### 2026 Jan-Aug
- HIGH months: **4**
- hit: **1**
- recall: **25%**
- hit: 2026-03 — H
- misses: 2026-01, 2026-06, 2026-08

### All usable
- HIGH months: **19**
- A/B/C/D/H hits: **11**
- misses: **8**
- alarm events: **19**
- false alarms relative to HIGH: **8**
- precision: **57.9%**
- recall: **57.9%**

These are descriptive mechanism-coverage figures, not production alarm performance.

## 5. Individual mechanisms on HIGH errors

### A
Events: 5  
HIGH hits:
- 2022-11
- 2023-08
- 2025-09

False alarms relative to HIGH:
- 2021-11
- 2025-12

Precision: **60%**

### B
Events: 4  
HIGH hits:
- 2023-01
- 2025-03

False alarms:
- 2023-02
- 2023-05

Precision: **50%**

### C
Event:
- **2024-07**

Return error = **3.005898pp**, therefore HIGH under the fixed 3% definition.

Result:
- 1 event
- 1 HIGH hit

Status:
**C regains its low-event HIGH-hit status.**
Still too few events for broad validation.

### D
Event:
- 2024-11

Result:
- 1 event
- 1 HIGH hit

Status unchanged: rare but real HIGH hit.

### H — CFTC POSITIONING SHIFT
Events: 9  
HIGH hits:
- 2021-12
- 2024-07
- 2025-02
- 2025-10
- 2026-03

False alarms relative to HIGH: 4

Precision:
**55.6%**

H remains the most important new repeated warning candidate because it links a valid pre-DEV event to later HIGH-error events without threshold retuning.

## 6. MEDIUM-error months

Exactly five:

| Target | Return error | Comment |
|---|---:|---|
| 2022-01 | 2.9143pp | no A/B/C/D/H |
| 2022-02 | 2.7126pp | no A/B/C/D/H |
| 2024-04 | 2.5–3.0pp | H warning present |
| 2025-01 | 2.9692pp | POSITION_EXTREME descriptor |
| 2025-05 | 2.7653pp | E + GVZ / volatility descriptor |

A/B/C/D/H catches only **1/5 MEDIUM** targets:
- 2024-04 via H.

Interpretation:
The current alarm family is much more oriented toward the larger HIGH-error mechanisms than toward borderline 2.5–3.0pp misses.

## 7. Elevated error = MEDIUM + HIGH

Across all usable rows:
- elevated-error months: **24**
- A/B/C/D/H hits: **12**
- recall: **50%**
- precision: **63.2%**

By period:
- pre-DEV: 1/3
- DEV: 6/10
- 2025: 4/7
- 2026: 1/4

## 8. HIGH misses after A/B/C/D/H

Eight remain:

- 2022-05
- 2022-07
- 2022-09
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

Existing descriptors:
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

1. Alarm error severity is now permanently reported as:
   - NORMAL <2.5pp
   - MEDIUM 2.5–<3.0pp
   - HIGH >=3.0pp
2. The previous 3.005898pp DEV-Q3 rule is superseded for severity naming.
3. ΣAE remains the main project economic/model-selection metric.
4. C's 2024-07 event is HIGH under the fixed 3.0pp rule.
5. H remains warning-only, not hard alarm.
6. No alarm-rule thresholds were retuned.
7. No routing/model switching is authorized.
