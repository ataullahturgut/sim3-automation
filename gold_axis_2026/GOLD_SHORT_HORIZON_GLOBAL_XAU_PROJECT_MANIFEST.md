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

**User-authorized H3 repair override, 2026-10-02:** NOVA-H3 V1 was preregistered and executed after the ANFIS/RBFNN-family checklist was written. The earlier RBFNN item is retained as an unexecuted challenger-family note, but it is no longer the immediate mechanism-repair action for the H3 lane.

NOVA-H3 V1 shows that raw novelty detection and adaptive uncertainty are **diagnostically useful but not sufficient directional repair**:
- cross-market novelty improves class balance in 2022-2024 but does not beat ARCR on probability quality;
- 2026 still fails badly;
- adaptive conformal width expands strongly in 2026, correctly indicating higher uncertainty, but the selected return/uncertainty gate collapses to rho=0 and therefore adds no directional filtering.

The next H3 mechanism question is therefore **forecastability/error-risk**, not another generic classifier blend: can origin-safe pre-2022 state, expert disagreement, novelty and probability-distance variables predict when the frozen H3 direction call itself is likely to be wrong? Any such experiment requires a separately named authority and must select all gates using pre-2022 information only. 2025/2026 remain report-only.

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


## H3 cross-family failure anatomy + ARCR-H3-v1 (2026-10-02)

### Error anatomy

Authority:
- `GOLD_H3_CROSS_FAMILY_ERROR_ANATOMY_AUTHORITY_2026-10-02.md`

Workflow:
- run **37021645437**

Five-model panel:
- LOGIT_L2_CORE3
- LGBM_CORE3
- XGB_CORE3
- VANILLA_ANFIS
- CHHHO_ANFIS

DEV 2022-2024:
- Logistic remains the best full-sample model: 54.97% accuracy / 54.48% balanced.
- Best UP recall: Logistic 65.06%.
- Best DOWN recall: ChHHO-ANFIS 44.44%, only slightly above Logistic 43.89%.
- Majority vote: 52.32% accuracy.
- Unanimous calls: 43.44% coverage / 55.49% accuracy.
- Disagreement rows: 56.56% coverage / 49.88% accuracy.
- all-five-wrong: 146/755 rows.
- exactly-one-correct: 103/755 rows; unique rescuers: Logistic 44, Vanilla ANFIS 21, ChHHO 19, LGBM 10, XGB 9.

2026 state shift:
- sigma20 mean is **+7.88 DEV SD** over all 2026 rows.
- on 2026 majority-wrong rows sigma20 is **+9.19 DEV SD**.
- consensus itself fails under shift: unanimous 2026 accuracy 44.79%.

Binding diagnosis:
- near-term H3 weakness is not primarily a missing model-family router;
- models share substantial information-set bias and fail together;
- the main unresolved problem is weak DOWN recall plus severe distribution shift / volatility novelty;
- a pure consensus hybrid is not sufficient.

### ARCR-H3-v1

Authority:
- `GOLD_H3_ASYMMETRIC_RECALL_ROUTER_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37022215922**

Design:
- GLOBAL CORE3 Logistic L2
- RECENT252 balanced Logistic L2
- blend and asymmetric UP threshold selected only on 2019-2021
- frozen selected specification: global 0.75 / recent252 0.25 / UP threshold 0.50.

Confirmation 2022-2024:
- GLOBAL L2: 54.97% accuracy, 54.49% balanced, UP recall 64.81%, DOWN recall 44.17%, Brier 0.24664.
- **ARCR-H3-v1: 56.16% accuracy, 55.98% balanced, UP recall 59.75%, DOWN recall 52.22%, Brier 0.24626.**
- DOWN recall improves +8.06 pp while UP recall falls -5.06 pp.
- false-call rate improves 45.03% -> 43.84%.

Annual confirmation:
- 2022 ARCR 53.20%
- 2023 ARCR 58.96%
- 2024 ARCR 56.30%.

Transport diagnostics:
- 2025 ARCR accuracy 49.41%, balanced 51.96%; DOWN recall improves to 62.89% but UP recall falls to 41.03%.
- 2026 ARCR accuracy 37.17%, balanced 38.07%; no transport success.

Interpretation:
- the asymmetric recent/global mechanism is supported on 2022-2024 as a weak-side repair concept;
- it is not robust to the 2026 novelty regime;
- further classifier blending is not justified;
- next architecture should retain the asymmetric weak-side repair logic but add an explicit novelty / regime-break mechanism and, ideally, new origin-safe cross-market or realized-state information.


## 18. NOVA-H3 V1 — novelty, numerical return and adaptive conformal ablation (2026-10-02)

Authority:
- `GOLD_H3_NOVA_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37039484907**

Identity:
- `NOVA_H3_V1_RESEARCH`

Selection:
- 2019-2021 only.

Confirmation:
- 2022-2024, already-opened wider project history; not a pristine blind lockbox.

Transport/stress:
- 2025 and 2026 report-only; no tuning.

Frozen A0-A5 ladder:
- A0: CORE3 Logistic L2.
- A1: inherited ARCR 75% global / 25% recent252 balanced Logistic.
- A2: CORE-state novelty-conditioned mixture.
- A3: cross-market novelty-conditioned mixture; external variables affect novelty only.
- A4: numerical H3 Elastic-Net return head + direction/return agreement + reliability gate.
- A5: adaptive conformal H3 return interval + return/uncertainty gate.

Pre-2022 selections:
- A2 max recent weight **0.65**, shrink **0.75**.
- A3 max recent weight **0.65**, shrink **0.75**.
- A4 reliability threshold **0.021384**.
- ACI gamma **0.005**.
- A5 rho **0.00**.

### Full-coverage direction

| Period | Model | Accuracy | Balanced acc | UP recall | DOWN recall | Brier |
|---|---|---:|---:|---:|---:|---:|
| 2022-2024 | CORE3 A0 | 54.97% | 54.49% | 64.81% | 44.17% | 0.246643 |
| 2022-2024 | ARCR A1 | **56.16%** | **55.98%** | 59.75% | 52.22% | **0.246261** |
| 2022-2024 | CORE novelty A2 | 54.57% | 54.56% | 54.68% | 54.44% | 0.246345 |
| 2022-2024 | Cross-market novelty A3 | 55.63% | 55.64% | 55.44% | **55.83%** | 0.246701 |
| 2025 | A3 | 48.22% | 51.97% | 35.90% | 68.04% | 0.255517 |
| 2026 | A3 | 39.27% | 39.77% | 50.55% | 29.00% | 0.262216 |

Interpretation:
- A3 produces the most symmetric 2022-2024 UP/DOWN recall among this ladder, but it does not beat A1 ARCR on aggregate balanced accuracy or Brier.
- Novelty conditioning does not repair 2026 transport.
- Therefore NOVA V1 is **NOT_PROMOTED as a robust direction model**.

### Selective A4/A5

2022-2024:
- coverage **34.83%**
- selective accuracy **58.56%**
- selective balanced accuracy **55.09%**
- UP capture **29.37%**
- DOWN capture **10.56%**.

2025:
- coverage **25.69%**
- selective accuracy **53.85%**.

2026:
- coverage **23.56%**
- selective accuracy **33.33%**
- DOWN capture **0%**.

A5 selected rho=0.00, so the conformal return/uncertainty ratio did not add an additional selective gate beyond A4. A5 must not be represented as a directional improvement.

### Numerical H3 return head

| Period | MAE | RMSE | Sign accuracy |
|---|---:|---:|---:|
| 2019-2021 | 0.012308 | 0.017311 | 54.94% |
| 2022-2024 | 0.011874 | 0.015117 | 50.33% |
| 2025 | 0.015558 | 0.020203 | 55.73% |
| 2026 | 0.027411 | 0.050180 | 40.84% |

The numerical head also suffers a major 2026 breakdown and cannot be used as an independent rescue signal.

### Adaptive conformal diagnostic

| Period | Empirical coverage | Mean interval width |
|---|---:|---:|
| 2019-2021 | 80.11% | 0.04030 |
| 2022-2024 | 78.15% | 0.03552 |
| 2025 | 76.28% | 0.04578 |
| 2026 | 77.49% | **0.07833** |

The conformal layer behaves usefully as an uncertainty diagnostic: mean H3 interval width more than doubles relative to 2022-2024 in 2026. This confirms strong forecast uncertainty/regime stress, but uncertainty detection alone does not identify the correct direction.

Binding diagnosis:
1. NOVA V1 confirms that **novelty is not the same thing as forecastability**.
2. Cross-market state can help balance UP/DOWN recall without creating robust transport.
3. The main unresolved problem remains identifying which shifted states are directionally forecastable.
4. Do not retune NOVA V1 using 2025/2026.
5. A repair must be a separately identified model, with the next scientifically justified mechanism being a pre-2022-trained **forecastability / error-risk gate** or a separately governed new-information branch.

Evidence:
- `GOLD_H3_NOVA_V1_RESULT_2026-10-02.md`
- `GOLD_H3_NOVA_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_NOVA_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_NOVA_V1_RETURN_METRICS_2026-10-02.csv`
- `GOLD_H3_NOVA_V1_CONFORMAL_METRICS_2026-10-02.csv`
- `GOLD_H3_NOVA_V1_PREDICTIONS_2026-10-02.csv`.


## 19. FERG-H3 V1 — forecastability / error-risk gate (2026-10-02)

Authority:
- `GOLD_H3_FERG_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37040472781**

Identity:
- `FERG_H3_V1_RESEARCH`

Base direction engine:
- NOVA ledger A1 / ARCR-style 75% global CORE3 Logistic + 25% recent252 balanced Logistic.

Design:
- FERG does not predict direction directly.
- Meta-target is whether the frozen A1 H3 direction call will be wrong.
- Only already-matured prior H3 outcomes are available to each meta-model refit.
- meta features include direction confidence, global/recent disagreement, novelty, numerical-return agreement, conformal width and causal recent error-history summaries.
- candidate meta-models: L2 Logistic and shallow HistGradientBoosting.
- family and acceptance threshold selected only on 2019-2021.
- 2025/2026 are report-only.

Pre-2022 selection chose:
- meta-model: **META_HGB_SHALLOW**
- frozen P(ERROR) acceptance threshold: **0.388797**
- selection coverage: **30.04%**
- selection accepted accuracy: **57.89%** vs full A1 **54.81%**
- selection accepted-vs-rejected gap: **+4.41 pp**
- error-risk AUC: **0.515**.

### Confirmation failure

| Period | Coverage | Full A1 acc | FERG accepted acc | Rejected acc | Accepted-vs-rejected gap | Error AUC |
|---|---:|---:|---:|---:|---:|---:|
| 2022-2024 | 12.19% | 56.16% | **44.57%** | **57.77%** | **-13.20 pp** | 0.460 |
| 2022 | 8.80% | 53.20% | 40.91% | 54.39% | -13.48 pp | 0.450 |
| 2023 | 14.34% | 58.96% | 44.44% | 61.40% | -16.95 pp | 0.469 |
| 2024 | 13.39% | 56.30% | 47.06% | 57.73% | -10.67 pp | 0.453 |
| 2025 | 4.74% | 49.41% | 33.33% | 50.21% | -16.87 pp | 0.503 |
| 2026 | 1.05% | 37.17% | **0.00%** | 37.57% | -37.57 pp | 0.402 |

Error-risk probability itself reverses in confirmation:
- 2019-2021 mean P(error): correct calls 0.436 vs wrong calls 0.439 — only tiny positive separation.
- 2022-2024: correct calls 0.456 vs wrong calls 0.447 — wrong sign.
- 2026: correct calls 0.534 vs wrong calls 0.509 — wrong sign.

Binding conclusion:
1. **FERG-H3 V1 is NOT_PROMOTED.**
2. The existing CORE3/ARCR/NOVA-derived state variables do not contain a transportable pre-call error-risk signal.
3. This is stronger evidence that the short-horizon failure is not fixable by another selector/gate layered over the same information set.
4. Do not retune FERG thresholds using 2022-2026.
5. The next scientifically justified H3 branch must add **genuinely new origin-safe information**, rather than another meta-selector over the same daily features. This branch was subsequently executed as IRIS-H3 V1; see Section 20.
6. The most relevant new-information candidate is an explicitly governed intraday/realized-state branch, because the existing daily panel has now failed both direct-prediction and error-risk gating tests. Its later historical start must be handled with a separate evaluation contract; it cannot be silently treated as equivalent to the 2019-2021 selection regime.

Evidence:
- `GOLD_H3_FERG_V1_RESULT_2026-10-02.md`
- `GOLD_H3_FERG_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_FERG_V1_SELECTION_GRID_2026-10-02.csv`
- `GOLD_H3_FERG_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_FERG_V1_PREDICTIONS_2026-10-02.csv`.


## 20. IRIS-H3 V1 — intraday realized-state information supplement (2026-10-02)

Authority:
- `GOLD_H3_IRIS_V1_AUTHORITY_2026-10-02.md`

Workflow:
- successful run **37041653501**
- first implementation run **37041400069** failed before scoring on a pandas column/method naming collision; contract and model were unchanged, code was corrected and rerun.

Identity:
- `IRIS_H3_V1_RESEARCH`

Motivation:
- FERG showed that another selector over the same daily information set does not transport.
- IRIS therefore adds genuinely new XAU/USD intraday information from the 1-hour source.

### Source extension and clock

Historical registered source:
- `XAU_USD_TWELVE_1H_RESEARCH_V1`
- stored coverage 2022-01-02 .. 2024-12-31.

Same-provider successor extension was queried for overlap plus 2025-2026. No raw successor vendor values were committed.

Bridge:
- common hourly return rows **479**
- Pearson **1.000000**
- sign agreement **100.00%**
- return-difference SD **0.00000000**
- **PASS**.

Combined hourly rows: **30,978**.

Timing:
- intraday features are anchored at **16:00 America/New_York on feature_cutoff_date**;
- no bar from forecast_issue_date or later is used.

### Evaluation contract

Because 1h coverage starts in 2022, IRIS uses a separate later-history contract:
- 2022: initial training history;
- 2023: representation selection only;
- 2024: frozen confirmation;
- 2025/2026: frozen transport/stress.

Matched H3 origins:
- 2022: 229
- 2023: 219
- 2024: 240
- 2025: 248
- 2026 through Sep-25: 191.

### Frozen 2023 selection

Candidate families were fixed before scoring:
- hourly-only compact state
- A1 + PATH
- A1 + VOL
- A1 + SHAPE
- A1 + ALL.

2023 selected:
- **A1_PLUS_PATH**

PATH:
- 1h / 3h / 6h / 12h / 24h / 48h returns
- lag-2 hourly return
- local-session return.

2023 selection result:
- BASE A1 accuracy **61.64%**, balanced **61.87%**, Brier **0.2419**
- A1+PATH accuracy **71.23%**, balanced **71.83%**, Brier **0.2118**
- improvement: **+9.59 pp accuracy**, **+9.96 pp balanced accuracy**, Brier **-0.0301**.

### Frozen 2024 confirmation

| Model | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|
| matched BASE A1 | 58.33% | 57.58% | 0.2432 | 63.24% | 51.92% |
| **IRIS A1+PATH** | **70.83%** | **69.97%** | **0.2006** | **76.47%** | **63.46%** |

2024 mechanism confirmation: **PASS**.

### Frozen 2025/2026 transport

| Period | Model | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|
| 2025 | BASE A1 | 49.19% | 51.64% | 0.2528 | 40.40% | 62.89% |
| 2025 | **IRIS A1+PATH** | **63.71%** | **62.27%** | **0.2294** | **68.87%** | 55.67% |
| 2026 | BASE A1 | 37.17% | 38.07% | 0.2703 | 57.14% | 19.00% |
| 2026 | **IRIS A1+PATH** | **58.64%** | **59.12%** | **0.2556** | **69.23%** | **49.00%** |
| 2025-2026 | BASE A1 | 43.96% | 43.65% | 0.2604 | 46.69% | 40.61% |
| 2025-2026 | **IRIS A1+PATH** | **61.50%** | **60.65%** | **0.2408** | **69.01%** | **52.28%** |

This is the first model in the current Global-XAU H3 sequence to show a large frozen 2024 confirmation gain **and** remain materially above the failed daily baseline in both 2025 and 2026.

### Robustness / timing audit

Authority:
- `GOLD_H3_IRIS_V1_ROBUSTNESS_AUTHORITY_2026-10-02.md`

Workflow:
- run **37042232511**

Independent recomputation reproduced parent results exactly:
- maximum absolute accuracy difference **0.000000000000**.

Timing / placebo:
- A1+PATH at 15:00 NY remains strong:
  - 2024 accuracy **69.17%**
  - 2025 **64.92%**
  - 2026 **53.40%**.
- shifting the 16:00 path features back to the **previous available anchor** degrades sharply:
  - 2024 **60.00%**
  - 2025 **57.26%**
  - 2026 **46.60%**.
- this supports the interpretation that recent intraday path information, rather than a static historical correlate, carries the useful signal.

Intraday-only diagnostic:
- PATH_ONLY_16:
  - 2024 accuracy **65.00%**
  - 2025 **64.92%**
  - 2026 **60.73%**
  - 2025-2026 combined **63.10%** / balanced **62.09%**.
- This is diagnostic only and does **not** replace the frozen A1+PATH V1, because PATH-only was not the 2023-selected representation.

Single-factor diagnostic:
- A1 + only 12h return remains strong:
  - 2024 **70.00%**
  - 2025 **65.73%**
  - 2026 **56.54%**.
- Therefore 12h return is a major contributor, but the frozen full PATH representation still retains additional information.

Frozen parent monthly stability:
- 2023: 12/12 months >50% accuracy; median monthly **73.9%**
- 2024: 12/12; median **70.7%**
- 2025: 12/12; median **64.2%**
- 2026 Jan-Sep: 7/9; median **55.0%**.

Binding interpretation:
1. **IRIS-H3 V1 is the strongest current H3 mechanism candidate.**
2. The gain survives a frozen 2024 confirmation and frozen 2025/2026 transport.
3. The signal is concentrated in recent intraday price-path information; volatility-only information is much less robust in 2026.
4. Timing placebo evidence argues against a trivial stale-trend explanation.
5. The result is still retrospective research, not pristine prospective proof; overlapping H3 targets also mean raw row counts must not be treated as independent Bernoulli trials.
6. Do not retune V1 on 2024-2026.
7. Freeze A1+PATH as the current research champion and move to prospective/live-origin validation plus a separately governed numerical-return head if desired.

Evidence:
- `GOLD_H3_IRIS_V1_RESULT_2026-10-02.md`
- `GOLD_H3_IRIS_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_IRIS_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_IRIS_V1_SELECTION_GRID_2026-10-02.csv`
- `GOLD_H3_IRIS_V1_SOURCE_BRIDGE_2026-10-02.json`
- `GOLD_H3_IRIS_V1_ROBUSTNESS_RESULT_2026-10-02.md`
- `GOLD_H3_IRIS_V1_ROBUSTNESS_METRICS_2026-10-02.csv`
- `GOLD_H3_IRIS_V1_MONTHLY_STABILITY_2026-10-02.csv`.


## 21. IRIS-H3 RETURN V1 — numerical 3-day return head (2026-10-02)

Authority:
- `GOLD_H3_IRIS_RETURN_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37043746650**

Identity:
- `IRIS_H3_RETURN_V1_RESEARCH`

Purpose:
- add a numerical three-trading-day return estimate and causal 80% conformal interval to the frozen IRIS-H3 information set;
- this head supplements, but does not replace, the frozen IRIS direction champion.

Information set:
- frozen A1/ARCR base logit;
- frozen IRIS PATH features at 16:00 America/New_York on feature_cutoff_date.

Selection/transport contract:
- 2022 initial history and residual-bank formation;
- 2023 numerical-head selection only;
- 2024 frozen confirmation;
- 2025/2026 frozen transport/stress.

Candidate regressors:
- Ridge alpha 1
- Ridge alpha 10
- ElasticNet alpha 0.0001
- ElasticNet alpha 0.0005
- Huber.

2023 selected:
- **ELASTIC_0005**

2023:
- MAE **0.94%**
- RMSE **1.20%**
- correlation **0.459**
- sign accuracy **65.30%**
- zero-return baseline MAE **1.06%**
- zero-return baseline RMSE **1.34%**.

Frozen 2024 confirmation:
- MAE **1.08%**
- RMSE **1.40%**
- correlation **0.468**
- sign accuracy **69.17%**
- zero-return baseline MAE **1.26%**
- zero-return baseline RMSE **1.60%**
- **MECHANISM_PASS**.

### 2025 / 2026 transport

| Period | MAE | RMSE | Corr | Sign accuracy | Mean pred | Mean actual | 80% coverage | Mean interval width |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 1.37% | 1.81% | 0.371 | 65.32% | +0.20% | +0.56% | 74.6% | 3.90% |
| 2026 | 2.57% | 4.83% | 0.218 | 60.21% | +0.21% | -0.07% | 69.1% | 5.65% |
| 2025-2026 | 1.89% | 3.46% | 0.249 | 63.10% | +0.20% | +0.29% | 72.2% | 4.66% |

