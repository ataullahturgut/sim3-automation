# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.13  
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

### XAU live — primary `Piyasa` display monitoring

Series: `XAU_SPOT_GOLDAPI`  
Source: Gold API (`gold-api.com`)  
Role: **indicative live display / market monitoring only**  
Status: `APPROVED_INDICATIVE_PUBLIC_DISPLAY_NO_MODEL_USE`

Frozen provider contract:

- endpoint: `GET https://api.gold-api.com/price/XAU`;
- expected symbol/currency: `XAU` / `USD`;
- required fields: positive finite `price`, parseable `updatedAt`;
- provider asks clients to cache the current-price response for 30 seconds;
- UI must show source and freshness/stale state;
- provider-managed upstream fallback is opaque, therefore this series is **not** authority-grade and is prohibited from EOD, benchmark, H=1 forecast, VW reference, Fast/Slow source, or final-decision use;
- it is not equivalent to `XAU_EOD_TWELVE_NY17`, `XAU_SPOT_XAUS`, LBMA, CME/EBS, COMEX settlement, or Yahoo/GC=F.

Authority/licensing decision record:

`gold_axis_2026/GOLD_CONTROL_LIVE_MARKET_ROADMAP_CHANGE_CONTROL_2026-09-01.md`

Operational proof: GitHub Actions run `33518757788`, job `99892357951`, `SUCCESS`; HTTP/schema/freshness were validated without logging the raw market price and without database writes.

### XAU live — legacy / secondary indicative lineage

Series: `XAU_SPOT_XAUS`  
Contract source: XAUS public API  
Role: secondary monitoring / operational cross-check; Emergency candidate only under its separately frozen role  
Status: `APPROVED_INDICATIVE_NOT_SETTLEMENT; DEGRADED_UPSTREAM_HTTP_503`

The persisted-source-label discrepancy remains `UNRESOLVED_PERSISTED_SOURCE_LABEL_DIFFERS_FROM_XAUS_CONTRACT`. `XAU_SPOT_XAUS` and `XAU_SPOT_GOLDAPI` remain separate provider lineages and may never be silently merged or relabelled.

### XAU daily operational history

Series: `XAU_DAILY_XAUS`  
Contract source: XAUS history  
Role: **Piyasa daily history / last-completed-daily display cross-check only**  
Status: `CANDIDATE_NOT_BENCHMARK; APPROVED_EXPLICITLY_LABELLED_OPERATIONAL_DISPLAY`

The persisted operational lineage currently exposes an upstream/source label associated with Yahoo/GC=F. This remains an operational cross-check lineage and is not promoted to settlement/EOD authority. Any Piyasa rendering must explicitly disclose that it is not canonical spot/EOD, settlement, benchmark, or model authority. The current-day row is not eligible for the `last completed daily close`; that comparison uses the newest positive daily row strictly before the current UTC date.

### Canonical XAU EOD decision-reference contract

Canonical series: `XAU_EOD_TWELVE_NY17`  
Economic semantic: **spot XAU/USD 17:00 ET internal EOD decision reference price**  
Session-definition authority: **CME Group / EBS Market**  
Operational market-data provider: **Twelve Data**  
Provider symbol: `XAU/USD`  
Provider interval: `1min`  
Requested timezone: `America/New_York`  
Session boundary: **17:00 ET**  
Role: canonical R4.1 EOD decision reference  
Status: `APPROVED_CANONICAL_PIPELINE_SUCCESS`

The contract deliberately separates **session authority** from **price-data provider**:

- CME/EBS is the authority for the 17:00 ET spot FX / precious-metals trade-date roll;
- Twelve Data supplies the actual `XAU/USD` intraday OHLC observation used operationally;
- the stored series lineage is Twelve Data and must never be labelled as CME/EBS price data;
- `XAU_EOD_CME_EBS` is retained only as a superseded authority/feed candidate and is not the active production-ingestion series.

Official Twelve Data documentation states that for intraday intervals the requested IANA timezone may be applied, `datetime` identifies when the bar was opened, and `close` is the price at the end of that bar. Therefore the frozen R4.1 decision-reference rule is:

