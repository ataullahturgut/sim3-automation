# GOLD MONTHLY — Specialist Router + Cross-Model SAFE-Veto Overlay V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**DEV overlay:** **CANDIDATE PASS**  
**Transport-compatible SAFE-veto pool:** **NOT SAFETY-COMPATIBLE**  
**Binding operational decision:** keep the frozen Specialist Router alone; do **not** deploy the SAFE-veto overlay.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_SPECIALIST_ROUTER_SAFE_VETO_OVERLAY_V1_AUTHORITY_2026-09-30.md`
- authority commit: `2833f53701d67426e7306fb1052f4ef485324b33`

Code:
- `gold_axis_2026/tools/gold_monthly_specialist_router_safe_veto_overlay_v1.py`
- code commit: `8ecae4243ceb210f714927f0700a558280a1bc0b`

Workflow:
- `.github/workflows/gold-monthly-specialist-router-safe-veto-overlay-v1.yml`
- workflow commit: `111ca4c95e49084e311285677871ae304f973baf`

Execution:
- run: **36777740818**
- artifact: **11127255544**
- artifact digest: `sha256:550b16e3ae8852133c31db36a2c79088b0ebfa5a13c9b95d0386bdd0afef8893`
- scientific gate: **PASS**

## 2. Frozen components

### Router
Exact Specialist Router V1:
- Specialist Hedge
- eta = 0.25
- alpha = 0
- tau = 0.50.

### DEV SAFE-veto
Exact previously frozen 16-model:
- `V2_STRONG_DIRECTION_CONSENSUS`
- ChHHO direction agreement >=80%
- dispersion <= expanding prior median
- minimum prior history 6.

No router or veto parameter was changed.

## 3. Primary DEV overlay result — exact 16-model SAFE-veto

### Frozen Specialist Router alone

- events: **20**
- HIGH hits: **8**
- MEDIUM hits: **2**
- false calls: **10**
- HIGH recall: **100%**
- elevated recall: **100%**
- useful-call rate: **50.0%**
- false-call rate: **50.0%**

### Router + exact frozen 16-model SAFE-veto

- events: **18**
- HIGH hits: **8**
- MEDIUM hits: **2**
- false calls: **8**
- HIGH recall: **100%**
- elevated recall: **100%**
- useful-call rate: **55.6%**
- false-call rate: **44.4%**

Incremental effect versus Router:
- additional false calls removed: **2**
- HIGH lost: **0**
- MEDIUM lost: **0**.

This passes every preregistered DEV overlay condition.

## 4. Exact additional DEV false calls removed

The two additional router false calls removed by the original 16-model SAFE-veto are:

### target 2022-12
- origin 2022-11
- severity: NORMAL
- active signals: I2 + T1_WGC
- router p_HIGH: about **0.773**
- direction agreement: **100%**
- dispersion: **0.794%**
- prior dispersion median: **1.058%**.

### target 2024-08
- origin 2024-07
- severity: NORMAL
- active signal: H
- router p_HIGH: about **0.731**
- direction agreement: **93.75%**
- dispersion: **0.889%**
- prior dispersion median: **0.973%**.

No DEV HIGH or MEDIUM router warning is suppressed.

## 5. Combined DEV improvement from raw alarms to router + veto

Raw ANY_VISIBLE:
- 25 events
- 8 HIGH
- 2 MEDIUM
- **15 false**.

Specialist Router:
- 20 events
- 8 HIGH
- 2 MEDIUM
- **10 false**.

Router + exact 16-model SAFE-veto:
- **18 events**
- **8 HIGH**
- **2 MEDIUM**
- **8 false**.

Thus relative to raw ANY_VISIBLE:
- false calls fall **15 -> 8**
- reduction = **46.7%**
- HIGH lost = **0**
- MEDIUM lost = **0**
- useful-call rate rises **40.0% -> 55.6%**.

On DEV alone, this is the cleanest alarm stack observed so far.

## 6. Critical limitation: original 16-model pool is not available for frozen transport

The original SAFE-veto used 16 competitive model forecasts.

Only 7 of those 16 have a complete frozen prediction history for:
- DEV;
- all 2025;
- 2026 through July.

Transport-capable competitive intersection:

- AOA_ELM
- ChHHO_ANFIS
- FULL7_ANN
- REDUCED4_ANN
- DE_ABC_RBFNN
- LMC2_RBF_M32
- PLS1_V1.

Therefore a 7-model transport-compatible shadow SAFE-veto was constructed using the **same formula and unchanged thresholds**.

## 7. The 7-model shadow is NOT equivalent to the original 16-model veto

On DEV, before looking at transport interpretation:

7-model shadow applied to frozen router:
- false calls removed: **3**
- HIGH wrongly removed: **1**
- MEDIUM wrongly removed: **1**.

Therefore:
- **TRANSPORT_POOL_NOT_SAFETY_COMPATIBLE**.

The exact veto-month overlap is weak.

Among 27 jointly eligible DEV months:

16-model veto targets:
- 2022-12
- 2023-06
- 2023-07
- 2024-02
- 2024-08
- 2024-09
- 2024-10.

7-model shadow veto targets:
- 2023-06
- 2023-08
- 2023-10
- 2023-11
- 2023-12
- 2024-04
- 2024-08.

Intersection:
- 2023-06
- 2024-08.

Jaccard overlap:
- **0.167**.

This is a decisive warning: shrinking the forecast pool materially changes the SAFE-state signal.

## 8. Opened 2025 transport — 7-model shadow is harmful

Frozen Specialist Router 2025:
- 7 events
- 5 HIGH
- 1 MEDIUM
- 1 false
- HIGH recall **100%**
- useful-call rate **85.7%**.

7-model shadow overlay:
- 4 events
- **3 HIGH**
- 1 MEDIUM
- 0 false
- HIGH recall falls to **60%**.

It suppresses:
- target **2025-02 HIGH** — H
- target **2025-09 HIGH** — A + V2
- target 2025-12 NORMAL — A.

Removing one false call is not acceptable because two true HIGH warnings are lost.

## 9. Opened 2026 — critical V2-only catch is destroyed

Frozen Specialist Router 2026:
- 6 events
- **3 HIGH**
- 1 MEDIUM
- 2 false
- HIGH recall **100%**
- elevated recall **100%**.

7-model shadow overlay:
- 4 events
- **2 HIGH**
- 1 MEDIUM
- 1 false
- HIGH recall falls to **66.7%**.

It suppresses:
- target 2026-04 NORMAL — I1
- target **2026-06 HIGH** — V2_TRANSITION only.

The second one is the critical event we specifically needed to preserve:

### origin 2026-05 -> target 2026-06
- raw A/B/C/D/E/G/H/I1/I2/T1 alarms: none
- Specialist Router: WARN
- awake expert: V2_TRANSITION
- router p_HIGH: about **0.731**
- target: HIGH
- 7-model SAFE-veto: TRUE
- overlay would incorrectly suppress it.

Therefore the transport shadow directly conflicts with the strongest incremental value of the Specialist Router.

## 10. 2026-08 limitation

The 7-model frozen transport pool has no complete consensus feature for target 2026-08.

Therefore:
- origin 2026-07 -> target 2026-08
- G + V2 router warning
- HIGH target
- SAFE-veto = NO_FEATURE
- router warning is passed through unchanged.

No claim is made about SAFE-veto behavior for this month.

## 11. Combined opened 2025-2026

Specialist Router:
- 13 events
- **8 HIGH**
- 2 MEDIUM
- 3 false
- HIGH recall **100%**
- useful-call rate **76.9%**.

7-model shadow overlay:
- 8 events
- **5 HIGH**
- 2 MEDIUM
- 1 false
- HIGH recall **62.5%**
- useful-call rate **87.5%**.

The higher precision is obtained by incorrectly deleting **3 HIGH warnings**.

This is not acceptable for the project's primary objective.

## 12. Binding interpretation

Two conclusions must be kept separate.

### A. Exact original 16-model DEV veto is genuinely complementary
On DEV:
- Specialist Router removes 5 false calls;
- original 16-model SAFE-veto removes **2 additional false calls**;
- total false reduction versus raw ANY_VISIBLE = **46.7%**;
- zero HIGH/MEDIUM loss.

This is a real and useful DEV finding.

### B. A reduced model-pool approximation cannot be substituted
The 7-model transport-compatible pool:
- does not reproduce the 16-model veto;
- is already unsafe on DEV;
- removes true HIGHs in 2025;
- suppresses the critical 2026-06 V2-only HIGH catch.

Therefore the 7-model shadow is **rejected**.

## 13. Binding decision

Do **not** put the current SAFE-veto on top of the router operationally.

Freeze the Specialist Router V1 alone as the strongest transport-supported research candidate:

- Specialist Hedge
- eta=.25
- tau=.50
- A/B/C/D/E/G/H/I1/I2/T1/V2 specialists.

Retain the exact 16-model SAFE-veto as a **DEV-only promising orthogonal component**.

Do not:
- lower/raise the 80% threshold;
- alter the dispersion condition;
- use the 7-model shadow;
- retune on 2025/2026.

## 14. What would be required to revisit the SAFE-veto

A fair transport validation requires the **same 16-model forecast pool** used by the original DEV veto to have frozen origin-safe predictions for 2025/2026.

Only then can the exact V2 SAFE-veto be transported apples-to-apples.

Until those missing frozen transport forecasts are available or recreated under their frozen model contracts:

> the SAFE-veto cannot be validated outside DEV, and the Specialist Router should remain un-overlaid.
