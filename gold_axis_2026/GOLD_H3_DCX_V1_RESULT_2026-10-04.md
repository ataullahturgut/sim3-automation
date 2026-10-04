# DCX-H3 V1 — DIRECTIONAL-CHANGE OVERSHOOT EXHAUSTION RESULT

**Status:** **DCX_H3_V1_FAIL**  
**Evidence:** retrospective development/stress-test only.

- hourly GC rows: **10067**
- origin feature rows: **417**
- development rows: **309**
- issue dates: **2025-07-01 .. 2026-09-25**
- integrity/timeline failures: **0**

## DCX

- candidates: **4**
- rescue / broken / net: **1 / 3 / -2**
- precision: **25.00%**
- candidate rate: **1.57%**
- V5 -> DCX-assisted accuracy: **66.02% -> 65.37%**

## Increment over OCS

- OCS reference: **7 candidates, net +5, precision 85.71%**
- DCX-only: **4 candidates, 1/3, net -2**
- OCS-only: **7 candidates, 6/1, net +5**
- overlap: **0 candidates, net +0**
- union: **11 candidates, net +3, precision 63.64%**
- V5 -> union-assisted accuracy: **66.02% -> 66.99%**

## Half-year stability

| Block | Cand | Rescue | Broken | Net | Precision | V5 acc | DCX acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025_H2 | 1 | 0 | 1 | -1 | 0.0% | 69.0% | 68.3% |
| 2026_H1 | 2 | 1 | 1 | +0 | 50.0% | 66.4% | 66.4% |
| 2026_H2 | 1 | 0 | 1 | -1 | 0.0% | 59.0% | 57.4% |

## Gate

- positive blocks: **0/3**
- worst block net: **-1**
- DCX-only marginal net: **-2**
- union net vs OCS: **+3 vs +5**
- DCX V1 failed at least one frozen development criterion.
- Do not tune delta, rank or retracement thresholds on this same replay.
