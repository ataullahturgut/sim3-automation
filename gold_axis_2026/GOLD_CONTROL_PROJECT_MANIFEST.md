# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 2.34  
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


## 11N. SQRT alarm semantic audit V1 — risk versus direction disentanglement

**Identity:** `SQRT_ALARM_SEMANTIC_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-sqrt-semantic-audit-v1-20260922`  
**Preregistration commit:** `3fdc15cde48b8392d21b3de469c6f03b2d50bb57`  
**Implementation commit:** `ad0fc4dcbe1687833bd9a153cd4bc6a754523464`  
**Workflow commit:** `b9695d7d16dc5cc593b03b6862e8f39f81b41c6e`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_SQRT_ALARM_SEMANTIC_AUDIT_V1_RESULT_2026-09-22.json` (Git blob SHA `15a8365baa6be905bdc06e6b7768281e2d246fc7`)  
**Status:** `DIRECTION_FALSE_ALARM_LABEL_CONFOUNDS_RISK_AND_DIRECTION`.

### 11N.1 Audit question and frozen semantics

The audit tested whether the project had been incorrectly calling an SQRT alarm "false" merely because the next-day close direction ended UP.

The parent SQRT-HAR-DR target is next-day downside realized variance, not next-day close direction.

For each evaluation year Y:
- forecast high risk = frozen SQRT forecast `>= Q80_Y`;
- realized high risk = realized target-day downside realized variance `>= Q80_Y`;
- direction = sign of next-day close-to-close log return.

The same already-frozen annual Q80 boundary was used for forecast and realized risk. No alternative threshold was searched.

Alarm rows were partitioned into:
- `RISK_HIT_DOWN_CLOSE`;
- `RISK_HIT_UP_CLOSE`;
- `RISK_MISS_DOWN_CLOSE`;
- `RISK_MISS_UP_CLOSE`.

The audit does not claim chronological intraday "rebound" timing because that path ordering was not separately proven; `RISK_HIT_UP_CLOSE` means high downside-risk realized even though the day closed UP.

### 11N.2 Integrity

Frozen alarm counts reproduced exactly:
- 2020=212;
- 2021=28;
- 2022=11;
- 2023=2;
- 2024=17;
- pooled=270.

Frozen pooled alarm direction counts reproduced exactly:
- actual DOWN=127;
- actual UP=143.

Integrity errors=0.

### 11N.3 Four-way alarm anatomy

| year | alarms | risk hit + DOWN close | risk hit + UP close | risk miss + DOWN close | risk miss + UP close | risk-hit rate among alarms | share of UP-close alarms that were risk hits |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 89 | 91 | 8 | 24 | 84.91% | 79.13% |
| 2021 | 28 | 15 | 5 | 1 | 7 | 71.43% | 41.67% |
| 2022 | 11 | 4 | 5 | 2 | 0 | 81.82% | 100.00% |
| 2023 | 2 | 1 | 0 | 0 | 1 | 50.00% | 0.00% |
| 2024 | 17 | 6 | 2 | 1 | 8 | 47.06% | 20.00% |

Pooled 2020–2024:
- alarms=270;
- `RISK_HIT_DOWN_CLOSE`=115;
- `RISK_HIT_UP_CLOSE`=103;
- `RISK_MISS_DOWN_CLOSE`=12;
- `RISK_MISS_UP_CLOSE`=40;
- realized-risk hits among alarms=218/270=**80.74%**;
- realized-risk misses among alarms=52/270=19.26%.

Critically, among the 143 SQRT alarm days whose next-day close direction was UP:
- 103 were nevertheless realized high downside-risk days;
- only 40 were realized-risk misses;
- therefore **72.03% of the UP-close alarms were actual risk hits**.

Among the 127 DOWN-close alarm days:
- 115 were realized-risk hits;
- 12 were realized-risk misses;
- risk-hit share=90.55%.

### 11N.4 Full-parent risk-state diagnostics

Across all 1,131 evaluated parent rows from 2020–2024:
- realized high-risk targets=319;
- SQRT risk alarms=270;
- true high-risk positives=218;
- false high-risk positives=52;
- false negatives=101;
- true negatives=760;
- risk precision=**80.74%**;
- risk recall=**68.34%**;
- risk specificity=**93.60%**.

Year heterogeneity is material:
- 2020: risk precision 84.91%, recall 93.26%;
- 2021: precision 71.43%, recall 40.82%;
- 2022: precision 81.82%, recall 25.71%;
- 2023: precision 50.00%, recall 11.11% (only two alarms);
- 2024: precision 47.06%, recall 24.24%.

Thus the parent risk sensor is not uniformly calibrated across regimes, but the pooled semantic result is unequivocal: close-direction disagreement does not imply risk-forecast failure.

### 11N.5 Binding architecture correction

The prior phrase "SQRT false alarm" must no longer mean "SQRT alarm followed by an UP close."

That label confounds two separate tasks:
1. downside-risk-state forecasting;
2. next-day close-direction / resolution forecasting.

Of 143 historical UP-close SQRT alarms, 103 (72.03%) were genuine realized high-risk hits under the parent model's own frozen Q80 semantics. Any suppressor that deletes these alarms merely because direction later closes UP is deleting many correct risk warnings.

Therefore the completed hard-veto, persistence and conditional-competence experiments remain valuable diagnostic evidence about direction-resolution logic, but their "false-alarm cleaning" interpretation must be narrowed. They should not be treated as attempts to improve SQRT risk precision by deleting all UP-close cases.

The architecture must now separate:
- **risk state:** normal risk versus high downside risk;
- **conditional resolution:** within high-risk forecasts, DOWN-close / UP-close / uncertain.

The next research lane should not continue threshold tuning on suppression. It should first define and preregister a conditional outcome model for the high-risk subset, with an explicit abstain/uncertain state. Router V2 becomes one candidate feature or benchmark for that second-stage conditional-resolution problem, not a universal alarm deletion authority.

No production/runtime promotion is authorized.

---


## 11O. High-risk hurdle resolution V1 — first selective conditional-resolution probe

**Identity:** `HIGH_RISK_HURDLE_RESOLUTION_V1_RESEARCH`  
**Research branch:** `gold-high-risk-hurdle-resolution-v1-20260922`  
**Preregistration commit:** `00109f5c40c0161f72fd70de5ddfea0eb149cf7c`  
**Initial implementation commit:** `6b2fe6ab537ffd626a98aedbb765bfdc8d24223f`  
**Integrity correction commit:** `71589ca74b90fe08b6b4574094d4447bd32f7ae4`  
**Workflow commit:** `404f62e1ed69931cbf19b5e7dba00175619d066c`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_HIGH_RISK_HURDLE_RESOLUTION_V1_RESULT_2026-09-22.json` (Git blob SHA `8257916a44f16809c5e2f1e62d5a8d422ce4b7c8`)  
**Status:** `SELECTIVE_SIGNAL_PRESENT_NOT_CERTIFIED`.

### 11O.1 Problem definition

Following the semantic audit, this study no longer treats every UP-close after an SQRT alarm as a false risk alarm.

For each frozen SQRT alarm the joint outcome is one of:
- `HIT_DOWN`: realized target downside-RV >= frozen yearly Q80 and the day closes DOWN;
- `HIT_UP`: realized target downside-RV >= Q80 and the day closes UP;
- `MISS`: realized target downside-RV < Q80, regardless of close direction.

The model is therefore a conditional-resolution architecture, not a suppressor.

### 11O.2 Frozen two-stage hurdle architecture

Stage A:
- L2 logistic regression for realized risk hit versus miss.

Stage B:
- L2 logistic regression for DOWN versus UP, fitted only on formation rows that are realized risk hits.

Joint probabilities:
- P(HIT_DOWN)=P(hit)*P(DOWN|hit);
- P(HIT_UP)=P(hit)*(1-P(DOWN|hit));
- P(MISS)=1-P(hit).

Seven preregistered origin-safe features:
- daily / weekly / monthly downside-RV relative to Q80;
- daily realized variance relative to Q80;
- realized skewness;
- one-day origin return;
- recent 20-day high-risk share.

Router and legacy direction votes were intentionally excluded from V1.

Selective rule:
- emit the joint argmax only if max joint probability > 0.50;
- otherwise `UNCERTAIN`.

No hyperparameter, threshold, feature-list or class-weight tuning was allowed.

### 11O.3 Integrity correction

The first workflow run was correctly blocked by the mandatory integrity gate:
- 2020 alarms reproduced as 215 rather than 212;
- 2023 as 3 rather than 2;
- pooled n=274 rather than 270.

The cause was isolated to the parent SQRT-HAR reconstruction:
- incorrect implementation used `sqrt(mean(DR))` for weekly/monthly parent features;
- frozen SQRT-HAR-DR semantics use `mean(sqrt(DR))`.

This was corrected without changing the preregistered conditional model, feature list, decision threshold or scoring rule.

After correction:
- 2020=212;
- 2021=28;
- 2022=11;
- 2023=2;
- 2024=17;
- pooled=270;
- HIT_DOWN=115;
- HIT_UP=103;
- MISS=52;
- integrity errors=0.

### 11O.4 Final results

Pooled 2020–2024:
- n=270 SQRT alarms;
- observed HIT_DOWN=115;
- observed HIT_UP=103;
- observed MISS=52;
- emitted HIT_DOWN=11;
- emitted HIT_UP=68;
- emitted MISS=57;
- UNCERTAIN=134;
- selective coverage=**50.37%**;
- selective accuracy among emitted rows=**47.06%**;
- non-selective argmax accuracy=**39.26%**;
- largest observed class share=**42.59%**;
- multiclass Brier=**0.64869**;
- multiclass log loss=**1.03160**.

The preregistered selective-signal criterion technically passes because selective accuracy 47.06% exceeds the pooled largest-class share 42.59% with nonzero coverage.

However the class anatomy is weak:
- HIT_DOWN precision=36.36%, recall=3.48%;
- HIT_UP precision=50.00%, recall=33.01%;
- MISS precision=45.61%, recall=50.00%.

Conditional direction discrimination on the 218 alarms that actually realized high risk:
- AUC of P(DOWN|hit)=**0.5558**;
- 0.5-threshold direction accuracy=**50.92%**.

Year behavior is heterogeneous:
- 2020 selective accuracy 45.61% at 53.77% coverage; conditional direction AUC 0.533;
- 2021 selective accuracy 37.50% at 28.57% coverage; direction AUC 0.573 on only 20 hit rows;
- 2022 selective accuracy 42.86% at 63.64% coverage; direction AUC 0.350 on 9 hit rows;
- 2023 only two alarms;
- 2024 selective accuracy 83.33% at 35.29% coverage, but all six emitted decisions were MISS and there were only 17 alarms.

