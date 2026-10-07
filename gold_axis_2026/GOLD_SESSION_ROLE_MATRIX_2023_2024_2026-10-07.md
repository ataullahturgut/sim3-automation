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


---

## Model-03 — NOVA A1 / ARCR family

Sources:
- `GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_METRICS_2023_2024.csv`
- `GOLD_SESSION_MODEL03B_A1_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Duplicate-control cluster:
- canonical `A1_ARCR`
- `SELECTED_A1_ARCR`

These are alternative representations of the same A1 family and may not receive independent full consensus votes.

### Canonical A1/ARCR scored development profile

The raw replay's scored A1 sample is warm-up limited and is effectively concentrated in 2024, so it is lower-confidence for cross-year specialist-role assignment.

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 223 | 47.55% | 43.75% | 51.35% | DOWN_SKEW / weak |
| Sobti Asia Morning | 223 | 53.39% | 56.25% | 50.53% | BALANCED |
| Sobti Europe | 248 | 47.37% | 52.14% | 42.59% | UP_SKEW / weak |
| Sobti NY/London | 244 | 47.80% | 50.78% | 44.83% | UP_SKEW / weak |
| Sobti Late-US | 139 | 51.28% | 73.75% | 28.81% | UP_SKEW |
| WGC Asia | 241 | 50.60% | 66.91% | 34.29% | UP_SKEW |
| WGC Europe | 247 | 50.75% | 60.58% | 40.91% | UP_SKEW |
| WGC US | 211 | 46.44% | 46.49% | 46.39% | BALANCED / weak |

### Selected A1/ARCR development profile on exact common rows

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 168 | 52.39% | 52.22% | 52.56% | BALANCED |
| Sobti Asia Morning | 158 | 53.28% | 48.35% | 58.21% | DOWN_LEAN / balanced |
| Sobti Europe | 191 | 46.98% | **72.12%** | **21.84%** | **UP_SKEW** |
| Sobti NY/London | 194 | 50.10% | 45.45% | 54.74% | DOWN_LEAN / near-neutral |
| Sobti Late-US | 40 | 50.00% | 65.00% | 35.00% | UP_SKEW / low N |
| WGC Asia | 23 | 52.08% | 66.67% | 37.50% | UP_SKEW / very low N |
| WGC Europe | 192 | 49.61% | 67.89% | 31.33% | UP_SKEW |
| WGC US | 150 | 47.49% | **35.53%** | **59.46%** | **DOWN_SKEW** |

### Model-03 interpretation

- Canonical A1 has useful balanced evidence in Sobti Asia Morning but its scored development history is warm-up constrained.
- The selected representation reveals strong one-sided signatures, especially Sobti Europe UP-skew and WGC US DOWN-skew.
- Those signatures remain specialist evidence even though selected-A1 did not transport broadly as a primary model.
- Because canonical and selected A1 share the same structural lineage, later consensus logic must treat them as one dependency cluster.
- Consensus status remains `PENDING_INCREMENTAL_TEST`.


---

## Model-04 — IRIS HOURLY_ONLY / PATH_GLOBAL family

Sources:
- `GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_METRICS_2023_2024.csv`
- `GOLD_SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Duplicate-control cluster:
- canonical `PATH_GLOBAL_1H`
- `SELECTED_PATH_GLOBAL`

These are alternative PATH representations and must not receive independent full votes.

### Canonical PATH_GLOBAL development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 298 | 45.86% | 34.87% | 56.85% | DOWN_SKEW / weak |
| Sobti Asia Morning | 298 | 47.88% | 45.40% | 50.37% | BALANCED / weak |
| Sobti Europe | 323 | 50.36% | 55.75% | 44.97% | UP_LEAN / near-neutral |
| Sobti NY/London | 319 | 52.61% | 55.21% | 50.00% | BALANCED |
| Sobti Late-US | 214 | 48.04% | **84.96%** | **11.11%** | **UP_SKEW** |
| WGC Asia | 316 | 43.85% | **69.78%** | **17.91%** | **UP_SKEW** |
| WGC Europe | 322 | 45.08% | **65.17%** | **25.00%** | **UP_SKEW** |
| WGC US | 286 | 49.61% | 44.74% | 54.48% | DOWN_SKEW / near-neutral |

