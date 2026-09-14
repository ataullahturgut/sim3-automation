# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.52  
**Issue date:** 2026-09-14  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Active GC-BREAK research branch:** `gc-break-wp1-formation-backfill`  
**Default-branch scheduler:** `main`  
**Deployment mirror:** `gold-r4-direction-engine-ui-v122-final`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the only current Gold Control project manifest.

**Single-manifest rule:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control forecasting, sequential break research, direction/risk context, validation, readiness and future research governance. No second Gold Control project manifest may be created.

Files whose names contain `manifest`, including run manifests, validation manifests and historical artifacts, are subordinate evidence artifacts only. Handover documents, checkpoints, contracts, preregistrations, design notes, reports and audit outputs are also subordinate to this file. If any subordinate artifact conflicts with this manifest, the copy of this file at the current canonical `gold-r4-direction-engine` HEAD wins.

Every new Gold Control session must first re-read the current canonical branch HEAD and this exact manifest before interpreting older handovers, checkpoints, audit artifacts or historical run manifests.

GitHub is the authority for current code, frozen model/feature/source contracts, reproducibility and this manifest. Production Neon is the authority for mutable source observations, point-in-time lineage, append-only current runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail remains preserved in Git history and immutable audit storage. This manifest may reclassify historical evidence but may not rewrite or destroy it.

Gold Control is a **decision-support and research system, not an autonomous trading system**.

---

## 2. Current top-level architecture — two parallel primary lines

Gold Control currently has **two parallel primary lines**. They may exchange role-preserving context but they are not one homogeneous model-selection pool.

### 2.1 Monthly H=1 price-level forecasting — ACTIVE AND INDEPENDENT

The monthly programme forecasts the next calendar month's XAU/USD price level from the previous completed month-end information boundary.

Current monthly H=1 expert identities:

- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

`MONTHLY_DIRECTION_3M` remains a strategic monthly direction/prior context.

The monthly H=1 line remains a standalone forecast output regardless of the outcome of the short-term GC-BREAK research programme. Monthly forecasts may supply strategic context such as forecast gap, dispersion, direction prior and forecast age only when those features are origin-safe and empirically justified.

### 2.2 Short-term GC-BREAK — SEQUENTIAL TREND-HEALTH / BREAK EARLY WARNING

The current short-term research problem is **not** fixed-horizon 1D/3D direction prediction.

The binding state ontology is:

`STABLE -> WEAKENING -> BREAK_ALERT -> CONFIRMED_BREAK -> NEW_REGIME`

The system must also permit recovery transitions, including:

- `WEAKENING -> STABLE`
- `BREAK_ALERT -> STABLE` or a lower warning state when evidence recovers
- after `NEW_REGIME`, the new regime may become its own `STABLE` state

The primary short-term question is:

> Is the current trend healthy, weakening, escalating toward a break, confirmed as broken, or settling into a new regime?

The primary performance questions are:

- how early a true break is warned;
- how many false warning episodes are paid for that lead time;
- how many breaks are missed;
- how quickly a true break is confirmed;
- how stably a new regime is recognized;
- how often warning states recover correctly instead of forcing a false break.

**Binding correction:** `NEXT_NY17_1D`, `NEXT_NY17_3D`, 1D/3D directional accuracy and fixed-horizon break-risk are **historical research targets only**. They are not current primary Gold Control short-term outputs and may not silently re-enter the current architecture.

---

## 3. Current governed runtime inventory

The current governed runtime inventory remains exactly these 12 identities:

### Monthly H=1 price experts
- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

