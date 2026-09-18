# GOLD CONTROL — DIRECTION_BCT_CTW_V1_RESEARCH LOCKED 2025 TEST

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCT_CTW_V1_RESEARCH`  
**Status:** `LOCKED_2025_HISTORICAL_REPLAY_COMPLETE / EVENT_OVERLAY_NOT_YET_APPLIED`  
**Pre-2025 checkpoint:** `9121a15883e5788b8ef422bc8884994e7d9d4845`  
**Frozen weekly forecast table:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`

## Frozen model

The 2025 replay uses the unchanged preregistered BCT/CTW model:
- rolling 52 weekly signs;
- first 10 signs as fixed initial context;
- maximum depth D=10;
- beta=0.5;
- Jeffreys Dirichlet(1/2,1/2) transition priors;
- exact CTW model averaging;
- UP iff P(UP)>=0.5;
- no tuning, smoothing, NO_SIGNAL or other Gold Control motor inputs.

## Locked 2025 result

- n = 52
- accuracy = 0.6923076923
- balanced accuracy = 0.5000000000
- Brier score = 0.2320851721
- log loss = 0.6578097877
- actual UP / DOWN = 36 / 16
- forecast UP / DOWN = 52 / 0
- UP sensitivity = 1.0000000000
- DOWN sensitivity = 0.0000000000
- TP / TN / FP / FN = 36 / 0 / 16 / 0
- always-UP accuracy = 0.6923076923
- previous-week-sign accuracy = 0.5576923077
- mean P(UP) = 0.6179186590
- P(UP) range = 0.5195495534 .. 0.7344672524

## Interpretation

The complete 2025 table was frozen before the 19-event volatility overlay.

BCT/CTW must be evaluated against both class balance and the failed 2024 validation. A 2025 improvement cannot retroactively change D, beta, the 52-week window or the prior under this identity.

Probability quality is interpreted jointly with direction metrics. The exact Bayesian averaging is expected to avoid the VLMC-BS 0/1 probability pathology; this result page reports the realized range rather than assuming that advantage.
