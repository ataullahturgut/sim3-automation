# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.32  
**Freeze / issue date:** 2026-09-04  
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
2. Historical change-control, validation, status and evidence documents remain audit evidence only.
3. If an older document conflicts with this file, this v1.32 manifest governs unless a newer audited manifest version explicitly supersedes it.
4. `FILE_MANIFEST_SHA256.txt` is a repository file-checksum inventory, **not** the Gold Control project decision manifest.
5. Old `apply_manifest_*` / `reconcile_manifest_*` scripts and workflow names are historical tooling, not independent manifest authority.
6. Git history may contain older manifest versions, but the current branch may contain only this single canonical project-manifest file.

Before changing model roles, target/horizon, origin timing, source mappings, thresholds, UI semantics, runtime authority, selector/ensemble behavior or production writes, read this file first.

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
- expose every governed motor as ACTIVE / WAITING / BLOCKED or equivalent observable state;
- preserve exact evidence provenance and point-in-time availability;
- keep forecast/direction evidence separate from any later decision/action mapping.

It is **not** an autonomous trading system.

Canonical top-level UI:

`Piyasa | Görünüm | Tahmin | Geçmiş`

---

# 2. SOURCE-OF-TRUTH HIERARCHY

## 2.1 GitHub

GitHub is authoritative for:

- code;
- frozen model/signal contracts;
- source contracts;
- this manifest;
- reproducibility and audit evidence.

## 2.2 Production Neon

Production Neon is authoritative for mutable/current data state:

- observations and provider lineage;
- retrieval/vintage/PIT availability;
- derived feature snapshots;
- engine runtime state;
- forecast contracts when legitimately issued;
- decision snapshots/events when legitimately issued.

## 2.3 Application

The application is a read/presentation layer. It must not silently:

- tune thresholds;
- choose models;
- create an ensemble;
- substitute providers;
- manufacture missing outputs;
- convert a reconstruction into a backdated prospective issuance;
- create BUY / SELL / HOLD / EXIT / REDUCE mappings.

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
- no proxy may be presented under the exact identity of a blocked original source/model
- historical reconstruction, backtest and genuinely prospective evidence must remain distinguishable in audit metadata
- replay/reconstruction must never alter a true historical `issued_at`, `created_at`, retrieval timestamp or source vintage

---

# 4. CANONICAL MONTHLY ORIGIN CYCLE — BINDING v1.32 CORRECTION

This section supersedes all older wording that implied September 2026 forecasts should wait until the end of September.

## 4.1 Core rule

For target calendar month **M**, the H=1 forecast origin is the completed month-end boundary immediately before M.

Formally:

`origin(M) = completed month-end boundary of M-1`

`target(origin) = immediately following calendar month`

Examples:

| Information/origin boundary | Target month |
|---|---|
| 2026-08-31 | **September 2026** |
| 2026-09-30 | **October 2026** |
| 2026-10-31 | **November 2026** |
| 2026-11-30 | **December 2026** |

Therefore:

> **31 August data are the information set for September forecast and month-open direction motors.**

and:

> **30 September data are the information set for October forecast and month-open direction motors.**

There is no rule that September forecast motors should remain blank until 30 September.

## 4.2 What is frozen at month open

At each valid month-end origin, the system should create a month-open snapshot for the immediately following month containing every governed output that is technically executable at that origin.

This includes, according to each motor's own contract:

- H=1 point-forecast expert outputs;
- Monthly Direction 3M context;
- month-open Fast/Slow context;
- monthly Patch reference where executable;
- Emergency initialization state/reference;
- regime/risk context that is legitimately available at the origin.

The month-open snapshot is immutable as an origin snapshot.

## 4.3 Intramonth updating

The target-month snapshot and intramonth monitoring are different objects.

During the target month:

- the month-open H=1 forecasts remain tied to their month-end origin;
- Monthly Direction month-open snapshot remains historically immutable;
- FAST / SLOW may update as their frozen daily/weekly contracts receive new completed observations;
- Emergency Level / Reversal may update intramonth against the frozen monthly reference;
- Macro/Event or other event engines may update only under their own recovered/frozen contracts;
- updated intramonth state must never rewrite the original month-open origin snapshot.

---

