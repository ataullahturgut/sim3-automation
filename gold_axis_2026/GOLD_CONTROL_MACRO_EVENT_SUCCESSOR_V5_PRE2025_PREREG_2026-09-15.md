# GOLD CONTROL — MACRO EVENT SUCCESSOR V5 PRE-2025 PREREGISTRATION

**Date:** 2026-09-15  
**Research identity:** `MACRO_EVENT_SUCCESSOR_V5_PRE2025`  
**Status:** FROZEN BEFORE THE NEW V5 2025 REPLAY  
**Evidence class:** HISTORICAL_REPLAY_RECONSTRUCTION  
**Production authority:** NONE

## 1. Purpose

V5 replaces the methodological coupling in earlier Macro Event research that used one signed composite both as a gold-direction score and as a proxy for event severity. The V5 design separates two different questions:

1. **Shock intensity:** how unusual/large is the macroeconomic surprise at the release?
2. **Gold direction:** conditional on the released surprises, what immediate gold return direction is supported by pre-2025 gold reaction evidence?

The 2025 Gold Control volatility inventory is not an input to either head and may not be used for threshold, feature, coefficient or event-family selection.

## 2. Authority basis

The design follows the event-study literature in these respects:

- macroeconomic news is defined as the divergence between the released value and the pre-release market expectation (`actual - consensus`);
- surprises are standardized to permit comparison across indicators;
- volatility/severity uses the **absolute magnitude** of standardized surprise components so opposite-signed large surprises cannot cancel;
- gold response is measured in a short high-frequency window around scheduled announcements;
- direction effects are estimated from gold's historical high-frequency reaction rather than imposed as universal equal-weight signs;
- FOMC information is multi-dimensional and retains separate target/path components.

Key authority references include Andersen, Bollerslev, Diebold & Vega (2003), Christie-David, Chaudhry & Koch (2000), Elder, Miao & Ramchander (2012), Smales & Yang (2015), and Gürkaynak, Sack & Swanson (2005).

## 3. Clean-design cutoff and formation history

All V5 design, scale estimation, severity calibration and direction fitting must use observations with release timestamp strictly before:

`2025-01-01T00:00:00Z`

The common event-history start for all three families is:

`2016-01-01T00:00:00Z`

Thus V5 scale/severity history is **2016-01-01 through 2024-12-31** for Employment, Inflation and scheduled FOMC alike. Earlier FOMC factor observations remain source evidence but are not used in V5 calibration.

The fit runner must fail closed if a training/design query returns any release timestamp in 2025 or later.

2025 derived Macro Event scores from earlier research are not eligible inputs. In fact, **no derived `MACRO_EVENT_V3_*`, V4 or V2 score series may be used as a V5 predictor or training target**.

## 4. Frozen source lineage and event families

V5 uses only governed raw/reconstructed source channels and fixed source runs already available before the new V5 challenge replay.

### Employment

Frozen source run: `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`

- `MACRO_NFP_ACTUAL_FIRST_PRINT`
- `MACRO_NFP_CONSENSUS_PIT`
- `MACRO_UNEMP_ACTUAL_FIRST_PRINT`
- `MACRO_UNEMP_CONSENSUS_PIT`
- `MACRO_AHE_ACTUAL_FIRST_PRINT`
- `MACRO_AHE_CONSENSUS_PIT`

Raw surprises:

- `e_nfp = actual - consensus`
- `e_unemp = actual - consensus`
- `e_ahe = actual - consensus`

### Inflation

Frozen source run: `1e96b5ac-3d44-472b-b6fd-d5d6558181a6`

- `MACRO_CPI_ACTUAL_FIRST_PRINT`
- `MACRO_CPI_CONSENSUS_PIT`
- `MACRO_CORE_CPI_ACTUAL_FIRST_PRINT`
- `MACRO_CORE_CPI_CONSENSUS_PIT`

Raw surprises:

- `e_cpi = actual - consensus`
- `e_core_cpi = actual - consensus`

### FOMC

Frozen source run: `2f86f5d7-9800-4fe2-880c-48d6b84ff755`

Use the governed pre-existing high-frequency monetary-policy surprise channels:

- `MACRO_FOMC_GSS_TARGET_FROZEN2015`
- `MACRO_FOMC_GSS_PATH_FROZEN2015`

Target and path remain separate components. V5 does not collapse the FOMC event into a target-only shock.

**Only scheduled FOMC observations (`metadata.unscheduled = 0`) are eligible in V5 formation and challenge.** Emergency/unscheduled actions are a different event class and may not be mixed into the scheduled-event calibration.