Interpretation:
- the numerical head transports better in **sign** than in exact magnitude;
- 2026 magnitude error and interval width expand sharply;
- therefore IRIS direction remains the stronger primary output, while the numerical head is a secondary magnitude/uncertainty estimate.

### 2026 month-by-month numerical result

| Month | Mean predicted | Mean actual | MAE | Sign accuracy | 80% coverage | Mean width |
|---|---:|---:|---:|---:|---:|---:|
| Jan | +0.47% | +1.58% | 3.68% | 66.7% | 33.3% | 4.53% |
| Feb | +0.00% | -0.87% | 4.02% | 65.0% | 60.0% | 5.06% |
| Mar | -0.16% | +0.15% | 4.58% | 81.8% | 50.0% | 5.48% |
| Apr | +0.24% | -0.21% | 1.38% | 68.2% | 95.5% | 5.67% |
| May | +0.36% | -0.26% | 1.53% | 61.9% | 71.4% | 5.46% |
| Jun | +0.02% | -1.50% | 2.89% | 45.5% | 50.0% | 5.79% |
| Jul | +0.37% | +0.06% | 1.43% | 43.5% | 95.7% | 6.17% |
| Aug | +0.44% | +1.11% | 2.27% | 57.1% | 66.7% | 6.28% |
| Sep | +0.10% | -0.70% | 1.40% | 52.6% | 100.0% | 6.42% |

Binding conclusion:
1. **IRIS-H3 direction remains the primary short-horizon output.**
2. `IRIS_H3_RETURN_V1` is accepted as a secondary numerical head.
3. In 2026, sign information is materially more reliable than exact return magnitude.
4. Conformal width expansion correctly reflects higher 2026 uncertainty, but empirical coverage is below the nominal 80% overall.
5. Do not retune interval level or regression using 2024-2026.
6. Future live output should expose direction probability, numerical return estimate, and uncertainty interval separately rather than collapsing them into one confidence score.

Evidence:
- `GOLD_H3_IRIS_RETURN_V1_RESULT_2026-10-02.md`
- `GOLD_H3_IRIS_RETURN_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_IRIS_RETURN_V1_PERIOD_METRICS_2026-10-02.csv`
- `GOLD_H3_IRIS_RETURN_V1_2026_MONTHLY_2026-10-02.csv`
- `GOLD_H3_IRIS_RETURN_V1_2026_LATEST15_2026-10-02.csv`.


## 22. SAGE-H3 V1 — session-aware decomposition (2026-10-02)

Authority:
- `GOLD_H3_SAGE_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37045476304**

Identity:
- `SAGE_H3_V1_RESEARCH`

Hypothesis:
- decompose the 16:00 NY intraday path into Asia / Europe / US-AM / US-PM price-discovery blocks.

Selection:
- Jul-Dec 2022 only.

Result:
- **FAIL_CLOSED_NO_ELIGIBLE_2022H2_SESSION_MODEL**.

The least-bad candidate `A1_PATH_SESSION` improved 2022-H2 accuracy by +0.90 pp and balanced accuracy by +0.96 pp, but Brier worsened materially (+0.0176), so it failed the preregistered gate.

Later session models can look attractive in 2025/2026, but they are not promotable because the pre-2023 authority did not support them.

Binding conclusion:
- session decomposition is diagnostically interesting and consistent with external gold-session research,
- but SAGE V1 is **NOT_PROMOTED**,
- do not use 2025/2026 to rescue its representation.

Evidence:
- `GOLD_H3_SAGE_V1_RESULT_2026-10-02.md`
- `GOLD_H3_SAGE_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_SAGE_V1_SELECTION_GRID_2026-10-02.csv`.


## 23. AIM-H3 V1 — adaptive intraday mixture (2026-10-02)

Authority:
- `GOLD_H3_AIM_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37046126528**

Identity:
- `AIM_H3_V1_RESEARCH`

Experts:
- STRUCTURAL_IRIS = A1 + PATH,
- PATH_GLOBAL = PATH only,
- PATH_RECENT126 = recent 126-row balanced PATH model.

Mechanism:
- causal adaptive weights from decayed matured OOS Brier losses.

2022-H2 selected:
- half-life **126**
- eta **10**.

However frozen confirmation failed:
- 2023 AIM accuracy **68.49%** vs Structural IRIS **71.23%**
- 2024 AIM **66.67%** vs **70.83%**.

2026:
- AIM **57.07%**, below Structural IRIS **58.64%** and PATH_GLOBAL **60.73%**.

Binding conclusion:
- continuous expert averaging dilutes the strong structural expert in stable periods,
- recent-performance weighting did not adapt sharply enough,
- AIM V1 is **NOT_PROMOTED**.

Evidence:
- `GOLD_H3_AIM_V1_RESULT_2026-10-02.md`
- `GOLD_H3_AIM_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_AIM_V1_WEIGHTS_2026-10-02.csv`.


## 24. SENTRY-H3 V1 — causal expert failover (2026-10-02)

Authority:
- `GOLD_H3_SENTRY_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37046724814**

Identity:
- `SENTRY_H3_V1_RESEARCH`

Motivation:
- Structural IRIS dominates in 2023-2024.
- PATH_GLOBAL becomes relatively stronger in 2025-2026.
- Continuous AIM blending hurts stable periods.
- SENTRY therefore keeps Structural IRIS by default and performs a hard causal failover only when recent paired directional evidence supports PATH_GLOBAL.

Frozen rule:
- latest **63 matured paired H3 forecasts**
- paired score:
  - +1 if PATH correct / Structural wrong
  - -1 if Structural correct / PATH wrong
  - 0 otherwise
- enter PATH when net rescue >= **+3**
- return to Structural when net rescue <= **0**
- minimum matured paired history **42**
- no threshold optimization on 2023-2026.

### Confirmation

2023:
- Structural IRIS accuracy **71.23%**, balanced **71.83%**, Brier **0.2118**
- SENTRY **identical**
- PATH share **0%**.

2024:
- Structural IRIS accuracy **70.83%**, balanced **69.97%**, Brier **0.2006**
- SENTRY **identical**
- PATH share **0%**.

Thus SENTRY preserves the strong stable-period champion exactly.

### Transport

| Period | Model | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|
| 2025 | Structural IRIS | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| 2025 | **SENTRY** | **64.52%** | **62.93%** | **0.2276** | **70.20%** | 55.67% |
| 2026 | Structural IRIS | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| 2026 | PATH_GLOBAL | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| 2026 | **SENTRY** | **60.21%** | **60.71%** | **0.2513** | **71.43%** | **50.00%** |
| 2025-2026 | Structural IRIS | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| 2025-2026 | **SENTRY** | **62.64%** | **61.73%** | **0.2379** | **70.66%** | **52.79%** |

2026 rescue:
- base accuracy **58.64%**
- SENTRY accuracy **60.21%**
- rescued calls **4**
- broken calls **1**
- net rescue **+3**
- PATH active **80 / 191** origins.

State switches:
- **2025-09-18:** Structural IRIS -> PATH_GLOBAL, net rescue63 +3
- **2026-04-24:** PATH_GLOBAL -> Structural IRIS, net rescue63 0.

PATH state share:
- 2022: 0%
- 2023: 0%
- 2024: 0%
- 2025: 29.4%
- 2026: 41.9%.

Interpretation:
1. **SENTRY-H3 V1 is MECHANISM_PASS.**
2. It was the first adaptive H3 mechanism pass and is now superseded by DART-H3 V1 as the current adaptive H3 research champion; see Section 25.
3. PATH_GLOBAL alone has slightly higher 2026 accuracy (**60.73%**) but cannot replace the champion because it is materially weaker in 2023-2024.
4. SENTRY improves 2026 without a 2026-fitted threshold; switching uses only already-matured paired forecast correctness.
5. This remains retrospective research. The next decisive evidence is prospective origins under the frozen SENTRY rule.
6. Do not retune window=63, entry=+3, exit=0 from 2025/2026 outcomes.

Evidence:
- `GOLD_H3_SENTRY_V1_RESULT_2026-10-02.md`
- `GOLD_H3_SENTRY_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_SENTRY_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_SENTRY_V1_SWITCHES_2026-10-02.csv`
- `GOLD_H3_SENTRY_V1_PATH_SHARE_2026-10-02.csv`
- `GOLD_H3_SENTRY_V1_2026_RESCUE_2026-10-02.csv`
- `GOLD_H3_SENTRY_V1_2026_MONTHLY_2026-10-02.csv`.


## 25. DART-H3 V1 — disagreement-aware Bayesian regime transfer (2026-10-02)

Authority:
- `GOLD_H3_DART_V1_AUTHORITY_2026-10-02.md`

Workflows:
- initial full-data run **37049267033**
- isolated frozen-ledger rerun **37049528162**
- dependence-aware inference audit **37049733780**

Identity:
- `DART_H3_V1_RESEARCH`

Motivation:
- SENTRY improved transport using a fixed 63-origin paired-rescue window.
- However, expert-agreement rows contain no directional information about which expert is superior.
- DART updates only on matured expert-disagreement events.

Experts:
- STRUCTURAL_IRIS = A1 + hourly PATH
- PATH_GLOBAL = hourly PATH only.

### Bayesian change-point mechanism

For each matured disagreement:
- X=1 if PATH_GLOBAL is correct
- X=0 if STRUCTURAL_IRIS is correct.

Because expert directions differ, exactly one expert is correct at each disagreement event.

DART uses a Beta-Bernoulli Bayesian online change-point detector:
- new-regime prior Beta(1,1)
- constant hazard **1/20 disagreement events**
- maximum tracked run length **120 disagreement events**
- minimum matured disagreements before switching **8**.

Frozen state rule:
- enter PATH when:
  - Pr(theta > 0.5) >= **0.90**
  - posterior predictive q_path >= **0.60**
- return STRUCTURAL when:
  - Pr(theta > 0.5) <= **0.10**
  - q_path <= **0.40**.

No 2023-2026 threshold tuning.

### Confirmation

2023:
- Structural IRIS accuracy **71.23%**
- DART **71.23%**
- balanced accuracy **71.83%**
- Brier **0.2118**
- PATH share **0%**.

2024:
- Structural IRIS accuracy **70.83%**
- DART **70.83%**
- balanced accuracy **69.97%**
- Brier **0.2006**
- PATH share **0%**.

Thus DART preserves the strong historical champion exactly through 2023-2024.

### State transition

Single detected transition:
- **2025-10-14:** STRUCTURAL_IRIS -> PATH_GLOBAL
- q_path **0.831**
- Pr(PATH superior) **0.944**
- matured disagreement events **91**
- posterior expected run length **7.81**.

Annual PATH-active share:
- 2022: **0%**
- 2023: **0%**
- 2024: **0%**
- 2025: **22.2%**
- 2026: **100%**.

The posterior remained in PATH throughout 2026.

### Transport

| Period | Model | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|
| 2025 | Structural IRIS | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| 2025 | SENTRY | 64.52% | 62.93% | 0.2276 | 70.20% | 55.67% |
| 2025 | DART | 64.11% | 62.60% | 0.2303 | 69.54% | 55.67% |
| 2026 | Structural IRIS | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| 2026 | SENTRY | 60.21% | 60.71% | 0.2513 | 71.43% | 50.00% |
| 2026 | PATH_GLOBAL | **60.73%** | **61.12%** | **0.2477** | 69.23% | 53.00% |
| 2026 | **DART** | **60.73%** | **61.12%** | **0.2477** | 69.23% | **53.00%** |
| 2025-2026 | Structural IRIS | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| 2025-2026 | SENTRY | **62.64%** | 61.73% | 0.2379 | **70.66%** | 52.79% |
| 2025-2026 | **DART** | **62.64%** | **61.87%** | **0.2378** | 69.42% | **54.31%** |

2026 DART rescue:
- Structural accuracy **58.64%**
- DART **60.73%**
- rescued calls **7**
- broken calls **3**
- net rescue **+4**
- PATH active **191 / 191** origins.

### Dependence-aware inference audit

Authority:
- `GOLD_H3_DART_V1_INFERENCE_AUTHORITY_2026-10-02.md`

Method:
- paired circular moving-block bootstrap
- **10,000** replicates
- block lengths **5** and **10** origins
- no retuning.

2026 DART vs Structural:
- observed accuracy improvement **+2.09 pp**
- block-5 95% interval **[-1.05, +5.76] pp**
- block-10 **[-1.06, +5.76] pp**
- bootstrap improvement share **87.0% / 84.9%**.
- Interpretation: accuracy point estimate favors DART but is not statistically decisive.

2026 Brier:
- difference **-0.0079**
- block-5 95% interval **[-0.0140, -0.0024]**
- block-10 **[-0.0138, -0.0028]**
- bootstrap improvement share **99.8% / 99.9%**.

2026 log loss:
- difference **-0.03275**
- block-5 95% interval **[-0.0588, -0.0113]**
- block-10 **[-0.0630, -0.0105]**
- bootstrap improvement share **99.94% / 100%**.

DART vs SENTRY in 2026:
- accuracy +0.52 pp, uncertainty interval crosses zero;
- Brier **-0.00363**, with both 5- and 10-origin 95% intervals entirely below zero;
- log loss **-0.00837**, likewise with both intervals entirely below zero.

2025-2026 aggregate:
- DART and SENTRY have identical accuracy **62.64%**;
- DART has slightly better balanced accuracy **61.87% vs 61.73%** and Brier **0.23784 vs 0.23792**;
- these small aggregate differences are not statistically decisive.

### Binding interpretation

1. **DART-H3 V1 is MECHANISM_PASS.**
2. DART-H3 V1 was the first disagreement-aware Bayesian regime-transfer champion and is now superseded by AURORA-H3 V1; see Section 27.
3. DART preserves Structural IRIS exactly in the strong 2023-2024 regime.
4. It detects a probabilistically strong PATH regime on 2025-10-14 using only already-matured expert disagreements.
5. DART reaches **60.73% accuracy / 61.12% balanced accuracy in 2026**, the strongest governed adaptive H3 result so far.
6. The 2026 accuracy uplift is suggestive rather than statistically conclusive under dependence-aware bootstrap.
7. The 2026 **probability-quality** improvement is much stronger: both Brier and log-loss bootstrap intervals exclude zero under block lengths 5 and 10.
8. The scientific contribution is not simply a higher hit rate; it is an **information-efficient Bayesian regime-transfer mechanism based only on expert disagreement evidence**.
9. No DART hazard or posterior threshold may be retuned from 2025/2026 results.
10. The next decisive test is prospective/live H3 origins with the DART rule frozen.

Evidence:
- `GOLD_H3_DART_V1_RESULT_2026-10-02.md`
- `GOLD_H3_DART_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_DART_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_DART_V1_SWITCHES_2026-10-02.csv`
- `GOLD_H3_DART_V1_STATE_2026-10-02.csv`
- `GOLD_H3_DART_V1_2026_RESCUE_2026-10-02.csv`
- `GOLD_H3_DART_V1_INFERENCE_RESULT_2026-10-02.md`
- `GOLD_H3_DART_V1_INFERENCE_BOOTSTRAP_2026-10-02.csv`.


## 26. VISTA-H3 V1 — volatility-informed dynamic hazard (2026-10-02)

Authority:
- `GOLD_H3_VISTA_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37050915576**

Identity:
- `VISTA_H3_V1_RESEARCH`

Purpose:
- modify only the DART BOCPD change-point hazard using origin-safe XAU 1h realized-volatility and jump-concentration state;
- do not alter expert probabilities or direction features.

Origin-safe shock state:
- 24h realized volatility percentile
- 24h jump-concentration percentile
- prior 504 anchors only
- minimum history 60
- shock = 0.70 * rv_pct + 0.30 * jump_pct.

Dynamic hazard:
- base **0.05**
- `h_t = clip(0.05 * exp(k*(shock-0.5)), 0.02, 0.125)`
- `k = ln(4)/0.8`.

Annual mean shock / hazard:
- 2023: shock 0.437 / hazard 0.0493
- 2024: 0.528 / 0.0567
- 2025: 0.576 / 0.0614
- 2026: **0.678 / 0.0710**.

State transition:
- **2025-10-14 Structural -> PATH**
- origin shock **0.915**
- dynamic hazard **0.1026**
- q_path **0.823**
- Pr(PATH superior) **0.932**.

Result:
- 2023 / 2024 exactly preserved Structural IRIS;
- 2025 and 2026 predictions are **exactly identical to fixed-hazard DART**;
- 2026 accuracy **60.73%**, balanced **61.12%**, Brier **0.2477**.

Binding interpretation:
1. VISTA is **MECHANISM_PASS but NON-INCREMENTAL**.
2. The shock-conditioned hazard changes posterior internals, but not the discrete routing decision under frozen DART thresholds.
3. Therefore the extra complexity is not justified as the champion.
4. Keep VISTA as a documented negative/neutral mechanism result; do not promote over DART/AURORA.

Evidence:
- `GOLD_H3_VISTA_V1_RESULT_2026-10-02.md`
- `GOLD_H3_VISTA_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_VISTA_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_VISTA_V1_STATE_2026-10-02.csv`.


## 27. AURORA-H3 V1 — asymmetric unified regime online routing (2026-10-02)

Authority:
- `GOLD_H3_AURORA_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37051415369**

Identity:
- `AURORA_H3_V1_RESEARCH`

### Mechanism

AURORA combines two already-frozen causal mechanisms without introducing a new fitted threshold:

**Fast entry — SENTRY**
- latest 63 matured H3 paired outcomes
- minimum matured history 42
- enter PATH when net rescue >= **+3**.

**Slow exit — DART**
- matured expert-disagreement posterior
- return to Structural only when:
  - matured disagreements >= 8
  - Pr(PATH superior) <= **0.10**
  - q_path <= **0.40**.

This is deliberate asymmetric hysteresis:
- fast adaptation when the current structural expert shows recent realized weakness;
- conservative reversal once a transferred expert regime is established.

### Confirmation

2023:
- Structural IRIS **71.23% / BA 71.83 / Brier 0.2118**
- AURORA **identical**
- PATH share 0%.

2024:
- Structural IRIS **70.83% / BA 69.97 / Brier 0.2006**
- AURORA **identical**
- PATH share 0%.

### Transition

Single transition:
- **2025-09-18: STRUCTURAL_IRIS -> PATH_GLOBAL**
- net rescue63 **+3**
- matured pair history **63**
- matured disagreement events **90**
- q_path **0.794**
- Pr(PATH superior) **0.899**.

No reversal through the end of the 2026 stress window.

PATH share:
- 2022: 0%
- 2023: 0%
- 2024: 0%
- 2025: **29.4%**
- 2026: **100%**.

### Transport

| Period | Model | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|
| 2025 | Structural IRIS | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| 2025 | SENTRY | **64.52%** | **62.93%** | **0.2276** | **70.20%** | 55.67% |
| 2025 | DART | 64.11% | 62.60% | 0.2303 | 69.54% | 55.67% |
| 2025 | **AURORA** | **64.52%** | **62.93%** | **0.2276** | **70.20%** | 55.67% |
| 2026 | Structural IRIS | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| 2026 | SENTRY | 60.21% | 60.71% | 0.2513 | 71.43% | 50.00% |
| 2026 | DART | **60.73%** | **61.12%** | **0.2477** | 69.23% | **53.00%** |
| 2026 | **AURORA** | **60.73%** | **61.12%** | **0.2477** | 69.23% | **53.00%** |
| 2025-2026 | Structural IRIS | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| 2025-2026 | SENTRY | 62.64% | 61.73% | 0.2379 | 70.66% | 52.79% |
| 2025-2026 | DART | 62.64% | 61.87% | 0.2378 | 69.42% | 54.31% |
| 2025-2026 | **AURORA** | **62.87%** | **62.07%** | **0.2363** | 69.83% | **54.31%** |

2026 rescue vs Structural:
- rescued **7**
- broken **3**
- net rescue **+4**
- PATH active **191/191**.

### Dependence-aware inference

10,000-replicate circular moving-block bootstrap, block lengths 5 and 10.

2025-2026 AURORA vs DART:
- accuracy **+0.23 pp**
- block-10 95% interval **[0.00, +0.68] pp**
- Brier **-0.00150**
- block-5 95% interval **[-0.00369, -0.00003]**
- block-10 interval touches 0 at the upper endpoint.
- log loss **-0.00359**
- block-5 interval **[-0.00874, -0.00010]**.

2025-2026 AURORA vs SENTRY:
- accuracy **+0.23 pp**, not statistically decisive;
- Brier **-0.00158**
  - block-5 interval **[-0.00337, -0.00025]**
  - block-10 **[-0.00351, -0.00021]**
- log loss **-0.00364**
  - block-5 **[-0.00823, -0.00045]**
  - block-10 **[-0.00818, -0.00042]**.

2025-2026 AURORA vs Structural:
- accuracy **+1.37 pp**
- Brier **-0.00443**
  - block-5 **[-0.00856, -0.00033]**
  - block-10 **[-0.00865, -0.00012]**
- log loss **-0.01556**
  - block-5 **[-0.02967, -0.00219]**
  - block-10 **[-0.03184, -0.00162]**.

### Binding interpretation

1. **AURORA-H3 V1 is MECHANISM_PASS.**
2. **AURORA-H3 V1 is the current adaptive H3 research champion.**
3. It preserves the strong 2023-2024 Structural IRIS regime exactly.
4. It inherits SENTRY's earlier 2025 PATH entry and DART's persistence through 2026.
5. It produces the strongest governed 2025-2026 aggregate result:
   - accuracy **62.87%**
   - balanced accuracy **62.07%**
   - Brier **0.2363**.
6. 2026 standalone remains tied with DART/PATH at **60.73% accuracy / 61.12% balanced accuracy**.
7. The main incremental evidence over SENTRY is probability quality rather than a large hit-rate jump.
8. No new threshold was fitted; AURORA is a composition of two frozen parent mechanisms.
9. Do not retune the SENTRY entry or DART exit thresholds using 2025/2026.
10. Next decisive evidence is prospective/live-origin validation under the frozen AURORA state rule.

Evidence:
- `GOLD_H3_AURORA_V1_RESULT_2026-10-02.md`
- `GOLD_H3_AURORA_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_AURORA_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_AURORA_V1_SWITCHES_2026-10-02.csv`
- `GOLD_H3_AURORA_V1_STATE_2026-10-02.csv`
- `GOLD_H3_AURORA_V1_INFERENCE_2026-10-02.csv`.


## 28. AURORA-H3 V1 — prospective freeze / live validation (2026-10-02)

Freeze authority:
- `GOLD_H3_AURORA_V1_PROSPECTIVE_FREEZE_2026-10-02.md`

Prospective identity:
- `AURORA_H3_V1_PROSPECTIVE`

Frozen champion boundary:
- champion research commit before live harness: `20a0bd35f0c74bed6890378a3f95777e4be520ac`
- freeze timestamp: **2026-10-02T19:10:36Z**
- last retrospective feature cutoff: **2026-09-24**
- last retrospective forecast issue: **2026-09-25**
- first allowed prospective feature cutoff: **2026-10-02 16:00 America/New_York anchor or later**.

### Immutable prospective rules

- Structural expert = frozen A1 + IRIS PATH Logistic L2.
- PATH expert = frozen IRIS PATH Logistic L2.
- A1 = 0.75 expanding CORE3 + 0.25 recent252 balanced CORE3.
- prospective A1 refit cadence = one refit per **5 issued origins**, then reuse for the next four issued origins.
- expert refit cadence = first eligible issued origin of each calendar month.
- AURORA entry = frozen SENTRY fast-entry rule:
  - 63 matured paired H3 outcomes
  - minimum 42
  - net rescue >= +3.
- AURORA exit = frozen DART slow-exit rule:
  - minimum 8 matured expert disagreements
  - Pr(PATH superior) <= 0.10
  - q_path <= 0.40.
- DART hazard fixed at 0.05.
- VISTA dynamic hazard is **not** active in the prospective champion.
- no backfill after the prospective issue deadline.
- forecast probability, direction, state, evidence and origin-time features are immutable after issuance.
- settlement may only add actual target end / return / correctness after H3 maturity.

### Source immutability

Frozen public R2 history:
- pinned StakTrakr commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`
- common-metal history frozen through **2026-09-29**.