### 11O.5 Binding interpretation

The new semantic architecture is more coherent than suppressor tuning: risk realization and conditional direction are now explicitly separated, and an abstain state is part of the model contract. This is consistent with selective-classification methodology, where coverage is deliberately traded for lower error rather than forcing a label on every case.

But the first simple risk-geometry hurdle model does **not** solve conditional direction. The pooled Stage-B direction AUC of 0.556 and accuracy of 50.9% are only weakly above chance, while HIT_DOWN recall is essentially absent.

Therefore the technically positive selective-signal status must not be overstated. The main evidence is:

1. the architecture correction is justified;
2. origin-side realized-risk geometry contains some information about risk-hit versus miss;
3. the same feature set contains little stable information about DOWN versus UP resolution after a risk hit.

Do not tune C, the 0.50 abstain threshold, class weights or the seven-feature list under V1.

The next research identity should add genuinely directional or state information rather than another logistic variation. Candidate lanes are:
- Router/direct-expert/context features as an explicit Stage-B input;
- hidden-state / regime-state resolution models;
- selective/conformal direction classification on realized-risk-like states;
- competing-risk / cause-specific formulations if timing is modeled explicitly.

Any successor must remain chronological and preregistered. 2025 remains unavailable for tuning.

---


## 11P. SQRT + pure-UP detector conditional audit — test the manifest UP leader directly

**Identity:** `SQRT_PURE_UP_DETECTOR_CONDITIONAL_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-sqrt-pure-up-detector-audit-v1-20260922`  
**Preregistration commit:** `de9b472265104e8d71f9dc5ba2a6eebf987619ee`  
**Implementation commit:** `dd62f7f5ae78881c111d6ed89b5c727c84f009e7`  
**Workflow commit:** `d8c892e94b6369cc4b9f029eb6800d4163299ffc`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_SQRT_PURE_UP_DETECTOR_CONDITIONAL_AUDIT_V1_RESULT_2026-09-22.json` (Git blob SHA `f48ae6a1441858ae2ca0db26470e0d15f50ebd2a`)  
**Status:** descriptive audit; no promotion.

### 11P.1 Why this audit was required

The project had tested Router-based couplings, but the manifest already contains a direct pure-UP ranking. The binding UP-detector conclusions are:

- **pre-2025 pooled 2023–2024 pure-UP leader:** `RV_LOGIT`;
- **best 2025 transport trade-off among the frozen daily pure-UP models:** `TTSM-S2`.

Therefore the user's proposed simple composition was tested directly, without Router:

> if SQRT high-risk alarm and pure-UP detector says UP -> predict UP; otherwise -> predict DOWN.

No threshold tuning was performed:
- RV_LOGIT uses frozen p>=0.50;
- TTSM-S2 uses its frozen UP signal.

### 11P.2 Integrity

The audit reproduced exactly:
- SQRT alarms: 2020=212, 2021=28, 2022=11, 2023=2, 2024=17, pooled=270;
- joint alarm anatomy: HIT_DOWN=115, HIT_UP=103, MISS=52;
- integrity errors=0.

### 11P.3 Pooled 2020–2024 — all SQRT alarms

**RV_LOGIT**:
- UP calls=263/270;
- UP precision=52.85%;
- UP recall=97.20%;
- false-UP FPR=97.64%;
- DOWN recall=2.36%;
- binary accuracy under `UP else DOWN`=52.59%;
- balanced accuracy=49.78%.

**TTSM-S2**:
- UP calls=68/270;
- UP precision=52.94%;
- UP recall=25.17%;
- false-UP FPR=25.20%;
- DOWN recall=74.80%;
- binary accuracy=48.52%;
- balanced accuracy=49.99%.

Thus the two models fail in opposite directions on SQRT alarm days:
- RV_LOGIT becomes almost-always-UP;
- TTSM-S2 becomes mostly-not-UP / effectively mostly-DOWN under the user's complement rule.

Neither provides useful balanced discrimination on the SQRT-alarm subpopulation.

### 11P.4 Realized-high-risk subset only

Among the 218 SQRT alarms that truly realized high downside risk:
- actual HIT_UP=103;
- actual HIT_DOWN=115.

RV_LOGIT:
- UP calls=211/218;
- UP precision=46.92%;
- UP recall=96.12%;
- false-UP FPR=97.39%;
- DOWN recall=2.61%;
- accuracy=46.79%;
- balanced accuracy=49.36%.

TTSM-S2:
- UP calls=52/218;
- UP precision=46.15%;
- UP recall=23.30%;
- false-UP FPR=24.35%;
- DOWN recall=75.65%;
- accuracy=50.92%;
- balanced accuracy=49.48%.

The simple rule `UP signal => UP; otherwise => DOWN` therefore does not solve HIT_DOWN versus HIT_UP even when restricted to days where the downside-risk event actually materializes.

### 11P.5 Binding interpretation

The user correction was valid: Router is not the same thing as the manifest's best pure-UP detector, and the pure-UP leader had to be tested directly.

However the direct audit shows an important conditional-distribution shift. A model that looks useful on the general next-day population can lose discrimination inside the special subset selected by SQRT high-risk alarms.

RV_LOGIT's previously strong UP capture comes largely from very broad UP calling; on SQRT-high-risk days it calls virtually everything UP. TTSM-S2 is much more selective but misses most HIT_UP cases in this subset.

Therefore the simple two-model composition is not sufficient in its frozen form. The next Stage-B research must condition explicitly on the high-risk state rather than assume that general-population UP performance transports unchanged into the SQRT-alarm population.

Chronology warning: RV_LOGIT was designated the pre-2025 pure-UP leader using pooled 2023–2024 evidence, so 2020–2022 numbers in this audit are retrospective characterization, not prospective model-selection evidence. 2023–2024 themselves contain only 19 SQRT alarms, so they are too sparse for strong conditional validation.

---


## 11Q. SQRT × MOMENTUM_3M conditional-resolution audit — monthly prior tested directly

**Identity:** `SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-sqrt-momentum3m-resolution-audit-v1-20260922`  
**Preregistration commit:** `59ef9a34411f9f74b181f1665ccafb9fdef70e3d`  
**Implementation commit:** `57bbc02d7a0f241eaeb44411d6c378c70a62afe8`  
**Workflow commit:** `c1b6ba57f0328eb8685fe30301ac61b23649a4fd`  
**Frozen result commit:** `127286b68c3ef56c1b98ad955abcfaab7628f6fa`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_RESULT_2026-09-23.json` (Git blob SHA `8c96ff6ec5786aa77c55f317d2fdbf7f479af4ff`)  
**Status:** `DESCRIPTIVE_AUDIT_COMPLETE / NO_DAILY_RESOLUTION_DISCRIMINATION`.

### 11Q.1 Why this audit was required

The manifest already records `MOMENTUM_3M` as a strong **monthly H=1 price/momentum direction** expert, including 2025 direction accuracy 11/12 = 91.67%.

The user proposed the simple composition:

> if SQRT says next-day downside risk is high and MOMENTUM_3M says the target month is UP, interpret the alarm as UP; if MOMENTUM_3M says DOWN, interpret it as DOWN.

This was tested directly. MOMENTUM_3M was not converted into a next-day model; it remained a slower prior whose target-month forecast is formed in the previous month and is therefore available before each daily SQRT origin inside that month.

Frozen daily composition:
- monthly MOMENTUM_3M UP -> daily UP;
- monthly MOMENTUM_3M DOWN -> daily DOWN;
- NEUTRAL -> ABSTAIN.

No Router, RV_LOGIT, TTSM, threshold search, persistence gate or post-result rescue entered the rule.

### 11Q.2 Inputs and integrity

SQRT input:
- exact frozen forecast ledger from `2926796b6a7e9048d2c091c9c571cb928b773e02`.

MOMENTUM_3M input:
- `gold_axis_2026/patch_repro_v1/locked_replay_v7_daily_feature_pit_43.csv`;
- monthly direction = sign(`mom - rw`).

Integrity passed:
- 2023 SQRT alarms=2;
- 2024=17;
- 2025=90;
- 2023–2024 pooled=19;
- 2025 realized-high-risk alarms=66;
- no zero target returns;
- no missing MOMENTUM target month;
- integrity errors=0.

2025 remained locked retrospective stress only. 2026 was not used.

### 11Q.3 Primary 2023–2024 result

Across the 19 SQRT alarms:
- unique target months=5;
- MOMENTUM_3M UP on **19/19** alarm rows;
- MOMENTUM_3M DOWN on **0/19**;
- actual UP=11;
- actual DOWN=8;
- ordinary accuracy=57.89%;
- balanced accuracy=**50.00%**.

On the 9 alarms that truly realized high downside risk:
- MOMENTUM_3M UP=9/9;
- actual HIT_UP=2;
- actual HIT_DOWN=7;
- daily direction accuracy=22.22%;
- there was no DOWN call, so no two-sided daily discrimination was present.

The five alarm-bearing target months were:
- 2023-03;
- 2024-04;
- 2024-05;
- 2024-08;
- 2024-11.

MOMENTUM_3M was UP in all five.

### 11Q.4 Locked 2025 stress

Across 90 frozen SQRT alarms:
- unique target months=7;
- MOMENTUM_3M UP=**90/90**;
- DOWN=0;
- actual UP=45;
- actual DOWN=45;
- accuracy=50.00%;
- balanced accuracy=**50.00%**.

On the 66 alarms where high downside risk actually materialized:
- MOMENTUM_3M UP=66/66;
- HIT_UP=29;
- HIT_DOWN=37;
- accuracy=43.94%;
- balanced accuracy=50.00%.

The seven 2025 alarm-bearing months were April, May, June, July, October, November and December. MOMENTUM_3M was UP in every one of them.

### 11Q.5 Binding interpretation

The user's architecture idea was methodologically valid to test, but the frozen monthly MOMENTUM_3M prior does not resolve the daily high-risk direction problem.

The reason is structural rather than a threshold failure: **on every SQRT-alarm month available in the retained 2023–2025 replay, MOMENTUM_3M is UP.** Therefore the composition collapses to an always-UP daily rule on the very subset where discrimination is needed.

This does not contradict MOMENTUM_3M's strong monthly record. A month can finish above its previous-month reference while containing many individual high-risk days that close DOWN. Monthly direction accuracy and next-day conditional resolution are different targets.

