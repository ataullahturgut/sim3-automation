# GOLD MONTHLY — F4 RESET / PROCESSING-PARITY AUDIT

**Date:** 2026-09-29  
**Status:** BINDING RESET BEFORE ANY NEW F4 MODEL RUN  
**Scope:** External-information integration into frozen ChHHO-ANFIS  
**Reason for reset:** external variables were not processed with the same information architecture as CURRENT8 and optimizer search effort was not dimension-adjusted.

## 1. What remains valid

The internal ChHHO contract remains valid and unchanged:

- target: next-calendar-month average XAU/USD via Gold log-return;
- DEV: 2022-04..2024-12, n=33;
- baseline: **CURRENT8 = Gold/Silver/Platinum/Palladium × {MR1, VW}**;
- MR1: previous completed-month log-return based on monthly metal averages;
- VW: origin-month daily log returns compressed with the frozen GPR-conditioned weighting rule;
- lag architecture: **L1 only**;
- canonical ChHHO baseline: **ΣAE 1413.029779 / 23/33**;
- 2025: transport/reporting only;
- 2026: quarantine/reporting only;
- random split: NONE.

F0/F1/F2/F3 results are unaffected by this reset because they used the internal governed metal/GPR contract.

## 2. What was wrong or incomplete in first F4 native design

### 2.1 Processing-parity mismatch — HIGH

The first native Rates/FX implementation mostly transformed daily external series into a single endpoint-to-endpoint monthly change.

That is not the same information architecture used by CURRENT8.

CURRENT8 does **not** feed raw levels or simple month-end changes alone. It uses:
1. a monthly-average return representation (MR1); and
2. an origin-month daily-path summary (GPR-conditioned VW).

Therefore a direct comparison of CURRENT8 versus external endpoint-change inputs was not "apple-to-apple" at the representation level.

### 2.2 Frequency under-use — HIGH

Available daily series were unnecessarily reduced or blocked in the first plan:

- Rates: daily official H.15 existed.
- FX: daily official H.10 existed.
- VIX: daily official Cboe existed.
- Nasdaq-100: daily close history is available from FRED with upstream source Nasdaq, Inc.; the earlier direct GIW credential failure did not mean daily NDX data itself was unavailable.
- WTI/Brent: daily spot history is available from FRED with upstream source U.S. EIA.

Therefore monthly-only fallback for Nasdaq and WTI/Brent is superseded for the F4 restart.

### 2.3 Optimizer-dimension parity mismatch — HIGH

Frozen ChHHO optimizer budget was calibrated on 8 inputs.

With 5 fuzzy rules:
- 8 inputs -> antecedent parameter dimension = **80**;
- 9 inputs -> **90**;
- 10 inputs -> **100**.

The first F4 runs kept:
- POP = 24
- generations = 45
- repeats = 3

unchanged as dimension increased.

This reduced optimizer evaluations per optimized parameter and can create instability/pathological solutions even when input standardization is correct.

### 2.4 Standardization itself — PASS

The ChHHO select path fits feature scaling on chronological training history and applies it to validation/target rows.

Therefore the main problem is **not** that rates are percentage points while FX is log-return. Scaling exists.

But standardization does not repair:
- wrong temporal representation;
- lost intramonth path information;
- inadequate optimizer search budget.

### 2.5 Family-wide conclusions were too strong — SUPERSEDED

The corrected Rates run and completed FX run are valid computations for the exact legacy endpoint-change implementation, but they do **not** establish that Rates or FX are economically useless.

Their family-level rejection language is superseded.

## 3. Legacy F4 evidence classification

### Rates

- run **36550570628**
- BASE parity **1413.029779 / 23/33 PASS**
- routed legacy Rates **1657.1153 / 21/33**
- classification:
  **VALID_FOR_LEGACY_ENDPOINT_REPRESENTATION_ONLY / SUPERSEDED_FOR_FAMILY_DECISION**
- it may be cited only as evidence that the old endpoint-change/native implementation failed.

