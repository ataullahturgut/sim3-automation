# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 CHANGE CONTROL

Date: 2026-09-06
Scope: RESEARCH / HISTORICAL REPLAY ONLY
Identity: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Archived identity preserved: `VW_MIDAS_MSVR` remains `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`.

## 1. Objective
Rebuild the four-metal VW-MIDAS-MSVR research path transparently and deterministically, without claiming exact identity with the missing archived runner. The model predicts the next calendar month's monthly-average XAU/USD price and is evaluated as a separately named successor.

## 2. Canonical target and origin
- Horizon: H=1 month.
- Target month `t`: immediately following calendar month.
- Origin month `p=t-1`: completed prior calendar month.
- Price target for scoring: `CORE5_GOLD_USD_OZ_RESEARCH_R1` monthly-average USD/oz.
- Evaluation window: 2023-01 through 2026-07 inclusive, N=43.
- Random split forbidden.
- Future target information forbidden.

## 3. Four-metal research input surface
Required daily identities:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`

These are historical-reconstruction research series from the pinned StakTrakr source and are not relabelled as canonical market PIT data.

## 4. GPR lanes
### 4.1 Governed successor lane
Primary weighting input: `GPR_OFFICIAL_GIT_PIT`.
For each forecast origin month `p`, use only the official Git archive vintage with `metadata.origin_month = YYYY-MM(p)` and require that vintage to have been available no later than the end of `p`.

The GPR scalar used to weight daily returns is publication-lagged by one month: use GPR observation month `p-1`, not same-month `p`.

Normalize using the selected origin vintage history available through `p-1`:
`z = (gpr[p-1]-min(gpr_history<=p-1))/(max-min)`, with fail-closed handling if history is unavailable.

### 4.2 Legacy-reconciliation lane
`CORE5_GPR_ROUNDED_RESEARCH_R1` may be used only to reproduce/diagnose the old weekend research path. This lane is explicitly `RECONCILIATION_ONLY_NOT_PIT_ELIGIBLE` and cannot establish shadow/runtime eligibility.

## 5. Frozen feature mathematics
For each target month `t`, let `p=t-1`, `pp=t-2`.
For each metal m in `[Gold, Silver, Platinum, Palladium]`:

1. Monthly mean from daily research prices: `M_m(k)`.
2. Prior monthly log return: `MR_m(p)=log(M_m(p)/M_m(pp))`.
3. Within-origin-month daily log returns from completed daily observations in month p:
   `r_d=log(P_d/P_{d-1})` using only consecutive observations inside p.
4. GPR-adaptive decay:
   `lambda = 0.1 * exp(-10*z)`.
5. Age weights, newest daily return age 0:
   `w_i = exp(-lambda*age_i) / sum(exp(-lambda*age))`.
6. Weighted daily return:
   `VW_m(p)=sum(w_i*r_i)`.

Frozen input vector:
`X_t = [MR_Gold,VW_Gold, MR_Silver,VW_Silver, MR_Platinum,VW_Platinum, MR_Palladium,VW_Palladium]`.

Frozen four-output target vector for model fitting:
`Y_t = [log(M_Gold(t)/M_Gold(p)), log(M_Silver(t)/M_Silver(p)), log(M_Platinum(t)/M_Platinum(p)), log(M_Palladium(t)/M_Palladium(p))]`.

Gold price recovery for scoring:
`XAU_hat(t) = CORE5_GOLD_USD_OZ_RESEARCH_R1[p] * exp(Yhat_Gold(t))`.

No additional macro features are permitted in V1. `GPRT`, `GPRA`, Fed Funds, NASDAQ, USD/CNY, VIX/GVZ, equities or ETF proxies require separately preregistered ablation/challenger contracts.

## 6. Frozen MSVR architecture
- True multi-output MSVR, one joint 4-output model.
- RBF kernel.
- Iterative epsilon-insensitive multi-output objective consistent with the retained weekend research implementation.
- Deterministic numeric implementation.
- X and Y standardization fitted from the training rows inside each fit only.

Hyperparameter grid, frozen before scoring:
- `C in {0.1, 1.0, 10.0}`
- `epsilon in {0.02, 0.05}`
- `gamma_scale in {0.5, 1.0}`
- actual RBF gamma = `gamma_scale / 8`.

## 7. Nested rolling-origin tuning
For every outer evaluation target t:
- no information from target t or later may select hyperparameters;
- inner candidate forecasts must have target month `< t`;
- inner origins begin only where official GPR origin-vintage evidence exists;
- choose `(C,epsilon,gamma_scale)` by minimum expanding mean absolute Gold log-return prediction error over all eligible prior inner forecasts;
- deterministic tie-break: lower C, then lower epsilon, then lower gamma_scale;
- require at least 6 prior eligible inner forecasts; otherwise fail closed;
- after selection, refit the selected configuration on all training target rows `< t` using data available at outer origin t.

This supersedes the non-governed retained `run_models.py::tune_msvr` behavior that selected on 2025 targets.

## 8. Baseline and metrics
Primary benchmark: same-origin `RANDOM_WALK`, i.e. prior CORE5 monthly average.

Primary gate metric:
`Relative_MAE_vs_RW = sum(abs(candidate-actual))/sum(abs(RW-actual))`.

Report at minimum:
- MAE
- MAPE
- sMAPE
- median absolute error
- RMSE
- monthly win rate vs RW
- direction accuracy as secondary diagnostic
- completed-year breakdown
- reconciliation distance from archived weekend scorecard

Archived weekend reference is evidence only:
- N=43
- archived/audited VW MAPE = 2.672150%
- archived RW MAPE = 3.302322%
- archived VW median APE = 1.962940%
- archived VW worst APE = 8.831236%

Exact numerical equality to the archived VW output is NOT a pass criterion because the archived runner source is missing.

## 9. Historical replay shadow-eligibility gate
All must pass:
1. source/provenance/origin-vintage checks PASS;
2. deterministic rerun hash PASS;
3. `Relative_MAE_vs_RW < 1.00`;
4. candidate MAPE <= RW MAPE;
5. candidate median AE <= RW median AE;
6. candidate beats RW MAE in at least half of completed calendar years in the evaluation window;
7. in no completed calendar year may candidate MAE exceed `1.50 * RW MAE`;
8. no unresolved leakage/target/availability exception.

Failure => `REJECT_ALL_VW_MIDAS_MSVR_SUCCESSOR_V1_CANDIDATES`.
Pass => maximum research status `RESEARCH_SHADOW_CANDIDATE_HISTORICAL_REPLAY_PASS_PROSPECTIVE_VALIDATION_REQUIRED`.

A historical PASS is not production superiority.

## 10. Hard governance locks
- `AUTO_SELECTOR=OFF`.
- `AUTO_ENSEMBLE=OFF`.
- no forecast/decision production write.
- no runtime activation.
- no archived `VW_MIDAS_MSVR` repair/rename.
- no post-result retuning.
- no silent provider substitution.
- no backdated issuance.
- historical replay must remain labelled historical/reconstructed evidence.
