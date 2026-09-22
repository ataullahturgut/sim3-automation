# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 2.04  
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

## 6. UP / upward-direction research ledger — year-by-year performance

This section is the authoritative inventory of tested Gold Control models/engines that can emit UP, represent an upward state, imply an upward direction, or materially qualify an UP/rebound interpretation. Its purpose is to prevent future verifier/veto work from looking only at the newest models.

### 6.1 Reading rules

- Metrics are not directly rank-comparable across different target clocks. Monthly, daily, event-time, multi-day and weekly models remain separated.
- Acc = raw direction accuracy; BA = balanced accuracy; UP sens = sensitivity/recall on actual UP cases; AUC = ranking AUC; DirAgree = the governed FAST/SLOW next-observation direction-agreement diagnostic.
- 2026 means the available retrospective/frozen-OOS window only where the source artifact is partial.
- High raw accuracy with all/near-all UP forecasts is explicitly marked and is not treated as robust UP skill.
- Context engines that do not predict direction by contract remain in the ledger because they were used or discussed in UP/downside architecture; they are marked CONTEXT ONLY.
- Superseded implementations are not duplicated as separate winners. The latest corrected/source-faithful family result carries the family-level conclusion, while superseded versions remain in Git history.
- If a year-specific result is not present in the retained authoritative artifact set, the ledger says NOT_FOUND. No number is reconstructed from memory.

### 6.2 Governed legacy, context and monthly-direction surfaces

| Engine / model | Clock / role | 2023–2024 | 2025 | 2026 available | UP interpretation / decision |
|---|---|---|---|---|---|
| CAUSAL_PATCH | monthly H=1 price expert; implied monthly direction | annual split NOT_FOUND here | direction Acc 83.33% (10/12) | Jan–Jul mature targets: Acc 28.57% (2/7) | monthly price expert; not a next-day UP veto |
| VW_MIDAS_MSVR_SUCCESSOR_V1 | monthly H=1 price expert; implied monthly direction | annual split NOT_FOUND here | direction Acc 75.00% (9/12) | Jan–Jul: 42.86% (3/7) | monthly price expert; not a next-day UP veto |
| MOMENTUM_3M | monthly H=1 price/momentum direction | annual split NOT_FOUND here | direction Acc 91.67% (11/12) | Jan–Jul: 71.43% (5/7) | strong monthly-direction record, but wrong clock for next-day veto |
| RANDOM_WALK | monthly benchmark | — | direction Acc 0% | Jan–Jul 0% | benchmark only |
| MONTHLY_DIRECTION_3M | strategic monthly direction prior | annual split NOT_FOUND | hit rate 58.33% = 7/12 | Jan–Aug cells 62.50% = 5/8 | strategic UP/DOWN context; not next-day classifier |
| FAST | daily tactical trend state; ROBUST_UP / MIXED / ROBUST_DOWN | yearly split NOT_FOUND in retained pilot artifact | DirAgree 47.92%, n=204 | DirAgree 44.68%, n=196 | direct UP-state candidate for future veto tests; validated complementary context |
| SLOW | slower tactical trend state; ROBUST_UP possible | yearly split NOT_FOUND | DirAgree 36.98%, n=204 | DirAgree 45.21%, n=196 | slower UP confirmation/context |
| GVZ_RISK | volatility/risk governor | no direction score by contract | stressed mean next Gold return -0.1095% vs unstressed +0.1910%; panic=3 | stressed -0.0496% vs unstressed +0.0080%; panic=50 | CONTEXT ONLY; never an UP/DOWN predictor by itself |
| EMERGENCY_LEVEL | intramonth alert/context | independent direction label NOT_PROVEN | 77 alert observations across 8 months | 123 alert observations across 8 months | context geometry; no standalone UP accuracy |
| EMERGENCY_REVERSAL | reversal context | independent direction label NOT_PROVEN | 22 alert observations across 3 months | 21 alert observations across 6 months | reversal context; no standalone UP accuracy |
| BOCPD_RETURN_SUCCESSOR_V1 | regime/break context | direction vote forbidden | blocked role validation; risk diagnostic only | blocked by missing monthly input in frozen pilot | CONTEXT ONLY |
| BOCPD B2 baseline R2 | hourly break / abnormal-volatility benchmark | 2024 auxiliary comparison: precision 21.05%, recall 64.71%, F0.5 24.34% | — | — | risk/break benchmark, not UP direction |
| BOCPD B2 adaptive-hazard V5 | hourly adaptive-hazard break model | 2024 auxiliary comparison: precision 23.08%, recall 82.35%, F0.5 26.96% | — | — | better event recall; still not UP direction |
| Macro Event Employment+Inflation specialist | event-time direction | 2023–24: R5 80.49% (33/41), R15 75.61% (31/41), R30 75.61% (31/41) | R5 75.00% (15/20), R15 75.00% (15/20), R30 60.00% (12/20) | R5 88.89% (8/9), R15 77.78% (7/9), R30 77.78% (7/9) | strongest event-time direction specialist; eligible only on event clock |
| Market Shock + Macro Event overlap | event confirmation | — | — | 5/5 direction-concordant overlaps; post-shock continuation 2/5 | confirmation/context, not general UP continuation |

FAST-specific warning audit: the governed full 2025 FAST timeline produced 22 new ROBUST episode onsets. Same-direction abnormal-volatility events occurred strictly within 1/3/5/10 governed days after 1/2/3/5 of those 22 onsets, plus one same-day case. This is timing anatomy only. The old event-conditioned 11/19 number was explicitly withdrawn as a FAST alarm-accuracy claim.

### 6.3 Daily / next-day UP-capable research models

