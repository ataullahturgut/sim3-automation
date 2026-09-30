# GOLD MONTHLY — Transition V3 Duration-Aware / Semi-Markov Hazard Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / MARKET-ONLY / STRUCTURALLY DIFFERENT FROM V2

## 1. Scientific question

Can an explicit regime-duration layer reduce false transition calls while preserving useful transition detection?

V1/V2 treated transition mainly as a contemporaneous posterior/anomaly problem. V3 adds a semi-Markov idea:

> the probability that an incumbent regime is ending may depend on how long the current regime spell has already lasted.

V3 is not a full generative HSMM. It is an **explicit-duration hazard overlay** on the frozen HMM/prototype regime engine. The duration model is estimated only from completed historical regime spells available at each origin.

## 2. What V3 does not use

Forbidden:
- ChHHO forecasts;
- ChHHO errors;
- HIGH/MEDIUM/NORMAL forecast-error labels;
- alarm flags;
- routing/model-switch outcomes;
- target-month future information.

V3 is calibrated only on historical market-state/regime data.

## 3. Frozen chronology

Primary schedule:
- **EXPANDING_REFIT + prototype semantic alignment**.

Secondary sensitivity:
- **ANNUAL_ANCHORED**, using the exact rule frozen on expanding calibration.

Calibration:
- **2015-07..2021-12**.

Later validation:
- **2022-01..2024-12**.

Opened inspection/transport:
- **2025-01..2026-08**.

No 2022+ metric may enter rule selection.

## 4. Explicit-duration construction

For each HMM fit available at month t:

1. Filter the fit's training history.
2. Map raw latent hard states to prototype semantic R0/R1/R2.
3. Convert the semantic hard-state path into contiguous regime spells.
4. The final training spell, which is still ongoing/censored at t-1, is excluded from the duration-distribution estimation.
5. For each semantic regime, retain only **completed spell lengths**.

At origin t:
- incumbent regime = semantic hard state at t-1;
- current spell age d = number of consecutive months through t-1 assigned to the incumbent semantic regime, including already observed months in the same annual-anchor year when applicable.

Minimum completed-spell pool:
- 3 spells for duration statistics.
- Otherwise duration evidence is unavailable and only the strong-break branch may fire.

## 5. Duration statistics

For incumbent regime r with completed historical spell lengths D:

### D1 — empirical age percentile
`age_percentile = mean(D <= d)`.

Higher means the current spell is old relative to completed historical spells of the same regime.

### D2 — smoothed exit hazard
At age d:

- risk set = count(D >= d)
- exits = count(D == d)

Jeffreys-smoothed hazard:

`hazard = (exits + 0.5) / (risk_set + 1.0)`.

If risk set is zero, hazard is treated as 1.0 and age_percentile is 1.0.

## 6. Directional evidence

Using semantic posterior probabilities within the same fit:

- incumbent posterior at t-1 and t;
- alternative posterior at t-1 and t;
- incumbent drop;
- alternative growth;
- current incumbent-vs-best-alternative margin.

No emission anomaly, predictive surprise, or raw market jump is allowed to vote.

## 7. Candidate duration-aware rule family

### MODERATE duration-gated branch

Flag if all are true:
- completed-spell pool >= 3;
- age_percentile >= `age_pct_thr`;
- smoothed hazard >= `hazard_thr`;
- current alternative posterior >= `alt_prob_thr`;
- and either:
  - alternative growth >= `alt_growth_thr`; or
  - incumbent posterior drop >= `drop_thr`.

### STRONG break branch

Flag immediately if all are true:
- current alternative posterior >= `strong_alt_prob_thr`;
- current incumbent-vs-alternative margin <= `strong_margin_thr`;
- and either:
  - alternative growth >= `strong_growth_thr`; or
  - incumbent drop >= `strong_drop_thr`.

The strong branch is duration-independent so genuinely early regime breaks are not made impossible by a short spell age.

### Persistence

For the moderate branch:
- candidate can be required for either 1 or 2 consecutive completed origins.

For the strong branch:
- immediate firing is allowed.

Final TRANSITION:
- STRONG branch, or
- persisted MODERATE branch.

## 8. Frozen grid

- age_pct_thr: 0.60, 0.75, 0.85, 0.95
- hazard_thr: 0.15, 0.25, 0.35, 0.45
- alt_prob_thr: 0.20, 0.30, 0.40
- alt_growth_thr: 0.05, 0.10, 0.15
- drop_thr: 0.10, 0.15, 0.20
- moderate_persistence: 1, 2
- strong_alt_prob_thr: 0.50, 0.60, 0.70
- strong_margin_thr: 0.00, 0.10
- strong_growth_thr: 0.15, 0.25
- strong_drop_thr: 0.20, 0.30

## 9. Historical selection objective

Search the frozen grid on **EXPANDING_REFIT 2015-07..2021-12 only**.

Primary eligible set:
- non-zone false-transition rate <= **15%**.

Within the eligible set:
1. maximize reference-event hit rate;
2. maximize precision;
3. maximize transition-zone recall;
4. maximize mean lead before confirmation;
5. minimize total flag rate;
6. deterministic lexicographic parameter tie-break.

Fallback if no candidate reaches <=15% false rate:
1. minimize false-transition rate;
2. maximize event-hit rate;
3. maximize precision;
4. maximize zone recall;
5. deterministic lexicographic tie-break.

No 2022+ result may affect this choice.

## 10. Reference transition zones

Use the same Discovery V1 evaluation definition:

- reference state change occurs between confident R-states;
- intervening BELIRSIZ months bridge the transition;
- zone starts one month after the last confident old-state month;
- zone ends at first confident new-state month inclusive.

This reference is evaluation/calibration truth only; it is never an input to live detection.

## 11. Required reporting

For calibration, validation, opened transport, and full replay report:

- n months;
- transition flags;
- event hits / event-hit rate;
- transition-zone recall;
- non-zone false-transition rate;
- precision;
- mean lead before confirmation;
- duration-pool availability;
- regime spell-age distribution at flags;
- moderate vs strong branch counts.

Mandatory month diagnostics:
- 2024-03..2024-06;
- 2026-04..2026-08.

## 12. Promotion gate

V3 may be considered an operational transition candidate only if **2022-2024 validation** satisfies all:

- event hit rate >= **2/3**;
- non-zone false-transition rate <= **15%**;
- precision at least **5 percentage points above Transition V2** on the same validation period.

If it fails:
- do not retune on 2022-2026;
- do not attach it to ChHHO or alarms;
- record the failure and stop threshold-level transition refinement.

## 13. Governance

This stage does not:
- alter R0/R1/R2 definitions;
- alter Extreme V1;
- inspect ChHHO performance before detector freeze;
- select/weight/suppress alarms;
- correct forecasts;
- route among models.
