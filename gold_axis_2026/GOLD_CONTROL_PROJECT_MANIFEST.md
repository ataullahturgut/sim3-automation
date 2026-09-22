# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 2.19  
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

## 6D. FROZEN UP VERIFIER BASELINE — do not drift

**Frozen identity:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Frozen result commit:** `f4c661731c8888985b82b4bf16eab401184fa76f`  
**Status:** `FROZEN_RESEARCH_BASELINE / PROMISING / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

This is now the authoritative UP-verifier baseline. It must not be silently modified while downstream downside/suppression research continues.

### 6D.1 Frozen direct UP experts

The direct daily expert pool is fixed as:

1. TTSM-S2
2. TTSM-S1
3. Bonato AR1_RM QBoost h=1
4. AR1_RM_LOGIT
5. RM_LOGIT

No expert may be removed, replaced, threshold-shifted or redefined inside this frozen V2 identity.

### 6D.2 Frozen legacy competence context

The original Gold Control layer is fixed in role-preserving form:

- FAST_UP = FAST `ROBUST_UP`;
- SLOW_UP = SLOW `ROBUST_UP`;
- MONTHLY_UP = `MONTHLY_DIRECTION_3M == UP`;
- `CONSENSUS_UP` iff at least 2 of the 3 are UP;
- otherwise `NON_CONSENSUS_UP`.

These legacy states are **context for competence**, not equal votes.

The remaining original engines retain their roles:
- CAUSAL_PATCH / VW_MIDAS_MSVR_SUCCESSOR_V1 / MOMENTUM_3M = slower strategic priors;
- MACRO_EVENT_SUCCESSOR_V2 = event-time specialist;
- GVZ_RISK = risk context only;
- RANDOM_WALK = benchmark;
- BOCPD_RETURN_SUCCESSOR_V1 = blocked where historical daily state is unavailable;
- EMERGENCY_LEVEL / EMERGENCY_REVERSAL = NOT_PROVEN as independent next-day UP predictors.

### 6D.3 Frozen competence rule

For each active direct UP expert:

1. use only matured prior outcomes;
2. use same legacy-context bucket history when that expert has at least 30 historical UP calls in the bucket;
3. otherwise use the frozen global-history fallback;
4. require historical UP calls >=30;
5. require historical UP precision >50%;
6. require historical false-UP FPR <50%;
7. rank eligible active experts by one-sided 90% Wilson lower bound on UP precision;
8. tie-break by lower false-UP FPR, then higher raw UP precision, then fixed identity order:
   TTSM-S2 > TTSM-S1 > Bonato AR1_RM > AR1_RM_LOGIT > RM_LOGIT;
9. if none is eligible, output `ABSTAIN`.

Outputs are only:
- `UP`
- `ABSTAIN`

### 6D.4 Frozen performance reference

Standalone:
- 2024: UP precision **61.90%**, false-UP FPR **18.60%**, coverage **20.49%**;
- locked 2025 transport: UP precision **72.97%**, false-UP FPR **10.31%**, coverage **15.61%**.

SQRT countersign intersection:
- 2024: 4 vetoes = 3 good / 1 bad; veto precision **75.00%**; false-alarm reduction **30.00%**; true-DOWN retention **85.71%**;
- 2025 locked stress: 16 vetoes = 10 good / 6 bad; veto precision **62.50%**; true-DOWN retention **86.67%**.

The 2024 SQRT intersection remains a formal near miss because remaining forced-DOWN precision improved by **+4.98 pp** versus the preregistered **+5.00 pp** requirement. That does not unfreeze or invalidate the UP verifier itself; it means only that the current hard-veto coupling is not promoted.

### 6D.5 Change-control rule

Any future modification to:
- direct expert membership;
- legacy-context definition;
- support threshold;
- precision/FPR eligibility threshold;
- Wilson confidence level;
- ranking/tie-break rule;
- output semantics;

requires a **new router identity (V3 or later), preregistration, and side-by-side comparison against this frozen V2 baseline**.

V2 remains permanently reproducible as the reference UP verifier even if a successor later performs better.

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


## 11. Current next lane — cross-domain risk-controlled dampener

The UP-verifier architecture is frozen in section 6D. The next problem is not restricted to Gold forecasting literature. It is treated as a broader **false-alarm suppression / selective-decision / asymmetric-risk-control** problem.

### 11.1 Cross-domain research scan

The following fields were explicitly scanned because they solve structurally similar problems:

1. **Clinical alarm suppression / ICU monitoring**
   - PhysioNet/CinC Challenge 2015 framed the task as reducing false alarms with minimal or no loss of true vital alarms.
   - Multimodal confirmation and signal-quality fusion are directly analogous to using independent verifier/context evidence against a primary alarm.

2. **Selective classification / reject option**
   - Geifman & El-Yaniv (NeurIPS 2017) and SelectiveNet (ICML 2019) formalize prediction with abstention and the risk-coverage trade-off.
   - This maps naturally to RETAIN / SUPPRESS / ABSTAIN-WATCH rather than forcing a binary veto.

3. **Neyman-Pearson classification**
   - Tong, Feng & Li (Science Advances 2018) formalize minimizing the non-prioritized error while controlling a prioritized error below a user-specified bound.
   - Gold mapping: prioritize BAD_VETO / loss of true DOWN control, then maximize removal of false SQRT DOWN alarms.

4. **Risk-controlling / conformal decision calibration**
   - Bates et al. (JACM 2021) provide distribution-free risk-controlling prediction sets.
   - Angelopoulos et al. (ICLR 2024) extend conformal methods to control expected monotone losses.
   - Angelopoulos et al. (Annals of Applied Statistics 2025) provide Learn-Then-Test calibration for finite-sample risk control without retraining the base predictor.
   - Non-exchangeable conformal risk control (ICLR 2024) explicitly allows relevance weighting under time-series/change-point/distribution-shift settings.

5. **Online distribution-shift adaptation**
   - Gibbs & Candès (NeurIPS 2021) Adaptive Conformal Inference updates reliability under changing distributions.
   - This is relevant only as a later successor because the current project forbids 2025-driven tuning and requires a frozen pre-2025 design.

6. **Learning to defer**
   - Mozannar & Sontag (ICML 2020) and later work formalize a rejector that decides whether the model or another expert should make the decision.
   - Gold mapping: decide whether SQRT or the frozen UP verifier should dominate, rather than averaging them blindly.

7. **Industrial/statistical process monitoring**
   - Control-chart literature emphasizes jointly tracking detection, delay and false alarms rather than accuracy alone.
   - Gold mapping: evaluation must retain false-alarm reduction, true-DOWN retention, decision coverage and latency/availability together.

### 11.2 Selected research abstraction

The strongest cross-domain abstraction for Gold Control is:

**RISK-CONTROLLED SELECTIVE SUPPRESSION CONTROLLER (RCSSC)**

The controller does not retrain SQRT and does not modify frozen UP Router V2.

Inputs may only come from already-frozen evidence surfaces, such as:
- SQRT alarm/risk strength;
- frozen Router V2 UP/ABSTAIN state;
- frozen Router V2 competence/confidence quantities already computed by its selector;
- frozen legacy context state.

Actions should be triaged rather than binary:
- `RETAIN_DOWN`
- `DOWN_WATCH / ATTENUATE`
- `SUPPRESS_DOWN`

Primary design objective:

> maximize removal of false forced-DOWN alarms subject to an explicit upper bound on BAD_VETO / loss of true DOWN alarms.

This is structurally closer to Neyman-Pearson / risk-control / selective-prediction methods than to ordinary classification accuracy optimization.

### 11.3 First successor families to test

The first dampener study should compare, under separate preregistered identities:

1. **NP-constrained suppression**
   - choose suppression only under an explicit true-DOWN-loss constraint;
   - objective is false-alarm removal, not total accuracy.

2. **Risk-controlled selective suppression**
   - calibrate a suppression threshold from frozen SQRT + Router evidence using risk-control / Learn-Then-Test logic;
   - abstain or downgrade when evidence is insufficient.

3. **Non-exchangeable / recency-weighted risk control**
   - only if the static risk-control version is supportable;
   - intended to address regime drift without converting 2025 into a tuning set.

4. **Learning-to-defer style controller**
   - only after transparent constrained methods;
   - learns whether to trust SQRT, Router V2, or abstain, with asymmetric costs.

Deep RL, unconstrained neural gating, fuzzy/Dempster-Shafer fusion and unrestricted ensemble search are lower priority because the current SQRT-alarm sample is small and they add flexibility before the safety constraint is solved.

### 11.4 Critical support limitation

The frozen 2024 SQRT intersection contains only 17 alarms and 4 Router-V2 vetoes. Therefore a statistically sophisticated controller can still be invalid if it is fit directly to those 17 rows.

Binding methodological requirement:
- first prefer transparent threshold/risk-control methods with minimal degrees of freedom;
- preserve chronological / matured-only evidence;
- do not relax the existing 2024 gate after seeing its +4.98 pp near miss;
- seek longer same-clock historical parent-alarm support before fitting a flexible dampener;
- 2025 remains retrospective stress and cannot be used to choose the controller.

### 11.5 Current priority

The next methodological target is **not a new UP predictor**. The frozen Router V2 remains the UP baseline.

Current priority is:
1. establish whether an NP/risk-controlled selective suppressor can be identified without overfitting the small parent-alarm sample;
2. if support is insufficient, extend independent same-clock historical evidence;
3. only then test adaptive/conformal or learning-to-defer successors;
4. only after controller methods are exhausted return to new direction-resolving sensors such as options skew, futures flow, real yields, DXY, basis/liquidity and macro-surprise data.

---

## 11A. NP-constrained suppressor V1 — executed

**Identity:** `NP_CONSTRAINED_SUPPRESSOR_V1_RESEARCH`  
**Research branch:** `gold-np-constrained-suppressor-v1-20260922`  
**Preregistration:** `db782e19fa38fefb1fcace1366fa1d9b937991cf`  
**Frozen result:** `5c2646edcaf18bd386903397594e5efee78b9a2e`  
**Status:** `FORMAL_PASS_BUT_NP_GATE_NON_DISCRIMINATING / NO_INCREMENTAL_OPERATIONAL_GAIN`.

### 11A.1 Design

The frozen Router V2 remains unchanged.

Suppression score:
- selected Router-V2 expert's one-sided 90% Wilson lower bound on historical UP precision;
- Router ABSTAIN = no suppression.

Neyman-Pearson safety target:
- prioritized error = suppress an actual DOWN;
- alpha = **0.20**;
- delta = **0.10**.

2024 daily actual-DOWN calibration support:
- n0 = **86**;
- NP order-statistic index k = **74**;
- binomial tail = **0.098998**;
- threshold `tau = 0.4302662741`.

Operational rule:
- suppress only if SQRT alarms, Router V2 says UP and score > tau.

### 11A.2 2024 calibration diagnostics

All 2024 daily rows:
- actual DOWN = 86;
- suppressed DOWN = 12;
- daily DOWN suppression rate = **13.95%**;
- suppressed UP = 22;
- suppression precision = **64.71%**.

On 17 SQRT alarms:
- suppressions = 4;
- good / bad = 3 / 1;
- suppression precision = **75.00%**;
- false-alarm reduction = **30.00%**;
- true-DOWN retention = **85.71%**;
- remaining forced-DOWN precision = **46.15%**.

These are calibration diagnostics, not independent validation.

### 11A.3 Locked 2025 challenge

Frozen 2024 tau applied unchanged:

- SQRT alarms = 90;
- suppressions = **16**;
- good / bad = **10 / 6**;
- suppression precision = **62.50%**;
- false-alarm reduction = **22.22%**;
- true-DOWN retention = **86.67%**;
- remaining forced-DOWN precision = **52.70%**;
- precision change = **+2.70 pp**.

The full 2025 daily actual-DOWN suppression rate is **10.31%**, descriptively below alpha=20%.

### 11A.4 Binding interpretation

The NP threshold is below every frozen Router-V2 UP score that intersects SQRT alarms in 2024 and 2025. Therefore:

**NP V1 reproduces the existing hard Router-V2 veto exactly.**

It adds the correct asymmetric-risk framing and a formal safety-calibration layer, but it does **not** reduce any additional bad veto or false alarm relative to the hard veto.

Thus NP V1 is not a better operational dampener. The next method should change the action structure, not retrain the UP verifier: a separately preregistered `RETAIN / WATCH / SUPPRESS` selective controller is the preferred next experiment.

---


## 11B. Selective three-action controller V1 — executed

**Identity:** `SELECTIVE_THREE_ACTION_CONTROLLER_V1_RESEARCH`  
**Research branch:** `gold-selective-3action-controller-v1-20260922`  
**Preregistration:** `4d30b9b00b20d8edd14e61c999b2737570c0caf0`  
**Frozen result:** `7e40962c91ca0b7a76650a4deb583bf8d99bbf8f`  
**Status:** `SUPPRESS_SAFETY_FAILED_AND_THREE_ACTION_COLLAPSED`.

### 11B.1 Design

The frozen Router V2 was left unchanged.

The controller used two preregistered NP-style thresholds on the Router selected-expert Wilson lower-bound score:

- WATCH safety target: alpha=0.20, delta=0.10;
- SUPPRESS safety target: alpha=0.10, delta=0.10.

From 2024 actual-DOWN daily calibration rows (n0=86):

- `tau_watch = 0.4302662741`;
- `tau_suppress = 0.4948452868`.

Frozen actions:
- Router ABSTAIN or score <= tau_watch -> RETAIN_DOWN;
- tau_watch < score <= tau_suppress -> WATCH_DOWN;
- score > tau_suppress -> SUPPRESS_DOWN.

### 11B.2 2024 calibration diagnostics

All 205 daily rows:
- RETAIN: 171 = 97 UP / 74 DOWN;
- WATCH: 25 = 17 UP / 8 DOWN;
- SUPPRESS: 9 = 5 UP / 4 DOWN.

On 17 SQRT alarms:
- RETAIN: 13 = 7 UP / 6 DOWN;
- WATCH: 3 = 2 UP / 1 DOWN;
- SUPPRESS: 1 = 1 UP / 0 DOWN.

These are calibration diagnostics only.

### 11B.3 Locked 2025 challenge

All 237 daily rows:
- RETAIN: 200 = 113 UP / 87 DOWN;
- WATCH: **0**;
- SUPPRESS: **37 = 27 UP / 10 DOWN**.

On 90 SQRT alarms:
- RETAIN = 74;
- WATCH = **0**;
- SUPPRESS = **16**;
- good / bad suppressions = **10 / 6**;
- suppression precision = **62.50%**;
- false-alarm reduction = **22.22%**;
- true-DOWN retention = **86.67%**;
- remaining forced-DOWN precision = **52.70%**.

The 16 SUPPRESS actions are exactly the same 16 actions as the frozen hard Router-V2 veto.

### 11B.4 Binding interpretation

The intended middle WATCH region vanished in 2025 because every Router-V2 UP score exceeded the frozen 2024 `tau_suppress`.

The selected expert's Wilson lower confidence bound is **not stable on an absolute scale through time**. Its value can rise as matured support grows, empirical precision changes, or the selected expert changes.

Therefore fixed absolute Wilson-LCB thresholds are not a reliable way to maintain stable RETAIN / WATCH / SUPPRESS semantics across years.

The preregistered SUPPRESS safety gate required true-DOWN retention >=90%; observed 2025 retention was **86.67%**, so the safety gate failed.

**Conclusion:** the three-action idea remains conceptually open, but this static-score implementation is rejected. A successor should calibrate the action/loss risk itself, or use a time-normalized/rank-based confidence measure, rather than thresholding the raw Router Wilson-LCB.

---


## 11C. Selective-controller method audit — correction and parameter-learning scope

**Identity:** `SELECTIVE_CONTROLLER_METHOD_AUDIT_V1`  
**Audit branch:** `gold-selective-controller-method-audit-v1-20260922`  
**Audit commit:** `86e998f49feece984f55b814bd5f347fe46ad123`.

The NP order-statistic arithmetic used in NP Suppressor V1 and Three-Action V1 was independently rechecked and is correct:

- alpha=0.20, delta=0.10, n0=86 -> k=74; tail=0.0989978241; k=73 tail=0.1590683295;
- alpha=0.10, delta=0.10, n0=86 -> k=82; tail=0.0603435146; k=81 tail=0.1288214450.

However two methodological limitations are now binding:

1. **Risk-conditioning mismatch.** V1 thresholds were calibrated on all daily actual-DOWN rows, whereas the operational project safety target is retention conditional on `actual DOWN AND SQRT alarm`. Full-daily NP calibration does not directly guarantee the alarm-conditional error rate.

2. **Absolute Wilson-score drift.** The selected expert's cumulative Wilson lower confidence bound is not a time-stable absolute action score. 2024 Router-UP SQRT-alarm scores were roughly 0.474–0.504; 2025 Router-UP SQRT-alarm scores were all above the frozen 0.494845 SUPPRESS threshold, so WATCH collapsed to zero.

Direct 2024 alarm-conditional NP calibration is support-infeasible:
- only 7 actual-DOWN SQRT alarms exist;
- with delta=0.10, alpha=0.20 requires at least 11 class-0 calibration cases;
- alpha=0.10 requires at least 22;
- with n=7 even the most conservative possible tails are 0.8^7=0.2097152 and 0.9^7=0.4782969, both above 0.10.

Therefore:
- NP Suppressor V1 remains a correct unconditional-risk wrapper but adds no operational gain over hard Router V2;
- Three-Action V1 rejects only the **fixed absolute cumulative-Wilson-threshold implementation**, not the broader RETAIN/WATCH/SUPPRESS concept.

Legitimate successor parameter-learning formulations include:
- fixed-effective-sample / rolling competence;
- exponentially discounted Beta-Binomial competence;
- causal time-normalized confidence percentile/rank;
- direct BAD_SUPPRESSION action-risk calibration;
- alarm-conditional/Mondrian risk control when support is sufficient;
- importance-weighted risk control;
- hierarchical Bayesian partial pooling;
- adaptive/non-exchangeable conformal control.

Any successor requires a new identity and must state explicitly:
- the risk conditioning set;
- how parameters are learned;
- whether memory is cumulative, fixed-window, discounted, ranked, Bayesian or conformal;
- why its confidence/risk scale is transport-stable.

**Current preferred lane:** direct action-risk calibration with a time-stable confidence construction, while keeping frozen Router V2 unchanged and keeping 2025 out of parameter selection.

---


## 11D. Direct action-risk controller V1 — executed

**Identity:** `DIRECT_ACTION_RISK_CONTROLLER_V1_RESEARCH`  
**Research branch:** `gold-direct-action-risk-controller-v1-20260922`  
**Preregistration:** `d5529a3364176de16b61fd79b99ec91b04c8f469`  
**Frozen result:** `94542297ee1e83b2dc75bc6888e6b5b14ce4a8a1`  
**Status:** `NOT_SUPPORTED_AS_ACTION_RISK_SUCCESSOR`.

### 11D.1 Design

Frozen Router V2 remained unchanged.

Two time-stable competence constructions were added downstream:

- **F30:** most recent 30 selected-expert UP calls;
- **D30:** exponentially discounted Beta-Binomial competence with 30-call half-life.

Two separate ridge-logistic BAD_SUPPRESSION models were fit on 2024 daily Router-UP cases using:
- SQRT normalized risk score;
- competence error `1 - competence`;
- L2 lambda=1.0;
- intercept unpenalized;
- no hyperparameter search.

Conservative action risk:
- `p_bad = max(p_bad_F30, p_bad_D30)`.

Actions:
- p_bad <=0.20 -> SUPPRESS
- 0.20<p_bad<=0.35 -> WATCH
- p_bad>0.35 -> RETAIN.

### 11D.2 2024 development

Router-UP daily n=42:
- actual UP=26;
- actual DOWN=16.

Both logistic models converged in 5 Newton iterations.

Training Brier:
- F30=0.2322;
- D30=0.2286.

On 17 SQRT alarms:
- RETAIN=13;
- WATCH=4 = 3 UP / 1 DOWN;
- SUPPRESS=0.

Development only; no independent validation claim.

### 11D.3 Locked 2025 challenge

| Action | Count | Actual UP | Actual DOWN |
|---|---:|---:|---:|
| RETAIN | 77 | 35 | 42 |
| **WATCH** | **8** | **7** | **1** |
| **SUPPRESS** | **5** | **3** | **2** |

SUPPRESS:
- precision **60.00%**;
- false-alarm reduction **6.67%**;
- true-DOWN retention **95.56%**;
- remaining forced-DOWN precision **50.59%**;
- net benefit +1.

Frozen hard-veto benchmark:
- precision 62.50%;
- true-DOWN retention 86.67%;
- remaining precision 52.70%.

The successor gate failed because suppression precision and remaining forced-DOWN precision did not beat the hard-veto benchmark.

### 11D.4 Important positive diagnostic

Unlike Three-Action V1, the WATCH region survived transport:
- WATCH n=8;
- actual UP=7;
- actual DOWN=1;
- descriptive UP rate=87.5%.

This shows that fixed-window / discounted competence solves the raw confidence-scale drift problem and creates a stable middle action.

However WATCH may not be promoted to SUPPRESS post hoc.

### 11D.5 Failure mechanism

Both 2024 ridge-logit models learned a **negative** coefficient on `sqrt_normalized_risk_score`: stronger SQRT risk was associated in development with lower predicted BAD_SUPPRESSION risk.

That sign is not safety-coherent and did not transport reliably. Some strong-SQRT-risk 2025 Router-UP cases were therefore suppressed despite actual DOWN.

**Binding implication:** direct action-risk modeling remains open, but the next formulation should either:
- calibrate the action directly using Learn-Then-Test / risk-control logic, or
- impose monotonicity so stronger SQRT downside-risk evidence cannot reduce estimated BAD_SUPPRESSION risk.

Router V2 remains frozen.

---


## 11E. Monotonic action-risk controller V1 — executed

**Identity:** `MONOTONIC_ACTION_RISK_CONTROLLER_V1_RESEARCH`  
**Research branch:** `gold-monotone-action-risk-controller-v1-20260922`  
**Preregistration:** `a696308de6cc646fc9925ddb34f1299c21ab6609`  
**2024 fit freeze:** `194d9a1fb25f08379c1645089fdd55d079fcdc19`  
**Frozen result:** `3f3fe007da5a563fbedd002abae205152ec36f6c`  
**Status:** `TOO_CONSERVATIVE_INSUFFICIENT_SUPPRESS_SUPPORT`.

### 11E.1 Design

Frozen Router V2, F30 and D30 competence constructions were retained.

Two BAD_SUPPRESSION ridge-logistic models were refit on 2024 Router-UP daily origins with hard monotonicity:

- `beta_sqrt >= 0`;
- `beta_competence_error >= 0`.

The constrained optimum was selected by exact active-set comparison with no hyperparameter search.

### 11E.2 2024 fit result

Development support:
- Router-UP n=42;
- actual DOWN=16;
- actual UP=26.

For both F30 and D30 formulations:
- the unconstrained solution required negative SQRT and negative competence-error slopes;
- fixing either one slope at zero still left the other negative;
- the only feasible monotone solution fixed **both slopes at zero**.

Therefore both models collapsed to the same intercept-only risk:

`p_bad = 16/42 = 0.380952`.

The fit was frozen before reading 2025 challenge outcomes.

### 11E.3 Locked 2025 challenge

Frozen action thresholds:
- p_bad<=0.20 -> SUPPRESS;
- 0.20<p_bad<=0.35 -> WATCH;
- p_bad>0.35 -> RETAIN.

Since 0.380952>0.35, every SQRT alarm is retained.

2025:
- SQRT alarms=90;
- RETAIN=90;
- WATCH=0;
- SUPPRESS=0;
- true-DOWN retention=100%;
- false-alarm reduction=0%;
- remaining forced-DOWN precision=50.00%.

### 11E.4 Binding interpretation

The monotonic constraint correctly removes the safety-incoherent negative-risk slope found in the unconstrained controller, but it reveals that the chosen two-feature 2024 development surface contains no usable monotone signal strong enough to justify suppression.

This is not score drift and should not be repaired by retuning thresholds around the same fit.

**Next clean lane:** Learn-Then-Test / direct risk-control calibration of the suppression action itself rather than another parametric BAD-risk probability model.

Router V2 remains frozen.

---


## 11F. Learn-Then-Test action-risk V1 — support-blocked

**Identity:** `LEARN_THEN_TEST_ACTION_RISK_V1_RESEARCH`  
**Research branch:** `gold-ltt-action-risk-v1-20260922`  
**Preregistration:** `8de202f3cfe2c33eb6abffb7df3d4d656666fb88`  
**Frozen result:** `afb1a4d3d18980d68322d46f3df3393fece70a50`  
**Status:** `BLOCKED_INSUFFICIENT_ALARM_CONDITIONAL_CALIBRATION_SUPPORT`.

### 11F.1 Correct operational risk target

Unlike earlier all-daily safety wrappers, LTT V1 targeted exactly:

`P(SUPPRESS_DOWN | actual DOWN AND SQRT alarm)`

with:
- alpha=0.20;
- delta=0.10;
- equivalent project safety target: true-DOWN retention >=80%.

### 11F.2 Mandatory support feasibility

Before scoring any policy, the preregistered protocol required enough 2024 actual-DOWN SQRT alarms to certify the target even under zero observed bad suppressions.

2024:
- SQRT alarms=17;
- actual-DOWN SQRT alarms=7;
- actual-UP/false forced-DOWN alarms=10.

Best-case exact requirement:

`(1-alpha)^n <= delta`

therefore:

`n_min = ceil(log(0.10)/log(0.80)) = 11`.

Available:
- n=7;
- best possible zero-error tail = `0.8^7 = 0.2097152` >0.10.

Thus no suppression policy can be honestly risk-certified from the available 2024 alarm-conditional support at the frozen alpha/delta levels.

### 11F.3 Binding consequence

Per preregistration:
- no candidate policy was scored;
- no threshold family was selected;
- 2025 was not scored under this identity;
- alpha/delta were not relaxed;
- all-daily risk was not substituted for alarm-conditional risk.

This is a **data-support limitation**, not a negative model-performance result.

**Next clean step:** extend same-clock pre-2025 SQRT + frozen-verifier history until there are at least 11 actual-DOWN calibration alarms; more support is preferable if multiple candidate policies will be tested with multiplicity control.

Router V2 remains frozen.

---


## 11G. Router V2 historical extension V1 — validated

**Identity:** `ROUTER_V2_HISTORICAL_EXTENSION_V1_RESEARCH`  
**Research branch:** `gold-router-v2-historical-extension-v1-20260922`  
**Preregistration:** `2368e8856d12505eff705ebe9556d5fdf5444e55`  
**Frozen result:** `b1570d4abb816a14e62253882c2215b954effb08`  
**Status:** `HISTORICAL_EXTENSION_VALIDATED_SUPPORT_INCREASED_BUT_LTT_NOT_YET_CERTIFIABLE`.

### 11G.1 Reconstruction integrity

Frozen expert definitions were reconstructed directly from the governed 5-minute panel without using 2025.

Source:
- 958 retained weekdays;
- 2020-04-06 through 2024-12-30;
- >=240 five-minute bars/day.

Common expert rows:
- 2021=91;
- 2022=205;
- 2023=203;
- 2024=205.

Reconstruction validation against frozen 2023/2024 artifacts:
- target-date mismatches=0;
- actual-direction mismatches=0;
- TTSM UP-state mismatches=0;
- Bonato AR1_RM h=1 median-UP mismatches=0;
- RM_LOGIT UP mismatches=0;
- AR1_RM_LOGIT UP mismatches=0.

The 2024 Router V2 result is reproduced exactly:
- n=205;
- Router UP=42;
- TP=26;
- FP=16;
- UP precision=61.90%;
- false-UP FPR=18.60%;
- SQRT alarm overlap=4 = 3 actual UP + 1 actual DOWN.

### 11G.2 Historical yearly Router

Using only Y-1 common rows as formation and matured within-year outcomes:

| year | n | Router UP | TP | FP | UP precision | false-UP FPR |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 205 | 22 | 12 | 10 | 54.55% | 10.20% |
| 2023 | 203 | 19 | 5 | 14 | 26.32% | 13.73% |
| 2024 | 205 | 42 | 26 | 16 | 61.90% | 18.60% |

The weak 2023 result is retained; it is not removed post hoc.

### 11G.3 SQRT alarm support

| year | SQRT alarms | actual DOWN | actual UP | Router-UP overlap | good/bad hard veto |
|---|---:|---:|---:|---:|---:|
| 2022 | 11 | 6 | 5 | 0 | 0/0 |
| 2023 | 2 | 1 | 1 | 0 | 0/0 |
| 2024 | 17 | 7 | 10 | 4 | 3/1 |
| **pooled** | **30** | **14** | **16** | **4** | **3/1** |

Thus alarm-conditional actual-DOWN support increases from 7 to **14**.

### 11G.4 LTT implication

The earlier single-policy zero-bad feasibility floor was 11 cases, so raw support now exceeds that floor.

But the frozen hard Router policy has **1 bad suppression among 14 actual-DOWN alarms**.

At alpha=0.20:
- exact one-sided lower-tail p-value = **0.1979121**;
- required delta = 0.10;
- therefore the policy is **not risk-certified**.

With one bad suppression:
- a single-policy test needs at least **18** actual-DOWN alarm cases at alpha=0.20, delta=0.10.

For the previously proposed five-policy Bonferroni family:
- delta per policy=0.02;
- zero bad suppressions require at least **18** actual-DOWN alarms;
- one bad suppression requires at least **27**.

The governed SQRT multi-origin parent begins at 2022 because yearly fitting requires at least 250 formation rows; 2021 does not provide a methodologically equivalent earlier parent origin from the retained 2020 source. Therefore 2022 is the earliest currently defensible same-clock parent year under the frozen construction.

**Binding next step:** do not weaken alpha/delta. Either obtain additional valid historical parent/verifier support from a genuinely longer source, or define one single suppression policy under a new preregistration without selecting it from pooled SQRT outcomes.

Router V2 remains frozen.

---


## 11H. External Dukascopy-derived XAUUSD feature spine — staged

**Identity:** `EXTERNAL_DUKASCOPY_XAUUSD_FEATURE_SPINE_V1_RESEARCH`  
**Research branch:** `gold-external-dukascopy-spine-v1-20260922`  
**Staging/result commit:** `eea308e7099f3aaff810b6e0a62512b119cc0056`  
**Status:** `STAGED_AND_SOURCE_HARMONIZATION_DIAGNOSTIC_PASSED / RESEARCH_ONLY`.

To investigate methodologically valid pre-2022 support, older XAUUSD intraday evidence was staged from a public one-minute bid/ask history mirror whose README identifies Dukascopy as the historical source.

Raw third-party minute files were **not** copied into Gold Control. Only derived daily research features were retained.

### 11H.1 Staged derived data

Construction:
- exact bid/ask timestamp inner join;
- mid close = (bid+ask)/2;
- last close per UTC 5-minute bin;
- America/New_York daily grouping;
- weekday retention with >=240 five-minute bars.

Derived daily fields:
- last mid close;
- 5m bar count;
- realized variance;
- realized third moment;
- downside realized variance;
- positive/negative realized semivariance;
- average/max spread.

Consolidated period:
- 2018-01-01 through 2021-12-31.

Consolidated artifact:
- `gold_axis_2026/external_data/dukascopy_xauusd_mid_5m_daily_features_2018_2021.csv`

Consolidated audit:
- `gold_axis_2026/external_data/dukascopy_xauusd_mid_5m_daily_features_2018_2021_audit.json`

After dropping seven zero-variance holiday rows:
- retained daily rows = **1038**.

Per-segment provenance stores exact source ask/bid blob SHAs and row counts.

### 11H.2 Source harmonization against governed cache

Overlap with `public.xau_intraday_research_cache_5m`:
- common days = **345**;
- 2020-04-06 through 2021-12-30.

Close returns:
- n=344;
- Pearson correlation = **0.9999746**;
- sign agreement = **99.4186%**;
- mean absolute return difference = **0.00004326**.

Levels:
- close correlation = **0.9999991**;
- median external/internal ratio = **0.99999725**.

Realized risk:
- log RV correlation = **0.9981286**;
- log downside-RV correlation = **0.9979377**;
- median RV ratio = **0.9977241**;
- median downside-RV ratio = **0.9955379**.

Top-20% downside-risk state:
- both high = 69;
- external-only high = 1;
- internal-only high = 1;
- neither high = 274;
- state agreement = **99.4203%**.

### 11H.3 Binding authority

The overlap is strong enough to classify this spine as a **credible pre-2022 research-extension candidate**, but it is not silently merged into any frozen governed model.

Any use for 2020/2021 SQRT + Router extension requires a new preregistered research identity, source-boundary sensitivity reporting, and reproduction checks on the overlap period.

Production DB remains unchanged and read-only for this work.

---


## 11I. External Dukascopy pre-2022 SQRT + Router test — executed

**Research branch:** `gold-external-dukascopy-spine-v1-20260922`  
**Harmonization preregistration:** `039960e98489bd098e5e47344cb333b811bfe97c`  
**Single-policy LTT V2 preregistration:** `9a0c98861b6d26890d52dab576038a666492c25a`  
**Harmonization result:** `0cb9a445da28cea5a0f739e2154a31b7d8577d67`  
**Pre-2022 extension result:** `691de95745bf77a96e5b59e0c5ed410839c2f5f8`  
**Single-policy LTT result:** `d513c5672e83923330e67248579cb37645a1b553`  
**Report:** `5ba455da183982bddb07dbce68d8db5fb64a5eeb`.

### 11I.1 Harmonization gate

The external Dukascopy-derived spine passed every preregistered source-harmonization gate against the governed 5-minute cache.

Pooled exact overlap 2020-04-06..2021-12-31:
- governed retained days=345;
- exact common days=345;
- overlap=100%;
- close-return Pearson=**0.9999746**;
- close-return sign agreement=**99.42%**;
- RV Spearman=**0.99753**;
- downside-RV Spearman=**0.99699**;
- mean external/governed RV ratio=**0.99664**;
- mean external/governed downside-RV ratio=**0.99608**;
- top-quintile downside-risk event agreement=**99.42%**.

Year-specific checks remain equally strong:
- 2020 return correlation 0.999958; sign agreement 98.64%; DR Spearman 0.9950;
- 2021 return correlation 0.999993; sign agreement 100%; DR Spearman 0.9968.

Status: `HARMONIZED_FOR_RESEARCH_EXTENSION_NOT_PRODUCTION_AUTHORITY`.

### 11I.2 External SQRT parent

Using the exact frozen SQRT-HAR-DR annual-origin equations:

| year | formation n | test n | SQRT alarms | actual DOWN | actual UP |
|---|---:|---:|---:|---:|---:|
| 2020 | 498 | 260 | **212** | 97 | 115 |
| 2021 | 758 | 258 | **28** | 16 | 12 |

2020 is a severe crisis-regime stress case: the source-specific annual threshold makes SQRT active on **81.5%** of the year.

### 11I.3 External Router reconstruction

Frozen direct experts and legacy-context Router semantics were reconstructed origin-safely:

| year | n | Router UP | TP | FP | UP precision | false-UP FPR |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 260 | **185** | 111 | 74 | **60.00%** | **66.07%** |
| 2021 | 258 | **33** | 19 | 14 | **57.58%** | **11.20%** |

### 11I.4 SQRT × Router intersection

| year | SQRT alarms | Router-UP overlap | good suppress | bad suppress | veto precision | true-DOWN retention |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | **140** | 80 | **60** | 57.14% | **38.14%** |
| 2021 | 28 | **2** | 1 | 1 | 50.00% | **93.75%** |

The 2020 hard-veto coupling is therefore a clear crisis-regime safety failure.

Because source harmonization is near-exact on the governed overlap, this behavior must not be dismissed as a simple external-feed artifact.

### 11I.5 Single-policy LTT V2, pooled 2020–2024

Predeclared fixed policy:
- suppress SQRT forced-DOWN iff frozen Router V2 emits UP.

Pooled:
- SQRT alarms=**270**;
- actual DOWN=**127**;
- actual UP=**143**;
- suppressions=**146**;
- good suppressions=**84**;
- bad suppressions=**62**;
- suppression precision=**57.53%**;
- false-alarm reduction=**58.74%**;
- true-DOWN retention=**51.18%**;
- baseline forced-DOWN precision=**47.04%**;
- remaining forced-DOWN precision=**52.42%**;
- precision gain=**+5.38 pp**.

Exact safety test:
- alpha=0.20;
- delta=0.10;
- n=127 actual-DOWN alarms;
- x=62 bad suppressions;
- exact lower-tail binomial p≈**1.0000**.

Status:
`HARD_ROUTER_POLICY_DECISIVELY_NOT_RISK_CERTIFIED_ON_2020_2024_EXTENSION`.

### 11I.6 Binding interpretation

The larger historical sample resolves the earlier small-n ambiguity.

The frozen Router V2 may still be retained as an UP-verifier research baseline, because its standalone role is not the same as a universal suppression policy.

However the coupling:

`Router V2 UP => delete SQRT DOWN`

is now **rejected as a generally safe controller** across regimes.

The failure is strongly concentrated in 2020, where Router-UP is permissive during an extreme-risk environment and suppresses 60 of 97 true DOWN SQRT alarms.

**Current next lane:** preserve Router V2, but any future dampener must be explicitly regime/risk aware and must prevent extreme/high-SQRT-risk states from inheriting the same suppression semantics as calm regimes. No hard-veto runtime promotion is allowed.

---


## 11J. External-data full method audit V2 — session correction and confirmation

**Identity:** `EXTERNAL_DUKASCOPY_SESSIONMASK_V2_METHOD_AUDIT`  
**Audit branch:** `gold-external-dukascopy-sessionmask-v2-20260922`  
**Preregistration:** `77f6fe1856a3e2349bbf8f8f6e1dfbead7e50202`  
**Corrected consolidated spine commit:** `509c5ffa762f4ea49644b8ffe723ed2591ba52bf`  
**Audit result:** `f28bef02860dcc9f84acaf84d070a033e64aab40`  
**Status:** `METHOD_AND_DATA_AUDIT_PASSED_AFTER_SESSION_CORRECTION; HARD_VETO_FAILURE_CONFIRMED`.

### 11J.1 Audit correction

A real construction mismatch was found after the first external extension:

- external V1 normal days retained 288 five-minute bars;
- the governed internal source has 276 recurring local-time bins;
- the governed source consistently excludes **17:00–17:55 America/New_York**.

This mismatch was corrected from the governed source clock before any further model interpretation.

The correction is methodological, not outcome-tuned.

**Binding authority:** the V1 288-bar external spine is now **SUPERSEDED FOR MODEL USE**. It remains only as an audit/history artifact.

### 11J.2 Corrected V2 spine

The external raw mirrored one-minute bid/ask files were rebuilt as:

- exact bid/ask timestamp inner join;
- mid close;
- last close per 5-minute bin;
- America/New_York conversion;
- local 17:00–17:55 maintenance hour removed;
- weekday daily aggregation;
- zero-variance synthetic holiday rows removed.

Corrected retained panel:
- 2018=260;
- 2019=260;
- 2020=260;
- 2021=258;
- total=**1038**;
- duplicates=0;
- unsorted=0;
- nonfinite/bad rows=0;
- retained zero-RV rows=0;
- bars per retained day=**276 exactly**.

Corrected artifact:
`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`.

### 11J.3 Corrected source harmonization

Against governed 2020-04-06..2021-12-31:
- exact overlap=345/345=100%;
- close-return Pearson=**0.9999746**;
- return-sign agreement=**99.42%**;
- RV Spearman=**0.99753**;
- downside-RV Spearman=**0.99699**;
- mean RV scale ratio external/governed=**0.99664**;
- mean downside-RV scale ratio=**0.99608**;
- top-quintile downside-risk state agreement=**99.42%**.

The harmonization gate passes after correction.

### 11J.4 Frozen SQRT implementation audit

The exact extension implementation was rerun on the governed source and compared to the frozen parent artifact for 2022–2024.

Across **613 rows**:
- target-date mismatches=0;
- SQRT alert mismatches=0;
- next-return sign mismatches=0;
- max absolute SQRT-DR forecast difference=`4.93e-18`;
- max normalized-score difference=`7.82e-14`;
- high-risk-threshold difference=0.

Thus the SQRT parent extension code is numerically equivalent to the frozen governed method.

### 11J.5 Direct-expert / Router method audit

The prior exact reproduction remains binding:
- 2023/2024 TTSM mismatch=0;
- Bonato h=1 median-UP mismatch=0;
- RM_LOGIT mismatch=0;
- AR1_RM_LOGIT mismatch=0;
- target/date and actual-direction mismatches=0;
- frozen 2024 Router n=205 / UP=42 / TP=26 / FP=16 reproduced exactly.

### 11J.6 Corrected pre-2022 rerun

After rebuilding the external spine to the governed 276-bar session, the full 2020/2021 SQRT + Router reconstruction was rerun.

The result is **unchanged**:

| year | SQRT alarms | Router-UP overlap | good suppress | bad suppress | true-DOWN retention |
|---|---:|---:|---:|---:|---:|
| 2020 | 212 | 140 | 80 | **60** | **38.14%** |
| 2021 | 28 | 2 | 1 | 1 | **93.75%** |

Therefore the 2020 crisis-regime failure is **not caused by the discovered session-loading mismatch**.

### 11J.7 Hard-veto safety conclusion after full audit

Pooled 2020–2024 fixed hard-veto policy:
- SQRT alarms=270;
- actual DOWN=127;
- actual UP=143;
- suppressions=146;
- good=84;
- bad=62;
- suppression precision=57.53%;
- empirical BAD_SUPPRESSION rate among true DOWN alarms=**48.82%**;
- true-DOWN retention=**51.18%**;
- false-alarm reduction=58.74%;
- remaining forced-DOWN precision=52.42%.

At alpha=0.20 / delta=0.10, exact one-sided safety p-value≈1.0000.

**Binding conclusion:** after correcting and re-auditing data loading, clock/session construction, SQRT formula implementation and expert/Router reconstruction, there is no current evidence that the 2020 failure is an implementation artifact. The universal hard veto remains rejected.

The frozen UP Router V2 itself remains preserved as an UP-verifier baseline. Any next controller must be explicitly regime/risk aware.

### 11J.8 Provenance limitation

The older raw minute data come from a public GitHub mirror whose README states Dukascopy/`dukascopy-node` provenance. The audit did not independently redownload every minute directly from Dukascopy.

This limitation is mitigated for research by the near-exact overlap with the governed internal source, but external history remains research-only and never production authority.

---



## 11K. Regime-gated selective dampener V1 — preregistered Q80/Q90 reject gate

**Identity:** `REGIME_GATED_SELECTIVE_DAMPENER_V1_RESEARCH`  
**Research branch:** `gold-regime-gated-dampener-v1-20260922`  
**Preregistration:** `19973bd4ecc9a752b869990a6fe78f0f8ca11f73`  
**Frozen result:** `b1f501804c33cf01dc14bb0eebfea2d719911c3e`  
**Status:** `REJECTED_SAFETY`.

### 11K.1 Motivation and frozen rule

The V2 audit confirmed that the universal Router-UP hard veto fails in the 2020 crisis regime and that this failure is not a data/session implementation artifact. The first successor therefore tested a deliberately low-flexibility regime-aware reject option rather than another unconstrained classifier.

For each evaluation year, using only formation rows available by 31 December Y-1:

- `Q80` = the existing frozen nearest-rank 80th-percentile downside-RV threshold;
- `Q90` = a preregistered nearest-rank 90th-percentile downside-RV boundary;
- SQRT alarm with forecast in `[Q80,Q90)` = `HIGH_NON_EXTREME`;
- SQRT alarm with forecast `>=Q90` = `EXTREME`.

Controller:
- Router V2 ABSTAIN -> retain DOWN;
- Router V2 UP + EXTREME -> WATCH and retain DOWN;
- Router V2 UP + HIGH_NON_EXTREME -> suppress DOWN.

No percentile grid search, Router retuning or 2025/2026 policy selection was allowed.

### 11K.2 Integrity reproduction

The first implementation exposed a one-day SLOW completed-week clock discrepancy around Friday-holiday weeks. The audit correctly blocked scoring.

The implementation was corrected to preserve the frozen completed-week availability semantics: a shortened holiday week becomes available at its calendar Friday boundary, not one day early on Thursday.

After correction:
- 2023 FAST/SLOW/MONTHLY UP counts = 106 / 79 / 133 exactly;
- 2024 FAST/SLOW/MONTHLY UP counts = 124 / 111 / 205 exactly;
- 2020 Router UP=185, SQRT overlap=140, good/bad=80/60 exactly;
- 2021 Router UP=33, overlap=2, good/bad=1/1 exactly;
- 2022 Router UP=22, overlap=0 exactly;
- 2023 Router UP=19, overlap=0 exactly;
- 2024 Router UP=42, overlap=4, good/bad=3/1 exactly.

Final integrity errors=0.

### 11K.3 Preregistered V1 result

Year-by-year controller anatomy:

| year | SQRT alarms | suppress | WATCH | good suppress | bad suppress | false-alarm reduction | true-DOWN retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 51 | 89 | 26 | 25 | 22.61% | 74.23% |
| 2021 | 28 | 2 | 0 | 1 | 1 | 8.33% | 93.75% |
| 2022 | 11 | 0 | 0 | 0 | 0 | 0.00% | 100.00% |
| 2023 | 2 | 0 | 0 | 0 | 0 | 0.00% | 100.00% |
| 2024 | 17 | 4 | 0 | 3 | 1 | 30.00% | 85.71% |

Pooled 2020–2024:
- alarms=270;
- actual DOWN=127;
- actual UP=143;
- RETAIN=124;
- WATCH=89;
- SUPPRESS=57;
- good suppressions=30;
- bad suppressions=27;
- suppression precision=52.63%;
- false-alarm reduction=20.98%;
- true-DOWN retention=78.74%;
- baseline forced-DOWN precision=47.04%;
- remaining forced-DOWN precision=46.95%;
- precision change=**-0.09 pp**.

Primary safety diagnostic:
- alpha=0.20;
- delta=0.10;
- bad suppressions=27 of 127 actual-DOWN SQRT alarms;
- exact lower-tail binomial p=**0.68545**;
- exact 90% upper Clopper-Pearson bad-suppression bound=**26.64%**.

Therefore the preregistered safety diagnostic fails.

### 11K.4 Binding interpretation

The individual-risk magnitude gate materially improves true-DOWN retention relative to the rejected universal hard veto (78.74% versus 51.18%), but it does not make suppression safe and it destroys the precision benefit: remaining forced-DOWN precision is slightly below the parent baseline.

The 2020 failure is not confined to only the most extreme SQRT forecasts. Even after the >=Q90 cases are converted to WATCH, the Q80-Q90 band still contains 51 Router-UP suppression opportunities, including 25 actual DOWN cases.

This falsifies the simple hypothesis that one fixed upper SQRT-risk percentile boundary is sufficient to make Router veto authority safe.

Do not tune Q90 post hoc under this identity. The next controller, if pursued, must model **state/regime persistence or conditional competence** rather than only the instantaneous SQRT forecast magnitude. Candidate successor families remain causal crisis-state reject options, Mondrian/hierarchical alarm-conditional risk control, discounted competence with explicit regime conditioning, or non-exchangeable conformal risk control. Any successor requires a new preregistration.

---


## 11L. Persistent risk-state dampener V1 — preregistered causal persistence reject gate

**Identity:** `PERSISTENT_RISK_STATE_DAMPENER_V1_RESEARCH`  
**Research branch:** `gold-persistent-risk-state-dampener-v1-20260922`  
**Preregistration commit:** `58e9eafa6d46952f17861786b6e58abe12b217ce`  
**Implementation commit:** `d5655c28262fcf8e132e0e6c3dac641c92a21a07`  
**Workflow commit:** `ad6c52b32876436dad912db2445343a8d05df13b`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_PERSISTENT_RISK_STATE_DAMPENER_V1_RESULT_2026-09-22.json` (Git blob SHA `6c569b138c59f7e59042a72b3fab78767c6b149a`)  
**Status:** `RETROSPECTIVELY_PROMISING_NOT_CERTIFIED`.

