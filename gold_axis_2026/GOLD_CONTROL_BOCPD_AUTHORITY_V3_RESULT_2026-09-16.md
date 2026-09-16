# GOLD CONTROL — BOCPD AUTHORITY-ALIGNED V3 RESULT

**Date:** 2026-09-16  
**Identity:** `BOCPD_HOURLY_VARIANCE_BMA_SUCCESSOR_V3_RESEARCH`  
**Status for GC-BREAK early warning:** `FAILED_PRE2025_VALIDATION / DO_NOT_PROMOTE_AS_STANDALONE_EARLY_WARNING`  
**Residual role:** `REGIME_CHANGE_DETECTION_CONTEXT_RESEARCH_ONLY`  
**Direction vote:** NOT PERMITTED  
**Runtime promotion:** NONE  
**Database model-output writes:** NONE

## 1. Why V3 was opened

Daily Candidate A was selective but frequently late. Hourly Candidate B gave finer timing but treated every MAP run-length contraction as a signal and produced 177 reset hours over 114 days in 2025. Candidate B was therefore too nonselective for a standalone warning role.

V3 was opened only after an authority scan and under a new identity. It does not rewrite Candidate A/B history.

## 2. Authority findings that changed the design

1. Adams & MacKay (2007), *Bayesian Online Changepoint Detection*, derives online inference for the posterior run length / most recent changepoint. Its finance illustration uses zero-mean returns with piecewise-constant variance. This supports using BOCPD as a volatility/regime-change detector rather than a directional mean predictor.
2. Wilson, Nassar & Gold (2010), *Bayesian On-line Learning of the Hazard Rate in Change-Point Problems*, shows that BOCPD output can depend strongly on a fixed, pre-specified hazard and develops online inference for hazard uncertainty. V3 therefore does not select one fixed 20/40/60/120-day hazard from a single validation year.
3. Andersen & Bollerslev (1997), *Intraday periodicity and volatility persistence in financial markets*, establishes strong intraday volatility periodicity in high-frequency financial data. V3 therefore standardizes hourly returns by a frozen hour-of-day scale before BOCPD.
4. Altamirano, Briol & Knoblauch (ICML 2023), *Robust and Scalable Bayesian Online Changepoint Detection*, demonstrates that standard BOCPD can produce spurious changepoints under misspecification/outliers. V3 therefore does not equate every MAP run-length contraction with an alert.
5. Agudelo-España et al. (2019), *Bayesian Online Prediction of Change Points*, explicitly distinguishes online changepoint **detection** from predicting the future occurrence time of a changepoint and adds residual-time inference for the latter problem. This is important to GC-BREAK: ordinary BOCPD is not, by itself, a future shock timer.

## 3. Chronology

The research chronology was frozen before V3 scoring:

- **2022:** fit intraday hour scale and zero-mean variance prior only.
- **2023:** develop/select alert mapping only.
- **2024:** locked pre-2025 validation; no reselection or rescue.
- **2025:** reused retrospective diagnostic only. Because 2025 Candidate A/B results were already visible, V3 cannot claim pristine independent 2025 challenge evidence.

The hourly state is continuous across calendar years. No 1 January reset is used.

## 4. Additional 2022 source support

The existing research-only source `XAU_USD_TWELVE_1H_RESEARCH_V1` was extended backward to 2022 without backdating its retrieval availability.

2022 backfill workflow run: `35115951166`  
Job: `104861294411`  
Retrieval run: `6a217928-e4f7-4bd7-9b0b-fc081d947de8`  
Rows fetched/written: **5,893 / 5,893**  
Duplicate writes: **0**  
Lineage: `b9a3d21b5b43a9e7537e`

Stored hourly row counts now used by the pre-2025 chronology:

- 2022: 5,893
- 2023: 5,841
- 2024: 5,910

## 5. Frozen V3 model

### Input

- Twelve Data `XAU/USD`, 1h research-only bars.
- XAU session gate frozen before scoring.
- return used only when consecutive bar-start timestamps are exactly one hour apart.
- model output from an hourly bar becomes available only after that bar completes: bar start + 1 hour.

### Intraday periodicity correction

2022-only local-hour sample standard deviations are frozen by New York bar-start hour. Raw hourly log return is divided by the corresponding 2022 hour scale.

2022 support per hour after eligibility filtering:

- minimum: 238 observations;
- maximum: 258 observations.

### BOCPD observation model

- zero-mean Gaussian returns;
- unknown variance;
- inverse-gamma conjugate variance prior;
- Student-t posterior predictive;
- 2022 pooled standardized-return prior variance: approximately `1.0024903255`.

### Hazard uncertainty

Instead of selecting one fixed hazard, five constant-hazard BOCPD filters are causally model-averaged:

- expected regime 10 days / 220 eligible hourly returns;
- 20 days / 440;
- 40 days / 880;
- 60 days / 1320;
- 120 days / 2640.

Initial weights are equal. Weights are updated only by one-step predictive evidence, never by volatility-event labels.

This is an auditable discrete approximation to hazard uncertainty; it is **not** represented as an exact implementation of the Wilson-Nassar-Gold hierarchy.

### Alert score

The alert score is posterior mass that the current run length is recent (`r <= K`), after hazard-model averaging. Candidate `K` values are 6, 12 and 22 eligible hourly observations.

