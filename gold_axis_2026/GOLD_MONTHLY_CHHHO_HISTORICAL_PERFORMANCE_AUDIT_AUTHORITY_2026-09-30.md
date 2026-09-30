# GOLD MONTHLY — Historical ChHHO Performance Audit Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / BINDING PERFORMANCE AUDIT  
**Purpose:** determine whether the historical ChHHO replay itself is sufficiently informative before interpreting E/G alarm behavior.

## 1. Performance blocks

### Block H1 — counterfactual same-method history
Run the unchanged canonical ChHHO-ANFIS on **every feasible target from the earliest internal-history-feasible month through 2021-10**.

GPR:
- official current-method source family `data_gpr_export.xls`
- snapshot commit `5e4dfbfda5a89aceff9b30f5454fb36ab33c3baf`
- truncate to required historical lag month for each target

This is **counterfactual same-methodology stress history**, not PIT validation.

The earliest target is determined mechanically by the unchanged ChHHO internal training/validation minimum. Do not relax that minimum.

### Block H2 — valid same-method pre-DEV
Use frozen artifact **11084467079** for targets:
- 2021-11..2022-03

Do not rerun these forecasts.

### Block H3 — frozen canonical DEV
Use frozen ChHHO artifact **10989389723** for:
- 2022-04..2024-12

Do not rerun these forecasts.

## 2. Required metrics

For each block and year:
- n
- cumulative absolute error
- MAE
- MAPE
- RMSE
- direction accuracy
- median AE
- worst target / worst AE
- count AE > 63.06
- count APE > 2.96117%
- count absolute return-error > 3.00590pp

Also report:
- all HIGH_AE targets
- top-15 worst historical targets by AE
- E/G flag at each target origin.

## 3. E/G flags

Using canonical monthly Gold only:

### E-level
Gold monthly price >20% above prior trailing-12-month mean.

### E-full
E-level AND |ChHHO predicted return - current Gold 1m return| >5pp.

### G
Gold trailing 3-month log return <= -10%.

No E/G threshold retuning is allowed.

## 4. Interpretation

Historical E/G model-error evidence is interpretable only relative to the model's baseline performance in the same block.

If historical H1 is globally poor, isolated E/G errors cannot be called alarm-specific.

If H1 is globally reasonable but E/G conditional errors are not elevated, the alarm is not supported as a ChHHO-error detector.

H1 remains counterfactual, not PIT/out-of-sample historical validation.
