# GOLD H3 — Databento Bridge Cost Probe — 2026-10-05

**Status:** **DATABENTO_COST_AND_SYMBOLOGY_PROBE_PASS**

- This probe performs no historical market-data download.
- It does not change LLRS, IFBC, Handoff, DPTC, Q95 or Q99.
- Purpose: verify continuous symbology and estimate cost before spending credits.

## Symbology

- bridge: **PASS**
- historical: **PASS**

## Cost estimates

| Request | Status | Estimated USD |
|---|---|---:|
| bridge_all_15_symbols | PASS | 1.392569839954 |
| historical_2023_2024_calendar_5 | PASS | 0.396727621555 |
| historical_2023_2024_open_interest_5 | PASS | 0.585925355554 |
| historical_2023_2024_volume_5 | PASS | 0.585717260838 |

## Next scientific step

After cost approval, download only the 2025 bridge window for all three roll rules. Select the roll mapping using source agreement only: timestamp/session, return correlation, direction agreement, 1h/3h/6h rolling returns and GC/SI volume stability. Never use DPTC outcome labels to choose the roll rule.
