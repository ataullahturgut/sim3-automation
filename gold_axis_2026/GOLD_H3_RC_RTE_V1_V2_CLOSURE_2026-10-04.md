# GOLD H3 — RC-RTE V1 / V2 FUSE CLOSURE

**Date:** 2026-10-04  
**Final clean holdout status:** **FAILED / HELIOS V5-DCE REMAINS CHAMPION**

## 1. Why RC-RTE was built

RTE V1-V4 showed that reversal rescue is state-dependent:
- 2025 H1 could be favorable;
- 2025 H2 could invert the same reversal logic.

RC-RTE therefore introduced unsupervised origin-state regimes and allowed frozen reversal specialists to override V5 only inside historically reversal-enabled regimes.

## 2. RC-RTE V1

State axes:
- persistence
- fragility
- option opposition
- participation shock

Unsupervised map:
- KMeans K=3
- training-only standardization
- training-only regime utility audit

Frozen proposal union:
- SB slow-burn
- OPT option-confirmed
- MAT material-reversal

Sequential pre-2026 result:
- 2024 H2: net 0
- 2025 H1: 15 rescue / 7 broken / **+8**
- 2025 H2: 6 rescue / 14 broken / **-8**

Pooled:
- 21 rescue / 21 broken / net 0
- precision 50%

Status:
`NO_ROBUST_RC_RTE_RULE`.

2026 remained unopened at V1.

## 3. 2025 H2 chronology insight

The H2 inversion was visible quickly:
- first five static RC-RTE candidates were all broken;
- regime-level live utility turned negative early;
- overlapping H3 proposals could also cluster before prior outcomes matured.

This motivated an online risk-control layer rather than another static threshold.

## 4. RC-RTE V2 — online credibility fuse

Added:
1. only one unresolved accepted event per regime;
2. matured accepted utility +1 rescue / -1 broken;
3. close a regime for the rest of the refit block as soon as its matured live score becomes negative.

Sequential pre-2026:

| Block | Accepted | Rescue | Broken | Net | Precision |
|---|---:|---:|---:|---:|---:|
| 2024 H2 | 0 | 0 | 0 | 0 | — |
| 2025 H1 | 9 | 7 | 2 | **+5** | **77.78%** |
| 2025 H2 | 2 | 0 | 2 | **-2** | 0% |

Pooled:
- 11 accepted
- 7 rescue
- 4 broken
- net **+3**
- precision **63.64%**
- pooled V5 accuracy **68.24%**
- pooled assisted accuracy **69.18%**

The preregistered robustness gate passed.

Therefore 2026 was opened once as final clean holdout.

## 5. 2026 clean holdout

Final pre-2026 static enabled regimes:
- regime 1 only

2026:
- eligible origins: 153
- raw proposals: 35
- accepted by regime + fuse: **1**
- overlap-suppressed: 1
- fuse-suppressed: 9
- static-regime suppressed: 24
- rescue: **0**
- broken: **1**
- net rescue: **-1**
- OPAL-no-candidate missed reversals hit: **0 / 55**

Whole clean 2026:
- V5: **121 / 191 = 63.35%**
- RC-RTE V2 assisted: **120 / 191 = 62.83%**

Binding result:
> **RC-RTE V2 is not promoted. HELIOS V5-DCE remains champion.**

## 6. Post-holdout diagnosis — why the one 2026 candidate failed

The single accepted 2026 event:
- issue: 2026-03-04
- target H3 return: -1.81%
- V5 was already correct
- proposal source: MAT-only
- assigned regime: 1

Pre-2026 regime-1 proposal history:
- 36 proposals
- 20 rescue / 16 broken
- union precision 55.56%

Specialist identity alone does not explain the failure:
- pre-2026 regime-1 MAT-only: 3 rescue / 1 broken = 75% precision.

The stronger diagnosis is geometric extrapolation.

Inside pre-2026 regime 1:
- rescue median persistence: **-0.357**
- broken median persistence: **-0.491**

The accepted 2026 candidate:
- persistence: **+0.880**
- fragility: -0.317
- option opposition: +0.717
- participation shock: +1.077

Thus the candidate was assigned to regime 1 by nearest-centroid KMeans despite being far outside the historical persistence geometry of that regime's proposal population.

This is an **out-of-distribution / mixed-state assignment problem**, not merely a threshold failure.

## 7. Binding next architecture

Do not re-tune RC-RTE V2 on the spent 2026 holdout.

The next scientifically valid successor should be a **Support-Constrained Regime Reversal Engine**:

1. keep origin-state regime compression;
2. add a regime-membership confidence / support-envelope gate;
3. a candidate must not only be assigned to a reversal-enabled regime but also lie inside the historical support of successful proposal states;
4. candidate acceptance should be fail-closed for cluster-edge / OOD states;
5. preserve specialist identity within the regime rather than collapsing all proposals into one union utility;
6. retain overlap-aware one-outstanding-event control and online credibility fuse.

Possible implementation families for the support gate:
- training-only robust Mahalanobis / covariance distance;
- conformal nearest-neighbor support score;
- distance-to-rescue-prototype versus continuation/broken prototype;
- cluster assignment margin.

Because 2026 is now spent, any successor inspected on 2026 must be labeled retrospective/post-hoc. Its next clean evaluation must be prospective or use another untouched time segment.

## 8. Governance

- RC-RTE V2 opened 2026 only after its preregistered pre-2026 robustness gate passed.
- The negative 2026 holdout result is binding and retained.
- No post-holdout modification may be presented as a clean 2026 improvement.
- HELIOS V5-DCE remains binding.
- CLEAN_H3_PROSPECTIVE_V1 remains untouched.

Evidence:
- `GOLD_H3_RC_RTE_V1_RESULT_2026-10-04.md`
- `GOLD_H3_RC_RTE_2025H2_CANDIDATE_CHRONOLOGY_2026-10-04.md`
- `GOLD_H3_RC_RTE_V2_FUSE_RESULT_2026-10-04.md`
- `GOLD_H3_RC_RTE_SPECIALIST_REGIME_AUDIT_PRE2026_2026-10-04.md`
- `GOLD_H3_RC_RTE_REGIME1_GEOMETRY_DIAGNOSTIC_2026-10-04.md`
