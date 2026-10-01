# GOLD DAILY FORECAST — Stage 1 Daily Data Authority & PIT Audit

**Date:** 2026-10-01  
**Status:** PRE-REGISTERED DATA-AUTHORITY AUDIT  
**Parent:** `GOLD_DAILY_FORECAST_PROJECT_MANIFEST.md`

## 1. Purpose

Freeze the exact daily data contract before any governed daily-model development.

This stage does **not** select a forecasting model or feature set. It only determines which daily series are scientifically admissible and under what timestamp/release rules.

## 2. PASS criteria for a daily input family

A family may be marked READY only if all are documented:

- identifiable source/provider;
- observation definition and timestamp convention;
- historical coverage sufficient for pre-2026 development;
- deterministic date/value retrieval or governed frozen artifact;
- no target-day look-ahead under the proposed forecast-origin timestamp;
- missing-day/holiday treatment defined;
- if macro/released data rather than market prices, release-lag rule defined.

A source may be marked RESEARCH_RECONSTRUCTION if historical values are usable retrospectively but historical origin-time availability is not proven.

A source must be BLOCKED if its daily history or timing cannot be established without silent proxy substitution.

## 3. Target-price rule

Stage 1 must choose one exact daily Gold reference identity for the project. Candidate identities may include:

- an official daily benchmark/reference;
- a governed fixed-time spot observation;
- another reproducible XAU/USD daily reference.

The chosen target must be used consistently for training, validation, retrospective transport and prospective forecasts.

No generic “close” terminology is permitted unless the source actually represents a close.

## 4. Families to audit

Core:
- Gold;
- Silver;
- Platinum;
- Palladium.

Cross-market:
- nominal 10Y rate;
- real 10Y rate;
- breakeven proxy;
- Broad USD / FX;
- VIX;
- Nasdaq-100;
- WTI;
- Brent;
- GPR vintage/monthly state.

## 5. Daily forecast-origin convention to resolve

The audit must recommend a single operational forecast cutoff. Candidate:

- **after all required day-t observations are available, forecast day t+1**.

For every family, either prove availability by that cutoff or impose an explicit lag.

No family may use a value whose publication/observation occurs after the forecast cutoff.

## 6. Calendar rules to resolve

The result must freeze:
- common observation-day calendar;
- weekends;
- market holidays;
- asynchronous cross-market holidays;
- stale carry-forward policy;
- missing observations;
- next-target date definition.

## 7. Prior evidence boundary

Daily V1 remains INVALID/SUPERSEDED.

Daily V2 remains valid retrospective frequency-transfer evidence but is not a production data-authority proof because the historical four-metal series were labeled reconstruction-only.

## 8. Stage gate

Stage 1 PASS requires:
- a usable Gold target identity;
- a usable pre-2026 development history for that target;
- at least one valid baseline feature source;
- explicit treatment for every blocked optional family.

Stage 1 may PASS with some optional families BLOCKED; Stage 2 must simply exclude those families.

No model development is authorized before this result is committed.
