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
