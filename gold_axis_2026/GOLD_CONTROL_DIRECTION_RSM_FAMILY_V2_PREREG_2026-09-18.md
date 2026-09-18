# GOLD CONTROL — DIRECTION_RSM_FAMILY_V2_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_FAMILY_V2_RESEARCH`  
**Status:** `FROZEN_BEFORE_2025_FAMILY_REPLAY`  
**Parent baseline:** `DIRECTION_RSM_V1_RESEARCH`  
**Evidence class:** historical research replay only; no runtime or production authority

## 1. Purpose

Re-open the first direction-research family and reproduce the full source-feasible Return Signal Momentum family from Liu, Papailias & Quinn (2021), rather than treating the previously evaluated rolling RSM-52 baseline as the complete family.

Primary authority:
Liu, J., Papailias, F. & Quinn, B. (2021), *Direction-of-change forecasting in commodity futures markets*, International Review of Financial Analysis 74, 101677, DOI `10.1016/j.irfa.2021.101677`.

Related RSM authority:
Papailias, F., Liu, J. & Thomakos, D.D. (2021), *Return signal momentum*, Journal of Banking & Finance 124, 106063.

## 2. Source-family formulas

For weekly return sign
`x_t = 1[r_t>0]`, else `0`.

### RSM(k)

`P_RSM(t+1;k) = (1/k) * sum_{i=t-k+1}^t x_i`.

Direction:
- UP iff `P_RSM >= 0.5`;
- DOWN otherwise.

### ERSM(k)

The source exponential extension is retained exactly:

`alpha = 2/(k+1)`

`w_i = alpha * (1-alpha)^(t-i)`

`P_ERSM(t+1;k) = sum_{i=t-k+1}^t w_i*x_i`.

The finite-window weights are **not renormalized**. This follows the published Equation (2)-(3), where the selected alpha places approximately 86% of total exponential mass inside the k-period lookback.

Direction:
- UP iff `P_ERSM >= 0.5`;
- DOWN otherwise.

No alternate alpha, weight normalization, threshold shift or smoothing is allowed under V2.

## 3. Weekly return construction

Source research data:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

The source paper states that daily percentage returns are calculated and aggregated to weekly returns. V2 therefore uses:

1. New-York-local Monday-Friday daily observations;
2. simple daily percentage return
   `r_d = C_d/C_(d-1)-1`,
   using the immediately preceding governed observation;
3. Monday-start calendar week;
4. weekly return
   `r_w = sum_{d in week} r_d`;
5. weekly sign `x_w=1[r_w>0]`, else 0.

No interpolation, forward-fill or provider substitution.

A non-authoritative construction audit will compare this sign series with the previous weekly-close log-return sign series. That audit cannot change the V2 source-text-faithful construction after 2025 is opened.

## 4. Source-feasible lookback family

The source paper evaluates k in:
`26, 52, 104, 156, 208, 260, 520, 780` weeks.

Under the retained same-source chronology beginning in March 2022, only the following have pre-2025 evaluable forecasts:

`k in {26,52,104}`.

Therefore V2 freezes exactly six source-family variants:

- `RSM_26`
- `RSM_52`
- `RSM_104`
- `ERSM_26`
- `ERSM_52`
- `ERSM_104`.

Windows 156+ are `NOT_EVALUABLE_WITH_SAME_SOURCE_PRE2025_HISTORY` and will not be rescued by provider splicing or older non-equivalent series.

RSM and ERSM are fixed-k lookback filters. V2 does **not** invent a separate recursive RSM/ERSM identity. The source paper reports RSM/ERSM as one row per k; explicit rolling/recursive rows are separately reported for the dynamic probability / Markov classes.

## 5. Chronology and comparison

- 2022: source-history / warm-up;
- 2023: development/audit for variants with sufficient history;
- 2024: fixed pre-2025 evaluation;
- 2025: all six variants are replayed unchanged only after the complete pre-2025 family checkpoint is committed;
- 19-event volatility overlay is applied only after the complete 2025 forecast tables are frozen.

No random split.

### Fair common-support comparison

Because k=104 becomes eligible later than k=26/52, the primary family comparison before 2025 uses the **common 2024 target-week support beginning at the first target week on which all six variants are simultaneously eligible**.

Each variant's full own-support 2023/2024 metrics are also retained descriptively.

No single Gold winner is selected before 2025 unless a later explicit promotion rule is separately authorized. All six source-feasible variants will be frozen and carried unchanged into 2025. Thus 2025 cannot select k or RSM-versus-ERSM under V2.

## 6. Required metrics

For every variant:
- n;
- success rate / accuracy;
- balanced accuracy;
- Brier score;
- log loss;
- actual UP/DOWN;
- forecast UP/DOWN;
- UP sensitivity;
- DOWN sensitivity;
- TP/TN/FP/FN;
- always-UP baseline;
- previous-week-sign baseline;
- probability min/mean/max.

Also report:
- source construction sign concordance versus weekly-close log-return signs, pre-2025 only;
- common-support 2024 comparison;
- complete 2025 tables before event overlay.

The source paper's primary direction metric is success rate. Gold Control additionally requires balanced accuracy and probability-quality diagnostics so class-degenerate forecasts are not misrepresented.

## 7. Locks

Forbidden under V2:
- choosing k from 2025;
- changing alpha from 2025;
- renormalizing ERSM weights after seeing outcomes;
- changing the 0.5 threshold;
- switching weekly-return construction after 2025;
- provider/source splicing to obtain k>=156;
- adding FAST/GVZ/BOCPD/Macro/Emergency inputs;
- adding NO_SIGNAL;
- event-conditioned tuning;
- post-2025 rescue under the same identity.

This V2 is the corrected source-family replication stage only. Gold-context extensions remain a later, separately governed ablation stage.
