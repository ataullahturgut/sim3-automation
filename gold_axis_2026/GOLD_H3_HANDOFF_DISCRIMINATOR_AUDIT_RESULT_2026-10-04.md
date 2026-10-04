# GOLD H3 — Handoff Rescue-vs-Broken Discriminator Audit

**Status:** retrospective mechanism diagnostic only; no new trade rule.

## Canonical broad Handoff alarm

`external_premax >= 0.60 AND internal_now >= 0.60 AND internal_d1 >= 0 AND combined baseline == momentum`

Topology veto is intentionally not applied before this audit, because topology is one of the candidate discriminators.

## 2025 alarm outcomes

- alarms: **13**
- rescue / broken: **4 / 9**
- raw flip precision: **30.77%**

## 2026 alarm outcomes

- alarms: **28**
- rescue / broken: **16 / 12**
- raw flip precision: **57.14%**

## Stable descriptive discriminators

Requirement: same rescue-vs-broken direction in 2025 and 2026, >=3 observations in every rescue/broken group, and |SMD|>=0.20 in both years.

| Feature | 2025 SMD | 2026 SMD | 2025 AUC | 2026 AUC | Direction 2025 | Direction 2026 | Cov25 | Cov26 |
|---|---:|---:|---:|---:|---|---|---:|---:|
| leadlag_score_premax | +0.626 | +0.798 | 0.625 | 0.711 | HIGHER_RESCUE | HIGHER_RESCUE | 100.0% | 100.0% |
| strong_pro_risk | +0.360 | +0.853 | 0.569 | 0.698 | HIGHER_RESCUE | HIGHER_RESCUE | 100.0% | 100.0% |
| scheduled_event_known | +0.957 | +0.290 | 0.625 | 0.552 | HIGHER_RESCUE | HIGHER_RESCUE | 100.0% | 100.0% |
| opt_vol_imbalance | +0.965 | +0.240 | 0.778 | 0.547 | HIGHER_RESCUE | HIGHER_RESCUE | 100.0% | 100.0% |

## Strongest cross-year candidates, including non-stable

| Feature | Stable | 2025 SMD | 2026 SMD | 2025 AUC | 2026 AUC | Min group N |
|---|---|---:|---:|---:|---:|---:|
| leadlag_score_premax | True | +0.626 | +0.798 | 0.625 | 0.711 | 4 |
| strong_pro_risk | True | +0.360 | +0.853 | 0.569 | 0.698 | 4 |
| scheduled_event_known | True | +0.957 | +0.290 | 0.625 | 0.552 | 4 |
| opt_vol_imbalance | True | +0.965 | +0.240 | 0.778 | 0.547 | 4 |
| leadlag_score | False | +1.291 | -0.985 | 0.667 | 0.747 | 3 |
| gc_dlog_volume_1 | False | -1.137 | +0.714 | 0.750 | 0.698 | 4 |
| flow_oi_chg1 | False | +0.673 | -1.544 | 0.694 | 0.857 | 4 |
| gc_volume_accel_5 | False | -1.133 | +0.645 | 0.806 | 0.661 | 4 |
| safe_topology_score | False | +0.528 | -0.790 | 0.611 | 0.703 | 4 |
| vix_r60 | False | +0.526 | -1.004 | 0.611 | 0.755 | 4 |
| ndx_r60 | False | -0.529 | +0.506 | 0.611 | 0.635 | 4 |
| gc_volume_z20 | False | -0.411 | +0.608 | 0.639 | 0.620 | 4 |
| rte_tension | False | +0.321 | -0.788 | 0.611 | 0.708 | 4 |
| signed_d_opt_pressure | False | -1.318 | +0.310 | 0.778 | 0.599 | 4 |
| opt_total_z20 | False | -0.342 | +0.307 | 0.611 | 0.599 | 4 |

## Topology contingency

| Year | Strong pro-risk: rescue/broken | Other topology: rescue/broken |
|---|---:|---:|
| 2025 | 1/1 | 3/8 |
| 2026 | 9/2 | 7/10 |

## Scheduled-event context

| Year | Event rescue/broken | Non-event rescue/broken |
|---|---:|---:|
| 2025 | 1/0 | 3/9 |
| 2026 | 3/1 | 13/11 |

## Interpretation discipline

- This audit asks what distinguishes a true Handoff reversal from a false Handoff alarm; it does not choose a threshold.
- Preliminary OI is incomplete after 2026-03-19 and cannot be promoted as a full-year discriminator.
- Sparse scheduled-event ledgers are context only; absence of a ledger row is not proof that no macro catalyst existed.
- Features derived from H3 future outcomes were excluded.
- Any apparent discriminator must be separately frozen and tested; no 2026 accuracy is modified here.