1. Request Twelve Data `/time_series` for `XAU/USD`, `interval=1min`, `timezone=America/New_York`.
2. Select the bar whose `datetime` is exactly `16:59:00` ET for the completed EBS trade date.
3. Require positive finite OHLC values and a unique `16:59:00` bar.
4. Use that bar's `close` as the 17:00 ET internal decision reference price.
5. If the exact 16:59 bar is absent, duplicated, invalid, or not retrievable after the session boundary, emit `BLOCKED_NO_VALID_TWELVE_NY1659_BAR`; no forward-fill or provider substitution is allowed.
6. Persist provider symbol, interval, requested timezone, source bar timestamp, retrieval timestamp, source vintage/payload hash and derived decision-price hash.
7. Raw vendor data remains subject to Twelve Data display/redistribution rights.
8. Historical reconstruction must use the same provider, interval, timezone and mapping rule; it may not relabel legacy XAUS/LBMA/futures history as Twelve data.

Access/mapping evidence: GitHub Actions run `33510985399`, job `99866288149`, `SUCCESS`, proved the protected Twelve credential can retrieve a valid `XAU/USD` `1min` bar at `16:59:00` with `America/New_York` timezone without logging raw prices or writing to the database.

Production-ingestion evidence: GitHub Actions run `33511805110`, job `99869043161`, `SUCCESS`, executed the frozen canonical writer against Neon. It selected completed trade date `2026-08-31`, stored observation timestamp `2026-08-31T21:00:00+00:00` (17:00 ET), source `Twelve Data`, quality status `APPROVED_CANONICAL_TWELVE_NY17`, retrieval run `12099dfa-a370-4710-aed5-d02388f652ac`=`SUCCESS`, wrote one canonical observation, reported zero quality errors, and logged no raw market price.

This value is named **decision reference price**, not official settlement or official market close. LBMA Gold Price PM remains a benchmark comparator; CME Group Spot Gold Reference Rate remains a 13:29–13:30 ET spot marker; COMEX settlement remains futures semantics; Twelve provider-default `1day` Australia/Sydney bar remains a different daily semantic and is not used here.

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
- Canonical Twelve NY17 XAU ingestion: `APPROVED_CANONICAL_PIPELINE_SUCCESS`; single-day production ingestion and PIT-safe same-lineage history backfill are proven. Historical backfill preserves actual retrieval-time availability and is not retroactively knowable.
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

The live Neon reconcile audit (run `33518909613`, job `99892866821`, `SUCCESS`) proves:

- `forecast_input_snapshots` = **0 rows**;
- `derived_feature_snapshots` = **1 row**;
- `monthly_forecast_contracts` = **0 rows**;
- append-only mutation guards cover all three forecast-state tables (3/3).

The single derived row is `MONTHLY_DIRECTION_3M`, version `R4_1_3M_SIMPLE_RETURN_V1`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`. It was calculated and persisted on 2026-09-01 with its true timestamps. It is **not** a prospective H=1 forecast and does not close the forecast-input or forecast-contract blockers.

Status:

`FORECAST_LEDGER_NOT_ISSUED; MONTHLY_DIRECTION_BOOTSTRAP_CONTEXT_PRESENT`

Historical closure/replay artifacts keep their original evidence class. No forecast may be relabelled as `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` unless it was issued before outcome realization with an immutable input snapshot and contract.

## 7.3 Prospective-origin cutoff — September 2026

The frozen H=1 contract requires the forecast origin to be the **end of the previous completed calendar month**. The current Neon forecast ledger was still empty after the `2026-08-31` origin had passed, and the first canonical NY17 production observation/backfill work occurred on `2026-09-01`.

Therefore a forecast first created on `2026-09-01` must **not** be backdated to `2026-08-31` or described as a contract-compliant prospective September H=1 issuance.

Status: `SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED`.

The first target still eligible to become a fully contract-compliant prospective H=1 forecast under the frozen origin rule is **October 2026**, with origin at the end of **2026-09-30**, subject to all model/input/provenance blockers being resolved before issuance.

A September monthly direction or R4.1 initialization computed now may only be stored as an explicitly labelled **late bootstrap/shadow context** using its true retrieval/calculation timestamp. Such a bootstrap context does not close the H=1 forecast issuance blocker and may not be presented as a 31-August prospective forecast.

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

# 15. PRODUCTION COMPONENT — DECISION STATE STORE

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

Decision Store V1 passed rollback-only CI, isolated Neon rehearsal, and guarded production migration. Production now contains the three append-only Decision Store tables, the evidence-scoped latest-state view, and the mutation-rejection function. The production migration run was GitHub Actions run `33496843121`, pinned to canonical commit `13d5a027849470b4a95341004300bd97a35e82f9`, and completed `SUCCESS` with `decision_rows=0`. Production writer/reader activation remains a separate Stage 3 gate.

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

Current forecast-state database reconciliation on 2026-09-01:

- `forecast_input_snapshots`: **0 rows**;
- `derived_feature_snapshots`: **1 row** — `MONTHLY_DIRECTION_3M`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`;
- `monthly_forecast_contracts`: **0 rows**;
- append-only UPDATE/DELETE guard coverage: **3/3 tables**;
- no historical file-backed forecast may be backfilled and relabeled as if it had existed prospectively in Neon.