Accordingly:
- keep MOMENTUM_3M as a strategic monthly prior;
- do not use its binary monthly sign alone as the Stage-B HIT_UP/HIT_DOWN resolver;
- do not retune MOMENTUM_3M to force daily variation;
- if retained in a future Stage-B model, use it only as one slow context feature alongside genuinely daily directional/state evidence.

Daily alarm rows inside a month are clustered because they share the same monthly prior, so they are not independent statistical trials.

---


## 11R. SQRT × frozen UP Verifier V2 semantic audit — correct UP motor re-tested under corrected semantics

**Identity:** `SQRT_FROZEN_UP_VERIFIER_V2_SEMANTIC_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-sqrt-frozen-up-verifier-semantic-audit-v1-20260923`  
**Preregistration commit:** `47c94d3ea6c9d60cfd5bec3c47ae8ff156e737a0`  
**Frozen result JSON commit:** `9382cb74fe0d5a342b128f2c754a51101e316d51`  
**Frozen report commit:** `b82ff4e4a815fd1a93cb1fe8a76eb264f0dbb163`  
**Status:** `RETROSPECTIVE_SEMANTIC_AUDIT_COMPLETE_NOT_CERTIFIED`.

### 11R.1 Why this audit was necessary

The authoritative frozen UP verifier is **not** RV_LOGIT, TTSM-S2 or MOMENTUM_3M in isolation.

The binding verifier baseline is:

`UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`

It passed the frozen standalone 2024 UP-verifier gate and transported descriptively to 2025:
- 2024 UP precision=61.90%, false-UP FPR=18.60%, coverage=20.49%;
- locked 2025 UP precision=72.97%, false-UP FPR=10.31%, coverage=15.61%.

The earlier direct RV_LOGIT/TTSM and MOMENTUM_3M conditional audits remain useful diagnostics, but they are not substitutes for testing the authoritative frozen UP verifier.

### 11R.2 Primary 2024 conditional result

Among 17 frozen SQRT alarms:
- actual UP=10;
- actual DOWN=7.

Router V2 emitted UP on 4:
- 3 actual UP;
- 1 actual DOWN;
- conditional UP precision = **75.00%**.

Router V2 abstained on 13:
- 7 actual UP;
- 6 actual DOWN;
- P(DOWN | ABSTAIN, SQRT alarm) = **46.15%**.

Thus the positive UP signal is selective and useful, but abstention does not imply DOWN.

If one forcibly applies the complement rule:
- Router UP -> UP;
- Router ABSTAIN -> DOWN;

then 2024 accuracy is only **52.94%** and balanced accuracy **57.86%**.

### 11R.3 Corrected risk-semantic crosswalk

The four 2024 Router-UP/SQRT-overlap rows are:

| target | actual close | realized risk semantics |
|---|---|---|
| 2024-08-07 | UP | RISK_MISS_UP_CLOSE |
| 2024-11-13 | DOWN | RISK_HIT_DOWN_CLOSE |
| 2024-11-14 | UP | RISK_MISS_UP_CLOSE |
| 2024-11-26 | UP | RISK_MISS_UP_CLOSE |

Therefore:
- 3/4 Router-UP calls were genuine realized-risk misses;
- all three correct UP calls were true SQRT risk misses, not merely days that happened to close UP;
- the single wrong Router-UP call was a genuine high-risk DOWN day.

This is important because it shows that the strongest 2024 UP-verifier overlap survives the later semantic correction: its three "good vetoes" were also genuine risk-cleaning successes.

Among the 13 Router-ABSTAIN alarms:
- RISK_HIT_DOWN_CLOSE=5;
- RISK_HIT_UP_CLOSE=2;
- RISK_MISS_DOWN_CLOSE=1;
- RISK_MISS_UP_CLOSE=5.

Abstention is therefore mixed in both risk realization and direction.

### 11R.4 Secondary 2022–2024 support

Across 30 frozen SQRT alarms:
- actual UP=16;
- actual DOWN=14;
- Router UP=4 = 3 UP / 1 DOWN;
- Router ABSTAIN=26 = 13 UP / 13 DOWN.

Forced complement-rule accuracy=53.33%, balanced accuracy=55.80%.

Again, the UP signal contains useful selective evidence; the complement does not.

### 11R.5 Locked 2025 stress

Among 90 frozen SQRT alarms:
- actual UP=45;
- actual DOWN=45.

Router V2 emitted UP on 16:
- 10 actual UP;
- 6 actual DOWN;
- conditional UP precision=**62.50%**.

Router abstained on 74:
- 35 actual UP;
- 39 actual DOWN;
- P(DOWN | ABSTAIN)=**52.70%**.

Forced complement-rule accuracy=54.44%, balanced accuracy=54.44%.

The retained frozen 2025 intersection artifact does not preserve the 16 individual Router-UP dates. Therefore the 2025 realized-risk semantic crosswalk is **NOT_PROVEN** and is not reconstructed from memory.

### 11R.6 Binding architecture consequence

The correct use of the frozen UP verifier is asymmetric:

- **Router V2 UP = positive evidence for UP / rebound resolution**;
- **Router V2 ABSTAIN ≠ DOWN**.

Therefore the project must not convert the verifier's silence into a DOWN label.

The active architecture becomes:

1. SQRT estimates whether downside risk is elevated.
2. Frozen UP Verifier V2 may identify a selective subset with strong UP evidence.
3. If the verifier abstains, the state remains **UNRESOLVED / UNCERTAIN** unless a separately validated DOWN-confirmation motor fires.

This narrows the unresolved problem substantially. We do not need another general UP model first; the missing component is a **positive DOWN-confirmation motor for the Router-abstain high-risk subset**.

No runtime promotion is authorized.

---


## 11S. DOWN verifier candidate audit — narrow baseline screen only

**Identity:** `DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-down-verifier-candidate-audit-v1-20260923`  
**Preregistration commit:** `f358f88b6fdc356ed8fd300f92d3034e38567b26`  
**Initial implementation commit:** `af1a29fabbf6036acbfc033e5dc44aa05746aae0`  
**Router chronology corrections:** `7300df8223c44b89658482335b35380d8ca0b3ea`, `b5e714f23311b8470bbc40fdc549516e987284c7`  
**Frozen result commit:** `7982b422476df61eb0339b74265afd553414f2d2`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESULT_2026-09-23.json` (Git blob SHA `181c06ad524520f6cdf96ab9ff16823b9c84b133`)  
**Status:** `NARROW_BASELINE_SCREEN_NO_ELIGIBLE_CANDIDATE / NOT_A_COMPREHENSIVE_EXISTING_MODEL_AUDIT`.

### 11S.1 Target subset

The audit did not re-open the solved positive-UP lane.

It examined only:

> `SQRT high-risk alarm AND frozen UP Verifier V2 ABSTAIN`

because section 11R showed:
- Router V2 UP contains useful positive-UP evidence;
- Router V2 ABSTAIN is not itself a DOWN label.

Primary candidate-selection period:
- 2022–2024 only.

Locked 2025 could be used only for unchanged transport of a candidate selected pre-2025. Since no candidate qualified, no 2025 candidate was selected or rescued.

### 11S.2 Frozen candidate pool

Ten existing same-clock next-day outputs were tested without changing their thresholds:

1. TTSM-S2 DOWN;
2. TTSM-S1 DOWN;
3. TSM DOWN;
4. Bonato AR1_RM QBoost h=1 median DOWN;
5. Bonato AR1 QBoost h=1 median DOWN;
6. AR1_RM_LOGIT p(UP)<0.50;
7. RM_LOGIT p(UP)<0.50;
8. RV_LOGIT p(UP)<0.50;
9. RSK_LOGIT p(UP)<0.50;
10. AR1_LOGIT p(UP)<0.50.

FAST/SLOW/monthly priors were not converted into flat next-day DOWN votes. Altuntaş and non-H1 horizons remained excluded for clock/horizon reasons.

### 11S.3 Integrity and Router reconstruction

The mandatory integrity gate exposed two implementation mistakes before any result was accepted.

First attempt incorrectly accumulated competence across all historical years.  
Second attempt correctly used Y-1 formation for the backward historical extension, but incorrectly reset the original locked 2025 challenge at the start of 2025.

The final implementation reproduces the two frozen chronology contracts exactly:

- historical extension:
  - 2022 initialized from 2021;
  - 2023 initialized from 2022;
- original frozen path:
  - 2024 initialized from 2023;
  - competence then continued causally through 2024 into locked 2025 without reset.

Final exact Router reproduction:
- 2022: n=205, Router UP=22, TP=12, FP=10;
- 2023: n=203, Router UP=19, TP=5, FP=14;
- 2024: n=205, Router UP=42, TP=26, FP=16;
- 2025: n=237, Router UP=37, TP=27, FP=10, all 37 selected through RM_LOGIT.

SQRT alarm counts also reproduced:
- 2022=11;
- 2023=2;
- 2024=17;
- 2025=90.

Pre-2025 SQRT/Router overlap reproduced exactly:
- 2022=0;
- 2023=0;
- 2024=4 = 3 actual UP / 1 actual DOWN.

Final integrity errors: **none**.

### 11S.4 Primary 2022–2024 unresolved subset

After removing the four Router-UP alarms, the exact unresolved pre-2025 subset is:

- n=26;
- actual DOWN=13;
- actual UP=13;
- baseline DOWN prevalence=50%.

Results:

| Candidate | DOWN calls | Correct DOWN | False DOWN | DOWN precision | DOWN recall | False-DOWN FPR |
|---|---:|---:|---:|---:|---:|---:|
| TTSM-S2 | 0 | 0 | 0 | — | 0.00% | 0.00% |
| TTSM-S1 | 2 | 1 | 1 | 50.00% | 7.69% | 7.69% |
| TSM | 3 | 1 | 2 | 33.33% | 7.69% | 15.38% |
| Bonato AR1_RM QBoost h=1 | 16 | 6 | 10 | 37.50% | 46.15% | 76.92% |
| Bonato AR1 QBoost h=1 | 14 | 4 | 10 | 28.57% | 30.77% | 76.92% |
| AR1_RM_LOGIT | 3 | 1 | 2 | 33.33% | 7.69% | 15.38% |
| RM_LOGIT | 1 | 1 | 0 | 100.00% | 7.69% | 0.00% |
| RV_LOGIT | 0 | 0 | 0 | — | 0.00% | 0.00% |
| RSK_LOGIT | 7 | 1 | 6 | 14.29% | 7.69% | 46.15% |
| AR1_LOGIT | 7 | 2 | 5 | 28.57% | 15.38% | 38.46% |

The preregistered exploratory eligibility rule required:
- at least 5 DOWN calls;
- DOWN precision >50%;
- false-DOWN FPR <50%.

**No candidate qualified.**

RM_LOGIT's single 1/1 DOWN call is not sufficient support and is explicitly not promoted.

### 11S.5 Corrected interpretation

**Correction entered 2026-09-23:** the original v2.25 wording overreached. This audit screened only ten baseline same-clock outputs drawn mainly from the Router/direct-expert and realized-moment families. It did **not** include all previously developed DOWN-specific / reversal / conditional-confirmation engines already recorded elsewhere in this manifest.

In particular it did not screen, among others:
- V1.53 moderate-downshock reversal specialist;
- DOWNSIDE_CROSSDOMAIN_DIRECTION_V1 variants;
- DOWNSIDE_CBR_DTW_PATH_V1;
- DOWNSIDE_SP500_CROSSMARKET_VETO_V1;
- DOWNSIDE_HETEROGENEOUS_CONSENSUS_VETO_V1;
- market-shock / macro-event conditional direction evidence;
- other previously frozen specialist outputs whose target clock and row-level artifacts must be verified before reuse.

Therefore this audit **does not establish that no existing Gold Control DOWN-capable model can help**. It establishes only that the ten preregistered baseline candidates in section 11S.2 did not provide an eligible DOWN verifier on the exact Router-abstain subset.

The ten screened baseline motors do not provide a supported positive DOWN verifier inside the exact state where one is needed:

> `SQRT high risk + frozen UP Verifier V2 abstain`.

The failure is not because the system lacks DOWN calls. Bonato variants emit many DOWN calls, but in this subset they are mostly false. Conversely, RM_LOGIT produces one clean DOWN call but has essentially no coverage.

Therefore:
- do not convert Router abstention into DOWN;
- do not reuse a weak existing DOWN complement merely because it emits often;
- do not tune thresholds on these 26 cases;
- do not use 2025 to choose a candidate after the pre-2025 failure.

The next clean step is first a **comprehensive authority scan and conditional crosswalk of the already-developed DOWN-specific/specialist engines** against the exact `SQRT high risk + Router V2 ABSTAIN` subset. Only if that comprehensive screen also fails should the project move to genuinely new information or a new DOWN-specific state model.

The intended role is narrow:

> given SQRT high risk and no verified UP signal, is there positive evidence strong enough to confirm DOWN; otherwise remain UNCERTAIN?

No runtime or production promotion is authorized.

---


## 11T. Comprehensive retained DOWN-specialist crosswalk — CBR-DTW emerges as a narrow candidate

**Final identity:** `COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_RESEARCH`  
**Research branch:** `gold-comprehensive-down-specialist-crosswalk-v1-20260923`  
**V1 preregistration commit:** `1a2a445c239f9f4674aa2fd7f303b11fbd43bbe6`  
**V1R2 integrity amendment:** `ca10e095a2c6e605c22c2bb0ad3895fc3a4c4dd4`  
**R2 implementation commit:** `8d2e58e978c335a454d4ba94c16eccbc6710ba9f`  
**Workflow freeze fix:** `25dabba3af6a013262fb0ede20c082cd0ddcb314`  
**Frozen result commit:** `58f0eadb4840bdc07470058251d89657dca6ad3b`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_RESULT_2026-09-23.json` (Git blob SHA `c29077a8d4172c8044593cf5435bb78442e3cb56`)  
**Status:** `PRE2025_SPECIALIST_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT / NOT_CERTIFIED / NOT_RUNTIME`.

