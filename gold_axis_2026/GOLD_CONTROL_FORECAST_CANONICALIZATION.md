# GOLD CONTROL — H=1 FORECAST CANONICALIZATION

**Canonicalization version:** 1.3  
**Audit date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.0  
**Production closure package:** `GOLD_H1_R1_STAGE9B_11_PRODUCTION_CLOSURE_V1.zip`  
**Package SHA256:** `943d9b79e19deb4ff56e9e51bba0d5c9ee50725c7a40f51b19187825497c5a0c`  
**Stage 2 status:** `PASS_CONTRACT_CANONICALIZED; PROSPECTIVE_LEDGER_PROVEN_EMPTY`

---

## 0. PURPOSE

This document prevents forecast-version drift inside Gold Control.

It defines which H=1 artifact is authoritative for the current production-closure release, which models are executable/reference/benchmark/challenger, which historical files are legacy experimental outputs, which metrics belong to which exact release, and what the current Neon forecast-state store actually contains.

No value from a legacy file may be silently substituted for a production-closure value because the model names look similar.

---

# 1. CANONICAL H=1 CONTRACT

Target:

> **Next calendar month's average XAU/USD price**

Forecast origin:

> **End of the previous completed calendar month**

Frozen validation requirements:

- random split forbidden;
- future target information forbidden;
- tuning only on past rolling/expanding origins;
- publication lag mandatory;
- vintage / point-in-time safety mandatory;
- comparison against same-horizon benchmark mandatory.

Canonical audited evaluation window for the current production-closure scorecard:

`2023-01 → 2026-07`, `N=43`.

---

# 2. AUTHORITY ORDER FOR FORECAST ARTIFACTS

For H=1 production-closure values, use this authority order:

1. `gold_axis_2026/production_closure/PROVENANCE.json`
2. `gold_axis_2026/production_closure/common_scorecard.csv`
3. `gold_axis_2026/production_closure/production_history_43.csv`
4. `gold_axis_2026/production_closure/production_2026.csv`

Older root-level SIM3 experiment outputs are retained for historical research lineage but are **not production-closure substitutes**.

The production `PROVENANCE.json` explicitly states:

> Do not substitute legacy SIM3 experimental output files for production-closure values.

This is binding.

---

# 3. CANONICAL MODEL ROLE REGISTRY

| Canonical ID | Exact model / artifact role | Production role | Executability / provenance status | UI treatment |
|---|---|---|---|---|
| `VW_AUDITED_SHADOW_V2` | VW-MIDAS-SVR Adapt V2 | audited analytical shadow/reference | audited outputs exist; exact original executable reproduction `BLOCKED_NOT_PROVEN` | show as `Audited reference`, never imply fully reproducible execution |
| `PATCH_R1_EXECUTABLE` | Causal PatchTST Gold R1 | temporary executable H=1 point-forecast path | reproducible executable path in production closure | show as production/executable point forecast only where an immutable issued record exists |
| `REPRO_SVR_DIAGNOSTIC` | reproducible SVR reconstruction | diagnostic/reconstruction only | executable diagnostic; does not replace audited VW identity | technical/audit only by default |
| `MOMENTUM_3M_R1` | 3M Momentum | direction challenger/context and price challenger in scorecard | reproducible | direction context; not primary point forecast |
| `RW_R1` | Random Walk | mandatory naive benchmark | reproducible | benchmark |

Frozen switches:

- `AUTO_SELECTOR = OFF / REJECT_NOT_PROVEN`
- `AUTO_ENSEMBLE_PRIMARY = OFF / REJECT_FOR_PRIMARY`
- model disagreement may be displayed where useful.

---

# 4. CURRENT PRODUCTION-CLOSURE SCORECARD

These metrics belong specifically to the current production-closure release and common `N=43` window.