Post-freeze public daily values:
- stored append-only at first observation;
- upstream revisions do not overwrite previously frozen prospective daily values.

Frozen support files:
- `GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv`
- `GOLD_H3_AURORA_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv`

Live evidence files:
- `GOLD_H3_AURORA_V1_PROSPECTIVE_LEDGER.csv`
- `GOLD_H3_AURORA_V1_PROSPECTIVE_DAILY_PRICES.csv`
- `GOLD_H3_AURORA_V1_PROSPECTIVE_MISSES.csv`
- `GOLD_H3_AURORA_V1_PROSPECTIVE_STATUS.md`
- `GOLD_H3_AURORA_V1_PROSPECTIVE_STATUS.json`.

### Initial dry-run

Workflow:
- `gold-h3-aurora-prospective-v1.yml`
- run **37053636046**
- completed **SUCCESS**.

Frozen September 2026 expert reproduction:
- rows: **19**
- max absolute Structural probability difference: **6.11e-16**
- max absolute PATH probability difference: **1.67e-16**
- source bridge:
  - 479 common hourly returns
  - Pearson ~1.000000
  - sign agreement 100%
  - return-difference SD 0.
- **PASS**.

Initial live state at dry-run:
- prospective forecast rows: **0**
- settled rows: **0**
- missed origins: **0**
- post-freeze daily price rows: **0**
- reason: the first eligible 2026-10-02 16:00 New-York anchor had not yet completed and the upstream public daily source had not advanced beyond the frozen 2026-09-29 snapshot.

### Automatic scheduler

A scheduler-only workflow was added to the repository default branch `main`:
- `.github/workflows/gold-h3-aurora-prospective-scheduler.yml`
- main commit `eb20b01c7fd1bee4731b564900c8dd42a4036563`.

Schedule:
- **01:30 UTC daily**
- **10:30 UTC daily**.

These two checks provide an evening and next-morning issuance opportunity around the New-York 16:00 anchor while remaining before the frozen 08:00 New-York next-weekday no-backfill deadline.

The scheduler checks out the research branch, runs the frozen harness, and writes state changes back only to:
- `gold-midas-headswap-v1-20260925`.

### Binding prospective interpretation

1. **AURORA-H3 V1 is now frozen.**
2. No 2025/2026 retrospective outcome may change V1.
3. New results after the freeze must be reported separately as prospective.
4. Missing an origin is preferable to reconstructing it after outcome information becomes available.
5. Prospective evidence cannot select a new V1 threshold or champion; any modification requires a new preregistered identity.
6. The current research question is no longer “can we improve the backtest?” but **“does frozen AURORA transport prospectively?”**


## 29. TWIN-H3 V1 — path-shape analogue rescue (2026-10-02)

Authority:
- `GOLD_H3_TWIN_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37055370848**
- conclusion **SUCCESS**

Identity:
- `TWIN_H3_V1_RESEARCH`

Purpose:
- attempt to correct AURORA errors with a new information representation based on normalized 24h/48h intraday path geometry and nearest historical analogues.

Representations:
- SHAPE24
- SHAPE48
- SHAPE_MULTI

Frozen rescue rule:
- k = 25 matured nearest analogues
- override AURORA DOWN only if local p(UP) >= 0.70
- override AURORA UP only if local p(UP) <= 0.30
- no rescue before 40 matured analogues.

Selection authority:
- Jul-Dec 2022 only.

Selection result:
- **no eligible representation**
- status: **FAIL_CLOSED_NO_ELIGIBLE_SHAPE_REPRESENTATION**.

Selection grid:
- SHAPE24:
  - accuracy delta **0.00 pp**
  - balanced-accuracy delta **-0.51 pp**
  - Brier delta **+0.00549**
  - 8 overrides: 4 rescued / 4 broken
- SHAPE48:
  - accuracy delta **-1.79 pp**
  - balanced-accuracy delta **-2.44 pp**
  - Brier delta **+0.01456**
  - 10 overrides: 4 rescued / 6 broken
- SHAPE_MULTI:
  - accuracy delta **0.00 pp**
  - balanced-accuracy delta **-0.51 pp**
  - Brier delta **+0.00578**
  - 8 overrides: 4 rescued / 4 broken.

Binding interpretation:
1. simple normalized path-shape nearest-neighbour analogues do not add stable information beyond AURORA/IRIS.
2. The local analogue rescues are approximately offset by broken correct calls in the selection authority.
3. Do not inspect 2025/2026 to rescue TWIN V1.
4. TWIN V1 is **NOT_PROMOTED**.
5. If revisiting shape information later, it requires a materially different representation or learning mechanism rather than tuning k / thresholds on later years.

Evidence:
- `GOLD_H3_TWIN_V1_RESULT_2026-10-02.md`
- `GOLD_H3_TWIN_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_TWIN_V1_SELECTION_GRID_2026-10-02.csv`.


## 30. PRISM-H3 V1 — phase-resolved intraday spectral residual model (2026-10-02)

Authority:
- `GOLD_H3_PRISM_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37060199766**
- conclusion **SUCCESS**

Identity:
- `PRISM_H3_V1_RESEARCH`

Purpose:
- correct a subset of AURORA errors using a fixed 48-hour stationary-wavelet latent representation;
- keep AURORA log-odds as a fixed offset and learn only a regularized residual correction.

Representation:
- last 48 hourly XAU log returns
- L2 normalization
- SWT `db2`, level 3
- 4 chronological PAA blocks for highest approximation and each detail scale
- 16 latent wavelet coefficients
- plus log realized 48h norm and jump concentration
- total 18 latent features.

Residual model:
- `logit(p_PRISM) = logit(p_AURORA) + beta' z_wavelet`
- only beta is learned;
- ridge penalties tested: lambda 1, 10, 50.

Selection authority:
- Jul-Dec 2022 only.

Selection result:
- **no eligible lambda**
- status: **FAIL_CLOSED_NO_ELIGIBLE_LAMBDA**.

2022-H2 selection grid:
- lambda 1:
  - accuracy delta **-6.06 pp**
  - balanced-accuracy delta **-7.69 pp**
  - Brier delta **+0.03075**
  - 6 changed calls: 2 rescued / 4 broken
- lambda 10:
  - accuracy delta **-3.03 pp**
  - balanced-accuracy delta **-3.85 pp**
  - Brier delta **+0.01922**
  - 3 changed calls: 1 rescued / 2 broken
- lambda 50:
  - accuracy delta **-3.03 pp**
  - balanced-accuracy delta **-3.85 pp**
  - Brier delta **+0.00771**
  - 1 changed call: 0 rescued / 1 broken.

Binding interpretation:
1. The fixed wavelet latent residual correction does not add stable directional information beyond AURORA.
2. Stronger regularization reduces the damage but does not create positive incremental value.
3. PRISM V1 is **NOT_PROMOTED**.
4. Do not tune lambda, wavelet family, level or latent dimension on 2023-2026.
5. Together with TWIN V1, this closes two direct intraday-path error-correction branches:
   - local path-shape analogues;
   - fixed wavelet latent residual correction.
6. AURORA-H3 V1 remains the frozen prospective champion.

Evidence:
- `GOLD_H3_PRISM_V1_RESULT_2026-10-02.md`
- `GOLD_H3_PRISM_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_PRISM_V1_SELECTION_GRID_2026-10-02.csv`.


## 31. RIFT-H3 V1 — learned momentum-reversal head (2026-10-02)

Authority:
- `GOLD_H3_RIFT_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37064085750**
- conclusion **SUCCESS**

Core error anatomy motivating RIFT:
- AURORA is exceptionally strong when the next H3 move continues the current 12h momentum, but weak when H3 reverses it.
- 2023 continuation / reversal accuracy: **93.10% / 28.38%**
- 2024: **92.21% / 32.56%**
- 2025: **91.14% / 17.78%**
- 2026: **94.50% / 15.85%**.

RIFT:
- predicts a separate target `REVERSAL = sign(H3) != sign(h_ret_12)`;
- fixed origin-time imbalance/deceleration/jump/path features;
- balanced Logistic L2;
- monthly expanding causal refit;
- only overrides when AURORA follows 12h momentum and `p_reversal >= 0.70`.

Results:
- 2023: AURORA **71.23%** -> RIFT **70.32%**, 2 rescues / 4 broken
- 2024: **70.83% -> 71.25%**, 4 rescues / 3 broken
- 2025: **64.52% -> 64.92%**, 8 / 7
- 2026: **60.73% -> 61.78%**, BA **61.12% -> 62.16%**, Brier **0.2477 -> 0.2434**, 3 / 1
- 2025-2026: **62.87% -> 63.55%**, net rescue +3.

Status:
- **NOT_PROMOTED_CONFIRM_FAIL**
- 2023-2024 aggregate net rescue = -1 and BA deteriorated.
- 2026 improvement is interesting mechanism evidence but may not override the confirmation failure.
- architecture itself was motivated after historical-error inspection, so all results are explicitly post-hoc retrospective mechanism validation.

## 32. TURN-H3 V1 — literature-derived semivariance-tail reversal rule (2026-10-02)

Authority:
- `GOLD_H3_TURN_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37064599625**
- conclusion **SUCCESS**

Mechanism:
- no fitted ML reversal head;
- latest 120 active hourly returns;
- positive and negative realized semivariance;
- prior 250 valid anchors;
- fixed 80th-percentile tails, inspired by published commodity momentum-reversal research;
- AURORA flipped only when the opposite-direction semivariance enters its tail and same-direction semivariance does not;
- both-tail state is recorded as risk but does not force a direction.

Results:
- 2023: **71.23% -> 72.60%**, 5 rescues / 2 broken
- 2024: **70.83% -> 65.42%**, 5 / 18
- 2025: **64.52% -> 62.90%**, 3 / 7
- 2026: **60.73% -> 59.69%**, 2 / 4
- 2023-2024 aggregate: **71.02% -> 68.85%**, net rescue -10.

Status:
- **NOT_PROMOTED_CONFIRM_FAIL**
- simple realized-semivariance tail reversal does not transport across the gold H3 regimes.
- Do not retune the 120h / 250-anchor / 80% tail parameters from these outcomes.
- The evidence indicates that the structural blind spot is reversal, but realized-price asymmetry alone is insufficient to identify the reversal reliably.

Binding implication:
- pursue genuinely forward-looking information for the reversal state, especially gold-options implied volatility / skew or other pre-origin expectation measures;
- frozen AURORA prospective ledger remains unchanged.


## 33. VEGA-H3 V1 — options-implied volatility reversal head (2026-10-02)

Authority:
- `GOLD_H3_VEGA_V1_AUTHORITY_2026-10-02.md`

Workflow:
- run **37065316324**
- conclusion **SUCCESS**

Purpose:
- test a genuinely forward-looking information channel for the structural momentum-reversal blind spot;
- use Cboe GVZ / FRED GVZCLS with a conservative D-1 lag;
- combine GVZ state and implied-vs-realized volatility gaps with the 12h trend state;
- balanced logistic reversal head; AURORA remains default;
- flip only when AURORA follows 12h momentum and p(reversal)>=0.70.

GVZ coverage:
- 2021-01-04 through 2026-09-30
- 1,444 daily observations.

Results:
- 2023: AURORA **71.23%** -> VEGA **69.86%**, 2 rescues / 5 broken
- 2024: **70.83% -> 70.42%**, 6 / 7
- 2025: **64.52% -> 64.11%**, 4 / 5
- 2026: **60.73% -> 60.21%**, 6 / 7
- 2023-2024: **71.02% -> 70.15%**, net rescue -4
- 2025-2026: **62.87% -> 62.41%**, net rescue -2.

Status:
- **NOT_PROMOTED_CONFIRM_FAIL**.
- GVZ improves probability quality slightly in some later windows but does not reliably identify reversal direction.
- This is consistent with GVZ being an expected-magnitude / implied-volatility measure rather than a directional options-asymmetry measure.

### Binding reversal-research conclusion

Across RIFT, TURN and VEGA:

1. The structural weakness is clearly **momentum reversal**, not ordinary continuation.
2. Continuation performance of AURORA is extraordinarily high (~91-95% in 2023-2026), while reversal accuracy is low.
3. Intraday realized-price asymmetry contains some reversal signal but is unstable.
4. A literature-derived semivariance tail rule does not transport reliably to gold H3.
5. Gold implied volatility (GVZ) is forward-looking but directionless and does not solve the reversal-routing problem by itself.
6. The next materially different information set must be **directional forward-looking positioning**, such as:
   - gold-options implied skew / risk reversal;
   - put/call volume or open-interest imbalance;
   - directional gold-options order-flow / dealer gamma exposure;
   - another pre-origin directional derivative-market measure.
7. Scheduled macro-event timing is useful as a risk-state diagnostic but is not sufficient as the main reversal direction engine.
8. Do not retune RIFT/TURN/VEGA from 2022-2026 outcomes.
9. Frozen AURORA remains the prospective champion until a separately frozen challenger proves itself on future origins.

Evidence:
- `GOLD_H3_VEGA_V1_RESULT_2026-10-02.md`
- `GOLD_H3_VEGA_V1_SUMMARY_2026-10-02.json`
- `GOLD_H3_VEGA_V1_METRICS_2026-10-02.csv`
- `GOLD_H3_VEGA_V1_2026_CHANGED_2026-10-02.csv`.


## 34. OPAL-H3 V1 — options-positioning asymmetry reversal layer (2026-10-03)

Authority:
- `GOLD_H3_OPAL_V1_AUTHORITY_2026-10-03.md`

Workflow:
- successful run **37070032373**
- earlier runs failed only on CFTC schema/parser compatibility; scientific contract was unchanged.

Identity:
- `OPAL_H3_V1_RESEARCH`

Information channel:
- official CFTC COMEX Gold disaggregated reports, contract code **088691**;
- futures-only plus futures-and-options-combined;
- delta-adjusted options-only cohort positioning reconstructed as:
  `combined - futures-only`;
- cohorts:
  - managed money
  - producer/merchant
  - swap dealer
  - other reportables;
- normalized by open interest;
- weekly change, rolling 52-report z-scores and cross-cohort gaps;
- conservative **7 calendar-day availability lag** from report as-of date.

Routing:
- separate reversal target:
  `sign(H3) != sign(h_ret_12)`;
- balanced Logistic L2;
- AURORA remains default;
- flip only when AURORA follows 12h momentum and `p_reversal >= 0.70`.

Results:
- 2023: AURORA **71.23%** -> OPAL **67.12%**, 9 rescues / 18 broken
- 2024: **70.83% -> 70.00%**, 9 / 11
- 2025: **64.52% -> 64.92%**, 12 / 11
- 2026: **60.73% -> 63.87%**
  - balanced accuracy **61.12% -> 64.21%**
  - Brier **0.2477 -> 0.2452**
  - 24 overrides
  - **15 rescues / 9 broken**
  - net rescue **+6**
- 2025-2026:
  - accuracy **62.87% -> 64.46%**
  - BA **62.07% -> 63.24%**
  - net rescue **+7**.

Status:
- **NOT_PROMOTED_CONFIRM_FAIL**
- 2023-2024 aggregate:
  - AURORA **71.02%**
  - OPAL **68.63%**
  - net rescue **-11**
  - Brier deteriorated **0.2059 -> 0.2181**.
- therefore the strong 2025-2026 improvement cannot justify promotion under the frozen confirmation rule.

Binding interpretation:
1. Options-positioning asymmetry is the strongest genuinely new reversal channel found so far for **2025-2026**, especially 2026.
2. The signal is strongly **regime-dependent**: harmful in 2023, near-neutral in 2024, positive in 2025 and clearly positive in 2026.
3. This points away from a universal reversal override and toward a preregistered **regime-conditioned reversal architecture**.
4. Do not retune the OPAL threshold, lag or features on 2025-2026.
5. A new regime-conditioned challenger must be a new identity and must not overwrite frozen AURORA prospective evidence.
6. Frozen AURORA remains the prospective champion.

Evidence:
- `GOLD_H3_OPAL_V1_RESULT_2026-10-03.md`
- `GOLD_H3_OPAL_V1_SUMMARY_2026-10-03.json`
- `GOLD_H3_OPAL_V1_METRICS_2026-10-03.csv`
- `GOLD_H3_OPAL_V1_2026_CHANGED_2026-10-03.csv`
- `GOLD_H3_OPAL_V1_COT_STATE_2026-10-03.csv`.


## 35. HELIOS-H3 V1 — causal regime-gated reversal router (2026-10-03)

Authority:
- `GOLD_H3_HELIOS_V1_AUTHORITY_2026-10-03.md`

Successful workflow:
- run **37071952534**
- conclusion **SUCCESS**
- earlier attempts failed only because the frozen expert ledgers had different start dates; the scientific routing rules were unchanged.
- exact common expert evaluation window begins **2022-11-01**.

Identity:
- `HELIOS_H3_V1_RESEARCH`

### Structural motivation

OPAL established that derivatives-positioning reversal information is strongly regime-dependent:
- harmful in 2023;
- near neutral in 2024;
- positive in 2025;
- strongly positive in 2026.

HELIOS therefore does not use regime variables as another direct forecast input. It uses **matured expert competence only for routing**.

Candidate reversal:
- `OPAL AND (RIFT OR VEGA OR TURN)`.

Candidate precision by year:
- 2022 common window: **1/1 = 100%**
- 2023: **1/3 = 33.3%**
- 2024: **5/7 = 71.4%**
- 2025: **5/6 = 83.3%**
- 2026: **3/4 = 75.0%**.

Causal competence gate:
- latest **8 matured candidate outcomes**
- target maturity enforced before an outcome enters the gate
- initial state INACTIVE
- enter ACTIVE at >= **5/8 wins**
- exit ACTIVE at <= **3/8 wins**
- otherwise retain state.

Single regime switch:
- **2024-07-16 -> ACTIVE**
- matured latest-8 sequence: `10101011`
- **5 wins / 3 losses**
- gate remains ACTIVE through the end of the 2026 retrospective ledger.

V1 probability:
- Beta(1,1) competence mean `q=(wins+1)/10`
- routed probability is a competence-weighted blend of AURORA and its mirrored probability.

### HELIOS V1 results

