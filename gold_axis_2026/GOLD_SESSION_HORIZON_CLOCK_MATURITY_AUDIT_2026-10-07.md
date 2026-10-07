# GOLD SESSION — HORIZON / CLOCK / MATURITY AUDIT

**Date:** 2026-10-07  
**Status:** **COMPLETE / NO LEGACY-HORIZON CONTAMINATION FOUND**

## Objective

Audit all completed SESSION model families for accidental reuse of the legacy DAILY/H3 target horizon or H3 timing/state assumptions.

The audit asks four binding questions for every model family:

1. **Target identity:** is the scored target the corrected V5 SESSION `start_utc -> end_utc` direction rather than a legacy DAILY/H3 label?
2. **Feature clock:** is every predictive input available by the relevant session start, with no target-window observation used?
3. **Maturity:** are training/adaptive outcomes admitted only after the prior target has matured, i.e. `end_utc <= current start_utc`?
4. **State isolation:** where adaptive state exists, is it separated by `(partition, window)` rather than pooled across incompatible session horizons?

## Overall verdict

**No completed SESSION model was found to score or train directly against a legacy DAILY/H3 outcome while presenting the result as SESSION evidence.**

**No completed SESSION model was found to update its training/router state from a still-open target window.**

Historical H3 code/files are used only as algorithmic lineage references where explicitly documented; historical H3 prediction/state outputs are not silently substituted for SESSION outcomes in the audited active implementations.

The principal boundary nuance is PATH_GLOBAL's completed-hour rule, documented below. It is not classified as leakage or a horizon error.

## Family-by-family verdict

| Family | Target | Feature clock | Maturity/state | Legacy H3 contamination | Verdict |
|---|---|---|---|---|---|
| Model-01 CORE3 Logistic | V5 SESSION | prior NY calendar date only | same-window `end_utc <= cutoff` | none | **PASS** |
| Model-01B selected Logistic | V5 SESSION | daily D-1 + XAU15 strictly before start | same-window matured | none | **PASS** |
| Model-02 Shallow CART | V5 SESSION | all daily features D-1 or older | nested + outer matured | none | **PASS** |
| Model-03 NOVA A1/ARCR | V5 SESSION | daily D-1 | same-window matured; recent 252 matured rows | none | **PASS** |
| Model-03B selected A1 | V5 SESSION | XAU15 strictly before start | nested + outer matured | none | **PASS** |
| Model-04 PATH_GLOBAL | V5 SESSION | completed hourly close at/before start | same-window matured | none | **PASS — boundary note** |
| Model-04B selected PATH_GLOBAL | V5 SESSION | inherits completed-hour rule | nested + outer matured | none | **PASS — boundary note** |
| Model-05 STRUCTURAL_IRIS | V5 SESSION | XAU15/1H anchors strictly before start in canonical structural replay | same-window matured | none | **PASS** |
| Model-05B selected Structural | V5 SESSION | strict XAU15/1H pre-start anchors | nested + outer matured | none | **PASS** |
| Model-06 SAGE SESSION_ONLY | V5 SESSION | `sage_ready_utc < start_utc` | same-window matured | none | **PASS** |
| Model-07 SAGE PATH_SESSION | V5 SESSION | strict SAGE readiness + pre-target PATH | same-window matured | none | **PASS** |
| Model-08 SAGE A1_SESSION | V5 SESSION | fresh causal A1 + strict SAGE readiness | same-window matured | none | **PASS** |
| Model-09 SAGE A1_PATH_SESSION | V5 SESSION | fresh A1 + pre-target PATH + strict SAGE | same-window matured | none | **PASS** |
| RIFT | V5 SESSION reversal vs pre-target momentum | XAU15 strictly before start | monthly fit from matured same-window rows | none | **PASS** |
| VEGA | V5 SESSION reversal | pre-target XAU + GVZ dated no later than NY D-1 | matured same-window rows | none | **PASS** |
| SENTRY | V5 SESSION expert outcomes | consumes SESSION Structural/PATH forecasts | only matured pair outcomes | none | **PASS** |
| DART | V5 SESSION disagreement outcomes | consumes SESSION Structural/PATH forecasts | only matured disagreement rows | none | **PASS** |
| AURORA | V5 SESSION router | SESSION SENTRY/DART upstream | matured pair/disagreement state only | none | **PASS** |
| OPAL | V5 SESSION reversal | pre-target XAU + PIT COT available by start | monthly fit from matured rows | none | **PASS** |
| TURN | V5 SESSION correction | hourly anchor strictly before start | no target-window input | none | **PASS** |
| PRISM | V5 SESSION | hourly anchor strictly before start | monthly fit from matured rows | none | **PASS** |
| TWIN | V5 SESSION | hourly anchor strictly before start | same-window analogue memory only after maturity | none | **PASS** |
| AIM | V5 SESSION | fresh SESSION expert forecasts | decayed losses from matured exact-common rows | none | **PASS** |
| HELIOS V1-V5 | V5 SESSION correction/router | fresh SESSION upstream only | independent same-window matured event state | no H3 outputs used | **PASS implementation / NOT PROMOTED** |
| BOCPD V1 | V5 SESSION correction/meta-trust | exact session-start Handoff reconstruction | independent same-window matured alarm state | no H3 outcomes used | **PASS implementation / NOT PROMOTED** |

