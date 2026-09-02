# GOLD CONTROL — H=1 FORECAST PATH CORRECTION

**Date:** 2026-09-02  
**Status:** `APPROVED_PATH_CORRECTION`  
**Supersedes as active development path:** the simple monthly R2 successor model-search lane introduced on 2026-09-01.

## 1. Reason

The approved Gold Control architecture already froze the H=1 role structure around a reproducible Causal Patch production implementation, VW-MIDAS-MSVR as audited shadow/reference, 3M Momentum as direction challenger/context, and Random Walk as benchmark. The later R2 Ridge/Huber/SVR/Drift/Damped model-search lane was a methodological detour from that agreed architecture.

The R2 score run remains part of Git history as an auditable negative experiment, but it is no longer an active production-development contract and must not drive the next stage.

## 2. What is preserved

The following work remains valid and is retained:

- Neon data-plane architecture, source registry, vintages, observations, quality and PIT controls;
- World Bank/CORE5 target identity evidence and the historical research target rows written to Neon;
- ALFRED PIT reconstruction rows for DGS10, DFF, DEXCHUS and NASDAQ100;
- Twelve NY17 daily decision-reference pipeline;
- Decision Store V1 and its append-only reader/writer path;
- monthly 3M context, Fast/Slow tactical architecture, BOCPD return break alert, Emergency layer and GVZ risk layer;
- Piyasa/Görünüm/Tahmin/Geçmiş information architecture;
- legacy VW/Patch identity audits proving that exact old executable identity is not recovered.

The 639 historical data-plane rows written on 2026-09-01 are not rolled back because they are source-labelled historical/PIT research observations and no forecast contract, forecast input snapshot, or prospective decision was manufactured by that write.

## 3. What is retired from the active path

The following are retired as active development logic:

- `GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2.md`;
- `run_successor_r2_historical_replay.py`;
- the active `successor_r2/` score/evidence files;
- the GitHub Actions R2 replay launcher;
- manifest language that made Ridge/Huber/SVR/Drift/Damped the next canonical H=1 path.

Their Git commit history remains the audit trail.

## 4. Restored H=1 role contract

### Intended primary executable

`CAUSAL_PATCH_R1_REPRO_V1`

This is a newly reproducible implementation of the retained causal Patch architecture. It is **not** allowed to claim byte-for-byte or forecast-for-forecast identity with the archived Causal Patch artifact unless such identity is separately proven.

Before it can become the production point-forecast path it must pass the frozen reproducibility and leakage-safe replay contract.

### Audited shadow/reference

`VW_AUDITED_SHADOW_V2`

The audited VW-MIDAS-MSVR historical outputs remain the analytical reference. Exact original runner recovery is still `BLOCKED_NOT_PROVEN`, but that does not require replacing the agreed H=1 architecture with a broad new model search.

### Direction challenger/context

`MOMENTUM_3M_R1`

### Mandatory naive benchmark

`RW_R1`

### Frozen switches

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE_PRIMARY = OFF`

Model disagreement may be displayed; model identity may not be silently swapped.

## 5. Correct next stage

The next canonical Stage-4B task is:

> **Build and validate one deterministic, causal, reproducible Causal Patch R1-family implementation under the existing H=1 target/origin contract.**

The implementation must use only source-locked/origin-safe information, must be evaluated on the same 43-month 2023-01→2026-07 common window, and must be compared with RW plus the archived Patch/VW references without tuning on that locked window.

If the reproducible Patch candidate fails, development remains inside the Patch implementation/reproducibility problem until a formal change-control says otherwise. It does not automatically reopen a wide model zoo.

## 6. Prospective boundary

No September 2026 H=1 forecast may be backdated. The first still-eligible contract-compliant prospective target remains October 2026 at the end-September origin, subject to a validated executable forecast path and immutable forecast snapshot/contract being issued before outcome realization.