- 2023:
  - AURORA **71.23%**
  - HELIOS **71.23%**
  - gate inactive; OPAL's 2023 damage fully suppressed.
- 2024:
  - **70.83% -> 71.25%**
  - BA **69.97% -> 70.22%**
  - Brier **0.2006 -> 0.1989**
  - 2 rescues / 1 broken.
- 2025:
  - **64.52% -> 66.13%**
  - BA **62.93% -> 64.26%**
  - Brier **0.2276 -> 0.2253**
  - 5 rescues / 1 broken.
- 2026:
  - **60.73% -> 61.78%**
  - BA **61.12% -> 62.21%**
  - Brier **0.2477 -> 0.2460**
  - 3 rescues / 1 broken.
- 2023-2024:
  - **71.02% -> 71.24%**
  - BA **71.24% -> 71.40%**
  - Brier **0.2059 -> 0.2050**.
- 2025-2026:
  - **62.87% -> 64.24%**
  - BA **62.07% -> 63.31%**
  - Brier **0.2363 -> 0.2343**
  - **8 rescues / 2 broken**
  - net rescue **+6**.

2026 changed calls:
- 2026-03-11 UP -> DOWN: **RESCUED**, H3 -2.11%
- 2026-08-03 DOWN -> UP: **RESCUED**, H3 +3.09%
- 2026-08-04 DOWN -> UP: **RESCUED**, H3 +4.98%
- 2026-08-28 DOWN -> UP: **BROKEN**, H3 -4.95%.

Dependence-aware evidence vs AURORA:
- 2025-2026 accuracy delta **+1.3667 pp**
  - block5/10 bootstrap P(improve) about **95.7% / 95.9%**
  - 95% interval lower edge = 0.
- 2025-2026 Brier delta **-0.00203**
  - block5/10 95% CIs entirely below 0
  - P(improve) about **98.1% / 98.3%**.
- logloss delta **-0.00431**
  - both CIs below 0
  - P(improve) about **98.3%**.
- 2026-only hit-rate/Brier improvements are directionally positive but not statistically decisive.

Binding interpretation:
1. **Regime gating fixes the main raw-OPAL failure mode.**
2. 2023 is protected because the reversal competence gate remains closed.
3. A causal competence transition is detected in mid-2024.
4. Once active, the high-precision consensus reversal candidate is stable through 2025-2026.
5. HELIOS V1 is still post-hoc strengthening research, not pristine prospective proof.

## 36. HELIOS-H3 V2 — posterior-calibrated strengthening + robustness (2026-10-03)

Authority:
- `GOLD_H3_HELIOS_V2_AUTHORITY_2026-10-03.md`

Workflow:
- run **37072203269**
- conclusion **SUCCESS**

Identity:
- `HELIOS_H3_V2_RESEARCH`

Routing:
- **identical to HELIOS V1**.
- no change to candidate definition, window, entry, exit, hysteresis or maturity rules.

V2 calibration:
- recent competence posterior with Beta(1,1):
  `q=(wins+1)/(8+2)`.
- if active reversal changes UP -> DOWN:
  `p_UP = 1-q`.
- if active reversal changes DOWN -> UP:
  `p_UP = q`.
- outside active candidate events:
  `p_V2=p_AURORA`.

### HELIOS V2 results

Direction metrics are identical to V1:
- 2023: **71.23%**
- 2024: **71.25%**
- 2025: **66.13%**
- 2026: **61.78%**
- 2023-2024: **71.24%**
- 2025-2026: **64.24%**.

Balanced accuracy:
- 2026: **62.21%**
- 2025-2026: **63.31%**.

Brier:
- 2024: **0.1988**
- 2025: **0.2244**
- 2026: **0.2455**
- 2023-2024: **0.2050**
- 2025-2026: **0.2336**.

Comparison on 2025-2026:
- AURORA: Acc **62.87%**, BA **62.07%**, Brier **0.2363**
- raw OPAL: Acc **64.46%**, BA **63.24%**, Brier **0.2383**
- HELIOS V1 soft: Acc **64.24%**, BA **63.31%**, Brier **0.2343**
- HELIOS V1 hard: Acc **64.24%**, BA **63.31%**, Brier **0.2337**
- HELIOS V2: Acc **64.24%**, BA **63.31%**, Brier **0.2336**.

The calibration differences among HELIOS soft/hard/V2 are small and not statistically decisive. V2 is retained as the conceptually clean posterior-calibrated research version, not because a historical significance test proves it superior to V1 hard.

### Gate-sensitivity robustness

Neighboring preregistered diagnostic gates:

- W6: latest 6, enter 4, exit 2
  - switch **2024-07-16**
- W8 binding: latest 8, enter 5, exit 3
  - switch **2024-07-16**
- W10: latest 10, enter 6, exit 4
  - switch **2024-10-03**.

All three:
- remain active throughout 2025 and 2026;
- produce the same directional accuracy:
  - 2025 **66.13%**
  - 2026 **61.78%**
  - 2025-2026 **64.24%**
- produce the same 2025-2026 BA **63.31%**.

2025-2026 Brier:
- W6: **0.2331**
- W8 binding: **0.2336**
- W10: **0.2337**.

Thus the later-period directional benefit is **not a knife-edge artifact of one gate window**.

### Rejected strengthening ablation: sentinel opens full OPAL

A high-recall ablation used the consensus only to detect the regime and then allowed every raw OPAL override while the regime was active.

Result:
- 2023 remained protected;
- 2026 reproduced raw OPAL's **63.87%** accuracy;
- but 2024 fell to **69.58%** and 2025 BA deteriorated to **61.42%**.

Therefore this high-recall design is rejected:
- it recovers 2026 hit-rate by reintroducing OPAL's false-flip instability.
- HELIOS keeps the high-precision consensus filter after the regime gate opens.

### Binding strengthening conclusion

1. The most robust architecture found is:
   **AURORA base + causal competence regime gate + independent reversal-evidence consensus.**
2. The regime state should affect **routing**, not be appended as another direct forecast feature.
3. Raw OPAL contains more 2026 upside, but its regime instability is unacceptable historically.
4. HELIOS sacrifices some raw-OPAL 2026 hit rate in exchange for substantially better cross-regime stability and probability quality.
5. HELIOS V2 is the preferred **research challenger** to freeze prospectively.
6. It does **not** replace the already-frozen AURORA champion from retrospective evidence.
7. Proper next evidence is future-origin prospective HELIOS vs AURORA comparison under frozen rules.

Evidence:
- `GOLD_H3_HELIOS_V1_RESULT_2026-10-03.md`
- `GOLD_H3_HELIOS_V1_SUMMARY_2026-10-03.json`
- `GOLD_H3_HELIOS_V1_METRICS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V1_SWITCHES_2026-10-03.csv`
- `GOLD_H3_HELIOS_V1_CANDIDATE_ANATOMY_2026-10-03.csv`
- `GOLD_H3_HELIOS_V1_INFERENCE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V2_RESULT_2026-10-03.md`
- `GOLD_H3_HELIOS_V2_SUMMARY_2026-10-03.json`
- `GOLD_H3_HELIOS_V2_METRICS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V2_GATE_SENSITIVITY_2026-10-03.csv`
- `GOLD_H3_HELIOS_V2_INFERENCE_2026-10-03.csv`.

## 37. HELIOS-H3 V3-GT — game-theoretic event arbiter (2026-10-03)

Authority:
- `GOLD_H3_HELIOS_V3_GT_AUTHORITY_2026-10-03.md`

Successful workflow:
- run **37076021323**
- implementation commit **4c330c78e6a6acc86f6f906ec693e05da2a0b573**
- evidence commit **44ae2703**
- conclusion **PROMISING_POSTHOC_STRENGTHENING / NOT_PROSPECTIVE**

Identity:
- `HELIOS_H3_V3_GT_RESEARCH`

### Architecture

V3-GT keeps the frozen HELIOS macro competence gate and replaces the single hard event filter with a causal online policy market.

Binding policy game:
- `KEEP`
- `HELIOS_CONSENSUS`
- `COT_FRESH`
- `FRESH_OR_CONSENSUS`
- `OPAL_ALL`.

Binding market:
- latest **8 matured OPAL events**
- rescue utility **+1**
- broken utility **-1**
- multiplicative/Hedge weights
- flip only when macro gate is ACTIVE, OPAL override exists and weighted flip share is **> 0.50**
- probability on a GT route is the mirror of frozen AURORA probability
- no future or unmatured target information is used.

COT freshness is origin-safe:
- each available CFTC report vintage is identified from the frozen OPAL ledger;
- the first OPAL override generated by that report is marked fresh;
- repeated calls from the same report are not treated as independent new information.

### Binding results

| Period | AURORA Acc | HELIOS V2 | V3-GT | Raw OPAL | V3 GT net rescue | AURORA Brier | V3 Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | **71.23%** | 67.12% | +0 | 0.2118 | 0.2118 |
| 2024 | 70.83% | **71.25%** | 70.83% | 70.00% | +0 | 0.2006 | **0.1988** |
| 2025 | 64.52% | **66.13%** | 64.92% | 64.92% | +1 | 0.2276 | 0.2280 |
| 2026 | 60.73% | 61.78% | **65.45%** | 63.87% | **+9** | 0.2477 | **0.2370** |
| 2025-2026 | 62.87% | 64.24% | **65.15%** | 64.46% | **+10** | 0.2363 | **0.2319** |

2026 V3-GT:
- 17 routed events
- **13 rescue / 4 broken**
- net rescue **+9**
- BA **65.76%**
- accuracy gain vs AURORA **+4.712 pp**.

2025-2026:
- 30 routed events
- **20 rescue / 10 broken**
- net rescue **+10**
- accuracy **65.15%**
- BA **64.19%**.

### Dependence-aware evidence

V3-GT vs AURORA, 2026:
- accuracy delta **+4.712 pp**
  - block5 95% CI **[+1.047, +8.901] pp**, P(improve) **99.2%**
  - block10 95% CI **[+1.047, +8.901] pp**, P(improve) **99.7%**
- Brier delta **-0.01065**
  - both block bootstrap CIs entirely below zero
  - P(improve) **98.1% / 99.4%**
- logloss delta **-0.02271**
  - both block bootstrap CIs entirely below zero
  - P(improve) **97.9% / 99.4%**.

V3-GT vs HELIOS V2, 2026:
- accuracy delta **+3.665 pp**
- block5 95% CI **[+0.524, +6.806] pp**, P(improve) **98.8%**
- block10 95% CI **[+1.047, +6.806] pp**, P(improve) **99.5%**.

COT-vintage clustered net-rescue bootstrap:
- 2025-2026: **+10**, 22 unique routed vintages, 95% **[+1,+19]**, P(net>0) **97.5%**
- 2026: **+9**, 10 unique routed vintages, 95% **[+3,+15]**, P(net>0) **99.8%**.

### Robustness

2025-2026:
- W6: Acc **65.15%**, net **+10**
- W8 binding: Acc **65.15%**, net **+10**
- W10: Acc **64.69%**, net **+8**
- W12: Acc **64.92%**, net **+9**.

Conservative broken-cost diagnostics:
- W8 cost 1.25: Acc **65.60%**, rescue/broken **18/6**, net **+12**
- W8 cost 1.50: Acc **65.38%**, rescue/broken **17/6**, net **+11**.

These are diagnostics only and do not replace the binding W8 +1/-1 rule.

Policy-set ablations also remained positive on 2025-2026, with net rescue between **+8 and +9** for the tested reduced markets.

### Binding interpretation

1. Game-theoretic event arbitration materially improves the unresolved 2026 reversal-selection problem.
2. The gain is not explained only by repeated calls from one COT vintage; clustered inference remains strong.
3. The frozen HELIOS macro gate still fully protects 2023.
4. However V3-GT does **not** dominate HELIOS V2 in every historical regime:
   - 2024 directional accuracy falls from V2 **71.25%** to **70.83%**;
   - 2025 falls from V2 **66.13%** to **64.92%**.
5. Therefore V3-GT is not yet a clean replacement for V2.
6. The remaining scientific problem is now narrower: preserve HELIOS V2's high-precision consensus routing until there is causal evidence that the broader OPAL policy market has become competent, then permit controlled expansion.
7. A natural next architecture is a **regret-gated expansion layer** on top of V2, rather than another independent forecasting model.
8. AURORA remains the frozen prospective champion; neither V2 nor V3-GT may replace it from retrospective evidence.

Evidence:
- `GOLD_H3_HELIOS_V3_GT_RESULT_2026-10-03.md`
- `GOLD_H3_HELIOS_V3_GT_SUMMARY_2026-10-03.json`
- `GOLD_H3_HELIOS_V3_GT_METRICS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V3_GT_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V3_GT_EVENT_LEDGER_2026-10-03.csv`
- `GOLD_H3_HELIOS_V3_GT_POLICY_STATE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V3_GT_ROBUSTNESS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V3_GT_INFERENCE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V3_GT_VINTAGE_CLUSTER_INFERENCE_2026-10-03.csv`.

## 38. HELIOS-H3 V4-RGE — regret-gated expansion (2026-10-03)

Authority:
- `GOLD_H3_HELIOS_V4_RGE_AUTHORITY_2026-10-03.md`

Successful workflow:
- run **37076437687**
- implementation commit **1a68d028ab6172ec956961129adbd39da8afb54b**
- evidence commit **c1383c7a**
- conclusion **BEST REGIME-PROTECTED RETROSPECTIVE STRENGTHENING FOUND SO FAR**

Identity:
- `HELIOS_H3_V4_RGE_RESEARCH`

### Motivation

V2 preserved earlier regimes but under-routed the broader 2026 OPAL opportunity.
V3-GT recovered many 2026 rescues but gave back V2's 2024-2025 directional gains.

V4-RGE therefore uses:
1. HELIOS V2 as the protected base reversal router;
2. the V3-GT game-theoretic market only as an expansion selector;
3. a second causal regret gate that decides whether non-consensus OPAL is competent enough to be admitted at all.

### Binding regret gate

Expansion ledger:
- only OPAL overrides that do **not** satisfy the frozen HELIOS consensus candidate;
- outcomes enter only after H3 target maturity.

Recent window:
- latest **10 matured non-consensus OPAL events**.

Utility vs KEEP:
- rescue **+1**
- broken **-1**.

Recent regret:
- `R = rescues - broken`.

Hysteresis:
- initial INACTIVE
- enter ACTIVE at `R >= +2` (minimum 6/10 rescues)
- exit ACTIVE at `R <= -2` (maximum 4/10 rescues)
- otherwise retain state.

Even when active, an expansion event must also pass the frozen V3-GT policy market:
- weighted flip share **> 0.50**.

V2 consensus routes are always preserved.

### Observed expansion switch

Only one switch occurred:

- **2026-06-29 -> ACTIVE**
- latest 10 matured non-consensus sequence: `1000110111`
- **6 rescue / 4 broken**
- regret **+2**.

The expansion gate stayed inactive throughout 2023, 2024 and 2025.

### Binding results

| Period | AURORA | HELIOS V2 | V3-GT | V4-RGE | Raw OPAL | V4 net rescue | V4 Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | 71.23% | **71.23%** | 67.12% | +0 | 0.2118 |
| 2024 | 70.83% | **71.25%** | 70.83% | **71.25%** | 70.00% | +1 | 0.1988 |
| 2025 | 64.52% | **66.13%** | 64.92% | **66.13%** | 64.92% | +4 | 0.2244 |
| 2026 | 60.73% | 61.78% | **65.45%** | **64.40%** | 63.87% | **+7** | **0.2387** |
| 2025-2026 | 62.87% | 64.24% | 65.15% | **65.38%** | 64.46% | **+11** | **0.2306** |

Balanced accuracy:
- 2026: **64.76%**
- 2025-2026: **64.54%**.

2025-2026 routing:
- V2 base routes: **10**
- expansion routes: **11**
- total changed calls: **21**
- **16 rescue / 5 broken**
- net rescue **+11**.

2026:
- V2 base routes: **4**
- expansion routes: **11**
- total changed calls: **15**
- **11 rescue / 4 broken**
- net rescue **+7**.

### Dependence-aware evidence

V4-RGE vs AURORA, 2025-2026:
- accuracy delta **+2.5057 pp**
- block5 95% CI **[+0.6834,+4.5558] pp**, P(improve) **99.5%**
- block10 95% CI **[+0.6834,+4.5558] pp**, P(improve) **99.7%**
- Brier delta **-0.0057**, P(improve) **97.4% / 97.5%**
- logloss delta **-0.0120**, P(improve) **96.7% / 96.8%**.

V4-RGE vs HELIOS V2, 2025-2026:
- accuracy delta **+1.1390 pp**
- block5 P(improve) **95.0%**
- block10 P(improve) **96.3%**
- Brier delta **-0.0029**
- logloss delta **-0.0064**.

V4-RGE vs HELIOS V2, 2026:
- accuracy delta **+2.6178 pp**
- block5 P(improve) **95.2%**
- block10 P(improve) **96.9%**.

COT-vintage cluster bootstrap:
- 2025-2026 net rescue **+11**
  - 14 routed vintages
  - 95% **[+4,+18]**
  - P(net>0) **99.8%**
- 2026 net rescue **+7**
  - 8 routed vintages
  - 95% **[+1,+13]**
  - P(net>0) **98.7%**.

### Regret-window robustness

2025-2026:
- W8 regret +/-2: Acc **65.15%**, BA **64.28%**, Brier **0.2308**, net **+10**
- W10 binding: Acc **65.38%**, BA **64.54%**, Brier **0.2306**, net **+11**
- W12: Acc **65.38%**, BA **64.54%**, Brier **0.2306**, net **+11**.

W10 and W12 both produce the same single expansion switch on **2026-06-29**.
W8 is more reactive and later toggles, but still remains materially positive.

### Binding interpretation

1. V4-RGE solves the main weakness exposed by V3-GT: it does not trade away V2's earlier-regime gains merely to capture 2026.
2. 2023 remains fully protected.
3. 2024 and 2025 are exactly identical to HELIOS V2 in direction and probability quality because expansion never opens.
4. A separate non-consensus reversal regime is causally detected on **2026-06-29**.
5. After that transition, broader OPAL routing is admitted only when the game-theoretic event market also supports the event.
6. V4-RGE therefore gives the strongest historical compromise found so far between:
   - cross-regime protection,
   - 2026 reversal recall,
   - net rescue,
   - probability quality.
7. V3-GT remains the higher-recall 2026 diagnostic challenger (**65.45%**) but is less regime-protected historically.
8. V4-RGE is the preferred **regime-protected retrospective strengthening challenger**.
9. This remains second-order post-hoc evidence. It cannot replace the frozen AURORA prospective champion without a separate future-origin freeze.

Evidence:
- `GOLD_H3_HELIOS_V4_RGE_RESULT_2026-10-03.md`
- `GOLD_H3_HELIOS_V4_RGE_SUMMARY_2026-10-03.json`
- `GOLD_H3_HELIOS_V4_RGE_METRICS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V4_RGE_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V4_RGE_SWITCHES_2026-10-03.csv`
- `GOLD_H3_HELIOS_V4_RGE_EVENT_LEDGER_2026-10-03.csv`
- `GOLD_H3_HELIOS_V4_RGE_INFERENCE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V4_RGE_CLUSTER_INFERENCE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V4_RGE_ROBUSTNESS_2026-10-03.csv`.

## 39. HELIOS-H3 V5-DCE — dominant-expert contradiction exception (2026-10-03)

Authority:
- `GOLD_H3_HELIOS_V5_DCE_AUTHORITY_2026-10-03.md`

Successful workflow:
- run **37113852328**
- implementation commit **213839ee1ed6ebcc93e97c49dc8104bbd096d3ee**
- evidence commit **7b0cd95b8e6af4157690768bf8b67a868c8449b6**
- conclusion **BEST RETROSPECTIVE H3 STRENGTHENING FOUND SO FAR / NOT PROSPECTIVE**

Identity:
- `HELIOS_H3_V5_DCE_RESEARCH`

### Problem split

For 2026, V4 rejected 9 OPAL reversals:
- 4 were missed rescues
- 5 were correct rejects.

Two mechanisms were separated:
1. V4 broad regret expansion can open too late;
2. after expansion is active, low-GT-share rejects are mostly correct rejects.

A generic shadow high-share specialist was tested first. It preserved 2023-2025 but activated no earlier than V4 and produced no extra rescue. Rejected as redundant.

### Academic mechanism

V5 adds a narrow specialist / sleeping-expert exception on top of V4.

The exception is awake only when:
- V4 did not route;
- HELIOS macro gate is ACTIVE;
- OPAL reversal exists;
- HELIOS consensus is absent;
- V3-GT flip share > 0.50;
- AURORA's active expert is PATH_GLOBAL;
- frozen DART posterior `Pr(PATH_GLOBAL superior to STRUCTURAL_IRIS) > 0.50`.

This is interpreted as a **dominant-expert contradiction**:
the current causal state machine still favors PATH, and its posterior still says PATH is more likely superior than not, yet the independent OPAL/game-theoretic reversal layer strongly contradicts the active call.

The 0.50 posterior threshold is the natural Bayesian majority boundary and was not selected from historical performance.

