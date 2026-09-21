# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESEARCH PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESEARCH`  
**Literature parent:** Parisi, Parisi & Díaz (2008), DOI 10.1016/j.mulfin.2007.12.002  
**Status:** `FROZEN_BEFORE_ANY_V2_2025_SCORE`  
**Evidence class:** `SOURCE_CONSTRAINED_RECONSTRUCTION / HISTORICAL_RESEARCH_ONLY / NOT_EXACT_PROPRIETARY_REPLICATION`

## 1. Authority correction

The superseded `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH` implementation and result surfaces were removed from the active research branch by explicit user instruction. They remain only in Git history for audit and are not current evidence.

This V2 exists because the V1 architecture was not sufficiently faithful to the published Parisi method.

## 2. What the 2008 gold paper actually establishes

Primary source: Parisi, A., Parisi, F. & Díaz, D. (2008), *Forecasting gold price changes: Rolling and recursive neural network models*, Journal of Multinational Financial Management 18(5), 477–487.

Source-supported facts:

- native frequency: weekly gold-price changes;
- objective: one-step-ahead sign variation;
- regression target: gold-price first difference `ΔG_t`;
- exact predictor set:
  `ΔG_(t-1), ΔG_(t-2), ΔG_(t-3), ΔG_(t-4), ΔDJI_(t-1), ΔDJI_(t-2), ΔDJI_(t-3), ΔDJI_(t-4)`;
- compares feed-forward and Ward neural networks under recursive and rolling updating;
- network weights are recalculated period-by-period;
- rolling updating keeps a fixed recent-information window and drops the oldest information as new information arrives;
- different techniques and sample sizes are investigated;
- the reported Ward architecture reaching the best activation/scaling combination has **2 hidden layers and 21 neurons** and hits 57.94% of gold sign changes at the architecture-selection stage;
- the rolling Ward family is reported as the strongest dynamic family;
- block-bootstrap validation reports average rolling-Ward sign prediction 60.68% with standard deviation 2.82%;
- an ARIMA(4,1,2), selected in the source by AIC, is used as a benchmark and is reported as inferior to the rolling Ward network;
- directional success is evaluated with the Pesaran–Timmermann directional-accuracy framework.

## 3. What remains NOT_PROVEN from accessible primary material

The accessible primary record does not expose enough information to establish with certainty:

- exact allocation of the 21 neurons between the two hidden slabs/layers;
- exact activation-function pair selected for that gold architecture;
- exact output scaling interval;
- exact rolling-window-size candidate grid and selected source window;
- exact learning rate, momentum, weight initialization, calibration interval and stopping rule;
- exact historical weekly gold price source and weekly quote convention.

Therefore:
`PARISI_2008_EXACT_SOFTWARE_REPLICATION = NOT_PROVEN`.

No result from V2 may be described as an exact reproduction of the proprietary 2008 implementation.

## 4. Source-constrained Ward reconstruction

To avoid inventing an unrelated ANN, V2 uses Ward architecture evidence from the same software/methodological family.

Ward Systems / NeuroShell descriptions identify a two-hidden-slab Ward-1 network as:
- one Gaussian hidden slab;
- one Gaussian-complement hidden slab;
- both fed from the same scaled inputs and joined at the output.

The same authors' 2006 paper independently documents:
- supervised back-propagation;
- linear input scaling to `[-1,1]` so that the signs of first differences are preserved;
- Ward hidden activations built from Gaussian, Gaussian-complement and tanh slabs;
- logistic output with output de-scaling;
- fixed-window / recursive time-ordered forecasting logic;
- four-week block bootstrap with 500 bootstrap series.

V2 therefore freezes the following **reconstruction**, not an exact-replication claim:

Architecture:
- 8 input neurons;
- two parallel Ward hidden slabs;
- 21 hidden neurons total;
- Gaussian slab = 10 neurons;
- Gaussian-complement slab = 11 neurons;
- one logistic output neuron.

The 10/11 split is the deterministic near-equal allocation needed because 21 is odd. It is frozen before 2025 and is not tuned.

Scaling:
- each input column, within each rolling training sample, min-max scaled to `[-1,1]`;
- constant input -> 0;
- target `ΔG` scaled to `[0.1,0.9]` for the logistic output;
- forecast is inverse-scaled to original `ΔG` units before sign scoring.

