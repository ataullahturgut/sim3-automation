# Pre-registration: XAU session UP/DOWN 2026 drift-aware causal experiment
Date: 2026-10-08; project GOLD INTRAMONTH, Turkey 09→17 (DAY) and 17→next09 (regular OVN). This registration precedes running the coded tests described below; the 2026 outcomes have been examined in older studies, so subsequent results are **retrospective research, not blind out-of-sample evidence**.

## Falsifiable mechanism
Gold's 2026 regime changed label priors, scale and return-to-volatility relationships. Expanding static pre-2026 HGB and logistic models may exhibit probability-calibration collapse and excessive UP predictions. **Do not mistake greater DOWN recall from class-balanced reweighting for more information:** a trivial always-DOWN model has DOWN recall 100% and balanced accuracy 50%. Improve both recalls over matched BASE and original SHAPE_GVZ_HGB with an as-of-fitted, explicit adaptation, or reject.

## Three restricted fixed candidates, NO post-hoc 2026 tuning
(A) `EW_BAL_GVZ_LOGIT`: same original 12 price-shape variables + three origin-safe previous-day GVZ variables, StandardScaler logistic (C=0.3), training records weighed by exponential age half-life **252 calendar days** and inverse empirical *lagged fit-sample class share* (normalized per class). Decision at 0.5, no new 2026 features.
(B) `EW_BAL_VIX_LOGIT`: identical formula, VIX/GVZ divergence 18 variables instead.
(C) `ROLL_504_BAL_GVZ_LOGIT`: 504-calendar-day training window, equal weighted class-balanced StandardScaler logistic (C=0.3). If source history <250 records or no 2 classes, ABSTAIN (no imputation or future refit).
(D) `EQUAL_GVZ_VIX`: simple probability average of (A) and (B), evaluated as a fourth predeclared combination, no fitted ensemble weight.

Original fully fixed `FROZEN_SHAPE_GVZ_HGB_2021` and `BASE_LOGIT_2022` are reference research baselines. All candidate fits occur at **first day of calendar month**, include only labels mature prior month opening, no within-month label in that month's refit. 2023-24 DEV months are forward-chaining with prior history; 2025 and 2026 months are prequential stress, with 2026 **earlier months' matured labels** legitimately used for later monthly decisions, versus an additional `FROZEN_PRE2026` branch that never uses 2026 labels. This removes ambiguity between static holdout and causal online adaptation. No 2026-sample hyperparameter optimization.

## No-illusion acceptance rule
Primary target is **OVN**, count and report all eligible compared dates (never cherry pick high-confidence days). Report BA, DOWN and UP recall, Brier, year, source and month, 2025–2026 paired save/break and exact McNemar p, plus class-specific confusion matrix, 2026 observation coverage; compare same rows. Require 2023-24 DEV BA >=55%, 2025 retrospective BA >=55%, 2026 mirror BA >=55%, 2026 source-native subset BA>=55% and DOWN recall >=50% on all; p-value <0.05 vs existing paired HGB, and no monthly catastrophic July period (>=10 decisions with BA <35%). These are strict research criteria, not trading validation. Entire dataset is 2020–25 EV Dukascopy BID M15; mirror 2026 Jan–Aug20 quote gates (same-upstream cross-publisher) and first-party direct 2026 short panel are separately identified. No bank price/commission, no champion without unseen forward test.

## Domain-shift diagnostics without future leakage
Report preorigin 4h realized-volatility, jumps and GVZ distribution change 2025 to 2026 using distributional comparisons (KS, median scale, zero-range quarantines) and direction label shift separately. These **post-study diagnostics** cannot become causal trading features or preselected model gates.

Reference motivation (not performance evidence): Awartani/Hussain/Virk, 2024, doi:10.1016/j.irfa.2024.103486 (asymmetric gold intraday monetary shocks); Sobti, 2025, doi:10.1016/j.irfa.2025.104380 (macro gold jumps); financial abstention risk-coverage needs class persistence-matched checks (2026, doi:10.3390/jrfm19080609). No promised accuracy gain.