Probability:
- retain V4 outside DCE;
- mirror frozen AURORA probability on a DCE route.

### Binding exceptions

Only three historical exceptions were opened:

| Issue | PATH posterior | q_path | GT share | AURORA | V5 | Actual | H3 move | Effect |
|---|---:|---:|---:|---|---|---|---:|---|
| 2025-10-15 | 94.4% | 83.1% | 78.2% | DOWN | UP | UP | +4.59% | RESCUED |
| 2026-06-05 | 77.5% | 61.5% | 88.8% | UP | DOWN | DOWN | -3.85% | RESCUED |
| 2026-06-24 | 77.5% | 61.5% | 98.4% | UP | DOWN | DOWN | -1.93% | RESCUED |

All three were rescues.

### Binding results

| Period | AURORA | V2 | V3-GT | V4-RGE | V5-DCE | Raw OPAL | V5 Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 71.23% | 71.23% | 71.23% | 71.23% | **71.23%** | 67.12% | 0.2118 |
| 2024 | 70.83% | 71.25% | 70.83% | 71.25% | **71.25%** | 70.00% | 0.1988 |
| 2025 | 64.52% | 66.13% | 64.92% | 66.13% | **66.53%** | 64.92% | 0.2243 |
| 2026 | 60.73% | 61.78% | 65.45% | 64.40% | **65.45%** | 63.87% | **0.2369** |
| 2025-2026 | 62.87% | 64.24% | 65.15% | 65.38% | **66.06%** | 64.46% | **0.2298** |

Balanced accuracy:
- 2025: **64.59%**
- 2026: **65.76%**
- 2025-2026: **65.25%**.

2025-2026 routing:
- total routed: **24**
- rescue: **19**
- broken: **5**
- net rescue: **+14**.

2026:
- routed: **17**
- rescue: **13**
- broken: **4**
- net rescue: **+9**.

V5 exactly preserves V4 for 2023 and 2024.
It improves 2025 by one additional correct exception and recovers V3's full 2026 directional advantage without giving back V4's 2025 protection.

### Dependence-aware inference

V5 vs AURORA, 2025-2026:
- accuracy delta **+3.1891 pp**
- block5 95% CI **[+1.1390,+5.2392]**, P(improve) **99.9%**
- block10 95% CI **[+1.1390,+5.4670]**, P(improve) **100.0%**
- Brier delta **-0.0065**
- logloss delta **-0.0137**.

V5 vs HELIOS V2, 2025-2026:
- accuracy delta **+1.8223 pp**
- block5 95% CI **[+0.4556,+3.4169]**, P(improve) **99.2%**
- block10 same CI, P(improve) **99.7%**.

V5 vs V4, 2025-2026:
- accuracy delta **+0.6834 pp**
- block5 P(improve) **95.6%**
- block10 P(improve) **95.5%**.

V5 vs V4, 2026:
- accuracy delta **+1.0471 pp**
- P(improve) **87.4% / 87.8%**.
The weaker V5-vs-V4 certainty is expected because the difference is only two 2026 events.

COT-vintage cluster bootstrap:
- 2025-2026 net rescue **+14**
  - 17 routed COT vintages
  - 95% **[+7,+21]**
  - P(net>0) **99.99%**
- 2026 net rescue **+9**
  - 10 routed COT vintages
  - 95% **[+3,+15]**
  - P(net>0) **99.75%**.

### Sensitivity

PATH posterior threshold:
- 0.50, 0.60, 0.70 and 0.75 all produce the exact same binding result:
  - 2025-2026 Acc **66.06%**
  - BA **65.25%**
  - Brier **0.2298**
  - 3 exceptions
  - net rescue **+14**.
- 0.40 admits one additional broken event and weakens the result.
- 0.80 removes the two 2026 exceptions and loses the 2026 gain.

GT-share threshold:
- 0.50, 0.60 and 0.70 all produce the exact same result.
- 0.80 removes the 2025 exception but retains both 2026 exceptions.

Therefore the binding result is not a knife-edge artifact around either 0.50 threshold.

### Binding interpretation

1. The V4 miss analysis did reveal a recoverable mechanism.
2. A generic broader exception is unsafe; the broad high-share specialist did not add value.
3. The useful exception appears specifically when a **currently dominant PATH regime is strongly contradicted by an independent reversal layer**.
4. V5 recovers V3's 2026 accuracy while preserving V4's 2023-2025 regime protection and additionally improves 2025.
5. V5 is the strongest retrospective H3 architecture found so far on the recorded windows.
6. However DCE was discovered through retrospective anatomy. The three observed exceptions are too few to call the mechanism confirmed.
7. V5 therefore remains a research challenger; the frozen AURORA prospective champion remains unchanged.
8. The next scientifically clean step is not more retrospective rule search. It is a separately frozen prospective V5-DCE ledger or a pre-registered forward shadow test.

Evidence:
- `GOLD_H3_HELIOS_V5_DCE_RESULT_2026-10-03.md`
- `GOLD_H3_HELIOS_V5_DCE_SUMMARY_2026-10-03.json`
- `GOLD_H3_HELIOS_V5_DCE_METRICS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V5_DCE_EXCEPTIONS_2026-10-03.csv`
- `GOLD_H3_HELIOS_V5_DCE_INFERENCE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V5_DCE_CLUSTER_INFERENCE_2026-10-03.csv`
- `GOLD_H3_HELIOS_V5_DCE_SENSITIVITY_2026-10-03.csv`.

## 40. PRICE-INTEGRITY AUDIT + CLEAN H3 CHAIN (2026-10-03)

### Status

**Binding data-integrity correction.**

The historical H3 chain contained one confirmed corrupt multi-metal daily row on **2026-02-27**. Therefore all previously recorded 2026 AURORA / OPAL / HELIOS V2 / V3-GT / V4-RGE / V5-DCE performance figures in Sections 35-39 are retained for audit history but are **PRE-CLEAN / PROVISIONAL** and must not be used as the current retrospective 2026 result.

The clean-chain results in this section supersede them for retrospective integrity evaluation.

Original frozen prospective artifacts were not overwritten.

### 40.1 Confirmed corrupt source row

Frozen source:
- `GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv`

Bad 2026-02-27 values:
- Gold **3516.02**
- Silver **62.15**
- Platinum **1585.39**
- Palladium **1201.26**

Neighboring values:
- 2026-02-26 Gold **5178.70**
- 2026-03-02 Gold **5354.59**

The source row is inherited from the pinned StakTrakr daily snapshot and carries a different source provenance (`sqld`) from surrounding seeded observations.

Independent clean-overlay values:
- Gold **5183.80**
- Silver **88.14**
- Platinum **2369.25**
- Palladium **1789.96**

The clean overlay changes only this source row; it does not overwrite the frozen original.

### 40.2 Twelve Data integrity cross-check

Workflow:
- `gold-h3-price-integrity-audit-v1.yml`

Implementation commit:
- `92517be971b1a5f050035dd52bb6a6b8012d3ef6`

Evidence commit:
- `b83a279ed89dc54d07c5e1c1364b783787a46b3a`

For XAU/USD:
- 2026-02-27 frozen = **3516.02**
- Twelve 12:00 NY = **5234.21**
- Twelve 16:00 NY = **5278.64**
- discrepancy approximately **-40%**.

Neighboring dates differ only by ordinary intraday-anchor amounts.
Conclusion: 2026-02-27 is an isolated corrupt source row, not a legitimate alternate daily timestamp convention.

Evidence:
- `GOLD_H3_PRICE_INTEGRITY_AUDIT_2026-10-03.md`
- `GOLD_H3_PRICE_INTEGRITY_AUDIT_SUMMARY_2026-10-03.json`
- `GOLD_H3_PRICE_INTEGRITY_COMPARE_2026-10-03.csv`
- `GOLD_H3_PRICE_INTEGRITY_FLAGGED_2026-10-03.csv`.

### 40.3 Direct label contamination

Correcting 2026-02-27 flips exactly two H3 labels:

- issue **2026-02-25**, H3 end 2026-02-27:
  - old target ≈ **-37.90% / DOWN**
  - clean target ≈ **+0.93% / UP**
- issue **2026-03-02**, H3 end 2026-03-04:
  - old target ≈ **+38.32% / UP**
  - clean target ≈ **-0.50% / DOWN**

The corrupt row also contaminated lagged daily-metal features and `sigma20`; therefore a label-only repair is insufficient.

### 40.4 Full clean-core rebuild

Workflow run:
- **37116264623**

Implementation/fix commit:
- `3738c1f200218aee066f298f3eeca9d3553f774d`

Evidence commit:
- `e83f47cd176ab12d51128dec6af045c99593ded2`

Recomputed without threshold changes:
- H1/H3/H5 targets
- gold/silver/platinum/palladium daily-return features
- sigma20
- NOVA A1 sequence
- STRUCTURAL and PATH experts
- SENTRY
- DART
- AURORA state machine.

Clean AURORA:

| Period | Accuracy | BA | Brier |
|---|---:|---:|---:|
| 2023 | 71.23% | 71.83% | 0.2118 |
| 2024 | 70.83% | 69.97% | 0.2006 |
| 2025 | 64.52% | 62.93% | 0.2276 |
| **2026** | **58.64%** | **59.02%** | **0.2532** |
| 2025-2026 | 61.96% | 61.15% | 0.2388 |

The AURORA state switch remains stable:
- **2025-09-18 STRUCTURAL_IRIS -> PATH_GLOBAL**.

However the full clean refit changes AURORA direction on:
- **2026-09-15**
- **2026-09-22**.

Evidence:
- `GOLD_H3_CLEAN_CORE_RESULT_2026-10-03.md`
- `GOLD_H3_CLEAN_CORE_METRICS_2026-10-03.csv`
- `GOLD_H3_CLEAN_CORE_SUMMARY_2026-10-03.json`
- `GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv`.

### 40.5 Full clean reversal-chain rebuild

Workflow run:
- **37116588663**

Implementation commit:
- `170255bb96e577500521cc9ec4d7ada3080d2082`

Evidence commit:
- `b5c43eede3e1f85cfdfd3b1d4282e963503ff0b0`

All fixed rules were rerun on clean AURORA:
- RIFT
- TURN
- VEGA
- OPAL
- HELIOS V1
- HELIOS V2
- V3-GT
- V4-RGE
- V5-DCE.

No threshold was retuned.

#### Clean model metrics

| Model | 2025 Acc | 2026 Acc | 2026 BA | 2026 Brier | 2025-26 Acc |
|---|---:|---:|---:|---:|---:|
| AURORA | 64.52% | **58.64%** | 59.02% | 0.2532 | 61.96% |
| Raw OPAL | 64.92% | **63.35%** | 63.71% | 0.2467 | 64.24% |
| HELIOS V2 | 66.13% | **60.73%** | 61.16% | 0.2477 | 63.78% |
| V3-GT | 64.92% | **63.35%** | 63.76% | 0.2455 | 64.24% |
| V4-RGE | 66.13% | **62.30%** | 62.71% | 0.2447 | 64.46% |
| **V5-DCE** | **66.53%** | **63.35%** | **63.76%** | **0.2425** | **65.15%** |

Clean V5 2026:
- 191 origins
- **19 routed**
- **14 rescue**
- **5 broken**
- net rescue **+9**
- accuracy improvement over clean AURORA **+4.712 pp**.

Clean 2025:
- 7 routed
- 6 rescue
- 1 broken
- net **+5**.

Clean 2025-2026:
- V5 accuracy **65.15%**
- BA **64.24%**
- Brier **0.2322**.

#### Clean reversal experts, 2026

| Expert | Accuracy | Overrides | Rescue | Broken |
|---|---:|---:|---:|---:|
| RIFT | 59.16% | 3 | 2 | 1 |
| TURN | 57.59% | 6 | 2 | 4 |
| VEGA | 59.16% | 13 | 7 | 6 |
| **OPAL** | **63.35%** | **25** | **17** | **8** |

The core 2026 reversal signal remains real after data cleaning: OPAL improves clean AURORA by **+4.71 pp**.

### 40.6 Gate timing changes after cleaning

HELIOS macro consensus gate remains stable:
- **2024-07-16 -> ACTIVE**
- W8 sequence `10101011`, 5 wins / 3 losses.

V4 broad non-consensus regret gate changes materially:
- **2026-06-10 -> ACTIVE**
  - recent 10 sequence `1000110111`
  - 6 rescue / 4 broken
  - regret +2
- **2026-09-04 -> INACTIVE**
  - recent 10 sequence `0110011000`
  - 4 rescue / 6 broken
  - regret -2.

This supersedes the pre-clean V4 timing of 2026-06-29 activation with no later exit.

### 40.7 Clean V5-DCE exceptions

Clean DCE opens five historical exceptions in 2025-2026:
- 2025-10-15: RESCUED
- 2026-05-11: RESCUED
- 2026-06-05: RESCUED
- 2026-09-07: **BROKEN**
- 2026-09-17: RESCUED.

Therefore the pre-clean statement that all DCE exceptions were successful is superseded.

### 40.8 Clean dependence-aware inference

Workflow:
- **37116788243**

Implementation commit:
- `59daa374b4033cfb47ee346334d4bfaee0759447`

Evidence commit:
- `6f71efc62f74a9ebf13451e68bba7401b0fa3930`

V5 vs clean AURORA:

2025-2026 accuracy:
- delta **+3.1891 pp**
- block5 95% **[+1.1390,+5.4670]**, P(improve) **99.8%**
- block10 95% **[+1.1390,+5.6948]**, P(improve) **99.9%**.

2026 accuracy:
- delta **+4.7120 pp**
- block5 95% **[+0.5236,+8.9005]**, P(improve) **98.6%**
- block10 95% **[+0.5236,+9.4241]**, P(improve) **98.6%**.

COT-vintage clustered V5 net rescue:
- 2025-2026: **+14**, 19 clusters, 95% **[+6,+21]**, P(net>0) **99.95%**
- 2026: **+9**, 12 clusters, 95% **[+2,+16]**, P(net>0) **99.15%**.

V5 vs V2:
- 2025-2026 accuracy +**1.3667 pp**, P(improve) **95.5% / 96.0%**
- 2026 +**2.6178 pp**, but CI crosses zero; P(improve) **92.7% / 93.6%**.

V5 vs V4:
- 2026 +**1.0471 pp**
- evidence is weaker (P improve about **78-80%**).

### 40.9 Clean sensitivity and governance

Binding V5 remains:
- PATH posterior > **0.50**
- GT share > **0.50**.

PATH posterior sensitivity:
- 0.50 through 0.75 gives identical clean result:
  - 2025-2026 Acc **65.15%**
  - net rescue **+14**.

GT-share diagnostic:
- 0.60 and 0.70 would retrospectively produce:
  - 2026 Acc **63.87%**
  - 2025-2026 Acc **65.38%**
  - net rescue **+15**.

**Do not promote this diagnostic threshold change.**
It became attractive only after inspecting the clean historical outcomes; changing V5 to 0.60 now would be post-hoc retuning.

If studied further, GT >0.60 must be a separately named, preregistered future challenger.

### 40.10 Binding interpretation

1. The 2026-02-27 source row was genuinely corrupt and materially biased the H3 evaluation/training chain.
2. The earlier V5 2026 **65.45%** result is superseded.
3. The valid clean retrospective V5 result is **63.35% accuracy / 63.76% BA / 0.2425 Brier**.
4. The central scientific conclusion nevertheless survives: the reversal architecture adds material value in 2026.
5. Clean AURORA falls to **58.64%**, while clean V5 reaches **63.35%**, a +4.71 pp improvement.
6. OPAL alone also reaches **63.35%**, confirming that the 2026 reversal regime was not an artifact of the corrupt row.
7. V5 remains preferable as the cross-regime protected retrospective architecture because it preserves:
   - 2023 **71.23%**
   - 2024 **71.25%**
   - 2025 **66.53%**
   while matching V3/raw OPAL directional accuracy in clean 2026 and giving better probability quality.
8. V5 remains post-hoc research; AURORA prospective governance is unchanged.
9. Future work must use the clean overlay / integrity guard before any further H3 model comparison.

Evidence:
- `GOLD_H3_CLEAN_REVERSAL_CHAIN_RESULT_2026-10-03.md`
- `GOLD_H3_CLEAN_REVERSAL_CHAIN_SUMMARY_2026-10-03.json`
- `GOLD_H3_CLEAN_CHAIN_METRICS_2026-10-03.csv`
- `GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv`
- `GOLD_H3_CLEAN_V5_INFERENCE_RESULT_2026-10-03.md`
- `GOLD_H3_CLEAN_V5_INFERENCE_2026-10-03.csv`
- `GOLD_H3_CLEAN_V5_CLUSTER_INFERENCE_2026-10-03.csv`
- `GOLD_H3_CLEAN_V5_SENSITIVITY_2026-10-03.csv`.

## 41. SECOND-PASS DATABASE + UPSTREAM DATA-INTEGRITY AUDIT (2026-10-03)

### Status

**Completed, read-only. No database rows were changed.**

Purpose: test whether the 2026-02-27 corruption was an isolated bad source row or evidence of broader H3 database contamination.

### 41.1 Neon database-wide screening

Workflow run:
- **37117457359**

Implementation commit:
- `567810f0b5eb5566ed3b891ac9989975cfe3d019`

Evidence commit:
- `ea4dade6c0c433850cf0711a8f8cb806c44d772a`

Database inventory:
- 32 user tables
- 63 observation series
- 14 series contain duplicate timestamps
- 1,910 duplicate timestamp groups
- 374 duplicate groups contain different stored values.

These counts are **database-wide** and do not imply that every duplicate is corrupt; several series are revision/PIT-style sources.

Binding historical H3 hourly XAU source:
- `XAU_USD_TWELVE_1H_RESEARCH_V1`
- 17,644 deduplicated rows
- 2022-01-02 through 2024-12-31
- **0 timestamps with stored revisions**
- **0 adjacent 1-hour moves >= 2.5%**
- 68 robust |z|>=8 return observations, but none breached the absolute 2.5% one-hour screening threshold
- 158 gaps >4h, dominated by expected market/weekend/holiday spacing
- max adjacent hourly log return ≈ **2.411%**.

Conclusion: no 2026-02-27-style corruption was found in the binding historical hourly XAU series.

### 41.2 Neon daily-source cross-check

Evidence commit:
- `543f547c1c12f761504cb5c5153dee01a2e897d6`

StakTrakr XAU in Neon vs independent NY17 hourly-derived XAU:
- overlap **1,089 dates**
- median level ratio ≈ **0.99983**
- severe flags (>=5% deviation from normal ratio OR robust |z|>=8): **0**.

The multi-metal robust screen flagged:
- 2026-01-30
- 2026-02-02
- 2020-03-16
- 2013-04-15
- 2011-09-26.

These are synchronized multi-metal moves and are screening candidates, not confirmed errors.

`XAU_DAILY_XAUS` contains many stored revisions/conflicting historical values, but this series is **not the binding daily price source for the current frozen H3 chain**. The current H3 daily core uses the pinned StakTrakr four-metal snapshot; the hourly structural/path layer uses Twelve Data XAU.

### 41.3 Frozen upstream StakTrakr audit

Workflow run:
- **37118219172**

Implementation commit:
- `5edead472042efad6a234279e2a756c38fe0603a`

Evidence commit:
- `d9508a18757b559c9dece85aeb3a2cb19389e3ff`

The exact pinned source used to build the AURORA frozen price snapshot:
- StakTrakr ref `54fdf1c8d39b7b6c7b874d0f30f784296e886044`.

Direct comparison of this upstream source to independent NY17-derived XAU:
- overlap **1,072 dates**
- >=3% deviation: **4 dates**
- >=5% deviation: **1 date**
- robust |z|>=8 deviation: **1 date**.

Flags:

| Date | Stak | NY17 | Source | Deviation |
|---|---:|---:|---|---:|
| **2026-02-27** | **3516.02** | **5278.64** | **sqld** | **33.38%** |
| 2026-01-30 | 5063.45 | 4866.26 | seed/LBMA | 4.07% |
| 2025-10-21 | 4275.10 | 4130.33 | seed/LBMA | 3.53% |
| 2025-10-16 | 4225.55 | 4362.29 | seed/LBMA | 3.12% |

Only **2026-02-27** crosses both the >=5% level deviation screen and the robust |z|>=8 screen.

The raw pinned StakTrakr JSON itself contains:
- 2026-02-27 Gold 3516.02, source=`sqld`
- Palladium 1201.26, source=`sqld`
- Platinum 1585.39, source=`sqld`
- Silver 62.15, source=`sqld`.

Therefore the corruption originated **upstream in the pinned StakTrakr/SQ﻿LD row**, not in the AURORA snapshot writer and not in the Neon historical hourly XAU series.

The huge 2026-03-02 multi-metal rebound flag in the raw frozen panel is mechanically induced by the bad 2026-02-27 weekday observation; weekend observations are intentionally omitted by the frozen daily parser.

### 41.4 Binding conclusion