| Model ID | MAPE % | Median APE % | Worst APE % | MAE | RMSE | Wins |
|---|---:|---:|---:|---:|---:|---:|
| `VW_AUDITED_SHADOW_V2` | 2.6721495778 | 1.9629403593 | 8.8312361922 | 85.1347018619 | 125.1886307262 | 8 |
| `PATCH_R1_EXECUTABLE` | 3.0746698377 | 2.7624009318 | 9.9189382145 | 101.6591968894 | 146.0409634213 | 7 |
| `REPRO_SVR_DIAGNOSTIC` | 3.1300701099 | 2.6989727207 | 9.6452919299 | 100.7790103609 | 144.1756891083 | 7 |
| `MOMENTUM_3M_R1` | 3.2972968756 | 2.7739525829 | 10.7354441932 | 103.9768974645 | 147.9107047674 | 14 |
| `RW_R1` | 3.3023220233 | 2.9149797571 | 9.6258805962 | 107.4651162791 | 153.0688774740 | 7 |

Do not combine these metrics with older archived Patch/VW outputs under the same unlabeled model name.

---

# 5. LEGACY ROOT-LEVEL OUTPUTS — VERSION SEPARATION

`gold_axis_2026/monthly_predictions_2023_2026.csv` contains older SIM3 experiment outputs whose VW and Causal Patch forecast values differ from the production-closure history.

Examples exist across the same calendar months. Therefore the root file is classified as:

`LEGACY_EXPERIMENTAL_OUTPUT — DO_NOT_USE_AS_PRODUCTION_CLOSURE`

This is not interpreted as corruption. It is a **different historical experiment/model-output lineage**.

Rules:

1. Never relabel root-level `causal_patch_transformer` as `PATCH_R1_EXECUTABLE` without an explicit bridge proving identity.
2. Never relabel root-level `vw_midas_msvr` as the production-closure VW output merely because the names are similar.
3. Historical research reports may cite those old values only with their original lineage/version context.
4. Current app/forecast ledger must use production-closure values or a later explicitly versioned successor.

Status of exact mapping between all old root outputs and later production-closure implementations:

`UNRESOLVED_VERSION_MAPPING`.

No mapping is guessed.

---

# 6. AUGUST 2026 OPERATIONAL FORECAST — CANONICAL VALUE

The production-closure provenance records:

- origin date: `2026-07-31`
- origin price: `4073.0`
- target context: August 2026 H=1 monthly-average forecast
- temporary executable point model: `Causal PatchTST Gold R1`
- production-closure Patch operational forecast: **4115.6394040298055 USD/oz**

Therefore, if Gold Control needs the August 2026 production-closure Patch value for research/provenance display, the canonical production-closure value is:

`4115.6394040298055`

Older experimental/archived August forecast values must not overwrite or replace it.

### Evidence classification warning

The presence of this operational forecast in the closure package proves the artifact and its stated origin. The live Neon reconciliation now proves that no immutable forecast input/contract rows were persisted in the current forecast-state tables for this release.

Therefore its evidence label for prospective reporting remains:

`OPERATIONAL_CLOSURE_ARTIFACT; PROSPECTIVE_ISSUANCE_TIMESTAMP_NOT_PROVEN`

It must not be silently labeled `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` evidence. The empty ledger is evidence of absence from the current canonical database store, not evidence that the historical closure artifact was never created.

---

# 7. IMPORTANT ROLE SEPARATION — FORECAST SCREEN VS R4.1 DECISION REFERENCE

Two valid but different roles currently coexist and must not be conflated.

## 7.1 H=1 user-facing executable forecast

For the H=1 forecast product path:

- executable point path = `PATCH_R1_EXECUTABLE`
- audited shadow/reference = `VW_AUDITED_SHADOW_V2`
- benchmark = `RW_R1`
- direction challenger/context = `MOMENTUM_3M_R1`.

## 7.2 R4.1 decision-engine monthly price reference

The frozen `r4_1/config/frozen_r4_1.json` separately sets:

- `core.price_model = VW-MIDAS-SVR Adapt V2`
- `core.direction_model = 3M Momentum`
- monthly refit inside target month = `false`.

