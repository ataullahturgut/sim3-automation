# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.57  
**Issue date:** 2026-09-15  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the **only current Gold Control project manifest**.

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control architecture, model roles, data chronology, validation governance, research sequencing, frozen challenge definitions and promotion rules. No second Gold Control project manifest may be created.

Contracts, preregistrations, design notes, checkpoints, reports, event inventories, run artifacts, historical handovers and audit outputs are subordinate to this manifest. If any subordinate artifact conflicts with this manifest, the copy at the current canonical `gold-r4-direction-engine` HEAD wins.

Every new Gold Control session must first read the current canonical branch HEAD and this manifest before interpreting historical material.

Authority split:

- **GitHub:** current code, frozen model/feature/source contracts, reproducibility and this manifest.
- **Production Neon:** mutable source observations, point-in-time lineage, append-only runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail may remain in Git history or immutable audit storage, but historical model scores do not define current project authority.

This manifest stores **architecture, governance and frozen event/challenge definitions**; detailed model-result narratives and score tables belong outside the manifest.

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

The monthly H=1 line remains a standalone forecast output regardless of the outcome of GC-BREAK research. Monthly forecasts may provide strategic context only when derived features are origin-safe and empirically justified.

### 2.2 Short-term GC-BREAK — SEQUENTIAL TREND-HEALTH / BREAK EARLY WARNING

The current short-term research problem is **not** fixed-horizon 1D/3D direction prediction.

Binding state ontology:

`STABLE -> WEAKENING -> BREAK_ALERT -> CONFIRMED_BREAK -> NEW_REGIME`

Recovery transitions must also be permitted, including:

- `WEAKENING -> STABLE`
- `BREAK_ALERT -> STABLE` or a lower warning state when evidence recovers
- after `NEW_REGIME`, the new regime may become its own `STABLE` state

Primary short-term question:

> Is the current trend healthy, weakening, escalating toward a break, confirmed as broken, or settling into a new regime?

Primary performance questions:

- how early a true break is warned;
- how many false warning episodes are paid for that lead time;
- how many breaks are missed;
- how quickly a true break is confirmed;
- how stably a new regime is recognized;
- how often warnings recover correctly instead of forcing a false break.

`NEXT_NY17_1D`, `NEXT_NY17_3D`, standalone 1D/3D directional accuracy and fixed-horizon break-risk are historical research targets only. They are not current primary Gold Control short-term outputs and may not silently re-enter the architecture.

---

## 3. Governed runtime inventory

The governed runtime inventory contains exactly **12 identities**.

### Monthly H=1 price experts

1. `CAUSAL_PATCH`
2. `VW_MIDAS_MSVR_SUCCESSOR_V1`
3. `MOMENTUM_3M`
4. `RANDOM_WALK`

### Strategic / trend / event / regime / emergency / risk contexts

5. `MONTHLY_DIRECTION_3M`
6. `FAST`
7. `SLOW`
8. `MACRO_EVENT_SUCCESSOR_V2`
9. `BOCPD_RETURN_SUCCESSOR_V1`
10. `EMERGENCY_LEVEL`
11. `EMERGENCY_REVERSAL`
12. `GVZ_RISK`

No additional research channel becomes a governed runtime identity without explicit promotion and manifest change control.

Research-only channels may be evaluated without becoming runtime identities.

---

## 4. Role-preserving multi-clock architecture

Heterogeneous engines must not be flat-voted or ranked as though they solve the same task.

### Strategic block

- Monthly H=1 experts: independent price-level forecast plus strategic anchor/context.
- `MONTHLY_DIRECTION_3M`: slow strategic prior; not a daily trigger.

### Trend-structure block

- **FAST:** tactical daily trend state, flip, age and persistence; candidate early weakening evidence.
- **SLOW:** completed-week trend confirmation, alignment/conflict and state age; primarily confirmation/new-regime evidence.

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

- `BOCPD_RETURN_SUCCESSOR_V1`: change-point/regime context only; no equal direction vote.
- `EMERGENCY_LEVEL`: abnormal displacement context.
- `EMERGENCY_REVERSAL`: selective abnormal reversal/confirmation context.
- realized volatility: uncertainty/severity context.
- `GVZ_RISK` and chronology-safe optional VIX: risk, severity, uncertainty and possible abstention/veto context; never equal direction votes.

The frozen BOCPD identity remains on its native completed-month clock. A daily BOCPD requires a separately named research challenger.

### Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: release-aware event-surprise context at event time.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around eligible events.

Macro-event and Market-Shock evidence lives on an event-triggered intraday clock. Event windows or rules may not be changed after seeing challenge outcomes and then represented as frozen evidence.

