# GOLD MONTHLY FORECAST — DEV SNAPSHOT V1 FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE EXPORT / PARITY**

## Purpose

Stop repeated Neon public-network transfer during model development while preserving Neon as the authoritative source.

The snapshot is an **execution cache**, not a replacement data authority.

## Scope

Snapshot V1 contains only the data required to reconstruct the frozen VW-MIDAS CURRENT8 development input universe:

- CORE5 Gold monthly XAU/USD series, hard-cut before 2025
- common-date daily rows for Gold, Silver, Platinum, Palladium, hard-cut before 2025
- GPR official PIT vintages for development origins 2022-03..2024-11
- each GPR origin's minimum `available_as_of`
- DB authority invariant counts at export
- source/provenance checks and series identifiers

Explicitly excluded:
- all 2025 modeling rows
- all 2026 modeling rows
- 2025 holdout material
- 2026 reporting material

## Storage

The data payload will be stored as a GitHub Actions artifact, not committed into Git history.

The repository will retain only:
- schema/version definition
- workflow/run ID
- artifact identity
- payload SHA-256 / file SHA-256
- source checks
- parity result

## Origin-safety

The snapshot may contain history spanning multiple DEV origins, but model code must continue to reconstruct each target using only information available at that target's forecast origin.

The existing governed `all_samples_at_origin(..., governed=True)` logic remains authoritative for origin slicing.

## Parity gate

Before the snapshot can replace repeated Neon reads, the frozen CNN-LSTM parent must be replayed **without any DB connection**:

- architecture: CNN-LSTM
- lookback: 6
- width: 32
- dropout: 0.10
- Adam LR: 0.001
- batch: 16
- seeds: 1701, 2903, 4111
- DEV: 2022-04..2024-12

Canonical expected parent:
- DEV SigmaAE: 1528.5698506560245
- direction: 20/33
- relative MAE vs RW: 0.8694936579385805
- yearly SigmaAE:
  - 2022: 440.3790157846795
  - 2023: 501.4196081656596
  - 2024: 586.7712267056854
- yearly direction:
  - 2022: 5/9
  - 2023: 6/12
  - 2024: 9/12
- selected seeds:
  - 1701: 1
  - 2903: 23
  - 4111: 9

Parity tolerances frozen before outcome:
- direction counts: exact
- selected-seed counts: exact
- aggregate SigmaAE absolute difference <= 1e-6
- each yearly SigmaAE absolute difference <= 1e-6
- relative MAE vs RW absolute difference <= 1e-12

If parity fails, snapshot execution is **NOT authorized** for future models until root cause is resolved.

## Scientific / governance requirements

- export connection: READ_ONLY
- exactly one snapshot export job may query Neon
- parity job must not connect to Neon
- payload SHA-256 must verify before load
- hard cutoff < 2025-01-01 for daily/monthly source data
- GPR origin max <= 2024-11
- source checks must show 2025=0 and 2026=0 modeling rows
- no random split
- no 2025 opening
- no 2026 tuning/selection

## Future use

After PASS, subsequent compatible DEV model jobs should download this exact artifact instead of querying Neon.

If a future method requires a source not represented here, create a separately governed Snapshot V2 rather than silently altering V1.
