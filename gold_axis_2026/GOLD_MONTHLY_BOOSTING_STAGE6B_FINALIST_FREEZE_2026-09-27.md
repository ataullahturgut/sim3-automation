# GOLD MONTHLY — BOOSTING CATBOOST STAGE 6B FINALIST FREEZE

Date: 2026-09-27  
Status: **PRE-OUTCOME FREEZE — 6B RESULTS NOT YET RUN**

## Finalist selection rule
Eligibility requires a successful Stage 6A scientific gate and improvement versus Vanilla in all 6 Stage 6A inner-validation anchors.

Two independent promotion arms are frozen:
1. **Primary arm:** first 2 methods by ascending Stage 6A mean ratio vs Vanilla; tie-break median ratio, worst ratio, method name.
2. **Generalization arm:** first 3 methods by ascending 6-anchor outer diagnostic SigmaAE; tie-break higher direction-correct count, then method name.

Stage 6B finalists are the union of those arms plus Vanilla as an untuned comparator.

### Frozen finalists
- VANILLA comparator
- PSO
- MFO
- DE_ABC
- HHO
- TLBO

The rule is frozen **before any 33-month Stage 6B result exists**.

## Stage 6B evaluation
Each finalist is evaluated on every DEV target from **2022-04 through 2024-12 (n=33)**.

For each target month:
- only information available before that target is used;
- last 12 pre-target months form the chronological inner validation block;
- optimizer fitness excludes the target month;
- metaheuristic budget remains 80 objective calls;
- selected hyperparameters are refit on all pre-target data;
- one H=1 forecast is produced for the target month.

Primary metric: 33-month price-domain SigmaAE.

Secondary: direction, MAE, RMSE, MAPE/WAPE, relative MAE vs random walk, yearly stability and worst-month AE.

2025 and 2026 remain unopened. Database remains read-only. Random split remains prohibited.
