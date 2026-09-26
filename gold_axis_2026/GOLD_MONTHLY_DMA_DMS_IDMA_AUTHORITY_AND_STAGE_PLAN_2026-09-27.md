# GOLD MONTHLY — DMA / DMS / IDMA AUTHORITY AND STAGE PLAN

Date: 2026-09-27
Status: PRE-OUTCOME AUTHORITY FREEZE
Project: GOLD MONTHLY FORECAST
Target: H=1 next-calendar-month average XAU/USD
Selection authority: DEV 2022-04..2024-12 only
2025/2026: reporting-only, never tuning/selection

## 1. Why this family is next

The family is supported by direct monthly gold forecasting evidence and by the core DMA literature.

Primary authority:
1. Raftery, Karny & Ettler (2010), Technometrics, "Online Prediction Under Model Uncertainty via Dynamic Model Averaging".
2. Koop & Korobilis (2012), International Economic Review.
3. Aye, Gupta, Hammoudeh & Kim (2015), International Review of Financial Analysis.
   - Direct monthly gold-return forecasting.
   - Compares TVP, DMA, DMS, BMA and RW.
   - Uses alpha=0.99, lambda=0.99, non-informative model prior, diffuse initial-state prior.
   - Finds DMA/DMS forecast well; DMS is best overall across forecast horizons.
4. Baur, Beckmann & Czudaj (2016), International Review of Financial Analysis.
   - Direct gold forecasting under model and parameter uncertainty.
   - DMA improves forecasts and favors parsimonious, time-varying predictor sets.
5. Risse & Ohl (2017), Journal of Empirical Finance.
   - Extends DMA/DMS with Dynamic Occam's Window (DOW) in a monthly one-step-ahead gold/stock setting.
6. Chen et al. (2025), International Review of Financial Analysis.
   - Introduces Iterated Dynamic Model Averaging (IDMA).
7. Chen, Yang & Lan (2026), Economics Letters.
   - Direct monthly gold-price IDMA application.
   - IDMA and standard DMA outperform other benchmarks.

## 2. Canonical mathematical contract

For model k with predictor subset x_t^(k):

y_t = x_t^(k)' beta_t^(k) + epsilon_t^(k)

beta_t^(k) = beta_(t-1)^(k) + eta_t^(k)

The state/parameter forgetting factor is lambda.
The model-probability forgetting factor is alpha.

DMA:
- maintains forecast probabilities across models;
- combines model forecasts with prior-to-target model probabilities.

DMS:
- uses the single model with the largest prior-to-target model probability.

BMA special case:
- alpha = 1, lambda = 1.

Canonical gold-DMA benchmark from Aye et al.:
- alpha = 0.99
- lambda = 0.99
- non-informative/equal prior over models
- diffuse initial state
- monthly recursive forecasting.

## 3. Project adaptation

### Target
Primary scoring target remains next-month average Gold price.
The internal regression target should be next-month Gold log return / return so that the state-space model remains consistent with gold-DMA authority; convert return forecast back to price using only origin-known previous Gold price.

### Inputs
First production family uses the existing frozen 8 origin-safe VW-MIDAS predictors.
No external predictor extension in first pass.

With 8 optional predictors:
- full subset model space = 2^8 = 256 models;
- intercept always included;
- no future information enters model-space probabilities or coefficient updates.

### 4-metal issue
Canonical authority is single-target Gold forecasting.
Therefore:
- canonical DMA/DMS/IDMA selection is Gold-only;
- no custom multi-output DMA in Stage 0/1.
A multi-metal extension can be opened only later as a clearly labelled project-specific research variant after canonical Gold evidence exists.

## 4. Chronology and leakage rules

At forecast origin t:
- all transformations use data <= t only;
- Kalman/state updates use observations available <= t only;
- model probabilities used for t+1 are prior-to-t+1 probabilities;
- realized t+1 loss cannot affect the t+1 forecast;
- tuning of alpha/lambda/predictor thresholds uses nested historical/prequential data only.

Random split prohibited.

2025 and 2026 can never select:
- alpha;
- lambda;
- predictor subset;
- model-space pruning;
- DOW threshold;
- IDMA Stepsize;
- Thres;
- ThresPara;
- TrainWin;
- TestWin;
- MaxIter;
- winning family member.

## 5. Stage plan

### STAGE 0 — Canonical benchmark and implementation verification

Run:
0A. Random Walk price benchmark.
0B. Static full-predictor regression / project linear anchor.
0C. BMA: alpha=1, lambda=1.
0D. Full-predictor TVP: lambda=0.99, one model.
0E. Canonical DMA: alpha=0.99, lambda=0.99.
0F. Canonical DMS: alpha=0.99, lambda=0.99.

Model space:
- all 256 subsets of 8 frozen predictors;
- equal initial model probabilities;
- intercept always included.

Required diagnostics:
- probabilities sum to 1 at every origin;
- finite Kalman covariance;
- finite predictive variance;
- no-future-loss invariance;
- deterministic replay;
- model-size and inclusion-probability traces;
- scientific gate.

