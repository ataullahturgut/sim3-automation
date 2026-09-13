# Gold Control V1.65-DIAG — Forecast Failure Attribution Checkpoint

Date: 2026-09-13  
Branch: `gold-v165diag-failure-attribution-research`  
Draft PR: #57  
Parent: V1.65A-R1 detector validation failure checkpoint  
Freeze commit: `eaccac1e52a47ede2c651b104e87b3777cf58909`  
Successful workflow run: `34754559786` — SUCCESS  
Artifact: `10317175296`  
Artifact digest: `sha256:87f07c917922f890c5de501ced1ff80da27d08d2ca18b7e36e63694b635c67dd`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Frozen question

Why did the 1D/3D short-horizon probabilistic forecasts remain weak or temporally unstable: weak discrimination, calibration failure, covariate/target shift, state-dependent skill instability, estimation uncertainty, or insufficient expert-pool signal?

V1.65-DIAG changes no model. It does not refit, recalibrate, run a drift detector, trigger adaptation, score a selector, tune abstention, or write to production. It analyzes only the immutable V1.64 pointwise predictions and panel.

## Main result

`V1.65-DIAG = FAILURE ATTRIBUTION COMPLETE; NO SINGLE-CAUSE EXPLANATION`.

The dominant evidence is not that the models are merely miscalibrated. Across both horizons the frozen static parents generally fail to beat the expanding-frequency benchmark, and in 2026 several models are clearly worse than that benchmark. The strongest common failure mode is loss of discrimination, with additional distributional/state instability that is materially stronger at 3D.

## 1D diagnosis

No 1D parent has robust benchmark skill in both 2025 and available-2026.

2026 AUC values are all below the frozen 0.55 discrimination threshold:

- GOLD_RIDGE: AUC `0.4356`, Brier skill vs frequency `-7.73%`.
- SESSION_RM_RIDGE: AUC `0.4879`, Brier skill `-7.19%`.
- PRICE_DISCOVERY_HGB: AUC `0.4802`, Brier skill `-6.55%`.
- MACRO_CROSS_RIDGE: AUC `0.4948`, Brier skill `-6.79%`.
- FULL_HGB: AUC `0.4801`, Brier skill `-7.84%`.

Therefore the 1D failure is primarily a discrimination/signal problem rather than a pure calibration problem.

The 1D target base rate also changes materially: UP frequency falls from `57.64%` in 2025 to `46.11%` in available-2026, a `-11.53 percentage-point` shift.

Material 2025->2026 covariate shift is detected for GOLD_RIDGE, PRICE_DISCOVERY_HGB and FULL_HGB. The largest effect-size changes include:

- `gold_mom20`: SMD about `-0.82`;
- `gold_rv20`: SMD about `+0.71`;
- `gld_vol20`: SMD about `+1.39`;
- `gc_vol20`: SMD about `+1.30`;
- `broad_usd_level` inside FULL_HGB: SMD about `-1.37`.

However, the frozen predeclared univariate state audit does **not** cross the material state-instability threshold for any 1D parent. This means the observed distribution shift does not yet translate into a defensible simple state-routing rule.

The hindsight per-origin oracle has large apparent headroom (`0.1612` oracle Brier versus `0.2539` frequency Brier in available-2026), but this is explicitly an unattainable ex-post upper bound and may be inflated by choosing the winner after observing the outcome. It is not evidence that a practical selector has been found.

### 1D interpretation

Do not resume drift-triggered adaptation or selector work for 1D yet. The current evidence says the immediate bottleneck is weak discriminative information under the changed 2026 distribution. The next 1D work should prioritize signal discovery / information redesign / possibly horizon redesign, with more data required before strong causal attribution.

## 3D diagnosis

No 3D parent has robust benchmark skill in both periods either, but the failure mechanism is more structured than at 1D.

The clearest deterioration is in 2026:

- GOLD_RIDGE: AUC `0.3359`, Brier skill `-21.18%`, BA `40.56%`, MCC `-0.221`.
- MACRO_CROSS_RIDGE: AUC `0.4763`, Brier skill `-20.88%`, BA `46.56%`, MCC `-0.082`.
- PRICE_DISCOVERY_HGB: AUC `0.4582`, Brier skill `-11.63%`.
- FULL_HGB: AUC `0.4659`, Brier skill `-16.35%`.
- SESSION_RM_RIDGE is the least-bad static parent in 2026, but still has negative Brier skill (`-4.07%`) and AUC only `0.5253`.

For MACRO_CROSS_RIDGE, 2025 is different: AUC is `0.5707` while Brier skill is approximately flat (`-0.10%`) and ECE is `0.0877`. This meets the frozen rule for a **plausible calibration problem in 2025**. But by 2026 AUC collapses below 0.5 and Brier skill falls to `-20.88%`, so recalibration alone cannot explain or repair the temporal failure.

Material covariate shift is again present for GOLD_RIDGE, PRICE_DISCOVERY_HGB and FULL_HGB.

More importantly, the predeclared state audit finds material skill-sign instability for:

- GOLD_RIDGE: `4/13` comparable state strata flip Brier-skill sign (`30.77%`).
- SESSION_RM_RIDGE: `4/13` flips (`30.77%`).
- MACRO_CROSS_RIDGE: `6/13` flips (`46.15%`).

For MACRO_CROSS_RIDGE, examples include 2025-positive skill in low-volatility, negative gold-momentum, USD-up, real-yield-down, FAST-down and SLOW-neutral states turning negative in available-2026. This is consistent with a time-varying conditional performance map rather than a single static calibration error.

The 3D target UP rate falls from `62.19%` to `54.55%`, a `-7.64 percentage-point` shift; this is below the frozen 10-point material threshold.

The hindsight oracle again shows large ex-post headroom (`0.1436` oracle Brier versus `0.2511` frequency Brier in available-2026), but remains non-deployable evidence only.

### 3D interpretation

The 3D evidence supports further temporal-robustness research more strongly than 1D. Three mechanisms remain eligible in separate frozen follow-ups:

1. **Recalibration** as a narrow test for periods/parents where discrimination remains positive but probability calibration is poor (especially 2025 MACRO_CROSS).  
2. **Drift/adaptation** because several parent input distributions shift and three parents show material state-dependent skill instability.  
3. **State-dependent selection/gating** as a research hypothesis, but only after proving that the apparent hindsight complementarity is exploitable without outcome leakage.

## Uncertainty qualification

All parents have at least one period where the block-bootstrap excess-Brier interval includes zero, so strong causal attribution remains limited by sample size. At the same time, several 2026 failures are not explainable as noise alone: the 2026 excess-Brier confidence intervals are entirely above zero for multiple parents, including 1D GOLD_RIDGE / PRICE_DISCOVERY_HGB / FULL_HGB and 3D GOLD_RIDGE / PRICE_DISCOVERY_HGB / MACRO_CROSS_RIDGE / FULL_HGB.

## Decision

The previous plan to build a generic detector across both horizons is no longer the preferred next step.

- **1D:** pause adaptation/selector work; prioritize new discriminative signal or horizon redesign.
- **3D:** continue, but with a targeted temporal-robustness program. Do not treat calibration, drift and gating as the same problem.

The most defensible immediate next experiment is a **3D-only mechanism isolation study**, with frozen alternatives tested separately: `STATIC`, `MATURED_RECALIBRATION_ONLY`, and a separately prevalidated `DRIFT_TRIGGERED_ADAPTATION` path. State-dependent gating should remain a later challenger unless a leakage-safe predictability-of-expert-skill test shows exploitable competence information.

No production or prospective claim is made.
