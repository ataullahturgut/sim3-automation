# GOLD MONTHLY — ChHHO Alarm Audit V3 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / BINDING AUDIT SPECIFICATION  
**Scope:** alarm evaluation only; no routing, no model switching, no fallback selection.

## 1. Why V3 exists

The V2 pre-DEV backcast correctly established a same-methodology GPR path and a reproducible ChHHO forecast path, but its alarm-evaluation layer is not accepted as final evidence until two source-consistency questions are resolved:

1. V2 computed Gold alarm states from the common-daily four-metal monthly reconstruction, while the canonical alarm research overrides Gold with the frozen CORE5 monthly Gold series.
2. V2 reconstructed H.10/H.15 macro inputs separately; V3 must compare those values against the already-authorized External Authority V2 store.

Therefore V3 does **not** rerun or retune ChHHO. It audits the alarm layer against frozen forecast artifacts.

## 2. Frozen authorities

V3 must use these immutable inputs:

- DEV snapshot artifact **10985453248**
- public current bundle artifact **11015874673**
- frozen ChHHO authority artifact **10989389723**
- frozen 2026 transport artifact **11042740289**
- External Authority V2 artifact **11028494060**
- valid same-method pre-DEV V2 artifact **11084467079**

The pre-DEV V2 artifact is used only for:
- ChHHO forecast / predicted log return,
- target actual,
- source/GPR audit trail.

Its stored alarm booleans are **ignored and recomputed**.

## 3. Canonical alarm-state construction

### Gold
For every origin, Gold state must be built from the canonical monthly Gold authority:
- DEV: snapshot `core_gold`
- 2025/2026 extension: public bundle World Bank monthly Gold series

This is the binding V3 correction.

### Silver / Platinum / Palladium
Use the governed common-daily four-metal history from the DEV snapshot plus the public current daily extension, aggregated to monthly means.

### Macro variables for B/C/D
Use only External Authority V2:
- Broad USD: H.10 `BROAD_USD_INDEX`, 7-calendar-day safety lag
- nominal 10Y: H.15 `DGS10`, 2-calendar-day safety lag
- real 10Y: H.15 `DFII10`, 2-calendar-day safety lag

Monthly-mean changes are computed exactly with those lags. No separate mirror source is authoritative in V3.

## 4. Frozen alarm definitions

No thresholds may be changed.

### A — CROSS_METAL_FRAGILITY
- sign(ChHHO prediction) = sign(current Gold 1m log return)
- |Gold 1m log return| < 2%
- at least 2 of Silver / Platinum / Palladium move opposite to Gold

### B — SUPPORTED_MOMENTUM_UNDERREACTION — warning only
- Gold 1m > +3%
- at least 2 other precious metals positive
- Broad USD monthly mean log change < 0
- nominal 10Y monthly-mean change < 0
- real 10Y monthly-mean change < 0
- ChHHO predicted Gold move <= +1%

### C — DELAYED_RATES_CATCHUP
- Gold 1m < 0
- nominal 10Y change < 0
- real 10Y change < 0
- |ChHHO predicted move| < 1%

### D — MACRO_GOLD_CONFLICT
- Gold 1m > +3%
- Broad USD change > 0
- nominal 10Y change > 0
- real 10Y change > 0
- ChHHO predicts UP

### E — EXTREME_LEVEL_MODEL_DISAGREEMENT — discovery-frozen candidate
- Gold monthly price > 20% above trailing prior-12-month Gold mean
- |ChHHO predicted return − current Gold 1m return| > 5 percentage points

### G — POST_LIQUIDATION_HIGH_UNCERTAINTY — discovery-frozen candidate
- trailing Gold 3m log return <= -10%

Hard research alarm = **A OR C OR D OR E OR G**.  
B remains warning-only and is excluded from hard-alarm metrics.

## 5. Replay gate before pre-DEV interpretation

The same V3 motor must first reproduce the frozen DEV A/B/C/D event set using corrected canonical Gold and External Authority V2.

Expected DEV targets:

- A: 2022-11, 2023-08
- B: 2023-01, 2023-02, 2023-05
- C: 2024-07
- D: 2024-11

If any of these event lists differs, V3 fails and pre-DEV alarm results are not interpretable.

E/G are reported but are not part of this DEV gate because they were discovered later.

## 6. Legacy-source discrepancy audit

V3 must also reconstruct the old common-daily-Gold alarm state and compare it with corrected canonical Gold.

This comparison is diagnostic only. It must identify every target whose alarm flag changes solely because of the Gold source correction.

No threshold may be altered to preserve a prior event.

## 7. Error-risk labels

The main project metric remains absolute USD error. Alarm research must report three frozen labels in parallel:

- HIGH_AE: AE > **63.06 USD**
- HIGH_APE: APE > **2.96117%**
- HIGH_RETURN_ERROR: absolute Gold log-return forecast error > **3.00590 percentage points**

No label is tuned using pre-DEV, 2025, or 2026 outcomes.

## 8. Pre-DEV test

After the replay gate passes, recompute A/B/C/D/E/G for the five valid same-methodology pre-DEV origins:

- 2021-10 -> 2021-11
- 2021-11 -> 2021-12
- 2021-12 -> 2022-01
- 2022-01 -> 2022-02
- 2022-02 -> 2022-03

V3 must additionally verify that the V2 macro reconstruction values equal External Authority V2 values for all five origins to numerical tolerance.

## 9. Governance

- V1 old-method GPR backcast remains invalid.
- V2 ChHHO/GPR backcast remains usable as a forecast artifact, but its alarm booleans are superseded by V3.
- No routing/model switching is authorized.
- No threshold retuning is authorized.
- Any changed alarm event caused by canonical-source correction must be reported, not hidden.
