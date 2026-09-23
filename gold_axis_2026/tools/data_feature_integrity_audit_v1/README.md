# GOLD data/feature integrity audit V1

Research audit only. No DB writes, model changes, runtime promotion or raw-vendor publication.
Canonical authority: manifest v3.00 at 66fe1bac635e6135128d478aab9a6cba74883948.

Use Python 3.11 with numpy 2.1.3, pandas 2.2.3, scipy 1.14.1,
scikit-learn 1.5.2 and psycopg[binary] >=3.2,<4. Set GOLD_AUDIT_WORKDIR
to a private absolute scratch directory. Never commit NEON_DATABASE_URL or raw snapshots.

1. Fetch the exact commit objects named by prepare.py in the authorized sim3 repository.
2. Run `python prepare.py --repository /absolute/sim3 --workdir /absolute/private-audit --mirror`.
   This uses NEON_DATABASE_URL read-only. Alternatively supply raw_YEAR.json from authorized
   SQL connector reads and use --skip-db. Each JSON has [{"bars":[[epoch_seconds,close],...]}].
3. Export GOLD_AUDIT_WORKDIR=/absolute/private-audit.
4. Run run_audit.py, audit_external.py, verify_chronology.py, verify_external_spine.py in this order.
5. Inspect every comparison, not just process exit code. No model or threshold is chosen by this audit.

The frozen external builder needs the 2020/2021 and January2022 mirror files;
the independent formation audit additionally needs 2018/2019. RV=0 dates are excluded
according to frozen source construction. run_audit.py recomputes all retained daily features
independently, then runs pinned expert implementations. verify_chronology.py independently
reconstructs 442 Router selections. audit_external.py refits UP-2 using the newly verified
feature vectors, rather than trusting the frozen ledger inputs.

Stored db_*.json files are read-only metadata/check results from 2026-09-23, not a live DB.
The source cache hash is reproducible using 5000-row pages from newest to oldest, each
page ascending by timestamp: SHA256 of UTF-8 `timestamp_iso_utc|close:.12f\n` per page,
then SHA256 of concatenated page hex digests. Frozen batch1 expected hash is
de35938a49db2d7c8386280319a0ecfe5efa1fbac4a2409b56a5e7bd534a750d.

Tolerance: abs1e-12 + relative1e-9 for derived fields; probability abs1e-9.
Raw bar source conflicts and source/session/vintage gaps are NOT_PROVEN. Never replace
5m closes with 1m closes merely because they differ. No raw or production backfill
was justified by this audit. Recomputed research values are persisted in this branch.
