# GOLD MONTHLY — Transition V3 Duration-Aware / Semi-Markov Hazard Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / PROMOTION FAIL  
**Binding conclusion:** explicit regime-duration information did not solve the transition problem. The selected V3 became more conservative, but lost transition recall entirely on 2022-2024 validation and also missed the 2026 expanding transition. Duration-aware threshold refinement is therefore stopped.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_TRANSITION_V3_DURATION_AWARE_AUTHORITY_2026-09-30.md`
- authority commit: `5fb95b8f8e73cbaf5285c52a14fcf0e5b93de599`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_transition_v3_duration_aware.py`
- initial code commit: `51daa1b940b4eb7ea668235e58b4e973378c0539`
- comparator-only bug-fix commit: `30888f6e63e21adfe87d2797003e896b38cbb709`

Workflow:
- `.github/workflows/gold-monthly-market-regime-transition-v3-duration-aware.yml`
- workflow commit: `5a8736aadbe72f75a3cc10ec333c63a3571bf877`

Final valid execution:
- workflow: **Gold Monthly Market Regime Transition V3 Duration Aware**
- run: **36759519056**
- artifact: **11118042872**
- artifact digest: `sha256:ff1c0dbe03382cf5e360523bda47f51fd98bb270da907a86bfbfec2536f952b2`
- scientific gate: **PASS**

Non-scientific failed run:
- run **36759215106** failed only while computing the V2 comparator after the V3 detector had run.
- cause: comparator rows did not contain the V3-only duration field `completed_spell_pool_size`.
- the fix isolated comparator metrics; it did **not** change the preregistered V3 detector, grid, calibration objective, or thresholds.

## 2. Method

V3 was an explicit-duration semi-Markov hazard overlay on the frozen HMM/prototype regime engine.

For each incumbent semantic regime:
- historical completed spell lengths were extracted using only information available at the origin;
- current regime spell age was measured;
- empirical age percentile was calculated;
- Jeffreys-smoothed exit hazard was calculated;
- duration evidence was combined with incumbent posterior deterioration and alternative-regime probability growth.

The final rule had:
- duration-gated MODERATE branch;
- duration-independent STRONG-break branch;
- optional 1/2-month persistence.

No forecast/error/alarm data was used.

## 3. Frozen calibration search

Calibration:
- EXPANDING_REFIT
- 2015-07..2021-12 only.

Grid:
- **20,736** preregistered candidate rules.

Primary eligibility:
- non-zone false-transition rate <= **15%**.

Result:
- **0 / 20,736 candidates met the <=15% false-transition eligibility rule.**
- preregistered fallback therefore activated.

Selected fallback rule:
- age percentile >= **0.60**
- smoothed duration hazard >= **0.15**
- alternative posterior >= **0.20**
- alternative growth >= **0.05** or incumbent drop >= **0.10**
- MODERATE persistence = **2 months**
- STRONG alternative posterior >= **0.70**
- STRONG margin <= **0.00**
- STRONG growth >= **0.15** or strong incumbent drop >= **0.20**

## 4. Calibration result — 2015-07..2021-12

EXPANDING:
- months: 78
- duration pool available: **64/78 = 82.1%**
- transition flags: **13**
- reference transition events: 9
- event hits: **2/9 = 22.2%**
- transition-zone recall: **16.7%**
- false transitions: **11/66 = 16.7%**
- precision: **15.4%**
- mean lead among hits: 0 months

Therefore the historical calibration itself was weak:
- false rate remained above the desired 15%;
- most genuine transition events were missed.

ANNUAL with the same frozen rule was worse:
- event hits: **0/9**
- false-transition rate: **21.2%**
- precision: **0%**.

## 5. Later validation — 2022-01..2024-12

This period did not participate in selection.

### EXPANDING_REFIT

- months: 36
- duration pool available: **36/36**
- transition flags: **4**
- reference transition events: 3
- event hits: **0/3 = 0%**
- zone recall: **0%**
- false transitions: **4/33 = 12.1%**
- precision: **0%**

V3 did reduce the false-transition rate below 15%, but only by becoming too conservative: **every validation transition was missed**.

