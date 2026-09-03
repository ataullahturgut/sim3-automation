# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.24
**Freeze / issue date:** 2026-09-03
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
9. exposes the result through a simple user-facing interface without leaking backend complexity into the main UX,
10. exposes a complete governed forecast/direction/event/regime/risk motor inventory so users can verify what is running, waiting, blocked, or not proven before any later selector/final-decision research.

The product is a **decision-support system**, not an autonomous self-learning trading system.

---

# 2. PRIMARY SYSTEM QUESTION FLOW

The frontend must answer four questions in this order:

1. **Piyasa** — Piyasa şu anda ne durumda?
2. **Görünüm** — Hangi tahmin/yön/event/regime/risk motorları mevcut, hangileri çalışıyor veya blocked, son meşru çıktıları nedir ve sistem neden böyle düşünüyor?
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
- `gold_axis_2026/data_pipeline/source_contracts_successor.json`
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

Historical outcome/data-plane support:

- the locked CORE5 monthly gold target remains the canonical historical H=1 research target artifact;
- `XAU_MONTHLY_WB_PINKSHEET` is retained as a separately named World Bank historical data-plane lineage because the 127-month identity audit showed material equivalence to CORE5; it is not relabelled as CORE5 and does not redefine the forecast product;
- `XAU_EOD_TWELVE_NY17` remains the daily R4 decision-reference lineage; monthly forecast target and daily decision reference are intentionally different roles.

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
| VW-MIDAS-MSVR audited | ~2.672 | audited analytical shadow/reference; exact original runner not recovered |
| Causal Patch R1 archived | ~3.03–3.08 depending exact closure artifact | historical Patch evidence; exact old training source/identity not fully recovered |
| 3M Momentum R1 | ~3.297 | reproducible direction challenger/context |
| Random Walk R1 | ~3.302 | mandatory naive benchmark |

## 7.A CANONICAL CORE FORECAST / DECISION LOGIC — v1.21

This subsection freezes the **system-level forecasting and decision logic**. It is the architectural rule that governs how the monthly forecasting layer and intramonth decision layers relate to one another.

### Binding core logic

1. **The next calendar month's average XAU/USD price is a multi-expert monthly forecasting problem.** The system architecture is not defined as a single-model forecast system.
2. The monthly expert set is:
   - **Causal Patch Transformer**;
   - **VW-MIDAS-MSVR**;
   - **3M Momentum**;
   - **Random Walk (RW)** as the mandatory benchmark, not as a promoted expert solely because it is simple.
3. Each monthly expert output must remain separately identifiable and auditable by target month, forecast origin, model/version identity, evidence class and point-in-time-safe input lineage.
4. The monthly forecast layer provides the system's **strategic monthly direction/prior/context**. This monthly view is an anchor for the decision system; it is **not an unconditional daily execution instruction**.
5. The intramonth system must **not follow the monthly forecast blindly**. As new eligible information becomes available during the month, the daily/weekly state is updated through the separately governed tactical, event, emergency, regime and risk layers.
6. The intramonth layer roles remain distinct:
   - **Fast / Slow:** tactical confirmation / conflict state; not a permanent hard exposure gate;
   - **Macro Event:** event-risk state only when its timestamp-safe rule is fully recovered/frozen; current incomplete historical reconstruction remains `BLOCKED_NOT_FULLY_RECOVERED`;
   - **Emergency:** intramonth abnormal-move / reversal alert layer capable of identifying conditions that the monthly anchor cannot update quickly enough;
   - **BOCPD:** regime/break context and alert only; not a standalone price forecast or direction generator;
   - **GVZ:** volatility/risk-cap layer; it constrains risk and does not determine gold direction.
7. Therefore a valid intramonth state may **disagree with the monthly prior**. Any resulting final decision state must still come only from a frozen, audited mapping/engine and must preserve the true information set available at that time. No later outcome may be used to retrofit an execution rule.
8. The exact archived **expert-selection / aggregation rule** that produced different lead experts in the 2026 replay has not yet been proven from executable historical logic. Its status is `NOT_PROVEN_EXPERT_SELECTION_RULE`. No selector or ensemble rule may be invented from observed 2026 outcomes and presented as historical or production authority.
9. Until that selector/aggregation contract is recovered or newly frozen under change control, **auto selector remains OFF and auto ensemble remains OFF**. Individual expert forecasts may be compared and stored, but a composite or selected canonical forecast requires an explicitly governed rule.
10. The operational role freeze below may designate a currently reproducible forward issuer candidate (for example Patch V7) for ledger issuance. That operational limitation **does not redefine the Gold Control architecture as a single-model forecasting system**.

Canonical system summary:

```text
Multi-Expert Monthly Forecast Engine
  ├─ Causal Patch Transformer
  ├─ VW-MIDAS-MSVR
  ├─ 3M Momentum
  └─ Random Walk benchmark
          ↓
Monthly Direction / Prior / Context
          ↓
Fast / Slow tactical confirmation-conflict
          ↓
Macro Event state (only when contract-complete)
          ↓
Emergency intramonth reversal / abnormal-move layer
          ↓
BOCPD regime / break context
          ↓
GVZ risk cap
          ↓
Frozen Final Decision State
          ↓
Immutable Decision Snapshot / Event Ledger
```

