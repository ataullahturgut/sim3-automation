# GOLD CONTROL — CAUSAL PATCH R1 PROSPECTIVE INPUT BRIDGE CONTRACT V3

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V3_SOURCE_RESULT`  
**Parent evidence:** V2 decision `BLOCKED_PATCH_PROSPECTIVE_INPUT_V2_SOURCE_NOT_PROVEN`  
**Change control:** `GOLD_CONTROL_CAUSAL_PATCH_R1_INPUT_SOURCE_CHANGE_CONTROL_V3_2026-09-02.md`  
**Model architecture:** unchanged `CAUSAL_PATCH_R1_REPRO_V1`  
**Geometry:** unchanged `L=252`, `P=21`, `D=32`  
**Auto selector / auto ensemble:** OFF

## 1. Scope

V3 is an input-semantic correction only. It does not change target, horizon, model family, Patch geometry, optimizer/loss, VW/3M/RW roles, Emergency thresholds, Fast/Slow, BOCPD, GVZ, or decision-engine logic.

No production forecast, Decision Store, or Neon write is authorized by this contract.

## 2. Daily metals V3 — one provider over full Patch history

V1 and V2 attempted cross-provider compatibility. V3 does not.

The V3 candidate reconstructs the complete Patch daily-metal return history using Twelve Data `1day` series only:

- Gold `XAU/USD`;
- Silver `XAG/USD`;
- Platinum `XPT/USD`;
- Palladium `XPD/USD`.

Lineage:

`PATCH_METALS_TWELVE_DAILY_FULL_HISTORY_V3`

Rules:

1. interval is exactly `1day`;
2. no timezone claim is made because Twelve documentation states timezone is ignored for daily intervals;
3. values are not LBMA benchmark prices and may never be labelled LBMA;
4. no StakTrakr/Twelve cross-provider return is calculated;
5. all four metal closes for a date must be present before the date may enter the common feature matrix;
6. duplicates and non-positive/non-finite closes are invalid;
7. no forward fill/interpolation;
8. raw vendor values must not be printed to logs.

### 2.1 Source-depth gate

The existing Patch reproduction begins model samples from 2011-03 and frozen geometry requires `L=252` daily return rows.

V3 source readiness requires:

- common four-metal daily close intersection contains at least 253 observations strictly before the first 2011-03 target origin boundary;
- common four-metal history has no duplicate dates;
- all four symbols return valid provider metadata and `1day` interval;
- recent common history reaches at least `2026-08-28` for this 2026-09-02 source audit;
- at least 3,500 common four-metal daily close rows exist between the earliest qualifying history and `2026-08-31`;
- no raw values logged.

The row-count gate is a coverage/continuity guard, not a performance threshold.

## 3. NASDAQ V3 — completed-month market-close availability reconstruction

Feature identity:

`NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3`

For target month `t` and origin month `p=t-1`:

`nasdaq_return_v3 = log(mean(NASDAQCOM daily closes in p-1) / mean(NASDAQCOM daily closes in p-2))`

Source: FRED series `NASDAQCOM`, whose source is Nasdaq, Inc. and whose series note identifies observations as daily market-close index values.

Historical replay availability policy:

`MARKET_CLOSE_AVAILABILITY_RECONSTRUCTION_NEXT_DAY_V1`

- an observation dated `d` is treated as available no earlier than calendar day `d+1`;
- V3 never uses origin-month NASDAQ data;
- every daily observation used by the feature must therefore be available before the origin month-end under the next-day rule;
- this policy is a conservative reconstruction, not proof of an original historical retrieval timestamp.

### 3.1 NASDAQ source-identity/materiality gate

Fetch current FRED `NASDAQCOM` daily history required to reconstruct CORE5 monthly NASDAQ values.

For every CORE5 month required by the V3 locked replay and its training feature history where both sources overlap:

- reconstruct monthly mean from valid daily closes;
- require no future-dated observation relative to the month;
- require at least 95% of expected business-day-like observed days is not necessary; missing exchange holidays are allowed;
- require no month used by the 43 locked targets to be missing;
- relative level gap versus CORE5 monthly `nasdaq`:
  - median `<=0.30%`;
  - p95 `<=1.00%`.

These are the same NASDAQ materiality limits already frozen in V1/V2.

## 4. Macro fields not changed

The V1-proven DFF/FEDFUNDS and DEXCHUS/USDCNY constructions remain inherited and unchanged for this source gate.

GPR conservative lag remains unchanged.

V3 does not re-open them merely because other inputs changed.

## 5. V3 source decision

`PATCH_PROSPECTIVE_INPUT_BRIDGE_V3_SOURCE_PASS` requires:

1. Twelve full-history four-metal source-depth gate PASS;
2. NASDAQ V3 source-identity/materiality/availability gate PASS;
3. inherited DFF/FEDFUNDS PASS;
4. inherited DEXCHUS/USDCNY PASS;
5. zero raw vendor values in logs;
6. zero Neon/forecast-ledger/Decision Store writes.

Otherwise:

`BLOCKED_PATCH_PROSPECTIVE_INPUT_V3_SOURCE_NOT_PROVEN`

## 6. Model-impact gate after source PASS

Only after source PASS may the model-impact replay execute.

Reserved identity:

`CAUSAL_PATCH_R1_REPRO_V1_2_TWELVE_DAILY_ORIGIN_SAFE`

Frozen model-impact window:

`2023-01→2026-07`, `N=43`.

Frozen model-impact gates:

- target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic rerun equality;
- no future information;
- no geometry retune;
- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<=1.25 × RW worst APE`.

The 43-month result may not be used to retune V3 source rules, geometry, thresholds, or model family.

## 7. Downstream gates

A model-impact PASS is still only historical replay evidence. It does not itself authorize a live decision.

Next dependency sequence remains:

1. freeze accepted executable/input identity;
2. validate generic monthly-reference → Emergency geometry;
3. create immutable forecast input snapshot + forecast contract before an eligible real origin;
4. first forward evidence class `PROSPECTIVE_SHADOW`;
5. September 2026 remains non-backfillable.
