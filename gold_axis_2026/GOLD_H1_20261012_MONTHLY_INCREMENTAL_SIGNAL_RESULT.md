# H1 — Monthly incremental future-information audit, final retrospective result

**Decision: REJECT / NO PROMOTION for this fixed three-candidate *low-capacity feature screening*.**
Prereg commit `3dbb0f4d`; 199 archived monthly source rows, 108 chronologically replayed evaluation months 2016-01..2024-12, 36+ prior monthly training observations. **Not a valid origin-time/live model:** historical StakTrakr daily rows and World Bank monthly CORE5 rows were backfilled; origin-time World Bank average availability is not proven. The prior 2012–21 years also overlap historical model experimentation; this is no untouched validation.

## Tested
Residual of next World Bank mean relative to the retrospectively source-aligned known portion `K=WB_mean[origin]*STAK_last[origin]/STAK_mean[origin]`. Fixed expanding intercept-only benchmark vs ridge(alpha=10, standardized prior training features) for B1 gold last-to-last momentum, B2 equal-weight Ag/Pt/Pd momentum minus gold, B12 joint. No 2025/26 tuning. **Original ChHHO ANFIS, GPR and HMM regime blocks were not retested.** Their unsourced earlier vintages prohibit interpreting this study as a clean test of their incremental effect.

## Actual results: 2016–2024 (N=108), lower squared-error better
| Candidate | Residual MSE | R²_OS vs intercept-only | Reconstructed WB-level ΣAE USD |
|---|---:|---:|---:|
| Expanding baseline | 0.00065028 | 0.0000 | 3614.18 |
| B1 gold month momentum | 0.00066882 | -0.0285 | 3663.98 |
| B2 cross-metals vs gold | 0.00065500 | -0.0073 | 3632.70 |
| B12 joint | 0.00067162 | -0.0328 | 3695.51 |

R²_OS by 3-year block:
| Candidate | 2016–18 | 2019–21 | 2022–24 |
|---|---:|---:|---:|
| B1 | -0.1017 | +0.0313 | -0.0280 |
| B2 | +0.0121 | -0.0128 | -0.0162 |
| B12 | -0.0897 | +0.0227 | -0.0401 |

3-month moving-block bootstrap (10k fixed-seed resamples) of **baseline-minus-candidate** monthly squared-loss:
- B1 95% CI [-0.00005070, 0.00001568]
- B2 [-0.00005316, 0.00003715]
- B12 [-0.00006381, 0.00002612]

Every confidence interval includes zero. **All three require positive R²_OS, positive performance in each 3-year block, and a CI lower bound above zero; none passes.** No multiple-comparison correction can reverse this failure.

## Interpretation
An ordinary linear combination of completed-month metal momentum signals provides **no robust marginal forecasting advantage** against the source-adjusted known-component-plus-expanding-drift control in this retrospectively reconstructed set. This does not prove that ChHHO's residual signal is nonexistent: it uses a different model, does not validate original GPR, and lacks original daily first-publication proof. Do **not** close the whole monthly program or overwrite its authority. No 2025/26 winner selection.

## Reproduction
Inputs: `GOLD_H1_20261012_MONTHLY_ARCHIVE_INPUT_ROWS.csv`; month-by-month outputs: `GOLD_H1_20261012_MONTHLY_SCORE_ROWS.csv`; machine result: `GOLD_H1_20261012_MONTHLY_RESULTS.json`; deterministic verification: `tools/gold_h1_20261012_monthly_incremental_replay.py`. No database writes, no financial P&L.
