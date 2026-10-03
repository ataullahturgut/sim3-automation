# TRES-H3 V1 — STAGE 0 EVENT-TIME LABEL CONTRACT

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-tres-v1-20261004`  
**Identity:** `TRES_H3_V1`  
**Stage:** 0 — event-time semantics and leakage audit  
**Status:** **FROZEN BEFORE EVENT-LABEL RESULTS**

## 1. Purpose

Reformulate the V5 reversal problem as a discrete-time first-passage / competing-risk process rather than a single H3 terminal-direction label.

No model may be fitted until the event-label timeline passes the audit below.

## 2. Canonical origin and path

For every frozen H3 row:

- origin date = `feature_cutoff_date`
- origin Gold level = frozen daily Gold level on `feature_cutoff_date`
- H1 path level = first subsequent available Gold observation
- H2 path level = second subsequent available Gold observation
- H3 path level = third subsequent available Gold observation
- the third subsequent available date **must equal** `target_end_date_h3`

Semantic identity check:

`log(P_H3 / P_origin)`

must equal existing `target_r3` within absolute tolerance **1e-10**.

If any eligible row fails the date mapping or return identity, Stage 0 fails and no TRES model is fitted.

## 3. Momentum-normalized path

Let:

`m = +1` if `h_ret_12 >= 0`, else `-1`.

For horizon h in {1,2,3}:

`g_h = m * log(P_h / P_origin)`

Interpretation:
- positive g_h = movement in the prevailing 12h momentum direction;
- negative g_h = movement against the prevailing momentum direction.

## 4. Origin-adaptive barrier

Compute frozen daily Gold log returns from the frozen daily-price series.

At each origin:

`sigma20 = std(r_{t-19}, ..., r_t, ddof=0)`

using only daily returns whose end date is <= feature_cutoff_date.

Primary barrier:

`B_t = 1.00 * sigma20`

No target/future value enters B_t.

Robustness labels, reported but never selected from:
- LOW: `0.75 * sigma20`
- PRIMARY: `1.00 * sigma20`
- HIGH: `1.25 * sigma20`

No barrier search is allowed after results.

## 5. Competing-risk event

For each barrier scale separately, scan h=1,2,3 in chronological order.

- CONTINUATION event if `g_h >= B_t`
- REVERSAL event if `g_h <= -B_t`
- if neither occurs by H3: CENSORED / NO_DECISIVE_EVENT

The first crossing wins.

Recorded fields:
- event_type ∈ {CONTINUATION, REVERSAL, CENSORED}
- event_day ∈ {1,2,3, null}
- g1, g2, g3
- sigma20
- barrier

## 6. Relationship to existing H3 target

The existing `reversal_target` / V5 rescue label is **not** used to create the first-passage label.

Stage-0 reports, for diagnosis only:
- P(terminal reversal | first-passage reversal)
- P(terminal reversal | first-passage continuation)
- P(terminal reversal | censored)
- event-type counts by year
- disagreement examples.

This determines whether first-passage state provides genuinely different information from the terminal H3 label.

## 7. Leakage and integrity gates

Stage 0 PASS requires:

1. every audited H3 row has an origin Gold price;
2. the next three frozen price observations can be resolved;
3. resolved H3 date equals `target_end_date_h3`;
4. recomputed H3 log return matches `target_r3` within 1e-10;
5. sigma20 uses no date later than feature_cutoff_date;
6. no zero/non-positive Gold level;
7. no missing primary barrier;
8. event_day is chronologically valid;
9. all three barrier scales are deterministic transforms of the same origin sigma20.

Any failure => **STOP_MODELING_AND_REPAIR_TIMELINE**.

## 8. Governance

Historical 2022–2026-09 is development data.

No Stage-0 result may alter:
- origin definition;
- barrier scale;
- H1/H2/H3 path definition;
- first-crossing logic.

If Stage 0 passes, Stage 1 may fit a preregistered discrete-time competing-risk model.
