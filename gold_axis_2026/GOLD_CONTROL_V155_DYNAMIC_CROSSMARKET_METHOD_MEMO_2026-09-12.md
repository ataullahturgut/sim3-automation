# Gold Control V1.55 — Dynamic Cross-Market Direction Method Memo

**Status:** research-only successor; no production authority.  
**Contract:** `v155_thesis/contracts/v155_dynamic_crossmarket_direction_freeze_v1.json`  
**Freeze:** candidate set, horizons, dynamic-weight rule and selective threshold were fixed before V1.55 2025/2026 scoring.

## Research problem

V1.51–V1.54 show that a static universal gold-direction classifier is unstable across the visible 2025→2026 regime change. The objective of V1.55 is not to fit that already-seen break after the fact. It is to test a predeclared adaptive architecture in which model coefficients, training emphasis and model weights are updated only from information whose target has matured by each forecast origin.

## Literature anchors

1. **Aye, Gupta, Hammoudeh & Kim (2015), International Review of Financial Analysis, DOI 10.1016/j.irfa.2015.03.010.** Dynamic model averaging (DMA) and dynamic model selection (DMS) outperform static alternatives for gold-price forecasting in their experiment; DMS is best overall across their forecast horizons. Predictor relevance varies over time, with exchange-rate and stress factors particularly persistent.
2. **Baur, Beckmann & Czudaj (2016), International Review of Financial Analysis, DOI 10.1016/j.irfa.2016.10.010.** Gold predictor relevance changes materially over time; DMA addresses simultaneous model and parameter uncertainty and favors parsimonious models.
3. **Three horizon-specific drivers of gold prices with Iterated Dynamic Model Averaging (Economics Letters, 2026), DOI 10.1016/j.econlet.2026.113147.** IDMA/DMA outperform benchmarks in that study and identify horizon-specific drivers: stock-market spillovers in the short term and interest-rate factors at medium/long horizons.
4. **Forecasting gold price changes: Rolling and recursive neural network models (2008).** Rolling adaptation reports an average sign prediction around 60.68% in that study, supporting explicit adaptation rather than a permanently fixed training sample.
5. **Clark & McCracken (2009), International Economic Review, DOI 10.1111/j.1468-2354.2009.00533.x.** Rolling and recursive forecast combinations can mitigate structural-change bias/variance; this motivates evaluating recency-weighted and rolling learners rather than assuming one estimation window is universally optimal.

These papers motivate the *class of methods*. They do not prove that the V1.55 implementation will work on Gold Control data.

## Frozen architecture

### Targets

- `TACTICAL_H1`: one exact 13:29 ET XAU/USD endpoint ahead.
- `STRATEGIC_H20`: twenty exact 13:29 ET endpoints ahead.

The 13:29 ET spot bar is a research proxy aligned to the start of the CME Gold settlement window. It is **not** claimed to be the CME futures settlement price.

### Feature layers

`BASE` contains only Gold Control internal information observable at the origin: gold return/momentum/volatility/technical features, same-day gold session returns, and reconstructed role context (`FAST`, `SLOW`, `MONTHLY_DIRECTION_3M`).

`FULL` adds:

- PIT/reconstructed rates and FX: `DGS10_ALFRED_PIT_ME`, `DFF_ALFRED_PIT_ME`, `DEXCHUS_ALFRED_PIT_ME`;
- strictly previous-source-date Nasdaq/S&P500/DJIA returns;
- strictly previous-source-date XAG/XPT/XPD returns.

Same-date external closes are forbidden. Equity and precious-metal historical series are explicitly labeled economic-date reconstructions, not prospective archived-PIT evidence.

### Base learners

The frozen candidate set is:

- BASE rolling-126 logistic regression;
- FULL rolling-126 logistic regression;
- FULL exponentially weighted logistic regression, half-life 63;
- FULL rolling-126 histogram gradient boosting;
- FULL rolling-252 one-hidden-layer MLP(16).

No new candidate may be added after V1.55 scoring.

### Causal dynamic layer

For every origin `t`, a candidate's historical loss may enter DMA/DMS only if that historical forecast's target is already mature by `t`. The primary dynamic rule is `DMA_LOGLOSS63`, using the latest 63 mature predictions per member and weights proportional to

`exp(-5 × mean prior-only log loss)`.

`DMS_LOGLOSS63` is a sensitivity analysis selecting the member with the lowest prior-only 63-observation mean log loss.

`DMA_SELECT60` implements the reject option:

- `p >= 0.60` → UP;
- `p <= 0.40` → DOWN;
- otherwise → `NO_SIGNAL`.

The selective threshold is frozen before scoring.

## Evaluation

Primary metric: balanced accuracy. Secondary metrics: raw accuracy, Brier score, log loss, MCC, historical-frequency benchmark and selective risk/coverage.

Research-interest gates require performance in **both** 2025 validation and the available 2026 retrospective test:

- H1 DMA: accuracy and balanced accuracy ≥ 0.58 in each period;
- H20 DMA: accuracy and balanced accuracy ≥ 0.60 in each period;
- selective DMA: selective accuracy ≥ 0.65 and coverage ≥ 0.20 in each period.

Failure of these gates is recorded as `NOT_PROVEN`; thresholds or candidate sets may not be changed within V1.55 after reading the result.

## Evidence status

2025 and 2026 are already researcher-visible from predecessor work. Therefore V1.55 is a **retrospective successor diagnostic**, not fresh blind confirmation. Any thesis promotion claim ultimately requires a future prospective shadow sample frozen before those outcomes occur.

## Governance

- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- production authority = false
- production writes = none
- no trading/action mapping
- no post-score threshold or candidate edits
