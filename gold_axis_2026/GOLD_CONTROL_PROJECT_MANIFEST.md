# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.62  
**Issue date:** 2026-09-17  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Current research branch:** `gold-bocpd-hourly-b2-selective-20260916`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the **only current Gold Control project manifest**.

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control architecture, model roles, data chronology, validation governance, research sequencing, frozen challenge definitions and promotion rules.

Contracts, preregistrations, design notes, checkpoints, reports, event inventories, run artifacts, historical handovers and audit outputs are subordinate to this manifest. If a subordinate artifact conflicts with this manifest, the current manifest wins once the corresponding manifest change is accepted on the governed branch.

Authority split:

- **GitHub:** current code, frozen model/feature/source contracts, reproducibility and this manifest.
- **Production Neon:** mutable source observations, point-in-time lineage, append-only runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail may remain in Git history or immutable audit storage, but historical model scores do not define current project authority.

Gold Control is a **decision-support and research system, not an autonomous trading system**.

---

## 2. Current top-level architecture

Gold Control has **two parallel primary lines**. They may exchange role-preserving context but they are not one homogeneous model-selection pool.

### 2.1 Monthly H=1 price-level forecasting — ACTIVE AND INDEPENDENT

The monthly programme forecasts the next calendar month's XAU/USD price level from the previous completed month-end information boundary.

Current monthly H=1 expert identities:

- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

`MONTHLY_DIRECTION_3M` remains a strategic monthly direction/prior context.

The monthly H=1 line remains a standalone forecast output regardless of GC-BREAK research progress.

### 2.2 Short-term GC-BREAK — SEQUENTIAL TREND-HEALTH / BREAK EARLY WARNING

The current short-term problem is **not fixed-horizon 1D/3D direction prediction**.

Binding state ontology:

`STABLE -> WEAKENING -> BREAK_ALERT -> CONFIRMED_BREAK -> NEW_REGIME`

Recovery transitions are permitted, including `WEAKENING -> STABLE`, `BREAK_ALERT -> STABLE` or a lower warning state, and later stabilization of a new regime.

Primary short-term questions are warning lead time, false-warning burden, missed breaks, confirmation delay, regime stabilization and recovery behavior.

`NEXT_NY17_1D`, `NEXT_NY17_3D`, standalone 1D/3D directional accuracy and fixed-horizon break-risk are historical research targets only and may not silently re-enter the architecture.

---

## 3. Governed runtime registry versus current research activity

The governed runtime registry contains exactly **11 identities**. Runtime registration does **not** mean every identity is currently active in the GC-BREAK research sequence.

### 3.1 Governed runtime registry

1. `CAUSAL_PATCH`
2. `VW_MIDAS_MSVR_SUCCESSOR_V1`
3. `MOMENTUM_3M`
4. `RANDOM_WALK`
5. `MONTHLY_DIRECTION_3M`
6. `FAST`
7. `SLOW`
8. `MACRO_EVENT_SUCCESSOR_V2`
9. `EMERGENCY_LEVEL`
10. `EMERGENCY_REVERSAL`
11. `GVZ_RISK`

No additional research channel becomes a governed runtime identity without explicit promotion and manifest change control.

### 3.2 Current GC-BREAK research activity status

The current research-status layer is binding for work sequencing and must not be confused with the runtime registry above.