### 11L.1 Motivation and frozen state rule

The Q80/Q90 instantaneous-magnitude gate failed, so this successor did not retune Q90 or search another forecast-magnitude boundary. It tested whether Router-UP suppression should lose authority when downside risk has remained abnormally elevated across recent completed days.

For each evaluation year, the existing parent `Q80_Y` downside-RV threshold remains frozen from formation data available by 31 December Y-1.

At each forecast origin:
- take the latest 20 completed daily downside-realized-variance observations, ending at and including the origin day;
- count how many satisfy `DR >= Q80_Y`;
- `PERSISTENT_HIGH` iff that count is at least 9;
- otherwise `NON_PERSISTENT`;
- insufficient 20-day history would deny suppression authority.

The cutoff is analytical, not outcome-searched. Under the Q80 nominal exceedance probability p0=0.20, K=9 is the smallest integer with `P[Binomial(20,0.20)>=K] <= 0.01`:
- tail at K=9 = **0.0099817863**;
- tail at K=8 = **0.0321426631**.

Controller:
- Router ABSTAIN -> retain DOWN;
- Router UP + PERSISTENT_HIGH -> WATCH and retain DOWN;
- Router UP + NON_PERSISTENT -> suppress DOWN.

No 2025/2026 tuning, no alternate lookback/cutoff search and no production writes were allowed.

