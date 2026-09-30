# GOLD MONTHLY — Within-Regime Extreme / Stress Detector V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / DESCRIPTIVE CANDIDATE PASS  
**Binding conclusion:** the market-only Extreme layer is selective, materially distinct from Transition V2, and cleanly identifies the 2026 Jan–Mar R2 stress episode as within-regime EXTREME rather than transition. It also identifies 2026-06 as an R2 extreme month under EXPANDING_REFIT. This layer is descriptive only; it is not yet an alarm-weighting gate.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_EXTREME_V1_AUTHORITY_2026-09-30.md`
- authority commit: `6168ded0d04935628072bab2a57bdc60c4dd91a5`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_extreme_v1.py`
- code commit: `6469281e37a52573e2cf6b998f197c19852749a6`

Workflow:
- `.github/workflows/gold-monthly-market-regime-extreme-v1.yml`
- workflow commit: `3131f1cfcb3ab3f1bb8bf3e8c82b4b6f2a4e49ce`

Execution:
- workflow: **Gold Monthly Market Regime Extreme V1**
- run: **36752189037**
- artifact: **11115570221**
- artifact digest: `sha256:9f691d55da804b821f17e106d3640cc810bece64fd751b550f1176b08a019a8a`
- scientific gate: **PASS**

## 2. Frozen detector

Eligibility:
- same raw latent state at t-1 and t;
- both posteriors >= 0.60.

If not eligible:
- `DEFER`.

For eligible months:
- E1 = state emission tail <= training same-state q10;
- E2 = predictive log score <= training q10;
- E3 = distance to posterior-weighted same-state 13D standardized center >= training same-state q90;
- E4 = 13D month-to-month jump >= training q90.

Rule:
- at least 2 signals => `EXTREME`;
- otherwise => `NORMAL`.

No threshold search was performed.

The decision rule does not use:
- semantic prototypes;
- Transition V2;
- forecast errors;
- forecast values;
- alarm labels.

Prototype semantic labels and Transition V2 are attached only after Extreme status is computed for reporting.

## 3. Diagnostic gate

Primary EXPANDING_REFIT:

Historical 2015-07..2021-12:
- eligible months: **60/78**
- EXTREME: **11**
- EXTREME rate among eligible: **18.33%**
- selectivity target 5–30%: **PASS**

Later validation 2022-01..2024-12:
- eligible months: **26/36**
- EXTREME: **4**
- EXTREME rate among eligible: **15.38%**
- selectivity target 5–30%: **PASS**

Validation overlap with Transition V2:
- EXTREME also TRANSITION: **0/4 = 0%**
- distinctness target <50%: **PASS**

Overall descriptive-candidate gate:
- **PASS**

This is important: Extreme V1 is not simply re-labelling Transition V2.

## 4. Historical behavior

### EXPANDING_REFIT — 2015-07..2021-12

Extreme months:
- 2015-11
- 2016-02
- 2017-02
- 2017-09
- 2018-01
- 2018-09
- 2018-12
- 2019-04
- 2019-06
- 2019-08
- 2020-03

Rate:
- **11/60 eligible = 18.3%**

Transition V2 overlap:
- both: **1**
- Extreme-only: **10**
- Transition-only: **18**
- share of Extreme also Transition: **9.1%**

Thus the two layers are mostly measuring different phenomena historically.

### ANNUAL_ANCHORED — historical

- eligible: 59
- EXTREME: 15
- EXTREME rate: **25.4%**
- overlap with Transition V2: **0%**

Annual produces longer extreme runs, notably 2016-05..2016-08 and 2020-03..2020-05.

## 5. Later validation — 2022-01..2024-12

### EXPANDING_REFIT

Extreme months:
- **2022-07**
- **2022-09**
- **2022-11**
- **2023-12**

All four are Extreme-only; none overlaps Transition V2.

Rate:
- **4/26 eligible = 15.4%**

### ANNUAL_ANCHORED

Extreme months:
- 2022-04
- 2022-09
- 2022-10

Rate:
- **3/26 = 11.5%**

Again, no overlap with Transition V2.

## 6. 2024 transition checkpoint

EXPANDING:
- 2024-03: R1 + NORMAL / Transition STABLE
- 2024-04: `DEFER` / Transition **TRANSITION**
- 2024-05: R2 + NORMAL / Transition STABLE
- 2024-06: R2 + NORMAL / Transition STABLE

This is the intended separation:
- the actual regime-change month is not called EXTREME;
- it is deferred by the same-state eligibility rule and left to the Transition layer.

## 7. Critical 2026 result

