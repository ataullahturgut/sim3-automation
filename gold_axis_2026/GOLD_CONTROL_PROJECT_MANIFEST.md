# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.55  
**Issue date:** 2026-09-15  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the **only current Gold Control project manifest**.

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control architecture, model roles, data chronology, validation governance, research sequencing and promotion rules. No second Gold Control project manifest may be created.

Contracts, preregistrations, design notes, checkpoints, reports, run artifacts, historical handovers and audit outputs are subordinate to this manifest. If a subordinate artifact conflicts with this manifest, the copy of this file at the current canonical `gold-r4-direction-engine` HEAD wins.

Every new Gold Control session must first read the current canonical branch HEAD and this manifest before interpreting historical material.

Authority split:

- **GitHub:** current code, frozen model/feature/source contracts, reproducibility and this manifest.
- **Production Neon:** mutable source observations, point-in-time lineage, append-only runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail may remain in Git history or immutable audit storage, but historical results do not define current project authority.

This manifest intentionally stores **architecture and governance, not application-result narratives or score tables**.

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

The monthly H=1 line remains a standalone forecast output regardless of the outcome of GC-BREAK research. Monthly forecasts may provide strategic context only when the derived features are origin-safe and empirically justified.

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

### 4.1 Strategic block

- Monthly H=1 experts: independent price-level forecast plus strategic anchor/context.
- `MONTHLY_DIRECTION_3M`: slow strategic prior; not a daily trigger.

### 4.2 Trend-structure block

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

### 4.3 Regime / stress / risk block

- `BOCPD_RETURN_SUCCESSOR_V1`: change-point/regime context only; no equal direction vote.
- `EMERGENCY_LEVEL`: abnormal displacement context.
- `EMERGENCY_REVERSAL`: selective abnormal reversal/confirmation context.
- realized volatility: uncertainty/severity context.
- `GVZ_RISK` and chronology-safe optional VIX: risk, severity, uncertainty and possible abstention/veto context; never equal direction votes.

The frozen BOCPD identity remains on its native completed-month clock. A daily BOCPD requires a separately named research challenger.

### 4.4 Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: release-aware event-surprise context at event time.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around eligible events.

Macro-event and Market-Shock evidence lives on an event-triggered intraday clock. Event windows or rules may not be changed after seeing challenge outcomes and then represented as frozen evidence.

### 4.5 Reliability / meta block

Permitted reliability evidence includes:

- matured-only reliability/Brier evidence where applicable;
- support count;
- evidence age;
- missingness and missing reason;
- class-degeneracy flag;
- regime similarity where justified;
- event/regime-conditional reliability only when support is adequate.

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

Historical evidence should carry, where applicable:

- `available_at`;
- source identity;
- lineage/fingerprint;
- state/evidence age;
- `missing_reason`.

---

## 6. Governance locks

The following are binding:

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
- no fixed 1D/3D short-term target reintroduced without explicit architecture change
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

---

## 9. Frozen GC-BREAK event-label rule

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

The following may not define the ground-truth label:

- FAST;
- SLOW;
- Monthly Direction;
- Emergency;
- BOCPD;
- GVZ;
- Macro Event;
- Market Shock;
- any learned GC-BREAK model.

Future price may be used only to date the ground-truth event itself, never to construct pre-origin predictors.

---

## 10. Frozen research split

### Formation / development

`2022-01-01 .. 2024-12-31`

Permitted use:

- label-quality inspection;
- baseline development;
- rolling/prequential internal validation;
- learned calibration/reliability estimation;
- architecture development under frozen governance.

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

## 11. Current work-package status

The binding sequence is:

1. **Coverage / PIT audit — COMPLETE**
2. **WP0 — State / break-label contract — COMPLETE / FROZEN**
3. **WP1 — PIT-safe formation panel — COMPLETE**
4. **WP2 — independent break-event inventory — COMPLETE WITH DATA-DENSITY WARNING**
5. **Split Freeze — COMPLETE / PRE-SCORE FROZEN**
6. **WP3 — preregistered simple formation baselines — COMPLETE WITH LIMITATIONS**
7. **WP4 — role-preserving sequential model — OPEN FOR A NEW SEPARATELY GOVERNED CHALLENGER**
8. **Ablation / optional extensions — BLOCKED PENDING ACCEPTED WP4 CORE**
9. **Architecture/parameter freeze — PENDING**
10. **Prospective shadow — PENDING FINAL FREEZE**

