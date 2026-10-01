# GOLD SHORT-HORIZON GLOBAL XAU PROJECT MANIFEST

**Date:** 2026-10-01  
**Status:** ACTIVE — 2025/2026 TRANSPORT COMPLETE / H3 DIRECTION FAILED OUT-OF-SAMPLE TRANSPORT  
**Supersedes for tactical objective:** BIST-Metal-Price short-horizon mainline.

## 1. Objective

Build a separate short-horizon Gold forecast engine for **global XAU/USD** investment research.

Primary horizons:
- H1
- H3
- H5

Primary target form:
- forward log return
- direction
- Q10/Q50/Q90 distribution.

## 2. Target authority

Historical development target:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- source lineage: lbruton/StakTrakr
- underlying spot source: MetalPriceAPI XAU
- daily history semantic: daily spot-average representation
- coverage currently verified: 2010-01-04 .. 2026-07-31.

This is a **global spot research target**, not Borsa İstanbul Metal Price.

Prospective live extension:
- existing candidates `XAU_EOD_TWELVE_NY17` and `XAU_DAILY_XAUS` were screened;
- neither passes strict same-target bridge equivalence to the historical StakTrakr / MetalPriceAPI daily-average target;
- `XAU_EOD_TWELVE_NY17` is the closer candidate but remains a separate live anchor.

Therefore do not stitch any live series into the development target series.

## 3. Governance

- DEV selection: 2022-2024 only.
- 2025: frozen transport, no tuning.
- 2026: retrospective/prospective only after model contract freeze.
- no random split.
- chronological expanding evaluation.
- no BIST target values enter this mainline.

## 4. Global metal features

Historical daily research series:
- Gold: XAU_STAKTRAKR_RESEARCH_DAILY_R1
- Silver: XAG_STAKTRAKR_RESEARCH_DAILY_R1
- Platinum: XPT_STAKTRAKR_RESEARCH_DAILY_R1
- Palladium: XPD_STAKTRAKR_RESEARCH_DAILY_R1.

Initial blocks:
- GOLD_ONLY
- CORE3 = Gold + Silver + Platinum
- CORE4 = CORE3 + Palladium
- CORE3 + safe external.

## 5. Safe external families

Reuse existing release-aware authorities:
- H.15 nominal / real 10Y / breakeven proxy
- H.10 Broad USD + major FX
- VIX
- Nasdaq-100.

WTI/Brent remain excluded from first screen pending short-horizon PIT release mapping.
Daily GPR remains optional challenger.

## 6. Model order

First screen:
- direction baselines
- Logistic L2
- LightGBM
- XGBoost
- return zero/mean baselines
- Elastic Net
- LightGBM
- XGBoost
- LightGBM quantile Q10/Q50/Q90.

Deep models remain blocked until classical global-XAU evidence is established.

## 7. Economic scope

No trading/P&L rule is authorized in the first global-XAU screen.

First determine:
- which horizon passes;
- which model/feature block passes;
- whether the global target behaves materially better than the archived BIST target for short-horizon forecasting.

## 8. Prior BIST project

Stages 0-6C of the prior BIST-target short-horizon project remain archived evidence.

They must not be merged into global-XAU performance tables.

## 9. Current evidence

Data readiness:
- COMPLETE / PASS
- run **36900860852**
- artifact **11181284118**
- pre-DEV safe history: 3,011
- DEV: 755
- frozen 2025: 253.

Stage 1 classical / boosting screen:
- COMPLETE / PARTIAL SIGNAL
- run **36901409925**
- aggregate artifact **11181622889**.

| Horizon | Direction | Return | Quantile |
|---|---|---|---|
| H1 | FAIL | FAIL | FAIL |
| **H3** | **PASS** | FAIL | FAIL |
| H5 | FAIL | FAIL | FAIL |

Frozen first-screen H3 direction leader:
- **CORE3 / Logistic L2**
- Brier **0.246731**
- baseline **0.249712**
- relative improvement **+1.19%**
- log loss **0.686634** vs baseline **0.692572**.

Binding interpretation:
- H3 is the only horizon with pre-2025 predictive evidence;
- the evidence is direction-only;
- no return-magnitude, quantile, or tactical engine is yet promoted.

## 10. Stage 2 robustness evidence

Stage 2:
- COMPLETE / **ROBUST_PASS**
- run **36911524415**
- artifact **11186831488**.

Frozen H3 direction engine:
- **CORE3 / Logistic L2**
- Brier **0.246731**
- baseline **0.249712**
- relative improvement **+1.19%**
- log loss **0.686634**
- prediction SD **0.0442**.

