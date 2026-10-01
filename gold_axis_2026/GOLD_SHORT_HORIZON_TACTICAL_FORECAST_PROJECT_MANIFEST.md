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
- **Stage 3 Sequence Model Challengers: NEXT**

Current strongest research horizon: **H3**.

Frozen H3 classical benchmark heads:
- direction: **CORE3 / XGB_CLASS**
- point return: **GOLD_ONLY / LGBM_REG**
- quantile distribution: **GOLD_ONLY / LGBM_QUANT**

Stage-2 result:
- Palladium / CORE4 not promoted
- transformed Rates / FX / VIX / Nasdaq blocks not promoted
- quantile head retained with year/high-volatility concentration caution.

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

# 7. Stage Roadmap

| Stage | Purpose | Status |
|---|---|---|
| Data Audit | H1/H3/H5 merged PIT-safe readiness | COMPLETE / PASS |
| 0 | Scientific contract | COMPLETE / FROZEN |
| 1 | First model + feature + horizon screen | **COMPLETE / PASS** |
| 2 | H3 robustness + feature representation audit | **COMPLETE / PASS** |
| 3 | TCN / GRU / BiGRU challengers | **NEXT** |
| 4 | TFT multi-horizon challenger | BLOCKED |
| 5 | Forecast-head reconciliation | BLOCKED |
| 6 | Tactical allocation / utility layer | BLOCKED |
| 7 | Frozen 2025 transport | BLOCKED |
| 8 | Prospective daily ledger | NOT STARTED |

---

# 8. Exact Next Action

**Stage 3 — Compact Sequence Model Challengers**

Horizon:
- H3 only.

Frozen classical references:
- direction = CORE3 / XGB_CLASS
- return = GOLD_ONLY / LGBM_REG
- quantile = GOLD_ONLY / LGBM_QUANT.

Sequence challengers:
1. TCN
2. GRU
3. BiGRU

Before execution:
- preregister lookback windows
- preregister compact architectures
- keep parameter counts constrained for the modest daily sample
- preserve origin-safe sequences
- preserve H3 label maturity and chronological DEV evaluation.

Selection:
- 2022-2024 DEV only
- 2025 remains frozen
- challenger must beat the corresponding classical head under the same primary/co-primary metrics
- quantile challenger must also address the Stage-2 stability caution rather than win only through 2024.

TFT remains blocked until compact sequence challengers are resolved.
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

Sibling projects:
- monthly forecast: `GOLD_MONTHLY_PROJECT_MANIFEST.md`
- intramonth K100 research: `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

These projects are related but scientifically separate.