**Binding interpretation:** the monthly forecast establishes the strategic anchor; the intramonth system incorporates newly available information and may confirm, conflict with, or react against that anchor only through separately frozen rules.

## 7.B BUILD-FIRST / SELECT-LATER EXECUTION POLICY — v1.22

This subsection freezes the implementation order for the multi-expert monthly forecast system.

### Binding execution order

1. **Build the multi-expert forecasting substrate before selecting a winner.** The system must first be able to run, identify, persist and compare the separately governed outputs of Causal Patch Transformer, VW-MIDAS-MSVR, 3M Momentum and the Random Walk benchmark.
2. During this build phase, **no expert is promoted to canonical authority merely because it looks best on already observed 2026 outcomes**. The existing operational forward-issuer role freeze remains separate from the architectural multi-expert design.
3. `auto selector = OFF` and `auto ensemble = OFF` remain binding while the substrate and clean forecast history are being built.
4. The Early Indicative lane may be implemented before an expert selector exists. On each eligible completed-session update, every executable expert is recomputed using only point-in-time-safe information available at that `as_of` time; each expert result is stored separately with target month, origin/as-of time, model/version identity, immutable input lineage and evidence class.
5. Early Indicative outputs are **not** the canonical month-end H=1 forecast and must not be merged into the official month-end prospective scorecard. They form a separate forecast-revision history for the same fixed target month.
6. Only after a sufficiently clean comparable expert history exists may a selector/aggregation research phase begin. Candidate selection/combination rules must be learned and validated with leakage-safe rolling/expanding-origin procedures using only information available before each evaluated origin.
7. Selector/aggregation research must compare against at least the individual experts, Random Walk and simple transparent combination baselines where applicable. A more complex selector is not accepted merely because it wins one episode or one recent year.
8. A selector/aggregation rule may become canonical only through explicit change control, with a named version, frozen rule, reproducible code, provenance, robustness evidence and prospective-compatible validation.
9. If no selector/aggregation rule demonstrates stable incremental value, the system keeps the expert outputs separate and does **not** force a synthetic winner for presentation convenience.
10. The purpose of this order is to generate the unbiased evidence required to choose the best selection/aggregation mechanism later, rather than choosing the mechanism first and then backfitting the evidence to it.

Canonical implementation sequence:

```text
Build Multi-Expert Forecast Pipeline
        ↓
Persist Separate Expert Outputs + Immutable Inputs
        ↓
Run Early Indicative Revision Track with New PIT-Safe Data
        ↓
Accumulate Comparable Historical / Prospective Evidence
        ↓
Research Selector / Combination Rules
        ↓
Leakage-Safe Rolling-Origin Validation
        ↓
Change-Control Decision: FREEZE SELECTOR / KEEP EXPERTS SEPARATE
```

**Binding interpretation:** infrastructure and clean evidence come first; expert selection comes later. No future selector may be justified by hindsight from the outcomes it is supposed to predict.

## 7.C ALL-ENGINE OBSERVABILITY / INVENTORY-FIRST POLICY — v1.23

This subsection freezes the user-facing observability requirement before any future expert-selection or final-decision research.

Binding contract:

`gold_axis_2026/GOLD_CONTROL_ENGINE_OBSERVABILITY_CONTRACT_2026-09-03.md`

Status:

`FROZEN_ALL_GOVERNED_ENGINES_VISIBLE_V1`

Binding rules:

1. **All governed forecast and direction-related motors must remain visible as inventory items even when they have no issued value.** `BLOCKED`, `NOT_PROVEN`, `WAITING`, and `NOT_ISSUED` are legitimate observable states and must not collapse into a blank card.
2. The frozen inventory covers the four monthly H=1 experts (Causal Patch, VW-MIDAS-MSVR, 3M Momentum, Random Walk), the stored Monthly Direction 3M channel, Fast, Slow, Macro Event, Emergency Level, Emergency Reversal, BOCPD, and GVZ risk context.
3. Each item must expose its role, latest legitimate output if one exists, explicit operational status/blocker, model/feature version, evidence class, target/as-of context, and whether it is permitted to cast a direction vote.
4. A stored direction context is **not** an H=1 point forecast. In particular, `MONTHLY_DIRECTION_3M` may be displayable while the `MOMENTUM_3M` H=1 monthly-level expert remains `BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`.
5. GVZ remains risk-only and must never be rendered as a bullish/bearish direction vote.
6. Historical replay may be displayed as research evidence but may never be silently promoted to a current prospective/live output.
7. The application remains a read/presentation layer; it may not invent missing outputs, recompute production direction from live spot, or substitute providers/values merely to populate the inventory.
8. `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_EXPERT_SELECTION_RULE`, and `NOT_PROVEN_POSITION_MAPPING` remain unchanged. Engine visibility does not authorize a winner, composite forecast, or action mapping.
9. The implementation sequence is now explicitly: **see all motors → verify operation/evidence → accumulate clean comparable outputs → research selector/decision rules later**.
10. The existing `APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2` remains the visual-shell authority; this v1.23 contract extends content completeness/observability and does not change model methodology.