## Detailed findings

### 1. Model-01 / Model-03 daily-source models

These do **not** use the legacy daily/H3 direction as the target.

They join raw daily metal state to corrected V5 session rows and define the label from the session direction.

Because intraday publication timing of the daily Stak observations is not proven, the source-ready rule is deliberately conservative:

`daily_cutoff_date = NY session-start date - 1 calendar day`.

Therefore no same-day daily observation can enter a session forecast.

Training uses only same-window rows satisfying:

`end_utc <= first_start_of_current_block`.

**Verdict: PASS.**

### 2. Model-02 CART

CART uses corrected SESSION targets.

Gold, Silver, Platinum, Palladium, NASDAQ, S&P500 and DJIA daily features are all as-of the previous NY calendar date or earlier. The code explicitly raises a `SAME_DAY_FEATURE_LEAK` error if feature age is below one day.

Nested feature selection and outer replay both use matured targets only.

**Verdict: PASS.**

### 3. PATH_GLOBAL boundary convention

The original PATH_GLOBAL replay has:

`available_at_utc = hourly_bar_open_timestamp + 1 hour`

and selects the latest completed hourly close satisfying:

`available_at_utc <= session_start`.

Some windows therefore have median feature lag = 0 minutes.

This is **not the same as using the 15-minute target-start bar**.

For an hourly bar labeled by its opening time `T-1h`, availability at `T` means the bar covers the interval immediately **before** the target session and completes when the target begins. It does not contain `[T,T+1h)` target-window observations.

The 15-minute predictor rule remains stricter: a bar opening at `T` belongs to the target window and is rejected.

Therefore the PATH_GLOBAL equality convention is retained as an explicit **completed-bar boundary exception**, not classified as horizon leakage.

**Verdict: PASS — boundary convention must remain documented.**

### 4. Structural-IRIS and selected intraday models

The later structural/selected implementations use explicit pre-target XAU15/1H anchors and hard checks such as:

`anchor_available < start_utc`.

Training and nested selection use only matured outcomes.

No historical H3 Structural/IRIS prediction is used as the current target label.

**Verdict: PASS.**

### 5. SAGE family

SAGE creates completed market-cycle state and marks it ready at 16:15 New York.

Every model checks:

`sage_ready_utc < target_start`.

The current target session is never used to construct the SAGE cycle used for that target.

A1 and PATH branches are regenerated causally against SESSION targets; adaptive training uses matured same-window outcomes.

**Verdict: PASS.**

### 6. RIFT

