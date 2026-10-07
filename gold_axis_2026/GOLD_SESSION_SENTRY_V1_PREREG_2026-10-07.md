# SESSION SENTRY V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07  
**Status:** BINDING BEFORE SESSION RUN

## Role

SENTRY is a causal expert failover/router between two already-governed session experts.

It is not a new raw-feature direction model.

## Experts

### STRUCTURAL_IRIS
Canonical session expert:
`S14_A1_PLUS_1H_FULL`

### PATH_GLOBAL
Canonical session expert:
`PATH_GLOBAL_1H`

Only exact common session rows may be routed.

## State signal

For each matured historical common-row forecast:

- +1 = PATH_GLOBAL correct and STRUCTURAL_IRIS wrong
- -1 = STRUCTURAL_IRIS correct and PATH_GLOBAL wrong
- 0 = both have identical correctness

At each new session origin use only the latest **63 matured paired forecasts from the same partition/window**.

`net_rescue_63 = sum(paired_advantage)`

## Frozen state machine

Initial state:
- STRUCTURAL_IRIS

Switch STRUCTURAL -> PATH when:
- matured paired forecasts >= 42
- and `net_rescue_63 >= +3`

Switch PATH -> STRUCTURAL when:
- `net_rescue_63 <= 0`

Otherwise preserve state.

No threshold search is permitted.

## Session chronology

The router state is independent for each partition/window.

For a candidate row at `start_utc`, only prior common rows with:
`end_utc <= start_utc`
may contribute to paired correctness history.

This prevents current or overlapping session outcomes from entering the switch decision.

## Data / clock authority

Expert probabilities must come from the corrected V5 session project:

- Structural-IRIS: canonical fresh S14 A1+1h PATH lineage
- PATH_GLOBAL: canonical 1h PATH lineage
- V5 session target direction
- exact partition/window identity
- no archived H3 SENTRY/AURORA ledger as model input

## Evaluation

- 2022: warm-up only where common expert forecasts are available
- 2023–2024: development / confirmation
- 2025: frozen transport
- 2026: unopened

## Acceptance

For each session separately, promotion requires:

1. at least one actual state switch by the end of 2024;
2. 2023 and 2024 accuracy each no worse than Structural by more than 1 pp when that year has sufficient common rows;
3. 2023 and 2024 Brier each no worse than Structural by more than 0.003;
4. 2023–2024 combined Balanced Accuracy no worse than Structural by more than 1 pp;
5. minimum class recall >= 30% on combined development.

Only session heads passing this frozen pre-2025 gate may be opened in 2025.

No 2025 result may alter:
- window 63
- minimum matured 42
- enter threshold +3
- exit threshold 0
- expert identities
- 0.50 direction threshold.
