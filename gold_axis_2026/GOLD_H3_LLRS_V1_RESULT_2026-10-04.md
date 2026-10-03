# LLRS-H3 V1 — LEAD-LAG REPRICING STRESS RESULT

**Status:** **NO_ELIGIBLE_LLRS_V1_MECHANISM**  
**Evidence:** retrospective hourly-futures proxy mechanism; not a clean historical holdout.

## Hourly synchronized coverage

- synchronized rows: **9853**
- first / last UTC: **2025-01-02 05:00:00+00:00 / 2026-10-02 20:00:00+00:00**
- H3 origins scored: **332**

## Mechanism anatomy

| Block | n | Reversals | Reversal pressure med | Continuation med | Pressure SMD | AUC | Incremental SMD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025_H1 | 77 | 32 | 0.010 | -0.004 | -0.104 | 0.495 | -0.110 |
| 2025_H2 | 108 | 28 | 0.011 | -0.075 | +0.553 | 0.636 | +0.202 |
| 2026_H1 | 104 | 38 | -0.032 | 0.006 | -0.176 | 0.433 | -0.051 |
| 2026_H2 | 43 | 18 | 0.049 | -0.103 | +0.647 | 0.687 | +0.693 |

## Frozen candidate grid

| q | Cand | Rescue | Broken | Net | Precision | Recall | Rate | + blocks | Worst | Eligible |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.25 | 35 | 11 | 24 | -13 | 31.43% | 9.48% | 10.54% | 0 | -11 | False |
| 0.50 | 2 | 0 | 2 | -2 | 0.00% | 0.00% | 0.60% | 0 | -1 | False |
| 0.75 | 2 | 0 | 2 | -2 | 0.00% | 0.00% | 0.60% | 0 | -1 | False |
| 1.00 | 1 | 0 | 1 | -1 | 0.00% | 0.00% | 0.30% | 0 | -1 | False |

## Governance

Historical 2025-2026 is development/stress-test evidence. A successful mechanism may only become a shadow prospective challenger from the post-freeze period. Yahoo hourly futures are research proxies; production use requires an authoritative prospective source.
