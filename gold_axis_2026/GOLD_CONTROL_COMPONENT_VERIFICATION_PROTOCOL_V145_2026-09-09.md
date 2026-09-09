# GOLD CONTROL — COMPONENT VERIFICATION PROTOCOL V1.45

**Date:** 2026-09-09  
**Status:** `FROZEN_IMPLEMENTATION_OF_MANIFEST_V145_COMPONENT_VERIFICATION_GATE`  
**Parent manifest:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` v1.45  
**Parent readiness contract:** `gold_axis_2026/GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md`  
**Historical reconstruction lane:** `gold_axis_2026/GOLD_CONTROL_HISTORICAL_RECONSTRUCTION_ARTIFACT_LANES_V145_2026-09-09.md`

## 1. Scope

This protocol implements, without changing, the `COMPONENT VERIFICATION` gate already frozen in Manifest v1.45 section 11.4.

It does **not** create a new model, threshold, feature, source, hyperparameter, role, evaluation metric, selector, ensemble or position/action rule. It does not score economic/model performance and it cannot use 2025/2026 outcomes to repair or promote a component.

The only question answered here is:

> Is each governed component technically the frozen component we claim it is, using its governed source/timing semantics, with sufficient historical coverage and reproducibility evidence to enter role-specific validation?

## 2. Authority basis

The project-specific authority is Manifest v1.45 and the frozen component/source contracts already in canonical GitHub.

The verification design follows the general model-risk principle that validation rigor must be aligned with model purpose/use and should separately assess conceptual/implementation soundness, data/source appropriateness, limitations and outcomes. Component Verification is therefore intentionally separated from the later role-specific performance stage.

## 3. Engine inventory

Exactly 12 governed identities are in scope:

1. `CAUSAL_PATCH`
2. `VW_MIDAS_MSVR_SUCCESSOR_V1`
3. `MOMENTUM_3M`
4. `RANDOM_WALK`
5. `MONTHLY_DIRECTION_3M`
6. `FAST`
7. `SLOW`
8. `MACRO_EVENT_SUCCESSOR_V2`
9. `BOCPD_RETURN_SUCCESSOR_V1`
10. `EMERGENCY_LEVEL`
11. `EMERGENCY_REVERSAL`
12. `GVZ_RISK`

No other identity may be silently substituted.

## 4. Verification dimensions

Each component is checked across these dimensions. A dimension may be `PASS`, `FAIL`, `BLOCKED` or `NOT_PROVEN`.

### C1 — `FROZEN_IDENTITY`
The implementation/model version must match the frozen contract/runtime identity. A renamed or repaired model is not accepted as the same component.

### C2 — `IMPLEMENTATION_RULE`
Executable mathematics and hard-coded/frozen configuration must match the governing contract. Component Verification may test implementation behavior but may not alter it.

### C3 — `SOURCE_BINDING`
Only the governed source identity/provider/series semantics are permitted. Silent provider substitution is a failure.

### C4 — `HISTORICAL_COVERAGE`
The historical data and prehistory required for the full `2025-01..2026-08` pilot must be available or explicitly contractually excluded. Historical reconstruction may satisfy this dimension only through the frozen V1.45 artifact lane and must remain retrospective evidence.

### C5 — `ORIGIN_PIT`
The component must obey its frozen completed-period/release/origin rule. Revision-prone inputs require the frozen first-print/consensus/vintage semantic.

### C6 — `FUTURE_INFORMATION`
Known leakage/future-target violations must be zero. Where the component has a prefix-invariance or strict-before-origin test, it must pass.

### C7 — `RECONSTRUCTION_VINTAGE`
Historical reconstruction, late retrieval and revision-sensitive sources must retain truthful evidence class, retrieval/vintage semantics and source lineage. Backdating is forbidden.

### C8 — `DETERMINISM_REPRODUCIBILITY`
Where the component contract defines deterministic rerun/reconciliation evidence, it must pass. An existing immutable frozen replay may satisfy this dimension for its explicit window only.

### C9 — `PILOT_CELL_EXECUTION`
Required pilot cells outside existing frozen replay evidence are not silently treated as executed. A technically runnable but not-yet-executed cell remains `NOT_PROVEN` until the frozen identity is replayed without changing rules.

## 5. Final component status

`PASS` — every required technical dimension for the full frozen pilot is proven, with contractual exclusions explicitly preserved.

`NOT_PROVEN` — no contradiction is found, but one or more required replay/reproducibility/pilot-cell proofs are not yet present.

`BLOCKED` — a governed prerequisite is currently unavailable or the requested pilot cell is outside the frozen contract. The component is not repaired inside this pilot.

`FAIL` — executable identity/source/timing/rule contradicts the frozen contract, or future information/provider substitution is proven.

A component may have many passing dimensions while its final status remains `NOT_PROVEN` or `BLOCKED`. This prevents loss of valid evidence while remaining fail-closed.

## 6. Engine-specific mandatory checks

### `CAUSAL_PATCH`
- exact identity `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`;
- geometry `L=252, P=21, D=32` unchanged;
- completed-session feature strictly before origin;
- zero same-origin feature use and zero future-information violations;
- deterministic reconciliation evidence for the frozen covered window;
- uncovered `2026-08` pilot cell cannot be promoted merely from data availability.

### `VW_MIDAS_MSVR_SUCCESSOR_V1`
- four exact StakTrakr research series plus `GPR_OFFICIAL_GIT_PIT`;
- origin-local GPR vintage and p-1 publication-lag rule;
- frozen 8-feature four-metal vector;
- true multi-output RBF MSVR;
- frozen grid `C={0.1,1,10}`, `epsilon={0.02,0.05}`, `gamma_scale={0.5,1}`;
- nested rolling-origin selection from prior eligible targets only, minimum six inner forecasts, deterministic tie-break;
- deterministic rerun and authority-store invariance;
- no result/performance field may be used by this verifier to change status except a technical failure already defined by the frozen contract.

### `MOMENTUM_3M` / `RANDOM_WALK`
- exact R2 identities;
- only `SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`;
- Twelve Data `XAU/USD`, 1h, America/New_York, governed 17:00 ET hourly-close semantic;
- minimum selected observations/month rule preserved;
- zero provider substitution, future-information violations and deterministic rerun difference;
- uncovered `2026-08` execution remains explicit until replayed.

### `MONTHLY_DIRECTION_3M`
- last three completed monthly returns only;
- arithmetic mean; positive `UP`, negative `DOWN`, zero `NEUTRAL`;
- governed historical source semantic is exact NY17 V1.45 lane;
- no target-month observation at target-month open.

### `FAST`
- SMA20 and exactly two completed-trade-date persistence states;
- exact NY17 source semantic;
- chronological replay and sufficient prehistory.

### `SLOW`
- completed `W-FRI` weekly closes;
- incomplete current week excluded;
- SMA4 and exactly two completed-week persistence states;
- no missing daily NY17 input hidden by weekly aggregation.

### `MACRO_EVENT_SUCCESSOR_V2`
- exact frozen source retrieval run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`;
- exactly six governed series, 126 complete-case months / 756 rows;
- contractual exclusions `2020-08`, `2025-10` remain explicit;
- minimum 24 prior complete cases;
- MAD 1.4826 scale with deterministic IQR fallback only;
- frozen signs/equal weights/±1 state thresholds;
- prefix invariance and deterministic replay;
- no authority/runtime/model-result write by the research replay.

