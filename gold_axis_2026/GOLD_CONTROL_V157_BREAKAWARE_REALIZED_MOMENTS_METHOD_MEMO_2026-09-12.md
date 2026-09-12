# Gold Control V1.57 — Break-aware realized-moments quantile research

Date: 2026-09-12  
Status: **FROZEN BEFORE V1.57 2025/2026 SCORING**  
Evidence class: **RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC**

## Research question

Can same-origin intraday realized moments and an origin-observable structural-break context improve medium-horizon selective quantile forecasts of gold returns, while preserving strict target maturity and avoiding result-dependent tuning?

## Authority basis

1. **Bonato, Demirer, Gupta & Pierdzioch (2018), Resource Policy, DOI 10.1016/j.resourpol.2018.03.004.** Their gold-futures experiment uses quantile boosting and reports predictive content in realized volatility/skewness, particularly at intermediate horizons and distressed-market states. V1.57 therefore makes H10 primary, with H5/H20 secondary, and derives realized moments from the already available intraday XAU research cache.
2. **Pesaran & Timmermann (2004), International Journal of Forecasting, DOI 10.1016/S0169-2070(03)00068-2.** Ignoring structural breaks can be costly for directional forecasts; conditioning estimation on a recent break can improve on unconditional rolling/expanding windows when the break is material. V1.57 therefore tests a break-conditioned training rule.
3. **BOCPD_RETURN_SUCCESSOR_V1.** The project’s governed BOCPD successor is a regime-break context engine and explicitly has no direction-vote authority. V1.57 reuses it only as origin-observable context/gating; current-month and future-month BOCPD states are prohibited.
4. **Pesaran & Timmermann (1992), JBES, DOI 10.1080/07350015.1992.10509922.** Directional predictability is reported with the PT diagnostic rather than raw hit rate alone.
5. **El-Yaniv & Wiener (2010), JMLR 11:1605–1641.** Selective classification supports a reject/NO_SIGNAL option through the risk–coverage trade-off. V1.57 retains the frozen IQR-excludes-zero rule.
6. **White (2000), Econometrica, DOI 10.1111/1468-0262.00152; Hansen (2005), JBES, DOI 10.1198/073500105000000063.** Repeated specification search can create false discoveries. V1.57 therefore freezes a very small candidate family and reports a moving-block White Reality Check diagnostic for its H10 challengers. This does **not** erase the broader V1.51–V1.57 data-snooping history.

## Frozen information clock

The research origin is the exact XAU/USD 13:29 America/New_York cache bar. Realized moments use only same-day 03:30–13:29 ET one-minute close-to-close returns, with gaps above 90 seconds excluded and at least 500 valid returns required. No interpolation or fallback is allowed.

The daily baseline panel remains the V1.55 FULL surface: gold history/technical/session features, FAST/SLOW/MONTHLY_DIRECTION_3M, PIT rates/FX, and strictly previous-source-date equity/precious-metal reconstructions.

BOCPD monthly state becomes usable only on the first calendar day after the completed month. It can gate training but cannot vote UP/DOWN.

## Realized-moment surface

- realized volatility: sqrt(sum r_i^2)
- negative and positive realized semivariance
- downside variance share
- realized skewness
- realized kurtosis
- bipower-variation-based jump fraction
- maximum absolute one-minute return

Rows failing the frozen intraday coverage rule are unavailable for moment-dependent candidates; they are not silently imputed into the realized-moment channel.

## Candidate family

### PRIMARY_H10

- `H10_BASE_RTQ_R126`: V1.56-style FULL quantile benchmark, rolling 126 mature observations.
- `H10_MOM_R126`: FULL + realized moments + BOCPD context, rolling 126.
- `H10_MOM_BREAK`: same feature surface, but if the latest origin-observable BOCPD reset has at least 63 mature post-break observations, training uses only post-break mature data (capped at 126); otherwise it falls back to rolling 126.

### Secondary diagnostics

- `H5_MOM_BREAK`
- `H20_BASE_RTQ_R126`
- `H20_MOM_BREAK`

H1 is not re-promoted as a primary target; V1.56 already documented insufficient robust H1 evidence.

## Quantile and selective rule

Each candidate estimates q25/q50/q75 using frozen shallow HistGradientBoosting quantile regressors. Quantiles are sorted per origin to enforce q25 <= q50 <= q75.

- q25 > 0 → UP
- q75 < 0 → DOWN
- otherwise → NO_SIGNAL

NO_SIGNAL is abstention, not a neutral direction.

## Evaluation

The primary H10 assessment reports selective accuracy, balanced accuracy, MCC, coverage, UP/DOWN counts, PT directional diagnostic, q25/q50/q75 pinball loss and average pinball loss. Because H10 targets overlap, candidate-vs-baseline pinball loss differences use a Bartlett HAC lag of h-1 with an HLN-adjusted Diebold–Mariano diagnostic.

A V1.57 H10 challenger receives `two_period_multi_criteria_support=true` only when **both 2025 and 2026** satisfy all frozen conditions: coverage >=20%, selective balanced accuracy >50%, MCC >0, at least one UP and one DOWN signal, and lower aligned mean pinball loss than `H10_BASE_RTQ_R126`.

A moving-block White Reality Check with 2,000 frozen-seed replications and block length 10 is reported for the two H10 challengers against the baseline. It is a local diagnostic only.

## Thesis-governance interpretation

2025 and 2026 have already been exposed during predecessor research. Therefore V1.57 is **not** a fresh blind OOS test and cannot by itself authorize promotion. A positive V1.57 result would justify a separately frozen prospective shadow successor on future unseen origins; a negative result is retained as a thesis result and must not be repaired by changing thresholds, horizons or candidates after scoring.

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, no action mapping, no production writes, and no production authority remain binding.
