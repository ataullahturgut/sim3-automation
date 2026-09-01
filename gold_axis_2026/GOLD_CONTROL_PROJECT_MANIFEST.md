# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.1  
**Freeze / issue date:** 2026-09-01  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Project root:** `gold_axis_2026/`

---

## 0. MANDATORY READ-FIRST PROTOCOL

This file is the canonical project decision manifest for Gold Control.

Before changing code, UI, data contracts, model roles, signal rules, thresholds, source mappings, or production behavior:

1. **Read this manifest first.**
2. Check the current frozen files and production artifacts referenced here.
3. Do not silently change an approved role, threshold, source, target, horizon, or validation contract.
4. If new evidence conflicts with this manifest, mark the conflict explicitly as `UNRESOLVED` and update this manifest only after the evidence has been audited.
5. Missing historical code, training logic, provider lineage, definitions, or thresholds must be labeled `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, or `BLOCKED` as appropriate. Never reconstruct a missing rule by guesswork and present it as original.
6. Historical replay, retrospective backtest, and genuinely prospective/live evidence must remain visibly separated.
7. No new model, feature, data source, selector, ensemble, news block, whale-flow input, or UI metric enters the production path merely because it looks useful. It requires leakage-safe incremental evidence under the frozen contract.

**Default rule:** if a proposed change does not close a defined roadmap gap below, it stays outside the production path.

---

# 1. PRODUCT DEFINITION

Gold Control is not only a price-forecast model.

It is a **mobile-first, auditable gold decision-support system** that:

1. monitors current and historical market data,
2. produces an H=1 monthly-average XAU/USD forecast,
3. maintains a monthly direction context,
4. detects short/medium-horizon tactical reversals,
5. detects regime breaks and abnormal intramonth moves,
6. applies volatility/risk constraints,
7. stores the exact decision state that existed at each decision time,
8. separates live/prospective evidence from historical replay,
9. exposes the result through a simple user-facing interface without leaking backend complexity into the main UX.

The product is a **decision-support system**, not an autonomous self-learning trading system.

---

# 2. PRIMARY SYSTEM QUESTION FLOW

The frontend must answer four questions in this order:

1. **Piyasa** — Piyasa şu anda ne durumda?
2. **Görünüm** — Sistem neden böyle düşünüyor?
3. **Tahmin** — Gelecek ay için model ne bekliyor?
4. **Geçmiş** — Sistem geçmişte gerçekten ne yaptı?

Technical health/audit is a secondary system view, not a top-level user workflow.

Canonical navigation:

`Piyasa | Görünüm | Tahmin | Geçmiş`

Secondary technical surface:

`Sistem / Veri Sağlığı / Audit`

---

# 3. SOURCE-OF-TRUTH HIERARCHY

## 3.1 GitHub

GitHub is authoritative for:

- application code,
- model/signal implementation code,
- frozen configuration,
- source contracts,
- version history,
- this project manifest,
- reproducibility/audit documents.

GitHub must not be treated as the authoritative store for mutable live decision state.

## 3.2 Neon Postgres

Neon is the authoritative dynamic data plane for:

- observations,
- provider lineage,
- source vintages,
- retrieval runs,
- quality events,
- point-in-time data availability,
- immutable forecast input snapshots,
- derived feature snapshots,
- forecast contracts,
- future decision snapshots/events.

Current data-plane contract is documented in:

- `gold_axis_2026/data_pipeline/GOLD_DATA_R2_ARCHITECTURE.md`
- `gold_axis_2026/data_pipeline/schema.sql`
- `gold_axis_2026/data_pipeline/schema_patch_r2_6.sql`
- `gold_axis_2026/data_pipeline/source_contracts.json`
- `gold_axis_2026/data_pipeline/source_contracts_direct.json`
- `gold_axis_2026/data_pipeline/source_contracts_twelve_validated.json`
- `gold_axis_2026/GOLD_CONTROL_DATA_INVENTORY.md`

## 3.3 External providers

External providers are ingestion origins only. Provider identity and lineage are part of series identity and may not be silently substituted.

## 3.4 Application

The app is a presentation and interaction layer.

The app must not:

- tune thresholds,
- choose new features,
- silently swap providers,
- infer a new production direction directly from live spot,
- alter frozen model rules,
- convert monitoring data into settlement/EOD data without a contract.

---

# 4. DATA CONTRACT — NON-NEGOTIABLE RULES

The frozen Gold Data R2 principles remain binding:

1. No silent provider substitution.
2. Same economic semantic from different providers remains separate lineage/series identity.
3. Point-in-time availability is mandatory.
4. `observation_ts` is not automatically an availability timestamp.
5. Historical code must use `observations_as_of(origin_ts)` or an immutable forecast snapshot.
6. `canonical_latest` and `usable_observations` are current-state views, not historical backtest surfaces.
7. Backfilled history does not become retroactively knowable before first recorded retrieval unless historical publication/vintage timing is independently reconstructed.
8. Live/indicative XAU is not the frozen R4.1 EOD execution close.
9. Vendor current-day bars are not assumed completed while the relevant session may still be open.
10. Raw licensed/vendor series must respect display/redistribution rights.
11. Blocked inputs do not receive invented proxies under the same name.

---

# 5. VERIFIED / APPROVED DATA ROLES

## 5.1 Display/monitoring-capable core

### XAU live

Series: `XAU_SPOT_XAUS`  
Contract source: XAUS public API  
Role: Gold Control monitoring / Emergency candidate  
Status: `APPROVED_INDICATIVE_NOT_SETTLEMENT`

Current operational caveat: the live DB audit found the persisted latest source label `gold-api.com`, while the frozen contract names XAUS. This discrepancy is `UNRESOLVED_PERSISTED_SOURCE_LABEL_DIFFERS_FROM_XAUS_CONTRACT`; it is not authorization for a silent source rename or substitution.

### XAU daily operational history

Series: `XAU_DAILY_XAUS`  
Contract source: XAUS history  
Role: operational cross-check  
Status: `CANDIDATE_NOT_BENCHMARK`

The persisted operational lineage currently exposes an upstream/source label associated with Yahoo/GC=F. This remains an operational cross-check lineage and is not promoted to settlement/EOD authority.

### GVZ

Series: `GVZ_CBOE`  
Source: Cboe official history  
Role: R4 risk cap  
Status: `APPROVED`

### VIX

Series: `VIX_CBOE`  
Source: Cboe official history  
Role: forecast feature  
Status: `APPROVED`

## 5.2 Authority-grade macro/market data plane

Approved or approved-with-lag/proxy roles include:

- `DGS10_FRB_H15` — US 10Y constant-maturity Treasury yield
- `DEXCHUS_FRB_H10` — USD/CNY
- `DTWEXBGS_FRB_H10` — broad USD index proxy challenger, explicitly **not DXY**
- `EFFR_NYFED` — effective federal funds rate
- `GPR_OFFICIAL`
- `GPRT_OFFICIAL`
- `GPRA_OFFICIAL`
- `SP500_FRED`
- `DJIA_FRED`
- `NASDAQ100_FRED`

These are data-plane assets. Their presence in Neon does **not** automatically authorize them as replacements inside an archived model.

## 5.3 Vendor internal/non-display series

Validated Twelve Data identities include:

- `NEM_TWELVEDATA`
- `BARRICK_B_TWELVEDATA`
- `GLL_TWELVEDATA`
- `DZZ_TWELVEDATA`
- `HL_PB_TWELVEDATA`

Role: private/internal model use.  
Default UI rule: **do not display raw vendor series unless display rights and product need are separately approved.**

---

# 6. BLOCKED / UNRESOLVED DATA AND OPERATIONAL ITEMS

The following must remain visibly blocked/unresolved unless their exact problem is solved:

- Exact ICE DXY: `BLOCKED_LICENSE_OR_AUTHORIZED_VENDOR_ENTITLEMENT_REQUIRED`
- Exact legacy `^TNX` production identity: `BLOCKED_AS_NEW_PRODUCTION_SOURCE`
- LBMA platinum/palladium: `BLOCKED_LICENSE_REQUIRED_FROM_2026-07-01`
- Exact GPY identity: `BLOCKED_AMBIGUOUS_IDENTIFIER`
- Exact `long_term_trend` definition: `BLOCKED_DEFINITION_NOT_RECOVERED`
- Exact `volatility` definition: `BLOCKED_DEFINITION_NOT_RECOVERED`
- Exact archived VW executable runner: `BLOCKED_NOT_PROVEN` / missing original runner source
- Exact historical Causal Patch training source: missing archived training source; archived result is not equivalent to a reproducible executable model
- XAU persisted source-label vs frozen XAUS contract: `UNRESOLVED_PERSISTED_SOURCE_LABEL_DIFFERS_FROM_XAUS_CONTRACT`
- Current XAUS source availability incident: `DEGRADED_UPSTREAM_HTTP_503`; unrelated provider ingestion must continue independently
- Direct Neon management connector argument/schema mismatch: `BLOCKED_CONNECTOR_SCHEMA_MISMATCH`; do not claim branch/migration operations succeeded when this wrapper rejects them

Blocked data or code may not be approximated and then labeled as the exact original object.

---

# 7. H=1 FORECAST CONTRACT

Canonical target:

> **Next calendar month's average XAU/USD price**

Canonical origin:

> **End of the previous completed calendar month**

Validation rules:

- random split forbidden,
- future target information forbidden,
- tuning only on past rolling/expanding origins,
- publication lag mandatory,
- vintage safety mandatory,
- benchmark comparison at the same horizon mandatory.

Common audited evaluation window:

`2023-01 → 2026-07`, `N=43`

Current archived/audited scorecard evidence:

| Model | MAPE % | Role / interpretation |
|---|---:|---|
| VW-MIDAS-MSVR audited | ~2.672 | strongest audited analytical reference; exact original runner not recovered |
| Causal Patch R1 | ~3.075 | executable temporary point-forecast path in the production-closure contract |
| 3M Momentum R1 | ~3.297 | reproducible direction/price challenger |
| Random Walk R1 | ~3.302 | mandatory naive benchmark |

## 7.1 Production role freeze

Until explicitly superseded by audited evidence:

- **Audited shadow/reference:** VW-MIDAS-MSVR
- **Executable point-forecast path:** reproducible Causal Patch R1 implementation / temporary executable path
- **Direction challenger:** 3M Momentum
- **Benchmark:** Random Walk
- **Auto selector:** `OFF / REJECT_NOT_PROVEN`
- **Auto ensemble for primary:** `OFF / REJECT_FOR_PRIMARY`
- **Model disagreement:** visible to audit/UI where useful

Do not claim the audited VW output is fully executable/reproducible until the exact provenance gap is closed.

## 7.2 Current forecast-ledger state

The live Neon audit proves:

- `forecast_input_snapshots` exists with **0 rows**;
- `derived_feature_snapshots` exists with **0 rows**;
- `monthly_forecast_contracts` exists with **0 rows**.

Status:

`PROSPECTIVE_FORECAST_LEDGER_PROVEN_EMPTY`

This means model/contract canonicalization is complete, but no current Neon forecast row may be relabeled as `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`. Historical closure/replay artifacts keep their original evidence class.

Canonical detail is maintained in:

`gold_axis_2026/GOLD_CONTROL_FORECAST_CANONICALIZATION.md`

---

# 8. MONTHLY DIRECTION LAYER

Long-history monthly direction audit conclusion:

1. No additional simple monthly trend/MA rule has stable enough validation evidence to replace or hard-gate the current direction layer.
2. 3M Momentum remains useful as a bull/trend-continuation challenger/context signal.
3. Its recent directional hit rate must not be generalized into a universal downside detector.
4. VW direction may be kept as a disagreement/context signal; VW is stronger as a level forecast than as a standalone direction classifier.
5. Old TACTICAL V2 exact M20/M40 rule remains blocked because the exact formula/threshold/time-axis contract was not recovered.

Canonical monthly direction concept:

`Monthly context = VW level view + 3M Momentum prior + visible disagreement`

No monthly signal alone is sufficient to define the final daily execution state.

---

# 9. TACTICAL R1 — FAST / SLOW

Tactical R1 is a **CONFIRM / CONFLICT** layer.

It is not:

- a continuous hard gate,
- an automatic full direction flipper,
- a replacement for the monthly model.

## 9.1 Fast

Frozen concept:

- daily market close versus SMA20,
- persistent confirmation across 2 market days.

Role:

- early reversal confirmation / alert,
- short-horizon trend state.

Current audit status:

`PROVISIONAL_PASS_WITH_SOURCE_ROBUSTNESS_CONSTRAINT`

Fast must not be promoted beyond its audited role without a clean long-history source-consistent replay.

## 9.2 Slow

Frozen concept:

- completed weekly close versus SMA4 of completed weekly closes,
- persistent state across 2 completed weeks.

Role:

- slower tactical trend confirmation.

## 9.3 Rejected tactical architecture

Continuous weekly hard-gates were rejected because drawdown improvement came with excessive bull-upside sacrifice.

Therefore:

`FAST/SLOW != permanent exposure gate`

---

# 10. BOCPD REGIME / BREAK LAYER

Approved detector:

`BOCPD-RETURN`

Approved role:

> **REGIME / BREAK ALERT ONLY**

It is not:

- a price forecast,
- a standalone direction generator,
- an automatic exit rule by itself.

Rejected in the final BOCPD/CUSUM audit:

- CUSUM-return
- BOCPD-volatility
- Dual BOCPD

The historical 2024–2026 evaluation is a **locked historical replay**, not genuinely unseen prospective evidence.

This distinction must remain visible in reporting and UI.

---

# 11. EMERGENCY LAYER

Emergency exists to detect intramonth states the monthly model cannot update quickly enough.

## 11.1 Level Emergency

Role:

- detect large deviation from the frozen monthly reference.

Frozen R4.1 concept:

- compare current/frozen EOD price state against frozen monthly VW reference,
- use the frozen absolute threshold from R4.1 config,
- do not tune the threshold on later 2026 outcomes.

## 11.2 Reversal Emergency

Role:

- after an extreme move, detect a sufficiently large reversal from the running peak/trough.

Status/role:

- alert layer,
- not an automatic full direction flip.

The exact current threshold/rule must always be read from `gold_axis_2026/r4_1/config/frozen_r4_1.json`, not from memory or a mockup.

---

# 12. GVZ RISK LAYER

GVZ is a risk/exposure-cap layer.

It does **not** determine gold direction.

Interpretation:

> "Even if the directional state is favorable, how much risk is the system allowed to carry?"

The exact current thresholds must be read from the frozen R4.1 config.

UI may translate the frozen bands into user-facing states such as:

- Normal
- Elevated
- Panic

but must not infer direction from GVZ.

---

# 13. MACRO EVENT LAYER

Macro-event logic is a separate event-risk override layer.

Known recovered rule status is partial. If the full timestamp-safe consensus/vintage construction is not reproducible, status remains:

`BLOCKED_NOT_FULLY_RECOVERED`

Do not fabricate historical consensus or event timestamps to complete the rule.

---

# 14. CANONICAL DECISION FLOW

The target production flow is:

```text
Market/Data Snapshot
        ↓
