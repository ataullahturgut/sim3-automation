# GOLD SESSION — DPTC STAGE-1B SELLR LINEAGE RECONSTRUCTION AUTHORITY

**Date:** 2026-10-07  
**Status:** **LINEAGE RECOVERED / HISTORICAL SELLR IS HORIZON-DEPENDENT / DIRECT SESSION REUSE PROHIBITED**

## 1. Supersession

This authority supersedes the earlier repository-only conclusion that the SELLR producer lineage was unresolved.

The original producer was recovered from the historical branch:

`gold-h3-reversal-mechanism-tournament-v1-20261004`

Canonical producer implementation:

`gold_axis_2026/tools/gold_h3_reversal_mechanism_tournament_v1.py`

Producer-add commit:

`bbcc2affa9942fd7e6ae4a18f2e60de66cf4a5a6`  
message: **Add multi-mechanism reversal tournament V1**

Historical preregistration and result:
- `GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_PREREG_2026-10-04.md`
- `GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_RESULT_2026-10-04.md`
- `GOLD_H3_REVERSAL_MECHANISM_TOURNAMENT_V1_SUMMARY_2026-10-04.json`

## 2. What SELLR actually is

SELLR = **Sequential Evidence Log-Likelihood Ratio**.

It is not a fixed raw-market score. It is a supervised reversal-vs-continuation evidence accumulator.

Historical training chronology:
- 2023–2024: construct/freeze SELLR bin statistics;
- 2025: threshold eligibility/selection;
- 2026: frozen retrospective stress.

Historical target:

`reversal_target = 1[y_up != momentum_up]`

where `y_up` is the **H3 target direction** and `momentum_up` is the H3 pre-target prevailing-momentum state.

Therefore the learned SELLR score is explicitly tied to the H3 target horizon.

## 3. Exact historical feature set

For each feature, the producer applies the listed sign before fitting evidence bins:

1. `adverse_excursion` × +1
2. `trend_strength` × -1
3. `trend_close_location` × -1
4. `session_against_trend` × +1
5. `opposite_semivar_share` × +1
6. `signed_opt_pressure` × +1
7. `signed_d_opt_pressure` × +1
8. `core_confirmation` × -1
9. `cross_dispersion` × +1
10. `topology_rotation` × +1
11. `trend_age` × +1

The producer also defines:
- `trend_age` = consecutive historical origins with unchanged momentum direction;
- `topology_rotation = sqrt((ndx_r60_d1)^2 + (vix_r60_d1)^2)`.

## 4. Exact SELLR estimator

For every signed feature separately, using **2023–2024 H3 training rows**:

1. multiply feature by its frozen sign;
2. impute missing training values with the training median;
3. create quintile bins from the 2023–2024 training distribution;
4. for each bin, count H3 reversal and continuation outcomes;
5. apply Laplace smoothing;
6. compute:

`LLR_bin = log(P(bin | reversal) / P(bin | continuation))`

with implementation:

`P(bin | reversal) = (n_reversal_bin + 1) / (N_reversal + K)`

`P(bin | continuation) = (n_continuation_bin + 1) / (N_continuation + K)`

7. SELLR score at an origin = sum of the eleven feature-bin LLR contributions.

Thus **both the bin evidence values and the aggregate score depend on H3 reversal labels**.

## 5. Historical threshold identity

Threshold candidates were the 0.80 / 0.85 / 0.90 / 0.95 quantiles of the **2023–2024 H3 SELLR score distribution**.

2025 selected:

- family: SELLR
- quantile: **0.95**
- numeric threshold: **2.3677413378977423**
- Handoff confirmation: false
- actions: 9
- rescue / broken / net: 6 / 3 / +3
- precision: 66.7%

The numeric threshold is therefore not a universal market-state constant. It is a quantile of an H3-target-trained score.

## 6. SESSION portability verdict

### Portable
The **algorithmic idea** is portable:
- signed origin-safe mechanisms;
- per-feature distribution bins;
- Laplace-smoothed reversal-vs-continuation likelihood ratios;
- additive evidence score.

