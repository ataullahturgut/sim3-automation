# GOLD CONTROL — HISTORICAL PILOT READINESS CONTRACT V1.45

**Date:** 2026-09-08  
**Status:** `FROZEN_BEFORE_HISTORICAL_GAP_COMPLETION_AND_BEFORE_GOLD_PILOT_V1_SCORING`  
**Scope:** readiness only; no model selection, no performance optimization, no production forecast/decision authority  
**Canonical project manifest:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` v1.45  
**Canonical branch:** `gold-r4-direction-engine`

---

## 1. Purpose

This contract defines, before historical gap completion and before `GOLD_PILOT_V1` scoring, how Gold Control determines whether each of the 12 governed engines can be replayed and evaluated for the frozen historical pilot window.

This contract is intentionally **not** a model-development contract and **not** a model-selection contract.

It answers only:

> For each governed engine and each pilot target-month cell, do the frozen source, timing, lineage, implementation and evidence requirements permit a valid historical replay/evaluation?

A readiness `PASS` does not mean the engine is accurate, useful, superior or production-ready. A readiness `BLOCKED` does not mean the model is intrinsically poor. It means the required evidence for that cell is not presently sufficient under the frozen rules.

---

## 2. Authority basis

The following are methodological authority benchmarks. They are not asserted to be legally binding on Gold Control.

1. **Federal Reserve / OCC / FDIC — Revised Guidance on Model Risk Management, SR 26-2, 17 Apr 2026.** Validation rigor should be proportionate to model purpose, approach, use, materiality and limitations; validation considers methods, data, implementation, monitoring and outcomes rather than only one performance statistic.
   - https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm
   - https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf

2. **NIST AI 800-4, Mar 2026 — Challenges to the Monitoring of Deployed AI Systems.** Pre-deployment evaluation and post-deployment monitoring answer different questions; field behavior and changing inputs require explicit monitoring and provenance.
   - https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-4.pdf

3. **Hyndman & Athanasopoulos, Forecasting: Principles and Practice — time-series cross-validation.** Forecast evaluation must preserve temporal order: each forecast origin may use only information from before that origin; random split is not valid for the governed forecasting problem.
   - https://otexts.com/fpp3/tscv.html

4. **CME Group EBS trading hours.** Spot FX & Precious Metals use a 17:00 ET trade-date roll. This supports the project's NY17 internal boundary but does not convert a Twelve Data observation into an official CME settlement/fixing.
   - https://www.cmegroup.com/trading-hours.html

5. **Twelve Data API documentation.** Intraday requests may use IANA timezone names such as `America/New_York`; historical requests may use explicit date/time bounds. Gold Control nevertheless freezes a stricter internal source semantic: `XAU/USD`, `1min`, exact `16:59:00 America/New_York`, close value only after OHLC validation.
   - https://twelvedata.com/docs

6. **Cboe historical volatility-index data.** Cboe publishes historical price data for the Cboe Gold ETF Volatility Index (`GVZ`). Gold Control uses this official historical source for the governed GVZ reconstruction lane.
   - https://www.cboe.com/tradable_products/vix/vix_historical_data/

Project-specific frozen contracts, source bindings and evidence in the canonical repository take precedence over generic authority examples whenever they are more specific.

---

## 3. Governance invariants

The following are binding throughout readiness construction and historical data completion:

- governed engine inventory remains exactly 12;
- `AUTO_SELECTOR = OFF`;
- `AUTO_ENSEMBLE = OFF`;
- `NOT_PROVEN_EXPERT_SELECTION_RULE` remains unresolved;
- `NOT_PROVEN_POSITION_MAPPING` remains unresolved;
- no automatic `BUY / SELL / HOLD / EXIT / REDUCE`;
- no model, threshold, feature, architecture, hyperparameter, role, source identity or evaluation rule may be changed because of 2025/2026 pilot results;
- no random split;
- no silent provider substitution;
- no interpolation or forward-fill of governed missing source observations unless an existing frozen model contract explicitly permits it; the current Gold Control contracts relevant to this pilot do not permit such substitution for canonical NY17;
- no backdating of retrieval or availability timestamps;
- no historical reconstruction may be relabelled `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`;
- no readiness audit may write forecast/decision/selector/ensemble/authority state;
- no engine is removed from the governed architecture during readiness solely because of a standalone performance result;
- performance and contribution are later gates; readiness is a prerequisite only.

Any substantive change after this freeze requires a separately named change-control/challenger identity and may not rewrite this frozen pilot.

---

## 4. Frozen pilot axis

### 4.1 Common pilot target-month cells

The shared pilot axis contains **20 target-month cells**:

- `2025-01` through `2025-12` — `RETROSPECTIVE_VALIDATION_WINDOW`
- `2026-01` through `2026-08` — `RETROSPECTIVE_FROZEN_OOS_TEST`

These labels describe the project evaluation design. They do **not** claim that these outcomes were unknown when V1.45 was written. Historical replay remains retrospective evidence.

### 4.2 Important terminology

The 20 cells are not forced into one identical forecast-origin semantic for all engines.

The engines have different roles and therefore different evaluation clocks:

| Role | Engines | Historical evaluation clock |
|---|---|---|
| Monthly H=1 price expert / benchmark | `CAUSAL_PATCH`, `VW_MIDAS_MSVR_SUCCESSOR_V1`, `MOMENTUM_3M`, `RANDOM_WALK` | month-end origin immediately before target month |
| Strategic monthly direction | `MONTHLY_DIRECTION_3M` | target-month open using completed prior months only |
| Tactical direction | `FAST`, `SLOW` | chronological intramonth replay at eligible completed market observations/weeks |
| Event-risk context | `MACRO_EVENT_SUCCESSOR_V2` | actual release timestamp / release-aware event timeline |
| Regime/break context | `BOCPD_RETURN_SUCCESSOR_V1` | completed-month update timeline |
| Emergency context | `EMERGENCY_LEVEL`, `EMERGENCY_REVERSAL` | chronological target-month NY17 replay against the immutable permitted monthly reference |
| Risk-only context | `GVZ_RISK` | chronological released Cboe GVZ observations |

Therefore a `12 x 20` matrix is a **readiness-cell matrix**, not a claim that all 12 engines issue the same forecast at the same timestamp.

---

## 5. Evidence classes and late historical retrieval

### 5.1 Evidence classes remain separate

- `HISTORICAL_REPLAY` — reconstructed after the historical event/origin under a frozen source/timing rule;
- `PROSPECTIVE_SHADOW` — legitimately issued by a deployed governed mechanism before the future outcome is known;
- `LIVE_PRODUCTION` — separately authorized production evidence only.

### 5.2 Truthful retrieval semantics

A market observation with an old `observation_ts` that is retrieved in September 2026 must retain its truthful September 2026 `retrieved_at` / `available_as_of` evidence where applicable. The project may not manufacture an earlier ingestion timestamp.

Late retrieval may support a **historical reconstruction** when:

1. the governing model/source contract explicitly permits historical reconstruction;
2. the source identity and timestamp semantic are preserved exactly;
3. the value is not silently substituted, interpolated or synthetically manufactured;
4. the replay is labelled retrospective;
5. later target outcomes are not used in feature construction, parameter selection, source selection or threshold selection.

Late retrieval alone does **not** establish that Gold Control possessed the value prospectively at the original origin.

### 5.3 Revision/vintage-sensitive data

For revision-prone or expectation-based inputs (macro releases, consensus, vintage-sensitive GPR), a final historical value is insufficient by itself. The frozen source contract must prove the required first-print / consensus / vintage / release-time semantic for the historical event.

---

## 6. Readiness dimensions

Each engine-cell must be audited across the following independent dimensions.

### D1 — `CONTRACT_PRESENT`
A frozen engine identity, role, formula/source rule and timing rule exist in canonical GitHub authority.

### D2 — `IMPLEMENTATION_BOUND`
The executable implementation/evidence identifies the same governed engine identity and frozen source/parameter semantics. Readiness audit does not redesign the model.

### D3 — `SOURCE_IDENTITY_VALID`
The exact governed source identity is used. A semantically similar series is not sufficient.

### D4 — `SOURCE_COVERAGE_VALID`
The observations required by the engine for the pilot cell and required prehistory are present or explicitly adjudicated under the source contract.

### D5 — `TIMING_PIT_VALID`
The replay obeys the engine's origin/release/completed-period rule and does not use target/future information.

### D6 — `LINEAGE_PROVEN`
Source IDs, observation timestamps, retrieval/availability metadata, lineage IDs or immutable artifact identifiers, input fingerprints and model/version identity are traceable at the level required by the frozen engine contract.

### D7 — `DETERMINISM_OR_REPRODUCIBILITY`
Where the engine contract requires deterministic replay/reproducibility evidence, that evidence exists or the cell is marked ready-to-run but not yet proven-executed.

### D8 — `CELL_REPLAY_STATUS`
Whether the specific historical cell has already been successfully replayed under the frozen identity.

Readiness does not include forecast accuracy, contribution, economic value, selection weights or action mapping.

---

## 7. Top-level readiness states

Each engine-cell receives exactly one top-level state plus reason codes.

### `READY_PROVEN`
All required dimensions pass and the frozen cell replay/evidence already exists.

### `READY_TO_REPLAY`
Contract, source, timing and lineage requirements are sufficient, but the specific cell has not yet been executed/reconciled under the frozen identity.

### `PARTIAL`
Some required evidence exists, but one or more required dates/subcomponents/prehistory elements remain unresolved. No scoring is permitted for the incomplete cell.

### `BLOCKED_DATA`
The governed source observations required for the cell are unavailable or cannot yet be obtained under the permitted source identity.

### `BLOCKED_PIT`
Data exist, but required release/vintage/origin-safe semantics are not proven.

### `BLOCKED_CONTRACT`
The intended historical cell is outside or inconsistent with the currently frozen engine contract and no non-substantive governed replay rule yet authorizes it.

### `IMPLEMENTATION_FAIL`
The implementation contradicts the frozen model/source/timing contract.

### `CONTRACTUAL_EXCLUSION`
The frozen model contract explicitly excludes the cell or event because complete-case conditions are not satisfied. This is reported, never silently imputed, and is not counted as an implementation failure.

A global engine status may summarize its 20 cells, but global `BLOCKED` never deletes the engine from the governed inventory.

---

## 8. Engine-specific readiness contracts

### 8.1 `CAUSAL_PATCH`

Role: monthly H=1 expert.

Governed requirements:

- use the existing frozen Causal Patch identity and its existing frozen inputs/features;
- preserve the completed-session, origin-safe daily-feature rule;
- target month `t` uses the immediately preceding governed month-end origin;
- no target-month observation may enter feature construction or model fitting;
- no geometry, architecture, feature, source, threshold or hyperparameter reselection;
- existing locked historical replay evidence may satisfy `READY_PROVEN` only for cells explicitly covered by that immutable evidence;
- a later cell outside existing replay evidence may be `READY_TO_REPLAY` only if the identical frozen identity and all required source data are available;
- historical replay remains non-prospective.

No later Causal Patch result may modify the engine during `GOLD_PILOT_V1`.

### 8.2 `VW_MIDAS_MSVR_SUCCESSOR_V1`

Role: monthly H=1 expert.

Required historical research inputs remain exactly:

- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`
- governed `GPR_OFFICIAL_GIT_PIT` origin-vintage lane under the frozen publication-lag rule;
- frozen target/recovery semantics from the successor contract.

