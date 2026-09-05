# Gold Control — BOCPD Successor V1 Promotion Change-Control

**Date:** 2026-09-05
**Status:** `PRE_AUTHORIZED_BY_USER_FOR_RUNTIME_REPLACEMENT`
**Working branch:** `gold-control-bocpd-successor-v1-promotion`
**Canonical base:** `gold-r4-direction-engine`

## 1. Decision

The archived `BOCPD` runtime identity is not to be repaired or silently relabelled. It remains an archived historical identity with its recovery limitation recorded.

For current Gold Control runtime use, the new engine identity is:

`BOCPD_RETURN_SUCCESSOR_V1`

The user explicitly authorized replacement of the archived BOCPD runtime role by the validated successor, together with manifest, code and production runtime-state updates.

## 2. Evidence basis

The successor already completed its frozen research gate before this promotion decision:

- deterministic executable implementation;
- 14 tests PASS;
- future-prefix invariance PASS;
- frozen DEV / VAL / LOCK windows respected;
- database writes NONE during research validation;
- archived reset-score threshold not reused;
- role remains `REGIME_BREAK_CONTEXT`;
- direction vote remains prohibited;
- automatic action / position mapping remain prohibited.

The 31-Aug-2026 completed-month context run produced:

- `state = NO_ADVERSE_BREAK_CANDIDATE`;
- `map_reset = false`;
- `reset_fraction = 0.0`;
- `expected_run_length = 36` months.

## 3. Promotion semantics

This change promotes the successor only as the active regime/break-context engine. It does **not**:

- grant a direction vote;
- grant BUY / SELL / HOLD / EXIT / REDUCE authority;
- enable AUTO_SELECTOR;
- enable AUTO_ENSEMBLE;
- create position mapping;
- create forecast authority;
- write to Decision Store authority tables.

The archived `BOCPD` identity must remain traceable as historical/recovery-blocked evidence, while runtime/UI references for the active regime-break-context role must point to `BOCPD_RETURN_SUCCESSOR_V1`.

## 4. Operational state transition

Target runtime state after deployment:

- archived `BOCPD`: historical identity, not an active runtime engine;
- `BOCPD_RETURN_SUCCESSOR_V1`: `ACTIVE`;
- role: `REGIME_BREAK_CONTEXT`;
- direction vote permitted: `false`;
- current September context from 31-Aug completed-month data: `NO_ADVERSE_BREAK_CANDIDATE`.

## 5. Data and audit locks

- Do not backdate this runtime promotion to 31-Aug-2026.
- The 31-Aug result remains a historical/reconstructed context observation.
- Promotion effective time is the actual database/code deployment time on 2026-09-05.
- Do not overwrite historical evidence artifacts.
- Do not alter frozen BOCPD model mathematics, prior, hazard, validation windows, or state rule as part of this promotion.
- Do not write to `monthly_forecast_contracts`, `decision_signal_snapshots`, `decision_runs`, or `decision_events` as part of this change.

## 6. Authority basis

Methodological basis remains Adams & MacKay, *Bayesian Online Changepoint Detection* (2007), with exact causal run-length filtering under the separately frozen successor contract.

Current model-risk governance authority reviewed on 2026-09-05: Federal Reserve SR 26-2 / Revised Guidance on Model Risk Management. The promotion is deliberately limited to the validated intended use and preserves explicit limitations, monitoring, and traceability.
