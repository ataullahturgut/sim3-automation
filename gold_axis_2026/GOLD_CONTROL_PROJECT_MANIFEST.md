# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.40  
**Freeze / issue date:** 2026-09-06  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical model/app branch:** `gold-r4-direction-engine`  
**Scheduler branch:** `main`  
**Project root:** `gold_axis_2026/`

---

# 0. SOLE PROJECT-MANIFEST AUTHORITY

This file is the **only canonical Gold Control project manifest**.

Binding identity:

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`

Rules:

1. No other Markdown, YAML, JSON, workflow, status note, change-control document, replay report, handover, or historical manifest version is a second project manifest.
2. Historical change-control, validation, status and evidence documents remain immutable audit evidence only.
3. If older evidence conflicts with this file, this v1.40 manifest governs current product/runtime behavior.
4. Git history remains the historical record; current runtime/model inventory must contain only identities currently governed by this manifest.
5. `FILE_MANIFEST_SHA256.txt` is a repository checksum inventory, not a project decision manifest.
6. Before changing model roles, target/horizon, origin timing, source mappings, thresholds, UI semantics, runtime authority, selector/ensemble behavior or production writes, read this file first.

---

# 1. PRODUCT DEFINITION

Gold Control is a mobile-first, auditable gold decision-support system.

It must:

- monitor current and historical market data;
- produce H=1 monthly-average XAU/USD forecasts;
- maintain monthly direction context;
- maintain tactical Fast/Slow context;
- detect intramonth Emergency conditions;
- detect regime/break context;
- apply volatility/risk context;
- expose every current governed motor as ACTIVE / WAITING / BLOCKED or equivalent observable state;
- preserve exact evidence provenance and point-in-time availability;
- keep forecast/direction evidence separate from any later decision/action mapping.

It is **not** an autonomous trading system.

Canonical top-level UI:

`Piyasa | Görünüm | Tahmin | Geçmiş`

---

# 2. SOURCE-OF-TRUTH HIERARCHY

## 2.1 GitHub

GitHub is authoritative for code, frozen model/signal contracts, source contracts, this manifest, reproducibility and audit evidence.

## 2.2 Production Neon

Production Neon is authoritative for mutable/current data state: observations and provider lineage, retrieval/vintage/PIT availability, derived feature snapshots, engine runtime state, forecast contracts when legitimately issued, and decision snapshots/events when legitimately issued.

## 2.3 Application

The application is a read/presentation layer. It must not silently tune thresholds, choose models, create an ensemble, substitute providers, manufacture missing outputs, convert reconstruction into backdated prospective issuance, or create BUY / SELL / HOLD / EXIT / REDUCE mappings.

---

# 3. NON-NEGOTIABLE GOVERNANCE LOCKS

The following remain frozen:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no automatic BUY / SELL / HOLD / EXIT / REDUCE output
- no hindsight threshold tuning
- no random-split model validation for time series
- no silent provider substitution
- historical reconstruction, backtest and genuinely prospective evidence remain distinguishable
- replay/reconstruction never changes true historical timestamps or source vintages
- target, model identity, source identity and scoring measurement cannot be silently redefined
- production forecast/decision authority writes require explicit manifest authorization

---

# 4. CANONICAL MONTHLY ORIGIN CYCLE

For target calendar month **M**, the H=1 forecast origin is the completed month-end boundary immediately before M.

`origin(M) = completed month-end boundary of M-1`

`target(origin) = immediately following calendar month`

Examples:

| Information/origin boundary | Target month |
|---|---|
| 2026-08-31 | September 2026 |
| 2026-09-30 | October 2026 |
| 2026-10-31 | November 2026 |
| 2026-11-30 | December 2026 |

At each valid origin the month-open snapshot is immutable. Intramonth updates may create later state, but they never rewrite that origin snapshot.

---

# 5. SEPTEMBER 2026 — CURRENT ORIGIN REFERENCES

Required information boundary:

`2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET.

Current reconstructed September references:

