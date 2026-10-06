# GOLD CIG-D1 — EXACT CANONICAL 125 CLOCK RESCORE

**Date:** 2026-10-06  
**Status:** RETROSPECTIVE CLOCK RECONCILIATION / CANONICAL SAMPLE RECOVERED  
**Identity:** `CIG_D1_V1_CLOCK_RESCORE_20261006`

## 1. Purpose

Reproduce the exact published 2026 Jan-Jul CIG-D1 population before making any claim about post-signal execution.

This resolves the prior population mismatch between:
- canonical CIG-D1: 145 daily rows / 125 consensus rows;
- reconstructed execution panel: 151 daily rows / 131 consensus rows.

No model parameter, threshold, vote member, or historical outcome is changed.

## 2. Canonical daily realization ledger recovered

Recovered source:
`GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`

Origin:
prior project artifact recovered from the user's ChatGPT Library.

The old frozen snapshot contains **145 Jan-Jul 2026 rows**.

Six dates present in later-clean data were absent from that old snapshot:
- 2026-02-27
- 2026-03-02
- 2026-03-03
- 2026-03-04
- 2026-03-05
- 2026-03-06

These are a historical snapshot coverage gap. They are **not** a trading-session or market-holiday rule.

## 3. Exact reproduction gate

Historical expert states were pinned to commit:
`fcbf50080afdf164dae460e8e855faf3f72bb1b0`

Reconstruction exactly reproduces every published canonical count:

| Metric | Published | Reconstructed |
|---|---:|---:|
| Daily universe | 145 | **145** |
| SAGE+RuleFlow correct | 103 | **103** |
| V5 correct | 102 | **102** |
| RIFT correct | 102 | **102** |
| VEGA correct | 102 | **102** |
| 4/4 consensus | 125 | **125** |
| Consensus correct | 93 | **93** |
| Consensus accuracy | 74.40% | **74.40%** |
| Disagreement | 20 | **20** |
| SAGE forced correct on disagreement | 10 | **10** |

**Gate: PASS.**

The exact canonical 125 signal rows are stored in:
`GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv`

## 4. Clock semantics

The recovered daily realization ledger is a **daily reference series**, not an executable intraday print.

Known historical source semantics:
- StakTrakr historical `observation_ts` at 00:00 UTC is a **date label**, not an instant that should be converted to New York time.
- The daily semantic audit supports a full-UTC-day/daily-reference interpretation.
- Therefore the historical D1 label does not have an executable buy/sell timestamp.

Operational forecast governance:
- hourly H3 feature anchor: 16:00 America/New_York on feature-cutoff date;
- governed issue deadline: **08:00 America/New_York** on issue date;
- 08:00 NY is approximately **15:00 Istanbul** during US daylight time and **16:00 Istanbul** during US standard time.

Thus the 74.40% historical score is **daily-reference label accuracy**, not accuracy from 08:00 NY onward.

## 5. Exact same-125 post-issue rescore

The same exact 125 canonical consensus rows were joined to XAU/USD 15-minute prices.

To avoid using the 08:00 bar open as post-signal information, the first execution timestamp is **08:15 New York**.

### 08:15 -> 16:00 New York

- all consensus: **59/125 = 47.20%**
- UP signals: **34/71 = 47.89%**
- DOWN signals: **25/54 = 46.30%**

### 08:15 -> 20:00 New York

- all consensus: **59/125 = 47.20%**
- UP signals: **34/71 = 47.89%**
- DOWN signals: **25/54 = 46.30%**

### 17:00 -> 20:00 New York

- all consensus: **63/125 = 50.40%**
- UP signals: **35/71 = 49.30%**
- DOWN signals: **28/54 = 51.85%**

These are retrospective gross XAU/USD direction diagnostics. They are not prospective evidence and not instrument-specific net returns.

## 6. Interpretation

The exact canonical reconciliation changes the execution interpretation materially.

The published **74.40%** result is genuine and exactly reproducible **for its original daily label**.

However, on the same 125 signal rows, the signal does **not** retain comparable directional accuracy once the outcome is measured only after the governed 08:00 NY issuance clock.

Therefore:

- CIG-D1 V1 is proven as a selective classifier of the historical daily-reference label;
- it is **not proven as an 08:00-NY-forward tradable same-day direction model**;
- execution-hour optimisation cannot be used to convert the 74.40% label score into a post-signal trading score.

## 7. Supersession of reconstructed timing population

Earlier timing scans using the 151-row / 131-consensus reconstructed execution panel remain useful only as diagnostics.

For the canonical 2026 Jan-Jul CIG claim, they are superseded by this exact-125 reconciliation.

In particular, prior statements that a late-US UP timing window transported strongly into 2026 Jan-Jul must not be treated as canonical CIG evidence. On the exact 71 canonical UP rows, 17:00->20:00 NY direction hit is **49.30%**.

## 8. Binding terminology

From this result onward:

- **74.40%** = canonical historical daily-label accuracy.
- **47.20%** = exact-canonical post-issue direction accuracy for 08:15->16:00 NY and 08:15->20:00 NY under this diagnostic.
- **50.40%** = exact-canonical 17:00->20:00 NY direction accuracy.
- **Tradable D1 accuracy** = not established by CIG-D1 V1.

No future document may substitute one of these metrics for another.

## 9. Next research implication

If the investment objective is a decision available around 08:00 NY, the forecasting target must itself be defined from a price **after issuance** to a frozen future endpoint.

That execution-aware target is a new modelling task. It must not be created by silently relabelling CIG-D1 V1.
