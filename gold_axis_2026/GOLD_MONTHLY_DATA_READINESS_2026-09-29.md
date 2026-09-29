# GOLD MONTHLY FORECAST — DATA READINESS FOR FEATURE-ARCHITECTURE RESEARCH

**Date:** 2026-09-29  
**Status:** COMPLETE FOR F0–F4 CORE PROGRAM / ZERO NEON  
**Role:** Governing data-readiness record before native feature/representation/lag experiments

## 1. Binding result

The data side is ready to begin the ChHHO-ANFIS feature-architecture research program without waiting for Neon.

Two governed offline/public stores are now available:

1. **Frozen DEV snapshot** for the existing four-metal + GPR + Gold target contract.
2. **Direct external store** for rates, FX, VIX, realized CPI, and commodity/oil history.

One feature family remains deliberately not proven:
- long-history **survey-consensus CPI surprise**.
No synthetic consensus will be created.

Nasdaq is usable at **monthly** frequency from the locked CORE5 history. Credential-free long-history daily NDX was not proven; daily Nasdaq volatility/MIDAS therefore remains blocked, while monthly level/return/momentum experiments are authorized.

## 2. Canonical existing model-data layer

Frozen DEV snapshot:
- schema: `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`
- payload SHA256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`
- run: **36456042954**
- artifact: **10985453248**
- Neon use during downstream experiments: **0**

Contains:
- four-metal daily common history through 2024-12;
- monthly Gold target/history;
- exact required GPR PIT DEV vintages;
- enough information for CURRENT8 reconstruction;
- enough daily metal information for momentum, realized volatility, range, and causal distributed/MIDAS-style representations.

## 3. Current public extension / 2026 forward layer

Successful refresh run:
- run **36531420723**
- public bundle artifact **11015874673**
- Neon reads: **0**
- four-metal public extension: **2025-01-02..2026-09-28**
- World Bank monthly Gold: through **2026-08**
- August 2026 World Bank Gold monthly average: **4411.0**
- official GPR vintages available in the bundle: **2026-08, 2026-09**

Forward results remain:
- September 2026 ChHHO: **4592.06**
- September 2026 DE-ABC: **4569.91**
- October provisional ChHHO: **4257.33**
- October provisional DE-ABC: **4249.36**

October is not a final month-end-origin forecast.

## 4. Direct long-history external store

Successful scientific/data gate:
- workflow: `Gold Monthly Direct External Store V1`
- run **36533719167**
- commit **6909edb79386c56e4a33bf614deb244117c5a988**
- artifact **11018030682**
- artifact digest: `sha256:9181d4a8a346d9594ec5105ae23ed9c7251b463cfd60064a55fbda0fc819af48`
- payload SHA256: `c52670ccf7bccc75e7c92e6d8261fe25d2d8c62b986300d45d5f264a26142353`
- Neon reads: **0**

### Rates
Official Federal Reserve H.15 DDP:
- daily history: **2010-01-04..2026-09-25**
- rows: **4186**
- nominal 10Y: `RIFLGFCY10_N.B`
- real 10Y: `RIFLGFCY10_XII_N.B`
- package SHA256: `84460702e8e9b8934a0f16d611e8b9bfaa82576d3a44cf1fee1f42db358607dc`

Authorized representations may include:
- nominal level/change;
- real-yield level/change;
- nominal-real spread/breakeven proxy;
- compact lags;
- daily distributed/MIDAS representation.

Fed Funds monthly history is available from CORE5 for the common research span.

### FX
Official Federal Reserve H.10 DDP:
- history: **2010-01-04..2026-09-25**
- rows: **4187**
- EUR, GBP, JPY, CHF, CNY, broad USD.
- rates payload SHA256: `89038c942aa0d879127ccb4387f757150e0e588288af99d6b60690f9cc451008`
- index payload SHA256: `f63c9896c0d26285b0b852c17d67c4b9c07e956fbb791b3a98c63088636cac54`

Authorized representations may include:
- 1M return;
- 3M/6M momentum;
- breadth;
- dispersion;
- safe-haven rotation;
- daily distributed/MIDAS representation.

### VIX / equity-risk context
Official Cboe VIX history:
- **2010-01-04..2026-09-28**
- rows: **4242**
- payload SHA256: `f121a51697d7c90ab95e0583f21e87a38839357349c7bb7e5b7ce3e592540f9b`

### Inflation
U.S. BLS Public Data API:
- headline CPI NSA: `CUUR0000SA0`
- core CPI NSA: `CUUR0000SA0L1E`
- history: **2010-01..2026-08**
- months: **199**
- 2010–2019 payload SHA256: `d5fbd26be079cfac680e695649a382af0a787ffcfa7f3cf93efa114f8f4ea911`
- 2020–2026 payload SHA256: `85b61586e22006515a2520b88330b23d8c3f873ff744a0f7af9985a50afb8057`

Authorized representations:
- headline/core YoY;
- MoM or multi-month momentum where causally available;
- acceleration/deceleration;
- lags.

**Survey-consensus surprise:** `NOT_PROVEN_LONG_HISTORY`.
The existing 2022+ compact surprise snapshot remains usable for screening evidence only. It must not be silently backfilled with invented consensus.

### Commodity / oil
World Bank Pink Sheet:
- **2010-01..2026-08**
- months: **200**
- Brent;
- WTI;
- crude-oil average;
- copper.
- workbook SHA256: `9fdcfa8a2aed9a1bb545a10c1a5ce036c6a0acd4766f450424ca800b4b5a0225`

Commodity/oil status is therefore upgraded from `DATA_NOT_READY` to **READY_WORLD_BANK_MONTHLY**.

### Nasdaq
Binding monthly fallback:
- source: locked CORE5 monthly research snapshot;
- **2010-01..2026-07** for the current research span;
- role: monthly Nasdaq level/return/momentum experiments.

Credential-free official GIW daily long history was not available:
- status: **DAILY_NASDAQ_NOT_PROVEN**
- do not use a synthetic or silently substituted daily series.

Therefore:
- Nasdaq monthly level: READY
- 1M return: READY
- 3M/6M momentum: READY
- monthly rolling volatility based on monthly returns: READY
- daily realized volatility / daily drawdown / daily MIDAS: **BLOCKED_NOT_PROVEN**

## 5. Feature-research authorization

The following research can start now:

### F0
Frozen CURRENT8 ChHHO parity.

### F1
CURRENT8 necessity/ablation:
- MR-only;
- VW-only;
- leave-one-metal-out;
- compact metal subsets;
- single-feature ablation where justified.

### F2
Metal representation:
- 1M return;
- 3M/6M momentum;
- realized volatility;
- daily range;
- absolute-return activity;
- existing VW;
- causal distributed/MIDAS.

### F3
Lag architecture:
- L1;
- compact L1-L2/L1-L3;
- selected sparse longer lags;
- distributed/MIDAS lags.

### F4 external families
Authorized:
- nominal/real rates;
- FX;
- VIX;
- realized headline/core CPI;
- Nasdaq monthly;
- WTI/Brent/copper commodity context.

Not authorized without new evidence:
- synthetic long-history CPI survey surprise;
- daily long-history Nasdaq features.

## 6. Supersession

The earlier `Gold Monthly Long-History Market Drivers V1` FRED-heavy workflow attempts are:
**SUPERSEDED_TECHNICAL_PROVIDER_FAILURE / NOT MODEL RESULTS**.

Reason:
- repeated FRED download endpoint timeouts in GitHub Actions;
- no scientific result or model score was produced.

The successful direct-authority store run **36533719167** supersedes those retrieval attempts.

Earlier manifest statements that commodity/oil was `DATA_NOT_READY` and that no long-history external store existed are historical and superseded by this report.

## 7. Governance

- Random split: **NONE**
- DEV selection authority: **2022-04..2024-12**
- 2025 tuning/selection: **NONE**
- 2026 tuning/selection: **NONE**
- Neon reads in new stores: **0**
- synthetic missing-value fill: **NONE**
- synthetic CPI consensus: **NONE**
- inaccessible daily Nasdaq silently substituted: **NO**
- raw/low-transform data retained where available: **YES**
- transformations/lags to be selected inside chronological experiment only: **YES**

## 8. Kontrol ve Uyum Özeti

Data readiness for ChHHO F0–F4 core program: **PASS**.

The only deliberately unresolved optional feature lanes are:
1. long-history survey-consensus CPI surprise;
2. long-history daily Nasdaq volatility/MIDAS.

Neither blocks the planned first scientific feature-architecture program.
