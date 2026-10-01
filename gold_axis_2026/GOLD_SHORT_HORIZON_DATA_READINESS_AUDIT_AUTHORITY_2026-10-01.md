# GOLD SHORT-HORIZON TACTICAL FORECAST — Data Readiness Audit Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUDIT AUTHORITY

## 1. Purpose

Determine whether the currently governed daily data are sufficient to start a separate H1/H3/H5 short-horizon Gold tactical forecasting project.

This stage does not select a model.

## 2. Targets

For each Borsa İstanbul Gold observation t:

- H1 = log(P[t+1] / P[t])
- H3 = log(P[t+3] / P[t])
- H5 = log(P[t+5] / P[t])

Forecast issue convention remains the daily-project convention:
- after P[t] is known;
- before P[t+1] is published;
- operational reference time 00:30 Europe/Istanbul on the next eligible Borsa date.

## 3. Chronology

- training/background: 2011..2021
- DEV: 2022..2024
- 2025: frozen transport
- 2026: not selection authority.

## 4. Governed input authorities

Gold/Silver/Platinum/Palladium:
- Borsa İstanbul MTL / USD / OZ artifact from Stage 2.

External V2:
- H.15 Rates
- H.10 FX
- Cboe VIX
- Nasdaq-100
- WTI/Brent source histories.

## 5. Conservative PIT joins

For readiness counting:

- H.15: latest valid observation with observation date <= signal_date - 2 calendar days
- H.10: latest valid observation with observation date <= signal_date - 7 calendar days
- VIX: latest valid close <= signal_date - 1 calendar day
- Nasdaq-100: latest valid index observation <= signal_date - 1 calendar day.

These are conservative availability rules, not aggressive same-day joins.

WTI/Brent:
- source coverage is audited;
- excluded from the first strict merged feature panel because historical publication-date mapping remains unresolved for the short-horizon origin contract.

GPR:
- excluded from first strict merged feature panel pending complete daily-vintage merged-coverage audit.

## 6. Feature-history readiness blocks

GOLD_ONLY:
- Gold r1/r3/r5/r10/r21 + sigma20.

CORE3:
- GOLD_ONLY
- Silver r1/r5/r21
- Platinum r1/r5/r21
- causal age/staleness.

CORE4:
- CORE3
- Palladium r1/r5/r21
- causal age/staleness.

EXTERNAL_SAFE:
- Rates: DGS10, DFII10, breakeven
- FX: Broad USD + EUR/GBP/JPY/CHF/CNY
- VIX
- Nasdaq-100.

The audit must count strict complete rows at each horizon and chronology segment.

## 7. PASS criteria

Data readiness PASS if:

- H1/H3/H5 each have >= 700 DEV origins;
- at least one multi-asset core has >= 2,000 pre-DEV training origins or a clearly documented near-threshold alternative;
- 2025 transport has >= 200 observations per horizon;
- adding safe external families does not materially collapse DEV or transport coverage;
- no future fill is used.

Deep-learning suitability is reported separately and is not required for data-readiness PASS.
