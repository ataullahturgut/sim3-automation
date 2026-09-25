# GOLD MONTHLY ANN — Stage 2 Batch 2.1 DEV-only Filtering Audit

Date: 2026-09-25

## Authority
- Source: GitHub Actions artifacts from ANN Phase A batches 1.1–1.8; no model results were re-invented or copied from prose.
- Selection authority: DEV only, 2022-04..2024-12, n=33.
- 2025 transport and 2026 stress fields exist in source artifacts but are excluded from all filtering and shortlist decisions.
- Random split: none. DB authority remains READ_ONLY from Stage 1 gates.
- RW DEV benchmark: MAPE 2.5888209463%, MAE 53.2727272727.

## Metrics used
- Price error: MAPE, MAE, RMSE.
- Direction: monthly direction accuracy.
- Benchmark relation: relative MAE vs random walk and monthly win rate vs RW.
- Tail/origin risk: worst APE and p90 APE across 33 DEV origins.
- Year stability: DEV MAPE by 2022/2023/2024 plus SD/range across those yearly MAPEs.
- Repeat evidence: median coefficient of variation of the three inner-validation fitness values per origin.
- Limitation: repeat CV measures validation-fitness dispersion, not forecast-output variance; it must not be described as a full seed-forecast stability test.

## Predeclared DEV-only filtering logic
1. RW gate: require DEV MAPE < 2.58882% AND relative MAE < 1.0. 24/33 pass.
2. Core price gate: keep models within +10% of Vanilla ANN DEV MAPE (2.18895% -> threshold 2.40784%) while passing the RW gate.
3. Direction rescue: keep RW-pass models with DEV direction accuracy >= 66.67%.
4. Stability rescue: keep RW-pass models with yearly-MAPE SD <= 0.13 and median repeat-validation CV <= 0.035; Vanilla is exempt from repeat CV because its training procedure is not the metaheuristic-repeat protocol.
5. Redundancy prune: WOA-ANN and FA-ANN are removed because within the retained pool they are dominated on MAPE, MAE, RMSE, direction, yearly stability and worst APE by other retained candidates; they add no unique role.
6. Pareto cross-check: all nine RW-eligible Pareto-nondominated models on MAPE/RMSE/direction/year-stability remain in the shortlist.

## Batch 2.1 shortlist — 12/33
| Model | Role | DEV MAPE % | MAE | RMSE | Dir % | Rel MAE | Win vs RW | Worst APE % | 2022 MAPE | 2023 MAPE | 2024 MAPE | Year SD | Repeat CV med | Pareto |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| Vanilla ANN | baseline / price | 2.18895 | 44.873 | 58.308 | 54.55 | 0.8423 | 0.515 | 7.079 | 2.229 | 2.081 | 2.266 | 0.0800 | n/a | Y |
| MPA-ANN | price leader | 2.19947 | 44.592 | 56.292 | 57.58 | 0.8370 | 0.515 | 7.865 | 2.735 | 1.843 | 2.154 | 0.3698 | 0.0350 | Y |
| DE-ABC-ANN | price + direction / hybrid-parity | 2.26109 | 46.504 | 58.612 | 66.67 | 0.8730 | 0.515 | 5.716 | 2.012 | 2.234 | 2.475 | 0.1894 | 0.0454 | Y |
| CPA-ANN | price | 2.27985 | 47.220 | 63.017 | 60.61 | 0.8864 | 0.515 | 7.062 | 2.257 | 1.932 | 2.645 | 0.2912 | 0.0458 |  |
| FA-FPA-ANN | price / hybrid-parity | 2.28398 | 46.824 | 60.129 | 60.61 | 0.8790 | 0.515 | 6.896 | 2.415 | 2.078 | 2.392 | 0.1540 | 0.0509 | Y |
| ACO-ANN | balanced price-RMSE-direction | 2.35494 | 48.520 | 58.421 | 63.64 | 0.9108 | 0.485 | 6.348 | 2.181 | 2.267 | 2.573 | 0.1683 | 0.0539 | Y |
| GA-ANN | year-stable balanced | 2.36033 | 48.120 | 59.585 | 63.64 | 0.9033 | 0.545 | 6.285 | 2.298 | 2.367 | 2.400 | 0.0427 | 0.0465 | Y |
| SCA-ANN | direction leader | 2.36197 | 48.147 | 60.330 | 72.73 | 0.9038 | 0.576 | 6.628 | 2.779 | 1.976 | 2.435 | 0.3289 | 0.0449 | Y |
| Krill Herd-ANN | direction + RW win rate | 2.37501 | 48.186 | 62.818 | 66.67 | 0.9045 | 0.606 | 7.913 | 2.552 | 2.206 | 2.412 | 0.1421 | 0.0618 | Y |
| TLBO-ANN | repeat-stable balanced | 2.37828 | 48.451 | 62.184 | 60.61 | 0.9095 | 0.515 | 6.300 | 2.642 | 2.256 | 2.303 | 0.1723 | 0.0286 |  |
| SSA-ANN | direction + repeat stability | 2.41896 | 49.093 | 60.248 | 66.67 | 0.9215 | 0.606 | 6.402 | 2.571 | 2.451 | 2.273 | 0.1226 | 0.0203 | Y |
| HHO-ANN | year + repeat stability | 2.49709 | 51.376 | 60.868 | 57.58 | 0.9644 | 0.515 | 5.981 | 2.484 | 2.447 | 2.557 | 0.0459 | 0.0314 |  |

