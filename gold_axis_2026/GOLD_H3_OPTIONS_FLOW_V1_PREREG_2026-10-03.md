# OPTIONS-FLOW-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `OPTIONS_FLOW_H3_V1`  
**Branch:** `gold-h3-options-flow-v1-20261003`  
**Evidence class:** `SHORT_HISTORY_OFFICIAL_OCC_AUTHORITY`  
**Role:** directional GLD options-flow momentum-reversal candidate specialist.  
**Status:** **PREREGISTERED BEFORE FULL HISTORY DOWNLOAD / MODEL FIT**

## 1. Purpose

OPTIONS-FLOW-H3 tests whether directional GLD options activity contains reversal information that is absent from OPAL and from price-path-only specialists.

It does not claim to be CME Gold CVOL / implied-volatility skew.

Target:
`reversal_target = 1[y_up != momentum_up]`

Operational candidate universe:
`aurora_follows_momentum == True`.

The specialist never directly overwrites HELIOS V5-DCE in V1.

## 2. Official source authority

Primary source:
- The Options Clearing Corporation (OCC)
- public Volume Query batch endpoint:
  `https://marketdata.theocc.com/volume-query`

Frozen query identity:
- `volumeQueryType=O`
- `symbolType=O`
- `symbol=GLD`
- `reportType=D`
- `accountType=ALL`
- `productKind=OSTK`
- `porc=BOTH` where supported; otherwise separate `C` and `P` requests with identical semantics.

The exact options class `GLD` is used rather than all adjusted option classes under the GLD underlying.

OCC output fields used:
- quantity
- underlying
- symbol
- actype
- porc
- exchange
- actdate

Account-type semantics retained from the official output:
- `C` = customer
- `F` = firm
- `M` = market maker

Call/put side:
- `porc=C` = call
- `porc=P` = put

All exchange rows are summed within date / side / account type.

## 3. Source-history limitation and frozen period roles

The public OCC Volume Query currently rejects report dates more than two years old.

Verified:
- 2023-01-03 -> rejected as older than two years
- 2024-10-04 -> available
- 2026-10-02 -> available

This is a source-retention constraint, not a model-selection choice.

Period roles are frozen before full history download:

### Source warm-up / model formation
- 2024-10-04 through 2024-12-31
- used for rolling feature initialization and expanding training
- not used for candidate-threshold selection

### DEV / threshold selection
- 2025-01-01 through 2025-06-30 only

### Confirmation
- 2025-07-01 through 2025-12-31 only

### Final retrospective holdout
- 2026-01-01 onward
- opened only if the 2025 H2 confirmation gate passes

No 2026 outcome may select source handling, features, rolling windows, signs, model, threshold, or confirmation rule.

## 4. Origin-safe clock

Canonical H3 origin: 17:00 America/New_York.

To avoid relying on the unknown exact OCC daily-report publication minute, V1 uses a conservative rule:

`eligible OCC flow row = latest GLD options activity date strictly before feature_cutoff_date`

Same-date options volume is forbidden.

No lag search is permitted.

Maximum staleness:
- 5 calendar days

Rows exceeding the staleness rule are excluded from model scoring.

## 5. Daily source aggregation

For every OCC activity date:

- `call_customer`
- `call_firm`
- `call_mm`
- `put_customer`
- `put_firm`
- `put_mm`

Totals:
- `call_total = call_customer + call_firm + call_mm`
- `put_total = put_customer + put_firm + put_mm`
- `option_volume_total = call_total + put_total`

No exchange is outcome-selected or weighted.

## 6. Frozen feature construction

Numerical stabilizer:
`eps = 1.0`

Base directional ratios:
1. `log_pcr_total = log((put_total+eps)/(call_total+eps))`
2. `log_pcr_customer = log((put_customer+eps)/(call_customer+eps))`
3. `log_pcr_mm = log((put_mm+eps)/(call_mm+eps))`

One-day innovations:
4. `d_log_pcr_total_1`
5. `d_log_pcr_customer_1`