RIFT correctly refused to transplant one historical H3 feature whose session-clock-safe meaning was not proven:

`session_against_trend`.

That feature was omitted rather than silently reused.

Its reversal label is explicitly:

`SESSION actual direction != pre-target 12h momentum direction`.

This is a correct SESSION-specific target.

**Verdict: PASS.**

### 7. VEGA / OPAL / TURN

VEGA:
- uses V5 SESSION reversal outcome;
- GVZ is held to an origin-safe D-1 rule.

OPAL:
- uses fresh SESSION AURORA;
- COT must satisfy `cot_available_at_utc <= start_utc`;
- reversal target is the current SESSION direction versus pre-target momentum.

TURN:
- merges hourly state with `allow_exact_matches=False`;
- verifies `available_at_utc < start_utc`.

**Verdict: PASS.**

### 8. SENTRY / DART / AURORA

These are true SESSION routers, not old H3 routers masquerading as SESSION evidence.

SENTRY uses only Structural/PATH paired rows whose session outcome has matured.

DART updates only on matured disagreement rows.

AURORA keeps the fast pair ledger and slow disagreement ledger causal and isolated by partition/window.

**Verdict: PASS.**

### 9. PRISM / TWIN / AIM

PRISM uses strict pre-target hourly anchors and matured monthly training.

TWIN uses only matured same-window analogue memory.

AIM regenerates PATH_RECENT126 from the last 126 matured same-window rows and computes adaptive expert losses only from matured exact-common forecasts.

**Verdict: PASS.**

### 10. HELIOS

HELIOS was correctly ported to SESSION clocks and fresh SESSION upstream outputs.

It failed because the historical event-count architecture became too sparse at SESSION granularity: the eight-candidate competence gate never filled.

That is an **architecture transport failure**, not a horizon/clock leakage failure.

**Verdict: implementation PASS / model NOT PROMOTED.**

### 11. BOCPD

BOCPD was rebuilt at the exact SESSION origin:
- Handoff inputs strictly pre-target where required;
- state independent by partition/window;
- prior alarm outcome enters posterior only after `end_utc <= current start_utc`.

It failed 2025 transport because the frozen posterior thresholds produced zero ACTs in the two eligible heads.

That is a **transport-performance failure**, not a horizon error.

**Verdict: implementation PASS / model NOT PROMOTED.**

## Important distinction: frozen specification vs frozen coefficients

Several 2025 SESSION transports are **frozen-specification causal replays**, not static-coefficient 31-Dec-2024 forecasts.

That means:
- model family/features/hyperparameters/thresholds are frozen before 2025;
- but prior **matured 2025 outcomes may enter later 2025 training/state updates** where the preregistered online model identity requires expanding/adaptive learning.

This is legitimate online transport and is not horizon leakage.

It must not be confused with a static-coefficient holdout test.

## Audit conclusion

### FAIL findings
**None.**

### REVIEW findings
**None requiring result invalidation.**

### Documented boundary nuance
**PATH_GLOBAL hourly completed-bar equality at session start.**  
Retained as valid because the bar ends at the target boundary and contains only pre-target interval information. This convention must not be generalized to bars that begin at the target start.

### Models requiring rerun because of horizon error
**None.**

The currently reported SESSION results for the audited completed families do not need to be discarded or rerun due to a DAILY/H3 horizon mismatch.

## Forward governance

Before DPTC, RTE, RC-RTE, SCR-RTE and STCR are run:

1. perform this same identity audit first;
2. translate any time-based H3 assumption into a SESSION-native meaning;
3. preserve event-based parameters only when the event definition itself remains valid under SESSION;
4. prohibit any historical H3 prediction/state file from serving as a SESSION target or adaptive outcome;
5. isolate adaptive state by partition/window;
6. require prior target maturity before state updates.

This audit does not claim that every model is predictive. It establishes only that the completed SESSION implementations are using the intended SESSION horizon and causal timing contract.
