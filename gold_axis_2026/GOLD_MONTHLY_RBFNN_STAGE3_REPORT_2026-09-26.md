# RBFNN Stage 3 — refinement evidence

Parent freeze commit `80acdfeb141b1daaa0eecf893b740143fcac6202` preceded all production refinements. DEV selection only. External tuning cutoff 2024-12.

| Method | DEV ΣAE | Direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Job | Artifact | Decision |
|---|---:|---:|---|---|---|---|---|
| TLBO_TUNED_PSO | 1610.0497 | 19/33 | 1136.1138 / 9/12 | 1505.0122 / 6/7 | 108450632348 | 10911547589 | PASS; dominated by DE-ABC; benchmark only |
| DE_TUNED_PSO | 1524.1595 | 20/33 | 1088.6479 / 8/12 | 1763.5385 / 5/7 | 108450632407 | 10911677231 | PASS; dominated by DE-ABC; benchmark only |
| ADAPTIVE_TLBO | 1552.2502 | 21/33 | 1114.0970 / 10/12 | 1825.2132 / 3/7 | 108449967875 | 10911686683 | PASS; dominated by DE-ABC; benchmark only |
| ADAPTIVE_PSO | 1519.3532 | 18/33 | 1218.4411 / 10/12 | 2223.1454 / 4/7 | 108449967744 | 10911333701 | PASS; dominated by DE-ABC; benchmark only |

Run 36258593871, script `tools/rbfnn_stage3a_v1.py`, workflow `.github/workflows/rbfnn-stage3a-v1.yml`. Exact learned outer parameters, parameter bounds, objective calls, repeats and implementation SHA256 are in each monthly diagnostic.

Completed refinements: 4/6. Stage 3B/3C not yet executed.

## Kontrol ve Uyum Özeti

DEV-only selection PASS; 2025/2026 exclusion PASS; random split NONE; chronological leakage checks PASS; DB READ_ONLY and invariants equal; scientific gate PASS; artifact manifest updated.
