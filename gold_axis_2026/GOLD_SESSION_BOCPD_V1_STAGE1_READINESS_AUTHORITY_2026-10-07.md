# GOLD SESSION — BOCPD V1 STAGE-1 READINESS AUTHORITY

**Date:** 2026-10-07  
**Status:** **PASS / READY FOR PREREGISTERED 2023–2024 SESSION REPLAY**

## 1. Canonical identity

The canonical SESSION BOCPD port is **Handoff Competence BOCPD V1**.

BOCPD is a **meta-trust / correction controller**, not a stand-alone UP/DOWN model. It estimates whether a canonical Handoff alarm is currently competent enough that flipping the already-frozen session baseline is justified.

The historical V4 hysteresis extension is **not** promoted to the canonical SESSION identity. V4 was designed after inspection of the H3 V1 chronology and remains post-hoc challenger/diagnostic evidence only.

## 2. Frozen BOCPD V1 parameters

Inherited unchanged from the historical BOCPD V1 identity:

- likelihood: Bernoulli RESCUE/BROKEN;
- segment prior: Jeffreys `Beta(0.5, 0.5)`;
- hazard: constant;
- expected run length: **4 Handoff alarms**;
- action threshold: predictive `P(RESCUE) >= 0.60`;
- action threshold: mixture `P(theta > 0.50) >= 0.80`.

These parameters are **not reselected on SESSION 2023–2025 outcomes**.

Expected-run=4 is treated as an inherited model-identity parameter. The old H3 grid `{4,6,8,12}` is not reopened for SESSION optimization.

## 3. Frozen canonical Handoff alarm

At a session decision origin, Handoff alarm is:

- `leadlag_score_premax >= 0.60`;
- `internal_now >= 0.60`;
- `internal_d1 >= 0`;
- frozen session baseline direction still follows the prevailing pre-target XAU momentum.

No topology veto is part of BOCPD V1.

No DPTC phase gate, SELLR rule, V4 hysteresis rule, RTE rule or later controller is allowed into BOCPD V1 Stage-2.

## 4. SESSION clock mapping

For every target row:

- decision cutoff = exact corrected SESSION `start_utc`;
- only information whose availability timestamp is **strictly earlier than** `start_utc` may enter the Handoff state;
- exact-boundary equality is rejected;
- no current target-window price may enter any feature;
- cross-market hourly bars must be fully completed before `start_utc`.

The existing SESSION exact-clock authority remains binding.

### XAU momentum and fragility mapping

The prevailing momentum is the sign of the current SESSION-native pre-target **12-hour XAU return**.

Historical H3 `session_against_trend` is ported without target leakage as:

`-sign(momentum_12h) * completed_NY_day_return_at_cutoff / rv_12h`.

Here `completed_NY_day_return_at_cutoff` uses only completed XAU bars from the first available New-York-local hourly bar of the current local date through the latest fully available hourly bar strictly before target start.

This is the clock-safe SESSION analogue of the H3 `h_session_ret` term. It must never use the return of the target session being predicted.

The remaining fragility/path quantities retain their frozen formulas:
- trend strength;
- opposite semivariance share;
- deceleration;
- path consistency;
- trend close location;
- adverse excursion and related path state.

## 5. Cross-market raw-source producer

Handoff cross-market state is rebuilt from raw hourly futures observations, not archived H3 IFBC/LLRS/Handoff score files.

Required roots:
- GC
- SI
- NQ
- ZN
- CL

The raw-source reconstruction authority is currently PASS:
- IFBC overlap: 280 rows, numerical reproduction approximately machine precision;
- LLRS overlap: 332 rows, maximum score discrepancy approximately `1.43e-14`;
- raw-source reproduction gate: PASS.

For 2023–2024, Databento source-bridged history is available and previously reconstructed with seven fixed continuous-contract mappings without using outcome labels to select a winner.

### Source-robustness rule

Primary Stage-2 replay uses the existing canonical BASE mapping:

- GC.v
- SI.v
- NQ.v
- ZN.n
- CL.c