### 11L.2 Integrity gate

All predecessor reconstruction checks passed with zero integrity errors.

Frozen parent/Router intersections reproduced exactly:
- 2020: 212 SQRT alarms; Router UP total=185; overlap=140; good/bad universal-veto cases=80/60;
- 2021: 28 alarms; Router UP=33; overlap=2; good/bad=1/1;
- 2022: 11 alarms; Router UP=22; overlap=0;
- 2023: 2 alarms; Router UP=19; overlap=0;
- 2024: 17 alarms; Router UP=42; overlap=4; good/bad=3/1.

The corrected legacy-context counts also reproduced exactly:
- 2023 FAST/SLOW/MONTHLY=106/79/133;
- 2024 FAST/SLOW/MONTHLY=124/111/205.

### 11L.3 Preregistered result

| year | alarms | persistent alarms | suppress | WATCH | good suppress | bad suppress | false-alarm reduction | true-DOWN retention |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 199 | 3 | 137 | 3 | 0 | 2.61% | 100.00% |
| 2021 | 28 | 18 | 1 | 1 | 0 | 1 | 0.00% | 93.75% |
| 2022 | 11 | 4 | 0 | 0 | 0 | 0 | 0.00% | 100.00% |
| 2023 | 2 | 0 | 0 | 0 | 0 | 0 | 0.00% | 100.00% |
| 2024 | 17 | 8 | 4 | 0 | 3 | 1 | 30.00% | 85.71% |

