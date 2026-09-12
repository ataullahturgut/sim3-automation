# Gold Control V1.61 — Literature-Inspired Short-Horizon Method Memo

**Evidence class:** `RETROSPECTIVE_SHORT_HORIZON_LITERATURE_DIAGNOSTIC`  
**Production authority:** `FALSE`  
**Targets:** 5 eligible trading-day direction primary; 3-day direction secondary.  
**Relationship to V1.60:** separate short-horizon research line; it does not reopen or repair the closed V1.51–V1.60 H20 sequence.

## Why this experiment

The normal-day H20 sequence showed that adding more generic direction classifiers did not create stable two-direction evidence. V1.61 therefore changes the research question and horizon rather than tuning the failed H20 router.

The primary method is a gold-specific literature adaptation: quantile gradient boosting with realized moments. Bonato, Demirer, Gupta and Pierdzioch (2018, *Resources Policy*, DOI `10.1016/j.resourpol.2018.03.004`) report that realized volatility and skewness can add forecasting information for gold futures returns, especially at intermediate horizons and stressed quantiles, using quantile boosting. Pierdzioch, Risse and Rohloff (2016, *North American Journal of Economics and Finance*, DOI `10.1016/j.najef.2015.10.015`) use quantile boosting for out-of-sample gold-return forecasts under model uncertainty/instability. Aye et al. (2015, *International Review of Financial Analysis*, DOI `10.1016/j.irfa.2015.03.010`) provide the complementary motivation for time-varying cross-market/macroeconomic predictors. Yang et al. (2024, *Resources Policy*, DOI `10.1016/j.resourpol.2023.104430`) motivate taking temporal persistence/instability seriously rather than assuming one static process.

## Frozen translation

V1.61 uses `GradientBoostingRegressor(loss="quantile")` at q25/q50/q75. It is explicitly an **inspired adaptation**, not an exact software replication of the published boosting algorithms. The model is trained on a rolling 252 mature-origin window and refit only at the first eligible origin of each month. A direction is emitted only when the full q25–q75 forecast band is one-sided around zero:

- `q25 > 0` => `UP`
- `q75 < 0` => `DOWN`
- otherwise => `NO_SIGNAL`

The primary candidate adds same-origin realized volatility, downside share, realized skewness, realized kurtosis and jump fraction to technical, session, cross-market, broad-USD, real-yield and role-context inputs. `QB_BASE` is a fixed ablation without realized moments.

## Important data limitation

The governed research store does not contain an entitled official COMEX GC continuous/settlement history for this freeze. V1.61 therefore uses the XAU/USD 13:29 America/New_York research endpoint and **must not be described as a COMEX futures replication**. Acquiring a properly licensed futures history is a separate future data-enrichment step if this spot adaptation does not provide robust evidence.

## No-hindsight lock

The method, horizons, features, quantiles, tree settings, rolling window, monthly refit rule and support gate were frozen before V1.61 retrospective scoring. 2025 and 2026 are researcher-visible and are not fresh blind evidence. No post-score threshold, feature, model, horizon or hyperparameter repair is permitted inside V1.61.
