# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6C Cross-Instrument Mapping Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Test whether the frozen Borsa İstanbul Gold USD/oz H3 forecast can be transferred to a realistically tradable Gold instrument without materially degrading the signal.

Candidate implementation families:
1. **GLDM** — SPDR Gold MiniShares Trust
2. **MGC** — COMEX Micro Gold Futures.

No forecast model, utility coefficient, H3 horizon, or DEV threshold is changed.

2025 remains forbidden for tactical selection.

## 2. Selection window

Mapping / selection authority:
- **2022-01-03 through 2024-12-31**
- DEV only.

No 2025 observations may enter:
- correlation selection
- mapping thresholds
- execution-rule selection
- instrument choice.

## 3. Frozen forecast input

Use Stage-5 frozen DEV forecast object / Stage-6B U3 rule:

`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`

Frozen U3 utility:

`U3 = 0.5*RET_HAT3 + 0.5*Q50_3 + 0.5*(P_UP3-0.5)*hvol`

with:

`hvol = sigma20*sqrt(3)`.

The low-cost U3 feasibility band from Stage 6B:
- full tactical PASS: **0 to 1.25 bp round-trip**
- strong parity: **0 to 0.50 bp**.

## 4. BIST reference return

Reference mapping target:
- governed BIST Gold MTL/USD/OZ.

For origin row t:
- BIST H3 return = frozen `y_return`
- H3 end date = the third later governed Gold observation date.

These dates are reconstructed from the governed readiness panel.

## 5. External market-data source hierarchy

### GLDM
Primary research retrieval:
- Yahoo Finance daily OHLC through `yfinance`.

Independent price sanity cross-check:
- Stooq daily GLDM.US where available.

### MGC
Research retrieval:
- Yahoo Finance continuous Micro Gold futures ticker `MGC=F`.

CME official documentation is authoritative for:
- contract specification
- trading hours
- futures session structure
- continuous-series methodology concept.

Important limitation:

The free Yahoo continuous series is a **secondary research series**. It is not accepted as production settlement authority.

Therefore MGC can at most receive:
- RESEARCH_MAPPING_PASS

until an official/licensed CME continuous or contract-level settlement series reproduces the result.

## 6. GLDM mapping return

Two diagnostics are required.

### 6.1 Same-calendar close mapping

For each BIST origin/end pair:
- start = most recent GLDM close on or before BIST origin date
- end = most recent GLDM close on or before BIST H3 end date.

Compute log return.

Purpose:
- pure Gold-price mapping / tracking diagnostic.

This is not the execution backtest.

### 6.2 Origin-safe execution transfer

Forecast issue convention:
- 00:30 Europe/Istanbul on `signal_date`.

Because the U.S. cash equity session opens later that day, GLDM execution proxy is:

- entry = **GLDM Open on first U.S. trading session on or after signal_date**
- exit = **GLDM Open on first U.S. trading session on or after BIST H3 end date**.

If the two mapped sessions collapse to the same timestamp or a valid exit does not exist:
- row excluded from execution-transfer economics.

No same-day close entry is permitted.

## 7. MGC mapping return

### 7.1 Same-calendar continuous-close mapping

For each BIST origin/end pair:
- start = most recent MGC=F daily close on or before BIST origin date
- end = most recent MGC=F daily close on or before BIST H3 end date.

Compute log return.

Purpose:
- research mapping only.

### 7.2 Origin-safe execution limitation

A CME futures daily "Open" belongs to the Globex trade-date session that may have opened before the 00:30 Istanbul forecast issue time.

Therefore Stage 6C **forbids** treating same-date MGC daily Open as an origin-safe entry.

Daily-data execution stress instead uses:
- entry = first MGC daily Open whose session date is **strictly after signal_date**
- exit = first MGC daily Open whose session date is on/after BIST H3 end date and strictly after entry.

This is a deliberately delayed / conservative stress test.

A true same-origin MGC implementation requires intraday timestamped futures data and remains blocked even if mapping passes.

## 8. Mapping diagnostics

For GLDM close mapping and MGC close mapping report:

- common N
- Pearson correlation
- Spearman correlation
- OLS intercept
- OLS beta
- tracking-error standard deviation of:
  `instrument_return - BIST_return`
- mean absolute tracking error
- sign agreement
- severe divergence frequency:
  `abs(instrument_return - BIST_return) > 1.0%`
- mean return difference.

## 9. Mapping PASS gate

### GLDM mapping PASS

Require:
- common N >= 650
- Pearson >= **0.90**
- Spearman >= **0.88**
- beta in **[0.85, 1.15]**
- sign agreement >= **85%**
- tracking-error SD <= **0.60%**
- severe divergence frequency <= **10%**.

### MGC research mapping PASS

Same numerical gate.

But MGC cannot become production-frozen from secondary daily data alone.

## 10. Frozen U3 action-transfer economics

For each instrument apply the frozen U3 action decision using **instrument-specific assumed costs** fixed before results:

### GLDM research cost
- **1.25 bp round-trip**.

Reason:
- this is the top of the frozen low-cost U3 PASS band;
- it is conservative relative to public spread+short holding fee estimate, before broker/FX uncertainty.

### MGC research cost
- **1.00 bp round-trip**.

Reason:
- within U3 low-cost PASS band;
- leaves room above CME exchange-level published cost for additional broker/spread friction;
- not a claim of universal all-in MGC cost.

Entry decision:
- LONG iff `U3 > assumed_cost`
- else CASH.

No cost or hurdle search.

## 11. Transfer-economics metrics

Using the origin-safe / delayed execution conventions above:

- number of completed trades
- exposure proxy
- total return
- CAGR over common calendar span
- max drawdown
- Sortino
- win rate
- average trade return
- 2022 / 2023 / 2024 returns.

### Instrument transfer PASS

Require:
- mapping PASS
- completed trades >= 20
- CAGR > 0
- >=2/3 calendar years positive
- Sortino > 0.75
- max drawdown better than -25%.

This is a transfer-feasibility gate, not a final investment recommendation.

## 12. Instrument-freeze rule

### GLDM
May be frozen for Stage 7 only if:
- mapping PASS
- transfer PASS
- independent price sanity check does not reveal material discrepancy
- cost budget remains <=1.25 bp **before account-specific FX/commission review**.

If the account requires material FX conversion cost:
- production freeze remains conditional.

### MGC
May not be production-frozen from Stage 6C secondary daily data.

If research mapping + delayed transfer PASS:
- status = **RESEARCH_PASS / INTRADAY_AUTHORITY_REQUIRED**
- next step is official timestamped CME data verification.

## 13. No post-hoc repair

Forbidden:
- alternate GLDM entry price after results
- alternate MGC roll convention after results
- threshold tuning
- alternate H3 window
- 2025 rescue
- choosing whichever date alignment looks best.

## 14. Required outputs

- raw external daily-data coverage audit
- BIST-to-GLDM mapping table
- BIST-to-MGC mapping table
- mapping diagnostics
- frozen U3 GLDM transfer ledger
- frozen U3 MGC delayed-transfer ledger
- instrument decisions
- immutable hashes.
