# H3 — M15 realized-volatility forecasting for future XAU/USD DAY/OVN windows: preregistration

2026-10-12. Pre-register before computing actual future realized-volatility forecast-losses. **H3A** is the reproducible source-qualified HAR-RV-only component. H3B (pre-announced US macro calendar and historical pre-issue GVZ) is **BLOCKED until immutable/point-in-time schedule and GVZ vintages are validated**. Do not use realized macro releases or retrospective outcome labels as pre-event features.

## Exact, future-only window & extraction
- EVTradingLabs / Dukascopy-derived XAUUSD M15 BID/ASK 2020–2025, source `gold_research_evduka_xau15m_bidask_candidate`. Separate 2026 direct Dukascopy panel **not used for model selection**: `m1_matched` source-quality currently 0 on all 2026 bars; continuity/PIT gate must be independently passed first.
- Only calendar DAY 09:00→16:45 Europe/Istanbul weekdays, issue no later than **08:45 TRT**, and OVN 16:45→next 09:00 TRT Monday–Thursday, issue by **16:30 TRT**. All feature sessions are complete **before** issue; no target-window information permitted.
- `bar_start_utc` is start timestamp; M15 bar mid-close uses (bid_close+ask_close)/2 and is not known until bar closes.
- Strict window completeness DAY exactly **31** bar slots starting 09:00 through16:30 at contiguous 15min steps. OVN exactly **61** observed bar slots from 16:45 through08:45 and **one 75-minute quote blackout** (one 4-slot planned market maintenance), all other 15min steps; no interpolation or crosses across blackout. Source quote must have 0 < bid<=ask.
- Define `RV_window=sum(log(midclose_t/midclose_t-1)^2)` ONLY across 15min consecutive bars within that window. Excludes missing-market-closure jump. This is a *partial observed-M15 realized-variance proxy*, not complete overnight true variance. If strict completeness/gap fails, exclude window.
- Preissue feature at t: historical same-type RV from prior 1, mean of prior 5, mean of prior 22 **eligible earlier windows**, never use today's incomplete session. If gaps in chronological past, preceding eligible nights only. 2020–22 all training prior-history, DEV 2023–24, 2025 previously opened transport.
- No day/weekend lookahead; separate DAY/OVN learners. All target values positive.
## Frozen model and controls
- Response = log RV. `HAR3` low-capacity ridge with alpha10 on standardized features `logRV(last1)`, mean(logRV(last5)), mean(logRV(last22)), intercept unpenalized. Estimation rolling **expanding historical fit** from 2020 before each DEV decision, >=60 training windows with prior22 history per session type.
- Controls: `CLIM60` mean logRV from prior60 valid same-type windows; `PERSIST1` last valid logRV; `PERSIST5` mean logRV last5. Forecast level = exp(predicted logRV); no fitted threshold or events.
- Need source/time appropriate observations; models do not see target day's future. For 2025, freeze HAR coefficients using training data through2024-12, but lagged observed RV features themselves update chronologically (allowed after each actual session completion).
- Primary loss **QLIKE** = RV/forecast - log(RV/forecast)-1. Secondary log MSE. Fixed strict gate: HAR must beat **each** of three controls by mean QLIKE in each DEV calendar year (2023 and 2024), with 3-month moving-block bootstrap 95% CI for per-window QLIKE improvement excluding 0, and no 2025 opened sign reversal (diagnostic only). If not: NO PROMOTION. All windows, no minimum signal gate.
- No claiming directional or price-level forecasting improvements from variance alone. No bank products, no XAU/USD trade P&L.

## Source limitations and reporting
- Archived vendor backfill does not prove contemporaneous quote receipt times; strict bar-completion and hypothetical issuance times are historical causal reconstructions.
- If a source or cohort fails preissue completeness, mark it BLOCKED and stop that portion. Explain H3A negative even if H3B not attempted. No retuning to rescue.
- Retain SQL extraction, full row-level scores, replay script, machine summary and report in this separate branch; no Neon writes, no current authority/manifests changes.
