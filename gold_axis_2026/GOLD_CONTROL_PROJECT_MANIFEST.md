# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.97  
**Issue date:** 2026-09-22  
**Repository:** ataullahturgut/sim3-automation  
**Canonical branch:** gold-r4-direction-engine  
**Project root:** gold_axis_2026/  
**Status:** canonical research/governance authority

---

## 1. Sole authority and document policy

This file is the only project-level authority for Gold Control architecture, model status, data chronology, evaluation governance, research decisions and next-step sequencing.

GitHub is authoritative for code, branch/commit lineage and this manifest. Production Neon is authoritative for mutable observations and point-in-time source lineage. Research database access is read-only unless a later user authorization explicitly changes that rule.

A model entry in this manifest must contain, at minimum:

- identity and role;
- how the method is constructed;
- scientific or methodological source;
- data actually used;
- chronology/evaluation design;
- principal results;
- final decision/status;
- reproducibility branch or commit when available.

Do not create separate prose result summaries, handover notes, checkpoints, design notes or repeated model descriptions on the canonical branch when the same information belongs here. Detailed code, JSON/CSV outputs, preregistration and workflow evidence may remain on research branches and in Git history. Historical deletion from the current tree does not erase Git history.

If a source, exact paper, parameter, clock or data lineage is not proved, record NOT_PROVEN, NOT_FOUND or BLOCKED rather than reconstructing it by guesswork.

---

## 2. Binding governance

The following locks are binding:

- no random split for time-series research;
- use chronological, rolling or expanding-origin evaluation;
- 2025 is researcher-visible retrospective challenge/stress evidence and must not be used to retune a model after seeing its result;
- 2026 is retrospective transport/stress evidence, not fresh blind confirmation;
- no target/future observation may enter an earlier origin;
- no silent provider substitution;
- no result-dependent rescue under the same model identity;
- risk forecasting and direction forecasting are different tasks;
- a high downside-risk alarm is not automatically a DOWN, SELL or trading signal;
- AUTO_SELECTOR = OFF;
- AUTO_ENSEMBLE = OFF;
- CURRENT_GENERAL_DOWN_DIRECTION_ENGINE = NOT_PROVEN;
- RUNTIME_PROMOTION = NOT_AUTHORIZED for the downside research recorded below;
- no production DB writes from the research workflows;
- no automatic BUY/SELL/HOLD/EXIT mapping.

Evidence classes must remain explicit: historical replay, retrospective challenge/stress, or prospective shadow. Only future outcomes first observed after a frozen architecture can become genuine prospective evidence.

---

## 3. Current project architecture

Gold Control has two parallel primary lines.

### 3.1 Monthly H=1 price-level line

The monthly line remains active and independent. Governed identities:

- CAUSAL_PATCH
- VW_MIDAS_MSVR_SUCCESSOR_V1
- MOMENTUM_3M
- RANDOM_WALK
- MONTHLY_DIRECTION_3M as strategic direction/prior context

This manifest update does not alter their previously frozen monthly role or issued reference values.

### 3.2 Short-term structural / downside research

The short-term project must not collapse unlike tasks into one score. Current conceptual separation:

1. **Structural early-warning / GC-BREAK:** trend weakening, break alert, confirmation and new-regime recognition.
2. **Downside-risk motor:** estimate whether next-day downside risk intensity is high.
3. **Verifier / confirmation motor:** when the risk motor fires, determine whether the alarm is likely to resolve as true next-day DOWN or rebound/UP. The first frozen UP-countersign veto using existing direction models has been executed and did not produce a safe verifier; this role remains unresolved.
4. **Timing motor:** determine whether an apparent t+1 false alarm is actually an early warning for a downside event at t+2/t+3/t+5.

The currently strongest downside-risk research reference is SQRT_HAR_DR. It is not a proven general DOWN-direction engine.

---

## 4. Core data and clock authority

### 4.1 Gold intraday downside research panel

Primary source for the recent downside-risk sequence:

public.xau_intraday_research_cache_5m

Frozen construction:

- timezone America/New_York;
- weekdays only;
- retain a date when at least 240 five-minute closes are present;
- intraday returns are consecutive within the same date;
- no overnight/cross-date return enters realized semivariance;
- DR_t = sum of squared negative 5-minute returns;
- SD_t = sqrt(DR_t);
- daily close = final retained five-minute close.

### 4.2 Daily external Gold panel

The corrected extreme-loss hazard experiment uses true Twelve Data XAU/USD daily bars requested in America/New_York. The earlier StakTrakr R1 experiment is not authoritative because its return axis did not align sufficiently with governed NY17 semantics.

### 4.3 Cross-market sensor

SP500_FRED from public.observations was used as the only long-history daily external sensor in the 22 September cross-market veto experiment.

### 4.4 Insufficient-history sensors as of 2026-09-22

- VIX_CBOE: only 2026-03 onward in the current DB;
- DTWEXBGS_FRB_H10 broad USD: only late-2025 onward;
- DEXCHUS_FRB_H10 USDCNY: only late-2025 onward;
- DGS10_ALFRED_PIT_ME and DFF_ALFRED_PIT_ME: long calendar coverage but monthly-snapshot structure, not a daily verifier feed.

