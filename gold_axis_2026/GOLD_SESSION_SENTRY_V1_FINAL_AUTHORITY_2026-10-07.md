# SESSION SENTRY V1 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / NOT PROMOTED

## Identity

SESSION SENTRY V1 is a causal hard router between:

- `S14_A1_PLUS_1H_FULL` — canonical Structural-IRIS
- `PATH_GLOBAL_1H` — canonical hourly PATH expert

State is independent for each partition/window.

Frozen rule:
- latest 63 matured exact-common-row paired forecasts;
- minimum matured pairs = 42;
- enter PATH when `net_rescue_63 >= +3`;
- return to Structural when `net_rescue_63 <= 0`;
- initial state = Structural-IRIS.

Only rows with `end_utc <= current start_utc` may contribute to the paired correctness state.

No H3 SENTRY/AURORA ledger is consumed as model input.

## Development gate

Pre-2025 results:

| Session | N | SENTRY BA | Structural BA | UP recall | DOWN recall | Switches | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 175 | 52.76% | 52.76% | 50.53% | 55.00% | 0 | FAIL — no switch |
| Sobti Asia Morning | 170 | 45.83% | 49.77% | 50.00% | 41.67% | 4 | FAIL |
| Sobti Europe | 189 | **49.10%** | 48.71% | 67.96% | 30.23% | 4 | **PASS** |
| Sobti NY/London | 190 | 51.65% | 53.26% | 48.45% | 54.84% | 2 | FAIL |
| Sobti Late-US | 89 | 50.05% | 50.05% | 70.83% | 29.27% | 0 | FAIL |
| WGC Asia | 102 | 47.36% | 47.36% | 82.61% | 12.12% | 0 | FAIL |
| WGC Europe | 189 | 51.04% | 52.12% | 69.16% | 32.93% | 2 | FAIL |
| WGC US | 162 | 47.73% | 47.97% | 39.76% | 55.70% | 2 | FAIL |

Only Sobti Europe was legitimately opened in 2025.

## Frozen 2025 transport — Sobti Europe

N = 144.

### Structural-IRIS
- Accuracy = 50.69%
- Balanced Accuracy = 45.71%
- UP recall = 65/83 = 78.31%
- DOWN recall = 8/61 = 13.11%
- Brier = 0.2631

### PATH_GLOBAL
- Accuracy = 54.17%
- Balanced Accuracy = 51.12%
- UP recall = 59/83 = 71.08%
- DOWN recall = 19/61 = 31.15%
- Brier = 0.2627

### SENTRY
- Accuracy = 53.47%
- Balanced Accuracy = 49.43%
- UP recall = 63/83 = 75.90%
- DOWN recall = 14/61 = 22.95%
- Brier = 0.2590

SENTRY made one additional Structural -> PATH transition in 2025:
- 2025-09-12, net_rescue_63 = +3.

## Binding decision

1. SESSION SENTRY identity and chronology are valid.
2. Only Sobti Europe passed the frozen 2023–2024 gate.
3. In 2025, SENTRY improves on Structural-IRIS but does not beat PATH_GLOBAL in Balanced Accuracy.
4. SENTRY 2025 DOWN recall = 22.95%, below the binding 30% class-recall floor.
5. Therefore **SENTRY is not promoted** as a session router.
6. Its state history remains valid upstream evidence for DART/AURORA reconstruction, but SENTRY itself is not a primary selected head.
7. No threshold, window or state rule was retuned from 2025.
8. 2026 remains unopened.
9. Next dependency model: **SESSION DART**.