### 11T.1 Purpose and correction of the narrow audit

Section 11S screened only ten baseline same-clock outputs. It did not justify the broader claim that all previously developed DOWN/reversal specialists had failed inside the exact unresolved branch.

This successor performed the broader authority scan and exact conditional crosswalk against:

> `SQRT HIGH RISK + frozen UP Verifier V2 ABSTAIN`.

The frozen primary unresolved set remains:
- 2022–2024 total n=26;
- actual DOWN=13;
- actual UP=13.

The locked 2025 unresolved stress set is:
- n=74;
- actual DOWN=39;
- actual UP=35;
- baseline DOWN prevalence=52.70%.

No 2025 outcome participated in candidate selection or threshold design.

### 11T.2 Authority scan and target-clock integrity

The preregistered V1 attempted to include:
- V1.53 intraday specialists;
- Cross-domain conditional direction V1;
- CBR-DTW path morphology V1;
- S&P 500 cross-market V1;
- heterogeneous CBR + S&P consensus V1.

The V1 integrity gate correctly blocked interpretation because the V1.53 exact-NY17 target sign did **not** map one-to-one to the SQRT parent target-day sign under a simple `target_date` join. First observed mismatches included:
- 2024-04-16;
- 2025-05-01;
- 2025-05-02;
- 2025-05-07;
- 2025-05-13.

V1.53 was therefore removed under the preregistered V1R2 integrity amendment and is now:

`NOT_PROVEN_TARGET_CLOCK_ALIGNMENT`

for this SQRT conditional crosswalk. Its blocked V1 numbers have no candidate-selection authority.

The following were also not silently coerced into the daily same-clock task:
- Market Shock / Macro Event: event/minute target clock mismatch;
- weekly, H5/H10/H20 and 3D engines: horizon mismatch;
- MONTHLY_DIRECTION_3M / MOMENTUM_3M: slow-clock priors;
- Altuntaş AlexNet: target-clock identity unresolved;
- V1.63: 2024 is training history under that identity;
- later 1D models without a proven retained pre-scoring exact-row artifact;
- older internal variants whose exact row-level evidence is NOT_FOUND.

These are evidence-discipline exclusions, not claims that the methods are intrinsically useless.

### 11T.3 Final R2 integrity

Final R2 integrity errors: **none**.

The audit reproduced:
- primary unresolved set 26 = 13 DOWN + 13 UP;
- locked 2025 unresolved set 74 = 39 DOWN + 35 UP;
- frozen Router annual behavior;
- Cross-domain target signs;
- the original full-2024 CBR-DTW aggregates;
- the original full-2024 S&P aggregates;
- the original full-2024 heterogeneous-consensus aggregate.

No threshold was changed after observing subset outcomes.

### 11T.4 Pre-2025 conditional crosswalk

The screen rule, frozen before scoring, required:
- available support n >=10;
- at least 5 DOWN calls;
- DOWN precision >50%;
- false-DOWN FPR <50%.

Among the retained same-clock specialist candidates, exactly one passed:

> **`CBR_STRICT_P050_DOWN`**

This is the original CBR-DTW path-morphology model using:
- origin-day normalized cumulative intraday return path;
- cumulative signed-variance-pressure path;
- DTW nearest-neighbour case matching;
- STRICT historical pool = prior frozen SQRT high-risk alarms;
- fixed probability threshold = 0.50.

Its pre-2025 usable conditional support is **2024 only**, because the original CBR contract does not provide candidate predictions for the 2022–2023 unresolved rows.

On the 13 unresolved 2024 rows:
- actual DOWN=6;
- actual UP=7;
- DOWN calls=5;
- correct DOWN=3;
- false DOWN=2;
- DOWN precision=**60.00%**;
- DOWN recall=**50.00%**;
- false-DOWN FPR=**28.57%**;
- decision coverage=**38.46%**;
- one-sided 90% Wilson lower bound on DOWN precision=**33.04%**.

This satisfies the preregistered exploratory screen but is based on a very small retrospective support set. It is a candidate signal, not certification.

Other important retained results:
- Cross-domain STATIC: 0 DOWN calls;
- Cross-domain DYNAMIC D99: 2 DOWN calls, 0 correct / 2 false;
- Cross-domain competing-risk: 1 DOWN call, incorrect;
- Cross-domain explicit-duration: 17 calls, 7 correct / 10 false, precision 41.18%;
- CBR STRICT_RECALL75: 9 calls, 5 correct / 4 false, precision 55.56% but false-DOWN FPR 57.14%;
- CBR CONTEXT_P050: 6 calls, 3 / 3, precision 50%;
- S&P P050: 8 calls, 4 / 4, precision 50%, false-DOWN FPR 57.14%;
- heterogeneous consensus: 11 calls, 6 correct / 5 false, precision 54.55%, but false-DOWN FPR 71.43%.

Thus the useful property of CBR STRICT P050 is not merely raw accuracy; it is the combination of selective DOWN calling and lower false-DOWN contamination in the unresolved state.

### 11T.5 Locked 2025 transport of the pre-2025-selected CBR rule

Only the pre-2025 screen-positive candidate was transported to 2025, unchanged.

On the exact 74 locked 2025 unresolved rows:

- actual DOWN=39;
- actual UP=35;
- CBR DOWN calls=33;
- correct DOWN=21;
- false DOWN=12;
- DOWN precision=**63.64%**;
- DOWN recall=**53.85%**;
- false-DOWN FPR=**34.29%**;
- decision coverage=**44.59%**;
- one-sided 90% Wilson lower bound on DOWN precision=**52.50%**.

Baseline DOWN prevalence in the unresolved subset is 39/74 = **52.70%**.

Therefore the unchanged CBR rule's DOWN-call precision exceeds the unresolved-state base rate by **+10.93 percentage points**.

Under the preregistered transport rule this is:

`TRANSPORT_SUPPORTIVE`.

This is locked retrospective transport/stress, not fresh prospective confirmation and not a tuning authority.

### 11T.6 Binding interpretation

The corrected comprehensive screen changes the project state materially:

- the earlier broad statement that no existing DOWN-capable specialist was useful was wrong and remains superseded;
- one retained specialist, **CBR-DTW STRICT P050**, provides a plausible positive DOWN-confirmation signal specifically in the state where SQRT says high risk and the frozen UP verifier abstains;
- its pre-2025 selection evidence is only 13 unresolved 2024 rows, so the evidence is too small for certification;
- its unchanged locked-2025 behavior is directionally supportive rather than collapsing.

The active architecture is now:

1. **SQRT risk motor** -> HIGH RISK / NORMAL RISK.
2. **Frozen UP Verifier V2** -> VERIFIED UP or ABSTAIN.
3. On HIGH RISK + UP-ABSTAIN, **CBR-DTW STRICT P050** is the current research candidate for a positive VERIFIED DOWN lane.
4. If CBR does not confirm DOWN -> remain **UNCERTAIN**.

This is not yet a production model. The next scientific question is no longer "can any existing specialist help?" but whether this narrow CBR signal survives stronger same-clock support / prospective evidence without retuning.

No runtime or production promotion is authorized.

---