Evidence: read-only reconcile run `33518909613`, plus the guarded monthly-direction bootstrap issuance run `33516396253`. The first future H=1 `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` forecast must still be stored before outcome realization with immutable inputs and provenance.

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
- latest completed daily close from the explicitly labelled operational display history (`XAU_DAILY_XAUS`), never from raw Twelve vendor data unless display rights are separately proven
- GVZ latest official close
- GVZ risk regime
- XAU historical chart

Current timeframe contract for the existing XAUS history adapter:

`1A | 3A | 6A | 1Y`

Do not expose `1G`, `1H`, or `Tümü` until a real intraday/longer-history adapter is connected and audited. `XAU_EOD_TWELVE_NY17` remains the internal canonical R4.1 EOD decision-reference lineage; its raw numeric value is not a Piyasa display field unless Twelve external-display rights are separately proven and frozen.

Display/licensing change-control: `gold_axis_2026/GOLD_CONTROL_PIYASA_DISPLAY_CONTRACT_CHANGE_CONTROL_2026-09-01.md`.

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

# 23. PROJECT ROADMAP — FROZEN DEPENDENCY-GATED EXECUTION

The project roadmap is dependency-gated rather than globally linear. Model/decision claims preserve strict causal gates, while the market-monitoring surface may progress once its own data/display contract is proven.

| Stage | Deliverable | Exit criterion / dependency |
|---|---|---|
| 0 | **Production Manifest** | Read-first governance contract active |
| 1 | **Neon Data Inventory / Health Audit** | Actual inventory, freshness, quality, lineage and display policy documented |
| 2 | **Forecast Canonicalization** | Forecast target/origin and model roles unambiguous; no false prospective history |
| 3 | **Decision State Store** | Append-only decision persistence/read path present; evidence isolation enforced |
| 4A | **Current-state data/context substrate** | Canonical NY17 history sufficient; monthly direction context and Fast/Slow calculable; immutable state infrastructure proven |
| 4B | **Forecast-dependent R4.1 issuer** | Current H=1 issuer + VW reference + immutable forecast snapshot/contract + complete EngineSnapshot; first forward decision may be `PROSPECTIVE_SHADOW` |
| 5 | **Piyasa Screen** | Real live/history data only; source/freshness visible; may progress in parallel with 4B because it does not create a forecast or decision |
| 6 | **Görünüm Screen** | Real display-eligible stored decision snapshot drives explanation; no fabricated action/confidence |
| 7 | **Tahmin Screen** | Real canonical issued forecast drives display |
| 8 | **Geçmiş Screen** | Real forecast/decision ledgers; replay/prospective/live separated |
| 9 | **System Health / Audit Screen** | Full lineage/provenance/blockers exposed technically |
| 10 | **Mobile QA** | Mobile-first UX validated |
| 11 | **Prospective Shadow Run** | New forecasts/decisions stored before outcomes, immutable ledger accumulating |
| 12 | **Production Graduation** | Predefined prospective acceptance gates satisfied |

Dependency rule frozen by manifest v1.10:

- Stage 5 may proceed independently of unresolved Stage-4B forecast/VW blockers because `Piyasa` is a monitoring surface and must not infer a decision from live spot.
- Stage 6 cannot be marked complete without a display-eligible stored Decision Store state.
- Stage 7 cannot be marked complete without a canonical issued H=1 forecast.
- Stage 8 must never mix historical replay with prospective/live evidence.
- No stage may use fabricated placeholders to satisfy its own exit criterion.

Change-control record: `gold_axis_2026/GOLD_CONTROL_LIVE_MARKET_ROADMAP_CHANGE_CONTROL_2026-09-01.md`.

