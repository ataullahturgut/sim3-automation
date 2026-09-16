# GOLD CONTROL — BOCPD HOURLY CANDIDATE B 2025 RESULT

**Date:** 2026-09-16  
**Identity:** `BOCPD_HOURLY_SEASONAL_RETURN_CANDIDATE_B_V1_RESEARCH`  
**Status:** `TOO_NONSELECTIVE_AS_STANDALONE_EARLY_WARNING / INSUFFICIENT_SUPPORT_FOR_PROMOTION`  
**Evidence class:** `HISTORICAL_REPLAY_RETROSPECTIVE_DIAGNOSTIC`  
**Runtime promotion:** NONE  
**Direction vote:** NOT PERMITTED  
**Database model-output writes:** NONE

## 1. Purpose

Candidate B tests whether moving BOCPD from the daily clock to an hour-of-day-adjusted hourly XAU/USD return clock can surface regime-change context earlier than the daily BOCPD research successor without using the frozen 2025 volatility outcomes for model design, hazard selection, threshold selection or tuning.

This is a research challenger only. It does not replace the governed monthly `BOCPD_RETURN_SUCCESSOR_V1` and does not become a runtime identity.

## 2. Frozen chronology and model

- 2023: fit hour-of-day return location/scale and NIG prior.
- 2024: choose the constant hazard only by prequential log predictive evidence.
- 2025: retrospective challenge only.
- raw return: `ln(P_t/P_{t-1})` for exact one-hour elapsed observations after the XAU session gate.
- hour adjustment: `(r_t - mean_hour) / sd_hour`, fitted on 2023 only and then frozen.
- BOCPD: Adams-MacKay recursion, Gaussian unknown mean/variance, Normal-Inverse-Gamma conjugate prior, Student-t predictive.
- signal: MAP run-length reset, with no return-sign filter, no numeric alarm threshold and no post-hoc debounce/episode filter.
- all reset timestamps are retained.
- hourly bar timestamp is treated as bar start; model output is available only after bar completion, i.e. timestamp + 1 hour.

No 2025 volatility event was used to select the hour adjustment, prior, hazard, signal rule or a warning horizon.

## 3. Corrective data history before scientific scoring

Two runs failed closed before producing a model score.

1. The first 2025 provider fetch returned 6,802 raw hourly rows, exceeding the naive expected range. The run stopped before formation/challenge scoring.
2. A pre-score XAU session gate, derived from the already governed 2023-2024 clock, reduced 2025 to 5,909 in-session rows. The next run then stopped before scoring because the daily research query contained 267 2025 rows: 255 governed weekdays plus 12 Sunday rows. Neon verification confirmed weekday counts of 49 Monday, 51 Tuesday, 51 Wednesday, 52 Thursday, 52 Friday and 12 Sunday rows.
3. R2 corrected only the daily cross-check to the governed Monday-Friday universe. BOCPD mathematics, hazard candidates, reset rule and reporting windows were unchanged.

Therefore these corrections are data-quality/clock corrections, not repairs made from observed 2025 model performance.

## 4. Successful run and source validation

Successful workflow run: `35102281400`  
Job: `104814436206`  
Head SHA: `9c1131752e4216cc1b30efa7ef9f808ccafe6be3`  
Artifact: `bocpd-hourly-candidate-b-2025-r2`  
Artifact ID: `10448941286`  
Artifact ZIP SHA-256: `b01a5182faa4a269d4d92f1364e6133b1cb7533c5dfb429244da499095016e86`

Hourly source counts:

- 2023-2024 stored research rows after session gate: 11,751 / 11,751 retained.
- 2025 provider raw rows: 6,802.
- 2025 rows after XAU session gate: 5,909.
- 2025 out-of-session rows excluded: 893.
- exact eligible one-hour returns: 2023 = 5,579; 2024 = 5,650; 2025 = 5,645.
- 2023 per-hour support: minimum 224, maximum 257.

2025 daily-source cross-check:

- governed weekday daily rows: 255.
- exact timestamp overlap with 1h source: 255 / 255.
- exact value match: 255 / 255.
- maximum absolute difference: 0.

The fitted 2023 NIG prior was approximately `mu0=0`, `kappa0=1`, `alpha0=2`, `beta0=0.9962352098` on the hour-adjusted series.

## 5. 2024 hazard selection

| Expected regime | Expected hourly observations | 2024 log predictive evidence | 2024 MAP resets |
|---|---:|---:|---:|
| 20 days | 440 | -8792.928780 | 179 |
| 40 days | 880 | -8809.436204 | 142 |
| 60 days | 1320 | -8818.729896 | 141 |
| 120 days | 2640 | -8834.161794 | 109 |

Highest 2024 evidence selected **20 days / 440 observations**, giving frozen hazard `1/440 = 0.002272727273` before the 2025 challenge was evaluated.

## 6. Full 2025 engine-first output

Candidate B produced:

- eligible hourly returns: **5,645**;
- hourly MAP resets: **177**;
- unique calendar reset days: **114**;
- reset rate: **3.1355%** of eligible hourly returns.

Reset-hour counts by month:

| Month | Reset hours |
|---|---:|
| Jan | 3 |
| Feb | 9 |
| Mar | 7 |
| Apr | 13 |
| May | 25 |
| Jun | 14 |
| Jul | 19 |
| Aug | 20 |
| Sep | 15 |
| Oct | 17 |
| Nov | 22 |
| Dec | 13 |

