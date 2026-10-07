# SESSION AURORA V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07  
**Status:** BINDING BEFORE SESSION RUN

## Role

AURORA is an asymmetric hysteresis router between the same two governed session experts:

- STRUCTURAL_IRIS = `S14_A1_PLUS_1H_FULL`
- PATH_GLOBAL = `PATH_GLOBAL_1H`

It combines:
- SENTRY for fast PATH entry;
- DART for slow return to STRUCTURAL.

AURORA introduces no new fitted threshold.

## Fast entry — frozen SENTRY evidence

At each session origin, from exact-common same-window matured expert rows:

- latest 63 matured paired rows;
- minimum matured pairs = 42;
- +1 if PATH correct and Structural wrong;
- -1 if Structural correct and PATH wrong;
- `net_rescue_63 = sum(advantage)`.

When AURORA state is STRUCTURAL:

enter PATH if:
- `matured_pair_n >= 42`
- `net_rescue_63 >= +3`.

The SENTRY exit rule is ignored once AURORA is in PATH state.

## Slow exit — frozen DART evidence

DART is updated only on matured expert-disagreement rows.

Frozen BOCPD:
- Beta(1,1) new-regime prior
- hazard = 1/20 per matured disagreement
- max run length = 120
- minimum matured disagreements = 8

When AURORA state is PATH:

return STRUCTURAL only if:
- `matured_disagreements >= 8`
- `Pr(theta > 0.5) <= 0.10`
- `q_path <= 0.40`.

Otherwise keep PATH.

## Initial state

- STRUCTURAL_IRIS.

State is independent for every partition/window.

## Anti-leakage

For a session origin at `start_utc=T`:

SENTRY evidence may use only exact-common prior rows with:
- same partition/window
- `end_utc <= T`.

DART evidence may update only from expert-disagreement rows satisfying the same maturity condition.

No current or overlapping target outcome may affect the AURORA state.

Archived H3 SENTRY, DART, AURORA or OPAL prediction files are prohibited as session model inputs.

## Evaluation chronology

- 2023–2024: development / confirmation
- 2025: frozen transport only for AURORA heads passing the pre-2025 gate
- 2026: unopened

## Frozen pre-2025 gate

For each session:

1. 2023 AURORA accuracy no worse than Structural by >1 pp, when observations exist.
2. 2024 AURORA accuracy no worse than Structural by >1 pp.
3. 2023 AURORA Brier no worse than Structural by >0.003.
4. 2024 AURORA Brier no worse than Structural by >0.003.
5. 2023–2024 combined AURORA Balanced Accuracy no worse than Structural by >1 pp.
6. combined minimum class recall >= 30%.
7. at least one AURORA state transition by end-2024.

Only heads passing all applicable conditions may open 2025.

No 2025 result may alter:
- SENTRY window 63
- SENTRY minimum 42
- SENTRY enter threshold +3
- DART hazard 1/20
- DART min disagreements 8
- DART exit probability 0.10
- DART exit q_path 0.40
- expert identities
- 0.50 direction threshold.
