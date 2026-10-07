# GOLD OVERNIGHT RFR RESCUE-GATE PREREGISTRATION — 2026-10-07

**Status:** PREREGISTERED / DEVELOPMENT-ONLY GATE SEARCH  
**Target:** 17:00 -> next eligible 09:00 Europe/Istanbul  
**Base:** PAIR_1600_1700 / PAIR_ALL  
**Specialist:** RFR-NOMACRO V1  
**Selection:** 2023-2024 only  
**2025:** retrospective transport only

## Scientific rationale

This test is deliberately not a new consensus.

Three established findings motivate the gate:

1. RFR-NOMACRO shows a stable pre-17:00 reversal/first-impulse mechanism on no-macro days.
2. Gold price discovery is state-dependent around New York/London and macro-news states (Sobti, Sehgal & Ilango, 2021; DOI 10.1016/j.irfa.2021.101893).
3. Forecast-combination theory emphasizes incremental information and forecast-error dependence rather than assigning independent votes to correlated models (Timmermann, 2006; DOI 10.1016/S1574-0706(05)01004-9).

## Origin-safe context experts

Only predictions issued no later than 17:00 Europe/Istanbul (=14:00 UTC) are legal.

PATH family:
- canonical PATH_GLOBAL / PATH_GLOBAL_1H
- WGC_2026_NY3 US head
- SOBTI_5_ET NY_LONDON_LIT head

STRUCTURAL family:
- canonical S14_A1_PLUS_1H_FULL
- WGC_2026_NY3 US head
- SOBTI_5_ET NY_LONDON_LIT head

Within each family, the two probabilities are averaged. This is a state summary, not two independent votes.

Family direction:
- mean p_up >= 0.50 => UP
- otherwise DOWN

No 2025 calibration or threshold selection is allowed.

## Rescue question

The gate is evaluated only when:
- RFR-NOMACRO is active; and
- PAIR direction != RFR direction.

This is the only state in which overriding PAIR can rescue or break a call.

## Fixed candidate states

- G0_PAIR_RFR_DISAGREE: all PAIR/RFR disagreement rows.
- G1_ANY_FAMILY_CONFIRMS_RFR: PATH or STRUCTURAL agrees with RFR.
- G2_BOTH_FAMILIES_CONFIRM_RFR: both agree with RFR.
- G3_FAMILIES_SPLIT: PATH and STRUCTURAL disagree.
- G4_SPLIT_ONE_CONFIRMS_RFR: families disagree and therefore exactly one confirms RFR.
- G5_BOTH_FAMILIES_OPPOSE_RFR: both disagree with RFR; negative-control/veto state.

No probability-margin threshold is tuned in this stage.

## Development selection rule

A rescue gate may be retained only if, in both 2023 and 2024:
- common-row N >= 12;
- RFR accuracy on that gate > 50%;
- net rescue versus PAIR > 0.

Among eligible gates, choose the largest minimum yearly balanced accuracy, then pooled BA, then coverage.

If no gate passes, no rescue override is authorized.

2025 does not participate in gate selection.

## Required outputs

For every candidate/year:
- N / coverage
- RFR accuracy / BA / UP recall / DOWN recall
- PAIR accuracy / BA on identical rows
- rescue / break / net rescue
- PATH / STRUCTURAL agreement state
- 2025 frozen retrospective transport for the development-selected identity

The result must distinguish:
- contextual agreement,
- true incremental rescue,
- and apparent accuracy caused only by abstention or class prevalence.