The six already-defined alternative mappings are run as source-sensitivity evidence.

No roll mapping may be selected by BOCPD rescue/break performance. A conclusion that changes materially across source mappings must be labelled **SOURCE_SENSITIVE**, not promoted by choosing the best mapping.

## 6. SESSION state isolation and maturity

BOCPD state is independent for each `(partition, window)`.

For current session start `T`:

1. identify prior canonical Handoff alarms in that same partition/window;
2. an alarm outcome may update BOCPD only when its target satisfies `end_utc <= T`;
3. still-open/overlapping targets remain pending;
4. the current alarm is scored from the posterior **before** its own outcome is observed;
5. after maturity, competence label is:
   - `1 = RESCUE` if flipping the frozen baseline would have corrected an error;
   - `0 = BROKEN` if flipping would have destroyed a correct baseline call.

This prevents target-overlap leakage.

## 7. Frozen SESSION baselines

BOCPD does **not** build consensus at this stage.

The development-only balanced baseline already frozen for each session is the object that BOCPD may flip:

| Partition | Window | Frozen baseline |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S17_A1_SESSION |
| SOBTI_5_ET | ASIA_MORNING_LIT | CORE3_A0 |
| SOBTI_5_ET | EUROPE_LIT | CORE3_A0 |
| SOBTI_5_ET | NY_LONDON_LIT | STRUCTURAL_IRIS_1H |
| SOBTI_5_ET | US_LATE_LIT | S17_A1_SESSION |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY |
| WGC_2026_NY3 | EUROPE | STRUCTURAL_IRIS_1H |
| WGC_2026_NY3 | US | S18_A1_PATH_SESSION |

Specialist candidates, HELIOS, OPAL and other routers are not blended into the baseline before BOCPD testing.

## 8. Stage chronology

### Stage-2 — development only
Run causal SESSION BOCPD V1 on **2023–2024 only**.

Required reporting per session:
- eligible/common rows;
- Handoff alarm count;
- BOCPD ACT count;
- RESCUE;
- BROKEN;
- net rescue;
- action precision;
- baseline vs assisted Accuracy;
- baseline vs assisted Balanced Accuracy;
- UP recall;
- DOWN recall;
- first ACT date;
- source-mapping sensitivity.

No 2025 outcome may be inspected before the Stage-2 result and transport gate are frozen.

### Stage-3 — 2025 frozen transport
Only session heads passing the preregistered Stage-2 gate may open 2025.

### Stage-4 — 2026 stress
2026 remains retrospective stress only and cannot alter the model. It is currently unavailable until a V5-equivalent 2026 SESSION target/source extension is governed.

## 9. Stage-1 verdict

- BOCPD V1 identity: **PASS**
- V4 as canonical identity: **REJECTED; diagnostic only**
- raw Handoff producer: **PASS**
- 2023–2024 cross-market source coverage: **PASS**
- SESSION decision-clock mapping: **PASS**
- target-maturity handling: **PASS**
- frozen per-session baseline mapping: **PASS**
- 2025 status: **CLOSED**
- 2026 status: **UNOPENED / target extension pending**

**Next action:** preregister the Stage-2 promotion/retention gate, then run BOCPD V1 on 2023–2024 only.

## Authorities

- `GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_PREREG_2026-10-04.md`
- `GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_RESULT_2026-10-04.md`
- `GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS_PREREG_2026-10-04.md`
- `GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_RESULT_2026-10-04.md`
- `GOLD_H3_2025_BACKFILL_DPTC_RESULT_2026-10-05.md`
- `GOLD_H3_2025_BACKFILL_DPTC_SUMMARY_2026-10-05.json`
- `GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_2026-10-05.md`
- `GOLD_SESSION_CROSSMETAL_V3_EXACTCLOCK_RESULT_2026-10-06.md`
- `GOLD_SESSION_ROLE_AWARE_MODEL_EVALUATION_AUTHORITY_2026-10-07.md`
- `GOLD_SESSION_SELECTED_INCREMENTAL_DISAGREEMENT_V1_RESULT_2026-10-07.md`
