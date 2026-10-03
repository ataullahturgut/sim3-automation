# FLOW-PRELIM-OI-H3 V1 — RESULT

**Status:** **NO_ELIGIBLE_FLOW_PRELIM_OI_THRESHOLD**  
**Source:** CME anonymous FTP daily_volume XLSX; official CME preliminary GC Volume+OI.  
**PIT:** strict prior-trade-date only; same-day preliminary data forbidden.

## Source coverage

| Year | Listed files | PASS | Coverage | First PASS | Last PASS | Missing |
|---:|---:|---:|---:|---|---|---:|
| 2022 | 251 | 251 | 100.00% | 2022-01-03 | 2022-12-30 | 0 |
| 2023 | 251 | 250 | 99.60% | 2023-01-03 | 2023-12-29 | 1 |
| 2024 | 252 | 252 | 100.00% | 2024-01-02 | 2024-12-31 | 0 |
| 2025 | 251 | 251 | 100.00% | 2025-01-02 | 2025-12-31 | 0 |
| 2026 | 188 | 53 | 28.19% | 2026-01-02 | 2026-03-19 | 135 |

## DEV 2023-2024 threshold grid

| Threshold | Candidate | Precision | Recall | Rate | F2 | Eligible |
|---:|---:|---:|---:|---:|---:|---|
| 0.35 | 343 | 28.86% | 89.19% | 88.40% | 0.6290 | False |
| 0.40 | 302 | 28.15% | 76.58% | 77.84% | 0.5697 | False |
| 0.45 | 239 | 26.36% | 56.76% | 61.60% | 0.4612 | False |
| 0.50 | 176 | 26.14% | 41.44% | 45.36% | 0.3710 | False |
| 0.55 | 109 | 28.44% | 27.93% | 28.09% | 0.2803 | False |

## Governance

This is the separately named preliminary-OI challenger. The original FINAL-only FLOW-H3 V1 remains unchanged. No 2026 outcome selected features, lags, model or threshold.
