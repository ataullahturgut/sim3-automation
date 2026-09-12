# Gold Control V1.52 — Literature-grounded selective specialist routing

**Status:** research successor; no production authority.  
**Freeze:** scoring rules are in `v152_selective_event_router_freeze_v1.json` and were written before this successor run.

## Why V1.51 failed and what the literature says

V1.51 showed that forcing an unconditional 1D/3D direction forecast is unstable across years. This is consistent with gold-forecasting literature: predictor relevance varies materially over time and across horizons, and static winner selection is fragile.

Key methodological anchors:

1. **Aye et al. (2015), International Review of Financial Analysis, DOI 10.1016/j.irfa.2015.03.010.** Dynamic model averaging/selection improves gold forecasts under model and parameter uncertainty; exchange-rate, stress, stock-market and business-cycle factors vary in importance through time.
2. **Baur, Beckmann & Czudaj (2016), International Review of Financial Analysis, DOI 10.1016/j.irfa.2016.10.010.** Gold predictors are time-varying; DMA improves forecasts under model uncertainty.
3. **Risse (2019), International Journal of Forecasting, DOI 10.1016/j.ijforecast.2018.11.008.** Separating short- and long-run frequency components improves gold forecasting and predictor importance is not stable over the evaluation sample.
4. **Three horizon-specific drivers of gold prices with IDMA (Economics Letters, 2026), DOI 10.1016/j.econlet.2026.113147.** Gold drivers are horizon-specific: stock-market spillovers dominate the short term, while rates/FX and geopolitical-risk channels matter more at longer horizons.
5. **Dichtl (2020), Journal of Commodity Markets, DOI 10.1016/j.jcomm.2019.100106.** Gold excess-return predictability is strongly regime-dependent; the paper explicitly motivates regime-dependent and classification-oriented forecasting when directional hit rate is the objective.
6. **Elder, Miao & Ramchander (2012), Journal of Banking & Finance, DOI 10.1016/j.jbankfin.2011.06.007.** U.S. macro surprises have fast and directional effects on gold; strong economic surprises generally pressure gold lower.
7. **Smales & Yang (2015), International Review of Financial Analysis, DOI 10.1016/j.irfa.2015.01.017.** Most macro-announcement reaction in gold futures is completed very quickly; belief dispersion materially amplifies the response.
8. **Awartani, Hussain & Virk (2024), International Review of Financial Analysis, DOI 10.1016/j.irfa.2024.103486.** Gold reacts asymmetrically to FOMC shocks and adjustment can continue beyond five minutes, supporting a dedicated FOMC lane rather than pooling it mechanically with data releases.
9. **El-Yaniv & Wiener (2010), JMLR 11:1605–1641.** Selective classification formalizes the reject option and the risk–coverage trade-off: a system may rationally abstain on hard cases instead of forcing a low-quality classification.
10. **Clark & McCracken (2009), International Economic Review, DOI 10.1111/j.1468-2354.2009.00533.x.** Recursive and rolling forecasts can be combined to mitigate structural-change bias/variance, but combination must be evaluated out of sample rather than presumed helpful.

## V1.52 thesis hypothesis

The system should **not** force one universal UP/DOWN forecast on every day. It should act as a selective mixture of specialists:

- Monthly price experts answer the price-level question.
- Monthly Direction / FAST / SLOW provide strategic/tactical context.
- BOCPD / Emergency / GVZ modify regime and confidence, not direction votes.
- General 1D/3D remains `NO_SIGNAL` until a genuinely reliable lane is proven.
- Macro Event is the short-horizon specialist on scheduled releases.
- Employment and Inflation are pooled into the primary data-release specialist because both the literature and the pre-2025 Gold Control formation sample show stronger, more homogeneous directional reaction than pooled FOMC.
- FOMC remains a distinct diagnostic specialist because monetary-policy shocks have different timing, information effects and asymmetry.
- Market Shock V3 is a post-release confirmation layer only; it may upgrade confidence after it becomes observable but cannot backdate the initial event signal.

This is a **selective-router contribution**, not an equal-vote ensemble.

## Evidence labeling

The V1.52 family/router rule is frozen using literature plus the pre-2025 formation evidence. Because 2025–2026 outcomes were already visible in predecessor work, successor results on those years are retrospective diagnostics, not fresh confirmation. Any promotion claim requires future prospective events after the V1.52 freeze.