1. **One confirmed severe H3 daily source corruption exists: 2026-02-27.**
2. No second comparable corruption was found in the binding frozen StakTrakr XAU history over the independent-source overlap.
3. No comparable corruption was found in the binding historical hourly Twelve XAU series.
4. The clean-chain correction in Section 40 remains the valid retrospective dataset.
5. The three additional 3-4% Stak-vs-NY17 discrepancies are not classified as data errors because they remain below the severe threshold and can arise from source/anchor differences; they should not be corrected without independent confirmation.
6. Database-wide duplicate/revision rows exist and require source-specific handling, but they do not presently invalidate the clean H3 result.
7. Future H3 ingestion should fail closed on isolated multi-metal daily discontinuities and require independent-source confirmation before such a row is admitted to the model panel.

Evidence:
- `GOLD_H3_NEON_INTEGRITY_AUDIT_2026-10-03.md`
- `GOLD_H3_NEON_INTEGRITY_SUMMARY_2026-10-03.json`
- `GOLD_H3_NEON_CROSS_SOURCE_AUDIT_2026-10-03.md`
- `GOLD_H3_NEON_CROSS_SOURCE_SUMMARY_2026-10-03.json`
- `GOLD_H3_STAK_UPSTREAM_AUDIT_2026-10-03.md`
- `GOLD_H3_STAK_UPSTREAM_AUDIT_SUMMARY_2026-10-03.json`
- `GOLD_H3_STAK_UPSTREAM_FLAGS_2026-10-03.csv`.

## 41. DATABASE + SOURCE-VINTAGE INTEGRITY RE-AUDIT (2026-10-03)

### 41.1 Status

**COMPLETE / NO ADDITIONAL CONFIRMED H3 DATA CORRUPTION**

A second, broader integrity audit was run after the confirmed 2026-02-27 frozen daily-price corruption.

The audit was read-only against Neon and covered:
- database schema / series inventory,
- duplicate timestamps and revisions,
- binding historical hourly XAU,
- frozen daily metals vs Neon registered historical metals,
- independent XAU source-clock comparison,
- upstream StakTrakr source-vintage changes,
- same-semantic full-UTC-day-average comparison using Twelve Data hourly XAU.

No additional daily observation met the evidentiary standard for correction.

Therefore the clean-chain result from Section 40 remains binding:
- 2026 clean AURORA: **58.64%**
- 2026 clean V5-DCE: **63.35%**
- net V5 rescue vs AURORA: **+9**
- accuracy delta: **+4.71 pp**.

### 41.2 Neon database structural audit

Read-only workflow:
- run **37117457359**
- implementation commit `567810f0b5eb5566ed3b891ac9989975cfe3d019`
- evidence commit `ea4dade6c0c433850cf0711a8f8cb806c44d772a`.

Database inventory:
- user tables: **32**
- observation series: **63**
- series with duplicate timestamps: **14**
- duplicate timestamp groups inspected: **1,910**
- groups with conflicting stored values: **374**.

These counts are not themselves errors because several registered series are revision/vintage feeds.

Binding historical H3 hourly source:
- series `XAU_USD_TWELVE_1H_RESEARCH_V1`
- **17,644** deduplicated rows
- range 2022-01-02 23:00 UTC through 2024-12-31 21:00 UTC
- duplicate/revision timestamps: **0**
- adjacent one-hour absolute log returns >=2.5%: **0**
- suspicious large one-hour spike + immediate reversal patterns: **0**
- maximum adjacent one-hour absolute log return: approximately **2.41%**.

Conclusion:
**no obvious bad-tick corruption was found in the binding historical hourly XAU database source.**

### 41.3 Revision-prone database series

`XAU_DAILY_XAUS` contains:
- **125** revised timestamps
- all 125 have conflicting values
- median absolute first-to-last revision: **0.453%**
- P95: **1.389%**
- maximum first-to-last revision: **1.763%**
- maximum within-timestamp range: **2.463%**.

This series is registered as:
- operational/display cross-check,
- `CANDIDATE_NOT_BENCHMARK`,
- not the current H3 target/model authority.

Therefore these revisions do **not** alter the clean H3 retrospective score.

`VIX_CBOE` and `GVZ_CBOE` had repeated retrieval rows but **no conflicting values** in this audit.

### 41.4 Why frozen-vs-Neon Stak values differ

The registered Neon Stak history and AURORA frozen daily file use different upstream StakTrakr vintages:

Neon historical series:
- upstream commit `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`
- date **2026-08-19**.

AURORA frozen daily file:
- upstream commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`
- date **2026-09-30**
- release explicitly includes **STRK-403 — Spot history accuracy**.

Upstream STRK-403 documentation states that the old current-year mechanism:
- appended observations before a UTC day was complete,
- did not revisit those partial-day observations,
- froze the public year file at 2026-02-26 after the prior writer retired,
- left a late-February / early-March gap.

The new rule rebuilds current-year history as:
- one row per metal / UTC day,
- SQL `AVG(spot)`,
- complete UTC days only,
- and fills the missing gap.

Therefore the many Apr-Jul differences between Neon and the frozen file are largely:
**older partial-day vintage vs newer full-day-average vintage**, not evidence that Neon is correct and frozen is corrupt.

The 2026-02-27 row is exceptional because the new gap-fill value itself was independently proven wrong.

### 41.5 Frozen-vs-Neon comparison

Deep read-only audit:
- implementation commit `ed2a3ccbfe684b836171d9ac61beccaed92d3da0`
- evidence commit `bb8a216ef516e8d9d423e4e87d7f8f09ddd242db`.

Through Neon four-metal common end 2026-07-31:
- same-date differing metal cells: **135**
- frozen-only dates: **6**
- Neon-only dates: mainly weekend rows excluded by the H3 frozen parser.

Frozen-only dates:
- 2026-02-27
- 2026-03-02
- 2026-03-03
- 2026-03-04
- 2026-03-05
- 2026-03-06.

These are exactly within the STRK-403 historical gap-fill region.

Among same-date old-vintage/new-vintage differences:
- Gold max difference: about **1.81%**
- Silver max: about **6.24%**
- Platinum max: about **3.21%**
- Palladium max: about **2.31%**.

Do not replace the newer values with the older Neon values mechanically; the upstream semantics changed from partial-day snapshots to completed UTC-day averages.

### 41.6 Source-clock comparison is not an error test

Clean frozen Stak daily-average XAU was also compared with:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Result:
- H3 direction disagreement around **20%**.

This does **not** establish corruption because the two target identities have different clocks / semantics:
- Stak = daily average,
- NY17 research = selected New York hourly endpoint.

The project had already frozen the rule:
**explicit target identity; do not stitch clocks.**

The earlier source-bridge test also failed target-equivalence:
- Stak vs canonical NY17 return Pearson ≈ **0.9375**
- sign agreement only ≈ **65%**
- return-difference SD ≈ **1.049%**.

Thus historical Stak development and NY17 live reference must remain separate target identities.

### 41.7 Binding same-semantic audit

To distinguish true data problems from source-clock differences, a final same-semantic test was run.

Workflow:
- run **37118309408**
- implementation commit `e4e73aa3165b1c2cb2f2ecea7da0e7d126950831`
- evidence commit `f2dbd6f25dacbb4608f80510abe4778bce2ead6a`.

Comparator:
- Twelve Data XAU/USD 1-hour observations in UTC,
- arithmetic mean of hourly closes for each UTC calendar day,
- compared with StakTrakr STRK-403 full-UTC-day-average history.

2026 Jan-Sep:
- Twelve hourly observations: **6,527**
- common weekday daily levels: **193**
- median Stak / Twelve daily-mean ratio: **1.000118**
- deviation >=1%: **1**
- >=2%: **0**
- >=3%: **0**
- >=5%: **0**
- maximum deviation: **1.05%** on 2026-02-18.

The 2026-02-18 Stak value is still inside the Twelve intraday hourly range and does not meet an error threshold.

The only mechanically flagged outside-hourly-close-range row was:
- 2026-04-03
- Stak **4676.71**
- Twelve hourly-close mean **4676.45**
- hourly-close max **4676.63**
- difference from mean approximately **0.01%**.

This is economically negligible and is not evidence of corruption; an hourly close range is not the same thing as the complete intrahour trade range.

### 41.8 Revalidation of the February/March gap-fill

Same-semantic cross-check:

2026-02-27:
- original frozen Gold: **3516.02**
- clean patched Gold: **5183.80**
- Twelve hourly daily mean: **5214.11**
- clean deviation from same-semantic comparator: approximately **0.6%**.

Subsequent STRK-403 gap-fill days are highly consistent:

- 2026-03-02: Stak 5354.59 vs Twelve mean 5353.01
- 2026-03-03: 5218.71 vs 5211.12
- 2026-03-06: 5125.05 vs 5126.13.

Thus:
**2026-02-27 is the only confirmed corrupt row in the gap-fill block.**

### 41.9 H3 target-direction same-semantic sensitivity

Using the same retained H3 date clock:
- comparable origins: **190**
- direction disagreements: **8 / 190 = 4.21%**
- disagreements where both absolute H3 moves are >=0.5%: **2**
- disagreements where both are >=1.0%: **0**.

The eight disagreements are concentrated around small/medium movements and ordinary cross-provider daily-average differences.

The two largest opposing cases are:
- 2026-02-04 -> 2026-02-09:
  - Stak H3 **-1.18%**
  - Twelve hourly-mean H3 **+0.52%**
- 2026-02-13 -> 2026-02-18:
  - Stak H3 **+0.98%**
  - Twelve hourly-mean H3 **-0.87%**.

Neither has a single-day level anomaly >~1.1%, and no daily level lies outside a plausible provider range. They remain **source-definition/provider dispersion**, not confirmed erroneous labels.

### 41.10 Binding conclusion

1. No additional confirmed corrupt H3 observation was found.
2. Neon binding historical hourly XAU is structurally clean.
3. 2026-02-27 remains the only proven corrupt daily row requiring correction.
4. Apr-Jul frozen-vs-Neon differences are mainly explained by StakTrakr's STRK-403 full-day-average correction versus the older partial-day vintage.
5. NY17-vs-daily-average label disagreement is a target-clock issue, not a database corruption issue.
6. Revision-prone `XAU_DAILY_XAUS` must not be silently substituted into H3.
7. The Section 40 clean V5 result **63.35%** remains the valid retrospective binding result.

### 41.11 Mandatory integrity gate for future H3 work

Before any future H3 retrospective or prospective score is accepted:

- pin source identity and upstream commit/vintage;
- preserve first-seen timestamp for prospective observations;
- reject silent replacement by a different daily clock;
- never mix daily-average and NY17 target identities;
- detect duplicate/conflicting revisions before feature construction;
- for historical gap-fill or source rewrite, run a same-semantic independent-source comparison;
- quarantine a daily row for manual verification when a same-semantic cross-provider level discrepancy is extreme;
- do not auto-correct statistical outliers: a true market crash must remain in the data;
- after any confirmed correction, rebuild targets, lagged features, volatility state and downstream causal routers from the affected origin onward.

Evidence:
- `GOLD_H3_NEON_INTEGRITY_AUDIT_2026-10-03.md`
- `GOLD_H3_NEON_CROSS_SOURCE_AUDIT_2026-10-03.md`
- `GOLD_H3_DEEP_DATA_INTEGRITY_AUDIT_2026-10-03.md`
- `GOLD_H3_FROZEN_INDEPENDENT_XAU_AUDIT_2026-10-03.md`
- `GOLD_H3_DAILY_AVERAGE_SEMANTIC_AUDIT_2026-10-03.md`
- `GOLD_H3_DAILY_AVERAGE_SEMANTIC_SUMMARY_2026-10-03.json`
- `GOLD_H3_DB_REVISION_SUMMARY_2026-10-03.csv`
- `GOLD_H3_FROZEN_VS_NEON_MISMATCHES_2026-10-03.csv`.

## 42. GOLD H3 DATA INTEGRITY GATE V1 — fail-closed prospective ingestion (2026-10-03)

Authority:
- `GOLD_H3_DATA_INTEGRITY_GATE_V1_AUTHORITY_2026-10-03.md`

Implementation:
- gate commit `9a3fbfa65fa39b8b52d25d9e43ac0c109cafda4f`
- prospective integration commit `2a7f6e2becbc47afa99eb3d7d5cf180bfba125db`
- integrity-ledger workflow commit `a47545b08d9e964844189829ce9f3f17a8bd8527`

Historical replay:
- workflow run **37118595672**
- evidence commit **931dd19de6a094a96fcfb7e6a5bb42e987bf9866**
- evaluated **446** retained daily rows
- admitted **445**
- quarantined **1**
- only quarantine: **2026-02-27**.

Stress-date replay:

| Date | Decision | Gold move | Independent XAU | Meaning |
|---|---|---:|---:|---|
| 2026-01-30 | PASS_NORMAL | -8.30% | 4866.26 | real severe market move not falsely removed |
| 2026-02-02 | PASS_NORMAL | -7.76% | 4660.07 | real severe market move not falsely removed |
| 2026-02-27 | **QUARANTINE_XAU_SOURCE_DIVERGENCE** | **-38.72%** | **5278.64** | confirmed bad upstream row caught |
| 2026-03-02 | PASS_NORMAL | +3.34% from previous accepted row | 5322.13 | artificial rebound disappears after quarantine |

### Frozen integrity policy

A row requires confirmation if:
- at least 2 of Gold/Silver/Platinum/Palladium move by >=25% absolute log-return from the previous **accepted** retained row; or
- any one metal moves by >=35%; or
- optional robust discontinuity |z|>=12.

For a triggered row:
- independent XAU unavailable -> **QUARANTINE**
- independent XAU level divergence >=5% -> **QUARANTINE**
- divergence <=3% -> **PASS_SEVERE_XAU_CONFIRMED**
- 3%-5% -> **QUARANTINE_AMBIGUOUS**.

Normal rows pass without requiring a second-source match.

### Fail-closed behavior

A quarantined daily row:
- is not appended to the admitted prospective price ledger;
- cannot generate CORE3 features;
- cannot issue an H3 forecast;
- cannot settle an outstanding H3 target;
- is retained in a separate integrity audit ledger.

Prospective integrity ledger:
- `GOLD_H3_AURORA_V1_PROSPECTIVE_DATA_INTEGRITY.csv`.

The audit record includes:
- date
- source Stak ref
- four metal values
- decision/status
- severe asset count
- max absolute log-return
- independent XAU
- cross-source divergence
- check timestamp.

### Live prospective integration

Workflow:
- `gold-h3-aurora-prospective-v1.yml`

Validation run:
- **37118755744**
- result **SUCCESS**
- evidence commit **3d08dcf9ace9d3f5232f4bd5a33bb9d4f97174fd**

Current live state at validation:
- integrity gate **ACTIVE**
- prospective forecast rows **0**
- post-freeze daily-price rows **0**
- integrity audit rows **0**
- quarantine rows **0**.

No new post-freeze common-metal Stak row was available on that validation run, so the live ledger remained empty. The gate is nevertheless active and will evaluate the next candidate row before admission.

### Governance

1. Integrity-gate thresholds are data-quality policy, not forecast-performance hyperparameters.
2. They are frozen before forward use; any change requires a new gate version.
3. Historical frozen evidence is not rewritten.
4. A quarantined source row cannot be silently backfilled into a missed prospective forecast.
5. The original AURORA prospective model identity remains unchanged; the gate protects **new data ingestion**.
6. The separate clean retrospective chain in Section 40 remains the authoritative retrospective performance evidence.
7. The pre-existing frozen AURORA expert matrix still represents the original V1 prospective freeze; replacing it with a clean-history matrix would require a separately named clean prospective freeze/version rather than an in-place edit.

Evidence:
- `GOLD_H3_DATA_INTEGRITY_GATE_V1_REPLAY_RESULT_2026-10-03.md`
- `GOLD_H3_DATA_INTEGRITY_GATE_V1_REPLAY_SUMMARY_2026-10-03.json`
- `GOLD_H3_DATA_INTEGRITY_GATE_V1_REPLAY_QUARANTINES_2026-10-03.csv`
- `GOLD_H3_AURORA_V1_PROSPECTIVE_DATA_INTEGRITY.csv`.

## 43. CLEAN H3 PROSPECTIVE V1 FREEZE (2026-10-03)

**Identity:** `CLEAN_H3_PROSPECTIVE_V1`  
**Status:** **FROZEN / READY FOR FIRST FUTURE ORIGIN**  
**First eligible feature cutoff:** **2026-10-05**

This is a separate prospective experiment. It does not replace, edit, relabel or backfill the original AURORA prospective ledger.

Bootstrap workflow:
- run **37120224350**
- result **SUCCESS**
- evidence commit `c2286108458c47a65aade15da7ec5eadbd842498`.

Freeze commit:
- `562901ccb92cb6d7ebf50645f6b2c73c5848a831`.

### 43.1 Clean frozen source

The clean daily freeze changes exactly the validated corrupt 2026-02-27 row:
- Gold 3516.02 -> 5183.80
- Silver 62.15 -> 88.14
- Platinum 1585.39 -> 2369.25
- Palladium 1201.26 -> 1789.96.

All other frozen daily prices remain unchanged.

### 43.2 Reproduction checks

Clean AURORA expert matrix:
- 19 September rows
- max structural probability difference 8.05e-16
- max PATH probability difference 8.88e-16
- **PASS**.

Reversal experts:
- RIFT: 931 rows, identical overrides, max probability diff 9.27e-15
- TURN: 1029 rows, identical overrides, max probability diff 8.33e-17
- VEGA: 931 rows, identical overrides, max probability diff 9.44e-16
- OPAL: 931 rows, identical overrides, max probability diff 7.51e-12
- all **PASS**.

### 43.3 Frozen prospective architecture

No retuning is allowed:
- Clean AURORA baseline
- RIFT V1
- TURN V1
- VEGA V1
- OPAL V1 threshold 0.70
- HELIOS V1 W8 / enter 5 / exit 3
- HELIOS V2 posterior calibration
- V3-GT W8 / broken cost 1.0 / GT >0.50
- V4-RGE W10 / regret +2 / -2
- V5-DCE PATH posterior >0.50 / GT >0.50
- Data Integrity Gate V1.

GT >0.60 / 0.70 remains diagnostic only and is not part of the prospective freeze.

### 43.4 Governance

- no clean prospective evidence exists before 2026-10-05;
- missed future origin -> MISS, never backfilled;
- forecast fields immutable after issuance;
- settlement appends realized fields only;
- quarantined source rows cannot issue or settle;
- any rule, threshold, source-lag or clean-history change requires a new version.

Authority:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FREEZE_2026-10-03.md`.

