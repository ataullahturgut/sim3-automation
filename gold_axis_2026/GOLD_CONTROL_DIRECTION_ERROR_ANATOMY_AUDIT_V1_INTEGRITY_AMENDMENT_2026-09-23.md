# GOLD CONTROL — DIRECTION ERROR ANATOMY AUDIT V1 INTEGRITY AMENDMENT

**Date:** 2026-09-23  
**Identity:** `DIRECTION_ERROR_ANATOMY_AUDIT_V1_RESEARCH`  
**Timing:** after the first workflow blocked on an integrity assertion; before any result is accepted/frozen.

## Block reason

The first workflow run correctly blocked because the audit code asserted that the field named `close_location` must be numerically identical in the frozen One-Sided UP-2 ledger and the frozen Trajectory-Morphology ledger.

That assertion is invalid.

The two frozen experiments use slightly different path-origin conventions:

- One-Sided UP-2 V1 computes cumulative intraday return from `cumsum(r)`, without explicitly prepending the session-start zero.
- Trajectory Morphology V1 prepends the session-start zero before computing its path range.

Therefore the two fields can differ on days when the explicit start point changes the session range. This is a definition difference, not a data corruption.

## Frozen correction

- Keep the preregistered anatomy feature `close_location` exactly as sourced from the **One-Sided UP-2 frozen ledger**.
- Do **not** substitute the Trajectory-Morphology version.
- Remove only the invalid cross-ledger equality assertion for `close_location`.
- Preserve the exact equality assertions for `downside_share` and `last_quarter_return_norm`, whose definitions are identical across the two frozen ledgers.
- No group, feature, contrast, effect-size threshold, 2025 rule, or statistical calculation changes.

The failed run is non-binding. Only a rerun with this integrity correction may be frozen.
