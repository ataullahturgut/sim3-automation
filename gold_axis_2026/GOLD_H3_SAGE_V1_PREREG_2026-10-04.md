# SAGE-H3 V1 — SELECTIVE ACTION + GUARDED EXCEPTION PREREGISTRATION

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-sage-v1-20261004`  
**Identity:** `SAGE_H3_V1`  
**Status:** **FROZEN BEFORE SAGE COMBINED OUTCOMES**

## 1. Objective

Separate two tasks that repeatedly failed when forced into one global reversal score:

1. **Path-state risk / uncertainty** — handled by TRES.
2. **Rare independent reversal exception** — handled by OCS.

SAGE does not average the channels.

It uses a mechanism-specific policy:

- TRES decides whether a V5 continuation call is safe enough to **KEEP** or should be **ABSTAINED**.
- OCS is the only channel allowed to **FLIP** V5.

## 2. Scientific rationale

TRES Stage 1:
- produced stable reversal-risk stratification across all six half-year blocks;
- but direct FLIP policies were not selective enough.

OCS:
- combines independent internal Gold/Silver hourly flow breakdown with external cross-asset lead-lag repricing stress;
- individual IFBC/LLRS channels were weak, but their strict conjunction produced a rare high-specificity reversal mechanism.

The two channels are intentionally not required to agree:
an external/flow shock may reverse price even when the endogenous path-survival model still favors continuation.

## 3. Historical status

All 2025–2026 historical results are development/stress-test evidence.

No SAGE retrospective result is a clean holdout claim.

The original OCS V1 development universe begins at **2025-07-01**.
SAGE preserves that maturity boundary and does not back-activate the OCS mechanism into 2025 H1.

## 4. Frozen OCS exception

Use the previously identified OCS configuration exactly:

### IFBC condition
- `ifbc_count60 >= 4`
- `ifbc_score >= 0.70`

### LLRS condition
- `llrs_external_opposes == True`
- `llrs_incremental > 0`
- `llrs_pressure >= 0.10`

### OCS exception
`OCS = IFBC_condition AND LLRS_condition`

No OCS threshold is re-searched in SAGE.

The q=0.70 / 0.10 pair is inherited from prior OCS development and therefore carries no new clean validation status.

## 5. Frozen TRES state

Use only out-of-sample TRES Stage-1 probabilities:

- `F_reversal`
- `F_continuation`
- `S3`

Define:

`TRES_CONTINUATION_SAFE = F_continuation >= max(F_reversal, S3)`

No numeric threshold is added.

## 6. Frozen action hierarchy

For every origin in the common mature coverage:

### Existing V5 reversal call
If:
`v5_pred != momentum_up`

Action:
**KEEP V5**

SAGE never overrides an already non-momentum V5 call in V1.

### V5 continuation call
If:
`v5_pred == momentum_up`

Apply the following precedence:

1. If `OCS == True`:
   - **FLIP V5**

2. Else if `TRES_CONTINUATION_SAFE == True`:
   - **KEEP V5**

3. Else:
   - **ABSTAIN**

Thus:
- OCS supplies the rare direction-changing evidence.
- TRES supplies the confidence / uncertainty governor.
- TRES never vetoes an OCS exception.
- TRES alone never flips direction.

## 7. Benchmark semantics

Two evaluations are reported.

### Forced full-direction comparator

For benchmark comparability:
- KEEP = V5
- FLIP = reversed V5
- ABSTAIN defaults to original V5 direction

Therefore full-direction improvement comes only from OCS.

### Selective action evaluation

Exclude ABSTAIN rows.

Report:
- action coverage
- action accuracy
- KEEP accuracy
- FLIP precision
- ABSTAIN count
- counterfactual V5 accuracy inside ABSTAIN rows

A useful governor should concentrate errors into ABSTAIN rather than merely reduce coverage randomly.

## 8. Development replay

Common mature universe:
- 2025 H2
- 2026 H1
- 2026 H2 through available September history.

All source rows must be matched by `feature_cutoff_date`.

Leakage rules:
- TRES rows must be previously generated OOS Stage-1 predictions.
- IFBC and LLRS scores must be origin-time features from their frozen historical score ledgers.
- no current/future target may enter action construction.

## 9. Development gate

SAGE is development-promising only if all hold:

1. OCS FLIP candidates >= 6;
2. aggregate FLIP precision >= 0.60;
3. aggregate FLIP net rescue >= +3;
4. every available half-year block has FLIP net >= 0;
5. at least 2 blocks have FLIP net > 0;
6. worst block FLIP net >= 0;
7. selective action coverage >= 0.50;
8. selective action accuracy >= 0.70;
9. selective action accuracy > forced V5 accuracy on the same universe;
10. ABSTAIN-row V5 accuracy < selective action accuracy;
11. maturity / date-match leakage failures = 0.

If PASS:
`SAGE_H3_V1_DEVELOPMENT_PASS`

If FAIL:
`SAGE_H3_V1_FAIL`

No gate component may be changed after results.

## 10. Prospective governance

Even on development PASS:
- SAGE remains shadow-only;
- first new clean evidence begins after the freeze;
- promotion requires at least 20 prospective FLIP actions or 6 calendar months, whichever is later;
- cumulative prospective FLIP net rescue must remain >0;
- prospective FLIP precision must be >=0.60;
- HELIOS V5-DCE remains binding until those criteria are met.

## 11. Source provenance

Frozen inputs are copied from their existing research branches without recomputation:

- IFBC score ledger:
  `gold-h3-ifbc-v1-20261004 / GOLD_H3_IFBC_V1_SCORES_2026-10-04.csv`
- LLRS origin score ledger:
  `gold-h3-llrs-v1-20261004 / GOLD_H3_LLRS_V1_ORIGIN_SCORES_2026-10-04.csv`
- TRES Stage-1 OOS predictions:
  `gold-h3-tres-v1-20261004 / GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv`