# 5. SEPTEMBER 2026 — CURRENT GOVERNED ORIGIN SET

## 5.1 Correct target/origin relationship

Target month:

`2026-09`

Required information boundary:

`2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET

The system must treat the reconstructed 31-August information set as the **September 2026 month-open reference set**.

## 5.2 Current September outputs reconstructed from the 31-Aug information boundary

The following governed values have been reproduced and persisted in the historical/reconstruction evidence lane:

| Motor / context | September 2026 month-open result |
|---|---:|
| `MONTHLY_DIRECTION_3M` | `DOWN` |
| `FAST` | `ROBUST_UP` |
| `SLOW` | `ROBUST_UP` |
| `MOMENTUM_3M` H=1 | `4345.814584037808 USD/oz` |
| `RANDOM_WALK` H=1 | `4397.305673870967 USD/oz` |
| `CAUSAL_PATCH` H=1 reference | `4452.046728838838 USD/oz` |
| `EMERGENCY_LEVEL` month-open state | `NEUTRAL` |
| `EMERGENCY_REVERSAL` month-open state | `OFF` |
| `BOCPD_RETURN_SUCCESSOR_V1` context | `NO_ADVERSE_BREAK_CANDIDATE` |

Patch last selected daily feature date:

`2026-08-30`

This satisfies the frozen `< origin_date` daily-feature rule for the reconstructed 31-Aug origin.

## 5.3 September evidence semantics

The **target/origin logic is valid**: these are September outputs based on the 31-Aug information boundary.

However, some of these values were actually calculated/persisted on 2026-09-04 rather than being emitted on 2026-08-31.

Therefore the system must preserve two facts simultaneously:

1. **Business/forecast interpretation:** September 2026 month-open forecast/direction reference using the 31-Aug origin information set.
2. **Audit/evidence interpretation:** later reconstruction of that origin; not a false claim that the output was actually issued on 31 August.

Required UI primary semantics:

`EYLÜL 2026 · 31 AĞUSTOS ORIGIN`

Required audit/provenance semantics for reconstructed outputs:

`ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY`

or an equivalent explicit secondary label such as:

`31 Ağustos bilgi setiyle 4 Eylül'de yeniden hesaplandı`

The UI must **not** make the September reference look like expired history merely because reconstruction occurred after month open.

The UI also must **not** say or imply `issued on 31-Aug` when no such immutable issuance existed.

---

# 6. OCTOBER 2026 AND FORWARD MONTHLY OPERATION

The next normal monthly cycle is:

- September observations accumulate during September;
- after the completed 2026-09-30 origin boundary and each motor's availability/PIT gates;
- the system calculates **October 2026** H=1 forecasts and month-open direction/reference states;
- if these are actually calculated and immutably persisted before October outcome realization, they may enter the appropriate prospective/shadow evidence class under their individual contracts.

The same rule repeats every month.

No motor should wait until target-month end to generate that same target month's month-open forecast.

---

# 7. H=1 FORECAST TARGET AND VALIDATION CONTRACT

Canonical target:

> **Next calendar month's average XAU/USD price**

Canonical origin:

> **Completed month-end information boundary immediately before the target month**

Binding validation rules:

- rolling/expanding origin only;
- future target information forbidden;
- origin-local data availability mandatory;
- publication lag mandatory;
- vintage/PIT safety mandatory;
- benchmark comparison at identical origin/horizon mandatory;
- no 2026 hindsight tuning;
- model identity, source identity and target identity may not be silently changed.

A reconstructed historical origin may be useful as current-month reference or research evidence but cannot be counted as a truly prospective observation unless it was genuinely emitted before outcome realization.

---

# 8. FORECAST / DIRECTION MOTOR ROLES

## 8.1 H=1 price experts

Governed expert identities currently include:

- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`
- archived `VW_MIDAS_MSVR`

Current role rules:

- Causal Patch is the intended forward challenger/issuer lane under its frozen V7 contracts.
- Momentum 3M and Random Walk remain separate expert/reference outputs.
- Their outputs must not be averaged or winner-selected without a separately proven selector contract.
- archived VW remains blocked until its exact executable/PIT contract is recovered or a separately named successor is built.

## 8.2 Direction/context motors

- `MONTHLY_DIRECTION_3M` — monthly direction context; direction vote permitted.
- `FAST` — tactical short-horizon context; direction vote permitted under frozen contract.
- `SLOW` — tactical slower context; direction vote permitted under frozen contract.
- `GVZ_RISK` — risk-only, never a direction vote.
- Emergency — intramonth alert/context, not standalone automatic action.
- BOCPD successor — regime/break context only, no direction vote.

---

# 9. BOCPD GOVERNANCE

Archived engine:

`BOCPD`

remains:

`BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`

It must not be silently repaired or renamed.

Separate successor identity:

`BOCPD_RETURN_SUCCESSOR_V1`

Current maximum status:

`RESEARCH_SHADOW_CANDIDATE_RISK_DIAGNOSTIC_COMPLETE_PROSPECTIVE_VALIDATION_REQUIRED`

Role:

`REGIME_BREAK_CONTEXT`

Locks:

- direction vote = false;
- no H=1 price forecast;
- no automatic action;
- no selector/ensemble role;
- no position mapping;
- no archived-threshold reuse under an unproven score identity.

September reconstructed context:

`NO_ADVERSE_BREAK_CANDIDATE`

This does not reactivate archived BOCPD.

---

# 10. EMERGENCY GOVERNANCE

Emergency uses the governed monthly reference for the target month and then monitors completed target-month observations.

September 2026 month-open reconstruction:

- monthly Patch reference = `4452.046728838838 USD/oz`;
- `EMERGENCY_LEVEL = NEUTRAL`;
- `EMERGENCY_REVERSAL = OFF`.

31-Aug close is not a September close.

Therefore September Emergency begins from the frozen monthly reference and changes only when legitimate September observations satisfy its frozen rules.

Emergency remains an alert/context layer; it does not create an automatic BUY / SELL / EXIT action.

---

# 11. CURRENT PRODUCTION RUNTIME AUTHORITY

Last audited production runtime distribution:

- `ACTIVE = 4`
- `WAITING = 5`
- `BLOCKED = 3`
- direction-vote permitted = `3`

Current BLOCKED archived identities:

- `VW_MIDAS_MSVR` — `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`
- `MACRO_EVENT` — `BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED`
- `BOCPD` — `BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`

Current WAITING forward-runtime identities include:

- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`

**Interpretation of WAITING after v1.32:**

WAITING means **waiting for the next forward issuance/update gate**, not that the current September month-open reference is absent.

For September, reconstructed 31-Aug reference outputs may be shown separately as available current-month origin references while the forward runtime waits for 30-Sep → October issuance.

This dual-state distinction is mandatory in the UI.

---

# 12. CURRENT PRODUCTION AUTHORITY STORES

Last audited counts remain:

- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`

The September reconstruction evidence does not populate these tables as a backdated canonical/prospective issuance.

Reconstructed values may live only in explicitly non-canonical historical/reconstruction evidence lanes with:

- `prospective_claim = false`
- `canonical_authority = false`
- `direction_vote_permitted = false` for replay-only engine-execution rows unless a separate live runtime state independently grants a vote
- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`

---

# 13. UI CONTRACT — v1.32

## 13.1 Tahmin

During September 2026, the first useful forecast surface must show September month-open information, not an empty card waiting for 30 September.

Primary heading:

`EYLÜL 2026 · 31 AĞUSTOS ORIGIN`

It may show the separate governed September expert outputs:

- Momentum 3M
- Random Walk
- Causal Patch

No synthetic average/winner may be invented.

Secondary provenance must explain when a value was reconstructed later.

## 13.2 Görünüm

Every governed motor remains visible.

For motors with a September reconstructed origin result and a forward WAITING/BLOCKED runtime state, the card must show both:

1. **Eylül / 31 Ağustos origin referansı** — available reconstructed result;
2. **İleri operasyonel durum** — ACTIVE / WAITING / BLOCKED for the next live/prospective cycle.

A user must never interpret `WAITING` as “September için hiçbir sonuç yok” when a valid reconstructed September origin reference exists.

## 13.3 Geçmiş

Geçmiş/audit view must preserve true calculation/persistence timestamps and evidence class.

No historical timestamp may be rewritten for visual convenience.

---

# 14. DATA CONTRACT — CORE RULES

