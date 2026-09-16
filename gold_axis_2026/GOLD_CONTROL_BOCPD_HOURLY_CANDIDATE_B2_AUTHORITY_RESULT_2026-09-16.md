# GOLD CONTROL — BOCPD HOURLY CANDIDATE B2 AUTHORITY RESULT

**Date:** 2026-09-16  
**Identity:** `BOCPD_HOURLY_POSTERIOR_MASS_CANDIDATE_B2_V1_RESEARCH`  
**Evidence class:** `HISTORICAL_REPLAY_VISIBLE_REUSED_CHALLENGE`  
**Status:** `PROMISING_SELECTIVE_RESEARCH_CONTEXT / PROSPECTIVE_VALIDITY_NOT_PROVEN`  
**Runtime promotion:** NONE  
**Direction vote:** NOT PERMITTED  
**Database model-output writes:** NONE

## 1. Why B2 exists

Candidate B demonstrated that moving BOCPD from a daily to an hour-adjusted hourly clock can surface regime-change context earlier, but the raw MAP-reset extraction rule was too nonselective: 177 reset hours across 114 days in 2025.

Candidate B2 is a separately named successor designed only after an authority review. Because Candidate B's 2025 result was already visible before B2 was designed, B2's 2025 replay is explicitly **not** a pristine holdout. No B2 parameter is selected using 2025, but 2025 evidence is classified as a visible reused retrospective challenge.

## 2. Authority basis

Project authority is `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` v1.58. It requires engine-first replay, truthful availability time, no challenge-result tuning, no event-conditioned signal generation, no post-hoc warning horizon, and separate identity for research successors.

External methodological authority reviewed before B2 design included:

- Adams & MacKay Bayesian Online Changepoint Detection: the online state is the posterior distribution over run length, not only a binary MAP-reset event.
- sequential changepoint literature: detection delay must be balanced against explicit false-alarm / alarm-spacing control;
- robust BOCPD literature: ordinary BOCPD can create spurious changepoints under outliers or model misspecification;
- high-frequency financial and precious-metals literature: intraday periodicity in volatility is material and should not be ignored.

B2 does **not** claim to implement published beta-divergence robust BOCPD. It retains a Student-t posterior predictive and changes the operational extraction rule from raw MAP reset to posterior short-run mass plus a pre-2025 signal-budget calibration.

## 3. Frozen B2 design

Preregistration was written before 2025 B2 replay:

`gold_axis_2026/bocpd_hourly_candidate_b2/authority_preregistration_v1.md`

Frozen contract was written after pre-2025 calibration and before 2025 replay:

`gold_axis_2026/bocpd_hourly_candidate_b2/frozen_contract_v1.json`

### Data chronology

- 2023: fit hour-of-day mean/scale and Normal-Inverse-Gamma prior.
- 2024: select BOCPD constant hazard and alarm threshold.
- 2025: frozen replay only; no B2 retuning.

### Observation process

- source: Twelve Data XAU/USD 1h research data;
- New York XAU session gate;
- exact one-hour elapsed log returns only;
- hour-of-day standardization fit on 2023 only;
- bar timestamp treated as bar start;
- output usable only after bar completion (`bar start + 1 hour`).

### BOCPD core

- Adams-MacKay run-length recursion;
- Gaussian unknown mean/variance within regime;
- Normal-Inverse-Gamma conjugate prior;
- Student-t posterior predictive.

### B2 authority-led score

Instead of treating every MAP run-length reset as an alarm, B2 computes:

`short_run_mass_t = sum_{r=0}^{22} P(run_length_t = r | x_1:t)`

The 22-observation short-run window is approximately one full eligible XAU trading day.

A new B2 alarm requires all three conditions:

1. `short_run_mass_t >= q`;
2. previous short-run mass `< q` (an up-crossing; continued high mass is one episode, not repeated alarms);
3. previous MAP run length `>= 22`, requiring at least approximately one trading day of mature preceding regime.

No sign filter, event filter, post-2025 debounce or event-conditioned selection is used.

## 4. Pre-2025 calibration — 2024 only

Calibration workflow:

- run: `35104431047`
- job: `104821834958`
- artifact: `bocpd-hourly-b2-pre2025-calibration-r1`
- artifact ID: `10449636487`
- artifact ZIP SHA-256: `cb6d7f2d21b1f109b6ba9614d3e9c5afd0b31d09fb4e4eebc3ce1433f6760d84`
- `challenge_2025_accessed = false`

