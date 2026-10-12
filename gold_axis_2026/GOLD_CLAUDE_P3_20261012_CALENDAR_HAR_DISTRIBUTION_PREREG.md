# CLAUDE P3 — Macro-calendar HAR-RV and conditional return/price distribution: PREREGISTRATION

Date: 2026-10-12. Investigator: Claude (independent; GPT-6 P3 work not read). Protocol: PR #93, stage
P3. Written and committed **before** any P3 forecast or loss is computed. Inputs already seen: the
H3A session RV rows (PR #91; their DEV/2025 losses were published there) and P1/P2 results.

## Question
Does the **pre-announced macro calendar** (information that is not in past prices but is known before
the decision) improve forecasts of (a) realized variance and (b) the distribution of the
post-decision XAU/USD return and price for the DAY and OVN windows? Direction is **not** tested here.

## What is new versus prior work (no relabelling)
- H3A (PR #91) = HAR3 ridge (alpha 10, standardized, expanding fit), coefficients **locked** at
  2024-12 for 2025; no calendar (H3B blocked). Result: positive OVN DEV, failed vs PERSIST5 in 2025.
- P3 adds exactly two things: (1) a single pre-announced event dummy per window type; (2) daily
  expanding re-estimation continued through 2025/26 (no locking). HAR-X below is H3A's HAR in
  2023–24 by construction (same data, features, alpha, expanding fit).
- (3) Return/price distribution forecasts built from the RV forecast are new to this repository's
  exact-clock work.

## Data
- RV: `GOLD_H3A_20261012_SESSION_RV_<2020..2025>.csv` (PR #91 branch, copied unchanged; EV/Dukascopy
  M15 mid, strict window completeness; RV = Σ squared 15-minute log mid returns inside the window).
- 2026 DAY RV: same H3A rule on `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` (separate
  source; OVN 2026 is BLOCKED, as in P1). Reported separately, never pooled.
- Returns/price origins: P1 panels (`data_claude_p1/`).
- Calendar (Neon `observations`): NFP release timestamps (`MACRO_NFP_ACTUAL_FIRST_PRINT`), CPI release
  timestamps (`MACRO_CPI_ACTUAL_FIRST_PRINT`), scheduled FOMC statement times (`MACRO_FOMC_USMPD_MP1`,
  `unscheduled`=0). Only dates/times are used, never values. **Scheduling-vintage approximation:** the
  realized release dates (including 2025 shutdown re-schedulings) are assumed known before the
  decision day; BLS/Fed publish them in advance. This is a documented research approximation.

## Event dummies (frozen)
- DAY window 09:00–16:45 TR contains the 08:30 ET release (15:30 TR under EDT, 16:30 TR under EST):
  `E_DAY = 1` if an NFP or CPI release falls on the decision date.
- OVN window 16:45 TR → 09:00 TR contains the 14:00 ET FOMC statement (21:00/22:00 TR):
  `E_OVN = 1` if a scheduled FOMC statement falls on the decision date.

## Volatility models (per window type, log RV, forecasts made before issue)
- PERSIST5: mean log RV of last 5 eligible same-type windows. CLIM60: last 60.
- HAR-X: ridge alpha 10 on standardized [logRV last1, mean last5, mean last22], intercept unpenalized,
  expanding fit on all prior windows with ≥60 history (identical to H3A), re-estimated every window
  including 2025/26.
- HAR-XE: HAR-X features + the event dummy (same ridge, dummy standardized like the others).
- Reference (secondary): H3A locked HAR from PR #91 score rows on matched dates.
- RV forecast = exp(predicted log RV). Loss: **QLIKE** = RV/F − ln(RV/F) − 1; secondary log-MSE.

## Primary tests (2, Holm) and gate
- Per target T ∈ {DAY, OVN}: event increment `QLIKE(HAR-X) − QLIKE(HAR-XE)` pooled DEV 2023–24,
  one-sided Diebold–Mariano (Newey–West 5), H1: > 0.
- **SUPPORTED (RV only)** for T if: (a) Holm p < 0.05; (b) HAR-XE mean QLIKE below PERSIST5 and below
  CLIM60 in **each** of 2023 and 2024; (c) the 2025 event increment does not reverse sign
  (diagnostic). Otherwise REJECT for T.
- A supported result is a **volatility** result only; it is never presented as direction skill.

## Secondary: return and price distribution (reported, not gating)
- Mean return μ = INT (expanding mean of prior eligible returns of the same window type).
- σ² = k·F, F = model RV forecast, k = Σ(prior y²)/Σ(prior realized RV) (expanding; maps observed
  M15 RV to full-window return variance, including the gap/blackout share).
- Compare Gaussian CRPS (bp) and pinball loss at τ ∈ {0.05, 0.25, 0.50, 0.75, 0.95} for σ from
  HAR-XE, HAR-X, PERSIST5 and UNCOND (expanding std of y); report 90% interval coverage, mean width
  in bp and in USD/oz (`P_origin·exp(μ ± 1.645σ)`), per year.

## Honesty rules
No change of dummies, windows, models, alpha or loss after seeing results; no additional event types
as rescue. 2025/26 are opened retrospective periods. Neon read-only; small derived files only.
