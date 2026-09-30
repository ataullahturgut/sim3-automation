# GOLD MONTHLY — Contextual HIGH-Alarm Rescueability Analysis V1 Authority

**Date:** 2026-10-01  
**Status:** ANALYSIS AUTHORITY / NO SWITCH / NO BLEND / NO PRODUCTION RULE

## 1. Question

The frozen Specialist Hedge router can warn that the main ChHHO point forecast is at elevated error risk. This study asks a separate question:

> When the router warns, is the ChHHO error actually rescueable by one or more already-frozen competitive models, and does rescue structure vary with the origin-known market-state context?

This is an anatomy / rescueability study. It does not authorize a rescue router.

## 2. Frozen inputs

Alarm layer:
- Specialist Hedge V1
- eta = 0.25
- alpha = 0
- HIGH threshold tau = 0.50
- frozen experts A/B/C/D/E/G/H/I1/I2/T1_WGC/V2_TRANSITION + NULL.

Competitive model pool:
- exact original 16-model pool from Cross-Model Error Overlap / Exact16 work;
- no new challenger may be added after seeing results.

Market-state context:
- primary EXPANDING_REFIT rows from Market-State × ChHHO Reliability Audit V1;
- semantic R0/R1/R2/BELIRSIZ label and confidence;
- state category NORMAL / EXTREME / TRANSITION / DEFER;
- V2 status;
- OOD flag.

Cross-model geometry:
- exact16 direction agreement and dispersion are diagnostic context only;
- they are not used as a hard veto.

## 3. Chronology and coverage

Primary historical analysis:
- DEV targets 2022-04..2024-12.

Opened descriptive transport:
- 2025-01..2026-07 where the exact 16-model transport panel exists.
- 2026-08 is reported as a coverage boundary and is not imputed.

2025/2026 is already opened and may not be used to select thresholds, models, rescue rules, or production actions.

## 4. Rescue measurements

For each frozen router warning (p_HIGH >= 0.50), calculate:

- ChHHO AE;
- every alternative model AE;
- best alternative AE and model;
- best alternative gain = ChHHO AE - best alternative AE;
- best gain as fraction of ChHHO AE;
- number of 15 alternatives beating ChHHO;
- number of alternatives producing at least 25% AE reduction;
- median alternative AE;
- exact16 direction agreement and forecast dispersion;
- origin-known regime / transition / extreme / OOD context.

## 5. Descriptive taxonomy only

This taxonomy is for interpretation, not model selection.

- FALSE_ALARM: router warning but realized ChHHO severity is NORMAL.
- SHARED_HARD_OR_SHALLOW: realized severity HIGH/MEDIUM and even the best alternative reduces ChHHO AE by less than 25%.
- BROAD_MATERIAL_RESCUE: HIGH/MEDIUM; at least 8/15 alternatives beat ChHHO; at least 4 alternatives reduce AE by >=25%; best alternative reduction >=25%.
- BROAD_RESCUE: HIGH/MEDIUM; at least 8/15 alternatives beat ChHHO and best alternative reduction >=25%, but fewer than 4 alternatives meet the 25% material-improvement condition.
- NARROW_MATERIAL_RESCUE: HIGH/MEDIUM; fewer than 8/15 alternatives beat ChHHO but the best alternative reduces AE by >=25%.

The 25% and majority criteria are descriptive bins. They do not become decision thresholds.

## 6. Mandatory diagnostics

Report separately:

1. DEV warning anatomy.
2. Opened 2025..2026-07 warning anatomy.
3. Fixed single-fallback retrospective performance on:
   - realized elevated warning months only;
   - all router-warning months, including false alarms.
4. Oracle headroom:
   - best alternative on every warning;
   - KEEP-or-best-alternative hindsight ceiling.
5. Rescue pattern by market-state context.
6. Critical case review:
   - 2025-02
   - 2025-09
   - 2026-01
   - 2026-03
   - 2026-06.

## 7. Scientific boundaries

Do not:
- retune Specialist Hedge;
- change alarm definitions;
- tune a rescue threshold;
- select a production fallback from 2025/2026;
- infer that a regime cell deterministically implies SWITCH or KEEP;
- use target-month market-state information;
- modify any price forecast.

A valid result may conclude that rescue headroom exists but is not yet origin-predictable.

## 8. Next-stage gate

This study may justify a later origin-safe rescueability predictor only if it shows meaningful rescue headroom and material heterogeneity between warning months.

Any later predictor must target relative loss / rescue gain, not re-fit the gold price target from scratch, and must preserve KEEP MAIN / abstention as valid actions.
