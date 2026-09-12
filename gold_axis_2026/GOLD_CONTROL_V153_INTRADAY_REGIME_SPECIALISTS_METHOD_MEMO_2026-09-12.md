# Gold Control V1.53 — Intraday Regime Specialists Method Memo

**Status:** research-only successor; no production authority.  
**Freeze:** the scoring contract was committed before V1.53 2025/2026 successor scoring.

## Research motivation

The V1.51/V1.52 evidence indicates that unconditional close-to-close 1D/3D direction is unstable, while event-conditioned signals are substantially stronger. The next thesis hypothesis is therefore not another universal classifier but a set of selective specialists that exploit intraday state information already present in the Gold Control source stack.

### Literature anchors

1. Liu, Lu, Li & Wang (2023), *Journal of Empirical Finance*, DOI 10.1016/j.jempfin.2023.03.001: positive and negative realized semivariance contain information about commodity time-series momentum reversals. Their tuned time-series momentum uses a 20-day momentum signal, five-day realized semivariance, rolling 250-day 80th-percentile reference points, and asymmetric reverse/abstain decisions.
2. Bonato, Demirer, Gupta & Pierdzioch (2018), *Resources Policy*, DOI 10.1016/j.resourpol.2018.03.004: realized volatility/skewness have predictive value for gold futures returns, especially at intermediate horizons and in distressed states.
3. Demirer et al. (2017), *Economics Letters*, DOI 10.1016/j.econlet.2016.11.027: short-term negative semivariance is persistently important in gold, with positive semivariance becoming more important in rising-gold regimes.
4. Crespo Cuaresma et al. (2024), *Journal of Forecasting*, DOI 10.1002/for.3152: regime-dependent threshold models improve commodity predictive ability, including precious metals, and the best regime model depends on the prediction objective.
5. Tian & Anderson (2014), *International Journal of Forecasting*, DOI 10.1016/j.ijforecast.2013.06.003, and Pesaran et al. (2013), *Journal of Econometrics*, DOI 10.1016/j.jeconom.2013.04.002: structural-break uncertainty motivates recency/robust weighting rather than one static long-history estimator.
6. Franc, Prusa & Voracek (2023), *JMLR* 24:11: reject-option classification formalizes abstention as an optimal response to uncertainty under selective-risk or coverage constraints.
7. Hauptfleisch, Putnins & Lucey (2016), *Journal of Futures Markets*, DOI 10.1002/fut.21775: gold price discovery varies materially across London/New York trading hours and macro-announcement periods.
8. Intraday return-predictability work on gold/commodity ETFs documents session-specific continuation/reversal patterns and stronger predictability in high-volatility/jump states, motivating a separate Europe-session diagnostic rather than a universal daily vote.

## Frozen V1.53 specialists

### RSV_TTSM_S2_1D — primary literature replication/adaptation

Gold Control adapts the Liu et al. TTSM-S2 rule as a direction-only specialist. It never maps to a trade or position size.

- Base momentum: sign of exact-NY17 20-origin cumulative log return.
- State variables: positive and negative realized semivariance from 5-minute returns, accumulated over five trade days.
- Reference state: rolling 250-trade-day 80th percentiles for RS+ and RS-.
- Both RS+ and RS- high: `NO_SIGNAL`.
- Both low: keep momentum direction.
- RS- high only: reverse an UP momentum to DOWN; DOWN momentum abstains.
- RS+ high only: reverse a DOWN momentum to UP; UP momentum abstains.
- Missing or immature state: `NO_SIGNAL`.

### MODERATE_DOWNSHOCK_REVERSAL_1D — formation-derived specialist

A pre-2025 formation-only diagnostic found that moderate negative exact-NY17 returns had a stronger next-origin reversal tendency than the unconditional daily classifier. To avoid a fixed hindsight threshold, V1.53 defines the regime using trailing 126-origin absolute-return quantiles computed from prior observations only. A negative return between the trailing median and 75th percentile predicts UP; all other states abstain.

### EUROPE_SESSION_CONTINUATION_1D — diagnostic only

Using only information observable before NY17, the 03:29–07:59 ET return sign is tested as a next-origin direction diagnostic. This is motivated by the time-zone segmentation and intraday price-discovery literature. It has no production authority and cannot override the primary specialist.

## Evidence discipline

2025 and 2026 are retrospective successor diagnostics because predecessor work already exposed those periods. The V1.53 rules may not be changed after scoring to improve those years. Any promotion claim requires a newly frozen prospective shadow period. `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, and production writes remain `NONE`.
