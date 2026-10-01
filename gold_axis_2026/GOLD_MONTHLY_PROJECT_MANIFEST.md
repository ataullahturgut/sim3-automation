# GOLD MONTHLY FORECAST — CANONICAL PROJECT MANIFEST

**Manifest version:** 2.1  
**Date:** 2026-10-01  
**Status:** **CURRENT / BINDING / PROFESSIONAL PROJECT STATE**  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`

> **Single-source rule:** Bu dosya güncel proje durumunun canonical otoritesidir. Ayrıntılı RESULT / AUTHORITY / JSON / workflow dosyaları kanıt katmanıdır. Tarihsel “next / active / current leader” ifadeleri bu manifesti geçersiz kılamaz.

> **Katman ayrımı:** **Fiyat tahmini ≠ piyasa rejimi ≠ tahmin-hata alarmı ≠ alarm sonrası aksiyon.**

---

# 1. Executive Project State

## 1.1 Proje kontratı

- **Target:** bir sonraki takvim ayının ortalama XAU/USD fiyatı
- **Horizon:** H=1 ay
- **Forecast origin:** önceki tamamlanmış takvim ayı
- **DEV selection authority:** 2022-04..2024-12, n=33
- **2025/2026:** opened transport / retrospective evidence; seçim ve retuning için kullanılamaz
- **Primary metrics:** DEV cumulative absolute price error ΣAE + Direction Accuracy
- **Random split:** yok
- **Target-month leakage:** yasak
- **Database:** READ_ONLY

## 1.2 Güncel fiyat modeli

**Primary: ChHHO-ANFIS**
- DEV ΣAE **1413.0298 USD**
- Direction **23/33**
- feature contract **CURRENT8**
- representation **MR1 + origin-safe GPR-conditioned VW**
- lag architecture **L1 only**

Frozen reference frontier:

| Model | Family | DEV ΣAE | Direction |
|---|---|---:|---:|
| **ChHHO-ANFIS** | ANFIS | **1413.0298** | 23/33 |
| DE-ABC-RBFNN | RBFNN | 1415.8371 | **25/33** |
| PLS1 V1 All-4 | Challenger B | 1420.0291 | 20/33 |
| LMC2_RBF_M32 | GPR/MOGP | 1424.1711 | 19/33 |
| FULL7 ANN | ANN | 1428.8590 | 22/33 |
| REDUCED4 ANN | ANN | 1431.4587 | 24/33 |
| EPSILON_RBF_DAILY12 | SVR | 1449.1874 | 19/33 |
| CATBOOST_PRICE | Boosting | 1460.4339 | 20/33 |

## 1.3 Güncel market-state / alarm / rescue

**Market state:** R1 / STABLE / NORMAL  
**p(R1):** 0.9823228737  
**OOD:** NO

**Frozen alarm router:** Specialist Hedge
- eta 0.25
- alpha 0
- HIGH threshold 0.50

**October snapshot**
- p_HIGH 0
- p_ELEVATED 0
- active signals none
- HIGH alarm NO

**Post-alarm action**
- fixed fallback REJECTED
- Rescue-Gain Predictor V1 research-only / WEAK
- Safety Guard V1 REJECTED
- automatic SWITCH / BLEND NOT AUTHORIZED

## 1.4 October-2026 forward

Origin 2026-09 / target 2026-10:

- predicted log return **-0.0135908895**
- multiplier **0.9865010496**
- September complete level proxy **4336.8513**
- October average proxy **4278.3084 USD/oz**
- implied move approximately **-1.35%**
- direction **DOWN**
- DE-ABC comparator **4255.7049 USD/oz**, DOWN

World Bank September Gold monthly average was not available at execution. When available, canonical level conversion is mechanical:

`WB_Gold_2026_09 × 0.9865010496`

No refit is required for that level-only conversion.

## 1.5 Exact next research task

**Direct Harmful-Switch / Shared-Hard Probability Model V1 — NOT YET RUN**

Goal: frozen Rescue-Gain Predictor bir switch önerdiğinde, yalnız origin-known DEV bilgisiyle bu switch’in ChHHO’da kalmaktan daha kötü olacağı öngörülebiliyor mu?

Requirements:
- harmful-switch target
- low-capacity model
- chronological expanding DEV validation
- KEEP / ABSTAIN first-class actions
- 2025/2026 only after freeze

---

# 2. Scientific Governance

## 2.1 Evaluation authority

Current decision order:
1. DEV ΣAE
2. DEV Direction Accuracy
3. MAE / RMSE / MAPE / WAPE / RW-relative / worst-month / yearly stability

Early MAPE-centered family winners are historical only.

## 2.2 Chronology

- DEV 2022-04..2024-12
- no random split
- no target-month information
- opened outcomes cannot choose model, feature, alarm threshold, regime rule, rescue selector or guard.

## 2.3 Data execution

Neon remains the authoritative source. Normal experiments use governed immutable snapshot/artifact execution after parity checks.

Authorized DEV Snapshot V1:
- artifact **10985453248**
- payload SHA-256 `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`
- canonical parity PASS.

## 2.4 Status vocabulary

- **FROZEN:** no opened-data retuning
- **PASS:** valid scientific execution; not automatic promotion
- **NOT_PROMOTED:** valid but does not replace authority
- **REJECTED:** do not deploy/revive without new reason
- **COMPLETE_CLOSED:** lane complete
- **DEFERRED / PAUSED:** not current priority
- **RESEARCH_ONLY:** no operational action
- **SUPERSEDED:** historical evidence retained, later authority controls interpretation

---

# 3. Price-Model Registry

Broad model-family search is no longer the active bottleneck.

| Family | Current status | Retained reference |
|---|---|---|
| ELM | COMPLETE_CLOSED | AOA / Vanilla |
| ANN | COMPLETE_CLOSED | FULL7 / REDUCED4 |
| ELMFIS | COMPLETE_CLOSED | completed broad/refinement program |
| ANFIS | COMPLETE_CLOSED / PRIMARY | ChHHO |
| RBFNN | COMPLETE_CLOSED | DE-ABC |
| GPR/MOGP | benchmark retained | LMC2_RBF_M32 |
| Boosting/Trees | COMPLETE_CLOSED | CATBOOST_PRICE |
| SVR/DWT-SVR | PAUSED | EPSILON_RBF_DAILY12 |
| Challenger B | COMPLETE_CLOSED | PLS1 V1 All-4 |
| CNN/LSTM/BiLSTM | CLOSED FOR CURRENT PRIORITY | CNN-LSTM LB6 / BiLSTM evidence |
| DMA/DMS/IDMA | DEFERRED_REVISIT_LAST | broader PIT panel needed |
| Modern sequence/foundation | DEFERRED | no current mandate |

Reopen only for:
- materially new architecture,
- corrected scientific defect,
- new governed representation/data contract,
- explicit user authorization.

Detailed duplicate-prevention registry:
`GOLD_MONTHLY_MODEL_REGISTRY_V2_1_2026-10-01.md`

---

# 4. Data, Variable & Feature Architecture

## 4.1 Binding ChHHO input contract

After F0–F3:
- CURRENT8 retained
- MR1 retained
- GPR-conditioned VW retained
- L1 only
- no feature deletion promoted
- no F2 representation expansion promoted
- no multi-lag package promoted.

## 4.2 Main feature-audit conclusions

**F0/F1**
- MR-only and VW-only materially worse
- every one-feature deletion worsened DEV ΣAE
- Gold+Silver compact version showed small aggregate gain but poor month-wise robustness
- decision: CURRENT8 retained.

**F2**
- MR3/MR6/RV/range/ABSRET variants tested
- best non-baseline still failed promotion robustness
- decision: MR1 + VW retained.

**F3**
- L1+L2, L1+L2+L3 and distributed-lag packages materially worse
- decision: L1 only.

## 4.3 Native external-family research

ALL6 compact external expansion (Rates + USD + VIX + Nasdaq + WTI + Brent) degraded strongly.

Subsequent decomposition:
- Rates native family: tested / not promoted / closed for current contract
- FX native family: tested / not promoted / closed for current contract
- raw-data reaudit: PASS; no source/date/transform corruption demonstrated.

Therefore current evidence does **not** justify expanding primary ChHHO beyond CURRENT8.

## 4.4 Residual research boundary

Residual correction is separate from native feature promotion.

Later BIAS_ONLY control:
- BIAS_ONLY DEV ≈1338.89
- VIX_R1 ≈1338.33, only ≈0.56 better than BIAS_ONLY
- Brent R1 ≈1346.50, worse than BIAS_ONLY
- PIT Rates ≈1370.92, worse than BIAS_ONLY.

Earlier CPI/external-driver results remain preserved under their own frozen protocol but are not treated as native CURRENT8 promotions.

Detailed feature/data ledger:
`GOLD_MONTHLY_FEATURE_RESEARCH_LEDGER_V2_1_2026-10-01.md`

---

# 5. Market-Regime & State System

## 5.1 Non-circular regime contract

Regime fitting uses market-state variables only. ChHHO errors, alarms, severity labels, model forecasts and router outputs are excluded.

## 5.2 Regime Discovery V1

Development 2010-07..2024-12, 174 months.

13D panel includes Gold trend/level/volatility, cross-metal dispersion, GVZ, CFTC positioning/OI, USD, nominal/real yields and ETF-flow state.

Gaussian HMM BIC:
- K1 3405.30
- K2 3342.75
- **K3 3334.20**
- K4 3353.59
- K5 3380.92

Weighted self-transition ≈89.2%.

Binding semantic states:
- **R0:** drawdown / macro-pressure / stress
- **R1:** quiet / neutral / low-volatility
- **R2:** bullish / accumulation / elevated
- **BELIRSIZ:** low posterior confidence, not a fourth economic regime.

## 5.3 Walk-forward / alignment

Walk-forward 2025-01..2026-08:
- confident-state accuracy 88.9%
- decided-only 100%
- R2 recall 93.75%
- R1 recall 50%.

Prototype alignment improves historical semantic consistency but changes 0/20 recent transport months; recent transition difficulty is not a label-switching artifact.

Annual anchoring is sensitivity evidence; no decisive operational winner.

## 5.4 Transition / extreme

**Transition V1:** too many false transitions → not promoted.  
**Transition V2:** catches later transitions better but 2022-2024 false-transition rate remains above gate → promotion fail; context only.  
**Transition V3 duration-aware:** lower false rate by missing true transitions → promotion fail.  
**Extreme V1:** distinct within-regime stress layer; descriptive only.

No regime / transition / extreme state automatically changes ChHHO.

## 5.5 ChHHO reliability by state

Origin-state audit does not show a stable monotonic regime-risk rule:
- DEV EXTREME/TRANSITION do not behave consistently as high-risk;
- opened 2025/2026 transition origins look dangerous, but the relationship reverses relative to DEV.

Decision:
- no regime multiplier
- no transition switch
- no extreme switch.

## 5.6 Current state

September-2026 origin:
- **R1**
- posterior **0.9823228737**
- STABLE
- NORMAL
- OOD NO.

Evidence:
`GOLD_MONTHLY_SEPTEMBER_2026_REGIME_STATE_RESULT_2026-10-01.md`

---

# 6. Alarm & Reliability System

## 6.1 Severity

- NORMAL: APE <2.5%
- MEDIUM: 2.5% <= APE <3.0%
- HIGH: APE >=3.0%.

Alarm predicts **forecast-error risk**, not UP/DOWN.

## 6.2 Signal catalog

| Signal | Role |
|---|---|
| A | selective metal-disagreement / underreaction mechanism |
| B | strong-Gold / supportive-macro underreaction warning |
| C | medium-error / weak-forecast warning |
| D | rare HIGH mechanism |
| E | discovery-period elevated-level mismatch warning |
| G | high-movement regime warning |
| H | CFTC positioning/OI repricing warning |
| I1 | ETF flow deterioration warning |
| I2 | persistent GLD+IAU outflow breadth warning |
| T1_WGC | early target-month WGC two-outflow confirmation |
| V2_TRANSITION | market-only transition context expert |
| NULL | always-awake no-risk expert |

## 6.3 Rejected simplifications

- DEV fine-tuned RED: rejected on untouched transport
- hard cross-model SAFE veto: transport harmful
- recency/adaptive reliability gate: insufficient
- regime/V2 shrinkage reliability: worsened calibration.

Do not retune these on opened outcomes.

## 6.4 Frozen Specialist Hedge

Selected:
- HEDGE eta=0.25
- alpha=0
- tau=0.50.

DEV:
- 20 warnings
- 8/8 HIGH
- 2/2 MEDIUM
- 10 false
- HIGH/elevated recall 100%
- raw false calls reduced from 15 to 10.

Opened 2025:
- 7 warnings = 5 HIGH +1 MEDIUM +1 false.

Opened 2026 Jan-Aug:
- 6 warnings = 3 HIGH +1 MEDIUM +2 false.

Decision:
**Specialist Hedge is the frozen reliability router.**

## 6.5 October snapshot

Origin 2026-09:
- all T0 signals OFF
- V2 STABLE
- T1_WGC unavailable at T0
- p_HIGH 0
- p_ELEVATED 0
- HIGH alarm NO.

Evidence:
`GOLD_MONTHLY_OCTOBER_2026_SPECIALIST_HEDGE_ALARM_SNAPSHOT_V1_RESULT_2026-10-01.md`

---

# 7. Post-Alarm Rescue & Decision Research

## 7.1 Rescueability

DEV Specialist Hedge warnings:
- 20 total
- 10 true HIGH/MEDIUM
- 10 false/NORMAL.

LMC2 on true elevated warnings:
- +101.76 USD gain
- wins 8/10.

LMC2 on all 20 ex-ante warnings:
- -16.11 USD gain vs KEEP.

Decision:
**HIGH → fixed fallback rejected.**

KEEP-or-best warning hindsight ceiling:
**+469.73 USD**.

## 7.2 33×15 gain matrix

`gain(j,t)=|error_ChHHO|-|error_model_j|`

Findings:
- no fixed challenger beats ChHHO cumulatively over all 33 DEV months
- best fixed all-33 DE-ABC gain = -2.81 USD
- all-33 KEEP-or-best hindsight ceiling = +708.51 USD
- simple p_HIGH/regime/consensus/dispersion rules are insufficient.

## 7.3 Rescue-Gain Predictor V1

Frozen DEV leader:
- RIDGE_CORE_A10
- DIRECT_SWITCH.

Chronological DEV warnings:
- KEEP ΣAE 782.7432
- selector 778.0388
- gain +4.7044
- beneficial 5
- harmful 8
- worst harm 31.6639.

Decision:
**formal PASS but WEAK / research-only.**

## 7.4 Frozen opened transport

2025-01..2026-07:
- KEEP ΣAE 2153.0192
- selector 2057.7830
- gain +95.2362
- beneficial 7
- harmful 4
- worst harm 238.5690.

Critical 2026-03:
- predicted rescue positive
- realized switch loss vs KEEP ≈ -238.57 USD.

## 7.5 Safety Guard V1

Breadth/confidence deterministic guard family failed.

Expanding replay:
- guard -22.5427 USD
- same-window NO_GUARD +0.9418 USD.

Decision:
**Guard V1 REJECTED.**

## 7.6 Production boundary

- ChHHO = price forecast
- Specialist Hedge = frozen risk warning
- regime = context
- Rescue Predictor = research-only
- Guard V1 = rejected
- automatic SWITCH / BLEND = not authorized.

---

# 8. Live Forward State

October-2026:
- ChHHO proxy **4278.3084 USD/oz**
- direction **DOWN**
- DE-ABC **4255.7049**
- origin state **R1/STABLE/NORMAL**
- p_HIGH **0**
- automatic correction **none**.

Evidence:
- `GOLD_MONTHLY_OCTOBER_2026_FORWARD_RESULT_2026-10-01.md`
- `GOLD_MONTHLY_SEPTEMBER_2026_REGIME_STATE_RESULT_2026-10-01.md`
- `GOLD_MONTHLY_OCTOBER_2026_SPECIALIST_HEDGE_ALARM_SNAPSHOT_V1_RESULT_2026-10-01.md`

---

# 9. Current Roadmap

## 9.1 Immediate priority

**Direct Harmful-Switch / Shared-Hard Probability Model V1**

Allowed origin-known context:
- router probabilities
- active signals/experts
- regime posterior/state
- transition/extreme/OOD
- ensemble geometry
- predicted rescue distribution
- selected challenger prior-history diagnostics.

Forbidden:
- target actual
- target realized severity
- target-month state
- opened-period tuning.

Evaluation:
- low-capacity candidates
- expanding DEV validation
- cumulative AE / gain vs KEEP
- beneficial/harmful actions
- worst incremental harm
- coverage.

Promotion requires both aggregate improvement and meaningful harm reduction.

## 9.2 Explicit non-actions

Do not:
- use fixed fallback
- switch on R0/R1/R2
- use EXTREME or Transition V2 as hard switch
- revive Exact16 veto
- retune Specialist Hedge on 2025/2026
- productionize Rescue Predictor V1
- revive Guard V1 thresholds
- choose a challenger from opened hindsight.

---

# 10. Document Hierarchy & Change Control

## 10.1 Canonical hierarchy

**Current state**
- `GOLD_MONTHLY_PROJECT_MANIFEST.md`

**Model duplicate-prevention**
- `GOLD_MONTHLY_MODEL_REGISTRY_V2_1_2026-10-01.md`

**Detailed feature/variable research**
- `GOLD_MONTHLY_FEATURE_RESEARCH_LEDGER_V2_1_2026-10-01.md`

**Historical archives**
- `archive/GOLD_MONTHLY_PROJECT_MANIFEST_PRE_V2_2026-10-01.md`
- `archive/GOLD_MONTHLY_PROJECT_MANIFEST_V2_0_2026-10-01.md`

Run-level RESULT/AUTHORITY/JSON files remain authoritative evidence for exact experiment details.

## 10.2 Update standard

Each new experiment records:
- question
- frozen authority
- chronology
- candidate universe
- DEV result
- opened role
- scientific gate
- decision
- reopen condition
- run/artifact/commit provenance.

**Do not append unstructured date blocks at EOF.**

## 10.3 Supersession

Sections 1 and 9 are the definitive current state and roadmap.

Old stage-local references such as:
- CNN-BiLSTM “next”
- F2/F3/F4 “next”
- RED alarm
- hard consensus veto
- Rescue Predictor “not yet run”
- Safety Guard “next”

are historical and non-binding.

## 10.4 Compliance checkpoint

- professional canonical structure: YES
- old local next/active statements in canonical: NO
- old 20A–20L numbering in canonical: NO
- detailed evidence preserved externally: YES
- DEV authority: 2022-04..2024-12
- random split: NO
- opened-data tuning: NO
- target leakage: NO
- DB write: NO
- ChHHO primary: YES
- Specialist Hedge frozen: YES
- automatic rescue switch: NO
- exact next task: Direct Harmful-Switch / Shared-Hard Probability Model V1

---

# 11. Executive Chronology

- **2026-09-25..28:** broad model-family program and cross-family frontier
- **2026-09-28..29:** external-driver, data-governance and F0–F4 feature research
- **2026-09-30:** regime discovery / transition / extreme / alarm program; Specialist Hedge frozen
- **2026-10-01:** complete-September October forward; current regime/alarm snapshot; rescue matrix; relative-loss predictor; opened transport; rejected Safety Guard; manifest V2.1 corporate normalization

**Current one-line state:**  
**ChHHO-ANFIS remains the monthly price anchor; CURRENT8 remains the input contract; September-2026 origin is R1/STABLE/NORMAL; Specialist Hedge is OFF for October; automatic rescue switching is not authorized; next research is Direct Harmful-Switch / Shared-Hard Probability Model V1.**