The complete 177-reset timeline is preserved in the workflow artifact. It is not filtered down to the 19 realized volatility-event dates.

## 7. Frozen 19-event overlay

The table below uses the latest Candidate B reset available strictly before each event's governed daily close becomes available. `STRICT_PRE_EVENT_WINDOW` means that reset was already available before the previous governed daily close. `INTRADAY_PRE_EVENT_CLOSE` means the reset occurred after the previous daily close but before the current event close; this can be earlier than final daily-event realization but may already lie inside the day's price-move accumulation and therefore is not automatically a clean pre-movement warning.

| Event date | Latest prior-reset category | Lead to event close availability |
|---|---|---:|
| 2025-02-10 | STRICT_PRE_EVENT_WINDOW | 175 h |
| 2025-02-14 | STRICT_PRE_EVENT_WINDOW | 81 h |
| 2025-02-18 | STRICT_PRE_EVENT_WINDOW | 177 h |
| 2025-03-13 | STRICT_PRE_EVENT_WINDOW | 43 h |
| 2025-04-04 | STRICT_PRE_EVENT_WINDOW | 40 h |
| 2025-04-09 | STRICT_PRE_EVENT_WINDOW | 67 h |
| 2025-04-10 | STRICT_PRE_EVENT_WINDOW | 91 h |
| 2025-07-21 | INTRADAY_PRE_EVENT_CLOSE | 72 h |
| 2025-08-01 | INTRADAY_PRE_EVENT_CLOSE | 2 h |
| 2025-09-02 | STRICT_PRE_EVENT_WINDOW | 25 h |
| 2025-09-22 | INTRADAY_PRE_EVENT_CLOSE | 2 h |
| 2025-09-29 | STRICT_PRE_EVENT_WINDOW | 156 h |
| 2025-10-06 | INTRADAY_PRE_EVENT_CLOSE | 72 h |
| 2025-10-13 | INTRADAY_PRE_EVENT_CLOSE | 10 h |
| 2025-10-16 | INTRADAY_PRE_EVENT_CLOSE | 6 h |
| 2025-10-17 | INTRADAY_PRE_EVENT_CLOSE | 24 h |
| 2025-10-21 | STRICT_PRE_EVENT_WINDOW | 120 h |
| 2025-12-22 | INTRADAY_PRE_EVENT_CLOSE | 72 h |
| 2025-12-29 | STRICT_PRE_EVENT_WINDOW | 93 h |

Latest-prior-reset categories:

- `STRICT_PRE_EVENT_WINDOW`: **11 / 19**.
- `INTRADAY_PRE_EVENT_CLOSE`: **8 / 19**.
- same event 16:00 hourly-bar reset: **1** (`2025-10-16`); because that bar is usable only after completion, it is confirmation rather than early-warning evidence.

Descriptive event lookbacks, declared before 2025 scoring and not selected as a winning horizon:

- prior reset within 24 calendar hours: **5 / 19**;
- within 72 hours: **12 / 19**;
- within 120 hours: **16 / 19**;
- within 240 hours: **19 / 19**.

These are not recall/accuracy numbers because no warning-validity horizon is frozen and Candidate B emits many signals.

## 8. Reverse accounting: all signals to later events

Among all **177** Candidate B reset signals, the next frozen volatility event occurred within:

- 24 hours for **11** resets;
- 72 hours for **29** resets;
- 120 hours for **39** resets;
- 240 hours for **56** resets.

Thus a large majority of hourly resets are not followed by a frozen event even within 240 hours. Because 240 hours was not preregistered as an alarm-validity horizon, this is descriptive signal burden rather than a formal false-alarm rate.

This reverse accounting is essential: the attractive-looking `19/19 within 240h` event-side coverage is largely explained by the high density of 177 resets and must not be interpreted as near-perfect warning performance.

## 9. Interpretation

Candidate B demonstrates that hourly BOCPD can generate regime-change context substantially earlier and more frequently than the daily BOCPD clock. However, the frozen no-threshold MAP-reset rule is **too nonselective for a standalone early-warning motor** in its current form:

- 177 reset hours across 114 days is a high signal burden;
- many resets occur far from any frozen volatility event;
- several apparently impressive near-event signals are intraday and may have fired after the daily move had already started;
- one reset is on the event's own 16:00 hourly bar and is explicitly not early warning;
- the 10-day event-side coverage is not meaningful without accounting for the dense full-year reset timeline.

Current scientific classification:

`TOO_NONSELECTIVE_AS_STANDALONE_EARLY_WARNING / INSUFFICIENT_SUPPORT_FOR_PROMOTION`

Candidate B may remain useful as a high-frequency **regime-context layer**, but the present evidence does not justify runtime promotion, standalone warning claims or automated integration.

For comparison, the separately frozen daily Candidate A produced only 14 reset days in 2025. Candidate A is materially more selective, while Candidate B offers finer timing at the cost of much greater signal density. Neither has prospective evidence sufficient for production promotion.

## 10. Governance consequence

Do **not** repair Candidate B by choosing a `reset_fraction` cutoff, episode-stitching rule or preferred warning horizon from these visible 2025 results. Any such refinement requires a separately named successor whose filtering/threshold design is calibrated using only pre-2025 data and frozen before re-overlaying 2025.

No canonical merge, governed-runtime replacement, production action, direction-vote role or database model-output write is authorized by this result.
