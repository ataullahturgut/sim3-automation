# GOLD MONTHLY FORECAST — FINAL ELM vs ANN COMPARISON & FAMILY FREEZE

Date: 2026-09-25
Repository: ataullahturgut/sim3-automation
Branch: gold-midas-headswap-v1-20260925

## 1. Binding comparison authority

Target and data contract remain unchanged:
- H=1 next-calendar-month average XAU/USD price.
- Origin = previous completed month-end.
- Frozen 8 origin-safe VW-MIDAS inputs.
- DEV = 2022-04..2024-12, n=33.
- 2025 = locked transport, reporting only.
- 2026 Jan-Jul = retrospective stress, reporting only.
- No random split.
- No target-month leakage.
- DB READ_ONLY during model-development runs.
- Family/model freeze decisions are based on DEV only.

The final comparison therefore uses DEV as the selection authority and treats 2025/2026 only as external descriptive evidence.

## 2. ELM family closure

### Baseline
Vanilla ELM:
- DEV MAPE 2.19286%
- 2025 MAPE 2.55897%
- 2026 MAPE 5.25830%

### Best DEV single/metaheuristic ELM
AOA-ELM:
- DEV MAPE **2.15854%**
- 2025 MAPE 2.52849%
- 2026 MAPE 5.13545%
- 2026 direction 42.86%

This is the best documented ELM DEV MAPE across the broad ELM screen.

### Best targeted ELM refinement/hybrid
PSO-TLBO Hybrid ELM:
- DEV MAPE **2.18548%**
- 2025 MAPE 2.26698%
- 2026 MAPE 4.93398%
- 2026 direction 57.14%

### ELM interpretation
- ELM optimization can improve meaningfully over weaker optimizer configurations.
- The best ELM single model (AOA) outperforms the ELM baseline on DEV.
- The targeted PSO-TLBO refinement is strong on DEV but does not beat AOA-ELM.
- Several ELM variants show strong individual 2025 or 2026 retrospective behavior, but those periods are not selection authority and cannot be used to replace the DEV winner post hoc.
- No verifiable prediction-level ELM ensemble definition was found in the repo/initial ledger; exact ELM ensemble parity is therefore NOT_PROVEN / NOT_FOUND.

## 3. ANN family closure

### Baseline
Vanilla ANN:
- DEV MAPE 2.18895%
- DEV direction 54.55%
- 2025 MAPE 2.77892%
- 2026 MAPE 4.57914%

### Best DEV single/metaheuristic ANN
MPA-ANN:
- DEV MAPE **2.19947%**
- DEV direction 57.58%
- 2025 MAPE 2.45524%
- 2026 MAPE 4.05739%

### Strongest ANN refinement/hybrid price profiles
MPA+SCA Hybrid ANN:
- DEV MAPE **2.23957%**
- DEV direction 60.61%
- improves year-stability relative to MPA.

Adaptive TLBO-ANN:
- DEV MAPE **2.24090%**
- DEV direction 54.55%.

TLBO-tuned PSO-ANN:
- DEV MAPE 2.28920%
- DEV direction **69.70%**.

SCA-ANN remains the single ANN direction specialist:
- DEV MAPE 2.36197%
- DEV direction **72.73%**.

### Frozen ANN ensembles

#### PRIMARY — FULL7 equal-weight ANN ensemble
Components:
- Vanilla ANN
- MPA-ANN
- SCA-ANN
- DE-ABC-ANN
- Adaptive TLBO-ANN
- TLBO-tuned PSO-ANN
- MPA+SCA Hybrid ANN

Frozen equal weight = 1/7 each.

DEV:
- MAPE **2.10665%**
- MAE 43.299
- RMSE 55.634
- direction 66.67%
- relative MAE vs RW 0.8128

External reporting:
- 2025 MAPE 2.46790%, direction 91.67%
- 2026 MAPE 4.35551%, direction 71.43%

#### SECONDARY — REDUCED4 equal-weight ANN ensemble
Components:
- Vanilla ANN
- MPA-ANN
- SCA-ANN
- DE-ABC-ANN