### `BOCPD_RETURN_SUCCESSOR_V1`
- source `core5_monthly.csv.gz.b64:gold_monthly`;
- completed-month `log(P_t/P_t-1)` only;
- development prior only;
- constant-geometric hazard 1/36;
- frozen locked window ends `2026-07` and `tuning_2026=NONE`;
- `2026-08` remains `BLOCKED` until a separately governed evaluation-only extension exists; no mathematics/tuning change is permitted.

### `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL`
- exact NY17 chronological target-month sequence;
- positive immutable/origin-bounded monthly reference;
- level threshold ±4%; reversal threshold 4%;
- month reset and chronological peak/trough memory preserved;
- no later peak/trough may rewrite an earlier state.

### `GVZ_RISK`
- `GVZ_CBOE` only;
- frozen thresholds `25.9795` and `30.5238`;
- cap mapping `1.0 / 0.5 / 0.25`, panic only above the upper threshold;
- V1.45 official-Cboe reconstruction artifact may supply historical coverage but remains retrospective.

## 7. Performance isolation

The verifier must not consume MAE, MAPE, RMSE, win rate, direction accuracy, shock frequency, event reaction performance, economic value or architecture contribution to determine Component Verification status.

Those belong to later stages.

A regression test must prove that modifying/removing performance-only fields cannot convert a technical component status.

## 8. Read-only boundary

The Component Verification implementation must be read-only against production Neon. It may use `SELECT` and read-only transactions only.

It must not write:

- observations/source registry/retrieval runs;
- runtime/context tables;
- forecast/decision stores;
- selector/ensemble state;
- model result tables.

Generated evidence is stored in canonical GitHub/audit artifacts only.

## 9. Current sequencing rule

As of protocol issue, final NY17 exact-date reconstruction is still a prerequisite for the five NY17-dependent components. Their implementation/source rules may be verified in advance, but their final full-pilot component status must remain `BLOCKED` until the historical gap lane is fully adjudicated and post-gap readiness is rerun.

The verifier may therefore emit a **provisional pre-gap Component Verification** result. It must be rerun after historical gap completion before role-specific validation begins.

## 10. Acceptance to next stage

`ROLE-SPECIFIC VALIDATION` may begin for a component only after its final Component Verification status is `PASS` for the required frozen pilot scope, or where the manifest explicitly permits a contractual exclusion that does not invalidate the component.

`NOT_PROVEN`, `BLOCKED`, and `FAIL` are not silently overridden by performance.