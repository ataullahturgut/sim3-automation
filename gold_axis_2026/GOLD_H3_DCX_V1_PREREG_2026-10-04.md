# DCX-H3 V1 — DIRECTIONAL-CHANGE OVERSHOOT EXHAUSTION PREREGISTRATION

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-exception-channel-lab-v1-20261004`  
**Identity:** `DCX_H3_V1`  
**Status:** **FROZEN BEFORE DCX OUTCOMES**

## 1. Scientific question

Can a sparse H3 reversal exception be detected from the **pre-origin intrinsic-time state** of Gold alone?

DCX is deliberately distinct from:
- TRES, which models the future H1/H2/H3 event path;
- IFBC/VAST, which uses hourly volume-flow microstructure;
- LLRS/OCS, which uses cross-asset lead-lag stress.

DCX uses only pre-origin hourly Gold price geometry.

## 2. Source / clock

Research proxy:
- Yahoo `GC=F` hourly close.

Research interval:
- 2025-01-01 through freeze date.

Canonical H3 origin remains 17:00 America/New_York.

Last usable hourly observation:
- <=16:00 ET on feature-cutoff date.

Freshness:
- last usable GC bar must be <=3 wall-clock hours stale.

Historical 2025–2026 evidence is development/stress-test only.

## 3. Origin-adaptive directional-change threshold

For each origin:

1. compute 6-trading-bar log return on GC hourly data;
2. take the last **480 valid hourly bars strictly before the current origin bar**;
3. define:

`delta = median(abs(GC_6h_return))`.

Requirements:
- at least 240 valid calibration bars;
- delta > 0.

No target information enters delta.

## 4. Intrinsic-time reconstruction

Using the last **240 hourly GC bars** ending at the origin and the fixed origin delta:

Run a standard directional-change reconstruction:
- UP mode confirms when price rises by delta from the active low;
- DOWN mode confirms when price falls by delta from the active high;
- after confirmation, track the running extreme until the opposite directional change is confirmed.

Origin outputs:

- `dc_mode` = +1 UP / -1 DOWN;
- `event_age_bars`;
- `overshoot_ratio` = extension beyond the last confirmation level / delta;
- `retracement_ratio` = current retracement from the active extreme / delta.

## 5. Momentum alignment

Let:
- s = +1 if 12h momentum is UP;
- s = -1 if 12h momentum is DOWN.

DCX only acts when:
- HELIOS V5 follows momentum;
- `dc_mode == s`.

Thus the intrinsic-time state still agrees with the prevailing trend; DCX searches for exhaustion **before a confirmed directional change**.

## 6. Origin-only overshoot rank

For every origin after features are computed:

Compare current `overshoot_ratio` only with the last **120 prior eligible DCX origins**.

Minimum prior origins:
- 60.

One-sided empirical rank:

`overshoot_rank = (1 + count(prior_overshoot <= current_overshoot)) / (N + 1)`.

No target labels are used.

## 7. Frozen DCX candidate

Candidate if all hold:

1. V5 follows momentum;
2. dc_mode == momentum direction;
3. `overshoot_rank >= 0.80`;
4. `retracement_ratio >= 0.50`.

Because the active DC mode must still equal momentum, the retracement is necessarily below the opposite full directional-change confirmation in the reconstructed state.

Action:
- FLIP V5.

Otherwise:
- KEEP V5.

No threshold grid is allowed in V1.

## 8. Development evaluation

Use common historical development blocks:
- 2025 H2
- 2026 H1
- 2026 H2 through Sep.

Report:
- candidate count/rate;
- rescue / broken / net;
- precision;
- block stability;
- V5 vs DCX-assisted full-direction accuracy;
- overlap with frozen OCS;
- DCX-only marginal rescue / broken / net;
- OCS+DCX union;
- OPAL-no-candidate rescues.

## 9. Development gate

DCX is development-promising only if all hold:

1. candidates >= 6;
2. precision >= 0.60;
3. net rescue >= +3;
4. candidate rate <= 0.12;
5. every available half-year block net >= -1;
6. at least 2 blocks net > 0;
7. DCX-only marginal net over OCS > 0;
8. OCS+DCX union net > OCS net;
9. source/timeline integrity failures = 0.

If PASS:
`DCX_H3_V1_PROMISING`

If FAIL:
`DCX_H3_V1_FAIL`.

No delta rule, windows, rank threshold or retracement threshold may be tuned on the same replay after results.

## 10. Prospective interpretation

A historical PASS would only justify a separately frozen prospective shadow channel.

HELIOS V5-DCE remains binding.
SAGE-H3 V2 OCS exception remains the current frozen shadow exception.