| Model / frozen variant | Metric | 2022 | 2023 | 2024 | 2025 | 2026 | Decision |
|---|---|---:|---:|---:|---:|---:|---|
| V1.49 HS-SDL-DMA 1D outer | Acc / BA | — | — | — | annual split NOT_FOUND | 45.28 / 46.26%, n=159 | NOT_PROVEN |
| V1.49 selected 1D model | Acc / BA | — | — | — | annual split NOT_FOUND | 43.40 / 50.00%, n=159 | NOT_PROVEN |
| V1.50 frozen general 1D candidate | Acc / BA | — | development pre-lock | 2024-H2 52.94 / 53.36%, n=68 | not scored under this identity | — | NOT_ELIGIBLE_FOR_PROSPECTIVE_SHADOW |
| V1.53 RSV/TTSM-S2 specialist | selective Acc | — | 2023–24 pooled 49.35% | pooled with 2023 | 42.86% | NO_SIGNAL | NOT_PROVEN_GENERAL_1D |
| V1.53 moderate-downshock reversal | selective Acc | — | 2023–24 pooled 78.57% | pooled with 2023 | 64.71% | 45.00% | strong formation pocket, failed transport |
| V1.53 Europe-session continuation | selective Acc | — | 2023–24 pooled 56.13% | pooled with 2023 | 53.19% | 49.09% | decayed toward chance |
| V1.53 raw 20-origin momentum | Acc | — | 2023–24 pooled 52.08% | pooled with 2023 | 52.94% | 54.49% | benchmark only |
| TSM | active BA / UP sens | 46.88 / 45.79% | 52.26 / 61.39% | 47.41 / 68.07% | 51.18 / 80.71% | not run | FAIL |
| TTSM-S1 | active BA / UP sens | 52.85 / 56.98% | 52.60 / 57.73% | 47.25 / 56.04% | 53.44 / 82.24% | not run | FAIL |
| TTSM-S2 | active BA / UP sens | 51.55 / 60.00% | 52.44 / 55.91% | 48.20 / 55.42% | 53.07 / 81.55% | not run | FAIL |
| Bonato AR1_QBOOST h=1 | BA / UP sens | — | 46.46 / 78.22% | 49.70 / 77.31% | 52.10 / 92.86% | not run | NO_PROMOTION |
| Bonato AR1_RM_QBOOST h=1 | BA / UP sens | — | 48.81 / 57.43% | 52.93 / 60.50% | 50.90 / 65.71% | not run | NO_PROMOTION |
| Downside RM Logit — AR1_LOGIT | BA / UP sens | — | 49.49 / 95.05% | 49.38 / 94.12% | 51.35 / 98.57% | not run | pre-2025 contribution gate FAIL |
| Downside RM Logit — RV_LOGIT | BA / UP sens | — | 56.71 / 68.32% | 49.48 / 81.51% | 50.00 / 100% | not run | pre-2025 contribution gate FAIL |
| Downside RM Logit — RSK_LOGIT | BA / UP sens | — | 46.96 / 80.20% | 48.19 / 88.24% | 50.43 / 95.71% | not run | pre-2025 contribution gate FAIL |
| Downside RM Logit — RM_LOGIT | BA / UP sens | — | 54.69 / 57.43% | 47.50 / 70.59% | 49.76 / 96.43% | not run | pre-2025 contribution gate FAIL |
| Downside RM Logit — AR1_RM_LOGIT | BA / UP sens | — | 52.71 / 53.47% | 49.35 / 73.11% | 49.92 / 95.71% | not run | pre-2025 contribution gate FAIL |
| Altuntaş AlexNet candle V1 | Acc / BA / UP sens | — | train/dev only | 51.94 / 49.84 / 65.75% | 54.86 / 50.44 / 72.73% | not run | PRE2025_GATE_FAILED |
| V1.63 GOLD_RIDGE 1D | BA | — | — | training history | 48.31% | 49.41% | FAIL |
| V1.63 SESSION_RM_RIDGE 1D | BA | — | — | training history | 52.43% | 52.19% | FAIL |
| V1.63 PRICE_DISCOVERY_HGB 1D | BA | — | — | training history | 51.44% | 47.82% | FAIL |
| V1.63 MACRO_CROSS_RIDGE 1D | BA | — | — | training history | 53.89% | 51.26% | FAIL |
| V1.63 FULL_HGB 1D | BA | — | — | training history | 55.08% | 50.04% | FAIL / unstable |
| V1.69 SESSION_RM direct binary 1D | AUC / Brier skill | — | 2023H2 65.22% / +6.57% | H1 54.70% / -6.68%; Q3 51.49% / +0.90%; Q4 bridge AUC 56.00% | 53.59% / -2.84% | 52.97% / -4.38% | weak ranking signal; no stable probability skill |

Daily interpretation: several models show very high UP sensitivity because they over-predict UP. BA/AUC is therefore kept beside UP sensitivity. No daily general model currently shows stable, strong two-direction performance across years.

### 6.4 Multi-day UP-capable research models