## 11U. CBR DOWN verifier historical extension — superseded for cascade use because the historical CBR pool was not route-consistent

**Identity:** `CBR_DOWN_VERIFIER_HISTORICAL_EXTENSION_V1_RESEARCH`  
**Research branch:** `gold-cbr-down-historical-extension-v1-20260923`  
**Preregistration commit:** `476527a73f351ebb05f0f1b94789dc98f710d5a5`  
**Initial implementation commit:** `2c1bcac63b1c8d841231ea9a868602ef91fa2ea6`  
**Workflow commit:** `4e1f7e10567f18a3b764a2e98cfd5ff7ebc46639`  
**Workflow YAML fix:** `734525b38f16afee4793b08589c6c3cbec86d8d1`  
**Representable-overlap integrity amendment:** `92434d47ac4a6e1faa7b34eeab0932bcb214d0f9`  
**Path-harmonization implementation fix:** `e4b68e2da7012506cbfba668b5bd119741e9eac5`  
**Governed path materialization fix:** `1949c553a41fe420c7baba831522c7137055072f`  
**Frozen result commit:** `2ad6b1d02783c2e08768669d72a246f9da0d84c1`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_CBR_DOWN_VERIFIER_HISTORICAL_EXTENSION_V1_RESULT_2026-09-23.json` (Git blob SHA `4153d7a2c980131e3a5b789cdb1803c60f488cdb`)  
**Status:** `HISTORICAL_EXTENSION_NOT_SUPPORTED / METHODOLOGICALLY_NON_BINDING_FOR_FINAL_CASCADE`.

### 11U.1 Frozen question

Section 11T found `CBR_STRICT_P050_DOWN` as a narrow research candidate in the unresolved state:

> `SQRT HIGH RISK + frozen UP Verifier V2 ABSTAIN`.

Its original pre-2025 candidate evidence was only the 13 unresolved 2024 rows. This successor therefore kept the CBR method completely frozen and extended only its historical case library backward using the corrected external Dukascopy 2020–2021 SQRT-alarm cases.

Frozen CBR method:
- NPTS=48;
- two path channels = normalized cumulative intraday return and cumulative signed-variance pressure;
- DTW band=6;
- K=3;
- EPS=1e-8;
- STRICT pool = prior SQRT high-risk alarms;
- DOWN iff `p(DOWN) >= 0.50`.

No threshold, K, band or representation was tuned.

### 11U.2 External raw-path reconstruction and harmonization

Pinned public minute source:
`kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`.

Pinned corrected external daily spine:
`509c5ffa762f4ea49644b8ffe723ed2591ba52bf`.

The raw 2020–2021 bid/ask minute history was downloaded transiently in CI, rebuilt as:
- exact bid/ask timestamp inner join;
- mid close;
- 5-minute last close;
- America/New_York calendar;
- 17:00–17:55 maintenance hour excluded.

External daily reconstruction passed exactly enough for method use:
- reconstructed rows=518;
- corrected-spine rows=518;
- missing/extra dates=0;
- bad 276-bar dates=0;
- max absolute close difference=4.55e-13;
- max RV difference=3.55e-17;
- max downside-RV difference=3.25e-17.

The first path-harmonization implementation exposed governed overlap days with fewer than the frozen CBR minimum of 239 intraday returns. Before scoring, the preregistered integrity amendment restricted path harmonization to dates representable by the frozen CBR contract; no padding or imputation was allowed.

Final cross-source path gate:
- calendar overlap=450;
- CBR-representable exact-date overlap=345;
- short governed overlap days excluded from the gate=105;
- median same-date flattened path correlation=**0.999914**;
- median same-date DTW=**0.005832**;
- median deterministic shifted-date DTW=**0.440900**;
- same/shifted median DTW ratio=**0.01323**;
- fraction of same-date DTW below shifted-date median=**100%**.

The path-harmonization gate passed strongly.

### 11U.3 External SQRT parent reproduction

The pinned frozen SQRT implementation reproduced the corrected external historical alarm anatomy exactly:

- 2020: 212 alarms = 97 DOWN + 115 UP;
- 2021: 28 alarms = 16 DOWN + 12 UP.

Thus the extended CBR formation pool contributed 240 external high-risk historical cases:
- DOWN=113;
- UP=127.

### 11U.4 Historical-extension results, 2022–2024

The frozen CBR rule was tested only on the exact unresolved rows:
`SQRT HIGH RISK + Router V2 ABSTAIN`.

#### 2022
- test n=11;
- actual DOWN=6, UP=5;
- training cases=240 external 2020–2021 alarms;
- DOWN calls=6;
- correct DOWN=3;
- false DOWN=3;
- precision=**50.00%**;
- recall=**50.00%**;
- false-DOWN FPR=**60.00%**.

#### 2023
- test n=2;
- actual DOWN=1, UP=1;
- training cases=251;
- DOWN calls=1;
- correct DOWN=0;
- false DOWN=1;
- precision=**0.00%**;
- false-DOWN FPR=**100%**.

#### 2024
- test n=13;
- actual DOWN=6, UP=7;
- training cases=253;
- DOWN calls=5;
- correct DOWN=3;
- false DOWN=2;
- precision=**60.00%**;
- recall=**50.00%**;
- false-DOWN FPR=**28.57%**.

The 2024 unresolved result is numerically the same 3/5 DOWN confirmation pattern that had made CBR promising in section 11T.

#### Pooled 2022–2024
- n=26;
- actual DOWN=13, UP=13;
- DOWN calls=12;
- correct DOWN=6;
- false DOWN=6;
- precision=**50.00%**;
- recall=**46.15%**;
- false-DOWN FPR=**46.15%**;
- coverage=**46.15%**;
- one-sided 90% Wilson lower bound on precision=32.65%.

The preregistered support gate required DOWN precision strictly above 50%. It therefore **failed**.

### 11U.5 Locked 2025 transport under the extended formation

The unchanged extended CBR pool was then carried to the exact 74 locked 2025 unresolved rows:

- actual DOWN=39, UP=35;
- training cases=270;
- DOWN calls=33;
- correct DOWN=18;
- false DOWN=15;
- precision=**54.55%**;
- recall=**46.15%**;
- false-DOWN FPR=**42.86%**;
- coverage=**44.59%**;
- unresolved-subset DOWN base rate=**52.70%**;
- precision lift over base rate=**+1.84 pp**.

This narrowly satisfies the preregistered 2025 descriptive transport condition, but the pre-2025 extension gate had already failed. Therefore 2025 cannot rescue the architecture and the final status remains:

`HISTORICAL_EXTENSION_NOT_SUPPORTED`.

For comparison, the original governed-history CBR candidate in section 11T had performed better on the same locked 2025 unresolved subset:
- 21 correct / 12 false;
- precision=63.64%;
- recall=53.85%;
- false-DOWN FPR=34.29%.

Adding the large 2020–2021 external case library therefore **diluted**, rather than strengthened, the 2025 conditional DOWN signal.

### 11U.6 Neighbor-provenance diagnostic

The extension is heavily dominated by the 2020 external crisis-regime case library.

Across the 26 pre-2025 test rows, the K=3 nearest-neighbour slots were sourced:
- external 2020: 64;
- external 2021: 9;
- governed 2022: 4;
- governed 2023: 1.

Across locked 2025:
- external 2020: 182 neighbour slots;
- external 2021: 17;
- governed 2022: 10;
- governed 2023: 3;
- governed 2024: 10.

This is descriptive diagnosis only; no post-hoc weighting or year filtering is authorized under this identity. It indicates that mechanically enlarging the CBR case library with older high-risk episodes changes the effective neighbour regime substantially.

### 11U.7 Binding interpretation

The historical extension does **not** strengthen the CBR candidate.

What remains valid:
- external source reconstruction passed;
- cross-source CBR path morphology harmonizes very strongly;
- historical SQRT alarm reconstruction passed exactly;
- original 2024 CBR unresolved result remains 3/5 correct DOWN calls;
- original locked-2025 governed-history transport remains a real retrospective observation.

What is newly learned:
- when 240 older 2020–2021 high-risk cases are added without changing CBR, pooled 2022–2024 precision falls to exactly 50%;
- locked-2025 precision falls from 63.64% to 54.55%;
- the nearest-neighbour set becomes dominated by 2020 external crisis cases.

Therefore **do not adopt the historical-extension formation pool**.

The original `CBR_STRICT_P050_DOWN` candidate may remain preserved as a narrow retrospective candidate, but confidence in its cross-regime robustness is materially weaker. The project must not solve this by post-hoc year weighting, K changes, distance thresholds or excluding 2020 under the same identity.

The next DOWN-lane research should explicitly address **regime-conditioned case relevance / transportability** under a new preregistered identity, or seek independent prospective same-clock evidence for the original frozen CBR rule.

No runtime or production promotion is authorized.

---


## 11V. Cascade-route-consistent CBR — intended architecture tested correctly

**Identity:** `CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESEARCH`  
**Research branch:** `gold-cbr-cascade-route-consistent-v1-20260923`  
**Preregistration commit:** `17894825ce71af1895cd4e721ce9281843878ab7`  
**Implementation commit:** `f60b77a75465c04cd42707338cbb90c422b34438`  
**Generated-source newline fix:** `b7a10307652afca0ea493f4818e322ca161f5ccf`  
**Workflow commit:** `3e5ed0606b4d3fbedcdb00470a7d035f71cf89ee`  
**Frozen result commit:** `b22235f04dc48b173a93a98cc2ce22081bb0054e`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json` (Git blob SHA `be617fe6d33a3ab846ccf8907cc72097e051a0ec`)  
**Status:** `CASCADE_ROUTE_CONSISTENT_NOT_SUPPORTED`.

### 11V.1 Correct binding cascade

The intended architecture is:

```
SQRT
  |
HIGH RISK
  |
Frozen UP Verifier V2
 /                  \
UP                  ABSTAIN
|                      |
VERIFIED UP           CBR-DTW
                     /       \
                  DOWN        no
                    |          |
             VERIFIED DOWN   UNCERTAIN
```

The critical correction is **route consistency**.