Historical StakTrakr inputs remain historical-reconstruction research series; they are not relabelled canonical market PIT data.

For each cell:

- source completeness must satisfy the frozen model's four-metal requirements;
- required common dates must be present under the model contract;
- GPR vintage and publication-lag requirements must pass;
- nested rolling-origin tuning may use only prior eligible inner targets under the already frozen rule;
- no 2025/2026 result-driven hyperparameter grid or selection-rule change is permitted.

Historical replay success never establishes prospective four-metal source readiness.

### 8.3 `MOMENTUM_3M`

Role: monthly H=1 expert.

Current identity:

`MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

Governed source:

`SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`

Requirements:

- only completed prior months;
- target-month observations forbidden;
- source-bound R2 identity must remain unchanged;
- historical input set may be reconstructed from the governed R2 source only under its frozen source-binding evidence and minimum-observation rule;
- existing 43-origin immutable replay evidence may establish `READY_PROVEN` only for covered cells;
- later uncovered cells require deterministic replay/reconciliation with no rule changes.

### 8.4 `RANDOM_WALK`

Role: mandatory monthly H=1 benchmark.

Current identity:

`RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

Governed source:

`SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`

Requirements:

- forecast equals the governed prior completed monthly mean under the frozen R2 source rule;
- target-month observations forbidden;
- source-bound identity cannot be silently replaced by canonical daily XAU or another monthly gold series;
- covered immutable replay evidence may be `READY_PROVEN`; uncovered cells require deterministic replay under the same identity.

