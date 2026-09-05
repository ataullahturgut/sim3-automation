# Gold Control — Broad Research Data Spine Change Control R1

**Freeze date:** 2026-09-05  
**Branch:** `gold-control-broad-research-data-spine-r1`  
**Scope:** source/data readiness only; no model scoring, selection, ensemble, direction vote, decision or position mapping.

## 1. Why this change exists

The current production data plane is narrower than the data universe actually used in the pre-database Gold Control research implementations.

Binding retained evidence is now reconciled from both code and the canonical research dataset:

1. `gold_axis_2026/run_models.py`
   - daily `Gold`, `Silver`, `Platinum`, `Palladium` history for 2010..2026;
   - true four-output MSVR using prior monthly returns plus GPR-weighted daily returns;
   - the broader research path also used the locked CORE5 monthly block containing gold monthly average, Fed funds, NASDAQ average, USD/CNY average and GPR.
2. `GOLD_H1_R1_CANONICAL_DATASET_V1.xlsx`
   - `Source_Lineage` identifies `CORE5_MONTHLY` as the locked common monthly source, 390 rows from 1994-02 through 2026-07;
   - `Source_Lineage` identifies `PRECIOUS_METALS_DAILY_PINNED` as `lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, annual files 2010..2026;
   - the same dataset explicitly labels current GPR/GPRT/GPRA history as not point-in-time vintage, so it is not reused as PIT authority.
3. `gold_axis_2026/run_vw_full_rebuild_v2.py`
   - broader market family including DJI, DXY, NDX, U.S. 10Y yield, S&P 500, VIX, GVZ, Barrick proxy, NEM, DZZ, GLL and HL preferred-B;
   - GPR/GPRT/GPRA and gold monthly/daily-return features;
   - unresolved GPY / exact long-term-trend / generic-volatility identities remain explicitly unresolved.

The purpose is to make Neon capable of reproducing the actual research input universe before any new VW/MSVR or other H=1 model is judged. This change does not alter the terminal statuses of archived `VW_MIDAS_MSVR`, `VW_MIDAS_SVR_XAU_SUCCESSOR_V1`, or `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`.

## 2. Frozen governance

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- no model score is computed by the data-spine preflight or ingestion
- no forecast/decision-store write
- no model status/promotion change
- no backdated retrieval timestamps
- no silent provider substitution
- no current/final-vintage series may be relabelled as historical PIT
- reconstructed historical data must use separate research identities and truthful reconstruction metadata
- raw vendor market values must not be printed to CI logs or evidence summaries

## 3. Tier A — actual prior-research input recovery

### A0. Locked CORE5 monthly research block

Repository artifact: `gold_axis_2026/core5_monthly.csv.gz.b64`.

Required exact shape:

- 390 monthly rows;
- 1994-02 through 2026-07;
- gold monthly average;
- Fed funds;
- NASDAQ average;
- USD/CNY average;
- rounded GPR core field.

This is preserved as a **locked research snapshot**, not relabelled as historical PIT. Separate Neon research identities are reserved for each column so the old research matrix can be rebuilt without silently replacing the source.

### A1. Four-metal daily research panel

Upstream: `lbruton/StakTrakr`.

The exact research source lock recovered from `GOLD_H1_R1_CANONICAL_DATASET_V1.xlsx / Source_Lineage` is:

`ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

The annual files are `spot-history-2010.json` through `spot-history-2026.json`, using:

- Gold
- Silver
- Platinum
- Palladium

The panel is retained through 2026-07-31 for parity with the old model run. The pinned payload is a reproducible historical research source, **not** evidence that the same payload was known unchanged at every earlier forecast origin.

Separate research identities are reserved:

- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`

### A2. XAU hourly-derived 17:00 ET daily research line

The prior V2 source preflight proved Twelve Data hourly XAU history for 54/54 months from `2022-03` through `2026-08`.

Persistent research identity:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Frozen construction:

- provider symbol `XAU/USD`;
- interval `1h`;
- provider timezone `America/New_York`;
- select timestamp `16:00:00` as the hourly bar ending at 17:00 ET;
- 2022-03..2026-08;
- at least 15 selected daily references per required month.

This research lineage is **not** identical to production `XAU_EOD_TWELVE_NY17`, whose canonical decision reference is derived from the exact 16:59 1-minute bar.

### A3. GPR companion historical vintages

`GPR_OFFICIAL_GIT_PIT` already has 54/54 governed origin vintages in Neon. The same exact official archive workbook/commit identities are used to preflight:

- `GPRT_OFFICIAL_GIT_PIT`
- `GPRA_OFFICIAL_GIT_PIT`

For every origin `p` in `2022-03..2026-08`, the exact archive workbook must contain the companion column and required `p-1` observation. Availability remains the earliest official archive-add commit floor; retrieval/first-seen remain the true reconstruction time.

### A4. Existing broad-market inventory

The preflight inventories, without relabelling, current Neon coverage for:

- `DJIA_FRED`, `NASDAQ100_FRED`, `SP500_FRED`;
- `DGS10_ALFRED_PIT_ME`, `DFF_ALFRED_PIT_ME`, `DEXCHUS_ALFRED_PIT_ME`, `NASDAQ100_ALFRED_PIT_ME`;
- `BARRICK_B_TWELVEDATA`, `NEM_TWELVEDATA`, `DZZ_TWELVEDATA`, `GLL_TWELVEDATA`, `HL_PB_TWELVEDATA`;
- `VIX_CBOE`, `GVZ_CBOE`.

A broad trade-weighted dollar index is not renamed `DXY`; monthly ALFRED series are not relabelled as the old daily market proxies. Missing historical coverage is reported rather than patched silently.

## 4. Tier B — broader research backlog, not yet a proven old-model input contract

The earlier research also identified high-value future H=1 data families:

- 10Y TIPS real yield (`DFII10`);
- nominal Treasury curve (`DGS2`, `DGS5`, `DGS10`, `DGS30`);
- breakevens (`T5YIE`, `T10YIE`);
- exact DXY under its own identity;
- CPI/PCE and release-surprise features;
- VIX/MOVE and uncertainty/stress;
- ETF holdings/flows;
- central-bank / WGC demand flows;
- CFTC positioning;
- futures curve/basis/carry;
- options IV/skew;
- oil/silver/copper cross-commodity context;
- M2/global-liquidity features.

These are research candidates, not silently asserted as exact archived VW inputs. Each requires its own source/PIT/availability contract before model use.

## 5. R1 preflight gate

Before any append-only research persistence to production Neon:

1. locked CORE5 must parse as exactly 390 months, 1994-02..2026-07, with all five required research columns;
2. StakTrakr at the exact canonical research commit `ed2e549...` must produce the common four-metal daily panel through July 2026;
3. Twelve hourly XAU must pass 54/54 monthly coverage with >=15 selected 16:00 ET references per month;
4. GPRT and GPRA must each pass 54/54 exact-vintage `p-1` coverage;
5. existing broad-market Neon coverage is recorded as metadata/counts only;
6. evidence contains no raw market values;
7. `database_writes = NONE` and `model_scores = NONE`.

Only after this preflight is `SUCCESS` may a separate append-only research ingestion step be created.

## 6. Stop rule

Any failed Tier-A gate stops ingestion. Do not relax dates, substitute a provider, change a series identity, reinterpret a locked local snapshot as PIT, or score a model to compensate for missing data.
