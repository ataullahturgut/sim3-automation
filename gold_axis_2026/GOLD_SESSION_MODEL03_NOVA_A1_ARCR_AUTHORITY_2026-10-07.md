# SESSION MODEL-03 — NOVA A1 / ARCR — IDENTITY + FEATURE-SELECTION AUTHORITY

**Date:** 2026-10-07  
**Status:** BASELINE COMPLETE / FEATURE-SELECTED CHALLENGER DIAGNOSTIC COMPLETE

## Baseline identity

The existing raw session replay is accepted as the authoritative SESSION Model-03 baseline:

- model: NOVA A1 / ARCR
- mixture: 0.75 global CORE3 + 0.25 recent252 balanced CORE3
- global head: StandardScaler + LogisticRegression(L2, C=1.0)
- recent head: StandardScaler + LogisticRegression(L2, C=1.0, class_weight=balanced)
- recent window: 252 matured same-window rows
- threshold: 0.50
- daily source-ready rule: strictly earlier America/New_York calendar date
- V5 session target reproduction: PASS
- 2025 identity audit: 1,061 matched rows; maximum probability difference 2.7e-13

No duplicate baseline rerun is required.

## Model-specific feature-selection challenger

Authority:
- `GOLD_SESSION_MODEL03B_NOVA_A1_ARCR_FEATURE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_MODEL03B_A1_FEATURE_SELECTION_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL03B_A1_FEATURE_SELECTION_2025_METRICS_2026-10-07.csv`
- `GOLD_SESSION_MODEL03B_A1_FEATURE_SELECTION_FROZEN_FEATURES_2026-10-07.json`

Candidate features:
- daily CORE3;
- exact pre-session XAU15 momentum / realized-volatility / semivolatility / shape state.

Clock gate:
- every XAU15 input is available strictly before the relevant session start;
- equality at target_start is rejected;
- no target-window observation is used;
- 2025 does not select variables;
- 2026 is unopened.

## Exact-common-row 2025 comparison

| Session | Baseline A1 BA | Selected A1 BA | Delta BA | Baseline Brier | Selected Brier | Decision |
|---|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 56.70% | 50.54% | -6.16 pp | 0.2453 | 0.2621 | reject selected |
| Sobti Asia Morning | 53.29% | 49.49% | -3.80 pp | 0.2606 | 0.2662 | reject selected |
| Sobti Europe | 50.40% | 43.85% | -6.55 pp | 0.2600 | 0.2616 | reject selected |
| Sobti NY/London | 49.08% | 46.95% | -2.13 pp | 0.2616 | 0.2668 | reject selected |
| Sobti Late-US | 51.99% | 50.44% | -1.55 pp | 0.2590 | 0.2405 | reject: BA lower and DOWN recall 20% |
| WGC Asia | 50.97% | **54.03%** | **+3.06 pp** | 0.2654 | **0.2572** | retain as limited-coverage challenger |
| WGC Europe | 51.78% | 50.62% | -1.16 pp | 0.2623 | 0.2642 | reject selected |
| WGC US | 44.42% | 39.57% | -4.85 pp | 0.2748 | 0.2668 | reject: directional skill worse |

## Coverage caution

The selected challenger requires XAU15 feature availability and therefore is evaluated on a smaller exact-common-row population than the full daily A1 baseline. For example, WGC Asia selected-A1 transport covers 107 rows versus 253 rows in the full 2025 A1 baseline transport.

Therefore:
- selected-A1 does **not** replace baseline A1 globally;
- selected-A1 does **not** become a universal session head;
- WGC Asia selected-A1 may be retained only as a limited-coverage candidate for later routing/consensus analysis;
- no fallback for non-common rows is created here.

## Binding Model-03 verdict

1. **SESSION Model-03 baseline A1/ARCR = COMPLETE / ACCEPTED.**
2. Baseline A1 remains the canonical Model-03 representation.
3. Model-specific variable selection does not improve A1 broadly.
4. WGC Asia selected-A1 is retained as a narrow challenger only.
5. All other selected-A1 session variants are rejected.
6. No 2026 data were used.
7. The next primary model in the Stage-1 lineage is IRIS HOURLY_ONLY / PATH_GLOBAL, subject to the existing raw-source identity/replay evidence.
