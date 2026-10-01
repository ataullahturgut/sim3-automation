# GOLD SHORT-HORIZON TACTICAL FORECAST — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.0  
**Date:** 2026-10-01  
**Status:** CURRENT / BINDING / PROJECT INITIATED  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`

> Mission: forecast short-horizon Gold direction, return and return distribution over H1/H3/H5, then build a separate tactical allocation layer.

---

# 1. Executive State

## 1.1 Goal

At each daily origin estimate:
- P_UP_1 / RET_1 / Q10-Q50-Q90_1
- P_UP_3 / RET_3 / Q10-Q50-Q90_3
- P_UP_5 / RET_5 / Q10-Q50-Q90_5.

Then, only after forecast validation, determine which horizon offers the strongest risk-adjusted tactical opportunity.

## 1.2 Current stage

- Data Readiness Audit: COMPLETE / PASS
- Stage 0 Scientific Contract: COMPLETE / FROZEN
- Stage 1 First Multi-Horizon Model Screen: **COMPLETE / PASS**
- Stage 2 H3 Robustness + Feature Representation Audit: **COMPLETE / PASS**
- Stage 3 Sequence Model Challengers: **COMPLETE / NO_SEQUENCE_PROMOTION**
- Stage 4 TFT Multi-Horizon Probabilistic Challenger: **COMPLETE / NO_TFT_PROMOTION**
- Deep-learning challenger program: **CLOSED**
- **Stage 5 Forecast-Head Reconciliation & Tactical Signal Architecture: NEXT**

Current strongest research horizon: **H3**.

Frozen H3 forecast heads:
- direction: **CORE3 / XGB_CLASS**
- point return: **GOLD_ONLY / LGBM_REG**
- quantile distribution: **GOLD_ONLY / LGBM_QUANT**

Rejected deep replacements:
- TCN L20/L60
- GRU L20/L60
- BiGRU L20/L60
- constrained joint H1/H3/H5 TFT.

Supporting non-core evidence:
- H5 TFT Q50 point-return improves Stage-1 H5 classical MAE by **1.47%**, but H5 direction and quantile fail.

No tactical trading champion exists yet.

## 1.3 Governance

- 2011-2021 = background/train history
- 2022-2024 = DEV selection
- 2025 = frozen transport
- 2026 = opened / no selection
- no random split
- no label leakage
- no trading-rule optimization during forecasting stages.

---

# 2. Data Contract

Governed target:
- Borsa İstanbul Gold Metal Price MTL/USD/OZ.

Preferred first strict feature panel:
- Gold
- Silver
- Platinum
- Fed H.15 rates
- Fed H.10 FX
- Cboe VIX
- Nasdaq-100.

Readiness:
- H1: train 2722 / DEV 749 / 2025 249
- H3: train 2722 / DEV 749 / 2025 247
- H5: train 2722 / DEV 749 / 2025 245.

Palladium:
- later CORE4 challenger.

WTI/Brent:
- blocked from first batch pending short-horizon PIT mapping.

Daily GPR:
- blocked from first batch pending merged vintage audit.

---

# 3. Target Contract

H1:
`r1f = log(P[t+1]/P[t])`

H3:
`r3f = log(P[t+3]/P[t])`

H5:
`r5f = log(P[t+5]/P[t])`

For each:
- direction probability
- point return
- Q10/Q50/Q90 distribution.

---

# 4. First Feature Blocks

1. GOLD_ONLY
2. CORE3
3. CORE3_SAFE_EXTERNAL

Every block is tested on the same DEV rows per horizon.

---

# 5. First Model Families

Direction:
- Logistic L2
- LightGBM
- XGBoost

Point return:
- Elastic Net
- LightGBM
- XGBoost

Quantiles:
- LightGBM quantile Q10/Q50/Q90.

Baselines are mandatory.

---

# 6. Evaluation

Direction:
- Brier / log loss primary.

Return:
- MAE / RMSE primary.

Quantile:
- pinball loss primary.

Supporting:
- direction accuracy
- balanced accuracy
- precision/recall
- ROC/PR-AUC
- Spearman
- forecast dispersion
- quantile coverage.

Economic/trading metrics are deferred until forecast models are frozen.

---

# 6A. Stage-1 First-Screen Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE1_RESULT_2026-10-01.md`

Primary run:
- **36870914575**

