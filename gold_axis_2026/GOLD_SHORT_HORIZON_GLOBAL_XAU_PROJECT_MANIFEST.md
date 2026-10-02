# GOLD SHORT-HORIZON GLOBAL XAU PROJECT MANIFEST

**Manifest version:** 2.0  
**Date:** 2026-10-02  
**Status:** ACTIVE — R2 SOURCE/TIMELINE REPAIR COMPLETE / H3 DEV SIGNAL ROBUST / 2025–SEP-2026 FROZEN TRANSPORT FAILED  
**Canonical branch:** `gold-midas-headswap-v1-20260925`  
**Supersedes for current daily objective:** R1 stale-snapshot mainline and the archived BIST-Metal-Price tactical mainline.

## 1. Objective and frequency

Build a separate **daily-frequency Global XAU/USD** short-horizon research engine.

Frozen horizons:
- H1
- H3
- H5

Frozen target forms:
- forward log return
- direction
- Q10/Q50/Q90 distribution.

Target equations:
- H1 = `log(P[t+1]/P[t])`
- H3 = `log(P[t+3]/P[t])`
- H5 = `log(P[t+5]/P[t])`.

The project does **not** revert to monthly target frequency. Monthly-project data authorities may be reused, but their monthly aggregation is not imported into this daily target.

## 2. Current target/source authority

### 2.1 Active research identity — R2

The current daily research identity is:

**`GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`**

R2 is a **full-history reconstruction at one pinned public StakTrakr commit**, not a silent append to the prior Neon R1 snapshot.

Current frozen evidence snapshot:
- StakTrakr commit: `54fdf1c8d39b7b6c7b874d0f30f784296e886044`
- common weekday Gold/Silver/Platinum/Palladium coverage: **2010-01-04 .. 2026-09-29**
- common observations: **4,233**.

The StakTrakr payload is a mixed historical reconstruction. Provider/source labels in the frozen R2 payload are, per metal:
- `seed|LBMA`: 4,069 rows
- `seed|MetalPriceAPI`: 8 rows
- `seed|StakTrakr`: 4 rows
- `sqld|`: 152 rows.

Therefore the earlier shorthand “StakTrakr = MetalPriceAPI daily spot-average” is **superseded**. The binding description is: **pinned StakTrakr public research reconstruction with mixed provider labels, overwhelmingly LBMA-tagged in the historical payload**.

R2 is research reconstruction evidence; it is not represented as historical point-in-time market data.

### 2.2 Historical R1 identity — retained but no longer active

