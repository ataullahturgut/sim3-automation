# GOLD SHORT-HORIZON — FORECAST CLOCK / TARGET WINDOW AUDIT

**Date:** 2026-10-06  
**Status:** GOVERNANCE CORRECTION / RETROSPECTIVE CLOCK AUDIT  
**Purpose:** separate model feature time, forecast issue time, scored target interval, and executable trading interval before any further return claim.

## 1. Core finding

The current H3/CIG research contains **two different clocks** that must not be treated as the same thing:

1. **model/scoring clock** — the historical label against which accuracy was measured;
2. **execution clock** — the price interval that begins only after the forecast is actually available.

The model scores are not automatically invalid, but some previously displayed "realized" moves are **label-space realizations**, not returns that begin at the forecast timestamp.

## 2. H3 clock

Frozen prospective authority:
- feature cutoff date = D
- hourly IRIS/SAGE anchor = **16:00 America/New_York on D**
- no hourly bar from forecast issue date is allowed
- planned forecast issue = **next weekday after D**
- issue deadline = **08:00 America/New_York**
- H3 target end = third future governed daily observation after D.

The prospective code settles:

`target_r3 = log(target_end_price / target_start_price)`

where:
- `target_start_price` = governed daily Gold reference on **feature_cutoff_date D**
- `target_end_price` = governed daily Gold reference on the third future observation.

Therefore the H3 scored target **starts at the daily reference on D**, not at 08:00 New York on the forecast issue date.

### Example

For the first 2026 clean V5 row:
- feature cutoff: **2025-12-31**
- forecast issue date: **2026-01-02**
- target end date: **2026-01-06**
- reported target_r3: **+3.30597%**
- p_up: **0.51026**

The +3.30597% is the move from the **2025-12-31 governed daily reference** to the **2026-01-06 governed daily reference**.

It is **not** the return from 2026-01-02 08:00 New York to 2026-01-06.

## 3. Daily-reference semantic

The governed Gold daily series used by the clean H3 chain is a full-day/daily-reference semantic, cross-audited against the arithmetic mean of Twelve Data hourly closes over a UTC calendar day.

Consequences:
- the daily reference is not an executable single market print;
- the feature-cutoff daily reference is completed only after the full governed day is known;
- a target return based on two daily references is a **forecast label**, not automatically a transaction return.

## 4. CIG-D1 clock

CIG-D1 repurposes the H3 expert state into a same-day action signal.

Binding decision time currently recorded:
- **08:00 America/New_York** on the issue date.

Historical CIG-D1 result document defines its same-day realization using a previous-daily-reference/close to current-daily-reference/close direction.

The Sep28-Oct2 extension code explicitly computes:

`d1_actual = sign(gold_issue_daily_reference - gold_cutoff_daily_reference)`

Thus the D1 historical label begins from a reference **before the 08:00 issue timestamp**.

This means:
- the reported CIG-D1 accuracy is a valid accuracy measure for its historical **same-day label definition**;
- it is **not yet proven to be the same as accuracy of the executable 08:00-NY -> later-price direction**;
- any statement that the whole historical daily move occurred *after* the signal is incorrect.

## 5. Istanbul clock mapping

08:00 New York maps approximately to:
- **15:00 Europe/Istanbul** while New York is on daylight time;
- **16:00 Europe/Istanbul** while New York is on standard time.

All audit calculations must convert by date; fixed offsets are forbidden.

The H3 hourly feature anchor 16:00 New York maps approximately to:
- **23:00 Istanbul** in New York daylight time;
- **00:00 Istanbul next calendar day** in New York standard time.

## 6. What was correct vs what must be corrected

### Correct
- H3 p_up values are model probabilities under the frozen H3 label.
- H3 UP/DOWN accuracy is accuracy against the frozen H3 daily-reference target.
- CIG-D1 4/4 consensus accuracy is accuracy against its historical same-day label.

### Must not be claimed without re-scoring
- that H3 target_r3 is an investor return starting when the forecast was issued;
- that CIG-D1 74.40% means 74.40% correct direction **from 08:00 New York onward**;
- that a displayed daily "actual" price/move is fully future information relative to the decision timestamp;
- that target-series compound return equals executable P&L.

## 7. Required correction audit

Before any further execution-return statement, create three distinct realized labels from the 15-minute XAU/USD source:

1. **POST-ISSUE D1:** 08:00 NY -> fixed same-day end timestamp.
2. **NEXT-DECISION:** 08:00 NY -> next issue day's 08:00 NY.
3. **LATE-US:** selected/frozen late-US window, if retained as a separate execution hypothesis.

Report the original historical CIG label beside these three executable labels.

The original CIG accuracy must be called **label accuracy** until this reconciliation is complete.

## 8. Governance decision

No existing model probability is deleted or retrospectively changed by this audit.

However, prior wording that presented `target_r3`, daily-reference movement, or the CIG historical same-day label as if it were an executable post-signal return is superseded.

**Next authorized step:** re-score the unchanged CIG-D1 signals against post-08:00 executable 15-minute labels and compare that accuracy with the original label accuracy.