These are not accepted as pre-2025 daily verifier data without a new origin-safe data path.

---

## 5. Current governed/runtime context

The existing governed runtime identities remain registered unless a later manifest change explicitly removes them. The recent downside research identities below are research-only and do not become governed runtime identities by appearing in this manifest.

FAST remains tactical trend context. SLOW remains slower confirmation/new-regime context. GVZ_RISK remains risk/severity context where chronology-safe. MACRO_EVENT_SUCCESSOR_V2 and Emergency identities retain their previously governed contextual roles. They are not equal direction votes.

Historical fixed-horizon 1D/3D studies remain historical evidence only and do not redefine the current short-term architecture.

---

## 6. Historical direction / GC-BREAK family decisions retained compactly

This section preserves only the decisions needed to avoid repeating failed work. Detailed legacy artifacts remain in Git history.

| Family / model | Source / construction | Key retained result | Decision |
|---|---|---|---|
| BOCPD hourly B2 baseline R2 | Bayesian online change-point detection on hourly Gold; frozen pre-2025 comparator | 2024 auxiliary abnormal-volatility comparison: precision 0.2105, recall 0.6471, F0.5 0.2434 | benchmark only |
| BOCPD hourly B2 adaptive-hazard V5 | adaptive-hazard BOCPD successor | same 2024 comparison: precision 0.2308, recall 0.8235, F0.5 0.2696; false-warning burden still material | retained research reference; not runtime |
| RSM / ERSM family | regime-switching / explicit regime sequence | failed family under governed tests | TERMINATED / DO_NOT_REVISIT unless user reopens |
| VLMC family | variable-length Markov chain direction models | corrected family found unstable signal; successors failed transport; 2025 variants often collapsed toward always-UP | CLOSED / NO_PROMOTION |
| BCT / CTW-52 direction | Bayesian context tree / context-tree weighting | probability stability improved but 2025 produced 52/52 UP and no useful DOWN discrimination | CLOSED / NO_PROMOTION |
| RealP-CARR direction | realized-probability plus asymmetric CARR/QMLE | 2024 BA 0.4651, DOWN sensitivity 0.1154; 2025 BA 0.4444, DOWN sensitivity 0 | CLOSED / NO_PROMOTION |
| Parisi Rolling-Ward reconstruction V2 | Parisi, Parisi & Díaz (2008), weekly Gold + DJIA lag structure, rolling Ward NN reconstruction | 2024 BA 0.5180, DOWN sensitivity 0.1739; 2025 BA 0.5017, DOWN sensitivity 0.1176 | NO_PROMOTION |
| Bonato QBoost realized moments | Bonato et al. (2018), quantile boosting with realized moments, source-constrained Spot-XAU adaptation | no 2024 horizon/model passed frozen promotion gate; 2025 raw accuracy pockets had weak DOWN discrimination | NO_PROMOTION |
| Altuntaş AlexNet candle V1 | source-constrained AlexNet on true daily XAU/USD OHLC | 2024 BA 0.4984; 2025 BA 0.5044, below always-UP raw accuracy | NO_PROMOTION |

Literature candidates whose source-faithful input panel or exact method remained incomplete stay NOT_IMPLEMENTED/BLOCKED rather than being treated as tested successes.

---

## 7. DOWN / downside-risk research ledger

This is the canonical record for the 21–22 September 2026 downside sequence. Each entry records method, source, data, result and decision once.

### 7.1 TTSM realized-semivariance direction/reversal

**Identity:** DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_RESEARCH  
**Role:** standalone direction/reversal candidate.  
**Source:** Liu, Lu, Li & Wang (2023), “Time series momentum and reversal: Intraday information from realized semivariance”, Journal of Empirical Finance 72, 54–77, DOI 10.1016/j.jempfin.2023.03.001.  
**Data:** public.xau_intraday_research_cache_5m.  
**Construction:** 20-day momentum; five-day positive/negative realized semivariance; 250-observation empirical Q80 references; source Region 1–4 mapping.  
**Chronology:** warm-up through 2021; 2022–2023 development/audit; 2024 fixed validation; unchanged 2025 challenge.  
**Result:** 2024 TTSM-S1 active BA 0.4725, full DOWN sensitivity 0.2907, UP-to-DOWN reversal sensitivity 0.1111. In 2025 full DOWN sensitivity fell to 0.1753 and reversal sensitivity to 0.0395.  
**Decision:** NO_PROMOTION / PRE2025_DOWN_REVERSAL_GATE_FAILED / 2025_TRANSPORT_FAILED. Retain only as signed-semivariance reversal reference.

### 7.2 Discrete-Burr LACD-POT extreme-DOWN hazard R2