Pooled 2020–2024:
- SQRT alarms=270;
- actual DOWN=127;
- actual UP=143;
- persistent alarms=229;
- non-persistent alarms=41;
- RETAIN=124;
- WATCH=138;
- SUPPRESS=8;
- good suppressions=6;
- bad suppressions=2;
- bad-suppression rate among actual DOWN alarms=**1.57%**;
- suppression precision=**75.00%**;
- false-alarm reduction=**4.20%**;
- true-DOWN retention=**98.43%**;
- baseline forced-DOWN precision=47.04%;
- remaining forced-DOWN precision=47.71%;
- precision change=**+0.67 pp**.

Primary exact safety diagnostic:
- alpha=0.20;
- delta=0.10;
- n=127 actual-DOWN alarms;
- x=2 bad suppressions;
- exact lower-tail binomial p=**2.624e-10**;
- exact 90% Clopper-Pearson upper bad-suppression bound=**4.14%**;
- retrospective safety diagnostic=**PASS**.

For comparison:
- rejected universal Router veto suppressed 146 alarms, including 62 true DOWN; true-DOWN retention=51.18%;
- rejected Q80/Q90 gate suppressed 57 alarms, including 27 true DOWN; true-DOWN retention=78.74%;
- persistent-state V1 suppresses only 8 alarms, including 2 true DOWN; true-DOWN retention=98.43%.

