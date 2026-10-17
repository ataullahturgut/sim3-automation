# CLAUDE P2 — FOMC announcement response → next Türkiye DAY XAU/USD return: PREREGISTRATION

Date: 2026-10-12. Investigator: Claude (independent; GPT-6 P2 work not read). Protocol: PR #93, stage P2.
Written and committed **before** any FOMC-window price, return or score is computed. Only the event
calendar (dates, times, scheduled/unscheduled flags) has been read.

## Hypothesis and mechanism
Lee & Wang (2025, RAPS; currency markets) report that post-FOMC price moves partly reverse 12–24 h
after the announcement as uncertainty resolves; Awartani, Hussain & Virk (2024, IRFA) report gold's
FOMC adjustment lasts longer than five minutes. **Untested for gold at our clock.** The next Türkiye
DAY window (09:00→16:45 TR) begins +11 h (EST) / +12 h (EDT) after a 14:00 ET statement and ends
+18¾ / +19¾ h after it, inside the 12–24 h window. FX evidence is not treated as evidence for gold.

## Events (calendar is pre-announced → point-in-time)
- Source: Neon `observations`, series `MACRO_FOMC_USMPD_MP1` (SF Fed US Monetary Policy Event-Study
  Database, event times in America/New_York, `unscheduled` flag). Only the event **times** are used;
  MP1 surprise values are not used in any test.
- Primary sample: **scheduled** statements (`unscheduled`=0) 2020-01-01..2024-12-31 = 39 events
  (7 in 2020 because the March meeting was replaced by an unscheduled action; 8 per year 2021–24).
  Opened retrospective: 2025 (8), 2026 (5, separate source). Unscheduled actions are excluded.
- t0 = 14:00 America/New_York on the event date (all scheduled 2020–26 statements are at 14:00 ET).

## Prices (M15 mid close; bar_start_utc is bar START; P(c) = close of bar starting c−15 min)
- 2020–2025 `gold_research_evduka_xau15m_bidask_candidate`; 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`.
- `x_react = ln P(t0+45m) / P(t0−15m)` (immediate reaction window, known at 14:45 ET).
- `x_pre  = ln P(t0−15m) / P(t0−24h−15m)` (pre-announcement drift window).
- `x_full = ln P(next TR day 08:30) / P(t0−15m)` (everything known by the 08:45 decision with the
  15-minute buffer).
- Target `y` = DAY return of the next Türkiye calendar day (event date + 1): `ln P(16:45)/P(09:00)`,
  taken from the P1 panels (`data_claude_p1`, same eligibility rule; ineligible days dropped).
  Decision time 08:45 TR on event date + 1; all inputs precede it.

## Placebo (control for generic Wednesday-night → Thursday behaviour)
Every Wednesday 2020–2024 with no FOMC event (scheduled or unscheduled) on that date or within ±1
calendar day; pseudo t0 = 14:00 ET; identical x and y definitions.

## Primary test (single, frozen)
OLS `y = a + b·x_react` on the scheduled events 2020–2024; H1: **b < 0** (reversal); one-sided t-test
with HC3 standard errors, α = 0.05.

## Gate for TENTATIVE (all required); otherwise REJECT
1. Primary p < 0.05.
2. Placebo slope not significantly negative (one-sided HC3 p ≥ 0.05) **and** pooled interaction
   regression `y = a + b·x + c·D + d·x·D` (D = FOMC event) gives d < 0 with one-sided HC3 p < 0.05.
3. Out-of-sample return forecast on events, `ŷ_t = â_{<t} + b̂_{<t}·x_react,t` estimated on prior
   scheduled events only (minimum 10 prior events; first forecast ≈ 2021), has lower MSE than both
   **RW** (ŷ=0) and **INT** (expanding mean of all prior eligible DAY returns since 2020-01-01) over
   the 2021–2024 OOS events.
4. 2025 and 2026 (opened; diagnostic) reported separately: slope sign and hit rate; a reversed sign is
   reported but cannot rescue or fail the 2020–24 decision on its own.

## Secondary (Holm over 2, reported, not gating)
- Same OLS with `x_pre` (pre-FOMC drift reversal) and `x_full` (all information up to 08:30 TR).

## Reported for every block (2020–24 pooled, per year, 2025, 2026)
N; slope, HC3 SE, one-sided p; Spearman ρ; reversal sign-rule `ŷ = −sign(x_react)` hit rate with exact
binomial p and the always-UP hit rate on the same rows; OOS MSE / RMSE (bp) and price-level MAE (USD)
for the slope model, RW and INT; direction accuracy, balanced accuracy, UP/DOWN recall; R67 matched
DAY direction comparison where dates overlap. Power statement: with N ≈ 39 a one-sided 5% test has
80% power only for |ρ| ≳ 0.39; a null is **not** evidence of no effect of smaller size.

## Honesty rules
No change of windows (−15/+45 min, 24 h pre-window), clocks, event set or placebo after seeing
results; no additional event types (minutes, CPI, NFP) as rescue. No profitability claim. Neon is
read-only; outputs are small derived CSV/JSON on this branch.