| Motor / context | September 2026 result | Evidence semantics |
|---|---:|---|
| `MONTHLY_DIRECTION_3M` | `DOWN` | reconstruction |
| `FAST` | `ROBUST_UP` | reconstruction |
| `SLOW` | `ROBUST_UP` | reconstruction |
| `MOMENTUM_3M` H=1 | `4345.814584037808 USD/oz` | historical replay |
| `RANDOM_WALK` H=1 | `4397.305673870967 USD/oz` | historical replay |
| `CAUSAL_PATCH` H=1 reference | `4452.046728838838 USD/oz` | historical replay |
| `VW_MIDAS_MSVR_SUCCESSOR_V1` H=1 | `4565.115907930242 USD/oz` | origin reconstruction / historical replay |
| `EMERGENCY_LEVEL` | `NEUTRAL` | reconstruction |
| `EMERGENCY_REVERSAL` | `OFF` | reconstruction |
| `BOCPD_RETURN_SUCCESSOR_V1` | `NO_ADVERSE_BREAK_CANDIDATE` | historical replay context |
| `MACRO_EVENT_SUCCESSOR_V2` | `MACRO_MIXED_OR_SMALL` | historical replay context |

The `VW_MIDAS_MSVR_SUCCESSOR_V1` September value was calculated on 2026-09-06 from the completed 31-Aug information boundary. It is **not** evidence that a forecast was actually issued on 31-Aug and must not be backdated.

Required UI provenance wording is equivalent to:

`EYLÜL 2026 · 31 AĞUSTOS ORIGIN`

and

`31 Ağustos bilgi setiyle 6 Eylül'de yeniden hesaplandı · HISTORICAL_REPLAY`

No September expert values may be averaged or winner-selected without a separately proven selector contract.

---

# 6. H=1 FORECAST EXPERT INVENTORY — v1.40

Current governed H=1 expert identities are:

- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`

`VW_MIDAS_MSVR_SUCCESSOR_V1` is the sole governed VW/MSVR identity in the current model/runtime/application inventory.

Its current maximum authority is:

`RESEARCH_SHADOW_CANDIDATE_HISTORICAL_REPLAY_PASS_PROSPECTIVE_VALIDATION_REQUIRED`

Operational current-month runtime state:

`ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE`

This ACTIVE state means the frozen V1 model has been executed for the September 2026 H=1 reference using only the completed 31-Aug information boundary. It is not a backdated prospective issuance. The 30-Sep -> October gate remains a later prospective validation milestone, not a blocker for the September reference.

It has:

- no selector authority;
- no ensemble authority;
- no automatic action authority;
- no production forecast-contract authority;
- no decision-store authority;
- no position mapping.

Historical repository evidence may retain superseded names as immutable audit history, but superseded identities are not part of the current manifest, current runtime registry, current application registry or executable production path.

---

# 7. VW_MIDAS_MSVR_SUCCESSOR_V1 — FROZEN MODEL CONTRACT

## 7.1 Target and horizon

- target: next calendar month's average XAU/USD price;
- horizon: H=1 month;
- origin: completed prior calendar month-end;
- random split forbidden;
- future target information forbidden.

## 7.2 Four-metal input surface

Historical replay uses four metals:

- Gold
- Silver
- Platinum
- Palladium

Two features are produced per metal:

1. prior monthly log return;
2. GPR-adaptive weighted within-origin-month daily log return.

Frozen input dimension = `8`.

For metal `m`, target month `t`, origin month `p=t-1`, previous month `pp=t-2`:

`MR_m(p) = log(M_m(p) / M_m(pp))`

GPR uses `GPR_OFFICIAL_GIT_PIT` with origin vintage `p` and publication-lagged observation `p-1`.

`lambda = 0.1 * exp(-10 * z_GPR)`

Daily-return age weights:

`w_i = exp(-lambda * age_i) / sum(exp(-lambda * age))`

Weighted within-month return:

`VW_m(p) = sum(w_i * r_i)`

Frozen feature vector:

`X_t = [MR_Gold,VW_Gold, MR_Silver,VW_Silver, MR_Platinum,VW_Platinum, MR_Palladium,VW_Palladium]`

The model jointly predicts next-month log returns for all four metals.

## 7.3 MSVR architecture

- true multi-output MSVR;
- one joint four-output model;
- RBF kernel;
- deterministic implementation;
- X and Y standardization fitted only on training rows for each fit.

Frozen hyperparameter grid:

- `C in {0.1, 1.0, 10.0}`
- `epsilon in {0.02, 0.05}`
- `gamma_scale in {0.5, 1.0}`
- actual `gamma = gamma_scale / 8`

## 7.4 Nested rolling-origin selection

For each outer target:

- candidate hyperparameters are scored only on earlier target months;
- origin-local GPR PIT availability is required;
- at least 6 eligible prior inner forecasts are required;
- selection objective is mean absolute Gold log-return error;
- deterministic tie-break is lower C, then lower epsilon, then lower gamma_scale;
- after selection, refit on all eligible training targets before the outer target;
- no post-result retuning.

## 7.5 Historical replay evidence

Evaluation window: `2023-01..2026-07`, N=`43`.

Frozen results:

| Metric | Successor V1 | Random Walk |
|---|---:|---:|
| MAE | `87.70325` | `107.46512` |
| MAPE | `2.69106498%` | `3.30232202%` |
| Relative MAE | `0.816109` | `1.000000` |
| Median AE | `50.49628` | `72.00000` |

The 2026 Jan-Jul partial period was slightly worse than Random Walk and remains disclosed. Historical PASS is not production superiority.

---

# 8. FIRST GENUINELY PROSPECTIVE VW/MSVR SHADOW TEST

First preregistered genuine prospective origin:

`2026-09-30T21:00:00Z`

Target month:

`2026-10`

Prospective-validation readiness state on 2026-09-06:

`WAITING_ORIGIN_NOT_REACHED`

Secondary readiness conditions:

- `WAITING_FOUR_METAL_SOURCE_DATA`
- `WAITING_GPR_2026_09_ORIGIN_VINTAGE`

Before issuance, the frozen prospective source-refresh and XAU target-anchor contracts must pass. No October actual or partial October target information may enter training, selection, scaling, features or issuance.

Maximum valid state after a successful origin-time issue:

`PROSPECTIVE_SHADOW_FORECAST_ISSUED_AWAITING_TARGET_MATURITY`

A single prospective month is evidence, not proof of production superiority.

---

# 9. SOURCE / MEASUREMENT RULES FOR THE VW/MSVR SUCCESSOR

Historical Broad Research Data Spine R1 remains frozen evidence.

Historical four-metal R1 identities:

- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`

