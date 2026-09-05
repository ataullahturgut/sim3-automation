# Gold Control — Macro Event Successor V2 Promotion Change-Control

**Date:** 2026-09-05  
**Status:** `PRE_AUTHORIZED_BY_USER_FOR_RUNTIME_REPLACEMENT`  
**Working branch:** `gold-control-macro-event-successor-v2-promotion`  
**Canonical base:** `gold-r4-direction-engine`

## 1. Decision

The archived `MACRO_EVENT` runtime identity is not repaired, renamed, or silently relabelled. It remains a historical/recovery-blocked identity with its unrecovered archived implementation limitation preserved.

For current Gold Control runtime use, the separately validated successor identity is:

`MACRO_EVENT_SUCCESSOR_V2`

The user explicitly authorized replacement of the archived Macro Event runtime slot by the validated V2 successor, together with canonical manifest, application registry, production runtime-state, and the minimum schema update required to admit the new identity.

## 2. Evidence basis

Promotion is based on two frozen, pre-registered stages completed before this decision:

1. Robust-score replay:
   - frozen source run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`;
   - 126 complete-case reference months;
   - DEV / VAL / LOCK windows preserved;
   - expanding prior MAD normalization with predeclared IQR fallback;
   - future-prefix invariance PASS;
   - result `PASS_V2_ROBUST_PREREG_REPLAY_REPRODUCIBLE`.
2. Gold event-reaction validation:
   - frozen VAL+LOCK strong-shock set: 8 events;
   - preregistered primary window: 08:29 ET bar close to 08:44 ET bar close around the 08:30 Employment Situation release;
   - directional hits: `7/8` = `87.5%`;
   - one-sided exact sign-test p-value: `0.03515625`;
   - median signed R15: `+0.9590818647119803%`;
   - final status: `PASS_EVENT_REACTION_EVIDENCE`;
   - final workflow run: `33980279756`.

The latest governed macro event in the frozen source panel is reference month `2026-08`, released 2026-09-04. Under the frozen V2 rule its state is:

`MACRO_MIXED_OR_SMALL`

with robust composite score:

`-0.414773053241`

## 3. Intended-use boundary

This promotion grants only an active **event-risk/context** role.

Binding role:

`EVENT_RISK_CONTEXT`

It does **not** establish or grant:

- H=1 monthly-average XAU/USD forecast authority;
- a gold direction vote;
- BUY / SELL / HOLD / EXIT / REDUCE authority;
- selector participation;
- ensemble participation;
- position mapping;
- trading-profitability claims;
- Forecast Store authority;
- Decision Store authority.

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_EXPERT_SELECTION_RULE`, and `NOT_PROVEN_POSITION_MAPPING` remain unchanged.

## 4. Operational state transition

Target current-runtime state after deployment:

- archived `MACRO_EVENT`: historical identity, excluded from the current 12-engine application registry;
- `MACRO_EVENT_SUCCESSOR_V2`: `ACTIVE`;
- role: `EVENT_RISK_CONTEXT`;
- status code: `ACTIVE_MACRO_EVENT_SUCCESSOR_V2_EVENT_RISK_CONTEXT`;
- direction vote permitted: `false`;
- current September event-context reference: `MACRO_MIXED_OR_SMALL`.

The archived identity remains queryable in the append-only runtime ledger and should receive an explicit archival transition record with:

`BLOCKED_ARCHIVED_REPLACED_BY_MACRO_EVENT_SUCCESSOR_V2`

and `replaced_by = MACRO_EVENT_SUCCESSOR_V2` metadata.

## 5. Evidence and timestamp semantics

The current September state was reconstructed from historical/PIT research data after the historical release and therefore remains:

`HISTORICAL_REPLAY`

It must not be presented as if Gold Control prospectively issued that state at 08:30 ET on 2026-09-04.

The runtime promotion itself becomes effective only at the true deployment timestamp on 2026-09-05 and must not be backdated.

The live runtime row may expose the historical current-state reference through metadata while its own evidence class remains `RUNTIME_GOVERNANCE_AUDIT`.

## 6. Production-write authorization

This change-control authorizes only the minimum production writes required for this runtime replacement:

- schema constraint update on `engine_execution_runs` to admit `MACRO_EVENT_SUCCESSOR_V2` while preserving archived identities;
- append-only archival runtime record for `MACRO_EVENT`;
- append-only active runtime record for `MACRO_EVENT_SUCCESSOR_V2`.

It does **not** authorize writes to:

- `monthly_forecast_contracts`;
- `decision_signal_snapshots`;
- `decision_runs`;
- `decision_events`.

Those four authority-store counts must remain `0/0/0/0` before and after promotion.

## 7. Expected current application inventory

After successful code + production runtime deployment, the current 12-engine application registry target is:

- `ACTIVE = 6`;
- `WAITING = 5`;
- `BLOCKED = 1`;
- direction-vote permitted = `3`;
- total current governed application motors = `12`.

The remaining current blocker is:

`VW_MIDAS_MSVR`

Archived `BOCPD` and archived `MACRO_EVENT` remain audit/history ledger identities and do not count in the current 12-engine registry.

## 8. Stop conditions

Promotion must fail closed if any of the following occurs:

- validated V2 identity or frozen scoring rule changes;
- production schema cannot preserve archived identities while adding V2;
- current registry count differs from 12;
- V2 direction vote becomes true;
- any Forecast/Decision authority-store count changes;
- old `MACRO_EVENT` remains in the current application registry;
- timestamp/evidence semantics are backdated or rewritten.
