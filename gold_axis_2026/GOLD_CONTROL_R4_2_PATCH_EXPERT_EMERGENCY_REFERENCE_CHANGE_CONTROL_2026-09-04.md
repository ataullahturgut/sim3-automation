# Gold Control — R4.2 Patch Expert Emergency Reference Change Control

**Issue date:** 2026-09-04  
**Status:** `FROZEN_PATCH_EXPERT_EMERGENCY_REFERENCE_V1`  
**Scope:** Forward Emergency reference persistence bridge  
**Selector authority:** unchanged / `OFF`  
**Ensemble authority:** unchanged / `OFF`  
**Canonical forecast authority:** unchanged

## 1. Problem

R4.2 Emergency geometry already accepts a generic `MonthlyPriceReference`, but its persisted-reference gate was written before the v1.22 multi-expert ledger became authoritative. The old gate recognizes only the legacy/canonical identity family `input_snapshot_id + forecast_contract_id`.

The governed forward Patch issuer persists its output instead as one `monthly_expert_forecasts` row linked to an immutable `forecast_input_sets` row. It intentionally does not write `monthly_forecast_contracts` because expert selection remains `NOT_PROVEN_EXPERT_SELECTION_RULE` and both auto selector and auto ensemble remain OFF.

Treating a multi-expert record ID as a forecast-contract ID would be false provenance and is prohibited.

## 2. Frozen correction

`MonthlyPriceReference` may carry exactly one complete persisted identity family:

1. `FORECAST_CONTRACT`: `input_snapshot_id + forecast_contract_id`; or
2. `MONTHLY_EXPERT_FORECAST`: `input_set_id + expert_forecast_id`.

Partial identity families, mixed identity families, or missing persistence identity fail closed when persisted reference is required.

## 3. Forward Patch reference policy

The only expert-ledger adapter authorized by this change control is an explicitly named **Patch-referenced Emergency context**. It accepts a persisted row only when all are true:

- `expert_id = CAUSAL_PATCH`;
- `forecast_track = MONTH_END_EXPERT`;
- evidence is `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`;
- `canonical_authority = false`;
- `AUTO_SELECTOR = OFF`;
- `AUTO_ENSEMBLE = OFF`;
- `selector_status = NOT_PROVEN_EXPERT_SELECTION_RULE`;
- persisted `monthly_expert_forecasts.id` exists;
- persisted `input_set_id` exists.

This is **not** an expert-winner rule. Patch is used only because it is the separately frozen operational forward issuer candidate. The resulting Emergency state must remain explicitly Patch-referenced and may not be relabelled as a canonical system Emergency state until a separate authority contract proves such promotion.

## 4. September 2026 rule

This change does not authorize a September Patch replay. No governed Patch expert row exists for the missed 31-August prospective origin, and the Aug-31 replay contract remains authoritative.

Therefore September Emergency Level/Reversal remain blocked as a single governed Emergency reference. Momentum or Random Walk may not be substituted, averaged, selected, or relabelled as Patch.

## 5. First forward opportunity

The first eligible Patch expert reference can exist only after the governed Patch V7 issuer successfully writes the October 2026 `MONTH_END_EXPERT` row at the frozen Sep-30 origin window.

Until that persisted row exists, the forward Emergency reference state is `WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE`; it is not ACTIVE and no Emergency output may be fabricated.

## 6. Frozen geometry unchanged

This change does not modify:

- level emergency threshold geometry;
- reversal threshold geometry;
- reversal alert-only semantics;
- monthly direction logic;
- FAST/SLOW logic;
- GVZ risk cap;
- Macro Event or BOCPD;
- Decision Store or position mapping.

Only persistence identity/provenance compatibility is changed.

## 7. Required validation

Promotion requires tests proving:

- legacy forecast-contract persistence still passes;
- multi-expert persistence passes only with a complete expert/input-set identity;
- Patch expert adapter rejects non-Patch experts;
- historical replay is rejected by the forward Patch adapter;
- selector/ensemble/canonical locks fail closed;
- frozen Emergency geometry is numerically unchanged by identity family.
