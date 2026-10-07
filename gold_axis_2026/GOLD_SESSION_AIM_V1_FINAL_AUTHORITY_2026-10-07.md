# SESSION AIM V1 — FINAL AUTHORITY

**Date:** 2026-10-07
**Status:** COMPLETE / TRANSPORT FAILED / NOT RETAINED AS DIRECTION COMBINER

## Identity

SESSION AIM V1 is a performance-adaptive mixture of three fresh session experts:

1. STRUCTURAL_IRIS = `S14_A1_PLUS_1H_FULL`
2. PATH_GLOBAL = `PATH_GLOBAL_1H`
3. PATH_RECENT126 = balanced Logistic on canonical 1h PATH features using the latest 126 matured same-window rows

Adaptive weights are based only on already-matured OOS Brier losses.

Frozen grid:
- half-life = 21 / 63 / 126 matured forecasts
- eta = 10 / 20 / 40

If fewer than 30 matured OOS expert forecasts are available, equal one-third weights are used.

## Development selection

Three heads had an eligible combined-development configuration:

### Sobti Asia Morning
Selected:
- half-life = 63
- eta = 40

Year confirmation:
- 2023 N=34: Structural BA 52.98% -> AIM BA 57.02%; PASS
- 2024 N=136: Structural BA 48.90% -> AIM BA 53.92%; PASS

This was the only fully year-confirmed session head.

### WGC Europe
Selected:
- half-life = 126
- eta = 10

Year confirmation:
- 2023 N=41: Structural BA 58.33% -> AIM BA 48.69%; FAIL
- 2024 N=148: Structural BA 49.98% -> AIM BA 56.79%; PASS

Not transport-eligible.

### WGC US
Selected:
- half-life = 126
- eta = 20

Year confirmation:
- 2023 N=20: insufficient year confirmation
- 2024 N=142: Structural BA 47.89% -> AIM BA 51.59%; PASS

Not transport-eligible.

## Frozen 2025 transport — Sobti Asia Morning

N = 140

Structural-IRIS:
- Accuracy = 60.71%
- Balanced Accuracy = 60.86%
- UP recall = 43/67 = 64.18%
- DOWN recall = 42/73 = 57.53%
- Brier = 0.2557

AIM:
- Accuracy = 59.29%
- Balanced Accuracy = 59.43%
- UP recall = 42/67 = 62.69%
- DOWN recall = 41/73 = 56.16%
- Brier = 0.2621

Changed calls:
- 6
- rescued = 2
- broken = 4
- net rescue = -2

Mean 2025 adaptive weights:
- Structural = 37.2%
- PATH_GLOBAL = 53.9%
- PATH_RECENT126 = 8.9%

## Binding decision

1. SESSION AIM V1 is complete and leakage-safe.
2. Sobti Asia Morning is the only session to pass development plus year-stability confirmation.
3. Frozen 2025 transport deteriorates versus Structural-IRIS in BA, both class recalls, Brier and net rescue.
4. AIM is therefore not retained as a primary/session direction combiner.
5. Its adaptive weight ledger remains diagnostic router-state evidence only.
6. WGC Europe and WGC US remain development diagnostics but were never opened in 2025.
7. No 2025 retuning occurred.
8. 2026 remains unopened.
