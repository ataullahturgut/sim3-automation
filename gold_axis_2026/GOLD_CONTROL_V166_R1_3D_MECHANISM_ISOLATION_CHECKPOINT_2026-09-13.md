# Gold Control V1.66 R1 — 3D Mechanism Isolation Result Checkpoint

Date: 2026-09-13  
Branch: `gold-v166-3d-mechanism-isolation-r1-research`  
Draft PR: #59  
Parent: V1.65-DIAG failure attribution  
Successful workflow run: `34755204268` — SUCCESS  
Artifact: `10317231185`  
Artifact digest: `sha256:08e0c8efb2333642b8b02dc97ba46e465f2d39cc23af488bf237bb81f0eb01ca`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Frozen question

For 3D only, can temporal weakness be repaired by either (a) matured causal probability recalibration alone or (b) the already-frozen recency-weighted refit alone, relative to the unchanged static parent, before adding gated residual correction, drift detection, selector logic, or abstention?

The experiment used only the immutable V1.64 artifact. No external data fetch or panel reconstruction occurred. The maturity rule remained `j+3<=t`.

## Result

`V1.66 R1 = NEITHER MECHANISM PASSES THE FROZEN GATE`.

Family-level pass:

- `RECAL_ONLY = FALSE`
- `FORGET_ONLY = FALSE`

Frozen decision:

`NEITHER_MECHANISM_PASSES_STOP_ADAPTATION_ESCALATION_RETURN_TO_SIGNAL_OR_NEW_HYPOTHESIS`

## Main numerical findings

### SESSION_RM_RIDGE — closest case

2026:

- STATIC: Brier `0.26130`, AUC `0.52533`, BA `0.49333`.
- RECAL_ONLY: Brier `0.25281`, AUC `0.52267`, BA `0.51222`, MCC `0.04880`.
- FORGET_ONLY: Brier `0.25989`, AUC `0.55378`, BA `0.52222`, MCC `0.05164`.
- Frequency benchmark: Brier `0.25107`.

RECAL_ONLY materially improves STATIC in 2026 by about `0.00849` Brier and preserves AUC above the frozen `0.52` threshold, but still fails to beat the frequency benchmark and does not establish 2025 robustness. FORGET_ONLY improves directional discrimination in 2026 but barely improves Brier and also fails the benchmark/2025 conditions.

### MACRO_CROSS_RIDGE

2025 STATIC had useful discrimination (AUC `0.57074`) and near-benchmark Brier (`0.23820` vs frequency `0.23795`). In 2026 STATIC collapses to Brier `0.30349`, AUC `0.47630`.

- RECAL_ONLY repairs 2026 Brier to `0.26770`, an improvement of about `0.03579` versus STATIC, but AUC remains weak (`0.46770`) and Brier remains worse than frequency (`0.25107`).
- FORGET_ONLY repairs 2026 Brier to `0.27792` and AUC to `0.52756`, but still misses the frequency benchmark and worsens 2025 Brier relative to STATIC.

This confirms that calibration and recency each repair different parts of the failure, but neither alone produces robust forecast skill.

### GOLD_RIDGE / PRICE_DISCOVERY_HGB / FULL_HGB

RECAL_ONLY often reduces severe 2026 Brier error substantially:

- GOLD_RIDGE: `0.30425 -> 0.27278`.
- PRICE_DISCOVERY_HGB: `0.28028 -> 0.26092`.
- FULL_HGB: `0.29213 -> 0.26311`.

However discrimination remains below the frozen AUC threshold and every recalibrated result remains worse than the frequency benchmark. FORGET_ONLY is inconsistent and in PRICE_DISCOVERY_HGB / FULL_HGB makes 2026 Brier worse than STATIC.

## Interpretation

The V1.65-DIAG diagnosis is strengthened rather than overturned.

1. Pure recalibration can reduce probability error when the static model becomes overconfident or base-rate-misaligned, but it cannot restore lost discrimination.
2. Pure recency weighting can improve discrimination for selected parents (especially SESSION_RM and MACRO_CROSS in 2026), but the gain is not stable enough across 2025/2026 and does not consistently beat the simple frequency benchmark.
3. Therefore the current 3D problem is not a single calibration defect and not a single forgetting-rate defect.
4. The fact that RECAL_ONLY and FORGET_ONLY repair different aspects is evidence for a multi-component temporal failure, but this result does **not** authorize an ad-hoc hybrid because that would be a post-score construction.

## Research decision

Do not escalate immediately to a gated hybrid, CRASE, or a drift detector using these same visible outcomes.

The next legitimate step should return to the literature and formulate a **new predeclared hypothesis** aimed at the remaining bottleneck: loss of discriminative information under distribution shift, while preserving the useful evidence that calibration/recency corrections can partially stabilize probability error.

A future hybrid is eligible only if independently justified before scoring, with its own frozen contract and without choosing components/weights from the V1.66 result table.

No production, trading, or prospective claim is made.
