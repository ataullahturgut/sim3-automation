# GOLD H3 — Handoff Competence BOCPD V1 Result

**Status:** FROZEN_2026_STRESS_COMPLETE

## Formation — 2025 Handoff competence only

- alarms: **13**; rescue/broken = **4 / 9**
- sequential log evidence: E[run]=4: -9.4938, E[run]=6: -9.5811, E[run]=8: -9.5995, E[run]=12: -9.5987
- selected expected competence run: **4 Handoff alarms**

## Frozen trust rule

- ACT only if predictive P(rescue) >= **0.60**
- and mixture P(theta>0.50) >= **0.80**
- otherwise reject Handoff and keep the combined baseline.

## 2026 causal sequential stress

- broad Handoff alarms: **28**
- acted / rejected: **5 / 23**
- action rescue / broken / net: **3 / 2 / +1**
- action precision: **60.00%**
- remaining-53 reversals rescued: **3**
- rejected Handoff alarms contained rescue/broken: **13 / 10**
- first trusted Handoff origin: **2026-05-27**

- baseline: **126/191 = 65.97%**, BA **66.31%**
- + competence BOCPD: **127/191 = 66.49%**, BA **66.81%**

## Handoff alarm chronology

| Date | P(rescue) | P(theta>.5) | MAP run | Act | Actual Handoff outcome |
|---|---:|---:|---:|---|---|
| 2026-01-26 | 0.184 | 0.070 | 3 | False | RESCUE |
| 2026-01-27 | 0.184 | 0.070 | 3 | False | RESCUE |
| 2026-02-09 | 0.721 | 0.770 | 1 | False | BROKEN |
| 2026-02-10 | 0.721 | 0.770 | 1 | False | BROKEN |
| 2026-02-24 | 0.276 | 0.177 | 1 | False | RESCUE |
| 2026-02-25 | 0.276 | 0.177 | 1 | False | RESCUE |
| 2026-03-02 | 0.708 | 0.776 | 1 | False | BROKEN |
| 2026-03-04 | 0.708 | 0.776 | 1 | False | BROKEN |
| 2026-03-13 | 0.289 | 0.202 | 1 | False | BROKEN |
| 2026-03-16 | 0.289 | 0.202 | 1 | False | RESCUE |
| 2026-03-19 | 0.559 | 0.542 | 0 | False | BROKEN |
| 2026-03-23 | 0.559 | 0.542 | 0 | False | BROKEN |
| 2026-04-07 | 0.260 | 0.138 | 1 | False | BROKEN |
| 2026-04-10 | 0.211 | 0.089 | 2 | False | BROKEN |
| 2026-04-28 | 0.180 | 0.066 | 3 | False | BROKEN |
| 2026-04-30 | 0.180 | 0.066 | 3 | False | RESCUE |
| 2026-05-18 | 0.553 | 0.527 | 0 | False | RESCUE |
| 2026-05-21 | 0.731 | 0.784 | 1 | False | RESCUE |
| 2026-05-27 | 0.807 | 0.888 | 2 | True | RESCUE |
| 2026-06-01 | 0.843 | 0.929 | 3 | True | BROKEN |
| 2026-06-08 | 0.431 | 0.437 | 0 | False | RESCUE |
| 2026-06-29 | 0.675 | 0.763 | 0 | False | RESCUE |
| 2026-07-14 | 0.758 | 0.873 | 1 | True | RESCUE |
| 2026-07-17 | 0.802 | 0.918 | 2 | True | BROKEN |
| 2026-09-03 | 0.454 | 0.482 | 0 | False | RESCUE |
| 2026-09-09 | 0.676 | 0.781 | 0 | False | RESCUE |
| 2026-09-11 | 0.676 | 0.781 | 0 | False | RESCUE |
| 2026-09-24 | 0.796 | 0.920 | 2 | True | RESCUE |

## Monthly acted net

- 2026-05: **+1**
- 2026-06: **-1**
- 2026-07: **+0**
- 2026-09: **+1**

## Scientific interpretation

- The engine estimates the time-varying competence of the Handoff expert, not Gold direction directly.
- Each 2026 decision uses only Handoff outcomes whose H3 targets had already matured by that feature cutoff.
- 2026 did not select the BOCPD hazard or trust thresholds.
- Because the Handoff family itself was motivated by retrospective 2026 analysis, this is stringent retrospective stress evidence, not pristine prospective validation.
