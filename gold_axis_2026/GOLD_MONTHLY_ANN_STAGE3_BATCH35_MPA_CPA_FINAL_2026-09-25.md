# GOLD MONTHLY ANN — Stage 3 Batch 3.5 Final MPA+CPA Fallback

Date: 2026-09-25

## Scope
This is the single controlled CPA fallback authorized by the frozen Stage 2 plan after:
- MPA+GA failed;
- MPA+SCA added balance/stability value but did not improve the MPA parent on aggregate DEV MAPE.

No further ANN-specific optimizer hybrid combinations are permitted after this test.

## Method
Optimizer-level hybrid on the frozen canonical ANN (8 -> 4 tanh -> 4 linear).

At each generation:
1. incumbent population;
2. one full MPA proposal population;
3. one full CPA proposal population;
4. best 24 survive using inner-training weighted MAE only.

CPA and MPA receive equal proposal budgets. There is no fixed mix coefficient. Operator contribution is learned implicitly by survivor competition.

Validation does not drive population evolution; it is used only under the common chronological top-training-candidate selection rule.

## Authority
- DEV selection authority: 2022-04..2024-12, n=33.
- 2025 transport and 2026 stress: reporting only.
- Random split: none.
- DB: READ_ONLY.
- Target month excluded from all tuning/fitness.
- Population 24; 45 selection generations; 15 refit generations; 3 repeats.

## Results

| Model | DEV MAPE % | DEV MAE | DEV RMSE | DEV Direction % | Win vs RW | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|---:|---:|---:|
| MPA+CPA Hybrid ANN | 2.56713 | 52.320 | 65.602 | 57.58 | 48.48% | 2.48144 | 4.43815 |

Reference DEV:
- MPA-ANN: MAPE 2.19947%, direction 57.58%.
- CPA-ANN: MAPE 2.27985%, direction 60.61%.
- RW benchmark MAPE: 2.58882%.

## Parent comparison
- Versus MPA: MAPE worsens 2.19947% -> 2.56713%.
- Versus CPA: MAPE worsens 2.27985% -> 2.56713%.
- Direction equals MPA (57.58%) and is below CPA (60.61%).
- The hybrid is therefore dominated by both parents on the main DEV price-error objective and offers no directional compensation.

## DEV yearly behavior
- 2022 MAPE: 3.11026%
- 2023 MAPE: 2.21755%
- 2024 MAPE: 2.50936%
- yearly-MAPE SD: 0.37166

For comparison, MPA-ANN yearly-MAPE SD was ~0.3698. The hybrid therefore does not improve the principal MPA year-stability weakness.

## Learned operator survivor shares

Mean selected-repeat survivor shares across 33 DEV origins:
- CPA: 56.32%
- MPA: 23.02%
- incumbent/memory: 20.66%

Mean refit survivor shares:
- CPA: 57.83%
- MPA: 21.39%
- incumbent: 20.78%

Interpretation:
- The shared-population mechanism is functioning; it does not collapse to a fixed configured mix.
- However, training selection strongly favors CPA proposals.
- That CPA dominance destroys the strong MPA aggregate price profile without delivering a compensating direction or stability gain.
- This is evidence against further MPA+X combinatorial optimizer search under the current small-sample ANN setting.

## Final Stage 3 evidence-driven hybrid decisions
- MPA+SCA: RETAIN as balanced/stability hybrid evidence; not a price leader.
- MPA+GA: REJECT; dominated by parents.
- MPA+CPA: REJECT; dominated by parents and CPA-dominated survivor dynamics.
- No further ANN-specific optimizer hybrids are authorized.

## Stage 3 closure

### Mandatory ELM-parity refinements — completed 6/6
1. Adaptive PSO-ANN — DEV MAPE 2.26567%
2. TLBO-tuned PSO-ANN — 2.28920%, direction 69.70%
3. DE-tuned PSO-ANN — 2.30759%
4. Adaptive/Improved TLBO-ANN — 2.24090%
5. Adaptive Crow Search-ANN — 2.49577%
6. PSO-TLBO Hybrid ANN — 2.34425%

### ANN-specific evidence-driven hybrids
- MPA+SCA — 2.23957%, retain as balance/stability evidence
- MPA+GA — 2.48841%, reject
- MPA+CPA — 2.56713%, reject

### Current important DEV reference set
- Vanilla ANN — 2.18895%
- MPA-ANN — 2.19947%
- MPA+SCA Hybrid — 2.23957%
- Adaptive TLBO-ANN — 2.24090%
- DE-ABC-ANN — 2.26109%
- Adaptive PSO-ANN — 2.26567%
- CPA-ANN — 2.27985%
- TLBO-tuned PSO-ANN — 2.28920% / direction 69.70%
- SCA-ANN — direction leader 72.73%

## Final decision
**AŞAMA 3/5 is complete.**

Next governed stage: **AŞAMA 4/5 — ANN Ensemble**.
Before running it, recover the exact ELM ensemble components, weight-learning protocol and prior result definitions so ANN ensemble parity is implemented correctly. Ensemble weights must be learned using pre-2025 chronological evidence only; fixed default weights are not permitted except the simple-average benchmark.
