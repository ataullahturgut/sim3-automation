# GOLD D1 — FORECAST CLOCK RECONCILIATION

**Date:** 2026-10-06  
**Status:** GOVERNANCE CORRECTION / RETROSPECTIVE DIAGNOSTIC  
**Purpose:** prevent future mixing of label-time accuracy with executable post-signal accuracy.

## 1. What we learned

The historical CIG-D1 result and the execution study use different time semantics.

The historical CIG-D1 label asks whether the governed daily Gold reference moved UP or DOWN from the prior reference to the current reference. That label can include price movement occurring **before** the current-day signal is formally available.

The governed prospective issue deadline for the H3/CIG chain is:

- **08:00 America/New_York on forecast issue date**
- approximately **15:00 Europe/Istanbul** while New York is on daylight time
- approximately **16:00 Europe/Istanbul** while New York is on standard time.

Therefore the historical label accuracy must not be described as "accuracy from 08:00 New York onward."

## 2. Forecast-clock timeline

For a normal issue:

1. H3 hourly feature anchor: **16:00 New York on feature_cutoff_date**.
2. Full-UTC-day daily reference completes at the next UTC midnight:
   - **03:00 Europe/Istanbul**
   - approximately 20:00 New York in EDT / 19:00 New York in EST.
3. The daily-reference completion time is only a **theoretical lower bound** for readiness. It does not prove that every external source required by every expert was already available.
4. Governed issue deadline: **08:00 New York on issue date** = approximately **15:00/16:00 Istanbul**.
5. Retrospective historical rows do **not** contain a real `issued_at_utc` timestamp.

Consequently, for historical retrospective rows the exact historical production time is unknown. Under governance, execution claims must use the 08:00 New York deadline unless an earlier source-ready timestamp is separately proven.

## 3. Fifteen-minute clock reconciliation

Authoritative data:
- `GOLD_FORECAST_CLOCK_RECONCILIATION_2026-10-06.json`
- `GOLD_FORECAST_CLOCK_RECONCILIATION_ROWS_2026-10-06.csv`

Scope:
- reconstructed raw 4/4 CIG execution panel
- 2025-07-01 through 2026-09-25
- XAU/USD 15-minute prices.

Three intervals were separated:

- **THEORETICAL-READY -> 08:00 NY**
- **08:00 NY -> 20:00 NY**
- **THEORETICAL-READY -> 20:00 NY**

### Direction accuracy against the 08:00 -> 20:00 executable interval

| Period | N | Raw 4/4 signal accuracy |
|---|---:|---:|
| 2025 H2 | 111 | **50.45%** |
| 2026 Jan-Jul | 131 | **51.15%** |
| 2026 Aug-Sep | 26 | **42.31%** |

UP-only post-08:00 hit:
- 2025 H2: **55.56%**
- 2026 Jan-Jul: **50.68%**
- 2026 Aug-Sep: **44.44%**

DOWN-only post-08:00 hit:
- 2025 H2: **41.03%**
- 2026 Jan-Jul: **51.72%**
- 2026 Aug-Sep: **37.50%**

Interpretation:
the strong historical CIG label score does **not** automatically imply strong full-session post-08:00 direction accuracy.

## 4. Critical population mismatch

The canonical CIG-D1 result reports for 2026 Jan-Jul:
- common daily evaluation universe: **145**
- 4/4 consensus: **125**
- correct: **93**
- historical label accuracy: **74.40%**.

The execution timing reconstruction currently contains:
- 151 issue dates in Jan-Jul
- 131 reconstructed raw 4/4 consensus dates.

Therefore **131 is not the exact canonical 125-date CIG population**.

This means:
- the 51.15% post-08:00 result is a valid diagnostic for the reconstructed raw execution panel;
- it must **not** be presented as a direct re-score of the exact canonical 125 CIG observations;
- the exact canonical row-level CIG ledger must be recovered/reconstructed before a final apples-to-apples 74.40% vs post-08:00 comparison is published.

Until that reconciliation is completed, both metrics must remain separately named.

## 5. Superseded interpretations

The following statements are now prohibited:

- "CIG-D1 is 74.4% accurate after 08:00 New York."
- "The reported historical actual move is the return available after the signal."
- "The H3 target return begins when the forecast is issued."
- "The full historical daily move could have been traded using the current-day signal."
- "Theoretical daily-reference readiness at 03:00 Istanbul is the proven actual historical signal time."

Correct replacements:

- **74.40% = historical daily-label accuracy on the canonical 125 consensus observations.**
- **08:00->20:00 metrics = executable-clock diagnostics on a separate reconstructed timing population.**
- **03:00 Istanbul = theoretical lower-bound readiness from the daily-reference clock only.**
- **15:00/16:00 Istanbul = governed 08:00 New York issue deadline.**
- **Historical actual issuance timestamp = unknown unless explicitly recorded.**

## 6. Relationship to late-US timing finding

The weak 08:00->20:00 full-session direction result does not automatically invalidate the separate late-US UP-window finding.

The late-US finding asks a narrower question:

> conditional on an UP signal, is there a repeatable positive price interval later in the US session?

That is a different target from:

> is the entire 08:00->20:00 interval UP?

The late-US timing result therefore remains a diagnostic hypothesis, but it must not be used to restore or reinterpret the 74.40% historical label accuracy.

## 7. Binding next step

Before any final execution claim:

1. recover or reproduce the exact **145-row canonical D1 evaluation universe**;
2. reproduce the exact **125 consensus rows** and **93 correct** historical-label result;
3. join those same 125 dates to the 15-minute XAU/USD clock;
4. calculate post-08:00, next-issue, and late-US executable outcomes on **the identical rows**;
5. report label accuracy and executable-clock accuracy side by side.

No new model tuning is permitted during this reconciliation.


---

## 8. Resolution update — exact canonical 125 recovered

The exact canonical Jan-Jul population has now been recovered and the unresolved comparison in Section 4 is closed.

Authority:
`GOLD_CIG_EXACT_125_CLOCK_RESCORE_RESULT_2026-10-06.md`

Recovered source:
`GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`

Exact reproduction:
- universe 145
- consensus 125
- consensus correct 93
- historical daily-label accuracy 74.40%.

Exact same-125 post-issue diagnostic:
- 08:15->16:00 NY: 59/125 = **47.20%**
- 08:15->20:00 NY: 59/125 = **47.20%**
- 17:00->20:00 NY: 63/125 = **50.40%**.

Therefore the earlier 131-row post-08:00 diagnostic is superseded for the canonical Jan-Jul comparison.

The six rows absent from the old realization snapshot are 2026-02-27 and 2026-03-02 through 2026-03-06. Their absence was a frozen-data coverage gap, not a trading-clock definition.

**Final clock conclusion:** CIG-D1's historical 74.40% describes its date-labelled daily-reference target. It does not describe price direction after the 08:00 New York issuance deadline.
