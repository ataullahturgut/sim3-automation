# GOLD MONTHLY FORECAST — CHALLENGER B MANIFEST

**Manifest version:** 1.0  
**Date:** 2026-09-28  
**Repo:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`  
**Status:** CHALLENGER-B MODEL SCREEN COMPLETE FOR USER-AUTHORIZED SCOPE

---

## 1. Purpose

Challenger-B is a parallel research path. It does **not** replace or modify the existing Gold Monthly / Challenger-A path.

Its purpose is to port selected model families previously used in the Grup-ARGE forecasting program into the governed Gold Monthly H=1 problem and test them under the same chronological evaluation authority.

User-authorized final scope:
- run the selected advanced Grup-ARGE challengers,
- add ARIMA, SARIMA and Prophet,
- do **not** run the remaining omitted classical models,
- document the entire Challenger-B result set in one manifest.

---

## 2. Binding Gold Monthly governance

### Forecast target
- H=1 next-calendar-month average XAU/USD price.
- Forecast origin = previous completed calendar month end.

### Model-selection authority
- **DEV:** 2022-04..2024-12, n=33.
- **2025:** LOCKED_REPORT_ONLY.
- **2026-01..2026-07:** QUARANTINED_REPORT_ONLY.

### Hard controls
- Random split: **NONE**.
- Target-month leakage: **FORBIDDEN**.
- DB: **READ_ONLY**.
- Main selection metric: DEV cumulative absolute price error (SigmaAE).
- Secondary: monthly direction accuracy.
- Supporting: MAE, RMSE, MAPE/WAPE, relative MAE vs Random Walk, worst month, stability.
- 2025/2026 may not promote, rescue, retune or choose a model.

---

## 3. Input / preprocessing families

### CURRENT8 engineered-feature models
Frozen 8 origin-safe predictors:
- Gold_MR, Gold_VW
- Silver_MR, Silver_VW
- Platinum_MR, Platinum_VW
- Palladium_MR, Palladium_VW

MR = prior-month log return.  
VW = GPR-adaptive weighted within-origin-month daily log return.

GPR geopolitical-risk chronology:
- official Git PIT vintage,
- exact-origin vintage,
- publication-lagged p-1 observation,
- causal normalization.

### Scaling rules
- Ridge / Elastic Net / Huber: StandardScaler fitted only on training fold.
- PLS1 / PLS2: PLSRegression(scale=True), internal training-fold scaling.
- GPReg-RBF / GPReg-Matérn: StandardScaler on X only, training-fold fit.
- Extra Trees / HGB: no scaler; tree-native engineered CURRENT8 values.

### Raw univariate monthly-level models
ARIMA, SARIMA and Prophet are not forced onto CURRENT8.
They use:
- authoritative completed monthly average Gold/XAU/USD price level,
- training start 2010-05,
- no scaling,
- no external regressors.

This preserves the actual model-family logic from the prior Grup-ARGE work.

---

## 4. Challenger-B DEV ranking

Primary ordering below is by DEV SigmaAE. Direction is shown as the second objective.

| Rank | Model | Input path | DEV SigmaAE | Direction | DEV rel.MAE vs RW | Decision |
|---:|---|---|---:|---:|---:|---|
| **1** | **PLS1 V1** | CURRENT8 | **1420.0291** | 20/33 | 0.8078 | **RETAIN — strongest Challenger-B price model** |
| 2 | PLS2 V1 | CURRENT8, 4-output target | 1489.3300 | **23/33** | 0.8472 | RETAIN — direction-improved secondary |
| 3 | Ridge V1 | CURRENT8 | 1520.9926 | 21/33 | 0.8652 | NOT PROMOTED |
| 4 | Huber V1 | CURRENT8 | 1530.1300 | 20/33 | 0.8704 | NOT PROMOTED |
| 5 | Extra Trees V1 | CURRENT8 | 1539.9221 | 20/33 | 0.8760 | NOT PROMOTED |
| 6 | Elastic Net V1 | CURRENT8 | 1590.3571 | 16/33 | 0.9046 | NOT PROMOTED |
| 7 | GPReg-Matérn V1 | CURRENT8 | 1637.9165 | 19/33 | 0.9317 | NOT PROMOTED |
| 8 | GPReg-RBF V1 | CURRENT8 | 1696.3365 | 16/33 | 0.9649 | NOT PROMOTED |
| 9 | SARIMA | raw monthly Gold level | 1751.5242 | 19/33 | 0.9963 | NOT PROMOTED |
| 10 | ARIMA | raw monthly Gold level | 1781.7822 | 15/33 | 1.0135 | NOT PROMOTED |
| 11 | HGB V1 | CURRENT8 | 1840.2678 | 20/33 | 1.0468 | NOT PROMOTED |
| 12 | Prophet | raw monthly Gold level | 7521.1360 | 14/33 | 4.2782 | **REJECT / NOT PROMOTED** |

### DEV interpretation
- **PLS1 is the clear Challenger-B leader for price error.**
- **PLS2 has the best direction count among the main Challenger-B models: 23/33**, but with materially higher price error than PLS1.
- SARIMA only barely beats Random Walk on DEV SigmaAE.
- ARIMA and HGB are worse than Random Walk on DEV cumulative price error.
- Prophet is decisively noncompetitive in this frozen raw-monthly-price formulation.

---

## 5. B5 PLS1 metal ablation

The PLS1 All-4 reference was reproduced before ablation:
- expected SigmaAE: 1420.0291314697745
- observed: 1420.0291314697738
- absolute difference: 6.82e-13
- expected direction: 20/33
- observed: 20/33
- reproduction gate: **PASS**

### DEV metal-set ranking

| Rank | Variant | Metals | DEV SigmaAE | Direction | Decision |
|---:|---|---|---:|---:|---|
| **1** | **M2_ALL4_REFERENCE** | Au+Ag+Pt+Pd | **1420.0291** | 20/33 | **Primary retained set** |
| 2 | M3_NO_SILVER | Au+Pt+Pd | 1454.3225 | **22/33** | Pareto trade-off reference |
| 3 | M5_NO_PALLADIUM | Au+Ag+Pt | 1461.6772 | 19/33 | Not selected |
| 4 | M1_GOLD_SILVER | Au+Ag | 1491.2346 | 20/33 | Not selected |
| 5 | M0_GOLD_ONLY | Au | 1519.4727 | 21/33 | Not selected |
| 6 | M4_NO_PLATINUM | Au+Ag+Pd | 1519.6757 | 20/33 | Not selected |

### Metal-ablation conclusion
- All four metals remain justified for the primary price-error objective.
- Removing Silver gains 2 correct directions but costs +34.29 SigmaAE.
- Removing Platinum causes the largest single-metal price-error deterioration: +99.65 SigmaAE.
- Removing Palladium costs +41.65 SigmaAE and one correct direction.
- Gold-only costs +99.44 SigmaAE versus All-4.

Binding decision:
- **PLS1 primary representation remains Gold + Silver + Platinum + Palladium.**
- No-Silver is retained only as a direction-heavy DEV Pareto reference.

---

## 6. Model-by-model method and decision ledger

### Ridge V1
- Input: CURRENT8.
- Target: Gold next-month log return.
- Scaling: StandardScaler training-fold only.
- Alpha grid: 0.01, 0.1, 1, 10, 100.
- DEV: 1520.9926 / 21 directions.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_RIDGE_RESULT_2026-09-28.md`

