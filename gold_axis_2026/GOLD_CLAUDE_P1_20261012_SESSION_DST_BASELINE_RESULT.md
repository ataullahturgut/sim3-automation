# CLAUDE P1 — Session / US-DST conditional baselines: RESULT — **BASELINE_ONLY (negative)**

Prereg: `GOLD_CLAUDE_P1_20261012_SESSION_DST_BASELINE_PREREG.md` (commit `7c926e21`, pushed before any
outcome was computed). Code: `tools/gold_claude_p1_20261012_session_dst_baseline.py`. SQL:
`sql/gold_claude_p1_20261012_session_panel.sql` (run read-only inside `SET TRANSACTION READ ONLY`).
Derived panels: `data_claude_p1/GOLD_CLAUDE_P1_PANEL_<year>.csv` (per-date clock prices/returns; each
year's row count and column sums verified against SQL-side checksums). Outputs:
`GOLD_CLAUDE_P1_20261012_SUMMARY.json`, `..._SCORE_ROWS.csv` (every scored forecast),
`..._BASELINE_ATLAS.csv`. GPT-6's P1 branch was not opened before this result was frozen.

## What was predicted
Future XAU/USD **log return** (bp) and implied **price level** (USD/oz), plus direction, for
- DAY: decision 08:45 TR → `ln P(16:45)/P(09:00)`; OVN: decision 16:30 TR → `ln P(next 09:00)/P(16:45)`.
- Candidates: M1 shrunk US-DST×weekday cell mean; M2 ridge on pre-issue segment returns (previous US
  session to the CME daily break, Asia/early-London to 08:30, previous window; OVN: DAY-so-far to
  16:15, previous night); M3 = M2 × DST interactions. Comparators: RW (zero return) and INT
  (expanding mean). Daily expanding re-estimation from 2020; 2020–22 warm-up only.

## Data gate
| Cohort | Source | DAY eligible | OVN eligible |
|---|---|---|---|
| 2020–2022 (warm-up) | EV/Dukascopy M15 bid/ask | 258/258/258 | 201/200/199 |
| 2023, 2024 (DEV) | EV/Dukascopy | 256, 259 | 198, 197 |
| 2025 (opened) | EV/Dukascopy | 258 | 198 |
| 2026 (opened, separate source) | Dukascopy direct, `m1_matched`=0 | 179 | **0 → BLOCKED** |

2023 counts equal H3A/BSC-8 (DAY 256, OVN 198). The 2026 direct source has no 75-minute daily
quote break, so under the frozen H3A-identical window rule no 2026 night is eligible and the
break-anchored segment features exist on only 45 DAY rows (mostly post-weekend Mondays). The rule was
not changed. 2026 is not pooled with any other year.

## Primary gate (12 tests, Holm) — all fail
Pooled DEV 2023–24, one-sided Diebold–Mariano (Newey–West 5), MSE gain in bp² (positive = better):

| Target | Model | gain vs RW (p) | gain vs INT (p) | beats RW & INT both DEV years | 2025 no reversal | Verdict |
|---|---|---|---|---|---|---|
| DAY (n=515) | M1 | −14.4 (0.88) | −12.0 (0.83) | no | no | REJECT |
| DAY | M2 | −49.8 (0.92) | −47.4 (0.91) | no | no | REJECT |
| DAY | M3 | −74.7 (0.97) | −72.3 (0.97) | no | no | REJECT |
| OVN (n=395) | M1 | −7.1 (0.61) | −21.9 (0.81) | no | yes | REJECT |
| OVN | M2 | +5.9 (0.33) | −8.9 (0.93) | no | yes | REJECT |
| OVN | M3 | +7.5 (0.39) | −7.3 (0.62) | no | yes | REJECT |

All Holm-adjusted p = 1.0. **P1 classification: BASELINE_ONLY.**

## Per-year errors (row-matched; RMSE in bp = √MSE; price MAE in USD/oz)
| Target, year | n | RW RMSE / $MAE | INT | M1 | M2 | M3 | best R²_OS vs RW |
|---|---|---|---|---|---|---|---|
| DAY 2023 | 256 | 47.75 / 6.77 | 47.77 / 6.77 | 47.85 / 6.78 | 48.12 / 6.86 | 48.15 / 6.91 | −0.44% (M1) |
| DAY 2024 | 259 | 54.61 / 9.74 | 54.64 / 9.74 | 54.78 / 9.80 | 55.19 / 9.92 | 55.62 / 9.98 | −0.63% (M1) |
| DAY 2025 | 258 | 67.69 / 16.99 | 67.65 / 16.93 | 67.72 / 16.96 | 67.85 / 17.00 | 67.93 / 17.05 | −0.07% (M1) |
| DAY 2026* | 45 | 86.83 / 27.46 | 86.91 / 27.46 | 87.36 / 27.44 | 90.39 / 27.59 | 88.25 / 28.03 | −1.23% (M1) |
| OVN 2023 | 198 | 58.98 / 8.57 | 58.91 / 8.55 | 58.91 / 8.56 | 59.01 / 8.58 | 58.97 / 8.57 | +0.23% (M1) |
| OVN 2024 | 197 | 64.52 / 11.10 | 64.35 / 11.05 | 64.70 / 11.07 | 64.40 / 11.07 | 64.41 / 11.08 | +0.37% (M2) |
| OVN 2025 | 198 | 86.75 / 23.27 | 86.37 / 23.22 | 86.22 / 23.15 | 86.04 / 23.20 | 86.21 / 23.10 | +1.61% (M2) |

\*2026 DAY matched rows are only the 45 with segment features. On all 179 2026 DAY rows the calendar
models give RW 90.25 bp / $29.72, INT 90.18 / $29.68, M1 90.30 bp.

The OVN gains are tiny (≤0.4% in DEV) and **do not beat INT**: they are drift capture, not
session information. The opened 2025 OVN improvement (+1.6% vs RW, +0.8% vs INT) is consistent with
the 2025 rally and is not a pass (prereg: diagnostic only).

## Direction (secondary) — none beats the class baseline
| Target, year | always-UP acc | M1 acc / BA / DOWN recall | M2 | M3 | log-loss PRIOR vs best |
|---|---|---|---|---|---|
| DAY 2023 | 48.6% | 49.0 / 48.8 / 0.58 | 51.0 / 50.9 / 0.55 | 52.9 / 52.8 / 0.56 | 0.6963 vs 0.6935 (M1) |
| DAY 2024 | 57.9% | 48.3 / 49.1 / 0.54 | 47.1 / 47.3 / 0.49 | 46.3 / 46.3 / 0.46 | 0.6867 vs 0.6962 (worse) |
| DAY 2025 | 58.9% | 50.4 / 50.0 / 0.48 | 51.2 / 49.8 / 0.42 | 48.4 / 47.5 / 0.42 | 0.6831 vs 0.6910 (worse) |
| OVN 2023 | 58.6% | 52.5 / 52.3 / 0.51 | 47.5 / 42.7 / 0.15 | 53.5 / 51.2 / 0.38 | 0.6911 vs 0.6920 (worse) |
| OVN 2024 | 56.3% | 47.2 / 45.8 / 0.35 | 55.3 / 49.4 / 0.02 | 56.9 / 53.3 / 0.26 | 0.6888 vs 0.6893 (worse) |
| OVN 2025 | 53.5% | 51.0 / 48.6 / 0.15 | 51.5 / 48.5 / 0.05 | 53.5 / 51.1 / 0.16 | 0.6912 vs 0.6896 (M1) |

M3's 52.8% BA (DAY 2023) reverses to 46.3% in 2024. Matched against R67 `new_pred` on identical
dates, no candidate differs significantly in any DEV year (McNemar p ≥ 0.36 for DAY; the one OVN
p<0.05, M3 vs R67 in 2024 with 49 corrected / 30 broken, is a secondary test that does not survive
any multiplicity correction and coincides with M3 losing to INT on MSE). For DAY 2025, always-UP corrected
82 and broke 46 decisions vs R67 `new_pred` (p=0.002): the earlier exact-clock model is worse than the
trivial class baseline in the opened year.

## Baseline atlas (descriptive; full table in `..._BASELINE_ATLAS.csv`)
UP rate by US-DST regime, DEV years (Wilson 95% CI):
- DAY 2023: EST 40.9% [31.2, 51.4] vs EDT 52.4% [44.9, 59.8]; 2024: EST 51.1% vs EDT 61.5%; but 2025
  reverses (EST 61.8% vs EDT 57.4%) and 2022 also reverses (59.6% vs 47.9%).
- OVN 2023: 58.2% vs 58.8%; 2024: 52.2% vs 58.5%; 2022: 57.4% vs 40.5%.
- The sign of the DST difference changes across years: no stable DST effect on direction or mean.
- Mean returns (bp, all rows): DAY 2023/24/25 = −0.9 / +3.6 / +5.9; OVN = +7.2 / +6.9 / +11.8. The
  night window carried more of the 2023–25 drift than the day window, matching the overnight-positive
  pattern in the literature, but it is a level/drift fact that INT already captures.

## Answer to the program question
Structural information known at decision time (US-DST regime, weekday, pre-issue segment returns
around the CME daily break) **does not** forecast the post-decision XAU/USD return, price level or
direction better than the random walk or the historical mean, in either DEV year. The correct
baselines for P2–P7 are: **RW and INT for return/price error** (they differ by <0.5% MSE) and
**always-UP / expanding UP prior for direction** (always-UP accuracy 48.6–58.9%, BA 50%).

## Limits
Historical vendor backfill, not live receipt times; 15-minute latency buffer assumed. The M15
mid-quote is not an executable price. No bank quotes, no profitability claim. 2025/26 are opened
retrospective periods. 2026 is a different source with a different session structure.
