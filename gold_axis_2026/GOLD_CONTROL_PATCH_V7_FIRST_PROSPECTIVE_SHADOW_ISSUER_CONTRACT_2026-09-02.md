# GOLD CONTROL — PATCH V7 FIRST PROSPECTIVE SHADOW ISSUER CONTRACT

**Freeze date:** 2026-09-02  
**Status:** `FROZEN_BEFORE_FIRST_ELIGIBLE_FORWARD_ORIGIN`  
**Parent manifest:** v1.18  
**Executable identity:** `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`  
**Parent model-impact evidence:** `PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS`  
**First allowed evidence class:** `PROSPECTIVE_SHADOW`  

## 1. Purpose

This contract closes the Stage 4B gap between the accepted historical-replay executable and the first genuinely forward H=1 shadow forecast. It does not promote Patch V7 to `LIVE_PRODUCTION` and does not alter the model, geometry, source thresholds or decision engine.

## 2. First eligible origin

The first issuer version is intentionally scoped to one genuinely future target only:

- earliest eligible New York calendar date: `2026-09-30`;
- target month: `2026-10`;
- issuance may occur only on the last calendar day of September 2026 after `17:20 America/New_York`;
- the actual issuance timestamp is persisted as `forecast_origin`;
- September 2026 may never be inserted as prospective evidence;
- any attempt before the eligible date/time is a no-write `SKIP_NOT_ELIGIBLE_ORIGIN`;
- any attempt after a successful October shadow issuance is a no-write duplicate skip.

This narrow first-issuer scope prevents unproven continuation logic from being silently generalized beyond the first prospective evidence point.

## 3. Frozen model behavior

Unchanged from V7/V6:

- Patch Transformer architecture;
- geometry `L=252 / P=21 / D=32`;
- Huber loss, AdamW, seed family and median-of-three prediction;
- expanding historical training set with the V6/V7 85/15 train/validation split rule;
- Twelve `XAU/USD 1day` daily-return channel only;
- daily feature rule `observation_date < origin_date`;
- daily-training monthly level semantic `PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN`;
- hourly anchor semantic `PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR`;
- V3 NASDAQ completed-month rule;
- V1 DFF/FEDFUNDS and DEXCHUS/USDCNY source constructions;
- GPR conservative lag;
- auto selector OFF;
- auto ensemble OFF.

For the October 2026 target, the expanding training set is allowed to add the now-observed August 2026 training target because `2026-08 < p=2026-09`. This follows the frozen expanding-origin rule and is not hindsight tuning.

## 4. First-forward source rules

### 4.1 XAU daily return tensor

Provider: Twelve Data  
Symbol: `XAU/USD`  
Interval: `1day`  

- fetch full required history;
- derive daily log returns;
- for October target use only return observations whose date is strictly earlier than `2026-09-30`;
- select the last 252 eligible returns;
- no same-origin-date bar, forward fill or provider substitution.

### 4.2 September monthly anchor

Provider: Twelve Data  
Symbol: `XAU/USD`  
Interval: `1h`  
Timezone: `America/New_York`  

- query September 2026 only;
- select valid bars whose open timestamp is exactly `16:00:00` ET;
- their close is the frozen `17:00_ET_HOURLY_CLOSE` semantic;
- require at least 15 valid daily observations;
- arithmetic mean is the September monthly anchor used by the model;
- no raw vendor values may be printed or committed to GitHub.

### 4.3 FEDFUNDS

Series: FRED/ALFRED `DFF`  

- reconstruct September 2026 monthly mean with `realtime_start=realtime_end=2026-09-30`;
- use only observations then visible in the provider vintage;
- require at least one valid observation and no source date after September 30.

### 4.4 USD/CNY

Series: FRED/ALFRED `DEXCHUS`  

- reconstruct September 2026 monthly mean as of `2026-09-30`;
- reconstruct August 2026 monthly mean as of `2026-08-31`;
- feature is `log(SepMean/AugMean)`;
- require at least one valid observation for each month.

### 4.5 NASDAQ

Series: FRED `NASDAQCOM`  
Feature identity: `NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3`  

For October target:

`log(mean(Aug-2026 daily closes) / mean(Jul-2026 daily closes))`

Only fully completed pre-origin months are used.

### 4.6 GPR

Source: Caldara-Iacoviello official workbook  
Series: `GPR`  

- October target uses August 2026 (`p-1`) under the existing conservative lag;
- August must exist in the official workbook retrieved at issuance;
- if absent, block;
- GPR z-scaling extends the frozen CORE5 GPR history with the retrieved August value only; it does not rewrite historical CORE5 values from a current revised workbook.

## 5. Immutable forecast snapshot

Before committing the forecast contract, the issuer must atomically persist the exact model inputs used.

At minimum:

1. compressed exact training tensor (`x`, macro, `y`, target-month labels) in private Neon metadata, with SHA-256;
2. compressed exact 252×2 test tensor in private Neon metadata, with SHA-256;
3. the five scalar test macro values as separately identified snapshot rows;
4. the September hourly monthly-anchor scalar;
5. source identities, transforms, retrieval/availability timestamps, model version and git SHA.

No raw vendor values or tensor payloads may be printed to CI logs or committed to the public repository.

## 6. Forecast contract

After snapshots are inserted in the same database transaction:

- insert exactly one `monthly_forecast_contracts` row;
- target month `2026-10-01`;
- model name `CAUSAL_PATCH_R1`;
- model version `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`;
- model role `PRIMARY_EXECUTABLE`;
- provenance `evidence_class=PROSPECTIVE_SHADOW`;
- provenance includes all snapshot IDs and input fingerprint;
- unit `USD/oz`;
- no Decision Store write in this first issuer transaction.

Any duplicate, missing source, invalid tensor, unavailable input, DB schema drift or failed post-write verification aborts the entire transaction.

## 7. Writer proof already inherited

Required parent infrastructure evidence:

- `FORECAST_WRITER_SCHEMA_AUDIT_PASS`;
- `PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS`;
- append-only guards active on forecast state tables;
- pre-issuance input/contract ledgers empty.

## 8. Scheduling

Canonical model/issuer code remains on `gold-r4-direction-engine`.

Because GitHub Actions scheduled workflows execute from the repository default branch (`main`), a separate `main`-branch scheduler stub is permitted only to:

1. check out `gold-r4-direction-engine`;
2. run the frozen issuer from that branch with protected secrets;
3. contain no model implementation, source transformation or threshold logic of its own.

The scheduler is operational transport only and does not become a model source of truth.

## 9. Promotion prohibition

A successful October row is only the first `PROSPECTIVE_SHADOW` forecast. It does not by itself authorize:

- `LIVE_PRODUCTION` status;
- retrospective September insertion;
- automatic selector/ensemble;
- threshold/model/source retuning;
- Decision Store live promotion.
