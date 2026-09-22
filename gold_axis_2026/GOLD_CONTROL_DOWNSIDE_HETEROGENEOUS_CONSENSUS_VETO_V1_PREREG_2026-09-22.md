# GOLD CONTROL — HETEROGENEOUS CONSENSUS VETO V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_HETEROGENEOUS_CONSENSUS_VETO_V1_RESEARCH`  
**Status class:** EXPLORATORY / POST-RESULT-DESIGNED / NOT CONFIRMATORY  
**Manifest update:** FORBIDDEN  
**Runtime / production authority:** NONE

## 1. Motivation

Two heterogeneous second-opinion channels showed different retrospective pockets but failed individually:

- `DOWNSIDE_CBR_DTW_PATH_V1_RESEARCH`: intraday Gold path morphology / historical-case similarity;
- `DOWNSIDE_SP500_CROSSMARKET_VETO_V1_RESEARCH`: independent S&P 500 cross-market context.

This identity tests a safety-system style rule:

> suppress a primary Gold downside alarm only when BOTH heterogeneous verifiers reject it.

The design is explicitly result-informed and cannot create pre-2025 confirmatory evidence.

## 2. Primary alarm

Frozen parent:
`DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`.

Primary alarm:
`sqrt_high_risk_alert == 1`.

Reference:
all primary alarms interpreted as DOWN.

## 3. Verifier A — PATH

Use the exact `STRICT` CBR-DTW engine from V1:

- historical cases only where `sqrt_high_risk_alert==1`;
- 48-point, two-channel normalized intraday path;
- multivariate DTW band=6;
- k=3 inverse-distance probability;
- `p_path=P(next-day DOWN)`.

No parameter changes.

## 4. Verifier B — CROSSMARKET

Use the exact context-logit construction from SP500 V1:

Training pool:
`sqrt_normalized_risk_score >= 0.80`.

Features:
- SP500 one-day return;
- SP500 five-observation return;
- SP500 one-day return divided by 20-day volatility;
- Gold primary log risk margin.

Ridge logistic C=1.0.

Output:
`p_sp=P(next-day Gold DOWN)`.

No parameter changes.

## 5. Consensus rule

No learned stacker is allowed.

Continuous consensus score:
`p_consensus = max(p_path, p_sp)`.

Decision:
- CONFIRM if `p_consensus >= 0.50`;
- VETO only if `p_path < 0.50 AND p_sp < 0.50`.

This OR-to-confirm / AND-to-veto structure is chosen to protect primary recall.

No threshold tuning.

## 6. Chronology

For each target year:
- 2024 verifier histories use outcomes through 2023-12-31;
- 2025 through 2024-12-31;
- 2026 YTD through 2025-12-31.

No target-year outcome enters either verifier training.

Because the architecture was designed after observing V1 verifier results, ALL years are exploratory retrospective evidence.

## 7. Outputs

On actual primary alarms:
- TP/FP/FN/TN;
- precision;
- recall;
- specificity;
- balanced accuracy;
- ROC AUC of `p_consensus`;
- false-alarm reduction;
- true-DOWN retention;
- counts of:
  - both confirm;
  - path-only confirm;
  - SP-only confirm;
  - both veto.

## 8. Exploratory usefulness rule

Label `EXPLORATORY_CONSENSUS_PROMISING` for a year only if:
1. false alarms are reduced by >=20%;
2. true-DOWN recall >=0.70;
3. balanced accuracy >0.55;
4. AUC >0.55.

This is descriptive only; it is not a promotion or validation gate.
