# GOLD MONTHLY ANN — Stage 3 Batch 3.3

Date: 2026-09-25

## Scope
Adaptive Crow Search-ANN and PSO-TLBO Hybrid ANN were executed as the final mandatory ELM-parity refinement pair.

Selection authority remained DEV only (2022-04..2024-12, n=33). 2025 transport and 2026 stress were reporting-only.

## ANN translation
ELM ridge alpha was not copied mechanically. The ANN analog is weight decay because all ANN weights, including output weights, are directly optimized.

### Adaptive Crow Search-ANN outer tuning
Tuned on chronological pre-target validation only:
- AP0
- initial flight length
- AP slope
- flight decay
- hidden width
- weight decay

### PSO-TLBO Hybrid ANN outer tuning
Tuned on chronological pre-target validation only:
- PSO w
- c1
- c2
- Vmax fraction
- PSO/TLBO mix
- TLBO gain
- hidden width
- weight decay

Both methods use population 24, 35 selection iterations, 3 independent repeats, and 15-iteration warm-start full-history refit.

## Results

| Model | DEV MAPE % | DEV MAE | DEV RMSE | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|---:|---:|
| Adaptive Crow Search-ANN | 2.49577 | 51.596 | 63.340 | 60.61 | 2.68521 | 4.54980 |
| PSO-TLBO Hybrid ANN | 2.34425 | 48.042 | 60.289 | 60.61 | 2.46744 | 4.42872 |

Reference DEV MAPE:
- Crow Search-ANN: 2.50491%
- PSO-ANN: 2.61194%
- TLBO-ANN: 2.37828%
- Adaptive TLBO-ANN: 2.24090%
- TLBO-tuned PSO-ANN: 2.28920%
- Vanilla ANN: 2.18895%
- MPA-ANN: 2.19947%

## Improvement interpretation
- Adaptive Crow reduces base Crow Search DEV MAPE from 2.50491% to 2.49577%, only about **0.37% relative improvement**. This is technically positive but small.
- PSO-TLBO Hybrid reduces base PSO DEV MAPE from 2.61194% to 2.34425%, about **10.25% relative improvement**.
- Relative to the stronger TLBO parent, the hybrid improves 2.37828% -> 2.34425%, about **1.43% relative improvement**.
- Therefore the hybrid is a genuine improvement over both primitive PSO and TLBO, but it does not beat Adaptive TLBO, Adaptive PSO, TLBO-tuned PSO, Vanilla or MPA on DEV MAPE.

## Hyperparameter audit — DEV origins

### Adaptive Crow Search-ANN
Hidden width:
- h=3: 9/33
- h=4: 17/33
- h=6: 7/33

Weight decay:
- 0: 10/33
- 1e-4: 14/33
- 1e-3: 9/33

Selected repeat:
- repeat 0: 16
- repeat 1: 8
- repeat 2: 9

Adaptive Crow controls:
- AP0: min 0.02, median 0.2730, max 0.6476, mean 0.3026
- flight0: min 0.2704, median 1.1580, max 2.1093, mean 1.1213
- AP slope: min 0, median 0.1493, max 0.7845, mean 0.2580
- flight decay: min 0.2, median 1.4115, max 2.9044, mean 1.5058

Boundary hits:
- AP0 lower: 4/33
- AP-slope lower: 6/33
- flight-decay lower: 1/33
- no material upper-bound collapse

Interpretation: tuning is active and not collapsed to one default, but the predictive gain is too small to make Adaptive Crow a leading Stage 3 candidate.

### PSO-TLBO Hybrid ANN
Hidden width:
- h=3: 5/33
- h=4: 15/33
- h=6: 13/33

Weight decay:
- 0: 8/33
- 1e-4: 14/33
- 1e-3: 11/33

Selected repeat:
- repeat 0: 11
- repeat 1: 8
- repeat 2: 14

Hybrid controls:
- w: min 0.20, median 0.5431, max 0.9448, mean 0.5350
- c1: min 0.20, median 1.9651, max 3.00, mean 1.7850
- c2: min 0.20, median 1.4917, max 3.00, mean 1.6830
- Vmax fraction: min 0.05, median 0.4297, max 0.80, mean 0.4179
- mix: min 0.0341, median 0.5095, max 1.00, mean 0.5257
- TLBO gain: min 0.0308, median 0.9926, max 1.9013, mean 0.9500

Boundary hits are sparse:
- w lower 2/33
- c1 lower 2/33, upper 2/33
- c2 lower 1/33, upper 2/33
- Vmax lower 1/33, upper 1/33
- mix upper 1/33
- TLBO gain has no boundary collapse

Interpretation: the learned hybrid is genuinely mixed. Median mix ~0.51 and TLBO gain ~0.99 show that the tuner is not degenerating into pure PSO or pure TLBO.

## Mandatory parity track summary after Batches 3.1–3.3

| Stage 3 parity model | DEV MAPE % | DEV Direction % |
|---|---:|---:|
| Adaptive TLBO-ANN | 2.24090 | 54.55 |
| Adaptive PSO-ANN | 2.26567 | 57.58 |
| TLBO-tuned PSO-ANN | 2.28920 | 69.70 |
| DE-tuned PSO-ANN | 2.30759 | 54.55 |
| PSO-TLBO Hybrid ANN | 2.34425 | 60.61 |
| Adaptive Crow Search-ANN | 2.49577 | 60.61 |

## Decision
- Adaptive Crow Search-ANN: parity experiment completed; positive but negligible improvement; do not promote to leading set.
- PSO-TLBO Hybrid ANN: successful hybrid refinement over both base PSO and base TLBO; retain as useful Stage 3 evidence, but not as current leader.
- Mandatory ELM-parity refinement track is now **complete (6/6)**.
- Next: evidence-driven ANN-specific hybrids frozen in Stage 2:
  1. MPA + SCA
  2. MPA + GA
  A CPA-based alternative is allowed only if those two fail to add DEV value.
- No 2025/2026-based retuning is permitted.
