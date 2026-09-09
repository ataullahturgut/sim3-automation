# Gold Control V1.45 — 2025 Retrospective Validation Checkpoint

Status: `PASS_WITH_ROLE_LIMITATIONS`

* Previous canonical HEAD: `82ccb51ec9ec15b53e6d5fce5e4483a44c8df996`
* Window: `2025-01..2025-12` (`RETROSPECTIVE_VALIDATION_WINDOW`)
* Workflow/artifact: `34357321506 / 10106314049`
* No-tuning confirmation: `PASS`
* Production writes / authority records: `NONE / 0`

All four H=1 experts have 12 origin-safe scored cells. MAE is 120.0971 for
CAUSAL_PATCH, 81.7722 for VW, 129.3923 for MOMENTUM and 140.5833 for the
mandatory RANDOM_WALK benchmark. Context/risk evidence is window-scoped and
role-specific; Emergency independent false/miss labels remain `NOT_PROVEN`.
The results did not change any model, threshold, source, hyperparameter or 2026
evaluation rule.
