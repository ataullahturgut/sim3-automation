# GOLD CONTROL — 2025 MACRO EVENT V2 FULL-TIMELINE REPLAY PREREGISTRATION

**Date:** 2026-09-15  
**Engine:** `MACRO_EVENT_SUCCESSOR_V2`  
**Challenge:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_V1`  
**Evidence class:** `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`  
**Status:** FROZEN BEFORE 2025 V2 SCORE OUTPUTS ARE INSPECTED IN THIS REPLAY

## 1. Purpose

This preregistration freezes the 2025 evaluation procedure for the governed Macro Event identity before its 2025 states are computed/inspected for the volatility challenge.

The evaluation direction is binding:

> run the engine first on every eligible 2025 native event-clock origin -> retain every engine output -> freeze that output table -> only then overlay the independently frozen 19 daily volatility event-days.

The volatility event list is not an input to the Macro Event engine and may not affect its inputs, score, thresholds, state mapping, event inclusion or output timing.

## 2. Identity decision

The 2025 challenge uses **`MACRO_EVENT_SUCCESSOR_V2`**, because it is the current governed runtime identity in the project manifest and its formula was frozen before this 2025 volatility replay.

`MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE` is explicitly excluded from this challenge identity because:

- it is a research challenger, not governed runtime authority;
- its own preregistration states that 2025 retrospective results were already inspected during method development;
- using it as a supposedly untouched 2025 engine would violate the challenge freeze.

Stored V3 research-family outputs may be audited separately but do not replace V2 in this governed 12-engine challenge.

## 3. Frozen V2 inputs and formula

Use the existing V2 implementation and its frozen source run only:

`6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`

Six source series:

- `MACRO_NFP_ACTUAL_FIRST_PRINT`
- `MACRO_NFP_CONSENSUS_PIT`
- `MACRO_UNEMP_ACTUAL_FIRST_PRINT`
- `MACRO_UNEMP_CONSENSUS_PIT`
- `MACRO_AHE_ACTUAL_FIRST_PRINT`
- `MACRO_AHE_CONSENSUS_PIT`

Raw surprise is `actual - consensus`.

For each component, scale uses only prior complete-case events:

1. median of prior surprises;
2. `1.4826 * MAD` as primary robust scale;
3. deterministic normal-calibrated IQR fallback when MAD is zero/non-finite;
4. no classical-standard-deviation fallback;
5. minimum 24 prior complete cases.

Gold orientation remains:

- NFP: `-z_nfp`
- unemployment: `+z_unemp`
- AHE: `-z_ahe`

Composite remains equal-weight mean of the three gold-oriented standardized surprises.

State mapping remains frozen:

- `GOLD_ADVERSE_MACRO_SHOCK` if score `<= -1.0` and adverse breadth `>= 2`;
- `GOLD_SUPPORTIVE_MACRO_SHOCK` if score `>= +1.0` and supportive breadth `>= 2`;
- otherwise `MACRO_MIXED_OR_SMALL`.

No formula, weight, sign, scale, threshold or breadth rule may be changed after 2025 outputs are viewed.

## 4. Native event clock and 2025 eligibility

V2 is an **Employment Situation release-time engine**, not a daily continuously-issued warning engine.

Eligible 2025 origins are all official Employment Situation releases whose actual release timestamp falls in calendar year 2025 and for which the six frozen V2 source rows exist.

Release time is the governed official `08:30 America/New_York` timestamp stored in the source lineage.

The official BLS 2025 lapse schedule is authoritative for the exceptional late-year chronology:

- September 2025 Employment Situation was released 2025-11-20 at 08:30 ET;
- October 2025 Employment Situation was **canceled**;
- November 2025 Employment Situation was released 2025-12-16 at 08:30 ET.

A canceled official release is not a data-imputation opportunity. It creates no V2 event origin and may not be synthesized.

## 5. Point-in-time limitation

The consensus rows are historical reconstruction from a provider `Forecast` field. Their metadata explicitly records:

`provider_exact_pre_release_update_timestamp_proven = false`

and classifies them as `HISTORICAL_REPLAY_RECONSTRUCTION`.

Therefore:

- V2 may be evaluated as retrospective reconstructed event-surprise evidence;
- it may **not** be relabelled as a genuinely issued/prospective 2025 signal;
- the exact historical pre-release provider update time remains `NOT_PROVEN`;
- this limitation must appear in every result table/report.

No backdating is permitted.

## 6. Full-output requirement

Before looking at the frozen volatility events, the replay must emit one row for **every eligible 2025 Macro Event origin**, including:

- reference month;
- official release date/time;
- V2 score;
- breadth;
- V2 state;
- signal role;
- source/PIT limitation;
- all scale methods/required lineage checks.

All strong and non-strong outputs are retained.

`MACRO_MIXED_OR_SMALL` is `NO_SIGNAL`, not silently deleted.

There is no daily carry-forward alarm. Macro Event evidence is event-local unless a separately preregistered persistence rule is later created.

## 7. Volatility-overlay rule — frozen before V2 2025 outputs

Only after the complete 2025 V2 event-clock table is frozen may the 19-event volatility inventory be joined.

### Primary role-preserving match

The primary match is **same New York calendar date** only.

Reason: V2 surprise evidence first exists at the macro release time itself. The macro-event literature documents rapid intraday gold reaction to U.S. macro surprises, especially 08:30 announcements and nonfarm payrolls. V2 is therefore event-time evidence, not a multi-day forecast that should be carried forward until an unrelated later volatility day.

Classification:

- strong V2 state on a frozen volatility event date -> `SAME_EVENT_SIGNAL`;
- if strong direction equals the daily event direction, additionally `DIRECTION_ALIGNED`;
- if strong direction opposes it, additionally `DIRECTION_OPPOSED`;
- eligible release date but V2 is mixed/small -> `NO_SIGNAL`;
- strong V2 state on a release date that is not a frozen volatility event date -> `FALSE_WARNING_FOR_DAILY_VOLATILITY_CHALLENGE`;
- frozen volatility date with no Employment Situation release -> `NOT_APPLICABLE`, never an automatic Macro Event miss.

No arbitrary 1/3/5/10-day carry-forward window is permitted for the primary Macro Event evaluation.

### Timing interpretation

A same-day V2 signal is available at **08:30 ET**, after the actual macro announcement arrives. It is not a day-ahead volatility forecast.

If a daily volatility event is same-day, report the Macro signal as event-time evidence. Do not call it `EARLY_HIT` unless an independently frozen pre-release signal exists, which V2 does not provide.

## 8. Intraday reaction diagnostic

For every eligible 2025 release, where data exist, also compute the already-governed event-study reaction without changing V2:

- `P0` = close of the 08:29 one-minute bar;
- `P15` = close of the 08:44 one-minute bar;
- `R15 = 100 * (P15/P0 - 1)`.

Expected direction:

- adverse macro shock -> `R15 < 0`;
- supportive macro shock -> `R15 > 0`.

This intraday reaction diagnostic tests the native event-time directional role and is kept distinct from the daily volatility challenge.

No alternate reaction window may replace R15 after results are observed.

## 9. Data/source gates

Replay fails closed if any of the following occurs:

- frozen source run missing/invalid;
- source row count or complete-case contract drifts;
- any eligible 2025 release lacks all six V2 rows;
- duplicate source rows;
- official release timestamp is inconsistent with lineage;
- current-event surprise enters its own historical robust scale;
- prefix invariance fails;
- deterministic replay fails;
- required R15 bars are duplicated or invalid;
- any production forecast/decision/runtime row is written.

Missing R15 bars block only that reaction diagnostic; they may not alter the V2 macro state.

## 10. Literature basis

Methodological anchors:

- Christie-David, Chaudhry & Koch (2000), *Journal of Economics and Business*, 52(5), 405-421, DOI `10.1016/S0148-6195(00)00029-1`: intraday gold responses differ across macro release types; unemployment and inflation-related announcements materially affect gold.
- Elder, Miao & Ramchander (2012), *Journal of Banking & Finance*, 36(1), 51-65, DOI `10.1016/j.jbankfin.2011.06.007`: metal-futures responses to U.S. macro surprises are swift; 08:30 announcements, especially nonfarm payrolls, are particularly influential; unexpectedly stronger economic news tends to be negative for gold.
- The V2 robust normalization uses standard robust scale estimators (normal-calibrated MAD with deterministic IQR fallback) strictly on prior events to resist extreme-outlier scale distortion while preserving actual-minus-consensus economic zero.

The literature supports event-time surprise analysis. It does not justify pretending V2 is a day-ahead volatility predictor.

## 11. Anti-hindsight lock

After 2025 V2 outputs are inspected, this replay identity may not change:

- engine version;
- input series/provider/source run;
- robust-scale estimator;
- score signs/weights;
- thresholds/breadth;
- eligible release set;
- same-day primary volatility overlay rule;
- R15 primary reaction window;
- treatment of canceled/missing release origins.

Any revised design requires a separately named successor and may not overwrite this replay.
