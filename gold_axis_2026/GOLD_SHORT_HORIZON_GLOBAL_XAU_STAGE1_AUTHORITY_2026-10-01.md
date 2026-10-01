# GOLD SHORT-HORIZON GLOBAL XAU — Stage 1 Classical / Boosting Screen Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN  
**Parent:** `GOLD_SHORT_HORIZON_GLOBAL_XAU_PROJECT_MANIFEST.md`

## 1. Target
Historical development target:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- global XAU/USD daily spot-average representation
- H1/H3/H5 forward log returns.

BIST Metal Price is excluded.

## 2. Chronology
- history/training: through 2021
- DEV: 2022-2024
- 2025: frozen / forbidden for selection
- 2026: not selection authority
- expanding chronological refits every 5 origins
- horizon-specific target-maturity purge.

## 3. Feature blocks
- GOLD_ONLY
- CORE3 = Gold + Silver + Platinum
- CORE4 = CORE3 + Palladium
- CORE3_SAFE_EXTERNAL = CORE3 + H.15 Rates + H.10 FX + VIX + Nasdaq-100.

No WTI/Brent/GPR in first screen.

## 4. Models

Direction:
- Logistic L2
- LightGBM
- XGBoost.

Point return:
- Elastic Net
- LightGBM
- XGBoost.

Distribution:
- LightGBM quantile Q10/Q50/Q90.

No hyperparameter tuning.

## 5. Baselines

Direction:
- expanding historical UP prevalence
- trailing-252 UP prevalence.

Return:
- zero return
- expanding mean
- trailing-252 mean.

Quantiles:
- expanding empirical Q10/Q50/Q90
- trailing-252 empirical Q10/Q50/Q90.

## 6. Gates

Direction PASS:
- relative Brier improvement >= 1.0% versus best frozen baseline
- log loss not worse
- non-degenerate prediction dispersion.

Return PASS:
- relative MAE improvement >= 1.0%
- RMSE not worse.

Quantile PASS:
- mean Q10/Q50/Q90 pinball improvement >= 1.0%.

## 7. Horizon interpretation

Do not preselect H3 from the archived BIST project.

The global XAU data decide H1/H3/H5 independently.

A horizon is "complete-pass" only if all three heads pass.
Supporting partial-pass horizons remain documented.

## 8. No economic selection yet

No P&L, entry, exit, cost, or position-size rule is selected in Stage 1.

## 9. Next gate

Only after Stage 1 results are frozen:
- run robustness on successful global-XAU horizon/head contracts;
- 2025 stays unopened.
