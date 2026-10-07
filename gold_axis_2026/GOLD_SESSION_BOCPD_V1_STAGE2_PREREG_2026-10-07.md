# GOLD SESSION — BOCPD V1 STAGE-2 PREREGISTRATION

**Date:** 2026-10-07  
**Status:** **PREREGISTERED BEFORE 2023–2024 SESSION RESULTS**

Authority:
- `GOLD_SESSION_BOCPD_V1_STAGE1_READINESS_AUTHORITY_2026-10-07.md`

## Objective

Test the frozen Handoff Competence BOCPD V1 as a **correction/meta-trust controller** on corrected SESSION targets using **2023–2024 development only**.

BOCPD does not create a new base direction forecast. It decides whether a canonical Handoff alarm is trustworthy enough to flip the already-frozen balanced baseline for that partition/window.

## Frozen BOCPD identity

- Bernoulli competence outcome: RESCUE=1, BROKEN=0.
- Jeffreys segment prior: Beta(0.5, 0.5).
- constant hazard with expected run = **4 Handoff alarms**.
- ACT iff:
  - predictive `P(RESCUE) >= 0.60`, and
  - mixture `P(theta > 0.50) >= 0.80`.
- no V4 hysteresis;
- no DPTC phase gate;
- no SELLR;
- no RTE/RC-RTE/SCR-RTE/STCR input.

No parameter is selected on 2023–2024 results.

## Frozen Handoff alarm

For the current session origin T:

1. `leadlag_score_premax >= 0.60`;
2. `internal_now >= 0.60`;
3. `internal_d1 >= 0`;
4. the frozen baseline direction equals the sign of the pre-target XAU 12-hour momentum.

State/ranks are built independently per `(partition, window)`.

## Exact-clock / maturity contract

- target decision origin = `start_utc`;
- every hourly source observation is usable only when its completion/availability timestamp is **strictly earlier** than `start_utc`;
- exact-boundary equality is rejected;
- no target-window information is used;
- a prior Handoff competence outcome updates BOCPD only after its target `end_utc <= current start_utc`;
- current alarm outcome is never used in its own decision.

## Frozen base model per session

| Partition | Window | Base |
|---|---|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S17_A1_SESSION |
| SOBTI_5_ET | ASIA_MORNING_LIT | CORE3_A0 |
| SOBTI_5_ET | EUROPE_LIT | CORE3_A0 |
| SOBTI_5_ET | NY_LONDON_LIT | STRUCTURAL_IRIS_1H |
| SOBTI_5_ET | US_LATE_LIT | S17_A1_SESSION |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY |
| WGC_2026_NY3 | EUROPE | STRUCTURAL_IRIS_1H |
| WGC_2026_NY3 | US | S18_A1_PATH_SESSION |

These bases were frozen from 2023–2024 canonical balanced-base selection before this BOCPD result.

## Raw-source mapping

Primary mapping:
- GC.v.0
- SI.v.0
- NQ.v.0
- ZN.n.0
- CL.c.0

Already-governed archived Databento 1h files are used; no new vendor purchase is needed.

Sensitivity mappings, inherited unchanged from the H3 source-robust audit:
- BASE
- SI_n
- NQ_n
- ZN_v
- CL_v
- GC_n
- NQ_c

No mapping can be selected using BOCPD performance.

## SESSION-native path state

XAU path state is rebuilt from governed XAU/USD 15m source and completed 1h bars.

Frozen formulas preserve the RIFT/Handoff identity:
- momentum sign from pre-target 12h XAU return;
- trend_strength;
- opposite_semivar_share;
- deceleration_6h;
- session_against_trend using only completed New-York-local day information available before target start;
- path_consistency;
- trend_close_location;
- opposite_extreme_recency;
- jump_concentration;
- trend_to_range;
- adverse_excursion.

## Stage-2 development retention gate

BOCPD is a correction specialist; the 30% balanced-primary recall floor does not apply.

A session head may open frozen 2025 transport only if the **canonical BASE source mapping** satisfies all of:

1. at least one actual BOCPD ACT occurs in 2023–2024;
2. combined 2023–2024 net rescue > 0;
3. combined assisted Balanced Accuracy >= baseline Balanced Accuracy;
4. neither 2023 nor 2024 assisted Accuracy is worse than baseline by more than 1.0 percentage point when that year has scored rows;
5. source robustness: none of the six already-defined alternative continuous-contract mappings has a **negative combined 2023–2024 net rescue** for that same session head.

Zero-net alternative mappings are allowed but force the label `SOURCE_WEAK`; any negative alternative mapping forces `SOURCE_SENSITIVE_FAIL`.

No 2025 result may modify this gate.

## Reporting

For BASE and all six source sensitivity mappings, by partition/window and period:
- common/eligible N;
- Handoff alarms;
- ACT count;
- RESCUE;
- BROKEN;
- net rescue;
- action precision;
- baseline Accuracy / BA / UP recall / DOWN recall;
- assisted Accuracy / BA / UP recall / DOWN recall;
- first ACT origin;
- source sensitivity status.

## Chronology

- 2022: source/rank warm-up only where required;
- 2023–2024: **development scoring**;
- 2025: **not read in Stage-2**;
- 2026: **not read in Stage-2**.

If no session passes the frozen gate, BOCPD closes as a non-promoted controller and the project proceeds to DPTC without opening 2025 for BOCPD.