Stage-5 runtime evidence added in manifest v1.11:

- canonical live adapter smoke: run `33519370028`, job `99894418747`, `SUCCESS`; source series `XAU_SPOT_GOLDAPI`, freshness PASS, role `INDICATIVE_DISPLAY_ONLY_NO_MODEL_USE`, no raw-value logging or writes;
- current 1-year XAU history adapter smoke: run `33519506662`, job `99894890585`, `SUCCESS`; row/span/freshness/duplicate/null gates PASS, no raw-value logging or writes.

Stage-5 closure evidence added in manifest v1.12:

- Piyasa deterministic contract tests: 4/4 PASS;
- canonical Streamlit tabs: `Piyasa | Görünüm | Tahmin | Geçmiş`;
- live Gold API and operational XAUS history rendered with explicit distinct lineage labels;
- raw Twelve NY17 numeric market value intentionally not rendered;
- Decision Store absence renders `KANONİK KARAR YOK`;
- no forecast or decision write performed;
- run `33521193615`, job `99900581399`, `STAGE5_PIYASA_UI_SMOKE_PASS`.

## 23.1 Current roadmap status — 2026-09-01

| Stage | Current status | Evidence / blocker |
|---|---|---|
| 0 | `PASS` | Manifest read-first contract active |
| 1 | `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS` | Data inventory/lineage audited; XAUS remains degraded but independent sources continue |
| 2 | `PASS_CONTRACT_CANONICALIZED; FORECAST_NOT_ISSUED` | Forecast roles frozen; no prospective H=1 row exists; one late-bootstrap monthly-direction context row exists |
| 3 | `PASS_DECISION_STORE_AND_READ_PATH` | Production append-only store/read path active; no fabricated current decision |
| 4A | `PASS_CURRENT_STATE_SUBSTRATE_FOR_SHADOW_CONTEXT` | NY17 backfill SUCCESS; monthly direction bootstrap issued; Fast/Slow rehearsal SUCCESS; forecast-state append-only guards 3/3 |
| 4B | `IN_PROGRESS_BLOCKED_FORECAST_ISSUER` | Current H=1 issuer and VW monthly reference remain unresolved; forecast input snapshot/contract not issued |
| 5 | `PASS_PIYASA_SCREEN_CONTRACT` | Canonical Piyasa implementation + deterministic/live Streamlit smoke `SUCCESS` (run `33521193615`, job `99900581399`); approved tabs, live/history sources, freshness/source disclosure, timeframe gate, no decision/forecast writes |
| 6 | `BLOCKED_NO_DISPLAY_ELIGIBLE_DECISION_SNAPSHOT` | Component rehearsals exist, but no complete forward R4.1 decision row may be fabricated |
| 7 | `BLOCKED_FORECAST_NOT_ISSUED` | Canonical H=1 forecast ledger has no issued row |
| 8–12 | `NOT_STARTED / NOT_COMPLETE` | Their own dependency gates are not satisfied |


---

# 24. IMMEDIATE NEXT WORK

The immediate canonical task is now:

## `STAGE 4B — RESOLVE THE H=1 FORECAST ISSUER AND VW MONTHLY REFERENCE WITHOUT SILENT MODEL SUBSTITUTION`

Stage 5 is closed as `PASS_PIYASA_SCREEN_CONTRACT` by run `33521193615`, job `99900581399`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. Stage 4B forecast-governance therefore becomes the next dependency to resolve; no September H=1 row may be backdated and no missing VW/Patch identity may be guessed.

Stage 3 is closed as:

`PASS_DECISION_STORE_AND_READ_PATH`

Stage 3 closure evidence:

- production Decision Store migration: run `33496843121`, job `99820886297`, `SUCCESS`;
- guarded emitted-state → store → reader bridge: run `33498177345`, job `99825081623`, `R4_1_DECISION_BRIDGE_SMOKE_PASS`;
- transitional app now reads Decision Store instead of `latest_signal.json`;
- app read-only evidence-isolation smoke: run `33498603322`, job `99826433286`, `GOLD_CONTROL_DECISION_STORE_APP_READER_PASS`;
- `HISTORICAL_REPLAY` is excluded from the current-state app reader;
- `action_state` remains null under `NOT_PROVEN_POSITION_MAPPING`;
- production Decision Store remains empty because no valid prospective issuer has been authorized.

A canonical continuously scheduled live/EOD R4.1 producer is still:

