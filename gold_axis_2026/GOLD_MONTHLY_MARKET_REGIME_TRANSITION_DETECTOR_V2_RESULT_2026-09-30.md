# GOLD MONTHLY — Transition / Change Detector V2 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / PROMOTION GATE FAIL  
**Binding conclusion:** V2 substantially improves the 2025-2026 transition chronology and catches the 2026 transition from May, but it does not satisfy the pre-registered historical/later-validation selectivity gate and is therefore not authorized as the operational transition layer.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_TRANSITION_DETECTOR_V2_AUTHORITY_2026-09-30.md`
- initial authority commit: `84ee7988cb0990781139acb2d310b47771680279`
- quantified precision gate amendment: `7be25bb1e400c32e8d08e6a926b0a6ec7ae62299`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_transition_detector_v2.py`
- code commit: `b98e10a7f66c7ec9964e77466d871f2e2447d04a`

Workflow:
- `.github/workflows/gold-monthly-market-regime-transition-detector-v2.yml`
- workflow commit: `5c01d5152eca243b833f87ccc8605aed2bfaed99`

Execution:
- workflow: **Gold Monthly Market Regime Transition Detector V2**
- run: **36750689971**
- artifact: **11114806383**
- artifact digest: `sha256:b73d78137e79f64d4429d525b1dda5c53b27f951651a7791b2a6e2e17d61f782`
- scientific gate: **PASS**

Underlying prototype-aligned regime outputs reproduce the prior detector exactly.

## 2. What changed from V1

V2 removes generic anomaly/surprise variables from the transition vote.

Transition evidence uses only:
- incumbent posterior drop;
- incumbent-vs-alternative posterior margin;
- posterior-margin collapse;
- alternative-regime posterior growth;
- deterioration of the incumbent prototype advantage;
- one-month persistence through the previous interval.

No:
- emission anomaly vote;
- predictive-surprise vote;
- raw jump vote;
- raw latent-state switch vote.

## 3. Frozen calibration design

Threshold calibration used only:
- **EXPANDING_REFIT 2015-07..2021-12**

No 2022+ month was computed before the V2 rule was selected.

Grid:
- 12,288 candidate rules.

Pre-registered eligibility:
- historical event-hit rate >= 2/3.

Result:
- **0/12,288 candidates met the 2/3 eligibility requirement.**
- therefore the pre-registered fallback path was used.

Selected fallback rule:
- posterior-drop threshold: **0.10**
- current margin threshold: **0.45**
- margin-collapse threshold: **0.15**
- alternative-growth threshold: **0.10**
- prototype-advantage-drop threshold: **0.25**
- FAST votes required: **2**
- PERSISTENT votes required: **1**
- persistent margin threshold: **0.30**

This rule was frozen before later validation.

## 4. Historical calibration result — 2015-07..2021-12

### EXPANDING_REFIT
- months: 78
- reference transition events: 9
- event hits: **4/9 = 44.4%**
- transition-zone recall: **33.3%**
- false-transition rate outside zones: **15/66 = 22.7%**
- precision: **21.1%**
- mean lead among hit events: **0.25 months**

The historical calibration itself is weak. V2 did not discover a highly selective, high-recall persistence rule in this candidate family.

### ANNUAL_ANCHORED, same frozen rule
- event hits: **3/9 = 33.3%**
- false-transition rate: **22.7%**
- precision: **21.1%**

## 5. Later validation — 2022-01..2024-12

This period did not participate in threshold selection.

### EXPANDING_REFIT
- events: **3**
- event hits: **3/3 = 100%**
- transition-zone recall: **100%**
- transition flags: **11/36**
- false transitions outside zones: **8/33 = 24.2%**
- precision: **27.3%**

V1 precision on the same 2022-2024 period:
- **16.7%**

Thus V2 precision improves by about **+10.6 percentage points** and passes the precision-improvement gate.

However the pre-registered false-transition ceiling was **15%**.
Observed:
- **24.2%**

Therefore:
- event-hit gate: PASS
- precision-improvement gate: PASS
- false-transition gate: **FAIL**
- overall promotion: **FAIL**

