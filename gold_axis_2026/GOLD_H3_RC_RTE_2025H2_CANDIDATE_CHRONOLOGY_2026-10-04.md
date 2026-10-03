# RC-RTE 2025 H2 — CANDIDATE CHRONOLOGY

- enabled regimes from pre-H2 training: **[0, 2]**
- static candidates: **20**
- rescue / broken / net: **6 / 14 / -8**

## Pre-H2 regime audit

| Regime | Support | Rescue | Broken | Net | Precision | Enabled |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 20 | 14 | 6 | +8 | 70.0% | True |
| 1 | 14 | 7 | 7 | +0 | 50.0% | False |
| 2 | 28 | 17 | 11 | +6 | 60.7% | True |

## Candidate sequence

| Issue | End | Regime | SB | OPT | MAT | Effect | Cum net | Matured regime n | Matured regime net | Last5 net |
|---|---|---:|---|---|---|---|---:|---:|---:|---:|
| 2025-07-07 | 2025-07-09 | 0 | False | True | False | BROKEN | -1 | 0 | +0 | +0 |
| 2025-07-08 | 2025-07-10 | 0 | False | False | True | BROKEN | -2 | 0 | +0 | +0 |
| 2025-07-25 | 2025-07-29 | 2 | False | True | False | BROKEN | -3 | 0 | +0 | +0 |
| 2025-08-12 | 2025-08-14 | 2 | False | True | False | BROKEN | -4 | 1 | -1 | -1 |
| 2025-09-11 | 2025-09-15 | 2 | False | True | False | BROKEN | -5 | 2 | -2 | -2 |
| 2025-09-19 | 2025-09-23 | 2 | False | True | False | RESCUE | -4 | 3 | -3 | -3 |
| 2025-10-02 | 2025-10-06 | 2 | False | True | False | RESCUE | -3 | 4 | -2 | -2 |
| 2025-10-24 | 2025-10-28 | 2 | False | True | False | RESCUE | -2 | 5 | -1 | -1 |
| 2025-11-03 | 2025-11-05 | 0 | False | True | True | BROKEN | -3 | 2 | -2 | -2 |
| 2025-11-10 | 2025-11-12 | 0 | False | True | True | RESCUE | -2 | 3 | -3 | -3 |
| 2025-11-18 | 2025-11-20 | 0 | False | True | False | BROKEN | -3 | 4 | -2 | -2 |
| 2025-11-20 | 2025-11-24 | 0 | False | True | True | BROKEN | -4 | 4 | -2 | -2 |
| 2025-11-26 | 2025-11-28 | 0 | False | False | True | BROKEN | -5 | 6 | -4 | -3 |
| 2025-11-27 | 2025-12-01 | 0 | True | False | False | BROKEN | -6 | 6 | -4 | -3 |
| 2025-12-02 | 2025-12-04 | 0 | False | True | True | BROKEN | -7 | 8 | -6 | -3 |
| 2025-12-04 | 2025-12-08 | 0 | False | False | True | BROKEN | -8 | 8 | -6 | -3 |
| 2025-12-05 | 2025-12-09 | 0 | True | False | False | BROKEN | -9 | 9 | -7 | -5 |
| 2025-12-09 | 2025-12-11 | 0 | False | True | False | RESCUE | -8 | 10 | -8 | -5 |
| 2025-12-29 | 2025-12-31 | 2 | False | True | False | BROKEN | -9 | 6 | +0 | +1 |
| 2025-12-31 | 2026-01-05 | 2 | False | True | False | RESCUE | -8 | 6 | +0 | +1 |