### Elastic Net V1
- Input: CURRENT8.
- Scaling: StandardScaler training-fold only.
- Alpha × L1-ratio frozen grid.
- DEV: 1590.3571 / 16.
- Mean zero coefficients: 4.45/8.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_ELASTICNET_RESULT_2026-09-28.md`

### Huber V1
- Input: CURRENT8.
- Scaling: StandardScaler training-fold only.
- Frozen alpha × epsilon grid.
- DEV: 1530.1300 / 20.
- Mean fitted training outlier fraction: ~18.24%.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_HUBER_RESULT_2026-09-28.md`

### PLS1 V1
- Input: CURRENT8.
- Single target: Gold next-month log return.
- Scaling: PLS internal scale=True.
- Components: 1..8, selected chronologically.
- DEV: **1420.0291 / 20**.
- All DEV origins selected only 1, 2 or 3 components.
- Decision: **RETAIN — strongest Challenger-B primary-price candidate.**
- Result: `GOLD_MONTHLY_CHALLENGER_B_PLS1_RESULT_2026-09-28.md`

### PLS2 V1
- Input: CURRENT8.
- Joint target: Gold/Silver/Platinum/Palladium next-month returns.
- Gold is evaluation target.
- DEV: 1489.3300 / **23**.
- Decision: RETAIN as secondary direction-improved PLS challenger.
- Result: `GOLD_MONTHLY_CHALLENGER_B_PLS2_RESULT_2026-09-28.md`