| Model / horizon | 2023–2024 / formation | 2025 | 2026 available | Decision |
|---|---|---|---|---|
| V1.49 selected 3D outer | annual split NOT_FOUND | annual split NOT_FOUND | Acc 48.41%, BA 50.00%, n=157 | NOT_PROVEN |
| V1.54 RF500 H20 | — | Acc 58.51%, BA 49.67% | Acc 45.27%, BA 49.58% | FAIL |
| V1.54 BAG300 H20 | — | Acc 67.22%, BA 59.30% | Acc 44.59%, BA 49.26% | unstable; FAIL |
| V1.54 SGB300 H20 | — | Acc 55.60%, BA 59.86% | Acc 45.27%, BA 48.98% | unstable; FAIL |
| V1.54 LOGIT H20 | — | Acc 55.19%, BA 40.78% | Acc 46.62%, BA 51.24% | FAIL |
| V1.56 LEGACY_RTQ_R126 H20 | formation metric table NOT_FOUND in retained checkpoint | coverage 58.92%; Acc 77.46%; BA 50.00%; 142 UP / 0 DOWN | coverage 72.97%; Acc 70.37%; BA 69.23%; 88 UP / 20 DOWN | strongest normal-day retrospective pocket, but 2025 one-class collapse forbids promotion |
| V1.59 DRIVER_RTQ_R126 H20 | — | coverage 51.45%; Acc 71.77%; BA 49.44%; 123 UP / 1 DOWN | coverage 77.03%; Acc 69.30%; BA 67.59%; 95 UP / 19 DOWN | corrected drivers did not solve transport |
| V1.59 nonlinear meta-trust | — | accepted outputs collapsed to UP; BA 50% | direction Acc about 74%; BA about 70.65% | regime-sensitive; NO_PROMOTION |
| V1.60 final regime selector H20 | 2024 coverage 0% | coverage 0% | coverage 0% | NO_SIGNAL / FAIL |
| V1.61 H5_PD_RM_QB | 2024: coverage 15.42%; Acc 51.28%; BA 46.12%; 35 UP / 4 DOWN | coverage 21.61%; Acc 72.55%; BA 52.22%; 49 UP / 2 DOWN | coverage 14.29%; Acc 43.48%; BA 50.00%; 23 UP / 0 DOWN | NO_PROMOTION |
| V1.63 GOLD_RIDGE 3D | — | BA 52.84% | BA 40.56% | FAIL |
| V1.63 SESSION_RM_RIDGE 3D | — | BA 47.97% | BA 49.33% | FAIL |
| V1.63 PRICE_DISCOVERY_HGB 3D | — | BA 51.42% | BA 45.56% | FAIL |
| V1.63 MACRO_CROSS_RIDGE 3D | — | BA 54.62% | BA 46.56% | FAIL / transport reversal |
| V1.63 FULL_HGB 3D | — | BA 50.90% | BA 48.11% | FAIL |
| V1.64 SESSION_RM LOCAL_ERRMEM 3D | — | BA about 48.46%; Brier 0.25924 | BA 57.00%; MCC 0.1526; 116 UP / 49 DOWN | real 2026 repair, not stable across 2025 |
| V1.66 SESSION_RM RECAL_ONLY 3D | — | robustness condition not met | 2026 Brier 0.25281; AUC 52.27%; BA 51.22% | benchmark/transport gate FAIL |
| V1.66 SESSION_RM FORGET_ONLY 3D | — | robustness condition not met | 2026 Brier 0.25989; AUC 55.38%; BA 52.22% | benchmark/transport gate FAIL |
| V1.68 SESSION_RM GLOBAL 3D | 2024Q4 bridge: Brier 0.24812; AUC 66.15%; BA 60.00% | AUC 39.50% | AUC 52.40% | local-similarity research did not transport |
| V1.68 MACRO_CROSS SIMILAR_K 3D | 2024Q4: Brier 0.34981 vs freq 0.26616; AUC 56.41%; BA 56.67% | AUC 54.93% | AUC 52.09% | discrimination pocket but poor proper-score skill |
| V1.70 PUBLIC_ONLY 3D (COT + GVZ) | pre-2025 bridge FAIL | AUC 61.92%; Brier skill +2.40% | AUC 43.56%; Brier skill -13.01% | 2025 pocket reverses; NO_PROMOTION |
| V1.70 BASE_PLUS_PUBLIC 1D | pre-2025 Q4 bridge AUC 52.44% | AUC 53.37%; Brier skill -7.99% | AUC 48.11%; Brier skill -10.61% | FAIL |
| V1.70 BASE_PLUS_PUBLIC 3D | pre-2025 Q4 bridge AUC 46.67% | AUC 60.03%; Brier skill -6.83% | AUC 42.24%; Brier skill -19.87% | FAIL |

V1.48 HS-SDL-DMA, V1.51 locked-audit general-direction models, V1.55 DMA/DMS, V1.57 break-aware realized-moment quantiles and V1.58 trend-reversal router were executed and retained as negative research steps. Exact year-by-year metric tables for every internal variant are NOT_FOUND in the retained checkpoint set used for this consolidation. Their available canonical conclusions remain NOT_PROVEN / frozen-gate failure; no missing annual number is invented.

### 6.5 Weekly UP-capable direction families

| Model / variant | 2023 | 2024 | 2025 | Decision |
|---|---|---|---|---|
| RSM-26 | Acc/BA 50.00 / 49.70%; UP sens 53.57% | 50.94 / 50.00%; UP sens 100%; 53/0 UP/DOWN | 71.15 / 50.00%; 52/0 UP/DOWN | all-UP collapse; no promotion |
| RSM-52 | 54.55 / 57.47%; UP sens 36.00% | 50.94 / 50.07%; 51/2 | 71.15 / 50.00%; 52/0 | no promotion |
| RSM-104 | insufficient warm-up | 48.89 / 44.50%; UP sens 84.00% | 71.15 / 50.00%; 52/0 | no promotion |
| ERSM-26 | 50.00 / 52.38% | 37.74 / 37.96% | 61.54 / 43.24%; DOWN sens 0 | no promotion |
| ERSM-52 | 45.45 / 52.00% | 39.62 / 39.96% | 63.46 / 44.59%; DOWN sens 0 | no promotion |
| ERSM-104 | insufficient warm-up | 42.22 / 47.50% | 59.62 / 41.89%; DOWN sens 0 | no promotion |
| VLMC-BS-26 V2 | Acc/BA 50.00 / 50.60%; UP sens 42.86% | 56.60 / 56.41%; UP sens 66.67% | 57.69 / 50.45%; UP sens 67.57% | no stable transport |
| VLMC-BS-52 V2 | 51.16 / 51.86%; UP sens 45.83% | 67.92 / 67.81%; UP sens 74.07% | 57.69 / 44.50%; UP sens 75.68% | strong 2024, failed 2025 |
| VLMC-BS-104 V2 | warm-up unavailable | 56.82 / 55.83%; UP sens 66.67% | 61.54 / 55.14%; UP sens 70.27% | best 2025 VLMC member, but no stable winner |
| VLMC Fixed-Share V1 | 60.47 / 61.84%; UP sens 50.00% | 66.04 / 65.95%; UP sens 70.37% | 48.08 / 39.73%; UP sens 59.46% | REJECTED |
| VLMC adaptive meta — Fixed-Share | 60.47 / 61.84% | fair-support 56.82 / 56.67% | 50.00 / 41.08% | failed to stabilize |
| VLMC adaptive meta — fading recent-best | 60.47 / 61.84% | 56.60 / 56.34% | 51.92 / 42.43% | failed |
| COVLMC-X3 | — | Acc 54.55%; BA 50.00%; 44/0 UP/DOWN | Acc 71.15%; BA 50.00%; 52/0 | neutral/all-UP collapse |
| VLMC-C 104 | — | 47.73 / 44.17%; UP sens 83.33% | 71.15 / 50.00%; 52/0 | NO_PROMOTION |
| BCT/CTW-52 | 55.81 / 58.77%; UP sens 33.33% | 49.06 / 48.29%; UP sens 88.89% | 69.23 / 50.00%; 52/0 | stable probabilities, no two-sided edge |
| BCT-AR | development selected through 2023 | 56.60 / 55.84%; UP sens 96.30% | 69.23 / 48.65%; 51/1 | family closed |
| B-CARS-SV | 44.19 / 50.00%; 0/43 UP/DOWN | 47.17 / 47.29%; UP sens 40.74% | 67.31 / 48.61%; 51/1 | NO_PROMOTION |
| RealP-CARR | — | 47.17 / 46.51%; UP sens 81.48% | 61.54 / 44.44%; UP sens 88.89% | family closed |
| Parisi Rolling-Ward V2 | selected 2023 Acc 57.69%; BA 57.04% | 55.77 / 51.80%; UP sens 86.21% | 63.46 / 50.17%; UP sens 88.57% | NO_PROMOTION |

