# GOLD CONTROL — PIYASA DISPLAY CONTRACT CHANGE CONTROL

**Date:** 2026-09-01  
**Scope:** Stage 5 / `Piyasa` display semantics only  
**Decision:** `APPROVED_WITH_EXPLICIT_PROVIDER_ROLE_SEPARATION`

## Problem

The product requires a market-first `Piyasa` screen while the canonical R4.1 EOD decision reference (`XAU_EOD_TWELVE_NY17`) is a Twelve Data vendor series whose external-display/redistribution rights depend on subscription/add-on terms. A display screen must not silently expose a vendor raw value merely because the model is entitled to use it internally.

## Authority evidence

### Twelve Data

Official 2026 Terms of Use:

- data access is licensed primarily for Internal Use unless the subscription/add-on/separate agreement expressly permits external display or redistribution;
- external display/redistribution requires the applicable subscription rights, Redistribution Rights Add-On, or separate agreement;
- attribution requirements can apply when data is publicly displayed.

References:

- https://twelvedata.com/terms
- https://support.twelvedata.com/en/articles/12647398-attribution-guidelines-for-using-twelve-data

Therefore `XAU_EOD_TWELVE_NY17` remains an internal canonical decision-reference series and its raw numeric market value is **not rendered in the user-facing Piyasa UI unless display rights are separately proven and frozen**.

### Gold API

Official Gold API documentation states:

- `GET /price/{symbol}` is a free current-price endpoint;
- no authentication is required for the current-price endpoint;
- clients should cache current-price responses for 30 seconds;
- CORS / website use is supported;
- the provider may use provider-managed fallback sources, so lineage is not authority-grade.

Reference:

- https://gold-api.com/llms.txt

Therefore `XAU_SPOT_GOLDAPI` is approved only for **indicative live display / monitoring** and is prohibited from R4.1 EOD, forecast, VW, Fast/Slow, or final-decision use.

Gold API historical endpoints require an API key. No protected Gold API history credential has been frozen in this project, so Stage 5 does not silently assume that entitlement.

### Existing XAUS history

The existing `XAU_DAILY_XAUS` adapter has already passed runtime history smoke, but prior forensic evidence shows that this lineage behaves futures-like / Yahoo `GC=F`-like. Therefore it may be used only as an explicitly labelled **operational daily history / cross-check display**, never as canonical spot/EOD authority or model input under another name.

## Frozen Piyasa display contract

1. **Live price card**
   - source: `XAU_SPOT_GOLDAPI`;
   - role: indicative display only;
   - show source, timestamp and freshness/stale state;
   - never infer a direction or action from the live value.

2. **Daily chart and last completed daily display close**
   - source: current `XAU_DAILY_XAUS` history adapter;
   - role: operational history / cross-check display only;
   - visible disclosure that it is not canonical Twelve NY17 EOD, settlement, benchmark, or model authority;
   - only completed daily rows strictly before the current UTC date are eligible for the “last completed daily close” comparison.

3. **Canonical R4.1 EOD**
   - source: `XAU_EOD_TWELVE_NY17`;
   - model/decision internal contract remains unchanged;
   - raw numeric vendor value is not displayed without separately frozen display rights;
   - technical surfaces may expose non-price metadata such as source identity, quality state and as-of timestamp when available.

4. **Decision state**
   - Piyasa may show only a display-eligible stored Decision Store state (`LIVE_PRODUCTION`, then `PROSPECTIVE_SHADOW`);
   - if neither exists, show `KANONİK KARAR YOK`;
   - `HISTORICAL_REPLAY` is never surfaced as current decision;
   - mandatory warning: `Canlı spot ≠ son EOD karar`.

5. **Timeframes**
   - approved now: `1A | 3A | 6A | 1Y`;
   - `1G`, `1H`, `Tümü` remain blocked until an audited intraday/long-history display adapter exists.

## Implementation evidence

Canonical implementation artifacts:

- `gold_axis_2026/apps/live_sources.py`
- `gold_axis_2026/apps/piyasa_contract.py`
- `gold_axis_2026/apps/gold_control.py`
- `gold_axis_2026/apps/test_piyasa_contract.py`

Stage-5 UI smoke:

- workflow run: `33521193615`
- job: `99900581399`
- deterministic Piyasa tests: `4 passed`
- canonical tabs: `Piyasa | Görünüm | Tahmin | Geçmiş`
- Streamlit runtime exceptions: none
- forecast/decision writes: none
- result: `STAGE5_PIYASA_UI_SMOKE_PASS`

## Non-effects

This change does **not**:

- close any Stage-4B forecast blocker;
- create an H=1 forecast;
- create a Decision Store row;
- approve action/position mapping;
- promote XAUS history to canonical spot/EOD authority;
- grant or assume Twelve Data external-display rights.