### Strategic / trend / event / regime / emergency / risk contexts
- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `MACRO_EVENT_SUCCESSOR_V2`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`
- `GVZ_RISK`

No additional research channel becomes a governed runtime identity without explicit later promotion and manifest change control.

The runtime inventory is **not the complete research evidence universe**. Research-only channels may be evaluated without becoming production/runtime identities.

---

## 4. Role-preserving multi-clock research architecture

Heterogeneous engines must not be flat-voted or ranked as though they solve the same task.

### 4.1 Strategic block

- Monthly H=1 experts: independent price-level forecast plus strategic anchor/context.
- `MONTHLY_DIRECTION_3M`: slow strategic prior, not a daily trigger.

### 4.2 Trend-structure block

- **FAST:** tactical daily trend state, flip, age and persistence; candidate early weakening evidence.
- **SLOW:** completed-week trend confirmation, alignment/conflict and state age; primarily confirmation/new-regime evidence rather than next-day direction.

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

- `BOCPD_RETURN_SUCCESSOR_V1`: change-point/regime context only; no direction vote.
- `EMERGENCY_LEVEL`: abnormal displacement context.
- `EMERGENCY_REVERSAL`: selective abnormal reversal/confirmation context.
- realized volatility: uncertainty/severity context.
- `GVZ_RISK` and optional VIX where chronology-safe: risk, severity, uncertainty and possible abstention/veto context; never equal direction votes.

The frozen BOCPD identity remains on its native completed-month clock. A daily BOCPD would be a separately named research challenger and may not silently replace the frozen identity.

### 4.4 Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: release-aware event-surprise context at event time.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around events; not next-day continuation.

Macro-event and Market-Shock evidence lives on an event clock, typically the first 5–15 minutes around eligible releases. A 60-minute reaction is research-only unless separately frozen.

### 4.5 Expert Evidence block — research only unless promoted

Research evidence may include:

- H20 / `LEGACY_RTQ_R126`
- `GOLD_RIDGE`
- `SESSION_RM_RIDGE`
- `PRICE_DISCOVERY_HGB`
- `MACRO_CROSS_RIDGE`
- `FULL_HGB`
- `LOCAL_ERRMEM`

These channels may contribute continuation-vs-weakening probabilities, disagreement, entropy, sharpness, quantile geometry, IQR, sign consistency, session stress, cross-market pressure or matured reliability **only on origins where chronology-safe replay is proven**.

They are not current production winners and are not universal daily-direction authorities.

### 4.6 Reliability/meta block

Permitted reliability evidence includes:

- matured-only Brier/reliability estimates;
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

A slower state may be carried forward only under its native-clock semantics and must carry an explicit `age` / `state_age`. Missing channels may not be silently imputed as neutral or zero.

Every historical feature used by the sequential system should carry, where applicable:

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
- no challenge/stress result used to retune the locked challenge/stress result
- no fixed 1D/3D short-term target reintroduced without an explicit future architecture change
- no production forecast/decision authority write without explicit later authorization
- no stale context labelled fresh merely because an engine is `ACTIVE`
- no fabricated state or feature when a historical channel is unavailable

When evidence is absent or unproven, use `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, `BLOCKED`, `NOT_TESTABLE` or `INSUFFICIENT_SUPPORT` as appropriate.

---

## 7. Evidence and point-in-time semantics

Evidence classes remain separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin from information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is frozen/deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

`RUNTIME_GOVERNANCE_AUDIT` may wrap current runtime-state evidence but does not convert historical reconstruction into prospective evidence.

For every historical origin, all features, model states and reliability estimates must respect the information available at that origin. Later target observations, future price paths and later revisions are forbidden from feature construction or model selection.

Late retrieval of a historically dated market value does not make the row historically issued. Retrieval timestamps must remain truthful.

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

The Twelve Data value is Gold Control's internal NY17 reference, not an official CME price.

Historical formation reconstruction must use the same exact source/bar semantics. Late historical retrieval remains `HISTORICAL_REPLAY_RECONSTRUCTION`; it may not be backdated or relabelled prospective.

---

## 9. Frozen GC-BREAK event-label contract

Current research event-label authority:

`gold_axis_2026/gc_break_v0/gc_break_event_contract_v1.json`

Binding primary event rule:

- family: volatility-normalized directional change;
- daily log return;
- volatility scale: trailing 20 governed observations;
- sigma is lagged one observation;
- primary threshold: `k = 3.0`;
- current regime extreme is updated causally;
- break timestamp is the first governed observation whose adverse move from the regime extreme reaches the frozen threshold;
- after the event, regime direction flips and the extreme resets to the event close.

`k = 2.5` is sensitivity-only and may not replace `k = 3.0` because a downstream model scores better.

The event label is engine-independent. The following may **not** define the label:

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

## 10. Frozen research split and evidentiary interpretation

Current split authority:

