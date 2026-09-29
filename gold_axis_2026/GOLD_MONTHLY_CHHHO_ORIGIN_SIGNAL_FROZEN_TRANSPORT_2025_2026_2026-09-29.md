# GOLD MONTHLY — ChHHO Origin-Signal Frozen Transport 2025/2026

**Date:** 2026-09-29  
**Status:** FROZEN TRANSPORT COMPLETE / HARD SWITCH NOT VALIDATED  
**Purpose:** Transport the DEV-derived origin-signal mechanisms unchanged into reporting-only 2025 and 2026 without retuning.

## 1. Frozen rule set

No 2025/2026 outcome was used to alter these rules.

### A — CROSS_METAL_FRAGILITY
At the forecast origin:
- ChHHO forecast direction = current Gold monthly direction;
- |Gold monthly log return| < 2%;
- at least 2 of Silver / Platinum / Palladium move in the opposite direction to Gold.

### B — SUPPORTED_MOMENTUM_UNDERREACTION
At the forecast origin:
- Gold monthly log return > +3%;
- at least 2 of Silver / Platinum / Palladium are positive;
- Broad USD monthly mean log change < 0;
- nominal 10Y monthly-mean change < 0;
- real 10Y monthly-mean change < 0;
- ChHHO predicted Gold move <= +1% (near-flat or opposite-direction forecast).

### C — DELAYED_RATES_CATCHUP
At the forecast origin:
- Gold monthly log return < 0;
- nominal 10Y monthly-mean change < 0;
- real 10Y monthly-mean change < 0;
- |ChHHO predicted Gold move| < 1%.

### D — MACRO_GOLD_CONFLICT
At the forecast origin:
- Gold monthly log return > +3%;
- Broad USD monthly mean log change > 0;
- nominal 10Y monthly-mean change > 0;
- real 10Y monthly-mean change > 0;
- ChHHO predicts UP.

Strong switch-type set = A + C + D.  
Four-mechanism warning set = A + B + C + D.

## 2. Frozen transport data

- ChHHO 2025 forecasts: frozen ANFIS authority artifact 10989389723.
- ChHHO 2026 Jan-Aug forecasts/actuals: frozen VIX transport authority artifact 11042740289; August 2026 ChHHO BASE is unchanged frozen base forecast.
- Four-metal origin data: governed DEV snapshot through 2024-12 plus public StakTrakr extension from 2025-01-02 through 2026-09-28.
- Broad USD / nominal 10Y / real 10Y: External Authority V2 artifact 11028494060.
- Release cutoffs retained: H.10 Broad USD = 7 calendar days; H.15 rates = 2 calendar days.
- 2025/2026 are reporting-only. No rule or threshold was changed after seeing transport outcomes.

## 3. Alarm months

| Target | Mechanism | ChHHO AE | ChHHO direction | FULL7 AE | REDUCED4 AE | Transport reading |
|---|---|---:|---|---:|---:|---|
| **2025-03** | B Momentum underreaction | **119.06** | WRONG | 76.73 | **73.29** | successful warning; both ANN challengers rescue |
| **2025-09** | A Cross-metal fragility | **288.42** | CORRECT | 230.51 | **215.79** | successful magnitude-risk warning |
| **2025-12** | A Cross-metal fragility | **93.32** | CORRECT | 95.99 | **80.65** | partial rescue; REDUCED4 helps, FULL7 slightly worse |
| **2026-05** | A Cross-metal fragility | **55.10** | CORRECT | 70.63 | 74.23 | false switch alarm; ChHHO is better |

No C or D alarm fires in 2025 or 2026 Jan-Aug.

## 4. Error-risk transport

Frozen DEV Q3 ChHHO absolute-error threshold = **63.06 USD**.

### 2025
- months: 12
- ChHHO ΣAE: **1252.05**
- warning alarms: **3**
- alarms above frozen DEV-Q3: **3/3**
- total months above frozen DEV-Q3: **8**
- precision for Q3-high error: **100%**
- recall for Q3-high error: **37.5%**
- ChHHO direction: **9/12**

Interpretation: 2025 transport is selective and useful, but incomplete. It identifies three genuine high-error months and produces no low-error alarm.

### 2026 Jan-Aug
- months: 8
- ChHHO ΣAE: **1526.13**
- warning alarms: **1** (2026-05)
- alarm above frozen DEV-Q3: **0/1**
- total months above frozen DEV-Q3: **5**
- precision for Q3-high error: **0%**
- recall for Q3-high error: **0%**
- ChHHO direction: **5/8**

Major unflagged misses include:
- **2026-01: 458.50 USD**
- **2026-06: 362.17 USD**
- **2026-08: 347.99 USD**
- **2026-03: 145.62 USD**
- **2026-07: 82.68 USD**

Interpretation: the frozen DEV mechanisms do not cover the dominant 2026 failure regime.