### 11L.4 Binding interpretation

This is the first preregistered successor in this sequence to pass the frozen pooled historical safety diagnostic. The main scientific finding is that **risk persistence is materially informative for veto safety**: 229 of 270 SQRT alarms are classified persistent, and 138 of the 146 Router-UP/SQRT overlaps occur inside that persistent state. In 2020 specifically, 199 of 212 SQRT alarms are persistent; the gate converts 137 Router-UP conflicts to WATCH and permits only three suppressions, all three of which are false alarms.

However the controller is deliberately very conservative. It removes only 6 of 143 false parent alarms (4.20%) and improves remaining forced-DOWN precision by only +0.67 pp. Therefore the historical safety problem is substantially controlled, but the practical false-alarm-cleaning problem is **not yet solved**.

The preregistered status remains `RETROSPECTIVELY_PROMISING_NOT_CERTIFIED`, not a promotion decision. The hypothesis was created after prior historical failures were visible, so the tiny p-value is a retrospective diagnostic and must not be interpreted as prospective certification.

Do not tune N=20, K=9 or the 0.01 persistence boundary post hoc under this identity. Freeze this model as the current **safety-reference dampener**. Any successor intended to recover useful suppression coverage must use a new preregistration, preferably alarm-conditional / within-regime Router competence or hierarchical/non-exchangeable risk control. 2025 may only serve as retrospective locked transport and may not be used for parameter selection; genuine certification requires new prospective or otherwise independent same-clock evidence.