RSM V1 and VLMC-BS V1 remain audit history only because the corrected V2 source constructions supersede their family-level conclusions.

### 6.6 Pure next-day UP-detector ranking — catch UP while minimizing false UP alarms

This ranking is **not** a SQRT-veto ranking. It answers the pure UP-model question:

> Which same-clock next-day model catches actual UP moves well while generating as few false UP alarms as possible?

Primary pre-2025 comparison uses pooled 2023–2024 evidence. The principal trade-off metric is **Youden J = UP recall - false-positive rate (FPR)**, equivalently balanced accuracy after accounting for both actual UP and actual DOWN classes. UP precision is shown separately so a model cannot look good merely by predicting UP almost every day.

| Rank | Model | UP recall | UP precision | False-UP among UP calls | FPR on actual DOWN | Youden J | Balanced acc. | Interpretation |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| **1** | **RV_LOGIT** | **75.45%** | **56.66%** | **43.34%** | 67.55% | **+7.90 pp** | **53.95%** | best pooled 2023–24 catch-vs-false-alarm trade-off in the same-clock daily set |
| **2** | **AR1_RM_LOGIT** | 64.09% | 55.51% | 44.49% | **60.11%** | +3.98 pp | 51.99% | lower recall than RV, somewhat lower FPR |
| **3** | **RM_LOGIT** | 64.55% | 55.47% | 44.53% | 60.64% | +3.91 pp | 51.95% | nearly tied with AR1_RM |
| **4** | **Bonato AR1_RM QBoost h=1** | 59.09% | 54.62% | 45.38% | **57.45%** | +1.64 pp | 50.82% | cleaner/conservative, but misses more UP moves |
| **5** | **TSM** | 65.00% | 54.17% | 45.83% | 64.36% | +0.64 pp | 50.32% | broad UP detector with little net discrimination |
| **6** | **TTSM-S1** | 48.64% | 53.77% | 46.23% | 48.94% | -0.30 pp | 49.85% | selective and lower FPR, but misses too many actual UPs pre-2025 |
| **7** | **TTSM-S2** | 44.55% | 53.55% | 46.45% | **45.21%** | -0.66 pp | 49.67% | lowest FPR among this set, but pre-2025 UP capture is too low to be the best pure UP detector |
| **8** | **AR1_LOGIT** | **94.55%** | 53.61% | 46.39% | **95.74%** | -1.20 pp | 49.40% | catches almost every UP only by calling almost everything UP; not a useful detector |
| **9** | **Bonato AR1 QBoost h=1** | 77.73% | 52.62% | 47.38% | 81.91% | -4.19 pp | UP-biased; false-alarm burden outweighs catch rate |
| **10** | **RSK_LOGIT** | 84.55% | 52.69% | 47.31% | 88.83% | -4.28 pp | strongly UP-biased |

**Altuntaş AlexNet** is excluded from the same-clock ranking because its provider-day target axis is not sufficiently aligned with the governed SQRT/NY daily axis. Its 2024 descriptive metrics are UP recall 65.75%, UP precision 56.47%, FPR 66.07%, BA 49.84%.

### 6.6.1 2025 transport check

The pre-2025 leader **RV_LOGIT does not transport as a selective UP detector**: in 2025 it predicts UP on every evaluated day, producing UP recall 100% but FPR 100% and BA 50%.

TTSM becomes more selective in 2025:
- TTSM-S1: full-timeline UP recall 62.86%, UP precision 62.86%, FPR 53.61%, Youden J +9.25 pp;
- TTSM-S2: full-timeline UP recall 60.00%, UP precision 64.62%, FPR 47.42%, Youden J +12.58 pp.

Bonato AR1_RM in 2025: UP recall 65.71%, UP precision 59.74%, FPR 63.92%, Youden J +1.79 pp.

Therefore the binding conclusion is two-part:

1. **Best pre-2025 pooled pure-UP detector:** RV_LOGIT.
2. **Best 2025 pure-UP trade-off among these frozen daily models:** TTSM-S2.

No single model is yet proven to be the stable best UP detector across 2023–2025. A future UP-engine decision must therefore distinguish **formation leader** from **transport leader** rather than selecting on 2025 alone.

### 6.7 Source and artifact anchors for this ledger

