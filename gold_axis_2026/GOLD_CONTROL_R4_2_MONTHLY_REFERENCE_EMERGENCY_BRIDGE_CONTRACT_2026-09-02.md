# GOLD CONTROL — R4.2 MONTHLY REFERENCE → EMERGENCY BRIDGE CONTRACT

**Date:** 2026-09-02  
**Status:** `FROZEN_BEFORE_BRIDGE_TEST_RESULT`  
**Parent manifest:** v1.18  
**Active issuer candidate:** `CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`

## 1. Problem being solved

Frozen R4.1 names the monthly numeric reference field `monthly_vw_forecast`. The active H=1 issuer candidate is Patch V4 XAU-only. Writing a Patch value into a field whose semantic identity says VW would violate provenance.

The Emergency calculation itself is model-agnostic: it uses the numeric displacement `close / monthly_reference - 1` and the frozen 4% level/reversal thresholds. Therefore the integration correction is a provenance bridge, not a threshold/model change.

## 2. Frozen bridge rule

R4.2 introduces a generic `MonthlyPriceReference` carrying:

- numeric reference value;
- explicit `model_id`;
- target month;
- forecast origin;
- evidence class;
- immutable input snapshot id when persisted;
- forecast contract id when persisted.

The frozen R4.1 Emergency geometry remains unchanged:

- level threshold absolute = `0.04`;
- reversal threshold absolute = `0.04`;
- reversal role = `ALERT_ONLY`;
- automatic full direction flip = `false`.

R4.2 may call the frozen Emergency implementation with the numeric reference value, but it must carry the source model identity separately and must never relabel Patch as `monthly_vw_forecast`.

## 3. Acceptance gates

Before this bridge is marked PASS:

1. for the same positive numeric reference and EOD close, generic-reference level Emergency must exactly equal the legacy R4.1 numeric geometry across boundary and off-boundary cases;
2. reversal-alert state transitions must exactly match the legacy R4.1 numeric geometry;
3. changing only `model_id` must not change Emergency mathematics;
4. bridge output must preserve the explicit reference model id;
5. when `require_persisted_reference=true`, missing input-snapshot or forecast-contract ids must fail closed;
6. R4.1 frozen config must not be edited;
7. no model score, threshold, geometry, source rule, or historical outcome may be used to tune this bridge;
8. no Neon/forecast-ledger/Decision Store write is permitted during bridge validation.

PASS identity:

`R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_PASS`

FAIL identity:

`BLOCKED_R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_NOT_VALIDATED`

## 4. Evidence class

Bridge validation is a structural/integration test. It is not a new forecasting performance result and does not alter the V4 `HISTORICAL_REPLAY_MODEL_IMPACT` evidence class.

## 5. Downstream dependency

After bridge PASS, the remaining forward path is:

1. verify forecast-state schema/immutability read-only;
2. implement fail-closed immutable forecast snapshot + contract writer bound to the frozen Patch issuer identity;
3. rehearse the writer without persistence / with rollback-only verification;
4. construct the complete R4.2 forward EngineSnapshot;
5. arm the eligible-origin issuer;
6. first real issuance remains `PROSPECTIVE_SHADOW`.