---


## 11M. Persistent conditional-competence dampener V1 — causal within-cell authority recovery

**Identity:** `PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_RESEARCH`  
**Research branch:** `gold-conditional-competence-dampener-v1-20260922`  
**Preregistration commit:** `968959dcfa645581c9454877f05791c312c05b66`  
**Implementation commit:** `4b23ca1fcec2764711ef011feb6155307de4b5c9`  
**Workflow commit:** `19fdfb1fcaca65ce763da887b8d40a822fb8d8e4`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_RESULT_2026-09-22.json` (Git blob SHA `3d8dc00fc32ec8fe733689da81973c9624c1b503`)  
**Status:** `RETROSPECTIVE_UTILITY_GAIN_NOT_CERTIFIED`.

### 11M.1 Motivation and frozen rule

The N20/K9 persistence gate created a strong safety reference but was too conservative: only 8 suppressions, 6 good / 2 bad, 4.20% false-alarm reduction and 98.43% true-DOWN retention.

This successor kept that persistence definition unchanged and tested whether suppression authority could be restored inside `PERSISTENT_HIGH` only when the exact Router cell demonstrated sufficient causal competence.

Frozen cell:
`(selected_expert, legacy_bucket)`.

For a persistent SQRT alarm where Router V2 emits UP, the cell history contains only earlier matured rows that are:
- SQRT alarms;
- Router-UP;
- `PERSISTENT_HIGH`;
- same selected expert;
- same legacy bucket;
- target outcome matured by the current forecast origin.

No global fallback or neighboring-cell pooling was allowed.

Persistent-state suppression authority required:
- same-cell matured n >= 30, reusing frozen Router V2's competence floor;
- one-sided 90% Wilson lower confidence bound for UP precision > 0.50, using the same z=1.2815515655446004 convention.

Non-persistent Router-UP behavior remained unchanged from the safety reference: suppress.

### 11M.2 Integrity gate

All frozen parent, Router, common-row and legacy-context reconstruction checks passed with zero integrity errors.

The frozen persistence reference was also reproduced exactly:
- alarms=270;
- suppressions=8;
- good=6;
- bad=2.

No 2025/2026 data entered policy definition or scoring; governed DB access remained read-only.

### 11M.3 Preregistered result

| year | alarms | suppress | WATCH | good suppress | bad suppress | false-alarm reduction | true-DOWN retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 37 | 103 | 21 | 16 | 18.26% | 83.51% |
| 2021 | 28 | 1 | 1 | 0 | 1 | 0.00% | 93.75% |
| 2022 | 11 | 0 | 0 | 0 | 0 | 0.00% | 100.00% |
| 2023 | 2 | 0 | 0 | 0 | 0 | 0.00% | 100.00% |
| 2024 | 17 | 4 | 0 | 3 | 1 | 30.00% | 85.71% |

Pooled 2020–2024:
- alarms=270;
- actual DOWN=127;
- actual UP=143;
- RETAIN=124;
- WATCH=104;
- SUPPRESS=42;
- good suppressions=24;
- bad suppressions=18;
- empirical bad-suppression rate among actual DOWN alarms=**14.17%**;
- suppression precision=**57.14%**;
- false-alarm reduction=**16.78%**;
- true-DOWN retention=**85.83%**;
- baseline forced-DOWN precision=47.04%;
- remaining forced-DOWN precision=47.81%;
- precision change=**+0.77 pp**.

Relative to the frozen persistence safety reference:
- +34 additional suppressions;
- +18 additional good suppressions;
- +16 additional bad suppressions;
- no previously permitted non-persistent suppression was removed.

Primary exact safety diagnostic:
- alpha=0.20;
- delta=0.10;
- n=127 actual-DOWN alarms;
- x=18 bad suppressions;
- exact lower-tail p=**0.05864**;
- exact 90% Clopper-Pearson upper bad-suppression bound=**18.97%**;
- retrospective safety diagnostic=**PASS**, but with materially less safety margin than the persistence-only reference.

### 11M.4 Competence anatomy

Only one persistent cell obtained suppression authority:

`BONATO_AR1_RM_QBOOST_H1 | NON_CONSENSUS_UP`.

Across the full persistent sample this cell contains:
- 77 Router-UP cases;
- 44 actual UP;
- 33 actual DOWN;
- 34 causally authorized suppressions;
- 18 authorized good;
- 16 authorized bad.

Authority first becomes available after enough matured evidence accumulates and the Wilson LCB rises above 0.50. The rule remains active through a late-2020 interval while cumulative cell precision deteriorates, then loses authority once the confidence bound falls back below the threshold.

Other persistent cells never qualified:
- TTSM_S2 | CONSENSUS_UP: 50 cases; max decision-time LCB < 0.50;
- RM_LOGIT | NON_CONSENSUS_UP: only 7 cases;
- TTSM_S2 | NON_CONSENSUS_UP: only 3 cases;
- AR1_RM_LOGIT | NON_CONSENSUS_UP: only 1 case.

### 11M.5 Binding interpretation

Conditional competence recovers a meaningful amount of utility relative to the persistence-only safety reference: false-alarm reduction rises from 4.20% to 16.78% and good suppressions rise from 6 to 24.

However the recovered utility is expensive. True-DOWN retention falls from 98.43% to 85.83%, 18 true DOWN alarms are suppressed, and the exact 90% upper bad-suppression bound rises to 18.97%, only narrowly below the frozen 20% risk limit. The +0.77 pp remaining-precision gain is small relative to the added safety burden.

The central methodological finding is therefore not that a static competence threshold solves the controller. Rather, the persistent Bonato/non-consensus cell shows **time-varying competence**: expanding-history confidence can authorize the cell during a favorable run and react too slowly when its error rate worsens.

Freeze this V1 result. Do not tune n=30, the 90% Wilson level, the 0.50 threshold, cell definition, or persistence N/K post hoc under the same identity.

The next lane should explicitly address competence non-stationarity while preserving causal safety: a newly preregistered discounted/recency-weighted competence controller, sequential change-detection reject gate, or non-exchangeable/hierarchical risk-control method. The objective is to retain more of the 16.78% false-alarm reduction without allowing the risk bound to drift toward the 20% ceiling. 2025 remains unavailable for parameter selection; genuine certification still requires independent/prospective same-clock evidence.

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

SQRT-HAR-DR remains the current recent downside-risk research reference. RAW HAR-DR remains the mandatory comparator. ME-SQRT shows a small coherent mechanism signal but did not pass its calibration gate. HARK-SD, cross-domain direction classifiers, scalar meta-veto, standalone DTW path veto and standalone SP500 veto did not pass their frozen pre-2025 gates. Heterogeneous consensus produced one exploratory 2024 pocket but did not transport.

UP Expert Router V2 remains frozen as an UP-verifier baseline, but its universal coupling to SQRT remains rejected. The audited hard veto suppresses 62 of 127 actual-DOWN alarms and retains only 51.18% of true DOWN events. The instantaneous Q80/Q90 successor also fails safety, with 27 bad suppressions and 78.74% true-DOWN retention.

PERSISTENT_RISK_STATE_DAMPENER_V1 then established that regime persistence is a critical safety variable. It passes the frozen retrospective safety diagnostic with only 2 bad suppressions, a 4.14% exact 90% upper risk bound and 98.43% true-DOWN retention, but removes only 4.20% of false alarms. It is the current high-safety reference.

PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1 restores some suppression authority inside persistent regimes using causal same-cell competence. It raises false-alarm reduction to 16.78% and good suppressions from 6 to 24 while still passing the frozen alpha=0.20/delta=0.10 retrospective diagnostic. However it also raises bad suppressions to 18, lowers true-DOWN retention to 85.83%, and pushes the exact 90% upper bad-suppression bound to 18.97%, close to the 20% limit. The utility gain is therefore real but the safety margin becomes thin.

The active research question is now **competence non-stationarity**, not whether persistence matters. The Bonato/non-consensus persistent cell gains authority during a favorable 2020 run and loses quality faster than expanding-history confidence reacts. The next successor, if pursued, must be newly preregistered and explicitly time-adaptive—discounted/recency-weighted competence, sequential change detection, or non-exchangeable/hierarchical risk control—while keeping the frozen persistence insight as the safety backbone. No post-hoc threshold tuning is allowed under the completed identities. 2025 remains unavailable for parameter selection and may only be used as locked retrospective transport; genuine certification requires new prospective or otherwise independent same-clock evidence.
