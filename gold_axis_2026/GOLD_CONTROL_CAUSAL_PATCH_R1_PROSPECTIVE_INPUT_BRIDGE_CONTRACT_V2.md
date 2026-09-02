# GOLD CONTROL — CAUSAL PATCH R1 PROSPECTIVE INPUT BRIDGE CONTRACT V2

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V2_RESULT`  
**Parent evidence:** V1 decision `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`  
**Model family:** unchanged `CAUSAL_PATCH_R1_REPRO_V1` architecture  
**Geometry:** unchanged `L=252`, `P=21`, `D=32`  
**Auto selector / auto ensemble:** OFF

## 1. Scope

V2 fixes only the two input-continuation failures observed under the already-frozen V1 contract. It does not change the forecast target, Patch architecture, training loss, geometry, VW/3M/RW roles, Emergency thresholds or decision engine.

V1 thresholds are not relaxed after seeing V1 results.

No forecast-ledger, Decision Store or production DB write is authorized.

## 2. Macro V2 — minimal origin-safe correction

V1 proved these constructions and they remain unchanged:

- `FEDFUNDS_ORIGIN_MEAN_V1`: current origin-month mean of DFF visible by month-end;
- `DEXCHUS_ORIGIN_MEAN_V1`: current origin-month mean of DEXCHUS visible by month-end;
- GPR conservative lag rule remains unchanged.

V1 found 3 missing current-month NASDAQCOM month-end PIT reconstructions. V2 therefore changes **only the NASDAQ feature timing**:

`NASDAQCOM_LAG1_RETURN_ORIGIN_SAFE_V2`

For target month `t` and origin month `p=t-1`, use the return between completed months `p-2` and `p-1`:

`log(NASDAQCOM_mean[p-1] / NASDAQCOM_mean[p-2])`

Both monthly means must be visible in the ALFRED snapshot dated the origin calendar month-end. Current origin-month NASDAQCOM is never required.

This is an explicit new input semantic and therefore, if accepted, receives a new executable/input identity. It may not silently overwrite `CAUSAL_PATCH_R1_REPRO_V1`.

### Macro V2 source gates

Audit targets: `2023-01→2026-07`, `N=43`.

- DFF current-month reconstructions: `43/43` required;
- DEXCHUS current-month reconstructions: `43/43` required;
- NASDAQCOM lagged-return inputs: `43/43` required;
- no future observation date;
- no forward fill/current-vintage fill;
- no missing month silently substituted.

Materiality against the corresponding locked CORE5 source months keeps V1 thresholds:

- DFF level: median relative gap `<=0.50%`, p95 `<=1.50%`;
- DEXCHUS level: median relative gap `<=0.20%`, p95 `<=0.75%`;
- each of the two completed NASDAQCOM monthly levels used in the lagged return: pooled median relative gap `<=0.30%`, p95 `<=1.00%`.

## 3. Daily metals V2 — provider-defined daily spot proxy

The V1 London-hour Twelve construction is retired as a failed candidate and is not retuned.

V2 candidate is separately named provider-defined **daily spot** data from Twelve Data:

- Gold: `XAU/USD`, interval `1day`;
- Silver: `XAG/USD`, interval `1day`;
- Platinum: `XPT/USD`, interval `1day`;
- Palladium: `XPD/USD`, interval `1day`.

Timezone requested: `Europe/London`.

These values are not LBMA benchmark prices and may never be labelled as LBMA. The purpose of the audit is only to determine whether their **daily return behavior** is sufficiently compatible to continue the Patch return feature operationally.

### Metal V2 gates

Audit overlap is strengthened to `2025-01-01→2026-08-19` where the frozen historical artifact and operational candidate overlap.

The V1 quantitative gates are retained unchanged:

Per metal:

- common aligned daily observations `>=120`;
- consecutive common return pairs `>=100`;
- Pearson correlation of aligned log returns `>=0.90`;
- return-direction sign agreement `>=0.75`;
- median absolute log-return gap:
  - Gold/Silver `<=75 bps`;
  - Platinum/Palladium `<=100 bps`;
- p95 absolute log-return gap `<=300 bps`.

All four metals must pass every gate. A provider/API failure is `NOT_PROVEN`, not PASS.

## 4. Stitch rule if metals pass

Historical daily-metal observations remain frozen to:

`lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

The historical artifact is authoritative only through its final pinned observation. Twelve daily spot starts afterward as a separate operational lineage.

No cross-provider level return is allowed. The first operational return requires two consecutive operational-source observations. Missing days remain missing; no forward fill.

## 5. V2 source-bridge decision

`PATCH_PROSPECTIVE_INPUT_BRIDGE_V2_SOURCE_PASS` requires:

1. all macro V2 source gates PASS; and
2. all four daily-metal V2 gates PASS.

Otherwise:

`BLOCKED_PATCH_PROSPECTIVE_INPUT_V2_SOURCE_NOT_PROVEN`

## 6. Model-impact gate after source PASS

Source PASS alone is not enough because the lagged NASDAQ feature changes model inputs.

Without retuning geometry, rerun the frozen `2023-01→2026-07`, `N=43` historical replay under the V2 input construction.

New identity reserved only if the replay is executed:

`CAUSAL_PATCH_R1_REPRO_V1_1_ORIGIN_SAFE`

Model-impact hard gates:

- target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic rerun equality;
- no future information;
- no geometry retune;
- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<= 1.25 × RW worst APE`.

If these fail, V2 is rejected. Do not adjust thresholds or geometry using the locked-window result.

## 7. Downstream gates remain unchanged

Even after V2 source and model-impact PASS:

1. freeze the new executable/input identity;
2. validate generic monthly-reference → Emergency geometry;
3. persist immutable forecast input snapshot + forecast contract before an eligible real origin;
4. first forward evidence class is `PROSPECTIVE_SHADOW`;
5. no September 2026 backdating.
