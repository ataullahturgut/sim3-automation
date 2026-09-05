# Gold Control — Macro Event Successor V1 Score Preregistration

Date: 2026-09-05
Engine identity: `MACRO_EVENT_SUCCESSOR_V1`
Status at preregistration: source-data research only; **no score results have been inspected under this formula**.

## 1. Purpose and authority boundary

This document freezes the first successor score formula before historical score replay. It is a new successor definition; it is **not** a reconstruction of the archived `MACRO_EVENT` score.

The archived identity remains blocked because its exact NFP/unemployment/AHE scoring and normalization contract was not recovered.

This score is research context only. It has:
- no direction vote;
- no H=1 price forecast;
- no selector/ensemble authority;
- no action or position mapping;
- no Forecast Store or Decision Store write authority;
- no runtime promotion authority.

## 2. Inputs

Each monthly U.S. Employment Situation event requires all six governed DB inputs:
- NFP first-print actual;
- NFP Investing.com research consensus;
- unemployment-rate first-print actual;
- unemployment-rate Investing.com research consensus;
- AHE MoM first-print actual;
- AHE MoM Investing.com research consensus.

Missing-data rule: complete case only. No imputation, carry-forward, provider switching, or model-forecast substitution.

## 3. Raw surprises

For event t:

`e_nfp[t]   = actual_nfp[t] - consensus_nfp[t]`

`e_unemp[t] = actual_unemp[t] - consensus_unemp[t]`

`e_ahe[t]   = actual_ahe[t] - consensus_ahe[t]`

The definition follows the standard macro-news convention of announced value minus pre-release market consensus.

## 4. Point-in-time standardization

For each component i, define `sigma_i[t]` as the sample standard deviation (`ddof=1`) of **all prior complete-case surprises for that same component**, using only events strictly before t.

Rules:
- minimum prior complete-case history = 24 events;
- no current or future event may enter `sigma_i[t]`;
- no clipping/winsorization;
- no demeaning by a full-sample mean;
- if fewer than 24 prior events exist or prior sigma is zero/non-finite, state = `INSUFFICIENT_HISTORY` and no composite score is issued.

Standardized surprises:

`z_i[t] = e_i[t] / sigma_i[t]`

This adapts the common historical-standard-deviation normalization to a point-in-time implementation.

## 5. Gold-oriented signs

The successor score is oriented so **positive = gold-supportive macro news** and **negative = gold-adverse macro news**.

Frozen orientation hypotheses:
- stronger-than-expected NFP is treated as gold-adverse: `g_nfp = -z_nfp`;
- higher-than-expected unemployment is treated as gold-supportive: `g_unemp = +z_unemp`;
- hotter-than-expected AHE MoM is treated as gold-adverse/hawkish: `g_ahe = -z_ahe`.

The NFP/unemployment orientation is consistent with the established event-study literature in which unexpectedly good U.S. economic news tends to be negative for gold. The AHE orientation is a preregistered policy-rate/hawkishness hypothesis and remains subject to validation; it must not be flipped after viewing results under V1.

## 6. Composite score and breadth

Equal weights are frozen to avoid fitted or post-result weights:

`macro_gold_score[t] = (g_nfp[t] + g_unemp[t] + g_ahe[t]) / 3`

Breadth:
- `adverse_breadth` = number of component scores `< 0`;
- `supportive_breadth` = number of component scores `> 0`.

No component may be dropped when present and no weights may be changed in V1.

## 7. Frozen state mapping

- `GOLD_ADVERSE_MACRO_SHOCK` if `macro_gold_score <= -1.0` **and** `adverse_breadth >= 2`.
- `GOLD_SUPPORTIVE_MACRO_SHOCK` if `macro_gold_score >= +1.0` **and** `supportive_breadth >= 2`.
- otherwise `MACRO_MIXED_OR_SMALL`.

The +/-1.0 threshold is a preregistered standardized-effect threshold, not the recovered archived `macro_score <= -1` rule and must not be described as the old threshold.

## 8. Chronological evidence windows

Frozen windows by reference month:
- DEV: `2016-01..2020-12`;
- VAL: `2021-01..2023-12`;
- LOCK: `2024-01..2026-08`.

The two known incomplete source months (`2020-08`, `2025-10`) remain excluded by the already-frozen complete-case source rule.

No formula, sign, threshold, history rule, or weight may be changed after looking at DEV/VAL/LOCK results under `MACRO_EVENT_SUCCESSOR_V1`. Any change requires a separately named successor revision/change-control.

## 9. Event-reaction confirmation is not yet claimed

The recovered archived outer trigger also referenced `FAST=DOWN` and same-day gold return <= -0.5%. Those conditions are **not silently imported into this score**.

V1 score replay may establish deterministic macro-surprise context. Promotion to an event-confirmed gold context requires a separately frozen, point-in-time gold event-reaction data source/window and validation contract. Until then, score results remain research-only and cannot vote on direction.

## 10. External methodological basis

Federal Reserve research commonly defines macroeconomic surprise as actual release minus median market consensus and normalizes surprise series by historical standard deviation. Federal Reserve work also emphasizes using the latest pre-release survey expectation. Gold event-study literature finds that U.S. macro news can move gold very quickly and that unexpectedly good economic news tends to be negative for gold; NFP and unemployment announcements are among the relevant releases.
