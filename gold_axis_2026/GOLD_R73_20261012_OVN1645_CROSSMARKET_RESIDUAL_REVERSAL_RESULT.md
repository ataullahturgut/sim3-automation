# R73 RESULT — OVN 16:45 → next calendar day 09:00 TR: ZN/NQ/CL cross-market residual reversal

**Verdict (pre-registered, primary window W7): REJECT.** The gold-specific residual after removing ZN/NQ/CL co-movement carries **no additional overnight direction information** beyond the raw gold move, and neither one transports to 2025/2026.

- Preregistration: `GOLD_R73_20261012_OVN1645_CROSSMARKET_RESIDUAL_REVERSAL_PREREG.md`, committed (`2371b588`) before any target outcome was queried.
- Code: `tools/gold_r73_ovn1645_xmkt_residual_reversal.py`, numpy/pandas only, about 4 s.
- Panel SQL: `sql/gold_r73_ovn1645_xmkt_panel.sql`.
- Panel (derived log-returns ×1e5, no raw prices): `GOLD_R73_20261012_OVN1645_XMKT_PANEL_LOGRET_E5.csv`.
- Per-night ledger: `GOLD_R73_20261012_OVN1645_XMKT_RESIDUAL_ROWS.csv`.
- All metrics: `GOLD_R73_20261012_OVN1645_XMKT_RESIDUAL_SUMMARY.json`.

## 1. What was done
- **Data:**
  - Neon `gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c` (`ZN.c.0`, `NQ.c.0`, `CL.c.0`).
  - XAU BID/ASK M15 from `gold_research_evduka_xau15m_bidask_candidate` for 2023–2025.
  - XAU BID/ASK M15 from `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` for 2026.
  - The two XAU sources are labelled per row and never pooled.
- **New Neon objects created; nothing existing was modified:**
  - table `gold_research_r73_ovn1645_xmkt_residual_panel_v1`
  - view `gold_research_r73_ovn1645_panel_compact_v1`
- **Clock audit:**
  - CME `ts_event` is the bar START. In 2024, the GC hourly return correlates 0.649 with XAU over [ts, ts+1h), against 0.065 for [ts−1h, ts).
  - Features end at 13:00 UTC (16:00 TR). The CME bar starting 13:00 UTC is never used.
  - The 13:00–13:45 UTC gap is used neither as feature nor as target.
  - Target: (bid+ask)/2 open at 13:45 UTC → next calendar day 06:00 UTC open, Mon–Thu decisions only.
  - No intra-window contract roll occurred: Databento `c.0` rolls at session boundaries, so the roll-flag count is 0.
- **ZN coverage gap:** ZN `c.0` has no 03:00–05:00 UTC trade in quarterly roll weeks (Mar/Jun/Sep/Dec). This removes 18–32 days per year. The days are dropped by the prereg rule, without imputation.
- **Transfer integrity:** the panel was exported via Neon MCP and checked per year against SQL column sums. All 11 columns × 4 years match exactly.
- **Leakage checks, both PASS:**
  - Residuals are identical after permuting the overnight target.
  - Residuals computed before 2024-06-30 are unchanged when all later rows are deleted.
- **Model:** ridge regression (alpha 10 on the standardized design, intercept) of gold W7 (09–16 TR) and W3 (13–16 TR) log-returns on ZN/NQ/CL returns over the same exact interval. It is fit on the most recent 250 prior complete weekdays, needs at least 60, and never uses an overnight outcome.
- **Rule:** `sign(−residual)`.

## 2. Results — W7 (primary), Dukascopy-family mid labels

| Year | N / eligible (cov.) | UP rate | R_RESID acc / BA | R_REV acc / BA | R_MOM BA | ALWAYS_UP acc | RESID vs REV (rescue/break) | Spearman(e, ovn) |
|---|---|---|---|---|---|---|---|---|
| 2023 | 134 / 205 (65.4%) | 59.7% | 56.72% / 55.93% | 56.0% / 55.90% | 44.10% | 59.70% | 16 / 15 | −0.121 |
| 2024 | 182 / 205 (88.8%) | 56.0% | 53.85% / 54.64% | 56.0% / 56.47% | 43.53% | 56.04% | 8 / 12 | −0.055 |
| **DEV 2023–24** | **316 / 410 (77.1%)** | 57.6% | **55.06% / 55.38%** (Wilson 49.6–60.5) | 56.01% / 56.30% | 43.70% | 57.59% | **24 / 27 (p=0.71)** | −0.078 |
| 2025 (retro., inspected) | 187 / 204 (91.7%) | 54.5% | 45.99% / 46.37% | 47.06% / 47.94% | 52.06% | 54.55% | 8 / 10 | +0.109 |
| 2026 (retro., direct Dukascopy) | 121 / 133 (91.0%) | 48.8% | 51.24% / 51.23% | 48.76% / 48.73% | 51.27% | 48.76% | 7 / 4 | +0.061 |

2023 coverage is lower because of the 60-day ridge warm-up (CME data only begin 2023-01-02) plus the ZN roll-week gaps.