Authority rationale: the 2026 Federal Reserve/OCC/FDIC revised model-risk guidance emphasizes comprehensive model inventory, ongoing monitoring, limitations, outputs and functioning status; NIST AI RMF Govern 1.6 calls for mechanisms to inventory AI systems; NIST AI 800-4 emphasizes post-deployment functionality/operational monitoring. Gold Control adopts these principles as internal engineering governance, without claiming banking-regulatory applicability.

## 7.1 H=1 role freeze — restored agreed architecture

The active H=1 development path is **not a broad model search**.

Frozen roles:

- **Intended forward point-forecast issuer candidate:** `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE` — Patch V7. It retains the frozen Patch Transformer geometry `L=252`, `P=21`, `D=32`, uses the V6 origin-safe daily-train/hourly-anchor monthly-level architecture, and adds the completed-session daily-feature rule `observation_date < origin_date`. V7 locked historical model-impact gates passed with zero same-origin daily-feature use, zero future-information violations, deterministic rerun equality, and performance better than RW on the frozen 43-month window. Evidence remains `HISTORICAL_REPLAY_MODEL_IMPACT`; no live/prospective performance claim is made until a real pre-outcome forecast is issued. `CAUSAL_PATCH_R1_REPRO_V1` remains immutable predecessor evidence and the exact archived historical Patch executable identity remains separately unproven;
- **Audited shadow/reference:** `VW_AUDITED_SHADOW_V2` — historical analytical reference; exact original executable runner remains `BLOCKED_NOT_PROVEN`;
- **Direction challenger/context:** `MOMENTUM_3M_R1`;
- **Mandatory naive benchmark:** `RW_R1`;
- **Auto selector:** `OFF`;
- **Auto ensemble primary:** `OFF`.

The simple monthly Ridge/Huber/SVR/Drift/Damped R2 successor lane introduced on 2026-09-01 is retired from the active production-development path. Its prior run remains recoverable in Git history as a negative historical experiment; it is not the next canonical model lane.

Binding correction record:

`gold_axis_2026/GOLD_CONTROL_FORECAST_PATH_CORRECTION_2026-09-02.md`

Active reproducibility contract:

`gold_axis_2026/GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`

The earlier successor R1/change-control documents are retained only as audit evidence of the failed exact legacy identity-recovery attempt. They do not override this v1.16 role freeze.

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

Manifest v1.19 operational update: forecast-writer schema audit `FORECAST_WRITER_SCHEMA_AUDIT_PASS` confirmed identity/PK/unique/immutable guards; read-only writer rehearsal `PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS` validated insert plans with zero persistent rows and no identity consumption; first-shadow preflight `FIRST_SHADOW_ISSUER_PREFLIGHT_PASS_WAITING_FOR_ELIGIBLE_ORIGIN` confirmed the ledger remains empty and the earliest eligible target/origin is October 2026 / end-September. No forecast has yet been issued.

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

## 17.6 Final mobile mockup contract V2

Binding presentation specification:

`gold_axis_2026/GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V2_FINAL_MOCKUPS.md`

Status: `APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2`.

This V2 contract supersedes V1 for presentation structure. It does **not** change model, source, forecast, decision, threshold, evidence, licensing, or point-in-time semantics.

The latest approved mockup family is now the canonical visual target for `Görünüm`, `Tahmin`, and `Geçmiş/Performans`; `Bugün` / canonical `Piyasa` must be restyled into the same shell.

### Global mobile shell — binding

Every primary screen must use the same product shell:

- compact white institutional header;
- Gold Control logo + `DECISION SYSTEM` subtitle;
- menu affordance on the left;
- notification/profile controls only if implemented, never decorative dead controls;
- page title, short subtitle, and real last-update/freshness timestamp when available;
- white/light cool-neutral page surface;
- deep navy primary hero where the mockup uses one;
- controlled gold brand/selection accent;
- green only for favorable/up/normal state;
- red only for adverse/down/alert state;
- restrained white cards with subtle cool-gray border/shadow;
- four-item bottom navigation: `Bugün | Görünüm | Tahmin | Geçmiş`;
- one consistent navy/gold selected-state treatment across the four tabs.

`Bugün` remains only a user-facing alias for canonical `Piyasa`.

### Görünüm — final mockup hierarchy

The screen order is frozen as:

1. `GÖRÜNÜM` page header + last update;
2. deep navy primary state hero;
3. `1 · SİNYAL ÖZETİ`;
4. `2 · MODEL YÖNÜ (AYLIK)`;
5. `3 · FAST / SLOW TEYİDİ`;
6. `4 · RİSK SEVİYESİ`;
7. `5 · SİNYAL ZAMAN ÇİZELGESİ`;
8. `6 · EMERGENCY DURUMU`;
9. `7 · SİSTEM YORUMU`;
10. explanatory footer note;
11. bottom navigation.

The hero composition is also frozen: primary stored state on the left/center, monthly context on the upper-right, GVZ/risk state on the lower-right, plus a real system-health pill only when supported.

Mockup-to-production substitutions are mandatory:

- `POZİSYONU KORU` slot -> stored descriptive R4 classification;
- `MODEL YÖNÜ` -> stored monthly direction/context;
- `RİSK SEVİYESİ` -> frozen GVZ risk-state translation;
- `SİSTEM AKTİF` -> only a real health state;
- signal timeline -> actual stored decision/model events only;
- system comment -> deterministic explanation generated only from stored state.

