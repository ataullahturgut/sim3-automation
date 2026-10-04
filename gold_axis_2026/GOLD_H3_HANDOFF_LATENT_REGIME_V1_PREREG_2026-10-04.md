# GOLD H3 — Handoff Latent Regime V1 Preregistration

**Date:** 2026-10-04  
**Status:** unsupervised regime discovery on 2023-2024; Handoff regime qualification on 2025; frozen 2026 retrospective stress.  
**Purpose:** test whether the same Handoff warning has different reliability because the market occupies different latent states.

## Key anti-overfit design

- Regimes are learned with **no reversal labels and no Handoff outcomes**.
- Regime geometry uses only 2023-2024 origin-safe market features.
- 2025 is used only to decide in which already-defined regimes the canonical Handoff alarm is reliable.
- 2026 is not used for clustering, regime selection, thresholds, or tie-breaking.

## Canonical Handoff alarm

Before any topology veto:

- external_premax >= 0.60
- internal_now >= 0.60
- internal_d1 >= 0.00
- combined baseline still follows prevailing momentum

Combined baseline = HELIOS V5-DCE + frozen SAGE/OCS exception-only + frozen RuleFlow V3-TG.

## Unsupervised regime feature vector

Use only features available across 2023-2026 and known at the origin:

1. |12h Gold return| — current trend impulse magnitude
2. trend_strength
3. adverse_excursion
4. path_consistency
5. signed_opt_pressure
6. opt_total_z20
7. gc_volume_z20
8. core_confirmation — cross-asset confirmation
9. cross_dispersion — cross-asset disagreement

No target, reversal label, V5 error, rescue flag, Handoff score, or future H3 path is used.

## Preprocessing

Fit on 2023-2024 only:
- clip every feature to its 1st/99th percentile;
- median impute using 2023-2024 medians;
- standardize using 2023-2024 mean/std.

Apply the frozen preprocessing unchanged to 2025 and 2026.

## Number of regimes

Fit KMeans for K = 2, 3, 4, 5 on 2023-2024 only, random_state=20261004, n_init=50.

Select K by:
1. highest silhouette score;
2. if silhouette difference is <0.01, choose smaller K.

No outcome metric enters K selection.

## 2025 regime qualification

For the canonical Handoff alarms in 2025, report per regime:
- support
- rescue
- broken
- net
- precision

A regime is **Handoff-trusted** only if:
- support >= 3 alarms
- rescue >= 2
- precision >= 60%
- net > 0

All qualifying regimes are trusted; there is no winner-picking among them.

If no regime qualifies, V1 closes and no 2026 assisted result is produced.

## Frozen 2026 stress

Apply Handoff FLIP only when:
- the canonical Handoff alarm fires, and
- the origin is assigned to a 2025-qualified trusted regime.

Do not add a topology veto or any 2026-derived filter.

Report:
- regime occupancy shifts 2023-2026
- 2025 qualification table
- 2026 actions/rescue/broken/net/precision
- remaining-53 rescues
- combined baseline vs assisted accuracy and balanced accuracy
- every 2026 action date

## Scientific status

The broad Handoff hypothesis was originally motivated by retrospective 2026 analysis, so a positive 2026 result is not pristine prospective OOS evidence. However, the latent regime geometry is label-free and trained only on 2023-2024, while Handoff regime qualification is frozen on 2025 before the 2026 stress.