### 8.5 `MONTHLY_DIRECTION_3M`

Role: strategic direction/prior, not an H=1 price expert.

Governed source:

`XAU_EOD_TWELVE_NY17`

Frozen formula:

- last three **completed** monthly returns only;
- arithmetic mean of the three completed monthly returns;
- positive => `UP`, negative => `DOWN`, zero => `NEUTRAL`.

Historical readiness for target month `t` requires:

- sufficient completed prior-month canonical NY17 references to derive the last three monthly returns (therefore the required prior level history as well);
- no target-month NY17 observation in the month-open state;
- exact governed canonical-source semantics or an explicitly governed historical NY17 reconstruction lane that preserves the same source/bar identity;
- truthful reconstruction metadata.

A daily/5m/hourly substitute is forbidden for this engine's historical NY17 lane.

### 8.6 `FAST`

Role: tactical direction context.

Governed source:

`XAU_EOD_TWELVE_NY17` only.

Frozen rule:

- SMA20;
- persistence = two completed trade-date states;
- at least 21 ordered daily closes are needed to evaluate the two latest SMA20-relative states without `INSUFFICIENT_DATA`.

Historical target-month cell readiness requires:

1. historical NY17 reconstruction for all required accepted session observations in the target month and sufficient preceding history;
2. an explicit per-date classification of `VALID_EXACT_BAR`, `PROVIDER_NO_BAR`, or blocker reason;
3. no assumption that every weekday must contain a bar;
4. only unique exact `16:59:00 America/New_York` Twelve Data `XAU/USD` 1-minute bars;
5. chronological replay; future target-month observations cannot alter earlier daily states;
6. enough valid prehistory before the first eligible state timestamp in the cell.