Historical DB series:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`.

R1 provenance:
- pinned source: `lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`
- DB coverage through **2026-07-31**
- source-registry evidence class: `HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM`
- status: `APPROVED_RESEARCH_ONLY_NOT_PIT`.

R1 remains historical evidence only. It must not be extended as if current public StakTrakr were byte-for-byte the same frozen series.

### 2.3 Why silent R1 append was rejected

Repair V1 attempted a fail-closed same-source continuity check before appending August/September.

Workflow run:
- **36984276527**

Result:
- **FAIL CLOSED**
- Gold maximum same-date relative difference versus current public StakTrakr: **1.8088%**.

A dedicated lineage audit then confirmed that current public 2026 values differ from the old pinned DB snapshot for all four metals.

Lineage audit:
- run **36984720262**
- artifact **11216956630**.

For Gold in 2026 same-date comparison:
- n = 189
- exact-within-1e-8 share = 75.13%
- mean relative difference = 0.1069%
- maximum relative difference = 1.8088%.

Thus the active repair became a **new full-history R2 reconstruction**, not a stitch.

## 3. Correct daily timeline contract

The former generic `date` / `signal_date` wording is superseded for current ledgers.

Binding fields:
- `feature_cutoff_date`: last retained Gold observation used by the feature transforms;
- `forecast_issue_date`: next retained weekday Gold observation date after the feature cutoff;
- `target_start_date`: Gold date from which the forward return is measured;
- `target_end_date_h1`, `target_end_date_h3`, `target_end_date_h5`: exact retained Gold dates at which each target matures.

This is a **label/clock correction**, not a target-formula change.

For H3, a row is usable for scoring only when `target_end_date_h3` is observed.

## 4. Governance

Binding evaluation roles:
- training/background history: through 2021
- DEV selection/tuning authority: **2022-2024 only**
- 2025: **frozen transport; no tuning**
- 2026: opened retrospective/prospective reporting only; **no selection authority**.

Other rules:
- no random split
- chronological expanding evaluation
- no target-day/future measurements in earlier-origin features
- no 2025/2026 threshold, calibration, feature or regime-gate rescue
- no BIST target values in the active Global-XAU lane
- no trading/P&L optimization until statistical transport evidence is adequate.

## 5. Existing project source registry and daily clock rules

The daily project inherits the already-established Gold Control / monthly-project source universe. It must not rediscover unrelated providers when an existing project authority already exists.

| Family | Existing project authority / examples | Daily short-horizon rule |
|---|---|---|
| XAU market | StakTrakr reconstruction; Twelve Data XAU/USD; `XAU_EOD_TWELVE_NY17`; XAU 1m/5m research caches; XAUS series | Target identity and clock must be explicit; clocks are never silently stitched. |
| Precious metals | Gold/Silver/Platinum/Palladium research histories | As-of feature cutoff / previous available observation. |
| Rates | DGS10, DFII10, H.15 concepts | Release-aware/as-of; conservative availability lag. |
| FX / USD | corrected Broad-USD authority / H.10 plus major FX | Release-aware/as-of. DEXCHUS is not Broad USD. |
| Volatility | VIX, GVZ | Strictly previous available observation at a daily origin unless an origin-time contract proves otherwise. |
| Equities | Nasdaq-100, S&P500, DJIA | Strictly previous available observation at the XAU origin. |
| GPR / regime | GPR, BOCPD | Release/vintage-aware context only. |
| Macro events | NFP, unemployment, AHE first-print + PIT consensus; inflation/FOMC aligned data where proven | Event-time specialist/context, not ordinary daily forward-fill. |
| Oil | WTI / Brent authorities in the wider project data estate | Challenger only after exact short-horizon PIT/clock mapping is frozen. |
| Engine states | FAST, SLOW, Monthly Direction, Emergency, GVZ, Macro Event, BOCPD | Optional context/meta-model inputs; not equal-vote signals by default. |

Daily source-clock audit:
- run **36985733236**
- artifact **11216859190**.

Observed registry coverage in that audit:
- EQUITY: latest 2026-10-01
- FX/USD: latest 2026-09-25
- GPR: latest 2026-09-01
- RATES: latest 2026-09-29
- VOL: latest 2026-10-01
- XAU registered sources: latest 2026-10-02.

The old R1 precious-metal DB series remain through 2026-07-31; R2 August/September evidence comes from the pinned **full public StakTrakr reconstruction**, not from silently writing new rows into R1.

## 6. Feature blocks

Gold path:
- gold_r1
- gold_r3
- gold_r5
- gold_r10
- gold_r21
- sigma20.

CORE3:
- Gold path
- Silver r1/r5/r21 + age
- Platinum r1/r5/r21 + age.

CORE4:
- CORE3 + Palladium r1/r5/r21 + age.

External blocks:
- H.15 rates
- H.10/Broad-USD + FX
- VIX
- Nasdaq-100
- related registered challengers only under frozen source-clock contracts.

Current winning direction engine remains **CORE3**. External families are not silently added because they are available.

## 7. R2 data readiness — current authority

R2 readiness:
- run **36985071213**
- artifact **11217361007**
- status **PASS**.

Pinned source:
- StakTrakr commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`.

Coverage:

| Horizon | Train history | DEV | 2025 frozen | Opened 2026 | Last forecast issue |
|---|---:|---:|---:|---:|---|
| H1 | 3,010 | 755 | 253 | 193 | 2026-09-29 |
| H3 | 3,010 | 755 | 253 | 191 | 2026-09-25 |
| H5 | 3,010 | 755 | 253 | 189 | 2026-09-23 |

August and September 2026 are therefore present in the corrected daily research panel.

## 8. R2 Stage 1 — model/horizon screen

Scientific screen:
- run **36985266866**
- all H1/H3/H5 screen jobs completed successfully;
- aggregate computation also completed successfully;
- the workflow-level failure was only a concurrent Git push rejection after calculation.

The aggregate evidence was recovered and committed by:
- run **36985805975**.

R2 Stage-1 result:

| Horizon | Direction | Return | Quantile |
|---|---|---|---|
| H1 | FAIL | FAIL | FAIL |
| **H3** | **PASS** | FAIL | FAIL |
| H5 | FAIL | FAIL | FAIL |