**Pre-registered gates (DEV):**
- **H1 FAIL.** R_RESID 174/316, one-sided binomial p = 0.0405, which becomes **0.081 after Holm** across W7/W3.
- **H2 FAIL.** McNemar against raw reversal: 24 vs 27, one-sided p = 0.71. The month-block bootstrap gives a BA difference of −0.92 pp, 95% CI [−4.97, +3.00].
- **H3 FAIL.** In the OLS `ovn ~ fitted + resid` (HC3), the residual coefficient is −0.042 (t = −0.54, one-sided p = 0.30). The fitted (factor) part has a similar coefficient of −0.099 (t = −0.61), so there is no residual-specific reversal.

**W3 (13–16 TR), secondary:** DEV R_RESID 175/336, 52.08%, BA 52.28%, Holm p = 0.24. 2023: BA 56.50%; 2024: BA 48.87%; 2025: BA 49.65%; 2026: BA 52.27%.

**Matched comparison with R67** (16:45→09 HistData logistic, W7, same dates, scored on the EV/Dukascopy label). R67 was fitted on 2023–24, so it is in-sample on DEV.

| Rows | N | R_RESID | R_REV | R67 new_pred | R67 h3bit |
|---|---|---|---|---|---|
| DEV 2023–24 | 230 | BA 54.65% | BA 54.92% | BA 51.50% | BA 53.08% |
| 2025 | 179 | BA 47.17% | BA 48.64% | BA 47.22% | BA 47.86% |
| 2026 | 117 | BA 50.44% | BA 47.85% | BA 52.28% | BA 48.73% |

R_RESID against R67 new_pred, rescues/breaks: DEV 46/39, 2025 34/35, 2026 17/19. No significant difference.

**Source sensitivity (new, descriptive):** the EV/Dukascopy and R67/HistData overnight signs disagree on **14.8%** of matched DEV nights. By year, the agreement rate is 2023 90.6%, 2024 83.1%, 2025 95.0% and 2026 87.2%. The sign of small 16:45→09 moves is vendor-dependent.

## 3. What is new versus earlier work
- **New (negative) mechanism evidence:** this is the first direct test of a factor residual on the 16:45 clock.
  - The ZN/NQ/CL factor fit explains only 30% (2023), 12.5% (2024), 4.6% (2025) and 7.7% (2026) of the variance of the gold 09–16 move.
  - The average standardized loading is dominated by ZN (gold moves with bond prices); the NQ and CL loadings are small and unstable.
  - Because the factor part is small, `sign(residual) = sign(raw move)` on 77–91% of nights. The residual rule therefore differs from raw reversal on only 51 DEV nights, where it went 24 right / 27 wrong.
  - The gold–ZN link nearly vanished in 2025 (fit R² ≈ 0.05).
- **Confirmation of existing knowledge, not new alpha:**
  - Raw reversal of the 09–16 move works in DEV: 177/316, binomial p = 0.019.
  - It flips to momentum in 2025 (R_MOM BA 52.06%) and is a coin flip in 2026.
  - This matches the manifest's prior finding that reversal structures fitted in 2023–24 do not transport.
  - It is also already partly encoded in R67's `pre_close_day` input.
- **Residual quintiles (DEV, W7):** the most negative residual quintile gives a next-night UP rate of 67.2%, but the most positive quintile gives 54.0%, not DOWN. The apparent effect is mostly gold's 2023–24 up-drift (ALWAYS_UP 57.6%), not a symmetric reversal.

## 4. Economics: why no profitability conclusion is possible
- **Mid-to-mid gross mean per night, DEV:** R_RESID +2.87 bp, R_REV +5.02 bp, ALWAYS_UP +6.86 bp.
- **Crossing the Dukascopy BID/ASK** (about 1.7 bp per trade) leaves R_RESID at +1.18 bp per night against ALWAYS_UP's +5.17 bp.
- **Night volatility:** mean |ovn| is 43 bp in DEV, 66 bp in 2025 and 105 bp in 2026.
- No bank BID/ASK quote history exists in the project. A Turkish bank's gold spread is typically many times the Dukascopy spread, so no bank P&L claim is possible.
- In any case, the rule does not beat the unconditional long-drift baseline even before costs.

## 5. What is and is not predictable after 16:45 (supported findings only)
- Supported: gold's own 2023–24 unconditional overnight up-drift (57.6% UP), which disappeared in 2026 (48.8% UP).
- Supported: overnight magnitude rose strongly across years (43 → 66 → 105 bp mean absolute move). Magnitude and volatility are therefore more forecastable than sign.
- **Not supported:** any directional information in the 09–16 TR gold move, raw or factor-residualized, that holds across 2023–2026 for the 16:45→09 night.

## 6. Decision
**REJECT** this hypothesis as stated, under its pre-registered gates.

Do not retune the windows, the alpha, the factor set or the thresholds, and do not move the cutoff to 16:30.

The ZN-dominated factor share is too small and unstable for residualization to change the decision on more than about 10–20% of nights. Any successor needs information that is genuinely orthogonal to the gold path itself, not a re-expression of it.
