# GOLD DAILY FORECAST — Stage 1 Daily Data Authority & PIT Audit Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PASS WITH OPTIONAL-FAMILY RESTRICTIONS**  
**Authority:** `GOLD_DAILY_FORECAST_STAGE1_DATA_AUTHORITY_PIT_AUDIT_2026-10-01.md`

## 1. Binding decision

The daily project now has a governed core price identity and may advance to Stage 2.

### Governed daily target

**Borsa İstanbul Precious Metals Market — Gold Metal Price, USD/ONS**

Interpretation:
- this is the official Borsa İstanbul Precious Metals Market daily Gold metal price in USD per ounce;
- it is used as the governed daily XAU/USD reference for this project;
- it is **not** described as the global OTC spot close or LBMA PM price.

Borsa İstanbul states that Metal Prices are available from **2011-01-01** and are computed separately for each precious metal / price type from T+0 transactions as a weighted-average price. If no qualifying transaction occurs, the latest/current international price present at bulletin publication is used.

The same official framework covers:
- Gold
- Silver
- Platinum
- Palladium.

This removes the prior need to treat the four-metal core as StakTrakr historical reconstruction.

## 2. Why LBMA is not the primary development target

LBMA/IBA is the international benchmark authority:
- Gold is set twice daily at 10:30 and 15:00 London time;
- Silver once daily at 12:00;
- Platinum/Palladium twice daily at 09:45 and 14:00.

However, historical tabulated LBMA precious-metal price data require the relevant IBA licence / MyLBMA access.

Therefore:
- LBMA may be retained as benchmark/context;
- it is **not** the primary open-data development target under the current project contract.

## 3. Operational daily forecast timestamp

Frozen operational issue time:

**00:30 Europe/Istanbul on each Borsa İstanbul target business date D**

Forecast target:
- the official Borsa İstanbul Gold Metal Price USD/ONS published for business date D after that day's precious-metals session/end-of-day processing.

This means the model forecasts the next Borsa İstanbul daily Gold reference using all information that was public by 00:30 Istanbul on the target date.

Rationale:
- previous Borsa İstanbul metal prices are already final;
- prior U.S. market close is complete;
- Federal Reserve H.15 16:15 ET release is available even during U.S. standard time by approximately 00:15 Istanbul;
- 00:30 provides a fixed safety buffer.

No same-target-day Borsa metal information is permitted.

## 4. Target calendar

Primary calendar:
- Borsa İstanbul Precious Metals Market official Gold Metal Price publication dates.

Rules:
- weekends: excluded;
- official Borsa holidays: excluded if no official Metal Price is published;
- half-days: retained only when an official Gold Metal Price is published;
- no synthetic weekend rows;
- no backward fill;
- target date is the next Borsa İstanbul date with an official Gold Metal Price.

Four-metal core row:
- require official Gold target and official Gold/Silver/Platinum/Palladium Metal Price observations for the previous usable Borsa date;
- if a core metal observation is absent, do not silently fill it from a future date.

## 5. Source/PIT matrix

| Family | Authority | Historical scope | Daily availability rule at 00:30 Istanbul | Stage-2 status |
|---|---|---|---|---|
| Gold/Silver/Platinum/Palladium | Borsa İstanbul Precious Metals Market Metal Prices | from 2011-01-01 | prior official Borsa publication only | **READY / CORE** |
| Nominal 10Y | Federal Reserve H.15 | long daily history | latest H.15 observation published by origin; H.15 posts weekdays 16:15 ET | **READY_LAGGED** |
| Real 10Y | Federal Reserve H.15 inflation-indexed yield | long daily history | latest published H.15 value only | **READY_LAGGED** |
| Breakeven proxy | nominal 10Y - real 10Y | derived | derived only from jointly available published H.15 values | **READY_LAGGED** |
| Broad USD / major FX | Federal Reserve H.10 | daily observations; official history | H.10 is released Monday 16:15 ET for prior business week; use latest released batch only | **READY_WEEKLY_PIT** |
| VIX | Cboe official VIX daily close | 1990-present | prior completed U.S. close | **READY** |
| Nasdaq-100 | Nasdaq official NDX Index History | official daily index history | prior completed U.S. close | **READY** |
| WTI | EIA Cushing WTI daily closing spot | 1986-present | source history ready, but observation-date != guaranteed public-date; historical release mapping required | **SOURCE_READY / PIT_MAPPING_BLOCKED** |
| Brent | EIA Europe Brent daily closing spot | 1987-present | same restriction as WTI | **SOURCE_READY / PIT_MAPPING_BLOCKED** |
| GPR daily | Caldara-Iacoviello Recent GPR daily vintages | recent daily series; archived vintages | use only a daily vintage whose update date <= forecast origin | **READY_PIT_VINTAGES** |
| GPR monthly | Caldara-Iacoviello monthly vintages | long monthly history | use only published vintage available by origin | **READY_PIT_VINTAGES** |
| LBMA metals | LBMA/IBA benchmarks | long benchmark history | historical tabular access requires licence | **BENCHMARK_ONLY / LICENCE_BLOCKED** |
| StakTrakr metals | prior project reconstruction | project-specific | no longer core authority | **RESEARCH_COMPARATOR_ONLY** |