| Research block | Retained evidence anchor |
|---|---|
| Governed monthly/context engines, FAST/SLOW/GVZ/Emergency | data_pipeline/audits/pilot_validation_v145/retrospective_validation_2025_v145.json; frozen_oos_2026_jan_aug_v145.json; role_specific_validation_v145.json |
| FAST full 2025 timeline | GOLD_CONTROL_2025_FAST_FULL_TIMELINE_RESULT_2026-09-15.md |
| V1.50–V1.70 research sequence | GOLD_CONTROL_V150_ROLE_HIERARCHY_DEVELOPMENT_RESULT_2026-09-12.md through GOLD_CONTROL_V170_PUBLIC_POSITIONING_CONTEXT_CHECKPOINT_2026-09-13.md; GOLD_CONTROL_MASTER_FAILURE_AUDIT_V151_V159_2026-09-12.md |
| RSM / ERSM | GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_PRE2025_RESULT_2026-09-18.md; ..._2025_RESULT_2026-09-18.md |
| VLMC family and adaptive meta | GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_PRE2025_RESULT_2026-09-18.md; ..._2025_RESULT_2026-09-18.md; GOLD_CONTROL_DIRECTION_VLMC_ADAPTIVE_META_V1_RESULT_2026-09-19.md |
| BCT/CTW, BCT-AR, B-CARS, RealP-CARR, Parisi | corresponding frozen RESULT files dated 2026-09-18 through 2026-09-21 |
| TTSM | GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_PRE2025_RESULT_2026-09-21.json; ..._RESULT_2026-09-21.md |
| Bonato QBoost | GOLD_CONTROL_DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_PRE2025_RESULT_2026-09-21.json; ..._2025_RESULT_2026-09-21.json |
| Downside realized-moments logit | GOLD_CONTROL_DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_RESULT_2026-09-21.md |
| Altuntaş AlexNet | GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESULT_2026-09-21.md |

### 6.8 What this ledger means for the UP-veto hypothesis

The historical record contains genuine UP-capable surfaces that were omitted from the first narrow UP-countersign veto V1, especially FAST, SLOW, MONTHLY_DIRECTION_3M, monthly implied-direction experts, the event-time Macro specialist and older multi-horizon specialists.

Role and clock remain binding. FAST can be tested directly as a daily-state counter-context. SLOW and Monthly Direction can be tested only as slower confirmation/context. GVZ, BOCPD and Emergency are not independent UP classifiers and may only qualify a veto rule. Macro Event is eligible only on its event-time origins. H5/H20 and weekly models cannot be carried into a next-day SQRT origin as if they predicted the same target.

Therefore section 10's first UP-countersign veto result is not evidence that every historical UP-capable Gold Control engine has been tested against SQRT. It is evidence only for the narrow candidate set explicitly named in that preregistration.

### 6.9 Unresolved historical aliases

The labels BYZD / BZYD / BYDZ were searched in the retained GitHub project history available to this consolidation and were NOT_FOUND as an exact model identity. No performance is assigned to those labels. If a later artifact establishes the exact identity, it must be appended here rather than guessed.

Literature candidates whose source-faithful input panel or exact method remained incomplete stay NOT_IMPLEMENTED/BLOCKED rather than being treated as tested successes.

---
## 6A. UP Expert Router V1 — dynamic class-specific selector

**Identity:** `UP_EXPERT_ROUTER_V1_RESEARCH`  
**Research branch:** `gold-up-expert-router-v1-20260922`  
**Preregistration commit:** `aaad05b7773b021a7485e07aec48332596cca8cb`  
**Frozen result commit:** `c2996600ecafef0d31d708e94536f8f0afb597cf`  
**Status:** `ROUTER_V1_NOT_PROMOTED_2024_PRECISION_GAIN_GATE_FAILED`.

### 6A.1 Purpose and pool

The router implements class-specific dynamic expert selection rather than majority voting. On each daily origin it chooses the most credible currently-active UP expert or abstains.

Frozen same-clock pool:
- TTSM-S2;
- TTSM-S1;
- Bonato AR1_RM QBoost h=1;
- AR1_RM_LOGIT;
- RM_LOGIT.

The competence state uses only matured prior outcomes. Eligibility requires >=30 historical UP calls, historical UP precision >50%, and historical false-UP FPR <50%. Eligible active experts are ranked by a one-sided 90% Wilson lower bound on UP precision; no eligible expert means ABSTAIN.

Alignment across TTSM, Bonato h=1 and realized-moment-logit artifacts is exact on 645 rows: 203 in 2023, 205 in 2024 and 237 in 2025; target-date mismatches=0, actual-sign mismatches=0.

### 6A.2 2023 development benchmark

The 2023-only fixed benchmark selected before 2024 scoring is `RM_LOGIT`.

| Expert | 2023 UP precision | 2023 false-UP FPR |
|---|---:|---:|
| TTSM-S2 | 51.49% | 48.04% |
| TTSM-S1 | 51.85% | 50.98% |
| Bonato AR1_RM h=1 | 48.74% | 59.80% |
| AR1_RM_LOGIT | 52.43% | 48.04% |
| RM_LOGIT | **54.21%** | **48.04%** |

### 6A.3 Frozen 2024 validation

| Metric | Router | Fixed RM_LOGIT |
|---|---:|---:|
| UP outputs | 135 | 149 |
| Coverage | 65.85% | 72.68% |
| True UP / false UP | 77 / 58 | 84 / 65 |
| **UP precision** | **57.04%** | 56.38% |
| **False-UP FPR** | **67.44%** | 75.58% |
| Actual-UP recall | 64.71% | 70.59% |

2024 selected-expert counts:
- RM_LOGIT 64;
- TTSM-S1 55;
- TTSM-S2 14;
- AR1_RM_LOGIT 2;
- Bonato 0.

The router reduced false-UP FPR by **8.14 pp**, but UP precision improved by only **+0.66 pp**. The preregistered promising gate required at least +3 pp precision lift as well as at least -5 pp FPR. Therefore V1 failed the frozen 2024 gate.

### 6A.4 Locked 2025 challenge

Rules remained unchanged and updated only causally from matured prior outcomes.

