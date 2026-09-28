# SVR STAGE 4.1 — IMPLEMENTATION FREEZE

Date: 2026-09-28
Status: PRE-OUTCOME / BINDING

Methods:
- PSO
- GA
- DE
- MPA

Parameter vector:
theta = [log2(C), log2(gamma), epsilon]

Bounds:
- log2(C): [-8,12]
- log2(gamma): [-12,4]
- epsilon: [0.01,0.50]

Parent anchor:
- log2(C)=0
- gamma anchor = 1/12 on standardized 12-feature input
- log2(gamma)=log2(1/12)
- epsilon=0.10

Initialization:
- population size 24
- first agent = parent anchor
- half of remaining agents local around anchor
- remaining agents uniform over full bounds
- local sigma = [2.0, 2.0, 0.05] in theta coordinates

Budget:
- 45 update generations
- 3 deterministic repeats per outer origin
- no post-selection optimizer refit
- after repeat/validation selection, selected hyperparameters are fit once on all pre-target rows for outer forecast

Optimizer update equations:
- reuse repository-audited ELMFIS/RBFNN equations without changing method dynamics
- PSO/GA/DE from vw_midas_elmfis_meta_batch_1_v1.py
- MPA from vw_midas_elmfis_meta_batch_2_v1.py

Inner objective:
- optimizer evolution: standardized Gold log-return MAE on inner train
- validation selection: standardized Gold log-return MAE on chronological validation tail
- validation tail: final 20% of pre-target rows, minimum 12

Seed policy:
- target hash + repository method SEED_BASE + 1009*repeat

No 2025.
No 2026.
No random split.
DB READ_ONLY.