### Not portable without refitting
The following historical objects are **H3-horizon-specific** and prohibited as SESSION inputs:
- historical SELLR bin cut points;
- historical per-bin LLR values;
- historical SELLR scores;
- historical threshold 2.3677413378977423;
- historical H3 trend-age sequence;
- any H3 `reversal_target`, `y_up`, baseline or competence outcome.

## 7. Why this is a horizon dependency

The historical score is trained using the conditional distribution:

`P(feature-bin | H3 reversal)`

versus

`P(feature-bin | H3 continuation)`.

The current project needs:

`P(feature-bin | SESSION reversal in a specific partition/window)`

versus

`P(feature-bin | SESSION continuation in that partition/window)`.

Those are not the same statistical target.

Even if the raw features were numerically identical at some origin, the learned LLR table can change because:
- SESSION labels differ from H3 labels;
- session lengths differ;
- reversal prevalence differs by window;
- feature-to-outcome mapping can differ by Asia / Europe / NY-London / US;
- historical `trend_age` counted one H3 origin sequence and cannot be pooled blindly across multiple same-date session origins.

Therefore direct reuse would be a genuine horizon/model-identity error.

## 8. Required SESSION successor identity

If DPTC is to retain a SELLR-like catalyst, it must be a new named model:

**SESSION-SELLR V1**

Minimum binding design requirements before any results are opened:

1. target = corrected V5 SESSION reversal:
   `SESSION direction != pre-target SESSION momentum direction`;
2. fit state independently by `(partition, window)`, unless a pooling rule is preregistered before results;
3. training outcomes admitted only after `end_utc <= current start_utc`;
4. all feature availability must be proven at exact `start_utc`;
5. `trend_age` must be same-window momentum-run age, not a global multi-session counter;
6. daily topology/options state may attach to several sessions on one date, but daily persistence must advance once per daily observation, not once per session;
7. H3 SELLR scores may not be used as labels, calibration targets or reconstruction objectives;
8. old 2.3677413378977423 threshold is prohibited;
9. any threshold/quantile eligibility must be selected only from 2023–2024 SESSION development;
10. 2025 remains unopened until SESSION-SELLR specification and development gate are frozen.

## 9. Component-level feature readiness

The historical feature list requires a fresh SESSION audit before implementation:

- intraday path family:
  `adverse_excursion`, `trend_strength`, `trend_close_location`,
  `session_against_trend`, `opposite_semivar_share`
  — conceptually reconstructable from governed pre-target XAU data;

- options family:
  `signed_opt_pressure`, `signed_d_opt_pressure`
  — must be proven source-ready for each session origin;

- cross-market family:
  `core_confirmation`, `cross_dispersion`
  — must be reconstructed from governed source-ready state;

- topology:
  `topology_rotation`
  — daily-state clock must be attached without multiple same-day state advancement;

- duration:
  `trend_age`
  — must be redefined as same-window SESSION momentum age.

No feature is accepted solely because it existed in the H3 panel.

## 10. Stage-1B verdict

| Question | Verdict |
|---|---|
| Original SELLR producer recovered? | **PASS** |
| Exact feature list recovered? | **PASS** |
| Exact scoring formula recovered? | **PASS** |
| Training chronology recovered? | **PASS** |
| Historical threshold provenance recovered? | **PASS** |
| Is historical SELLR horizon-independent? | **NO** |
| Can historical scores be reused in SESSION? | **FAIL / PROHIBITED** |
| Can historical 2.3677 threshold be reused? | **FAIL / PROHIBITED** |
| Can SELLR concept be rebuilt as SESSION-native successor? | **YES** |
| Is full DPTC Stage-2 ready now? | **NO** |

## 11. Correct next action

**DPTC Stage-1C — SESSION-SELLR V1 preregistration/readiness audit.**

That stage must:
- prove each of the eleven feature clocks;
- define same-window trend age;
- define whether per-window fitting or preregistered pooling is statistically feasible;
- define 2023–2024-only score fitting and catalyst-selection gate;
- keep 2025 fully closed.

Only after SESSION-SELLR V1 has a frozen pre-2025 identity may DPTC Stage-2 be opened.