Earlier Rates run **36549022859**:
**SUPERSEDED_METHODOLOGY / NOT SCIENTIFIC RESULT** because BASE history parity failed.

### FX

- run **36552598677**
- artifact **11026195076**
- digest `sha256:db389252b953b252a3a0b33fefbbc00c8e2df757ef53f25c64fcf254442d1a56`
- BASE parity **1413.029779 / 23/33 PASS**
- routed legacy FX **1811.986846 / 18/33**
- classification:
  **VALID_FOR_LEGACY_ENDPOINT_REPRESENTATION_ONLY / SUPERSEDED_FOR_FAMILY_DECISION**
- pathological static candidates are architecture/optimizer diagnostics, not literal claims that CNY or safe-haven FX has no forecasting information.

### Residual-correction screens

Earlier external residual-correction results remain valid **for the residual-correction architecture they tested**.

They are not native-input evidence and are not superseded merely because native F4 is being redesigned.

## 4. New "apple-to-apple" external feature contract

External series are assigned to a native-frequency class. No series is forced into a frequency it does not naturally have.

### Class P — daily positive price/index series

Examples:
- Nasdaq-100
- VIX
- WTI
- Brent
- broad USD index
- normalized FX quote levels

Required pair:

**P_MR1**
- compute the arithmetic mean of eligible daily levels in origin month p;
- compute the arithmetic mean in p-1;
- feature = `log(mean_level[p] / mean_level[p-1])`.

**P_VW**
- compute daily log returns inside origin month p;
- apply the **same frozen GPR-conditioned age-weighting formula** used by CURRENT8;
- use only observations available under the family release-lag rule.

This is the direct analogue of metal MR1 + VW.

### Class Y — daily yields/rates that may be zero/negative

Examples:
- nominal 10Y
- real 10Y
- nominal-real/breakeven proxy

Required pair:

**Y_MR1_ANALOG**
- feature = `mean_yield[p] - mean_yield[p-1]`.

**Y_VW_ANALOG**
- compute daily first differences in yield inside origin month p;
- apply the same frozen GPR-conditioned age weights.

No logarithm is applied to yield levels.

### Class M — native monthly statistics

Examples:
- CPI headline/core
- monthly Copper until a governed daily authority is proven

No synthetic daily interpolation is permitted.

CPI admissible transforms:
- YoY inflation;
- MoM inflation where release-safe;
- acceleration/deceleration;
- compact predeclared lags.

Copper monthly admissible transform:
- monthly-average MR1 analogue from the governed monthly price series.

## 5. Quote-direction contract for FX

All FX series must have one common economic sign before MR/VW construction:

**positive = USD strengthening**.

- broad USD: as published;
- CNY per USD: as published;
- JPY per USD: as published;
- CHF per USD: as published;
- EUR per USD quote: invert direction;
- GBP per USD quote: invert direction.

The sign transform is applied at the **daily level before** MR/VW aggregation.

## 6. Release/availability contract

Conservative origin cutoffs remain family-specific:

- Fed H.10 FX: month-end minus **7 calendar days**;
- Fed H.15 rates: month-end minus **2 calendar days**;
- Nasdaq-100 daily close: month-end minus **1 calendar day**;
- VIX daily close: month-end close permitted when available; operational pipeline may use a 1-day safety lag for forward production;
- WTI/Brent via EIA/FRED: month-end minus **7 calendar days** until a stricter historical release-time table is governed;
- CPI: use only the latest monthly observation actually admissible under the frozen CPI release rule; no same-month synthetic CPI;
- Copper monthly: conservative completed previous published month unless a release-date authority is added.

No target-month future observation is allowed.

## 7. Optimizer-parity contract

Baseline optimizer density is frozen from 8-input ChHHO:

- base parameter dimension = 80
- base POP = 24
- generations = 45
- repeats = 3
- base population evaluations per parameter per generation/repeat density is preserved.

For input count `k`:

- `D(k) = 2 × RULES × k = 10k`
- `POP(k) = ceil(24 × D(k) / 80)`

Therefore:
- 8 inputs -> POP 24
- 9 inputs -> POP 27
- 10 inputs -> POP 30
- 11 inputs -> POP 33
- etc.

Generations and repeats remain 45 and 3 unless a later optimizer audit is explicitly opened.

No external candidate may be compared with BASE under a lower evaluations-per-parameter budget.

## 8. Stability gates added before scientific scoring

Every external candidate must pass before its DEV score is interpreted:

1. canonical BASE parity = **1413.029779 / 23/33**;
2. all transformed features finite;
3. no history shortening versus BASE;
4. same train/validation chronology;
5. same output target/reconstruction;
6. optimizer density parity;
7. no target-month leakage;
8. source/frequency/release metadata attached;
9. feature summary ranges logged;
10. pathological reconstructed forecasts flagged and candidate marked **ARCHITECTURE_UNSTABLE**, not economically "bad".

## 9. Revised data readiness

Required V2 authority:

- Rates daily: Fed H.15 — READY
- FX daily: Fed H.10 — READY
- VIX daily: Cboe — READY
- Nasdaq-100 daily: Nasdaq direct historical API. — TO BE GOVERNED IN V2
- WTI daily: U.S. EIA direct daily history — TO BE GOVERNED IN V2
- Brent daily: U.S. EIA direct daily history — TO BE GOVERNED IN V2
- CPI: BLS monthly native frequency — READY
- Copper: World Bank monthly — READY_MONTHLY / DAILY_NOT_PROVEN

## 10. Restart sequence after data completion

No new external model run is authorized until B0-B2 pass.

### F4-B0 — data authority completion
Build and freeze External Authority V2 with daily Nasdaq/WTI/Brent plus existing H.10/H.15/VIX/CPI/Copper.

### F4-B1 — transform parity audit
Generate MR/VW analogues without fitting ChHHO.
Check coverage, release cutoffs, quote signs, summary ranges and leakage.

### F4-B2 — optimizer parity audit
Verify dimension-aware population rule and exact BASE parity.

### F4-B3 — Rates restart
Daily mean-change + GPR-weighted daily yield-change; predeclared compact rate blocks.

### F4-B4 — FX restart
Daily quote-normalized MR1 + GPR-VW; predeclared compact FX blocks.

### F4-B5 — VIX restart
Daily MR1 + GPR-VW.

### F4-B6 — Nasdaq restart
Daily MR1 + GPR-VW; extra representation only if predeclared before outcomes.

### F4-B7 — Energy restart
WTI signed-difference pair + Brent MR1/GPR-VW.

### F4-B8 — native-monthly families
CPI and Copper under their natural monthly frequencies.

### F4-B9 — constrained combination
Only independently promoted families may enter compact combinations.

## 11. Workflow governance

Legacy endpoint-change workflows:
- `gold-monthly-chhho-f4-rates-v1.yml`
- `gold-monthly-chhho-f4-fx-v1.yml`

are placed on **MANUAL LEGACY HOLD** and are not valid promotion workflows.

## Kontrol ve Uyum Özeti

- external family model development: **PAUSED FOR RESET**
- F0-F3 internal evidence: **VALID**
- Rates family rejection: **SUPERSEDED AS FAMILY-WIDE CLAIM**
- FX family rejection: **SUPERSEDED AS FAMILY-WIDE CLAIM**
- raw source error proven: **NO**
- processing-parity defect: **YES**
- optimizer-dimension parity defect: **YES**
- daily Nasdaq/WTI/Brent authority gap: **being closed in V2**
- next authorized action: **F4-B0 data authority completion only**

## WTI signed-transform note

WTI cannot be forced into a log-return representation because the official daily history contains non-positive observations during the 2020 dislocation. This is real market data, not a bad row. Therefore WTI uses monthly-mean price difference + GPR-weighted daily first differences. No clipping, deletion, absolute-value transform, or synthetic repair is allowed.
