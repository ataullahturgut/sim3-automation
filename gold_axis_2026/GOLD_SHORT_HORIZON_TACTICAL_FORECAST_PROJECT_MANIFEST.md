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
- **Stage 1 First Multi-Horizon Model Screen: NEXT**

No tactical champion exists yet.

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

# 7. Stage Roadmap

| Stage | Purpose | Status |
|---|---|---|
| Data Audit | H1/H3/H5 merged PIT-safe readiness | COMPLETE / PASS |
| 0 | Scientific contract | COMPLETE / FROZEN |
| 1 | First model + feature + horizon screen | **NEXT** |
| 2 | Incremental CORE4 / optional feature challengers | BLOCKED |
| 3 | TCN / GRU / BiGRU challengers | BLOCKED |
| 4 | TFT multi-horizon challenger | BLOCKED |
| 5 | Forecast-head reconciliation | BLOCKED |
| 6 | Tactical allocation / utility layer | BLOCKED |
| 7 | Frozen 2025 transport | BLOCKED |
| 8 | Prospective daily ledger | NOT STARTED |

---

# 8. Exact Next Action

Run Stage 1 on 2022-2024 DEV only:

- H1/H3/H5
- GOLD_ONLY / CORE3 / CORE3_SAFE_EXTERNAL
- baselines
- Elastic Net
- LightGBM
- XGBoost
- LightGBM quantiles.

Do not inspect 2025 results until the Stage-1 selection is frozen.

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

Sibling projects:
- monthly forecast: `GOLD_MONTHLY_PROJECT_MANIFEST.md`
- intramonth K100 research: `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

These projects are related but scientifically separate.