H3 direction:
- feature block: **CORE3**
- model: **Logistic L2**
- Brier: **0.246637**
- baseline Brier: **0.249707**
- relative Brier improvement: **+1.23%**
- log loss: **0.686447** vs baseline **0.692562**.

The structural result from R1 survives the repair: **only H3 direction clears the pre-2025 first-screen gate**.

## 9. R2 Stage 2 — robustness and representation

Stage 2:
- run **36985881794**
- artifact **11217532283**
- status **ROBUST_PASS**.

Frozen H3 direction engine:
- **CORE3 / Logistic L2**
- Brier **0.246637**
- baseline **0.249707**
- relative improvement **+1.23%**
- log loss **0.686447**
- prediction SD **0.04478**
- accuracy **54.97%**
- balanced accuracy **54.48%**.

Annual relative Brier improvement:
- 2022: **+1.93%**
- 2023: **+0.19%**
- 2024: **+1.56%**.

All three DEV years remain positive.

Representation comparison:
- GOLD_ONLY: -0.14%
- **CORE3: +1.23%**
- CORE4: +0.76%
- CORE3 + raw external: -0.24%
- CORE3 + transformed external: -0.31%.

Decision:
- retain **CORE3**
- do not promote Palladium
- do not promote the current external block
- H5 remains below the >=1% secondary gate.

Pre-2025 coefficient-sign audit across 151 refits shows strong directional stability for the main nonzero CORE3 coefficients, including silver_r5 (+), platinum_r5 (-), gold_r5 (-), platinum_r1 (+), gold_r1 (-), gold_r21 (-), platinum_r21 (-), sigma20 (+), and gold_r3 (-).

## 10. R2 Stage 3 — calibration and conviction

Stage 3:
- run **36985982704**
- artifact **11217776177**
- status **CONVICTION_PASS**
- selected probability stream: **RAW**.

Calibration:

| Method | Brier | Log loss | Pred SD | ECE | Decision |
|---|---:|---:|---:|---:|---|
| **RAW** | **0.246637** | **0.686447** | 0.0448 | 0.0256 | **RETAIN** |
| PLATT | 0.250293 | 0.694202 | 0.0544 | 0.0223 | REJECT |
| ISOTONIC | 0.252886 | 0.746264 | 0.1017 | 0.0460 | REJECT |

Frozen DEV conviction:
- p >= 0.55: n=148, realized H3 UP **62.84%**
- p <= 0.45: n=64, realized H3 UP **40.63%**
- separation: **22.21 pp**
- yearly support counts high side: 54 / 44 / 50
- yearly support counts low side: 18 / 25 / 21.

This is a DEV-level conviction pass only. It does **not** authorize a tactical rule because frozen transport below fails.

## 11. R2 frozen transport through September 2026

Frozen transport:
- run **36985617377**
- artifact **11217536725**
- engine: **H3 / CORE3 / Logistic L2 / RAW**
- mode: **STRICT_FROZEN_FIT**
- training rows: **3,784**
- last training target maturity: **2024-12-31**
- no 2025/2026 tuning.

Scoring coverage:
- last forecast issue: **2026-09-25**
- last observed H3 target end: **2026-09-29**
- August 2026: **21** fully matured H3 forecasts
- September 2026: **19** fully matured H3 forecasts.

| Period | N | Accuracy | Balanced accuracy | Brier | Log loss | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 253 | 50.2% | 50.1% | 0.2508 | 0.6946 | 50.6% | 49.5% |
| 2026 Jan-Sep | 191 | 44.0% | 45.2% | 0.2727 | 0.7420 | 71.4% | 19.0% |
| 2026 Aug | 21 | 47.6% | 53.6% | 0.2488 | 0.6906 | 35.7% | 71.4% |
| 2026 Sep | 19 | 47.4% | 58.3% | 0.2602 | 0.7137 | 100.0% | 16.7% |

Conviction transport also fails/reverses:
- 2025 p>=0.55: n=54, realized UP **46.30%**
- 2025 p<=0.45: n=47, realized UP **44.68%**
- 2026 p>=0.55: n=86, realized UP **44.19%**
- 2026 p<=0.45: n=19, realized UP **63.16%**.

Binding interpretation:
- the repaired R2 H3 DEV signal is real under the pre-2025 contract;
- it **does not transport** into 2025/2026;
- the DEV conviction bands do not transport and in 2026 reverse economically/directionally;
- do not tune probability thresholds on 2025/2026;
- do not proceed to tactical/P&L optimization with this engine.

