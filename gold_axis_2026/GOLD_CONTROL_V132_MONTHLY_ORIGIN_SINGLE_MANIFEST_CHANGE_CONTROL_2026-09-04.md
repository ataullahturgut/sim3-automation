# GOLD CONTROL v1.32 — MONTHLY ORIGIN + SINGLE MANIFEST CHANGE CONTROL

**Date:** 2026-09-04  
**Status:** `FROZEN_V132_SEMANTIC_AND_GOVERNANCE_CORRECTION`  
**Canonical project-manifest target:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`  
**Feature branch:** `gold-control-v132-monthly-origin-contract`

## 1. User-requested correction

The binding monthly operating cycle is corrected to:

- completed 31-Aug-2026 information boundary → September 2026 H=1 forecast and month-open direction/reference set;
- completed 30-Sep-2026 information boundary → October 2026 H=1 forecast and month-open direction/reference set;
- repeat monthly.

The system must not wait until the end of a target month to calculate that same target month's month-open forecast.

## 2. Evidence truthfulness

September values reconstructed on 2026-09-04 from the frozen 31-Aug information boundary are valid September origin references, but their audit metadata must remain truthful:

- target/origin interpretation: `SEPTEMBER_2026_FROM_2026_08_31_ORIGIN`;
- actual reconstruction timing: 2026-09-04;
- audit class: `ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY`;
- no claim that the values were actually issued on 31-Aug-2026;
- no backdating of `issued_at`, persistence, retrieval or source-vintage timestamps.

This change does not change any numeric September result, model coefficient, threshold, source series, feature rule, or model identity.

## 3. Current frozen September origin results

- Monthly Direction 3M = `DOWN`
- FAST = `ROBUST_UP`
- SLOW = `ROBUST_UP`
- Momentum 3M = `4345.814584037808 USD/oz`
- Random Walk = `4397.305673870967 USD/oz`
- Causal Patch = `4452.046728838838 USD/oz`
- Emergency Level = `NEUTRAL`
- Emergency Reversal = `OFF`
- BOCPD successor = `NO_ADVERSE_BREAK_CANDIDATE`
- archived BOCPD remains blocked.

## 4. Single-manifest governance

There must be one current Gold Control project manifest only:

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`

All other change-control/status/evidence/handover files are supporting audit records, not alternative manifests.

Historical manifest reconciliation/apply workflows must not be allowed to auto-downgrade or rewrite the current canonical manifest. Legacy manifest writers are to be retired to manual-only historical workflows.

## 5. UI semantics

Primary September user-facing semantics:

`EYLÜL 2026 · 31 AĞUSTOS ORIGIN`

The Tahmin surface must show separate September expert references (no invented winner/average): Momentum, Random Walk and Causal Patch.

The Görünüm surface must show both:

1. September / 31-Aug origin reference where available;
2. forward operational state for the next live cycle.

Secondary audit provenance must say the origin was reconstructed on 4 September when applicable.

## 6. Non-negotiable locks

Unchanged:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no BUY / SELL / HOLD / EXIT / REDUCE
- no canonical/Decision Store backfill for reconstructed September outputs
- production runtime distribution remains read from Neon, not rewritten by UI semantics.

## 7. Acceptance gates before canonical promotion

1. manifest v1.32 is the sole current project manifest;
2. no legacy auto-triggered workflow can downgrade/rewrite it;
3. app and deterministic tests pass;
4. production Neon read-only audit proves 4 ACTIVE / 5 WAITING / 3 BLOCKED and decision-authority tables remain zero;
5. exact September origin values remain unchanged;
6. DB-backed and DB-less 390x844 UI show `EYLÜL 2026 · 31 AĞUSTOS ORIGIN` and the three separate forecast references;
7. audit provenance remains visible and truthful;
8. selector/ensemble/action locks remain closed;
9. canonical/UI promotion occurs only after exact candidate-head PASS.