Missed:
- 2022-02 R1 -> R0
- 2023-01 R0 -> R1
- 2024-04 R1 -> R2

Promotion gate:
- event-hit >=2/3: **FAIL**
- false rate <=15%: PASS
- precision V2+5pp: **FAIL**
- overall: **FAIL**

### ANNUAL_ANCHORED

- event hits: **0/3**
- false transitions: **3/33 = 9.1%**
- precision: **0%**

Same conclusion: lower false rate was purchased by losing the true transitions.

## 6. Why 2024-04 was missed

2024-03:
- R1
- spell age 14 months in expanding;
- age percentile 0.90;
- STABLE.

2024-04:
- incumbent posterior collapsed from about 0.982 to 0.024;
- alternative posterior rose to about 0.555;
- incumbent-vs-alternative margin became negative;
- regime spell age reached 15 months;
- duration age percentile about 0.778;
- MODERATE condition became true.

But the selected historical rule required:
- **2-month persistence** for MODERATE; and
- >=0.70 alternative posterior for immediate STRONG.

So 2024-04 was not flagged.

This shows the core trade-off:
- duration/persistence suppresses false calls;
- but monthly regime changes can occur too abruptly for a two-month duration gate.

## 7. Opened 2025-2026 result

### EXPANDING_REFIT

- duration pool available: 20/20
- transition flags: **0**
- 2026 R2 -> R1 event hit: **MISS**
- false-transition rate: **0%**
- precision: NA

This is not useful operationally: zero false calls, but also zero transition calls.

### ANNUAL_ANCHORED

- transition flags: 2
- 2026 event hit: YES
- first in-zone flag: **2026-06**
- one month before July R1 confirmation
- false transitions: **1/17 = 5.9%**
- precision: **50%**

However the annual schedule retains its known semantic/dynamics instability and this opened evidence cannot override the failed validation.

## 8. 2026 expanding checkpoint

- 2026-04: R2 + STABLE; spell age 24; age percentile 1.0.
- 2026-05: R2 + STABLE; spell age 25; age percentile 1.0; MODERATE raw condition true, but 2-month persistence not yet satisfied.
- 2026-06: R2 + STABLE; spell age 26; directional evidence recovers, so moderate persistence breaks.
- 2026-07: BELIRSIZ/R1 + STABLE; large posterior break but alternative posterior about 0.508, below STRONG 0.70 threshold.
- 2026-08: R1 + STABLE.

Thus V3 misses exactly the recent transition that motivated the experiment.

## 9. Scientific conclusion

The hypothesis tested was:

> regime age / exit hazard can make transition detection more selective without losing real transitions.

Under this preregistered V3 candidate family, the answer is **NO**.

Duration information is real and measurable:
- the 2026 R2 spell is extraordinarily long;
- by 2026-04/05 its age percentile is already 1.0.

But duration alone does not tell us **when** the regime will break.

The duration gate makes the detector conservative but cannot resolve the timing problem:
- false calls fall;
- true transition recall collapses.

## 10. Binding decision

**Transition V3 is rejected.**

Do not:
- loosen the V3 thresholds using 2024/2026 outcomes;
- remove persistence because 2024/2026 were missed;
- lower the strong alternative threshold to force May/July 2026;
- connect V3 to ChHHO or alarms.

Per the preregistered authority, **threshold-level transition refinement stops here**.

Current transition evidence:
- V1: too noisy.
- V2: detects 2024/2026 well but historically too many false transitions.
- V3 duration-aware: more selective but misses genuine transitions.

Therefore no current Transition detector is operationally promoted.

## 11. What remains valid

- R0/R1/R2 regime identity remains useful descriptive structure.
- Extreme V1 remains a frozen descriptive same-regime stress layer.
- Transition remains a research/descriptive concept, not an operational alarm gate.
- The 2025-2026 association between V2 transition origins and large ChHHO errors remains interesting but unvalidated historically.

If the transition question is pursued again, it must be a genuinely different statistical architecture, such as a dedicated multivariate changepoint model rather than another HMM-threshold/duration rule.

Alarm weighting remains unauthorized.