Authoritative aggregate:
- run **36871668075**
- artifact **11167138282**.

Head summary:

| Horizon | Direction | Return | Quantile |
|---|---|---|---|
| H1 | NO PASS | PASS | PASS |
| **H3** | **PASS** | **PASS** | **PASS** |
| H5 | NO PASS | PASS | PASS |

Current strongest horizon:
**H3**

H3 details:
- direction CORE3/XGB: Brier **0.24646**, +**1.13%** vs baseline
- return Gold-only/LightGBM: MAE **0.013384**, +**1.07%**
- quantile Gold-only/LightGBM: mean pinball **0.004295**, +**1.81%**.

First-screen feature finding:
- CORE3_SAFE_EXTERNAL wins **no head**.
- Gold-only or Gold+Silver+Platinum wins every head.
- current raw external representation is therefore not promoted.

Binding caution:
- improvements are modest;
- no tactical investment rule is authorized;
- 2025 remains frozen.

---

# 6B. Stage-2 H3 Robustness Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE2_RESULT_2026-10-01.md`

Authoritative run:
- **36874561989**
- artifact **11167744845**
- artifact digest `sha256:63e70127447ec23531f59ff6dd589933085905260adcfb3b9c558b253d9cdadb`.

Frozen head decisions:

| Head | Decision | Frozen contract |
|---|---|---|
| Direction | RETAIN | CORE3 / XGB_CLASS |
| Return | RETAIN | GOLD_ONLY / LGBM_REG |
| Quantile | RETAIN | GOLD_ONLY / LGBM_QUANT |

No feature challenger clears the +0.5% promotion gate.

### Stability

Direction relative Brier gain vs baseline:
- 2022 +1.29%
- 2023 -0.07%
- 2024 +2.19%.

Return relative MAE gain:
- 2022 +0.94%
- 2023 -0.85%
- 2024 +2.57%.

Quantile relative pinball gain:
- 2022 -0.47%
- 2023 -0.08%
- 2024 +4.82%.

Quantile therefore carries a binding stability caution: its aggregate edge is concentrated in 2024/high-volatility conditions.

### Volatility diagnostic

Relative retained-head gains:

| Volatility | Direction | Return | Quantile |
|---|---:|---:|---:|
| LOW | -0.29% | +0.64% | +1.57% |
| MID | -0.36% | -1.12% | -1.81% |
| HIGH | +2.06% | +1.74% | +2.81% |

No post-hoc volatility gate is authorized.

### Feature representation conclusion

Not promoted:
- CORE4 / Palladium
- Rates transforms
- FX transforms
- VIX transforms
- Nasdaq transforms
- combined transformed external block.

The cleanest current architecture remains head-specific rather than one giant all-feature model.

---

# 6C. Stage-3 Sequence Challenger Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE3_RESULT_2026-10-01.md`

Run:
- **36877156753**
- aggregate artifact **11169543476**
- aggregate digest `sha256:a23e21682a6dc4db14c69c33b806f151f9842a9a19cbf0958379611aacd24392`.

Result:
**NO_SEQUENCE_PROMOTION**

Best sequence by head:

| Head | Best sequence | Relative vs classical |
|---|---|---:|
| Direction | GRU-L60 | **-1.45%** |
| Return | GRU-L60 | **-1.10%** |
| Quantile | TCN-L20 | **-2.95%** |

All six sequence configurations are worse than the frozen classical H3 benchmark.

Compact model sizes:
- TCN 1,557 parameters
- GRU 1,621
- BiGRU 2,141.

Binding decision:
- retain classical H3 boosting heads;
- do not reopen TCN/GRU/BiGRU without materially new architecture/data evidence;
- proceed only to the materially distinct TFT multi-horizon hypothesis.

---

# 6D. Stage-4 TFT Challenger Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE4_RESULT_2026-10-01.md`

Scientific run:
- **36889006614**
- TFT-CLASS artifact **11176206620**
- TFT-QUANT artifact **11176830553**.

Authoritative aggregate V2:
- run **36890974544**
- artifact **11176262943**
- digest `sha256:93de732490a5cddebe842089e89cd03056f5c09ed2ef13c473d1ff3d3090d245`.

Result:
**NO_TFT_PROMOTION**

H3 comparison:

| Head | TFT vs classical | Decision |
|---|---:|---|
| Direction | **-2.55%** Brier | RETAIN XGB |
| Return | **+0.18%** MAE | RETAIN LightGBM |
| Quantile | **-1.16%** pinball | RETAIN Quantile LightGBM |

TFT architecture remained constrained:
- CLASS 10,712 parameters
- QUANT 10,739 parameters.

Supporting H5 finding:
- TFT H5 Q50 MAE improves by **1.47%** versus Stage-1 H5 classical return head;
- H5 direction and quantile do not pass;
- this does not replace H3 as the research core.

Binding decision:
- deep-learning challenger program CLOSED;
- current data/target contract favors boosting;
- proceed to forecast-head reconciliation before any trading optimization.

---

# 7. Stage Roadmap

| Stage | Purpose | Status |
|---|---|---|
| Data Audit | H1/H3/H5 merged PIT-safe readiness | COMPLETE / PASS |
| 0 | Scientific contract | COMPLETE / FROZEN |
| 1 | First model + feature + horizon screen | **COMPLETE / PASS** |
| 2 | H3 robustness + feature representation audit | **COMPLETE / PASS** |
| 3 | TCN / GRU / BiGRU challengers | **COMPLETE / NO PROMOTION** |
| 4 | TFT multi-horizon challenger | **COMPLETE / NO PROMOTION** |
| 5 | Forecast-head reconciliation / tactical signal architecture | **NEXT** |
| 6 | Tactical allocation / utility layer | BLOCKED BY STAGE 5 |
| 7 | Frozen 2025 transport | BLOCKED |
| 8 | Prospective daily ledger | NOT STARTED |

---

# 8. Exact Next Action

**Stage 5 — Forecast-Head Reconciliation & Tactical Signal Architecture**

Frozen H3 heads:
- direction = CORE3 / XGB_CLASS
- point return = GOLD_ONLY / LGBM_REG
- distribution = GOLD_ONLY / LGBM_QUANT.

Supporting horizons:
- H1 remains secondary;
- H5 remains secondary;
- H5 TFT Q50 return improvement is evidence only and cannot override failed H5 direction/quantile heads.

Stage 5 must work on 2022-2024 DEV only and answer:

1. How often do frozen H3 heads agree/disagree?
2. Define origin-level consistency states, e.g.:
   - ALIGNED_UP
   - ALIGNED_DOWN
   - MIXED
   - HIGH_DOWNSIDE
   - LOW_CONVICTION.
3. Test whether preregistered consistency states separate:
   - sign accuracy
   - return MAE
   - realized positive/negative H3 return
   - downside-tail outcomes
   without fitting a new high-capacity model.
4. Determine whether H1/H5 should be shown as supporting horizon context around H3.
5. Freeze a single daily forecast object before any entry/exit or P&L optimization.

No 2025 tuning.
No transaction-cost or position-sizing optimization in Stage 5.
No reopening deep-learning models.
---

# 9. Document Hierarchy

Canonical:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

Stage 0:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE0_SCIENTIFIC_CONTRACT_2026-10-01.md`

Data readiness:
- `GOLD_SHORT_HORIZON_DATA_READINESS_AUDIT_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_DATA_READINESS_AUDIT_RESULT_2026-10-01.md`
- run 36870048143
- artifact 11166972412.

Stage 1:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE1_RESULT_2026-10-01.md`
- primary run **36870914575**
- H1 artifact **11166394641**
- H3 artifact **11166279606**
- H5 artifact **11166224706**
- aggregate V2 run **36871668075**
- aggregate artifact **11167138282**.

Stage 2:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE2_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE2_RESULT_2026-10-01.md`
- authoritative corrected run **36874561989**
- artifact **11167744845**
- earlier runs 36873375235 / 36873744569 superseded due preprocessing mismatch.

Stage 3:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE3_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE3_RESULT_2026-10-01.md`
- run **36877156753**
- aggregate artifact **11169543476**.

Stage 4:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE4_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE4_RESULT_2026-10-01.md`
- scientific run **36889006614**
- TFT-CLASS artifact **11176206620**
- TFT-QUANT artifact **11176830553**
- aggregate V2 run **36890974544**
- aggregate artifact **11176262943**
- original aggregate job superseded due artifact-copy directory error; no retraining.

Sibling projects:
- monthly forecast: `GOLD_MONTHLY_PROJECT_MANIFEST.md`
- intramonth K100 research: `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

These projects are related but scientifically separate.