H=1 Monthly Price Forecast
        ↓
Monthly Direction Context
        ↓
Fast Tactical
        ↓
Slow Tactical
        ↓
BOCPD Regime/Break Alert
        ↓
Level / Reversal Emergency
        ↓
Macro Event State
        ↓
GVZ Risk Cap
        ↓
FINAL DECISION STATE
        ↓
Immutable Decision Snapshot / Event Ledger
```

The frontend must never mirror this whole backend chain on the home screen. It should progressively disclose it.

---

# 15. MISSING PRODUCTION COMPONENT — DECISION STATE STORE

The current Streamlit app still expects:

`gold_axis_2026/r4_1/output/latest_signal.json`

as a latest decision-state artifact.

That is not sufficient as the long-term production state contract.

## Required database objects / logical entities

The production roadmap must add:

### `decision_runs`

Tracks each decision-engine execution and its provenance.

### `decision_signal_snapshots`

Stores the exact frozen R4.1 signal vector used by a decision.

### `decision_events`

Stores the append-only classification/change history.

The recovered R4.1 engine currently emits **descriptive classifications**, not a proven position instruction. Exact current classification vocabulary is:

- `MACRO_DOWN_RISK`
- `REVERSAL_RISK_DOWN`
- `REVERSAL_RISK_UP`
- `ALIGNED_UP`
- `ALIGNED_DOWN`
- `CONFLICT`
- `UNRESOLVED_MIXED`

Current position/action mapping status:

`NOT_PROVEN_POSITION_MAPPING`

Therefore the database/UI must not fabricate `BUY`, `SELL`, `HOLD_LONG`, `EXIT`, `REDUCE`, or an exposure percentage from those classifications until a separate audited mapping is recovered or frozen under change control.

Current Stage 3 implementation artifacts:

- `gold_axis_2026/GOLD_CONTROL_DECISION_STORE_CONTRACT.md`
- `gold_axis_2026/data_pipeline/schema_patch_decision_store_v1.sql`
- `gold_axis_2026/data_pipeline/test_decision_store_schema.py`
- `.github/workflows/gold-control-decision-store-schema-smoke.yml`

The candidate DDL has passed a rollback-only compatibility/constraint smoke against the actual Neon database. **No production decision-store migration has been applied yet.**

The UI should eventually read canonical stored decision state rather than deriving a decision from live spot.

---

# 16. FORECAST STATE STORE

Every issued production forecast must be immutable and auditable.

Each forecast record must bind:

- forecast origin,
- target month,
- target definition,
- production point forecast,
- audited shadow/reference,
- RW benchmark,
- direction challenger/context,
- model version,
- input snapshot id,
- code SHA,
- issued-at timestamp,
- status (`PRODUCTION`, `SHADOW`, `BENCHMARK`, `BLOCKED`, etc.).

Later revisions must not rewrite an old forecast snapshot.

Current database state on the 2026-09-01 audit:

- forecast snapshot/contract tables exist;
- their current row counts are zero;
- no historical file-backed forecast may be backfilled and relabeled as if it had existed prospectively in Neon.

The first future `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast must be stored before outcome realization with immutable inputs and provenance.