## 12. R2 regime / distribution-shift diagnostic

Diagnostic:
- run **36986075498**
- artifact **11216934518**
- status **DIAGNOSTIC ONLY — NO RETUNING**.

Probability/outcome state:

| Period | Mean P(UP) | Actual UP | Accuracy |
|---|---:|---:|---:|
| 2025 | 0.500 | 61.7% | 50.2% |
| 2026 Jan-Sep | 0.553 | 47.6% | 44.0% |
| 2026 Jul | 0.546 | 34.8% | 30.4% |
| 2026 Aug | 0.475 | 66.7% | 47.6% |
| 2026 Sep | 0.536 | 36.8% | 47.4% |

Largest documented shift:
- 2026 `sigma20` mean shift: **+7.88 DEV SD**
- 2026 `sigma20` standard-deviation ratio: **14.93**
- PSI: **7.768**.

Other 2026 shifts include materially wider Gold/Silver/Platinum return-feature distributions.

2025 also shows meaningful shifts, particularly silver_r21, gold_r21, sigma20 and platinum_r21.

These findings diagnose failure anatomy. They **must not** be converted into a post-hoc 2025/2026 regime gate.

## 13. What is superseded versus retained

### Superseded for the active lane

The following R1 interpretations are superseded by R2:
- active target coverage ending 2026-07-31
- the shorthand “underlying source = MetalPriceAPI”
- ambiguous `signal_date` presentation
- R1 Stage-3 `NO_CONVICTION_PASS` as the current pre-2025 conclusion
- R1 Jan-Jul-only 2026 transport as the current transport table.

R1 artifacts remain historical audit evidence and are not deleted.

### Retained findings

The following structural findings survive R2:
- Global XAU, not BIST Metal Price, is the active tactical-research target family
- H3 is the only first-screen horizon with a pre-2025 direction signal
- CORE3 / Logistic L2 is the current classical direction comparator
- Palladium and the first external block are not promoted
- no return-magnitude or quantile head passes
- 2025/2026 transport is inadequate for tactical promotion
- no P&L optimization is authorized.

### Archived BIST lane

`GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md` is archived historical evidence. Its BIST target results must not be merged into the Global-XAU performance tables.

## 14. Prospective refresh contract

The R2 evidence above is frozen to StakTrakr commit:
`54fdf1c8d39b7b6c7b874d0f30f784296e886044`.

A later daily refresh must:
1. resolve and record a new exact source commit/ref;
2. preserve the prior R2 evidence snapshot;
3. rebuild the current-source panel under the same explicit timeline semantics;
4. never mutate past reported R2 numbers silently;
5. never use newly observed 2025/2026 outcomes to retune the frozen comparator.

Twelve Data/NY17, XAUS, intraday cache, ETF or futures clocks remain separate identities unless a separately frozen target contract authorizes them.

## 15. Daily cross-family challenger checklist

Frozen comparator for the checklist:
- target: H3 UP/DOWN
- feature comparator: CORE3
- model comparator: Logistic-L2 / RAW
- DEV: 2022-2024 only
- comparator Brier: 0.2466373999
- comparator log loss: 0.6864471944
- 2025/2026: transport/reporting only, never selection.

Checklist order:

| # | Family / model | Daily H3 status | Decision |
|---:|---|---|---|
| 1 | ANFIS | **COMPLETE** | Vanilla and ChHHO both NOT_PROMOTED |
| 2 | RBFNN | NOT_RUN | NEXT |
| 3 | PLS | NOT_RUN | queued |
| 4 | GPR / MOGP | NOT_RUN | queued |
| 5 | ANN FULL7 | NOT_RUN | queued |
| 6 | ANN REDUCED4 | NOT_RUN | queued |
| 7 | SVR | NOT_RUN | queued |
| 8 | CatBoost | NOT_RUN | queued |
| 9 | ELM | NOT_RUN | queued |
| 10 | DMA / DMS | NOT_RUN | queued |
| 11 | Random Forest | NOT_RUN | queued |
| 12 | Extra Trees | NOT_RUN | queued |
| 13 | CNN-LSTM | NOT_RUN | queued |
| 14 | ELMFIS | NOT_RUN | queued |
| 15 | Huber | NOT_RUN | queued |
| 16 | Ridge | NOT_RUN | queued |
| 17 | BiLSTM | NOT_RUN | queued |
| 18 | GPReg-Matérn | NOT_RUN | queued |
| 19 | GPReg-RBF | NOT_RUN | queued |