### GPReg-RBF V1
- Grup-ARGE-style ConstantKernel × RBF.
- X scaling only; normalize_y=True; optimizer=None.
- DEV: 1696.3365 / 16.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_GPREG_RBF_RESULT_2026-09-28.md`

### GPReg-Matérn V1
- Grup-ARGE-style ConstantKernel × Matérn.
- Grid includes nu=0.5,1.5,2.5.
- All DEV origins selected nu=2.5.
- DEV: 1637.9165 / 19.
- Better than GPReg-RBF but still noncompetitive.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_GPREG_MATERN_RESULT_2026-09-28.md`

### Extra Trees V1
- Two actually executed Grup-ARGE candidate configurations ported.
- No scaling.
- DEV: 1539.9221 / 20.
- ET_B selected 27/33 DEV origins.
- Mean tree importance led by Gold_VW and Silver_VW.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_EXTRA_TREES_RESULT_2026-09-28.md`

### HistGradientBoosting V1
- Two actually executed Grup-ARGE candidate configurations ported.
- early_stopping=False to prevent internal non-chronological validation.
- No scaling.
- DEV: 1840.2678 / 20.
- Worse than RW on DEV.
- Decision: NOT PROMOTED.
- Result: `GOLD_MONTHLY_CHALLENGER_B_HGB_RESULT_2026-09-28.md`

### ARIMA
Grup-ARGE candidate grid:
- (1,0,0), trend c
- (1,1,1), trend t
- (0,1,1), trend t

Input: raw completed monthly average Gold price level.

DEV:
- SigmaAE 1781.7822
- direction 15/33
- rel.MAE vs RW 1.0135

Decision: NOT PROMOTED.

### SARIMA
Grup-ARGE candidate grid:
- (1,0,0) × (1,0,0,12)
- (0,1,1) × (0,1,1,12)

Input: raw completed monthly average Gold price level.

DEV:
- SigmaAE 1751.5242
- direction 19/33
- rel.MAE vs RW 0.9963

Decision: NOT PROMOTED. Only marginally improves on Random Walk.

### Prophet
Grup-ARGE candidates:
- additive, changepoint_prior_scale 0.01
- multiplicative, changepoint_prior_scale 0.1
- seasonality_prior_scale 1.0

Input: raw completed monthly average Gold price level; no regressors.

DEV:
- SigmaAE 7521.1360
- direction 14/33
- rel.MAE vs RW 4.2782

Decision: **REJECT / NOT PROMOTED.**

Technical note:
- initial V1 run hit a Prophet/CmdStanPy backend compatibility failure before scientific Prophet results;
- clean V2 pinned cmdstanpy=1.2.5 and explicit CMDSTANPY;
- ARIMA and SARIMA were rerun in the same clean V2 workflow;
- final scientific trio authority is workflow run **36438580750**.
- Trio result: `GOLD_MONTHLY_CHALLENGER_B_CLASSICAL_TRIO_RESULT_2026-09-28.md`

---

## 7. 2025 and 2026 report-only summary

These values are **not selection authority**.

| Model | 2025 SigmaAE | 2025 Dir | 2026 Jan-Jul SigmaAE | 2026 Dir |
|---|---:|---:|---:|---:|
| Ridge | 1060.21 | 10/12 | 1382.50 | 5/7 |
| Elastic Net | 1078.90 | 11/12 | 1401.11 | 5/7 |
| Huber | 1051.82 | 10/12 | 1412.01 | 5/7 |
| PLS1 | 1058.90 | 10/12 | 1392.69 | **6/7** |
| PLS2 | 1067.92 | 10/12 | **1361.87** | 5/7 |
| GPReg-RBF | 1069.25 | 10/12 | 1726.53 | 3/7 |
| GPReg-Matérn | 1084.11 | 9/12 | 1766.21 | 3/7 |
| Extra Trees | 1019.72 | **11/12** | 1462.63 | **6/7** |
| HGB | **849.67** | 10/12 | 1751.62 | 4/7 |
| ARIMA | 1320.11 | **11/12** | 1954.68 | 2/7 |
| SARIMA | 1374.57 | **11/12** | 1849.41 | 2/7 |
| Prophet | 8109.54 | 1/12 | 5233.70 | 5/7 |

Important:
- HGB and Extra Trees look strong retrospectively in 2025, but this cannot override their weaker DEV status.
- 2026 cannot be used for rescue or model selection.

---

## 8. Existing external references — not rerun as Challenger-B

These already existed in the Gold Monthly program and were used as context, not newly rerun in this Challenger-B track:

- RBF/DWT-SVR family; frozen parent reference: DEV SigmaAE 1449.187363 / direction 19/33.
- Random Forest reference: DEV SigmaAE 1491.550694 / 20/33.
- XGBoost CURRENT8 and broader boosting work already existed.
- CatBoost PRICE reference: DEV SigmaAE 1460.433935 / 20/33.

These are not counted as new Challenger-B runs.

---

## 9. Challenger-A cross-family context

Known top references used only for contextual comparison:
- ChHHO-ANFIS: DEV SigmaAE 1413.029779 / 23/33.
- RBFNN DE-ABC: ~1415.8371 / 25/33.
- PLS1 Challenger-B: 1420.0291 / 20/33.
- GPR/MOGP LMC2_RBF_M32: ~1424.17 / 19/33.
- FULL7 ANN: 1428.86 / 22/33.
- REDUCED4 ANN: 1431.46 / 24/33.

Therefore PLS1 enters the high-performing cross-family price-error group but does not dominate the existing top two-objective frontier.

---

## 10. Explicitly not run in this final Challenger-B scope

By user instruction, after adding ARIMA, SARIMA and Prophet the following omitted Grup-ARGE families were **not** run:
- Seasonal Naive
- Drift
- Theta
- Optimized Theta
- SARIMAX_SAFE
- Dynamic Ridge
- exact Grup-ARGE Linear SVR port

Status: **OUT OF USER-AUTHORIZED CHALLENGER-B SCOPE / NOT RUN.**

They must not later be described as completed Challenger-B experiments unless a new explicit run is performed.

---

## 11. Final Challenger-B decision

### Primary Challenger-B model
**PLS1 V1, All-4 metals**
- DEV SigmaAE = **1420.0291**
- direction = 20/33
- All-4 metal set retained after frozen ablation.

### Secondary trade-off candidates
- **PLS2:** 1489.33 / 23 directions — stronger direction, weaker price.
- **PLS1 No-Silver ablation:** 1454.32 / 22 directions — DEV Pareto trade-off within metal subsets.

### Rejected / not promoted
Ridge, Elastic Net, Huber, GPReg-RBF, GPReg-Matérn, Extra Trees, HGB, ARIMA, SARIMA, Prophet.

### Main-path status
No Challenger-B experiment automatically replaces Challenger-A or activates any production selector/ensemble. Any future promotion requires a separately frozen comparison/decision stage.

---

## 12. Control and compliance summary

- DB remained READ_ONLY.
- No random split.
- No target-month leakage.
- DEV remained the only selection authority.
- 2025 remained locked report-only.
- 2026 remained quarantined report-only.
- Model-specific preprocessing was preserved rather than forcing all families into one preprocessing scheme.
- Classical univariate models used raw monthly Gold levels.
- Engineered-feature models used governed CURRENT8.
- Main Gold Monthly / Challenger-A path was not modified.
