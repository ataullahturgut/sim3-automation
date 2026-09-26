# RBFNN Stage 2 — DEV filtering and frozen parents

Status: FROZEN BEFORE STAGE 3. All 32 Stage-1 artifacts audited; both baseline references included.
Selection: DEV only, 2022-04..2024-12. No external metric used.

| Role | Model | DEV ΣAE | Direction | Worst-year RW relative MAE |
|---|---|---:|---:|---:|
| architecture_anchor | VANILLA | 1666.0440 | 19/33 | 1.0200 |
| direction_leader | DE_ABC | 1415.8371 | 25/33 | 0.8894 |
| optimizer_hybrid_parent | MPA | 1510.5118 | 20/33 | 0.9290 |
| price_leader | DE_ABC | 1415.8371 | 25/33 | 0.8894 |
| stability_parent | SALP | 1426.6878 | 23/33 | 0.8698 |

34 numerically valid models beat aggregate DEV RW MAE; none met the predeclared .995 signed-error redundancy cut while being dominated. Retained as benchmarks does not mean promoted. The small frozen parent set is DE_ABC, SALP, VANILLA, MPA.

The RBFNN Stage-1 Pareto frontier contains DE-ABC only. It dominates all other RBFNN broad-screen/baseline points on ΣAE and direction.

Hybrid opening rule: at most one of MPA+SCA/GA/CPA; both retained, correlation<.90, bidirectional direction rescues>=2, each price wins>=8; minimum correlation then price tie-break.
No eligible MPA+SCA/GA/CPA pair meets that rule. Stage 3B remains conditionally closed; reassess only against the frozen evidence, never external outcomes or a changed pool.

All per-year metrics, worst month, leave-one-origin sums, pairwise signed/absolute-error correlations, disagreement/rescue/loss counts, repeat validation spread and numerical conditioning appear in the companion JSON.
Repeat spread describes internal validation variation, not end-to-end prediction uncertainty. Independent repeat forecasts remain NOT_PROVEN.

Next: six mandatory Stage-3A refinements, two independent jobs per batch. No parent pool changes after Stage-3 outcomes.