Explicitly excluded from this checklist:
- ARIMA
- SARIMA
- Prophet
- TimesFM-3
- TimeMixer++
- TimeXer.

### 15.1 ANFIS Stage A — Vanilla

Authority:
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_CHALLENGER_AUTHORITY_2026-10-02.md`

Vanilla architecture:
- 14 CORE3 inputs
- 5 Gaussian rules
- first-order Sugeno/TSK
- analytic LSE consequents
- Jang-style normalized-gradient premise learning
- chronological checking tail
- no metaheuristic.

Result:
- workflow run **36991069231**
- status **NOT_PROMOTED**
- DEV n = 755
- Brier **0.251124**
- log loss **0.695898**
- accuracy **52.05%**
- balanced accuracy **51.64%**
- relative Brier improvement vs frozen Logistic = **-1.82%**.

Annual relative Brier versus Logistic:
- 2022: **-3.47%**
- 2023: **+1.35%**
- 2024: **-3.38%**.

Vanilla challenger gate: **FAIL**.

### 15.2 ANFIS Stage B — ChHHO hybrid

Execution order respected: Vanilla completed and was recorded before hybrid execution.

Hybrid architecture:
- same 14-input / 5-rule ANFIS
- chaotic initialization
- Harris Hawks Optimization of premise centers/log-spreads
- population 8
- generations 8
- analytic consequents per candidate
- chronological checking selection
- Jang local refinement after HHO.

Result:
- workflow run **36991497737**
- status **NOT_PROMOTED**
- DEV n = 755
- Brier **0.255899**
- log loss **0.706268**
- accuracy **50.20%**
- balanced accuracy **49.94%**
- relative Brier improvement vs frozen Logistic = **-3.76%**.

Annual relative Brier versus Logistic:
- 2022: **-5.56%**
- 2023: **-0.03%**
- 2024: **-5.73%**.

ChHHO challenger gate: **FAIL**.

Binding ANFIS decision:
- monthly ChHHO superiority does **not** transfer to this daily H3 direction problem;
- Vanilla is better than the daily ChHHO hybrid on DEV;
- no ANFIS rescue tuning on opened years;
- ANFIS checklist row is closed.

### 15.3 User-authorized 2025/2026 opened transport report

After the DEV decision was frozen, the user explicitly authorized reporting both ANFIS models on opened years.

Transport authority:
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_TRANSPORT_AUTHORITY_2026-10-02.md`
- mode: **STRICT_FROZEN_FIT**
- training rows: **3,784**
- last training target maturity: **2024-12-31**
- no 2025/2026 label used for fitting or selection
- scoring through forecast issue **2026-09-25**, H3 target end **2026-09-29**.

Opened results:

| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss |
|---|---|---:|---:|---:|---:|---:|
| Vanilla ANFIS | 2025 | 253 | 51.38% | 50.83% | 0.257784 | 0.710436 |
| ChHHO-ANFIS | 2025 | 253 | **53.75%** | **53.53%** | **0.249717** | **0.694378** |
| Logistic L2 | 2025 | 253 | 50.20% | 50.06% | 0.250756 | 0.694636 |
| Vanilla ANFIS | 2026 Jan-Sep | 191 | 45.03% | 45.87% | 0.304693 | 1.248899 |
| ChHHO-ANFIS | 2026 Jan-Sep | 191 | **50.26%** | **51.21%** | 0.303964 | 1.235350 |
| Logistic L2 | 2026 Jan-Sep | 191 | 43.98% | 45.21% | **0.272677** | **0.741953** |

2026 August:
- Vanilla ANFIS accuracy **57.14%**, balanced accuracy **67.86%**, Brier 0.259859.
- ChHHO-ANFIS accuracy **38.10%**, balanced accuracy **42.86%**, Brier 0.274031.
- Logistic L2 accuracy **47.62%**, balanced accuracy **53.57%**, Brier 0.248849.

2026 September:
- Vanilla ANFIS accuracy **47.37%**, balanced accuracy **55.36%**, Brier 0.276403.
- ChHHO-ANFIS accuracy **52.63%**, balanced accuracy **56.55%**, Brier 0.257079.
- Logistic L2 accuracy **47.37%**, balanced accuracy **58.33%**, Brier 0.260167.