A month is not `READY_PROVEN` merely because a sparse set of exact bars exists.

### 8.7 `SLOW`

Role: tactical direction context.

Governed underlying source:

`XAU_EOD_TWELVE_NY17` only.

Frozen rule:

- daily canonical observations are transformed to completed weekly closes using `W-FRI` semantics;
- incomplete current week excluded;
- SMA4;
- two completed-week persistence;
- five completed weekly closes provide full prior/current persistence evaluation; insufficient-history states remain valid model states only when caused by genuine history length, not by missing governed data.

Historical cell readiness therefore requires complete/adjudicated canonical NY17 daily input sufficient to reproduce completed weekly closes and required prehistory. Missing daily canonical data may not be hidden by weekly aggregation.

### 8.8 `MACRO_EVENT_SUCCESSOR_V2`

Role: release-aware event-risk context; no direction vote or H=1 price forecast.

Frozen governed input panel:

- `MACRO_NFP_ACTUAL_FIRST_PRINT`
- `MACRO_NFP_CONSENSUS_PIT`
- `MACRO_UNEMP_ACTUAL_FIRST_PRINT`
- `MACRO_UNEMP_CONSENSUS_PIT`
- `MACRO_AHE_ACTUAL_FIRST_PRINT`
- `MACRO_AHE_CONSENSUS_PIT`

