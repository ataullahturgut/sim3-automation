# GOLD MONTHLY — ChHHO Miss Mechanism Screen V2 Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Workflow:** Gold Monthly ChHHO Miss Mechanism Screen V2
**Run:** **36700638160**
**Artifact:** **11089099005**
**Authority commit:** `69ea7d54308573928a1761ae56c246b5fd70266c`
**Code commit:** `297202a174940883a06d84b76c70595665742afc`
**Workflow commit:** `ec5159fe926123426de3b1ca36709c72670df89f`

## 1. Scope

The unstable H1 2013-2021 counterfactual ChHHO replay is excluded from model-error validation.

Usable model periods:
- valid same-method pre-DEV 2021-11..2022-03;
- frozen canonical DEV 2022-04..2024-12;
- frozen 2025 transport;
- frozen 2026 Jan-Aug.

Existing explanation set for this screen = A OR B OR C OR D.

Research target:
**UNEXPLAINED_HIGH_AE = AE > 63.06 USD and no A/B/C/D.**

## 2. Independent candidate threshold calibration

All GVZ/CFTC quantile thresholds were calibrated on **2010-01..2020-12 only**.

Frozen calibration values:
- CFTC abs monthly Managed-Money net/OI change Q90 = **0.1499821**
- CFTC abs monthly open-interest pct change Q90 = **14.9766%**
- CFTC OI / prior-12m median Q10 = **0.865006**
- CFTC Managed-Money net/OI Q10 = **0.0293005**
- CFTC Managed-Money net/OI Q90 = **0.363831**
- GVZ max Q80 = **24.468**
- GVZ max Q90 = **28.321**
- GVZ dynamic ratio Q90 = **1.404916**
- Gold realized-vol ratio Q95 = **1.861729**

No 2021+ ChHHO error was used to choose these threshold values.

## 3. Existing A/B/C/D unexplained HIGH_AE targets

Fourteen usable-period high-error targets are not identified by A/B/C/D:

- 2021-12
- 2022-05
- 2022-07
- 2024-03
- 2025-01
- 2025-02
- 2025-05
- 2025-10
- 2025-11
- 2026-01
- 2026-03
- 2026-06
- 2026-07
- 2026-08

## 4. Only repeated pre-discovery -> later mechanism: CFTC POSITION SHIFT

Definition, fixed from 2010-2020:
- abs monthly change in Managed-Money net position / OI >= **0.1499821**
  OR
- abs monthly open-interest change >= **14.9766%**.

### Pre-discovery 2021-11..2024-12

Alarm targets:
- 2021-12 — HIGH ERROR / previously unexplained
- 2023-03 — false alarm
- 2023-09 — false alarm
- 2024-04 — false alarm
- 2024-07 — HIGH ERROR, already identified by C
- 2024-08 — false alarm

Performance:
- events = **6**
- high-error hits = **2**
- false alarms = **4**
- precision = **33.3%**
- unexplained high-error hit = **2021-12**

### 2025

Alarm targets:
- 2025-02 — HIGH ERROR / previously unexplained
- 2025-10 — HIGH ERROR / previously unexplained

Performance:
- events = **2**
- hits = **2**
- false alarms = **0**

### 2026 Jan-Aug

Alarm target:
- 2026-03 — HIGH ERROR / previously unexplained

Performance:
- events = **1**
- hit = **1**
- false alarms = **0**

### Combined usable period

- events = **9**
- high-error hits = **5**
- false alarms = **4**
- precision = **55.6%**
- recall of all HIGH_AE = **22.7%**
- previously unexplained hits = **4/14 = 28.6%**

Previously unexplained targets identified:
- **2021-12**
- **2025-02**
- **2025-10**
- **2026-03**

Interpretation:
**CFTC_POSITION_SHIFT is the only candidate in this screen that has one pre-discovery unexplained ChHHO error event and repeats on later unexplained high-error events without threshold retuning.**

Status:
**PROMISING WARNING / POSITIONING-REPRICING MECHANISM — NOT HARD ALARM.**

The pre-discovery false-alarm count is too high for hard-alarm promotion.

## 5. Other candidate families

### POSITION_EXTREME
All usable:
- events 7
- high-error hits 3
- false alarms 4
- unexplained hits: 2025-01, 2025-02

