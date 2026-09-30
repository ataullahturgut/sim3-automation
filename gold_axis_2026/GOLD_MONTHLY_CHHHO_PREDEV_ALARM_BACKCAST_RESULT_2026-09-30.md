# INVALIDATION NOTICE — 2026-09-30

**This historical backcast result is NOT admissible evidence for or against the ChHHO alarm mechanisms.**

Post-run audit found that the pre-DEV source `gpr_files/gpr_web_latest.xlsx` belongs to the **old GPR methodology** documented on the official Caldara–Iacoviello `gpr2019.htm` page. The current canonical project GPR authority is based on the later methodology documented in `gpr.Rmd` / `data_gpr_export.xls`, whose search terms/methodology were changed in 2021.

Therefore the backcast changed not only the vintage date but also the **definition of the GPR feature**. That violates the frozen data contract and makes the 2019-2021 ChHHO predictions non-comparable to the canonical 2022+ ChHHO model.

Observed evidence of non-equivalence includes large level differences, e.g. the old-source January 2020 GPR snapshot value is about 333.03 while the canonical CORE5 GPR value for 2020-01 is 138.42.

The numerical run itself was reproducible and passed its internal gate, but its **scientific source equivalence premise was wrong**. All hit/false-alarm conclusions below are therefore retained only as an audit trail and must not be used to promote or downgrade A/C/D/E/G.

A separate reconciliation test proved that the backcast helper code itself is correct when supplied with the canonical GPR authority:
- workflow run: 36687542392
- artifact: 11084196490
- result: **PASS**
- targets checked: 2022-04, 2023-08, 2024-11
- sample arrays: exact match
- ChHHO predictions: exact match within floating-point tolerance
- train-row counts and diagnostics: exact match

**Binding status:** `INVALIDATED_GPR_METHODOLOGY_MISMATCH`

---

# GOLD MONTHLY — ChHHO Pre-DEV Alarm Backcast Result

**Date:** 2026-09-30  
**Run:** GitHub Actions 36684719608  
**Artifact:** 11083172327  
**Code commit:** `b31e181487c016cad15b7d4c7ce7e9ef80b13633`  
**Authority:** `GOLD_MONTHLY_CHHHO_PREDEV_GPR_WEB_LATEST_AUTHORITY_2026-09-30.md`  
**Authority commit:** `4c607f78d37291fd0c4685efffd03ef060c187a0`  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS

## 1. Source coverage

Requested origin range: **2019-12..2022-02** (27 origins).

Official Git PIT source:
- repository: `iacoviel/iacoviel.github.io`
- file: `gpr_files/gpr_web_latest.xlsx`
- selection rule: latest commit timestamp <= forecast-origin month-end cutoff.

Buildable origins: **21 / 27**.

Passing origins:
- 2019-12
- 2020-01
- 2020-02
- 2020-03
- 2020-04
- 2020-05
- 2020-06
- 2020-07
- 2020-08
- 2020-09
- 2020-11
- 2020-12
- 2021-01
- 2021-02
- 2021-03
- 2021-04
- 2021-06
- 2021-07
- 2021-08
- 2021-09
- 2021-10

Blocked because required p-1 GPR month was not present in the last official snapshot available by the origin cutoff:
- 2020-10
- 2021-05
- 2021-11
- 2021-12
- 2022-01
- 2022-02

No final-vintage/current GPR substitution was used.

## 2. ChHHO backcast performance in the 21 buildable origins

- n = **21**
- cumulative AE = **922.53 USD**
- MAE = **43.93 USD**
- mean APE = **2.518%**

Using the existing frozen nominal high-error definition:
- HIGH ERROR = AE > **63.06 USD**
- high-error months = **6**

High-error targets:
- 2020-03 — AE **81.87**, APE **5.14%**
- 2020-04 — AE **113.65**, APE **6.75%**
- 2020-07 — AE **70.42**, APE **3.81%**
- 2021-03 — AE **93.31**, APE **5.43%**
- 2021-04 — AE **66.64**, APE **3.79%**
- 2021-08 — AE **74.79**, APE **4.19%**