The frozen source retrieval identity, first-print/consensus semantics, release timestamps, minimum prior complete-case history, robust MAD/IQR scale hierarchy, signs, equal weights and thresholds must remain unchanged.

Known complete-case exclusions in the frozen V2 source contract remain explicit, including `2025-10`. Such a cell is `CONTRACTUAL_EXCLUSION`, not silently imputed and not relabelled a model failure.

For all other cells, prefix invariance and deterministic replay requirements remain binding.

### 8.9 `BOCPD_RETURN_SUCCESSOR_V1`

Role: regime/break context only.

Frozen source:

- repository artifact `gold_axis_2026/core5_monthly.csv.gz.b64`;
- field `gold_monthly`;
- transform `log(P_t/P_{t-1})`;
- completed month only.

Frozen statistical identity, hazard, prior and state rule remain unchanged.

Existing contract evidence covers only the window explicitly named in the frozen BOCPD contract. A target-month cell outside that explicit window must be reported `BLOCKED_CONTRACT` until an evaluation-only extension is separately governed **without** changing model mathematics or using the extension result to tune the model. Such an extension remains retrospective evidence and does not create prospective proof.

### 8.10 `EMERGENCY_LEVEL`

Role: intramonth emergency context.

Governed XAU source:

`XAU_EOD_TWELVE_NY17`

Frozen level rule:

- monthly reference must be positive and explicitly permitted for the target month;
- displacement = `close / monthly_reference - 1`;
- `>= +4%` => `UP`;
- `<= -4%` => `DOWN`;
- otherwise `NEUTRAL`.

Historical cell readiness requires both:

1. a valid immutable/origin-bounded monthly reference for that historical target month under the permitted Emergency reference contract; and
2. chronological exact NY17 target-month observations under the governed historical reconstruction lane.

Missing reference or missing canonical NY17 history blocks the cell; neither may be substituted after observing the outcome.

### 8.11 `EMERGENCY_REVERSAL`

Role: intramonth emergency reversal context.

Same governed source/reference prerequisites as `EMERGENCY_LEVEL`.

Frozen reversal rule remains:

- after an UP shock, track running peak; decline of at least 4% from peak => `DOWN_ALERT`;
- after a DOWN shock, track running trough; rise of at least 4% from trough => `UP_ALERT`;
- state resets at the beginning of each month.

Historical replay must process target-month observations in chronological order from the beginning of the month. A later peak/trough may not be used to rewrite an earlier state.

### 8.12 `GVZ_RISK`

Role: risk-only context; never a gold-direction predictor.

Governed source:

`GVZ_CBOE` only.

Frozen thresholds remain:

- `GVZ <= 25.9795` => cap `1.0`, panic `false`;
- `25.9795 < GVZ <= 30.5238` => cap `0.5`, panic `false`;
- `GVZ > 30.5238` => cap `0.25`, panic `true`.

Historical reconstruction requirements:

- Cboe official historical GVZ data only;
- preserve observation date and truthful retrieval provenance;
- no proxy volatility index, interpolation or forward-fill;
- chronological evaluation using released/historical Cboe observations;
- late retrieval is `HISTORICAL_REPLAY` evidence only, not proof that the project consumed GVZ prospectively at the historical date.

---

## 9. Historical NY17 reconstruction lane

This section governs the highest-priority shared blocker for:

- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`

### 9.1 Accepted source semantic

Only:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1min`;
- request timezone: `America/New_York`;
- accepted source timestamp: exact unique `16:59:00`;
- accepted value: bar `close` after positive/range-valid OHLC checks;
- Gold Control stored semantic: corresponding 17:00 ET session boundary converted to UTC.

### 9.2 Forbidden recovery shortcuts

The following are prohibited:

