# GOLD MONTHLY — ChHHO Origin-Signal Diagnostic

**Date:** 2026-09-29  
**Status:** DIAGNOSTIC COMPLETE / NO ROUTER PROMOTION  
**Selection authority:** DEV 2022-04..2024-12 (33 target months)  
**Purpose:** Test whether ChHHO rescueable failure months have origin-visible signatures before any helper model/router is built.

## 1. Data authority

This diagnostic uses only information available at each forecast origin:

- frozen ChHHO DEV forecasts from the authorized ChHHO artifact;
- frozen DEV snapshot of Gold/Silver/Platinum/Palladium daily history and origin-safe GPR vintages;
- External Authority V2 daily Broad USD, nominal 10Y, real 10Y, VIX, Nasdaq-100, WTI and Brent data with the already-governed release-safety cutoffs;
- no target-month external data;
- no 2025/2026 information for DEV classification or rule construction.

The five diagnostic `RESCUEABLE` months are the previously established ChHHO-specific/partly rescueable cases: **2022-11, 2023-01, 2023-08, 2024-07, 2024-11**. Shared-hard months remain a separate class.

## 2. Main result: one generic score is not enough

Single-score screens do **not** cleanly separate all rescueable months. Examples:

| Origin-visible diagnostic | Rescueable AUC* | Interpretation |
|---|---:|---|
| Precious-metal sign disagreement | 0.725 | useful but partial |
| Gold–macro conflict | 0.636 | useful mainly for divergence cases |
| Macro/Gold gap | 0.579 | weak/moderate |
| Momentum-gap magnitude | 0.543 | weak as a universal score |
| VIX level | 0.507 | no useful universal separation |
| ChHHO absolute predicted move | 0.500 | no rescueable discrimination |

*AUC is descriptive on the same 33-month DEV sample; it is not an out-of-sample router performance claim.

Important counterexamples show why a universal gate is unsafe. ChHHO can strongly suppress momentum or Gold can diverge from macro variables without producing a large ChHHO error. Examples include 2022-06, 2022-08 and 2024-05.

## 3. Mechanism-specific signatures

The five rescueable months separate into distinct origin-visible mechanisms.

### A. Cross-metal fragility — 2022-11 and 2023-08

A simple descriptive condition:

- ChHHO forecasts continuation in Gold's current direction;
- Gold's monthly move is modest (absolute move <2%);
- at least **2 of Silver/Platinum/Palladium move in the opposite direction**.

Within the 33 DEV origins this condition flags exactly:

- **2022-11** — RESCUEABLE; ChHHO AE 102.20 USD;
- **2023-08** — RESCUEABLE; ChHHO AE 77.53 USD.

No other DEV month satisfies this exact descriptive condition. This is the cleanest new finding of the diagnostic. It says that cross-metal **directional breadth**, not simple Gold-vs-metals distance, is potentially valuable as a fragility indicator.

### B. Supported bullish momentum but ChHHO suppresses it — 2023-01

At the 2022-12 origin:

- Gold monthly return: **+3.91%**;
- Silver: **+10.15%**; Platinum: **+2.34%**;
- Broad USD monthly signal: **-2.28%**;
- nominal 10Y monthly-mean change: **-30.8 bp**;
- real 10Y monthly-mean change: **-18.6 bp**;
- ChHHO predicted move: **-0.04%**.

This is a genuine model-underreaction pattern: bullish Gold/metal breadth and macro support are already present, while ChHHO predicts essentially no move.

However the same broad rule also fires in **2023-02** (ChHHO AE 29.06) and **2023-05** (AE 19.38). Therefore this mechanism is a **warning/confidence signal**, not yet a safe hard-switch rule.

### C. Rates tailwind but Gold has not caught up — 2024-07

At the 2024-06 origin:

- Gold monthly return: **-1.08%**;
- nominal 10Y monthly-mean change: **-17.2 bp**;
- real 10Y monthly-mean change: **-9.5 bp**;
- ChHHO predicted move: **+0.04%**.

