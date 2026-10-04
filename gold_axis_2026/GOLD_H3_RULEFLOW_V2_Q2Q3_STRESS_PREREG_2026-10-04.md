# GOLD H3 RULEFLOW V2 — 2026 Q2-Q3 STRESS PREREG

**Date:** 2026-10-04
**Status:** frozen retrospective stress test
**Rule source:** RuleFlow V2 Gated (frozen before this Q2-Q3 run)

## Frozen decision rule

For each scheduled major U.S. macro/Fed event origin:

### Gate 1 — expectation hotspot
Use the latest three event-to-event changes in the official U.S. Treasury 2-year par yield.

- gross3 = |s1| + |s2| + |s3|
- net3 = s1 + s2 + s3
- conflict_ratio = (gross3 - |net3|) / gross3
- current_dominance = |s3| / gross3

Hotspot iff:
- conflict_ratio > 0.359
- current_dominance > 0.294
- current_dominance <= 0.502

### Gate 2 — causal transport gate
Pass iff either:
- internal susceptibility >= 0.60
OR
- macro breadth >= 0.30

Internal susceptibility is the median expanding percentile rank over the prior 120 H3 origins of:
- -trend_strength
- +session_against_trend
- -trend_close_location
- +adverse_excursion

Macro breadth is the mean absolute rolling-60 correlation of Gold daily return with:
- USD return
- 10Y yield change
- Nasdaq return
- VIX return

Silver is intentionally excluded from breadth because it can remain strongly linked during a narrow metals regime.

### Action
Only if both gates pass AND V5 follows event-day momentum:
- FLIP V5
Otherwise:
- KEEP V5

No threshold, event-family filter, or sign convention may be changed after this file is committed.

## Q2-Q3 2026 event universe

Same families as discovery:
- ADP
- Employment Situation / NFP
- JOLTS
- CPI
- Personal Income and Outlays / PCE
- FOMC

Verified release dates used:
- ADP: Apr 1, May 6, Jun 3, Jul 1, Aug 5, Sep 2
- NFP: Apr 3, May 8, Jun 5, Jul 2, Aug 7, Sep 4
- JOLTS: May 5, Jun 2, Jun 30, Aug 4, Sep 1, Sep 29
- CPI: Apr 10, May 12, Jun 10, Jul 14, Aug 12, Sep 11
- PCE: Apr 9, Apr 30, May 28, Jun 25, Jul 30, Aug 26, Sep 30
- FOMC: Apr 29, Jun 17, Jul 29, Sep 16

Continuity anchors before Q2:
- Mar 13 PCE
- Mar 18 FOMC
- Mar 31 JOLTS

If an event date has no clean H3 origin/outcome in the frozen panel, it is excluded and reported as unavailable.

## Metrics

- scored events
- hotspots
- gated hotspots
- actions
- rescue / broken / net
- action precision
- H3 reversal rate inside and outside the gated hotspot
- Q2 and Q3 separately
