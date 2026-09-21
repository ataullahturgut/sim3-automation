# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH`  
**Parent literature identity:** `DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_2025_MODEL_SCORE`  
**Evidence class:** `SOURCE_GROUNDED_GOLD_CONTROL_ADAPTATION / RETROSPECTIVE_RESEARCH_ONLY`

## 1. Why this is an adaptation rather than an exact replication

Primary paper:

Parisi, A., Parisi, F. & Díaz, D. (2008), *Forecasting gold price changes: Rolling and recursive neural network models*, Journal of Multinational Financial Management 18(5), 477–487, DOI 10.1016/j.mulfin.2007.12.002.

The accessible primary record proves the following core method:
- one-step-ahead forecasting of the sign of the gold-price first difference;
- output variable `ΔG_t`;
- eight inputs: `ΔG[t-1]..ΔG[t-4]` and `ΔDJI[t-1]..ΔDJI[t-4]`;
- feed-forward and Ward neural networks are compared;
- networks are repeatedly retrained;
- rolling operation keeps recent information and sets less-recent information aside;
- the reported best Ward architecture has two hidden layers and 21 neurons;
- the paper searches combinations of activation/scaling functions and sample sizes;
- rolling Ward is the strongest reported family;
- block-bootstrap validation reports average sign accuracy 60.68% with standard deviation 2.82%.

However, the accessible primary record does **not** expose enough information to reconstruct with certainty:
- the exact allocation of the 21 neurons across the two hidden layers;
- the exact activation-function assignment in that winning gold architecture;
- the exact scaling combination;
- the exact rolling-window sizes used in the gold-paper grid;
- the proprietary training optimizer/learning-rate/momentum/stopping settings;
- the exact historical weekly gold quote/close convention.

Therefore this project MUST NOT label the executable model an exact Parisi replication.

## 2. Source-family information used to resolve only the Ward mechanism

A separate 2006 paper by the same three authors, *Modelos de Algoritmos Genéticos y Redes Neuronales en la Predicción de Índices Bursátiles Asiáticos* (Cuadernos de Economía 43(128), 251–284, DOI 10.4067/S0717-68212006000200002), provides an explicit Ward-network implementation from the same authors and period:

- supervised back-propagation;
- weekly first differences;
- linear input scaling to [-1,1] to preserve sign;
- Ward hidden slabs using Gaussian, Gaussian-complement and hyperbolic-tangent activation functions;
- logistic output followed by de-scaling;
- recursive training starts with 50 weeks;
- Ward networks are explicitly described as using distinct activation-function slabs to detect different characteristics.

This related paper is used only to define a defensible **Ward-style Gold Control adaptation** where the gold paper is silent. It is not represented as proof of the exact 2008 gold-paper hidden-layer allocation.

## 3. Gold-Control weekly data bridge

Gold source:
- `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`;
- Twelve Data XAU/USD;
- research-only daily series derived from the governed hourly NY17 lane.

DJIA source:
- `DJIA_FRED`;
- S&P Dow Jones Indices via FRED;
- private model use / no public raw redistribution.

Weekly bridge:
1. inner-join XAU and DJIA by completed calendar date;
2. group into Monday-start / Friday-ending calendar weeks;
3. use the **latest date from Monday through that Friday on which both series have an observation**;
4. take both XAU and DJIA levels from that same date;
5. label the target by the nominal Friday `week_end`, not by Monday `week_start`;
6. a 2025 target means `week_end` is in calendar year 2025, preventing the 2024-12-30→2025-01-03 week from being lost and preventing the incomplete 2025-12-29→2026-01-02 week from being misclassified as a 2025 target;
7. compute simple first differences in levels, not log returns:
   `ΔG_t = G_t - G_(t-1)`;
   `ΔDJI_t = DJI_t - DJI_(t-1)`.

This synchronous-common-date bridge is a Gold-Control adaptation. It avoids mismatched weekly endpoints and uses only completed observations.

No interpolation, forward fill or proxy substitution.

## 4. Feature/target definition

For target week t:

`X_t = [ΔG_(t-1), ΔG_(t-2), ΔG_(t-3), ΔG_(t-4), ΔDJI_(t-1), ΔDJI_(t-2), ΔDJI_(t-3), ΔDJI_(t-4)]`

`y_t = ΔG_t`.

Direction:
- UP iff predicted `ΔG_t > 0`;
- DOWN otherwise.
- exact-zero prediction -> DOWN.

No probability threshold tuning and no abstention band.

## 5. Frozen Ward-style network

Because the exact 2008 layer allocation is not recoverable, the executable adaptation preserves the two most strongly documented Ward facts without inventing a hidden partition:
- total hidden neurons = 21 from the gold paper;
- three canonical Ward activation families from the same-author 2006 method.

Executable hidden representation:
- one fully connected Ward hidden bank of 21 neurons;
- 7 Gaussian neurons: `exp(-z^2)`;
- 7 Gaussian-complement neurons: `1-exp(-z^2)`;
- 7 hyperbolic-tangent neurons: `tanh(z)`;
- one logistic output neuron.

This is intentionally labelled `GC_V1_ADAPTATION`, not the exact 2008 two-hidden-layer architecture.

Scaling at every rolling origin:
- each input column: training-window min/max -> [-1,1];
- constant input -> 0;
- target `ΔG`: training-window min/max -> [0.1,0.9];
- inverse-transform output to the original `ΔG` scale before direction scoring.

Training:
- supervised back-propagation;
- full-batch Adam, learning rate 0.01;
- maximum 2000 epochs;
- stop after 200 epochs without training-MSE improvement greater than 1e-10;
- no validation observation from the forecast target period enters stopping;
- deterministic starts `[11,29,47,71,101]`;
- at each origin, retain the start with the lowest in-window training MSE;
- no seed voting/ensemble.

Adam is an implementation adaptation because the proprietary optimizer settings of the source gold paper are not exposed. It is frozen before 2025.

## 6. Rolling-window selection frozen before 2025

The gold paper explicitly studies different sample sizes but the exact candidate sizes are not exposed in the accessible primary text.

Gold-Control candidate windows are frozen as:
- 50 weeks;
- 75 weeks;
- 100 weeks.

Rationale:
- 50 weeks is directly anchored in the same authors' 2006 recursive Ward procedure;
- 75 and 100 extend the same recent-information principle without creating a large search space.

Selection chronology:
- generate rolling one-step forecasts through 2024 only;
- compare candidates on **identical common 2024 forecast weeks**;
- primary selector: highest balanced accuracy;
- tie-break 1: highest raw accuracy;
- tie-break 2: lowest RMSE of predicted `ΔG`;
- tie-break 3: smaller rolling window.

The selected window is frozen before any 2025 model score is computed.

No architecture, scaling, optimizer, seed set, lag set or sign threshold is selected using 2025.

## 7. 2025 challenge semantics

2025 is a **locked retrospective challenge**, not a pristine prospective holdout.

After pre-2025 selection is frozen:
- run the selected rolling Ward adaptation for all complete Friday-ending 2025 target weeks;
- every 2025 forecast uses only the immediately preceding selected-window training samples;
- retrain the network period-by-period as required by the rolling methodology;
- 2025 results cannot trigger rescue tuning under this identity.

## 8. Mandatory metrics

Pre-2025 selection report and 2025 report:
- n;
- accuracy;
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity;
- TP/TN/FP/FN;
- forecast UP/DOWN counts;
- always-UP accuracy;
- always-DOWN accuracy;
- previous-week-sign accuracy;
- RMSE and MAE of predicted first difference;
- Pesaran-Timmermann directional-accuracy test where numerically defined.

Additional checks:
- complete-week/date synchronization audit;
- deterministic repeatability;
- selected-window evidence;
- weekly source-row hash.

## 9. Decision interpretation

This experiment answers only:

> Does the source-grounded Parisi rolling-Ward signal, adapted transparently to governed Gold Control XAU/DJIA data, retain useful one-week directional discrimination in the 2025 retrospective challenge?

It does not claim:
- exact reproduction of the paper's proprietary Ward implementation;
- prospective evidence;
- runtime/production authority.

No production database write, forecast-ledger write or decision-store write is authorized.