`gold_axis_2026/gc_break_v0/gc_break_split_contract_v1.json`

The split was frozen before formation-backfill results and before full WP3/WP4 scoring.

### Formation / development

`2022-01-01 .. 2024-12-31`

Use:

- label-quality inspection;
- baseline development;
- rolling/prequential internal validation;
- learned calibration/reliability estimation;
- architecture development under frozen governance.

### Retrospective Challenge

`2025-01-01 .. 2025-12-31`

Locked retrospective challenge. No threshold/model choice may be derived from its outcomes and then claimed as untouched challenge evidence.

### Retrospective Stress / transport check

`2026-01-01 .. 2026-08-31`

This period has been heavily inspected historically. It is a retrospective stress/transport check and is **not fresh blind OOS evidence**.

### Prospective Shadow

Begins only after final architecture/parameter freeze and before future outcomes are known. This is the strongest future evidence.

**Terminology correction:** older files may contain names such as `FROZEN_OOS_2026` or “retrospective frozen OOS”. Those historical artifact names remain preserved, but under the current manifest their evidentiary interpretation is **researcher-visible retrospective stress**, not fresh unseen OOS.

Random splitting is forbidden.

---

## 11. Current work-package roadmap and status

The binding order is:

1. **Coverage / PIT audit — COMPLETE**
2. **WP0 — State / break-label contract — COMPLETE / FROZEN**
3. **WP1 — PIT-safe formation panel — COMPLETE / CLOSURE PASS / CANONICAL PERSISTENCE VERIFIED**
4. **WP2 — independent break-event inventory — COMPLETE WITH DATA-DENSITY WARNING**
5. **Split Freeze — COMPLETE / PRE-SCORE FROZEN**
6. **WP3 — preregistered formation baselines — COMPLETE WITH LIMITATIONS / WP4 ENTRY SUPPORTED**
7. **WP4 — main role-preserving sequential model — PHASE A LEARNED-HAZARD FAMILY REJECTED / RESEARCH REDIRECTION REQUIRED**
8. **Ablation / extensions — BLOCKED PENDING ACCEPTED WP4 CORE**
9. **Architecture/parameter freeze — PENDING**
10. **Prospective shadow — PENDING FINAL FREEZE**

### WP1 closure condition

WP1 is not complete merely because raw historical XAU exists. It closes only when the governed formation panel is built and quality-checked under exact NY17 semantics with required chronology/lineage fields.

Current WP1 research tooling includes:

- `tools/gc_break_wp1_resume_exact_ny17_v2.py`
- `tools/gc_break_wp1_build_formation_panel_v1.py`
- `tools/gc_break_wp1_add_bocpd_native_context_v1.py`
- `tools/gc_break_wp1_add_monthly_h1_context_v1.py`
- `tools/gc_break_wp1_formation_event_context_v1.py`

No later WP may be claimed complete merely because its code exists.

### Evidence-backed closure update — 2026-09-14

The following work-package status changes are supported by executed and inspected evidence, not code existence alone:

- **WP1:** closure run `34792800170` completed successfully; exact-NY17 canonical persistence/verification run `34822912320` completed successfully. The formation panel contains 351 governed origins for 2022-2024 and retains explicit missingness rather than interpolation/forward-fill.
- **WP2:** ground-truth run `34828001360` completed successfully under the frozen engine-independent `k=3.0` event contract. The formation inventory contains 21 primary break events. The inherited sparse-calendar/data-density warning remains binding.
- **WP3:** preregistered formation baseline run `34829522473` and manifest closure review run `34829777783` completed successfully. WP3 closes as `COMPLETE_WITH_LIMITATIONS_READY_FOR_WP4`.

Binding WP4 entry implications from the inspected WP3 evidence:

- 21 formation break events justify only a **simple low-dimensional, time-ordered** first learned challenger; they do not justify high-capacity model search or broad interaction mining.
- FAST has usable tactical weakening signal but retains a recall/lead-time trade-off; it is not a standalone authority.
- SLOW's confirmation role is supported: 17/21 formation breaks were confirmed before the next break, with median delay 3 governed origins / 9 calendar days.
- On the 213 Emergency-eligible origins containing 13 breaks, adding `EMERGENCY_REVERSAL` to FAST via `CORE_WEAKENING_NATIVE` produced no detected-break or recall gain and increased false-warning burden. Emergency therefore remains selective confirmation/context at WP4 entry, not an automatically promoted early-warning OR trigger.
- `PATH_HALF` remains anatomy-only because it shares the event-label price path. BOCPD remains slow regime context and is not promoted as a daily direction/break trigger.
- Optional or short-history blocks remain subject to the same-origin comparison rule; the full-window Core score may not be compared directly with a shorter optional-block score.

