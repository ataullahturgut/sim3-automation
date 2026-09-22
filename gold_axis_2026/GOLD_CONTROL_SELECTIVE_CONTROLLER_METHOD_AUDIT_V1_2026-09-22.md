# GOLD CONTROL — SELECTIVE CONTROLLER METHOD AUDIT V1

**Date:** 2026-09-22  
**Identity:** `SELECTIVE_CONTROLLER_METHOD_AUDIT_V1`  
**Purpose:** audit whether NP Suppressor V1 and Selective Three-Action V1 were mathematically and operationally aligned with the intended SQRT false-alarm problem.

## 1. Executive finding

The implementations are internally reproducible and the Neyman-Pearson order-statistic arithmetic is correct.

However, two important methodological limitations were identified:

1. **Risk-conditioning mismatch:** the NP thresholds were calibrated on all daily actual-DOWN rows, while the operational safety target is true-DOWN retention *conditional on an SQRT alarm*. Full-daily NP calibration controls an unconditional daily false-suppression risk, not the alarm-conditional false-suppression risk that the project ultimately cares about.

2. **Non-stationary confidence scale:** the selected expert's cumulative Wilson lower confidence bound is not stable on an absolute scale through time. A fixed absolute 2024 threshold can move from WATCH territory to SUPPRESS territory in 2025 even when the semantic evidence has not changed equivalently.

Therefore the V1 three-action result should be interpreted as a rejection of **that specific parameterization**, not of selective RETAIN/WATCH/SUPPRESS control as a concept.

## 2. NP arithmetic verification

For n0 = 86 actual-DOWN daily calibration rows:

### alpha = 0.20, delta = 0.10
- chosen k = 74
- P[Binomial(86, 0.80) >= 74] = 0.0989978241 <= 0.10
- previous k=73 gives tail = 0.1590683295 > 0.10

Therefore k=74 is the smallest admissible order statistic.

### alpha = 0.10, delta = 0.10
- chosen k = 82
- P[Binomial(86, 0.90) >= 82] = 0.0603435146 <= 0.10
- previous k=81 gives tail = 0.1288214450 > 0.10

Therefore k=82 is the smallest admissible order statistic.

The NP umbrella-style order-statistic calculation itself is correct.

## 3. Conditioning mismatch

The operational safety event is:

`BAD_SUPPRESSION = SUPPRESS_DOWN | actual DOWN AND SQRT alarm`

because the controller is only used to alter an SQRT alarm.

But the V1 NP calibration sample was:

`actual DOWN across all daily origins`

with no conditioning on SQRT-alarm status.

Calibrating the score on all actual-DOWN days is conservative for the unconditional event

`P(SUPPRESS AND SQRT_ALARM | actual DOWN)`

but does not directly guarantee

`P(SUPPRESS | actual DOWN, SQRT_ALARM)`.

This distinction matters because the project gate is stated as **true-DOWN retention among SQRT alarms**.

## 4. Why direct alarm-conditional NP calibration was not available in 2024

The 2024 SQRT alarm set contains only 7 actual-DOWN alarms.

For a one-sided NP order-statistic guarantee with delta=0.10:

- alpha=0.20 requires at least 11 class-0 calibration examples before even the most conservative possible order statistic can satisfy the binomial-tail bound;
- alpha=0.10 requires at least 22.

With n=7:
- best possible alpha=0.20 tail = 0.8^7 = 0.2097152 > 0.10;
- best possible alpha=0.10 tail = 0.9^7 = 0.4782969 > 0.10.

Therefore a direct 2024 alarm-conditional NP guarantee at the chosen confidence level is **mathematically infeasible from the available support**.

This is a data-support limitation, not an implementation bug.

## 5. Score drift audit

The frozen Three-Action V1 used the selected expert's cumulative one-sided 90% Wilson lower confidence bound as an absolute score.

On 2024 SQRT alarm origins where Router V2 emitted UP, the scores were approximately:

- 0.4741
- 0.4874
- 0.4801
- 0.5044

The frozen SUPPRESS threshold was 0.494845, so only one of the four became SUPPRESS and three became WATCH.

On 2025 SQRT alarm origins where Router V2 emitted UP, the observed scores began around 0.5263 and were all above the frozen 0.494845 threshold. Thus every Router-UP case became SUPPRESS and WATCH vanished.

This confirms that the cumulative Wilson-LCB score is not suitable as a time-invariant absolute action scale.

## 6. Parameter-learning / formulation variants that remain scientifically open

The following are legitimate successor formulations and must be given new identities rather than altering V1:

### A. Fixed-effective-sample competence
Use a fixed rolling number of prior UP calls (for example a prespecified N) before computing Wilson/Beta confidence. This prevents confidence from rising merely because the cumulative sample grows.

### B. Exponentially discounted Beta-Binomial competence
Update expert correctness with a fixed forgetting factor and bounded effective sample size. This explicitly models changing expert reliability.

### C. Time-normalized confidence percentile
Convert the current competence score into a causal percentile/rank relative to its own matured historical distribution. This creates a more stable [0,1] scale than an absolute Wilson bound.

### D. Direct action-risk calibration
Calibrate the probability/loss of BAD_SUPPRESSION itself instead of thresholding an expert-confidence proxy.

### E. Alarm-conditional / Mondrian risk control
Calibrate within the SQRT-alarm stratum. This is closest to the actual objective but currently support-limited.

### F. Covariate-shift / importance-weighted risk control
Use full daily history but weight observations according to similarity/relevance to SQRT-alarm conditions. This increases usable support but adds modeling assumptions.

### G. Hierarchical Bayesian pooling
Pool information between all daily DOWN cases and the SQRT-alarm DOWN stratum with partial pooling. This can work with small alarm samples but is model-dependent rather than distribution-free.

### H. Adaptive / non-exchangeable conformal control
Allow the calibration parameter to change causally under distribution shift. This is relevant after a valid static action-risk formulation exists.

## 7. Corrected interpretation of prior experiments

### NP Suppressor V1
- arithmetic: correct;
- objective alignment: partial;
- operational result: identical to hard Router-V2 veto;
- conclusion: no incremental gain.

### Selective Three-Action V1
- arithmetic: correct;
- action construction: internally correct;
- confidence-scale choice: not transport-stable;
- safety calibration: unconditional daily rather than alarm-conditional;
- conclusion: this specific fixed-absolute-Wilson-threshold implementation is rejected.

The broader three-action concept remains open.

## 8. Binding next-step rule

Do not silently retune `tau_watch` or `tau_suppress`.

A successor must:
1. receive a new identity;
2. explicitly state whether it controls daily-unconditional or SQRT-alarm-conditional risk;
3. use a confidence/risk quantity whose semantics remain stable through time;
4. state how parameters are learned (cumulative, fixed-window, discounted, ranked, Bayesian, conformal, etc.);
5. preserve Router V2 as the frozen UP-verifier baseline;
6. keep 2025 out of parameter selection.

The preferred next scientific lane is **direct action-risk calibration with a time-stable confidence construction**, not another raw absolute Wilson threshold.
