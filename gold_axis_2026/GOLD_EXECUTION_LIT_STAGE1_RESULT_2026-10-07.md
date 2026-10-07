# GOLD EXECUTION LITERATURE STAGE-1 RESULT — 2026-10-07

**Status:** COMPLETE / LOW-CAPACITY MECHANISM TEST

No 2025 result was used to choose an interval, sign, threshold or model family.

## OVERNIGHT 17:00 -> next 09:00

| Spec | DEV BA | DEV R2_OS | 2023 BA | 2024 BA | 2025 BA | 2025 Acc |
|---|---:|---:|---:|---:|---:|---:|
| LIT_OVN0_1530_1600 | 50.63% | -0.18% | 53.21% | 47.79% | 49.68% | 56.69% |
| LIT_OVN0_1600_1630 | 50.45% | 0.78% | 49.06% | 51.51% | 55.11% | 59.06% |
| LIT_OVN0_1630_1700 | 48.90% | -0.26% | 47.73% | 50.00% | 50.23% | 57.25% |
| LIT_OVN1_PAIR | 49.55% | 0.51% | 47.36% | 51.50% | 50.12% | 52.17% |

Development-only OVN0 leader: **LIT_OVN0_1530_1600**.
OVN0 stability gate: **False**.
OVN1 pair stability gate: **False**.

## DAY

| Spec | Target | DEV BA | DEV R2_OS | 2023 BA | 2024 BA | 2025 BA | 2025 Acc |
|---|---|---:|---:|---:|---:|---:|---:|
| LIT_DAY0_EXEC_0900 | DAY | 47.32% | -1.25% | 46.55% | 47.46% | 44.11% | 45.38% |
| LIT_DAY1_DELAY_0930 | DAYD | 52.01% | -0.61% | 51.58% | 50.58% | 51.60% | 58.42% |

LIT_DAY1_DELAY_0930 is a 09:30 decision challenger only; it is not a 09:00 backtest.
LIT-OVN-2 state conditioning is allowed only if Stage-1 development evidence is coherent; no extra half-hour mining is allowed.