### EXPANDING_REFIT

| Month | Regime | Extreme status | Transition V2 |
|---|---|---|---|
| 2026-01 | R2 | **EXTREME** | STABLE |
| 2026-02 | R2 | **EXTREME** | STABLE |
| 2026-03 | R2 | **EXTREME** | STABLE |
| 2026-04 | R2 | NORMAL | STABLE |
| 2026-05 | R2 | NORMAL | **TRANSITION** |
| 2026-06 | R2 | **EXTREME** | STABLE |
| 2026-07 | BELIRSIZ/R1 | DEFER | **TRANSITION** |
| 2026-08 | R1 | DEFER | STABLE |

This cleanly separates the two phenomena that V1 Transition had mixed together.

### 2026-01
- EXTREME, 3 signals:
  - E1 emission tail
  - E2 predictive surprise
  - E3 within-state 13D distance
- raw-state posterior essentially 1.0
- therefore: very confident R2 identity, but unusual R2 market state.

### 2026-02
- EXTREME, same E1+E2+E3 pattern
- again highly confident R2.

### 2026-03
- EXTREME via:
  - E2 predictive surprise
  - E4 large market-state jump
- still highly confident R2.

### 2026-04
- NORMAL R2.

### 2026-05
- NORMAL under Extreme layer;
- TRANSITION under V2.
- This is exactly the desired conceptual separation: not an extreme same-regime month, but a directional regime deterioration month.

### 2026-06
- EXTREME under expanding:
  - E1 emission tail
  - E2 predictive surprise
  - E3 within-state 13D distance
- still R2 under expanding.
- V2 expanding says STABLE in June.
- This month therefore looks like a same-R2 stress/extreme observation rather than a clean directional transition under expanding.

### 2026-07
- DEFER because same-regime confidence is broken;
- Transition V2 = TRANSITION.

### 2026-08
- R1 but DEFER because prior/current raw-state continuity/confidence rule is not yet satisfied.
- This prevents an immediate new-regime month from being mislabeled NORMAL/EXTREME.

## 8. Transport summary — 2025-01..2026-08

EXPANDING:
- eligible: **16/20**
- EXTREME: **4**
- rate among eligible: **25%**
- extreme months:
  - 2026-01
  - 2026-02
  - 2026-03
  - 2026-06
- Transition V2 overlap: **0%**

ANNUAL:
- eligible: 17/20
- EXTREME: **3**
- rate: **17.6%**
- extreme months:
  - 2026-01
  - 2026-02
  - 2026-03
- Transition V2 overlap: **0%**

Thus both schedules independently identify Jan–Mar 2026 as a coherent R2 extreme episode.

## 9. Binding interpretation

The earlier conceptual split is now empirically supported:

### Transition
Answers:
> Is the incumbent regime losing dominance / moving toward another regime?

Example:
- 2026-05 = R2 + TRANSITION.

### Extreme
Answers:
> Is the market highly unusual relative to its current, still-persistent latent regime?

Examples:
- 2026-01 = R2 + EXTREME
- 2026-02 = R2 + EXTREME
- 2026-03 = R2 + EXTREME

The layers are not duplicates:
- 2022-2024 validation overlap = **0%**
- 2025-2026 overlap = **0%**.

## 10. Important limitation

Extreme V1 has no independent "ground-truth extreme" label. Its scientific support is:
- strict ex-ante market-only construction;
- training-distribution quantiles;
- no threshold search;
- stable selectivity across historical and validation periods;
- clear separation from Transition V2.

It is therefore a **descriptive market-state candidate**, not yet proof that EXTREME months predict larger ChHHO errors or warrant alarm reweighting.

That downstream relationship must be evaluated only after this detector is frozen.

## 11. Binding decision / next step

Extreme V1 is retained as a frozen descriptive layer.

Current market-state representation can now be expressed as separate dimensions:

- semantic regime: R0 / R1 / R2 / BELIRSIZ;
- transition status: current V2 remains research-only, not promoted;
- within-regime state: NORMAL / EXTREME / DEFER.

Next stage should **not** retune Extreme V1.

Before alarm weighting, perform a frozen downstream audit:
- compare ChHHO forecast error distributions for NORMAL vs EXTREME, separately from TRANSITION/DEFER;
- do this without changing any regime/extreme threshold;
- report by regime where event counts permit;
- treat 2025/2026 as opened descriptive evidence, not untouched model-selection data.

This audit will answer whether the market-state layers are actually informative about main-model forecast reliability.

Alarm weighting remains unauthorized until that audit is complete.