---

# 17. FRONTEND INFORMATION ARCHITECTURE

## 17.1 Screen 1 — `Piyasa`

Question:

> **Piyasa şu anda ne durumda?**

Primary content:

- XAU/USD indicative live price
- absolute / percentage change if defensibly calculable from available completed data
- as-of timestamp
- freshness/stale state
- source label
- latest completed daily close
- GVZ latest official close
- GVZ risk regime
- XAU historical chart

Current timeframe contract for the existing XAUS history adapter:

`1A | 3A | 6A | 1Y`

Do not expose `1G`, `1H`, or `Tümü` until a real intraday/longer-history adapter is connected and audited.

Secondary decision strip:

- last stored EOD decision state
- decision as-of timestamp
- explicit warning: `Canlı spot ≠ son EOD karar`

Home screen must be market-first, not model-first.

## 17.2 Screen 2 — `Görünüm`

Question:

> **Sistem neden böyle düşünüyor?**

Content:

- final stored decision state
- monthly context
- Fast
- Slow
- regime/break alert
- Emergency
- GVZ/risk
- deterministic plain-language explanation generated only from stored states
- expandable technical details

Do not show invented confidence metrics.

## 17.3 Screen 3 — `Tahmin`

Question:

> **Gelecek ay için model ne bekliyor?**

