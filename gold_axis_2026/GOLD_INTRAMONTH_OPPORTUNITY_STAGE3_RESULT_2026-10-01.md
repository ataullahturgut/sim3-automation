# GOLD INTRAMONTH OPPORTUNITY — Stage 3 Predictability Screen Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / SCIENTIFIC_GATE=PASS**  
**Workflow:** Gold Intramonth Opportunity Stage3  
**Run:** **36862897415**  
**Artifact:** **11163151830**  
**Artifact digest:** `sha256:2fd22603ab47d573d47716a3e87fb380d3a2795b42af62fb194d827e1dcecff6`  
**Runner commit:** `b62d89117fcf2c4b0347f8adfcd4e1885addcf6a`  
**Authority:** `GOLD_INTRAMONTH_OPPORTUNITY_STAGE3_AUTHORITY_2026-10-01.md`

## 1. Main conclusion

Stage 3 passes, but the predictive evidence is **selective rather than broad**.

The core daily feature set does **not** reliably predict:
- general K050 opportunities,
- general K075 opportunities,
- continuous MFE5 magnitude.

It **does** show origin-safe predictive evidence for:
1. **K100 strong-upside event probability**, especially with Gold-only nonlinear features;
2. **MAE5 downside excursion magnitude**, especially with four-metal features.

Binding interpretation:

> The data do not support a generic “any short-term rally” predictor. They support a narrower detector for unusually strong five-observation upside excursions relative to current Gold volatility.

This is materially closer to the user's tactical objective: find the stronger intramonth rallies worth distinguishing from ordinary noise.

## 2. Scientific protocol

- Initial/background history: 2011-2021.
- DEV evaluation: **2022-01-01..2024-12-31**, n = **749 daily origins**.
- 2025: not evaluated or used.
- 2026: not evaluated or used.
- No random split.
- Refit every **5 Gold origins**.
- A training row enters only after its full five-observation label window has matured.
- Monthly ChHHO direction/alarm/regime is **not used as a Stage-3 feature**.
- Feature blocks:
  - G_ONLY = 11 features;
  - FOUR_METAL = 29 features.
- 24 fixed model/target/feature combinations tested.
- 7 combinations pass the pre-registered gate.

## 3. Binary opportunity targets

### 3.1 K050 — FAIL

Best:
- G_ONLY / LOGIT_L2
- Brier = **0.25385**
- best baseline = **0.25062**
- relative change = **-1.29%**
- log loss = **0.70167**
- baseline log loss = **0.69440**

Decision:
**NO PASS**.

Broad low-threshold opportunity is too common/noisy for the current core feature set.

### 3.2 K075 — FAIL

Best:
- FOUR_METAL / LOGIT_L2
- Brier = **0.23332**
- best baseline = **0.23185**
- relative change = **-0.63%**
- log loss = **0.66155**
- baseline = **0.65648**

Decision:
**NO PASS**.

Intermediate-strength opportunity is not yet forecastable better than prior-history prevalence.

### 3.3 K100 — PASS

Primary Stage-3 classifier:

**G_ONLY / HGB_CLASS**

- Brier = **0.18942**
- best matured baseline Brier = **0.19223**
- relative Brier improvement = **+1.46%**
- log loss = **0.56550**
- best baseline log loss = **0.57283**
- PR-AUC = **0.3296**
- ROC-AUC = **0.6078**
- prediction SD = **0.0902**
- gate = **PASS**.

Supporting linear comparator:

**G_ONLY / LOGIT_L2**

- Brier = **0.19015**
- relative improvement = **+1.09%**
- log loss = **0.56834**
- PR-AUC = **0.3184**
- ROC-AUC = **0.6027**
- gate = **PASS**.

Four-metal K100 variants do not pass:
- FOUR_METAL / LOGIT_L2: +0.22% Brier improvement only, log loss slightly worse;
- FOUR_METAL / HGB_CLASS: +0.20% only.

Therefore:

> For strong-upside event probability, **Gold's own recent path is more useful than the current four-metal expansion**.

## 4. What K100 means economically

K100 is not a fixed +X% event.

Definition:

`MFE5 >= SIGMA20 × sqrt(5)`

where SIGMA20 is the origin-known population standard deviation of the last 20 one-observation Gold log returns.

Across DEV:
- median K100 threshold ≈ **+2.09%**
- 25th percentile ≈ **+1.57%**
- 75th percentile ≈ **+3.10%**
- 90th percentile ≈ **+4.01%**.

Inside monthly-DOWN origins:
- median K100 hurdle ≈ **+1.94%**.

Thus K100 is approximately a volatility-adjusted “meaningful rally” detector rather than a tiny positive-move classifier.

## 5. K100 robustness diagnostics — descriptive, not selection gates

### 5.1 By DEV year

G_ONLY / HGB_CLASS Brier improvement versus the better matured baseline:

- **2022:** +0.33%
- **2023:** +2.65%
- **2024:** +1.29%
- **aggregate DEV:** +1.46%.