The following visible mockup content remains blocked until separately proven: `POZİSYONU KORU`, position/action labels, BUY/SELL/HOLD/EXIT/REDUCE, `Güç %`, and arbitrary confidence labels.

### Tahmin — final mockup hierarchy

The screen order is frozen as:

1. `TAHMİN` page header + last update;
2. deep navy `GELECEK AY TAHMİNİ` hero;
3. `GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI` chart;
4. scenario/module row, only when a canonical scenario contract exists;
5. `MEVCUT FİYATA GÖRE FARK`;
6. `MODEL PERFORMANSI`;
7. methodology / non-advice information note;
8. bottom navigation.

The hero layout is frozen but data-gated:

- left slot = canonical immutable H=1 point forecast from `monthly_forecast_contracts` after issuance;
- right slot = separately stored/frozen monthly direction context;
- target month, evidence class and origin/issued time must remain available in the UI hierarchy.

Before a valid issuance, the hero must show `TAHMİN HENÜZ YAYIMLANMADI` and `NOT_ISSUED_IN_CANONICAL_LEDGER`, never a mockup number.

The mockup's confidence gauge, `Güven %`, lower/base/upper scenario values and forecast band are reserved visual slots only and remain hidden until a calibrated scenario/interval contract is frozen, prospectively validated and immutably stored.

The three-card `Baz / Yukarı / Aşağı` row has current status `BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT`. It may not be populated by inventing scenarios or by relabelling VW/RW references as upside/downside cases.

`MEVCUT FİYATA GÖRE FARK` may compare the current indicative display spot with the issued H=1 point forecast when both are available; this is a comparison, not expected return.

`MODEL PERFORMANSI` must use realized prospective/live forecast rows for production-facing metrics. Historical replay belongs in a separately labelled research surface.

### Geçmiş / Performans — final mockup hierarchy

The bottom-navigation key remains `Geçmiş`; a user-facing `PERFORMANS` page heading is allowed.

The screen order is frozen as:

1. page header + last update;
2. four summary metric cards;
3. large primary history/performance chart;
4. secondary timeline/risk/error chart;
5. selected historical records table/list;
6. evidence/methodology footer;
7. bottom navigation.

The four-card row is visually binding but labels are data-contract dependent. Under the current production contract, preferred production-safe metrics are realized prospective forecast count, prospective MAPE, prospective MAE USD, and prospective direction hit rate only if direction has a frozen definition. Insufficient history renders an empty/not-enough-history state.

The original mockup's YBB strategy return, 12-month strategy return, portfolio maximum drawdown, trade count, entry/exit prices, trade return, `DOĞRU/YANLIŞ` trading outcome, strategy equity curve and buy-and-hold outperformance remain blocked until an audited execution/portfolio contract exists.

The primary chart slot should therefore use actual-vs-issued forecast history or another frozen forecast-performance view until a strategy ledger exists. The secondary drawdown/timeline slot may use forecast error plus actual stored event markers; it must not fabricate portfolio drawdown.

`HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, and `LIVE_PRODUCTION` must remain visibly separate. Replay metrics may not populate prospective summary cards.

### Final mockup interpretation rule

The final mockups are authority for **layout and visual hierarchy**, not for example values.

If a mockup slot lacks an authorized datum, the slot is hidden, empty-stated, or relabelled truthfully. It is never filled with a placeholder number merely to preserve visual balance.

If implementation and the V2 mockup structure disagree, V2 controls presentation. If V2 presentation and canonical data/model/evidence semantics disagree, the canonical semantic contract controls content truth.

Implementation candidate remains `gold_axis_2026/apps/gold_control_mobile_v1.py`, but it must be reconciled to this V2 hierarchy before Stage-10 mobile QA can pass.

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
| 10 | **Mobile QA** | Final V2 mockup hierarchy, phone viewport behavior, empty states and semantic gates validated |
| 11 | **Prospective Shadow Run** | New forecasts/decisions stored before outcomes, immutable ledger accumulating |
| 12 | **Production Graduation** | Predefined prospective acceptance gates satisfied |

Dependency rule frozen by manifest v1.10:

Final-mockup rule added by manifest v1.20:

- Stage 10 is not a generic responsive-design check; it must validate fidelity to `GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V2_FINAL_MOCKUPS.md`.
- Mockup layout slots may remain hidden/empty when their data contract is unresolved; a visual placeholder never satisfies a stage gate.
- `Görünüm`, `Tahmin`, and `Geçmiş` implementation must preserve the final V2 section ordering unless a later explicit UI change-control supersedes it.

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

## 23.1 Current roadmap status — 2026-09-02

| Stage | Current status | Evidence / blocker |
|---|---|---|
| 0 | `PASS` | Manifest read-first contract active |
| 1 | `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS` | Data inventory/lineage audited; useful 2026-09-01 historical/PIT backfill retained |
| 2 | `PASS_CONTRACT_CANONICALIZED; FORECAST_NOT_ISSUED` | H=1 target/origin and restored Patch/VW/3M/RW role registry frozen; no prospective H=1 row exists |
| 3 | `PASS_DECISION_STORE_AND_READ_PATH` | Production append-only store/read path active; no fabricated current decision |
| 4A | `PASS_CURRENT_STATE_SUBSTRATE_FOR_SHADOW_CONTEXT` | NY17 backfill SUCCESS; monthly direction bootstrap issued; Fast/Slow rehearsal SUCCESS; forecast-state append-only guards 3/3 |
| 4B | `PATCH_V7_MODEL_IMPACT_PASS; R4_2_BRIDGE_PASS; WRITER_PREFLIGHT_PASS; WAITING_ELIGIBLE_ORIGIN` | V7 completed-session PIT gate PASS; generic monthly-reference→Emergency bridge PASS; forecast schema + read-only writer rehearsal + first-shadow preflight PASS. Forecast/input ledgers remain empty until a real eligible origin; complete forward EngineSnapshot/Decision Store issuance remains outstanding. |
| 5 | `PASS_PIYASA_SCREEN_CONTRACT` | Canonical Piyasa implementation + deterministic/live Streamlit smoke PASS |
| 6 | `BLOCKED_NO_DISPLAY_ELIGIBLE_DECISION_SNAPSHOT` | No complete forward stored decision row may be fabricated |
| 7 | `BLOCKED_FORECAST_NOT_ISSUED` | Canonical H=1 forecast ledger has no issued row |
| 8–12 | `NOT_STARTED / NOT_COMPLETE` | Their own dependency gates are not satisfied |

The architecture remains the agreed six-layer system: data plane → H=1 forecast/monthly context → Fast/Slow tactical → BOCPD break → Emergency → GVZ risk/Decision State. The R2 detour did not alter those layers.

---

# 24. IMMEDIATE NEXT WORK

The immediate canonical task is now:

## `STAGE 4B — PATCH V7 FORWARD ISSUER PREPARED; COMPLETE ENGINE SNAPSHOT + REAL ELIGIBLE-ORIGIN ISSUANCE; DO NOT REOPEN MODEL SEARCH`

Completed and frozen:

1. `CAUSAL_PATCH_R1_REPRO_V1` geometry was selected only on pre-2023 development data: `L=252`, `P=21`, `D=32`;
2. the original reproducible Patch locked replay established historical eligibility under the frozen 43-month window; archived exact historical Patch executable identity remains separate and unproven;
3. prospective-input bridge V1 failed closed and did not authorize substitution, threshold relaxation, or production issuance;
4. V2 was closed as `FAIL`;
5. V3 repaired the NASDAQ continuation without changing model geometry: 199 monthly comparisons, 0 missing, 86/86 locked completed-month inputs availability-safe, 0 availability violations; DFF/FEDFUNDS and DEXCHUS/USD-CNY semantics remained passed;
6. current Twelve entitlement proved `XAU/USD` accessible while `XAG/USD`, `XPT/USD`, and `XPD/USD` require higher provider entitlement; alternative Nasdaq Data Link/CME four-metal probes returned HTTP 403 and were not treated as usable;
7. V4 change-control was frozen before result inspection: Patch architecture unchanged, `L=252`, `P=21`, `D=32`; daily metals changed from four channels to XAU only; Silver/Platinum/Palladium are `OMITTED_NOT_IMPUTED` with no zero-fill, stale carry-forward, synthetic proxy, futures substitution, or silent provider mixing;
8. V4 source gate passed by workflow run `33606111783`, job `100170350792`: Twelve XAU full history contained 4487 daily observations from `2010-01-01`, including 302 observations before the original first model boundary; NASDAQ/FEDFUNDS/USD-CNY inherited/validated source gates passed; raw vendor prices were not logged and no database/forecast/decision writes occurred;
9. V4 locked model-impact replay passed by workflow run `33606337904`, job `100171077252`: target reconciliation `43/43`, RW reconciliation `43/43`, deterministic max absolute difference `0`, future-information violations `0`, V4 MAPE `3.133034811%` < RW `3.302322023%`, V4 MAE `102.233331072` < RW `107.465116279`, V4 worst APE `9.021401201%`, RW worst APE `9.625880596%`, worst-APE ratio `0.937202691`, `V4_MODEL_IMPACT_PASS=true`;
10. model-impact evidence is explicitly `HISTORICAL_REPLAY_MODEL_IMPACT`, `prospective_claim=false`; geometry was not reselected, no post-result retune occurred, and Neon / forecast ledger / Decision Store writes remained `NONE`.

Active successor identity after the V4 source + model-impact gates:

`CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`

This identity must be frozen as a versioned executable/input contract before it is allowed to issue any forward forecast. It does not inherit the exact archived Patch executable identity claim.

Remaining Stage-4B dependency gates after v1.19 reconciliation:

1. V7 completed-session Patch identity is the active forward issuer candidate: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`; do not reopen broad model search or retune from locked outcomes;
2. R4.2 generic monthly-price-reference → Emergency bridge is validated; do not relabel the generic reference as historical `monthly_vw_forecast`;
3. forecast DB schema/identity/immutability audit and read-only writer rehearsal are PASS; no real forecast row is authorized before an eligible origin;
4. first-shadow issuer preflight is PASS and correctly returns `SKIP_NOT_ELIGIBLE_ORIGIN` on 2026-09-02; September remains non-backfillable;
5. first possible contract-compliant target remains October 2026 at the end-September origin, after the issuer's availability/time gates close;
6. a complete versioned forward `EngineSnapshot` and subsequent Decision Store write still must be built from the actually persisted forecast contract/snapshot IDs;
7. first real forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` requires later prospective graduation gates;
8. operational scheduler/dispatcher must actually execute from the repository default-branch scheduling surface without moving model authority out of `gold-r4-direction-engine`.

Stage 5 remains closed as `PASS_PIYASA_SCREEN_CONTRACT`. Stage 6 remains blocked until a display-eligible stored Decision Store state exists. October 2026 at the end-September origin remains only a possible next prospective target if every Stage-4B gate closes before that origin.

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

Confirmed active Stage-4B blockers after manifest v1.18 reconciliation:

1. `PATCH_V4_EXECUTABLE_INPUT_IDENTITY_NOT_YET_FROZEN_AS_FORWARD_ISSUER`
   - V4 source and locked historical model-impact gates passed, but the forward issuer contract/provenance still must be frozen before a real origin;
2. `R4_2_MONTHLY_REFERENCE_BRIDGE_NOT_VALIDATED`
   - Patch/V4 may not be silently inserted into the historical R4.1 `monthly_vw_forecast` identity; the generic monthly-reference → Emergency geometry must be validated explicitly;
3. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`;
4. `FORECAST_CONTRACT_NOT_ISSUED`;
5. `COMPLETE_FORWARD_ENGINE_SNAPSHOT_NOT_ISSUED`.