Training:
- supervised error back-propagation;
- classical full-batch gradient descent with momentum;
- learning rate = 0.05;
- momentum = 0.50;
- maximum 1500 epochs;
- deterministic early stop after 200 epochs without training-MSE improvement > 1e-10;
- weight initialization uniform `[-0.3,0.3]`;
- fixed seed = 2008;
- no seed ensemble and no post-result optimizer search.

The learning-rate/momentum/initial-weight choices are NeuroShell-era reconstruction settings, not claimed as proven Parisi-2008 values.

## 5. Gold-Control data bridge — corrected long history

Gold:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`;
- daily research-only historical Gold series;
- available from 2010 onward;
- final-vintage / non-PIT research surface, so V2 evidence remains retrospective only.

DJIA:
- `DJIA_FRED`;
- daily close;
- available from 2016-08-29 onward.

Weekly construction:
1. inner-join Gold and DJIA on calendar date;
2. create Monday-start / Friday-ending weeks;
3. within each week, use the latest Monday–Friday date on which both series are observed;
4. use both Gold and DJIA values from that same date;
5. no interpolation or forward fill;
6. compute level first differences, not log returns;
7. assign a target to calendar year Y by its nominal Friday `week_end`.

This long-history bridge corrects the unnecessary short-history limitation of the deleted V1.

## 6. Exact feature/target equation

For target week t:

`X_t = [ΔG_(t-1), ΔG_(t-2), ΔG_(t-3), ΔG_(t-4), ΔDJI_(t-1), ΔDJI_(t-2), ΔDJI_(t-3), ΔDJI_(t-4)]`.

`y_t = ΔG_t`.

Direction:
- UP iff inverse-scaled predicted `ΔG_t > 0`;
- DOWN otherwise;
- exact zero forecast -> DOWN.

No abstention band and no direction-threshold tuning.

## 7. Rolling-window reconstruction and pre-2025 chronology

The source explicitly treats sample size as part of the model design but the exact grid is not recoverable.

V2 reconstructs the source's "search for optimal rolling sample size" using the fixed pre-registered grid:

`W ∈ {50, 75, 100, 125, 150, 175, 200, 225, 250}` weeks.

This grid is frozen before V2 scoring.

Selection protocol:
- architecture/training/scaling are fixed and are NOT searched;
- rolling-window size is selected using **2023 only**;
- every candidate produces genuine rolling one-step-ahead forecasts on identical common 2023 support;
- primary selection criterion = highest source-native sign accuracy;
- tie-break 1 = highest balanced accuracy;
- tie-break 2 = highest Pesaran–Timmermann statistic where defined;
- tie-break 3 = smaller rolling window.

After selection:
- freeze the selected window;
- replay **2024 unchanged as the pre-2025 validation checkpoint**;
- do not retune after seeing 2024;
- persist the complete configuration and 2024 result before any 2025 model score is computed;
- replay all complete Friday-ending 2025 target weeks unchanged.

2025 is a locked retrospective challenge, not pristine prospective evidence.

## 8. Source-native benchmark and robustness

Mandatory benchmarks:
- always-UP;
- always-DOWN;
- previous-week sign;
- ARIMA(4,1,2) rolling benchmark on Gold levels using the same selected rolling window where fitting succeeds.

Mandatory metrics:
- n;
- accuracy / percentage prediction sign (PPS);
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity;
- TP/TN/FP/FN;
- forecast UP/DOWN counts;
- previous-sign / always-UP / always-DOWN;
- RMSE / MAE for `ΔG`;
- Pesaran–Timmermann DA statistic and two-sided p-value.

Bootstrap robustness:
- 500 paired block-bootstrap replications;
- fixed four-week blocks, following the same authors' 2006 robustness procedure;
- fixed seed 2008;
- report mean and standard deviation of sign accuracy;
- bootstrap is robustness evidence only and cannot select/tune V2.

## 9. Binding interpretation

V2 answers:

> Does a source-constrained reconstruction of the published Parisi rolling-Ward signal, with the correct two-slab Ward structure, long Gold/DJIA history, source-native lags and period-by-period rolling retraining, show one-week Gold directional edge in 2024 and then in unchanged 2025?

Possible outcomes must be worded as:
- result for `PARISI_ROLLING_WARD_RECON_V2`;
- not an exact software replication unless the missing 2008 implementation details are independently recovered later.

No 2025 result may cause a change in:
- architecture;
- activations;
- scaling;
- optimizer;
- learning rate/momentum;
- initialization;
- rolling-window grid;
- lag structure;
- sign threshold.

No production DB write, forecast-ledger write, decision-store write, runtime promotion or PR merge is authorized.