| Identity / lane | Current research status | Binding interpretation |
|---|---|---|
| `FAST` | `EVALUATED / RETAINED_TACTICAL_CONTEXT` | 2025 full-timeline replay complete; not proven standalone volatility-warning engine |
| `GVZ_RISK` | `EVALUATED / RETAINED_RISK_CONTEXT` | 2025 full-timeline historical replay complete; risk/severity only, no direction vote |
| `BOCPD` research lane | `EVALUATED / RETAINED_RESEARCH_REFERENCE` | only V5 + R2 remain authoritative; BOCPD is retained as regime/change context, not as the next standalone future-change-time predictor |
| Post-BOCPD future-change-time lane | `NEXT_RESEARCH_LANE / PREREGISTRATION_REQUIRED` | separately named residual-time / explicit-duration / Bayesian online changepoint-prediction challenger; exact identity and parameters must be frozen before implementation |
| `MACRO_EVENT_SUCCESSOR_V2` | `SUSPENDED_FOR_CURRENT_GC_BREAK_RESEARCH_SEQUENCE` | governed runtime identity remains registered, but it is **not the next motor** and no new Macro Event tuning/evaluation is authorized in the current sequence |
| `MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE` | `FROZEN_RESEARCH_CHALLENGER / NOT_RUNTIME_AUTHORITY` | historical preregistration remains audit lineage; not promoted and not the current workstream |
| `EMERGENCY_LEVEL` | `SUSPENDED / REDESIGN_REQUIRED` | do not treat as next motor until separately redesigned/preregistered |
| `EMERGENCY_REVERSAL` | `SUSPENDED` | do not treat as next motor until separately re-authorized |
| `SLOW` | `LOW_PRIORITY / NOT_NEXT` | valid confirmation/new-regime context but not the immediate research priority |
| Monthly H=1 line | `ACTIVE_INDEPENDENT` | continues separately from GC-BREAK motor sequencing |

**Important:** suspension here is a research-sequencing status. It does not erase historical runtime identities, old contracts or Git history, and it does not promote a replacement automatically.

The binding post-BOCPD scientific direction is **not another ordinary BOCPD threshold/hazard retune** and is not Macro Event, GVZ, Emergency or SLOW. The next research lane is a separately named **future change-time prediction** motor in the residual-time / explicit-duration / Bayesian online prediction of changepoints family. Its exact implementation is not pre-approved; it requires preregistration using pre-2025 chronology before any new outcome inspection.

---

## 4. BOCPD research authority — exactly two retained identities

The active BOCPD research authority contains exactly **two** identities:

1. `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — **primary BOCPD research model**.
2. `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — **frozen comparison baseline only**.

No other BOCPD identity is active authority. Raw hourly Candidate B, earlier optimized B2 identities, daily Candidate A, monthly `BOCPD_RETURN_SUCCESSOR_V1`, duration/residual V2, robust-clipped V3, duration+robust V4 and other superseded BOCPD experiments are historical only. Their active model-code/result/workflow surfaces are removed from the current research branch; Git history may retain them solely for audit traceability.

The **only authoritative BOCPD model surfaces** on the active research branch are:

- code: `gold_axis_2026/tools/bocpd_hourly_b2_adaptive_hazard_pre2025.py`;
- code: `gold_axis_2026/tools/bocpd_hourly_b2_baseline_r2_pre2025.py`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_ADAPTIVE_HAZARD_V5_PRE2025_RESULT_2026-09-16.md`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_BASELINE_R2_PRE2025_RESULT_2026-09-17.md`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-adaptive-hazard-pre2025-20260916.yml`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-baseline-r2-pre2025.yml`.

Any other BOCPD-named model code, model result or model workflow present on the active research branch is non-authoritative and must be removed or separately re-authorized by manifest change control.

The retained hourly input series is `XAU_USD_TWELVE_1H_RESEARCH_V1`. It is **research-only** and does not replace canonical `XAU_EOD_TWELVE_NY17` runtime semantics.

Neither retained BOCPD identity is a governed runtime or production engine. V5 is the active research reference; R2 is its benchmark. Neither emits an equal-weight direction vote.

### 4.1 BOCPD chronology

Binding chronology for both retained BOCPD identities:

- **2022:** research formation, hour-of-day normalization and prior formation;
- **2023:** development and parameter selection;
- **2024:** pre-2025 chronological retrospective comparison, not a pristine untouched holdout because BOCPD programme-level 2024 evidence had already been seen;
- **2025:** prohibited for tuning/model selection in the retained line and not queried/accessed by the V5/R2 pre-2025 model scripts.

The 2022 hourly history is accepted as **sufficient high-coverage research formation data for this phase**. This manifest does not claim that every theoretically expected 2022 market-hour slot has been independently completeness-certified.

### 4.2 BOCPD pre-2025 auxiliary comparison

`BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` on the 2024 auxiliary abnormal-volatility comparison:

- 57 episodes;
- 12 matched episodes;
- 45 unmatched episodes;
- 11 / 17 events captured;
- precision `0.210526`;
- recall `0.647059`;
- F0.5 `0.243363`.

`BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` on the same 2024 comparison:

