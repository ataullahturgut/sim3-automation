# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6 Tactical Allocation / Utility Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / NO_TACTICAL_PASS**  
**Workflow:** Gold Short Horizon Stage6 Tactical Utility  
**Run:** **36892963306**  
**Artifact:** **11178115214**  
**Artifact digest:** `sha256:3f1b8d5a458521c1c64cda9f3a6df0a30adcad88d9140a966998ca3f14713b5c`  
**Authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

No preregistered H3 tactical utility rule satisfies the frozen 20 bp economic promotion gate.

Therefore:

- **no tactical champion is frozen**
- 2025 remains **unopened for tactical transport**
- the H3 forecast engine remains research-valid
- but it is **not yet an economically validated allocation strategy**.

Frozen forecast engine remains:

- direction: CORE3 / XGB_CLASS
- point return: GOLD_ONLY / LGBM_REG
- distribution: GOLD_ONLY / LGBM_QUANT.

Frozen continuous daily forecast vector:

`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`

## 2. Economic simulation contract

Research price proxy:
- Borsa İstanbul Gold MTL / USD / OZ.

Position:
- LONG 100% or CASH 0%.

Holding:
- exactly 3 Gold observations after a LONG entry.

No:
- short
- leverage
- overlapping positions
- stop/take-profit optimization.

Primary transaction cost:
- **20 bp round-trip**.

Sensitivity only:
- 0 bp
- 50 bp.

## 3. Benchmarks at 20 bp

| Benchmark | CAGR | Max DD | Sortino | Terminal wealth |
|---|---:|---:|---:|---:|
| CASH | 0.00% | 0.00% | — | 1.000 |
| **BUY_AND_HOLD** | **13.54%** | **-19.40%** | **1.016** | **1.462** |
| ALWAYS_LONG_H3_ROLL | -3.88% | -30.26% | -0.302 | 0.888 |

Important:

Repeated non-overlapping 3-observation rolling exposure is economically poor once 20 bp is paid on every roll.

The relevant market benchmark is therefore BUY_AND_HOLD, not repeated H3 rolling.

## 4. Candidate utility rules at 20 bp

| Rule | Trades | Exposure | CAGR | Max DD | Sortino | Win rate | Positive years | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| U1 RET_ONLY | 87 | 34.9% | 2.64% | **-12.45%** | 0.279 | 56.3% | 1/3 | FAIL |
| **U2 MEDIAN_CONSENSUS** | **89** | **35.7%** | **6.56%** | **-13.79%** | **0.743** | **57.3%** | **2/3** | **FAIL** |
| U3 PROB_TILT | 101 | 40.5% | 3.14% | -14.51% | 0.332 | 57.4% | 2/3 | FAIL |
| U4 FULL_RISK | 0 | 0.0% | 0.00% | 0.00% | — | — | 0/3 | FAIL |

U2 is the strongest 20 bp candidate, but still fails because:

- Sortino = **0.743**
- BUY_AND_HOLD Sortino = **1.016**.

The frozen gate requires tactical Sortino to exceed BUY_AND_HOLD.

Therefore U2 cannot be promoted.

## 5. U2 year-by-year result

At 20 bp:

### 2022
- return: **+7.39%**
- CAGR-equivalent: +7.48%
- max DD: **-4.62%**
- Sortino: **1.515**
- exposure: 25.2%.

### 2023
- return: **-1.60%**
- max DD: **-13.79%**
- Sortino: **-0.182**
- exposure: 42.6%.

### 2024
- return: **+14.44%**
- CAGR-equivalent: +14.53%
- max DD: **-9.11%**
- Sortino: **1.249**
- exposure: 39.3%.

Interpretation:

U2 is not uniformly poor.

It is useful in 2022 and 2024, but loses money in 2023.

This is insufficient for economic promotion under the frozen gate.

## 6. Cost sensitivity

### 0 bp

U3 PROB_TILT becomes the strongest gross-cost sensitivity result:

- terminal wealth: **1.512**
- total return: **+51.21%**
- CAGR: **14.83%**
- max DD: **-17.13%**
- Sortino: **1.276**
- trades: 191
- positive years: 2/3.

BUY_AND_HOLD at the 20 bp benchmark:
- CAGR 13.54%
- max DD -19.40%
- Sortino 1.016.

Thus before trading friction, the frozen forecasts contain economically interesting timing information.

### 20 bp — binding

Best:
- U2 CAGR **6.56%**
- max DD -13.79%
- Sortino 0.743.

