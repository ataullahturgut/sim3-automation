# HERA-H3 V1 — PROSPECTIVE CHALLENGER FREEZE

**Date:** 2026-10-03  
**Identity:** `HERA_H3_V1_PROSPECTIVE_CHALLENGER`  
**Research parent:** `HERA_H3_V1_RESEARCH`  
**Research result status:** `MECHANISM_PASS`  
**Manifest commit containing retrospective result:** `a17e2dc88363533bc74418328a80f512c8a95e2e`

## 1. Freeze principle

HERA-H3 V1 is frozen as a separate prospective challenger.

The existing `AURORA_H3_V1_PROSPECTIVE` ledger is not edited, overwritten, relabeled, or backfilled.

Only HERA forecasts issued after this freeze may count as prospective HERA evidence.

## 2. Frozen hierarchy

At origin t:

1. obtain the frozen AURORA V1 probability and active expert state;
2. if AURORA state is `STRUCTURAL_IRIS`:
   - HERA probability = AURORA probability;
3. if AURORA state is `PATH_GLOBAL`:
   - compute the frozen OPAL V1 reversal probability from origin-safe CFTC options-positioning state;
   - apply OPAL V1's frozen reversal rule;
   - HERA probability = OPAL output.

No other gate is permitted.

## 3. Frozen OPAL component

Official source:
- CFTC Disaggregated Public Reporting API
- Gold code 088691
- futures-only dataset 72hh-3qpy
- futures+options-combined dataset kh3c-gbw2.

Options-only positions:
- combined minus futures-only.

Availability:
- report as-of date + 7 calendar days.

Features/model/threshold:
- exactly OPAL-H3 V1 authority;
- StandardScaler + balanced LogisticRegression C=1.0;
- monthly expanding target-matured refit;
- reversal threshold 0.70;
- OPAL may change direction only when AURORA follows 12h momentum.

## 4. Frozen AURORA component

Use the already-frozen AURORA prospective state rules unchanged.

HERA must never infer or recreate a different AURORA state from future hindsight.

## 5. No-backfill

If HERA cannot produce its shadow forecast before the prospective issuance deadline:
- record MISS;
- never reconstruct that forecast after H3 outcome information becomes available.

## 6. Settlement

HERA forecast fields are immutable after issuance.

After H3 maturity, append only:
- target end date
- realized H3 return
- actual direction
- correct / wrong
- row Brier
- row log loss.

## 7. Prospective comparisons

Primary:
- HERA vs frozen AURORA on matched prospective origins.

Report:
- N
- accuracy
- balanced accuracy when both classes exist
- Brier
- log loss
- UP recall
- DOWN recall
- HERA direction changes
- rescued / broken AURORA calls
- active PATH share.

Do not claim statistical superiority from a small prospective sample.

## 8. Forbidden changes

A new version is required for any change to:
- AURORA state rules;
- OPAL CFTC data family;
- CFTC lag;
- OPAL feature set;
- model class/C;
- reversal threshold;
- HERA hierarchy.

## 9. Interpretation

The retrospective HERA result is hypothesis-generating / mechanism evidence because the hierarchy was conceived after historical regime dependence was observed.

Only this separately frozen challenger can provide future prospective confirmation.
