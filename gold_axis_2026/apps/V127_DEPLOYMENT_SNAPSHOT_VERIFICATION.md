# Gold Control v1.27 Deployment Snapshot Verification

This file is a no-runtime-effect release verification trigger.

Required exact-head acceptance:

- manifest v1.27 and `FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1`;
- committed production display snapshot exactly equals a fresh read-only Neon export;
- snapshot fingerprint and 12-runtime / 7-context / 7-link integrity gates pass;
- browser with `NEON_DATABASE_URL` deliberately absent visibly renders persisted Monthly Direction, FAST, SLOW and GVZ context from the validated production snapshot;
- browser with production Neon available still passes the canonical 390x844 mobile QA;
- selector, ensemble and position-mapping locks remain closed.
