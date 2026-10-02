# ORBIT-H3 V1 — ORIGIN-SAFE RELATIONAL BULLION INTRADAY TRANSFER AUTHORITY

**Date:** 2026-10-02
**Identity:** `ORBIT_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Motivation

TWIN-H3 and SIGNET-H3 tested richer representations of XAU's own intraday path and failed their pre-2023 gates.

ORBIT therefore introduces genuinely new origin-safe information:
**hourly XAG/USD relative to XAU/USD**.

The hypothesis is that some AURORA errors are exhaustion / confirmation failures that can be detected from gold-silver intraday divergence and lead-lag structure.

## 2. Data timing

Gold:
- validated IRIS XAU/USD 1h source.

Silver:
- Twelve Data `XAG/USD`, 1h, America/New_York;
- requested historically from 2022-01-01 through the frozen 2026 research endpoint.

At each H3 origin:
- anchor 16:00 America/New_York on feature_cutoff_date;
- no issue-date or later bars;
- gold and silver hourly rows are inner-aligned by timestamp.

Source coverage must support >=95% of AURORA origin anchors; otherwise fail closed.

## 3. Cross-asset features

From aligned hourly gold/silver log returns:

### Multi-horizon relative motion
For h in 1,3,6,12,24,48:
- silver return sum `xag_rh`
- gold-minus-silver return `rel_rh`.

### Co-movement
- return correlation over 24h and 48h
- sign agreement fraction over 24h and 48h
- realized-volatility ratio gold/silver over 24h and 48h.

### Directed lead-lag correlation
For lags 1,3,6 hours:
- Silver leads Gold: corr(XAG_t, XAU_{t+lag})
- Gold leads Silver: corr(XAU_t, XAG_{t+lag})
- difference between the two directions.

### Signature lead-lag area
For 24h and 48h:
- construct normalized cumulative XAG and XAU return path;
- calculate the antisymmetric second-level path-signature term
  `S_XAG,XAU - S_XAU,XAG`;
- positive/negative values encode directional sequencing of the two bullion paths.

## 4. Rescue heads

Two fixed Logistic L2 heads are compared on 2022-H2 only:

1. `CROSS_ONLY`
   - cross-asset features only.

2. `AURORA_PLUS_CROSS`
   - logit(p_AURORA) + cross-asset features.

Both:
- StandardScaler
- LogisticRegression
- C=0.25
- monthly expanding chronological refit
- no class weighting.

No model-family or C search.

## 5. Frozen rescue rule

AURORA remains default.

For the selected ORBIT head:
- AURORA DOWN and ORBIT p(UP) >= 0.70 -> ORBIT overrides;
- AURORA UP and ORBIT p(UP) <= 0.30 -> ORBIT overrides;
- otherwise retain AURORA.

Thresholds are fixed before evaluation.

## 6. Selection authority

**Jul-Dec 2022 only.**

Eligibility:
- balanced accuracy >= AURORA;
- accuracy >= AURORA -0.5 pp;
- Brier <= AURORA +0.0025;
- at least 3 override decisions.

Rank:
1. balanced accuracy
2. accuracy
3. Brier
4. log loss.

No eligible head -> fail closed.

## 7. Frozen confirmation

Selected head must satisfy separately in both 2023 and 2024:
- accuracy >= AURORA -1 pp;
- Brier <= AURORA +0.003.

Aggregate 2023-2024:
- balanced accuracy >= AURORA;
- at least one genuine corrected AURORA error.

Only after passing are 2025 / 2026 opened.

## 8. 2025 / 2026 diagnostics

Report:
- accuracy, balanced accuracy, Brier, log loss;
- overrides, corrected AURORA errors, broken AURORA calls, net rescue;
- 2026 call-by-call overrides;
- whether high-confidence AURORA errors are rescued;
- conditional results for strong gold-silver divergence / lead-lag area.

## 9. Governance

If ORBIT fails:
- do not tune lag set,
- do not tune rescue thresholds,
- do not tune C,
- do not add/remove cross features based on 2023-2026 outcomes.

Any redesign gets a new identity.

The frozen AURORA prospective ledger is not modified retroactively.
