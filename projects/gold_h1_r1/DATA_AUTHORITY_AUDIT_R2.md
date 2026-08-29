# GOLD H1 R1 — Data Authority Audit R2

Date: 2026-08-29

## Scope
Audit whether the data used in the current monthly reversal study are internally canonical, reproducible, origin-safe, and externally authority-verified.

## Findings

### 1. Canonical monthly target — INTERNAL CONSISTENCY: PASS
`GOLD_H1_R1_CANONICAL_DATASET_V1.xlsx` contains 390 monthly rows from 1994-02 through 2026-07. Audit checks show:
- required core missing rows = 0
- 43 evaluation origins
- 43/43 target reconciliation exact
- origin-safe feature missing = 0
- canonical Stage-4 RW/3M rebuild ready

The operational target is `GOLD_USD_OZ` monthly average, forecast one calendar month ahead from the previous completed month-end.

### 2. 3M Momentum reconstruction — PASS
The archived Stage-4 audit reports:
- actual reconciliation 43/43 exact
- RW reconciliation 43/43 exact
- Momentum reconciliation 43/43, max numerical difference about 4.9e-09

Therefore the 2023 reversal audit used the project's canonical monthly target correctly.

### 3. Canonical monthly target — EXTERNAL AUTHORITY PROVENANCE: PARTIAL / NOT FULLY PROVEN
The canonical monthly target lineage points to a locked local file:
`IDMA_ALTIN_VERI_PANELI_V3_2026-07_TAM_CORE5.xlsx / Aylik_Panel`
with a stored content hash. This proves immutability/reproducibility of the local target series, but the current canonical workbook does not independently establish that every monthly target observation is an official LBMA PM monthly average.

Independent LBMA public evidence reports the actual 2023 LBMA PM annual average gold price as USD 1,940.54. The simple arithmetic mean of the project's twelve rounded 2023 monthly target values is USD 1,942.75. These are close (about +0.11%), but they are not an exact like-for-like reconciliation because an annual LBMA business-day average is not equal to an unweighted mean of rounded monthly averages. Therefore this is only a plausibility cross-check, not proof of exact authority provenance.

Status: `MONTHLY_TARGET_EXTERNAL_AUTHORITY = PARTIAL / NOT_FULLY_PROVEN`.

### 4. Pinned StakTrakr daily precious-metals source — SOURCE LOCK PASS, PROVIDER LABEL CORRECTION REQUIRED
The exact Git commit is pinned:
`lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`.

However, the old canonical note saying all precious-metal rows have provider=LBMA is false for later history. Raw 2026 inspection showed provider/source transitions including LBMA, MetalPriceAPI and StakTrakr/sqld, plus calendar/weekend observations.

This raw chain must not be treated as a homogeneous official LBMA daily series and must not be used blindly for daily regime detection.

### 5. Tactical XAUUSD source
Pinned source:
`simom1/XAUUSD-history@f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0`.

Frozen Tactical R1 contract:
- Slow: sign(completed weekly close - SMA4 completed weekly closes), two completed-week persistence.
- Fast: sign(daily market close - SMA20 completed market-day closes), two market-day persistence.

Known source audit:
- W1 is usable historically but becomes partial/unreliable in spring/summer 2026.
- D1 was used for recent 2026 diagnostic reconstruction.
- The full 2010-2022 event-level canonical Tactical panel with weekly gap strength and persistence is not yet stored.

Therefore the next reversal-discriminator study must not use a hand-written or partially remembered weekly table.

## Decision
- Current monthly reversal audit numbers: `PASS_PROJECT_CANONICAL`.
- Claim that monthly target is fully reconciled to an authoritative official LBMA history: `NOT_FULLY_PROVEN`.
- Claim that pinned StakTrakr daily history is homogeneous LBMA data: `REJECT`.
- Weekly event-level reversal work: proceed only after rebuilding a canonical 2010-2022 event panel from pinned market-day data and cross-checking W1 against D1-derived week-ending closes.

## Required next data gate
Before fitting any weekly reversal discriminator:
1. Build completed-week close series from pinned D1 market-day closes for 2010-2022.
2. Independently compare those week-ending closes to pinned W1 on overlapping completed weeks.
3. Quantify exact-match/tolerance rate, missing weeks, duplicates, date-label alignment and outliers.
4. Reconstruct Tactical R1 states from the D1-derived weekly series.
5. Reconcile aggregate CONFIRM/CONFLICT/NEUTRAL counts against the archived Tactical validation workbook.
6. Only if reconciliation passes, freeze the event panel and begin reversal-strength modeling.

Until this gate passes: `WEEKLY_REVERSAL_MODEL_FIT = BLOCKED_DATA_GATE`.