Historical WP4A, WP4B and WP4D families have already been evaluated under frozen rules and are **rejected**. Their detailed scores, run IDs and application-result narratives are intentionally not stored in this manifest.

A rejected family may not be retuned on challenge outcomes and reintroduced under the same identity.

---

## 12. Research eligibility by role

Eligibility is role- and origin-specific. A short-history channel may not shrink the entire core study window.

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

Optional or short-history blocks must be compared against Core on the **same eligible origins**.

---

## 13. Evaluation principles

Simple preregistered baselines must precede complex learned promotion.

Primary GC-BREAK metrics:

- break-event recall / miss rate;
- false warning episodes per 100 governed origins;
- first `WEAKENING -> break` lead time;
- first `BREAK_ALERT -> break` lead time;
- confirmation delay after a true break;
- warning duration/persistence;
- spurious state flips;
- time spent in warning states;
- recovery behaviour;
- proper score/calibration when a transition probability is emitted.

Standalone direction accuracy is not the primary metric for GC-BREAK.

Comparisons must be time-ordered, point-in-time safe and same-origin where eligibility differs.

---

## 14. WP4 development rule

WP4 remains open only for a **separately named and preregistered challenger**.

The project should prefer low-dimensional, role-preserving sequential transition/state-duration models before high-capacity alternatives.

A conceptual transition model may be expressed as:

`P(S_t = j | S_{t-1} = i, D_t, X_t)`

where:

- `S_{t-1}` is the prior state;
- `D_t` is state duration/sojourn information;
- `X_t` contains role-preserving, origin-safe evidence.

An explicit latent-state/state-duration HMM/HSMM challenger is scientifically eligible for investigation under a new preregistration, but is **not pre-approved**.

Boosting, mixture-of-experts and deep-learning escalation remain blocked until simpler challengers justify additional complexity under time-ordered evidence with adequate support.

No next challenger may be selected or tuned from 2025 challenge outcomes.

---

## 15. Historical research interpretation

Historical fixed-horizon, 1D/3D, V1.48/V1.49, HS-SDL-DMA and related studies remain historical/auxiliary research only.

They may inform scientific understanding where chronology-safe, but they do not override:

- the GC-BREAK state ontology;
- the current event-label rule;
- the frozen research split;
- native engine roles;
- current promotion governance.

Old result files or artifact names are not current project authority. Historical traceability belongs in Git history and/or immutable evidence storage, not in this manifest.

---

## 16. Neon / write authority

GC-BREAK currently has **no production forecast, decision or trading authority**.

Unless separately authorized later:

- no production decision-signal writes;
- no BUY/SELL/action mapping;
- no automatic selector/ensemble writes;
- no mutation of legitimately issued historical records;
- no speculative schema expansion solely for an unaccepted research challenger.

Research panels, labels, predictions and evaluations must remain logically separated and lineage-complete.

---

## 17. Promotion and prospective-evidence rule

Binding scientific order:

`PIT-safe formation`

-> `independent break-event inventory`

-> `simple preregistered baselines`

-> `role-preserving sequential challenger`

-> `same-origin ablation / optional extensions`

-> `architecture + parameter freeze`

-> `prospective shadow`

A model is not promoted because it is theoretically elegant or retrospectively impressive. Promotion requires reproducible, time-ordered incremental evidence with adequate support and no leakage.

The strongest future claim comes only from outcomes first observed after final architecture/parameter freeze.

---

## 18. Final binding summary

Gold Control is a **role-preserving, multi-clock sequential early-warning / regime-transition research programme** running in parallel with an independent monthly H=1 price-level forecasting programme.

The short-term objective is not to predict tomorrow or three days ahead. It is to detect trend deterioration early, escalate warning only when evidence accumulates, confirm structural breaks, recognize new regimes and recover cleanly from aborted warnings.

All future work must preserve:

- point-in-time integrity;
- native engine clocks;
- role semantics;
- engine-independent ground-truth labels;
- time-ordered validation;
- explicit missingness;
- separation of historical replay, retrospective challenge/stress and genuine prospective evidence;
- strict distinction between architecture/governance and application-result artifacts.

This manifest is intentionally concise. Detailed experimental results must live outside the manifest and may not become project authority by accumulation.