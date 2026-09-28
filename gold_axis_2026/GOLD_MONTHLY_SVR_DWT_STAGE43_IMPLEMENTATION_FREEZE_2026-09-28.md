# SVR STAGE 4.3 — IMPLEMENTATION FREEZE

Date: 2026-09-28
Status: PRE-OUTCOME / BINDING

Methods:
- ACO
- BAT
- FA
- MFO
- FPA

Global Stage-4 contract remains unchanged:
- theta = [log2(C), log2(gamma), epsilon]
- bounds = [-8,12] x [-12,4] x [0.01,0.50]
- parent anchor = [0, log2(1/12), 0.10]
- population = 24
- generations = 45
- repeats = 3
- inner validation = final 20% chronological pre-target tail, minimum 12
- evolution objective = inner-train standardized Gold log-return MAE
- validation selection = prior-only validation standardized Gold log-return MAE
- no optimizer refit after validation selection
- selected hyperparameters fit once on all pre-target rows for outer forecast
- DEV only 2022-04..2024-12
- 2025 unopened
- 2026 unused
- random split none
- DB READ_ONLY

Reused audited optimizer equations:
- ACO, BAT:
  `vw_midas_elmfis_meta_batch_3_v1.py`
- FA, MFO, FPA:
  `vw_midas_elmfis_meta_batch_4_v1.py`

Only the objective and 3D SVR hyperparameter-bounds interface are adapted.
Method dynamics and repository seed bases are unchanged.

## Binding observability layout
This batch MUST run as five independent GitHub jobs:
- stage43_aco
- stage43_bat
- stage43_fa
- stage43_mfo
- stage43_fpa

Each method job:
- has independent queued/in_progress/completed/failure status
- has directly fetchable logs
- uploads its own JSON artifact

A sixth aggregate job:
- has explicit needs on all five method jobs
- downloads all five artifacts
- aggregates/ranks only after all five jobs complete successfully
- performs the batch scientific gate
- creates the Stage-4.3 report artifact

No shell-background multi-optimizer execution is allowed.

Batch 4.3 completion will bring Stage-4 progress from 9/32 to 14/32.
No Stage-4 parent selection is permitted after this batch.
