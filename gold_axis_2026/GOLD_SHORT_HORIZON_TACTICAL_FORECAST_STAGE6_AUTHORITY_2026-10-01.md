# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6 Tactical Allocation / Utility Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Translate the frozen continuous H3 forecast vector into a simple, auditable long-or-cash tactical allocation rule.

Frozen input:

`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`

No new forecast model is fit.

## 2. Research price / instrument convention

Research execution proxy:
- governed Borsa İstanbul Gold MTL / USD / OZ series.

This is a **research price proxy**, not a claim that the user can execute at the fixing with zero slippage.

Therefore Stage 6 is an economic research simulation, not a broker-ready implementation.

## 3. Decision timing

At origin t:
- P[t] and all frozen H3 forecast outputs are known;
- decision is made immediately after the origin observation is available;
- a LONG action receives the subsequent Gold returns for exactly the next three Gold observations.

No future price enters the action decision.

## 4. Position mechanics

Allowed positions:
- LONG = 100% notional Gold exposure
- CASH = 0% Gold exposure.

Forbidden:
- short
- leverage
- pyramiding
- overlapping multiple positions.

If LONG at origin t:
- hold for exactly 3 Gold return intervals;
- ignore intermediate new signals;
- exit after the third interval;
- next action may be taken at that exit origin.

If CASH at origin t:
- reassess at the next Gold origin.

This makes H3 forecast and economic holding horizon consistent.

## 5. Transaction-cost convention

Primary selection cost:
- **20 basis points round-trip** per completed LONG trade.

Sensitivity only:
- 0 bp
- 50 bp.

The cost is an instrument-agnostic research allowance for spread/slippage/fees.

Only 20 bp can select a rule.

## 6. Frozen utility ingredients

Origin-known volatility scale:

`hvol = sigma20 * sqrt(3)`

Downside magnitude:

`D = max(0, -Q10_3)`

Candidate utility scores:

### U1 — RET_ONLY
`U1 = RET_HAT3`

### U2 — MEDIAN_CONSENSUS
`U2 = 0.5 * RET_HAT3 + 0.5 * Q50_3`

### U3 — PROB_TILT
`U3 = 0.5 * RET_HAT3 + 0.5 * Q50_3 + 0.5 * (P_UP3 - 0.5) * hvol`

### U4 — FULL_RISK
`U4 = 0.5 * RET_HAT3 + 0.5 * Q50_3 + 0.5 * (P_UP3 - 0.5) * hvol - 0.5 * D`

No coefficient search is allowed.

Q90 remains displayed in the forecast object but is not rewarded in the utility score; upside-tail optimism is intentionally not used to justify entry.

## 7. Entry rule

Primary 20 bp run:

LONG iff
`U_k > 0.0020`

otherwise CASH.

The hurdle equals the preregistered round-trip research cost.

No additional probability threshold.
No Stage-5 categorical threshold reuse.

Sensitivity:
- 0 bp: hurdle 0
- 50 bp: hurdle 0.0050

Sensitivity cannot select the champion.

## 8. DEV authority

Selection:
- 2022-2024 only.

2025:
- fully frozen.

2026:
- not selection authority.

## 9. Benchmarks

### CASH
- wealth constant at 1.0.

### BUY_AND_HOLD
- long Gold from first DEV origin through last DEV observation;
- one 20 bp round-trip cost for economic comparison.

### ALWAYS_LONG_H3_ROLL
- continuously hold non-overlapping 3-observation Gold positions;
- pay 20 bp round-trip every 3-observation roll.

This separates:
- market drift
- repeated H3 trading cost
- forecast-based timing value.

## 10. Economic metrics

Primary:
- CAGR / annualized return using actual calendar span
- maximum drawdown.

Co-primary:
- Sortino ratio.

Supporting:
- Sharpe ratio
- terminal wealth
- total net return
- number of trades
- exposure percentage
- win rate per completed trade
- average trade return
- median trade return
- worst trade
- turnover / entries
- positive calendar-year return count.

Risk-free rate:
- 0 for research comparison.

## 11. Tactical PASS gate

At 20 bp primary cost, a candidate is **TACTICAL PASS** only if:

1. completed trades >= **20**
2. CAGR > 0
3. maximum drawdown is no worse than BUY_AND_HOLD
4. Sortino > BUY_AND_HOLD Sortino
5. at least **2 of 3 DEV calendar years** have positive strategy return.

### Strong economic pass

Report separately if:
- CAGR >= BUY_AND_HOLD CAGR
- and maximum drawdown <= BUY_AND_HOLD drawdown.

This is not required for ordinary tactical PASS.

## 12. Champion selection

Among TACTICAL PASS candidates:

1. highest CAGR
2. if CAGR difference <= 0.50 percentage points, highest Sortino
3. if still effectively tied, choose simpler score:
   U1 -> U2 -> U3 -> U4.

If no candidate passes:
- do not force an allocation strategy;
- preserve forecast engine only.

## 13. Robustness / sensitivity

For selected candidate, report:
- 0 bp
- 20 bp
- 50 bp.

Also report:
- 2022
- 2023
- 2024
- LOW / MID / HIGH volatility entry counts and trade outcomes.

No cost sensitivity may be used to choose a different rule.

## 14. No threshold optimization

Forbidden:
- scanning entry hurdle
- scanning coefficients
- scanning holding periods
- scanning stop/take-profit
- using 2025 to improve the rule.

H3 = 3 observations remains fixed.

## 15. 2025 opening rule

Only if one candidate earns TACTICAL PASS:
- freeze champion and all execution assumptions;
- then Stage 7 may run 2025 transport with no retuning.

If none passes:
- 2025 remains unopened for tactical selection.

## 16. Required outputs

- daily strategy equity table
- trade ledger
- candidate metric table
- yearly metric table
- cost-sensitivity table
- volatility trade summary
- benchmark table
- champion decision
- immutable hashes.