### Selected PATH_GLOBAL development profile on exact common rows

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 239 | 50.83% | 54.33% | 47.32% | BALANCED / UP_LEAN |
| Sobti Asia Morning | 232 | 49.24% | 35.11% | 63.37% | DOWN_SKEW |
| Sobti Europe | 260 | 46.56% | **78.47%** | **14.66%** | **UP_SKEW** |
| Sobti NY/London | 262 | 49.58% | 48.80% | 50.36% | BALANCED / near-neutral |
| Sobti Late-US | 110 | 52.49% | **75.81%** | **29.17%** | **UP_SKEW** |
| WGC Asia | 92 | 52.81% | 65.00% | 40.63% | UP_SKEW / two-class viable |
| WGC Europe | 262 | 48.49% | **67.79%** | **29.20%** | **UP_SKEW** |
| WGC US | 219 | 51.53% | 35.00% | **68.07%** | **DOWN_SKEW** |

### Model-04 interpretation

- PATH_GLOBAL is one of the clearest sources of one-sided specialist structure in development.
- Late-US, WGC Asia and WGC Europe show persistent UP-skew in canonical PATH.
- WGC US shows a repeated DOWN-skew profile, especially after feature selection.
- Sobti Europe selected PATH is an extreme UP-skew representation and must not be discarded merely because its DOWN recall fails the balanced-primary floor.
- The selected/canonical pair remains one PATH dependency cluster; later consensus can use at most one independent PATH vote per session unless an explicit decorrelation rule is proven.
- Consensus status remains `PENDING_INCREMENTAL_TEST`.


---

## Model-05 — STRUCTURAL_IRIS / A1_PLUS_PATH family

Sources:
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Dependency cluster:
- canonical `S14_A1_PLUS_1H_FULL`
- selected 1h Structural-IRIS
- historical S1.4 15m/full/selected siblings

These are related A1+PATH representations and must be decorrelated before any consensus vote.

### Canonical 1h Structural-IRIS development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 190 | 51.02% | 51.46% | 50.57% | BALANCED |
| Sobti Asia Morning | 183 | 49.91% | 55.66% | 44.16% | UP_LEAN / near-neutral |
| Sobti Europe | 213 | 48.17% | **69.75%** | **26.60%** | **UP_SKEW** |
| Sobti NY/London | 215 | 53.26% | 46.15% | 60.36% | DOWN_LEAN / balanced |
| Sobti Late-US | 89 | 50.05% | 70.83% | 29.27% | UP_SKEW / one-year scored |
| WGC Asia | 102 | 47.36% | **82.61%** | **12.12%** | **UP_SKEW** |
| WGC Europe | 210 | 52.28% | 68.60% | 35.96% | UP_SKEW / two-class viable |
| WGC US | 177 | 50.28% | **30.23%** | **70.33%** | **DOWN_SKEW** |

### Selected 1h Structural-IRIS development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 190 | 52.47% | 54.37% | 50.57% | BALANCED |
| Sobti Asia Morning | 183 | 44.54% | 56.60% | 32.47% | UP_SKEW / weak |
| Sobti Europe | 213 | 48.65% | **78.15%** | **19.15%** | **UP_SKEW** |
| Sobti NY/London | 215 | 52.75% | 44.23% | 61.26% | DOWN_SKEW / balanced viable |
| Sobti Late-US | 89 | 47.61% | 70.83% | 24.39% | UP_SKEW |
| WGC Asia | 102 | 45.78% | **85.51%** | **6.06%** | **UP_SKEW** |
| WGC Europe | 210 | 52.36% | 74.38% | 30.34% | UP_SKEW / two-class edge borderline |
| WGC US | 177 | 52.42% | **27.91%** | **76.92%** | **DOWN_SKEW** |

### Model-05 interpretation

