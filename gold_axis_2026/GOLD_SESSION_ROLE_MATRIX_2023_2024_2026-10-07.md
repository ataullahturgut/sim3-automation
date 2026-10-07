# GOLD SESSION — 2023–2024 ROLE MATRIX

**Date:** 2026-10-07  
**Status:** IN PROGRESS / DEVELOPMENT-ONLY ROLE FREEZE

Authority:
- `GOLD_SESSION_ROLE_AWARE_MODEL_EVALUATION_AUTHORITY_2026-10-07.md`

## Interpretation

This matrix is built only from 2023–2024 development evidence.

Role profile labels are descriptive:
- `BALANCED`
- `UP_SKEW`
- `DOWN_SKEW`
- `CORRECTION`
- `CALIBRATION`
- `ROUTER_STATE`
- `NON_INCREMENTAL`

A role profile is **not yet a consensus vote**.

Final consensus eligibility additionally requires a development-only incremental/disagreement test so correlated or nested models are not double-counted.

No 2025 outcome is used to assign the role profile in this matrix.

---

## Model-01 — Classical CORE3 Logistic

Source authority:
- `GOLD_SESSION_MODEL01_CLASSICAL_CORE3_IDENTITY_AUTHORITY_2026-10-07.md`

| Session | N | BA | UP recall | DOWN recall | Development profile | Consensus status |
|---|---:|---:|---:|---:|---|---|
| Sobti Asia Afternoon | 358 | 47.91% | 39.56% | 56.25% | DOWN_SKEW / weak overall | PENDING_INCREMENTAL_TEST |
| Sobti Asia Morning | 358 | 53.88% | 57.14% | 50.62% | BALANCED | PENDING_INCREMENTAL_TEST |
| Sobti Europe | 383 | 51.12% | 54.81% | 47.43% | BALANCED / weak | PENDING_INCREMENTAL_TEST |
| Sobti NY/London | 379 | 50.34% | 48.11% | 52.58% | BALANCED / near-neutral | PENDING_INCREMENTAL_TEST |
| Sobti Late-US | 274 | 49.94% | 79.88% | 20.00% | **UP_SKEW** | PENDING_INCREMENTAL_TEST |
| WGC Asia | 376 | 51.05% | 68.98% | 33.12% | UP_SKEW / two-class viable | PENDING_INCREMENTAL_TEST |
| WGC Europe | 382 | 49.59% | 61.68% | 37.50% | UP_SKEW / weak overall | PENDING_INCREMENTAL_TEST |
| WGC US | 346 | 47.55% | 39.41% | 55.68% | DOWN_SKEW / weak overall | PENDING_INCREMENTAL_TEST |

### Model-01 interpretation

- Sobti Asia Morning is the clearest balanced development head.
- Sobti Late-US must remain visible as an UP-oriented specialist signal despite failing the balanced-primary floor.
- WGC Asia is UP-skewed but retains both-class coverage and therefore may contribute either as a weak primary/window head or an UP specialist depending on incremental tests.
- Sobti Asia Afternoon and WGC US contain DOWN-skew evidence but weak overall BA; they are not deleted from the evidence pool.
- No Model-01 session receives an independent consensus vote yet.



---

## Model-02 — Shallow CART family

Source authority:
- `GOLD_SESSION_MODEL02_SHALLOW_CART_VARSEL_DEV_METRICS_2026-10-07.csv`

Duplicate-control cluster:
- `FULL_LEGACY_CART`
- `GOLD_ONLY_CART`
- `SELECTED_CART`

These are alternative representations of the same CART family. They must **not** receive three independent consensus votes.

### FULL_LEGACY_CART development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 473 | 49.04% | 46.61% | 51.48% | BALANCED / near-neutral |
| Sobti Asia Morning | 473 | 49.69% | 54.88% | 44.49% | UP_SKEW / near-neutral |
| Sobti Europe | 503 | 51.93% | 43.77% | 60.08% | DOWN_SKEW |
| Sobti NY/London | 499 | 51.91% | 54.22% | 49.60% | BALANCED |
| Sobti Late-US | 349 | 52.77% | 63.21% | 42.34% | UP_SKEW |
| WGC Asia | 496 | 51.34% | 58.84% | 43.84% | UP_SKEW |
| WGC Europe | 502 | 49.20% | 54.24% | 44.16% | UP_SKEW / weak |
| WGC US | 461 | 50.63% | 45.98% | 55.27% | DOWN_SKEW |

### GOLD_ONLY_CART development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 473 | 48.61% | 40.68% | 56.54% | DOWN_SKEW |
| Sobti Asia Morning | 473 | 49.53% | 53.25% | 45.81% | UP_SKEW / weak |
| Sobti Europe | 503 | 49.47% | 46.42% | 52.52% | DOWN_SKEW / weak |
| Sobti NY/London | 499 | 48.68% | 39.36% | 58.00% | DOWN_SKEW |
| Sobti Late-US | 349 | 47.31% | **69.81%** | **24.82%** | **UP_SKEW** |
| WGC Asia | 496 | 49.21% | 49.10% | 49.32% | BALANCED / near-neutral |
| WGC Europe | 502 | 54.53% | 60.15% | 48.92% | BALANCED / UP_LEAN |
| WGC US | 461 | 51.12% | **33.04%** | **69.20%** | **DOWN_SKEW** |

### SELECTED_CART development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 473 | 49.66% | **37.71%** | **61.60%** | **DOWN_SKEW** |
| Sobti Asia Morning | 473 | 47.08% | 54.07% | 40.09% | UP_SKEW / weak |
| Sobti Europe | 503 | 48.05% | 38.11% | 57.98% | DOWN_SKEW |
| Sobti NY/London | 499 | 53.29% | 45.78% | 60.80% | DOWN_SKEW / balanced viable |
| Sobti Late-US | 349 | 47.64% | 64.62% | 30.66% | UP_SKEW |
| WGC Asia | 496 | 51.12% | 50.18% | 52.05% | BALANCED |
| WGC Europe | 502 | 53.13% | 51.29% | 54.98% | BALANCED |
| WGC US | 461 | 48.90% | 44.64% | 53.16% | DOWN_SKEW / weak |

### Model-02 interpretation

- CART contains useful **directional asymmetry evidence** even though no representation is a universal primary model.
- Late-US contains repeated UP-skew behavior, especially GOLD_ONLY_CART.
- WGC US contains strong DOWN-skew behavior in GOLD_ONLY_CART.
- Sobti Asia Afternoon and several Europe/NY variants contain DOWN-skew signals.
- Because these are one model family, the later incremental test must select or weight **at most one CART representation per session**, rather than allowing correlated duplicate voting.
- Consensus status for all CART rows remains `PENDING_INCREMENTAL_TEST`.
