# GOLD H3 — DPTC V1 Result

**Status:** POSTHOC_DEVELOPMENT_CHALLENGER — frozen for prospective shadow after 2026-10-05.

Combined baseline reference: **126/191 = 65.97%**, BA **66.31%**.

## Variant summary

| Variant | 2025 actions R/B/net | 2026 entry | 2026 actions | Rescue | Broken | Net | Precision | Accuracy | BA | Worst leave-one-month-out |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Q95 | 2 (1/1/+0) | 2026-05-21 | 13 | 11 | 2 | +9 | 84.6% | 70.68% | 70.86% | +5 |
| Q99 | 2 (1/1/+0) | 2026-05-21 | 12 | 10 | 2 | +8 | 83.3% | 70.16% | 70.36% | +4 |

## Q95 action chronology

| Date | Mode | Outcome | SELLR catalyst |
|---|---|---|---|
| 2026-04-30 | PHASE | RESCUE | False |
| 2026-05-18 | PHASE | RESCUE | False |
| 2026-05-21 | TRUST | RESCUE | True |
| 2026-05-27 | TRUST | RESCUE | False |
| 2026-06-01 | TRUST | BROKEN | False |
| 2026-06-08 | TRUST | RESCUE | False |
| 2026-06-29 | TRUST | RESCUE | False |
| 2026-07-14 | TRUST | RESCUE | False |
| 2026-07-17 | TRUST | BROKEN | False |
| 2026-09-03 | TRUST | RESCUE | False |
| 2026-09-09 | TRUST | RESCUE | False |
| 2026-09-11 | TRUST | RESCUE | False |
| 2026-09-24 | TRUST | RESCUE | False |

## Scientific interpretation

- Q95 and Q99 were both frozen; future data may not be used to choose between them.
- Pre-trust actions come from label-free dependence topology; TRUST entry comes from the already-frozen SELLR threshold.
- Hysteresis handles delayed expert feedback after TRUST.
- The synthesis was designed after inspecting 2026 development evidence, so 2026 accuracy is development evidence, not independent validation.
- The value of DPTC is mechanistic separation: dependence state detects the competence phase, SELLR confirms a structural transition, and hysteresis preserves expert trust through noisy individual alarms.