- 5-minute substitute;
- hourly substitute;
- daily substitute;
- alternate provider;
- nearest timestamp;
- interpolation;
- forward-fill;
- synthetic bar;
- copying an unrelated XAU cross-check into the governed source;
- backdating `retrieved_at` or `available_as_of` to the observation date;
- claiming an official CME settlement/fixing.

### 9.3 Exact-date probe classification

Every required historical date probed from Twelve Data must be classified into exactly one acquisition state:

- `VALID_EXACT_BAR`
- `PROVIDER_NO_BAR`
- `ENTITLEMENT_BLOCKED`
- `AUTHENTICATION_ERROR`
- `RATE_LIMITED`
- `INVALID_REQUEST`
- `MALFORMED_BAR`
- `SERVER_ERROR`
- `UNRESOLVED`

Only `VALID_EXACT_BAR` and an explicitly accepted `PROVIDER_NO_BAR` resolve the date for coverage accounting. All other states remain blockers until resolved.

Weekday counting by itself is not a completeness test.

### 9.4 Storage/evidence rule

Historical reconstruction must be stored in a separately identifiable reconstruction/research lane or immutable artifact with:

- source/provider/symbol/interval/timezone;
- requested historical date;
- source bar timestamp;
- normalized stored timestamp;
- OHLC values used for validation;
- accepted close;
- actual retrieval timestamp;
- acquisition status;
- lineage ID;
- request/retrieval run ID;
- SHA-256 input/source fingerprint where feasible;
- explicit evidence class `HISTORICAL_REPLAY` / historical reconstruction;
- `prospective_claim=false`;
- `canonical_forecast_authority=false`;
- no Decision Store write.

The reconstruction lane must not silently rewrite current production canonical history to imply historical prospective availability.

---

## 10. GVZ historical reconstruction lane

Historical gap completion for `GVZ_RISK` must use Cboe official GVZ historical price data.

Required controls:

- record source URL/identity and retrieval timestamp;
- preserve source observation date/value;
- detect duplicate observation dates;
- reject non-finite values;
- no alternate volatility proxy;
- no interpolation/forward-fill;
- store as historical reconstruction evidence;
- current prospective GVZ observations remain separately evidenced.

The first intended gap scope is the missing pilot history required for `2025-01..2026-02`, subject to a fresh baseline audit before acquisition.

---

## 11. Formal historical readiness auditor

Planned implementation:

`tools/audit_historical_pilot_readiness_v145.py`

The auditor becomes binding only after its implementation is reviewed against this contract and frozen in the manifest.

### 11.1 Auditor behavior

The auditor must be **read-only**.

It must not:

- fetch missing external data;
- mutate Neon;
- create forecasts;
- create decision rows;
- change engine state;
- choose a winning model;
- calculate selector/ensemble weights;
- tune any model or threshold.

### 11.2 Required outputs

At minimum the auditor must emit:

1. one row per governed engine x pilot target-month cell (`12 x 20 = 240` rows);
2. role/evaluation-clock semantic;
3. top-level readiness state;
4. all failed/passed readiness dimensions D1-D8;
5. exact blocker/reason codes;
6. required source identities;
7. observed source coverage and required prehistory;
8. source/lineage identifiers;
9. replay-evidence reference where one already exists;
10. a global per-engine summary that preserves partial-cell information.

Recommended immutable report names:

- `historical_pilot_readiness_v145.json`
- `historical_pilot_readiness_v145.csv`

The JSON report is the primary machine-readable evidence; CSV is a human review surface.

### 11.3 No hidden denominator changes

The auditor must always report all 20 pilot cells. `CONTRACTUAL_EXCLUSION` remains visible rather than being dropped silently from a denominator.

Any later role-specific validation contract must predeclare how contractual exclusions and common-cell comparisons are handled before performance results are used.

---

## 12. Baseline-before-backfill rule

Before any historical gap completion write/import:

1. run the frozen V1.45 historical readiness auditor once against the current state;
2. preserve its JSON/CSV output and Git/DB source fingerprints;
3. record the exact missing dates/cells/reason codes;
4. only then perform the minimum governed data acquisition needed to resolve those blockers;
5. rerun the same frozen auditor with no rule changes;
6. compare pre/post readiness only; do not inspect model performance to decide which missing dates to fetch.

This ensures that data completion is driven by the frozen source contract rather than by model outcomes.

---

## 13. Data-completion order after baseline audit

Subject to the frozen baseline report, the intended sequence is:

1. **Historical canonical-semantics NY17 reconstruction** — resolve required exact 16:59 ET Twelve Data dates and prehistory for Monthly Direction, FAST, SLOW and both Emergency engines.
2. **Historical GVZ reconstruction** — fill the Cboe GVZ pilot gap, initially expected to include 2025 and Jan-Feb 2026 if the baseline confirms it.
3. **Unexecuted frozen monthly replay cells** — execute/reconcile missing covered cells for Patch, RW, Momentum and VW under unchanged identities.
4. **BOCPD contract-window disposition** — if August 2026 lies outside its frozen window, do not silently extend it; create an evaluation-only change-control that freezes the same mathematics and labels the result retrospective.
5. **Re-run V1.45 readiness audit** — no performance scoring yet.
6. Proceed only then to component verification, role-specific validation and contribution testing under separately frozen evaluation rules.

---

## 14. Acceptance gate for `GOLD_PILOT_V1` readiness

`GOLD_PILOT_V1` may move from data-readiness work to component/role validation only when:

- the V1.45 auditor is frozen and read-only;
- every one of the 240 cells has an explicit status;
- no cell is silently omitted;
- every `READY_PROVEN` / `READY_TO_REPLAY` cell has the exact governed source identity;
- all historical NY17 dates required by eligible cells are resolved by governed exact-date evidence;
- all late reconstructions remain labelled historical;
- macro vintage/release semantics remain intact;
- selector/ensemble/position locks remain closed;
- authority stores remain unchanged by readiness work;
- no model or source contract was modified in response to performance results.

The project does **not** require all 240 cells to be `READY_PROVEN` before proceeding. It requires all unresolved cells to be explicit and role-specific validation to use only cells permitted by its subsequently frozen evaluation contract. Global architecture decisions are deferred until the full validation/contribution phase.

---

## 15. Stop conditions

Readiness/backfill work stops and reports `BLOCKED` rather than improvising if:

- Twelve Data entitlement does not permit a required exact historical NY17 bar;
- the exact 16:59 bar is absent and provider evidence cannot resolve the date;
- a required macro vintage/consensus timing rule cannot be proved;
- a governed source identity conflicts with available data;
- a requested historical cell requires changing model mathematics/thresholds/features to run;
- a source would need interpolation, forward-fill or provider substitution;
- historical evidence would need to be falsely relabelled prospective;
- production forecast/decision authority would need to be written merely to complete the pilot.

Correct statuses include `BLOCKED_DATA`, `BLOCKED_PIT`, `BLOCKED_CONTRACT`, `IMPLEMENTATION_FAIL` and `NOT_PROVEN`; no hallucinated completion is permitted.

---

## 16. Explicit non-goals

This readiness contract does **not**:

- choose the best model;
- eliminate an engine based on forecast error;
- optimize model parameters;
- define final role-specific performance metrics;
- define a forecast ensemble;
- define an expert selector;
- define position sizing;
- create trading actions;
- prove prospective performance;
- authorize production forecast/decision writes.

Those questions occur only after readiness is established and separately frozen validation/contribution rules are issued.

---

## 17. Frozen next step

After this contract is committed:

1. implement `tools/audit_historical_pilot_readiness_v145.py` exactly against this contract;
2. run and preserve the baseline `12 x 20` readiness matrix;
3. only after that baseline, complete missing historical data under Sections 9-13;
4. rerun the unchanged audit;
5. proceed to component verification and role-specific validation.

This sequence is binding for V1.45 historical-pilot readiness work.
