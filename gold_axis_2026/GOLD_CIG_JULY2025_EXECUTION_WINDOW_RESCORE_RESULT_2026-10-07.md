# GOLD CIG-D1 — JULY 2025 EXECUTION-WINDOW RESCORE

**Status:** retrospective diagnostic only; no model retraining, no threshold tuning, no new consensus.

Old CIG-D1 signal states are held fixed and rescored against the two current investment objectives.

## Window definitions

- DAY: 09:00 Europe/Istanbul OPEN -> 16:45 CLOSE (17:00 boundary).
- OVERNIGHT-HOLD: 17:00 Europe/Istanbul OPEN -> next available trading date 08:45 CLOSE (09:00 boundary).

## Summary

- July signal rows: **23**
- old CIG 4/4 consensus rows: **18**
- UNCERTAIN rows: **5**
- consensus coverage: **78.26%**
- old state available by 09:00 TRT on all consensus rows: **True**
- DAY: **11/18 = 61.11%**, BA **62.99%**
- OVERNIGHT: **7/18 = 38.89%**, BA **37.01%**
- same old signal correct on BOTH windows: **4/18 = 22.22%**

## Daily rows

| Date | Old CIG | DAY actual | DAY correct | Overnight actual | Overnight correct |
|---|---|---|---:|---|---:|
| 2025-07-01 | UP | UP | YES | DOWN | NO |
| 2025-07-02 | UNCERTAIN | DOWN |  | UP |  |
| 2025-07-03 | UP | DOWN | NO | UP | YES |
| 2025-07-04 | DOWN | DOWN | YES | UP | NO |
| 2025-07-07 | DOWN | UP | NO | UP | NO |
| 2025-07-08 | UP | DOWN | NO | DOWN | NO |
| 2025-07-09 | DOWN | UP | NO | UP | NO |
| 2025-07-10 | UP | DOWN | NO | UP | YES |
| 2025-07-11 | UP | UP | YES | UP | YES |
| 2025-07-14 | UP | DOWN | NO | UP | YES |
| 2025-07-15 | DOWN | DOWN | YES | DOWN | YES |
| 2025-07-16 | DOWN | DOWN | YES | UP | NO |
| 2025-07-17 | UNCERTAIN | DOWN |  | UP |  |
| 2025-07-18 | UP | UP | YES | DOWN | NO |
| 2025-07-21 | UP | UP | YES | DOWN | NO |
| 2025-07-22 | UP | UP | YES | UP | YES |
| 2025-07-23 | UP | DOWN | NO | DOWN | NO |
| 2025-07-24 | DOWN | DOWN | YES | DOWN | YES |
| 2025-07-25 | DOWN | DOWN | YES | UP | NO |
| 2025-07-28 | UNCERTAIN | DOWN |  | UP |  |
| 2025-07-29 | DOWN | DOWN | YES | UP | NO |
| 2025-07-30 | UNCERTAIN | DOWN |  | DOWN |  |
| 2025-07-31 | UNCERTAIN | UP |  | DOWN |  |

## Interpretation guardrail

This test answers only: if the historical old CIG state were reused unchanged, how often would its direction match the two new execution-aligned windows in July 2025? It does not validate a new DAY/OVERNIGHT model and it must not be used as untouched OOS evidence for selecting a new policy.