Frozen equal weight = 1/4 each.

DEV:
- MAPE **2.12123%**
- RMSE **54.966**
- direction **72.73%**
- relative MAE vs RW 0.8143

External reporting:
- 2025 MAPE 2.47331%, direction 91.67%
- 2026 MAPE 4.46679%, direction 71.43%

## 4. Direct ELM vs ANN comparisons

### 4.1 Baseline architecture comparison
| Family | Baseline | DEV MAPE % |
|---|---|---:|
| ELM | Vanilla ELM | 2.19286 |
| ANN | Vanilla ANN | **2.18895** |

ANN baseline improves ELM baseline by only about **0.18% relative**. This difference is very small. The architecture change alone is not the main source of the final gain.

### 4.2 Best single/metaheuristic comparison
| Family | Best DEV single/metaheuristic | DEV MAPE % |
|---|---|---:|
| ELM | **AOA-ELM** | **2.15854** |
| ANN | MPA-ANN | 2.19947 |

Here **ELM is stronger**. AOA-ELM has about **1.86% lower relative MAPE** than the best ANN single/metaheuristic model.

This is a key scientific finding:
> ANN does not beat ELM simply because it is ANN.

### 4.3 Targeted refinement/hybrid comparison
| Family | Best targeted refinement/hybrid | DEV MAPE % |
|---|---|---:|
| ELM | **PSO-TLBO Hybrid ELM** | **2.18548** |
| ANN | MPA+SCA Hybrid ANN | 2.23957 |

The ELM targeted hybrid is about **2.47% relatively better** than the best ANN optimizer-hybrid on DEV MAPE.

Adaptive TLBO-ANN is very close to MPA+SCA at 2.24090% and does not change the conclusion.

### 4.4 Final overall comparison
| Final candidate | Family/type | DEV MAPE % | DEV direction % |
|---|---|---:|---:|
| AOA-ELM | ELM single | 2.15854 | not consistently preserved in final ELM ledger |
| PSO-TLBO Hybrid ELM | ELM refinement | 2.18548 | not consistently preserved in final ELM ledger |
| MPA-ANN | ANN single | 2.19947 | 57.58 |
| MPA+SCA ANN | ANN hybrid | 2.23957 | 60.61 |
| **FULL7 ANN Ensemble** | **ANN ensemble** | **2.10665** | 66.67 |
| REDUCED4 ANN Ensemble | ANN ensemble | 2.12123 | **72.73** |

The final FULL7 ANN ensemble improves on the best ELM DEV model (AOA-ELM) by about **2.40% relative MAPE**.

REDUCED4 also improves on AOA-ELM by about **1.73% relative MAPE**, while providing 72.73% DEV direction accuracy.

## 5. Same-candidate external comparison: AOA-ELM vs frozen ANN ensembles

This comparison is descriptive only; it does not change selection.

| Candidate | DEV MAPE % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|
| AOA-ELM | 2.15854 | 2.52849 | 5.13545 |
| **FULL7 ANN** | **2.10665** | **2.46790** | **4.35551** |
| REDUCED4 ANN | 2.12123 | 2.47331 | 4.46679 |

Relative to the DEV-selected AOA-ELM candidate, FULL7 is:
- ~2.40% better on DEV MAPE;
- ~2.40% lower MAPE on 2025 descriptive transport;
- ~15.19% lower MAPE on 2026 descriptive stress.

This is supportive external evidence for the frozen ANN ensemble, but the freeze remains DEV-governed.

Important limitation:
other ELM variants have stronger post-hoc results in individual external periods (for example MPA-ELM in 2025 and TLBO/Crow/PSO-family ELMs in 2026). Those retrospective specialists cannot be substituted after seeing the holdout outcomes.

## 6. Why ANN wins overall even though ELM wins single-model comparisons

The evidence indicates three separate effects:

1. **Architecture effect is small.**
   Vanilla ANN and Vanilla ELM are essentially tied on DEV.