| Metric | Router | Fixed RM_LOGIT |
|---|---:|---:|
| UP outputs | 137 | 229 |
| Coverage | 57.81% | 96.62% |
| True UP / false UP | 87 / 50 | 135 / 94 |
| **UP precision** | **63.50%** | 58.95% |
| **False-UP FPR** | **51.55%** | 96.91% |
| Actual-UP recall | 62.14% | 96.43% |

2025 router selections:
- TTSM-S2: **109**;
- TTSM-S1: **28**;
- all other experts: **0**.

This is strong descriptive transport evidence that the causal competence layer learned to distrust the broad logit UP states. However 2025 cannot rescue the failed 2024 gate or be used to retune V1.

### 6A.5 Interpretation

V1 is not promoted, but the architecture is not rejected. The selector materially reduced false-UP burden in both 2024 and 2025 and by 2025 routed all UP decisions through TTSM-S1/S2. The missing requirement is a sufficient pre-2025 UP-precision lift.

A successor may investigate a preregistered recency-aware competence or conservative probability-combination layer, but it must not use 2025 to tune thresholds or candidate rules.

---

## 6B. Original 12-engine stack — UP inclusion audit

**Identity:** `LEGACY12_UP_INCLUSION_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-up-legacy12-inclusion-audit-v1-20260922`  
**Preregistration:** `3a3f1344bc7240271d9f7369af91664147b39883`  
**Frozen result:** `9e532260992cca425908f57341876d83152cf015`

The original governed 12-engine stack is:
CAUSAL_PATCH, VW_MIDAS_MSVR_SUCCESSOR_V1, MOMENTUM_3M, RANDOM_WALK, MONTHLY_DIRECTION_3M, FAST, SLOW, MACRO_EVENT_SUCCESSOR_V2, BOCPD_RETURN_SUCCESSOR_V1, EMERGENCY_LEVEL, EMERGENCY_REVERSAL and GVZ_RISK.

Router V1 omitted this legacy layer. That omission is now explicitly corrected: the original 12 must be retained in successor UP architecture in **role-preserving** form, not flattened into equal daily votes.

### 6B.1 Same-clock FAST / SLOW / monthly-direction reconstruction

Frozen FAST, SLOW and MONTHLY_DIRECTION_3M rules were reconstructed on the exact next-day daily-close axis used by TTSM/Bonato/logit models.

| Legacy UP state | 2023 UP precision / false-UP FPR | 2024 | 2025 |
|---|---:|---:|---:|
| FAST ROBUST_UP | 51.89% / 50.00% | 54.84% / 65.12% | 57.80% / 75.26% |
| **SLOW ROBUST_UP** | **54.43% / 35.29%** | 52.25% / 61.63% | 57.06% / 75.26% |
| MONTHLY_DIRECTION_3M UP | 51.88% / 62.75% | 58.05% / **100%** | 57.73% / 95.88% |

SLOW has a genuine 2023 low-false-UP pocket, but it does not transport. FAST gains nominal precision while becoming more permissive. MONTHLY_DIRECTION_3M becomes effectively always-UP in 2024 and therefore cannot be treated as a standalone next-day expert.

### 6B.2 Role-preserving eligibility

- **FAST / SLOW / MONTHLY_DIRECTION_3M:** eligible as causal context/regime inputs to expert competence; not unconditional equal votes.
- **CAUSAL_PATCH / VW_MIDAS_MSVR_SUCCESSOR_V1 / MOMENTUM_3M:** retain as slower monthly H1 strategic priors. Their retained direction accuracies are already listed in section 6.
- **MACRO_EVENT_SUCCESSOR_V2:** retain only on its event-time clock.
- **GVZ_RISK:** retain as risk context only.
- **RANDOM_WALK:** benchmark only.
- **BOCPD_RETURN_SUCCESSOR_V1:** blocked where pre-2025 daily origin state is not retained.
- **EMERGENCY_LEVEL / EMERGENCY_REVERSAL:** context/reversal roles remain NOT_PROVEN as independent next-day UP predictors.

**Binding implication:** Router V1 remains a valid narrow same-clock experiment, but it is incomplete as the full Gold Control UP architecture. A successor router must reintegrate the original 12 in role-preserving form.

---

## 6C. UP Expert Router V2 — original legacy context reintegrated

**Identity:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Research branch:** `gold-up-expert-router-v2-legacy-context-20260922`  
**Preregistration:** `f97dd635664db4506d6f8a622ced762249d3cdfc`  
**Frozen result:** `f4c661731c8888985b82b4bf16eab401184fa76f`  
**Status:** `PROMISING_LEGACY_CONTEXT_ROUTER_V2_PRE2025_GATE_PASSED`.

V2 corrects Router V1's omission of the original legacy layer. Direct daily UP experts remain TTSM-S2, TTSM-S1, Bonato AR1_RM h=1, AR1_RM_LOGIT and RM_LOGIT. The original FAST, SLOW and MONTHLY_DIRECTION_3M states are reintegrated **as competence context, not equal votes**.

Frozen legacy context:
- FAST_UP = ROBUST_UP;
- SLOW_UP = ROBUST_UP;
- MONTHLY_UP = MONTHLY_DIRECTION_3M UP;
- CONSENSUS_UP iff at least 2 of 3 are UP;
- otherwise NON_CONSENSUS_UP.

Each modern expert is ranked from matured historical UP performance in the current legacy context bucket, with frozen global fallback if bucket support is below 30 UP calls.

### 6C.1 Frozen 2024 validation

| Metric | Router V2 | Router V1 | Fixed RM_LOGIT |
|---|---:|---:|---:|
| UP outputs | 42 | 135 | 149 |
| Coverage | **20.49%** | 65.85% | 72.68% |
| True UP / false UP | **26 / 16** | 77 / 58 | 84 / 65 |
| **UP precision** | **61.90%** | 57.04% | 56.38% |
| **False-UP FPR** | **18.60%** | 67.44% | 75.58% |
| Actual-UP recall | 21.85% | 64.71% | 70.59% |

Relative to Router V1:
- UP precision: **+4.87 pp**;
- false-UP FPR: **-48.84 pp**;
- coverage: **-45.37 pp**.

