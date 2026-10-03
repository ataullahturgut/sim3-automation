# ORS-H3 V1 — ORTHOGONAL REVERSAL SURPRISE PREREGISTRATION

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-tres-v1-20261004`  
**Identity:** `ORS_H3_V1`  
**Status:** **FROZEN BEFORE ORS OUTCOMES**

## 1. Scientific question

TRES Stage 1 found a stable reversal-risk signal, but:
- a second V5 error classifier degraded it;
- absolute survival dominance alone was not selective enough.

ORS tests a different hypothesis:

> A reversal signal should overturn V5 only when it is not merely high in absolute terms, but unusually high relative to historical origins in which V5 saw a similar continuation state.

This targets **incremental / orthogonal information**, not another prediction model.

## 2. Eligible universe

Intervention is considered only when:

`v5_pred == momentum_up`

because in this universe:
`V5 wrong == terminal reversal`

This identity was verified with zero mismatches in the prior direct-survival diagnostic.

## 3. Input survival signal

Use only the already out-of-sample TRES Stage-1 predictions:

- F_reversal
- F_continuation
- S3

No Stage-1 in-sample fitted value may enter ORS.

## 4. V5-state conditioning space

For every eligible origin define the frozen V5/continuation state vector Z:

1. `p_v5_cont`
   - if momentum_up=1: p_helios_v5_dce
   - if momentum_up=0: 1-p_helios_v5_dce
2. v5_confidence
3. abs_h_ret_12
4. trend_strength
5. path_consistency
6. adverse_excursion
7. opposite_semivar_share
8. deceleration_6h

These variables describe the continuation state already visible to V5/path logic.

No target label enters the conditioning distance.

## 5. Historical neighbor library

Monthly expanding-origin replay.

For a test month, an eligible historical row is admissible only when:
- it has an OOS TRES Stage-1 prediction;
- `target_end_date_h3 <= first feature_cutoff_date of test month`;
- it precedes the test month.

Minimum matured eligible library:
- **160 origins**

Standardize Z using the matured library only.

For each test origin:
- find the **40 nearest** historical eligible origins by Euclidean distance in standardized Z-space.

K=40 is frozen and not searched.

## 6. Conditional reversal surprise

Among the 40 local neighbors, compare the current OOS `F_reversal` to neighbor OOS `F_reversal`.

One-sided local rank p-value:

`p_surprise = (1 + count(F_R_neighbor >= F_R_current)) / 41`

Define:
`surprise = 1 - p_surprise`

No target labels are used in this score.

## 7. Frozen intervention actions

### FLIP candidate

Only if all hold:

1. V5 follows momentum;
2. `p_surprise <= 0.10`;
3. `F_reversal > F_continuation`;
4. `F_reversal > S3`.

Thus reversal must be both:
- locally unexpected relative to V5-similar history; and
- the largest TRES event-state probability.

### DAMP candidate

If:
- `p_surprise <= 0.10`;
- but either dominance condition fails.

DAMP never changes direction in V1. It is reported only as a confidence-risk diagnostic.

### KEEP

Otherwise.

No numeric F_reversal threshold is fitted.

## 8. Development replay metrics

Historical replay is development/stress-test only.

Report:
- FLIP count / rate
- rescue / broken / net
- FLIP precision
- V5 vs assisted accuracy
- DAMP count
- local-neighbor distance
- block stability
- OPAL-no-candidate missed reversal hits
- terminal reversal rate by surprise quintile
- terminal reversal rate for:
  - high surprise + reversal dominant
  - high surprise + non-dominant
  - low surprise

## 9. Development gate

ORS V1 is development-promising only if all hold:

1. FLIP candidates >= 8;
2. FLIP precision >= 0.60;
3. net rescue >= +3;
4. candidate rate <= 0.15 of eligible origins;
5. assisted accuracy >= V5 accuracy + 0.005 on the same replay universe;
6. at least ceil(0.80 × available half-year blocks) have net >= 0;
7. at least half of available blocks have net > 0;
8. worst block net >= -2;
9. maturity leakage failures = 0.

If PASS:
`ORS_H3_V1_PROMISING`

If FAIL:
`ORS_H3_V1_FAIL`

## 10. Governance

No outcome-dependent threshold search is allowed.

If ORS fails, do not tune p_surprise or K on the same replay.

If ORS passes, it still requires a separate prospective freeze before any clean claim.

HELIOS V5-DCE remains binding until prospective evidence.
