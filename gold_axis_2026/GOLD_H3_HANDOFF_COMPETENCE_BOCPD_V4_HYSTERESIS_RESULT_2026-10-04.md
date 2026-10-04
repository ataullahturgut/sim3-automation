# GOLD H3 — Handoff Competence BOCPD V4 Hysteresis

**Status:** POSTHOC_DEVELOPMENT_DIAGNOSTIC

## Frozen state machine

- enter trust: P(rescue)>=0.60 and P(theta>.5)>=0.80
- once ON, act on every Handoff alarm
- exit only after **2 consecutive matured BROKEN outcomes from acted Handoff alarms**

## 2026 replay

- Handoff alarms: **28**; acted/rejected **10 / 18**
- rescue/broken/net: **8 / 2 / +6**
- precision: **80.00%**
- remaining-53 rescued: **8**
- baseline: **126/191 = 65.97%**, BA **66.31%**
- + hysteretic competence: **132/191 = 69.11%**, BA **69.36%**

## Trust-state events

- 2026-05-27: **TRUST_ENTRY**

## Chronology

| Date | P(rescue) | P(theta>.5) | Entry | Trust | Fail streak | Act | Outcome |
|---|---:|---:|---|---|---:|---|---|
| 2026-01-26 | 0.184 | 0.070 | False | False | 0 | False | RESCUE |
| 2026-01-27 | 0.184 | 0.070 | False | False | 0 | False | RESCUE |
| 2026-02-09 | 0.721 | 0.770 | False | False | 0 | False | BROKEN |
| 2026-02-10 | 0.721 | 0.770 | False | False | 0 | False | BROKEN |
| 2026-02-24 | 0.276 | 0.177 | False | False | 0 | False | RESCUE |
| 2026-02-25 | 0.276 | 0.177 | False | False | 0 | False | RESCUE |
| 2026-03-02 | 0.708 | 0.776 | False | False | 0 | False | BROKEN |
| 2026-03-04 | 0.708 | 0.776 | False | False | 0 | False | BROKEN |
| 2026-03-13 | 0.289 | 0.202 | False | False | 0 | False | BROKEN |
| 2026-03-16 | 0.289 | 0.202 | False | False | 0 | False | RESCUE |
| 2026-03-19 | 0.559 | 0.542 | False | False | 0 | False | BROKEN |
| 2026-03-23 | 0.559 | 0.542 | False | False | 0 | False | BROKEN |
| 2026-04-07 | 0.260 | 0.138 | False | False | 0 | False | BROKEN |
| 2026-04-10 | 0.211 | 0.089 | False | False | 0 | False | BROKEN |
| 2026-04-28 | 0.180 | 0.066 | False | False | 0 | False | BROKEN |
| 2026-04-30 | 0.180 | 0.066 | False | False | 0 | False | RESCUE |
| 2026-05-18 | 0.553 | 0.527 | False | False | 0 | False | RESCUE |
| 2026-05-21 | 0.731 | 0.784 | False | False | 0 | False | RESCUE |
| 2026-05-27 | 0.807 | 0.888 | True | True | 0 | True | RESCUE |
| 2026-06-01 | 0.843 | 0.929 | False | True | 0 | True | BROKEN |
| 2026-06-08 | 0.431 | 0.437 | False | True | 1 | True | RESCUE |
| 2026-06-29 | 0.675 | 0.763 | False | True | 0 | True | RESCUE |
| 2026-07-14 | 0.758 | 0.873 | False | True | 0 | True | RESCUE |
| 2026-07-17 | 0.802 | 0.918 | False | True | 0 | True | BROKEN |
| 2026-09-03 | 0.454 | 0.482 | False | True | 1 | True | RESCUE |
| 2026-09-09 | 0.676 | 0.781 | False | True | 0 | True | RESCUE |
| 2026-09-11 | 0.676 | 0.781 | False | True | 0 | True | RESCUE |
| 2026-09-24 | 0.796 | 0.920 | False | True | 0 | True | RESCUE |

## Governance

V4 was designed after inspecting V1 chronology. Its 2026 result is therefore development evidence, not validation. Entry thresholds, BOCPD hazard and the two-strike exit were frozen before this run.
