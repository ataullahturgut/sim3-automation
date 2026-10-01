# GOLD MONTHLY — Harmful-Switch / Shared-Hard Safety Guard V1 Result

**Date:** 2026-10-01  
**Status:** COMPLETE / SCIENTIFIC_GATE=FAIL / DEV-ONLY / NO PRODUCTION SWITCH

## Authority and execution

Authority:
- `GOLD_MONTHLY_HARMFUL_SWITCH_SHARED_HARD_GUARD_V1_AUTHORITY_2026-10-01.md`
- authority commit: `f866167df637606da66820fa4ebedfa00cdd4594`

Official execution:
- workflow: **Gold Monthly Harmful Switch Shared Hard Guard V1**
- run: **36848597787**
- artifact: **11153893189**
- artifact digest: `sha256:26f8d19b603adffed0f36f5e83c8bb865c3cbf0da6d338deda5b64b67397c4e9`
- head commit: `edfa4391a2b195f4a0228f2d6a39ab275262cd00`
- conclusion: **SUCCESS**

Scientific result:
- V1 guard gate: **FAIL**

## Baseline NO_GUARD

Frozen Rescue-Gain Predictor V1 DIRECT_SWITCH:
- gain versus KEEP: **+4.7044 USD**
- allowed switches: **13**
- beneficial switches: **5**
- harmful switches: **8**
- worst incremental harm: **31.6639 USD**

## Pre-registered guard result

No deterministic guard candidate satisfied the acceptance conditions.

Full-DEV examples:
- BREADTH_50 gain: **-3.78 USD**
- BREADTH_67 gain: **-74.93 USD**
- BREADTH_80 gain: **-56.81 USD**
- CONF_050 gain: **-3.78 USD**
- CONF_100 gain: **-42.05 USD**
- CONF_150 gain: **-23.96 USD**

The gates reduce switch count but eliminate genuine rescue opportunities faster than they eliminate harmful switches.

## Expanding guard-selection replay

Protocol:
- first 4 frozen predictor switch opportunities = warm-up;
- next 9 switch opportunities evaluated sequentially;
- guard choice at each step used only prior DEV switch opportunities.

Result:
- expanding guard replay gain versus KEEP: **-22.5427 USD**
- same-window NO_GUARD gain: **+0.9418 USD**
- replay beneficial / harmful allowed switches: **2 / 4**
- worst incremental harm: **31.6639 USD**

Therefore the guard-selection replay is worse than leaving the frozen predictor unguarded.

## Critical 2023-03 finding

2023-03 is the key shared-hard / false-warning-style failure:
- frozen predictor chose CNN-LSTM LB6;
- predicted top rescue gain: **+86.996 USD**
- predicted positive-gain breadth: **93.3% of challengers**
- confidence ratio: **3.42× residual RMSE**
- realized selected-switch gain: **-23.965 USD**

This disproves the V1 assumption that broad predicted rescue consensus or high confidence is sufficient to identify safe rescue.

## Binding decision

- **Harmful-Switch / Shared-Hard Safety Guard V1 is rejected.**
- No V1 guard is frozen.
- No 2025/2026 guard transport is authorized, because there is no DEV-passing guard to transport.
- ChHHO remains the main forecast.
- Specialist Hedge remains the reliability-warning layer.
- Rescue-Gain Predictor V1 remains research-only.
- Automatic SWITCH / BLEND remains unauthorized.

## Next research direction

Do not add another deterministic breadth/confidence threshold.

The next defensible stage is a **direct harmful-switch / shared-hard probability model** using DEV-only chronological validation. Its target should be whether the frozen predictor's proposed switch is harmful, rather than trying to infer safety from breadth or confidence heuristics.
