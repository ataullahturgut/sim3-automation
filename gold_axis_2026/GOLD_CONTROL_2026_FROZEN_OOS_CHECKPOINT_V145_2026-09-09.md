# Gold Control V1.45 — 2026 Frozen OOS Checkpoint

Status: `PARTIAL_BLOCKED_DATA`

* Previous canonical HEAD: `4bfcc3708a1c90071b7cddca2b82edcba6d72a81`
* Window: `2026-01..2026-08` (`RETROSPECTIVE_FROZEN_OOS_TEST`)
* Workflow/artifact: `34357321506 / 10106314049`
* No 2025-result-driven change: `PASS`
* Production writes / authority records: `NONE / 0`

January through July contain seven exact realized H=1 targets. August forecasts
were technically replayed but the exact realized target was not present, so all
four August H=1 performance cells are `BLOCKED_DATA` and were not imputed.
Scoreable seven-month MAE: CAUSAL_PATCH 249.9195, VW 238.7926, MOMENTUM
207.9089, RANDOM_WALK 236.8571. BOCPD August is separately blocked by the exact
CORE5 monthly-source boundary. These outcomes caused no tuning, model selection,
source change, selector/ensemble activation or authority write.