`NOT_FOUND_CANONICAL_LIVE_R4_1_EMITTER`

The older R4 LONG/CASH / AL/SAT workflow is not an acceptable substitute because that would violate `NOT_PROVEN_POSITION_MAPPING`.

### Stage 4 readiness audit

Read-only production audit:

- run: `33499509482`;
- job: `99829327414`;
- commit: `37fed93cbef76f394e8dee8b334f89617d94b3ef`;
- result: `SUCCESS` audit execution, `readiness=BLOCKED`;
- raw market values logged: `NO`.

Confirmed active Stage-4B forecast blockers after manifest v1.10 reconciliation:

1. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
2. `FORECAST_CONTRACT_NOT_ISSUED`
3. `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`
   - retained Patch code is proven only through its prior August horizon and may not be date-extended by assumption.
4. `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED`
   - `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`; the exact original VW-MIDAS-MSVR Adapt V2 runner/source chain is not retained.

Closed current-state/context gates:

- `CANONICAL_XAU_HISTORY_BACKFILL_NOT_YET_SUCCESS` → `CLOSED_BY_RUN_33515654716`;
- `MONTHLY_DIRECTION_CONTEXT_NOT_ISSUED` → closed for **late-bootstrap shadow context only** by run `33516396253`; this does not close H=1 forecast issuance;
- Fast/Slow calculability → rehearsal `SUCCESS` by run `33516790212` (`ROBUST_UP` / `ROBUST_UP`), read-only and not a prospective forecast claim;
- forecast-state DB immutability → production append-only migration `SUCCESS` by run `33516015898`; reconcile audit run `33518909613` confirms trigger coverage 3/3.

