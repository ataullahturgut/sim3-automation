# GOLD MONTHLY — Transition / Change Detector V2 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / HISTORICAL-CALIBRATION TRANSITION DETECTOR  
**Parent:** Transition Detector V1

## 1. Purpose

V1 showed that generic anomaly/surprise signals are not equivalent to regime transition. V2 therefore removes emission surprise, predictive surprise, raw jump magnitude and raw latent-state switch from the transition decision.

V2 asks only:

> Is the incumbent semantic regime losing posterior support persistently and directionally, with movement toward an alternative semantic regime / away from the incumbent prototype?

V2 does not predict the next regime and does not use gold-forecast outcomes.

## 2. Frozen development / validation / inspection periods

Threshold/rule calibration authority:
- **2015-07..2021-12 only**
- primary schedule for calibration: **EXPANDING_REFIT + prototype semantic mapping**

Post-calibration validation:
- **2022-01..2024-12**

Already-opened inspection/transport:
- **2025-01..2026-08**
- this period is not untouched and must not be described as such.

The final calibrated V2 rule is frozen before any 2022+ metrics are computed.

ANNUAL_ANCHORED is a secondary schedule comparison and uses the exact same rule selected on expanding 2015-2021. It is not separately tuned.

## 3. Underlying regime engines

Exactly reproduce Prototype Alignment V1:
- K=3;
- 13 market-state features;
- frozen 2010-2024 semantic R0/R1/R2 prototypes;
- posterior-weighted latent-state profiles;
- Hungarian one-to-one semantic mapping.

No HMM/scaler/PCA parameter is altered by V2.

## 4. Directional transition features

All posterior changes for month t are computed within the HMM fit available at t.

Let the incumbent semantic regime be the semantic state with highest posterior at t-1.

### F1 — incumbent posterior drop
`drop = p_inc(t-1) - p_inc(t)`

### F2 — incumbent-vs-alternative semantic margin
`margin(t) = p_inc(t) - max_{r != inc} p_r(t)`

Lower/negative margin means the incumbent is losing dominance.

### F3 — margin collapse
`margin_drop = margin(t-1) - margin(t)`

### F4 — alternative-regime growth
`alt_growth = max_alt(t) - max_alt(t-1)`

### F5 — prototype-advantage deterioration

Using frozen 2010-2024 13D standardized semantic prototypes:
- `d_inc(t)` = Euclidean distance of current 13D market vector to incumbent prototype;
- `d_alt(t)` = distance to nearest alternative prototype;
- `proto_adv(t) = d_alt(t) - d_inc(t)`.

Positive = incumbent prototype is closer.

`proto_drop = proto_adv(t-1) - proto_adv(t)`

Positive means the observation is moving away from the incumbent prototype toward an alternative.

## 5. Persistence

For each t also compute the same directional evidence for interval t-2 -> t-1 under the same fit available at t.

This produces:
- current directional vote count;
- previous directional vote count.

No future month is used.

## 6. Candidate rule family

A directional vote is counted for:
- F1 >= `drop_thr`
- F3 >= `margin_drop_thr`
- F4 >= `alt_growth_thr`
- F5 >= `proto_drop_thr`

Candidate thresholds:

- `drop_thr`: 0.10, 0.15, 0.20, 0.25
- `margin_thr`: 0.15, 0.25, 0.35, 0.45
- `margin_drop_thr`: 0.15, 0.25, 0.35, 0.45
- `alt_growth_thr`: 0.10, 0.15, 0.20, 0.25
- `proto_drop_thr`: 0.25, 0.50, 0.75, 1.00
- `fast_votes`: 2 or 3
- `persistent_votes`: 1 or 2
- `persistent_margin_thr`: 0.30, 0.45, 0.60

Rule:

**FAST transition**
- current margin <= margin_thr; and
- current directional votes >= fast_votes.

**PERSISTENT transition**
- current margin <= persistent_margin_thr; and
- current directional votes >= persistent_votes; and
- previous-interval directional votes >= persistent_votes.

Final:
- TRANSITION = FAST OR PERSISTENT.
- otherwise STABLE.

Generic anomaly/surprise variables are logged for later Regime-Extreme work if available, but they do not vote in V2.

## 7. Historical calibration objective

Reference transition zones use the same Discovery V1 definition as V1:
- BELIRSIZ bridges are included;
- zone begins the month after the last confident old-regime month;
- zone ends at the first confident new-regime month inclusive.

Search all candidate rules on **EXPANDING_REFIT 2015-07..2021-12 only**.

Selection order:

1. Eligible set: event-level transition hit rate >= **2/3**.
2. Among eligible, minimize non-zone false-transition rate.
3. Tie-break: maximize precision.
4. Then maximize transition-zone recall.
5. Then maximize mean lead before confirmation among hit events.
6. Final deterministic tie-break: lexicographic parameter tuple.

Fallback if no candidate reaches 2/3 event hit:
1. maximize event-hit rate;
2. minimize false-transition rate;
3. maximize precision;
4. maximize zone recall;
5. deterministic lexicographic tie-break.

No 2022+ result may enter rule selection.

## 8. Required post-freeze reporting

After the rule is selected and frozen, report separately:

### Historical calibration
- 2015-07..2021-12

### Later validation
- 2022-01..2024-12

### Opened transport/inspection
- 2025-01..2026-08

### Full descriptive replay
- 2015-07..2026-08

For EXPANDING_REFIT and ANNUAL_ANCHORED:
- transition flags / flag rate;
- transition-zone recall;
- event hit rate;
- non-zone false-transition rate;
- precision;
- first in-zone flag and lead to confirmation for every reference event.

## 9. Mandatory checkpoints

Report:
- 2024-03..2024-06
- 2026-04..2026-08

V2 is not tuned to force a 2026-05 flag.

The important question is whether persistence/directional evidence reduces false transitions while preserving useful detection of 2024 and the 2026 transition zone.

## 10. Promotion rule

V2 may be considered a regime-engine candidate only if the **2022-2024 later validation** shows:
- event hit rate >= 2/3;
- non-zone false-transition rate <= 15%;
- and precision at least **5 percentage points above** V1's 2022-2024 result.

2025/2026 may be described only after this validation decision is frozen.

If V2 fails validation, do not retune on 2022-2026. Move to a structurally different transition model or accept that current monthly variables do not support sufficiently selective transition detection.

## 11. Governance

Forbidden in calibration and detection:
- ChHHO forecasts;
- ChHHO errors;
- any alarm flags;
- HIGH/MEDIUM/NORMAL labels;
- forecast routing/model-switch outcomes;
- future market observations.

No alarm selection, weighting, suppression, forecast correction or routing is authorized by V2.
