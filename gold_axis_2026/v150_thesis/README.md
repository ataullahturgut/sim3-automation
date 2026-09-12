# Gold Control V1.50 — Role-Hierarchical Thesis Research Lane

## Scope

This lane is a development-only successor study. It does **not** replace the canonical V1.49 system, does not authorize production forecasts, and does not reactivate `AUTO_SELECTOR` or `AUTO_ENSEMBLE`.

The central hypothesis is that Gold Control contains several heterogeneous information channels that should not be forced into a homogeneous voting pool. Monthly level forecasting, strategic direction, tactical trend, macro-event reaction, market-shock confirmation, structural-break context, emergency/reversal context, and volatility-risk context are separate statistical tasks with different clocks and loss functions.

## Immutable outer lock

The V1.49 2025-2026 outer outcomes are already researcher-visible. V1.50 therefore forbids those labels for feature design, model selection, threshold selection, calibration, or performance scoring. The general-direction development runner reads only exact NY17 origins from 2023-01-01 through 2024-12-31. Candidate selection ends at 2024-06-30; 2024-07-01 through 2024-12-31 is a one-pass development lock. A result can nominate a prospective shadow candidate only. It cannot prove promotion.

## Role hierarchy

1. `VW_MIDAS_MSVR_SUCCESSOR_V1`: monthly H=1 price-level expert; unchanged by V1.50.
2. `MONTHLY_DIRECTION_3M`: strategic direction prior.
3. `FAST` / `SLOW`: tactical and slow trend-state context. Frozen R4 formulas are reconstructed from the exact NY17 gold history.
4. `BOCPD_RETURN_SUCCESSOR_V1`: break/regime context. It is not silently added until an exact daily-origin PIT state artifact is proven.
5. `MACRO_EVENT`: sparse event-time direction specialist.
6. `MARKET_SHOCK_CHALLENGER_V3`: event confirmation/context only; never an unconditional daily vote.
7. `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL`: displacement and reversal context. They remain outside this development model unless a contemporaneous immutable monthly reference is available at each development origin.
8. `GVZ_RISK`: risk/confidence context. It is not backfilled into pre-2025 development because the current persistent direct series does not prove that historical NY17 availability clock.

## General 1D / 3D redesign

V1.49 grouped rates/FX and equities/volatility into complete-case blocks. This can erase a long-history information channel when one late-starting series is missing. V1.50 therefore evaluates role-preserving blocks separately and uses train-only missing-data handling rather than deleting an entire block.

The fixed candidate information sets are:

- `G0`: gold own-history returns, momentum, realized volatility.
- `G1`: frozen FAST/SLOW/Monthly-Direction role context reconstructed from gold only.
- `G2`: rates/FX using `DGS10_ALFRED_PIT_ME`, `DFF_ALFRED_PIT_ME`, `DEXCHUS_ALFRED_PIT_ME` with `available_as_of <= origin`.
- `G3`: one-economic-date-lagged NASDAQ100/S&P500/DJIA, explicitly labelled historical source-date reconstruction rather than proven historical PIT.
- `G4`: one-economic-date-lagged XAG/XPT/XPD, explicitly labelled research reconstruction rather than proven historical PIT.

The frozen model family is deliberately small: ridge logistic regression at two regularization strengths and depth-2 histogram gradient boosting. Every prediction is expanding-window and uses only labels matured by that origin. No random split is allowed.

A `NO_SIGNAL` state is allowed. Its confidence threshold is chosen only on the pre-lock selection window from a frozen threshold grid, subject to minimum coverage and sample-size constraints, then applied once to the development lock.

## Event-time redesign

Macro events are evaluated on their own clock rather than diluted into every daily origin. Gold-oriented Macro Event score sign is evaluated at:

- first 5 completed minutes after release (`R5`),
- first 15 completed minutes (`R15`),
- first 30 completed minutes (`R30`),
- release to the next governed NY17 observation.

Existing frozen strong-state metadata may be reported, but no new score threshold is fitted from V1.50 event outcomes. Initial reaction, continuation, and reversal are separate targets.

## Methodological basis

The design follows evidence that gold predictors are time-varying and horizon-specific rather than stable universal coefficients. Aye et al. (2015, *International Review of Financial Analysis*, DOI 10.1016/j.irfa.2015.03.010) found Dynamic Model Averaging/Selection useful for gold and highlighted exchange-rate and financial-stress channels. The 2026 Iterated Dynamic Model Averaging study on gold identifies horizon-specific roles for the Nasdaq index, Federal Funds Rate, USD/CNY, and geopolitical risk, supporting separate information blocks rather than one static predictor pool.

For event time, Smales and Yang (2015, *International Review of Financial Analysis*, DOI 10.1016/j.irfa.2015.01.017) show that most gold-futures macro-announcement adjustment occurs rapidly and that belief dispersion matters. Sobti, Sehgal and Ilango (2021, DOI 10.1016/j.irfa.2021.101893) show that macro-news effects on gold price discovery are asymmetric and state-dependent. These findings support a separate event specialist and argue against treating an initial release reaction as automatic 1D/3D continuation.

Market Shock V3 remains grounded in Lee-Mykland extreme-value jump detection, causal MedRV-type robust local scale, EVT fast-move detection, and robust intraday periodicity. Its role in V1.50 is confirmation/context, not unconditional direction authority.

## Required interpretation

A strong development-lock result is evidence that a candidate is worth freezing for prospective shadow observation. It is **not** proof of real-time predictive superiority. Genuine performance evidence after V1.49 requires forecasts frozen before future outcomes mature.