**Identity:** DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1R2_RESEARCH  
**Role:** next-day probability of an extreme negative return; not ordinary DOWN classification.  
**Source:** Bień-Barkowska (2024), “Forecasting extreme negative returns in gold and silver: A discrete-duration approach to POT models”, DOI 10.1002/asmb.2759; reconstruction authority Bień-Barkowska (2020), DOI 10.12693/APhysPolA.138.48.  
**Data:** Twelve Data XAU/USD daily bars, America/New_York.  
**Construction:** formation Q95 loss threshold; inter-event duration and excess magnitude; log-LACD state; right-shifted discrete Burr duration likelihood; one-day hazard; formation Q95 hazard alert threshold.  
**Chronology:** formation through 2023-12-31; 2024 fixed validation; unchanged 2025 challenge.  
**Result:** 2024 AUC 0.5933 but alert coverage and recall were 0. In 2025 AUC 0.5649; TP 4, FP 40, recall 0.2353, precision 0.0909.  
**Decision:** NO_PROMOTION / EXTREME_DOWN_HAZARD_NOT_SUPPORTED. R1 StakTrakr input conclusion is non-authoritative.

### 7.3 RAW HAR-DR

**Identity:** DOWNSIDE_HAR_DR_XAU_V1_RESEARCH  
**Role:** next-day downside realized-semivariance intensity.  
**Source:** Xie, Wang, Chen & Gong (2019), DOI 10.1016/j.physa.2018.11.028; realized-semivariance authority Barndorff-Nielsen, Kinnebrock & Shephard.  
**Data:** public.xau_intraday_research_cache_5m.  
**Construction:** OLS HAR with daily DR, mean5(DR), mean22(DR). No regularization, transforms, jumps, macro or nonlinear terms.  
**Result:** annual-origin comparison gave 2022 R2 0.2791/AUC 0.7146; 2023 0.5308/0.6821; 2024 0.1891/0.7283; 2025 stress -0.0014/0.8395; 2026 YTD 0.2474/0.6198. Original 2024 fixed validation passed the risk gate; level calibration weakened in 2025 while risk ranking remained strong.  
**Decision:** RETAINED_DOWNSIDE_RISK_BASELINE / MANDATORY_COMPARATOR / NOT_RUNTIME. Risk sensor only, not a DOWN-direction engine.

### 7.4 RAW QHAR-DR

**Identity:** DOWNSIDE_QHAR_DR_XAU_V1_RESEARCH  
**Role:** test direct QLIKE estimation of the raw HAR-DR form.  
**Source:** same HAR-DR structure; estimation intervention only.  
**Data:** same 5-minute Gold panel.  
**Construction:** identical daily/5D/22D linear form, coefficients estimated by direct QLIKE rather than OLS.  
**Result:** 2024 QLIKE 0.7361 versus raw OLS 0.1565; high-risk coverage collapsed to 1.0; 2025 remained worse.  
**Decision:** REJECTED / RAW_QLIKE_ESTIMATION_FAILED. Closed under this identity.

### 7.5 SQRT-QHAR-DR

**Identity:** DOWNSIDE_SQRT_QHAR_DR_XAU_V1_RESEARCH  
**Role:** source-consistent QLIKE estimation on semideviation scale.  
**Source:** transformed realized-volatility literature; same HAR memory structure.  
**Data:** same 5-minute Gold panel.  
**Construction:** SD=sqrt(DR); QLIKE fit on SD using daily/5D/22D components; squared back to DR.  
**Result:** 2024 SD-QLIKE 0.037432 versus transformed OLS 0.037306; DR-QLIKE 0.157983 versus raw HAR-DR 0.156463. 2025 DR-QLIKE 0.335471 versus raw 0.309654.  
**Decision:** NO_PROMOTION / SOURCE_CONSISTENT_QLIKE_HYPOTHESIS_FAILED. QLIKE route closed; transformed OLS comparator motivated the next study.

### 7.6 SQRT-HAR-DR multi-origin representation study

**Identity:** DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH  
**Role:** current strongest recent downside-risk research candidate.  
**Source:** HAR-DR plus semideviation representation; hypothesis isolated to representation only.  
**Data:** public.xau_intraday_research_cache_5m.  
**Construction:** OLS HAR on SD=sqrt(DR), predictors SD_t, mean5(SD), mean22(SD), target SD_t+1; forecast squared back to DR. No bias correction, clipping, macro, regime, window search or QLIKE fit.  
**Chronology:** annual expanding origins; 2022–2024 primary retrospective falsification, 2025/2026 retrospective stress.  
**Result:** R2/AUC by year: 2022 0.2640/0.7153; 2023 0.5698/0.6896; 2024 0.2025/0.7320; 2025 stress 0.0611/0.8401; 2026 YTD 0.2841/0.6434. Pooled 2022–2024 MSE improved about 0.67% versus RAW and QLIKE improved about 2.32%; paired HAC loss differences were not statistically strong. Native 2025 high-risk task: 90 alarms, TP 66, FP 24, precision 0.7333, recall 0.6735, F1 0.7021. If those alarms are incorrectly forced into DOWN calls, the same 90 become 45 TP and 45 FP, precision 0.50 and recall about 0.464.  
**Decision:** CURRENT_RECENT_DOWNSIDE_RISK_RESEARCH_REFERENCE / RESEARCH_ONLY / NOT_RUNTIME / NOT_PROVEN_GENERAL_DOWN_DIRECTION_ENGINE.  
**Evidence branch/commit:** gold-downside-sqrt-hardr-multiorigin-v1-20260922 @ 2926796b6a7e9048d2c091c9c571cb928b773e02.