Signed volume imbalances:
6. `imbalance_total = (call_total-put_total)/(call_total+put_total+eps)`
7. `imbalance_customer = (call_customer-put_customer)/(call_customer+put_customer+eps)`

Backward-looking normalization:
- `volume_z20`: current log total volume relative to preceding 20 available OCC observations, with rolling mean/std shifted by one source date.
- `log_pcr_total_z20`: current total log-PCR relative to preceding 20 available OCC observations, also shifted by one.
- no current observation enters its own normalization baseline.

Let `s=+1` for current 12h Gold momentum UP and `s=-1` for DOWN.

Frozen reversal-oriented model features:
1. `mom_x_log_pcr_total = s * log_pcr_total`
2. `mom_x_d_log_pcr_total = s * d_log_pcr_total_1`
3. `mom_x_log_pcr_customer = s * log_pcr_customer`
4. `mom_x_d_log_pcr_customer = s * d_log_pcr_customer_1`
5. `reversal_imbalance_total = -s * imbalance_total`
6. `reversal_imbalance_customer = -s * imbalance_customer`
7. `mom_x_log_pcr_z20 = s * log_pcr_total_z20`
8. `volume_z20`
9. `flow_pressure_x_volume = reversal_imbalance_total * volume_z20`
10. `customer_mm_divergence_mom = s * (log_pcr_customer-log_pcr_mm)`

No feature search is allowed after outcome inspection.

## 7. Model

- StandardScaler
- LogisticRegression
- `C=1.0`
- `solver=lbfgs`
- `class_weight=balanced`
- seed `20261003`
- monthly expanding-origin refit

Minimum matured training rows:
- 40

Training rows at a monthly refit must satisfy:
`target_end_date_h3 <= current month first feature cutoff`.

Random split is forbidden.

## 8. DEV threshold selection

Frozen threshold grid:
`[0.35, 0.40, 0.45, 0.50, 0.55, 0.60]`

Selection set:
- only 2025-01-01 through 2025-06-30
- only `aurora_follows_momentum=True`

Primary objective:
- maximize reversal F2

Eligibility:
- candidate precision >= 0.45
- candidate rate <= 0.40

Tie-break:
1. higher reversal recall
2. higher precision
3. lower candidate rate
4. higher threshold

No eligible threshold =>
`NO_ELIGIBLE_OPTIONS_FLOW_THRESHOLD`.

## 9. 2025 H2 confirmation

All conditions are required:
1. OPTIONS-FLOW reversal recall > OPAL candidate recall on the same eligible universe.
2. OPTIONS-FLOW nominates at least one true reversal where OPAL candidate is false.
3. OPTIONS-FLOW candidate precision >= 0.40.
4. `OPAL union OPTIONS-FLOW` reversal recall > OPAL recall.

If any condition fails:
- status = `CONFIRMATION_2025_H2_FAIL`
- formal 2026 evaluation remains unopened.

## 10. 2026 holdout

Only after confirmation PASS:

Report:
- reversal recall
- candidate precision
- candidate rate
- OPAL overlap
- OPTIONS-FLOW-only true reversals
- OPAL-union-OPTIONS-FLOW reversal recall
- count of V5-missed / OPAL-no-candidate reversals nominated
- diagnostic forced-flip rescue / broken / net relative to V5
- Brier/logloss for reversal probability if available

No HELIOS router is promoted from this specialist result alone.

## 11. Interpretation

A PASS means:
> official directional GLD options flow contains complementary reversal information and may enter a later recall-first candidate union.

A FAIL means only:
> this preregistered short-history flow representation did not meet the selectivity/transport gate.

It does not disprove CME CVOL skew, which remains a separate unavailable implied-volatility information channel.

## 12. Governance

- HELIOS V5-DCE remains unchanged.
- CLEAN_H3_PROSPECTIVE_V1 remains unchanged.
- The source retention window is explicitly disclosed.
- Same-date flow is forbidden.
- No threshold may be relaxed after seeing DEV/confirmation/2026.
- The known 2026 missed-reversal set cannot influence this V1 contract.
