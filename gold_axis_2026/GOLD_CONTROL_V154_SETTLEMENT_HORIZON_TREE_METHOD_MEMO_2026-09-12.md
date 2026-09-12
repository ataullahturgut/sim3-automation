# Gold Control V1.54 — Settlement-Window Multi-Horizon Direction Method Memo

**Status:** research-only successor; no production authority.  
**Freeze:** scoring contract committed before V1.54 2025/2026 scoring.

## Why change the target clock and horizon?

V1.51–V1.53 repeatedly failed to establish reliable unconditional next-NY17 1D/3D direction. This failure is consistent with recent one-day gold-classification evidence showing only marginal accuracy above chance, while several strands of literature report stronger predictability at longer horizons, in specific sessions, or under regime-specific formulations.

The key methodological change is therefore not post-hoc tuning of the failed one-day model. V1.54 defines a new research endpoint and new forecast horizons before scoring:

- exact XAU/USD spot bar at **13:29 ET**, aligned to the beginning of the official CME Gold (GC) **13:29–13:30 ET settlement window**;
- the spot bar is explicitly a proxy clock, **not** the CME futures settlement price;
- target directions are 5, 10 and 20 subsequent observed settlement-window endpoints;
- 20 sessions is primary, 10 and 5 secondary.

The endpoint is attractive scientifically because the research cache has dense exact 13:29 observations across 2023–2026, whereas historical 16:59 exact coverage is sparse in 2023–2024. It also maps to a market-microstructure-relevant clock rather than an arbitrary end-of-day proxy.

## Literature anchors

1. **CME Group Gold futures settlement procedure.** The active GC contract's daily settlement period is 13:29:00–13:30:00 ET. This provides an authoritative market-clock anchor for the research endpoint, although Gold Control uses XAU/USD spot and does not claim to reconstruct the futures settlement price.
2. **Sadorsky (2021), Journal of Risk and Financial Management, DOI 10.3390/jrfm14050198.** Tree bagging, gradient boosting and random forests substantially outperform logit for gold/silver ETF directional classification at longer horizons. In recursive time-series cross-validation, GLD random-forest accuracy was about 80.6% at 10 days and 86.1% at 20 days in that sample. The paper therefore motivates testing whether our failure is horizon-specific rather than universal.
3. **Kwon, Kang & Yun (2020), Finance Research Letters, DOI 10.1016/j.frl.2019.101306.** Commodity futures exhibit strong short-term weekly momentum, with the past week's return carrying substantial predictive content.
4. **Chen, Yang & Lan (2026), Economics Letters, DOI 10.1016/j.econlet.2026.113147.** Gold drivers are horizon-specific; short-, medium- and long-horizon predictive structures differ, and dynamic model averaging outperforms benchmark models in their monthly application.
5. **Crespo Cuaresma et al. (2024), Journal of Forecasting, DOI 10.1002/for.3152.** Regime-dependent dynamics improve commodity predictive ability, including precious metals, and the best model depends on the prediction objective.
6. **Xu et al. (2020), Resources Policy, DOI 10.1016/j.resourpol.2020.101830.** Intraday predictability in gold is time-of-day specific and stronger on high-volatility/jump days, reinforcing the importance of target-clock choice.
7. **Yadav (2026), SSRN 6323238.** One-day-ahead gold direction from conventional technical-indicator classifiers remains statistically difficult, supporting the decision not to keep forcing the same 1D target after repeated Gold Control failures.

## Frozen feature and model design

V1.54 uses only origin-observable information from the 13:29 endpoint history. Features include return lags, 3/5/10/20/50-session momentum, 5/10/20-session volatility, RSI14, MACD, moving-average ratios, Bollinger z-score, and reconstructed Gold Control FAST/SLOW/Monthly Direction context. No same-period future prices enter any feature.

Four predeclared model families are scored without an automatic selector:

- `RF500` — primary literature-motivated random forest;
- `BAG300` — bagged decision trees;
- `SGB300` — stochastic gradient boosting sensitivity;
- `LOGIT` — linear benchmark.

The validation model is trained only on labels whose target endpoint is no later than 2024-12-31. The 2026 model is refreshed once using labels whose target endpoint is no later than 2025-12-31. No within-period refitting is permitted.

## Evaluation discipline

Raw accuracy can be misleading in a persistent bull or bear regime. Therefore **balanced accuracy is primary**, with ordinary accuracy, Brier score, log loss, MCC, training-majority accuracy and a fixed-grid non-overlapping accuracy sensitivity also reported. A retrospective research-interest gate requires at least 60% ordinary and balanced accuracy in both 2025 and 2026 plus at least +5 percentage points balanced-accuracy gain over the training-majority classifier in both periods.

Passing this gate would justify prospective study, not production promotion. 2025 and 2026 were already researcher-visible in predecessor work, so they cannot serve as fresh blind confirmation. `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, production authority remains false, and production writes remain `NONE`.