### 7.7 ME-SQRT-HAR-DR

**Identity:** DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_RESEARCH  
**Role:** measurement-error correction of SQRT-HAR-DR.  
**Source:** Barndorff-Nielsen, Kinnebrock & Shephard realized semivariance; Bollerslev, Patton & Quaedvlieg (2016) HARQ measurement-error mechanism; Taylor (2017) transformed realized-volatility benchmark.  
**Data:** same 5-minute Gold panel.  
**Construction:** downside quarticity proxy RQminus and semideviation measurement-error proxy ME_SD; one added interaction ME_SD_t × SD_t. Coefficient sign not constrained.  
**Result:** bME was negative in every annual origin. R2: 2022 0.2644, 2023 0.5703, 2024 0.2054, 2025 0.0862, 2026 YTD 0.2983. Pooled 2022–2024 MSE improved only about 0.16% and QLIKE about 0.32% versus SQRT; HAC significance was weak. Calibration-slope error did not improve in the required pre-2025 years.  
**Decision:** RETROSPECTIVE_MECHANISM_NOT_SUPPORTED. Keep as a small, theoretically coherent mechanism signal, not as a superior new model.  
**Evidence branch/commit:** gold-downside-me-sqrt-hardr-v1-20260922 @ 1840b9e411b099ab69b8c443663fc6398339c576.

### 7.8 HARK-SD latent-state transfer

**Identity:** DOWNSIDE_HARK_SD_XAU_V1_RESEARCH  
**Role:** test whether latent-state filtering and quarticity-informed measurement uncertainty improve downside-risk forecasts.  
**Source:** Buccheri & Corsi (2021) HARK/SHARK; realized-semivariance asymptotics from Barndorff-Nielsen, Kinnebrock & Shephard.  
**Data:** same 5-minute Gold panel.  
**Construction:** 22-state latent HAR Kalman filter on SD. HARK_SD_CONST uses formation median observation variance; HARK_SD_TV uses causal quarticity-derived time-varying variance.  
**Result:** constant-noise model stayed very close to SQRT-HAR. Time-varying model R2: 2022 0.1925, 2023 0.5751, 2024 0.1778, 2025 0.0533, 2026 YTD 0.1354. Pooled 2022–2024 MSE was about 6.2% worse than SQRT and QLIKE worsened from about 0.1485 to 0.1575; the quarticity-TV model over-filtered genuine risk shocks.  
**Decision:** RETROSPECTIVE_LATENT_STATE_NOT_SUPPORTED. HARK-SD V1 closed in this form.  
**Evidence branch/commit:** gold-downside-hark-sd-v1-20260922 @ 5a138346d450e8b56dd8aae7e98e683d622e2473.

### 7.9 Cross-domain direction bridge family

**Identity:** DOWNSIDE_CROSSDOMAIN_DIRECTION_V1_RESEARCH  
**Role:** distinguish true next-day DOWN from rebound/UP when downside risk is elevated.  
**Source:** cross-domain transfers from biostatistics dynamic binary models, medical competing-risk models, reliability/semi-Markov duration models and robust estimation. Exact single-paper authority was not frozen for every submodel; where absent it remains NOT_PROVEN rather than invented.  
**Data:** same 5-minute Gold panel; four fixed origin-safe features: current close return, log SD, short-run SD acceleration, medium-run SD slope.  
**Construction/results:**

| Submodel | Construction | 2022–2024 pooled BA | Pooled AUC | Decision |
|---|---|---:|---:|---|
| STATIC_LOGIT | fixed-coefficient logistic | about 0.513 | about 0.507 | FAIL |
| DYNAMIC_LOGIT_D99 | causal dynamic logistic, discount 0.99 | about 0.499 | about 0.496 | FAIL |
| COMPETING_RISK_MULTINOMIAL | UP/flat vs normal DOWN vs extreme DOWN softmax | about 0.511 | about 0.518 | FAIL |
| EXPLICIT_DURATION_TRANSITION | risk-state × return-sign × duration with fixed backoff | about 0.511 | about 0.507 | FAIL |
| HUBER_SQRT_HAR | Huber-loss SQRT-HAR risk model, epsilon 1.35 | risk model; pooled MSE about 7.283e-10 vs SQRT 6.875e-10 | QLIKE about 0.1584 vs 0.1485 | FAIL |

The direction models repeatedly returned near chance despite very different architectures.  
**Decision:** RETROSPECTIVE_DIRECTION_BRIDGE_NOT_SUPPORTED and RETROSPECTIVE_ROBUST_RISK_NOT_SUPPORTED. This is the principal evidence for an information-set problem rather than a simple classifier-choice problem.  
**Evidence branch/commit:** gold-downside-crossdomain-direction-v1-20260922 @ 8c7a3b7f4b9c580fc599aa41a50b768358488609.

### 7.10 Meta false-alarm veto