Eligible returns used before challenge:

- 2023: 5,579
- 2024: 5,650

Hazard selection by 2024 prequential log predictive evidence:

| Expected regime | Observations | 2024 log evidence | MAP resets |
|---|---:|---:|---:|
| 20 trading days | 440 | **-8792.928780** | 179 |
| 40 trading days | 880 | -8809.436204 | 142 |
| 60 trading days | 1320 | -8818.729896 | 141 |
| 120 trading days | 2640 | -8834.161794 | 109 |

Frozen hazard: **1/440 = 0.002272727273**.

Threshold grid was preregistered before calibration. The selection rule was the smallest threshold whose empirical 2024 alarm-onset spacing proxy was at least the selected 440-observation expected regime length.

| q | 2024 alarm onsets | Empirical spacing proxy | Pass 440 target? |
|---:|---:|---:|---|
| 0.50 | 32 | 176.562 | No |
| 0.60 | 20 | 282.500 | No |
| 0.70 | 14 | 403.571 | No |
| **0.80** | **12** | **470.833** | **Yes** |
| 0.90 | 10 | 565.000 | Yes |
| 0.95 | 9 | 627.778 | Yes |
| 0.975 | 6 | 941.667 | Yes |
| 0.99 | 6 | 941.667 | Yes |

Therefore the preregistered rule selected **q = 0.80**. This value was frozen before the B2 2025 replay.

The spacing statistic is an empirical alarm-spacing proxy, not formal null `ARL0`, because 2024 itself contains unknown genuine regime changes.

## 5. Frozen 2025 replay validation

Successful replay workflow:

- run: `35104862668`
- job: `104823329690`
- artifact: `bocpd-hourly-b2-2025-visible-reused-challenge`
- artifact ID: `10449173861`
- artifact ZIP SHA-256: `b53b49cf52d7e09cd2b4a4738bede599f6da8f3fd009e98b52da379f9e05dbdf`

Source and freeze checks:

- 2025 provider raw rows: 6,802;
- after XAU session gate: 5,909;
- governed weekday daily cross-check: 255/255 exact timestamp matches and 255/255 exact value matches;
- eligible exact one-hour returns: 2023 = 5,579; 2024 = 5,650; 2025 = 5,645;
- frozen 2024 calibration reproduced exactly: 12 alarm onsets;
- no calibration parameter changed after contract freeze.

## 6. Full 2025 engine-first B2 output

B2 produced only **7 alarm onsets** in 2025 from 5,645 eligible hourly returns.

Alarm-onset rate: **0.1240%** of eligible hourly observations.

Unique alarm dates: **7**.

There were 31 raw threshold-above segments, but only 7 satisfied the complete frozen B2 onset rule, including mature preceding regime. This distinction is intentional: threshold activity is not automatically an alarm.

Exact alarm onsets:

| # | New York bar start | Signal available after bar | Short-run posterior mass |
|---:|---|---|---:|
| 1 | 2025-02-11 07:00 EST | 2025-02-11 08:00 EST | 0.914865 |
| 2 | 2025-04-06 21:00 EDT | 2025-04-06 22:00 EDT | 0.826459 |
| 3 | 2025-08-31 22:00 EDT | 2025-08-31 23:00 EDT | 0.999931 |
| 4 | 2025-09-17 14:00 EDT | 2025-09-17 15:00 EDT | 0.903325 |
| 5 | 2025-10-09 12:00 EDT | 2025-10-09 13:00 EDT | 0.994063 |
| 6 | 2025-12-25 19:00 EST | 2025-12-25 20:00 EST | ~1.000000 |
| 7 | 2025-12-31 00:00 EST | 2025-12-31 01:00 EST | 0.917146 |

Monthly alarm counts:

- February: 1
- April: 1
- August: 1
- September: 1
- October: 1
- December: 2

Compared with Candidate B's 177 raw MAP reset hours, B2 reduces signal burden by **170 signals**, or approximately **96.0%**, while using no 2025 parameter tuning.

## 7. Frozen 19-event overlay

The event inventory was overlaid only after the full B2 engine output was frozen.

Descriptive event-side counts:

