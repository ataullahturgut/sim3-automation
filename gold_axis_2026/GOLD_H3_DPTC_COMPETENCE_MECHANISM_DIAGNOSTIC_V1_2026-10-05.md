# GOLD H3 — DPTC Competence Mechanism Diagnostic V1 — 2026-10-05

**Status:** MECHANISM_DIAGNOSTIC_COMPLETE — post-hoc mechanism diagnosis, not prospective validation.

Databento estimated cost: **USD 1.3890**.

## Scientific design

Five label-free structural diagnostics are computed at each H3 origin: SPD covariance-geometry shift, multivariate energy distance, empirical tail-copula shift, directional transfer-entropy shift, and lead-lag asymmetry shift.
All anomaly thresholds are frozen from pre-2026 data at the 95th percentile before any RESCUE/BROKEN outcome comparison.

## 2026 label-free onset dates

| Signal | First 2026 origin |
|---|---|
| structural_broad | 2026-02-03 |
| structural_strict | 2026-03-05 |
| structural_broad_persistent3 | 2026-03-05 |
| gate_broad_plus_pro | none |
| gate_persistent_plus_pro | none |
| dependence_phase | 2026-04-30 |

## Multiview change-point test

- Full 2024–2026 multiview change point: **2026-03-16**, score 39.182, block-permutation p **0.0175**.
- 2026-only multiview change point: **2026-02-06**, score 0.000, block-permutation p **1.0000**.

## DPTC action-year profiles

| Year | N | Rescue | Precision | Mean anomaly count | Broad shift | Strong-pro-risk | Broad + pro-risk |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 11 | 6 | 54.5% | 0.18 | 9.1% | 0.0% | 0.0% |
| 2024 | 6 | 2 | 33.3% | 0.33 | 0.0% | 0.0% | 0.0% |
| 2025 | 9 | 4 | 44.4% | 0.44 | 11.1% | 33.3% | 0.0% |
| 2026 | 13 | 11 | 84.6% | 0.00 | 0.0% | 84.6% | 0.0% |

## Frozen gate enrichment on DPTC actions

| Gate | Inside R/N | Inside precision | Outside R/N | Outside precision | Odds ratio | Fisher p |
|---|---:|---:|---:|---:|---:|---:|
| structural_broad | 1/2 | 50.0% | 22/37 | 59.5% | 0.68 | 1.0000 |
| structural_strict | 0/0 | — | 23/39 | 59.0% | — | — |
| structural_broad_persistent3 | 0/0 | — | 23/39 | 59.0% | — | — |
| gate_broad_plus_pro | 0/0 | — | 23/39 | 59.0% | — | — |
| gate_persistent_plus_pro | 0/0 | — | 23/39 | 59.0% | — | — |
| strong_pro_risk | 11/14 | 78.6% | 12/25 | 48.0% | 3.97 | 0.0930 |
| dependence_phase | 11/14 | 78.6% | 12/25 | 48.0% | 3.97 | 0.0930 |

## Strongest rescue-vs-broken feature separations

| Feature | Cliff delta | Permutation p | Rescue mean | Broken mean |
|---|---:|---:|---:|---:|
| corr_gc_cl | -0.342 | 0.0570 | -0.1234 | 0.0476 |
| corr_gc_si | +0.288 | 0.5326 | 0.7423 | 0.7210 |
| te_shift | -0.283 | 0.1437 | 0.0259 | 0.0314 |
| r_gv | -0.255 | 0.2377 | -0.1633 | -0.1117 |
| strong_run | +0.250 | 0.5746 | 8.4783 | 5.6875 |
| corr_gc_nq | +0.228 | 0.1410 | 0.2779 | 0.1595 |
| spd_shift | +0.217 | 0.2747 | 0.8137 | 0.7330 |
| r_gn | +0.217 | 0.2064 | 0.1421 | 0.0732 |
| eig1_share | +0.196 | 0.1892 | 0.5019 | 0.4589 |
| leadlag_shift | -0.179 | 0.2872 | 0.1305 | 0.1485 |

## Interpretation discipline

- No structural threshold or gate is selected using DPTC correctness.
- 2023–2024 actions are included only when supported by at least 6 of 7 admissible Databento source mappings.
- 2025 and 2026 use the existing frozen Yahoo-lineage Q95 action evidence.
- 2026 is already consumed development evidence; any proposed competence gate remains a challenger until prospective validation.
- If several independent label-free structural diagnostics converge near the known competence transition and enrich RESCUE precision, that supports a mechanism-level regime interpretation rather than a generic volatility-regime label.