No PASS.

### 50 bp

U2:
- CAGR **2.00%**
- max DD **-4.02%**
- Sortino **0.978**
- only **8 trades**.

The 50 bp version fails minimum trade-count support and cannot select a rule.

## 7. Central economic finding

Stage 6 does **not** show that the forecast engine is useless.

It shows:

> The currently detected short-horizon edge is too thin / turnover-sensitive to support the preregistered 3-observation long-or-cash strategy under a generic 20 bp round-trip cost assumption.

This is a different conclusion from forecast failure.

Evidence:
- H3 forecast heads passed statistical gates;
- gross-cost tactical timing can outperform the market benchmark in the 0 bp sensitivity;
- realistic research friction materially erodes that advantage.

Therefore the economic bottleneck is now:
**execution economics / turnover**, not model-family search.

## 8. Volatility diagnostics at 20 bp

U2 trade results:

### HIGH volatility
- 67 trades
- win rate **56.7%**
- average trade return **+0.163%**
- worst trade **-3.56%**.

### MID volatility
- 13 trades
- win rate 53.8%
- average trade return **+0.276%**.

### LOW volatility
- 9 trades
- win rate **66.7%**
- average trade return **+0.660%**
- worst trade **-0.86%**.

These are diagnostics only.

No volatility-specific rule is created post hoc.

## 9. Why U4 produces no trades

U4 explicitly subtracts 0.5 × Q10 downside magnitude from the continuous utility score.

Under the frozen 20 bp hurdle this is too conservative:
- 0 trades
- 0 exposure.

This confirms that the current Q10 tail forecasts are too wide to support a direct downside-penalty allocation formula at the preregistered strength.

Do not weaken the penalty after inspecting this result.

## 10. What is rejected

Do not now:
- scan lower transaction-cost hurdles
- scan P_UP thresholds
- scan utility coefficients
- shorten/extend holding period
- add stop-loss / take-profit
- select only LOW/MID volatility
- use 2025 to rescue economics.

All such changes would be new Stage-6 research hypotheses and require a new preregistered authority.

## 11. Artifact hashes

- `stage6_trade_ledger_20bp.csv`: `f1e7278973f4445e2fbf585310e8c89a01e6ca70f3176d9903edf378ded29456`
- `stage6_candidate_metrics_20bp.csv`: `776b89eaebcf38dc7c9eb13ef0447c4571a2d9fc099a19e4ad75b3bc35791573`
- `stage6_equity_curves_20bp.csv`: `396e70f02c20f816c5905def975b1d6d72c607e030be282a22f7575eedcb5856`
- `stage6_cost_sensitivity.csv`: `340e81a72216a7d07b99361903020f3566bd6d74cb9348f655198e763ec95184`
- `stage6_year_metrics_20bp.csv`: `32c7c3da482f5cbec0600669179e9c489ba1b0ec223af29cf29b5d29fd742ef5`
- `stage6_volatility_trade_summary.csv`: `129c7823ef4f354c206e0f9737bb0156bb95d1faddc09e35a69248b5f8b6ad67`
- `stage6_benchmarks.csv`: `b284ed85d4633dc7d6df899c84e1efd44e3f723b3bd5c40ec2d58ba6d5ca04bc`
- `STAGE6_RESULT.md`: `efc24c48b4dca526ca583a14f27d8c7fb8f9d9dc6ab44205c5c70003b692fe8a`.

## 12. Decision

**Stage 6 = COMPLETE / NO_TACTICAL_PASS.**

No 2025 tactical transport is authorized.

The forecast engine remains frozen and usable for research reporting, but no capital-allocation rule is currently promoted.

## 13. Exact next research path

The next scientifically defensible step is **not another model zoo**.

It is an execution-economics diagnostic:

### Stage 6B — Turnover / Tradable-Instrument Economic Feasibility Audit

Without choosing new thresholds, determine:

1. how much of the gross tactical edge is lost specifically to turnover;
2. break-even round-trip cost for each frozen utility rule;
3. whether the user's actual intended tradable instrument has a realistic all-in cost below that break-even level;
4. whether the non-overlapping 3-observation mechanic is economically mismatched to the real instrument;
5. whether a lower-turnover implementation can be specified **ex ante** from actual instrument mechanics rather than DEV curve fitting.

Only after a real tradable instrument and realistic execution-cost convention are frozen should economic rule research continue.

2025 remains closed.