A historical row may enter the CBR case library only if that historical row itself would have reached the CBR node:

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`.

Rows where the UP verifier emitted UP terminate at `VERIFIED UP` and are excluded from the CBR library.

Section 11U did not enforce this on the historical training pool and is therefore not binding evidence for the final cascade.

### 11V.2 External route reconstruction — exact integrity

The corrected external 2020–2021 source and frozen Router V2 were reconstructed before CBR scoring.

External SQRT:
- 2020: 212 alarms = 97 DOWN +115 UP;
- 2021: 28 alarms =16 DOWN +12 UP.

External Router V2:
- 2020: n=260, Router UP=185, TP=111, FP=74;
- 2021: n=258, Router UP=33, TP=19, FP=14.

Exact SQRT × Router intersection:
- 2020: Router-UP overlap=140 =80 actual UP +60 actual DOWN;
- 2021: overlap=2 =1 UP +1 DOWN.

Therefore the historical rows that truly route to CBR are:

- 2020: **72 =37 DOWN +35 UP**;
- 2021: **26 =15 DOWN +11 UP**;
- pooled external CBR library: **98 =52 DOWN +46 UP**.

This replaces the incorrect section-11U use of all 240 external SQRT alarms as CBR cases.

External raw-path reconstruction and cross-source path harmonization remained valid:
- 518/518 corrected 2020–2021 daily rows reproduced;
- CBR-representable overlap n=345;
- median same-date path correlation=0.999914;
- same/shifted median DTW ratio=0.01323;
- 100% of same-date distances below the shifted-date median.

Final integrity errors: **none**.

### 11V.3 Route-consistent chronological training sizes

Only prior matured Router-ABSTAIN high-risk rows were admitted.

- 2022 test: train n=98;
- 2023 test: train n=109 =98 external +11 governed-2022 unresolved;
- 2024 test: train n=111 =98 +11 +2;
- locked 2025 test: train n=124 =98 +11 +2 +13.

The test sets remained:
- 2022 unresolved n=11 =6 DOWN +5 UP;
- 2023 n=2 =1/1;
- 2024 n=13 =6 DOWN +7 UP;
- pooled 2022–2024 n=26 =13 DOWN +13 UP;
- locked 2025 n=74 =39 DOWN +35 UP.

No VERIFIED-UP row entered CBR training.

### 11V.4 Correct route-consistent results

#### 2022
- DOWN calls=10/11;
- correct DOWN=6;
- false DOWN=4;
- precision=**60.00%**;
- DOWN recall=**100%**;
- false-DOWN FPR=**80.00%**.

The high recall is therefore achieved with excessive false-DOWN contamination.

#### 2023
Only two unresolved rows:
- DOWN calls=1;
- correct=1;
- false=0;
- precision=100%.

This sample is too small to carry independent authority.

#### 2024
- DOWN calls=5/13;
- correct DOWN=2;
- false DOWN=3;
- precision=**40.00%**;
- recall=**33.33%**;
- false-DOWN FPR=**42.86%**.

This differs from the earlier non-route-consistent/original CBR diagnostic (3/5 correct), confirming that cascade-consistent historical case selection materially changes the prediction surface.

#### Pooled 2022–2024
- n=26;
- actual DOWN=13, UP=13;
- DOWN calls=16;
- correct DOWN=9;
- false DOWN=7;
- precision=**56.25%**;
- recall=**69.23%**;
- false-DOWN FPR=**53.85%**;
- coverage=**61.54%**;
- one-sided 90% Wilson LCB precision=40.52%.

The preregistered support rule required:
- DOWN calls >=5;
- precision >50%;
- false-DOWN FPR <50%.

Precision passed, but false-DOWN FPR failed. Therefore:

`PRE2025 ROUTE-CONSISTENT SUPPORT = FALSE`.

### 11V.5 Locked 2025 transport

The unchanged route-consistent CBR was carried to the exact 74 locked 2025 unresolved rows.

- DOWN calls=36;
- correct DOWN=20;
- false DOWN=16;
- precision=**55.56%**;
- recall=**51.28%**;
- false-DOWN FPR=**45.71%**;
- coverage=**48.65%**;
- unresolved DOWN base rate=52.70%;
- precision lift=**+2.85 pp**.

Under the isolated 2025 descriptive gate this is technically supportive, because precision is above the unresolved-state base rate and FPR is below 50%.

However the pre-2025 route-consistent gate had already failed. By preregistration, 2025 cannot rescue the model. Final status therefore remains:

`CASCADE_ROUTE_CONSISTENT_NOT_SUPPORTED`.

### 11V.6 Binding interpretation

The user's cascade definition was correct, and the historical training population must obey that same route.

Once tested correctly, CBR-DTW STRICT P050 does **not** currently qualify as the VERIFIED-DOWN motor.

The result is not a total absence of signal:
- pooled precision is 56.25%;
- locked-2025 precision is 55.56%;
- but the pre-2025 false-DOWN rate among actual UP cases is 53.85%, above the frozen limit.

The principal failure is therefore **insufficient selectivity**, not total inability to find DOWN cases.

The active architecture remains:

1. SQRT -> HIGH RISK / NORMAL RISK.
2. Frozen UP Verifier V2 -> VERIFIED UP / ABSTAIN.
3. On ABSTAIN, **no DOWN verifier is yet validated**.
4. Until a positive DOWN confirmer passes its own gate -> **UNCERTAIN**.

The prior statements that CBR was a current VERIFIED-DOWN candidate based on section 11T are superseded for the final cascade because those CBR histories were not fully route-consistent.

No post-hoc tuning of CBR p=0.50, K, DTW band, year weights, or 2020 exclusion is authorized under this identity.

---


## 11W. False-DOWN next-origin UP rescue audit — frozen UP verifier does not immediately rescue CBR mistakes

**Identity:** `CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-cbr-falsedown-nextup-rescue-audit-v1-20260923`  
**Preregistration commit:** `ee14080e93bb627f2e361367ceedf2f4c3f81031`  
**Implementation commit:** `9609e5cc046412b1ac278109a0964522d855f08d`  
**Workflow commit:** `c29e18794b483993deb81db0cc10ea8901c14869`  
**Frozen result commit:** `2b8270fe8d69da666c87f1656871cd2c58f0ad8f`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_RESULT_2026-09-23.json` (Git blob SHA `00a78c87c072c51a8bef72e58557cf817c5c623e`)  
**Status:** `RETROSPECTIVE_NEXT_ORIGIN_RESCUE_AUDIT_COMPLETE`.

### 11W.1 Question

Section 11V showed that route-consistent CBR produces false-DOWN calls. The economic question was whether the frozen UP verifier would emit an UP signal at the close of such a false-DOWN day for the immediately following trading day, potentially allowing a trader to reverse on the next leg and recover some of the loss.

This audit distinguishes:

- **standalone next-origin Router-UP**: Router V2 emits UP at the false-DOWN target day's close;
- **cascade next-origin VERIFIED-UP**: the next-origin SQRT state is HIGH RISK and Router V2 emits UP.

The T-close signal cannot erase the short loss already realized from the prior origin close to T close. It can only affect the following trade.

### 11W.2 Exact false-DOWN universe

Route-consistent CBR false-DOWN counts reproduced exactly:

- 2022: 4;
- 2023: 0;
- 2024: 3;
- locked 2025: 16.

Total=23.

### 11W.3 Immediate next-origin UP result

Across **all 23** route-consistent CBR false-DOWN cases:

- standalone frozen Router V2 emitted UP at the immediately following origin: **0 / 23**;
- cascade next-origin VERIFIED-UP: **0 / 23**.

Annual:
- 2022: 0/4;
- 2024: 0/3;
- 2025: 0/16.

Thus the hypothesis that the current frozen UP verifier would immediately reverse these CBR false-DOWN mistakes on the next trading decision is **not supported**.

The exact audit ledger also shows that many next origins remained HIGH RISK, yet Router V2 still abstained. For example, the 2025 false-DOWN sequence around October/November contains several consecutive next origins with SQRT HIGH RISK and Router ABSTAIN.

### 11W.4 Economic implication

Gross false-DOWN move totals, using equal fixed notional, no leverage/fees/slippage:

- 2022: 5.2731%;
- 2024: 1.9610%;
- locked 2025: 17.7773%.

Because next-origin Router-UP count is zero, there is no frozen-UP-model following-leg recovery to subtract under this immediate one-step rescue definition.

This does **not** mean the whole trading strategy loses these amounts after accounting for correct DOWN trades or other independent signals. It means only that the specific "the UP verifier will probably flip us long on the very next origin" rescue mechanism does not exist in the current frozen architecture.

### 11W.5 Binding interpretation

The UP verifier and CBR errors are not complementary in the way initially hypothesized.

When CBR falsely calls DOWN inside `SQRT HIGH RISK + Router ABSTAIN`, the frozen Router V2 does not immediately recognize the rebound on the next origin in any observed 2022–2025 false-DOWN case.

Therefore the false-DOWN selectivity problem cannot be dismissed on the assumption that the UP verifier automatically repairs it one trading decision later.

A separate full-strategy P&L audit may still be useful, but it must include:
- correct DOWN profits;
- VERIFIED-UP profits/losses;
- UNCERTAIN/flat treatment;
- one-day position reset;
- transaction-cost assumptions.

No model tuning is authorized from this audit.

---


## 11X. Residual one-sided UP-2 — first dedicated missed-UP specialist passes the pre-2025 gate

**Identity:** `RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`  
**Research branch:** `gold-residual-up2-onesided-logit-v1-20260923`  
**Preregistration commit:** `2c2805adf232d8d2eae35c41db387cb540263898`  
**Integrity amendment commits:** `5361178290d59cad39c5982c92b8cd0fa3378f85`, `031703f65a8fe080d9fbdc3488f1e1cac2ac93c6`  
**Implementation commit:** `e7db0333b1a7b13635e5df4142c0be9c11bd6558`  
**Workflow commit:** `f11b2ee6dfca41398db2b44ac5c5226d9be3b5cc`  
**Frozen result commit:** `eb928b2d5be6250227d8e14dea2d58abe494f762`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESULT_2026-09-23.json` (Git blob SHA `76633b00586dcc6854b3845f737fdcf22bf61f0a`)  
**Status:** `RESIDUAL_UP2_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT / RESEARCH_ONLY / NOT_RUNTIME`.

### 11X.1 Role

This is the first model built specifically for the residual state:

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`.

It is not a general UP model and it never emits DOWN.

Its outputs are:

- `UP2`: second-stage positive UP evidence;
- `ABSTAIN`: no second-stage UP confirmation.

The intended cascade is now:

```
SQRT HIGH RISK
      |
Frozen UP Verifier V2
   /             \
 UP              ABSTAIN
 |                  |
VERIFIED UP      UP-2 specialist
                /             \
              UP2              ABSTAIN
              |                  |
      VERIFIED UP-2        downstream resolver
```

### 11X.2 Frozen model

Base classifier:
- L2 logistic regression;
- C=1.0;
- lbfgs;
- no hyperparameter sweep.