- 65 episodes;
- 15 matched episodes;
- 50 unmatched episodes;
- 14 / 17 events captured;
- precision `0.230769`;
- recall `0.823529`;
- F0.5 `0.269576`.

These are **auxiliary abnormal-daily-volatility metrics**, not structural GC-BREAK precision/recall. V5 improves event coverage, precision, recall and F0.5 relative to R2 under the same comparison, but false-warning burden remains material. No runtime/production promotion is authorized.

Any future BOCPD successor requires a separately named preregistration/change-control step. The next future-change-time lane is a **separate model identity**, not a silent V6 retune of V5.

---

## 5. Role-preserving multi-clock architecture

Heterogeneous engines must not be flat-voted or ranked as though they solve the same task.

### Strategic block

- Monthly H=1 experts: independent price-level forecast plus strategic anchor/context.
- `MONTHLY_DIRECTION_3M`: slow strategic prior; not a daily trigger.

### Trend-structure block

- **FAST:** tactical daily trend state, flip, age and persistence; candidate early weakening evidence.
- **SLOW:** completed-week trend confirmation, alignment/conflict and state age; confirmation/new-regime evidence, currently low priority.

Frozen FAST rule:

- SMA20;
- current and previous completed daily state relative to SMA20;
- both UP -> `ROBUST_UP`;
- both DOWN -> `ROBUST_DOWN`;
- otherwise `MIXED`;
- exactly two-day persistence.

Frozen SLOW rule:

- completed W-FRI weekly closes;
- incomplete current week excluded;
- SMA4;
- previous and current completed week on same side -> `ROBUST_UP` / `ROBUST_DOWN`;
- otherwise `NOT_YET_ROBUST`;
- exactly two completed-week persistence.

### Regime / stress / risk block

- `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH`: primary hourly BOCPD research context; causal adaptive hazard from run length and lagged volatility; no equal direction vote.
- `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH`: frozen constant-hazard benchmark only.
- `GVZ_RISK`: retained options-implied gold-market risk/severity context only; never an equal direction vote and never silently converted into UP/DOWN.
- post-BOCPD future-change-time challenger: next research lane; must model prospective time-to-change / residual-time or equivalent explicit-duration hazard without reusing 2025 for tuning.
- `EMERGENCY_LEVEL`: **suspended / redesign required**.
- `EMERGENCY_REVERSAL`: **suspended**.
- realized volatility: retrospective uncertainty/severity/event context; never a predictor of the same realized event.
- chronology-safe optional VIX: risk context only.

### Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: governed release-aware event-surprise identity, but **suspended for the current GC-BREAK research sequence**.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around eligible events.

Historical Macro Event contracts remain audit lineage. Their existence does not make Macro Event the next work item.

### Reliability / meta block

Permitted evidence includes matured reliability, support count, evidence age, explicit missingness, missing reason, class-degeneracy flags and justified regime/event-conditional reliability.

`NO_SIGNAL` / abstention is valid when support is insufficient.

---

## 6. Native clocks, availability time and evidence age

The architecture is multi-clock by design:

- **GC-BREAK main origin:** daily completed reference origin;
- **FAST:** tactical completed-daily clock;
- **SLOW:** completed weekly clock;
- **BOCPD research (V5/R2):** eligible completed-hour XAU clock; output usable only after the corresponding one-hour bar is complete;
- **future change-time challenger:** native clock must be explicitly preregistered; no output may be credited before all inputs required at that origin are complete;
- **Monthly H=1 / Monthly Direction:** strategic monthly clock;
- **Macro Event / Market Shock:** event-triggered intraday clock when that research lane is active;
- **GVZ_RISK:** completed GVZ daily-close clock under the frozen R4.1 implementation.

A slower state may be carried forward only under its native-clock semantics and must carry explicit `age` / `state_age` information.

Missing channels may not be silently imputed as neutral or zero.

### 6.1 Binding signal-availability rule

A model output cannot be credited before the latest input needed to compute that output was actually available.

For completed-daily-close engines such as FAST and GVZ_RISK:

- a state calculated using date `t` close becomes usable only **after that close**;
- a volatility event realized during date `t` cannot be called an `EARLY_HIT` using a signal that itself requires date `t` close;
- same-date daily-close overlap is at most `SAME_EVENT_CONFIRM` / same-date diagnostic unless an earlier timestamp independently proves availability;
- genuine one-session-ahead warning comparison must use the latest completed engine origin strictly before the event session;
- no event date may be used to select which historical engine date is treated as the signal origin.