### Reliability / meta block

Permitted evidence includes matured reliability, support count, evidence age, explicit missingness, missing reason, class-degeneracy flags and justified regime/event-conditional reliability.

`NO_SIGNAL` / abstention is a valid outcome when evidence support is insufficient.

---

## 5. Native clocks and evidence age

The architecture is multi-clock by design:

- **GC-BREAK main origin:** daily completed reference origin;
- **FAST:** tactical daily clock;
- **SLOW:** completed weekly clock;
- **BOCPD:** completed-month clock;
- **Monthly H=1 / Monthly Direction:** strategic monthly clock;
- **Macro Event / Market Shock:** event-triggered intraday clock.

A slower state may be carried forward only under its native-clock semantics and must carry explicit `age` / `state_age` information.

Missing channels may not be silently imputed as neutral or zero.

Historical evidence should carry, where applicable: `available_at`, source identity, lineage/fingerprint, state/evidence age and `missing_reason`.

---

## 6. Governance locks

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
- no stale context labelled fresh merely because an engine is `ACTIVE`
- no fabricated state or feature when a historical channel is unavailable
- no rejected model family rescued by post-score tuning

When evidence is absent or unproven, use `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, `BLOCKED`, `NOT_TESTABLE` or `INSUFFICIENT_SUPPORT` as appropriate.

---

## 7. Evidence and point-in-time semantics

Evidence classes remain separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin using information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is frozen/deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

For every historical origin, all features, model states and reliability estimates must respect information available at that origin. Later target observations, future price paths and later revisions are forbidden from predictor construction or model selection.

Late retrieval of a historically dated value does not make the row historically issued. Retrieval timestamps and lineage must remain truthful.

---

## 8. Canonical XAU / NY17 contract

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

Historical reconstruction must preserve the same source/bar semantics and may not be backdated or relabelled prospective.

Exact historical provider gaps remain gaps; a different bar may not be inserted into the canonical series merely to improve coverage.

---

## 9. Frozen GC-BREAK structural event-label rule

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

This structural event universe is separate from the 2025 volatility challenge below.

---

## 10. Frozen 2025 volatility challenge

Authority file:

`gold_axis_2026/GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

Purpose: evaluate how the 12 governed engines behave around materially abnormal **daily XAU/USD moves**, independently of the GC-BREAK structural-break labels.

### 10.1 Research source

Research event source:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Metadata:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- transform: `SELECT_16_00_AMERICA_NEW_YORK_HOURLY_CLOSE`;
- quality: `APPROVED_HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17`;
- 2025 weekday research observations: **255**.

This source is **research-only** and does not replace the canonical exact-16:59 NY17 runtime series.

The exact 1-minute historical provider probe contains many dates with `PROVIDER_NO_BAR`; those gaps remain unfilled in the canonical series.

On the 168 directly comparable 2025 daily-return pairs where both research and exact-16:59 series shared the same previous close date:

- return correlation = **1.000000**;
- mean absolute return difference = **0.000000 percentage points**;
- sign agreement = **168/168**.

### 10.2 Frozen event formula

`r_t = 100 * ln(P_t / P_{t-1})`

`sigma20_t = sample standard deviation of the 20 immediately preceding governed daily log returns`

`z_t = r_t / sigma20_t`

The current return is excluded from its own volatility estimate.

Frozen tiers:

- **MAJOR:** `|z_t| >= 2.0`
- **EXTREME:** `|z_t| >= 3.0`

EXTREME is a subset of MAJOR. Raw percentage return is descriptive only; a fixed raw `%2` rule is not the event definition.

Consecutive qualifying dates remain separate directional event-days in the primary evaluation.

### 10.3 Frozen 2025 event inventory

The frozen primary inventory contains **19 event-days**, of which **5 are EXTREME**:

1. `2025-02-10` UP — z `+2.3407`
2. `2025-02-14` DOWN — z `-2.2468`
3. `2025-02-18` UP — z `+2.1885`
4. `2025-03-13` UP — z `+2.1237`
5. `2025-04-04` DOWN — z `-3.3930` — EXTREME
6. `2025-04-09` UP — z `+3.2185` — EXTREME
7. `2025-04-10` UP — z `+2.3440`
8. `2025-07-21` UP — z `+2.0611`
9. `2025-08-01` UP — z `+2.5481`
10. `2025-09-02` UP — z `+2.6673`
11. `2025-09-22` UP — z `+2.6254`
12. `2025-09-29` UP — z `+2.3040`
13. `2025-10-06` UP — z `+2.7911`
14. `2025-10-13` UP — z `+2.5043`
15. `2025-10-16` UP — z `+2.9074`
16. `2025-10-17` DOWN — z `-2.0589`
17. `2025-10-21` DOWN — z `-4.1054` — EXTREME
18. `2025-12-22` UP — z `+4.0174` — EXTREME
19. `2025-12-29` DOWN — z `-6.6415` — EXTREME