R4.1 provenance also describes the R4.1 addition as:

`VW analytical primary + 3M monthly direction prior`.

Therefore:

> **The Patch executable forecast shown in the H=1 forecast product and the frozen VW monthly price reference used by the R4.1 decision architecture are not the same role.**

This is a scope distinction, not a license to interchange them.

Until a future audited architecture change explicitly unifies these roles:

- `Tahmin` screen may use a canonical issued Patch point forecast only after an immutable issued record exists, and may show VW as audited reference;
- R4.1 Emergency/decision calculations must use the exact frozen reference specified by the R4.1 config;
- no app layer may choose between them dynamically.

---

# 8. 2026 REPLAY / SCORECARD BOUNDARY

The current production-closure `production_2026.csv` contains completed monthly actuals and model forecasts for `2026-01` through `2026-07`.

Those rows are part of the common historical evaluation set.

They are not evidence that later 2026 thresholds or models may be tuned against those outcomes outside the frozen research protocol.

R4.1 separately forbids threshold tuning on 2026 outcomes.

---

# 9. WHAT THE TAHMİN SCREEN IS ALLOWED TO SHOW

Once an immutable issued forecast record exists for the target month, the `Tahmin` screen may show:

1. target month;
2. canonical executable H=1 point forecast;
3. forecast origin;
4. issued-at / snapshot timestamp;
5. current spot comparison, explicitly separated from the monthly target definition;
6. VW audited shadow/reference;
7. RW benchmark;
8. 3M direction context;
9. exact model version and provenance status;
10. historical issued-forecast vs actual chart.

Until such a row exists, the primary production forecast area must be `NOT_ISSUED_IN_CANONICAL_LEDGER`; it may separately display research/closure artifacts with their evidence label.

The screen must **not** show:

- a forecast copied from a legacy experimental file when production closure has a different value;
- an uncertainty band without a calibrated interval model;
- `Güven: Orta` or arbitrary confidence percentages;
- a model metric without exact version/window labeling;
- a retrospective forecast as if it were a genuinely prospective issued forecast.

---

# 10. LIVE NEON FORECAST-STATE RECONCILIATION

A protected GitHub Actions read-only audit queried the actual Neon schema/state and rolled the transaction back. The current forecast-state objects are:

| Object | Exists | Current rows | Audit interpretation |
|---|---:|---:|---|
| `forecast_input_snapshots` | yes | **0** | immutable input snapshot surface exists but contains no issued forecast inputs |
| `derived_feature_snapshots` | yes | **0** | feature snapshot surface exists but is empty |
| `monthly_forecast_contracts` | yes | **0** | canonical monthly forecast contract table exists but contains no issued forecasts |

This replaces the previous `ISSUANCE_LEDGER_NOT_PROVEN_CURRENT_DB` status.

Current exact status:

`PROSPECTIVE_FORECAST_LEDGER_PROVEN_EMPTY`

Consequences:

1. No existing forecast in the current Neon store can be classified as `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`.
2. Historical/closure forecasts remain file-backed research or operational-closure evidence with their original labels; they must not be backfilled and relabeled as if they had been stored prospectively.
3. The first future production/shadow forecast must write its immutable input snapshot and forecast contract **before outcome realization**.
4. Later source revisions must not rewrite that forecast snapshot.
5. Database schema presence is not equivalent to prospective evidence; row existence with timestamp/provenance is required.

The direct Neon connector wrapper remains unreliable for some management calls (`BLOCKED_CONNECTOR_SCHEMA_MISMATCH`), but this no longer blocks read-only reconciliation because the protected GitHub Actions audit provides a verified read path to the actual database.

---

# 11. STAGE 2 CLOSURE DECISION

**Decision:** `PASS_CONTRACT_CANONICALIZED; PROSPECTIVE_LEDGER_PROVEN_EMPTY`

Stage 2 exit criterion is satisfied at the contract/canonicalization level:

