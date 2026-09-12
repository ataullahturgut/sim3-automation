# Gold Control V1.59 - Driver-Corrected Meta-Trust Research Memo

Date: 2026-09-12
Status: RESEARCH ONLY / FROZEN BEFORE V1.59 RETROSPECTIVE SCORING
Evidence class: RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC

## Research problem

V1.56 produced the strongest normal-day H20 result to date, but 2025 collapsed to one-direction UP signals while 2026 showed genuine two-direction skill. V1.57 and V1.58 did not improve the combined 2025/2026 result. The next question is therefore not "which larger classifier should replace RTQ?" but "when should the existing H20 RTQ be trusted, and did the prior cross-market driver ontology omit or mislabel important gold opportunity-cost variables?"

## Correction audit

The inherited V1.55 panel labels DEXCHUS as a generic `fx` channel. DEXCHUS is not a broad U.S. dollar factor; it is the Chinese Yuan Renminbi / U.S. Dollar exchange-rate series. V1.59 does not rewrite or hide this historical fact. The exact legacy RTQ is preserved as a benchmark. The driver-corrected parent removes `fx_level` and `fx_logdiff` from the parent feature surface and adds two explicitly named public FRED reconstructions:

- DTWEXBGS: Nominal Broad U.S. Dollar Index.
- DFII10: 10-Year Treasury Inflation-Indexed Security Constant Maturity real yield.

Historical values are downloaded during the research run, hashed, timestamped, and joined strictly from a previous economic source date. Same-date joins, fallback, and interpolation are forbidden. These are 2026-retrieved historical reconstructions and are not relabelled as contemporaneously archived prospective PIT evidence.

## Authority basis

Aye, Gupta, Hammoudeh and Kim (2015), *Forecasting the price of gold using dynamic model averaging*, International Review of Financial Analysis, DOI 10.1016/j.irfa.2015.03.010, report DMS as the best overall approach across their forecast horizons and identify exchange-rate information as particularly strong for gold forecasting. This supports correcting the generic FX ontology and retaining time-varying expert reliability rather than imposing one static winner.

The World Gold Council Gold Return Attribution Model groups gold drivers into economic expansion, risk and uncertainty, opportunity cost through FX, opportunity cost through interest rates, and momentum/trends. Current WGC 2026 commentary continues to attribute meaningful gold variation to risk, U.S. dollar, rates and momentum. This supports explicit broad-dollar and real-rate channels rather than treating a bilateral CNY/USD series as the generic dollar factor.

Giacomini and White (2006), *Tests of Conditional Predictive Ability*, Econometrica, motivates asking whether a forecast is reliable conditional on the current information state rather than only asking which model is unconditionally best. V1.59 implements that idea as a causal meta-trust layer over an already-frozen H20 RTQ parent.

Raftery, Karny and Ettler (2010), *Online Prediction Under Model Uncertainty via Dynamic Model Averaging*, Technometrics, motivates time-varying model reliability. V1.59 is not claimed to be exact state-space DMA; its meta-trust layer is a separate, explicitly named causal classification approximation.

El-Yaniv and Wiener (2010), JMLR selective classification, motivates abstention. In V1.59 a low trust estimate produces NO_SIGNAL. NO_SIGNAL is not NEUTRAL.

## Frozen hypothesis

The parent H20 RTQ remains the primary normal-day candidate. V1.59 creates two parent diagnostics:

1. `LEGACY_RTQ_R126`: exact inherited H20 RTQ benchmark.
2. `DRIVER_RTQ_R126`: same rolling-126 quantile geometry, but the generic legacy `fx_level/fx_logdiff` pair is removed and broad USD + 10Y real-yield features are added.

The meta target is not gold direction. It is whether a matured parent RTQ direction was correct. At each origin, only prior parent predictions whose H20 targets are already mature may train the meta layer.

Frozen meta candidates:

- `META_BASE_LOGIT`: RTQ geometry + market/regime/reversal context, without the corrected dollar/real-yield variables.
- `META_DRIVER_LOGIT`: same model plus corrected broad-dollar and real-yield variables. This is the primary trust candidate.
- `META_DRIVER_HGB`: nonlinear diagnostic only.

The meta layer is veto-only. If `P(parent correct) >= 0.60`, the parent direction survives. Otherwise the output is NO_SIGNAL. V1.59 is forbidden from flipping an RTQ UP into DOWN or vice versa.

## Why reversal is context, not a replacement direction engine

V1.58 showed that reversal probability can contain information while the final trend/reversal-to-direction router can still degrade direction performance. Therefore realized semivariance, Emergency onset/age, role disagreement and BOCPD context enter the trust model as reliability information. They do not receive independent equal votes and they do not obtain override authority in V1.59.

## Evaluation lock

Raw accuracy cannot pass V1.59 by itself. The primary `META_DRIVER_LOGIT` support gate requires, in both visible 2025 validation and visible 2026 test:

- adequate coverage,
- positive MCC,
- both UP and DOWN final signals,
- trust Brier and log loss non-worse than the causal prior-frequency benchmark with at least one strict improvement.

In addition, 2025 final balanced accuracy must strictly exceed the legacy RTQ balanced accuracy; 2026 balanced accuracy must be at least 0.65 and no more than 0.03 below the legacy RTQ balanced accuracy.

These are research-interest gates only. 2025/2026 have already been researcher-visible across prior successors. Passing them cannot establish fresh blind or prospective proof. Promotion still requires future prospective shadow evidence after freeze.

## Governance

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, no production authority, no production writes, no action mapping, and no post-score candidate/threshold/feature changes inside V1.59. Any methodology change after the first real V1.59 score requires a new successor identity.
