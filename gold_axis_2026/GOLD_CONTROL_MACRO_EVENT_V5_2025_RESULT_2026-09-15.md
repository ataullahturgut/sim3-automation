# GOLD CONTROL — MACRO EVENT V5 2025 CHALLENGE RESULT

**Date:** 2026-09-15  
**Research identity:** `MACRO_EVENT_SUCCESSOR_V5_PRE2025`  
**Evidence class:** `HISTORICAL_REPLAY_RECONSTRUCTION / RETROSPECTIVE_CHALLENGE`  
**Production write:** NONE

## 1. Clean-start statement

Before this V5 replay, all 2025 derived `MACRO_EVENT_%` rows in Neon were removed. The cleanup deleted **29 derived rows** from the prior Macro Event research layer:

- 11 Employment score rows;
- 10 Inflation score rows;
- 8 FOMC score rows.

The raw/reconstructed 2025 source inputs were intentionally retained because they are the independent challenge inputs. The V5 challenge runner fails closed if any pre-existing 2025 derived `MACRO_EVENT_%` row exists.

A post-run Neon check again returned **0** 2025 derived `MACRO_EVENT_%` rows. V5 wrote no result back to Neon.

The superseded V2 2025 audit PR was closed and its head branch was reset to the canonical base. It is not current model evidence.

## 2. Pre-2025 model freeze

V5 was designed and fit before opening its 2025 challenge inputs.

Frozen model file:

`gold_axis_2026/contracts/macro_event_v5_pre2025_model.json`

Frozen model payload SHA-256:

`651b2261823c358617fd752aa3458681b20cc2fb7dabdd3929852e9dc547f600`

Last training/design release timestamp:

`2024-12-18T19:00:00+00:00`

Formation history for robust scale/severity calibration:

`2016-01-01 .. 2024-12-31`

Gold direction reaction-fit window:

`2023-01-01 .. 2024-12-31`

No 2025 Macro Event output, volatility label or 2025 XAU reaction entered the fit.

## 3. Frozen V5 architecture

V5 separates two tasks that earlier Macro Event research coupled together.

### Shock intensity

For each native macro family:

`shock_intensity = mean(abs(standardized surprise components))`

Standardization is strictly prior-only robust MAD with deterministic IQR fallback.

Family-specific severity tiers are frozen from the pre-2025 distribution:

- NORMAL: below Q75;
- ELEVATED: Q75 to below Q90;
- HIGH: Q90 or above.

Primary warning tier: **HIGH**.

### Gold direction

Direction is not imposed by equal fixed weights. It is estimated separately for Employment, Inflation and scheduled FOMC from the pre-2025 15-minute XAU reaction:

`R15 = alpha + beta' z + error`

where:

`R15 = 100 * ln(XAU(release+14m) / XAU(release-1m))`

FOMC retains separate target and path surprise factors.

## 4. Pre-2025 direction support

| Family | R15 fit events | Leave-one-out sign accuracy |
|---|---:|---:|
| Employment | 23 | 86.96% |
| Inflation | 24 | 70.83% |
| Scheduled FOMC | 16 | 93.75% |

These small-sample diagnostics are descriptive and are not promotion proof.

## 5. Complete 2025 Macro Event timeline accounting

V5 was first run on every eligible 2025 native Macro Event origin, without access to the frozen 19 volatility dates as model inputs.

Eligible 2025 macro origins: **29**

- Employment: **11**
- Inflation: **10**
- scheduled FOMC: **8**

Severity outputs:

- NORMAL: **26**
- ELEVATED: **2**
- HIGH: **1**

Primary HIGH warning dates:

- **2025-04-10 — Inflation — HIGH — predicted UP**

Secondary ELEVATED dates:

- 2025-02-12 — Inflation — ELEVATED — predicted DOWN;
- 2025-06-11 — Inflation — ELEVATED — predicted UP.

Frozen 2025 engine-timeline SHA-256:

`88286d169b7d55f70bbc97cd65090b692655274637be233f199b8bad33e21f6a`

## 6. Overlay with the independently frozen 19 volatility event-days

The volatility inventory was overlaid only after the 29-event Macro timeline had been produced and hashed.

Only **3 / 19** frozen volatility event-days had a native Macro Event origin on the same New York calendar date:

| Date | Volatility event | Native macro family | V5 intensity tier | V5 direction | Primary result |
|---|---|---|---|---|---|
| 2025-04-04 | DOWN / EXTREME | Employment | NORMAL | DOWN | `NO_SIGNAL` |
| 2025-04-10 | UP / MAJOR | Inflation | **HIGH** | **UP** | `SAME_EVENT_HIGH_DIRECTION_MATCH` |
| 2025-08-01 | UP / MAJOR | Employment | NORMAL | UP | `NO_SIGNAL` |

The remaining **16 / 19** volatility dates are `NOT_APPLICABLE` for this native event-clock engine.

Primary challenge accounting:

- volatility event-days: **19**;
- macro-applicable volatility dates: **3**;
- NOT_APPLICABLE: **16**;
- HIGH same-event signals: **1**;
- HIGH same-event direction matches: **1**;
- applicable volatility dates with no primary HIGH signal: **2**;
- HIGH warnings on non-volatility macro dates: **0**.

The direction head happened to align with the daily volatility direction on all three macro-applicable dates (DOWN on 4 April, UP on 10 April, UP on 1 August), but only 10 April exceeded the preregistered HIGH shock-intensity threshold. This 3/3 direction observation is based on only three applicable challenge dates and is therefore **INSUFFICIENT_SUPPORT** for a general direction-performance claim.

## 7. Timing interpretation

Macro Event V5 is not a day-ahead predictor. Actual-minus-consensus surprise becomes observable at the scheduled release itself.

Therefore the 2025-04-10 result is correctly interpreted as:

**same-event / release-time warning**, not an advance-day warning.

No 1/3/5/10-day carry-forward was used. The ELEVATED 12 February signal is not retrospectively credited to the 14 February volatility event.

## 8. Interpretation

V5 fixes the main methodological defect identified in the earlier design: large opposite-signed surprises can no longer cancel in the severity head, and direction is learned independently from pre-2025 gold reactions instead of being defined by equal fixed signs/weights.

For the frozen 2025 challenge:

- the model generated one primary HIGH warning;
- that warning coincided with a frozen volatility event and its direction matched;
- it produced zero primary HIGH false warnings;
- it did not issue a primary warning on two other macro-applicable volatility dates;
- most daily volatility dates were outside the native Macro Event clock.

This is **PROMISING BUT NOT PROVEN**. The sample of applicable 2025 volatility dates is only three, and the historical consensus timestamps remain reconstruction rather than proven prospective captures.

V5 therefore remains a research successor. It should not be represented as a generic daily volatility detector or as a proven replacement until additional later/prospective evidence exists.

## 9. Reproducibility

Preregistration:

`gold_axis_2026/GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V5_PRE2025_PREREG_2026-09-15.md`

Core:

`gold_axis_2026/tools/macro_event_v5_core.py`

Pre-2025 fit runner:

`gold_axis_2026/tools/run_macro_event_v5_fit_pre2025.py`

2025 challenge runner:

`gold_axis_2026/tools/run_macro_event_v5_2025_challenge.py`

Frozen model:

`gold_axis_2026/contracts/macro_event_v5_pre2025_model.json`

Dedicated pre-2025 fit workflow: PASS.  
Dedicated 2025 challenge workflow: PASS.

No production/decision write occurred.
