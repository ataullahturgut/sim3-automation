# Gold Control V1.46 — Prospective Shadow Observation Contract

State: `FROZEN_OBSERVATION_EVALUATION_ONLY_NOT_PRODUCTION_AUTHORITY`

Historical replay/reconstruction rows are excluded from prospective evidence.
Each future shadow record must carry engine/version, source identities, actual
collection/release timestamp, immutable origin timestamp, input fingerprint,
code commit, evidence class `PROSPECTIVE_SHADOW`, and `prospective_claim=true`
only when it was genuinely issued before the outcome.

| Role | Earliest governed issue clock | Fail-closed prerequisite |
|---|---|---|
| H=1 experts | completed prior month-end | every frozen source available by origin |
| MONTHLY_DIRECTION | completed prior months | canonical NY17 prior-month reference |
| FAST | each chronological NY17 observation | exact canonical source observation |
| SLOW | completed week only | all required completed-week observations |
| MACRO_EVENT V2 | governed release timeline | first-print actual and PIT consensus |
| BOCPD | completed-month timeline | exact frozen CORE5 monthly inputs |
| Emergency roles | chronological target-month NY17 | exact canonical NY17 observation |
| GVZ | released official Cboe observation | exact released observation and lineage |

Collection must be append-only and idempotent. Missing, duplicate, conflicting,
late or lineage-invalid inputs produce an explicit blocker; there is no provider
substitution, interpolation, forward-fill, synthetic row or backdating.

Monitoring must verify source freshness, origin monotonicity, engine/version
identity, input and output fingerprints, duplicate/conflict counts, schedule
lateness, PIT/future-information violations and drift. Any failure suppresses the
shadow observation and records the blocker. It never creates a production trade,
position, forecast contract or decision event.

Activation gate: all 12 roles must have proven prospective source availability,
runtime identity, schedule, lineage, deterministic execution and fail-closed
monitoring. Because BOCPD exact 2026-08 input and prospective availability for
all 12 are not proven, the current result is `BLOCKED_DATA` and not
`PROSPECTIVE_SHADOW_READY`.
