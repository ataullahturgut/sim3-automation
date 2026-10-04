# TPC-H3 V1 — TEMPORAL PROPAGATION CONCURRENCE RESULT

**Status:** **TPC_H3_V1_FAIL**  
**Evidence:** retrospective development/stress-test only.

- common rows: **252**
- issue dates: **2025-07-01 .. 2026-09-25**
- identity mismatches: **0**
- leakage failures: **0**

## TPC

- candidates: **23**
- rescue / broken / net: **9 / 14 / -5**
- precision: **39.13%**
- candidate rate: **9.13%**
- V5 -> TPC-assisted accuracy: **66.67% -> 64.68%**

## Increment over OCS

- OCS reference: **7 candidates, net +5, precision 85.71%**
- TPC-only: **20 candidates, 7/13, net -6**
- OCS-only: **4 candidates, 4/0, net +4**
- overlap: **3 candidates, net +1**
- union: **27 candidates, net -1, precision 48.15%**
- V5 -> union-assisted accuracy: **66.67% -> 66.27%**

## Half-year stability

| Block | Eligible | Cand | Rescue | Broken | Net | Precision | V5 acc | TPC acc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025_H2 | 105 | 7 | 3 | 4 | -1 | 42.9% | 73.3% | 72.4% |
| 2026_H1 | 104 | 11 | 3 | 8 | -5 | 27.3% | 63.5% | 58.7% |
| 2026_H2 | 43 | 5 | 3 | 2 | +1 | 60.0% | 58.1% | 60.5% |

## Gate

- positive blocks: **1/3**
- worst block net: **-5**
- TPC-only marginal net over OCS: **-6**
- union net vs OCS: **-1 vs +5**
- TPC V1 failed at least one frozen development criterion.
- Do not tune propagation_count or component signs on this replay.