Direction totals: **14 UP / 5 DOWN**.

### 10.4 Motor-evaluation lock

The event inventory is frozen **before** the new 12-engine replay. After engine results are inspected, the following may not be changed under this challenge identity:

- 2σ / 3σ thresholds;
- trailing-20 scale window;
- provider/source identity;
- event-day inclusion/exclusion;
- episode splitting/consolidation used for primary counts.

The same 19 event-days must be presented to all 12 governed identities, but each engine must be judged according to its native role. Permitted statuses include `EARLY_HIT`, `SAME_EVENT_HIT`, `CONFIRM`, `WRONG_DIRECTION`, `MISS`, `NO_SIGNAL`, `NOT_APPLICABLE`, `BLOCKED` and `NOT_TESTABLE`.

Macro Event non-event dates are not automatic misses; BOCPD/GVZ/Emergency/Monthly engines are not to be converted into flat daily direction voters.

This volatility challenge is `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC` evidence. It may be used to judge complementarity and model feasibility, but a model tuned after viewing 2025 may not claim the same 2025 period as untouched OOS validation.

### 10.5 Engine-first full-timeline evaluation lock

The binding 2025 motor-evaluation direction is **engine first, challenge overlay second**.

For every governed engine:

1. the independently frozen volatility inventory must not be passed into the engine as an input, scoring feature, threshold-selection target or origin filter;
2. first run/replay the engine over its **complete eligible 2025 origin set on its native clock**;
3. retain every output required to reconstruct what would have been observable at those origins, including signals, non-signals/abstentions, state transitions, new episode onsets, persistence/state age, missingness, `BLOCKED`, `NOT_TESTABLE` and `NOT_APPLICABLE` where role-appropriate;
4. for stateful engines, a continued state is not a new warning: new warning/episode onset and state persistence must be represented separately;
5. freeze the complete engine-output table before the 19 volatility event-days are overlaid for scoring;
6. only after that freeze may event-to-engine coverage, engine-to-event false-warning burden, lead/lag, same-event confirmation, direction relation and role-specific support be computed;
7. a calculation that starts only from realized volatility dates and looks backward at the engine is **event-conditioned diagnostics only** and may not by itself be reported as alarm precision, warning accuracy or false-warning performance;
8. non-native origins are not fabricated. For event-clock engines such as Macro Event, non-event dates are `NOT_APPLICABLE`; an event-time signal may not be silently carried forward across later days unless such persistence was separately preregistered before outcomes were inspected;
9. no warning-validity horizon, carry-forward window, threshold, score mapping or episode rule may be selected after 2025 outcomes to improve the same challenge result. A scientifically desired revision requires a separately named successor evaluation.

This rule applies to all remaining 2025 replays and supersedes any earlier challenge result that evaluated only the realized event dates while hiding the engine's full-year signal/output history.

---

## 11. Frozen research split

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

## 12. Current work-package status

1. **Coverage / PIT audit — COMPLETE**
2. **WP0 — State / break-label contract — COMPLETE / FROZEN**
3. **WP1 — PIT-safe formation panel — COMPLETE**
4. **WP2 — independent break-event inventory — COMPLETE WITH DATA-DENSITY WARNING**
5. **Split Freeze — COMPLETE / PRE-SCORE FROZEN**
6. **WP3 — preregistered simple formation baselines — COMPLETE WITH LIMITATIONS**
7. **WP4 — role-preserving sequential model — OPEN FOR A NEW SEPARATELY GOVERNED CHALLENGER**
8. **2025 volatility-challenge inventory — FROZEN; engine-first full-timeline role-preserving replay ACTIVE**
9. **Ablation / optional extensions — BLOCKED PENDING ACCEPTED CORE**
10. **Architecture/parameter freeze — PENDING**
11. **Prospective shadow — PENDING FINAL FREEZE**

Historical WP4A, WP4B and WP4D are rejected. Their detailed application scores and run IDs are intentionally not stored in this manifest.

A rejected family may not be retuned on challenge outcomes and reintroduced under the same identity.

---

## 13. Research eligibility by role

