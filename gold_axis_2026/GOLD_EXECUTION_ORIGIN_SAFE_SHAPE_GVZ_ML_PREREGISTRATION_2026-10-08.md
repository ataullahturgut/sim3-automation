# GOLD EXECUTION — ORIGIN-SAFE PRICE SHAPE + LAGGED GVZ ML CHALLENGE
**Registered:** 2026-10-08
**Status:** Research-only challenger. Not a trading policy or replacement for frozen PRAMV / FSMR / SESSION lineage.

## Hypothesis
On audited XAUUSD 15-minute BID data, pre-origin path shape and interactions with the previously known GVZ state may add information to the previous two half-hour impulses, separately for DAY 09:00-17:00 and regular weekday OVN 17:00-next eligible 09:00, all Europe/Istanbul. Friday 17:00-Monday 09:00 (64h) is excluded. Old SESSION labels are never reused.

## Data gate
The existing audited source loader (private Neon) retains source identity and frozen target gates. Features derive only from 15-minute bars that **end no later than prediction time**. GVZ observation dates must be strictly earlier than each Turkish issue date; its independent release-vintage proof remains limited. No same-day future GVZ, future macro surprise, or target-window return is permitted.

2022 supplies warmup history; 2023-2024 are scored using calendar-month chronological refits with previously matured labels, 2025 uses a frozen 2024 endpoint fit. Previously examined 2025 is retrospective transport only, NEVER fresh blind OOS.

## Four fixed specifications
1. BASE_LOGIT: previous two 30m impulses. DAY includes the last fully matured overnight return.
2. SHAPE_LOGIT: baseline plus completed 4h/2h return, asymmetric semivariance, 15m volatility, sign persistence, path efficiency, jump share and prior completed DAY/OVN return.
3. SHAPE_GVZ_LOGIT: SHAPE_LOGIT plus previous-date GVZ log and two GVZ × impulse interactions.
4. SHAPE_GVZ_HGB: identical shape+GVZ predictors using strongly regularized shallow histogram gradient boosting (max leaf nodes 7, min samples leaf 35, max depth 3, 90 iterations, learning rate .04, L2 10).

Logistic heads use training-only StandardScaler and LogisticRegression L2 C=.3. Both methods use p(UP)>=.50; no new abstention cutoff. Parameters fixed before metrics; no 2025 tuning.

## Measurement and promotion gate
For every target/year: N, accuracy, BA, UP/DOWN recall, TN/FP/FN/TP, Brier, log loss and predicted-UP share. Compare exactly matching eligible dates across all models. Report DEV stability separately by year: BA>50% and DOWN recall>=30% for both 2023 and 2024 is a minimal retention screen, not statistical significance. Require paired improvement vs simple base and relevant FSMR4 matched records, then statistical uncertainty and untouched 2026+ truly prospective confirmation before any production promotion.

2025/2026 historic errors must not determine which features, thresholds, experts or windows are chosen. No raw vendor quote prices or dated trade signals are published in Git; date-level predictions remain private GitHub Actions artifacts. No bank-executable profit is claimed.

## Scientific evidence
Xu et al. (2020), Resources Policy 69, 101830 (10.1016/j.resourpol.2020.101830); Sobti et al. (2021), International Review of Financial Analysis 78, 101893 (10.1016/j.irfa.2021.101893); Bailey et al. (2017), Journal of Computational Finance, backtest-overfitting research (10.21314/JCF.2016.322).

## Reproducibility
Script gold_axis_2026/tools/gold_execution_origin_safe_shape_gvz_ml_challenge_20261008.py; workflow .github/workflows/gold-origin-safe-shape-gvz-ml-20261008.yml. If no successful execution has occurred, no new numerical result is asserted.
