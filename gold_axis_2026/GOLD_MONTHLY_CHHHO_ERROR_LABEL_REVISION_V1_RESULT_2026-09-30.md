# GOLD MONTHLY — ChHHO Error Label Revision V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Workflow:** Gold Monthly ChHHO Error Label Revision V1  
**Run:** **36701753769**  
**Artifact:** **11089679811**  
**Authority commit:** `b539f41999656a995b4885d8cbb8d28714e18784`  
**Code commit (exact-Q3 correction):** `b1de501398940701ff3c89dbdb6e45eafc780472`

## 1. Binding correction

The fixed USD absolute-error threshold is no longer the primary alarm/failure label.

Project model evaluation remains:
- cumulative absolute USD error (ΣAE);
- direction accuracy;
- supporting MAE/MAPE/WAPE/RMSE.

Alarm research now uses a scale-invariant primary target:

**HIGH_RETURN_ERROR = absolute Gold log-return forecast error > exact DEV Q3.**

Exact DEV thresholds from the authoritative 33-row DEV distribution:
- AE Q3 = **63.0550184580 USD**
- APE Q3 = **2.9611704846%**
- absolute return-error Q3 = **3.0058983302 percentage points**

No thresholds were optimized against 2025/2026.

## 2. Why AE was wrong for alarm classification

Across the 58 scientifically usable ChHHO targets:

- HIGH_AE: **22**
- HIGH_APE: **18**
- HIGH_RETURN_ERROR: **18**

Crucially, HIGH_APE and HIGH_RETURN_ERROR select **exactly the same 18 targets**.

This shows the normalized classification is robust to whether percentage price error or log-return error is used.

### AE-only high-error targets

These are classified high by fixed-dollar AE but **not** by either normalized metric:

| Target | AE USD | APE | Return error |
|---|---:|---:|---:|
| 2024-07 | 71.01 | 2.9612% | 3.005898pp |
| 2025-01 | 79.28 | 2.9256% | 2.9692pp |
| 2025-05 | 90.25 | 2.7274% | 2.7653pp |
| 2025-12 | 93.32 | 2.1657% | 2.1895pp |
| 2026-07 | 82.68 | 2.0299% | 2.0508pp |

The late-period cases demonstrate the price-level bias: nominal USD error rises as Gold's level rises even when percentage/return miss is moderate.

2024-07 is exactly the DEV Q3 boundary in normalized space and therefore is not above Q3.

### Normalized-only high-error target

**2022-09**
- AE = **58.98 USD** — below fixed AE threshold
- APE = **3.5093%**
- return error = **3.4492pp**

Therefore fixed AE also creates the opposite error: it can miss a genuinely large proportional forecast miss when the Gold price level is lower.

## 3. New canonical HIGH_RETURN_ERROR target set

### Valid pre-DEV
- 2021-12

### DEV 2022-04..2024-12
- 2022-05
- 2022-07
- **2022-09**
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- 2024-11

Removed vs AE:
- **2024-07**

Added vs AE:
- **2022-09**

### 2025
- 2025-02
- 2025-03
- 2025-09
- 2025-10
- 2025-11

Removed vs AE:
- 2025-01
- 2025-05
- 2025-12

### 2026 Jan-Aug
- 2026-01
- 2026-03
- 2026-06
- 2026-08

Removed vs AE:
- 2026-07

## 4. Consequence for alarm mechanisms

### A — cross-metal fragility
All usable:
- events 5
- normalized high-error hits 3
- false alarms 2
- hits: 2022-11, 2023-08, 2025-09
- false alarms: 2021-11, **2025-12**

A remains useful/selective, but 2025-12 is no longer a true high-error event under the normalized definition.

### B — supported momentum underreaction
All usable:
- events 4
- hits 2
- false alarms 2
- hits: 2023-01, 2025-03

Status remains warning-only.

### C — delayed rates catch-up
- only event: **2024-07**
- return error = exact DEV Q3 boundary, not above Q3
- normalized hit count = **0/1**

Binding revision:
**C loses its previous “high-error hit” status and is downgraded to a mechanism descriptor / unvalidated warning.**

### D — macro-Gold conflict
- only event: 2024-11
- normalized high error: YES
- remains a clean low-event hit.

### H — CFTC positioning shift
All usable:
- events 9
- normalized high-error hits 4
- false alarms 5
- hits: 2021-12, 2025-02, 2025-10, 2026-03

The previous AE-based 2024-07 H hit disappears.

H still has the important repeated pattern:
- valid pre-DEV hit 2021-12;
- later hits 2025-02, 2025-10, 2026-03.

But precision falls to **44.4%**. Status remains warning-only candidate.

### E — extreme-level/model disagreement
Events:
- 2025-05 — normalized FALSE
- 2025-11 — normalized TRUE
- 2026-01 — normalized TRUE
- 2026-03 — normalized TRUE

Result:
- 3/4 normalized hits
- precision 75% descriptively
- still discovery-period / not independently validated.

### G — post-liquidation
Events:
- 2022-08 — normalized FALSE
- 2026-07 — normalized FALSE
- 2026-08 — normalized TRUE

Result:
- 1/3 normalized hits

This strongly reinforces:
**G is a market high-movement/uncertainty regime signal, not a ChHHO high-error alarm.**

## 5. A/B/C/D/H coverage under the new primary label

### Pre-DEV valid
- high errors: 1
- hit: 2021-12 via H
- recall: 1/1
- one false alarm: 2021-11 via A

Small sample; no stable rate claim.

### DEV
- normalized high errors: 8
- hits: 4
  - 2022-11 A
  - 2023-01 B
  - 2023-08 A
  - 2024-11 D
- misses:
  - 2022-05
  - 2022-07
  - **2022-09**
  - 2024-03
- recall: **50%**
- C and H add no normalized DEV hit beyond the existing mechanisms.

### 2025
- normalized high errors: 5
- A/B/H coverage: 4/5
  - 2025-02 H
  - 2025-03 B
  - 2025-09 A
  - 2025-10 H
- miss: 2025-11
- descriptive recall: **80%**

### 2026 Jan-Aug
- normalized high errors: 4
- H catches only 2026-03
- misses:
  - 2026-01
  - 2026-06
  - 2026-08
- descriptive recall: **25%**

## 6. Current normalized-error misses after A/B/C/D/H

Eight targets:
- 2022-05
- 2022-07
- **2022-09**
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

No currently fixed candidate signal:
- 2022-05
- 2022-07
- **2022-09**
- 2024-03

2022-09 is newly exposed by correcting the error definition and requires separate mechanism/cross-model audit.

## 7. Binding governance

1. **Alarm primary error label = HIGH_RETURN_ERROR**, exact DEV-Q3 threshold 3.0058983302pp.
2. HIGH_APE is the required robustness label and currently produces the identical target set.
3. HIGH_AE is retained only for economic/dollar reporting and the project's ΣAE objective.
4. Historical alarm hit/false-alarm claims based only on AE are superseded where classifications differ.
5. C is downgraded because its only event is not above the normalized-error Q3.
6. 2025-12 A and 2026-07 G are no longer high-error hits.
7. 2022-09 is now a genuine alarm-research miss.
8. No alarm threshold was retuned.
9. No routing/model switching is authorized.
