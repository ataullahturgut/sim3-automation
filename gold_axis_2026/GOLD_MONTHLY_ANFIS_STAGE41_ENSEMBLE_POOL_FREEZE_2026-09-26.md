# GOLD MONTHLY FORECAST — ANFIS STAGE 4.1 ENSEMBLE COMPONENT POOL FREEZE

Date: 2026-09-26
Status: COMPLETE / POOLS FROZEN BEFORE ENSEMBLE EVALUATION

## 1. Authority
- DEV selection authority only: 2022-04..2024-12, n=33.
- 2025/2026 excluded from pool selection.
- Original successful prediction artifacts only.
- No model retraining.
- No ensemble result was computed before pool freeze.
- Random split: none.
- Target-month leakage: none.

## 2. Eligible role candidates

| Model | Role | DEV SumAE | Direction | Relative MAE vs RW | Scientific gate |
|---|---|---:|---:|---:|---|
| ChHHO-ANFIS | current price leader / Stage3C literature-specific champion | 1413.0298 | 23/33 | 0.8038 | PASS |
| MFO-ANFIS | broad-screen price parent | 1630.3325 | 20/33 | 0.9274 | PASS |
| HHO-ANFIS | broad-screen direction/balance parent | 1646.1336 | 23/33 | 0.9364 | PASS |
| Vanilla ANFIS | architecture anchor | 1852.0465 | 21/33 | 1.0535 | PASS |
| MPA-CPA ANFIS | only valid Stage3 optimizer-hybrid representative | 1918.5637 | 18/33 | 1.0913 | PASS |

Rejected / ineligible:
- scientific-gate failures from broad/refinement stages;
- MVO-ANFIS (valid but rejected on DEV, no unique frozen role);
- other valid but dominated broad-screen models without a distinct frozen role.

## 3. DEV signed forecast-error correlation

| | ChHHO | MFO | HHO | Vanilla | MPA-CPA |
|---|---:|---:|---:|---:|---:|
| ChHHO | 1.000 | 0.826 | 0.703 | 0.800 | 0.628 |
| MFO | 0.826 | 1.000 | 0.694 | 0.648 | 0.796 |
| HHO | 0.703 | 0.694 | 1.000 | 0.694 | 0.456 |
| Vanilla | 0.800 | 0.648 | 0.694 | 1.000 | 0.452 |
| MPA-CPA | 0.628 | 0.796 | 0.456 | 0.452 | 1.000 |

Interpretation:
- ChHHO and MFO are the most redundant price-error pair.
- MPA-CPA is weak on aggregate error but supplies structurally different Stage3 hybrid behavior and relatively low correlation with HHO/Vanilla.
- HHO preserves the strongest broad-screen direction role and is materially less correlated with ChHHO than MFO.

## 4. Direction complementarity versus ChHHO

| Model | Direction disagreements vs ChHHO | Rescues ChHHO misses | Loses ChHHO hits |
|---|---:|---:|---:|
| HHO | 8 | 4 | 4 |
| Vanilla | 10 | 4 | 6 |
| MFO | 9 | 3 | 6 |
| MPA-CPA | 9 | 2 | 7 |

HHO is the cleanest directional complement among eligible non-ChHHO models: its disagreements are symmetric in rescue/loss count, while the other models lose more ChHHO hits than they rescue.

## 5. Frozen ensemble pools

### FULL5 ANFIS
Role-complete pool:
1. Vanilla ANFIS — architecture anchor
2. ChHHO-ANFIS — price leader
3. MFO-ANFIS — broad-screen price parent
4. HHO-ANFIS — direction/balance parent
5. MPA-CPA ANFIS — Stage3 optimizer-hybrid representative

Rationale:
- preserves one representative from every frozen ANFIS role;
- pool fixed before any ensemble performance evaluation;
- intentionally allows redundancy diagnostics later without post-hoc subset promotion.

### REDUCED4 ANFIS
Predeclared role-diverse pool:
1. Vanilla ANFIS — anchor
2. ChHHO-ANFIS — price leader
3. HHO-ANFIS — direction/balance parent
4. MPA-CPA ANFIS — hybrid/refinement representative

MFO is omitted only from the reduced pool because:
- it duplicates the price-parent role already represented by stronger ChHHO;
- ChHHO–MFO signed-error correlation is the highest among the principal accepted parent pairings (~0.826);
- exclusion was decided before observing any ensemble result.

## 6. Next authorized step
Stage 4.2 — ensemble baselines on both frozen pools:
- simple average;
- median ensemble;
- expanding-prequential inverse-prior-MAE weighting;
- no optimized simplex yet.

Only after 4.2 results are reported may Stage 4.3 learned/simplex weights begin.

## 7. Control and compliance
- Pool frozen before ensemble evaluation: PASS.
- 2025/2026 excluded from pool selection: PASS.
- Prediction-level artifact audit: PASS.
- Scientific-gate rejected models excluded: PASS.
- Arbitrary subset search: NONE.
- Stage 4.1: COMPLETE.
