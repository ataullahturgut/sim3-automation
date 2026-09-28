# GOLD MONTHLY FORECAST — DEV SNAPSHOT V1 AUTHORIZATION

Date: 2026-09-28
Status: **AUTHORIZED FOR COMPATIBLE DEV MODEL EXECUTION**

## Purpose

Replace repeated Neon reads during model development with one governed, hash-verified DEV execution cache while retaining Neon as the authoritative source.

Freeze:
- `gold_axis_2026/GOLD_MONTHLY_DEV_SNAPSHOT_V1_FREEZE_2026-09-28.md`
- freeze commit `e5750d8e338e6ccafe3dfea3b5dbdf99a46caf89`

Snapshot tooling:
- `gold_axis_2026/tools/gold_monthly_dev_snapshot_v1.py`
- `gold_axis_2026/tools/gold_monthly_dev_snapshot_parity_v1.py`

Workflow:
- `.github/workflows/gold-monthly-dev-snapshot-v1.yml`
- workflow commit `be98365d25e2e81b0f70fb724940e09d0191eb6c`
- run id `36456042954`

## Snapshot identity

Snapshot artifact:
- artifact id: `10985453248`
- artifact name: `gold-monthly-dev-snapshot-v1-be98365d25e2e81b0f70fb724940e09d0191eb6c`
- artifact size: 75,668 bytes
- retention requested: 90 days
- expired at authorization: NO

Parity artifact:
- artifact id: `10986965324`
- artifact name: `gold-monthly-dev-snapshot-v1-parity-be98365d25e2e81b0f70fb724940e09d0191eb6c`
- artifact size: 2,205 bytes
- expired at authorization: NO

Cryptographic identity:
- payload SHA-256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`
- snapshot file SHA-256: `c771c9ca9ecb85aac808d4d976649e920783545803dcecc6183add2c9981037b`

Schema:
- `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`

## Export source checks

One READ_ONLY Neon export produced:
- Gold monthly observations: 371
- Gold monthly range: 1994-02..2024-12
- common daily metal rows: 3,787
- common daily range: 2010-01-04..2024-12-31
- monthly metal coverage: 180 months for each of Gold / Silver / Platinum / Palladium
- GPR PIT origin vintages: 33
- GPR origin range: 2022-03..2024-11
- missing required GPR origins: NONE
- late required GPR origins: NONE
- missing required GPR lag months: NONE
- 2025 modeling rows loaded: 0
- 2026 modeling rows loaded: 0

Export gate:
- READ_ONLY: PASS
- authority invariants unchanged: PASS
- daily max before 2025: PASS
- Gold max <= DEV end: PASS
- GPR origin max <= 2024-11: PASS
- GPR PIT completeness: PASS

## Offline parity result

Parity job had no `NEON_DATABASE_URL` and used only the downloaded snapshot artifact.

Frozen CNN-LSTM parent:
- lookback 6
- width 32
- dropout 0.10
- Adam LR 0.001
- batch 16
- seeds 1701 / 2903 / 4111

Canonical vs offline snapshot replay:
- DEV SigmaAE: `1528.5698506560245` vs `1528.5698506560245`
- absolute difference: **0.0**
- direction: `20/33` vs `20/33`
- relative MAE vs RW: `0.8694936579385805` vs `0.8694936579385805`
- absolute difference: **0.0**
- 2022 SigmaAE difference: **0.0**
- 2023 SigmaAE difference: **0.0**
- 2024 SigmaAE difference: **0.0**
- yearly direction counts: exact
- selected seed counts: exact
  - 1701: 1
  - 2903: 23
  - 4111: 9

All frozen parity checks: **PASS**.

## Authorization decision

Snapshot V1 is authorized as the execution source for future **compatible DEV-only models** using this same data universe.

Future compatible model jobs should:
1. download artifact from run `36456042954`,
2. verify payload SHA-256,
3. load via `gold_monthly_dev_snapshot_v1.load_snapshot()`,
4. preserve governed origin slicing,
5. avoid Neon queries during model fitting/evaluation.

Neon remains the authoritative source. Snapshot V1 is only an immutable execution cache.

If a future model requires a data series not contained in V1:
- do not silently query Neon from every model job;
- define and freeze Snapshot V2;
- perform one READ_ONLY export;
- run parity/data-integrity gates before authorization.

If the artifact expires, re-export under the same governed schema and rerun parity before continued use.

## Model-roadmap consequence

Stage 1D has already triggered the pre-frozen micro-tuning stop rule.

Next compatible structural models can therefore run from Snapshot V1:
1. BiLSTM
2. CNN-BiLSTM

No Stage 1E batch sweep or Stage 1F kernel micro-sweep is authorized.

## Kontrol ve Uyum Özeti

- Neon queried for snapshot export: exactly one export job.
- Snapshot verification: PASS.
- Offline parity used Neon: NO.
- Offline parity: PASS with zero aggregate/yearly SigmaAE difference.
- Random split: NONE.
- 2025 opened: NO.
- 2026 used: NO.
- DB writes: NONE / READ_ONLY.
- Snapshot role: EXECUTION CACHE ONLY.
- Neon remains authority: YES.
- Compatible future DEV runs may use snapshot without DB reads: YES.
