# SIGNET-H3 V1 — SIGNATURE GEOMETRY ERROR NETWORK AUTHORITY

**Date:** 2026-10-02
**Identity:** `SIGNET_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Objective

Test whether rough-path signature geometry can correct a subset of AURORA-H3 errors that are not captured by aggregate hourly returns or simple nearest-neighbour path matching.

SIGNET uses a supervised path-signature classifier only as a **rescue head**. AURORA remains the default.

## 2. Timing

- Same validated IRIS XAU 1-hour source.
- Feature anchor: 16:00 America/New_York on feature_cutoff_date.
- No forecast_issue_date or later hourly bar.
- Every training row must satisfy `target_end_date_h3 <= test feature cutoff`.

## 3. Window normalization

For each 24h or 48h window:
- compute hourly log returns;
- normalize the return vector by `sqrt(sum(r^2)) + eps`;
- construct normalized cumulative return path `x_t`, starting at zero.

Amplitude normalization deliberately separates **shape geometry** from the magnitude information already present in IRIS/AURORA.

## 4. Signature maps

For each window compute two depth-2 signatures.

### A. TIME-RETURN path
2D path:
`(t/T, x_t)`

Captures ordering / whether movement occurs early or late through second-level signed area.

### B. LEAD-LAG path
For successive scalar path values x0,x1,...:
`(x0,x0) -> (x1,x0) -> (x1,x1) -> ...`

Depth-2 lead-lag signature captures path-dependent quadratic variation / roughness information that is lost by a plain one-dimensional signature.

For any 2D piecewise linear path, retain:
- level 1: 2 terms
- level 2: 4 terms.

Each transform therefore contributes 6 terms; TIME-RETURN + LEAD-LAG gives **12 signature terms per window**.

Representations:
1. `SIG24`
2. `SIG48`
3. `SIG_MULTI` = concatenate 24h and 48h signature features.

## 5. Signature classifier

For each calendar-month test block:
- StandardScaler
- LogisticRegression L2
- `C=0.25`
- expanding chronological training
- no class weighting.

The classifier outputs `p_signature_up`.

No model-family or C search is allowed.

## 6. Frozen rescue rule

AURORA remains the output unless SIGNET strongly contradicts it:

- AURORA DOWN and `p_signature_up >= 0.70` -> use signature probability;
- AURORA UP and `p_signature_up <= 0.30` -> use signature probability;
- otherwise retain AURORA.

Thresholds 0.70 / 0.30 are fixed ex ante.

## 7. Representation selection

Only representation is selected on **Jul-Dec 2022**.

Eligibility relative to matched AURORA:
- balanced accuracy >= AURORA;
- accuracy >= AURORA -0.5 pp;
- Brier <= AURORA +0.0025;
- at least 3 rescue decisions.

Rank:
1. balanced accuracy
2. accuracy
3. Brier
4. log loss.

No eligible representation -> fail closed.

## 8. Frozen confirmation

The selected representation must then satisfy:

2023:
- accuracy >= AURORA -1 pp
- Brier <= AURORA +0.003

2024:
- accuracy >= AURORA -1 pp
- Brier <= AURORA +0.003

Aggregate 2023-2024:
- balanced accuracy >= AURORA
- at least one genuine rescue.

Only after this may 2025/2026 be examined.

## 9. Transport diagnostics

Report:
- annual metrics;
- number of overrides;
- AURORA errors corrected;
- AURORA correct calls broken;
- net rescue;
- 2026 call-by-call override table;
- high-confidence AURORA errors corrected, if any.

## 10. Governance

If SIGNET fails, no tuning of:
- C,
- signature depth,
- rescue threshold,
- window size,
- signature transform
may use 2023-2026 outcomes.

A new design requires a new identity.

The frozen AURORA prospective champion is not modified by this retrospective challenger.