| Channel | Current eligibility | Binding interpretation |
|---|---|---|
| XAU price/trend | CORE | primary structural evidence |
| FAST | REPLAYABLE | tactical weakening evidence |
| SLOW | REPLAYABLE | confirmation/new-regime evidence |
| MONTHLY_DIRECTION_3M | REPLAYABLE | strategic context only |
| Emergency Level/Reversal | CONDITIONAL BY ORIGIN | selective context/confirmation; unavailable origin -> NOT_TESTABLE |
| BOCPD_RETURN_SUCCESSOR_V1 | NATIVE MONTHLY CLOCK | regime/change context only |
| Monthly H=1 experts | REPLAYABLE/PARTIAL BY ORIGIN | independent forecast + strategic context, not short-term trigger |
| Macro Event | ELIGIBLE EVENT ORIGINS | event-time surprise/context |
| Market Shock V3 | PARTIAL / RESEARCH-ONLY | realized event-shock extension |
| GVZ_RISK historical extension | PARTIAL | same-origin extension only unless PIT proof is complete |
| Other research experts | RESEARCH-ONLY UNTIL PIT PROVEN | no runtime authority without promotion |

Optional/short-history blocks must be compared against Core on the same eligible origins.

---

## 14. Evaluation principles

Simple preregistered baselines must precede complex learned promotion.

For GC-BREAK, primary metrics include break recall/miss rate, false-warning burden, warning lead time, confirmation delay, persistence, spurious flips, recovery behavior and proper scores where probabilities are emitted.

For the 2025 volatility challenge, each engine must additionally report role-appropriate event coverage, lead/lag, direction correctness where direction is actually emitted, abstention/NO_SIGNAL and PIT/missing limitations.

For the 2025 volatility challenge, both directions of accounting are required where the engine role permits them: **event -> engine** for coverage/miss/lead-lag and **engine -> event** for false-warning/selectivity burden. The complete engine-origin output table is the primary replay record; event-conditioned extracts are secondary views of that record.

Standalone direction accuracy is not the universal metric for heterogeneous engines.

Comparisons must be time-ordered, point-in-time safe and same-origin where eligibility differs.

---

## 15. WP4 / future model-development rule

WP4 remains open only for a **separately named and preregistered challenger**.

The project should prefer low-dimensional, role-preserving sequential transition/state-duration models before high-capacity alternatives.

A conceptual transition model may be expressed as:

`P(S_t = j | S_{t-1} = i, D_t, X_t)`

where `S_{t-1}` is prior state, `D_t` is duration/sojourn information and `X_t` contains role-preserving origin-safe evidence.

An explicit latent-state/state-duration HMM/HSMM challenger is scientifically eligible under a new preregistration, but is **not pre-approved**.

Boosting, mixture-of-experts and deep-learning escalation remain blocked until simpler challengers justify additional complexity under time-ordered evidence with adequate support.

The 2025 volatility replay may determine whether the 12 engines show useful complementarity. It may not be used to tune a combined model and then relabel the same 2025 evidence as untouched validation.

---

## 16. Historical research interpretation

Historical fixed-horizon, 1D/3D, V1.48/V1.49, HS-SDL-DMA and related studies remain historical/auxiliary research only.

They may inform scientific understanding where chronology-safe, but they do not override the GC-BREAK state ontology, current event-label rules, frozen split, native engine roles or current promotion governance.

Old result files or artifact names are not current project authority. Historical traceability belongs in Git history and/or immutable evidence storage.

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

---

## 18. Promotion and prospective-evidence rule

Binding scientific order:

`PIT-safe formation`

-> `independent event inventories`

-> `role-preserving engine evaluation`

-> `simple preregistered baselines`

-> `role-preserving sequential challenger`

-> `same-origin ablation / optional extensions`

-> `architecture + parameter freeze`

-> `prospective shadow`

A model is not promoted because it is theoretically elegant or retrospectively impressive. Promotion requires reproducible, time-ordered incremental evidence with adequate support and no leakage.

The strongest future claim comes only from outcomes first observed after final architecture/parameter freeze.

---

## 19. Final binding summary

Gold Control is a **role-preserving, multi-clock sequential early-warning / regime-transition research programme** running in parallel with an independent monthly H=1 price-level forecasting programme.

Two distinct retrospective event universes are now explicit:

1. the frozen GC-BREAK structural-break labels;
2. the frozen 2025 volatility challenge of 19 abnormal daily moves.

The governed 2025 motor procedure is engine-first: each of the 12 identities must first be replayed over its complete eligible 2025 native-clock origin set and its complete output history frozen; only then may the independent 19-event volatility inventory be overlaid. Event-conditioned backward lookup alone is not alarm-performance evidence.

Only after those role-preserving full-timeline replays may the project judge whether the engines provide enough complementary information to justify a new combined model research programme.

All future work must preserve point-in-time integrity, native engine clocks, role semantics, engine-independent event definitions, time-ordered validation, explicit missingness and strict separation of retrospective diagnostics from genuine prospective evidence.