Frozen files:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_VEGA_PANEL.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv`.

## 44. RECENT H3 MODEL FAMILY — FULL CLEAN SWEEP (2026-10-03)

**Scope:** only the recent post-AURORA performance-improvement lineage. Older generic challenger families were intentionally excluded.

Included:
- AURORA
- TWIN
- PRISM
- RIFT
- TURN
- VEGA
- OPAL
- HELIOS V1 hard/soft
- HELIOS V2
- HELIOS V3-GT
- HELIOS V4-RGE
- HELIOS V5-DCE.

Workflow:
- run **37120950441**
- result **SUCCESS**
- implementation commit **00c6c8520939afa63487f0b5be434b6559d78df7**
- evidence commit **70218342986894cdbe972d7bb1fb7d3158dc9942**.

### 44.1 TWIN and PRISM clean rerun

Both were rerun from clean AURORA under their original frozen selection/confirmation contracts.

TWIN:
- SHAPE24: not eligible
- SHAPE48: not eligible
- SHAPE_MULTI: not eligible
- clean status: **NO_ELIGIBLE_REP**.

PRISM:
- lambda 1: not eligible
- lambda 10: not eligible
- lambda 50: not eligible
- clean status: **NO_ELIGIBLE_LAMBDA**.

Therefore neither TWIN nor PRISM re-enters the promoted recent-model ranking after data cleaning.

### 44.2 Clean 2026 ranking

| Rank | Model | Accuracy | Balanced accuracy | Brier | Logloss |
|---:|---|---:|---:|---:|---:|
| 1 | **HELIOS V5-DCE** | **63.35%** | **63.76%** | **0.2425** | **0.6976** |
| 2 | HELIOS V3-GT | 63.35% | 63.76% | 0.2455 | 0.7045 |
| 3 | OPAL | 63.35% | 63.71% | 0.2467 | 0.7100 |
| 4 | HELIOS V4-RGE | 62.30% | 62.71% | 0.2447 | 0.7029 |
| 5 | HELIOS V2 | 60.73% | 61.16% | 0.2477 | 0.7089 |
| 6 | HELIOS V1 hard | 60.73% | 61.16% | 0.2508 | 0.7158 |
| 7 | HELIOS V1 soft | 60.73% | 61.16% | 0.2513 | 0.7169 |
| 8 | RIFT | 59.16% | 59.57% | 0.2499 | 0.7130 |
| 9 | VEGA | 59.16% | 59.47% | 0.2497 | 0.7118 |
| 10 | AURORA | 58.64% | 59.02% | 0.2532 | 0.7207 |
| 11 | TURN | 57.59% | 58.12% | 0.2568 | 0.7286 |

V5, V3-GT and OPAL tie on directional accuracy at **63.35%**.
V5 is preferred within this tie because it has the best probability quality:
- V5 Brier **0.2425**
- V3 Brier **0.2455**
- OPAL Brier **0.2467**
and the best logloss.

### 44.3 Clean 2025-2026 ranking

| Rank | Model | Accuracy | Balanced accuracy | Brier | Logloss |
|---:|---|---:|---:|---:|---:|
| 1 | **HELIOS V5-DCE** | **65.15%** | **64.24%** | **0.2322** | **0.6717** |
| 2 | HELIOS V4-RGE | 64.46% | 63.57% | 0.2332 | 0.6741 |
| 3 | HELIOS V3-GT | 64.24% | 63.17% | 0.2357 | 0.6788 |
| 4 | OPAL | 64.24% | 62.98% | 0.2389 | 0.6883 |
| 5 | HELIOS V2 | 63.78% | 62.85% | 0.2346 | 0.6767 |
| 6 | HELIOS V1 hard | 63.78% | 62.85% | 0.2360 | 0.6798 |
| 7 | HELIOS V1 soft | 63.78% | 62.85% | 0.2366 | 0.6811 |
| 8 | RIFT | 62.41% | 61.61% | 0.2385 | 0.6850 |
| 9 | VEGA | 61.96% | 61.39% | 0.2381 | 0.6836 |
| 10 | AURORA | 61.96% | 61.15% | 0.2388 | 0.6856 |
| 11 | TURN | 60.59% | 59.49% | 0.2454 | 0.7009 |

### 44.4 Binding interpretation

1. Cleaning the data does **not** uncover a superior TWIN or PRISM branch.
2. The recent-model improvement hierarchy survives the integrity correction.
3. 2026 directional accuracy has a three-way tie at **63.35%** among V5-DCE, V3-GT and raw OPAL.
4. V5-DCE is the strongest recent clean retrospective architecture because:
   - it ties for best 2026 accuracy,
   - has materially better Brier/logloss than V3 and OPAL,
   - and leads the combined clean 2025-2026 window at **65.15%**.
5. V4-RGE remains the second-best cross-regime protected router on 2025-2026.
6. AURORA remains the baseline architecture, not the best final recent model.
7. No thresholds were retuned after cleaning.

Evidence:
- `GOLD_H3_RECENT_CLEAN_SWEEP_RESULT_2026-10-03.md`
- `GOLD_H3_RECENT_CLEAN_SWEEP_SUMMARY_2026-10-03.json`
- `GOLD_H3_RECENT_CLEAN_SWEEP_METRICS_2026-10-03.csv`
- `GOLD_H3_RECENT_CLEAN_2026_RANKING_2026-10-03.csv`
- `GOLD_H3_RECENT_CLEAN_2025_2026_RANKING_2026-10-03.csv`
- `GOLD_H3_RECENT_CLEAN_TWIN_SELECTION_2026-10-03.csv`
- `GOLD_H3_RECENT_CLEAN_PRISM_SELECTION_2026-10-03.csv`.



## 45. MULTI-SPECIALIST REVERSAL DISCOVERY — PHASES 1–9 CLOSURE (2026-10-03)

**Batch objective:** expand reversal candidate recall without using 2026 outcomes for feature/threshold selection.

Motivation remains the clean V5 error anatomy:
- clean 2026 V5 = 121/191 = **63.35%**
- errors = 70
- missed reversal errors = **58**
- V5 missed reversals with no OPAL candidate = **55/58**.

### 45.1 Specialist outcomes

| Phase | Specialist / layer | Binding result | Promotion |
|---:|---|---|---|
| 1 | FLOW-H3 Volume+OI | BLOCKED_EXTERNAL_HISTORICAL_OI_ACCESS | NO |
| 1A | FLOW-VOL-H3 | NO_ELIGIBLE_FLOW_VOL_THRESHOLD | NO |
| 2 | SKEW-H3 | BLOCKED_EXTERNAL_CVOL_ENTITLEMENT | NO |
| 3 | HAZARD-H3 | NO_ELIGIBLE_HAZARD_THRESHOLD | NO |
| 4 | DIVERGE-H3 exact | SOURCE_BLOCKED | NO |
| 4A | DIVERGE-PROXY-H3 | NO_ELIGIBLE_DIVERGE_THRESHOLD | NO |
| 5 | candidate union | NO_ADMISSIBLE_EXPANSION | NO |
| 6 | vintage/overlap accounting | entry gate closed: no new multi-specialist evidence | NO NEW FIT |
| 7 | HELIOS V6 router | NO_ADMISSIBLE_V6_ROUTER_INPUT | NOT FIT |
| 8 | sequential evidence | DEFERRED_NO_V6_EVENT_STREAM | NOT FIT |
| 9 | selective action | DEFERRED_NO_PROMOTED_V6_SIGNAL | NOT FIT |

### 45.2 FLOW result

Full FLOW source and clock were frozen for official COMEX GC FINAL daily Volume+Open Interest. Official historical daily OI was unavailable in the current environment, so the full model was not fit.

A separately preregistered volume-only ablation used strict prior-trade-date GC=F volume. It failed the DEV selectivity gate at every frozen threshold. 2025 and 2026 were therefore not opened.

This rejects only the volume-only fallback; it does **not** reject the untested Volume+OI mechanism.

### 45.3 SKEW result

Gold CVOL directional identities were frozen:
- GCVL
- GCUP
- GCDN
- GCSK
- GCAM
- GCCV.

Historical directional CVOL entitlement was unavailable. No pseudo-skew substitution was allowed. SKEW remains externally blocked rather than model-failed.

### 45.4 HAZARD result

Duration-dependent path features were implemented under a frozen DEV protocol. Recall could be increased only with excessive candidate rate / insufficient precision. No threshold satisfied the preregistered gate. 2025/2026 remained unopened.

### 45.5 DIVERGE result

Exact-source DIVERGE remained transport-blocked. A separately named DXY/TNX/NDX/VIX proxy mechanism test executed with strict prior-date alignment and also failed the DEV selectivity gate. It was not promoted and did not open 2025/2026.

### 45.6 HELIOS V6 admissibility

No new specialist passed its own preregistered admission rule.

Therefore the admissible candidate union is still only OPAL. Renaming an OPAL-only universe as V6 would not create new reversal information and would return to router tuning despite the diagnosed candidate-generation bottleneck.

**HELIOS V6 was therefore not fit or scored.**

Phases 6–9 had their entry gates evaluated separately; none was silently skipped.

### 45.7 Binding state

HELIOS V5-DCE remains the binding clean retrospective champion:
- clean 2026 accuracy **63.35%**
- balanced accuracy **63.76%**
- Brier **0.2425**
- clean 2025–2026 accuracy **65.15%**.

No new 2026 performance claim is created by this batch.

The two highest-information proposed channels — official historical GC Open Interest and directional Gold CVOL — remain **untested due access**, not disproven.

Primary closure authority:
- `GOLD_H3_MULTI_SPECIALIST_PHASE1_9_CLOSURE_2026-10-03.md`
- closure commit `8dd6d3c780a98812437bdc9eed1e0158cc72c6cf`.

Supporting phase authorities:
- `GOLD_H3_FLOW_STAGE1A_CLOSURE_2026-10-03.md`
- `GOLD_H3_SKEW_V1_AUTHORITY_2026-10-03.md`
- `GOLD_H3_HAZARD_V1_RESULT_2026-10-03.md`
- `GOLD_H3_DIVERGE_V1_RESULT_2026-10-03.md`
- `GOLD_H3_DIVERGE_PROXY_V1_RESULT_2026-10-03.md`
- `GOLD_H3_HELIOS_V6_ADMISSIBILITY_RESULT_2026-10-03.md`
- `GOLD_H3_PHASE6_VINTAGE_OVERLAP_GATE_2026-10-03.md`
- `GOLD_H3_PHASE7_HELIOS_V6_ROUTER_GATE_2026-10-03.md`
- `GOLD_H3_PHASE8_SEQUENTIAL_EVIDENCE_GATE_2026-10-03.md`
- `GOLD_H3_PHASE9_SELECTIVE_ACTION_GATE_2026-10-03.md`.


## 46. FLOW PRELIMINARY OPEN INTEREST SALVAGE (2026-10-03)

**Identity:** `FLOW_PRELIM_OI_H3_V1`  
**Status:** **NO_ELIGIBLE_FLOW_PRELIM_OI_THRESHOLD / NOT PROMOTED**

The historical-OI access problem was partially resolved through CME's anonymous FTP:
- `ftp.cmegroup.com/daily_volume`
- daily `daily_volume_YYYYMMDD.xlsx`
- COMEX(STATS) / GC / GOLD FUTURES / F
- Total Volume + **preliminary** Open Interest.

CME marks this OI as preliminary and states that official final OI follows in the next-morning Daily Bulletin. Therefore the original FINAL-only FLOW-H3 V1 remains unchanged; this is a separately named challenger.

### 46.1 Origin-safe rule

- H3 same-day preliminary VOI forbidden.
- Use latest valid CME row with `trade_date < feature_cutoff_date`.
- No lag search.
- No OI imputation.

### 46.2 Source coverage

| Year | Valid / Listed | Coverage |
|---:|---:|---:|
| 2022 | 251 / 251 | 100.00% |
| 2023 | 250 / 251 | 99.60% |
| 2024 | 252 / 252 | 100.00% |
| 2025 | 251 / 251 | 100.00% |
| 2026 through Sep-30 | 53 / 188 | 28.19% |

The FTP product format stops exposing the expected GC OI field after 2026-03-19. This does not affect the essentially complete 2023-2024 DEV test.

### 46.3 DEV 2023-2024

Eligible AURORA-follows-momentum origins: **388**  
True reversals: **111**

| Th | Precision | Recall | Candidate rate | F2 | Eligible |
|---:|---:|---:|---:|---:|---|
| 0.35 | 28.86% | 89.19% | 88.40% | 0.6290 | NO |
| 0.40 | 28.15% | 76.58% | 77.84% | 0.5697 | NO |
| 0.45 | 26.36% | 56.76% | 61.60% | 0.4612 | NO |
| 0.50 | 26.14% | 41.44% | 45.36% | 0.3710 | NO |
| 0.55 | 28.44% | 27.93% | 28.09% | 0.2803 | NO |

Frozen eligibility required:
- precision >=45%
- candidate rate <=35%.

No threshold passed.

Therefore:
- no threshold selected;
- 2025 confirmation **not opened**;
- 2026 outcome holdout **not opened**;
- no V5/OPAL missed-reversal rescue analysis performed;
- no HELIOS promotion.

### 46.4 Interpretation

The prior FLOW-VOL negative result is now reinforced with actual official CME daily aggregate preliminary GC Open Interest.

Under the frozen simple aggregate Volume+OI representation, the reversal score remains insufficiently selective.

This does **not** invalidate FINAL OI, contract-level OI term structure, or Gold options positioning asymmetry.

The same CME FTP files expose separate daily `OG GOLD CALL` and `OG GOLD PUT` Volume/OI rows, enabling a separately preregistered options-positioning asymmetry specialist if research continues.

Authority:
- `GOLD_H3_FLOW_PRELIM_OI_V1_CLOSURE_2026-10-03.md`
- closure commit `1314c1405b0855f51a1881fde053b74f5f8eefa5`.


## 47. RTE — REVERSAL TRANSITION ENGINE V1–V4 (2026-10-03)

**Objective:** solve HELIOS V5 residual reversal errors with an original transition architecture rather than another generic forecasting-model substitution.

### 47.1 RTE V1

Architecture:
- V5-conditioned rescue target;
- matched continuation twins using only matured prior origins;
- intraday/path state;
- official CME prior-trade-date GC volume;
- official CME Gold CALL/PUT volume asymmetry;
- sequential latent transition tension.

CME source coverage is 100% for 2022, 2023, 2024, 2025 and 2026 through Sep-30.

DEV 2023-2024 threshold result:
- 0.55 => rescue/broken/net = 27/44/-17
- 0.60 => 26/34/-8
- 0.65 => 20/25/-5
- 0.70 => 14/18/-4
- 0.75 => 13/13/0
- 0.80 => 11/11/0

Status: `NO_ELIGIBLE_RTE_THRESHOLD`.

### 47.2 Slow-burn discovery and V2B

DEV false-positive anatomy showed high-tension true rescues were generally **persistent/plateau** states, while broken calls were sharp one-origin spikes.

At pRTE >=0.75:
- rescued median ΔpRTE ≈ +0.004
- broken median ΔpRTE ≈ +0.175.

Frozen slow-burn rule:
- previous pRTE >=0.60
- ΔpRTE <=0.05.

2023-2024 development:
- candidates 11
- rescue 9
- broken 2
- net +7
- precision 81.82%.

Untouched 2025 confirmation:
- candidates 1
- rescue 0
- broken 1
- net -1.

Status: `RTE_V2B_2025_CONFIRM_FAIL`.

2026 remained unopened.

### 47.3 2025 mechanism diagnosis

2025 pRTE levels did not collapse:
- q75 ≈0.689
- q90 ≈0.792
- 31 origins >=0.75.

The slow-burn morphology itself failed to transport.

Largest 2025 reversal-vs-continuation separation among audited RTE features:
- signed Gold options pressure against momentum: SMD ≈ +0.39
- pRTE: +0.35
- pInst: +0.34.

### 47.4 RTE V3 — option-confirmed transition

Candidate:
`pRTE >= q AND pInst >=0.50 AND signed Gold options pressure >0`.

2024-2025 aggregate:
- q=.60 => net 0, precision 50.0%
- q=.65 => net +2, precision 51.72%
- q=.70 => net +2, precision 52.38%.

Half-year instability was material:
- 2025 H1 consistently positive, up to net +5;
- 2025 H2 consistently negative, down to net -5.

Status: `NO_ROBUST_RTE_V3_RULE`.

2026 remained unopened.

### 47.5 RTE V4 — material reversal target

Target:
`V5 missed reversal AND abs(H3 return) >=1.0%`.

Best development threshold q=.70:
- candidates 28
- rescue 15
- broken 13
- net +2
- precision 53.57%
- half-year nets +3 / 0 / +4 / -5.

Status: `NO_ROBUST_RTE_V4_RULE`.

2026 remained unopened.

### 47.6 Binding scientific conclusion

RTE produced one strong development mechanism — slow-burn V2B at +7 net and 81.82% precision — but it failed to transport to 2025.

Across V3 and V4, 2025 H1 is favorable while 2025 H2 is systematically harmful.

Therefore the remaining reversal error is now treated as **regime/state conditional** rather than a scalar candidate-threshold problem.

Do not continue blind threshold searches on V1-V4.

Next research direction:
**Regime-Conditional Reversal Transition Engine**.

Primary question:
what origin-observable state changed between 2025 H1 and 2025 H2 that caused reversal-rescue logic to invert?

Governance:
- no RTE version opened 2026 holdout outcomes;
- no 2026 tuning occurred;
- HELIOS V5-DCE remains binding;
- CLEAN_H3_PROSPECTIVE_V1 remains untouched.

Authority:
- `GOLD_H3_RTE_V1_V4_CLOSURE_2026-10-03.md`
- closure commit `7b62df90088f1add53c344ec604975056c9a3bae`.


## 48. RC-RTE — REGIME-CONDITIONAL REVERSAL ENGINE V1/V2 (2026-10-04)

**Objective:** condition reversal-rescue specialists on origin-observable latent market state and bound damage when a historically valid reversal regime inverts.

### 48.1 RC-RTE V1

State axes:
- persistence
- fragility
- option opposition
- participation shock.

Unsupervised state compressor:
- KMeans K=3
- training-only scaling
- training-only regime utility audit.

Frozen proposal union:
- SB slow-burn
- OPT option-confirmed
- MAT material-reversal.

Sequential pre-2026:
- 2024 H2: net 0
- 2025 H1: 15 rescue / 7 broken = **+8**
- 2025 H2: 6 rescue / 14 broken = **-8**.

Pooled net 0, precision 50%.

Status: `NO_ROBUST_RC_RTE_RULE`.

### 48.2 Online credibility insight

2025 H2 chronology showed regime failure was detectable early:
- first five static candidates were broken;
- live regime utility turned negative quickly;
- overlapping H3 candidates could arrive before prior outcomes matured.

This motivated RC-RTE V2.

### 48.3 RC-RTE V2 Fuse

Added:
- maximum one unresolved accepted event per regime;
- accepted matured utility +1 rescue / -1 broken;
- close a regime for the rest of the block as soon as live matured score becomes negative.

Pre-2026:
- 2024 H2: 0 / 0 / net 0
- 2025 H1: 7 rescue / 2 broken = **+5**, precision **77.78%**
- 2025 H2: 0 rescue / 2 broken = **-2**.

Pooled:
- 11 accepted
- 7 rescue / 4 broken
- net **+3**
- precision **63.64%**
- pooled V5 accuracy **68.24%**
- assisted **69.18%**.

The preregistered robustness gate passed, so 2026 was opened exactly once.

### 48.4 2026 clean holdout

- eligible origins: 153
- raw proposals: 35
- accepted: **1**
- rescue / broken / net: **0 / 1 / -1**
- OPAL-no-candidate missed reversals hit: **0 / 55**

Whole clean 2026:
- HELIOS V5-DCE: **121/191 = 63.35%**
- RC-RTE V2 assisted: **120/191 = 62.83%**

Binding result:
**RC-RTE V2 NOT PROMOTED. HELIOS V5-DCE remains champion.**

### 48.5 Post-holdout geometry diagnosis

The single accepted 2026 candidate:
- issue 2026-03-04
- V5 was already correct
- assigned regime 1
- MAT-only proposal
- target H3 return -1.81%.

Specialist identity alone does not explain failure:
- pre-2026 regime-1 MAT-only = 3 rescue / 1 broken = 75% precision.

The stronger failure mode is out-of-distribution regime assignment.

Pre-2026 regime-1 proposal geometry:
- rescue median persistence **-0.357**
- broken median persistence **-0.491**

Accepted 2026 candidate:
- persistence **+0.880**
- fragility -0.317
- option opposition +0.717
- participation shock +1.077.

KMeans forced a nearest-regime assignment even though the candidate was outside the historical persistence support of regime 1.

### 48.6 Binding next direction

Next successor:
**Support-Constrained Regime Reversal Engine**

Required additions:
- regime-membership confidence / support envelope;
- fail-closed OOD behavior;
- specialist-specific regime competence;
- overlap-aware one-outstanding-event control;
- online credibility fuse.

Possible support scores:
- robust Mahalanobis distance;
- conformal nearest-neighbor support;
- rescue-prototype vs broken-prototype distance;
- cluster assignment margin.

Governance:
- 2026 holdout is now spent;
- no later modification may be described as a clean 2026 improvement;
- future successor requires another untouched period or prospective evaluation;
- HELIOS V5-DCE remains binding;
- CLEAN_H3_PROSPECTIVE_V1 remains untouched.

Authority:
- `GOLD_H3_RC_RTE_V1_V2_CLOSURE_2026-10-04.md`
- closure commit `114ca7b5785f6d1a5b3518b5e12c8a24c8b9edd5`.


## 49. SCR-RTE — SUPPORT-CONSTRAINED SPECIALIST REVERSAL ENGINE V1 (2026-10-04)

**Status:** **RETROSPECTIVE DEVELOPMENT FAIL / NOT PROMOTED**

After the RC-RTE V2 clean 2026 holdout was spent, historical 2022–2026-09 data were reclassified as development/stress-test only.

SCR-RTE V1 tested:
- specialist-specific conformal support;
- 5th-nearest-neighbor nonconformity;
- p_support >= 0.10;
- 15-nearest local competence;
- local precision >=60%;
- one-sided Wilson-80 lower bound >50%;
- specialist arbitration;
- one-outstanding H3 event per specialist;
- monthly credibility fuse.

Forward retrospective replay:

| Block | Accepted | Rescue | Broken | Net | Precision |
|---|---:|---:|---:|---:|---:|
| 2024 H2 | 3 | 0 | 3 | -3 | 0.00% |
| 2025 H1 | 7 | 4 | 3 | +1 | 57.14% |
| 2025 H2 | 3 | 0 | 3 | -3 | 0.00% |
| 2026 H1 | 4 | 1 | 3 | -2 | 25.00% |
| 2026 H2 through Sep | 0 | 0 | 0 | 0 | — |

Aggregate:
- accepted 17
- rescue / broken / net = **5 / 12 / -7**
- rescue precision **29.41%**
- V5 accuracy **66.24%**
- SCR-RTE assisted **64.76%**

Therefore the support/OOD filter as implemented does **not** solve the reversal-selection problem and is not promoted.

A prospective freeze artifact was generated before post-freeze use:
- first clean origin 2026-10-05
- training rows 573
- max matured target end 2026-09-29
- SB library 19
- OPT library 85
- MAT library 35

However, because retrospective development performance is materially negative, SCR-RTE V1 should remain **shadow-only** and should not override HELIOS V5-DCE.

Binding champion remains HELIOS V5-DCE.

Authority:
- `GOLD_H3_SCR_RTE_V1_RETRO_RESULT_2026-10-04.md`
- `GOLD_H3_SCR_RTE_V1_PROSPECTIVE_FREEZE_2026-10-04.json`.


## 50. FRS — FUZZY / UNCERTAINTY REPRESENTATION TOURNAMENT V1 (2026-10-04)

Eight uncertainty representations were compared on the **same** origin-safe evidence layer:
- Type-1
- Intuitionistic
- Pythagorean
- q-rung orthopair q=3
- Hesitant
- Picture
- Single-valued Neutrosophic
- Interval Type-2.

Historical 2024H2–2026Sep is development/stress-test only.

### 50.1 Directional FLIP result

| Representation | Flip | Rescue | Broken | Net | Precision |
|---|---:|---:|---:|---:|---:|
| T1 | 22 | 8 | 14 | -6 | 36.36% |
| IFS | 175 | 73 | 102 | -29 | 41.71% |
| Pythagorean | 0 | 0 | 0 | 0 | — |
| q-rung-3 | 0 | 0 | 0 | 0 | — |
| Hesitant | 177 | 74 | 103 | -29 | 41.81% |
| Picture | 84 | 37 | 47 | -10 | 44.05% |
| Neutrosophic | 115 | 53 | 62 | -9 | 46.09% |
| IT2 | 116 | 51 | 65 | -14 | 43.97% |

No representation passed the frozen development gate.

Status:
`NO_PROMISING_FUZZY_REPRESENTATION`.

Rich uncertainty geometry did not solve the regime instability:
- Picture 2025 H1 +10 but 2025 H2 -7 and 2026 H1 -10;
- Neutrosophic 2025 H1 +8 but 2025 H2 -6 and 2026 H1 -9;
- IT2 2025 H1 +7 but 2025 H2 -10 and 2026 H1 -11.

### 50.2 DAMP-only diagnostic

Same-universe V5 baseline:
- n 452
- accuracy 65.93%
- Brier 0.2279
- log loss 0.6612.

IFS / Hesitant / Neutrosophic used only as confidence-damping layers:
- Brier **0.2240**
- delta **-0.0039**
- log loss **0.6515**
- delta **-0.0097**
- direction unchanged.

Block result:
- improvement in 2024 H2, 2025 H1, 2026 H1, 2026 H2;
- degradation in 2025 H2.

Interpretation:
**fuzzy uncertainty is not promoted as a reversal direction engine, but it retains a weak development signal as a confidence-calibration / damping layer.**

Binding next fuzzy direction:
**Fuzzy Confidence Governor**, not another fuzzy UP/DOWN classifier.

HELIOS V5-DCE remains the binding direction champion.

Authority:
- `GOLD_H3_FRS_V1_CLOSURE_2026-10-04.md`
- closure commit `adc95549b9bc90c0533b688f2068e5808c055781`.


## 51. TRES — TRANSITION / REVERSAL EVENT-SURVIVAL RESEARCH V1/V2 (2026-10-04)

**Objective:** replace the terminal-only H3 reversal framing with an origin-safe path-event representation, then test whether that representation can safely repair HELIOS V5 continuation errors.

### 51.1 Stage 0 — event semantics

Frozen path:
- origin = feature_cutoff_date;
- H1/H2/H3 = next 1st/2nd/3rd available Gold observations;
- primary barrier = 1.00× origin-safe sigma20;
- momentum-normalized cumulative return.

Integrity:
- 1,029 / 1,029 rows audited;
- failures 0;
- max target-r3 identity error 9.975e-17.

First-passage terminal-reversal rates:
- REVERSAL: **96.59%**
- CONTINUATION: **10.18%**
- CENSORED: **46.35%**.

Stage 0: PASS.

### 51.2 Stage 1 — discrete competing-risk survival

Monthly expanding multinomial hazard model, no leakage.

Replay:
- 679 OOS predictions;
- 2024-01-02 .. 2026-09-24;
- cumulative-incidence identity failures 0;
- maturity leakage failures 0.

F_reversal top-vs-bottom quintile:
- first-passage reversal: **4.41% -> 34.56%** (+30.15 pp)
- terminal H3 reversal: **20.59% -> 52.94%** (+32.35 pp).

Terminal-reversal separation stayed positive in all six half-year blocks:
+50.0 / +40.0 / +45.8 / +19.2 / +23.1 / +15.4 pp.

Status:
`TRES_EVENT_SIGNAL_PASS`.

Binding positive finding:
**event-time/path state is one of the most stable reversal-risk representations found in the project.**

### 51.3 Stage 2 — V5 error-risk stacking

Only prior OOS Stage-1 predictions were used.

Baseline -> survival-augmented error-risk:
- AUC 0.5595 -> **0.5552**
- Brier 0.2332 -> **0.2355**
- log loss 0.6673 -> **0.6730**.

Status:
`NO_INCREMENTAL_TRES_ERROR_RISK`.

The extra logistic stacking layer degraded the survival signal.

Direct diagnostic in V5-continuation eligible origins:
- F_reversal AUC **0.6194**
- cause-share AUC 0.6138
- cause-dominance AUC 0.6030
- F_reversal bottom/top error rate **19.47% -> 40.71%** (+21.24 pp).

On the exact Stage-2 scored universe:
- meta p_error AUC 0.5552
- direct F_reversal AUC **0.6033**.

Conclusion:
**retain the survival representation; reject the Stage-2 meta-classifier.**

### 51.4 Absorbing-risk flaw / path sequence

The first-passage abstraction loses later crossovers.

Fixed 1σ motifs:
- C_ONLY 527, terminal reversal 6.45%
- R_ONLY 199, 99.50%
- C_THEN_R 23, **95.65%**
- R_THEN_C 6, **0.00%**
- NONE 274, 46.35%.

Latest decisive barrier state:
- CONTINUATION_LAST 533, terminal reversal **6.38%**
- REVERSAL_LAST 222, **99.10%**
- UNRESOLVED 274, **46.35%**.

This provides a principled three-state uncertainty representation:
reversal / continuation / unresolved.

### 51.5 TRES V2 — last-state path governor

Multinomial probabilities:
- mu_R = P(REVERSAL_LAST)
- mu_C = P(CONTINUATION_LAST)
- mu_U = P(UNRESOLVED).

Frozen reversal action:
- only when V5 follows momentum;
- FLIP only if mu_R is the largest membership.

Replay:
- eligible 561
- flips 35 (6.24%)
- rescue / broken / net = **15 / 20 / -5**
- precision **42.86%**
- V5 67.30% -> assisted **66.57%**.

Block net:
+1 / -1 / +4 / **-6** / -2 / -1.

Status:
`TRES_V2_PATH_GOVERNOR_FAIL`.

### 51.6 Binding conclusion

Retain:
- Stage-1 event-time / survival outputs as an auxiliary research signal;
- last-state reversal/continuation/unresolved representation.

Reject:
- V5 error-risk restacking;
- simple argmax path-state FLIP governor.

The remaining problem is intervention selectivity:
**which reversal-prone origin is strong enough to justify overturning an already-good V5 continuation call?**

For later fuzzy / Picture / Neutrosophic work, the path-state tuple
`(mu_R, mu_U, mu_C)`
is the preferred uncertainty basis instead of hand-built arbitrary memberships.

Until independent FLIP evidence exists, use it only for:
- confidence damping;
- abstention;
- conflict / uncertainty measurement.

HELIOS V5-DCE remains the binding direction champion.

Authority:
- `GOLD_H3_TRES_V1_V2_CLOSURE_2026-10-04.md`
- closure commit `7811feb369df56a4369b68d5fd8ac579688f878b`.


## 52. ORS — ORTHOGONAL REVERSAL SURPRISE V1 (2026-10-04)

**Objective:** test whether TRES reversal risk becomes actionable only when it is unusually high relative to historical origins where V5 saw a similar continuation state.

Method:
- use only OOS TRES Stage-1 `F_reversal`;
- condition on an 8-dimensional V5 continuation state;
- monthly expanding matured library;
- K=40 nearest historical V5-similar origins;
- one-sided local rank surprise;
- FLIP only if `p_surprise <=0.10` and reversal is the dominant TRES state.

Integrity:
- maturity leakage failures **0**.

Replay:
- scored origins: 2024-10-31 .. 2026-09-24
- FLIP 15
- rescue / broken / net = **5 / 10 / -5**
- precision **33.33%**
- V5 **66.08% -> 64.81%**
- non-negative blocks 1/5
- worst block -3.

Status:
`ORS_H3_V1_FAIL`.

Important diagnostic:
- high-surprise + reversal-dominant states: terminal reversal 33.33%
- high-surprise but non-dominant states: terminal reversal 50.00%.

Conclusion:
local reversal surprise exists, but the dominance mapping does not create a safe direction override. Do not retune K or surprise threshold on the same replay.

Authority:
- `GOLD_H3_ORS_V1_RESULT_2026-10-04.md`.


## 53. SAGE V1 — SELECTIVE ACTION + GUARDED EXCEPTION (2026-10-04)

SAGE V1 separated:
- TRES path-state for KEEP / ABSTAIN;
- OCS orthogonal concurrence for rare FLIP exceptions.

Common mature universe:
- **252 rows**
- 2025 H2 through 2026 Sep
- source identity mismatches 0
- leakage failures 0.

### 53.1 OCS exception

Frozen concurrence:
- IFBC count60 >=4
- IFBC score >=0.70
- LLRS external-opposes
- LLRS incremental >0
- LLRS pressure >=0.10.

Result:
- FLIP 7
- rescue / broken / net = **6 / 1 / +5**
- precision **85.71%**.

Half-year net:
- 2025 H2 **+1**
- 2026 H1 **+2**
- 2026 H2 **+2**.

### 53.2 TRES abstention

- KEEP 208
- ABSTAIN 37
- selective coverage 85.32%
- selective action accuracy 67.91%
- counterfactual V5 accuracy inside ABSTAIN rows **72.97%**.

Therefore the TRES argmax abstention rule removed rows where V5 was relatively strong rather than concentrating errors.

Binding result:
`SAGE_H3_V1_FAIL`.

Retain OCS exception; reject TRES abstention mapping.

### 53.3 Full-direction development effect of exception-only rule

2025:
- V5 **165/248 = 66.53%**
- V5 + OCS **166/248 = 66.94%**
- net +1.

2026:
- V5 **121/191 = 63.35%**
- V5 + OCS **125/191 = 65.45%**
- exception rescue / broken / net = **4 / 0 / +4**.

These are retrospective development results, not clean holdout evidence.

Authority:
- `GOLD_H3_SAGE_V1_CLOSURE_2026-10-04.md`
- closure commit `6ed564f17f2f4406eaeed8824d537bda493e7736`.


## 54. SAGE V2 — EXCEPTION-ONLY PROSPECTIVE SHADOW FREEZE (2026-10-04)

**Identity:** `SAGE_H3_V2_EXCEPTION_ONLY`  
**Status:** **FROZEN SHADOW CHALLENGER**  
**First eligible clean origin:** **2026-10-05**

Binding baseline:
**HELIOS V5-DCE**.

Frozen action:
- if V5 does not follow momentum -> KEEP V5;
- if V5 follows momentum and the frozen OCS concurrence is true -> FLIP V5;
- otherwise -> KEEP V5.

No ABSTAIN.
No TRES direction override.

Frozen OCS concurrence:
- IFBC count60 >=4
- IFBC score >=0.70
- LLRS external-opposes = True
- LLRS incremental >0
- LLRS pressure >=0.10.

Source fail-safe:
- both IFBC and LLRS must be available under origin-time source integrity;
- missing / invalid source => no exception, KEEP V5;
- no retrospective backfill may create a prospective action.

TRES survives as shadow telemetry only.

Promotion gate:
- >=20 prospective exception actions;
- >=6 calendar months;
- cumulative net rescue >0;
- prospective exception precision >=60%;
- no data-integrity violation;
- same-origin full-direction accuracy >= V5;
- no completed calendar quarter net < -2.

Fail-safe:
- cumulative prospective exception net <= -3 => suppress direction overrides, keep logging in shadow mode.

Until the promotion gate passes:
**HELIOS V5-DCE remains binding production champion.**

Authorities:
- `GOLD_H3_SAGE_V2_EXCEPTION_ONLY_PROSPECTIVE_FREEZE_2026-10-04.md`
- freeze commit `814ed94239cfaf9ad07736ed1f824bfa1b1945b0`
- JSON commit `9d9c6c85b331c0f1e8715d3b7521c34babc391a8`
- prospective ledger initialized at `GOLD_H3_SAGE_V2_PROSPECTIVE_LEDGER.csv`.


## 55. DAILY ACTION LAYER — CIG-D1 CONSENSUS INTEGRITY GATE (2026-10-05)

**Identity:** `CIG_D1_V1`  
**Status:** `RETROSPECTIVE_SELECTIVE_D1_CHALLENGER`  
**Detailed authority:** `GOLD_D1_CIG_V1_RESULT_2026-10-05.md`

### 55.1 Objective

The original H3 target remains the net XAU direction over the next three business days. CIG-D1 is a separate operational layer asking:

> Given only the H3 expert state available at issuance, what should be done for the current trading day?

The same-day D1 target is scored from the previous available XAU close to the current daily close. The H3 models themselves are not retrained or relabeled.

Binding action semantics:
- D1 UP -> **LONG**
- D1 DOWN -> **OUT / CASH**
- unresolved -> **UNCERTAIN / no new D1 position**

### 55.2 Direct H3-to-D1 diagnostic

Common 2026-01-02 through 2026-07-31 window, N=145:

| H3-derived daily signal | Correct | D1 accuracy |
|---|---:|---:|
| **SAGE V2 + RuleFlow V3-TG** | **103/145** | **71.03%** |
| HELIOS V5-DCE | 102/145 | 70.34% |
| RIFT | 102/145 | 70.34% |
| VEGA | 102/145 | 70.34% |
| RC-RTE V2 | 102/145 | 70.34% |
| DPTC-Q95 | 98/145 | 67.59% |

Key result:

**the best H3 model is not the best same-day model.**

DPTC-Q95 is stronger on the H3 terminal target, but some of its reversal interventions are early relative to the current day. It is therefore not used as the binding D1 direction engine.

### 55.3 Binding CIG-D1 expert set

CIG-D1 V1 uses four expert states:
1. SAGE V2 + RuleFlow V3-TG;
2. HELIOS V5-DCE;
3. RIFT;
4. VEGA.

They are not claimed to be formally independent estimators. They are retained because they expose materially different continuation/reversal mechanisms within the H3 stack.

RC-RTE V2 is not granted an additional equal vote because it adds insufficient independent daily variation relative to V5 on the common 2026 window. DPTC, BOCPD, SELLR, OPAL and dependence-phase states remain telemetry/challenger context rather than binding equal-vote D1 inputs.

### 55.4 Binding decision rule

- 4/4 UP -> **HIGH-CONFIDENCE D1 UP -> LONG**
- 4/4 DOWN -> **HIGH-CONFIDENCE D1 DOWN -> OUT/CASH**
- any disagreement -> **UNCERTAIN**

No majority override is allowed.

2026 Jan-Jul:

| State | N | Correct | Accuracy |
|---|---:|---:|---:|
| **4/4 consensus** | **125** | **93** | **74.40%** |
| **disagreement** | **20** | **10** | **50.00%** |

Selective coverage:
**125/145 = 86.21%**.

The improvement comes from **abstaining when expert integrity breaks**, not from adding more votes.

### 55.5 Historical transport evidence

Because the exact current SAGE source contract cannot be reconstructed identically for all early years, older transport is separated rather than fabricating a synthetic SAGE history.

Common-core proxy, V5 + RIFT + VEGA:
- 2023: **169/206 = 82.04%**, coverage 94.1%
- 2024: **178/220 = 80.91%**, coverage 91.7%.

Current enhanced CIG-D1 architecture:
- 2025: **176/218 = 80.73%**, coverage 87.9%
- 2026 Jan-Jul: **93/125 = 74.40%**, coverage 86.2%.

Interpretation:
- the consensus effect predates 2026;
- absolute accuracy weakens in 2026;
- consensus remains materially stronger than disagreement;
- the architecture is a **selective predictor**, not an unconditional daily classifier.

### 55.6 Resolver research — rejected

The UNCERTAIN subset was explicitly attacked with several alternatives.

**Majority voting**
- 2026 Jan-Jul: **102/145 = 70.34%**
- below SAGE+RuleFlow alone and below selective consensus.

**Static disagreement-pattern lookup**
- 2025 resolved examples: **5/11 = 45.45%**
- 2026 resolved examples: **3/8 = 37.50%**
- failed transport.

**Rolling best-expert / recent competence selector**
- unstable across years;
- representative 60-day selection deteriorates from useful 2024 behavior to approximately chance in 2025 and materially below chance in the 2026 disagreement sample.

**Supervised KEEP/FLIP residual classifier**
- DR-Selective: 2025 **12/16 = 75.0%**, 2026 **6/15 = 40.0%**
- DR-Full: 2025 **27/39 = 69.2%**, 2026 **9/18 = 50.0%**
- non-stationary mapping; rejected.

**Label-free dependence / transition state as direct direction override**
- useful as regime telemetry;
- not stable enough to decide KEEP/FLIP on the D1 disagreement subset.

**Recency-weighted Pattern Regime Memory**
- local useful pockets exist;
- under the binding requirement to increase coverage without reducing 2025 consensus accuracy, no acceptable parameterization survived.

Scientific conclusion:

> **expert disagreement is the observable uncertainty state.**

The correct formulation is:
`H3 expert state -> trustworthy D1 direction OR abstain`,
not
`all days -> forced UP/DOWN`.

### 55.7 Next research lane

CIG-D1 already covers approximately 86% of the 2026 Jan-Jul D1 universe. The remaining research problem is restricted to the UNCERTAIN subset.

Any future rescue layer must add **orthogonal information**, not another recombination of the same H3 states. Preferred inputs:
- H1 / intraday path;
- overnight move;
- opening-state momentum and reversal;
- intraday volatility / deceleration;
- event proximity and event-time reaction;
- origin-safe cross-asset state.

This component must be a separately named and frozen **D1 Rescue Head**, and ABSTAIN remains mandatory when evidence is weak.

### 55.8 2026-10-05 diagnostic issuance

For feature cutoff 2026-10-02 and planned issue 2026-10-05, diagnostic-nowcast evidence currently gives:
- AURORA: DOWN, p_up 0.30075;
- HELIOS V5-DCE: DOWN, p_up 0.30075;
- RIFT: DOWN, reversal probability 0.55628, no override;
- VEGA: DOWN, reversal probability 0.46319, no override.

This is **diagnostic-nowcast**, not clean prospective validation. A completed CIG-D1 4/4 record requires the same-origin SAGE+RuleFlow state under its frozen source/timing contract.

### 55.9 Governance

Allowed:
- retrospective D1 diagnostics;
- frozen future shadow evaluation;
- LONG / OUT / UNCERTAIN reporting under the exact CIG-D1 rule.

Not allowed:
- relabeling retrospective evidence as prospective;
- tuning membership/thresholds on 2026 outcomes and calling the result OOS;
- forcing an action on UNCERTAIN days without a separately frozen rescue identity;
- silently mixing target clocks or price sources.



### 55.10 CIG-D1 extended 2026 Jan–Sep source-refresh replay (2026-10-05)

A later audit established why the original CIG-D1 2026 Jan–Jul universe contained **145** days: the then-frozen StakTrakr 2026 source vintage had exactly 145 weekday Gold observations through 2026-07-31 and lacked six weekdays later restored by the clean source refresh:

- 2026-02-27
- 2026-03-02
- 2026-03-03
- 2026-03-04
- 2026-03-05
- 2026-03-06

Therefore the original **125/145 consensus, 93 correct = 74.40%** remains the authority for its frozen source vintage and must not be mechanically concatenated with later-source Aug–Sep rows.

A coherent replay was instead run from scratch on the later clean frozen daily-price snapshot, using the unchanged four-expert CIG rule:
- SAGE V2 + RuleFlow V3-TG
- HELIOS V5-DCE
- RIFT
- VEGA
- 4/4 agreement only; otherwise UNCERTAIN.

Refreshed replay:

| Period | D1 days | Consensus N | Correct | Consensus accuracy | Coverage | Disagreement |
|---|---:|---:|---:|---:|---:|---:|
| Jan–Jul refreshed | 151 | 131 | 94 | 71.76% | 86.75% | 20 |
| Aug–Sep | 40 | 26 | 18 | 69.23% | 65.00% | 14 |
| **Jan–Sep refreshed** | **191** | **157** | **112** | **71.34%** | **82.20%** | **34** |

Aug–Sep detail:
- August: 21 D1 days; 10 consensus; 8 correct = **80.00%**; coverage **47.62%**.
- September: 19 D1 days; 16 consensus; 10 correct = **62.50%**; coverage **84.21%**.
- Across all 34 refreshed Jan–Sep disagreement days, a forced V5 call is **17/34 = 50.00%**, preserving the core interpretation that disagreement is an observable uncertainty state.

Important governance:
- this is **retrospective source-refresh diagnostic evidence**, not prospective OOS;
- it does **not supersede** the original CIG-D1 V1 frozen-vintage result;
- old-vintage Jan–Jul counts and refreshed Aug–Sep counts must not be silently mixed;
- archived mature H3 expert states support D1 issue dates through 2026-09-25; Sep 28–30 require same-origin inference under frozen contracts rather than outcome-based imputation.

Authority:
- `GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.md`
- `GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv`