### ANNUAL_ANCHORED
- event hits: **3/3 = 100%**
- false-transition rate: **7/33 = 21.2%**
- precision: **30.0%**

Annual also remains too noisy.

## 6. 2024 mandatory checkpoint

Both schedules:
- 2024-03: R1 + STABLE
- 2024-04: BELIRSIZ/R2 + **TRANSITION**
- 2024-05: R2 + STABLE
- 2024-06: R2 + STABLE

2024-04 is a strong directional transition:
- large incumbent posterior loss;
- large margin collapse;
- strong alternative growth;
- prototype advantage deterioration.

This remains a clean success.

## 7. 2025-01..2026-08 opened transport

### EXPANDING_REFIT
- 20 months
- transition flags: **3**
- 2026 event hit: **YES**
- first in-zone flag: **2026-05**
- lead to R1 confirmation in 2026-07: **2 months**
- transition-zone hits: **2/3**
- false transitions: **1/17 = 5.9%**
- precision: **66.7%**

Flagged months:
- **2025-08** — false transition
- **2026-05** — true transition-zone flag
- **2026-07** — true transition-zone flag

### ANNUAL_ANCHORED
- transition flags: **3**
- first 2026 flag: **2026-05**
- transition-zone hits: **2/3**
- false transitions: **1/17 = 5.9%**
- precision: **66.7%**

Flagged:
- 2026-05
- 2026-06
- 2026-08

The 2025/2026 result is encouraging but is **not promotion authority**, because this period was already inspected in V1 and the formal 2022-2024 validation gate failed.

## 8. 2026 mandatory checkpoint

### EXPANDING_REFIT
- 2026-04: R2 + STABLE
- **2026-05: R2 + TRANSITION**
- 2026-06: R2 + STABLE
- **2026-07: BELIRSIZ/R1 + TRANSITION**
- 2026-08: R1 + STABLE

The May flag is exactly the desired early-warning behavior:
- incumbent posterior drop about 0.282;
- margin collapse about 0.563;
- alternative growth about 0.281;
- prototype-advantage deterioration about 0.866;
- 4/4 directional evidences active.

### ANNUAL_ANCHORED
- 2026-04: R2 + STABLE
- **2026-05: BELIRSIZ/R2 + TRANSITION**
- **2026-06: R0 + TRANSITION**
- 2026-07: R0 + STABLE
- **2026-08: R1 + TRANSITION**

Annual catches May too, but continues to show the previously known R0/late-switch instability.

## 9. Binding interpretation

V2 demonstrates something important:

- the 2026 May deterioration can be detected using purely directional/persistent regime evidence;
- this does not require ChHHO errors, alarms, emission surprise or predictive surprise;
- V2 is much cleaner in 2025-2026 than V1.

But the formal historical evidence remains insufficient:
- calibration event hit only 44.4%;
- 2022-2024 false-transition rate still 24.2%;
- no candidate in the entire frozen grid reached the historical 2/3 event-hit eligibility rule.

Therefore the 2026 success must not be used to justify a post-hoc promotion.

## 10. Binding decision

**Transition Detector V2 is NOT promoted.**

Do not:
- retune V2 on 2022-2026;
- lower/raise thresholds to remove known false months;
- connect V2 directly to alarm weights;
- treat May-2026 success as validated production performance.

The current evidence says the simple threshold/vote family is not sufficiently selective across historical transitions.

## 11. Next exact stage

Proceed to the already-planned, scientifically separate:

**Regime-Extreme / Within-Regime Stress Detector V1**

Purpose:
- identify months that are unusual/extreme **inside an otherwise persistent regime**;
- explain cases such as long R2 episodes where anomaly/surprise is high but the regime does not change;
- keep this status separate from TRANSITION.

This stage must be built independently and must not be used to retroactively retune V2.

After the Extreme layer is measured, the project can decide between:
1. a structurally different transition model, e.g. dedicated changepoint / duration-aware semi-Markov transition detector; or
2. accepting that monthly market-state data supports only a descriptive transition warning, not a sufficiently selective operational transition gate.

Alarm selection/weighting remains blocked.
