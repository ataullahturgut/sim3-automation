# GOLD SHORT-HORIZON TACTICAL FORECAST — Data Readiness Audit Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PASS**  
**Workflow:** Gold Short Horizon Data Readiness Audit  
**Run:** **36870048143**  
**Artifact:** **11166972412**  
**Artifact digest:** `sha256:c8abd6d86a2c74d436241e59aa59540f0a1e68804e33ee39d08294c4b237a908`  
**Runner commit:** `2a6a368af901caf50bf018ef45561af5cda2d002`  
**Authority:** `GOLD_SHORT_HORIZON_DATA_READINESS_AUDIT_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

**The governed data are sufficient to start H1/H3/H5 short-horizon Gold tactical forecasting research.**

Preferred first strict panel:

**Gold + Silver + Platinum + Rates + FX + VIX + Nasdaq-100**

Palladium is retained as an incremental challenger rather than a mandatory core field because its historical gaps shorten the strict common training history without adding any DEV/transport coverage.

WTI/Brent and daily GPR are excluded from the first batch until their short-horizon PIT contracts are separately completed.

## 2. Targets

Forward returns:

- H1 = log(P[t+1] / P[t])
- H3 = log(P[t+3] / P[t])
- H5 = log(P[t+5] / P[t]).

The Borsa İstanbul Gold MTL/USD/OZ series remains the governed target.

## 3. Preferred safe-panel coverage

Panel:
**CORE3 + Rates + FX + VIX + Nasdaq-100**

CORE3:
- Gold
- Silver
- Platinum.

| Horizon | Pre-DEV train/history | DEV 2022-2024 | Frozen 2025 transport | First signal | Last labelled signal |
|---|---:|---:|---:|---|---|
| **H1** | **2,722** | **749** | **249** | 2011-02-03 | 2025-12-31 |
| **H3** | **2,722** | **749** | **247** | 2011-02-03 | 2025-12-29 |
| **H5** | **2,722** | **749** | **245** | 2011-02-03 | 2025-12-25 |

All pre-registered readiness gates pass:
- DEV >=700 per horizon: **PASS**
- pre-DEV CORE3 training >=2,000: **PASS**
- 2025 transport >=200 per horizon: **PASS**
- safe external families cause no DEV collapse: **PASS**.

## 4. Palladium effect

Strict CORE4 adds Palladium r1/r5/r21 and staleness.

Because Palladium history contains early gaps, the strict complete CORE4 panel begins only on **2014-02-10**.

| Horizon | CORE3 train | CORE4 train | DEV CORE3 | DEV CORE4 | 2025 transport CORE4 |
|---|---:|---:|---:|---:|---:|
| H1 | **2,722** | 1,965 | 749 | 749 | 249 |
| H3 | **2,722** | 1,965 | 749 | 749 | 247 |
| H5 | **2,722** | 1,965 | 749 | 749 | 245 |

Decision:
- do **not** make Palladium mandatory in the first model batch;
- test CORE4 as a separate incremental feature block;
- compare whether its information gain compensates for the shorter training history.

## 5. DEV target characteristics

Preferred safe panel, 2022-2024:

| Horizon | N | UP share | Mean forward return | Median forward return | Log-return SD |
|---|---:|---:|---:|---:|---:|
| H1 | 749 | **50.3%** | +0.051% | +0.013% | 0.01212 |
| H3 | 749 | **53.8%** | +0.154% | +0.153% | 0.01750 |
| H5 | 749 | **53.5%** | +0.256% | +0.198% | 0.02191 |

Interpretation:
- no horizon is pathologically class-imbalanced;
- H1 is nearly perfectly balanced;
- H3/H5 have mild positive skew in sign frequency but remain suitable for probabilistic classification.

## 6. Conservative PIT timing audit

The readiness audit intentionally used conservative availability lags.

### Rates — Fed H.15

Rule:
- latest valid observation <= signal date - 2 calendar days.

Observed staleness:
- median: **2 days**
- p95: **4 days**
- max: **5 days**.

This holds for:
- nominal 10Y
- real 10Y
- breakeven proxy.

### FX — Fed H.10

Rule:
- latest valid observation <= signal date - 7 calendar days.

Broad USD:
- median: **7 days**
- p95: **7 days**
- max: **12 days**.

Major FX:
- EUR / GBP / JPY / CHF / CNY
- median: **7 days**
- p95: **7 days**
- max: **10 days**.

This is intentionally conservative and avoids treating date-labelled H.10 observations as contemporaneously published daily information.

### VIX

Prior-completed-U.S.-session rule:
- median age **1 day**
- p95 **3 days**
- max **5 days**.

### Nasdaq-100

Prior-completed-U.S.-session rule:
- median age **1 day**
- p95 **3 days**
- max **4 days**.

## 7. Safe external block does not reduce sample

Adding, sequentially:

1. Rates
2. FX
3. VIX
4. Nasdaq-100

to CORE3 produces **zero additional row loss** at H1/H3/H5.

Therefore the first model screen can compare:
- Gold-only
- CORE3
- CORE3 + Rates
- CORE3 + Rates + FX
- CORE3 + Rates + FX + VIX
- CORE3 + Rates + FX + VIX + NDX

without changing the DEV sample.

This is important for apples-to-apples feature-family testing.

## 8. Optional families not authorized in the first batch

### WTI
Official daily source:
- 2010-01-04..2026-09-22
- n=4,140.

Status:
**SOURCE_READY / SHORT-HORIZON PIT MAPPING NOT FROZEN**.

### Brent
Official daily source:
- 2010-01-04..2026-09-22
- n=4,230.

Status:
**SOURCE_READY / SHORT-HORIZON PIT MAPPING NOT FROZEN**.

### Daily GPR
Status:
**EXCLUDED PENDING COMPLETE DAILY-VINTAGE MERGED-COVERAGE AUDIT**.

These are optional feature challengers, not blockers.

## 9. Model-family suitability

### Fully supported by current sample
- zero-return / historical mean / momentum baselines
- Ridge / LASSO / Elastic Net
- logistic models
- LightGBM
- XGBoost
- CatBoost
- quantile boosting / quantile tree models.

### Feasible later challengers
- small TCN
- GRU
- BiGRU

with strong regularization and chronological validation.

### TFT
Technically feasible, but the sample is **modest for a large transformer**.

Decision:
- TFT should be a constrained later challenger;
- it should not be the first or sole model architecture.

## 10. Data artifacts

Source authorities:
- BIST Stage-2 artifact: **11161358194**
- External Authority V2 artifact: **11028494060**.

Readiness artifact:
- **11166972412**.

Generated hashes:
- `coverage_by_horizon_and_block.csv`: `911729d271420163006a360505251921fb0b4ebd589b752e0f1cbdbd4e45cadf`
- `dev_target_characteristics.csv`: `d5e3f690ec20ffd811b7025679a767cb83a0beb85966b674ba05671c9a39dd57`
- `external_staleness_audit.csv`: `c94eeeab92b624b483263e146c00b81f97d4e8cbf22d7b7488b9bd054a63b9df`
- `optional_family_status.csv`: `08f26b3b992f492729dc5af3b65973ac0a196c3553f1db577d568c103f9608ad`
- `short_horizon_readiness_panel.csv`: `2a25bff08b41e50df4804c1f30c7ecf058a34b5cc027130e2f9af44c200cebb4`
- `READINESS_RESULT.md`: `199f3c4b377c376bdf604871ab09af51d91c7d5b046b2772dff825802c13e934`.

## 11. Decision

**DATA READINESS = PASS.**

The data side does not block the new tactical project.

Exact next action:

1. initialize `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`;
2. freeze H1/H3/H5 forecast and economic-evaluation contract;
3. first batch:
   - zero-return / historical-mean / momentum baselines
   - Elastic Net
   - LightGBM
   - XGBoost
   - quantile boosting;
4. first feature blocks:
   - Gold-only
   - CORE3
   - CORE3 + safe external;
5. Palladium / CORE4 only as incremental challenger;
6. 2025 remains frozen until horizon/model/feature selection is complete.
