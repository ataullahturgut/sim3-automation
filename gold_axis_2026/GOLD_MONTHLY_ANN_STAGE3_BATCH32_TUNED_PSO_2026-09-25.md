# GOLD MONTHLY ANN — Stage 3 Batch 3.2

Date: 2026-09-25

## Scope
TLBO-tuned PSO-ANN and DE-tuned PSO-ANN were executed as the mandatory ELM-parity meta-on-meta PSO experiments.

Selection authority remained DEV only (2022-04..2024-12, n=33). 2025 transport and 2026 stress were reporting-only.

## ANN translation
The outer optimizer tunes:
- PSO inertia w
- PSO cognitive coefficient c1
- PSO social coefficient c2
- PSO velocity-limit fraction Vmax
- ANN hidden width
- ANN weight decay

ELM ridge alpha was replaced by ANN weight decay because ANN output weights are directly optimized.

Outer tuner budget follows the ELM meta-on-meta class:
- inner PSO population 12, iterations 20
- TLBO population 6, iterations 5
- DE population 8, iterations 6
- outer score averages two independent PSO fits on the chronological validation tail

After the outer tuner freezes q=(w,c1,c2,Vmax,hidden,weight_decay), the chosen q is re-tested with:
- PSO population 24
- 45 iterations
- 3 independent repeats
- chronological validation selection
- 15-iteration warm-start full-history refit

## Results

| Model | DEV MAPE % | DEV MAE | DEV RMSE | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|---:|---:|
| TLBO-tuned PSO-ANN | 2.28920 | 47.476 | 62.160 | 69.70 | 2.82828 | 4.17474 |
| DE-tuned PSO-ANN | 2.30759 | 47.788 | 62.632 | 54.55 | 2.79166 | 4.73900 |

Reference:
- base PSO-ANN DEV MAPE: 2.61194%
- Adaptive PSO-ANN: 2.26567%
- Adaptive TLBO-ANN: 2.24090%
- Vanilla ANN: 2.18895%
- MPA-ANN: 2.19947%

## Improvement relative to base PSO
- TLBO-tuned PSO: ~12.36% relative DEV MAPE reduction.
- DE-tuned PSO: ~11.65% relative DEV MAPE reduction.
- Both clearly rescue the base PSO configuration that failed the Stage 2 RW gate.

## Hyperparameter audit — DEV origins

### TLBO-tuned PSO
Hidden width:
- h=3: 24/33
- h=4: 4/33
- h=6: 5/33

Weight decay:
- 0: 13/33
- 1e-4: 15/33
- 1e-3: 5/33

Selected repeat:
- repeat 0: 7
- repeat 1: 14
- repeat 2: 12

PSO parameter distribution:
- w: min 0.20, median 0.3364, max 0.9038, mean 0.4152
- c1: min 0.20, median 1.2770, max 2.9810, mean 1.2915
- c2: min 0.20, median 1.5465, max 3.00, mean 1.6656
- Vmax fraction: min 0.05, median 0.05, max 0.7657, mean 0.1438

Boundary hits:
- w lower bound: 8/33
- c1 lower bound: 5/33
- c2 lower: 2/33, upper: 3/33
- Vmax lower bound: 17/33

### DE-tuned PSO
Hidden width:
- h=3: 11/33
- h=4: 14/33
- h=6: 8/33

Weight decay:
- 0: 7/33
- 1e-4: 10/33
- 1e-3: 16/33

Selected repeat:
- repeat 0: 12
- repeat 1: 12
- repeat 2: 9

PSO parameter distribution:
- w: min 0.20, median 0.4934, max 0.8518, mean 0.5197
- c1: min 0.20, median 1.5489, max 3.00, mean 1.4608
- c2: min 0.20, median 1.8489, max 3.00, mean 1.8271
- Vmax fraction: min 0.05, median 0.05, max 0.7595, mean 0.1591

Boundary hits:
- w lower bound: 4/33
- c1 lower: 6/33, upper: 1/33
- c2 lower: 4/33, upper: 10/33
- Vmax lower bound: 18/33

## Interpretation
1. Both outer tuners materially improve PSO-ANN, confirming that PSO internal parameters should not be left at one fixed default on this problem.
2. TLBO-tuned PSO is the stronger of the two on DEV MAPE and, importantly, reaches 69.70% DEV direction accuracy.
3. TLBO-tuned PSO therefore offers a different profile from Adaptive TLBO-ANN: its MAPE is worse (2.28920 vs 2.24090), but its direction accuracy is much stronger (69.70% vs 54.55%).
4. DE-tuned PSO improves price error strongly versus base PSO but does not provide comparable directional benefit.
5. Both tuners frequently select the minimum Vmax fraction (0.05). This is not a total parameter collapse—other parameters and architecture choices vary materially—but it is a real boundary preference. It suggests small PSO step sizes are useful in this small-sample ANN problem and creates a future sensitivity check: test whether an even smaller Vmax lower bound changes the DEV result, without using 2025/2026.
6. DE tuner also shows a notable c2 upper-bound preference (10/33), another parameter-boundary signal that should be documented rather than silently ignored.

## Decision
- TLBO-tuned PSO-ANN: retain as a strong Stage 3 refinement, especially for price+direction balance.
- DE-tuned PSO-ANN: retain as successful parity evidence, but it is not a leading candidate.
- Do not retune based on 2025 or 2026.
- Proceed to Batch 3.3: Adaptive Crow Search-ANN + PSO-TLBO Hybrid ANN.
