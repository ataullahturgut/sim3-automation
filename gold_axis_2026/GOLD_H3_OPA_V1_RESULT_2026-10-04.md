# OPA-H3 V1 — GOLD OPTIONS POSITIONING ASYMMETRY RESULT

**Status:** **OPA_DEV_FAIL**  
**Source:** official CME anonymous FTP daily_volume workbooks; OG GOLD CALL / GOLD PUT aggregate volume + preliminary OI.  
**PIT:** strict prior-trade-date only; same-day source values forbidden.

## Source coverage

| Year | Listed | PASS | Coverage | First | Last | Missing |
|---:|---:|---:|---:|---|---|---:|
| 2022 | 251 | 251 | 100.00% | 2022-01-03 | 2022-12-30 | 0 |
| 2023 | 251 | 250 | 99.60% | 2023-01-03 | 2023-12-29 | 1 |
| 2024 | 252 | 252 | 100.00% | 2024-01-02 | 2024-12-31 | 0 |
| 2025 | 251 | 251 | 100.00% | 2025-01-02 | 2025-12-31 | 0 |
| 2026 | 188 | 53 | 28.19% | 2026-01-02 | 2026-03-19 | 135 |

## DEV 2023-2024

| Threshold | Candidates | Precision | Recall | Rate | F2 | Eligible |
|---:|---:|---:|---:|---:|---:|---|
| 0.35 | 284 | 28.52% | 87.10% | 85.54% | 0.6174 | False |
| 0.40 | 247 | 28.74% | 76.34% | 74.40% | 0.5735 | False |
| 0.45 | 197 | 31.47% | 66.67% | 59.34% | 0.5448 | False |
| 0.50 | 154 | 33.77% | 55.91% | 46.39% | 0.4943 | False |
| 0.55 | 120 | 32.50% | 41.94% | 36.14% | 0.3963 | False |
| 0.60 | 83 | 32.53% | 29.03% | 25.00% | 0.2967 | False |

## Governance

2023-2024 selected the threshold. 2025 was the untouched confirmation. 2026 was evaluated only if the frozen 2025 gate passed. No 2026 outcome changed source alignment, features, model or threshold.
OPA is options-positioning asymmetry, not implied-volatility skew and not CME CVOL.