**Identity:** DOWNSIDE_META_FALSE_ALARM_VETO_V1_RESEARCH  
**Role:** second-stage verifier; primary SQRT-HAR-DR alarm is unchanged.  
**Source:** project false-alarm filtering/meta-classification architecture; no single exact external paper authority was frozen.  
**Data:** frozen SQRT-HAR forecast surface plus five Gold-origin features: risk margin, RAW-vs-SQRT disagreement, origin close return, signed semivariance imbalance, risk acceleration.  
**Construction:** ridge logistic C=1.0; STRICT training on prior alarms; CONTEXT on normalized risk >=0.80; P050 and formation-only Recall75 thresholds.  
**Result:** 2024 STRICT P050 AUC 0.657 but retained only 2 of 7 true DOWN cases; Recall75 preserved all 7 but removed no false alarms. In 2025/2026 AUC fell below 0.50 for the main variants; false alarms and true DOWNs were vetoed at similar rates.  
**Decision:** PRE2025_META_VETO_NOT_SUPPORTED. Architecture remains conceptually valid, current Gold scalar features do not resolve alarm correctness.  
**Evidence branch/commit:** gold-downside-meta-veto-v1-20260922 @ c75fc6de33a8b3011f2bdf384d481eb02a59f5f7.

### 7.11 CBR-DTW intraday path morphology

**Identity:** DOWNSIDE_CBR_DTW_PATH_V1_RESEARCH  
**Role:** case-based verifier using the entire completed intraday path shape.  
**Source:** case-based reasoning in fault diagnosis/predictive maintenance, Dynamic Time Warping signal matching, and waveform-morphology false-alarm suppression in medical monitoring. No single exact paper was frozen; source family is recorded as cross-domain methodology.  
**Data:** same 5-minute Gold panel plus frozen primary alarm surface.  
**Construction:** two 48-point channels: RV-normalized cumulative return path and cumulative signed variance-pressure path; multivariate DTW, Sakoe-Chiba band 6, k=3 inverse-distance vote; no hyperparameter search.  
**Result:** 2024 STRICT P050 BA 0.514, AUC 0.557, recall 0.429, so the pre-2025 gate failed. 2025 STRICT P050 was an interesting stress pocket: TP 26, FP 16, recall 0.578, BA 0.611, AUC 0.604; 2026 context AUC was only about 0.535.  
**Decision:** PRE2025_PATH_MORPHOLOGY_NOT_SUPPORTED. Keep path shape as a possible heterogeneous sensor, not a standalone proven verifier.  
**Evidence branch/commit:** gold-downside-cbr-dtw-v1-20260922 @ f187f89c166a75cefa8cf60709dcd4ce1027663d.

### 7.12 S&P 500 cross-market veto

**Identity:** DOWNSIDE_SP500_CROSSMARKET_VETO_V1_RESEARCH  
**Role:** independent external verifier.  
**Source:** safe-haven mechanism hypothesis: severe equity weakness may coincide with flight-to-gold rebound rather than Gold continuation DOWN. Exact single-paper authority was not frozen for this V1.  
**Data:** SP500_FRED daily close aligned causally to Gold origin; plus parent Gold risk margin.  
**Construction:** mechanism-first formation Q10 equity-return veto and a ridge logistic using SP500 1-observation return, 5-observation return, 20-day-vol-normalized return and Gold risk margin.  
**Result:** 2024 logistic P050 AUC 0.657 but BA 0.536 and recall 0.571; the Q10 rule vetoed the wrong single case in 2024. In 2025 logistic AUC fell to 0.477 and did not transport; later stress remained weak.  
**Decision:** PRE2025_CROSSMARKET_VETO_NOT_SUPPORTED. External-sensor idea retained, SP500 alone insufficient.  
**Evidence branch/commit:** gold-downside-sp500-veto-v1-20260922 @ 1af5d5eb37d3c34881c206ff11b295d9099e2b0d.

### 7.13 Heterogeneous consensus veto

**Identity:** DOWNSIDE_HETEROGENEOUS_CONSENSUS_VETO_V1_RESEARCH  
**Role:** combine two heterogeneous weak verifiers without a learned stacker.  
**Source:** safety-system consensus logic applied to the existing CBR-DTW and SP500 V1 verifiers. This architecture was explicitly designed after viewing their results.  
**Data:** frozen Gold path verifier plus frozen SP500 context verifier.  
**Construction:** p_consensus = max(p_path, p_sp); confirm if either verifier supports DOWN; veto only if both reject. Threshold fixed at 0.50.  
**Result:** 2024 exploratory pocket: TP 6, FP 7, FN 1, TN 3, recall 0.857, BA 0.579, AUC 0.743, false alarms reduced 30%. Because the architecture was result-informed, this is not confirmatory. 2025 AUC 0.499/BA 0.522; 2026 AUC 0.567/BA 0.527 with recall 0.689.  
**Decision:** EXPLORATORY_ONLY / NOT_PROMOTED. The heterogeneous-verifier architecture remains a research direction, but current two sensors do not establish a transportable solution.  
**Evidence branch/commit:** gold-downside-consensus-veto-v1-20260922 @ 4f6efce38d636695d44d2fbb3282fa0ec78cc0c2.

