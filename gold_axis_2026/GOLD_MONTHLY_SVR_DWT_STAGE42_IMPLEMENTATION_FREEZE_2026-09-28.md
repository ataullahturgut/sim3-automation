# SVR STAGE 4.2 — IMPLEMENTATION FREEZE

Date: 2026-09-28
Status: PRE-OUTCOME / BINDING

Methods:
- ABC
- SSA
- GWO
- WOA
- HHO

All global Stage-4 rules remain unchanged:
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
- 2025 unopened
- 2026 unused
- random split none
- DB READ_ONLY

Reused audited optimizer equations:
- ABC, SSA, GWO:
  `vw_midas_elmfis_meta_batch_2_v1.py`
- WOA, HHO:
  `vw_midas_elmfis_meta_batch_3_v1.py`

Only the objective and 3D hyperparameter bounds interface are adapted.
Method dynamics, seed bases, and update equations are not changed.

Batch 4.2 completion will bring Stage-4 progress from 4/32 to 9/32.
No Stage-4 parent selection is allowed after this batch.
