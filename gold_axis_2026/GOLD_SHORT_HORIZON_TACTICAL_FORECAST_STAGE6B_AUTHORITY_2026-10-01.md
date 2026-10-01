# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6B Turnover / Tradable-Instrument Feasibility Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Diagnose whether the Stage-6 forecast edge is economically implementable once turnover and realistic execution friction are accounted for.

No forecast model is changed.
No 2025 data are opened.

## 2. Frozen forecast and utility rules

Forecast vector:

`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`

Frozen utility rules:
- U1 RET_ONLY
- U2 MEDIAN_CONSENSUS
- U3 PROB_TILT
- U4 FULL_RISK.

Holding:
- non-overlapping 3-Gold-observation LONG or CASH.

At an assumed round-trip cost `c`:
- entry hurdle remains mechanically `U_k > c`
- realized net trade log return subtracts `c`.

This is not threshold optimization; cost and hurdle are linked by the frozen Stage-6 contract.

## 3. Cost-feasibility grid

Evaluate all frozen utility rules on a deterministic cost grid:

- 0 to 50 basis points round-trip
- increment = **0.25 bp**.

No other grid is permitted.

## 4. Break-even definitions

For each rule report:

### PROFIT_BREAKEVEN_COST
Highest round-trip cost on the grid with:
- CAGR > 0.

### SORTINO_PARITY_COST
Highest cost with:
- Sortino >= 20-bp BUY_AND_HOLD Sortino benchmark.

### STRONG_PARITY_COST
Highest cost with:
- CAGR >= 20-bp BUY_AND_HOLD CAGR
- and max drawdown no worse than BUY_AND_HOLD.

### TACTICAL_GATE_COST
Highest cost at which the full frozen Stage-6 TACTICAL PASS gate is satisfied:
- trades >=20
- CAGR >0
- max drawdown no worse than BUY_AND_HOLD
- Sortino > BUY_AND_HOLD
- >=2 of 3 DEV years positive.

The key feasibility threshold is TACTICAL_GATE_COST.

## 5. Turnover decomposition

For 0, 5, 10, 15, 20, 30, 40 and 50 bp report:
- trades
- exposure
- gross log return before costs
- explicit transaction-cost drag
- net log return
- terminal wealth
- CAGR
- max drawdown
- Sortino.

Also report:
- gross average return per trade
- cost as percentage of gross average trade return where defined.

## 6. Instrument mapping principle

Stage 6B may compare current public execution characteristics for plausible Gold exposure instruments, but it may **not** silently substitute a new target or tradable asset.

Instrument classes to examine:

1. highly liquid U.S.-listed physically backed Gold ETFs
2. COMEX Gold futures / Micro Gold futures
3. Borsa İstanbul Gold-linked exchange-traded products/certificates where a clean mapping exists.

For each instrument class distinguish:
- bid/ask spread
- broker commission/fees
- fund expense ratio or futures roll/carry
- FX conversion cost for a TRY-based investor where relevant
- basis/tracking mismatch versus the project’s BIST MTL/USD/OZ research target.

Do not claim a single universal all-in cost; execution cost is broker/account/time dependent.

## 7. Feasibility classification

### PLAUSIBLE
A documented, repeatable implementation can reasonably operate below the frozen TACTICAL_GATE_COST with acceptable target tracking.

### BORDERLINE
Observed public spread/fee data can sometimes fall below the threshold, but FX, commissions, market impact, roll/carry or target mismatch could erase the margin.

### NOT PLAUSIBLE
Typical unavoidable friction is above the frozen threshold or target mismatch is too large.

This classification is technical feasibility, not an investment recommendation.

## 8. No new tactical rule

Forbidden:
- changing H3
- changing holding period
- changing utility coefficients
- threshold search unrelated to transaction cost
- volatility filters
- stop/take-profit
- 2025 tuning.

## 9. Decision

If no plausible instrument implementation exists below TACTICAL_GATE_COST:
- close current tactical allocation research;
- retain H3 as forecast/reporting engine.

If at least one plausible implementation exists:
- freeze that instrument’s execution contract before any 2025 transport.

## 10. Required outputs

- cost-grid metrics
- break-even table
- turnover-decomposition table
- instrument-feasibility evidence table
- Stage-6B decision
- immutable hashes.