All preregistered 2024 promising-gate conditions passed.

### 6C.2 Locked 2025 transport

| Metric | Router V2 | Router V1 |
|---|---:|---:|
| UP outputs | 37 | 137 |
| Coverage | **15.61%** | 57.81% |
| True UP / false UP | **27 / 10** | 87 / 50 |
| **UP precision** | **72.97%** | 63.50% |
| **False-UP FPR** | **10.31%** | 51.55% |
| Actual-UP recall | 19.29% | 62.14% |

2025 did not tune V2 and cannot alter the pre-2025 decision.

### 6C.3 Interpretation

Reintroducing the original 12-engine legacy direction layer materially changes the UP-verifier result. The gain comes from **selectivity**, not broad direction coverage: Router V2 abstains on most days and emits only a small subset of high-specificity UP calls.

All emitted V2 signals in both 2024 and 2025 occur in the frozen `NON_CONSENSUS_UP` legacy context. This is an empirical routing result, not a causal economic claim.

The original 12-engine work is therefore **not obsolete**. In role-preserving form it materially improves the modern UP router. CAUSAL_PATCH/VW-MIDAS/MOMENTUM remain slower priors, Macro Event remains event-time, GVZ remains risk context, and BOCPD/Emergency retain their blocked/not-proven statuses.

**Next allowed step:** freeze V2 as-is and test its emitted UP calls against SQRT downside alarms in a new preregistered countersign-veto study. No V2 threshold or context rule may change in that intersection test.

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

This does not reject the counter-model architecture itself. Scope correction in v1.98: V1 tested only the preregistered narrow set TTSM, Bonato and Altuntaş plus their fixed family-consensus rule. It did not test the full historical UP/context inventory consolidated in section 6 — notably FAST, SLOW, MONTHLY_DIRECTION_3M, monthly implied-direction experts, Macro Event, GVZ-qualified context or older multi-horizon specialists. It rejects only the preregistered narrow candidate set as a safe next-day verifier.

The verifier requirement remains:
- same target clock as SQRT;
- genuinely selective UP/rebound information on SQRT alarm days;
- strong false-alarm removal without sacrificing true DOWN alarms;
- no 2025-based tuning.

A successor dedicated UP/rebound verifier requires a new identity and preregistration. Given only 30 pre-2025 parent alarms, fitting a flexible verifier directly on the alarm subset is support-limited; new direction-resolving information or a longer same-clock history is preferred over unconstrained model fitting.


### 10.6 V2 expanded historical-UP veto — executed

**Identity:** DOWNSIDE_UP_COUNTERSIGN_VETO_V2_FULLHISTORY_RESEARCH  
**Branch:** gold-downside-up-counterveto-v2-fullhistory-20260922  
**Preregistration commit:** 06276faa56483465eeed135cfdd4fcdbb6ffee99  
**FAST SQRT-clock reconstruction preregistration:** 100feec892d2b23c5d6bdf648eeb5e1210103b40  
**Frozen result commit:** a87ee586a804cee85e3ba6688f2fe74cb764a2d1  
**Final status:** NO_EXISTING_HISTORICAL_UP_ENGINE_SAFELY_CLEANS_SQRT_FALSE_ALARMS_UNDER_V2.

V2 explicitly tested the historical candidates requested after the V1 scope correction:
- FAST ROBUST_UP;
- RV_LOGIT UP;
- RM_LOGIT UP;
- AR1_RM_LOGIT UP;
- TTSM-S1 UP;
- TTSM-S2 UP.

Primary common support is 2023–2024 because all logit/TTSM candidates exist there. The parent baseline on those exact origins is 19 SQRT alarms = 8 true next-day DOWN + 11 false forced-DOWN, baseline forced-DOWN precision 42.11%.

| Candidate | Vetoes | Good / bad veto | False DOWN removed | True DOWN retained | Remaining forced-DOWN precision | Decision |
|---|---:|---:|---:|---:|---:|---|
| TTSM-S1 | 0 | 0 / 0 | 0% | 100% | 42.11% | INSUFFICIENT_ACTION_SUPPORT |
| TTSM-S2 | 0 | 0 / 0 | 0% | 100% | 42.11% | INSUFFICIENT_ACTION_SUPPORT |
| RV_LOGIT | 19 | 11 / 8 | 100% | 0% | none remain | UNSAFE_VETO |
| RM_LOGIT | 19 | 11 / 8 | 100% | 0% | none remain | UNSAFE_VETO |
| AR1_RM_LOGIT | 18 | 10 / 8 | 90.91% | 0% | 0% | UNSAFE_VETO |
| FAST original | 10 | 5 / 5 | 45.45% | 37.50% | 33.33% | BLOCKED_TARGET_CLOCK_MISMATCH |
| FAST SQRT-clock recon | 13 | 6 / 7 | 54.55% | 12.50% | 16.67% | UNSAFE_VETO |

The original FAST clock audit matched parent next target date on only 14/19 primary alarm origins and next-direction sign on 13/19. A separately preregistered reconstruction applied the unchanged SMA20 + two-day persistence FAST rule to the exact SQRT daily-close panel; clock integrity then passed 19/19, but veto performance remained unsafe.

2025 stress, unchanged:
- TTSM-S1: 20 vetoes, 11 good / 9 bad, false-alarm reduction 24.44%, true-DOWN retention 80.00%;
- TTSM-S2: 15 vetoes, 8 good / 7 bad, false-alarm reduction 17.78%, retention 84.44%;
- RV_LOGIT: 90/90 alarms vetoed, retention 0%;
- RM_LOGIT: 88/90 vetoed, retention 4.44%;
- AR1_RM_LOGIT: 86/90 vetoed, retention 6.67%;
- FAST SQRT-clock recon: 59/90 vetoed, retention 31.11%.

2025 cannot retroactively select TTSM because both TTSM variants issued zero UP vetoes on the pre-2025 primary parent-alarm subset.

