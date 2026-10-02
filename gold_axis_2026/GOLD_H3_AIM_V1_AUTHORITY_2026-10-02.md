# AIM-H3 V1 — ADAPTIVE INTRADAY MIXTURE AUTHORITY

**Date:** 2026-10-02
**Identity:** `AIM_H3_V1_RESEARCH`
**Parent:** `IRIS_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Hypothesis

IRIS showed a transportable hourly PATH signal, but its daily structural A1 component weakened sharply in 2026. FERG showed that a static error-risk gate over the same state variables does not transport.

AIM tests a different mechanism:

**do not predict which model will fail from a static regime label; instead, continuously reweight multiple leakage-free H3 experts according to their own recently matured out-of-sample probability losses.**

This is a performance-adaptive mixture, not a new black-box classifier.

## 2. Experts

All experts use the same 16:00 America/New_York feature-cutoff anchor and the validated IRIS hourly source.

### E1 STRUCTURAL_IRIS
- expanding Logistic L2
- features: A1 structural logit + frozen IRIS PATH.

### E2 PATH_GLOBAL
- expanding Logistic L2
- features: frozen IRIS PATH only.

### E3 PATH_RECENT126
- Logistic L2 with class_weight=balanced
- features: frozen IRIS PATH only
- training memory: latest 126 matured H3 rows.

Expert architectures and lookback are frozen before evaluation.

## 3. Expert OOS ledger

- Generate chronological monthly-block out-of-sample probabilities from April 2022 onward.
- Each fit uses only rows with `target_end_date_h3 <= test feature cutoff`.
- The adaptive mixer at origin t may use only expert forecast losses from earlier rows whose H3 targets have matured by t.

## 4. Adaptive weighting

For each expert e, compute a decayed Brier loss over matured OOS forecasts:

`L_e(t) = weighted_mean((p_e-y)^2, decay half-life H)`

Adaptive weight:

`w_e(t) = exp(-eta * L_e(t)) / sum_j exp(-eta * L_j(t))`

Final probability:

`p_AIM(t) = sum_e w_e(t) p_e(t)`.

If fewer than 30 matured OOS expert forecasts exist, use equal expert weights.

## 5. Frozen hyperparameter grid

Selected only on Jul-Dec 2022:

- half-life H: 21 / 63 / 126 matured H3 forecasts
- eta: 10 / 20 / 40.

No expert set, lookback, half-life or eta may be changed from 2023+ results.

## 6. Evaluation chronology

- Jan-Mar 2022: initial training history.
- Apr-Jun 2022: OOS expert-ledger warm-up.
- **Jul-Dec 2022: AIM hyperparameter selection.**
- **2023: frozen confirmation 1.**
- **2024: frozen confirmation 2.**
- 2025: frozen transport.
- 2026: frozen stress transport.

Matched E1 STRUCTURAL_IRIS is the comparator.

## 7. Selection rule

AIM candidate is eligible on 2022 H2 when:
- balanced accuracy >= E1;
- accuracy >= E1 - 0.5 percentage points;
- Brier <= E1 Brier;
- log loss <= E1 log loss + 0.005.

Among eligible:
1. highest balanced accuracy;
2. highest accuracy;
3. lowest Brier;
4. lowest log loss.

Fail closed if none eligible.

## 8. Confirmation rule

The selected AIM configuration must separately satisfy in both 2023 and 2024:
- balanced accuracy >= E1;
- accuracy >= E1 - 1.0 percentage point;
- Brier <= E1 + 0.0025.

No later-period rescue is allowed.

## 9. Diagnostics

Report:
- annual expert and AIM metrics;
- mean adaptive expert weights by year;
- 2026 monthly AIM vs STRUCTURAL_IRIS;
- 2026 rescued and broken calls;
- weight shifts in 2026 relative to 2023-2024.

## 10. Interpretation

AIM tests whether **recent realized expert competence** is a more transportable adaptation mechanism than static novelty or error-risk prediction.

2025/2026 remain retrospective transport evidence, not pristine prospective proof.
