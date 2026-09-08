# GOLD CONTROL — MARKET SHOCK V2 2026 MULTI-FREQUENCY NULL AUDIT

**Date:** 2026-09-08  
**Status:** `POST-FINDING SANITY AUDIT / PRE-REGISTERED BEFORE NULL OUTPUT / RESEARCH ONLY`  
**Trigger:** the Jan–May 2026 multi-frequency audit found 247/247 LM5 episodes in `FREQ_STRONG`. Because 1m/3m/5m/10m LM statistics share the same underlying price path, a matched negative-control audit is required before interpreting this as strong corroboration.

## 1. Frozen question

Do ordinary non-Market-Shock 5-minute windows, matched on month and intraday timing, also receive `FREQ_STRONG` confirmation from the alternative 1m/3m/10m LM tests at a high rate?

If they do, the cross-frequency result is not discriminative. If they do not, the 247/247 result is evidence of frequency-stable events rather than a generic consequence of the alternative detectors firing often.

## 2. Inputs and signal definitions

Use exactly the already frozen Jan–May 2026 common-support audit definitions:

- 1m/3m/10m LM models and 99.9% primary significance;
- 1m ±5m, 3m ±5m, 10m ±10m timestamp matching tolerances;
- `FREQ_STRONG` = at least two of {1m,3m,10m} confirm and at least one is 3m or 10m;
- authoritative 5m episode population unchanged.

No model threshold or frequency definition changes are allowed.

## 3. Matched negative controls

For each authoritative Jan–May LM5 episode request five control windows.

A control window must:

- be in the same calendar month as its matched episode;
- start on the same UTC weekday;
- have start time-of-day within ±60 minutes of the matched episode start;
- have the same number of 5-minute bars as the matched episode;
- contain no V2 Market Shock bar;
- be at least 60 minutes away from every V2 Market Shock bar;
- contain contiguous 5-minute observations with no >10-minute gap;
- be selected deterministically with seed `20260908 + episode_id`;
- be unique within the controls for that episode.

The alternative-frequency confirmation rule is applied to the control window exactly as to a real LM5 episode, using each control bar timestamp as a possible base timestamp.

## 4. Frozen outputs

Report:

- requested and constructed controls;
- control completion rate;
- observed LM episode `FREQ_STRONG` rate;
- matched-control `FREQ_STRONG`, `FREQ_CONFIRMED`, `MICRO_ONLY`, and `FREQ_ISOLATED` rates;
- observed/control `FREQ_STRONG` risk ratio;
- Wilson 95% confidence intervals for observed and control `FREQ_STRONG` rates;
- two-sided Fisher exact p-value comparing observed LM episodes against constructed controls. Because controls are clustered within episodes, Fisher is explicitly a simple diagnostic rather than a definitive inferential model.

## 5. Pre-registered interpretation

Call the multi-frequency result `DISCRIMINATIVE_SANITY_PASS` only when:

1. at least 90% of requested controls are constructed;
2. the 95% Wilson interval for the observed `FREQ_STRONG` rate does not overlap the 95% Wilson interval for the control `FREQ_STRONG` rate;
3. two-sided Fisher exact `p < 0.001`.

Otherwise call it `DISCRIMINATIVE_SANITY_FAIL`.

No arbitrary control-rate target is introduced after seeing the 247/247 result.

## 6. Governance

This sanity audit does not turn cross-frequency confirmation into authoritative true-event labels. It does not change V2, create V3, authorize 2025, or promote production.

`prospective_claim = false`  
`authoritative_false_positive_rate = NOT_PROVEN`  
`production_promotion = BLOCKED_RESEARCH_ONLY`  
`canonical_merge = NOT_AUTHORIZED`
