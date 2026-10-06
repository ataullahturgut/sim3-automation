# GOLD SESSION SAGE V1 — PREREGISTRATION

**Freeze date:** 2026-10-07  
**Branch:** `gold-execution-channel-audit-20261006`  
**Identity:** `GOLD_SESSION_SAGE_V1`  
**Status:** **PREREGISTERED BEFORE SESSION-SAGE RESULTS**

## 1. Purpose

Complete Stage-1 items S1.5–S1.8 without inventing a new post-result session representation.

The session adaptation inherits the already-frozen H3 SAGE V1 mechanism:
the same total move can have different implications depending on which global trading phase generated it.

This preregistration is committed before any S1.5–S1.8 score is produced.

## 2. Raw sources and chronology

- XAU path / SAGE phase state: governed Twelve Data XAU/USD 15-minute UTC archive.
- 2022 extension: governed V5-equivalent warm-up authority; **training/warm-up only**.
- Daily structural block: fresh raw-derived NOVA CORE3.
- A1: regenerated fresh from raw daily metals; archived A1 predictions are forbidden.
- 2023–2024: development/scoring.
- 2025: unopened frozen transport.
- 2026: unopened stress.

No archived H3 SAGE prediction, H3 target, or H3 model score may enter a session model.

## 3. Frozen SAGE phase decomposition

Use the original SAGE four-phase New-York-local decomposition:

- `sess_asia`: previous NY date 18:00 -> current NY date 03:00
- `sess_europe`: 03:00 -> 08:00
- `sess_us_am`: 08:00 -> 12:00
- `sess_us_pm`: 12:00 -> 16:00

Boundary value = exact XAU/USD 15m bar **OPEN** at the registered boundary.
No nearest-bar substitution.

A SAGE cycle dated D is considered source-ready at **16:15 America/New_York on D**.
This deliberately waits one full 15-minute interval after the final 16:00 boundary.

For every target start T, use the latest complete SAGE cycle satisfying:

`sage_ready_utc < target_start_utc`

Equality is rejected.

This means:
- targets after 16:15 NY may use the same NY-date SAGE cycle;
- targets earlier in the day use the latest prior complete cycle;
- the rule is deterministic and independent of outcomes.

## 4. Frozen derived phase features

Primary returns:
- `sess_asia`
- `sess_europe`
- `sess_us_am`
- `sess_us_pm`

Derived:
- `sess_us_total = US_AM + US_PM`
- `sess_west_total = EUROPE + US_AM + US_PM`
- `sess_east_west = ASIA - WEST_TOTAL`
- `sess_us_reversal = US_PM - US_AM`
- `sess_dispersion = std(ASIA, EUROPE, US_AM, US_PM)`
- `sess_sign_changes`
- `sess_dominance = max(abs(phase))/sum(abs(phase))`
- `sess_asia_us_interaction = ASIA * US_TOTAL`
- `sess_east_west_conflict = 1[ASIA * WEST_TOTAL < 0]`
- `sess_us_conflict = 1[US_AM * US_PM < 0]`

No additional session feature may be added after results.

## 5. Stage-1 representations

All direct heads use StandardScaler + LogisticRegression(L2, C=1.0).

### S1.5 SESSION_ONLY
`SESSION_ALL`

### S1.6 PATH_SESSION
same-source-derived 1h XAU full IRIS PATH + `SESSION_ALL`

### S1.7 A1_SESSION
fresh A1 logit + `SESSION_ALL`

### S1.8 A1_PATH_SESSION
fresh A1 logit + same-source-derived 1h XAU full IRIS PATH + `SESSION_ALL`

The canonical S1.4 comparator is fresh A1 + 1h full IRIS PATH.

## 6. Training

- same-window expanding causal replay;
- outer block size = 5;
- only labels with `end_utc <= test_block_start` may enter training;
- S1.5/S1.6 minimum training rows = 120;
- S1.7/S1.8 require fresh A1 and minimum matured A1-feature rows = 80;
- no imputation of target or SAGE boundary prices.

## 7. Matched comparators

Evaluate on exact common scored rows:

- S1.5 SESSION_ONLY: report standalone metrics.
- S1.6 PATH_SESSION vs PATH_GLOBAL built on the same 1h PATH rows.
- S1.7 A1_SESSION vs matched fresh A1 direct.
- S1.8 A1_PATH_SESSION vs matched canonical S1.4 A1+PATH.

## 8. Promotion/retention rule before 2025

A SAGE representation is eligible for frozen 2025 transport for a given head only if:

1. combined 2023–2024 scored N >= 80;
2. `min(UP recall, DOWN recall) >= 0.30`;
3. for a model with a named comparator, combined Balanced Accuracy >= comparator;
4. if both 2023 and 2024 matched slices have N >= 40, candidate Balanced Accuracy must not be below comparator in either year;
5. candidate Brier may be at most comparator Brier + 0.010 on the combined matched sample.

SESSION_ONLY has no structural/path comparator; it is retained only if:
- combined BA >= 0.52,
- both class recalls >= 0.30,
- and each year with N >= 40 has BA >= 0.50.

If no SAGE representation passes for a head, that head fails closed for SAGE.

## 9. Governance

- This preregistration precedes all session-SAGE result files.
- 2025 remains closed until S1.5–S1.8 results and the Stage-1 freeze are recorded.
- 2026 cannot change representation, clocks, features or thresholds.
