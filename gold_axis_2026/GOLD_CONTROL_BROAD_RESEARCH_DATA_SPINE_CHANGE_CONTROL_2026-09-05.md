# Gold Control — Broad Research Data Spine Change Control R1

**Freeze date:** 2026-09-05  
**Branch:** `gold-control-broad-research-data-spine-r1`  
**Scope:** source/data readiness only; no model scoring, selection, ensemble, direction vote, decision or position mapping.

## 1. Why this change exists

The current production data plane is narrower than the data universe actually used in the pre-database Gold Control research implementations.

Two retained research implementations are binding evidence for this correction:

1. `gold_axis_2026/run_models.py`
   - daily `Gold`, `Silver`, `Platinum`, `Palladium` history from StakTrakr for 2010..2026;
   - true four-output MSVR using, for each metal, prior monthly return plus GPR-weighted daily return;
   - Patch research also used Fed funds, NASDAQ, USD/CNY and GPR.
2. `gold_axis_2026/run_vw_full_rebuild_v2.py`
   - broader market family including DJI, DXY, NDX, U.S. 10Y yield, S&P 500, VIX, GVZ, Barrick proxy, NEM, DZZ, GLL and HL preferred-B;
   - GPR/GPRT/GPRA and gold monthly/daily-return features;
   - unresolved GPY / exact long-term-trend / generic-volatility identities remained explicitly unresolved.

The purpose of this change is to make the database capable of reproducing the *research input universe* before any new VW/MSVR or other H=1 model is judged. It does not change the terminal status of archived `VW_MIDAS_MSVR`, `VW_MIDAS_SVR_XAU_SUCCESSOR_V1`, or `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`.

## 2. Frozen governance

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- no model score is computed by the data-spine preflight or ingestion
- no forecast/decision-store write
- no model status/promotion change
- no backdated retrieval timestamps
- no silent provider substitution
- no current/final-vintage series may be relabelled as historical PIT
- reconstructed historical data must use a separate series identity and truthful reconstruction metadata
- raw vendor market values must not be printed to CI logs or evidence summaries

## 3. Tier A — exact prior-research input recovery

### A1. Four-metal daily research panel

Upstream: `lbruton/StakTrakr`.

The old research code requested annual `spot-history-YYYY.json` files for 2010..2026 and used:

- Gold
- Silver
- Platinum
- Palladium

For the governed historical reconstruction the upstream repository is pinned to the verified pre-research-run data refresh commit:

`429d8e612d504a964846ff6438dbdb28ace630c3`

That commit is dated 2026-08-19 and refreshed the 2026 spot bundle. It is used only as a reproducible reconstruction anchor before the retained 2026-08-26 research implementation. It is **not** evidence that the same payload was available unchanged at every historical forecast origin and therefore does **not** create a historical PIT claim.

Separate research identities are reserved:

- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`

### A2. XAU hourly-derived 17:00 ET daily research line

The V2 source preflight already proved Twelve Data hourly history for 54/54 months from `2022-03` through `2026-08`.

The persistent research identity is reserved as:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Construction is frozen to the V2 research semantics:

- provider symbol `XAU/USD`;
- interval `1h`;
- provider timezone `America/New_York`;
- select bar timestamp `16:00:00` as the hourly bar ending at 17:00 ET;
- source window `2022-03..2026-08`;
- at least 15 selected daily references per required month.

This is a research lineage and is **not** identical to production `XAU_EOD_TWELVE_NY17`, whose canonical decision reference is derived from the exact 16:59 1-minute bar.

### A3. GPR companion historical vintages

`GPR_OFFICIAL_GIT_PIT` already has 54/54 governed origin vintages in Neon. The same exact official archive workbooks will be preflighted for the companion columns used by the broader VW research:

- `GPRT_OFFICIAL_GIT_PIT`
- `GPRA_OFFICIAL_GIT_PIT`

For each origin `p` in `2022-03..2026-08`, the exact archived workbook/commit already proven for GPR must contain the companion series and the required `p-1` observation. Availability remains the earliest official archive-add commit floor; retrieval/first-seen remain the true reconstruction time.

No companion series is persisted unless all 54 required origins pass the source-only preflight.

### A4. Existing broad market families

The preflight must inventory, without relabelling, current Neon coverage for the research families already present, including:

- `DJIA_FRED`, `NASDAQ100_FRED`, `SP500_FRED`;
- `DGS10_ALFRED_PIT_ME`, `DFF_ALFRED_PIT_ME`, `DEXCHUS_ALFRED_PIT_ME`, `NASDAQ100_ALFRED_PIT_ME`;
- `BARRICK_B_TWELVEDATA`, `NEM_TWELVEDATA`, `DZZ_TWELVEDATA`, `GLL_TWELVEDATA`, `HL_PB_TWELVEDATA`;
- `VIX_CBOE`, `GVZ_CBOE`.

A broad trade-weighted dollar index is not silently renamed `DXY`, and monthly ALFRED series are not silently relabelled as the old Yahoo daily market proxies.

## 4. Tier B — broader research universe, not yet promoted to Tier A

The prior research also identified the following high-value families for future H=1 research:

- 10Y TIPS real yield (`DFII10`);
- nominal Treasury curve (`DGS2`, `DGS5`, `DGS10`, `DGS30`);
- breakevens (`T5YIE`, `T10YIE`);
- broad USD / exact DXY under separate identities;
- CPI/PCE and release-surprise features;
- VIX/MOVE and uncertainty/stress;
- ETF holdings/flows;
- central-bank / WGC demand flows;
- CFTC positioning;
- futures curve/basis/carry;
- options IV/skew;
- oil/silver/copper cross-commodity context;
- M2/global-liquidity features.

Tier B is a source-contract backlog. None of these may be inserted into an existing model or scored until its own source/PIT/availability contract is frozen.

## 5. R1 preflight gate

Before any Tier-A production database persistence:

1. StakTrakr pinned annual files 2010..2026 must parse and produce a non-empty common four-metal daily panel through July 2026;
2. Twelve hourly XAU research line must pass 54/54 monthly coverage with >=15 selected references per month;
3. GPRT and GPRA must each pass 54/54 exact-vintage `p-1` coverage using the already-proven GPR archive identities;
4. existing broad-market Neon coverage must be recorded as metadata/counts only;
5. evidence must contain no raw market values;
6. `database_writes = NONE` and `model_scores = NONE`.

Only after this preflight is `SUCCESS` may a separate append-only research ingestion step be created.

## 6. Stop rule

Any failed Tier-A source gate stops the ingestion work. Do not relax dates, substitute a provider, change a series identity, or score a model to compensate for missing data.