Interpretation:
- ChHHO gives the best **opened-year direction accuracy** among the three in both 2025 and Jan-Sep 2026.
- On 2025 Brier, ChHHO is also slightly better than Logistic.
- In 2026, however, both ANFIS probability streams are badly overconfident/miscalibrated: Brier and especially log loss deteriorate sharply relative to Logistic.
- Therefore opened accuracy improvement must not be confused with better probabilistic forecasting.

## 15.4 Raw-source shallow CART pattern screen

User authorized a simple pattern screen on the already-available raw daily source families before deeper log/rule inspection.

Authority:
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_RAW_SOURCE_CART_AUTHORITY_2026-10-02.md`

Workflow:
- run **37000320782**
- model: shallow CART
- criterion: log-loss
- max depth: 3
- minimum leaf: 60
- DEV only: 2022-2024
- 2025/2026 not used.

Raw daily source families represented:
- Gold
- Silver
- Platinum
- Palladium
- NASDAQ-100
- S&P 500
- DJIA.

Minimal lag-safe transforms:
- 1-day, 5-day, 21-day log returns
- Gold 20-day realized daily-return volatility.

The XAU 1-hour source was intentionally left for a separate intraday add-on screen because its available history begins in 2022 and cannot support the same pre-DEV expanding-history contract at the start of 2022.

DEV results:

| Source block | N | Accuracy | Balanced acc | Brier | Log loss |
|---|---:|---:|---:|---:|---:|
| GOLD_ONLY | 755 | **51.92%** | **50.35%** | **0.252650** | **0.698884** |
| METALS4 | 755 | 50.60% | 50.02% | 0.252962 | 0.701126 |
| GOLD_EQUITY3 | 755 | 49.40% | 49.21% | 0.258808 | 0.712499 |
| ALL7 | 755 | 48.48% | 48.36% | 0.263193 | 0.721218 |

Immediate result:
- the simple depth-3 tree does **not** improve as more raw source families are added;
- `GOLD_ONLY` is the strongest of the four tree blocks on aggregate DEV;
- METALS4 is close on Brier but not on accuracy;
- adding the three equity indices reduces aggregate DEV performance in this first shallow-tree specification.

Logs retained for later analysis:
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_RAW_SOURCE_CART_SPLIT_USAGE_2026-10-02.csv`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_RAW_SOURCE_CART_IMPORTANCES_2026-10-02.csv`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_RAW_SOURCE_CART_RULES_2026-10-02.json`
- annual and prediction ledgers.

No rule/log interpretation is promoted yet; that is a separate next diagnostic step.

## 16. Exact next research action

The next checklist family is:

**RBFNN — first plain RBFNN, then the DE-ABC hybrid/reference adaptation.**

The same governance remains binding:
- DEV selection 2022-2024 only;
- frozen H3 CORE3 Logistic-L2 comparator;
- no 2025/2026 selection or retuning;
- only a DEV-gate passer receives one-shot frozen transport.

No tactical/P&L layer is authorized before a challenger shows adequate statistical transport evidence.

## 17. Current evidence hierarchy

## 17. Current evidence hierarchy