These are historical-reconstruction research series and are not silently relabelled as live market PIT data.

The August 2026 Myfxbook four-metal snapshot was used only under the separately frozen reconstruction bridge for the 31-Aug → September reconstruction. It does not automatically become the prospective provider contract.

Primary GPR input remains:

`GPR_OFFICIAL_GIT_PIT`

No current/final GPR substitution is permitted for historical or prospective origin logic.

The price-level anchor and later actual used for prospective scoring must follow the separately frozen target-measurement bridge. Changing a measurement source without disclosure is forbidden.

---

# 10. DIRECTION / RISK / REGIME MOTORS

Current direction/context motors:

- `MONTHLY_DIRECTION_3M` — strategic monthly direction; direction vote permitted.
- `FAST` — tactical short-horizon direction; direction vote permitted.
- `SLOW` — tactical slower direction; direction vote permitted.
- `GVZ_RISK` — risk-only; no direction vote.
- `EMERGENCY_LEVEL` — intramonth alert/context; no automatic action.
- `EMERGENCY_REVERSAL` — intramonth alert/context; no automatic action.
- `BOCPD_RETURN_SUCCESSOR_V1` — active regime/break context; no direction vote.
- `MACRO_EVENT_SUCCESSOR_V2` — active labor-event risk/context; no direction vote and no H=1 price forecast.

No context motor creates an automatic position/action mapping.

---

# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.40 TARGET STATE

After the v1.38 runtime canonicalization migration, the current governed 12-motor application inventory must be exactly:

- `ACTIVE = 12`
- `WAITING = 0`
- `BLOCKED = 0`
- direction-vote permitted = `3`
- total current governed motors = `12`

ACTIVE:

- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `GVZ_RISK`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `MACRO_EVENT_SUCCESSOR_V2`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`

WAITING:

- none in the current governed 12-motor inventory.

`VW_MIDAS_MSVR_SUCCESSOR_V1` runtime status is `ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE`; its September value remains explicitly historical-replay/origin-reconstruction evidence and is not a backdated prospective issue. The 30-Sep → October prospective test remains a separate later validation gate.

No superseded VW identity may exist in the current application registry or current production runtime rows after this migration.

---

# 12. v1.40 AUG31 -> SEPTEMBER CURRENT-REFERENCE ACTIVATION AUTHORIZATION

Binding authorization token:

`MANIFEST_V1_40_ALL_AUG31_SEPTEMBER_REFERENCE_ACTIVATION`

The user-directed current-month objective is to run and expose every already-proven 31-Aug -> September motor now. 30 September is not a blocker for these September references.

Authorized append-only current runtime changes:

- `CAUSAL_PATCH` -> ACTIVE historical-replay current-month reference `4452.046728838838 USD/oz`;
- `MOMENTUM_3M` -> ACTIVE historical-replay current-month reference `4345.814584037808 USD/oz`;
- `RANDOM_WALK` -> ACTIVE historical-replay current-month reference `4397.305673870967 USD/oz`;
- `EMERGENCY_LEVEL` -> ACTIVE historical-replay month-open state `NEUTRAL`;
- `EMERGENCY_REVERSAL` -> ACTIVE historical-replay month-open state `OFF`.

The already-active `VW_MIDAS_MSVR_SUCCESSOR_V1` September reference remains `4565.115907930242 USD/oz`.

For all six reconstructed/replayed September reference surfaces:

- information/origin boundary remains `2026-08-31T21:00:00Z`;
- actual reconstruction/replay execution timestamps are preserved;
- evidence remains `HISTORICAL_REPLAY` / origin reconstruction as applicable;
- `prospective_claim = false`;
- `canonical_authority = false`;
- `direction_vote_permitted = false` for these expert/reference outputs;
- `AUTO_SELECTOR = OFF`;
- `AUTO_ENSEMBLE = OFF`;
- no forecast-contract or Decision Store write is authorized.

Required post-write assertions:

- current governed runtime = `ACTIVE 12 / WAITING 0 / BLOCKED 0`;
- all four forecast/decision authority stores remain zero;
- no historical timestamp is rewritten;
- archived/superseded identities remain audit history and are not reactivated.

---

# 13. CURRENT PRODUCTION AUTHORITY STORES

The required invariant remains:

- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`

Source-data ingestion, historical reconstruction, runtime observability, and successor registration do not grant forecast/decision authority.

---

# 14. UI CONTRACT — v1.40

## 14.1 Tahmin

During September 2026 the forecast surface may show the four separate governed H=1 references:

- Momentum 3M
- Random Walk
- Causal Patch
- VW/MSVR Successor V1

The V1 September value must display historical-reconstruction provenance. No synthetic average/winner may be invented.

## 14.2 Görünüm

Every current governed motor remains visible. The VW/MSVR card must use only `VW_MIDAS_MSVR_SUCCESSOR_V1` and show both:

1. September / 31-Aug origin reconstructed reference = `4565.115907930242 USD/oz`;
2. current operational state = `ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE`; the 30-Sep → October prospective test is shown separately as a later validation milestone.

The current application UI must not render a superseded VW runtime/model card.

## 14.3 Geçmiş

Historical/audit surfaces preserve true calculation/persistence timestamps and evidence class. Git history and immutable historical evidence may retain prior identities for audit traceability; they are not current model inventory.

---

# 15. CORE DATA CONTRACT

1. No silent provider substitution.
2. Provider identity is part of series identity.
3. Point-in-time availability is mandatory.
4. Historical/reconstructed code uses origin-bounded observations/snapshots.
5. Retrieval-time backfills do not become retroactively knowable.
6. Live/indicative XAU is not canonical EOD authority.
7. Current-day bars cannot be assumed completed before the frozen session boundary.
8. Raw vendor/licensed data respects display/redistribution rights.
9. Missing inputs fail closed; they are not filled with invented same-name proxies.

Canonical R4 decision-reference series remains:

`XAU_EOD_TWELVE_NY17`

