# GOLD MONTHLY — ChHHO E/G Historical Validation V2 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Workflow:** Gold Monthly ChHHO E/G Historical Validation V2  
**Run:** **36697319930**  
**Artifact:** **11087809958**  
**Authority commit:** `f569785f9247c87e0d4fbec5808614ca81ed7a35`  
**Code commit:** `31cd6f975a97a5ef62dd9e9d60ec50c0a02346a6`  
**Workflow commit:** `94d9fc3af6704f9afd42830d2e3db4eb94adac4c`

## 1. Question

Can E and G be validated from pre-discovery history, and where possible does the canonical ChHHO model actually fail when those signals occur?

The answer differs sharply by signal.

## 2. Independent market-state evidence, 2010-2024

Baseline across 180 monthly origins:
- mean next-month absolute Gold log return: **2.639%**
- median: **2.211%**
- Q3: **3.998%**

### E-level precursor
Rule:
- Gold monthly price >20% above prior trailing-12-month mean.

Historical origins:
- 2011-08
- 2011-09
- 2020-08
- 2024-10

Results:
- events: **4**
- next-month absolute-return mean: **2.695%**
- uplift vs baseline: **1.02x**
- above baseline Q3: **1/4 = 25%**

Conclusion:
**The >20% level condition by itself is not a strong historical next-month risk detector.**

### G
Rule:
- Gold 3-month log return <= -10%.

Historical origins:
- 2013-04
- 2013-05
- 2013-06
- 2013-07
- 2016-12
- 2022-07

Results:
- events: **6**
- next-month absolute-return mean: **4.067%**
- uplift vs baseline: **1.54x**
- above baseline Q3: **4/6 = 66.7%**

Conclusion:
**G is supported as a recurring high-movement / uncertainty market-state signal.**

It is not directional: both continuation and reversal occur.

## 3. ChHHO model-specific historical evidence

Frozen error thresholds:
- AE > 63.06 USD
- APE > 2.96117%
- absolute return error > 3.00590pp

### Historical replay policy
- 2022-2024: frozen canonical ChHHO artifact used directly.
- Pre-2022: unchanged ChHHO run with earliest current-method GPR snapshot, truncated by historical origin.
- Pre-2022 runs are counterfactual same-methodology stress tests, not PIT validation.
- Unbuildable historical cases remain unbuildable.

### G model-specific evidence

Buildable pre-discovery G events:

| Target | Evidence type | AE | APE | Return error | High error? |
|---|---|---:|---:|---:|---|
| 2017-01 | counterfactual stress | 33.75 | 2.83% | 2.87pp | NO |
| 2022-08 | frozen canonical | 35.85 | 2.03% | 2.05pp | NO |

Result:
- buildable G events: **2**
- high AE: **0/2**
- high APE: **0/2**
- high return-error: **0/2**

Four earlier 2013 G events cannot be run with the unchanged ChHHO because its frozen internal training/validation minimum is not met. Those cases are reported as unbuildable rather than changing the model.

Conclusion:
**G is a historically supported market-risk signal, but pre-discovery evidence does not support it as a ChHHO high-error alarm.**

### E model-specific evidence

Buildable E-level pre-discovery cases:

| Target | E-level | Full E? | Evidence | AE | High error? |
|---|---|---|---|---:|---|
| 2020-09 | YES | **YES** | counterfactual stress | 26.68 | NO |
| 2024-11 | YES | NO | frozen canonical | 119.13 | YES |

The 2024-11 ChHHO failure does not satisfy full E because the frozen ChHHO-disagreement >5pp condition is not met; it is already captured by D.

Full E pre-discovery evidence:
- events: **1**
- target: 2020-09
- high AE: **0/1**
- high APE: **0/1**
- high return error: **0/1**

Two 2011 E-level cases are unbuildable under the unchanged main model.

Conclusion:
**Full E does not receive historical ChHHO-error validation. Its only buildable pre-discovery full-E stress case is a false alarm.**

## 4. Binding interpretation

### G
Promote only as:
**HISTORICALLY SUPPORTED HIGH-MOVEMENT / UNCERTAINTY REGIME SIGNAL**

Do not call G a validated ChHHO error alarm.

Evidence:
- strong pre-discovery market-state recurrence;
- but 0/2 buildable pre-discovery ChHHO high-error events.

### E
Downgrade from a strong alarm candidate to:
**DISCOVERY-PERIOD CHHHO DISAGREEMENT PATTERN / UNVALIDATED ERROR ALARM**

Evidence:
- E-level alone has essentially no historical movement uplift (1.02x);
- full E has only one buildable pre-discovery historical model case and it is low error;
- later 2025/2026 hits therefore cannot be treated as independent validation.

## 5. Consequence for current alarm system

E and G must not be counted as independently validated hard alarms when quoting alarm-system performance.

They may remain:
- E: research/disagreement descriptor;
- G: uncertainty-regime warning.

The validated-performance discussion should continue to distinguish them from frozen A/B/C/D transport evidence.

No routing or model switching is authorized from this result.