## 5. Prior-only robust standardization

For each family/component at event `t`, scale is estimated from **strictly prior** same-component events only within the common 2016-2024 event history.

Minimum prior events: **24**.

Primary scale:

`scale = 1.4826 * MAD(prior values)`

If the scaled MAD is zero/non-finite, use:

`scale = IQR(prior values) / 1.3489795003921634`

If neither scale exists, the event is `INSUFFICIENT_HISTORY`.

No current event enters its own scale. No future event enters any earlier origin.

Standardized surprise:

`z_i = e_i / scale_i`

For FOMC, `e_i` is the existing target/path surprise factor itself.

## 6. Shock-intensity head

For a scored event with `k` standardized surprise components:

`shock_intensity = mean(abs(z_i))`

This is intentionally unsigned. Opposite-signed large surprises do not cancel.

Severity thresholds are calibrated only from each family's scored 2016-2024 `shock_intensity` distribution:

- `NORMAL`: below family Q75;
- `ELEVATED`: Q75 <= intensity < Q90;
- `HIGH`: intensity >= family Q90.

Primary Macro Event warning onset is `HIGH`. `ELEVATED` is retained as a secondary watch state and may not be relabelled a primary warning after viewing 2025.

Quantiles use deterministic linear interpolation.

## 7. Gold-direction head

Direction is not hard-coded with equal component weights.

For each family separately, fit a low-dimensional ordinary least squares event-study regression on pre-2025 events with complete 15-minute XAU reaction data:

`R15_t = alpha + beta' z_t + epsilon_t`

where:

`R15 = 100 * ln(XAU_{release+14min} / XAU_{release-1min})`

The available clean reaction-cache window for this fit is **2023-01-01 through 2024-12-31**. No 2025 reaction is eligible for fitting.

Family feature dimensions:

- Employment: 3 standardized surprise components;
- Inflation: 2;
- FOMC: 2.

No interaction terms, nonlinear terms, post-result feature dropping, LASSO search, hyperparameter search or threshold search are allowed in V5.

The predicted direction is:

- `UP` if predicted `R15 > 0`;
- `DOWN` if predicted `R15 < 0`;
- `FLAT` only for exact numerical zero.

Because the reaction sample is limited, direction must carry training support count and a pre-2025 leave-one-out sign-accuracy diagnostic. This diagnostic is descriptive and cannot change the V5 formula after the 2025 replay.

## 8. Event output

Every eligible event produces, where history is sufficient:

- event family;
- release timestamp;
- raw surprises;
- prior-only robust scales;
- standardized surprises;
- `shock_intensity`;
- severity tier (`NORMAL`, `ELEVATED`, `HIGH`);
- predicted R15;
- predicted direction;
- direction fit support count;
- pre-2025 leave-one-out sign accuracy for that family;
- evidence/PIT limitations.

V5 does not carry an event signal forward to later days.

## 9. 2025 challenge rule

Only after the V5 pre-2025 model parameters and severity thresholds are frozen may the 2025 source inputs be read.

The 2025 engine replay must:

1. run on **all eligible 2025 Employment, Inflation and scheduled-FOMC origins**;
2. retain every event output, including NORMAL/ELEVATED/HIGH;
3. freeze that complete event timeline;
4. only then overlay the independent 19-day Gold Control volatility inventory;
5. use same-New-York-calendar-date matching as the primary event-clock comparison;
6. report HIGH warnings on non-volatility dates as false-warning burden for the daily-volatility challenge;
7. report volatility days without a native macro event as `NOT_APPLICABLE`, not Macro misses;
8. report eligible volatility days with no HIGH warning as `NO_SIGNAL` for the primary warning tier;
9. retain ELEVATED results as secondary sensitivity only.

No 1/3/5/10-day carry-forward window is permitted for Macro Event V5.

## 10. PIT limitation

Historical consensus rows whose exact provider pre-release update timestamp is not proven remain `HISTORICAL_REPLAY_RECONSTRUCTION`. They may be used for retrospective research but may not be described as genuinely issued prospective signals.

## 11. Promotion rule

V5 is a research successor, not automatically a governed runtime replacement for V2. Promotion requires:

- successful fail-closed implementation;
- reproducible pre-2025 fit;
- complete 2025 engine-first replay;
- explicit comparison with the frozen 19-event volatility challenge;
- no post-2025 retuning under the V5 identity;
- later prospective evidence for any production claim.
