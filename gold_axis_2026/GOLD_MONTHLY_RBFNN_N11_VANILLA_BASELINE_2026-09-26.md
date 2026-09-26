# GOLD MONTHLY FORECAST — N1.1 VANILLA RBFNN BASELINE

Date: 2026-09-26
Status: COMPLETE / SCIENTIFIC_GATE=PASS

## Authority
Canonical references:
- Moody & Darken (1989), locally tuned processing units / RBF networks.
- Classical RBF formulation: nonlinear localized Gaussian hidden basis + linear supervised output fit.

Project contract:
- Target: H=1 next-calendar-month average XAU/USD price.
- Inputs: unchanged governed 8-feature VW-MIDAS contract.
- Outputs: four metal returns jointly; Gold price primary.
- DEV selection authority: 2022-04..2024-12, n=33.
- 2025: locked retrospective transport only.
- 2026 Jan-Jul: retrospective stress only.
- Random split: none.
- Target-month leakage: none.
- DB: READ_ONLY.

## Canonical vanilla RBFNN
- Inputs: 8.
- Gaussian RBF centers: 8.
- Center learning: deterministic k-means on all pre-target training rows only.
- KMeans n_init: 20.
- Widths: per-cluster RMS Euclidean distance to its center.
- Singleton fallback: nearest-center distance.
- Width clipping: [0.10, 10.0] in standardized feature space.
- Output: linear 4-output OLS with intercept.
- Ridge: NONE.
- Metaheuristic: NONE.
- Hyperparameter search: NONE.
- Standardization: pre-target training history only.

This stage deliberately does not optimize center count, ridge, width multiplier, center selection, or kernel shape. Those belong to N1.2 if N1.1 is sufficiently promising.

## Execution evidence
- Script: gold_axis_2026/tools/vw_midas_rbfnn_vanilla_v1.py
- Workflow: .github/workflows/gold-monthly-rbfnn-vanilla-v1.yml
- Run: 36255366631
- Job: 108441010234
- Artifact: 10910331925
- OUTPUT_GATE=PASS
- SCIENTIFIC_GATE=PASS

## DEV results
2022-04..2024-12, n=33:
- ΣAE = 1666.0440165
- direction = 19/33 = 57.58%
- MAE = 50.4862
- MAPE = 2.44418%
- RMSE = 62.1013
- relative MAE vs RW = 0.94769
- monthly win rate vs RW = 51.52%
- worst APE = 6.6512%

Yearly:
- 2022 Apr-Dec: ΣAE 412.3279; direction 6/9; relative MAE vs RW 0.85545.
- 2023: ΣAE 460.1468; direction 5/12; relative MAE vs RW 0.92399.
- 2024: ΣAE 793.5694; direction 8/12; relative MAE vs RW 1.02001.

## Reporting only
2025:
- ΣAE = 1082.2402
- direction = 9/12 = 75%
- MAE = 90.1867
- relative MAE vs RW = 0.64152

2026 Jan-Jul:
- ΣAE = 1467.8600
- direction = 5/7 = 71.43%
- MAE = 209.6943
- relative MAE vs RW = 0.88532

Neither period influenced selection or model construction.

## Numerical diagnostics
Across DEV + 2025 + 2026:
- design-matrix condition number median ≈ 19.84
- maximum condition number ≈ 24.37
- minimum observed cluster size = 1
- median minimum cluster size = 11
- observed width range ≈ 1.342 to 5.003
- no non-finite forecast
- no |predicted log return| >= 1

Interpretation:
- OLS conditioning is controlled; no numerical explosion.
- occasional singleton clusters occur but are handled by the predeclared nearest-center width fallback.
- no width boundary collapse.

## Comparison with current references
- ChHHO-ANFIS: 1413.03 / 23/33.
- REDUCED4 ANN: 1431.46 / 24/33.
- AOA-ELM: 1474.10 / 20/33.
- Vanilla RBFNN: 1666.04 / 19/33.
- SMA-ELMFIS: 1651.45 / 25/33.

Vanilla RBFNN does not enter the global DEV Pareto frontier.
It beats RW on aggregate DEV relative MAE but is materially behind the current price leaders.

## Decision
N1.1 Vanilla RBFNN: VALID BASELINE / NOT A LEADER.

The family is not closed yet because:
- the vanilla model is numerically stable;
- it beats RW in aggregate DEV;
- regularization and width/center-complexity control are core RBFNN design choices rather than arbitrary optimizer additions.

Authorized next step:
N1.2 compact regularized RBFNN only:
- predeclared small center-count grid;
- ridge output regularization;
- compact width-scale grid;
- chronology-safe inner selection;
- no metaheuristic.

No broad RBFNN optimizer screen is authorized.

## Control and compliance
- Correct RBF geometry: PASS.
- OLS output layer: PASS.
- Hyperparameter tuning in vanilla stage: NONE.
- Random split: NONE.
- DEV-only selection authority: PASS.
- 2025/2026 selection exclusion: PASS.
- Scientific gate: PASS.
- N1.1: COMPLETE.
