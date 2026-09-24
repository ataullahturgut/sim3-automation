# GOLD CONTROL — Direction Engine Estimation-Window Robustness V1 Preregistration

**Identity:** `DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESEARCH`  
**Date:** 2026-09-24  
**Branch:** `gold-direction-history-window-robustness-v1-20260924`  
**Canonical authority at preregistration:** `gold-r4-direction-engine@66fe1bac635e6135128d478aab9a6cba74883948`

## 1. Purpose

This is a chronology-safe **history / estimation-window robustness audit** of the existing Direction Engine components. It is not a new feature search, not a new classifier-family search, and not a 2025/2026 rescue.

The experiment asks whether the frozen components are materially sensitive to how much matured history is used.

Components audited independently:

1. SQRT-HAR-DR risk reference;
2. Frozen Primary UP Verifier V2 competence memory;
3. One-Sided UP-2 Logit V1 residual training memory.

The first-stage audit changes **one factor at a time**. Downstream routes remain frozen while the component under audit changes, so a result cannot be attributed simultaneously to route changes and history changes.

## 2. Authority basis

Methodological basis:

- rolling/forecast-origin evaluation: Hyndman & Athanasopoulos, Forecasting: Principles and Practice, time-series cross-validation;
- estimation-window uncertainty / window-size snooping: Rossi & Inoue (2012), *Out-of-Sample Forecast Tests Robust to the Choice of Window Size*, JBES;
- structural change and optimal estimation windows: Pesaran & Timmermann (2007), *Selection of Estimation Window in the Presence of Breaks*, Journal of Econometrics;
- forecast direction under structural instability: Pesaran & Timmermann (2004), *How Costly is it to Ignore Breaks when Forecasting the Direction of a Time Series?*, International Journal of Forecasting;
- multiple structural breaks: Bai & Perron (1998/2003).

Binding project authority remains the canonical manifest. This V1 does **not** implement a structural-break model. Break-conditioned estimation is deferred until the fixed/expanding window surface is observed. That prevents a break algorithm from becoming an additional simultaneous degree of freedom.

## 3. Governance

- No random split.
- Only matured rows available before each target may enter training, competence, calibration or thresholds.
- 2025 is **not used anywhere in this V1**: not for selection, tuning, ranking, thresholding, diagnostics or tie-breaking.
- 2026 is not used.
- Research DB access is read-only.
- No production/runtime write.
- Frozen feature definitions, expert membership, eligibility thresholds, Wilson confidence level, tie order, UP-2 classifier C/solver/class-weight rule and threshold formula remain unchanged.
- HIGH RISK is not DOWN.
- Router ABSTAIN is not DOWN.
- UP-2 ABSTAIN is not DOWN.
- External and governed source boundaries remain explicit.
- A history variant is a **new research comparison**, never a silent replacement of the frozen baseline.

## 4. Source panels

### 4.1 Governed panel

Governed five-minute source:
`public.xau_intraday_research_cache_5m`

Frozen semantics:
- America/New_York calendar-date grouping;
- weekdays;
- >=240 bars/day;
- no cross-date intraday returns.

### 4.2 Corrected external historical extension

Pinned corrected external daily spine:

`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`

Pinned source commit:

`509c5ffa762f4ea49644b8ffe723ed2591ba52bf`

The external panel is already classified only as a harmonized historical research extension, not production authority.

Extended chronology uses:
- external corrected V2 through 2021-12-31;
- governed source from 2022 onward.

No overlap rows are double-counted.

## 5. Frozen baseline reproduction gate

Before any robustness result is accepted, the workflow must reproduce the frozen reference quantities available from the pinned authorities.

At minimum:
- governed SQRT 2022/2023/2024 alarm counts = 11 / 2 / 17;
- frozen Router historical 2022/2023 calls = 22 / 19;
- frozen Router 2024 = 42 calls = 26 TP + 16 FP;
- UP-2 external formation = 98 rows = 46 UP + 52 DOWN;
- UP-2 governed residual 2022/2023/2024 = 11 / 2 / 13 rows;
- frozen UP-2 pooled 2022-2024 = 11 calls = 8 true UP + 3 false UP.

If reproduction fails, final status is `BLOCKED_BASELINE_REPRODUCTION`; no window conclusion is allowed.

## 6. SQRT history audit

The SQRT equation remains unchanged:

`SD_(t+1) ~ 1 + SD_t + mean5(SD) + mean22(SD)`

and forecast DR is the square of the strictly positive predicted SD.

Formation HIGH-RISK threshold remains nearest-rank Q80 of training target DR.

Evaluation years: **2022, 2023, 2024 only**.

Panels:

1. `GOVERNED_FROZEN_EXPANDING` — exact frozen governed baseline;
2. `EXTENDED_EXPANDING` — all matured corrected-external + governed history;
3. `EXTENDED_ROLLING_W` with deterministic dense grid:
   `W = 250, 275, 300, ..., 1000` supervised rows.

A W is scored only when it is feasible for all required annual evaluations; infeasible cells are labeled, not shortened silently.

Metrics:
- MSE;
- DR-QLIKE;
- OOS R2 vs training historical mean;
- HIGH-RISK ROC AUC;
- alert count / coverage;
- alert precision and recall;
- training size;
- positive-SD integrity.

No single W is promoted in V1. Report the full surface, Pareto/non-dominated windows, and local sensitivity.

## 7. Router V2 competence-memory audit

Direct expert **states themselves remain frozen**. This audit changes only the matured history supplied to the existing competence calculation.

Expert membership remains:
- TTSM-S2;
- TTSM-S1;
- Bonato AR1_RM QBoost h=1;
- AR1_RM_LOGIT;
- RM_LOGIT.

Legacy bucket, support >=30 calls, precision >50%, FPR <50%, one-sided 90% Wilson LCB ranking and tie order remain unchanged.

Evaluation years: **2022, 2023, 2024 only**.

Policies:

1. `FROZEN_YEAR_RESET` — existing historical contract: Y-1 formation + causal within-year matured rows;
2. `EXPANDING` — all matured aligned rows available before each target;
3. `ROLLING_W` — last W matured aligned rows before each target, with
   `W = 30, 40, 50, ..., 500`.

Extended history before 2022 may use corrected external 2020-2021 aligned expert rows. Governed 2022-2024 evaluation rows remain the scored target surface.

Metrics:
- calls;
- TP / FP;
- UP precision;
- false-UP FPR on actual DOWN;
- actual-UP recall;
- coverage;
- Wilson90 precision LCB;
- selected-expert counts.

No winner is promoted in V1. Report the full precision/FPR/coverage frontier and whether results form a broad stable region or isolated spikes.

## 8. UP-2 residual-memory audit

The **route is held frozen** to the current frozen SQRT + Frozen Router V2 residual route. Router/SQRT window variants do not redefine the UP-2 population in this V1.

Nine features remain unchanged.

Classifier remains:
- L2 logistic;
- C=1.0;
- lbfgs;
- no class weighting;
- training-only standardization.

Threshold remains:
`tau = max(0.50, nearest-rank Q80 of strictly-prequential historical actual-DOWN p_UP scores)`.

Minimums remain:
- 40 prior rows before a prequential calibration score;
- 20 historical DOWN calibration scores.

Evaluation years: **2022, 2023, 2024 only**.

Policies:

1. `EXPANDING_FROZEN` — exact existing training-history rule;
2. `ROLLING_W` using the last W matured residual cases with
   `W = 60, 65, 70, 75, 80, 85, 90, 95`.

If a W cannot satisfy calibration support, mark `BLOCKED_CALIBRATION_SUPPORT`. Do not weaken the frozen minimums.

Metrics:
- n;
- UP2 calls;
- true / false UP;
- UP precision;
- missed-UP recall;
- false-UP FPR;
- coverage;
- Wilson90 precision LCB;
- AUC;
- Brier;
- tau.

Apply the existing pre-2025 support gate separately to every history policy. Do not invent a new success threshold.

## 9. V1 decision rule

V1 is a **robustness mapping study**, not a model-selection study.

Final classifications are limited to:

- `ROBUSTNESS_SURFACE_COMPLETE`;
- `HISTORY_SENSITIVE`;
- `HISTORY_INSENSITIVE_WITHIN_TESTED_RANGE`;
- `BLOCKED_BASELINE_REPRODUCTION`;
- `BLOCKED_DATA_OR_SOURCE_INTEGRITY`.

Do not declare an “optimal” start year/window merely because it has the best point estimate.

A potential V2 memory policy may be proposed only if V1 shows a broad, neighboring region with coherent improvements rather than an isolated best W. That V2 must be preregistered before any 2025 replay under that policy.

## 10. Required artifacts

Produce:

- `GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESULT_2026-09-24.json`
- `GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESULT_2026-09-24.md`
- `GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_SQRT_SURFACE_2026-09-24.csv`
- `GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_ROUTER_SURFACE_2026-09-24.csv`
- `GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_UP2_SURFACE_2026-09-24.csv`

The final report must explain in simple Turkish:
1. whether older history helps or hurts each component;
2. whether any effect is broad/stable or a narrow spike;
3. whether external history changes the conclusion materially;
4. whether a V2 history policy is justified;
5. what remains frozen.

No manifest update and no runtime promotion in V1.