### WP4 Phase A evidence-backed closure — 2026-09-14

The first learned WP4 family was preregistered before scoring as `GC_BREAK_WP4_HAZARD_PREREG_V1` and executed only on the 2022-2024 formation window. Run `34830376294` completed successfully and the independent closure review run `34831293583` completed successfully.

Binding interpretation of the frozen Phase A evidence:

- Common prequential evaluation support was 241 governed origins containing 15 break events.
- `M1_FAST_DURATION_RIDGE` improved log loss versus the empirical-hazard null but did not improve Brier score.
- `M2_ROLE_CORE_RIDGE` also improved log loss but did not improve Brier score.
- The preregistered primary gate required improvement in both Brier score and log loss; therefore the family closes as `REJECT_LEARNED_HAZARD`.
- `M3_PATH_AUGMENTED_SENSITIVITY` improved both primary probability scores, but it uses `adverse_fraction` derived from the same price path as the frozen event label. It remains sensitivity/anatomy evidence and cannot rescue or promote the learned-hazard family.
- Phase-B probability thresholds / `WEAKENING` / `BREAK_ALERT` mappings are **not authorized** from this family.
- High-capacity escalation, hyperparameter search and post-score tuning of M1/M2/M3 are **not authorized**.
- The 2025 challenge remains locked and 2026 Jan-Aug remains nonselection retrospective stress.
- Any next WP4 architecture must be a separately named, preregistered, simple role-preserving challenger before scoring.

---

## 12. Research replayability / eligibility matrix

Current eligibility is role- and origin-specific. A short-history channel may not shrink the entire core study window.

| Channel | Current research eligibility | Binding interpretation |
|---|---|---|
| XAU price/trend | CORE, subject to governed NY17 formation completion | primary structural evidence |
| FAST | REPLAYABLE | core tactical weakening evidence |
| SLOW | REPLAYABLE | core confirmation/new-regime evidence |
| MONTHLY_DIRECTION_3M | REPLAYABLE | strategic context only |
| Emergency Level/Reversal | REPLAYABLE WHERE FROZEN MONTHLY REFERENCE EXISTS | absent reference -> NOT_TESTABLE |
| BOCPD_RETURN_SUCCESSOR_V1 | REPLAYABLE ON NATIVE MONTHLY CLOCK | regime/change context only |
| Monthly H=1 experts | REPLAYABLE/PARTIAL BY ORIGIN | independent forecast + strategic context, not short-term trigger |
| Macro Event | REPLAYABLE ON ELIGIBLE EVENT ORIGINS | event-time hazard/surprise context |
| Market Shock V3 | PARTIAL / EVENT-SPECIFIC RESEARCH | realized event-shock extension |
| GVZ_RISK historical extension | PARTIAL | core window may not be shortened for it; same-origin extension only unless PIT proof is complete |
| H20 / LEGACY_RTQ_R126 | PARTIAL / NOT PROVEN FOR FULL 2022-24 PIT REPLAY | research extension only |
| GOLD_RIDGE | PARTIAL | same-origin research extension only until full PIT replay proven |
| SESSION_RM_RIDGE | PARTIAL | same-origin research extension only |
| PRICE_DISCOVERY_HGB | PARTIAL | same-origin research extension only |
| MACRO_CROSS_RIDGE | PARTIAL | same-origin research extension only |
| FULL_HGB | PARTIAL | same-origin research extension only |
| LOCAL_ERRMEM | PARTIAL / SAME-ORIGIN EXTENSION | research-only; not a core formation authority |
| XAG/XPT/XPD historical research series | NOT CORE-PIT-PROVEN | do not use as formal historical daily evidence without chronology proof |
| GC/GLD/COT | NOT PROVEN / DATA-GATED | no fabricated backfill |