The simple condition “Gold down, nominal and real 10Y both down, ChHHO absolute forecast <1%” occurs only in **2024-07** in DEV. This supports the delayed-catch-up hypothesis.

### D. Gold rises into a simultaneous USD/rates headwind — 2024-11

At the 2024-10 origin:

- Gold monthly return: **+4.64%**;
- Broad USD monthly signal: **+0.93%**;
- nominal 10Y monthly-mean change: **+35.8 bp**;
- real 10Y monthly-mean change: **+18.0 bp**;
- ChHHO still forecasts **+2.94%** continuation.

The descriptive condition “Gold >+3%, Broad USD up, nominal 10Y up, real 10Y up, and ChHHO still forecasts up” occurs only in **2024-11** in DEV. This is a strong macro–Gold conflict / fragile-continuation signal.

## 4. Combined diagnostic flag

Using the four mechanism definitions above, without fitting a statistical classifier:

- all **5/5 rescueable** months are flagged;
- only **2 additional months** are flagged: 2023-02 and 2023-05, both from the weaker momentum-underreaction rule;
- the three stronger mechanisms (cross-metal fragility + delayed rates catch-up + macro conflict) flag **4/5 rescueable months with 0 extra DEV flags**;
- the known shared-hard months **2024-03, 2022-07 and 2024-04 are not flagged by these strong switch-type rules**.

This is encouraging but **not router performance**. The mechanism rules were formulated after inspecting the same DEV failure cases, so 5/5 and 4/5 are in-sample descriptive results and cannot be reported as validated precision/recall.

## 5. Important negative result: “small ChHHO move” is not enough

Although the eight worst ChHHO months have a low average predicted movement ex post, ChHHO's absolute predicted move by itself has **AUC 0.50** for the five rescueable months. Therefore a rule such as “ChHHO predicts a small move, so switch model” is not supported.

Likewise VIX alone, generic cross-risk stress, generic macro stretch and simple Gold-vs-metals distance are not sufficient universal gates.

## 6. Residual-attribution correction

The same-day residual experiments must be interpreted with the mandatory bias-only control. ChHHO has a DEV mean signed residual of **+13.6909 USD**. Bias-only correction reduces DEV ΣAE from **1413.03 to 1338.89 USD**. After that control:

- VIX R1 adds only **+0.56 USD** incremental DEV improvement;
- Brent R1 is **7.61 USD worse** than bias-only;
- PIT Rates is **32.03 USD worse** than bias-only;
- Rates+Brent is **38.21 USD worse** than bias-only.

Therefore the new mechanism evidence should not be confused with the older BASE-relative residual gains.

## 7. Router implication

The evidence does **not** support one binary “high-error gate” or one fixed fallback model. The signal should be mechanism-specific and conservative:

- **cross-metal fragility** → ChHHO continuation is suspect;
- **rates catch-up gap** → ChHHO magnitude is suspect;
- **macro conflict** → continuation/regime-break risk is high;
- **supported momentum underreaction** → confidence should be reduced, but hard switching is not yet justified.

The cross-model oracle audit also shows why one fallback is unsafe: the best alternatives differ by month (REDUCED4 ANN for 2022-11, CNN-LSTM LB6 for 2023-01 and 2024-11, Random Forest for 2023-08, LSTM LB3 for 2024-07).

## 8. Decision

**Finding:** There is real origin-visible structure, but it is **heterogeneous**. The correct next architecture is not “predict high error”, but a small mechanism classifier / rule-gate with separate states.

**Not yet authorized:** production router, automatic model switching, 2025/2026 retuning.

**Next validation requirement:** freeze the DEV-derived mechanism definitions, then test them without modification on retrospective 2025/2026 origins (where all required inputs are available) and measure false alarms, ChHHO error conditional on each flag, and whether a predeclared fallback/pool actually improves realized error. COMEX/ETF/GVZ additions should remain separate incremental challengers rather than being assumed useful.