No rescue tuning in Stage 0.

### STAGE 1 — Authority-supported DMA/DMS variants

1A. Canonical DMA 0.99/0.99.
1B. Canonical DMS 0.99/0.99.
1C. BMA 1.00/1.00.
1D. Fixed-parameter/static-model probability ablations needed to identify source of gain.
1E. Small predeclared forgetting-factor sensitivity:
    lambda in {0.95, 0.97, 0.99, 1.00}
    alpha  in {0.95, 0.97, 0.99, 1.00}

Rules:
- same-DEV grid score is diagnostic only;
- promoted alpha/lambda pair must be chosen by expanding/nested prequential tuning within DEV;
- canonical 0.99/0.99 is always reported independently.

Outputs:
- DEV SigmaAE;
- direction;
- MAE/RMSE;
- relative MAE vs RW;
- predictive log score where valid;
- average active model size;
- posterior inclusion probabilities;
- stability across DEV years.

### STAGE 2 — Dynamic Occam's Window (DOW)

Authority:
- Risse & Ohl (2017) monthly one-step-ahead state-space DMA/DMS + DOW for gold/stock.

Run:
2A. DOW-DMA.
2B. DOW-DMS.

With only 256 models, DOW is not required for computation.
It is tested as a literature-backed sparsity/adaptation mechanism.

Threshold/cut settings must be predeclared from authority or tuned only through nested prequential DEV.
No 2025/2026 selection.

### STAGE 3 — IDMA

Authority:
- Chen et al. (2025).
- Chen, Yang & Lan (2026) monthly gold IDMA.

IDMA iteratively:
1. starts from candidate predictors and alpha/lambda;
2. evaluates local training performance;
3. tests predictor inclusion/exclusion;
4. updates forgetting factors;
5. accepts updates only when a predeclared metric passes its threshold;
6. repeats until convergence/MaxIter;
7. freezes revised inputs before forecasting adjacent test block.

Hyperparameters frozen before production:
- Stepsize;
- Thres;
- ThresPara;
- TrainWin;
- TestWin;
- MaxIter;
- objective metric.

Run:
3A. IDMA-log predictive likelihood.
3B. IDMA-forecast-error objective, adapted to primary price-error metric with strictly nested history.
3C. Fixed-alpha/lambda IDMA predictor-selection ablation.
3D. Fixed-predictor IDMA alpha/lambda-calibration ablation.

Strict rule:
IDMA local optimization must be nested behind each forecast origin.
No global 2022-2024 optimum may be retroactively applied to earlier DEV origins.

### STAGE 4 — DEV filtering / family freeze

Compare:
- RW
- static anchor
- BMA
- TVP
- canonical DMA
- canonical DMS
- best nested-tuned DMA/DMS
- DOW-DMA/DMS
- IDMA variants

Selection:
1. DEV SigmaAE.
2. Direction.
3. MAE/RMSE.
4. relative MAE vs RW.
5. year stability.
6. worst month.
7. prequential predictive log score.
8. parsimony/active predictor count.
9. numerical stability.
10. forgetting-factor sensitivity.

Freeze:
- price leader;
- direction leader;
- balanced challenger;
- parsimony/interpretability representative.

### STAGE 5 — Reporting-only external periods and global comparison

After DEV freeze:
- report 2025 transport;
- report 2026 available-month stress.

Compare frozen DMA-family leaders with:
- ChHHO-ANFIS;
- DE-ABC-RBFNN;
- LMC2_RBF_M32 GPR;
- REDUCED4 ANN;
- SMA-ELMFIS where relevant.

2025/2026 cannot change the frozen family choice.

## 6. What NOT to do

- no random split;
- no global feature selection using all years;
- no alpha/lambda tuning on 2025/2026;
- no arbitrary metaheuristic screen;
- no PSO/GA/DE wrapping of DMA absent specific authority;
- no multi-output custom DMA before canonical evidence;
- no full-sample PCA/decomposition before rolling split;
- no use of realized next-month errors in current model weights.

## 7. Binding next action

Implement and run STAGE 0 only first:
- RW
- static anchor
- BMA
- TVP
- canonical DMA
- canonical DMS

Verify numerical, chronology and probability invariants.
Write run/job/artifact/commit provenance.
Only after Stage 0 audit may Stage 1 begin.

## Kontrol ve Uyum Özeti

- Gold-specific authority: PASS.
- Monthly H=1 relevance: PASS.
- DEV-only selection: REQUIRED.
- 2025/2026 exclusion: REQUIRED.
- Random split: PROHIBITED.
- DB: READ_ONLY.
- Frozen feature model space: 256 subsets.
- Canonical alpha/lambda: 0.99/0.99.
- DOW: authority-backed Stage 2.
- IDMA: authority-backed Stage 3.
- Multi-output DMA: NOT YET AUTHORIZED.
