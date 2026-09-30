# GOLD MONTHLY — Transition / Change Detector V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / NOT OPERATIONALLY PROMOTED  
**Binding conclusion:** V1 can identify the 2024 transition and gives a one-month-early warning in the 2026 transition, but false-transition rates are too high. The main reason is that generic surprise/anomaly signals are also firing during within-regime extreme months.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_TRANSITION_DETECTOR_V1_AUTHORITY_2026-09-30.md`
- authority commit: `749a6063563136f0132698728fd026c11ac3e2fd`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_transition_detector_v1.py`
- code commit: `dfcdb8ad79177e3a38200e1bf398cdb5a2d46ec8`

Workflow:
- `.github/workflows/gold-monthly-market-regime-transition-detector-v1.yml`
- workflow commit: `6f2dab9231aa2cd2ef34d1158b31f53f7553a770`

Execution:
- workflow: **Gold Monthly Market Regime Transition Detector V1**
- run: **36746942724**
- artifact: **11112209814**
- artifact digest: `sha256:424378a92623b6a64b14dd11fd2682794edd62a9a7828dad5d108d78d3e833cb`
- scientific gate: **PASS**

The expanding-refit and annual-anchored semantic regime outputs reproduce Prototype Alignment V1 exactly.

## 2. Frozen V1 signals

- S1 posterior erosion: incumbent posterior <0.70 or drop >=0.20.
- S2 incumbent emission anomaly: <= training incumbent-state q10.
- S3 global predictive surprise: <= training predictive-score q10.
- S4 13D market-state jump: >= training q90.
- S5 confident raw latent-state switch: new raw state with posterior >=0.60.

V1 transition rule:
- S5, or
- at least 2 of S1..S4.

No ChHHO forecast/error/alarm information was used.

## 3. Core result — 2022-01..2026-08

### EXPANDING_REFIT

- months: 56
- transition flags: **16**
- flag rate: **28.6%**
- reference transition events: 4
- event hits: **3/4 = 75%**
- transition-zone months: 6
- flagged transition-zone months: **3/6 = 50%**
- false transitions outside transition zones: **13/50 = 26.0%**
- precision: **18.75%**

Reference event results:
- 2022-02 R1->R0: HIT at confirmation
- 2023-01 R0->R1: MISS
- 2024-04 R1->R2: HIT at confirmation
- 2026-07 R2->R1: first flag **2026-06**, one month before confirmation

### ANNUAL_ANCHORED

- transition flags: **17**
- flag rate: **30.4%**
- event hits: **3/4 = 75%**
- transition-zone recall: **3/6 = 50%**
- false transitions outside zones: **14/50 = 28.0%**
- precision: **17.65%**

Event pattern is the same:
- hits 2022-02, 2024-04, 2026 transition;
- miss 2023-01;
- first 2026 flag in June, one month before July R1 confirmation.

Binding reading:
The V1 rule has useful event sensitivity, but roughly one quarter of non-transition months are falsely classified as TRANSITION. That is too noisy for alarm weighting.

## 4. Long replay — 2015-07..2026-08

EXPANDING_REFIT:
- event hits **7/13 = 53.8%**
- transition-zone recall **44.4%**
- false-transition rate outside zones **28.4%**
- precision **19.5%**

ANNUAL_ANCHORED:
- event hits **6/13 = 46.2%**
- transition-zone recall **38.9%**
- false-transition rate outside zones **34.5%**
- precision **14.9%**

Long-history evidence therefore does not support promoting either V1 transition detector.

## 5. 2025-01..2026-08 inspected transport

EXPANDING_REFIT:
- 20 months
- 4 transition flags
- 2026 transition event HIT
- first in-zone flag: **2026-06**
- one month before 2026-07 R1 confirmation
- false transitions: **3/17 non-zone months = 17.6%**
- precision **25%**

ANNUAL_ANCHORED:
- 5 transition flags
- 2026 transition event HIT
- first in-zone flag: **2026-06**
- false transitions: **4/17 = 23.5%**
- precision **20%**

