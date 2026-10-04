# TPC-H3 V1 — TEMPORAL PROPAGATION CONCURRENCE PREREGISTRATION

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-exception-channel-lab-v1-20261004`  
**Identity:** `TPC_H3_V1`  
**Status:** **FROZEN BEFORE TPC OUTCOMES**

## 1. Scientific question

OCS showed that a rare conjunction of:
- internal Gold/Silver hourly flow breakdown, and
- external cross-asset lead-lag stress

can produce high-specificity reversal exceptions.

TPC tests a different, stricter mechanism:

> is the external reversal pressure accompanied by a *recent deterioration pattern* inside Gold/Silver, rather than merely a high static flow-breakdown score?

TPC does not claim causal identification. It tests a frozen temporal-propagation proxy using 3h/6h/12h origin-time states.

## 2. Universe

A TPC action is considered only when:
- HELIOS V5 follows prevailing 12h momentum;
- IFBC and LLRS source rows are both available and identity-matched;
- forecast issue date is within the already-mature OCS development era beginning 2025-07-01.

Historical 2025–2026 evidence is development/stress-test only.

## 3. External stress prerequisite

Frozen from the previously surviving OCS external leg:

- `llrs_external_opposes == True`
- `llrs_incremental > 0`
- `llrs_pressure >= 0.10`

No LLRS threshold search is performed in TPC.

## 4. Internal temporal-propagation flags

All variables are already origin-safe VAST / IFBC features.

Let one point be earned for each:

1. **Opposition acceleration**
   `gc_opp_vol_share_3 > gc_opp_vol_share_12`

2. **Flow deterioration**
   `gc_flow_3 < gc_flow_12`

3. **Gold late rejection**
   `gc_late_rejection_3 > 0`

4. **Silver late rejection**
   `si_late_rejection_3 > 0`

5. **Efficiency decay**
   `gc_efficiency_6 < gc_efficiency_12`

Define:
`propagation_count = sum(flags)`

No feature sign or comparison is changed after results.

## 5. TPC candidate

TPC candidate if all hold:

- V5 follows momentum;
- external stress prerequisite passes;
- `propagation_count >= 3`.

Action:
- FLIP V5.

Otherwise:
- KEEP V5.

The majority rule 3/5 is structural and frozen. There is no threshold grid.

## 6. Development evaluation

Report:

- candidates;
- rescue / broken / net;
- precision;
- candidate rate;
- half-year blocks;
- whole-period V5 vs TPC-assisted accuracy;
- overlap with the frozen OCS q=.70/.10 exception;
- TPC-only marginal candidates;
- TPC-only marginal rescue / broken / net;
- OCS-only candidates;
- union rescue / broken / net;
- OPAL-no-candidate rescue count.

## 7. Development gate

TPC is development-promising only if all hold:

1. candidates >= 8;
2. precision >= 0.60;
3. net rescue >= +3;
4. candidate rate <= 0.12 of eligible common origins;
5. every available half-year block has net >= -1;
6. at least 2 half-year blocks have net > 0;
7. TPC-only marginal net over OCS >= 0;
8. TPC+OCS union net > OCS net alone;
9. source identity mismatches = 0.

If PASS:
`TPC_H3_V1_PROMISING`

If FAIL:
`TPC_H3_V1_FAIL`

No propagation-count threshold, component sign, LLRS threshold, or V5 eligibility rule may be changed after this replay.

## 8. Prospective interpretation

Even if development-promising:
- no historical 2026 result is a clean holdout;
- a new prospective freeze is required;
- HELIOS V5-DCE remains binding;
- SAGE-H3 V2 OCS exception remains the existing shadow challenger until superseded by prospective evidence.
