# GOLD H3 — ARAC-H3-v1 TRANSPORT AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN BEFORE 2025/2026 TRANSPORT  
**Parent model:** `ARAC-H3-v1`

## Purpose

Transport the already-frozen ARAC-H3-v1 specification into 2025 and 2026 without changing the model.

No architecture, feature, parameter, expert, memory length, analog K, regime definition, adaptive-weight rule, or reliability threshold may be altered from ARAC-H3-v1.

## Frozen specification

Use the exact implementation in:

- `gold_axis_2026/tools/gold_h3_arac_v1.py`

Experts:
- GLOBAL_EN
- RECENT504_BAL_LOGIT
- LOCAL_ANALOG
- REGIME_PRIOR

Adaptive weighting:
- META_N = 126
- META_HALFLIFE = 63
- META_ETA = 30

Analog:
- K = 75
- pseudo-count = 20

Regime prior:
- pseudo-count = 25

Frozen selective reliability threshold:
- **0.03337519281868787**

## Transport protocol

Run one continuous chronological sequence from 2019 through the last available matured H3 target in 2026.

This preserves the original online adaptation rule:
- earlier 2025/2026 targets may influence later expert weights and training only after those targets have matured;
- no future target may influence an earlier forecast.

Report separately:
- 2025
- 2026 available year-to-date
- 2025+2026 combined

Also report:
- full coverage ARAC
- CORE3 Logistic L2 comparator
- CORE3 Elastic-Net comparator
- expanding prior
- frozen selective ARAC calls
- monthly 2026 selective diagnostics.

This is a transport evaluation, not a tuning stage. Any change after observing these results belongs to ARAC-H3-v2.
