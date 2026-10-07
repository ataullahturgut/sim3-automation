# SESSION DART V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07  
**Status:** BINDING BEFORE SESSION RUN

## Role

DART is a disagreement-aware causal regime-transfer router between two governed session experts:

- STRUCTURAL_IRIS = `S14_A1_PLUS_1H_FULL`
- PATH_GLOBAL = `PATH_GLOBAL_1H`

It is not a raw-feature direction model.

## Information-bearing events

For each exact-common-row matured expert forecast:

- if Structural and Path issue the same direction, the row does not update DART;
- if they disagree:
  - X=1 when PATH_GLOBAL is correct;
  - X=0 when STRUCTURAL_IRIS is correct.

Because expert directions differ, exactly one expert is directionally correct on each disagreement row.

## Bayesian online change-point model

Within the current regime:

`X_t ~ Bernoulli(theta)`

Prior at a new regime:
- Beta(1,1)

Frozen BOCPD settings:
- constant hazard = 1/20 per matured disagreement event
- maximum run length = 120 disagreement events

At each session origin report:
- `q_path = E[theta | matured disagreements]`
- `Pr(theta > 0.5 | data)`
- expected run length
- matured disagreement count.

## Frozen state rule

Initial state:
- STRUCTURAL_IRIS

Before 8 matured disagreement events:
- remain STRUCTURAL_IRIS.

Enter PATH_GLOBAL when:
- matured disagreements >= 8
- `Pr(theta > 0.5) >= 0.90`
- `q_path >= 0.60`

Return STRUCTURAL_IRIS when:
- `Pr(theta > 0.5) <= 0.10`
- `q_path <= 0.40`

Otherwise retain current state.

No threshold or hazard search is permitted.

## Session chronology / anti-leakage

State is independent for every partition/window.

At a session row with `start_utc = T`, only disagreement rows satisfying:
- same partition/window
- prior row
- `end_utc <= T`

may update the detector.

Current or overlapping session outcomes cannot enter state.

## Data authority

Use only corrected session expert probabilities:
- canonical Structural-IRIS session lineage;
- canonical PATH_GLOBAL session lineage;
- exact common V5 session rows.

Do not use archived H3 DART/SENTRY/AURORA prediction ledgers as model input.

## Evaluation

- 2023–2024: development / confirmation
- 2025: frozen transport only for heads passing the pre-2025 gate
- 2026: unopened

## Frozen pre-2025 acceptance gate

For each session:

1. DART 2023 accuracy no worse than Structural by >1 pp, where 2023 has observations.
2. DART 2024 accuracy no worse than Structural by >1 pp.
3. DART 2023 Brier no worse than Structural by >0.003.
4. DART 2024 Brier no worse than Structural by >0.003.
5. 2023–2024 combined DART Balanced Accuracy no worse than Structural by >1 pp.
6. Combined minimum class recall >= 30%.
7. At least one DART state transition by end-2024.

Only heads passing all applicable conditions may be opened in 2025.

No 2025 result may alter:
- hazard
- run-length cap
- entry/exit thresholds
- expert identities
- direction threshold 0.50.