- Structural-IRIS contains some of the strongest one-sided development profiles in the project.
- WGC Asia and Sobti Europe are strong UP-skew examples; WGC US is a strong DOWN-skew example.
- The 30% floor continues to reject the extreme rows as stand-alone balanced engines, but it no longer removes them from specialist evidence.
- The 15m S1.4 siblings show similar one-sided behavior and belong to the same dependency cluster; they cannot be counted as independent votes without an incremental/disagreement test.
- Consensus status remains `PENDING_INCREMENTAL_TEST`.


---

## Model-06 — SAGE SESSION_ONLY family

Sources:
- `GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_METRICS_2026-10-07.csv`
- `GOLD_SESSION_MODEL06B_SAGE_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Duplicate-control cluster:
- canonical `S15_SESSION_ONLY`
- selected SAGE-only representation

### Canonical SAGE SESSION_ONLY development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 279 | 50.03% | 44.83% | 55.22% | BALANCED / DOWN_LEAN |
| Sobti Asia Morning | 272 | 44.95% | 37.93% | 51.97% | DOWN_SKEW / weak |
| Sobti Europe | 295 | 48.11% | **78.66%** | **17.56%** | **UP_SKEW** |
| Sobti NY/London | 297 | 51.67% | 44.14% | 59.21% | DOWN_SKEW |
| Sobti Late-US | 170 | 44.29% | **70.00%** | **18.57%** | **UP_SKEW** |
| WGC Asia | 152 | 56.21% | 67.33% | 45.10% | BALANCED / UP_LEAN |
| WGC Europe | 297 | 46.23% | **76.19%** | **16.28%** | **UP_SKEW** |
| WGC US | 264 | 45.65% | **27.35%** | **63.95%** | **DOWN_SKEW** |

### Selected SAGE-only development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 279 | 49.88% | 48.28% | 51.49% | BALANCED / near-neutral |
| Sobti Asia Morning | 272 | 44.01% | 34.48% | 53.54% | DOWN_SKEW / weak |
| Sobti Europe | 295 | 47.88% | **80.49%** | **15.27%** | **UP_SKEW** |
| Sobti NY/London | 297 | 49.21% | 37.24% | 61.18% | DOWN_SKEW |
| Sobti Late-US | 170 | 50.50% | **91.00%** | **10.00%** | **EXTREME_UP_SKEW** |
| WGC Asia | 152 | 49.83% | 66.34% | 33.33% | UP_SKEW |
| WGC Europe | 297 | 46.08% | **79.76%** | **12.40%** | **EXTREME_UP_SKEW** |
| WGC US | 264 | 45.28% | **17.09%** | **73.47%** | **EXTREME_DOWN_SKEW** |

### Model-06 interpretation

- SAGE SESSION_ONLY is not a strong balanced model family, but it contains pronounced session-direction asymmetry.
- Europe and Late-US provide strong UP-skew evidence; WGC US provides strong DOWN-skew evidence.
- The selected SAGE representation amplifies these one-sided signatures rather than producing a robust balanced engine.
- Canonical and selected SAGE-only variants are one dependency cluster and may not be counted as independent votes.
- Consensus status remains `PENDING_INCREMENTAL_TEST`.


---

## Model-07 — SAGE PATH_SESSION family

Source:
- `GOLD_SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Dependency cluster:
- canonical PATH_SESSION
- selected PATH_SESSION
- matched PATH comparators

### Canonical PATH_SESSION

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 279 | 49.11% | 48.97% | 49.25% | BALANCED / near-neutral |
| Sobti Asia Morning | 272 | 49.88% | 46.21% | 53.54% | DOWN_LEAN / near-neutral |
| Sobti Europe | 295 | 44.08% | 53.05% | 35.11% | UP_SKEW / weak |
| Sobti NY/London | 297 | 52.21% | 53.10% | 51.32% | BALANCED |
| Sobti Late-US | 170 | 48.36% | 61.00% | 35.71% | UP_SKEW |
| WGC Asia | 152 | 54.72% | 62.38% | 47.06% | BALANCED / UP_LEAN |
| WGC Europe | 297 | 47.38% | 58.33% | 36.43% | UP_SKEW |
| WGC US | 264 | 47.46% | 38.46% | 56.46% | DOWN_SKEW |

