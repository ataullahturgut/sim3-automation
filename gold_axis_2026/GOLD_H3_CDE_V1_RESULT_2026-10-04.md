# CDE-H3 V1 — COUNTERFACTUAL DISLOCATION EXCEPTION RESULT

**Status:** **CDE_H3_V1_FAIL**  
**Evidence:** retrospective development only.

- complete eligible rows: **676**
- coverage: **2023-06-01 .. 2026-09-24**
- chronology/leakage failures: **0**

## Aggregate CDE

- candidates: **109 (16.12%)**
- rescue / broken / net: **36 / 73 / -37**
- precision: **33.03%**
- V5 -> CDE-assisted: **68.49% -> 63.02%**
- OPAL-no-candidate missed reversals hit: **34/191**

## Half-year stability

| Block | N | Cand | Rescue | Broken | Net | Precision | V5 acc | Assisted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023_H1 | 19 | 1 | 0 | 1 | -1 | 0.0% | 78.9% | 73.7% |
| 2023_H2 | 96 | 10 | 3 | 7 | -4 | 30.0% | 71.9% | 67.7% |
| 2024_H1 | 90 | 14 | 5 | 9 | -4 | 35.7% | 74.4% | 70.0% |
| 2024_H2 | 107 | 20 | 7 | 13 | -6 | 35.0% | 69.2% | 63.6% |
| 2025_H1 | 102 | 20 | 9 | 11 | -2 | 45.0% | 60.8% | 58.8% |
| 2025_H2 | 109 | 17 | 5 | 12 | -7 | 29.4% | 74.3% | 67.9% |
| 2026_H1 | 109 | 20 | 6 | 14 | -8 | 30.0% | 63.3% | 56.0% |
| 2026_H2 | 44 | 7 | 1 | 6 | -5 | 14.3% | 59.1% | 47.7% |

## Complementarity vs frozen OCS (common mature coverage)

- common rows: **252**
- cde_only: **41** candidates, rescue/broken/net **12/29/-17**, precision **29.3%**
- ocs_only: **6** candidates, rescue/broken/net **6/0/+6**, precision **100.0%**
- overlap: **1** candidates, rescue/broken/net **0/1/-1**, precision **0.0%**
- union: **48** candidates, rescue/broken/net **18/30/-12**, precision **37.5%**
- incremental true CDE-only rescues: **12**

## Gate

- non-negative blocks: **0/8** (required 6)
- positive blocks: **0/8** (required 4)
- worst block net: **-8**
- CDE failed the frozen development gate.
- The 5/6 concurrence and signs must not be retuned on this same replay.
