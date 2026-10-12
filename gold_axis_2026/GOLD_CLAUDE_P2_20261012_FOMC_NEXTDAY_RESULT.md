# CLAUDE P2 — FOMC reaction → next Türkiye DAY XAU/USD return: RESULT — **REJECT (negative)**

Prereg `GOLD_CLAUDE_P2_20261012_FOMC_NEXTDAY_PREREG.md` (commit `83fc0b66`, pushed before outcomes).
SQL `sql/gold_claude_p2_20261012_fomc_windows.sql` (read-only); window prices
`data_claude_p2/GOLD_CLAUDE_P2_FOMC_WINDOW_PRICES.csv` (356 dates, checksum-verified); DAY targets
reuse the P1 panels (`data_claude_p1/`, identical eligibility). Code
`tools/gold_claude_p2_20261012_fomc_nextday.py`; outputs `GOLD_CLAUDE_P2_20261012_{SUMMARY.json,EVENT_ROWS.csv}`.

## What was predicted
Next Türkiye DAY (09:00→16:45) XAU/USD log return after a scheduled 14:00 ET FOMC statement,
decision 08:45 TR, from the immediate reaction `x_react = ln P(t0+45m)/P(t0−15m)`. Hypothesis
(Lee & Wang 2025, FX): reversal, slope < 0.

## Data gate
Scheduled events (USMPD `unscheduled`=0) with usable reaction and eligible next-day DAY window:
2020 7/7, 2021–2025 8/8 each, 2026 3/5 (direct source missing bars around 2026-03-18 and
2026-07-29). Primary sample 2020–24: **N = 39**. Placebo: 215 non-FOMC Wednesdays 2020–24.

## Primary and gate
| Test | N | slope (bp per bp) | HC3 SE | one-sided p (slope<0) | Spearman ρ | reversal hits |
|---|---|---|---|---|---|---|
| **FOMC 2020–24 (primary)** | 39 | **+0.113** | 0.251 | **0.67** | +0.03 | 16/39 = 41.0% (binom p=0.90) |
| Placebo Wednesdays | 215 | +0.172 | 0.226 | 0.78 | −0.03 | 110/215 = 51.2% |
| FOMC − placebo interaction | 254 | −0.059 | 0.338 | 0.43 | — | — |

| Gate item | Result |
|---|---|
| Primary p < 0.05 | **fail** (0.67; estimated sign is continuation, not reversal) |
| Placebo not negative | pass |
| Interaction p < 0.05 | **fail** (0.43) |
| OOS slope model beats RW and INT (2021–24) | **fail** |

**Verdict: REJECT.** The power caveat from the prereg applies (N=39 detects only |ρ| ≳ 0.39), but
the point estimate has the wrong sign, so this is not a near-miss.

## Out-of-sample error (expanding slope fitted on prior events only; ≥10 prior events)
| Block | N | slope RMSE bp / price MAE $ | RW | INT | R²_OS vs RW |
|---|---|---|---|---|---|
| 2021–24 pooled | 29 | 85.15 / 10.89 | 65.30 / 8.97 | 65.39 / 8.96 | **−70.0%** |
| 2021 | 5 | 165.05 / 22.06 | 102.50 / 15.53 | 103.01 / 15.56 | — |
| 2022 | 8 | 57.92 / 8.57 | 62.23 / 9.24 | 62.21 / 9.25 | — |
| 2023 | 8 | 62.11 / 9.74 | 58.50 / 7.16 | 58.35 / 7.12 | — |
| 2024 | 8 | 45.25 / 7.38 | 39.97 / 6.40 | 39.90 / 6.40 | — |
| 2025 (opened) | 8 | 49.32 / 14.92 | 43.10 / 12.23 | 43.00 / 12.12 | — |
| 2026 (opened, other source) | 3 | 108.89 / 48.20 | 105.49 / 47.66 | 105.67 / 47.91 | — |

Direction 2021–24 (N=29): slope model accuracy 44.8%, BA 41.4%, DOWN recall 0.56; always-UP 37.9%
(BA 50%). Matched vs R67 `new_pred` on 15 overlapping dates: 3 corrected, 7 broken (McNemar p=0.34).

## Secondary (Holm over 2) — both fail
- Pre-FOMC 24 h drift `x_pre`: slope +0.102, p=0.65, hit rate 48.7%; Holm p=1.0.
- All information to 08:30 TR `x_full`: slope +0.146, p=0.87, hit rate 48.7%; Holm p=1.0.

## Per-year slopes (descriptive; 7–8 events each)
2020 −0.06, 2021 +0.25, 2022 +0.57, 2023 +0.00, 2024 −0.41, 2025 (opened) −0.04. No stable sign.

## Post-hoc observation (NOT a tested result)
The 2020–24 intercept on post-FOMC days is −14.2 bp versus +6.2 bp on placebo Thursdays, and
always-UP was right on 43.6% of post-FOMC days versus 54.9% on placebo days. This was not
preregistered, rests on 39 events, and is reported only so that a future prereg could test a
"post-FOMC day drift" hypothesis on new data. It must not be used as a signal.

## Answer to the program question
The XAU/USD reaction in the first 45 minutes after a scheduled FOMC statement, the 24-hour
pre-FOMC drift, and all price information up to 08:30 TR **do not** improve the forecast of the next
Türkiye DAY return, price level or direction over the random walk or the historical mean. The FX
12–24 h reversal (Lee & Wang) is **not replicated** for spot gold at this clock.
