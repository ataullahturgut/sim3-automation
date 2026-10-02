# IRIS-H3 V1 — INTRADAY REALIZED-STATE INFORMATION SUPPLEMENT AUTHORITY

**Date:** 2026-10-02  
**Identity:** `IRIS_H3_V1_RESEARCH`  
**Project:** GOLD SHORT-HORIZON GLOBAL XAU  
**Base H3 engine:** frozen NOVA ledger A1 / ARCR-style direction probability  
**New information source:** `XAU_USD_TWELVE_1H_RESEARCH_V1` plus same-provider 1h successor extension  
**Status:** PREREGISTERED / RESEARCH-ONLY / NO RUNTIME PROMOTION

## 1. Research question

Do origin-safe XAU/USD intraday realized-state features add transportable information to the three-trading-day H3 direction problem beyond the existing daily A1/ARCR probability?

This branch is explicitly motivated by the failure of:
- direct daily classifiers,
- ARAC / ARCR,
- novelty gating,
- adaptive conformal filtering,
- forecast-error gating.

IRIS therefore tests genuinely new intraday information rather than another selector over the same daily feature set.

## 2. Timing contract

For a Global-XAU H3 row:
- daily `feature_cutoff_date` is the final date whose features may be used;
- hourly features are anchored at **16:00 America/New_York on feature_cutoff_date**;
- no hourly bar from `forecast_issue_date` or later is allowed;
- H3 target remains the existing Global-XAU `target_r3` / `target_end_date_h3`.

This makes the hourly branch conservative relative to the daily H3 forecast origin.

## 3. Source extension contract

Historical registered source:
- series `XAU_USD_TWELVE_1H_RESEARCH_V1`
- stored Neon coverage: 2022-01-02 .. 2024-12-31.

Successor extension:
- same symbol: `XAU/USD`
- same interval: `1h`
- same timezone: `America/New_York`
- current Twelve Data endpoint queried only for 2024-12 overlap and 2025-01-01 .. 2026-09-30 extension;
- raw vendor values are not written to the repository.

Before model scoring, overlap bridge must pass:
- >= 250 common exact hourly timestamps;
- 1h return Pearson >= 0.99;
- sign agreement >= 0.95;
- return-difference SD <= 0.0015.

If the source bridge fails, IRIS V1 fails closed.

## 4. Intraday realized-state features

### PATH block
- 1h, 3h, 6h, 12h, 24h, 48h log returns
- lag-2 hourly return
- current local-session return.

### VOL block
- 6h, 12h, 24h, 48h realized hourly-return volatility
- 24h upside semivolatility
- 24h downside semivolatility
- downside/upside semivolatility ratio
- 24h jump-concentration ratio
- 24h log-price range.

### SHAPE block
- 24h up-hour fraction
- 6h and 24h log-price slope
- 24h maximum drawdown
- 24h recovery from rolling trough
- 24h close-location within rolling range
- age in hours of the largest positive and negative hourly return.

All features use only bars available by the 16:00 NY anchor.

## 5. Model candidates

The exact A1 probability remains the baseline and is never refit for the baseline comparison.

Candidate H3 bridge models use Logistic L2 only:

1. `HOURLY_ONLY_ALL`
2. `A1_PLUS_PATH`
3. `A1_PLUS_VOL`
4. `A1_PLUS_SHAPE`
5. `A1_PLUS_ALL`

For A1-plus models, `logit(p_A1)` is included as the structural daily signal. The hourly state is therefore tested strictly as incremental information.

No tree, neural-net or metaheuristic family is permitted in V1.

## 6. Walk-forward contract

Hourly history starts in 2022, so this branch has a separate later-history evaluation contract.

- 2022: initial training history only.
- **2023: model/block selection authority.**
- **2024: frozen confirmation.**
- **2025 and 2026: frozen transport/stress**, only if the successor source bridge passes.

At every monthly test block:
- training rows must have `target_end_date_h3 <= test feature cutoff`;
- models refit expanding;
- block identity and model family remain frozen after 2023.

## 7. 2023 selection rule

Same matched rows are used for candidate and baseline.

A candidate is eligible when:
- balanced accuracy >= baseline balanced accuracy;
- accuracy >= baseline accuracy - 0.5 percentage points;
- Brier <= baseline Brier + 0.0025;
- prediction standard deviation >= 0.02.

Among eligible candidates:
1. highest balanced accuracy;
2. highest accuracy;
3. lowest Brier;
4. lowest log loss.

If no candidate is eligible, V1 fails closed.

## 8. 2024 mechanism confirmation

A selected candidate is a mechanism pass only if on frozen 2024:
- balanced accuracy > same-row A1 baseline;
- accuracy >= same-row A1 baseline - 0.5 percentage points;
- Brier <= same-row A1 baseline + 0.0025.

A 2024 failure cannot be repaired using 2025/2026.

## 9. 2025/2026 transport

If source bridge passes, the frozen 2023-selected representation is scored through the available H3 ledger:
- 2025 full year,
- 2026 through the last matured H3 issue already present in the Global-XAU ledger.

2025/2026 outcomes do not alter V1.

## 10. Metrics

- accuracy
- balanced accuracy
- Brier
- log loss
- UP recall
- DOWN recall
- false-call rate
- prediction standard deviation.

Also report:
- matched origin count by year;
- source bridge diagnostics;
- standardized Logistic coefficients from a descriptive fit through 2023 (not used for selection).

## 11. Interpretation

The decisive question is whether intraday information produces a frozen 2024 improvement and whether that mechanism survives 2025/2026.

A 2023-only gain is not evidence of transport.
