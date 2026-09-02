# GOLD CONTROL — CAUSAL PATCH R1 MONTHLY LEVEL INPUT CHANGE CONTROL V6

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V6_SOURCE_RESULT`  
**Parent manifest:** v1.18  
**V5 status:** `BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_NOT_PROVEN`  
**Reserved V6 identity:** `CAUSAL_PATCH_R1_REPRO_V1_5_DAILY_TRAIN_HOURLY_ANCHOR_ORIGIN_SAFE`

## 1. Why V6 exists

V5 required Twelve Data `XAU/USD` hourly history from 2011 onward. The frozen V5 entitlement audit proved:

- 2011-01: HTTP/API 400, unavailable;
- 2016-01: HTTP/API 400, unavailable;
- 2020-01: accessible;
- 2023-01: accessible;
- 2026-01: accessible.

Therefore V5 was closed before model-impact scoring. No threshold was relaxed and no source was silently substituted.

V6 solves only the remaining monthly-level/anchor continuity problem using source depths already demonstrated by current entitlement.

## 2. Frozen V6 measurement architecture

### 2.1 Historical training monthly level

Series identity:

`PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN`

Construction:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1day`;
- provider-default daily semantic retained exactly as provider returns it; no NY17, LBMA, settlement, official-close or timezone claim;
- arithmetic mean of positive finite daily closes for each completed calendar month;
- minimum 15 valid daily observations per model month;
- no interpolation, forward fill, or provider substitution.

This reuses the same XAU `1day` lineage whose full-history access from 2010 was already proven in V4. It is a separately named operational monthly-level measurement and is not relabelled as CORE5 or World Bank.

### 2.2 Forecast-origin monthly anchor

Series identity:

`PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR`

Construction:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1h`;
- requested timezone: `America/New_York`;
- select the hourly bar opened at `16:00:00`; its `close` is the end of the 16:00–17:00 ET hourly bar;
- arithmetic mean of selected positive finite daily closes in the just-completed origin calendar month;
- minimum 15 valid selected daily observations;
- current origin month is eligible only after the final required 16:00–17:00 ET bar has completed;
- no interpolation, forward fill, or provider substitution.

Hourly history is required only for the origin-anchor months used by the locked 43-origin impact test (`2022-12` through `2026-06`) and for future live origin months. V5 proved 2023+ hourly access under the current entitlement; V6 must still prove the exact locked-anchor coverage before scoring.

## 3. Origin-safe training cutoff correction

At a real end-month origin the provider-default `1day` bar for that same calendar date is not assumed completed under Gold Data R2.7. Therefore the just-completed month `p` may not be used as a V6 training target through the daily-monthly series at that origin.

Frozen V6 rule for target month `t`:

- origin month `p = t-1`;
- most recent eligible training target month is `pp = t-2`;
- training sample set is restricted to target months `< p`;
- the forecast level is anchored on the origin-safe hourly monthly mean for `p`.

This one-month target-availability lag is an explicit causal correction, not an ex-post model tuning decision.

## 4. Source/semantic gates — frozen before V6 result

The same pre-existing monthly-gold materiality thresholds are retained unchanged:

### Daily training level versus canonical CORE5

- level correlation `>= 0.995`;
- median absolute relative level gap `<= 50 bps`;
- p95 absolute relative level gap `<= 100 bps`;
- consecutive monthly log-return correlation `>= 0.95`;
- monthly return direction agreement `>= 0.80`.

Coverage:

- all required training months `2011-02→2026-07` present;
- each required month has at least 15 valid daily closes.

### Hourly origin anchor versus daily training level

Over every locked anchor month `2022-12→2026-06`:

- all 43 anchor months present;
- each anchor month has at least 15 selected hourly daily closes;
- level correlation `>= 0.995`;
- median absolute relative level gap `<= 50 bps`;
- p95 absolute relative level gap `<= 100 bps`;
- consecutive monthly log-return correlation `>= 0.95`;
- monthly return direction agreement `>= 0.80`.

No raw vendor market values may be printed. No Neon, forecast-ledger, or Decision Store write is permitted during source/model-impact validation.

Source PASS identity:

`PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS`

Source FAIL identity:

`BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_NOT_PROVEN`

## 5. Locked V6 model-impact test

Only after both source gates pass:

- Patch Transformer architecture remains unchanged;
- `L=252`, `P=21`, `D=32` unchanged;
- daily XAU feature channel remains the V4 Twelve `1day` XAU-only channel;
- V3 NASDAQ completed-month semantic unchanged;
- FEDFUNDS/USDCNY/GPR semantics unchanged;
- optimizer/loss/epoch/ensemble-of-seeds procedure unchanged;
- auto selector OFF;
- auto ensemble primary OFF;
- locked evaluation window remains `2023-01→2026-07`, `N=43`.

For each locked origin:

1. historical training return targets are built from `PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN`;
2. the latest one-month target `p` is excluded from training to preserve the frozen origin-availability rule;
3. the forecast level uses `PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR[p]`;
4. evaluation actual remains the canonical CORE5/production-closure target;
5. RW remains the same frozen canonical benchmark.

Frozen acceptance gates are unchanged from V4/V5:

- target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic repeat equality;
- zero future-information violations;
- no geometry re-selection;
- candidate MAPE `< RW MAPE`;
- candidate MAE `< RW MAE`;
- candidate worst APE `<= 1.25 × RW worst APE`.

PASS identity:

`PATCH_R1_V6_MONTHLY_LEVEL_MODEL_IMPACT_PASS`

FAIL identity:

`PATCH_R1_V6_MONTHLY_LEVEL_MODEL_IMPACT_FAIL_NO_RETUNE`

## 6. Evidence boundary and downstream sequence

V6 source/model-impact PASS would remain `HISTORICAL_REPLAY_MODEL_IMPACT`, not prospective evidence.

After PASS only:

1. freeze V6 executable/input identity;
2. reconcile manifest;
3. implement immutable forecast-input snapshot + forecast contract writer;
4. validate writer in dry-run and rollback-only mode;
5. construct complete R4.2 forward EngineSnapshot;
6. arm future month-end issuer;
7. first actual issuance remains `PROSPECTIVE_SHADOW`.