Closed/superseded Stage-4B input-semantic blockers:

- `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN` → **closed for the active V4 XAU-only path** by V3/V4 source evidence plus V4 locked model-impact PASS;
- `NASDAQCOM_MONTH_END_PIT_CONTINUATION_NOT_COMPLETE` → **closed by V3**: 199 comparisons, 0 missing, 86/86 locked input availability-safe, 0 availability violations;
- `PATCH_DAILY_METALS_OPERATIONAL_CONTINUATION_NOT_PROVEN` → the original four-metal continuation remains unproven and is **not** relabelled as passed; it is superseded for the active path by pre-frozen V4 change-control using accessible XAU only, with Silver/Platinum/Palladium `OMITTED_NOT_IMPUTED`;
- Twelve XAU V4 source continuation → **PASS** by run `33606111783`, job `100170350792`;
- V4 model-impact gate → **PASS** by run `33606337904`, job `100171077252`.

Retained provenance/reference limitations that do not authorize fabrication:

- `PATCH_R1_ARCHIVED_EXECUTABLE_IDENTITY_NOT_PROVEN` — old archived Patch exact identity remains historical-only; the V4 successor uses its own explicit identity;
- `VW_EXECUTABLE_IDENTITY_RECOVERY = BLOCKED_NOT_PROVEN` — VW remains audited shadow/reference and is not silently rebuilt or promoted as an executable production issuer.

Closed Stage-4B sub-gate:

- `PATCH_R1_REPRODUCIBLE_PRODUCTION_IMPLEMENTATION_NOT_YET_VALIDATED` → **closed for HISTORICAL_REPLAY only** by run `33600343405`, job `100152429384`; deterministic replay PASS, Patch beat RW on MAPE and MAE. This does not constitute a prospective issuer approval.

Useful data readiness retained from 2026-09-01:

- CORE5 ↔ World Bank target identity audit PASS over 127/127 months;
- governed Neon historical/PIT backfill wrote 639 source-labelled observations and did not create a forecast contract;
- ALFRED DGS10/DFF/DEXCHUS/NASDAQ100 PIT reconstructions remain data-plane assets, but they do not force those variables into the Patch model beyond the frozen Patch contract.

Retired-model-path note:

- the simple R2 Ridge/Huber/SVR/Drift/Damped replay is no longer an active production-development lane;
- its Git history is retained for audit, but active R2 contract/runner/score artifacts were removed from the canonical tree on 2026-09-02.

Legacy executable-identity audit evidence remains valid: the old VW/Patch exact executable identities were not recovered. This is a provenance fact, not a mandate to abandon the agreed Patch/VW role architecture.

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

**Stage-4B H=1 forecast lane (fail-closed for prospective issuance):**

