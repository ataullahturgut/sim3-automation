# GOLD H3 — Databento Downstream Invariance Audit (2025) — 2026-10-05

**Status:** **DOWNSTREAM_DECISION_INVARIANCE_REQUIRES_REVIEW**  
Estimated Databento request cost: **USD 0.5777** (cap USD 1.00).  
**No thresholds or controller rules were retuned; no DPTC outcomes were used to select the source mapping.**

## Frozen source mapping used

| Channel | Databento |
|---|---|
| GC | GC.v.0 |
| SI | SI.v.0 |
| NQ | NQ.v.0 |
| ZN | ZN.n.0 |
| CL | CL.c.0 |

## Derived-state agreement

- IFBC score: corr=0.96402, MAE=0.0299419, max=0.85124
- LLRS pressure: corr=0.92269, MAE=0.0578231, max=0.509317
- LLRS incremental: corr=0.91002, MAE=0.0558281, max=0.494251
- Handoff leadlag premax: corr=0.72055, MAE=0.150541, max=0.966942
- Handoff internal_now: corr=0.99416, MAE=0.0134869, max=0.157025
- Handoff internal_d1: corr=0.99271, MAE=0.0240387, max=0.161157

## Decision invariance

- Handoff alarms: Databento **33**, Yahoo **30**, matched **28**, Jaccard **80.0%**.
- Added Databento alarms: **2025-04-17, 2025-08-05, 2025-08-06, 2025-09-26, 2025-10-31**.
- Missing vs Yahoo: **2025-05-29, 2025-08-11**.

| Variant | DB actions | Yahoo actions | Matched | Jaccard | DB R/B/net | Shared-mode match |
|---|---:|---:|---:|---:|---:|---:|
| Q95 | 10 | 9 | 9 | 90.0% | 4/6/-2 | 100.0% |
| Q99 | 9 | 8 | 8 | 88.9% | 3/6/-3 | 100.0% |

## Scientific interpretation

Source differences materially change Handoff/DPTC decisions; do not call a 2023-2024 replay equivalent without further mechanism-level diagnosis.

- This audit tests downstream invariance, not raw-bar identity.
- The primary objects are IFBC/LLRS states, canonical Handoff alarms, and frozen Q95/Q99 controller actions.
- A 90% decision-set threshold was preregistered in this audit script before observing its results.
- Even if passed, a 2023–2024 Databento replay must be labeled source-bridged historical reconstruction, not Yahoo-identical lineage.
