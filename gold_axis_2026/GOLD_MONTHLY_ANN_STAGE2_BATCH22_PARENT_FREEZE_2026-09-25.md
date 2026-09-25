# GOLD MONTHLY ANN — Stage 2 Batch 2.2 Parent Freeze

Date: 2026-09-25

## Scope and authority
This audit uses only the 33 DEV origins (2022-04..2024-12) from the original Phase A GitHub Actions artifacts. No 2025 transport or 2026 stress observation enters parent selection.

Input candidate pool from Batch 2.1: 12 models.

## Complementarity diagnostics
Pairwise diagnostics were computed on the 33 DEV forecast-error vectors:
- Pearson correlation of signed forecast errors;
- direction disagreement rate;
- number of origins where one model has lower absolute percentage error than an anchor;
- direction-rescue counts;
- simple 50/50 pair-average MAPE and direction accuracy used only as a complementarity proxy, not as an ensemble selection result.

### Key findings
- Vanilla ANN + DE-ABC-ANN: error correlation **0.7703**; 50/50 proxy MAPE **2.08507%**, direction **69.70%**.
- MPA-ANN + DE-ABC-ANN: correlation **0.8005**; proxy MAPE **2.11692%**, direction **69.70%**.
- MPA-ANN + CPA-ANN: correlation **0.8626**; proxy MAPE **2.15503%**, direction **66.67%**.
- CPA-ANN + SCA-ANN: correlation **0.8649**; proxy MAPE **2.16480%**, direction **66.67%**.
- MPA-ANN + GA-ANN: correlation **0.8839**; proxy MAPE **2.18681%**, direction **63.64%**.
- SCA-ANN rescues **7** DEV direction errors made by Vanilla ANN while losing only **1** Vanilla direction hit.
- Relative to MPA-ANN, SCA-ANN rescues **5** direction misses and loses **0** MPA direction hits.
- CPA-ANN beats MPA-ANN on absolute forecast error in **15/33** DEV origins.
- GA-ANN has DEV yearly-MAPE SD **0.0427**, one of the strongest year-stability profiles among high-performing candidates.
- TLBO-ANN has median repeat-validation fitness CV **0.0286** and remains a direct methodologically relevant parent for the planned meta-on-meta/parity track.
- SSA-ANN has even lower repeat-validation CV (**0.0203**) and 66.67% direction, but its DEV MAPE is weaker than TLBO and it is kept as a reserve stability challenger rather than an active parent.
- Krill Herd-ANN beats MPA on absolute error in **16/33** origins and has a 60.61% monthly win rate vs RW; it is kept as a reserve diversity challenger.

## Frozen Stage 3 structure

### A. Baseline anchor — retained, not a metaheuristic parent
**Vanilla ANN**
- DEV MAPE 2.18895%, MAE 44.873, RMSE 58.308.
- Remains the baseline anchor every Stage 3 model must beat or justify relative to.

### B. Active evidence-driven parent set — 5 optimizers
1. **MPA-ANN — primary price parent**
   - Best metaheuristic ANN DEV MAPE: 2.19947%.
   - DEV MAE 44.592 and RMSE 56.292.
   - Kept as the principal price-error search parent.

2. **CPA-ANN — complementary price/search-diversity parent**
   - DEV MAPE 2.27985%.
   - Lower error correlation with MPA (0.8626) than most upper-tier primitive candidates.
   - MPA+CPA 50/50 proxy improves to 2.15503% DEV MAPE.
   - Beats MPA absolute error in 15/33 origins.

3. **SCA-ANN — direction-specialist parent**
   - DEV direction leader: 72.73%.
   - Rescues 7 Vanilla direction misses while losing only 1 Vanilla hit.
   - Rescues 5 MPA direction misses while losing 0 MPA hits.
   - Retained for complementary directional information, not because it has the lowest MAPE.

4. **GA-ANN — year-stability parent**
   - DEV MAPE 2.36033%, direction 63.64%.
   - Yearly DEV MAPE: 2.298 / 2.367 / 2.400; SD 0.0427.
   - Retained to reduce dependence on a single DEV subperiod.

