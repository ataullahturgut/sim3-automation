# Gold Control — Macro Event Successor V2 Score Replay Change Control

Date: 2026-09-05
Branch: `gold-control-macro-event-successor-v2-robust-score`
Engine identity: `MACRO_EVENT_SUCCESSOR_V2`

## Scope

This change control authorizes a **read-only historical research replay** of the preregistered V2 robust macro-surprise score. It does not authorize runtime promotion, production model-state persistence, direction voting, selector/ensemble participation, action/position mapping, Forecast Store writes, or Decision Store writes.

## Binding preregistration

The replay must use the frozen formula in:
`gold_axis_2026/GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V2_ROBUST_SCORE_PREREG_2026-09-05.md`

Binding preregistration blob SHA:
`3584e8e89307971405a439fba9f8229f571e7852`

No formula, signs, weights, thresholds, fallback hierarchy, minimum-history rule, source run, or evidence window may be changed after V2 replay results are inspected.

## Frozen source input

The replay must read only the already-governed Macro Event research source bundle from Neon:
- retrieval run: `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`
- pipeline: `MACRO_EVENT_SUCCESSOR_V1_RESEARCH_DATA_PLANE_R1`
- expected observations: 756
- expected complete-case reference months: 126
- expected excluded months: `2020-08`, `2025-10`

No live API call or source substitution is allowed during score computation.

## Required engineering checks

The replay must fail closed unless:
- frozen source run status/pipeline/counts match exactly;
- all six series are present for every included month;
- source input fingerprint is emitted;
- prefix invariance passes;
- unit/compile tests pass;
- four Forecast/Decision authority-store counts are identical before and after replay;
- no model result is inserted into Neon;
- `direction_vote=false` and `forecast_or_decision_write=false` remain explicit.

## Output classification

Output is `HISTORICAL_REPLAY_RECONSTRUCTION` research evidence only.

Any shock-state dates are descriptive outputs of the frozen V2 formula and are not trading/position instructions.

## Stop point

A successful V2 score replay is not sufficient for promotion. The next admissible phase is a separately preregistered point-in-time gold event-reaction validation. Until that passes, V2 remains research-only.