Nine origin-safe features:
1. SQRT normalized risk score;
2. lag-1 close return;
3. downside semivariance share;
4. normalized intraday end position;
5. close location inside the origin-day intraday range;
6. normalized recovery from the intraday trough;
7. normalized final-quarter intraday return;
8. fraction of five frozen direct UP experts voting UP;
9. frozen legacy-context UP fraction.

The one-sided threshold is not ordinary 0.50 classification. For each target year, strictly prequential historical residual probabilities are generated after 40 matured prior cases. The threshold is:

`tau = max(0.50, nearest-rank q80 of historical prequential DOWN scores)`.

At least 20 historical DOWN calibration scores are required.

### 11X.3 Source and route integrity

External 2020–2021 route reconstruction reproduced exactly:
- 2020 residual CBR/UP2 population: 72 =37 DOWN +35 UP;
- 2021 residual: 26 =15 DOWN +11 UP;
- pooled external residual formation: 98 =52 DOWN +46 UP.

Governed evaluation:
- 2022: 11 =6 DOWN +5 UP;
- 2023: 2 =1/1;
- 2024: 13 =6 DOWN +7 UP;
- locked 2025: 74 =39 DOWN +35 UP.

Source-derived feature harmonization passed:
- exact representable overlap n=344;
- lag-1 return sign agreement=90.99%;
- all six raw/source-derived feature Pearson correlations >=0.90;
- five of six path-state features were >=0.994 correlation; lag-1 close return correlation=0.9014.

Final integrity errors: **none**.

### 11X.4 Pre-2025 chronological result

#### 2022
- residual n=11;
- UP2 calls=7;
- true UP=4;
- false UP=3;
- precision=57.14%;
- missed-UP recall=80.00%;
- false-UP FPR=50.00%;
- AUC=0.700;
- tau=0.5000.

This year is useful for recall but insufficiently selective on its own.

#### 2023
Only two residual rows:
- UP2 calls=1;
- true UP=1;
- false UP=0.

Too small to carry independent authority.

#### 2024
- residual n=13;
- UP2 calls=3;
- true UP=3;
- false UP=0;
- precision=100%;
- missed-UP recall=42.86%;
- false-UP FPR=0%;
- AUC=0.8571;
- tau=0.5346.

#### Pooled 2022–2024
- residual n=26 =13 UP +13 DOWN;
- UP2 calls=11;
- true UP=8;
- false UP=3;
- precision=**72.73%**;
- missed-UP recall=**61.54%**;
- false-UP FPR=**23.08%**;
- coverage=42.31%;
- one-sided 90% Wilson LCB precision=**53.45%**;
- AUC=**0.7870**;
- Brier=0.2272.

The frozen pre-2025 gate required:
- n=26;
- calls >=4;
- precision >50%;
- Wilson90 LCB precision >50%;
- false-UP FPR <=25%.

All conditions passed.

Therefore:

`PRE2025_RESIDUAL_UP2_SIGNAL = TRUE`.

### 11X.5 Locked 2025 transport

Unchanged V1 on exact locked residual rows:

- n=74 =35 UP +39 DOWN;
- UP2 calls=25;
- true UP=13;
- false UP=12;
- precision=**52.00%**;
- missed-UP recall=**37.14%**;
- false-UP FPR=**30.77%**;
- coverage=33.78%;
- Wilson90 LCB precision=39.47%;
- AUC=**0.5165**;
- tau=0.5312.

Residual UP base rate is 35/74 = 47.30%, so raw precision is +4.70 percentage points above base. This meets the preregistered descriptive locked-2025 transport criterion, but the discrimination is materially weaker than pre-2025 and the AUC is close to 0.50.

Therefore 2025 is **supportive only in the narrow preregistered descriptive sense**; it is not strong confirmation and does not authorize runtime use.

### 11X.6 Architectural implication

This experiment materially changes the residual problem.

Before UP-2, pooled 2022–2024 residual state was:
- 13 UP / 13 DOWN.

UP-2 removes:
- 8 UP;
- 3 DOWN.

The remaining downstream unresolved state becomes:
- **5 UP / 10 DOWN**, n=15.

So the DOWN share rises from 50.0% to **66.7%** before any DOWN specialist is applied.

Locked 2025:
- original residual: 35 UP / 39 DOWN;
- UP-2 removes 13 UP / 12 DOWN;
- remaining: **22 UP / 27 DOWN**, n=49;
- DOWN share rises from 52.70% to **55.10%**.

Thus the first missed-UP specialist does make the downstream direction problem cleaner pre-2025, although the 2025 improvement is modest.

### 11X.7 Binding interpretation

The first residual UP-2 experiment is **promising research evidence**, not production authority.

What is now supported:
- the residual state contains a recoverable missed-UP subpopulation;
- a one-sided specialist can identify a selective portion of it;
- pre-2025 evidence is materially stronger than the earlier route-consistent CBR DOWN evidence.

What is not yet supported:
- runtime promotion;
- treating every UP2 as production VERIFIED UP without further validation;
- assuming 2025 discrimination is strong;
- replacing the frozen primary UP Verifier V2.

The next research lane should preserve this exact role separation. A second method may now be tested against the same residual UP-2 task, or the downstream resolver may be reevaluated **only after** a separately preregistered cascade study that inserts this frozen UP-2 stage.

No result-dependent retuning of V1 is authorized.

---


## 11Y. Residual local-competence UP-2 DES — no eligible local expert signal

**Identity:** `RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESEARCH`  
**Research branch:** `gold-residual-up2-local-des-v1-20260923`  
**Preregistration commit:** `891f8547ea1dec3a6bea2d57d4ae6d5e926fe4af`  
**Implementation commit:** `54a686e5a25bd4e87a10a546f22eb68f9c119eff`  
**Workflow commit:** `5ded2d6d02f530b733afe0e986a4ea27734e2a39`  
**Frozen result commit:** `784772258570b74a439e11cb7351da94b0d5b296`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESULT_2026-09-23.json` (Git blob SHA `c7e0baaeb80c09660fdadc069219918284ffb477`)  
**Status:** `RESIDUAL_LOCAL_DES_V1_NOT_SUPPORTED / RESEARCH_ONLY / NOT_RUNTIME`.

### 11Y.1 Role and method

This experiment tested the second prespecified residual-UP idea: dynamic/local expert selection after

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`.

Candidate pool was fixed to the same five direct UP experts used by Router V2:

- TTSM-S2;
- TTSM-S1;
- Bonato AR1_RM QBoost h=1;
- AR1_RM_LOGIT;
- RM_LOGIT.

For each residual target case, the method:

1. standardized the nine frozen residual-state variables on prior matured residual history only;
2. selected the fixed K=25 nearest historical residual neighbours;
3. measured each currently-UP expert's competence inside those neighbours;
4. required at least 5 local UP calls, local precision >50%, local FPR <50%, and one-sided 90% Wilson precision LCB >50%;
5. emitted UP2_DES only if at least one expert passed all local gates.

No global fallback was allowed.

### 11Y.2 Integrity

All source and route checks passed exactly.

Residual populations reproduced:
- external 2020–2021: 98 =46 UP +52 DOWN;
- pooled governed 2022–2024: 26 =13 UP +13 DOWN;
- locked 2025: 74 =35 UP +39 DOWN.

The same raw-feature harmonization gate from UP-2 Logit V1 passed:
- representable overlap n=344;
- lag-1 return sign agreement 90.99%;
- all six source-derived feature correlations >=0.90.

Final integrity errors: **none**.

### 11Y.3 Result

The local DES emitted **zero** UP2_DES calls in every evaluated year:

- 2022: 0/11;
- 2023: 0/2;
- 2024: 0/13;
- pooled 2022–2024: **0/26**;
- locked 2025: **0/74**.

Thus:
- pre-2025 recall =0%;
- coverage =0%;
- no precision can be estimated;
- frozen pre-2025 gate fails immediately because calls <4.

Locked 2025 also produces zero calls and is not supportive.

### 11Y.4 Why the method abstained

The zero-call result is not caused by missing direct-expert UP votes. Many residual rows still have current UP votes from AR1_RM_LOGIT, RM_LOGIT and sometimes Bonato.

The problem is their **local historical competence** inside the residual state.

Representative 2022 rows show:
- AR1_RM_LOGIT / RM_LOGIT often vote UP on nearly all 25 local neighbours;
- local precision is commonly around 44–56%;
- because almost every local DOWN neighbour is also called UP, local false-UP FPR is commonly roughly 0.8–1.0;
- Wilson lower bounds therefore remain below the frozen eligibility threshold even when raw precision slightly exceeds 50%.

One representative residual case had RM_LOGIT local precision 65.2% with Wilson LCB 51.9%, but local false-UP FPR was still 80%, so it correctly remained ineligible.

Thus the retained direct experts are not locally selective enough in the **post-primary-Router residual population**.

### 11Y.5 Comparison with One-Sided Logit UP-2 V1

Pooled 2022–2024:

- One-Sided Logit V1: 11 calls, 8 true UP / 3 false UP, precision 72.73%, recall 61.54%, FPR 23.08%, coverage 42.31%;
- Local DES V1: 0 calls, recall 0%, coverage 0%.

Locked 2025:

- One-Sided Logit V1: 25 calls, 13 true UP /12 false UP, precision 52.0%, recall 37.14%, FPR 30.77%;
- Local DES V1: 0 calls.

This comparison is descriptive only. No automatic combination or result-dependent relaxation of DES gates is authorized.

### 11Y.6 Binding interpretation

Dynamic local selection of the **existing five direct UP experts** does not solve the missed-UP problem under the preregistered support and safety rules.

The result is informative: after the primary Router has abstained, the surviving direct experts still vote UP frequently, but those votes are not sufficiently selective in local residual neighbourhoods.

Therefore:

- do not tune K, local-call minimum, FPR limit or Wilson threshold under the same identity;
- do not add a global fallback after seeing this result;
- retain One-Sided Logit UP-2 V1 as the only currently promising second-stage UP specialist;
- proceed, if desired, to the third prespecified residual-UP family: a **trajectory / rebound morphology specialist** built to distinguish stress-to-rebound from stress-to-continuation directly, rather than recycling the same direct expert votes.

---


## 11Z. Residual trajectory/rebound morphology UP-2 — pre-2025 gate fails despite cleaner locked-2025 transport

