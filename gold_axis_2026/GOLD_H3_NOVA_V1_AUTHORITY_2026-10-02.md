# NOVA-H3 V1 — STAGE-0 SCIENTIFIC AUTHORITY

**Date:** 2026-10-02  
**Identity:** `NOVA_H3_V1_RESEARCH`  
**Project:** GOLD SHORT-HORIZON GLOBAL XAU  
**Target authority:** `GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`  
**Status:** PREREGISTERED / RESEARCH-ONLY / NO RUNTIME PROMOTION

## 1. Research question

Can a three-day Global XAU direction/return model improve robustness by separating:
1. structural H3 direction memory,
2. recent weak-side adaptation,
3. origin-safe novelty / regime-break evidence,
4. numerical H3 return magnitude,
5. adaptive conformal uncertainty?

The purpose is not to add another classifier family. The hypothesis is that the 2025-2026 failure is partly a non-stationarity / novelty problem and therefore requires explicit uncertainty handling.

## 2. Frozen target

- Horizon: H3 only.
- Return: `target_r3 = log(P[t+3]/P[t])`.
- Direction: UP iff `target_r3 > 0`.
- Forecast timing follows the current R2 fields:
  - `feature_cutoff_date`
  - `forecast_issue_date`
  - `target_end_date_h3`.

## 3. Governance

- No random split.
- All fits use only rows whose H3 target has matured by the current feature cutoff.
- Parameter selection authority: **2019-2021 only**.
- Confirmation report: **2022-2024**. This history has already been inspected in the wider project and is not represented as a pristine blind lockbox.
- 2025: frozen transport/report only; no tuning.
- 2026: opened stress/report only; no tuning.
- Model parameters may refit online using already matured prior H3 outcomes, but architecture, feature sets, grids, thresholds and selection rules are frozen before 2022-2026 scoring.
- No P&L or trading-rule optimization in V1.
- No target-day/future information.

## 4. Fixed structural feature block

CORE3 remains the direction feature authority:

Gold:
- `gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20`

Silver:
- `silver_r1, silver_r5, silver_r21, silver_age_days`

Platinum:
- `platinum_r1, platinum_r5, platinum_r21, platinum_age_days`

Palladium is not promoted in V1.

## 5. Ablation ladder

### A0 — Structural baseline
Expanding CORE3 Logistic L2, threshold 0.50.

### A1 — Asymmetric recent/global repair
Inherited ARCR mechanism:
- global CORE3 Logistic L2
- recent 252-row balanced Logistic L2
- base weights 0.75 global / 0.25 recent
- threshold 0.50.

No A1 re-selection on 2022+.

### A2 — CORE novelty-conditioned mixture
Novelty is estimated without labels from the currently matured training distribution using:
- shrinkage Mahalanobis distance percentile on CORE state variables;
- sigma20 empirical extremeness percentile.

The base A1 mixture may shift weight toward the recent expert under novelty, but extreme novelty also shrinks directional probability toward 0.50.

Frozen selection grid, 2019-2021 only:
- maximum recent weight: 0.35 / 0.50 / 0.65
- novelty shrink strength: 0.25 / 0.50 / 0.75.

Eligibility:
- Brier no worse than A1 by more than 0.0015;
- UP recall no lower than A1 by more than 5 percentage points.

Among eligible candidates: maximize DOWN recall, then balanced accuracy, then accuracy, then minimize Brier/log loss.

### A3 — Cross-market novelty-conditioned mixture
The direction experts remain CORE3. Cross-market variables may affect **novelty only**, not direct direction coefficients.

Origin-safe state transforms:
- DGS10 5-day change
- DFII10 5-day change
- BREAKEVEN10_PROXY 5-day change
- Broad USD 5-day log return
- VIX 5-day log return
- NDX 5-day log return.

A3 uses the same frozen A2 grid and selection rule on 2019-2021.

This design explicitly tests whether external information is more useful as a state/novelty sensor than as a direct direction predictor.

### A4 — Numerical H3 return head + selective agreement
Point-return head:
- CORE3 Elastic Net regression using the frozen project implementation.
- Direction call is eligible only when probability direction and numerical return sign agree.
- Reliability = `2*abs(p_up-0.5)*(1-novelty)`.

Reliability cutoff is selected on 2019-2021 from nominal coverage candidates:
- 70%, 60%, 50%, 40%, 30%.

Selection requires at least 25% coverage and chooses highest selective balanced accuracy, then selective accuracy, then coverage.

Outputs:
- `P_UP_H3`
- `RET_HAT_H3`
- UP / DOWN / UNCERTAIN.

### A5 — Adaptive conformal uncertainty
Adaptive conformal interval is applied to the numerical H3 return head.

- target interval coverage: 80%
- initial alpha: 0.20
- nonconformity score: absolute H3 return error
- only matured prior errors are available at each forecast origin
- calibration window: latest 504 matured scores
- ACI update:
  `alpha_next = clip(alpha + gamma*(0.20 - miss_indicator), 0.02, 0.40)`

Gamma grid selected only on 2019-2021:
- 0.001 / 0.005 / 0.010 / 0.020.

Primary gamma selection:
1. minimize absolute deviation from 80% empirical coverage;
2. minimize mean interval width.

Final directional call requires A4 eligibility plus a minimum return-to-uncertainty ratio:
`abs(RET_HAT_H3) / conformal_half_width >= rho`.

Rho grid selected only on 2019-2021:
- 0.00 / 0.10 / 0.20 / 0.30.

Minimum final coverage: 15%.

Among eligible rho values: maximize selective balanced accuracy, then accuracy, then coverage.

## 6. Metrics

Full-coverage A0-A3:
- Brier
- log loss
- accuracy
- balanced accuracy
- UP recall
- DOWN recall
- false-call rate.

A4-A5 selective:
- call coverage
- selective accuracy
- selective balanced accuracy
- UP precision
- DOWN precision
- UP capture recall over all actual UP days
- DOWN capture recall over all actual DOWN days
- false-UP FPR over all actual DOWN days
- false-DOWN FPR over all actual UP days.

Numerical head:
- MAE
- RMSE
- return-sign accuracy.

Conformal:
- empirical interval coverage
- mean interval width.

## 7. Intraday rule

The existing XAU 1-hour source begins too late to support the same 2019-2021 selection contract. Therefore V1 does **not** silently add intraday features.

If NOVA V1 shows a defensible pre-2025 improvement, intraday realized-state features may be tested under a separately named V1.1/V2 authority with an explicit later-history contract.

## 8. Interpretation contract

A DEV/confirmation improvement is not runtime proof. A 2025/2026 failure cannot be repaired by changing V1 thresholds or grids after inspection. Any such change creates NOVA-H3 V2.

The intended final research output is a probabilistic object:

`[P_UP_H3, RET_HAT_H3, LOWER_H3, UPPER_H3, NOVELTY, SIGNAL]`

where SIGNAL is UP, DOWN or UNCERTAIN.