- prior B2 alarm within 24 hours: **0 / 19**;
- within 72 hours: **2 / 19**;
- within 120 hours: **6 / 19**;
- within 240 hours: **10 / 19**.

Critically:

- `STRICT_PRE_EVENT_WINDOW`: **10 / 19**;
- `INTRADAY_PRE_EVENT_CLOSE`: **0 / 19**;
- `NO_ALARM_WITHIN_240H`: **9 / 19**;
- same-event-close alarm: **0 / 19**.

Thus every event-associated B2 alarm in the 240-hour descriptive window was already available **before the previous governed daily close**, rather than firing inside the realized event day.

Event details for the 10 events with a prior B2 alarm within 240 hours:

| Event date | Lead from latest prior B2 alarm |
|---|---:|
| 2025-02-14 | 81 h |
| 2025-02-18 | 177 h |
| 2025-04-09 | 67 h |
| 2025-04-10 | 91 h |
| 2025-09-02 | 42 h |
| 2025-09-22 | 122 h |
| 2025-10-13 | 100 h |
| 2025-10-16 | 172 h |
| 2025-10-17 | 196 h |
| 2025-12-29 | 93 h |

The other 9 frozen volatility events had no B2 alarm within the descriptive 240-hour window.

## 8. Reverse accounting from every B2 alarm

Among all 7 B2 alarm onsets, the next frozen volatility event occurred within:

- 24 hours: **0 / 7 alarms**;
- 72 hours: **2 / 7 alarms**;
- 120 hours: **5 / 7 alarms**;
- 240 hours: **6 / 7 alarms**.

The six alarms followed within 240 hours by a frozen event were:

- 2025-02-11 -> 2025-02-14 event;
- 2025-04-06 -> 2025-04-09 event;
- 2025-08-31 -> 2025-09-02 event;
- 2025-09-17 -> 2025-09-22 event;
- 2025-10-09 -> 2025-10-13 event;
- 2025-12-25 -> 2025-12-29 event.

The 2025-12-31 alarm has no later frozen 2025 volatility event available for same-year follow-up.

These counts are **descriptive association only**. Because no 240-hour warning-validity horizon was preregistered, `6/7` must not be reported as formal precision or accuracy.

## 9. Candidate B versus B2

| Property | Candidate B raw MAP reset | Candidate B2 posterior-mass onset |
|---|---:|---:|
| 2025 signals | 177 reset hours | **7 alarm onsets** |
| Unique signal dates | 114 | **7** |
| Event with prior signal <=72h | 12/19 | 2/19 |
| Event with prior signal <=120h | 16/19 | 6/19 |
| Event with prior signal <=240h | 19/19 | 10/19 |
| Signal -> next event <=240h | 56/177 | 6/7 |
| Intraday event-day latest prior signal | 8/19 | **0/19** |
| Same-event-close signal | 1 | **0** |

B2 gives up broad event coverage in exchange for dramatically greater selectivity and cleaner pre-event timing. That is the intended authority-led tradeoff.

## 10. Scientific interpretation

B2 is materially more credible than Candidate B as a **selective regime-change context signal**:

- signal burden falls from 177 to 7 without using 2025 for calibration;
- all 10 event-associated alarms in the 240-hour descriptive window are strict pre-event signals, not event-day confirmations;
- six of seven alarms are descriptively followed by a frozen abnormal daily event within 240 hours;
- one alarm at year-end cannot be followed beyond the frozen 2025 event inventory.

However, these facts do **not** establish prospective early-warning performance. B2 was designed after Candidate B's 2025 result had already been observed, so 2025 is a visible reused challenge even though B2 calibration itself is cleanly pre-2025.

Current classification:

`PROMISING_SELECTIVE_RESEARCH_CONTEXT / PROSPECTIVE_VALIDITY_NOT_PROVEN`

The scientifically correct next step is not further 2025 tuning. It is to freeze B2 exactly as it now stands and evaluate it in a genuinely prospective shadow period, with future alarms timestamped before outcomes are known.

## 11. Governance consequence

Do not change `K=22`, `hazard=1/440`, `q=0.80`, alarm maturity, episode rule, warning horizon or source clock using visible 2025 results and continue calling the result B2 V1.

Any material change requires a new identity and pre-challenge development process.

No runtime promotion, canonical merge, automated integration, direction vote, position mapping or database model-output write is authorized by this result.
