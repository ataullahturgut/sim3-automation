# GOLD MONTHLY — ChHHO Alarm Audit V3 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Workflow:** Gold Monthly ChHHO Alarm Audit V3  
**Run:** **36692016381**  
**Artifact:** **11086181973**  
**Authority commit:** `194e436855d7eb4a9d78ba5e843d5886693de760`  
**Audit code commit:** `6169f54414fc4da966e793726185fe64a2d31418`  
**Workflow commit:** `523b19140eab4d9d0a58d984d5cc349e0666705f`

## 1. Decision

The V3 audit passes.

The same audit motor:
- reproduces frozen DEV A/B/C/D events exactly;
- reproduces the prior 2026-05 A event when the legacy common-daily Gold source is deliberately used;
- shows that **2026-05 A disappears** when the canonical monthly Gold authority is used;
- proves the pre-DEV macro reconstruction is numerically identical to External Authority V2 for all five valid pre-DEV origins;
- recomputes the five pre-DEV alarm states from canonical sources.

Therefore:

> **V2 ChHHO/GPR forecasts remain valid, but V2 alarm booleans are superseded by V3.**

## 2. Frozen DEV replay gate

Expected and reproduced exactly:

| Alarm | DEV targets |
|---|---|
| A — Cross-metal fragility | 2022-11, 2023-08 |
| B — Momentum underreaction | 2023-01, 2023-02, 2023-05 |
| C — Delayed rates catch-up | 2024-07 |
| D — Macro-Gold conflict | 2024-11 |

All four replay gates passed.

This establishes that the V3 alarm formulas and canonical source construction reproduce the original DEV mechanism definitions before pre-DEV results are interpreted.

## 3. Gold-source bug isolated

Legacy alarm code used the common-daily four-metal monthly Gold reconstruction.

V3 uses the canonical monthly Gold authority:
- DEV: snapshot `core_gold`
- later period: public World Bank monthly Gold extension.

Across 2022-04..2026-08, exactly **one** A/B/C/D/E/G alarm event changes solely because of this correction:

### 2026-05 target / 2026-04 origin

Legacy common-daily Gold:
- Gold 1m log return = **-0.6383%**
- ChHHO prediction = **-1.6853%**
- 3 other metals opposite to Gold
- A = **TRUE**

Canonical monthly Gold:
- Gold 1m log return = **-2.8194%**
- ChHHO prediction = **-1.6853%**
- the frozen A condition requires |Gold 1m| < 2%
- A = **FALSE**

Therefore the previously reported **2026-05 A false alarm was an artifact of inconsistent Gold-source construction** and must be removed.

No threshold was changed.

## 4. Corrected event lists, 2022-04..2026-08

- **A:** 2022-11, 2023-08, 2025-09, 2025-12
- **B warning-only:** 2023-01, 2023-02, 2023-05, 2025-03
- **C:** 2024-07
- **D:** 2024-11
- **E discovery-frozen:** 2025-05, 2025-11, 2026-01, 2026-03
- **G discovery-frozen:** 2022-08, 2026-07, 2026-08

Hard research alarm remains A OR C OR D OR E OR G.

E/G remain discovery-frozen candidates and their later-period hit rates are descriptive, not validated out-of-sample performance.

## 5. Pre-DEV macro-source audit

For the five valid same-methodology pre-DEV origins, the V2 macro reconstruction and External Authority V2 are exactly equal for:

- Broad USD monthly mean log change
- nominal 10Y monthly-mean change
- real 10Y monthly-mean change

Maximum absolute difference for all three fields:

**0.0**

Thus the V2 concern about separate macro reconstruction does not create a numerical C/D discrepancy in this five-origin window.

## 6. Corrected pre-DEV result

Valid targets:

| Target | AE USD | APE | Return-error pp | Hard alarm | Result |
|---|---:|---:|---:|---|---|
| 2021-11 | 8.41 | 0.462% | 0.463 | **A** | **FALSE ALARM** |
| 2021-12 | **85.62** | **4.783%** | **4.672** | none | **MISS** |
| 2022-01 | 52.16 | 2.872% | 2.914 | none | normal |
| 2022-02 | 49.67 | 2.676% | 2.713 | none | normal |
| 2022-03 | 12.46 | 0.639% | 0.642 | none | normal |