The gain is positive in all three DEV years, although only the aggregate pre-registered gate determines PASS.

### 5.2 By frozen monthly ChHHO direction

Monthly direction is used here only to slice the already-generated Stage-3 predictions; it was not a Stage-3 input.

K100 G_ONLY / HGB_CLASS:

#### Monthly-DOWN origins
- n = **392**
- event prevalence = **17.60%**
- model Brier = **0.14115**
- best matured baseline Brier = **0.15128**
- relative improvement ≈ **+6.70%**.

#### Monthly-UP origins
- n = **293**
- event prevalence = **33.79%**
- model Brier = **0.24182**
- best baseline = **0.23110**
- relative change ≈ **-4.64%**.

This is highly relevant to the project mission:

> The core K100 signal is substantially more useful inside the very monthly-DOWN periods where the tactical opportunity detector is needed.

However this subset finding is descriptive Stage-3 evidence and must not be converted directly into a fitted monthly gate. Stage 4 must test monthly context prospectively within DEV chronology.

## 6. Continuous upside magnitude — MFE5 FAIL

Best MFE5 candidate:

**FOUR_METAL / RIDGE**

- MAE = **0.013424**
- best baseline MAE = **0.013368**
- relative change = **-0.41%**
- RMSE = **0.017604**
- baseline RMSE = **0.017908**
- Spearman ≈ **0.109**
- gate = **FAIL**.

All MFE5 models fail the primary MAE gate.

Binding implication:

> At this stage we can detect a strong-upside event somewhat better than baseline, but we cannot honestly forecast the exact five-observation maximum upside magnitude.

Do not report an expected MFE5 point estimate as a validated production output yet.

## 7. Downside-path model — MAE5 PASS

Best:

**FOUR_METAL / HGB_REG**

- MAE = **0.011285**
- best baseline MAE = **0.011572**
- relative improvement = **+2.47%**
- RMSE = **0.014463**
- best baseline RMSE = **0.015286**
- Spearman ≈ **0.153**
- gate = **PASS**.

Other MAE5 passes:
- FOUR_METAL / HUBER: +2.28%
- G_ONLY / HUBER: +1.54%
- FOUR_METAL / RIDGE: +1.54%
- G_ONLY / HGB_REG: +1.40%.

### Stability caution

The primary MAE5 HGB improvement by DEV year is:
- 2022: about **-0.55%**
- 2023: about **-2.78%**
- 2024: about **+7.55%**.

Therefore the aggregate MAE5 gate passes, but the gain is concentrated in 2024.

Role:
- **secondary downside-risk research channel**
- not yet a standalone production risk forecast.

## 8. Feature-family interpretation

Current evidence is asymmetric:

### Strong upside event K100
Best feature block:
**G_ONLY**

Adding current cross-metal features worsens the K100 evidence.

### Downside excursion MAE5
Best feature block:
**FOUR_METAL**

Cross-metal information appears more useful for downside-path magnitude than for strong-upside-event probability.

This separation should be preserved rather than forcing one common feature block.

## 9. Binding Stage-3 frozen core

For Stage 4 incremental monthly-context testing:

### Primary opportunity classifier
- target: **K100**
- features: **G_ONLY**
- model: **HGB_CLASS**
- supporting comparator: G_ONLY / LOGIT_L2.

### Secondary risk model
- target: **MAE5**
- features: **FOUR_METAL**
- model: **HGB_REG**
- status: PASS but yearly-stability caution.

Not promoted:
- K050
- K075
- continuous MFE5
- FOUR_METAL K100.

No 2025 evidence may alter this freeze.

## 10. Artifact hashes

- `feature_availability_audit.csv`: `9f0cce7783d3c51db9e1cdcc849fd8c3e50a11ab3c1698223382e457ae452aa0`
- `stage3_dev_predictions_long.csv`: `6eb1c11ad3188c123caccb318344e0cc632bc68d8ef7d6cce181349a8d79e958`
- `stage3_metrics.csv`: `4817de423c3282f1d38104f152c266533eef8e1f26f8506cb87ac42c7f6e38b8`
- `stage3_target_status.csv`: `a81b972117c4266224f322e1ad8419630b6f0cf75d5aac8a230849e290d3a0b3`
- `STAGE3_RESULT.md`: `6d1cba5bf7e5364ae0b83787e6a58535614d663af2ec48613284a999c4b4a75d`.

## 11. Decision

**Stage 3 = PASS.**

The project has moved from:
- “intramonth rallies exist”

to:
- “a subset of strong, volatility-adjusted rallies contains modest but real origin-safe predictive information.”

Exact next stage:

**Stage 4 — Monthly Context Incremental Test**

Stage 4 must keep the Stage-3 K100 G_ONLY/HGB core frozen and test whether origin-known monthly ChHHO information improves it:
- monthly forecast direction,
- predicted monthly return magnitude,
- alarm/reliability state,
- regime/state where causally available.

The core model may not be retuned merely to favor the monthly-context experiment.
