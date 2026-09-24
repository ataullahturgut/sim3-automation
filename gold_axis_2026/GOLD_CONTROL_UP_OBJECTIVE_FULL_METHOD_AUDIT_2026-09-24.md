# GOLD CONTROL — UP Objective Full-Method Audit

**Date:** 2026-09-24  
**Status:** RESEARCH-ONLY / NO PROMOTION / NO CANONICAL CHANGE

## Objective corrected

The relevant UP objective is **high actual-UP recall together with low false-UP rate on actual-DOWN days**.

This audit therefore forbids the following shortcuts:

- high precision with very low UP coverage is not enough;
- high UP recall from an almost-always-UP classifier is not enough;
- ABSTAIN / NOT-UP / UNCERTAIN is never silently treated as a positive DOWN call;
- route-specific results are not promoted to general-population results;
- weekly, multi-session, event-time and different target-clock results are not imported into the current next-day daily route.

Inventory reviewed: **57 R-registry + 37 H-registry = 94 manifest records**, plus the post-manifest Fixed Share, Local Competence V1/V2 and Default-Gold DOWN Logit V1/V2 research runs.

## A. Current governed same-clock, full-population next-day daily models

### 2024 frozen validation

| Model | UP recall | false-UP FPR | BA | Interpretation |
|---|---:|---:|---:|---|
| Bonato AR1_RM QBoost H1 | 60.50% | 54.65% | 52.93% | best full-population 2024 BA in this comparable set, but false-UP burden is too high |
| Router V1 | 64.71% | 67.44% | 48.64% implied | broader UP capture, worse class separation |
| RV_LOGIT | 81.51% | 82.56% | 49.48% | broad-UP collapse |
| AR1_RM_LOGIT | 73.11% | 74.42% | 49.35% | broad-UP collapse |
| RM_LOGIT | 70.59% | 75.58% | 47.50% | broad-UP collapse |
| TSM | 68.07% | 73.26% | 47.41% | weak two-class discrimination |
| Router V2 | 21.85% | 18.60% | 51.62% | selective verifier, not a high-recall general UP model |

No current-clock full-population model approaches the required combination of high UP recall and low false-UP FPR.

### Transport/stress

- Router V2: UP recall 19.29% / FPR 10.31% in locked 2025; 2.35% / 2.27% in 2026. It becomes too sparse for the user's high-recall objective.
- Local Competence V1: 2025 recall 77.86% / FPR 70.10%; 2026 recall 82.35% / FPR 78.41%. High recall is obtained by excessive UP calling.
- Local Competence V2 and Fixed Share show the same failure mode and are not solutions.
- RV/AR1/RSK/RM logit variants reach very high recall in later periods mainly by approaching always-UP behavior.

## B. Current-clock route-specific UP methods

### One-Sided UP-2 Logit V1 — residual route only

Pre-2025 pooled residual route (2022-2024):
- n=26 = 13 actual UP + 13 actual DOWN;
- 11 UP calls = 8 true + 3 false;
- UP precision = 72.73%;
- UP recall = 61.54%;
- false-UP FPR = 23.08%;
- AUC = 0.7870.

Locked 2025 residual route:
- n=74 = 35 UP + 39 DOWN;
- 25 calls = 13 true + 12 false;
- recall = 37.14%;
- FPR = 30.77%;
- AUC = 0.5165.

2026 residual stress:
- n=157 = 77 UP + 80 DOWN;
- 13 calls = 8 true + 5 false;
- recall = 10.39%;
- FPR = 6.25%;
- AUC ≈ 0.528.

**Interpretation:** UP-2 is the strongest chronology-clean, class-resolved **conditional residual UP signal** found in the current cascade, but it is not a general daily UP detector and its transport weakens materially.

