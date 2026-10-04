# GOLD H3 — Direction-Conditioned Handoff Competence BOCPD V2

**Status:** POSTHOC_MECHANISTIC_STRESS

## Frozen mechanics

- two independent competence streams: UP-momentum and DOWN-momentum
- expected run: **4 alarms** (frozen from V1)
- ACT: P(rescue)>=0.60 and P(theta>.5)>=0.80

## 2025 initialization

- UP: 11 alarms, 3 rescue / 8 broken
- DOWN: 2 alarms, 1 rescue / 1 broken

## 2026 stress

- Handoff alarms: **28**; acted/rejected **7 / 21**
- rescue/broken/net: **3 / 4 / -1**
- precision: **42.86%**
- remaining-53 rescued: **3**
- baseline: **126/191 = 65.97%**, BA **66.31%**
- + directional competence: **125/191 = 65.45%**, BA **65.76%**

## Direction detail

- DOWN: acted 3, rescue/broken 0/3, first trust 2026-02-10
- UP: acted 4, rescue/broken 3/1, first trust 2026-06-08

## Chronology

| Date | Stream | P(rescue) | P(theta>.5) | Act | Outcome |
|---|---|---:|---:|---|---|
| 2026-01-26 | DOWN | 0.600 | 0.627 | False | RESCUE |
| 2026-01-27 | UP | 0.184 | 0.067 | False | RESCUE |
| 2026-02-09 | UP | 0.546 | 0.513 | False | BROKEN |
| 2026-02-10 | DOWN | 0.734 | 0.818 | True | BROKEN |
| 2026-02-24 | DOWN | 0.423 | 0.409 | False | RESCUE |
| 2026-02-25 | DOWN | 0.423 | 0.409 | False | RESCUE |
| 2026-03-02 | DOWN | 0.733 | 0.845 | True | BROKEN |
| 2026-03-04 | DOWN | 0.733 | 0.845 | True | BROKEN |
| 2026-03-13 | DOWN | 0.297 | 0.236 | False | BROKEN |
| 2026-03-16 | UP | 0.321 | 0.212 | False | RESCUE |
| 2026-03-19 | DOWN | 0.218 | 0.129 | False | BROKEN |
| 2026-03-23 | UP | 0.575 | 0.573 | False | BROKEN |
| 2026-04-07 | UP | 0.362 | 0.272 | False | BROKEN |
| 2026-04-10 | UP | 0.271 | 0.149 | False | BROKEN |
| 2026-04-28 | DOWN | 0.176 | 0.081 | False | BROKEN |
| 2026-04-30 | UP | 0.219 | 0.094 | False | RESCUE |
| 2026-05-18 | UP | 0.545 | 0.509 | False | RESCUE |
| 2026-05-21 | UP | 0.709 | 0.756 | False | RESCUE |
| 2026-05-27 | DOWN | 0.151 | 0.060 | False | RESCUE |
| 2026-06-01 | DOWN | 0.565 | 0.552 | False | BROKEN |
| 2026-06-08 | UP | 0.791 | 0.871 | True | RESCUE |
| 2026-06-29 | DOWN | 0.322 | 0.227 | False | RESCUE |
| 2026-07-14 | UP | 0.833 | 0.920 | True | RESCUE |
| 2026-07-17 | UP | 0.855 | 0.941 | True | BROKEN |
| 2026-09-03 | UP | 0.431 | 0.439 | False | RESCUE |
| 2026-09-09 | UP | 0.679 | 0.770 | False | RESCUE |
| 2026-09-11 | UP | 0.679 | 0.770 | False | RESCUE |
| 2026-09-24 | UP | 0.805 | 0.921 | True | RESCUE |

## Governance

This successor was motivated by the observed 2026 directional asymmetry, so the replay is explicitly post-hoc mechanistic research. No threshold or hazard was changed after preregistration.