Content:

- target month
- production H=1 point forecast
- current spot comparison
- audited VW shadow/reference
- RW benchmark
- direction challenger/context
- actual vs issued forecast history
- model provenance/status

If the canonical forecast ledger has no issued row, production forecast state must be displayed as `NOT_ISSUED_IN_CANONICAL_LEDGER`; file-backed research/closure artifacts may only appear with their evidence label.

Do not show a prediction interval or uncertainty label unless a calibrated interval model exists and has been validated.

## 17.4 Screen 4 — `Geçmiş`

Question:

> **Sistem geçmişte gerçekten ne yaptı?**

Two separate histories:

### Forecast history

- issued forecast
- actual
- APE/error
- model version
- origin

### Decision history

- actual stored decision events
- timestamp
- signal-state context
- price at decision/evaluation point
- reason code

Never invent historical decision dates for visual design.

## 17.5 Technical screen — `Sistem / Veri Sağlığı`

Contains:

- source status
- last retrieval
- freshness
- latest pipeline run
- quality events
- model version
- decision-engine version
- config version
- Git SHA
- forecast snapshot id
- decision snapshot id
- blockers/provenance

This is secondary navigation, not one of the four primary user tabs.

---

# 18. UI / DESIGN SYSTEM FREEZE

Approved direction:

