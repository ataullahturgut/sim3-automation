# GOLD MONTHLY ANN — Stage 3 Batch 3.4 Evidence-Driven Hybrids

Date: 2026-09-25

## Scope
Two ANN-specific optimizer hybrids frozen by Stage 2 complementarity analysis were executed:
1. MPA + SCA Hybrid ANN
2. MPA + GA Hybrid ANN

Unlike a forecast ensemble, these are optimizer-level hybrids acting on one shared ANN weight population.

## Hybrid mechanism
At each generation:
- retain the incumbent population;
- generate one full candidate population with the Stage-1 MPA operator;
- generate one full candidate population with the second optimizer (SCA or GA);
- combine all three pools;
- keep the best 24 candidates using inner-training weighted MAE only.

No fixed 50/50 mix coefficient is imposed. Operator contribution is learned implicitly through survival. Chronological validation does not drive population evolution; it only selects among top training candidates under the frozen common ANN protocol.

Architecture is deliberately frozen to the canonical Stage-1 ANN (8 -> 4 tanh -> 4 linear) to isolate the effect of optimizer hybridization.

## Authority
- DEV selection authority: 2022-04..2024-12, n=33.
- 2025 transport and 2026 stress: reporting only.
- Random split: none.
- DB: READ_ONLY.
- Target month excluded from fitness.
- Same population 24, 45 selection generations, 15 refit generations, 3 deterministic repeats.

## Results

| Model | DEV MAPE % | DEV MAE | DEV RMSE | DEV Direction % | Win vs RW | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|---:|---:|---:|
| MPA+SCA Hybrid ANN | 2.23957 | 46.017 | 57.947 | 60.61 | 57.58% | 2.70259 | 4.52720 |
| MPA+GA Hybrid ANN | 2.48841 | 51.361 | 63.086 | 51.52 | 48.48% | 2.63731 | 4.71151 |

Reference DEV:
- MPA-ANN: MAPE 2.19947%, direction 57.58%.
- SCA-ANN: MAPE 2.36197%, direction 72.73%.
- GA-ANN: MAPE 2.36033%, direction 63.64%.
- Adaptive TLBO-ANN: MAPE 2.24090%.
- Vanilla ANN: MAPE 2.18895%.

## MPA + SCA interpretation
- DEV MAPE 2.23957% is slightly better than Adaptive TLBO-ANN (2.24090%) but worse than the MPA parent (2.19947%).
- Relative to MPA, price error worsens by ~1.82%, while direction rises from 57.58% to 60.61%.
- Relative to SCA, price error improves by ~5.18%, while direction falls from 72.73% to 60.61%.
- Therefore this hybrid is not a new price-error leader; it creates a price/direction/stability trade-off.

### DEV yearly behavior
- 2022 MAPE: 2.16977%
- 2023 MAPE: 2.09446%
- 2024 MAPE: 2.43703%
- yearly-MAPE SD: 0.1470

For comparison, MPA-ANN yearly-MAPE SD was ~0.3698. Thus MPA+SCA substantially stabilizes MPA across DEV years, even though aggregate MAPE becomes slightly worse.

### Learned operator survival
Mean selected-repeat survivor shares across 33 DEV origins:
- incumbent/memory: 44.78%
- MPA proposals: 45.87%
- SCA proposals: 9.35%

Mean refit shares:
- incumbent: 49.81%
- MPA: 42.93%
- SCA: 7.26%

Interpretation: the hybrid does not collapse fully to MPA, but MPA/memory dominates. SCA contributes a small, persistent survivor stream that is sufficient to change the error/direction/stability profile.

## MPA + GA interpretation
- DEV MAPE 2.48841%, worse than both MPA (2.19947%) and GA (2.36033%).
- DEV direction 51.52%, also worse than both MPA (57.58%) and GA (63.64%).
- It is therefore dominated by both parents on the principal DEV objectives.

### DEV yearly behavior
- 2022 MAPE: 2.40833%
- 2023 MAPE: 2.30745%
- 2024 MAPE: 2.72944%
- yearly-MAPE SD: 0.1799

### Learned operator survival
Mean selected-repeat survivor shares:
- incumbent: 24.53%
- MPA: 28.22%
- GA: 47.25%

Mean refit shares:
- incumbent: 27.92%
- MPA: 25.37%
- GA: 46.71%

Interpretation: GA becomes the dominant active operator and the resulting search loses the strong MPA price profile. The hybrid mechanism is functioning, but this operator combination is not useful for this ANN problem.

## Decision
- **MPA+SCA Hybrid ANN:** retain as a useful balanced/stability hybrid candidate, but do not call it a price leader because it does not beat MPA.
- **MPA+GA Hybrid ANN:** reject from leading Stage 3 set; dominated by both parents on DEV.
- Because the frozen Stage 2 plan allowed a CPA-based alternative if the first two evidence-driven hybrids failed to add sufficient DEV value, the condition is now met for one final controlled alternative:
  **MPA + CPA Hybrid ANN**.
  Rationale: MPA+GA clearly fails; MPA+SCA adds multidimensional stability/direction value but does not improve MPA DEV MAPE.
- No combinatorial expansion beyond this one CPA alternative is permitted.
- 2025/2026 are not used to trigger or choose this alternative.
