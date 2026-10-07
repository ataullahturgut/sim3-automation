# SESSION AURORA V1 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / NOT PROMOTED / FRESH SESSION UPSTREAM AVAILABLE

## Identity

SESSION AURORA V1 is the asymmetric hysteresis router between:

- `S14_A1_PLUS_1H_FULL` — canonical Structural-IRIS
- `PATH_GLOBAL_1H` — canonical hourly PATH expert

AURORA combines two frozen evidence mechanisms:

### Fast entry
SENTRY evidence:
- latest 63 matured exact-common-row pairs
- minimum 42
- enter PATH when `net_rescue_63 >= +3`

### Slow exit
DART evidence:
- minimum 8 matured expert disagreements
- return Structural when `Pr(PATH superior) <= 0.10`
- and `q_path <= 0.40`

Initial state:
- STRUCTURAL_IRIS

No new threshold is fitted.

All evidence is recomputed causally from corrected session expert rows. Archived H3 SENTRY/DART/AURORA ledgers are not model inputs.

## Development gate

| Session | N | AURORA BA | Structural BA | UP recall | DOWN recall | Switches | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 175 | 52.76% | 52.76% | 50.53% | 55.00% | 0 | FAIL — no switch |
| Sobti Asia Morning | 170 | 50.00% | 49.77% | 50.00% | 50.00% | 1 | PASS |
| Sobti Europe | 189 | 50.45% | 48.71% | 60.19% | 40.70% | 1 | PASS |
| Sobti NY/London | 190 | 51.65% | 53.26% | 48.45% | 54.84% | 2 | FAIL |
| Sobti Late-US | 89 | 50.05% | 50.05% | 70.83% | 29.27% | 0 | FAIL |
| WGC Asia | 102 | 47.36% | 47.36% | 82.61% | 12.12% | 0 | FAIL |
| WGC Europe | 189 | 49.78% | 52.12% | 65.42% | 34.15% | 1 | FAIL |
| WGC US | 162 | 43.90% | 47.97% | 40.96% | 46.84% | 2 | FAIL |

Only Sobti Asia Morning and Sobti Europe were legitimately opened in 2025.

## Frozen 2025 transport

### Sobti Asia Morning

N = 140

Structural-IRIS:
- Accuracy = 60.71%
- Balanced Accuracy = 60.86%
- UP recall = 43/67 = 64.18%
- DOWN recall = 42/73 = 57.53%
- Brier = 0.2557

PATH_GLOBAL:
- Accuracy = 53.57%
- Balanced Accuracy = 53.52%
- UP recall = 35/67 = 52.24%
- DOWN recall = 40/73 = 54.79%
- Brier = 0.2656

AURORA:
- Accuracy = 56.43%
- Balanced Accuracy = 56.50%
- UP recall = 39/67 = 58.21%
- DOWN recall = 40/73 = 54.79%
- Brier = 0.2698

State:
- entered PATH on 2024-01-25
- returned STRUCTURAL on 2025-05-21 after DART slow-exit evidence

Verdict:
- AURORA underperforms Structural-IRIS materially in 2025;
- not promoted.

### Sobti Europe

N = 144

Structural-IRIS:
- Accuracy = 50.69%
- Balanced Accuracy = 45.71%
- UP recall = 65/83 = 78.31%
- DOWN recall = 8/61 = 13.11%
- Brier = 0.2631

PATH_GLOBAL:
- Accuracy = 54.17%
- Balanced Accuracy = 51.12%
- UP recall = 59/83 = 71.08%
- DOWN recall = 19/61 = 31.15%
- Brier = 0.2627

AURORA:
- Accuracy = 54.17%
- Balanced Accuracy = 51.12%
- UP recall = 59/83 = 71.08%
- DOWN recall = 19/61 = 31.15%
- Brier = 0.2627

State:
- entered PATH on 2024-03-15
- remained PATH throughout 2025

Verdict:
- AURORA is identical to PATH_GLOBAL in 2025;
- it adds no incremental forecast value beyond the expert it selected.

## Binding decision

1. SESSION AURORA identity and chronology are valid.
2. AURORA is **not promoted** as a primary session router.
3. Sobti Asia Morning transports worse than Structural-IRIS.
4. Sobti Europe transports exactly as PATH_GLOBAL and therefore adds no incremental predictive value.
5. No thresholds or state rules were retuned using 2025.
6. 2026 remains unopened.
7. Crucially, a fresh causal **SESSION AURORA probability/state ledger now exists**.
8. Therefore the prior OPAL status `BLOCKED_UPSTREAM_AURORA` is resolved.
9. OPAL may now be reconstructed using:
   - corrected publication-time COT authority;
   - fresh session AURORA probability/state;
   - pre-target session momentum;
   - development-only gate;
   - frozen 2025 transport.
10. Next model: **SESSION OPAL**.
