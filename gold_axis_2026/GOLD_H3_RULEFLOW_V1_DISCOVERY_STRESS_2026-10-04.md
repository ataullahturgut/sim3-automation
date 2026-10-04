# GOLD H3 — RULEFLOW V1 DISCOVERY + 2026Q1 STRESS

**Date:** 2026-10-04

## 1. Discovery rule

Exploratory shallow-tree discovery on major U.S. macro/Fed event origins from 2025-03-12 through 2025-09-30 found a compact rule:

- recent 3-event 2Y-yield `conflict_ratio > 0.359`
- current event `dominance > 0.294`
- current event `dominance <= 0.502`

Interpretation:
the market has meaningful unresolved expectation conflict, and the newest shock is large enough to matter but not large enough to dominate/resolve the recent repricing history.

### 2025 descriptive performance

Flagged origins: **7**
Actual H3 reversals: **6/7 = 85.7%**

Where V5 still followed momentum:
- actions: **6**
- rescue: **5**
- broken: **1**
- net: **+4**
- precision: **83.3%**

Subperiods:
- Mar-Jun: **3 rescue / 1 broken = +2**, precision **75%**
- Jul-Sep: **2 rescue / 0 broken = +2**, precision **100%**

This is discovery evidence only because the exact tree thresholds were selected on this sample.

## 2. Frozen 2026 Q1 stress

The exact rule above was frozen before event-level 2026 Q1 outcomes were inspected.

Scored event origins: **12**

Hotspots:
- **3**
- actual reversals: **1/3 = 33.3%**

V5 incremental action accounting:
- rescue: **1**
- broken: **2**
- net: **-1**
- precision: **33.3%**

Non-hotspot reversal rate:
- **2/9 = 22.2%**

Conclusion:
the expectation-conflict/dominance geometry does **not** transport as a universal reversal rule.

## 3. Why the 2025 rule fails in 2026

A 60-origin cross-asset diagnostic shows a change in transmission structure.

Around Jul-29/30 2025, Gold was simultaneously coupled to several macro/risk channels:
- USD correlation roughly -0.42 to -0.46
- Nasdaq correlation roughly -0.51 to -0.52
- VIX correlation roughly +0.45 to +0.46
- Silver correlation roughly +0.55

Around Feb-2026, Gold remained strongly tied to USD and especially Silver, while Treasury/Nasdaq/VIX links were near zero:
- USD about -0.44 to -0.46
- Silver about +0.84 to +0.85
- Treasury near 0
- Nasdaq near 0
- VIX near 0

Therefore a raw 2Y-expectation rule is being applied in two different transmission regimes.

## 4. Rule-based successor architecture

### Gate 0 — MACRO TRANSMISSION REGIME

Before any rate-expectation reversal rule is allowed, measure whether Gold is currently coupled broadly to macro/risk channels rather than being dominated by a narrow metal/USD regime.

Candidate breadth channels:
- USD
- Treasury yield
- Nasdaq
- VIX

Silver is tracked separately because it can be strongly coupled even when the macro/risk transmission mechanism is weak.

### Gate 1 — EXPECTATION STATE

Using the last three major macro/Fed event-to-event 2Y moves:

- low conflict -> COHERENT
- high conflict -> FRAGMENTED

### Gate 2 — CURRENT SHOCK RESOLUTION

Inside FRAGMENTED:

- **too weak:** current shock is too small to alter the state -> KEEP
- **middle / unresolved:** shock matters but cannot dominate prior disagreement -> REVERSAL HOTSPOT
- **dominant:** new shock overwhelms the recent conflict -> RESOLUTION / CONTINUATION

The 2025 discovery band was approximately 29%-50% current dominance, but these exact thresholds are not considered portable yet.

### Gate 3 — GOLD ACCEPTANCE

Only then inspect:
- event-day momentum transition
- internal trend fragility
- Gold/Silver flow confirmation
- whether Gold accepts or rejects the new macro direction

### Gate 4 — ACTION

A FLIP is allowed only if:
1. macro transmission gate is ON;
2. expectation state is fragmented;
3. current shock is in the unresolved-middle state;
4. Gold acceptance/fragility evidence supports failure of the old trend.

Otherwise KEEP SAGE/V5.

## 5. Scientific status

The key discovery is not a finished threshold rule.

It is the **state ordering**:

**Transmission regime -> expectation fragmentation -> shock resolution -> Gold acceptance -> action**

This is materially different from prior attempts that fed all features into one classifier or used one fixed indicator threshold.
