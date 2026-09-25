# GOLD MONTHLY ANN — Stage 3 Batch 3.1

Date: 2026-09-25

## Scope
Adaptive PSO-ANN and Adaptive/Improved TLBO-ANN were executed under the frozen ANN/VW-MIDAS governance contract.

- DEV selection authority: 2022-04..2024-12 only, n=33.
- 2025 transport and 2026 stress are reporting-only.
- Random split: none.
- DB: READ_ONLY.
- Target month excluded from all fitness/tuning.
- Direct ANN optimization: all hidden/output weights and biases.
- Hidden grid: [3,4,6].
- Weight-decay grid: [0, 1e-4, 1e-3].
- Hidden activation: tanh; output: linear 4-output.
- Population 24; selection generations 45; refit generations 15; 3 repeats.

Important ANN translation note: ELM's ridge alpha was not copied mechanically. Its ANN analogue is weight decay, because the ANN has directly optimized output weights rather than an analytic ridge output layer.

## Methods

### Adaptive PSO-ANN
Adaptive schedules:
- w: 0.9 -> 0.4
- c1: 2.5 -> 0.5
- c2: 0.5 -> 2.5
- vmax: 1.6

For each origin, hidden width and weight decay are selected only on the chronological pre-target validation tail. The chosen configuration is then warm-start refit on the full pre-target history.

### Adaptive/Improved TLBO-ANN
Outer training-only tuning learns:
- teach_gain
- learn_gain
- TF=2 probability
- decay
- hidden width
- weight decay

The outer score is chronological validation MAE using only pre-target history. Final refit uses the selected configuration on full pre-target history.

## Results

| Model | DEV MAPE % | DEV MAE | DEV RMSE | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|---:|---:|
| Adaptive PSO-ANN | 2.26567 | 47.006 | 61.019 | 57.58 | 3.00291 | 4.69805 |
| Adaptive TLBO-ANN | 2.24090 | 46.067 | 56.305 | 54.55 | 2.64661 | 4.21136 |

Reference DEV MAPE:
- Vanilla ANN: 2.18895%
- MPA-ANN: 2.19947%
- DE-ABC-ANN: 2.26109%
- CPA-ANN: 2.27985%
- base PSO-ANN: 2.61194%
- base TLBO-ANN: 2.37828%

## Interpretation

### Adaptive PSO-ANN
- Improves base PSO-ANN from 2.61194% to 2.26567% DEV MAPE, an approximate **13.26% relative MAPE reduction**.
- This is a genuine rescue of a weak base PSO model: base PSO failed the Stage 2 RW gate, while Adaptive PSO comfortably beats RW on DEV (relative MAE 0.8824).
- It does not beat Vanilla ANN or MPA-ANN, and is marginally worse than DE-ABC-ANN on DEV MAPE.
- Therefore Adaptive PSO is successful as a refinement experiment, but is not the current overall ANN leader.

### Adaptive/Improved TLBO-ANN
- Improves base TLBO-ANN from 2.37828% to 2.24090% DEV MAPE, an approximate **5.78% relative MAPE reduction**.
- It becomes the **third-best DEV MAPE model currently observed after Vanilla ANN and MPA-ANN**, ahead of DE-ABC-ANN.
- DEV RMSE 56.305 is essentially level with MPA-ANN's 56.292.
- Direction accuracy remains only 54.55%, so this model is a price-error/refinement candidate rather than a directional specialist.

## Hyperparameter-selection audit

### Adaptive PSO-ANN — 33 DEV origins
Hidden width:
- h=3: 17 origins
- h=4: 11
- h=6: 5

Weight decay:
- 0: 12 origins
- 1e-4: 9
- 1e-3: 12

Selected repeat:
- repeat 0: 9
- repeat 1: 16
- repeat 2: 8

Interpretation: no single repeat or regularization level monopolizes selection; h=3 is preferred most often, suggesting the adaptive PSO frequently benefits from a slightly smaller ANN than the canonical h=4 baseline.

### Adaptive TLBO-ANN — 33 DEV origins
Hidden width:
- h=3: 8 origins
- h=4: 14
- h=6: 11

Weight decay:
- 0: 5 origins
- 1e-4: 21
- 1e-3: 7

Selected repeat:
- repeat 0: 12
- repeat 1: 8
- repeat 2: 13

Median tuned controls:
- teach_gain: 0.7791
- learn_gain: 0.9395
- TF=2 probability: 0.4817
- decay: 1.7299

Interpretation: Adaptive TLBO shows a meaningful preference for moderate weight decay (1e-4) while retaining architecture variation; tuning is not collapsing to a single boundary/default configuration.

## Decision
- Adaptive PSO-ANN: **successful refinement / retain as Stage 3 evidence**, but not a current leader.
- Adaptive TLBO-ANN: **strong Stage 3 candidate / retain in leading set**.
- No selection decision is based on 2025 or 2026.
- Continue mandatory parity track with TLBO-tuned PSO-ANN and DE-tuned PSO-ANN next.
