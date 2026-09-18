# GOLD CONTROL — DIRECTION_BCARS_SV_V1_RESEARCH LOCKED 2025 TEST

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCARS_SV_V1_RESEARCH`  
**Status:** `LOCKED_2025_HISTORICAL_REPLAY_COMPLETE / EVENT_OVERLAY_NOT_YET_APPLIED`  
**Pre-2025 checkpoint commit:** `ab7ff7a5883463bad659a958e71db4842b7ce07a`  
**Weekly input SHA-256:** `e7048cb9e478495e8832486cac4f763260dbcca6ab329ef7f4fc5e8216a41d9b`

No model rule was changed after the pre-2025 checkpoint.

## Locked 2025 result

- n = 52
- accuracy = 0.6730769231
- balanced accuracy = 0.4861111111
- actual UP / DOWN = 36 / 16
- forecast UP / DOWN = 51 / 1
- UP sensitivity = 0.9722222222
- DOWN sensitivity = 0.0000000000
- TP / TN / FP / FN = 35 / 0 / 16 / 1
- always-UP accuracy = 0.6923076923
- previous-week-sign accuracy = 0.5576923077

Continuous up-ratio forecast:
- B-CARS MSE = 0.0807706176
- expanding historical-mean MSE = 0.0819350078
- source-style up-ratio R2_oos = 0.0142111440

Derived Beta-tail probability diagnostic:
- Brier = 0.2367432044
- log loss = 0.6669115512
- P_ext(UP) range = 0.4985609991 .. 0.6738220694

Raw-scale forecast mean:
- mean = 0.5733132901
- range = 0.4989272738 .. 0.6204476915

## Interpretation

The positive source-style up-ratio R2_oos shows a small continuous-forecast improvement over the historical-mean up-ratio benchmark in 2025. It does **not** translate into useful two-sided return-direction discrimination.

The native direction rule produces 51 UP forecasts and one DOWN forecast. The single DOWN forecast targets 2025-03-03 and is incorrect. All 16 realized DOWN weeks are therefore missed.

Raw accuracy remains below the always-UP baseline and balanced accuracy is below 0.50.

The complete 52-row 2025 forecast table is frozen in GitHub before the 19-event volatility overlay.
