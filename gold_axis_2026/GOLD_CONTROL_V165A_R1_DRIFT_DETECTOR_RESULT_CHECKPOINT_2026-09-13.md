# Gold Control V1.65A-R1 — Drift Detector Validation Result Checkpoint

Date: 2026-09-13  
Branch: `gold-v165a-drift-detector-validation-research`  
Draft PR: #56  
Parent: V1.64 adaptive error-memory forecaster research  
Successful workflow run: `34753745098` — SUCCESS  
Artifact: `10316548635`  
Artifact name: `gold-v165a-r1-drift-detector-validation-f5801d64355f0686fe76a895250b14aa8ecd6984`  
Artifact digest: `sha256:cda318379765aebddc3a2b3592db335c1ac78b992ee2949187d651211f05de31`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Why R0 was stopped before detector scoring

The first V1.65A contract intended to calibrate ADWIN/Page-Hinkley on pre-2025 empirical V1.64 forecast-loss streams. During implementation it was established that the frozen V1.64 pointwise streams contain only about 32 matured 1D formation losses and 28 matured 3D formation losses per parent before 2025. That is insufficient support for a defensible empirical moving-block calibration of false-alarm and detection-delay properties.

Therefore R0 was explicitly marked `SUPERSEDED_BEFORE_DETECTOR_SCORING_INSUFFICIENT_FORMATION_SUPPORT`. No ADWIN/Page-Hinkley detector result from R0 was used to choose parameters. The earlier CI failure was also caused by an external FedBoard fetch/header failure (`DTWEXBGS`), but the more important scientific reason for replacing R0 was insufficient formation-loss support.

## R1 frozen design

R1 moved detector selection completely away from 2025/2026 outcomes. A compact predeclared detector grid was scored only on generic synthetic bounded/autocorrelated loss processes:

- ADWIN delta: `0.001`, `0.002`, `0.005`.
- One-sided Page-Hinkley: delta `0.0` or `0.1`; threshold `5`, `7.5`, `10`.
- Synthetic innovations: Normal and Student-t(5).
- AR(1) dependence: rho `0.0`, `0.3`, `0.6`.
- Stream length: 300; drift starts at 150.
- Drift shapes: abrupt and gradual-30.
- Shift sizes: `0.5`, `1.0`, `1.5` standard deviations.
- 200 replications per scenario.

Frozen gate:

- mean null false-alarm rate <= 0.10;
- worst-archetype null false-alarm rate <= 0.20;
- mean detection rate at 1 SD >= 0.70;
- worst-archetype detection rate at 1 SD >= 0.50.

Only after a detector passed this synthetic gate was the immutable V1.64 artifact allowed to be inspected descriptively. The actual 2025/2026 timeline was forbidden from changing detector family or parameters.

## Result

`V1.65A-R1 = FAIL / NO DETECTOR PASSES FROZEN SYNTHETIC GATE`.

| Candidate | Mean null FAR | Worst null FAR | Mean detection @1SD | Worst detection @1SD | Median delay @1SD | Pass |
|---|---:|---:|---:|---:|---:|---|
| ADWIN_D0.001 | 0.0000 | 0.0000 | 0.0271 | 0.0000 | 132.00 | FAIL |
| ADWIN_D0.002 | 0.0000 | 0.0000 | 0.0529 | 0.0050 | 130.75 | FAIL |
| ADWIN_D0.005 | 0.0000 | 0.0000 | 0.1679 | 0.0500 | 128.00 | FAIL |
| PH_D0_T5 | 1.0000 | 1.0000 | 0.0083 | 0.0000 | 3.00 | FAIL |
| PH_D0_T7.5 | 1.0000 | 1.0000 | 0.0713 | 0.0200 | 6.00 | FAIL |
| PH_D0_T10 | 0.9867 | 1.0000 | 0.1708 | 0.0525 | 11.00 | FAIL |
| PH_D0.1_T5 | 1.0000 | 1.0000 | 0.0463 | 0.0025 | 5.00 | FAIL |
| PH_D0.1_T7.5 | 0.9725 | 1.0000 | 0.1913 | 0.0475 | 10.75 | FAIL |
| PH_D0.1_T10 | 0.8558 | 0.9900 | 0.3783 | 0.1425 | 12.50 | FAIL |

Synthetic selection status: `NO_DETECTOR_PASSES_FROZEN_SYNTHETIC_GATE`.

Because no detector passed, the V1.64 2025/2026 actual timeline diagnostic was not run. This was required by the freeze and prevents outcome-driven detector tuning.

Next-step lock: `STOP_TRIGGERED_ADAPTATION_BLOCKED_NO_DETECTOR_PASSED`.

## Interpretation

The active/detect-then-adapt hypothesis is not rejected. What is rejected is the use of these uncalibrated detector configurations for the forecast-loss process.

ADWIN in the frozen grid is extremely conservative for a 1-SD deterioration: false alarms are essentially zero, but detection power is very low and delays are close to the end of the post-change monitoring window.

Page-Hinkley in the frozen grid has the opposite failure: it reacts quickly when it alarms, but its null false-alarm probability is unacceptably high (roughly 0.86 to 1.00 across the tested configurations). Thus neither family/configuration satisfies the required false-alarm/power trade-off.

## Next legitimate hypothesis

Do **not** lower the R1 gate and do **not** choose a detector from these results by eye. The next experiment should calibrate a one-sided forecast-loss CUSUM/control limit explicitly to a target in-control false-alarm probability, while accounting for temporal dependence.

A defensible V1.65A-R2 design is:

1. monitor excess Brier loss `e_t = L_model,t - L_benchmark,t`;
2. estimate/represent dependence using a long-run variance or dependence-aware synthetic/bootstrap process;
3. choose the CUSUM reference value from a predeclared target deterioration size rather than an arbitrary grid;
4. calibrate the decision boundary on null simulations to a fixed false-alarm target (for example 5% over the monitoring horizon);
5. lock that boundary;
6. evaluate detection probability and delay on separate held-out synthetic drift simulations;
7. only after that, apply the frozen monitor descriptively to the immutable V1.64 timeline;
8. only if the calibrated monitor passes should V1.65B `NORMAL -> WARNING -> DRIFT -> RECOVERY` triggered adaptation become eligible.

No selector, abstention tuning, triggered adaptation, production, or trading claim is made in V1.65A-R1.
