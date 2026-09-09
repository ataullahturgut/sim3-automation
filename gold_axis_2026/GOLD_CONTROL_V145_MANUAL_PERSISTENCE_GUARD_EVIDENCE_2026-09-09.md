# GOLD CONTROL — V1.45 MANUAL PERSISTENCE GUARD EVIDENCE

**Date:** 2026-09-09  
**Scope:** GitHub Actions production-write authorization hardening only  
**Historical-pilot contract:** unchanged and frozen  
**Production historical backfill:** NONE

## 1. Triggering governance issue

At canonical HEAD `4d2f6882910f8a5c2b98df1dfe701ef130faf5dd`, `.github/workflows/gold-control-live-intraday-recompute-v144.yml` contained a `canonical-catchup` job with condition:

`github.event_name == 'push' && github.ref_name == 'gold-r4-direction-engine'`

That job executed both:

- `twelve_xau_ny17.py --persist --reconcile-days 7`
- `live_intramonth_recompute_v144.py --persist --evidence-mode catchup`

Therefore a canonical-branch push affecting governed workflow paths could attempt production persistence without a separate explicit manual persistence authorization.

The same workflow also allowed the `persist` job to run on `workflow_call`, which did not satisfy the stricter rule that persistence must require explicit `workflow_dispatch persist=true` authorization.

## 2. Implemented guard

Commit:

`412bbb43547460f943ee0b5c6b4665eaef64495c`

Changes:

1. Removed the automatic `canonical-catchup` production-write job.
2. Removed `workflow_call` as a persistence authorization path.
3. Retained push/workflow-call execution only for unit tests and read-only production preflight.
4. Restricted the `persist` job to:

`github.event_name == 'workflow_dispatch' && inputs.persist == true`

5. Added explicit runtime prerequisites for manual persistence:
   - event must be `workflow_dispatch`;
   - `persist` must equal `true`;
   - `NEON_DATABASE_URL` must be present;
   - `TWELVE_DATA_API_KEY` must be present.
6. Preserved the required write order inside the explicitly authorized manual path:
   - canonical NY17 bounded reconciliation with `--persist`;
   - append-only intramonth context persistence;
   - post-write readiness audits;
   - authority-store zero assertion.

## 3. Push-event proof

GitHub Actions run:

`34333469802` — `Gold Control Live Intramonth Recompute V1.44`

Trigger:

`event = push`

Result:

- overall workflow: `SUCCESS`
- `unit-and-dry-run`: `SUCCESS`
- `persist`: `SKIPPED`

Therefore the guard commit itself demonstrated that a canonical push no longer enters the production persistence job.

## 4. Production read-only verification

After the guard commit, a read-only production Neon query returned:

- `XAU_EOD_TWELVE_NY17` observations: `52`
- `monthly_forecast_contracts`: `0`
- `decision_signal_snapshots`: `0`
- `decision_runs`: `0`
- `decision_events`: `0`

The latest NY17 row was for trade date `2026-09-08`, observation timestamp `2026-09-08T21:00:00Z`, with `retrieved_at = 2026-09-09T00:11:05.272Z`. This predates the guard commit (`2026-09-09T09:13:09Z`) and therefore was not produced by the guard-change push.

No historical NY17 or GVZ backfill was written by this change.

## 5. Governance result

`CANONICAL_PUSH_AUTOMATIC_PRODUCTION_PERSISTENCE = DISABLED`

`WORKFLOW_CALL_PRODUCTION_PERSISTENCE = DISABLED`

`MANUAL_WORKFLOW_DISPATCH_PERSIST_TRUE_REQUIRED = TRUE`

`PRODUCTION_HISTORICAL_BACKFILL = NONE`

`AUTO_SELECTOR = OFF`

`AUTO_ENSEMBLE = OFF`

The frozen V1.45 historical-pilot readiness contract and its scoring/evaluation rules are unchanged.