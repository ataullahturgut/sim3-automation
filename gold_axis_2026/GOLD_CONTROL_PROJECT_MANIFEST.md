# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.58  
**Issue date:** 2026-09-16  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the **only current Gold Control project manifest**.

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control architecture, model roles, data chronology, validation governance, research sequencing, frozen challenge definitions and promotion rules. No second Gold Control project manifest may be created.

Contracts, preregistrations, design notes, checkpoints, reports, event inventories, run artifacts, historical handovers and audit outputs are subordinate to this manifest. If any subordinate artifact conflicts with this manifest, the current manifest wins once the corresponding manifest change is accepted on the governed branch.

Every new Gold Control session must first read the current governed manifest before interpreting historical material.

Authority split:

- **GitHub:** current code, frozen model/feature/source contracts, reproducibility and this manifest.
- **Production Neon:** mutable source observations, point-in-time lineage, append-only runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail may remain in Git history or immutable audit storage, but historical model scores do not define current project authority.

This manifest stores architecture, governance, frozen event/challenge definitions and concise validated result facts needed to prevent superseded interpretations from being reused. Detailed score tables and long result narratives remain subordinate artifacts.

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

Research-only successors may be evaluated without becoming runtime identities.

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
- realized volatility: retrospective uncertainty/severity/event context; never a predictor of the same realized event.
- `GVZ_RISK`: options-implied gold-market risk/severity context only; never an equal direction vote and never silently converted into UP/DOWN.
- chronology-safe optional VIX: risk context only.

The frozen BOCPD identity remains on its native completed-month clock. A daily BOCPD requires a separately named research challenger.

### Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: release-aware event-surprise context at event time.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around eligible events.

Macro-event and Market-Shock evidence lives on an event-triggered intraday clock. Event windows or rules may not be changed after seeing challenge outcomes and then represented as frozen evidence.

### Reliability / meta block

Permitted evidence includes matured reliability, support count, evidence age, explicit missingness, missing reason, class-degeneracy flags and justified regime/event-conditional reliability.

`NO_SIGNAL` / abstention is a valid outcome when evidence support is insufficient.

---

## 5. Native clocks, availability time and evidence age

The architecture is multi-clock by design:

- **GC-BREAK main origin:** daily completed reference origin;
- **FAST:** tactical completed-daily clock;
- **SLOW:** completed weekly clock;
- **BOCPD:** completed-month clock;
- **Monthly H=1 / Monthly Direction:** strategic monthly clock;
- **Macro Event / Market Shock:** event-triggered intraday clock;
- **GVZ_RISK:** completed GVZ daily-close clock under the frozen R4.1 implementation.

A slower state may be carried forward only under its native-clock semantics and must carry explicit `age` / `state_age` information.

Missing channels may not be silently imputed as neutral or zero.

Historical evidence should carry, where applicable: `available_at`, source identity, lineage/fingerprint, state/evidence age and `missing_reason`.

### 5.1 Binding signal-availability rule

A model output cannot be credited before the latest input needed to compute that output was actually available.

For completed-daily-close engines such as frozen FAST and frozen GVZ_RISK:

- a state calculated using date `t` close becomes usable only **after that close**;
- a volatility event realized during date `t` cannot be called an `EARLY_HIT` using a signal that itself requires date `t` close;
- same-date daily-close overlap is at most `SAME_EVENT_CONFIRM` / same-date diagnostic unless an independent earlier timestamp proves the engine output existed before the event;
- a genuine one-session-ahead early-warning comparison must use the latest completed engine origin strictly before the event session;
- no event date may be used to select which historical engine date is treated as the signal origin.

This availability rule is binding for all future motor evaluations. Each motor must declare its native decision time before outcome overlay.

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
- no same-day completed-close value labelled as a pre-event warning for an event that already occurred during that same session
- no event-conditioned backward search presented as alarm precision, warning accuracy or false-warning performance
- no post-hoc warning horizon chosen because it makes 2025 results look better