**Identity:** `RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESEARCH`  
**Research branch:** `gold-residual-up2-trajectory-morph-v1-20260923`  
**Preregistration commit:** `6ec8051501fcee6ea9a6f38b5bab434824f31bab`  
**Implementation commit:** `57ad11ff6e358122c620f99632c6e53377da6220`  
**Workflow commit:** `2ca759c80fd33bdcb0da9bbe906bec950db5fd2e`  
**Frozen result commit:** `cee7fadff9490a667716520ed0c9479932e5c41e`  
**Frozen result artifact:** `gold_axis_2026/GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESULT_2026-09-23.json` (Git blob SHA `f44e005221b55682d5ab0705f28173232de09b4b`)  
**Status:** `RESIDUAL_TRAJECTORY_UP2_V1_NOT_SUPPORTED / RESEARCH_ONLY / NOT_RUNTIME`.

### 11Z.1 Role

This was the third prespecified missed-UP family for the residual state:

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`.

Unlike Local-DES, it does not recycle direct-expert votes. Unlike the first One-Sided Logit V1, it deliberately removes SQRT/context/expert-disagreement features and tests only the completed origin-day trajectory geometry.

Eight frozen morphology features were used:
- downside semivariance share;
- normalized maximum drawdown;
- trough position in the session;
- recovery-to-close ratio;
- close location;
- normalized post-trough return;
- normalized final-quarter return;
- post-trough positive-return fraction.

Classifier:
- L2 logistic regression, C=1.0, lbfgs;
- same chronological one-sided threshold rule:
  `tau=max(0.50, q80 of strictly prequential historical DOWN scores)`.

No feature or threshold sweep was performed.

### 11Z.2 Integrity

All route and source checks passed.

Exact residual populations reproduced:
- external 2020–2021: 98 =46 UP +52 DOWN;
- governed 2022–2024: 26 =13 UP +13 DOWN;
- locked 2025: 74 =35 UP +39 DOWN.

Morphology source harmonization passed strongly:
- exact representable overlap n=345;
- median trough-position difference =0;
- downside-share correlation=0.9946;
- max-drawdown correlation=0.9984;
- trough-position correlation=0.9930;
- recovery-to-close correlation=0.9992;
- close-location correlation=0.9997;
- post-trough-return correlation=0.9993;
- last-quarter-return correlation=0.9986;
- post-trough-positive-fraction correlation=0.8729, above its frozen 0.85 gate.

Final integrity errors: **none**.

### 11Z.3 Pre-2025 chronological result

#### 2022
- n=11;
- UP2_MORPH calls=1;
- true UP=0;
- false UP=1;
- precision=0%;
- recall=0%;
- FPR=16.67%;
- AUC=0.6667;
- tau=0.5879.

#### 2023
Only two rows:
- one UP call;
- one true UP;
- zero false UP.

This sample is too small to carry independent authority.

#### 2024
- n=13;
- calls=2;
- true UP=1;
- false UP=1;
- precision=50%;
- recall=14.29%;
- FPR=16.67%;
- AUC=0.5952.

#### Pooled 2022–2024
- n=26 =13 UP +13 DOWN;
- calls=4;
- true UP=2;
- false UP=2;
- precision=**50.00%**;
- missed-UP recall=**15.38%**;
- false-UP FPR=**15.38%**;
- coverage=15.38%;
- Wilson90 LCB precision=23.02%;
- AUC=0.6095.

The frozen gate required precision >50% and Wilson90 LCB >50%. Both failed.

Therefore:

`PRE2025_RESIDUAL_TRAJECTORY_UP2_SIGNAL = FALSE`.

### 11Z.4 Locked 2025 transport

Unchanged V1 on locked 2025:

- n=74;
- calls=13;
- true UP=8;
- false UP=5;
- precision=**61.54%**;
- missed-UP recall=22.86%;
- false-UP FPR=**12.82%**;
- coverage=17.57%;
- Wilson90 LCB precision=43.90%;
- AUC=0.5648;
- tau=0.5879.

This is descriptively cleaner than the first One-Sided Logit V1 in 2025:
- Morphology: 61.54% precision, 12.82% FPR, 17.57% coverage;
- One-Sided Logit V1: 52.0% precision, 30.77% FPR, 33.78% coverage.

However 2025 is locked transport and cannot rescue the failed pre-2025 gate.

### 11Z.5 Comparison of the three residual-UP methods

Pooled 2022–2024:

- **One-Sided Logit V1:** 11 calls, 8 true /3 false, precision 72.73%, recall 61.54%, FPR 23.08%;
- **Local-DES V1:** 0 calls;
- **Trajectory Morphology V1:** 4 calls, 2 true /2 false, precision 50.0%, recall 15.38%, FPR 15.38%.

Locked 2025:

- **One-Sided Logit V1:** 25 calls, 13 true /12 false, precision 52.0%, recall 37.14%, FPR 30.77%;
- **Local-DES V1:** 0 calls;
- **Trajectory Morphology V1:** 13 calls, 8 true /5 false, precision 61.54%, recall 22.86%, FPR 12.82%.

### 11Z.6 Binding interpretation

Pure origin-day rebound morphology is **not validated** as the second-stage UP specialist because it fails the pre-2025 gate.

The result nevertheless contains a useful transport clue:
- in locked 2025, morphology is much more selective than One-Sided Logit V1;
- but the pre-2025 evidence is too weak to authorize choosing it or combining it post hoc.

Therefore:
- One-Sided Logit UP-2 V1 remains the only residual-UP method that passed its frozen pre-2025 gate;
- Local-DES V1 remains unsupported;
- Trajectory Morphology V1 remains unsupported;
- no post-result hybrid, OR-rule, AND-rule, threshold change, or feature recombination is authorized under these identities.

A future method may use a new preregistered identity if there is a principled reason to combine stable morphology with the broader state/context information from Logit V1, but the current results themselves cannot be used to tune such a combination.

---


## 11ZA. Independent UP-2 integrity and economic arithmetic audit — PASS

**Identity:** `UP2_INDEPENDENT_INTEGRITY_ECON_AUDIT_V1_RESEARCH`  
**Research branch:** `gold-up2-independent-integrity-audit-v1-20260923`  
**Preregistration commit:** `00e195103d122e9033896ab09b70791ebe44494d`  
**Implementation commit:** `d31cd9a9a2b77400b0807d469ec6bdd9d14a15ca`  
**Workflow commit:** `bae723bf6e97e0a22aada01e0f87fdc2135b64bf`  
**Frozen audit result commit:** `a254f088144343dde8a2184084286f26312c8d6a`  
**Frozen audit artifact:** `gold_axis_2026/GOLD_CONTROL_UP2_INDEPENDENT_INTEGRITY_ECON_AUDIT_V1_RESULT_2026-09-23.json` (Git blob SHA `af7f09f0a18185917634f2f0a56f9e0d06bdf2e4`)  
**Status:** `AUDIT_PASS`.

Independent checks did not reuse the prior assistant arithmetic. The audit read the frozen UP-2 ledger, frozen SQRT parent, and independently reconstructed governed daily closes from the read-only 5-minute research table.

Results:
- ledger rows=100; unique origin/target pairs=100;
- no chronology, label, call-rule or metric mismatch;
- maximum absolute difference between frozen parent log return and independently reconstructed DB close-to-close log return = `3.469446951953614e-18`;
- maximum simple-return difference = exactly `0.0`;
- every `actual_up` equals the sign of the independently reconstructed return;
- every `up2_call` equals the frozen rule `p_up > tau`;
- annual and pooled confusion metrics exactly reproduce the frozen UP-2 result.

Independent DB-close economic arithmetic reproduces:
- 2022: gross correct-UP gain 7.0022%, false-UP loss 5.1922%, fixed-notional net +1.8100%;
- 2023: +2.7395% net;
- 2024: +2.8987% net;
- pooled 2022–2024: gross correct-UP gain 12.6404%, false-UP loss 5.1922%, fixed-notional net +7.4482%, compounded call-only return +7.5058%;
- locked 2025: gross correct-UP gain 16.1438%, false-UP loss 7.9752%, fixed-notional net +8.1686%, compounded call-only return +8.2311%.

Missed UP/DOWN values remain opportunity costs under a flat-on-ABSTAIN assumption, not realized losses. These figures are not whole-cascade or whole-portfolio P&L and exclude fees, spread, slippage and leverage.

This audit supports the correctness of the frozen ledger labels, signal rule and previously reported arithmetic. It does not remove model-risk/generalization uncertainty, especially the weaker locked-2025 discrimination of One-Sided UP-2 Logit V1.

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

Gold Control currently has one promising residual-UP method and two unsupported alternatives.

1. **SQRT-HAR-DR** — frozen downside-risk motor.
2. **Frozen UP Verifier V2** — primary selective positive-UP authority.
3. **Residual One-Sided UP-2 Logit V1** — promising research-only missed-UP specialist; it is the only residual-UP method that passed its frozen pre-2025 gate.
4. **Residual Local-Competence UP-2 DES V1** — unsupported; zero eligible calls.
5. **Residual Trajectory/Rebound Morphology UP-2 V1** — unsupported because pooled pre-2025 precision was only 50%, despite a cleaner locked-2025 transport result.
6. **Positive DOWN resolver** — still not validated; remaining unresolved cases stay UNCERTAIN.

The strongest pre-2025 residual-UP evidence remains One-Sided Logit V1:
- pooled 2022–2024: 11 calls =8 true UP +3 false UP;
- precision 72.73%;
- missed-UP recall 61.54%;
- false-UP FPR 23.08%;
- AUC 0.787;
- Wilson90 LCB precision 53.45%.

Its weakness remains locked 2025:
- precision 52.0%;
- recall 37.14%;
- FPR 30.77%;
- AUC 0.5165.

Trajectory Morphology V1 shows the opposite pattern:
- weak pre-2025 evidence: 4 calls =2 true +2 false, 50% precision;
- cleaner locked 2025 transport: 13 calls =8 true +5 false, 61.54% precision, 12.82% FPR.

Because 2025 is locked transport, that later performance cannot be used to select Morphology V1 over the pre-2025-supported Logit V1, nor to create a post-hoc hybrid.

The route-consistent CBR-DTW remains a DOWN research baseline only, not VERIFIED-DOWN authority. Its false-DOWN mistakes are not automatically repaired by the primary UP verifier at the immediately following origin.

The next clean research step should not tune the three completed residual-UP identities. It should either:
- preregister a genuinely new residual-UP method motivated independently of these outcomes; or
- freeze the supported One-Sided Logit UP-2 V1 as a research-stage second filter and run a new cascade study that reevaluates the downstream DOWN resolver only on the rows left after UP-2.

No automatic ensemble, BUY/SELL mapping, runtime promotion, 2025 retuning or 2026 model selection is authorized.
