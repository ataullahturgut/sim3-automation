# GOLD MONTHLY — September 2026 Current Regime State Result

**Date:** 2026-10-01  
**Month/state origin:** 2026-09  
**Forecast target context:** 2026-10  
**Status:** COMPLETE / PASS

Execution:
- workflow: **Gold Monthly September 2026 Regime State V1**
- run: **36832356597**
- artifact: **11147761924**
- digest: `sha256:c6107a38fd80fb0bbaf5c46e02c8707cfd336358a52982af5b90ab3d6ff74ff3`

Code:
- `gold_axis_2026/tools/gold_monthly_september_2026_regime_state_v1.py`
- code commit: `628a74f5743e383354c9f4b30b12b449d93e967a`
- workflow commit: `fe3b008dd519669c40ca3bc22b951148004d0cb2`

## September 2026 regime

Primary expanding-refit semantic regime:
- **R1**
- posterior probability: **0.9823228737**
- label: **R1**
- OOD: **NO**

Transition V2:
- status: **STABLE**
- transition flag: **NO**
- current transition votes: **0**
- active current transition signals: **none**
- incumbent posterior drop: **-0.004163**
- alternative posterior growth: **-0.003618**
- current margin: **0.964825**
- margin drop: **-0.007781**
- prototype-advantage drop: **-0.225601**

Extreme V1:
- status: **NORMAL**
- extreme flag: **NO**
- anomaly count: **0/4**
- active extreme signals: **none**
- emission percentile: **0.4094**
- predictive-score percentile: **0.5078**
- within-state distance percentile: **0.5276**
- month-to-month market-state jump percentile: **0.6632**

Combined state:
- **R1 / STABLE / NORMAL**
- not OOD
- not TRANSITION
- not EXTREME.

## Context for October 2026 forecast

The October ChHHO forecast was produced from a September origin whose regime context is therefore:

> **R1_STABLE_NORMAL, p(R1)=98.23%, no OOD / no transition / no extreme signal.**

This state classification is context only. It does not itself authorize a switch, blend, or forecast correction.

## Data qualification

- September common daily market data complete through **2026-09-30**.
- Current-state model trained strictly through **2026-08**; September is scored as the current origin month.
- No October market data used.
- World Bank September Gold monthly level was not yet available, so September Gold level-sensitive state features use the complete StakTrakr full-month proxy.
- Frozen regime architecture, prototype mapping, V2 transition rule and Extreme rule were unchanged.