1. No silent provider substitution.
2. Provider identity is part of series identity.
3. Point-in-time availability is mandatory.
4. Historical/reconstructed code must use origin-bounded observations/snapshots.
5. Retrieval-time backfills do not become retroactively knowable.
6. Live/indicative XAU is not canonical EOD authority.
7. Current-day bars cannot be assumed completed before the frozen session boundary.
8. Raw vendor/licensed data must respect display/redistribution rights.
9. Blocked inputs receive no invented same-name proxy.

Canonical R4 decision-reference series:

`XAU_EOD_TWELVE_NY17`

Semantic:

`spot XAU/USD 17:00 ET internal decision reference`

Operational mapping:

- Twelve Data `XAU/USD`
- interval `1min`
- timezone `America/New_York`
- exact bar open `16:59:00` ET
- use bar close as 17:00 ET internal decision reference

This is an internal decision reference, **not official settlement/official close**.

---

# 15. CURRENT EVIDENCE FILES REFERENCED BY THIS MANIFEST

The following are supporting evidence, not independent manifests:

- `GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md`
- `GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_ENGINEERING_EVIDENCE_2026-09-04.md`
- `GOLD_CONTROL_V131_AUG31_REPLAY_UI_FINAL_EVIDENCE_2026-09-04.md`
- `GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-04.md`
- `GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_ENGINEERING_EVIDENCE_2026-09-04.md`
- `GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_RISK_VALIDATION_CONTRACT_2026-09-04.md`
- `GOLD_CONTROL_R4_2_PATCH_EXPERT_EMERGENCY_REFERENCE_CHANGE_CONTROL_2026-09-04.md`
- `GOLD_CONTROL_DATA_EVIDENCE_SPINE_CONTRACT_2026-09-03.md`
- `GOLD_CONTROL_ENGINE_OBSERVABILITY_CONTRACT_2026-09-03.md`
- `GOLD_CONTROL_DECISION_STORE_CONTRACT.md`
- `GOLD_CONTROL_FORECAST_CANONICALIZATION.md`
- `GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md`
- `GOLD_CONTROL_CAUSAL_PATCH_R1_DAILY_FEATURE_PIT_CHANGE_CONTROL_V7_2026-09-02.md`
- `GOLD_CONTROL_PATCH_V7_FIRST_PROSPECTIVE_SHADOW_ISSUER_CONTRACT_2026-09-02.md`

Where old wording in these historical files conflicts with the v1.32 monthly-origin correction, **v1.32 controls the current product behavior** while the historical document remains immutable evidence of what was believed/frozen at that earlier time.

---

# 16. UNRESOLVED / NEXT WORK

## 16.1 VW successor

Archived `VW_MIDAS_MSVR` remains blocked.

If exact replication cannot be proven, build only under a separate successor identity with pre-result change control and PIT-safe validation.

## 16.2 Macro successor

Archived Macro Event remains blocked until exact score/consensus/vintage contract is recovered.

A consensus-free alternative, if researched, requires a separate successor identity.

## 16.3 BOCPD successor

Continue prospective/shadow evidence under its separate identity; do not replace archived BOCPD.

## 16.4 September → October live cycle

The next forward monthly issuance target is **October 2026 using the completed 30-Sep origin**, not September.

This must be executed on-time under the month-end contract so it becomes genuinely prospective rather than reconstructed.

## 16.5 Governance hardening

Branch protection/rulesets remain unresolved unless separately proven configured:

`UNRESOLVED_GOVERNANCE_HARDENING = BRANCH_PROTECTION_NOT_CONFIGURED`

---

# 17. FINAL BINDING SUMMARY

The governing monthly operating rule is now unambiguous:

> **At each completed month-end, Gold Control computes the immediately following month's forecast and month-open direction/reference state using only information available at that origin.**

For the current period:

> **31 Aug 2026 → September 2026 forecast/direction reference.**

Next cycle:

> **30 Sep 2026 → October 2026 forecast/direction reference.**

If an origin was reconstructed later, the target/origin interpretation remains valid, but the audit metadata must truthfully identify it as a reconstruction rather than falsely backdating the issuance.

`AUTO_SELECTOR=OFF` and `AUTO_ENSEMBLE=OFF` remain binding.
