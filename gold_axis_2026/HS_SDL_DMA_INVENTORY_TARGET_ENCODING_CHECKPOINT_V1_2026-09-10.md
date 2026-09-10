# HS-SDL-DMA inventory, target clock and encoding checkpoint V1

Status: `PASS_DIRECTION_CORE_WITH_CONTEXT_PIT_EXCLUSIONS`

The canonical start is `21321cdaf21fb95eb8bdf4e84fcb3bb827af7af5`, manifest
v1.48. Production was inspected read-only at transaction snapshot
`352263:352263:`; the 12-engine inventory is exact and all four authority stores
are empty.

The immutable role replay contains 400 unique chronological completed NY17
origins from 2025-01-03 through 2026-08-30. It supports 399 matured 1D and 397
matured 3D target mappings before any evaluation split. Target progression uses
subsequent actually present governed NY17 rows, never calendar-day arithmetic,
interpolation or forward-fill.

FAST, SLOW and MONTHLY_DIRECTION_3M are frozen as categorical one-hot contrasts;
no `-1/0/+1` vote encoding was invented. The reference levels are respectively
MIXED, NOT_YET_ROBUST and NEUTRAL. Missing or unknown labels hard-stop.

BOCPD, GVZ and Macro Event do not have a proven exact daily origin-as-of join in
the frozen direction panel. Emergency labels are present but remain context-only.
All five context components are excluded from the initial small direction-only
candidate set; they are not converted into direction votes. This is an explicit
PIT/role restriction, not imputation.

No outer outcome was scored in this checkpoint. No threshold or hyperparameter
was selected from performance.
