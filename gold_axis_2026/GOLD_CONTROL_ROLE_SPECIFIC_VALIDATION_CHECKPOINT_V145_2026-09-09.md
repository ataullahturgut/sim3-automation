# Gold Control V1.45 — Role-Specific Validation Checkpoint

Status: `PASS_WITH_EXPLICIT_BLOCKERS`

* Previous canonical HEAD: `bcdbd7c7564e88165486361bb220620868caccb1`
* Workflow run: `34357321506`
* Artifact: `10106314049`
* Artifact digest: `sha256:607f4b09adda49d1d78e8f23447bed6a3965e88fc0bd03e0217a1c177104e0ce`
* Tests: 18 PASS in the preceding governed run; final run PASS.
* Database access: read-only Macro V2 panel replay.
* Database writes / inserted rows / conflicts: `NONE / 0 / 0`.
* Authority invariants: no forecast or decision authority created; selector and ensemble OFF.

Role results: 4 `VALIDATED_CORE`, 5 `VALIDATED_COMPLEMENTARY`, 2
`NOT_PROVEN`, 1 `BLOCKED`. The two Emergency roles remain `NOT_PROVEN`
because an independent false-alert/miss truth label was not proven. BOCPD remains
`BLOCKED_DATA` for exact 2026-08 CORE5 gold monthly input. Macro V2 score replay
and the separately preregistered eight-event reaction replay both passed; the
2025-10 contractual exclusion remains unimputed.
