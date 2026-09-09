# Gold Control — BOCPD 2026-08 Evaluation-only Extension V1.45

**Status:** `FROZEN_BEFORE_2026_08_BOCPD_OUTPUT_EXECUTION_OR_INSPECTION`  
**Frozen at:** 2026-09-09  
**Parent identity:** `BOCPD_RETURN_SUCCESSOR_V1`

## Non-substantive extension

This change-control authorizes one additional completed-month evaluation cell, `2026-08`, only. It does not change:

- role `REGIME_BREAK_CONTEXT`;
- source identity `gold_axis_2026/core5_monthly.csv.gz.b64:gold_monthly`;
- transform `log(P_t/P_t-1)`;
- development-only Normal-Inverse-Gamma prior;
- constant-geometric hazard `1/36`;
- state/reset rule;
- threshold (none);
- model parameters, features, architecture or position/direction authority.

The prior and posterior through `2026-07` must be byte-for-byte reproducible under the parent implementation. The August update may execute only if a positive finite `2026-08` observation is present under the exact frozen CORE5 source/artifact identity with truthful historical-reconstruction lineage. A different gold series, NY17 aggregation, interpolation, forward-fill or synthetic monthly value is forbidden.

The currently observed frozen artifact ends at `2026-07`; this fact is a pre-result source-coverage observation, not a BOCPD output. If the exact-source August value cannot be proven, the extension result is `BLOCKED_DATA:CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND` and no BOCPD August state is computed.

Any allowed execution is historical replay, `prospective_claim=false`, with no database/model/authority write. The extension cannot be used to tune any rule or reinterpret earlier results.