Every MAP run-length drop is **not** an alert.

2023-only alert-rule candidates:

- posterior thresholds: 0.50, 0.70, 0.85, 0.95;
- persistence: 1, 2, 3 confirming hourly bars;
- clean warning horizons: 48, 72, 120 calendar hours.

A clean hit requires an alert to be available strictly before the previous governed daily close of the event and no more than the selected horizon before the event's daily-close availability.

The objective was frozen as F1 of episode precision and event recall, with deterministic tie-break rules.

## 6. Availability correction

The first V3 implementation version would have backdated a persistence-2/3 alert from the confirming bar to the first above-threshold bar. That would artificially improve apparent lead time.

This was detected before accepting any V3 result. The authoritative R2 rule is:

> an alert requiring `P` consecutive confirming bars becomes available only after the **P-th** confirming bar completes.

The earlier run is superseded and must not be used for evidence.

## 7. Authoritative R2 run

Workflow run: `35116780408`  
Job: `104864106846`  
Head SHA: `ccc58f7fda654e24de9fafec7cb4057aac684e68`  
Artifact: `bocpd-hourly-variance-bma-v3-2025-r2`  
Artifact ID: `10455198702`  
Artifact SHA-256: `1daefccb20395805c3b1bcf4b12dd6e03dd2caea1ccc031767667427e8ad3389`

2025 source cross-check remained exact:

- governed daily rows: 255;
- hourly source exact timestamp overlap: 255/255;
- exact daily-close value match: 255/255;
- maximum absolute value difference: 0.

Eligible exact-one-hour returns:

- 2022: 5,635
- 2023: 5,579
- 2024: 5,650
- 2025: 5,645

Maximum run-length truncation mass was approximately `9.68e-84`; numerical run-length truncation is therefore negligible in this replay.

## 8. 2023 development selection

The frozen 2023 selection chose:

- recent-run cutoff `K = 6` hours;
- posterior threshold `0.85`;
- persistence `1` hourly bar;
- clean warning horizon `48` calendar hours.

2023 development result:

- frozen volatility events: 17;
- alert episodes: 8;
- alert episodes followed by qualifying event: 2;
- events with qualifying prior alert: 2;
- episode precision: 25.0%;
- event recall: 11.76%;
- F1: 0.1600;
- median clean lead among detected events: 34.5 hours.

These figures are development evidence only.

## 9. 2024 locked validation — binding decision point

The 2023-selected rule was frozen and run on 2024 without reselection:

- frozen volatility events: **17**;
- alert episodes: **11**;
- qualifying signal hits: **1**;
- events with qualifying clean prior alert: **1 / 17**;
- episode precision: **9.09%**;
- event recall: **5.88%**;
- F1: **0.07143**;
- clean lead for the one detected event: **32 hours**.

This is a clear pre-2025 validation failure for a standalone GC-BREAK early-warning role. Under project governance V3 may not be rescued by changing its threshold, horizon, persistence, recent-run cutoff, hazard set, or event definition after seeing this validation result.

## 10. 2025 reused diagnostic

The exact same frozen 2023 rule was carried through 2024 state into 2025. No calendar-year reset was applied.

2025 result:

- frozen volatility events: **19**;
- alert episodes: **6**;
- clean qualifying hits inside the frozen 48-hour one-session-ahead window: **0 / 19**;
- episode precision under that frozen clean-warning definition: **0%**;
- event recall: **0%**;
- F1: **0**.

Latest-prior-alert descriptive overlay contains 12 events with some earlier strict-pre-event alert and 7 with no earlier alert, but those prior alerts are generally far outside the frozen 48-hour warning horizon. They are therefore not evidence of successful early warning.

2025 is explicitly `HISTORICAL_REPLAY_REUSED_CHALLENGE_DIAGNOSTIC`, not an independent test, and it is not used to change the V3 decision.

## 11. Scientific conclusion

The authority-aligned implementation changes the interpretation of the BOCPD programme:

- standard BOCPD is useful for **online detection/inference of regime change after new observations arrive**;
- it is not naturally a predictor of a future large-volatility day before the regime-changing evidence itself appears;
- making Candidate B more selective through a principled posterior recent-run probability removes the flood of alarms, but pre-2025 validation shows that it also removes most event-early-warning coverage;
- therefore the poor early-warning result is not adequately explained by 2023-2024 overfitting or by a 1 January 2025 cold start.

**Binding research classification:**

`BOCPD_HOURLY_VARIANCE_BMA_SUCCESSOR_V3_RESEARCH = FAILED_PRE2025_VALIDATION_FOR_STANDALONE_EARLY_WARNING`

BOCPD may remain a research **REGIME_CHANGE_DETECTION_CONTEXT** or confirmation layer. It should not be promoted as the motor whose job is to predict future large XAU volatility events.

If future-change timing is still desired from the Bayesian changepoint family, it requires a separately named predictive-duration/residual-time research line (for example the class of models studied by Agudelo-España et al. 2019), with its own pre-2025 duration model and validation. It must not be manufactured by post-hoc threshold tuning of V3.

## 12. Governance

- no runtime promotion;
- no direction vote;
- no database model-output write;
- no canonical merge authorization;
- no 2025-based threshold/horizon tuning;
- V3 result may not supersede the governed monthly BOCPD identity without explicit future promotion/change control.
