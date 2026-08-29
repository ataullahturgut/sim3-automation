# GOLD H1 R1 — Source Manifest

## Canonical monthly precious-metals chain
Pinned repository:
- `lbruton/StakTrakr`
- commit: `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`
- historical year files: `data/spot-history-2010.json` ... `data/spot-history-2026.json`

Important correction: the old note that all pinned precious-metal rows were LBMA is false. Inspection of 2026 raw data showed provider/source transitions including `LBMA`, `MetalPriceAPI`, and `StakTrakr/sqld`, plus weekend/calendar-day observations. Do not run daily BOCPD/CUSUM blindly on that raw chain.

## Independent XAUUSD tactical source
Pinned repository:
- `simom1/XAUUSD-history`
- commit: `f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0`

Known quality issue: `XAUUSD_W1.csv` becomes partial/unreliable in 2026 spring/summer. Recent 2026 weekly states must be reconstructed from D1 market-day closes or cross-source checked. Raw late-spring/summer W1 bars must not be treated as guaranteed completed weeks.

## Canonical monthly audit span
- Monthly master: 1994-02 through 2026-07.
- Exact 3M momentum reconciliation was previously verified against the archived 43-month test.
- 2026-Aug forecasts must use only information available through 2026-07-31.

## Source-handling rule
Any new source must record source/provider, commit/version or retrieval date, exact cutoff, market/calendar-day rule, missing/duplicate handling, provider transitions, and whether it is used for fitting, validation, or diagnostic cross-check only.
