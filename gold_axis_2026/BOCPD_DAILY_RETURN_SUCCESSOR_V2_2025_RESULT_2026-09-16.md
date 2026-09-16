# BOCPD Daily Return Successor V2 — 2025 retrospective result

**Identity:** `BOCPD_DAILY_RETURN_SUCCESSOR_V2_RESEARCH`  
**Evidence:** `HISTORICAL_REPLAY_RETROSPECTIVE_DIAGNOSTIC`  
**Runtime promotion:** `NOT_PROVEN`  
**Direction vote:** forbidden  
**Production writes:** none

## 1. Source and chronology

Research input is `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`, Twelve Data `XAU/USD`, daily research series derived from the 1h 16:00 America/New_York bar. It is research-only and is not the canonical exact-16:59 NY17 series.

Only ISO weekdays Monday-Friday are admitted.

- 2023: prior fit only.
- 2024: formation/internal validation and hazard selection only.
- 2025: locked retrospective challenge replay; no challenge outcome was used to select the hazard or state rule.

The engine consumes daily log returns `ln(P_t/P_t-1)`.

## 2. Model

The successor preserves the canonical Adams-MacKay BOCPD structure already used by `BOCPD_RETURN_SUCCESSOR_V1`:

- Normal-Inverse-Gamma posterior state;
- Student-t posterior predictive;
- constant geometric hazard;
- MAP run-length tracking.

The daily successor is nondirectional. A signal is issued when:

`current_MAP_run_length < previous_MAP_run_length + 1`

This is stored as `REGIME_CHANGE_CANDIDATE`.

No return-sign filter is used. `reset_fraction` is descriptive severity only and is not thresholded.

A completed date-t daily output is available only after the date-t bar is complete; it cannot be credited as an early warning for an event already realized during date t.

## 3. Formation-only hazard selection

Candidate expected run lengths were fixed before challenge replay: 20, 40, 60 and 120 governed trading days.

2024 prequential log predictive evidence:

| Expected run | 2024 log evidence | 2024 MAP-reset days |
|---:|---:|---:|
| 20 | 781.177736 | 59 |
| 40 | 783.264656 | 28 |
| 60 | 783.956508 | 21 |
| **120** | **784.476301** | **14** |

Selected formation-only setting: **120 governed trading days**, hazard `1/120`.

## 4. Complete 2025 signal inventory

The 2025 governed replay contains 255 weekday origins and **14 MAP-reset dates**:

| Date | Daily log return % | Previous MAP | Expected uninterrupted | Current MAP | Reset fraction |
|---|---:|---:|---:|---:|---:|
| 2025-02-13 | +0.8302 | 238 | 239 | 37 | 0.845188 |
| 2025-04-07 | -1.8654 | 274 | 275 | 2 | 0.992727 |
| 2025-04-10 | +2.9501 | 277 | 278 | 2 | 0.992806 |
| 2025-06-23 | +0.0101 | 53 | 54 | 5 | 0.907407 |
| 2025-06-26 | -0.1216 | 56 | 57 | 8 | 0.859649 |
| 2025-06-30 | +0.7570 | 58 | 59 | 20 | 0.661017 |
| 2025-07-02 | +0.4665 | 60 | 61 | 22 | 0.639344 |
| 2025-09-03 | +0.6438 | 66 | 67 | 7 | 0.895522 |
| 2025-09-08 | +1.4153 | 69 | 70 | 10 | 0.857143 |
| 2025-10-08 | +1.4646 | 91 | 92 | 32 | 0.652174 |
| 2025-10-13 | +2.4512 | 94 | 95 | 35 | 0.631579 |
| 2025-10-16 | +3.0313 | 37 | 38 | 9 | 0.763158 |
| 2025-11-27 | -0.1409 | 38 | 39 | 8 | 0.794872 |
| 2025-12-29 | -4.5237 | 29 | 30 | 1 | 0.966667 |

These dates are the primary engine-first record. They were not filtered by the 19-event volatility inventory.

## 5. Volatility overlay after signal freeze

Four of the 14 reset dates were themselves frozen volatility-event dates and therefore are **same-day confirmations, not early warnings**:

- 2025-04-10
- 2025-10-13
- 2025-10-16
- 2025-12-29

Looking from engine signal to the next frozen event, without declaring a winning warning horizon:

- 2025-02-13 -> 2025-02-14, lead 1 governed day;
- 2025-04-07 -> 2025-04-09, lead 2 governed days;
- 2025-09-08 -> 2025-09-22, lead 10 governed days;
- 2025-10-08 -> 2025-10-13, lead 3 governed days;
- four reset dates are same-day event confirmations;
- the remaining six reset dates have no frozen event within the next 10 governed days.

Because no warning-validity horizon was preregistered, the 1/3/5/10-day relations are descriptive sensitivity only and are not precision, recall or false-warning rates.

Event-conditioned backward diagnostics show prior reset distances of 1-10 governed days for 9 of 19 event-days, but this count may not be represented as alarm accuracy. Several events occur inside clusters whose earlier reset was itself triggered by another event.

## 6. Interpretation

This daily successor has **real early-warning examples**, notably:

- 2025-02-13 before 2025-02-14;
- 2025-04-07 before 2025-04-09;
- 2025-10-08 before the 2025-10-13/16/17/21 stress cluster.

However it is not a general abnormal-volatility predictor. It also produces resets with no nearby frozen event and several important events are detected only on the same day or have no recent reset.

Current status: **PROMISING AS REGIME-CONTEXT / INSUFFICIENT_SUPPORT FOR PROMOTION**.

The result supports testing a separately named intraday BOCPD challenger if earlier warning is required. It does not authorize changing this daily model after inspecting 2025.

## 7. Superseded prototype note

During implementation, an exploratory query used a noncanonical change-probability construction. Comparison against the repository's authoritative `BOCPD_RETURN_SUCCESSOR_V1` implementation showed that the project BOCPD contract uses MAP run-length reset semantics. The exploratory change-probability result was discarded before being accepted as project evidence and is not authoritative.
