# 2027 Gold monthly conditional projection — scientific boundary and real numerical run
Date: 2026-10-27. Branch: `research/gold-2027-monthly-conditional-20261027`. **STATUS: EXPERIMENTAL_SCENARIO_ONLY / NOT_ORIGINAL_H1_FORECAST / NOT_FINANCIAL_RECOMMENDATION**.

## Objective and fundamental feasibility boundary

Original monthly champions, ChHHO-ANFIS (CURRENT8, four metals × MR1 / GPR-weighted movement), REDUCED4 ANN, and FULL7 ANN forecast **H=1: next completed calendar-month average XAU/USD**. On 27 Oct 2026 a complete, source-audited Nov/Dec 2026 monthly record and future point-in-time GPR vintages do **not** exist. An unmodified original H1 model **cannot truthfully issue 12 independent certified January–December 2027 monthly forecasts** today. These numbers must not be cited as forecasts produced by the original champion weights.

The model families below are newly implemented and **adapted** to four monthly metal-to-metal return features, with no GPR. They run a fixed one-month-return map iteratively 15 times from **the last completed September 2026 observation**; October–December 2026 are hypothetical model outputs, not future actual data. The 2027 path inherits this chain's unobserved values.

## Sources and gate
- Gold Control Neon project `winter-art-94880101`, read-only `gold_monthly_h1.staktrakr_single_repository_monthly_research_v1`: 201 complete months, all 4 metals, 2010-01–2026-09, 804 metal-month values. Last completed gold monthly average September 2026: **4327.880454545455 USD/oz**.
- Frozen input: `research/gold_2027_monthly_source_snapshot_20261027.json` blob `ba977636966683ba5a48ba91f0f9c076e57b4156`; 2010–2025 StakTrakr revision `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, Jan–Sep 2026 revision `02964d0324dde362099976c867f5077a369acaa5`. Source is a research snapshot, not contemporaneously firstprint certified.
- February 27 2026 3516.02 USD/oz gold outlier affected monthly means. For fitting only, samples labeled 2026-02, 2026-03, 2026-04 were excluded because target and lag return inputs are tainted. Original DB data not mutated.
- October 1–23 2026 *partial* 17-day research gold mean: **4139.134705882352 USD/oz**, from pinned repository artifacts `v33_oct01_16_frozen_2026_four_metals_weekday_20261023_snapshot.csv` blob `008c5e2477698df2c9bc3b88248ebef1345e5159` and `v33_staktrakr_4metals_2026_10_19_to_10_23_FIXED_COMMIT.csv` blob `11e48dabc336eed2ec69745b616841ebb988c7d8`. Models' hypothetical October result was 4337.36 (ANFIS adaptation) or 4315.90 (ANN adaptation). Because October is incomplete, the observed 17-day mean is **not** a complete October monthly actual nor a point-in-time forecast score; the gap is a caution.

## Executed adaptive-family methods
- **ChHHO-ANFIS adaptation:** 4 input lagged monthly returns (AU/AG/PT/PD), 5 Gaussian first-order Sugeno fuzzy rules, 4 multioutput monthly log returns; ChHHO optimizes premise centers and spreads with 12 agents, 18 generations, 2 seeds; LSE stabilized with 0.002 ridge; 2022–2024 checking selected 0 added ANFIS gradient epochs (so final numerical fit uses optimized premise and least-square Sugeno consequent; do not falsely assert nonzero local gradient refinement).
- **ANN adaptation:** 4-input 8-tanh-hidden 4-output MLP, Adam and L2 regularization, 100 epochs selected on 2022–2024 checking; **not** original REDUCED4/FULL7 ensemble nor exact GPR inputs.
- Train: 2010-03–2021-12; validation: 2022-01–2024-12; chronological pre-2025 fit for out-of-period 2025 and 2026. Scenario refit uses 2010–Sep 2026 *excluding contaminated 2026 Feb–Apr*. 2027 target labels unavailable and never used in fit.
- A numerical cap of **±15% per metal per simulated month** guards recursive explosion, not an original H1 parameter. Neither 2027 metal/GPR path nor global risk shocks can be validated.

## 2027 monthly XAU/USD research scenarios (USD/oz monthly average)
| Month | ANFIS adaptation | ANN adaptation |
|---|---:|---:|
| 2027-01 | 4479.90 | 4385.82 |
| 2027-02 | 4532.29 | 4419.20 |
| 2027-03 | 4583.69 | 4453.88 |
| 2027-04 | 4634.19 | 4489.29 |
| 2027-05 | 4684.12 | 4525.17 |
| 2027-06 | 4733.80 | 4561.43 |
| 2027-07 | 4783.50 | 4598.00 |
| 2027-08 | 4833.42 | 4634.88 |
| 2027-09 | 4883.67 | 4672.07 |
| 2027-10 | 4934.35 | 4709.55 |
| 2027-11 | 4985.49 | 4747.34 |
| 2027-12 | 5037.14 | 4785.42 |
| **2027 mean of 12 projected months** | **4758.80** | **4581.84** |

2025 single-month heldout frozen-2024 diagnostic: ANFIS adaptation 12/12 months, MAPE **3.71%**, correct direction **11/12**; ANN adaptation MAPE **3.10%**, direction **12/12**. 2026 single-month heldout, excluding Feb–Apr, 6 months: ANFIS MAPE **4.30%**, correct direction **4/6**; ANN MAPE **5.71%**, direction **3/6**. **These 1-month metrics do not validate 15-step recursive 2027 accuracy** and should not be presented as error bands.

## Reproducibility
- Exact runner: `tools/gold_2027_conditional_monthly_scenario_v1.js`, pinned code blob `5473f923f2aacfe07d923dfc445aeb45697a8946`.
- Exact output including all 15 predicted months and checked metrics: `research/gold_2027_monthly_conditional_model_run_20261027.json` blob `322e50cc82d6139608b42b2e92996b7977101772`.
- Deterministic rerun: PASS; 15 × 2 projected outcomes matched saved values within 1e-7; 12-month 2025 holdout, 6-month cleansed 2026 holdout, source/blob pinning PASS. No Neon writes, no application changes.

## Interpretation
The two adapted scenarios rise monotonically through 2027 because of recursive dynamics in this fit. They are **not prediction intervals**. No statistically defensible claim that 2027 must rise, nor a reliable December price, can be made. Re-run original H1 with each future newly completed month and its actual GPR vintage if forecasting for live decisions; use a separately established multi-horizon protocol for long-horizon actionable forecasts.