Other residual UP methods:
- Local DES V1: zero eligible calls.
- Trajectory morphology V1: pre-2025 recall 15.38%, FPR 15.38%; pre-gate failed.
- Sequence-shapelet V1: pre-2025 recall 23.08%, FPR 38.46%; failed.
- Regime-conditioned failure detector: locked transport failed.
- Importance-weighted source adaptation improves filtering of UP-2 calls but lacks a mixed-label pre-2025 forward certification period; it is not a new general UP detector.

## C. Earlier daily families on different target clocks / research contracts

These are reviewed but **not directly rankable** against the current governed route.

### V1.53 Europe-session continuation, exact NY17 target

The original workflow artifact was re-opened and its row ledger re-counted for class-specific UP metrics.

Formation 2023-2024:
- actual UP=110, DOWN=102;
- UP calls=117 = 67 true + 50 false;
- UP recall = **60.91%**;
- false-UP FPR = **49.02%**;
- precision = 57.26%;
- BA = **55.94%**.

2025:
- recall 55.56%;
- FPR 51.72%;
- BA 51.97%.

2026 available:
- recall 40.26%;
- FPR 43.33%;
- BA 48.48%.

This is a genuine pre-2025 daily pocket, but it does not transport.

### V1.53 moderate-downshock reversal, exact NY17 target

Formation:
- 14 UP calls = 11 true + 3 false;
- precision 78.57%;
- full-timeline UP recall only **10.00%**;
- false-UP FPR **2.94%**.

This is a sparse high-confidence UP specialist, not a high-recall solution.

### Other older daily families

- V1.50 selected general NEXT_NY17_1D model: 2024-H2 BA 53.36%; failed frozen probabilistic gate.
- V1.63 FULL_HGB: 2025 BA 55.08% but approximately chance in 2026; 2025 cannot create retrospective selection authority.
- V1.68 SESSION_RM GLOBAL showed a 2024Q4 bridge pocket (AUC 0.6615, BA 0.6000), but the broader formation/bridge contract did not support stable forecast skill and later AUCs weakened. The checkpoint does not preserve enough class-count detail to rank it safely by UP recall/FPR, so it remains **NOT_PROVEN for the user's UP objective**.
- V1.69 SESSION_RM retained only weak 1D ranking signal (2025 AUC 0.5359; 2026 AUC 0.5297) and failed proper-score persistence.
- Altuntas AlexNet: BA 49.84% in 2024 and 50.44% in 2025; not a solution.
- HS-SDL-DMA and other 1D/3D adaptive/invariant/local families did not establish stable general daily direction skill.

## D. Strong-looking results that are not the same problem

- Macro Event V3: strong 5/15/30-minute event reaction hit rates (~72-75% all events; stronger in tiny strong-state subgroup), but this is event-time intraday prediction, not general next-day UP.
- Corrected VLMC / fixed-share families: strong weekly 2024 pockets (e.g. BA around 66-68%) but weekly horizon and poor 2025 transport; not daily next-day authority.
- H5/H10/H20 settlement models are multi-session targets and cannot be imported.

## Corrected conclusion

1. **There is no validated general daily UP model in the full matrix that combines high UP recall with low false-UP FPR and stable transport.**
2. **UP-2 remains the strongest current-clock conditional residual UP signal**, not the strongest general UP model.
3. **The best current-clock full-population 2024 validation result is Bonato AR1_RM QBoost H1 by balanced separation, but 60.5% UP recall with 54.7% false-UP FPR is not operationally acceptable for the user's objective.**
4. Earlier daily research contains pockets (Europe-session continuation; SESSION_RM), but none transports strongly enough to overturn the conclusion.
5. Further Router/selector engineering on the existing weak expert pool is not justified as the primary next step. A new general UP model must add genuinely new directional information and be evaluated directly on UP recall and false-UP FPR, with chronology frozen before 2025/2026 inspection.

## Governance

- random split: NO
- 2025 tuning: NO
- 2026 tuning: NO
- canonical branch modified: NO
- production DB writes: NO
- runtime promotion: NO