2025/2026 is already inspected and is not a threshold-fitting authority.

## 6. Mandatory checkpoints

### 2024

2024-03:
- expanding: R1 + STABLE
- annual: R1 + STABLE

2024-04:
- expanding: BELIRSIZ/R2 + **TRANSITION**
  - S1 posterior erosion
  - S2 incumbent emission anomaly
  - S3 predictive surprise
- annual: BELIRSIZ/R2 + **TRANSITION**
  - same three signals

2024-05:
- both R2 + STABLE

Thus the 2024 transition is cleanly identified.

### 2026

2026-04:
- both R2 + STABLE

2026-05:
- expanding R2 + **STABLE**
  - S1 only
- annual BELIRSIZ/R2 + **STABLE**
  - S1 only

2026-06:
- expanding R2 + **TRANSITION**
  - S2 emission anomaly
  - S3 predictive surprise
- annual R0 + **TRANSITION**
  - S1
  - S2
  - S3
  - S5 raw-state switch

2026-07:
- expanding BELIRSIZ/R1 + STABLE
  - S1 only
- annual R0 + STABLE

2026-08:
- expanding R1 + STABLE
- annual R1 + TRANSITION due S1 + S5

Therefore V1 gives an early warning in June, but not in May.

## 7. Why V1 is too noisy

Signal decomposition over the 2022-2026 core shows an important separation.

### EXPANDING_REFIT false-transition contributions
Among 13 false-transition months:
- S1: 7
- S2: 9
- S3: 7
- S4: 4
- S5: 6

Core true transition-zone hits:
- S1: 2
- S2: 3
- S3: 2
- S4: **0**
- S5: **0**

The most revealing false-transition sequence is:
- **2026-01**: S2 + S3
- **2026-02**: S2 + S3
- **2026-03**: S3 + S4

These months occur inside the long R2 episode and are exactly the kind of months previously identified as possible **within-regime extreme/stress**, not necessarily regime transition.

This is the central V1 finding:
**generic anomaly/surprise is not equivalent to transition.**

S2/S3 are useful anomaly information, but they should not by themselves force a transition classification.

S4 also produced no core transition-zone hit while contributing four false flags in the expanding detector.

S5 raw latent switches are not reliable semantic-transition evidence under monthly refits; in the expanding core they contributed to six false-transition flags and zero transition-zone hits.

## 8. Binding conclusion

V1 answers the scientific question partially:

- YES: a market-only transition layer can detect 2024-04 and can warn in 2026-06 before the July semantic confirmation.
- NO: the current fixed rule is not selective enough for operational use.

Do **not** attach V1 TRANSITION directly to alarm weights.

Do **not** loosen the rule to force a 2026-05 hit.

Do **not** tune thresholds on 2025/2026.

## 9. Next exact step

The next regime study should separate **transition evidence** from **within-regime extreme evidence**.

### Transition Detector V2 — historical-development calibration

Use only an earlier historical development period for rule calibration; 2025/2026 remain inspection only.

Transition-specific candidate features should emphasize:
- persistent posterior erosion rather than one-month anomaly;
- sustained growth of an alternative semantic regime probability / decreasing incumbent-vs-alternative margin;
- consecutive movement away from the incumbent regime profile;
- change-point persistence.

Generic surprise features:
- emission anomaly;
- predictive surprise;
- raw jump magnitude

should be moved to the later **Regime-Extreme / Within-Regime Stress** layer or used only as supporting evidence, not standalone transition votes.

V2 must be frozen before evaluating its 2025/2026 behavior.

## 10. Stage boundary

Alarm selection/weighting remains blocked.

Current regime roadmap:
- R0/R1/R2 discovery: COMPLETE
- walk-forward detection: COMPLETE
- anchored comparison: COMPLETE
- prototype semantic alignment: COMPLETE
- Transition Detector V1: COMPLETE / NOT PROMOTED
- next: **Transition Detector V2 with historical-only calibration and persistence**
- then: Regime-Extreme / Within-Regime Stress
- then: freeze market-state engine
- only then: alarm x regime x transition reliability.
