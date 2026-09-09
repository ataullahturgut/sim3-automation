# Gold Control data completion and readiness — 2026-09-09

Status is evaluated independently on three axes. Historical reconstruction is
never counted as prospective evidence.

## Executive result

* Historical-pilot data: **12/12 DATA_READY**. The previously missing exact
  August World Bank Gold target is 4411 USD/troy ounce; the frozen CORE5 file was
  not overwritten. BOCPD August evaluation replay is deterministic PASS.
* Prospective-shadow data: **0/12 fully proven as a complete system**. VW is
  `WAITING_FOUR_METAL_SOURCE_DATA`: the pinned StakTrakr snapshot has 19 August
  common dates and zero September dates versus the frozen 20/20 and Sep-27 gates.
  This is a source/calendar wait, not permission to substitute data.
* Current intramonth data: **5/5 relevant roles caught up by their role clock**.
  FAST and the two Emergency roles bind the Sep-09 NY17 bar; GVZ binds Sep-08.
  SLOW correctly remains bound to the last completed week (Sep-04), so a generic
  latest-daily-row comparison reports FAIL while the frozen completed-week clock
  is current.

## Engine matrix

| Engine | Historical pilot | Prospective source | Current/live freshness | Final data status |
|---|---|---|---|---|
| CAUSAL_PATCH | DATA_READY | NOT_PROVEN | NOT_APPLICABLE | HISTORICAL_READY_PROSPECTIVE_NOT_PROVEN |
| VW_MIDAS_MSVR_SUCCESSOR_V1 | DATA_READY | WAITING_FOUR_METAL_SOURCE_DATA | NOT_APPLICABLE | WAITING_SOURCE_CALENDAR |
| MOMENTUM_3M | DATA_READY | NOT_PROVEN | NOT_APPLICABLE | HISTORICAL_READY_PROSPECTIVE_NOT_PROVEN |
| RANDOM_WALK | DATA_READY | NOT_PROVEN | NOT_APPLICABLE | HISTORICAL_READY_PROSPECTIVE_NOT_PROVEN |
| MONTHLY_DIRECTION_3M | DATA_READY | NOT_PROVEN | NOT_APPLICABLE | HISTORICAL_READY_PROSPECTIVE_NOT_PROVEN |
| FAST | DATA_READY | NOT_PROVEN | PASS_SEP09_NY17 | CURRENT_INTRAMONTH_DATA_READY |
| SLOW | DATA_READY | NOT_PROVEN | PASS_COMPLETED_WEEK_SEP04 | CURRENT_INTRAMONTH_DATA_READY |
| MACRO_EVENT_SUCCESSOR_V2 | DATA_READY_WITH_CONTRACTUAL_EXCLUSION | NOT_PROVEN | NOT_APPLICABLE | HISTORICAL_READY_PROSPECTIVE_NOT_PROVEN |
| BOCPD_RETURN_SUCCESSOR_V1 | DATA_READY | NOT_PROVEN | NOT_APPLICABLE | HISTORICAL_READY_PROSPECTIVE_NOT_PROVEN |
| EMERGENCY_LEVEL | DATA_READY | NOT_PROVEN | PASS_SEP09_NY17 | CURRENT_INTRAMONTH_DATA_READY |
| EMERGENCY_REVERSAL | DATA_READY | NOT_PROVEN | PASS_SEP09_NY17 | CURRENT_INTRAMONTH_DATA_READY |
| GVZ_RISK | DATA_READY | NOT_PROVEN | PASS_SEP08_GVZ | CURRENT_INTRAMONTH_DATA_READY |

## Governed evidence and writes

* World Bank official payload SHA-256:
  `9fdcfa8a2aed9a1bb545a10c1a5ce036c6a0acd4766f450424ca800b4b5a0225`.
  Evidence class is `HISTORICAL_REPLAY_RECONSTRUCTION`; prospective claim false.
* GPR 202609 official archive commit:
  `21449bec606bc5a5b1bf58d08ce526dc35d66c94` at
  `2026-09-01T14:27:55Z`; August GPR = `117.9188461303711`, p-1 and origin-cutoff
  tests PASS. It is retained as immutable source evidence; no production row was
  added because persistence is not required to prove the Sep-30 readiness gate.
* Live catch-up workflow/run/artifact:
  `34409095422` / `10126512516`, artifact digest
  `sha256:30c62dad02ef9dcdf622ecea8837648a2e69c11c166b2b98a9991ef4f5d57144`.
* Production observations: one idempotent NY17 row inserted (Sep-09), raising
  `XAU_EOD_TWELVE_NY17` from 52 to 53. `GVZ_CBOE` remained 246 rows; no duplicate
  source row was created.
* Frozen recompute appended governed feature evidence and refreshed the five
  current runtime bindings. Exact feature-row insert counts are not asserted here
  because the workflow log does not expose a reconciled count; status is
  `NOT_PROVEN_COUNT`, not an inferred number.
* Post-write authority counts: `0/0/0/0`. AUTO_SELECTOR and AUTO_ENSEMBLE non-OFF
  counts: `0/0`. No forecast or decision authority was written.

## Tests and disclosed limitation

Source identity, August target reconstruction, BOCPD prefix invariance and
deterministic rerun pass. V1.44 unit tests pass 4/4. FAST, GVZ and Emergency
post-write freshness/lineage checks pass. The generic V1.44 post-write auditor's
`SLOW_STATE_CURRENT_SOURCE_LINEAGE_FRESH` check fails because it compares SLOW's
completed-week clock with the newest daily NY17 row; the role-clock adjudication
is PASS, but the generic audit result is preserved as a disclosed FAIL and was
not silently rewritten.

No leakage or PIT violation was found. No model, threshold, feature, provider,
target identity, selector, ensemble or production authority was changed.

