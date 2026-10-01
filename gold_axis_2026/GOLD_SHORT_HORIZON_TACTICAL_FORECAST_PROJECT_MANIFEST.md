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
- Stage 5 Forecast-Head Reconciliation & Tactical Signal Architecture: **COMPLETE / NO_RECONCILIATION_PASS**
- Stage 6 Tactical Allocation / Utility Contract: **COMPLETE / NO_TACTICAL_PASS**
- Stage 6B Turnover / Tradable-Instrument Economic Feasibility Audit: **COMPLETE / BORDERLINE IMPLEMENTABILITY**
- Stage 6C Cross-Instrument Mapping Audit: **COMPLETE / FAIL**
- **Stage 6D Tactical Target Authority Redesign: NEXT**

Current strongest horizon for the original BIST Metal Price target remains: **H3**.

Important:
the original target is no longer authorized as a universal proxy for a tradable global Gold instrument.

Frozen H3 forecast heads:
- direction: **CORE3 / XGB_CLASS**
- point return: **GOLD_ONLY / LGBM_REG**
- quantile distribution: **GOLD_ONLY / LGBM_QUANT**

Frozen daily forecast object:
`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`

Stage-6 economic result:
- no long/cash utility rule passes at frozen 20 bp round-trip cost;
- best 20 bp candidate = **U2 MEDIAN_CONSENSUS**, CAGR **6.56%**, max DD **-13.79%**, Sortino **0.743**;
- BUY_AND_HOLD = CAGR **13.54%**, max DD **-19.40%**, Sortino **1.016**;
- gross 0 bp sensitivity shows the timing edge is economically interesting but turnover-sensitive.

2025 tactical transport remains CLOSED.

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

# 6E. Stage-5 Forecast-Head Reconciliation Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE5_RESULT_2026-10-01.md`

Run:
- **36892132569**
- artifact **11177455544**
- digest `sha256:6363c1687cb6ced34b3119f58fa03261ac7c9c733728d5991fdb96d86b1229b5`.

Result:
**NO_RECONCILIATION_PASS**

Preregistered categorical components:

| Component | N | Lift vs unconditional | Decision |
|---|---:|---:|---|
| ALIGNED_UP | 9 | +12.86 pp UP-rate | FAIL — too sparse / unstable |
| ALIGNED_DOWN | 4 | +3.94 pp DOWN-rate | FAIL |
| HIGH_DOWNSIDE | 472 | +3.87 pp severe-downside | FAIL |

Directional-state frequencies:
- ALIGNED_UP 1.2%
- ALIGNED_DOWN 0.5%
- LOW_CONVICTION 93.3%
- MIXED 4.9%.

Binding interpretation:
- hard head alignment discards too much information;
- do not retune thresholds post hoc;
- retain continuous H3 forecast vector;
- Stage 6 must consume raw head outputs rather than categorical state labels.

Frozen forecast object:
`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`.

---

# 6F. Stage-6 Tactical Utility Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6_RESULT_2026-10-01.md`

Run:
- **36892963306**
- artifact **11178115214**
- artifact digest `sha256:3f1b8d5a458521c1c64cda9f3a6df0a30adcad88d9140a966998ca3f14713b5c`.

Result:
**NO_TACTICAL_PASS**

Primary 20 bp research-cost comparison:

| Strategy | CAGR | Max DD | Sortino |
|---|---:|---:|---:|
| BUY_AND_HOLD | **13.54%** | -19.40% | **1.016** |
| U1 RET_ONLY | 2.64% | **-12.45%** | 0.279 |
| **U2 MEDIAN_CONSENSUS** | **6.56%** | -13.79% | **0.743** |
| U3 PROB_TILT | 3.14% | -14.51% | 0.332 |
| U4 FULL_RISK | 0.00% | 0.00% | — |

No rule clears the frozen tactical gate.

Economic diagnosis:
- 0 bp U3: CAGR **14.83%**, max DD **-17.13%**, Sortino **1.276**
- 20 bp: no PASS
- 50 bp: best U2 CAGR ~2.0%, only 8 trades.

Binding interpretation:
- predictive timing edge exists in gross sensitivity;
- current edge is too thin / turnover-sensitive for promotion under generic 20 bp execution friction;
- do not open 2025 to rescue the strategy;
- next work is execution-economics / actual tradable-instrument feasibility, not another forecast model search.

---

# 6G. Stage-6B Cost / Instrument Feasibility Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6B_RESULT_2026-10-01.md`

Run:
- **36893955169**
- artifact **11178542233**
- digest `sha256:3372c1546f4f077fa23f263f03f5a18a7fc525d6ee1114253802a6e84351185b`.

Result:
**BORDERLINE IMPLEMENTABILITY**

Key frozen cost/hurdle findings:

- U3 PROB_TILT full tactical PASS band: **0–1.25 bp**
- U3 strong parity: up to **0.50 bp**
- U2 PASS exists only in a non-monotonic **23–24 bp** band because cost also acts as the entry hurdle
- U1/U4 never pass the full tactical gate.

Therefore 24 bp must not be interpreted as a general break-even ceiling.

Public 2026 execution evidence:

| Instrument | Cost-side view | Project status |
|---|---|---|
| GLDM | ~1.12 bp public spread+3d fee before broker/FX | BORDERLINE |
| IAU | ~1.30 bp before broker/FX | NOT PLAUSIBLE under U3 band |
| GLD | ~1.48 bp before broker/FX | NOT PLAUSIBLE under U3 band |
| MGC | CME stated cost ~0.28 bp before broker/spread uncertainty | BORDERLINE |
| GC | very low stated exchange cost, large notional / futures basis | BORDERLINE |
| 1OZ futures | CME stated cost ~1.98 bp | NOT PLAUSIBLE |
| ALTIN.S1 | USDTRY + premium/discount target mismatch | NOT DIRECTLY PLAUSIBLE |

No instrument is frozen because empirical BIST-USD/oz-to-instrument return mapping is not yet proven.

Technical shortlist for mapping only:
- GLDM
- MGC.

2025 remains closed.

---

# 6H. Stage-6C Cross-Instrument Mapping Result

Authority:
`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6C_RESULT_2026-10-01.md`

Primary run:
- **36895412116**
- artifact **11178394090**
- digest `sha256:185a31b3cb01db3a38de22ab86269be8c9afbda0a676e2b0334347d9a3441f3f`.

Post-run timing diagnostic:
- run **36895839549**
- artifact **11179492610**.

Result:
**MAPPING FAIL / NO INSTRUMENT FREEZE**

Frozen H3 mapping:

| Instrument | Pearson | Beta | Sign agreement | TE SD | Severe divergence | Mapping |
|---|---:|---:|---:|---:|---:|---|
| GLDM | 0.5796 | 0.5063 | 71.2% | 1.516% | 46.1% | FAIL |
| MGC | 0.6244 | 0.5454 | 73.7% | 1.435% | 44.2% | FAIL |

Frozen U3 transfer:
- GLDM 1.25 bp: CAGR 2.19%, max DD -12.22%, Sortino 0.326, 1/3 positive years -> FAIL
- MGC delayed daily stress 1.00 bp: CAGR 7.95%, max DD -10.49%, Sortino 1.656, 2/3 positive years, but mapping FAIL -> no transfer authorization.

Post-run timing diagnostic:
- best GLDM daily-return row lag correlation 0.4695
- best MGC daily-return row lag correlation 0.3938.

Thus the failure is not explained by a trivial one-session shift.

Binding implication:
- BIST Metal Price USD/oz is a local T+0 weighted transaction statistic, not a universal synchronous international spot proxy;
- preserve the current H3 engine for original-target research/reporting only;
- do not transport to GLDM/MGC;
- redesign the tactical target authority before further tactical modeling.

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
| 5 | Forecast-head reconciliation / tactical signal architecture | **COMPLETE / NO PASS** |
| 6 | Tactical allocation / utility contract | **COMPLETE / NO PASS** |
| 6B | Turnover / tradable-instrument feasibility audit | **COMPLETE / BORDERLINE** |
| 6C | Cross-instrument mapping audit (GLDM / MGC) | **COMPLETE / FAIL** |
| 6D | Tactical target authority redesign | **NEXT** |
| 7 | Frozen 2025 transport | **BLOCKED — target/instrument not frozen** |
| 8 | Prospective daily ledger | NOT STARTED |

---

# 8. Exact Next Action

**Stage 6D — Tactical Target Authority Redesign**

The tactical research objective is short-horizon investable Gold exposure.

The current BIST Metal Price target may not be reused automatically.

Before new model fitting, compare target lanes:

### Lane A — international synchronous Gold
Candidate:
- BIST Spot Gold Index or another origin-safe international spot representation.

Purpose:
- instrument-agnostic Gold direction/return target
- must demonstrate strong mapping to practical implementation instruments.

### Lane B — GLDM direct
Target:
- actual GLDM executable return.

Required:
- U.S. trading calendar
- 00:30 Istanbul signal -> same-day U.S. open execution convention
- ETF cost / FX convention.

### Lane C — MGC direct
Target:
- actual Micro Gold futures executable return.

Required:
- official/timestamped CME data
- explicit contract and roll convention
- origin-safe intraday execution price.

Rules:
- no 2025 selection
- do not mix redesigned-target results with the original BIST-Metal-Price record
- preserve all Stages 0–6C as historical evidence
- target authority must be frozen before model search resumes.

Only after one lane is frozen may a new short-horizon forecast program begin.
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

Stage 5:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE5_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE5_RESULT_2026-10-01.md`
- run **36892132569**
- artifact **11177455544**.

Stage 6:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6_RESULT_2026-10-01.md`
- run **36892963306**
- artifact **11178115214**.

Stage 6B:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6B_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6B_RESULT_2026-10-01.md`
- run **36893955169**
- artifact **11178542233**.

Stage 6C:
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6C_AUTHORITY_2026-10-01.md`
- `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6C_RESULT_2026-10-01.md`
- primary run **36895412116**
- primary artifact **11178394090**
- timing diagnostic run **36895839549**
- timing diagnostic artifact **11179492610**.

Sibling projects:
- monthly forecast: `GOLD_MONTHLY_PROJECT_MANIFEST.md`
- intramonth K100 research: `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

These projects are related but scientifically separate.