1. `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE` is the active Patch issuer candidate after V6 monthly-level source/model gates plus V7 completed-session PIT historical model-impact PASS; its predecessor and archived artifacts remain immutable historical evidence;
2. do not add Ridge/Huber/SVR/DOW/DMA/new Transformer variants or other model families merely because remaining production integration gates are difficult;
3. keep `VW_AUDITED_SHADOW_V2` as audited reference, `MOMENTUM_3M_R1` as direction context, and `RW_R1` as benchmark;
4. freeze the V4 executable/input identity and provenance without any post-result retuning;
5. validate the generic monthly-price-reference/Emergency bridge before building a complete EngineSnapshot;
6. before a real eligible month-end origin, persist immutable forecast input snapshot + forecast contract;
7. first forward forecast/decision evidence remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`;
8. September 2026 may not be backdated; October 2026 remains only a possible next fully compliant target if all gates close before the end-September origin.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B blocker prevents construction of the complete versioned EngineSnapshot. This does not block non-decision `Piyasa` monitoring.

### Manifest v1.19 Patch V7 / writer / mobile-UI reconciliation

New frozen evidence and product decisions on 2026-09-02:

- V5 hourly full-history monthly-level bridge failed closed on provider history entitlement; model scoring was skipped and thresholds were not relaxed;
- V6 daily-train/hourly-anchor monthly-level architecture passed source and locked model-impact gates without changing Patch geometry;
- V7 froze the final completed-session daily-feature correction before results: `TWELVE_XAU_USD_1DAY_OBSERVATION_DATE_STRICTLY_BEFORE_ORIGIN_DATE`; 43/43 origins used only strictly pre-origin daily observations, same-origin use 0, future-information violations 0, deterministic max diff 0;
- V7 candidate MAPE `3.212376055%` vs RW `3.302322023%`, MAE `104.214302424` vs RW `107.465116279`, worst APE `9.016478855%` vs RW `9.625880596%`; hard/performance/model-impact gates PASS; evidence remains `HISTORICAL_REPLAY_MODEL_IMPACT`;
- active forward candidate identity: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`;
- R4.2 generic monthly reference → Emergency bridge passed 5/5 tests while frozen R4.1 config remained unchanged;
- production forecast writer schema audit passed; `forecast_input_snapshots` and `monthly_forecast_contracts` remained 0 rows and immutable guards were verified;
- read-only writer rehearsal passed with insert-plan validation, 0→0 persistent rows and no identity consumption;
- first-shadow issuer preflight passed, September backfill remains forbidden, earliest eligible origin is 2026-09-30 after 17:20 America/New_York, first target October 2026; no forecast value has been issued yet;
- mobile product presentation is frozen by `GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V1.md`; approved mockup aesthetics do not authorize fabricated metrics or action mapping;
- mobile Streamlit implementation candidate begins at `gold_axis_2026/apps/gold_control_mobile_v1.py`, backed by canonical Decision Store/forecast-ledger readers and fail-closed empty states.

### Manifest v1.18 V3/V4 input-continuation and model-impact reconciliation

New frozen evidence on 2026-09-02, reconciled after manifest v1.17:

- V2 was closed `FAIL`; no threshold relaxation or silent substitution followed;
- V3 completed-month NASDAQ continuation passed: 199 monthly comparisons, 0 missing, 86/86 locked inputs availability-safe, 0 availability violations;
- Twelve entitlement proved `XAU/USD` available and `XAG/USD` / `XPT/USD` / `XPD/USD` unavailable under the current plan; alternative anonymous Nasdaq Data Link/CME four-metal probes returned HTTP 403;
- V4 source/input change-control was frozen before the result: retained Patch Transformer and `L=252`, `P=21`, `D=32`; active daily metal channel set became XAU-only; removed metals are `OMITTED_NOT_IMPUTED`;
- V4 source workflow run `33606111783`, job `100170350792`, `SUCCESS`; XAU history count 4487 from `2010-01-01`, with 302 observations before the original first model boundary; source gate PASS; raw vendor price logging NO; DB/forecast/decision writes NONE;
- V4 model-impact workflow run `33606337904`, job `100171077252`, `SUCCESS`; `V4_TARGET_RECONCILIATION=43/43`, `V4_RW_RECONCILIATION=43/43`, deterministic max diff `0`, future-information violations `0`;
- V4 MAPE `3.133034811%` versus RW `3.302322023%`; V4 MAE `102.233331072` versus RW `107.465116279`; V4 worst APE `9.021401201%` versus RW `9.625880596%`; worst-APE ratio `0.937202691`;
- `V4_HARD_GATE_PASS=true`, `V4_PERFORMANCE_GATE_PASS=true`, `V4_MODEL_IMPACT_PASS=true`, decision `PATCH_R1_V4_XAU_ONLY_MODEL_IMPACT_PASS`;
- evidence class remains `HISTORICAL_REPLAY_MODEL_IMPACT` with `prospective_claim=false`; no geometry reselection, no post-result retune, no Neon/forecast-ledger/Decision Store writes;
- evidence commit from the model-impact workflow: `ee9f68e7225e830b9156ba85a8333b61e68f1437`;
- active successor identity reserved by the frozen V4 change-control: `CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`.

This closes the active Patch prospective-input semantic blocker for the V4 XAU-only path **without** converting historical replay into prospective evidence. The remaining path is issuer identity freeze → monthly-reference/Emergency bridge → immutable forecast snapshot/contract → complete forward EngineSnapshot → first real `PROSPECTIVE_SHADOW`.

### Manifest v1.17 Patch reproducibility and prospective-input evidence

New frozen evidence on 2026-09-02:

- Patch pre-2023 geometry selection run `33600168927`, job `100151896585`, SUCCESS: `L=252`, `P=21`, `D=32`; locked score window not used for selection;
- Patch locked replay run `33600343405`, job `100152429384`, SUCCESS: target reconciliation `43/43`, RW reconciliation `43/43`, deterministic max absolute difference `0`, Patch MAPE `3.108253722%`, RW MAPE `3.302322023%`, Patch MAE `101.660660440`, RW MAE `107.465116279`;
- historical-replay status: `PATCH_R1_REPRO_V1_HISTORICAL_REPLAY_ELIGIBLE`; forecast/decision writes NONE;
- prospective-input bridge V1 contract frozen before audit: `GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V1.md`;
- bridge run `33602829565`, successful fail-closed attempt job `100161187043`, evidence commit `1a27dca699b6aa4c3c421156eafda6656d6061c4`;
- DFF→FEDFUNDS PASS `43/43`; DEXCHUS→USDCNY PASS `43/43`;
- NASDAQCOM hard gate FAIL `40/43` because origin months `2023-10`, `2023-11`, `2023-12` returned no valid month-end ALFRED reconstruction; available-month materiality was within the frozen threshold;
- metal continuation V1 overall FAIL/NOT_PROVEN: Gold coverage `29`, return correlation `0.776370092`, median return gap `83.777600 bps`, p95 `466.614818 bps`; Silver/Platinum/Palladium ended `HTTP_RETRY_EXHAUSTED` and are not semantic passes;
- overall bridge decision: `BLOCKED_PATCH_PROSPECTIVE_INPUT_SEMANTICS_NOT_PROVEN`;
- raw vendor values logged NO; DB, forecast-ledger and Decision Store writes NONE.