**Binding interpretation:** no active existing historical UP engine passes the predeclared safety rule of at least 80% true-DOWN retention with useful veto support. Generic UP classifiers/states are not sufficient as a SQRT false-alarm cleaner. The counter-model architecture remains open, but it now requires a deliberately high-specificity UP/rebound verifier or genuinely new direction-resolving information.


### 10.7 SQRT × frozen UP Router V2 countersign veto — executed

**Identity:** `SQRT_UP_ROUTER_V2_COUNTERSIGN_VETO_V1_RESEARCH`  
**Research branch:** `gold-downside-router-v2-countersign-v1-20260922`  
**Preregistration:** `375ceaa0d6a84ecb7a4da6f7dacc72c7a9b66693`  
**Frozen result:** `6d875ca9840eb6f00411e1398a71160d83508bd3`  
**Final status:** `NEAR_MISS_PRE2025_GATE_FAILED_BY_PRECISION_DELTA`.

The already-frozen legacy-context Router V2 was intersected with SQRT alarms without changing any verifier rule.

Exact alignment:
- 2024: 17/17 SQRT alarms matched exact Router target date and next-direction sign;
- 2025: 90/90 matched;
- no target-date or sign mismatches.

#### 10.7.1 Primary 2024

Baseline:
- 17 SQRT alarms;
- 7 true next-day DOWN;
- 10 false forced-DOWN / actual UP;
- forced-DOWN precision = **41.18%**.

Router V2 veto:
- vetoes = **4**;
- good vetoes = **3**;
- bad vetoes = **1**;
- veto precision = **75.00%**;
- false-alarm reduction = **30.00%**;
- true-DOWN retention = **85.71%**;
- remaining forced-DOWN precision = **46.15%**;
- precision improvement = **+4.98 percentage points**;
- net veto benefit = **+2**.

Veto origins:
- 2024-08-06 → actual UP → good veto;
- 2024-11-12 → actual DOWN → bad veto;
- 2024-11-13 → actual UP → good veto;
- 2024-11-25 → actual UP → good veto.

All four were emitted through RM_LOGIT competence inside the frozen NON_CONSENSUS_UP legacy bucket.

Frozen gate:

| Requirement | Observed | Result |
|---|---:|---|
| veto count >=3 | 4 | PASS |
| veto precision >=65% | 75.00% | PASS |
| false-alarm reduction >=25% | 30.00% | PASS |
| true-DOWN retention >=80% | 85.71% | PASS |
| remaining precision gain >=+5.00 pp | **+4.98 pp** | **FAIL** |

The final criterion misses by about **0.02 percentage point**. The preregistered gate is binding and is not relaxed after the result.

#### 10.7.2 Locked 2025 stress

Baseline:
- 90 alarms = 45 true DOWN + 45 false forced-DOWN;
- precision 50.00%.

Unchanged Router V2:
- 16 vetoes;
- 10 good / 6 bad;
- veto precision = **62.50%**;
- false-alarm reduction = **22.22%**;
- true-DOWN retention = **86.67%**;
- remaining forced-DOWN precision = **52.70%**;
- precision gain = **+2.70 pp**;
- net veto benefit = **+4**.

2025 is directionally supportive but cannot rescue the failed 2024 gate.

#### 10.7.3 Binding interpretation

This is the strongest SQRT countersign result in the current sequence. It is the first tested architecture to simultaneously show:
- veto precision materially above chance;
- meaningful false-alarm removal;
- >80% true-DOWN retention;
- improved remaining forced-DOWN precision.

However the formal pre-2025 gate fails by a very small margin and the primary sample is only 17 alarms / 4 vetoes. Therefore the result is **NEAR MISS, NOT PROMOTED**.

The correct next step is to preserve the frozen verifier and obtain more independent same-clock historical evidence / longer parent-alarm support rather than changing the threshold post hoc.


## 11. Direction-resolving verifier priority — current next lane

Priority acquisition/testing order:

1. Gold options skew / volatility surface / put-call asymmetry;
2. Gold futures positioning, volume, open interest or order-flow imbalance;
3. daily origin-safe US real yield;
4. long-history daily DXY / broad USD;
5. liquidity/spread or futures basis;
6. macro-surprise direction at event time.

Procedure: first preserve the V2 finding that generic historical UP states are unsafe or inactive on SQRT alarm days. Next, authority/coverage scan new direction-resolving information or preregister a dedicated high-specificity UP/rebound verifier. Only after a pre-2025 safety gate passes may a primary-risk + verifier architecture be reconsidered.

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

The time-to-event V1 diagnostic is closed as EARLY_ALARM_TIMING_NOT_SUPPORTED. UP-countersign V1 is retained as the narrow TTSM/Bonato/Altuntaş test. V2 then expanded the test to FAST, RV_LOGIT, RM_LOGIT, AR1_RM_LOGIT and TTSM S1/S2 and found NO_EXISTING_HISTORICAL_UP_ENGINE_SAFELY_CLEANS_SQRT_FALSE_ALARMS_UNDER_V2. Section 6 remains the authoritative year-by-year UP inventory. UP Expert Router V1 reduced false-UP burden but failed its 2024 precision-lift gate. The original 12-engine omission was then corrected. Legacy-context Router V2 passed its frozen standalone 2024 gate and transported strongly in 2025 at lower coverage. Its separately preregistered SQRT countersign test is now complete: 2024 produced 4 vetoes, 3 good / 1 bad, 75% veto precision, 30% false-alarm reduction and 85.71% true-DOWN retention. Remaining forced-DOWN precision improved by +4.98 pp, narrowly missing the frozen +5.00 pp gate. Status: NEAR_MISS_PRE2025_GATE_FAILED_BY_PRECISION_DELTA. The next lane is more independent same-clock evidence / longer parent-alarm support, not post-hoc threshold relaxation. Preferred evidence is new information—beginning with Gold options/futures structure if authoritative long-history data can be obtained—or a newly preregistered daily-horizon UP/rebound expert with sufficient historical support. Do not continue adding unconstrained complexity to the same Gold history or tune on 2025.