- corporate/institutional financial visual language,
- light/white primary surfaces,
- restrained navy as the institutional anchor,
- controlled gold accent for brand/selection,
- green only for favorable/up/normal states,
- red only for adverse/down/alert states,
- amber only for attention/warning,
- high whitespace,
- strong typographic hierarchy,
- thin separators instead of excessive card boxes,
- mobile-first layout,
- no decorative glow-heavy luxury-trading aesthetic,
- no black/white-only dashboard theme,
- no dashboard-card overload,
- no fake metrics added for visual balance.

The frontend should follow progressive disclosure:

1. action/meaning,
2. explanation,
3. technical mechanism/audit.

---

# 19. METRICS THAT MUST NOT BE INVENTED

Until separately defined, computed, and validated, the following are prohibited in production UI:

- `Güven: Orta`
- `Güç: %68`
- arbitrary confidence percentages
- arbitrary uncertainty labels
- direction accuracy percentages not tied to a named audited dataset/window
- arbitrary trade counts
- fabricated decision dates
- fabricated forecast values
- fabricated forecast bands

If a metric has no frozen definition and lineage, it does not appear.

---

# 20. REPLAY VS PROSPECTIVE EVIDENCE

Every performance result must be labeled as one of:

### `HISTORICAL_REPLAY`