### Selected PATH_SESSION

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 279 | 54.88% | 53.79% | 55.97% | BALANCED |
| Sobti Asia Morning | 272 | 51.54% | 39.31% | 63.78% | DOWN_SKEW |
| Sobti Europe | 295 | 49.49% | 67.68% | 31.30% | UP_SKEW |
| Sobti NY/London | 297 | 53.57% | 55.17% | 51.97% | BALANCED |
| Sobti Late-US | 170 | 48.00% | 66.00% | 30.00% | UP_SKEW |
| WGC Asia | 152 | 55.72% | 66.34% | 45.10% | BALANCED / UP_LEAN |
| WGC Europe | 297 | 54.11% | 70.24% | 37.98% | UP_SKEW / two-class viable |
| WGC US | 264 | 50.54% | 45.30% | 55.78% | DOWN_LEAN / balanced |

Interpretation:
- Selected PATH_SESSION contains balanced candidates in Asia Afternoon, NY/London and WGC Asia.
- Europe/Late-US contain UP-specialist structure; WGC US contains DOWN-oriented structure.
- PATH_SESSION remains nested on PATH/SAGE inputs, so incremental-value testing is mandatory before voting.

---

## Model-08 — SAGE A1_SESSION family

Source:
- `GOLD_SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Dependency cluster:
- canonical A1_SESSION
- selected A1_SESSION
- direct A1 comparator

### Canonical A1_SESSION

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 383 | 50.00% | 43.08% | 56.91% | DOWN_SKEW |
| Sobti Asia Morning | 383 | 46.11% | 47.34% | 44.89% | BALANCED / weak |
| Sobti Europe | 418 | 55.13% | 63.11% | 47.15% | BALANCED / UP_LEAN |
| Sobti NY/London | 414 | 46.64% | 47.26% | 46.01% | BALANCED / weak |
| Sobti Late-US | 259 | 50.27% | **84.38%** | **16.16%** | **UP_SKEW** |
| WGC Asia | 416 | 48.99% | 67.38% | 30.60% | UP_SKEW |
| WGC Europe | 417 | 52.33% | 64.66% | 40.00% | BALANCED / UP_LEAN |
| WGC US | 371 | 52.48% | 40.56% | 64.40% | DOWN_SKEW / two-class viable |

### Selected A1_SESSION

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 383 | 52.09% | 45.13% | 59.04% | DOWN_SKEW / balanced |
| Sobti Asia Morning | 383 | 49.17% | 44.93% | 53.41% | DOWN_LEAN |
| Sobti Europe | 418 | 55.95% | 65.78% | 46.11% | BALANCED / UP_LEAN |
| Sobti NY/London | 414 | 46.43% | 48.26% | 44.60% | BALANCED / weak |
| Sobti Late-US | 259 | 51.06% | **90.00%** | **12.12%** | **EXTREME_UP_SKEW** |
| WGC Asia | 416 | 51.22% | 69.10% | 33.33% | UP_SKEW |
| WGC Europe | 417 | 54.86% | **70.26%** | 39.46% | UP_SKEW / two-class viable |
| WGC US | 371 | 52.18% | 39.44% | **64.92%** | DOWN_SKEW / two-class viable |

Interpretation:
- Late-US is a very strong UP-skew signal family.
- WGC US is a persistent DOWN-oriented candidate.
- Europe has a relatively balanced but UP-leaning profile.
- A1_SESSION is nested on A1 and SAGE; duplicate control is mandatory.

---

## Model-09 — SAGE A1_PATH_SESSION family

Source:
- `GOLD_SESSION_MODEL09B_SAGE_A1_PATH_SESSION_FEATURE_SELECTION_DEV_METRICS_2026-10-07.csv`

Dependency cluster:
- selected A1_PATH_SESSION
- exact matched A1+PATH comparator

### Selected A1_PATH_SESSION development profile

| Session | N | BA | UP recall | DOWN recall | Development profile |
|---|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 191 | 56.14% | 54.81% | 57.47% | BALANCED |
| Sobti Asia Morning | 184 | 49.19% | 50.94% | 47.44% | BALANCED / near-neutral |
| Sobti Europe | 213 | 45.09% | 68.91% | 21.28% | UP_SKEW |
| Sobti NY/London | 215 | **56.41%** | 46.15% | **66.67%** | BALANCED / DOWN_LEAN |
| Sobti Late-US | 89 | 54.40% | **77.08%** | 31.71% | UP_SKEW / two-class viable |
| WGC Asia | 102 | 51.91% | **82.61%** | 21.21% | UP_SKEW |
| WGC Europe | 215 | 51.79% | **75.00%** | 28.57% | UP_SKEW |
| WGC US | 177 | **59.94%** | 41.86% | **78.02%** | **DOWN_SKEW / strong two-class candidate** |

### Model-09 interpretation

- Model-09 contains some of the strongest development-only specialist evidence:
  - Late-US, WGC Asia and WGC Europe on the UP side;
  - WGC US on the DOWN side.
- WGC US is especially important because DOWN recall is high while UP recall remains above 40%, producing BA 59.94%.
- Sobti NY/London is a balanced/down-leaning candidate rather than merely a generic weak model.
- Model-09 is nested on A1 + PATH + SAGE and must be tested for incremental value against its exact matched A1+PATH comparator before receiving consensus weight.
- Consensus status remains `PENDING_INCREMENTAL_TEST`.


---

# Specialist / Router Families

## RIFT — reversal/correction specialist

Authority:
- `GOLD_SESSION_RIFT_FINAL_AUTHORITY_2026-10-07.md`

Role profile:
- `CORRECTION_REVERSAL_SPECIALIST`

Development evidence:
- the only pre-2025 eligible correction window was Sobti Asia Afternoon;
- eligibility existed against multiple upstream baselines;
- therefore RIFT had a genuine development-period correction hypothesis.

Role-aware interpretation:
- RIFT is **not** evaluated as a stand-alone balanced direction model;
- its relevant measures are override count, rescue, break, net rescue and before/after class performance;
- frozen 2025 transport failed to preserve the correction benefit, so RIFT is currently `TRANSPORT_FAILED_CORRECTION`;
- it remains negative correction evidence, not an independent consensus direction vote.

Consensus status:
- `NO_DIRECTION_VOTE`
- `CORRECTION_EVIDENCE_ONLY`

---

## VEGA — GVZ / IV-gap reversal specialist

Authority:
- `GOLD_SESSION_VEGA_FINAL_AUTHORITY_2026-10-07.md`

Role profile:
- `CORRECTION_REVERSAL_SPECIALIST`

Development evidence:
- WGC US + PATH_GLOBAL was the sole canonical pre-2025 eligible pair;
- combined development BA improved 46.28% -> 46.88%;
- one override produced one rescue and no break.

Role-aware interpretation:
- VEGA is not a primary direction engine;
- its development hypothesis was a sparse correction mechanism;
- frozen 2025 produced zero overrides, so it contributed no operational correction information in transport.

Consensus status:
- `NO_DIRECTION_VOTE`
- `NON_INCREMENTAL_CORRECTION_EVIDENCE`

---

## SENTRY — fast-entry router evidence

Authority:
- `GOLD_SESSION_SENTRY_V1_FINAL_AUTHORITY_2026-10-07.md`

Role profile:
- `ROUTER_STATE_EVIDENCE`

Development profiles of interest:
- Sobti Europe was the only head passing the original router gate;
- SENTRY changed state based on the frozen 63-pair net-rescue rule.

Role-aware interpretation:
- SENTRY should not be treated as another independent Structural/PATH direction vote;
- when it selects PATH, its directional output is mechanically inherited from PATH;
- its useful information is the **state transition / net-rescue context**.

Consensus status:
- `NO_INDEPENDENT_DIRECTION_VOTE`
- `ROUTER_STATE_CANDIDATE`

---

## DART — disagreement posterior / slow-exit evidence

Authority:
- `GOLD_SESSION_DART_V1_FINAL_AUTHORITY_2026-10-07.md`

Role profile:
- `ROUTER_STATE_EVIDENCE`

Development evidence:
- only Sobti NY/London produced actual state transitions;
- the detector entered PATH in 2023 and returned Structural in 2024 using the frozen disagreement posterior.

Role-aware interpretation:
- DART is not a third direction expert;
- its information is the posterior state:
  - q_path
  - Pr(PATH superior)
  - disagreement count
  - regime transition timing.

Consensus status:
- `NO_INDEPENDENT_DIRECTION_VOTE`
- `ROUTER_STATE_CANDIDATE`

---

## AURORA — hysteresis router

Authority:
- `GOLD_SESSION_AURORA_V1_FINAL_AUTHORITY_2026-10-07.md`

Role profile:
- `ROUTER_STATE_EVIDENCE`

Development evidence:
- Sobti Asia Morning and Sobti Europe passed the original AURORA pre-2025 gate.

Role-aware interpretation:
- AURORA combines SENTRY fast-entry with DART slow-exit;
- when AURORA simply remains in PATH or Structural, its direction is mechanically identical to that selected expert;
- therefore AURORA must not receive a second full direction vote in addition to the expert it selected;
- its useful incremental signal is the **router state / switch decision**, not duplicate direction.

Consensus status:
- `NO_DUPLICATE_DIRECTION_VOTE`
- `ROUTER_STATE_CANDIDATE`

---

## OPAL — corrected-PIT COT reversal specialist

Authority:
- `GOLD_SESSION_OPAL_V1_FINAL_AUTHORITY_2026-10-07.md`

Role profile:
- `CORRECTION_REVERSAL_SPECIALIST`

Development evidence:
- Sobti Asia Morning:
  - AURORA BA 56.08% -> OPAL BA 58.73%
  - UP recall 60.78%
  - DOWN recall 56.67%
  - overrides 2
  - net rescue +2

- WGC Europe:
  - AURORA BA 45.24% -> OPAL BA 47.93%
  - UP recall 64.91%
  - DOWN recall 30.95%
  - overrides 6
  - net rescue +2

Role-aware interpretation:
- OPAL earns no generic always-on direction vote;
- it contributes only when its frozen reversal intervention condition is active;
- its correct consensus treatment is a conditional correction layer.

Consensus status:
- `CONDITIONAL_CORRECTION_CANDIDATE`

---

# Phase-1 role-freeze conclusion

The descriptive 2023–2024 role matrix is now complete for the currently completed session model families.

The matrix deliberately preserves asymmetric signals that the old binary primary gate hid.

Important examples:
- strong UP-skew: PATH, Structural-IRIS, SAGE, A1_SESSION, A1_PATH_SESSION in several Europe/Asia/Late-US heads;
- strong DOWN-skew: CART/WGC-US, Structural/WGC-US, SAGE/WGC-US, Model-09/WGC-US;
- balanced/window-specific candidates: CORE3 Sobti Asia Morning, selected PATH_SESSION and Model-09 heads, among others;
- correction specialists: RIFT, VEGA, OPAL;
- router evidence: SENTRY, DART, AURORA.

## What is frozen now

Frozen:
- model identity;
- session clock;
- 2023–2024 role profile;
- dependency/duplicate clusters;
- distinction between direction expert, correction specialist and router state.

Not yet frozen:
- final consensus membership;
- consensus weights;
- specialist override hierarchy.

Those require a **development-only incremental/disagreement audit**.

## Next binding step

Before HELIOS or final consensus:

1. for each session separately, compare candidates only on common 2023–2024 rows;
2. measure when each UP/DOWN specialist disagrees with the best balanced base;
3. compute:
   - disagreement N;
   - specialist precision on disagreement;
   - rescue count;
   - break count;
   - net rescue;
   - class-specific incremental recall;
   - correlation / duplicate exposure;
4. choose at most one representative from strongly nested clusters unless incremental value is proven;
5. freeze the role-aware candidate set;
6. only then continue HELIOS and later final consensus.

2025 is not used to choose those memberships.