This evidence does **not** reopen model search and does **not** permit post-result threshold relaxation. The next work is versioned input-semantic correction only.

### Manifest v1.16 forecast-path correction and retained data evidence

The approved architecture was restored on 2026-09-02 after the simple R2 successor model-search detour was identified as inconsistent with the previously agreed H=1 role freeze.

Preserved evidence:

- CORE5 ↔ World Bank monthly target identity audit: run `33535312896`, job `99948062874`, `SUCCESS`; 127/127 common months, 123/127 exact, all within USD 0.50;
- governed Neon historical/PIT backfill: run `33538748716`, job `99959440836`, `SUCCESS`; 639/639 observations written, revisions 0, no forecast issuance;
- forecast-state counts after the write remained `forecast_input_snapshots=0`, `derived_feature_snapshots=1`, `monthly_forecast_contracts=0`;
- Decision Store, NY17, Fast/Slow, BOCPD, Emergency, GVZ and Piyasa contracts remain unchanged.

Rolled back from active path:

- R2 validation contract;
- R2 replay runner/workflow;
- active R2 score/prediction/evidence files;
- manifest instruction to continue Ridge/Huber/SVR/Drift/Damped as the next canonical forecast lane.

Binding replacement:

- `GOLD_CONTROL_FORECAST_PATH_CORRECTION_2026-09-02.md`;
- `GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`.

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

- `gold_axis_2026/apps/gold_control.py` — current canonical Stage-5 app;
- `gold_axis_2026/apps/gold_control_mobile_v1.py` — manifest-aligned mobile UI V1 implementation candidate;
- `gold_axis_2026/apps/live_sources.py`;
- `gold_axis_2026/apps/forecast_source.py` — read-only canonical forecast-ledger display reader;
- `gold_axis_2026/apps/mobile_ui_contract.py` — deterministic presentation-state contract.

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

## 7.D SIMPLE-EXPERT SOURCE BINDING V2 — FROZEN PASS / FORWARD READINESS

Status frozen on 2026-09-03 under `GOLD_CONTROL_SIMPLE_EXPERT_SOURCE_BINDING_V2_CHANGE_CONTROL_2026-09-03.md`.

- Source identity: `SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`.
- Provider/semantic: Twelve Data `XAU/USD`, `1h`, `America/New_York`; use the close of the bar opened at `16:00:00` and aggregate positive finite selected closes to the completed calendar-month arithmetic mean; minimum 15 unique selected dates; no interpolation/forward-fill/provider substitution.
- CME/EBS 17:00 ET trade-date-roll evidence is supporting market-session context; the Gold Control source remains explicitly a Twelve hourly-derived measurement and is not relabelled as an official EBS/LBMA/settlement fixing.
- Frozen validation window: `2023-01..2026-07`, `N=43`; historical evidence class `HISTORICAL_REPLAY_MODEL_IMPACT`, not prospective proof.
- Extended required source months `2022-09..2026-06`: 46/46 present, zero low-count months, zero duplicate selected dates.
- Extended source vs CORE5: level correlation `0.9999721441764589`; median gap `10.9548 bps`; p95 gap `33.2791 bps`; return correlation `0.9964220374584144`; return direction agreement `0.9555555555555556`.
- Actual/R1 reconciliation: actual `43/43`; RW R1 `43/43`; Momentum R1 `43/43`; future-information violations `0`; deterministic rerun max diff `0.0`.
- Random Walk V2 identity: `RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`; result `RW_R2_SOURCE_BINDING_MODEL_IMPACT_PASS`.
- 3M Momentum V2 identity: `MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`; result `MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_PASS`.
- Joint gate: `SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS`.
- No threshold relaxation, post-result retuning, provider substitution, database write, forecast-ledger write, or Decision Store write occurred during validation.
- Forward status after this PASS: both V2 experts are executable, but **no September 2026 origin may be backfilled**. Their first eligible H=1 month-end issuance remains the end-September 2026 origin for the October 2026 target, subject to the frozen source-completion and immutable-snapshot gates.
- Until an eligible origin is actually issued, UI status is `WAITING_ELIGIBLE_MONTH_END_ORIGIN`, not a fabricated forecast value.
- `NOT_PROVEN_EXPERT_SELECTION_RULE` remains binding; `AUTO_SELECTOR=OFF`; `AUTO_ENSEMBLE=OFF`; every individual expert remains `canonical_authority=false`.
- This change does not authorize BUY/SELL/HOLD/EXIT/REDUCE or exposure mapping.