2. **Optimizer-to-single-model fit favors ELM.**
   Best single ELM (AOA) is better than best single ANN (MPA).
   Best targeted ELM hybrid is also better than the best ANN optimizer hybrid.

3. **Forecast diversity / aggregation favors ANN.**
   ANN Stage 4 combines models with distinct price, direction, refinement and stability roles.
   Equal weighting improves honest DEV MAPE to 2.10665%.

Thus the final ANN advantage is primarily an **ensemble-diversification result**, not evidence that every ANN specification is intrinsically superior to ELM.

## 7. Weight-learning conclusion

ANN ensemble weight learning was tested through:
- inverse-MAE performance weighting;
- optimized simplex weights;
- exact-LP simplex;
- shrinkage toward equal weights.

The honest prequential DEV evidence repeatedly favored equal or near-equal weights. In the final shrinkage audit:
- FULL7 selected alpha = 0;
- REDUCED4 selected alpha = 0.

Therefore equal weights are not an arbitrary default. They are the result of the weight-tuning study rejecting more aggressive learned weights under the small n=33 meta-sample.

## 8. Final frozen hierarchy

### PRIMARY MONTHLY FORECAST MODEL
**FULL7 equal-weight ANN ensemble**

Reason:
- best honest DEV MAPE of the completed ELM/ANN research program;
- weight-learning study independently selects equal weighting;
- robust to leave-one-origin checks;
- beats RW relative MAE in every DEV year;
- external 2025/2026 evidence is supportive relative to the DEV-selected AOA-ELM benchmark.

### SECONDARY / DIRECTION-RMSE CHALLENGER
**REDUCED4 equal-weight ANN ensemble**

Reason:
- near-primary DEV MAPE;
- better DEV RMSE than FULL7;
- 72.73% DEV direction accuracy.

### FROZEN ELM BENCHMARK
**AOA-ELM**

Reason:
- best documented ELM DEV MAPE under the broad single/metaheuristic screen.
- retained as the principal ELM family comparator, not as the final primary model.

### FROZEN ELM REFINEMENT BENCHMARK
**PSO-TLBO Hybrid ELM**

Reason:
- strongest documented targeted ELM refinement/hybrid DEV MAPE.

### FROZEN ANN SINGLE BENCHMARK
**MPA-ANN**

Reason:
- best ANN single/metaheuristic DEV MAPE.

### FROZEN ANN REFINEMENT BENCHMARKS
- MPA+SCA Hybrid ANN — balanced/stability hybrid.
- Adaptive TLBO-ANN — price refinement.
- TLBO-tuned PSO-ANN — price+direction refinement.
- SCA-ANN — direction specialist.

## 9. Closed research directions

Without genuinely new unseen data or a new scientific hypothesis, do not reopen:
- additional ELM optimizer cross-products;
- additional ANN metaheuristic screen;
- MPA+X hybrid enumeration;
- arbitrary ANN subset search;
- optimized ensemble weights;
- shrinkage/stacking/meta-learner;
- post-hoc 2025/2026-based model switching.

Any future redesign must be justified independently of known 2025/2026 outcomes.

## 10. Final project status

- AŞAMA 1/5 — ANN broad screen: COMPLETE.
- AŞAMA 2/5 — DEV filtering / parent freeze: COMPLETE.
- AŞAMA 3/5 — adaptive/meta-on-meta/hybrid ANN: COMPLETE.
- AŞAMA 4/5 — ensemble / robustness / freeze: COMPLETE.
- **AŞAMA 5/5 — ELM vs ANN final comparison / family freeze: COMPLETE.**

### Final research decision
**Primary frozen family: ANN ensemble.**  
**Primary frozen model: FULL7 equal-weight ANN ensemble.**  
**Secondary frozen challenger: REDUCED4 equal-weight ANN ensemble.**  
**ELM remains an important single-model benchmark because it is stronger than ANN at the best-single and targeted-hybrid levels.**

The program is now closed for further model search under the current evidence set.
