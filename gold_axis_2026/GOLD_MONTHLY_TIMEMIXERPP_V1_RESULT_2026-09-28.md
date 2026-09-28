# GOLD MONTHLY FORECAST — TIMEMIXER++ V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED  
**Workflow run:** 36445977068  
**Commit:** 6355bc165d573b54a9194be789e8d2a275b817e9  
**Implementation:** PyPOTS TimeMixerPP @ 53b3eac34be9491ac3f28e65ee1993436e9318af  
**Freeze:** `GOLD_MONTHLY_TIMEMIXERPP_V1_FREEZE_2026-09-28.md`

## Method
- 4-variate raw monthly price levels: Gold, Silver, Platinum, Palladium
- 48-month lookback
- H=1
- joint 4-metal forecast; Gold is evaluation target
- TimeMixer++ reference-style architecture:
  - term=short
  - n_layers=2
  - top_k=5
  - d_model=32
  - d_ffn=32
  - n_heads=1
  - n_kernels=3
  - downsampling_window=2
  - downsampling_layers=1
  - channel_mixing=True
  - channel_independence=True
  - use_norm=True
  - dropout=0.1
- max epochs=40
- patience=6
- seed=20260928
- latest 12 matured pre-target months = validation
- no random split
- no CURRENT8/GPR/macro covariates
- DB READ_ONLY

## DEV — 2022-04..2024-12
- n = 33
- SigmaAE = **4232.593110351562**
- MAE = **128.26039728338068**
- RMSE = **157.02194390297822**
- MAPE = **6.059549451700001%**
- WAPE = **6.228726934132147%**
- Direction = **13/33 = 39.39%**
- Relative MAE vs Random Walk = **2.407618379039569**
- Random Walk SigmaAE = **1758.0**
- Worst AE = **323.3125**, 2024-09

## DEV decision
**NOT PROMOTED / STOP V1.**

This frozen raw-level TimeMixer++ setup is substantially worse than:
- Random Walk
- TimesFM-3 zero-shot V1
- PLS1/PLS2
- the current Challenger-A frontier

Within the frozen comparison subset, it ranks **12/12** by DEV SigmaAE and is Pareto-dominated by every listed established comparator, including TimesFM-3 V1.

## 2025 — LOCKED REPORT ONLY
- SigmaAE = **2625.1667382812498**
- MAE = **218.7638948567708**
- RMSE = **266.4687695335217**
- Direction = **3/12 = 25.00%**
- Relative MAE vs RW = **1.5561154346658268**

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = **3152.66796875**
- MAE = **450.38113839285717**
- RMSE = **494.7484823588619**
- Direction = **1/7 = 14.29%**
- Relative MAE vs RW = **1.9014885215621231**

## Interpretation
The result establishes that the frozen V1 design is unsuitable for this dataset:
- raw monthly metal price levels,
- 48-month context,
- reference-style TimeMixer++ architecture,
- small monthly sample,
- per-origin training.

It does **not** justify architecture fishing after observing results. Any future TimeMixer++ experiment would require a separately frozen representation change such as return-space training, but V1 itself is closed.

## Governance
- Scientific gate PASS
- DB READ_ONLY
- random split NONE
- chronological last-12 validation only
- target-month leakage none
- DEV sole comparison authority
- 2025 locked
- 2026 quarantined
- existing Challenger-A/B paths unchanged

Result payload SHA256:
`cd6479ea5b9a0a2dc9c1a5c4a0b092af5749da863d2e2241c78f8a4233284f43`
