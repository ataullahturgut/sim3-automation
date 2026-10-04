# GOLD H3 RULEFLOW 2026 Q1 STRESS PREREG

**Date:** 2026-10-04
**Status:** frozen retrospective stress test
**Discovery source:** 2025-03-12 .. 2025-09-30 rule-flow discovery

## Frozen rule

For each major U.S. macro/Fed event origin:

1. Let the latest three event-to-event changes in the official U.S. Treasury 2-year par yield be `s1,s2,s3`.
2. `gross3 = |s1|+|s2|+|s3|`
3. `net3 = s1+s2+s3`
4. `conflict_ratio = (gross3-|net3|)/gross3`
5. `current_dominance = |s3|/gross3`

**REVERSAL HOTSPOT** iff:
- `conflict_ratio > 0.359`
- `current_dominance > 0.294`
- `current_dominance <= 0.502`

No additional filter, event-family exclusion, susceptibility gate, or threshold adjustment is allowed.

If V5 still follows event-day momentum, hotspot would flip V5.

## 2026 Q1 event universe

Same event families:
- ADP
- NFP
- JOLTS
- CPI
- PCE
- FOMC

Actual release dates are used. Same-day releases are aggregated as one event origin.

## Metrics

- hotspot count
- actual H3 reversals inside hotspot
- V5 incremental actions
- rescue / broken / net
- precision
- all non-hotspot reversal rate

Historical 2026 is not a pristine holdout; this is a frozen stress test only.
