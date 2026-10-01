# GOLD INTRAMONTH OPPORTUNITY — Stage 2 Label, Baseline & Feature Contract

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Canonical project:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

## 1. Purpose

Construct the first governed intramonth-opportunity dataset and quantify whether meaningful short-horizon upside excursions actually occur inside months where the frozen monthly ChHHO forecast is DOWN.

No complex opportunity model is selected in Stage 2.

## 2. Frozen chronology

Official Borsa İstanbul history begins in 2011.

Project split:
- **2011-01-01..2021-12-31:** background / training-history pool
- **2022-01-01..2024-12-31:** **DEV selection authority**
- **2025-01-01..2025-12-31:** frozen transport / reporting only
- **2026:** OPENED retrospective stress; never selection

Reason for DEV 2022-2024:
- aligns with the governed monthly ChHHO canonical DEV target period;
- permits honest monthly-context comparison;
- keeps 2025 outside selection.

## 3. Core price authority

Endpoint:
`https://www.borsaistanbul.com/metal-fiyatlari.php`

Operation:
`op=fetchMetalFiyatlari`

Metal codes:
- AU Gold
- AG Silver
- PT Platinum
- PD Palladium

Governed row filter:
- `priceRef == MTL`
- `priceCurrency == USD`
- `priceWeight == OZ`

Target calendar:
- official Gold MTL/USD/OZ observation dates.

Cross-metal features:
- use each companion metal's latest official observation available on or before the Gold origin date;
- never future-fill;
- record age/staleness.

## 4. Opportunity origin

For Gold observation index t:
- `P0 = Gold[t]`
- signal date = next official Gold observation date;
- future h-path = `Gold[t+1] ... Gold[t+h]`.

This matches the frozen 00:30 Istanbul issue-time concept: P0 is already known and the next Gold observation is not.

## 5. Continuous labels

For h in {1,3,5,10}:

`MFE_h = max_{k=1..h} log(P[t+k]/P0)`

`MAE_h = min_{k=1..h} log(P[t+k]/P0)`

Also report percentage form:
- `MFE_PCT_h = 100*(exp(MFE_h)-1)`
- `MAE_PCT_h = 100*(exp(MAE_h)-1)`.

Primary continuous labels:
- MFE_5
- MAE_5.

## 6. Frozen opportunity-event candidate family

Origin-known Gold risk scale:

`SIGMA20 = std(last 20 Gold one-observation log returns through origin t)`

Five-day scale:

`SCALE5 = SIGMA20 * sqrt(5)`

Pre-registered event candidates:

- **K050:** `MFE_5 >= 0.50 * SCALE5`
- **K075:** `MFE_5 >= 0.75 * SCALE5`
- **K100:** `MFE_5 >= 1.00 * SCALE5`

No 2025/2026 outcome may choose among K050/K075/K100.

Stage 2 only measures prevalence/base rates. Final primary binary threshold may be selected later using 2022-2024 DEV only and then frozen before 2025 transport.

## 7. Frozen descriptive excursion diagnostics

For business interpretation only, report whether each monthly forecast month contains at least one origin with future 5-observation MFE of:

- >= 1%
- >= 2%
- >= 3%.

These fixed percentages are **descriptive diagnostics**, not model-label selection thresholds.

## 8. Monthly ChHHO context

Frozen source:
- ANFIS Stage3C ChHHO artifact
- workflow run **36251783712**
- artifact id **10989389723**
- model `VW_MIDAS_CHHHO_ANFIS_V1`.

Monthly context direction:
- DOWN iff frozen `pred_log_return_gold < 0`
- UP iff > 0.

Join:
- daily signal belongs to monthly target YYYY-MM of its signal date;
- only target months present in the frozen ChHHO rows may be classified as monthly UP/DOWN.

Primary subset:
- DEV daily origins whose signal month has ChHHO **DOWN**.

2025 monthly rows are reporting/transport only.

## 9. Stage-2 core feature block

Gold:
- R1
- R3
- R5
- R10
- R21
- RV20
- ABSRET20
- drawdown from trailing 21-observation high
- distance from trailing 21-observation low
- short reversal: R1 - R5/5

Companion metals:
- latest causal R1 / R5 / R21 for Silver, Platinum, Palladium
- staleness age in calendar days.

Cross-metal:
- R1 breadth
- R5 breadth
- R1 dispersion
- R5 dispersion
- Gold-minus-companion mean R1/R5 divergence.

Macro/risk as-of blocks remain authorized by Stage 1 but are not required to pass the first core-label audit. They enter the Stage-2B release-aware snapshot after the core target/label gate is verified.

## 10. Baselines

Event-probability baselines:
- expanding prior prevalence, minimum warmup 252 Gold observations;
- trailing-252 prevalence.

Continuous baselines:
- expanding prior median MFE_5 / MAE_5;
- trailing-252 median MFE_5 / MAE_5.

No future labels may enter any baseline.

## 11. Required Stage-2A outputs

1. BIST four-metal source panel
2. Gold-calendar causal feature/label table
3. coverage + duplicate + missing audit
4. MFE/MAE distributions
5. K050/K075/K100 prevalence
6. monthly ChHHO UP/DOWN join for DEV and 2025
7. monthly-DOWN opportunity prevalence
8. percentage excursion diagnostics (1/2/3%)
9. baseline metrics
10. immutable artifact hashes.

## 12. Promotion gate

Stage 2A PASS requires:
- stable official Gold target extraction;
- no duplicate Gold dates after filter;
- future-label construction exact;
- no 2025/2026 selection;
- monthly context sourced from frozen ChHHO artifact;
- enough DEV positives and negatives to support later modeling.

If the binary event is nearly always 0 or 1 under all candidate thresholds, do not force a classifier; redesign the label on DEV only.