---

## 8. Binding scientific interpretation of the downside sequence

The recent sequence does not support a successful general “tomorrow DOWN” model.

The strongest stable conclusion is:

- SQRT-HAR-DR is a useful next-day downside-risk intensity/ranking sensor;
- the transformation from risk alarm to next-day direction remains unresolved;
- multiple very different direction classifiers returned near chance on pre-2025 evidence;
- scalar Gold meta-features did not reliably separate true and false alarms;
- intraday path morphology carries some nonzero information but did not pass the pre-2025 gate;
- SP500 alone did not provide a stable external veto;
- a heterogeneous consensus showed one interesting 2024 exploratory pocket but failed transport;
- therefore the bottleneck is currently treated as missing direction-resolving information and/or target timing, not merely insufficient model complexity.

Binding status:

CURRENT_RECENT_DOWNSIDE_RISK_RESEARCH_REFERENCE = SQRT_HAR_DR  
MANDATORY_COMPARATOR = RAW_HAR_DR  
CURRENT_GENERAL_DOWN_DIRECTION_ENGINE = NOT_PROVEN  
AUTO_SELECTOR = OFF  
AUTO_ENSEMBLE = OFF  
RUNTIME_PROMOTION = NOT_AUTHORIZED

---

## 9. Time-to-event / early-alarm diagnostic V1 — executed and closed

**Identity:** DOWNSIDE_TIME_TO_EVENT_EARLY_ALARM_DIAGNOSTIC_V1_RESEARCH  
**Role:** diagnostic test of whether t+1 false direction interpretations are actually early warnings for downside at t+2/t+3/t+5.  
**Methodological source:** discrete-time survival/time-to-event framing from Suresh, Severn & Ghosh (2022), DOI 10.1186/s12874-022-01679-6; multi-day financial early-warning-window precedent from Gresnigt, Kole & Franses (2015), DOI 10.1016/j.jbankfin.2015.03.003; early-warning prediction-horizon logic from event-level alarm evaluation literature.  
**Data:** frozen annual-origin SQRT-HAR-DR parent forecast panel plus read-only public.xau_intraday_research_cache_5m daily closes reconstructed under the same America/New_York, weekday and >=240-bar retention contract.  
**Preregistration branch:** gold-downside-time-to-event-diagnostic-v1-20260922.  
**Preregistration commit:** 6d7d3394f6edb40d78e66d7892af95fe23311e6f.  
**Frozen result commit:** c5e9f2dd456d2bc66812bc4915fa248d0aee64b0.

### 9.1 Construction

A t+1 false direction interpretation is:
- frozen SQRT high-risk alarm == 1;
- origin-to-t+1 cumulative close return >= 0.

Primary event:
- first origin-anchored cumulative close return < 0 within t+2/t+3/t+5;
- primary diagnostic horizon = t+3.

Severity diagnostics:
- formation-only supervised-history Q25 and Q05 one-day close-return thresholds;
- report whether the minimum origin-anchored cumulative return through the horizon crosses Q25 or Q05.

Primary comparator:
- CONTEXT_CONTROL: non-alarm origins with sqrt_normalized_risk_score >= 0.80 and t+1 return >= 0.

Fallback comparator:
- BROAD_CONTROL: all non-alarm origins with t+1 return >= 0.

No predictive model was fitted.

### 9.2 Integrity checks

- parent panel rows: 1,023;
- retained daily Gold rows: 1,368, 2020-04-06 through 2026-08-31;
- parent target-return versus independently reconstructed daily-return max absolute difference: 3.47e-18;
- supervised formation counts reproduced exactly: 323 / 528 / 731 / 936 / 1173 for 2022–2026;
- independently reconstructed formation Q05 thresholds matched the frozen parent extreme-return thresholds exactly in every year.

### 9.3 Primary 2022–2024 result

Pooled false-t+1 alarm sample:
- ALARM_FALSE_T1 n=16;
- t+2 conversion 31.25%;
- t+3 conversion 37.50%;
- t+5 conversion 43.75%;
- Q25 excursion by t+3 31.25%;
- Q05 excursion by t+3 18.75%.

CONTEXT_CONTROL:
- n=26;
- t+3 conversion 23.08%;
- t+3 absolute conversion lift for alarms +14.42 pp;
- t+3 risk ratio 1.625;
- Q25 excursion lift +15.87 pp;
- Q05 excursion lift +11.06 pp.

However the preregistered minimum pooled CONTEXT_CONTROL support was 30. Actual support was only 26, so the frozen rule required fallback to BROAD_CONTROL.

BROAD_CONTROL:
- n=311;
- t+3 conversion 37.62%;
- alarm-versus-broad t+3 lift -0.12 pp;
- risk ratio 0.997;
- Q25 excursion lift +9.06 pp;
- Q05 excursion lift +14.25 pp.

Annual t+3 context lift was positive in 2022 and 2024, but 2023 had only one false-t+1 alarm and four context controls. Stress results were unstable: 2025 alarm conversion 42.22% versus context 50.0%; 2026 40.54% versus 20.0%.

