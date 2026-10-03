# FLOW-VOL-H3 V1 — RESULT

**Status:** **NO_ELIGIBLE_FLOW_VOL_THRESHOLD**  
**Source:** Yahoo Finance GC=F daily volume proxy, host query1.finance.yahoo.com  
**PIT:** strict prior-trade-date volume only; same-day forbidden.

## DEV threshold grid

| Threshold | Candidate | Precision | Recall | Rate | F2 | Eligible |
|---:|---:|---:|---:|---:|---:|---|
| 0.35 | 380 | 28.95% | 99.10% | 97.94% | 0.6675 | False |
| 0.40 | 367 | 28.61% | 94.59% | 94.59% | 0.6473 | False |
| 0.45 | 307 | 27.69% | 76.58% | 79.12% | 0.5659 | False |
| 0.50 | 179 | 30.73% | 49.55% | 46.13% | 0.4414 | False |
| 0.55 | 56 | 32.14% | 16.22% | 14.43% | 0.1800 | False |

## Governance

FLOW-VOL is an ablation only. It does not replace the blocked official Volume+OI FLOW-H3 V1 and does not alter HELIOS V5-DCE. 2026 was opened only if the preregistered 2025 confirmation gate passed.