### Why 2021-11 becomes an A event

At origin 2021-10 using canonical Gold:
- Gold 1m log return = **+0.1126%**
- ChHHO predicted move = **+2.0382%**
- prediction direction = current Gold direction
- |Gold 1m| < 2%
- 2 of Silver / Platinum / Palladium move opposite to Gold

Therefore frozen A fires.

The same month did not fire in V2 because V2 used the common-daily Gold reconstruction instead of canonical monthly Gold.

## 7. Three-label robustness

Frozen alarm research labels:

- HIGH_AE = AE > **63.06 USD**
- HIGH_APE = APE > **2.96117%**
- HIGH_RETURN_ERROR = absolute log-return error > **3.00590 pp**

For the five pre-DEV targets, all three labels give exactly the same classification:

- high-error target: **2021-12**
- hard alarm target: **2021-11**
- hits: **0**
- false alarms: **1**
- misses: **1**
- precision: **0%**
- recall: **0%**

This is only a five-origin sample and must not be treated as a reliable population estimate.

## 8. Corrected descriptive period summaries

Using the main HIGH_AE definition and hard A/C/D/E/G research set:

| Period | High-error months | Hard alarms | Hits | False alarms | Misses | Recall |
|---|---:|---:|---:|---:|---:|---:|
| Pre-DEV valid V2 window | 1 | 1 | 0 | 1 | 1 | 0% |
| DEV 2022-04..2024-12 | 8 | 5 | 4 | 1 | 4 | 50% |
| 2025 | 8 | 4 | 4 | 0 | 4 | 50% |
| 2026 Jan-Aug | 5 | 4 | 4 | 0 | 1 | 80% |

Important:
- 2025/2026 counts include E/G, which were discovered using later misses.
- Therefore the 2025/2026 combined hard-alarm precision/recall is **descriptive research evidence only**, not validation.
- The removal of 2026-05 improves descriptive precision only because a data-source inconsistency was corrected; it is not threshold tuning.

## 9. Current mechanism reading after V3

### A — Cross-metal fragility
Evidence now includes:
- DEV hits: 2022-11, 2023-08
- 2025 hits: 2025-09, 2025-12
- valid pre-DEV event: **2021-11 false alarm**
- prior 2026-05 false alarm: **withdrawn due Gold-source inconsistency**

Interpretation:
- A remains a real, selective ChHHO interaction signature;
- it is **not independently validated as universally reliable**, because the only valid pre-DEV A event is false;
- event count remains very small.

### C — Delayed rates catch-up
- DEV event: 2024-07 hit
- no valid pre-DEV event
- status remains low-event / externally unconfirmed.

### D — Macro-Gold conflict
- DEV event: 2024-11 hit
- no valid pre-DEV event
- status remains rare / externally unconfirmed.

### E — Extreme-level/model disagreement
- later-period candidate only;
- no valid pre-DEV event;
- still discovery-frozen, not production validated.

### G — Post-liquidation
- 2022-08 false alarm, 2026-07 and 2026-08 later hits;
- no valid pre-DEV event;
- remains an uncertainty-regime candidate.

## 10. Binding governance

1. The old 21-origin V1 remains invalid due GPR methodology mismatch.
2. V2 same-methodology ChHHO forecasts remain admissible.
3. **V2 alarm booleans and alarm summary are superseded by V3.**
4. 2026-05 must no longer be listed as an A false alarm.
5. Valid pre-DEV A event **2021-11** must be listed as a false alarm.
6. Valid pre-DEV high-error miss **2021-12** remains unresolved and is robust across AE, APE and return-error labels.
7. No routing/model switching is authorized.
8. No alarm threshold retuning is authorized.
9. The next research question remains mechanism discovery for uncovered high-error states, especially the repeated structure around unresolved misses rather than forcing existing thresholds to catch them.