## 3. Frozen hard-alarm replay: A / C / D / E / G

Combined hard alarm:
- alarms = **2**
- hits = **0**
- false alarms = **2**
- misses = **6**
- precision = **0%**
- recall = **0%**

Per mechanism:

### A — Cross-metal fragility
- alarms: **0**
- no pre-DEV validation event
- no contradiction, but no added historical support

### C — Delayed rates catch-up
- alarm: **2021-09**
- AE = **14.32 USD**
- APE = **0.81%**
- result: **FALSE ALARM**

### D — Macro-Gold conflict
- alarms: **0**
- no pre-DEV validation event

### E — Extreme level + model disagreement
- alarm: **2020-09**
- AE = **23.68 USD**
- APE = **1.23%**
- result: **FALSE ALARM**

At origin 2020-08:
- Gold 1m ≈ **+6.84%**
- Gold 3m ≈ **+13.88%**
- Gold level vs trailing MA12 ≈ **+23.34%**
- ChHHO predicted move ≈ **-1.19%**

This is an important falsification: the extreme-level / disagreement state was present, but ChHHO still produced a relatively small error. Therefore E is **not validated as a ChHHO high-error alarm** merely because it is a meaningful market-state warning.

### G — Post-liquidation
- alarms: **0** in the 21 buildable ChHHO origins
- no ChHHO-specific pre-DEV validation event
- older market-state evidence remains descriptive only

## 4. Scale robustness check

The nominal AE threshold could in principle be unfair to 2020-2021 because Gold price levels were lower. Therefore the same replay was checked with the DEV relative-error threshold.

Frozen DEV ChHHO thresholds:
- AE Q3 = **63.0550 USD**
- APE Q3 = **2.96117%**
- absolute log-return error Q3 = **3.00590 percentage points**

On the 21 pre-DEV backcast origins:

### APE Q3 definition
- high-relative-error months = **8**
- alarms = 2
- hits = **0**
- false alarms = **2**
- misses = **8**
- precision = **0%**
- recall = **0%**

### Return-error Q3 definition
- high-return-error months = **8**
- alarms = 2
- hits = **0**
- false alarms = **2**
- misses = **8**
- precision = **0%**
- recall = **0%**

Thus the negative backcast result is **not caused by nominal USD scaling**.

## 5. Binding interpretation

This pre-DEV replay changes the alarm hierarchy materially.

### What remains supported
- A remains a **selective ChHHO-specific alarm in 2022+ evidence**, but pre-DEV supplied no A events, so it is not independently validated.
- D remains rare and untested pre-DEV.
- The old DEV findings for A/C/D remain descriptive/DEV evidence; they are not erased.

### What is downgraded
- C now has mixed evidence because its only pre-DEV event was a false alarm.
- E must be downgraded from “strong new alarm candidate” to **market-state / model-disagreement warning candidate**.
- G retains historical market-state evidence for elevated post-liquidation movement/uncertainty, but has no pre-DEV ChHHO-specific alarm event in the buildable sample.
- The combined A/C/D/E/G engine is **not validated for production use** and must not be described as an 80%-recall alarm system based on 2026 discovery-period performance.

### Governance
- no threshold retuning is authorized from this backcast;
- no routing/model switching is authorized;
- no attempt should be made to change E/G thresholds to rescue the six pre-DEV misses;
- the six pre-DEV missed high-error months should be characterized separately to determine whether they expose a recurring mechanism that also appears in 2022-2026.

## 6. Next scientific question

Characterize the six missed pre-DEV high-error months:

- 2020-03
- 2020-04
- 2020-07
- 2021-03
- 2021-04
- 2021-08

Then compare their origin-visible states to:
- 2022-2024 DEV worst months;
- 2025 high-error months;
- 2026 high-error months, especially unresolved 2026-06.

The objective is not to fit a rule to those six months. The objective is to determine whether a **natural repeated mechanism** exists across pre-DEV and later periods.