Current R2 authority files:
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_READINESS_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_READINESS_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE1_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE1_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE2_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE2_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE2_COEFFICIENT_STABILITY_2026-10-02.csv`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE3_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_STAGE3_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_TRANSPORT_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_TRANSPORT_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_TRANSPORT_PREDICTIONS_2026-10-02.csv`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_DRIFT_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_DRIFT_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_SOURCE_CLOCK_AUDIT_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_SOURCE_LINEAGE_AUDIT_2026-10-02.json`.
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_CHALLENGER_AUTHORITY_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_VANILLA_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_VANILLA_SUMMARY_2026-10-02.json`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_CHHHO_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_ANFIS_CHHHO_SUMMARY_2026-10-02.json`.

Repair/failure evidence:
- `GOLD_SHORT_HORIZON_GLOBAL_XAU_REPAIR_AUTHORITY_2026-10-02.md`
- failed continuity run **36984276527**
- lineage audit run **36984720262**.

Historical R1 files remain available for audit but do not override the R2 sections above.


## Target research — H1/H3/H5 and volatility-normalized barriers (2026-10-02)

Authority:
- `GOLD_SHORT_HORIZON_TARGET_RESEARCH_AUTHORITY_2026-10-02.md`

Successful workflow:
- run **37010849830**
- first implementation run **37010722781** failed only on a Pandas output-field naming bug before producing metrics; code was fixed and rerun.

Design:
- identity: `GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`
- fixed CORE3 features
- fixed Logistic L2 for every target
- DEV only: 2022-2024
- chronological expanding 5-origin blocks
- no 2025/2026 outcomes used.

Ordinary direction results:

| Target | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| H1 | 755 | 50.73% | 50.45% | 0.2499 | 0.6930 | 56.46% | 44.44% |
| H3 | 755 | 54.17% | **53.67%** | **0.2469** | **0.6869** | 64.56% | **42.78%** |
| H5 | 755 | **54.97%** | 53.43% | 0.2478 | 0.6888 | **79.25%** | 27.61% |

Annual direction accuracy:
- H1: 2022 54.80%, 2023 49.00%, 2024 48.43%
- H3: 2022 52.40%, 2023 51.00%, 2024 59.06%
- H5: 2022 56.00%, 2023 52.19%, 2024 56.69%.

Interpretation:
- H1 is effectively near chance and loses signal after 2022.
- H5 has the highest raw accuracy, but that number is driven by a strong UP bias; DOWN recall collapses to 27.61% overall and 22.86% in 2024.
- H3 has the strongest probability quality and the best overall balance between raw direction accuracy and class balance. This reinforces H3 as the primary short-horizon direction target.
- This target-screen implementation is a research comparison and does **not** supersede the already-frozen authoritative H3 Stage-1 comparator metrics (`Brier 0.2466373999`, log loss `0.6864471944`).

Volatility-normalized first-daily-close-hit targets did not improve the problem:

| Target | Accuracy | Balanced acc | NO_MOVE share | NO_MOVE recall | Pred directional coverage |
|---|---:|---:|---:|---:|---:|
| H3 ±0.50σ | 49.54% | 34.78% | 6.23% | 0.00% | 100.00% |
| H3 ±0.75σ | 45.43% | 36.09% | 17.48% | 0.00% | 100.00% |
| H3 ±1.00σ | 37.48% | 34.72% | 27.42% | 9.66% | 91.79% |
| H5 ±0.75σ | 52.19% | 36.23% | 5.83% | 0.00% | 100.00% |

Binding interpretation:
- simply adding a `NO_MOVE` class does not create useful selectivity under the current CORE3 Logistic representation;
- the model mostly refuses to predict `NO_MOVE`, so the barrier formulation does not solve label noise;
- the next research target remains **ordinary H3 direction**, with selectivity handled by a separate reliability/confidence layer rather than by forcing a 3-class barrier target.

Evidence:
- `GOLD_SHORT_HORIZON_TARGET_RESEARCH_RESULT_2026-10-02.md`
- `GOLD_SHORT_HORIZON_TARGET_RESEARCH_METRICS_2026-10-02.csv`.


## ARAC-H3-v1 — custom adaptive regime/analog model (2026-10-02)

Authority:
- `GOLD_H3_ARAC_MODEL_AUTHORITY_2026-10-02.md`

Workflow:
- run **37014640189**

Architecture:
- GLOBAL_EN: expanding CORE3 Elastic-Net Logistic
- RECENT504_BAL_LOGIT: recent 504-observation balanced Logistic
- LOCAL_ANALOG: 75-nearest historical state probability with shrinkage
- REGIME_PRIOR: sigma20 tertile × 21d Gold trend × Silver/Platinum breadth historical prior
- expert weights adapt online from matured recent Brier performance
- selective reliability score = expert agreement × final probability distance from 0.5.

Development:
- 2019-2021
- frozen reliability threshold `0.033375`
- development selected coverage ~30.04%.

Confirmation:
- 2022-2024, already-opened wider project history; not a pristine blind lockbox.

Full-coverage confirmation:

| Model | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Expanding prior | 52.32% | 50.00% | 47.68% | 0.2497 | 0.6925 | 100.00% | 0.00% |
| CORE3 Logistic L2 | 54.97% | 54.49% | 45.03% | 0.2466 | 0.6865 | 64.81% | 44.17% |
| CORE3 Elastic-Net | 54.97% | 54.45% | 45.03% | 0.2468 | 0.6867 | 65.57% | 43.33% |
| **ARAC-H3-v1** | **55.63%** | **55.29%** | **44.37%** | **0.2465** | **0.6862** | 62.53% | **48.06%** |

Frozen selective confirmation:
- calls: **243 / 755**
- coverage: **32.19%**
- accuracy: **61.73%**
- balanced accuracy: **59.73%**
- false-call rate: **38.27%**
- UP recall: **76.47%**
- DOWN recall: **42.99%**.

Selective annual:
- 2022: coverage 25.20%, accuracy 58.73%, balanced 54.63%
- 2023: coverage 31.47%, accuracy 68.35%, balanced 68.33%
- 2024: coverage 39.76%, accuracy 58.42%, balanced 54.19%.

Full-coverage annual ARAC:
- 2022 accuracy 52.40%, balanced 52.51%
- 2023 accuracy 58.57%, balanced 58.51%
- 2024 accuracy 55.91%, balanced 55.19%.

Interpretation:
- ARAC is the first custom short-horizon architecture in this research sequence to improve simultaneously over the frozen CORE3 Logistic comparator on full-coverage accuracy, balanced accuracy, false-call rate, Brier/log loss, and DOWN recall across the 2022-2024 aggregate.
- the selective layer produces a materially higher 61.73% directional accuracy at about 32% coverage, with positive results in each of 2022, 2023 and 2024.
- this is promising research evidence, not a blind-proof result because 2022-2024 was already-opened project history.
- 2025/2026 must not be used to redesign ARAC-v1; any transport run should use the frozen specification as-is.

Evidence:
- `GOLD_H3_ARAC_V1_RESULT_2026-10-02.md`
- `GOLD_H3_ARAC_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_ARAC_V1_RELIABILITY_CANDIDATES_2026-10-02.csv`
- `GOLD_H3_ARAC_V1_WEIGHTS_2026-10-02.csv`.


## ARAC-H3-v1 — frozen 2025/2026 transport (2026-10-02)

Authority:
- `GOLD_H3_ARAC_V1_TRANSPORT_AUTHORITY_2026-10-02.md`

Workflow:
- run **37015469425**

Frozen transport:
- architecture unchanged
- reliability threshold unchanged at `0.03337519281868787`
- online adaptation allowed only from already-matured prior H3 outcomes
- last evaluated forecast issue: **2026-09-25**.

Full coverage:

| Period | Model | Accuracy | Balanced acc | False calls | Brier | DOWN recall |
|---|---|---:|---:|---:|---:|---:|
| 2025 | CORE3 Logistic EN | 52.96% | 51.92% | 47.04% | 0.2495 | 47.42% |
| 2025 | ARAC | 50.99% | 50.12% | 49.01% | 0.2505 | 46.39% |
| 2026 | CORE3 Logistic EN | 42.93% | 44.07% | 57.07% | 0.2653 | 20.00% |
| 2026 | ARAC | 45.55% | 47.16% | 54.45% | 0.2544 | 13.00% |
| 2025-2026 | CORE3 Logistic EN | 48.65% | 47.12% | 51.35% | 0.2563 | 33.50% |
| 2025-2026 | ARAC | 48.65% | 46.70% | 51.35% | 0.2521 | 29.44% |

Frozen selective ARAC:
- 2025: 74 calls, 29.25% coverage, 54.05% accuracy, 52.08% balanced
- 2026: 64 calls, 33.51% coverage, 43.75% accuracy, 50.00% balanced, **0% DOWN recall**
- combined 2025-2026: 138 calls, 31.08% coverage, 49.28% accuracy, 48.82% balanced.

2026 monthly deterioration is severe:
- May full accuracy 38.10%
- June 27.27%
- July 39.13%
- September 31.58%
- September selective calls: 6/6 wrong.

Binding interpretation:
- the promising 2022-2024 ARAC confirmation does **not transport** into 2025-2026;
- ARAC-v1 must not be promoted as a robust forecasting solution;
- 2026 reveals strong UP-side collapse / inability to capture DOWN states;
- any repair must be a separately specified `ARAC-H3-v2`, not a retrospective change to v1.

Evidence:
- `GOLD_H3_ARAC_V1_TRANSPORT_RESULT_2026-10-02.md`
- `GOLD_H3_ARAC_V1_TRANSPORT_METRICS_2026-10-02.csv`
- `GOLD_H3_ARAC_V1_TRANSPORT_2026_MONTHLY_2026-10-02.csv`
- `GOLD_H3_ARAC_V1_TRANSPORT_WEIGHTS_2026-10-02.csv`.