Rules/architecture evaluated on historical data, even if locked before a sub-window.

### `PROSPECTIVE_SHADOW`

Decision/forecast recorded before outcome realization but not yet used as production authority.

### `LIVE_PRODUCTION`

Issued by the frozen production path before realization, with immutable input/decision snapshots.

Historical replay must never be described as live prospective evidence.

The current Neon forecast ledger is proven empty; therefore the project does not currently claim a historical Neon-backed `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast record.

This separation is mandatory in the `Geçmiş` screen and in all research reports.

---

# 21. CHANGE-CONTROL POLICY

A production-rule change requires all of the following:

1. explicit reason/problem statement,
2. frozen development evidence,
3. leakage-safe rolling/expanding-origin validation,
4. comparison against the current production/reference baseline,
5. robustness check across regimes where possible,
6. source/provenance audit,
7. no tuning on the final locked/prospective evaluation period,
8. new version identifier,
9. manifest update,
10. code/config commit.

A change that improves one recent episode but was discovered by inspecting that episode cannot silently become production logic.

---

# 22. CHALLENGER RESEARCH POLICY

The following remain research-lane ideas only until incremental evidence exists:

- new Transformer architectures,
- LSTM/GRU variants,
- XGBoost/boosted-tree price models,
- news sentiment,
- whale/large-flow features,
- ETF/futures/positioning features,
- options-derived variables,
- new regime models,
- auto selector,
- auto ensemble,
- confidence meta-model,
- self-learning threshold adaptation.

A challenger may enter production consideration only if it improves the frozen decision/forecast objective under the same causal information contract.

---

# 23. PROJECT ROADMAP — FROZEN EXECUTION ORDER

The project execution order remains:

| Stage | Deliverable | Exit criterion |
|---|---|---|
| 0 | **Production Manifest** | This file exists and is treated as read-first contract |
| 1 | **Neon Data Inventory / Health Audit** | Actual DB series inventory, first/last obs, retrieval freshness, quality, lineage, display policy documented |
| 2 | **Forecast Canonicalization** | One canonical issued-forecast contract; executable/reference/benchmark roles unambiguous |
| 3 | **Decision State Store** | Decision run/snapshot/event persistence replaces file-only latest-state dependency |
| 4 | **Deterministic R4.1 Decision Engine** | Same frozen input snapshot → same decision state; version and config recorded |
| 5 | **Piyasa Screen** | Real live/history data only; freshness and source visible |
| 6 | **Görünüm Screen** | Real stored decision snapshot drives explanation |
| 7 | **Tahmin Screen** | Real canonical issued forecast drives display |
| 8 | **Geçmiş Screen** | Real forecast ledger + real decision ledger; replay/prospective separated |
| 9 | **System Health / Audit Screen** | Full lineage/provenance/blockers exposed technically |
| 10 | **Mobile QA** | iPhone/mobile-first UX validated; no desktop-only critical interaction |
| 11 | **Prospective Shadow Run** | New forecasts/decisions stored before outcomes, immutable ledger accumulating |
| 12 | **Production Graduation** | Predefined prospective acceptance gates satisfied |

**No later stage may be treated as complete by using fabricated placeholders for an incomplete earlier stage.**

## 23.1 Current roadmap status — 2026-09-01

| Stage | Current status | Evidence / blocker |
|---|---|---|
| 0 | `PASS` | Manifest read-first contract active |
| 1 | `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS` | Actual Neon inventory generated read-only; XAU source currently degraded and lineage discrepancy remains explicit |
| 2 | `PASS_CONTRACT_CANONICALIZED; PROSPECTIVE_LEDGER_PROVEN_EMPTY` | Model roles/authority frozen; live forecast-state tables reconciled and contain 0 rows |
| 3 | `IN_PROGRESS` | DDL + contract + rollback smoke PASS; isolated temporary-branch rehearsal blocked by connector schema mismatch; production migration not applied |
| 4–12 | `NOT_STARTED / NOT_COMPLETE` | Cannot be promoted ahead of Stage 3 |

---

# 24. IMMEDIATE NEXT WORK

The next canonical task is now:

## `STAGE 3 — DECISION STATE STORE: ISOLATED MIGRATION REHEARSAL → PRODUCTION MIGRATION`

Completed Stage 3 preparation:

- live current schema reconciled;
- decision tables proven absent;
- exact descriptive state vocabulary frozen;
- `NOT_PROVEN_POSITION_MAPPING` enforced in the candidate database contract;
- versioned DDL created;
- rollback-only compatibility/constraint smoke against actual Neon: `PASS`;
- rollback verified no persistent schema change.

Required next gate:

1. create/use an isolated temporary Neon branch from the production branch;
2. apply `schema_patch_decision_store_v1.sql` there;
3. verify tables, constraints, indexes, view, append-only behavior, fingerprint idempotency and existing-data compatibility;
4. compare temporary schema against production;
5. only after successful isolated rehearsal, apply the same versioned migration to production through an auditable migration path;
6. verify production schema post-migration;
7. implement decision persistence writer and read contract.

Current blocker for the isolated-branch gate:

`BLOCKED_CONNECTOR_SCHEMA_MISMATCH`

The exposed Neon management connector currently presents conflicting argument contracts for branch/SQL management. Do not bypass this by pretending a temporary branch was created. The protected GitHub Actions path is verified for read-only audit and rollback smoke, but has not yet provided an isolated Neon branch lifecycle.

### Operational work that continues independently

- XAU ingestion remains degraded while the frozen XAUS endpoint returns HTTP 503.
- Cboe, Fed, GPR, FRED-index and Twelve jobs must remain independently runnable; XAU failure must not block them.
- No alternate XAU provider may be silently relabeled as the frozen XAUS source.

---

# 25. CURRENT APP CONTRACT / TECHNICAL DEBT

Current Streamlit paths:

- `gold_axis_2026/apps/gold_control.py`
- `gold_axis_2026/apps/live_sources.py`

Current app UI architecture is transitional and must not be treated as final product architecture.

Known mismatch:

- current app top-level tabs are still `Şimdi / Sinyaller / Model / Veri`
- final information architecture is `Piyasa / Görünüm / Tahmin / Geçmiş`

Current latest-state dependency:

- `gold_axis_2026/r4_1/output/latest_signal.json`

This is transitional. The roadmap requires database-backed decision state.

Current live adapter contract:

- XAU spot: indicative monitoring
- XAU history: 1-year daily history
- GVZ: Cboe daily history / latest close

Do not pretend the current adapter already provides full intraday history or unlimited historical range.

The app must not present a position instruction derived from current descriptive R4.1 classification while `NOT_PROVEN_POSITION_MAPPING` remains active.

---

# 26. IMPLEMENTATION PRINCIPLE

The project must now optimize for:

> **reproducibility + auditability + causal correctness + operational clarity**

not for:

> maximum number of models, indicators, tabs, or attractive metrics.

A lower-complexity rule with complete lineage is preferred over a more impressive but irreproducible black box.

---

# 27. FINAL PROJECT NORTH STAR

The project is successful when Gold Control can answer, without hindsight:

> **“At this exact time, what data did the system actually know, what did each frozen model/signal say, what final state did the engine issue, why did it issue it, and what happened afterward?”**

The final system must make that answer reproducible from stored snapshots and versioned code.

That is the production standard.

---

## Manifest maintenance rule

When a project-level decision changes, update this file in the **same change set** as the relevant code/config/data-contract modification.

If the manifest and implementation disagree, the discrepancy is a release blocker until reconciled.