Optional/short-history blocks must be compared against Core on the **same eligible origins**. A Core 2022–2026 score may not be compared directly with a Core+Optional score covering only a shorter late window.

---

## 13. WP3 baseline and evaluation principles

WP3 must evaluate preregistered simple baselines before a complex learned model is promoted.

Permitted baseline families include:

- no-warning / persistence reference;
- mechanical price-path precursor;
- FAST-only conflict/opposite evidence;
- SLOW confirmation behaviour;
- Emergency-only selective confirmation;
- simple role-preserving combinations frozen before scoring;
- classical change-detection baseline where chronology-safe and separately specified.

Primary sequential/event metrics:

- break-event recall / miss rate;
- false warning episodes per 100 governed origins;
- first `WEAKENING -> break` lead time;
- first `BREAK_ALERT -> break` lead time;
- confirmation delay after a true break;
- warning duration/persistence;
- spurious state flips;
- time spent in warning states;
- recovery behaviour;
- proper score/calibration where a transition probability is emitted.

Standalone direction accuracy is not the primary metric for GC-BREAK.

---

## 14. WP4 model-development rule

WP4 may begin only after WP1, WP2 and WP3 provide adequate support. The first preregistered low-dimensional discrete-time hazard family has now been executed and rejected under its frozen Phase A gate. WP4 therefore remains open only as a research-redirection problem: any replacement architecture must be separately named and preregistered before scoring, remain simple and role-preserving, and may not be tuned from the rejected M1/M2/M3 scores.

The preferred first learned family is a **simple role-preserving sequential state-transition / hazard model**, conceptually of the form:

`P(S_t = j | S_{t-1} = i, D_t, X_t)`

where:

- `S_{t-1}` is the prior state;
- `D_t` is state duration/sojourn information;
- `X_t` contains role-preserving evidence channels.

The modeling question is:

> Is there sufficient evidence for a transition from the current state to the next warning/confirmation state?

A simple discrete-time multi-state transition or hazard model should be tested before HSMM, boosting, mixture-of-experts or deep-learning complexity. Additional complexity is justified only if it beats simple benchmarks under time-ordered evidence with adequate event support.

---

## 15. Current September 2026 monthly H=1 references