But there is no pre-discovery unexplained high-error hit.

Status:
**2025 regime descriptor / not independently repeated.**

### OI_COMPRESSION
All usable:
- events 13
- high-error hits 7
- false alarms 6
- unexplained hits: 2026-03, 2026-06, 2026-07, 2026-08

Pre-discovery high-error hits existed at 2022-11 and 2023-01, but both were already identified by A/B mechanisms; there is no pre-discovery unexplained hit.

Status:
**flow/liquidity stress descriptor; 2026-heavy, not independently validated as a new miss mechanism.**

### FLOW_2OF4
All usable:
- events 11
- high-error hits 6
- false alarms 5
- unexplained hits: 2025-02, 2026-03, 2026-06, 2026-07, 2026-08

No pre-discovery unexplained hit.

Status:
**exploratory flow-regime warning only.**

### GVZ Q80
All usable:
- events 13
- high-error hits 8
- false alarms 5
- unexplained hits 7/14:
  2025-05, 2025-11, 2026-01, 2026-03, 2026-06, 2026-07, 2026-08

However there is no pre-discovery unexplained high-error hit; the pre-discovery event 2022-04 is a false alarm.

Status:
**later-regime gold-volatility warning; not validated as a general ChHHO error alarm.**

### Frozen E
Unexplained hits:
- 2025-05
- 2025-11
- 2026-01
- 2026-03

No pre-discovery unexplained hit.

Status unchanged:
**discovery-period pattern / unvalidated error alarm.**

### Frozen G
Unexplained hits:
- 2026-07
- 2026-08

Pre-discovery event 2022-08 is a false alarm.

Status unchanged:
**historically supported high-movement regime warning / not validated ChHHO error alarm.**

## 6. Three remaining no-signal high-error months

After evaluating all fixed candidate states, only three A/B/C/D-unexplained HIGH_AE targets have **none** of the candidate E/G/GVZ/CFTC/volatility states:

- **2022-05 — AE 79.94**
- **2022-07 — AE 64.95**
- **2024-03 — AE 131.58**

Cross-model overlap authority shows:

### 2024-03
- 16/16 competitive models rank it in their own worst 8.
- Best alternative AE 126.11 vs ChHHO 131.58.
- Rescue only 5.47 USD.

**Classification: SHARED-HARD.**

### 2022-07
- 14/16 competitive models rank it in their own worst 8.
- Best alternative AE 63.19 vs ChHHO 64.95.
- Rescue only 1.76 USD.

**Classification: SHARED-HARD.**

### 2022-05
- 11/16 competitive models rank it in their own worst 8.
- Best alternative AE 62.18 vs ChHHO 79.94.
- Rescue 17.77 USD.

**Classification: BROADLY HARD / LIMITED RESCUE, not a clean ChHHO-specific failure.**

Scientific implication:
These three months should not be used to force a new ChHHO-specific alarm threshold. They are better treated as global hard-month / shock-risk cases.

## 7. Revised mechanism map

### Existing ChHHO-specific mechanisms
- A — cross-metal fragility
- B — supported momentum underreaction, warning-only
- C — delayed rates catch-up
- D — macro-Gold conflict

### New repeated candidate
- **H — CFTC POSITIONING SHIFT**
  - repeated pre-discovery and later
  - catches 2021-12, 2025-02, 2025-10, 2026-03
  - false alarms remain material
  - warning-only candidate

### Later-regime descriptors
- E — trend/level + model disagreement
- G — post-liquidation high uncertainty
- GVZ / OI compression / FLOW_2OF4 — gold-specific flow/volatility stress descriptors

### Global hard-month class
- 2022-05
- 2022-07
- 2024-03

These are not currently supported as ChHHO-specific alarm failures.

## 8. Binding decision

1. Add **H — CFTC POSITIONING SHIFT** as a **candidate warning**, not a hard alarm.
2. Keep its 2010-2020 thresholds frozen.
3. Do not combine H with E/G/GVZ by searched Boolean rules yet.
4. Do not promote E/G/GVZ/OI compression as validated ChHHO high-error alarms.
5. Treat 2022-05, 2022-07 and 2024-03 as broad/shared-hard cases rather than forcing ChHHO-specific alarm rules.
6. No routing or model switching is authorized from this screen.
