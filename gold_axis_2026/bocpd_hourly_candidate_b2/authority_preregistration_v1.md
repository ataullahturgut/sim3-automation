# BOCPD HOURLY CANDIDATE B2 — AUTHORITY-LED PREREGISTRATION V1

Date: 2026-09-16

Identity to be frozen after pre-2025 calibration: `BOCPD_HOURLY_POSTERIOR_MASS_CANDIDATE_B2_V1_RESEARCH`

Status: `RESEARCH_ONLY / NOT_GOVERNED_RUNTIME / 2025_VISIBLE_REUSED_CHALLENGE`

## 1. Project-authority constraints

This successor is subordinate to `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` v1.58.

Binding consequences:

- no change to the 12 governed runtime identities;
- no direction vote;
- no production mapping or database model-output write;
- no challenge-result tuning;
- no event-conditioned signal generation;
- engine-first full-timeline replay;
- output availability = completion time of latest required hourly bar;
- 2025 is already visible from Candidate B and therefore is not a pristine holdout for B2; any B2 2025 result is retrospective reused-challenge evidence only;
- any promotion would require separate manifest change control and prospective shadow evidence.

## 2. External authority findings incorporated

1. Adams & MacKay BOCPD defines the online object as the posterior distribution over run length, not merely a binary reset flag.
2. With a constant hazard, isolated `P(r_t=0)` is not a useful data-driven operational score; evidence of a new regime is better read from posterior mass moving from mature to short run lengths.
3. Recent robust BOCPD literature warns that standard BOCPD can generate spurious changepoints under outliers/model misspecification. B2 does not claim to reproduce published beta-divergence robust BOCPD; instead it reduces raw-MAP-reset sensitivity and retains a heavy-tailed Student-t posterior predictive.
4. Sequential changepoint literature treats false-alarm burden / average run length and detection delay as a coupled design problem. B2 therefore calibrates an alarm-onset threshold on pre-2025 data without using 2025 event labels.
5. High-frequency finance and precious-metals literature documents strong intraday periodicity in volatility. B2 retains hour-of-day standardization fit only on pre-2025 data.

## 3. Data chronology

- 2023: fit hour-of-day location/scale and NIG prior.
- 2024: select constant hazard by prequential log predictive evidence; then calibrate posterior-mass alarm threshold using only 2024 engine output and an ARL-style signal-budget rule.
- 2025: only after the complete B2 specification is frozen, run full engine-first retrospective replay. Because 2025 has already been seen during Candidate B work, label it `VISIBLE_REUSED_CHALLENGE`, not independent validation.

No 2025 volatility-event date, return, label, lead time, Candidate-B event overlay, or Candidate-B 2025 reset frequency may enter B2 parameter selection.

## 4. Observation process

Source: `XAU_USD_TWELVE_1H_RESEARCH_V1` for 2023-2024 and same-provider 1h historical retrieval for 2025 replay.

Clock rules are inherited from Candidate B R2:

- America/New_York XAU weekly session gate;
- exact one-hour elapsed returns only;
- raw observation `r_t = ln(P_t/P_{t-1})`;
- bar timestamp means bar start;
- signal availability = bar start + 1 hour;
- no weekend reopen / maintenance-gap return is inserted into the one-hour process.

## 5. Intraday seasonality adjustment

Fit on 2023 only, separately by eligible New York bar-start hour:

- location = sample mean;
- scale = sample standard deviation with ddof=1;
- minimum support per hour = 150;
- adjusted observation `x_t = (r_t - mu_hour) / sigma_hour`.

Parameters are frozen after 2023.

## 6. BOCPD observation model

- Adams-MacKay run-length recursion;
- Gaussian unknown mean and variance within a regime;
- Normal-Inverse-Gamma conjugate prior;
- Student-t posterior predictive;
- prior fitted from 2023 hour-adjusted returns;
- `kappa0=1`, `alpha0=2`, `beta0=(alpha0-1)*sample_variance`.

This is not labelled beta-divergence robust BOCPD.

## 7. Hazard selection — pre-2025 only

Candidate expected regime lengths in trading days: `[20, 40, 60, 120]`.

With 22 eligible one-hour returns per full session, expected run observations: `[440, 880, 1320, 2640]`.

Selection metric: highest 2024 prequential log predictive evidence.

## 8. New authority-led detection score

Semantic short-run window is fixed before calibration:

`K = 22 eligible hourly returns`, approximately one full XAU trading day.

At each eligible observation after the BOCPD update:

`short_run_mass_t = sum_{r=0}^{K} P(r_t=r | x_1:t)`.

This is the primary B2 change-evidence score.

An alarm onset at threshold `q` requires:

1. `short_run_mass_t >= q`;
2. previous `short_run_mass_{t-1} < q` (up-crossing; continued high score is the same episode, not a new alarm);
3. previous MAP run length `>= K` (the preceding regime must have matured at least one trading day).

No sign filter is used.

## 9. Threshold calibration rule — frozen before running it

Fixed candidate threshold grid:

`q in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.975, 0.99]`.

For each q on the full 2024 eligible timeline, compute alarm-onset count and empirical onset spacing:

`ARL_PROXY(q) = eligible_2024_observations / alarm_onset_count(q)`.

Important: 2024 contains unknown real regime changes, so this is an empirical alarm-spacing proxy, not a formal null `ARL0` estimate.

After hazard selection, define target spacing equal to the selected expected run observations `lambda_selected`.

Threshold selection rule:

- choose the smallest q whose `ARL_PROXY(q) >= lambda_selected`;
- this maximizes sensitivity among grid values that satisfy the predeclared signal-budget constraint;
- if no q satisfies it, calibration fails closed and B2 is not run on 2025;
- if q yields zero onsets, its spacing is treated as infinity but it can only be selected if all lower thresholds fail the target; zero-onset selection must be explicitly flagged.

The threshold grid, K, alarm-onset rule and spacing criterion may not be altered after seeing the calibration output in order to improve 2025.

## 10. 2025 evaluation after freeze

Only after writing a frozen contract containing the selected hazard and q may 2025 be replayed.

Required outputs:

- every eligible hourly score;
- every B2 alarm onset and episode continuation;
- unique alarm dates and monthly counts;
- full signal universe before volatility overlay;
- 19-event overlay only after engine output freeze;
- signal-to-next-event reverse accounting;
- strict separation of `STRICT_PRE_EVENT_WINDOW`, `INTRADAY_PRE_EVENT_CLOSE`, and same/post-event confirmation;
- no precision/recall/false-alarm claim unless a warning-validity horizon was separately preregistered (none is preregistered here).

## 11. Promotion rule

B2 can at most be classified as a research regime-context challenger from retrospective replay. Since 2025 is now visible, no 2025 result can establish prospective validity. Runtime promotion is `NOT_PROVEN` until a separately frozen prospective shadow period matures.