Target month: `2026-09`  
Frozen information boundary: `2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET.

| Identity | September reference | Status |
|---|---:|---|
| `VW_MIDAS_MSVR_SUCCESSOR_V1` | `4565.115907930242 USD/oz` | frozen H=1 historical-origin reconstruction |
| `CAUSAL_PATCH` | `4452.046728838838 USD/oz` | frozen H=1 historical-origin reconstruction |
| `MOMENTUM_3M` | `4345.814584037808 USD/oz` | source-bound historical replay |
| `RANDOM_WALK` | `4397.305673870967 USD/oz` | source-bound benchmark |

September observations do not trigger recomputation of these frozen September H=1 references.

No selector/ensemble is authorized among the four experts.

The monthly H=1 programme remains active even if a short-term GC-BREAK model is later promoted.

---

## 16. Historical fixed-horizon research — preserved but non-current

Gold Control retains V1.48/V1.49, HS-SDL-DMA and related 1D/3D studies as historical evidence. Their code, reports and audit artifacts remain preserved in Git history/current archive paths.

Their current interpretation is:

- useful evidence about target difficulty, regime dependence, calibration and transportability;
- potential auxiliary feature/evidence channels where chronology-safe;
- **not** the current primary short-term target;
- **not** authority to restore `NEXT_NY17_1D` / `NEXT_NY17_3D` as primary outputs;
- **not** authority to override the sequential GC-BREAK state ontology.

A future fixed-horizon challenger may be researched only under a separately named, preregistered challenger contract and may not silently redefine the project objective.

---

## 17. Retrospective GC-BREAK diagnostic evidence — not promotion evidence

Researcher-visible 2025–2026 GC-BREAK diagnostics have shown a coherent but not yet validated role separation:

- price-path deterioration tends to warn earlier but with more false alarms;
- FAST can reduce noise and provide tactical weakening evidence;
- Emergency Reversal is highly selective and more confirmation-like than early-warning-like;
- SLOW behaves more like new-regime confirmation than an early precursor;
- Macro Event / Market Shock have not yet demonstrated stable incremental benefit as a daily primary trigger;
- Monthly H=1 forecasts have not justified use as a short-term break trigger and remain independent strategic forecasts.

These findings are retrospective diagnostics only. They may motivate preregistered formation tests, but they may not be used to retune the locked 2025/2026 challenge/stress results or to claim fresh OOS validation.

No statement such as “90% accurate break model” is authorized from these diagnostics.

---

## 18. Operational contracts retained

The following existing operational/data contracts remain binding where consistent with this manifest:

- `GOLD_CONTROL_MODEL_DATA_READINESS_CONTRACT_V143_2026-09-07.md`
- `GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_CONTRACT_V144_2026-09-07.md`
- `GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md`
- `GOLD_CONTROL_R4_1_EMITTED_STATE_CONTRACT.md`

Key implementations retained:

- canonical XAU reconciliation: `data_pipeline/twelve_xau_ny17.py`
- live intramonth append-only recompute: `data_pipeline/live_intramonth_recompute_v144.py`
- current/live readiness audit: `tools/audit_model_data_readiness_v143.py`
- post-write audit: `tools/audit_live_intramonth_postwrite_v144.py`
- historical pilot readiness audit: `tools/audit_historical_pilot_readiness_v145.py`

Operational identities and frozen historical runtime behaviour remain preserved. This v1.50 change corrects the **current research objective, evidence interpretation and future roadmap**; it does not silently rewrite already-issued runtime records.

---

## 19. Neon / write authority

GC-BREAK currently has **no production forecast, decision or trading authority**.

Unless separately authorized later:

- no production decision-signal writes;
- no BUY/SELL/action mapping;
- no automatic selector/ensemble writes;
- no mutation of legitimately issued historical records;
- no large speculative schema footprint.

Research panels, labels, predictions and evaluations should remain logically separated. If persistent GC-BREAK tables are later authorized, they should be lean, versioned and lineage-complete.

---

## 20. Promotion and prospective-evidence rule

The current scientific order is binding:

`WP1 PIT-safe formation panel`

-> `WP2 independent break-event inventory`

-> `WP3 simple preregistered baselines`

-> `WP4 role-preserving sequential model`

-> `same-origin ablation / optional extensions`

-> `architecture + parameter freeze`

-> `prospective shadow`

A model is not promoted because it is theoretically elegant or retrospectively impressive. Promotion requires reproducible, time-ordered incremental evidence with adequate event support and no leakage.

The strongest future claim comes only from outcomes first observed after the final architecture/parameter freeze.

---

## 21. Supersession and historical terminology

Manifest v1.52 carries forward all v1.51 architecture, evidence and governance locks, and additionally records the evidence-backed rejection and closure of the first WP4 learned-hazard Phase A family.

Manifest v1.50 supersedes the current-authority portions of v1.49 that defined the short-term programme as fixed `NEXT_NY17_1D` / `NEXT_NY17_3D` forecasting or treated those horizons as the primary current research objective.

All old files, reports, workflow names and artifact names are retained as historical evidence and remain interpretable in their original historical context. Their names do not override this manifest.

In particular:

- historical `1D`, `3D`, `5D`, HS-SDL-DMA and V1.49 direction studies remain historical/auxiliary evidence;
- historical artifact names containing `FROZEN_OOS` remain unchanged for traceability but do not imply fresh blind OOS under the current project interpretation;
- 2025 is the current **retrospective challenge** period;
- 2026 Jan–Aug is the current **retrospective stress/transport** period;
- only post-freeze future issuance may become **prospective shadow** evidence.

---

## 22. Final binding summary

Current Gold Control research is a **role-preserving, multi-clock sequential early-warning / regime-transition programme** running in parallel with an independent monthly H=1 price-forecast programme.

The short-term objective is not “predict tomorrow/three days ahead”. It is to detect trend deterioration early, escalate warning only when evidence accumulates, confirm true structural breaks, recognize new regimes and recover cleanly from aborted warnings.

All future work must preserve point-in-time integrity, native engine clocks, role semantics, time-ordered validation, explicit missingness and the separation between historical replay, retrospective challenge/stress and genuine prospective evidence.