### 9.4 Decision

**EARLY_ALARM_TIMING_NOT_SUPPORTED**

The V1 gate failed because the intended context comparator was under-supported and the preregistered fallback broad comparator showed essentially identical t+3 sign-conversion probability.

A descriptive severity difference remains: false-t+1 alarms showed more Q25/Q05 adverse excursions than broad controls even though their t+3 sign-conversion rate was not higher. This is retained as anatomy only and does not authorize a result-dependent timing-model rescue.

Therefore:
- do not promote a survival/hazard timing model from V1;
- do not retune horizons, event labels or context thresholds after the result;
- return to genuinely new direction-resolving information channels.


## 10. UP countersign veto V1 — executed and closed for current candidates

**Identity:** DOWNSIDE_UP_COUNTERSIGN_VETO_V1_RESEARCH  
**Role:** test the user's counter-model architecture: when SQRT-HAR-DR raises a downside-risk alarm, suppress the forced-DOWN interpretation if an independently frozen same-horizon direction model says UP. A veto is NO-DOWN/SUPPRESSED, not an UP trading signal.  
**Preregistration branch:** gold-downside-up-counterveto-v1-20260922.  
**Preregistration commit:** 34d69dbee2fc816e2def72ee2033abcd22a839b0.  
**Frozen result commit:** 3c95cc325db5167c386872f42214499f1f688a35.  
**Final status:** UP_COUNTERSIGN_VETO_NOT_SUPPORTED_WITH_CURRENT_ELIGIBLE_MODELS.

### 10.1 Parent baseline

Across 2022–2024 the frozen SQRT-HAR-DR parent issued 30 alarms:
- true next-day DOWN: 14;
- false forced-DOWN / actual UP: 16;
- forced-DOWN precision: 46.67%.

The verifier objective was to remove false forced-DOWN calls while retaining most true DOWN calls.

### 10.2 Eligible candidates and source

**TTSM S1/S2**
- source: Liu, Lu, Li & Wang (2023), Journal of Empirical Finance 72, 54–77, DOI 10.1016/j.jempfin.2023.03.001;
- data/clock: same governed Gold 5-minute panel and same next-trading-day target axis as SQRT;
- veto: TTSM S1 or S2 signal = +1.

**Bonato QBoost**
- source: Bonato, Demirer, Gupta & Pierdzioch (2018), Resources Policy 57:196–212, DOI 10.1016/j.resourpol.2018.03.004;
- data/clock: same governed Gold 5-minute panel and same next-trading-day target axis;
- veto surfaces: h=1 AR1_QBOOST median > 0 and h=1 AR1_RM_QBOOST median > 0.

**Altuntaş AlexNet candle model**
- source: Altuntaş, Okumuş & Kocamaz (2022), DOI 10.53070/bbd.1205299;
- data: Twelve Data provider-day daily OHLC;
- intended veto: frozen pred_up = 1;
- target-axis check failed sufficiently strong equivalence with the SQRT NY-grouped 5-minute daily axis.

Weekly BCTX-AR, VLMC-BS, COVLMC, RealP-CARR and Parisi Rolling-Ward were excluded from V1 because a weekly UP target cannot be carried into a next-trading-day SQRT origin as if it were the same forecast horizon.

### 10.3 Results

**TTSM S1/S2 — clean target axis**
- pre-2025 SQRT alarm overlap: 30;
- both S1 and S2 issued zero UP vetoes on those 30 alarms;
- therefore false-alarm reduction = 0 and precision unchanged;
- 2025 stress: S1 veto precision 55.0%, false-alarm reduction 24.44%, true-DOWN retention 80.0%, remaining precision 51.43%; S2 veto precision 53.33%, false-alarm reduction 17.78%, retention 84.44%, remaining precision 50.67%.
- decision: INSUFFICIENT_VETO_SUPPORT / NOT_PROMISING.

**Bonato AR1 h=1 — clean target axis**
- pre-2025 overlap 19, baseline 8 TP / 11 FP;
- vetoed 7: only 1 good veto and 6 bad vetoes;
- veto precision 14.29%;
- false-alarm reduction 9.09%;
- true-DOWN retention 25.0%;
- remaining DOWN precision fell from 42.11% to 16.67%.
- decision: COUNTERSIGN_VETO_NOT_SUPPORTED.

**Bonato AR1+realized-moments h=1 — clean target axis**
- pre-2025 overlap 19;
- vetoed 6: 1 good, 5 bad;
- veto precision 16.67%;
- false-alarm reduction 9.09%;
- true-DOWN retention 37.5%;
- remaining precision fell from 42.11% to 23.08%.
- decision: COUNTERSIGN_VETO_NOT_SUPPORTED.

**Altuntaş AlexNet**
- parent/candidate recorded next-day actual sign matched only 10/17 = 58.82% on 2024 SQRT-alarm overlap and 69/89 = 77.53% on 2025 stress overlap;
- therefore BLOCKED_TARGET_CLOCK_MISMATCH / NOT_VALID_AS_PARENT_VETO;
- even descriptive 2024 exact-date anatomy retained only 42.86% of true DOWNs after veto.