Temporal boundary (not a recoverable data blocker):

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED` — the frozen 31-August origin passed while the canonical forecast ledger was empty. No reconstruction performed on 1-September or later may be relabelled as a 31-August prospective issuance.

Closed XAU pipeline blocker:

`TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` → `CLOSED_BY_RUN_33511805110`

Closed source-side sub-blockers:

- `CME_EBS_TICKER_DATA_ENTITLEMENT_NOT_PROVEN` → superseded; direct CME/EBS feed is no longer required for the active operational contract.
- Twelve `XAU/USD` 1-minute credential/access → `PROVEN` by run `33510985399`, job `99866288149`.
- Twelve exact `16:59 ET` bar mapping → `PROVEN` by the same run.

Closed Stage-4 source-authority blocker:

`NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE` → `CLOSED_BY_MANIFEST_V1_4`

Important source interpretation:

- canonical R4.1 EOD series is **`XAU_EOD_TWELVE_NY17`**;
- **CME/EBS supplies the market-session convention only**: spot FX & precious-metals trade date rolls at **17:00 ET**;
- **Twelve Data is the actual operational price provider**: `XAU/USD`, `1min`, `timezone=America/New_York`; the exact `16:59:00` bar close is the 17:00 ET internal decision reference;
- this is a Gold Control decision-reference construction, not an official CME close, LBMA fixing, or Twelve provider-default daily close;
- `XAU_EOD_CME_EBS` is superseded as the active operational series because licensed EBS Ticker access is unnecessary for this contract;
- `XAU_DAILY_XAUS` remains operational cross-check only / `CANDIDATE_NOT_BENCHMARK`;
- `XAU_SPOT_XAUS` remains indicative monitoring;
- no silent fallback, relabelling, or forward-fill is allowed if the exact Twelve NY17 input is unavailable;
- Cboe GVZ and the Fed/FRED/GPR/Twelve auxiliary pipelines remain independent.

Required next gates by dependency:

**Piyasa / monitoring lane — CLOSED:**

1. `XAU_SPOT_GOLDAPI` live adapter: PASS by run `33519370028`, job `99894418747`.
2. XAUS 1-year operational display-history adapter: PASS by run `33519506662`, job `99894890585`.
3. Canonical Piyasa UI + deterministic contract + Streamlit runtime smoke: PASS by run `33521193615`, job `99900581399`.
4. Provider roles are explicit: Gold API live display, XAUS operational display history, Twelve NY17 internal canonical EOD decision reference.
5. `Canlı spot ≠ son EOD karar` and `KANONİK KARAR YOK` fail-safe behavior are active.
6. Stage 5 status is `PASS_PIYASA_SCREEN_CONTRACT`; later visual/mobile refinement belongs to Stage 10 and does not reopen Stage 5 data semantics.

**Stage-4B forecast/decision lane (continues fail-closed):**

1. resolve/freeze the current monthly VW reference without silent model substitution;
2. resolve the current H=1 executable point issuer with leakage-safe change control rather than extending Patch constants;
3. before the real end-September origin, issue the immutable forecast input snapshot + monthly forecast contract;
4. build/schedule the canonical R4.1 issuer only when every mandatory EngineSnapshot field has valid evidence;
5. first forward Decision Store state remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B blocker prevents construction of the complete frozen EngineSnapshot. This does not block non-decision `Piyasa` monitoring.
No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any active Stage-4 readiness blocker remains open.

### Manifest v1.8 forecast/monthly-context dependency audit

Evidence:

- live forecast-state schema audit: GitHub Actions run `33512445624`, job `99871192709`, `SUCCESS`, read-only Neon transaction; all three forecast-state tables existed and each had 0 rows;
- retained Patch input package ended at `core5` month `2026-07-01`; retained Patch runners contain July/August horizon constants, therefore `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`;
- canonical-history forensic: run `33513175499`, job `99873596626`, `SUCCESS`; exact original VW-MIDAS-SVR Adapt V2 runner/source chain was not recovered from reachable canonical history; rebuild scripts exist but are explicitly reconstruction/research paths, not identity proof;
- `r4_1/contracts.py` requires both `monthly_vw_forecast` and `monthly_direction` in every `EngineSnapshot`; neither may be silently replaced with RW/Patch/live spot;
- NY17 history-depth probe run `33513634775`, job `99875100590`, `SUCCESS`, proves exact 16:59 ET Twelve bars are accessible from May through August 2026 on sampled dates, but the first atomic July-August backfill run `33512957983`, job `99872871327`, failed before persistence due transient provider/request errors.

Canonical audit record: `gold_axis_2026/GOLD_CONTROL_STAGE4_FORECAST_ISSUANCE_AUDIT_2026-09-01.md`.

### Operational work that continues independently

- XAU ingestion remains degraded while the frozen XAUS endpoint returns HTTP 503.
- Cboe, Fed, GPR, FRED-index and Twelve jobs must remain independently runnable; XAU failure must not block them.
- No alternate XAU provider may be silently relabeled as the frozen XAUS source.

---

# 25. CURRENT APP CONTRACT / TECHNICAL DEBT

Current Streamlit paths:

- `gold_axis_2026/apps/gold_control.py`
- `gold_axis_2026/apps/live_sources.py`

Current app information architecture now matches the canonical primary workflow:

`Piyasa / Görünüm / Tahmin / Geçmiş`

Stage 5 data/display semantics are frozen and smoke-tested. Pixel-level design refinement and mobile interaction QA remain later Stage-10 work; they must not reintroduce fabricated metrics, action mapping, or provider ambiguity.

Current latest-state dependency:

- `gold_axis_2026/apps/decision_source.py` reads the production Neon Decision Store;
- display priority is `LIVE_PRODUCTION`, then explicitly labelled `PROSPECTIVE_SHADOW`;
- `HISTORICAL_REPLAY` is never surfaced as the current decision;
- if neither prospective class exists, the app shows `KANONİK KARAR YOK` rather than deriving a decision from live spot.

The previous file-only `gold_axis_2026/r4_1/output/latest_signal.json` dependency has been removed from the app path.

Current live/display adapter contract after manifest v1.13:

- XAU spot display primary: `XAU_SPOT_GOLDAPI` — indicative monitoring only, explicit source/freshness, never model/EOD/decision input;
- XAU spot legacy/secondary: `XAU_SPOT_XAUS` — separate degraded lineage, no silent provider merge;
- XAU daily display history: `XAU_DAILY_XAUS` — explicitly labelled operational cross-check only; current-day row excluded from last-completed-daily comparison;
- canonical decision EOD: `XAU_EOD_TWELVE_NY17` — internal model/decision reference, raw numeric value not rendered without separately proven Twelve display rights;
- GVZ: Cboe daily history / latest close;
- Stage 5 Piyasa UI contract: PASS by run `33521193615`, job `99900581399`.

Do not pretend the current adapter already provides full intraday history or unlimited historical range. Do not use Twelve raw vendor data in a public/external display path unless the applicable subscription/display rights are separately proven.

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