When evidence is absent or unproven, use `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, `BLOCKED`, `NOT_TESTABLE` or `INSUFFICIENT_SUPPORT` as appropriate.

---

## 7. Evidence and point-in-time semantics

Evidence classes remain separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin using information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is frozen/deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

For every historical origin, all features, model states and reliability estimates must respect information available at that origin. Later target observations, future price paths and later revisions are forbidden from predictor construction or model selection.

Late retrieval of a historically dated value does not make the row historically issued. Retrieval timestamps and lineage must remain truthful.

A historical daily close with a truthful observation date may be used in a retrospective replay at or after its close, but such reconstruction is still `HISTORICAL_REPLAY`, not proof that the signal was actually issued live at that historical time.

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

Purpose: evaluate how governed engines behave around materially abnormal **daily XAU/USD moves**, independently of the GC-BREAK structural-break labels.

### 10.1 Research event source

Research event source:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Metadata:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- transform: `SELECT_16_00_AMERICA_NEW_YORK_HOURLY_CLOSE`;
- quality: `APPROVED_HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17`;
- 2025 governed weekday research observations: **255**;
- weekend observations used: **0**.

This source is **research-only** and does not replace the canonical exact-16:59 NY17 runtime series.

The exact 1-minute historical provider probe contains many dates with `PROVIDER_NO_BAR`; those gaps remain unfilled in the canonical series.

Correct cross-check facts:

- same-day 2025 overlap with the exact 16:59 one-minute cache: **197 weekdays**;
- equal close values on that same-day overlap: **197 / 197**;
- directly comparable daily-return pairs requiring both current and previous dates in both sources: **168**;
- return correlation on those 168 pairs: **1.000000**;
- mean absolute return difference: **0.000000 percentage points**;
- sign agreement: **168 / 168**.

The 197 close-overlap count and 168 return-pair count measure different things and must not be substituted for each other.

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

The 19 dates are **outcomes / retrospective challenge events**, not information available to a live motor before those dates occur.

### 10.4 Motor-evaluation lock

The event inventory is frozen independently of motor outputs. After engine results are inspected, the following may not be changed under this challenge identity:

- 2σ / 3σ thresholds;
- trailing-20 scale window;
- provider/source identity;
- event-day inclusion/exclusion;
- episode splitting/consolidation used for primary counts.

The same 19 event-days may be overlaid onto governed identities, but each engine must be judged according to its native role and native decision time. Permitted statuses include `EARLY_HIT`, `SAME_EVENT_HIT`, `CONFIRM`, `WRONG_DIRECTION`, `MISS`, `NO_SIGNAL`, `NOT_APPLICABLE`, `BLOCKED` and `NOT_TESTABLE`.

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
9. no warning-validity horizon, carry-forward window, threshold, score mapping or episode rule may be selected after 2025 outcomes to improve the same challenge result. A scientifically desired revision requires a separately named successor evaluation;
10. every engine must state the timestamp at which its output becomes usable. Completed-close output on date `t` cannot be credited as an early warning for an event already realized during date `t`;
11. exact engine signal dates must be retained even when no volatility event is nearby. They may not be filtered out because they are inconvenient to the result.

This rule applies to all remaining 2025 replays and supersedes any earlier challenge result that evaluated only realized event dates while hiding the engine's full-year signal/output history.

### 10.6 FAST — corrected authoritative 2025 replay facts

Evidence class: `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`.

Source and engine facts:

- source: `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`;
- provider: Twelve Data, XAU/USD;
- complete 2025 governed FAST timeline: **255 daily rows**;
- weekend rows: **0**;
- frozen rule: SMA20 + two completed-daily observations on the same side;
- a warning candidate is a **new** `ROBUST_UP` / `ROBUST_DOWN` episode onset, not every continuation day;
- complete number of new robust episode onsets in 2025: **22**.

Authoritative 22 onset dates:

- `2025-01-06` DOWN
- `2025-01-08` UP
- `2025-02-28` DOWN
- `2025-03-05` UP
- `2025-03-10` DOWN
- `2025-03-12` UP
- `2025-04-08` DOWN
- `2025-04-10` UP
- `2025-05-13` DOWN
- `2025-05-22` UP
- `2025-06-03` UP
- `2025-06-25` DOWN
- `2025-07-04` DOWN
- `2025-07-14` UP
- `2025-07-17` UP
- `2025-07-29` DOWN
- `2025-08-04` UP
- `2025-08-12` DOWN
- `2025-08-25` UP
- `2025-10-28` DOWN
- `2025-11-11` UP
- `2025-11-19` UP

Predeclared descriptive lead sensitivity from the 22 onsets, without selecting a post-hoc winning horizon:

- same-direction event within **1 governed day strictly after onset:** `1 / 22`;
- within **3 governed days:** `2 / 22`;
- within **5 governed days:** `3 / 22`;
- within **10 governed days:** `5 / 22`;
- same event day: `1 / 22`, which is not an early-warning credit under the completed-close availability rule.

The older event-conditioned statement that `11/19` volatility dates had the same prior FAST direction is **withdrawn as alarm-performance evidence**. It must not be cited as FAST warning accuracy, precision, recall or false-warning performance.

Current interpretation: FAST is retained as a **daily tactical trend-state engine**. It is **not proven as a standalone volatility-warning engine**. A formal false-warning rate remains `NOT_FROZEN_UNTIL_WARNING_WINDOW_IS_PREREGISTERED`.

### 10.7 GVZ_RISK — corrected authoritative 2025 replay facts

Role: **RISK_ONLY**. GVZ_RISK emits no UP/DOWN direction vote.

Frozen R4.1 mapping:

- `GVZ <= 25.9795` -> `NORMAL`, `cap = 1.0`, `panic = false`;
- `25.9795 < GVZ <= 30.5238` -> `ELEVATED`, `cap = 0.5`, `panic = false`;
- `GVZ > 30.5238` -> `PANIC`, `cap = 0.25`, `panic = true`.

The thresholds are frozen in R4.1, freeze date `2026-08-30`. Their derivation is **not proven to be a pre-2025 preregistered calibration**, therefore 2025 results remain retrospective and may not be described as pristine prospective validation.

#### 10.7.1 2025 historical data source

Database research series:

`GVZ_CBOE_FRED_MIRROR_RESEARCH_V1`

Provenance:

- observable: Cboe Gold ETF Volatility Index daily close;
- retrieval path for 2025 backfill: FRED `GVZCLS` historical mirror;
- upstream/source attribution: Cboe;
- 2025 valid daily observations: **250**;
- first observation: `2025-01-02`;
- last observation: `2025-12-31`;
- source substitution is explicit, not silent: this research backfill is kept separate from direct `GVZ_CBOE` rows;
- a 2026 overlap sample was cross-checked against direct Cboe-retrieved rows and matched exactly on checked dates;
- historical exact first-publication timestamp reconstruction is `NOT_PROVEN`;
- evidence class: `HISTORICAL_REPLAY / HISTORICAL_RESEARCH_BACKFILL`, not prospective issuance.

Scored replay series:

`GVZ_RISK_R4_1_HISTORICAL_REPLAY_V1`

Validation facts:

- raw 2025 GVZ rows: **250**;
- scored rows: **250**;
- frozen-score mismatch: **0**;
- FAST used in GVZ score: **false for all rows**;
- FAST linkage/combined score: **NONE**.

#### 10.7.2 Full-year GVZ risk-signal inventory

2025 distribution:

- `NORMAL`: **237** days;
- `ELEVATED`: **10** days;
- `PANIC`: **3** days.

All non-NORMAL GVZ signal dates must be retained, regardless of whether a volatility event occurred nearby.

`ELEVATED` dates:

- `2025-04-10` — 26.59
- `2025-04-11` — 28.44
- `2025-04-16` — 26.73
- `2025-04-21` — 28.14
- `2025-04-22` — 28.44
- `2025-10-14` — 26.11
- `2025-10-15` — 27.12
- `2025-10-21` — 29.82
- `2025-10-22` — 27.19
- `2025-10-23` — 26.68

`PANIC` dates:

- `2025-10-16` — 32.78
- `2025-10-17` — 31.20
- `2025-10-20` — 31.43

Same-date overlaps with frozen volatility events occurred on `2025-04-10`, `2025-10-16`, `2025-10-17` and `2025-10-21`, but same-date GVZ **daily close** is not credited as an early warning for an event already realized during that date.

Using only the latest completed GVZ close strictly before each of the 19 volatility dates, the event-conditioned descriptive states are:

- prior state `NORMAL`: **16 / 19** events;
- prior state `ELEVATED`: **1 / 19** event (`2025-10-15` -> `2025-10-16`);
- prior state `PANIC`: **2 / 19** events (`2025-10-16` -> `2025-10-17`; `2025-10-20` -> `2025-10-21`).

Those `16/19`, `1/19`, `2/19` counts are **event-conditioned descriptive diagnostics only**. They are not GVZ precision, recall, accuracy or a frozen alarm-horizon result.

Current interpretation: GVZ_RISK is retained as a **selective market-stress / risk-context motor**. It is **not proven as a general volatility-day prediction engine**. The small PANIC sample is `INSUFFICIENT_SUPPORT` for promotion claims.

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
8. **2025 volatility challenge — event inventory FROZEN; FAST corrected full-timeline replay COMPLETE; GVZ_RISK full-timeline historical replay COMPLETE; remaining role-preserving motor replays governed by Section 10.5**
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
| FAST | REPLAYED / RETAIN TACTICAL ROLE | complete 2025 timeline required; 22-onset authority in §10.6; not proven standalone volatility warning |
| SLOW | REPLAYABLE | confirmation/new-regime evidence |
| MONTHLY_DIRECTION_3M | REPLAYABLE | strategic context only |
| Emergency Level/Reversal | CONDITIONAL BY ORIGIN | selective context/confirmation; unavailable origin -> NOT_TESTABLE |
| BOCPD_RETURN_SUCCESSOR_V1 | NATIVE MONTHLY CLOCK | regime/change context only |
| Monthly H=1 experts | REPLAYABLE/PARTIAL BY ORIGIN | independent forecast + strategic context, not short-term trigger |
| Macro Event | ELIGIBLE EVENT ORIGINS | event-time surprise/context |
| Market Shock V3 | PARTIAL / RESEARCH-ONLY | realized event-shock extension |
| GVZ_RISK | REPLAYED HISTORICAL RESEARCH | 250-day 2025 backfill/scoring in §10.7; risk-only; daily-close availability; no FAST linkage; prospective status NOT_PROVEN |
| Other research experts | RESEARCH-ONLY UNTIL PIT PROVEN | no runtime authority without promotion |

Optional/short-history blocks must be compared against Core on the same eligible origins.

---

## 14. Evaluation principles

Simple preregistered baselines must precede complex learned promotion.

For GC-BREAK, primary metrics include break recall/miss rate, false-warning burden, warning lead time, confirmation delay, persistence, spurious flips, recovery behavior and proper scores where probabilities are emitted.

For the 2025 volatility challenge, each engine must additionally report role-appropriate event coverage, lead/lag, direction correctness where direction is actually emitted, abstention/NO_SIGNAL, signal availability time and PIT/missing limitations.

Both directions of accounting are required where the engine role permits them:

- **engine -> future event:** primary for warning/selectivity/false-warning analysis;
- **event -> prior engine state:** secondary coverage/diagnostic view only.

The complete engine-origin output table is the primary replay record. Exact signal dates are retained before event overlay.

Standalone direction accuracy is not the universal metric for heterogeneous engines.

Comparisons must be time-ordered, point-in-time safe and same-origin where eligibility differs.

No result may use an outcome-defined date to decide which earlier engine state counts as the warning unless that lookback rule was preregistered before the challenge outcome was inspected.

---

## 15. WP4 / future model-development rule

WP4 remains open only for a **separately named and preregistered challenger**.

The project should prefer low-dimensional, role-preserving sequential transition/state-duration models before high-capacity alternatives.

A conceptual transition model may be expressed as:

`P(S_t = j | S_{t-1} = i, D_t, X_t)`

where `S_{t-1}` is prior state, `D_t` is duration/sojourn information and `X_t` contains role-preserving origin-safe evidence.

An explicit latent-state/state-duration HMM/HSMM challenger is scientifically eligible under a new preregistration, but is **not pre-approved**.

Boosting, mixture-of-experts and deep-learning escalation remain blocked until simpler challengers justify additional complexity under time-ordered evidence with adequate support.

The 2025 volatility replay may determine whether engines show useful complementarity. It may not be used to tune a combined model and then relabel the same 2025 evidence as untouched validation.

---

## 16. Historical research interpretation

Historical fixed-horizon, 1D/3D, V1.48/V1.49, HS-SDL-DMA and related studies remain historical/auxiliary research only.

They may inform scientific understanding where chronology-safe, but they do not override the GC-BREAK state ontology, current event-label rules, frozen split, native engine roles or current promotion governance.

Old result files or artifact names are not current project authority. Historical traceability belongs in Git history and/or immutable evidence storage.

Specific superseded interpretation lock:

- the old event-conditioned FAST `11/19` number is not current alarm performance;
- same-date GVZ daily-close overlap is not early-warning evidence;
- any future motor result that hides full-year engine outputs by starting only from the 19 realized events is methodologically invalid for alarm-performance claims.

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

Historical research backfills must use explicit research series identities and truthful provenance. They may not silently overwrite the direct-authority series identity.

---

## 18. Promotion and prospective-evidence rule

Binding scientific order:

`PIT-safe formation`

-> `independent event inventories`

-> `engine-first full native-clock replay`

-> `freeze exact engine outputs and signal timestamps`

-> `outcome overlay`

-> `role-preserving evaluation`

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

Two distinct retrospective event universes are explicit:

1. the frozen GC-BREAK structural-break labels;
2. the frozen 2025 volatility challenge of 19 abnormal daily moves.

The governed 2025 motor procedure is engine-first: each identity must first be replayed over its complete eligible 2025 native-clock origin set and its complete output history frozen; only then may the independent 19-event volatility inventory be overlaid.

For completed-daily engines, **signal availability time is binding**: date-t close-derived FAST/GVZ output is not an early warning for a date-t event already realized during that session.

Current validated 2025 facts preserved in this manifest are:

- volatility challenge: 255 governed research weekdays, 19 frozen abnormal-move event-days, 5 EXTREME, 14 UP / 5 DOWN;
- FAST: 255-row complete timeline, 22 new robust episode onsets, tactical trend-state role retained, standalone volatility-warning performance not proven;
- GVZ_RISK: 250 historical daily-close observations/scored rows, 237 NORMAL / 10 ELEVATED / 3 PANIC, risk-only role, no FAST linkage, general volatility-warning performance not proven.

Event-conditioned backward lookup alone is not alarm-performance evidence. Same-day completed-close overlap alone is not early-warning evidence. Full engine timelines, exact signal dates and native availability timestamps must remain visible for all future motors so the project does not repeat the same methodological error.

Only after role-preserving full-timeline replays may the project judge whether the engines provide enough complementary information to justify a new combined-model research programme.

All future work must preserve point-in-time integrity, native engine clocks, role semantics, engine-independent event definitions, time-ordered validation, explicit missingness and strict separation of retrospective diagnostics from genuine prospective evidence.