Operational mapping:

- Twelve Data `XAU/USD`
- interval `1min`
- timezone `America/New_York`
- exact bar open `16:59:00` ET
- bar close used as 17:00 ET internal decision reference

This is an internal decision reference, not official settlement/official close.

---

# 16. GPR PIT DATA PLANE

Binding identity:

`GPR_OFFICIAL_GIT_PIT`

Authority/source:

- Caldara-Iacoviello official repository;
- exact monthly archive vintage;
- evidence class `HISTORICAL_REPLAY_RECONSTRUCTION`.

Continuous PIT-proven origin window currently established:

`2022-03` through `2026-08` = 54 origins.

For each origin, the exact vintage must be available by the origin cutoff and contain the required lag observation. Current/final-vintage substitution is forbidden.

Source-data writes remain restricted to the source/audit plane and do not authorize forecast/decision writes.

---

# 17. BROAD RESEARCH DATA SPINE R1

Broad Research Data Spine R1 remains canonical research source-data evidence:

- exact research series = `12`;
- observations = `71,075`;
- source-vintage rows under the frozen ingestion evidence = `126`;
- quality events = `0` under the frozen ingestion evidence.

Evidence semantics remain frozen:

- CORE5 is not historical PIT;
- StakTrakr R1 makes no origin-PIT claim;
- Twelve-derived hourly research XAU is not canonical `XAU_EOD_TWELVE_NY17`;
- GPRT/GPRA are separate official-Git reconstruction identities;
- retrieval/first-seen timestamps are never backdated;
- silent provider substitution is forbidden.

---

# 18. CURRENT EVIDENCE FOR VW_MIDAS_MSVR_SUCCESSOR_V1

Current supporting evidence includes:

- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-06.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_ENGINEERING_EVIDENCE_2026-09-06.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_AUG31_SEPTEMBER_RECONSTRUCTION_CONTRACT.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_AUG31_SEPTEMBER_RECONSTRUCTION_EVIDENCE_2026-09-06.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_PROSPECTIVE_SHADOW_CONTRACT_2026-09-06.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_PROSPECTIVE_READINESS_EVIDENCE_2026-09-06.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_FOUR_METAL_PROSPECTIVE_SOURCE_REFRESH_CONTRACT.md`
- `GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_XAU_TARGET_ANCHOR_BRIDGE_CONTRACT.md`
- `gold_axis_2026/tools/vw_midas_msvr_successor_v1.py`
- `gold_axis_2026/tools/vw_midas_msvr_successor_v1_aug31_september_reconstruction.py`
- `gold_axis_2026/tools/vw_midas_msvr_successor_v1_prospective_readiness.py`

These are supporting evidence/contracts; this manifest remains the only current project manifest.

---

# 19. NEXT LEGITIMATE STOP POINT

The 31-Aug -> September current-month reconstruction/replay layer is now the immediate operational target; it does not wait for 30 September.

After v1.40 activation, the current governed 12-motor inventory must have no WAITING or BLOCKED current identity. Historical blocked rows for superseded identities remain immutable audit evidence and must not be revived.

The next engineering step is therefore consistency verification across production Neon, runtime bootstrap, application observability and the production display snapshot. Only after that current-month reconciliation is complete does the separate later VW/MSVR prospective validation milestone remain:

`2026-09-30 origin -> 2026-10 target`

That later prospective test does not invalidate or postpone the September historical-replay current-month references.

---

# 20. FINAL BINDING SUMMARY

Current VW/MSVR model identity:

`VW_MIDAS_MSVR_SUCCESSOR_V1`

Current model status:

`HISTORICAL_REPLAY_PASS / RESEARCH_SHADOW / PROSPECTIVE_VALIDATION_REQUIRED`

September reconstructed H=1 reference:

`4565.115907930242 USD/oz`

Current-month runtime state:

`ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE`

First genuine prospective test:

`30 Sep 2026 -> October 2026`

Target v1.40 runtime inventory after Aug31-to-September current-reference activation:

`ACTIVE 12 / WAITING 0 / BLOCKED 0 / TOTAL 12`

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, and `NOT_PROVEN_POSITION_MAPPING` remain binding.
