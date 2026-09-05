# Gold Control — Macro Event Successor V2 Robust-Scale Score Preregistration

Date: 2026-09-05
Engine identity: `MACRO_EVENT_SUCCESSOR_V2`
Parent research source lane: `MACRO_EVENT_SUCCESSOR_V1_RESEARCH_DATA_PLANE_R1`
Status at preregistration: **formula frozen before any V2 score replay has been executed or inspected**.

## 1. Why V2 is a separate identity

`MACRO_EVENT_SUCCESSOR_V1` used an expanding sample standard deviation of prior surprises. Its completed replay showed that the extreme 2020 labour-market observations dominate the scale sufficiently that no strong shock state appears in the 2021-2026 VAL/LOCK windows. That finding is retained as V1 evidence and is not edited away.

V2 is therefore a new successor identity. It changes only the surprise-scale estimator. It does **not** claim to reconstruct the archived `MACRO_EVENT` identity and it does not retroactively modify V1.

## 2. Authority boundary

V2 is research context only. It has:
- no direction vote;
- no H=1 price forecast;
- no selector/ensemble authority;
- no action or position mapping;
- no Forecast Store or Decision Store write authority;
- no runtime promotion authority.

The source panel is read from the governed Neon research source tables. V2 itself performs no production data write.

## 3. Frozen input panel

Use exactly the same six governed source series and source retrieval run as V1:
- `MACRO_NFP_ACTUAL_FIRST_PRINT`
- `MACRO_NFP_CONSENSUS_PIT`
- `MACRO_UNEMP_ACTUAL_FIRST_PRINT`
- `MACRO_UNEMP_CONSENSUS_PIT`
- `MACRO_AHE_ACTUAL_FIRST_PRINT`
- `MACRO_AHE_CONSENSUS_PIT`

Frozen source retrieval run: `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`.

Reference-month window: `2016-01..2026-08`.
Known complete-case exclusions remain `2020-08` and `2025-10`. No imputation, carry-forward, provider switching, or model substitution is permitted.

## 4. Raw surprises

For event t:

`e_nfp[t]   = actual_nfp[t] - consensus_nfp[t]`

`e_unemp[t] = actual_unemp[t] - consensus_unemp[t]`

`e_ahe[t]   = actual_ahe[t] - consensus_ahe[t]`

The economic zero remains `actual = consensus`. V2 therefore does **not** subtract a historical median from the numerator; robust statistics are used only to estimate scale.

## 5. Robust expanding scale

For each component i at event t, use only prior complete-case surprises strictly before t.

Minimum history: 24 prior complete-case events.

Primary scale:
1. `m_i[t] = median(prior surprises)`
2. `MAD_i[t] = median(|e_i - m_i[t]|)`
3. `scale_i[t] = 1.4826 * MAD_i[t]`

The factor 1.4826 calibrates MAD to the standard-deviation scale under a normal reference distribution while preserving MAD's outlier robustness.

### Deterministic zero-MAD fallback

If the MAD scale is zero or non-finite, use a robust IQR scale on the same prior sample:

`scale_i[t] = (Q75 - Q25) / 1.3489795003921634`

Quantiles use deterministic linear interpolation on the sorted prior sample:
- `h = (n - 1) * p`
- `j = floor(h)`
- `gamma = h - j`
- `Q(p) = x[j] + gamma * (x[j+1] - x[j])`, with the natural endpoint rule when `j = n-1`.

If the IQR fallback is also zero or non-finite, that event receives `INSUFFICIENT_HISTORY` and no composite score is issued.

No classical standard-deviation fallback is allowed in V2.

## 6. Robust standardized surprises

For each component:

`z_i[t] = e_i[t] / scale_i[t]`

The numerator remains the actual-minus-consensus surprise so that sign semantics do not drift when historical surprise medians are non-zero.

## 7. Gold-oriented signs

Keep the V1 orientation unchanged so that V2 isolates the normalization change:
- `g_nfp = -z_nfp`
- `g_unemp = +z_unemp`
- `g_ahe = -z_ahe`

Positive component score = gold-supportive macro news. Negative component score = gold-adverse macro news.

## 8. Composite score and breadth

Keep V1 equal weights unchanged:

`macro_gold_score_v2[t] = (g_nfp[t] + g_unemp[t] + g_ahe[t]) / 3`

Breadth:
- `adverse_breadth` = count of component scores `< 0`
- `supportive_breadth` = count of component scores `> 0`

No post-result component dropping or weight changes are permitted.

## 9. Frozen state mapping

Keep the V1 thresholds unchanged because both standard deviation and scaled MAD/IQR are calibrated to a sigma-like scale:
- `GOLD_ADVERSE_MACRO_SHOCK` if `macro_gold_score_v2 <= -1.0` and `adverse_breadth >= 2`
- `GOLD_SUPPORTIVE_MACRO_SHOCK` if `macro_gold_score_v2 >= +1.0` and `supportive_breadth >= 2`
- otherwise `MACRO_MIXED_OR_SMALL`

No threshold search is permitted under V2.

## 10. Evidence windows

Unchanged:
- DEV: `2016-01..2020-12`
- VAL: `2021-01..2023-12`
- LOCK: `2024-01..2026-08`

The V2 formula, fallback hierarchy, signs, weights, thresholds, and minimum-history rule are frozen before the V2 replay.

## 11. Engineering acceptance gates

A V2 replay is engineering-valid only if all are true:
- exact frozen source run and exact 126 complete-case months are used;
- source input fingerprint is reported;
- prefix invariance passes for every event;
- deterministic replay passes;
- no Forecast/Decision authority-store count changes before/after;
- no runtime/engine state write occurs;
- no model result is persisted to Neon under this research replay.

Shock frequency is **not** an engineering pass/fail gate; it is an observed model property.

## 12. Promotion stop point

Even if V2 produces plausible shock states, V2 cannot be promoted from macro-score replay alone. Promotion requires a separately frozen point-in-time gold event-reaction source/window and validation contract. That validation must be defined before inspecting the corresponding reaction-performance results.

## 13. Methodological basis

Federal Reserve event-study work defines macroeconomic surprise as announced value minus pre-release market expectation and commonly scales surprises for cross-series comparability. V2 preserves that actual-minus-consensus definition but replaces the non-robust scale estimator with robust scale estimators. Scaled MAD is a standard robust dispersion estimator; the 1.4826 factor places it on a normal-theory standard-deviation scale. IQR divided by 1.3489795003921634 is the corresponding normal-calibrated robust fallback.

This methodological change is intentionally limited to the denominator so that the economic meaning of zero surprise, the component signs, equal weights, and state thresholds remain unchanged from V1.