## 6. Important release-timing rules

### Federal Reserve H.15

The Board states:
- H.15 is posted Monday-Friday at **16:15 ET**;
- current release carries the preceding available market observations.

Rule:
- do not join an H.15 value by observation date alone;
- at each daily origin use the latest H.15 value that had actually been released.

### Federal Reserve H.10

The Board states:
- H.10 bilateral FX rates and dollar indexes are released **Mondays at 16:15 ET** for the previous business week.

Rule:
- date-labelled H.10 daily values are **not contemporaneously known every day**;
- daily backtests must join H.10 by publication batch, not by observation date.

This is a major leakage safeguard.

### VIX / Nasdaq-100

At the 00:30 Istanbul issue time:
- previous U.S. market session is complete;
- use only that completed close / index value;
- never use same-date U.S. data that will occur later after the daily Gold forecast is issued.

### EIA WTI / Brent

EIA provides long official daily closing spot-price histories:
- WTI Cushing from 1986;
- Europe Brent from 1987.

However, the public table is released/updated in batches and date-labelled price t cannot automatically be treated as known on t.

Decision:
- WTI/Brent are excluded from Stage-2 baseline feature blocks until a historical available-date mapping or conservative release-lag contract is implemented.
- no silent same-day oil join.

### GPR

Official GPR site:
- monthly data updated at the beginning of each month;
- Recent GPR daily data updated every Monday;
- older monthly and daily vintages are archived.

Decision:
- daily project may use the **daily Recent GPR** under vintage-date filtering;
- monthly GPR remains available as a slow state feature;
- latest-restated history must never be used as if it were point-in-time history.

## 7. Missing / holiday / stale rules

Core Borsa prices:
- no forward/backward synthetic fill for missing target/core rows;
- target rows require official Gold price;
- four-metal feature block uses previous usable official Borsa observations.

Optional asynchronous sources:
- latest **published** value may be carried forward causally;
- record `AGE_DAYS` / staleness for every carried source;
- never backfill from a later release;
- optional source missingness must be explicit.

H.10:
- carry latest published weekly batch until next official release;
- staleness is expected and must be represented.

H.15:
- carry only latest released daily observation.

VIX / NDX:
- use previous completed U.S. session;
- on U.S. holidays carry latest completed close with age flag if the Borsa target day remains open.

## 8. Development-period implication

Official Borsa four-metal Metal Prices begin 2011-01-01.

Therefore the project has sufficient pre-2026 history for:
- long development sample;
- chronological train/validation;
- multiple market regimes;
- no dependence on the reconstruction-only daily V1/V2 metal history.

Exact DEV/train windows remain Stage-2 decisions and must not use 2026 outcomes.

## 9. Stage-1 gate

Required:
- usable Gold target identity: **PASS**
- pre-2026 development history: **PASS**
- at least one valid baseline feature source: **PASS**
- optional blocked families explicitly identified: **PASS**
- forecast timestamp frozen: **PASS**
- calendar rules frozen: **PASS**
- no silent proxy substitution: **PASS**

**STAGE 1 = PASS**

Optional restrictions:
- WTI/Brent blocked pending PIT available-date mapping;
- LBMA history blocked without licence;
- StakTrakr removed from core authority.

## 10. Exact next stage

**Stage 2 — Baseline & Daily Feature Contract**

Stage 2 must:
- extract/freeze the Borsa İstanbul four-metal daily panel;
- run coverage/common-calendar audit;
- freeze train/DEV chronology from pre-2026 only;
- create RW / zero-return / drift baselines;
- define initial low-dimensional daily feature blocks;
- build a release-aware as-of join layer for H.15, H.10, VIX, NDX and GPR;
- exclude WTI/Brent until their PIT publication mapping passes.

No complex model-family screen before Stage 2 baseline/feature gates.