Annual relative Brier improvement:
- 2022: **+1.99%**
- 2023: **+0.15%**
- 2024: **+1.44%**.

All 3 DEV years remain positive versus baseline.

Representation result:
- GOLD_ONLY: -0.15%
- CORE3: **+1.19%**
- CORE4: +0.70%
- CORE3 + raw safe external: -0.34%
- CORE3 + transformed safe external: -0.35%.

Thus:
- retain CORE3;
- do not add Palladium;
- do not add the current rates / FX / VIX / Nasdaq external block to this H3 Logistic engine;
- H5 remains secondary and fails the >=1% gate.

## 11. Live-source bridge status

Existing-source screen:
- run **36911112098**
- artifact **11186955894**.

Bridge to historical target:
- NY17 Pearson 0.9375, sign agreement 65.3% -> FAIL
- XAU_DAILY_XAUS Pearson 0.7320, sign agreement 74.5% -> FAIL.

Prospective live source remains unresolved as an exact target-equivalent extension.

This does not affect the retrospective Stage-1/2 DEV evidence because no source stitching occurs there.

## 12. Stage 3 calibration / conviction evidence

Stage 3:
- COMPLETE / **NO_CONVICTION_PASS**
- workflow run **36925853403**
- selected probability stream: **RAW**
- 2025 remained unopened.

Calibration comparison:

| Method | Brier | Log loss | Prediction SD | ECE | Decision |
|---|---:|---:|---:|---:|---|
| **RAW** | **0.246731** | **0.686634** | 0.0442 | 0.0266 | **RETAIN** |
| PLATT | 0.250391 | 0.694437 | 0.0550 | 0.0204 | REJECT |
| ISOTONIC | 0.255205 | 0.781230 | 0.0992 | 0.0449 | REJECT |

Raw calibration diagnostics:
- intercept **0.0376**
- slope **1.2331**.

Frozen conviction bands:
- p >=0.55: n=139, realized H3 UP **61.15%**
- p <=0.45: n=64, realized H3 UP **43.75%**
- realized-UP separation: **17.40 pp**.

The high-UP side is supported and transports across DEV years by count, but the low-UP side misses the frozen <=42.5% realized-UP requirement. Therefore the joint conviction gate fails.

Binding interpretation:
- retain H3 / CORE3 / Logistic L2 as a modest probabilistic direction research engine;
- retain RAW probabilities; do not Platt/isotonic recalibrate;
- do not convert the current probability bands into a tactical trading rule;
- do not use the complement of weak-UP evidence as a validated DOWN signal;
- do not open 2025 to rescue the gate.

## 13. Frozen 2025 / 2026 transport evidence

Transport:
- COMPLETE
- authoritative run **36926432212**
- binding model: **H3 / CORE3 / Logistic L2 / RAW**
- primary mode: **STRICT_FROZEN_FIT**
- no 2025/2026 result used for tuning or selection.

Primary strict frozen-fit result:

| Year | N | Accuracy | Balanced accuracy | Brier | Log loss | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 253 | 49.4% | 49.4% | 0.2509 | 0.6949 | 49.4% | 49.5% |
| 2026 | 142 | 42.3% | 45.2% | 0.2655 | 0.7261 | 75.0% | 15.4% |

Frozen conviction-band transport:

2025:
- p>=0.55: n=53, realized UP **49.1%**
- p<=0.45: n=47, realized UP **42.6%**

2026:
- p>=0.55: n=71, realized UP **47.9%**
- p<=0.45: n=14, realized UP **71.4%**

Secondary frozen walk-forward diagnostic:
- 2025 accuracy 52.2%, balanced accuracy 51.3%, Brier 0.2499
- 2026 accuracy 42.3%, balanced accuracy 45.3%, Brier 0.2685.

Binding interpretation:
- the pre-2025 H3 direction edge does **not transport** to 2025/2026;
- Stage-3 high-UP conviction behavior also does not transport;
- 2026 shows severe directional asymmetry: UP recall is high only because the model over-predicts UP, while DOWN recall collapses to 15.4%;
- do not tune thresholds on 2025/2026 to rescue this engine;
- retain all results as frozen out-of-sample evidence.

## 14. Exact next action

Do **not** proceed to tactical/P&L optimization with the current H3 / CORE3 / Logistic L2 engine.

Next research question:
- diagnose why the signal transports in DEV but breaks in 2025/2026;
- specifically test regime / distribution shift and feature-sign stability using the already frozen prediction ledgers;
- this diagnostic must not retune the model on 2025/2026;
- any future challenger must be preregistered using pre-2025 evidence and evaluated against this frozen transport record.

Do not return to BIST as tactical target.
