# GOLD H1 R1 — Weekly Mismatch Autopsy R1

- weeks: **678**
- monfri_exact: **579**
- sunfri_exact: **678**
- sunsat_exact: **678**
- sunday_present: **99**
- resolved_by_adding_sunday: **99**
- unresolved_after_sunfri: **0**
- weekly_close_mismatch_count: **0**
- raw_state_mismatch_count: **0**
- slow_state_mismatch_count: **0**

Interpretation rules:
- If SUN_FRI exact materially exceeds MON_FRI, prior failures were mainly calendar-boundary aggregation artifacts (Sunday ticks), not corrupted weekly close history.
- Tactical Slow uses weekly close vs SMA4 and persistence; therefore close/state mismatch counts are the decision-relevant integrity checks.
- If slow_state_mismatch_count is zero or negligible, open/volume aggregation differences do not invalidate the Tactical close-based signal.
