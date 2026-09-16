# GOLD CONTROL — BOCPD HOURLY B2 OPTIMIZED RESULT

**Date:** 2026-09-16  
**Identity:** `BOCPD_HOURLY_SELECTIVE_CANDIDATE_B2_V1_RESEARCH`  
**Research-line status:** `ACTIVE_BOCPD_RESEARCH_REFERENCE`  
**Promotion status:** `PROMISING_SELECTIVE_REGIME_CONTEXT / NOT_READY_FOR_RUNTIME_PROMOTION`  
**Evidence:** retrospective challenge; 2025 not used for parameter selection.  
**Direction vote:** NOT PERMITTED.

## Design

- 2023: fit NY-hour mean/scale and NIG prior.
- 2024-01-01..2024-10-31: select hazard and reset-strength threshold only.
- 2024-11-01..2024-12-31: warm-start/state building only; no selection.
- 2025: locked retrospective challenge.
- Core model: hourly Adams-MacKay BOCPD with NIG/Student-t predictive structure.
- Candidate hazard grid: expected regime 20/40/60/120 days = 440/880/1320/2640 eligible hourly observations.
- Reset-fraction threshold grid: 0.50/0.70/0.80/0.90/0.95/0.98.
- Episode rule frozen before challenge: first qualifying reset retained, subsequent qualifying resets suppressed for 24 elapsed hours.
- 2024 optimization event definition: the same daily volatility construction (`abs(z)>=2`, lagged trailing-20 sample volatility).
- Frozen warning-validity rule: signal must be available no later than the previous governed daily close and no more than 120 calendar hours before event-close availability.
- Selection objective: maximize F0.5 so selectivity/precision is weighted more heavily than recall.

## 2024 selection

2024 Jan-Oct contained **14** frozen-formula volatility events.

The 24 predeclared hazard/threshold combinations were evaluated before 2025 challenge scoring. The selected combination was:

- expected regime: **120 days / 2640 hourly observations**;
- reset_fraction threshold: **0.80**;
- 24h episode cooldown.

2024 Jan-Oct selection performance under the frozen strict 120h warning rule:

- episodes: **26**;
- matched episodes: **8**;
- false episodes: **18**;
- captured events: **6/14**;
- precision: **0.307692**;
- recall: **0.428571**;
- F0.5: **0.326087**.

The selectivity-aware objective therefore chose a slow 120-day expected-regime prior together with an explicit reset-strength filter.

## Warm start

After selection, the model was reinitialized from the frozen prior at 2024-11-01, processed November and December continuously, and entered 2025 without resetting its BOCPD state at the calendar-year boundary.

No 2024 Nov-Dec outcome was used for model selection.

## 2025 locked challenge

Source checks passed:

- 255/255 governed 2025 daily research closes matched the hourly source exactly;
- 5,645 eligible exact-one-hour returns in 2025.

B2 produced:

- **46** 2025 warning episodes;
- **46** unique episode days;
- formal strict-120h matched episodes: **11**;
- formal false episodes: **35**;
- formal precision: **23.91%**;
- formal event recall: **63.16% (12/19)**;
- formal F0.5: **0.273066**.

The 12 formally captured 2025 event dates and lead times were:

| Event | Lead |
|---|---:|
| 2025-02-14 | 81 h |
| 2025-03-13 | 49 h |
| 2025-04-04 | 48 h |
| 2025-04-09 | 67 h |
| 2025-04-10 | 91 h |
| 2025-09-02 | 42 h |
| 2025-10-13 | 100 h |
| 2025-10-16 | 66 h |
| 2025-10-17 | 90 h |
| 2025-10-21 | 117 h |
| 2025-12-22 | 77 h |
| 2025-12-29 | 115 h |

Not captured under the frozen formal rule:

- 2025-02-10
- 2025-02-18
- 2025-07-21
- 2025-08-01
- 2025-09-22
- 2025-09-29
- 2025-10-06

## Interpretation

The useful B2 regime-context signal is represented by:

1. a slow **120-day** expected-regime prior,
2. relatively strong resets (`reset_fraction >= 0.80`), and
3. a 24-hour episode-onset rule rather than repeated hourly reset counting.

The 2025 challenge is consistent enough with the 2024 development result to justify retaining B2 as the **active BOCPD research reference**, but not to grant runtime or production authority. F0.5 moves from 0.326 in 2024 development to 0.273 in 2025 retrospective challenge; event recall is 12/19. At the same time, 35/46 2025 episodes are unmatched under the frozen 120h rule, so standalone warning precision remains limited.

Current classification:

`ACTIVE_BOCPD_RESEARCH_REFERENCE / PROMISING_SELECTIVE_REGIME_CONTEXT / NOT_READY_FOR_RUNTIME_PROMOTION`

Do not retune threshold, hazard, cooldown or 120h horizon using visible 2025 results. Any scientific development must use a separately named successor and pre-2025 chronology and/or genuinely prospective evidence.

Priority development questions for the successor line are:

- whether a learned or non-constant hazard improves regime-duration calibration;
- whether a robust/heavy-tail observation model reduces false episode burden from isolated XAU return shocks;
- whether residual-time / explicit-duration inference can estimate proximity to the next regime change rather than only detecting current regime change;
- whether these changes improve pre-2025 time-ordered evidence without sacrificing selectivity.

## Reproducibility

Workflow run: `35118669443`  
Job: `104870533925`  
Artifact: `bocpd-hourly-candidate-b2-2025`  
Artifact ID: `10456271581`  
Artifact ZIP SHA-256: `829ac1688cd22526df394b034a15864dac881065eb8075c45087961fe2aeba43`

No database model-output write, runtime promotion, direction vote or merge was performed.