**Preregistered 2-of-3 family consensus**
- not admissible as decision evidence because it contains the target-clock-misaligned Altuntaş family;
- raw 2024 anatomy had only two vetoes, one good and one bad, and reduced remaining DOWN precision;
- status: INVALID_TARGET_CLOCK_MIX / INSUFFICIENT_VETO_SUPPORT.

### 10.4 Execution integrity note

An interim in-memory Bonato check initially allowed multiple Bonato horizons to share an origin key, so a later h=10 row could overwrite h=1. This was detected before any result artifact was frozen. The final evidence filters horizon==1 before joining, as preregistered, and its actual_return reproduces the SQRT parent target_close_return exactly on overlap. No preregistered rule changed.

### 10.5 Decision and implication

**UP_COUNTERSIGN_VETO_NOT_SUPPORTED_WITH_CURRENT_ELIGIBLE_MODELS**

This does not reject the counter-model architecture itself. It rejects the currently available frozen candidate set as a safe next-day verifier.

The verifier requirement remains:
- same target clock as SQRT;
- genuinely selective UP/rebound information on SQRT alarm days;
- strong false-alarm removal without sacrificing true DOWN alarms;
- no 2025-based tuning.

A successor dedicated UP/rebound verifier requires a new identity and preregistration. Given only 30 pre-2025 parent alarms, fitting a flexible verifier directly on the alarm subset is support-limited; new direction-resolving information or a longer same-clock history is preferred over unconstrained model fitting.


## 11. Direction-resolving verifier priority — current next lane

Priority acquisition/testing order:

1. Gold options skew / volatility surface / put-call asymmetry;
2. Gold futures positioning, volume, open interest or order-flow imbalance;
3. daily origin-safe US real yield;
4. long-history daily DXY / broad USD;
5. liquidity/spread or futures basis;
6. macro-surprise direction at event time.

Procedure: authority/coverage scan first, then a minimum single-sensor falsification test, then only if supported reintroduce a primary-risk + verifier architecture.

---

## 12. Reproducibility and branch lineage for the 22 September sequence

Research evidence is preserved in Git history and the following research heads:

| Experiment | Commit |
|---|---|
| SQRT-HAR-DR multi-origin | 2926796b6a7e9048d2c091c9c571cb928b773e02 |
| ME-SQRT-HAR-DR | 1840b9e411b099ab69b8c443663fc6398339c576 |
| HARK-SD | 5a138346d450e8b56dd8aae7e98e683d622e2473 |
| Cross-domain direction | 8c7a3b7f4b9c580fc599aa41a50b768358488609 |
| Meta false-alarm veto | c75fc6de33a8b3011f2bdf384d481eb02a59f5f7 |
| CBR-DTW path | f187f89c166a75cefa8cf60709dcd4ce1027663d |
| SP500 cross-market veto | 1af5d5eb37d3c34881c206ff11b295d9099e2b0d |
| Heterogeneous consensus veto | 4f6efce38d636695d44d2fbb3282fa0ec78cc0c2 |

The canonical branch does not need duplicate model-summary markdown files when this manifest records the decision and the research branch/commit preserves exact preregistration, code, workflows and raw results.

---

## 13. Retained canonical support documents

The canonical project root should stay lean. These support documents are retained because they serve ongoing data/runtime operations rather than duplicate model conclusions:

- GOLD_CONTROL_DATA_INVENTORY.md
- GOLD_CONTROL_DATA_EVIDENCE_SPINE_CONTRACT_2026-09-03.md
- GOLD_CONTROL_MODEL_DATA_READINESS_CONTRACT_V143_2026-09-07.md
- GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_CONTRACT_V144_2026-09-07.md
- GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md
- GOLD_CONTROL_R4_1_EMITTED_STATE_CONTRACT.md

Technical README/provenance/runbook files inside implementation subdirectories may remain when they explain code operation rather than repeat project-level research conclusions.

---

## 14. Final binding summary

Gold Control currently has a useful downside-risk sensor but no proven general next-day DOWN-direction engine.

SQRT-HAR-DR is the current recent downside-risk research reference. RAW HAR-DR is the mandatory comparator. ME-SQRT shows a small coherent mechanism signal but did not pass its calibration gate. HARK-SD, cross-domain direction classifiers, scalar meta-veto, standalone DTW path veto and standalone SP500 veto did not pass their frozen pre-2025 gates. Heterogeneous consensus produced one exploratory 2024 pocket but did not transport.

The time-to-event V1 diagnostic is closed as EARLY_ALARM_TIMING_NOT_SUPPORTED, and the existing-model UP-countersign veto is also closed as UP_COUNTERSIGN_VETO_NOT_SUPPORTED_WITH_CURRENT_ELIGIBLE_MODELS. The next lane is to obtain or construct a genuinely same-clock direction-resolving verifier. Preferred evidence is new information—beginning with Gold options/futures structure if authoritative long-history data can be obtained—or a newly preregistered daily-horizon UP/rebound expert with sufficient historical support. Do not continue adding unconstrained complexity to the same Gold history or tune on 2025.