## Excluded groups
### A. Fail RW gate (9)
ABC-ANN, Bat-ANN, DE-ANN, FPA-ANN, GOA-ANN, HGSO-ANN, MFO-ANN, Multi-swarm ANN, PSO-ANN.

### B. Pass RW but do not meet price/direction/stability retention rule (10)
ALO-ANN, AOA-ANN, CS-ANN, ChOA-ANN, Crow Search-ANN, GWO-ANN, HGS-ANN, JAYA-ANN, SMA-ANN, Salp-ANN.

### C. Redundancy-pruned after initial retention (2)
FA-ANN, WOA-ANN.

## Full 33-model DEV audit
| Rank | Model | MAPE % | MAE | RMSE | Dir % | Rel MAE | Win RW | Worst APE % | Year SD | Repeat CV med | Batch 2.1 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | Vanilla ANN | 2.18895 | 44.873 | 58.308 | 54.55 | 0.8423 | 0.515 | 7.079 | 0.0800 | n/a | KEEP |
| 2 | MPA-ANN | 2.19947 | 44.592 | 56.292 | 57.58 | 0.8370 | 0.515 | 7.865 | 0.3698 | 0.0350 | KEEP |
| 3 | DE-ABC-ANN | 2.26109 | 46.504 | 58.612 | 66.67 | 0.8730 | 0.515 | 5.716 | 0.1894 | 0.0454 | KEEP |
| 4 | CPA-ANN | 2.27985 | 47.220 | 63.017 | 60.61 | 0.8864 | 0.515 | 7.062 | 0.2912 | 0.0458 | KEEP |
| 5 | FA-FPA-ANN | 2.28398 | 46.824 | 60.129 | 60.61 | 0.8790 | 0.515 | 6.896 | 0.1540 | 0.0509 | KEEP |
| 6 | ACO-ANN | 2.35494 | 48.520 | 58.421 | 63.64 | 0.9108 | 0.485 | 6.348 | 0.1683 | 0.0539 | KEEP |
| 7 | GA-ANN | 2.36033 | 48.120 | 59.585 | 63.64 | 0.9033 | 0.545 | 6.285 | 0.0427 | 0.0465 | KEEP |
| 8 | SCA-ANN | 2.36197 | 48.147 | 60.330 | 72.73 | 0.9038 | 0.576 | 6.628 | 0.3289 | 0.0449 | KEEP |
| 9 | Krill Herd-ANN | 2.37501 | 48.186 | 62.818 | 66.67 | 0.9045 | 0.606 | 7.913 | 0.1421 | 0.0618 | KEEP |
| 10 | TLBO-ANN | 2.37828 | 48.451 | 62.184 | 60.61 | 0.9095 | 0.515 | 6.300 | 0.1723 | 0.0286 | KEEP |
| 11 | WOA-ANN | 2.38669 | 49.715 | 62.905 | 63.64 | 0.9332 | 0.576 | 6.813 | 0.4595 | 0.0343 | OUT |
| 12 | FA-ANN | 2.39002 | 48.717 | 60.714 | 60.61 | 0.9145 | 0.545 | 6.874 | 0.4021 | 0.0360 | OUT |
| 13 | SSA-ANN | 2.41896 | 49.093 | 60.248 | 66.67 | 0.9215 | 0.606 | 6.402 | 0.1226 | 0.0203 | KEEP |
| 14 | Salp-ANN | 2.43583 | 49.888 | 59.615 | 60.61 | 0.9365 | 0.485 | 6.229 | 0.1891 | 0.0360 | OUT |
| 15 | ChOA-ANN | 2.46605 | 50.339 | 62.896 | 60.61 | 0.9449 | 0.576 | 6.244 | 0.2843 | 0.0403 | OUT |
| 16 | HGS-ANN | 2.48142 | 51.009 | 62.041 | 51.52 | 0.9575 | 0.394 | 7.219 | 0.3443 | 0.0239 | OUT |
| 17 | HHO-ANN | 2.49709 | 51.376 | 60.868 | 57.58 | 0.9644 | 0.515 | 5.981 | 0.0459 | 0.0314 | KEEP |
| 18 | ALO-ANN | 2.49827 | 51.821 | 63.576 | 60.61 | 0.9728 | 0.545 | 8.099 | 0.2678 | 0.0419 | OUT |
| 19 | CS-ANN | 2.50128 | 52.573 | 63.127 | 54.55 | 0.9869 | 0.424 | 6.285 | 0.4119 | 0.1119 | OUT |
| 20 | Crow Search-ANN | 2.50491 | 50.880 | 61.287 | 60.61 | 0.9551 | 0.485 | 6.642 | 0.5172 | 0.0401 | OUT |
| 21 | AOA-ANN | 2.51719 | 51.806 | 64.157 | 57.58 | 0.9725 | 0.545 | 7.071 | 0.4290 | 0.0000 | OUT |
| 22 | GWO-ANN | 2.53258 | 52.269 | 63.696 | 54.55 | 0.9812 | 0.455 | 7.074 | 0.3512 | 0.0370 | OUT |
| 23 | JAYA-ANN | 2.53899 | 52.632 | 68.058 | 63.64 | 0.9880 | 0.545 | 8.295 | 0.3355 | 0.0433 | OUT |
| 24 | SMA-ANN | 2.57631 | 52.719 | 65.313 | 51.52 | 0.9896 | 0.515 | 6.499 | 0.4268 | 0.0258 | OUT |
| 25 | Multi-swarm ANN | 2.59615 | 53.746 | 66.837 | 54.55 | 1.0089 | 0.485 | 7.118 | 0.2582 | 0.0401 | OUT |
| 26 | MFO-ANN | 2.60702 | 53.330 | 65.135 | 57.58 | 1.0011 | 0.424 | 7.678 | 0.1086 | 0.0475 | OUT |
| 27 | PSO-ANN | 2.61194 | 53.671 | 67.039 | 54.55 | 1.0075 | 0.515 | 7.142 | 0.3683 | 0.0370 | OUT |
| 28 | Bat-ANN | 2.64871 | 54.836 | 66.521 | 54.55 | 1.0293 | 0.424 | 7.931 | 0.3198 | 0.0582 | OUT |
| 29 | HGSO-ANN | 2.66180 | 54.558 | 67.687 | 54.55 | 1.0241 | 0.455 | 7.022 | 0.4332 | 0.0329 | OUT |
| 30 | FPA-ANN | 2.70125 | 54.242 | 68.699 | 42.42 | 1.0182 | 0.364 | 8.084 | 0.5405 | 0.0602 | OUT |
| 31 | DE-ANN | 2.84842 | 58.633 | 69.225 | 51.52 | 1.1006 | 0.424 | 6.360 | 0.2902 | 0.0538 | OUT |
| 32 | GOA-ANN | 3.00269 | 61.083 | 74.771 | 51.52 | 1.1466 | 0.424 | 8.456 | 0.5558 | 0.0631 | OUT |
| 33 | ABC-ANN | 3.06525 | 62.278 | 77.127 | 51.52 | 1.1690 | 0.424 | 10.106 | 0.0362 | 0.0618 | OUT |

## Batch 2.1 decision
- Candidate pool reduced from 33 to 12 using DEV-only evidence.
- No final hybrid parent is frozen yet.
- Stage 2 Batch 2.2 must perform redundancy/correlation/role selection among these 12 and freeze a small parent set for Stage 3.