### Combined 2025 + 2026 Jan-Aug
- months: 20
- alarms: 4
- alarms above frozen DEV-Q3: 3
- Q3-high months: 13
- precision: **75.0%**
- recall: **23.1%**
- flagged mean AE: **138.97 USD**
- unflagged mean AE: **138.89 USD**

Thus the warning set is not a general high-error detector.

## 5. Rescueability diagnostic against frozen ANN challengers

ANN rows exist for 2025 and 2026 Jan-Jul (19 months).

Define a descriptive ANN-rescueable month as one where at least one of frozen FULL7 or REDUCED4 has lower AE than ChHHO.

Across 19 months:
- ANN-rescueable by either challenger: **11/19**
- four-mechanism alarm catches: **3/11**
- alarm precision for “either ANN better”: **3/4 = 75%**
- alarm recall: **3/11 = 27.3%**

For the stricter definition “both ANN challengers beat ChHHO”:
- months: **9/19**
- alarm precision: **2/4 = 50%**
- alarm recall: **2/9 = 22.2%**

This confirms the central limitation: the frozen gate is selective but misses many genuinely rescueable months.

## 6. Fixed-challenger switch diagnostics — NOT promotion evidence

The gate was frozen before this transport, but choosing FULL7 or REDUCED4 as fallback is evaluated here only as a diagnostic. No fallback is promoted from this test.

### Warning set (A+B+C+D) -> FULL7 on alarm
2025:
- ChHHO ΣAE 1252.05 -> hybrid **1154.49**
- improvement **97.56 USD**
- direction **9/12 -> 10/12**

2026 Jan-Jul:
- ChHHO ΣAE 1178.14 -> hybrid **1193.67**
- deterioration **15.53 USD**
- direction **5/7 -> 5/7**

Combined 19 months:
- 2430.19 -> **2348.16**
- improvement **82.03 USD**
- direction **14/19 -> 15/19**

### Warning set (A+B+C+D) -> REDUCED4 on alarm
2025:
- ChHHO ΣAE 1252.05 -> hybrid **1121.00**
- improvement **131.06 USD**
- direction **9/12 -> 10/12**

2026 Jan-Jul:
- ChHHO ΣAE 1178.14 -> hybrid **1197.27**
- deterioration **19.13 USD**
- direction **5/7 -> 5/7**

Combined 19 months:
- 2430.19 -> **2318.26**
- improvement **111.93 USD**
- direction **14/19 -> 15/19**

Including 2026-08 (no alarm; ANN fallback row unavailable and no switch is made):
- ChHHO 20-month ΣAE: **2778.19**
- diagnostic REDUCED4-switch total: **2666.26**
- nominal improvement: **111.93 USD = 4.03%**
- direction: **14/20 -> 15/20**

The combined gain is driven by 2025. The rule loses value in 2026 and therefore cannot be called transport-stable.

## 7. Mechanism-level transport reading

### A — Cross-metal fragility
Transport alarms:
- 2025-09: strong useful warning
- 2025-12: useful only against REDUCED4
- 2026-05: false switch warning

Verdict: **PARTIAL TRANSPORT / NOT STABLE ENOUGH FOR HARD SWITCH**.

### B — Supported momentum underreaction
Transport alarm:
- 2025-03: large ChHHO error, wrong direction, both frozen ANN challengers better.

Verdict: **PROMISING BUT n=1 TRANSPORT EVENT**.

### C — Delayed rates catch-up
No transport event.

Verdict: **NOT TESTED OUT OF DEV BY AVAILABLE EVENT COUNT**.

### D — Macro-Gold conflict
No transport event.

Verdict: **NOT TESTED OUT OF DEV BY AVAILABLE EVENT COUNT**.

## 8. Scientific conclusion

The DEV finding was not pure noise: the frozen rules generate several meaningful 2025 warnings, especially 2025-03 and 2025-09.

However the hypothesis **does not validate as a general router**:
- recall is low;
- 2026 precision/recall collapses;
- very large 2026 misses are unflagged;
- the cross-metal rule produces a false switch warning in 2026-05;
- fixed fallback gains are regime-dependent.

Therefore:

**HARD SWITCH ROUTER: NOT PROMOTED.**

The evidence supports a narrower role:
- mechanism flags may be retained as **confidence/risk annotations**;
- automatic model replacement is not justified yet;
- 2026 introduces at least one missing failure mechanism not represented by the DEV-derived rule set.

## 9. Next research boundary

Do not retune the four rules on 2025/2026.

The scientifically clean next step is to study the **unflagged 2026 large-error months** (especially 2026-01, 2026-06, 2026-08) as a new, explicitly separate mechanism-discovery stage, using origin-visible variables not already exhausted. Candidate information families remain:
- COMEX positioning;
- gold ETF flows;
- GVZ / gold implied volatility;
- central-bank / gold-specific flow proxies;
- event-risk state.

Any new mechanism must then be frozen and tested separately; it must not be retrofitted into the existing DEV rule performance.
