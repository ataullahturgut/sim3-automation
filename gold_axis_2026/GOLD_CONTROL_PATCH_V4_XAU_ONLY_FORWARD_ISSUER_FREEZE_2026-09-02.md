# GOLD CONTROL — PATCH V4 XAU-ONLY FORWARD ISSUER FREEZE

**Date:** 2026-09-02  
**Status:** `FROZEN_FORWARD_ISSUER_CANDIDATE_NOT_YET_PROSPECTIVE`  
**Parent manifest:** v1.18  
**Issuer identity:** `CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`

## 1. Purpose

This file closes the identity/provenance ambiguity for the active Patch issuer candidate after the pre-frozen V4 source gate and locked historical model-impact gate passed.

It does **not** create a prospective forecast, does **not** authorize `LIVE_PRODUCTION`, and does **not** alter the model after inspection of the locked 43-month outcomes.

## 2. Frozen model identity

- architecture family: retained Patch Transformer;
- temporal geometry: `L=252`, `P=21`, `D=32`;
- training/loss/optimizer procedure: unchanged from the V4 locked runner;
- daily metal channels: `XAU` only;
- `XAG`, `XPT`, `XPD`: `OMITTED_NOT_IMPUTED`;
- macro semantics: DFF/FEDFUNDS V1-proven continuation, DEXCHUS/USDCNY V1-proven continuation, `NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3`, existing conservative GPR lag rule;
- target: next calendar month's average XAU/USD price;
- forecast origin: end of the previous completed calendar month;
- selector: `OFF`;
- ensemble primary: `OFF`.

## 3. Frozen code/data lineage

The executable source is frozen at canonical commit `e24b93062446641b206393196942d7d494b9806d` with the following Git blob identities:

- `gold_axis_2026/tools/causal_patch_r1_repro_v4_xau_only.py` → `24ab1645304b719ca3c6a3c0b5c867934a9df836`;
- `gold_axis_2026/GOLD_CONTROL_CAUSAL_PATCH_R1_INPUT_SOURCE_CHANGE_CONTROL_V4_2026-09-02.md` → `6eee89465ffd6b5e2209dfb74dc73a76aa3d6f7f`;
- `gold_axis_2026/GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V4.md` → `41f02269387816ec4bc7319c7146cddd081d67f8`;
- `gold_axis_2026/patch_repro_v1/frozen_geometry.json` → `c65fa295d5ce5ac669ee7b444bd2e19a650bcb6b`;
- `gold_axis_2026/patch_repro_v1/prospective_input_bridge_v4_source_evidence.json` → `12d1f88b53f760c0f6cb4d627a5a9b050a55069d`;
- `gold_axis_2026/patch_repro_v1/locked_replay_v4_xau_only_evidence.json` → `76085ebd591f487a850736001800ef87ec5c5a5b`;
- `gold_axis_2026/patch_repro_v1/locked_replay_v4_xau_only_43.csv` → `a110070b593244a4de3963b9d9c2a90ad7f9b81b`;
- `gold_axis_2026/core5_monthly.csv.gz.b64` → `d3389e532d943734fda632495c0be3bf11c276f3`.

The exact archived historical Patch executable identity remains separately `NOT_PROVEN`; this forward candidate does not inherit that identity claim.

## 4. Evidence boundary

V4 model-impact evidence remains:

- `HISTORICAL_REPLAY_MODEL_IMPACT`;
- `prospective_claim=false`;
- target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic max absolute difference `0`;
- future-information violations `0`;
- candidate MAPE `3.133034811%` < RW `3.302322023%`;
- candidate MAE `102.233331072` < RW `107.465116279`;
- worst-APE ratio vs RW `0.937202691`;
- decision `PATCH_R1_V4_XAU_ONLY_MODEL_IMPACT_PASS`.

These outcomes are evidence only. They may not be used for post-result geometry, threshold, channel, architecture, or source-rule retuning.

## 5. Forward issuance gate

This identity becomes an actual forward issuer only when all of the following are true at an eligible origin:

1. the generic monthly-price-reference → Emergency bridge is validated;
2. an immutable `forecast_input_snapshots` row is persisted before outcome realization;
3. an immutable `monthly_forecast_contracts` row is persisted and bound to that snapshot;
4. the complete versioned EngineSnapshot is constructible without relabelling Patch as historical `monthly_vw_forecast`;
5. evidence class is initially `PROSPECTIVE_SHADOW`;
6. origin/target timing satisfies the frozen H=1 contract.

September 2026 is not backfillable. The next possible fully compliant target remains October 2026 with end-September origin.

## 6. Prohibited changes

Until a separately frozen change-control is issued, do not:

- reselect `L/P/D`;
- add back inaccessible metal channels;
- impute omitted metals;
- introduce a new model family;
- activate auto-selection or auto-ensemble;
- relax V4 gates;
- rewrite historical V4 evidence;
- claim `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` before a real immutable issuance.