5. **TLBO-ANN — refinement/meta-tuning parent**
   - DEV MAPE 2.37828%.
   - Median repeat-validation CV 0.0286.
   - Retained because it combines acceptable DEV accuracy with strong repeat stability and is directly relevant to the pre-agreed TLBO-tuned/adaptive Stage 3 parity experiments.

### C. Frozen hybrid-parity benchmarks — benchmark only, not counted as new Stage 3 parents
**DE-ABC-ANN**
- DEV MAPE 2.26109%, direction 66.67%.
- Strongest complementarity to Vanilla among the Batch 2.1 pool.
- Because it is already a hybrid carried over for ELM parity, it remains a fixed Stage 3 benchmark and must not be re-labelled as a new hybrid contribution.

**FA-FPA-ANN**
- DEV MAPE 2.28398%, direction 60.61%.
- Also already hybrid/parity; fixed benchmark only.

### D. Reserve challengers — do not enter Stage 3 by default
- **SSA-ANN:** stability reserve; DEV MAPE 2.41896%, direction 66.67%, repeat-validation CV 0.0203.
- **Krill Herd-ANN:** diversity reserve; DEV MAPE 2.37501%, direction 66.67%, monthly win rate vs RW 60.61%.
- **ACO-ANN:** balanced reserve; DEV MAPE 2.35494%, RMSE 58.421, direction 63.64%.
- **HHO-ANN:** stability reserve; DEV MAPE 2.49709%, yearly-MAPE SD 0.0459.

Reserve challengers are activated only if the active-parent Stage 3 models show clear DEV overfit, collapse, or lack of diversity. They are not added merely to increase search count.

## Frozen parent error-correlation matrix
| | Vanilla | MPA | CPA | SCA | GA | TLBO |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla | 1.000 | 0.930 | 0.887 | 0.902 | 0.911 | 0.922 |
| MPA | 0.930 | 1.000 | 0.863 | 0.920 | 0.884 | 0.900 |
| CPA | 0.887 | 0.863 | 1.000 | 0.865 | 0.899 | 0.943 |
| SCA | 0.902 | 0.920 | 0.865 | 1.000 | 0.915 | 0.925 |
| GA | 0.911 | 0.884 | 0.899 | 0.915 | 1.000 | 0.924 |
| TLBO | 0.922 | 0.900 | 0.943 | 0.925 | 0.924 | 1.000 |

These correlations are high overall, so Stage 3 must remain tightly controlled; adding many more parents is unlikely to create useful diversity.

## Stage 3 governance after parent freeze
Two tracks are now frozen:

### Track 1 — mandatory ELM-parity refinement experiments
These remain required even if their base optimizer was not an active winner, because they were pre-agreed as direct ELM-to-ANN comparators:
1. Adaptive PSO-ANN
2. TLBO-tuned PSO-ANN
3. DE-tuned PSO-ANN
4. Adaptive/Improved TLBO-ANN
5. Adaptive Crow Search-ANN
6. PSO-TLBO Hybrid ANN

Their interpretation must explicitly account for the fact that base PSO-ANN failed the Batch 2.1 RW gate.

### Track 2 — evidence-driven ANN-specific experiments
Only a very small number of new combinations may be added, using the frozen active parents above. Initial scientific priority:
- **MPA + SCA:** price-error leader + direction specialist.
- **MPA + GA:** price-error leader + year-stability parent.
- A CPA-based alternative may replace one of these only if the first two fail to add DEV value.

No combinatorial cross-product search is permitted.

## Final Batch 2.2 decision
- Batch 2.1 pool: 12.
- Active evidence-driven parents: **5** (MPA, CPA, SCA, GA, TLBO).
- Baseline anchor: **Vanilla ANN**.
- Hybrid-parity benchmarks: **DE-ABC, FA-FPA**.
- Reserve challengers: **SSA, Krill Herd, ACO, HHO**.
- Stage 2 is complete.
- Stage 3 can begin under the frozen two-track plan above.