- H=1 target/origin contract frozen;
- production artifact authority order frozen;
- executable/reference/diagnostic/challenger/benchmark roles unambiguous;
- exact current production-closure `N=43` metrics bound to model IDs;
- legacy root output lineage separated from production closure;
- August 2026 closure value canonicalized without claiming unproven prospective issuance;
- forecast-product role separated from R4.1 monthly decision-reference role;
- auto selector/ensemble remain off;
- current Neon forecast ledger directly reconciled and proven empty rather than left unknown.

`STAGE_2 = PASS` does **not** mean prospective forecast operation has already started. It means the canonical forecast contract and role registry are resolved, and the database starting state is known.

Prospective issuance remains a later operational milestone under Stage 11. The system must accumulate new immutable forecasts from this point forward; it may not manufacture prospective history retrospectively.

---

# 12. NEXT ROADMAP CONSEQUENCE

The next structural stage is:

`STAGE 3 — DECISION STATE STORE`

Current Stage 3 preparation already includes:

- exact descriptive state vocabulary;
- explicit `NOT_PROVEN_POSITION_MAPPING` guard;
- run/snapshot/event persistence contract;
- a versioned DDL candidate;
- a rollback-only compatibility smoke against the actual Neon database.

The rollback-only smoke does not persist schema changes and is not a substitute for an isolated-branch migration test. Actual production migration remains blocked until the Stage 3 migration gate is satisfied.


---

# 12. 2026-09-01 CURRENT-ISSUER AUDIT — MANIFEST V1.8

The historical production-closure role registry remains unchanged, but executability must be separated from **current issuance readiness**.

## Patch R1

The retained executable artifacts prove the historical/closure Patch path through the August 2026 target. The live code audit found `core5_monthly` ending at `2026-07-01`, an August target constant in `run_august_2026.py`, and July cutoffs in retained model code. No audited September-2026 issuer contract was found.

Status: `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`.

This does not revoke the historical `PATCH_R1_EXECUTABLE` role inside the production-closure package; it prohibits silently date-extending that role into a new prospective target.

## VW-MIDAS-SVR Adapt V2

Canonical reachable-history forensic run `33513175499` found rebuild/research scripts but did not recover the exact original immutable production runner/source preprocessing chain. `r4_1/KNOWN_BLOCKERS.md` and `PROVENANCE.json` already classify exact reproduction as blocked.

Status: `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`.

R4.1 nevertheless requires a numeric `monthly_vw_forecast` input. Therefore Stage 4 cannot silently substitute Patch, RW, a rebuild, or live spot into that field. Recovery of exact identity or an explicit separately validated architecture change is required.

## Forecast ledger

Read-only Neon audit run `33512445624`, job `99871192709`, confirmed `forecast_input_snapshots`, `derived_feature_snapshots`, and `monthly_forecast_contracts` all exist and all remain empty. No row may be created merely to satisfy a readiness count without a valid executable issuance path.

---

# 13. PROSPECTIVE ORIGIN CUT-OFF — 2026-09-01

The canonical H=1 contract defines the forecast origin as the **end of the previous completed calendar month**.

The Neon forecast-state reconciliation proves that the immutable forecast ledger remained empty after the `2026-08-31` origin had passed. Accordingly, a September 2026 forecast first computed or persisted on `2026-09-01` cannot be backdated or labelled as a contract-compliant prospective forecast from 31 August.

Status:

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED`

Consequences:

1. No reconstructed September forecast may be labelled `PROSPECTIVE_SHADOW` with a 31-August origin.
2. Any September initialization produced after this audit must use its true issuance/retrieval timestamp and an explicit late-bootstrap/shadow label.
3. Such a bootstrap does not satisfy the canonical H=1 prospective issuance requirement.
4. The first target still eligible for a fully contract-compliant prospective H=1 issuance is **October 2026**, with origin at the end of `2026-09-30`, assuming the executable model path, point-in-time inputs, immutable snapshot, and forecast contract are all ready by that origin.
5. This temporal boundary does not authorize a model substitution or relaxation of VW/Patch provenance blockers.