Each motor must declare its native decision time before outcome overlay.

---

## 7. Governance locks

Binding rules:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no automatic `BUY / SELL / HOLD / EXIT / REDUCE`
- no flat/equal-weight voting across heterogeneous engines
- no hindsight threshold tuning
- no random-split time-series validation
- no silent provider substitution
- no interpolation or forward-fill of missing canonical XAU session references
- no backdating of reconstruction/replay evidence
- no historical reconstruction relabelled as prospective evidence
- no target/future observation inserted into an earlier origin
- no challenge/stress result used to retune that locked challenge/stress evaluation
- no production forecast/decision authority write without explicit later authorization
- no stale context labelled fresh merely because an identity remains registered
- no fabricated state or feature when a historical channel is unavailable
- no rejected model family rescued by post-score tuning
- no same-day completed-close value labelled as a pre-event warning for an event already realized during that session
- no event-conditioned backward search presented as alarm precision, warning accuracy or false-warning performance
- no post-hoc warning horizon chosen because it makes 2025 results look better
- no suspended motor silently reactivated merely because historical code/contracts remain in GitHub
- no ordinary BOCPD retuning represented as future-change-time prediction without a separately named identity and preregistration

When evidence is absent or unproven, use `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, `BLOCKED`, `NOT_TESTABLE` or `INSUFFICIENT_SUPPORT` as appropriate.

---

## 8. Evidence classes and point-in-time semantics

Evidence classes remain separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin using information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is frozen/deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

For every historical origin, all features, model states and reliability estimates must respect information available at that origin. Later target observations, future price paths and later revisions are forbidden from predictor construction or model selection.

Historical reconstruction is never proof that a signal was actually issued live at that historical time.

---

## 9. Canonical XAU / NY17 contract

Canonical tactical XAU series:

`XAU_EOD_TWELVE_NY17`

Provider/input contract:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1min`;
- requested timezone: `America/New_York`;
- accepted bar: unique exact `16:59:00` source bar;
- accepted value: `close` after positive/range-valid OHLC checks;
- stored timestamp: corresponding 17:00 ET session boundary converted to UTC;
- fallback: none;
- interpolation: forbidden;
- forward-fill: forbidden;
- alternate-provider substitution: forbidden;
- official CME/EBS settlement/fixing claim: forbidden.

The Twelve Data value is Gold Control's internal NY17 reference, not an official CME settlement/fixing price.

Exact historical provider gaps remain gaps; a different bar may not be inserted into the canonical series merely to improve coverage.

---

## 10. Frozen GC-BREAK structural event-label rule

The primary GC-BREAK ground-truth event definition is engine-independent.

Binding rule:

- family: volatility-normalized directional change;
- daily log return;
- volatility scale: trailing 20 governed observations;
- sigma lagged one observation;
- primary threshold: `k = 3.0`;
- current regime extreme updated causally;
- break timestamp: first governed observation whose adverse move from the regime extreme reaches the frozen threshold;
- after an event, regime direction flips and the extreme resets to the event close.

`k = 2.5` is sensitivity-only and may not replace `k = 3.0` because a downstream model scores better.

FAST, SLOW, Monthly Direction, Emergency, BOCPD, GVZ, Macro Event, Market Shock and learned models may not define this structural ground truth.

---

## 11. Frozen 2025 volatility challenge

Authority file:

`gold_axis_2026/GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

Research event source:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

This source is research-only and does not replace canonical exact-16:59 NY17 runtime semantics.

Cross-check facts:

- 2025 governed research weekdays: **255**;
- same-day overlap with exact 16:59 one-minute cache: **197**;
- equal close values on same-day overlap: **197 / 197**;
- directly comparable daily-return pairs: **168**;
- return correlation: **1.000000**;
- mean absolute return difference: **0.000000 percentage points**;
- sign agreement: **168 / 168**.

Frozen event formula:

`r_t = 100 * ln(P_t / P_{t-1})`

`sigma20_t = sample standard deviation of the 20 immediately preceding governed daily log returns`

`z_t = r_t / sigma20_t`

Frozen tiers:

- **MAJOR:** `|z_t| >= 2.0`
- **EXTREME:** `|z_t| >= 3.0`

The frozen inventory contains **19 event-days**, of which **5 are EXTREME**, with **14 UP / 5 DOWN**:

1. `2025-02-10` UP `+2.3407`
2. `2025-02-14` DOWN `-2.2468`
3. `2025-02-18` UP `+2.1885`
4. `2025-03-13` UP `+2.1237`
5. `2025-04-04` DOWN `-3.3930` EXTREME
6. `2025-04-09` UP `+3.2185` EXTREME
7. `2025-04-10` UP `+2.3440`
8. `2025-07-21` UP `+2.0611`
9. `2025-08-01` UP `+2.5481`
10. `2025-09-02` UP `+2.6673`
11. `2025-09-22` UP `+2.6254`
12. `2025-09-29` UP `+2.3040`
13. `2025-10-06` UP `+2.7911`
14. `2025-10-13` UP `+2.5043`
15. `2025-10-16` UP `+2.9074`
16. `2025-10-17` DOWN `-2.0589`
17. `2025-10-21` DOWN `-4.1054` EXTREME
18. `2025-12-22` UP `+4.0174` EXTREME
19. `2025-12-29` DOWN `-6.6415` EXTREME

These dates are retrospective outcomes, not information available to a live motor before they occur.

### 11.1 Engine-first evaluation lock

The binding evaluation direction is **engine first, challenge overlay second**.

For every evaluated engine:

1. run/replay the engine across its complete eligible origin set on its native clock;
2. retain signals, abstentions, state transitions, episode onsets, persistence/age, missingness and blocked/not-testable states;
3. freeze the complete engine-output table before outcome overlay;
4. only then compute event coverage, false-warning burden, lead/lag, same-event confirmation and role-specific support;
5. do not choose warning horizon, carry window, threshold, score mapping or episode rule after viewing challenge outcomes;
6. retain exact engine signal dates even when no event is nearby.

Event-conditioned backward lookup alone is diagnostic and is not alarm-performance evidence.

---

## 12. Current validated motor evidence

### 12.1 FAST

Evidence class: `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`.

- complete 2025 governed timeline: **255 daily rows**;
- frozen rule: SMA20 + two completed-daily observations on the same side;
- new robust episode onsets: **22**;
- descriptive same-direction future-event incidence after onset: 1-day `1/22`, 3-day `2/22`, 5-day `3/22`, 10-day `5/22`;
- same-event day `1/22` is not early-warning credit under completed-close semantics.

FAST is retained as a **daily tactical trend-state engine** and is not proven as a standalone volatility-warning engine.

### 12.2 GVZ_RISK

Role: **RISK_ONLY**. No UP/DOWN direction vote.

Frozen R4.1 mapping:

- `GVZ <= 25.9795` -> `NORMAL`, cap `1.0`;
- `25.9795 < GVZ <= 30.5238` -> `ELEVATED`, cap `0.5`;
- `GVZ > 30.5238` -> `PANIC`, cap `0.25`.

2025 historical replay facts:

- source: `GVZ_CBOE_FRED_MIRROR_RESEARCH_V1`;
- valid daily observations/scored rows: **250 / 250**;
- frozen-score mismatch: **0**;
- FAST used in score: **false for all rows**;
- `NORMAL`: **237** days;
- `ELEVATED`: **10** days;
- `PANIC`: **3** days.

Same-date overlap with a completed GVZ daily close is not credited as pre-event warning for an event already realized that date.

GVZ_RISK is retained as a **selective market-stress / risk-context motor**. General volatility-day prediction performance is not proven; the PANIC sample is too small for promotion claims.

### 12.3 BOCPD

See Section 4. The retained BOCPD research authority is V5 + R2 only. BOCPD is retained as regime/change context; it is not to be further tuned on visible 2025 outcomes as the project’s future-change-time predictor.

### 12.4 Macro Event

`MACRO_EVENT_SUCCESSOR_V2` remains a governed runtime registry identity, and historical V3/V4 research contracts remain traceable, but the Macro Event lane is **suspended for the current GC-BREAK research sequence**.

Do not interpret old Macro Event preregistrations, workflows or runtime registration as an instruction to resume it next. Reactivation requires explicit new project direction/change control.

### 12.5 Emergency and SLOW

- `EMERGENCY_LEVEL`: suspended / redesign required.
- `EMERGENCY_REVERSAL`: suspended.
- `SLOW`: low-priority confirmation/new-regime context; not the immediate next motor.

### 12.6 Next motor / future-change-time challenger

The next research motor is a **new, separately named future-change-time prediction challenger**. Its scientific family is residual-time / explicit-duration / Bayesian online prediction of changepoints or a closely equivalent causally valid duration-hazard formulation.

Binding design boundary:

- objective: estimate whether / when a break or changepoint is approaching, rather than only detect that a regime change may already have occurred;
- BOCPD V5 remains complementary regime/change context and is not silently renamed into this motor;
- formation/development must use pre-2025 chronology; 2025 is not available for parameter tuning or model selection;
- no random split;
- native clock, warning horizon, episode formation, output semantics and evaluation rule must be preregistered before outcome overlay;
- exact model identity and parameterization remain `NOT_FROZEN` until that preregistration is created.

---

## 13. Frozen research split

### Formation / development

`2022-01-01 .. 2024-12-31`

Permitted use: label-quality inspection, baseline development, rolling/prequential internal validation, calibration/reliability estimation and architecture development under frozen governance.

### Retrospective Challenge

`2025-01-01 .. 2025-12-31`

Locked retrospective challenge. No threshold, feature or model choice may be derived from its outcomes and then claimed as untouched challenge evidence.

### Retrospective Stress / transport

`2026-01-01 .. 2026-08-31`

Researcher-visible retrospective stress/transport period; not fresh blind OOS evidence.

### Prospective Shadow

Begins only after final architecture/parameter freeze and before future outcomes are known.

Random splitting is forbidden.

---

## 14. Current work-package and sequencing status

1. **Coverage / PIT audit — COMPLETE**
2. **WP0 — State / break-label contract — COMPLETE / FROZEN**
3. **WP1 — PIT-safe formation panel — COMPLETE**
4. **WP2 — independent break-event inventory — COMPLETE WITH DATA-DENSITY WARNING**
5. **Split Freeze — COMPLETE / PRE-SCORE FROZEN**
6. **WP3 — preregistered simple formation baselines — COMPLETE WITH LIMITATIONS**
7. **2025 volatility challenge inventory — FROZEN**
8. **FAST full-timeline replay — COMPLETE**
9. **GVZ_RISK full-timeline historical replay — COMPLETE**
10. **BOCPD retained research comparison — COMPLETE FOR CURRENT V5/R2 CHECKPOINT**
11. **Macro Event — SUSPENDED FOR CURRENT SEQUENCE**
12. **Emergency Level/Reversal — SUSPENDED; Level requires redesign**
13. **SLOW — LOW PRIORITY / NOT NEXT**
14. **Post-BOCPD future change-time challenger — NEXT RESEARCH LANE; exact identity/parameters require preregistration**
15. **WP4 role-preserving integration/state-transition work — AFTER the new challenger has a frozen design/evidence checkpoint**
16. **Architecture/parameter freeze — PENDING**
17. **Prospective shadow — PENDING FINAL FREEZE**

The next research lane is therefore **not inferred from runtime-registry order**. It is the separately governed future-change-time challenger defined in Section 12.6. Macro Event, Emergency and SLOW remain outside the immediate next step unless explicitly reactivated.

---

## 15. Post-BOCPD future model-development rule

Ordinary BOCPD is primarily an online **change-detection / regime-context** mechanism: after new evidence arrives, it updates belief that a change may have occurred. The next scientific question is different: whether the system can estimate **time-to-change / residual time / approaching-break hazard before the break**.

Accordingly, the next motor must be a separately named and preregistered future-change-time challenger. Preferred research families include:

- residual-time prediction under non-geometric duration models;
- explicit-duration / semi-Markov or duration-hazard formulations;
- Bayesian online prediction of changepoints / learned or structured time-to-change models;
- another low-dimensional causal duration-hazard formulation only if its role and timing semantics are explicitly frozen.

An HMM/HSMM may be used as an implementation family **only if it serves this frozen future-change-time objective**; `HSMM` by itself is not the binding motor identity and is not automatically selected.

The exact identity, features, native clock, duration state, horizon/output definition, loss/objective, episode rule and evaluation metrics must be preregistered before the model is run against outcomes used for evaluation.

Chronology lock for the new challenger:

- use 2022–2024 as the pre-2025 research/design universe under time ordering;
- do not use 2025 to choose thresholds, duration family, features, warning horizon or parameterization;
- 2025 is researcher-visible and cannot be relabelled as pristine holdout after design choices informed by it;
- no random split;
- BOCPD V5/R2, FAST and GVZ may contribute only in role-preserving origin-safe form; no flat equal vote.

High-capacity boosting, mixture-of-experts and deep-learning escalation remain blocked until a simpler duration/hazard challenger justifies additional complexity under time-ordered evidence.

---

## 16. Historical research interpretation

Historical fixed-horizon, 1D/3D, V1.48/V1.49, HS-SDL-DMA and related studies remain historical/auxiliary research only.

Old result files or artifact names are not current project authority. Historical traceability belongs in Git history and/or immutable evidence storage.

Specific superseded interpretation locks:

- old event-conditioned FAST `11/19` is not current alarm performance;
- same-date GVZ daily-close overlap is not early-warning evidence;
- any result that hides full-year engine outputs by starting only from realized event dates is invalid for alarm-performance claims;
- old Macro Event research artifacts do not override the current Macro research suspension;
- superseded BOCPD identities do not re-enter because historical files or commits exist;
- an ordinary BOCPD retune is not the approved substitute for the new future-change-time challenger.

---

## 17. Neon / write authority

GC-BREAK currently has **no production forecast, decision or trading authority**.

Unless separately authorized later:

- no production decision-signal writes;
- no BUY/SELL/action mapping;
- no automatic selector/ensemble writes;
- no mutation of legitimately issued historical records;
- no speculative schema expansion solely for an unaccepted research challenger.

Research panels, labels, predictions and evaluations must remain logically separated and lineage-complete.

Historical research backfills must use explicit research series identities and truthful provenance. They may not silently overwrite direct-authority series identities.

---

## 18. Promotion and prospective-evidence rule

Binding scientific order:

`PIT-safe formation`

-> `independent event inventories`

-> `engine-first full native-clock replay`

-> `freeze exact engine outputs and signal timestamps`

-> `outcome overlay`

-> `role-preserving evaluation`

-> `BOCPD context freeze`

-> `separately preregistered future-change-time challenger`

-> `role-preserving integration / state-transition work`

-> `same-origin ablation / optional extensions`

-> `architecture + parameter freeze`

-> `prospective shadow`

A model is not promoted because it is theoretically elegant or retrospectively impressive. Promotion requires reproducible, time-ordered incremental evidence with adequate support and no leakage.

The strongest future claim comes only from outcomes first observed after final architecture/parameter freeze.

---

## 19. Final binding summary

Gold Control is a **role-preserving, multi-clock sequential early-warning / regime-transition research programme** running in parallel with an independent monthly H=1 price-level forecasting programme.

Two distinct retrospective event universes are explicit:

1. frozen GC-BREAK structural-break labels;
2. frozen 2025 volatility challenge of 19 abnormal daily moves.

Current validated motor checkpoint:

- FAST: replay complete, retained tactical context, standalone volatility warning not proven;
- GVZ_RISK: replay complete, retained risk context, no direction vote;
- BOCPD: V5 primary research reference + R2 frozen benchmark only; retained as regime/change context;
- Macro Event: runtime registry identity retained but **current research lane suspended**;
- Emergency Level/Reversal: suspended, with Level requiring redesign;
- SLOW: low priority, not next.

The **next research motor/lane** is a new separately named **future-change-time prediction challenger** based on residual-time / explicit-duration / Bayesian online changepoint-prediction principles (or a causally equivalent preregistered duration-hazard formulation). Exact model identity and parameters are not yet frozen; the scientific lane is frozen. It must be designed with pre-2025 chronology and may not use visible 2025 outcomes for tuning.

All future work must preserve point-in-time integrity, native engine clocks, role semantics, engine-independent event definitions, time-ordered validation, explicit missingness and strict separation of retrospective diagnostics from genuine prospective evidence.
