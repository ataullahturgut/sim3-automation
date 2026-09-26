# GOLD MONTHLY FORECAST — RBFNN final family freeze and cross-family audit

Status: COMPLETE. Selection: DEV 2022-04..2024-12 only (33 months).

RBFNN primary: **DE_ABC**. Direction specialist: **DE_ABC**. Balanced challenger: **SALP** (benchmark role). Best hybrid: **DE_ABC**. Ensemble leader: **FULL_MEDIAN**, BENCHMARK_NOT_PRIMARY.

## Cross-family recomputed DEV evidence

| Model | ΣAE | Direction | MAE | RMSE | Worst AE | Relative MAE vs RW | LOO lower ΣAE than ChHHO |
|---|---:|---:|---:|---:|---:|---:|---:|
| ChHHO_ANFIS | 1413.0298 | 23/33 | 42.8191 | 54.8274 | 131.5843 | 0.80377 | 0/33 |
| RBFNN_DE_ABC | 1415.8371 | 25/33 | 42.9042 | 57.9188 | 155.5631 | 0.80537 | 15/33 |
| RBFNN_BEST_HYBRID_DE_ABC | 1415.8371 | 25/33 | 42.9042 | 57.9188 | 155.5631 | 0.80537 | 15/33 |
| FULL7_ANN | 1428.8590 | 22/33 | 43.2988 | 55.6338 | 145.9431 | 0.81278 | 9/33 |
| REDUCED4_ANN | 1431.4587 | 24/33 | 43.3775 | 54.9665 | 147.2164 | 0.81425 | 7/33 |
| RBFNN_ENSEMBLE_FULL_MEDIAN | 1444.3008 | 22/33 | 43.7667 | 57.3489 | 146.1002 | 0.82156 | 4/33 |
| RBFNN_STAGE3_ADAPTIVE_CROW | 1455.8616 | 21/33 | 44.1170 | 58.4904 | 150.1953 | 0.82814 | 1/33 |
| AOA_ELM | 1474.1021 | 20/33 | 44.6698 | 55.7632 | 136.1216 | 0.83851 | 0/33 |
| RBFNN_STAGE3_HYBRID_PSO_TLBO | 1489.6671 | 21/33 | 45.1414 | 58.7226 | 150.4068 | 0.84736 | 0/33 |
| SMA_ELMFIS | 1651.4482 | 25/33 | 50.0439 | 64.6558 | 174.8679 | 0.93939 | 0/33 |

Global point-estimate Pareto has **two distinct models: ChHHO-ANFIS and DE-ABC-RBFNN**. The two DE-ABC rows above report the same model in single-model and hybrid roles; they are not independent candidates.

## Stage-4 shrinkage and robustness

- FULL: components VANILLA, DE_ABC, SALP, ADAPTIVE_CROW; selected prequential alpha 0.75; full-DEV simplex ΣAE 1402.2173 is DIAGNOSTIC ONLY.
  - alpha 0.00: prequential ΣAE 1453.7884, direction 20/33.
  - alpha 0.10: prequential ΣAE 1449.7201, direction 20/33.
  - alpha 0.25: prequential ΣAE 1449.5563, direction 20/33.
  - alpha 0.50: prequential ΣAE 1449.4434, direction 21/33.
  - alpha 0.75: prequential ΣAE 1449.3304, direction 21/33.
  - alpha 1.00: prequential ΣAE 1450.5469, direction 22/33.
- REDUCED: components VANILLA, DE_ABC; selected prequential alpha 1.0; full-DEV simplex ΣAE 1415.8371 is DIAGNOSTIC ONLY.
  - alpha 0.00: prequential ΣAE 1493.5081, direction 20/33.
  - alpha 0.10: prequential ΣAE 1486.0585, direction 20/33.
  - alpha 0.25: prequential ΣAE 1477.2746, direction 22/33.
  - alpha 0.50: prequential ΣAE 1465.6223, direction 22/33.
  - alpha 0.75: prequential ΣAE 1457.4470, direction 23/33.
  - alpha 1.00: prequential ΣAE 1450.6011, direction 23/33.

Full monthly forecasts, prequential weight trajectories, all year blocks, worst-month errors and leave-one-component-out diagnostics are in the Stage-4 JSON. No component/pool changed after ensemble evaluation.

## Reporting only — no acceptance authority

Historical family external protocols differ from the strict RBFNN 2024-12 tuning freeze. These are reported values, not a controlled cross-family external ranking.

| Model | 2025 ΣAE | Direction | 2026 Jan–Jul ΣAE | Direction |
|---|---:|---:|---:|---:|
| AOA_ELM | 1052.2185 | 9/12 | 1679.0771 | 3/7 |
| ChHHO_ANFIS | 1252.0542 | 9/12 | 1178.1395 | 5/7 |
| FULL7_ANN | 1035.7821 | 11/12 | 1401.3193 | 5/7 |
| REDUCED4_ANN | 1040.8194 | 11/12 | 1438.5843 | 5/7 |
| SMA_ELMFIS | 1583.9840 | 10/12 | 2410.7639 | 3/7 |
| RBFNN_DE_ABC | 1145.3733 | 9/12 | 1932.7022 | 4/7 |
| RBFNN_STAGE3_ADAPTIVE_CROW | 1011.1308 | 9/12 | 1668.5494 | 6/7 |
| RBFNN_ENSEMBLE_FULL_MEDIAN | 1000.7708 | 9/12 | 1554.8466 | 6/7 |
| RBFNN_BEST_HYBRID_DE_ABC | 1145.3733 | 9/12 | 1932.7022 | 4/7 |
| RBFNN_STAGE3_HYBRID_PSO_TLBO | 1099.6425 | 9/12 | 1604.4205 | 5/7 |

## Kontrol ve Uyum Özeti

- DEV-only selection: PASS.
- 2025/2026 optimizer, parent, alpha and pool selection exclusion: PASS for this RBFNN program after explicit external correction.
- Random split: NONE.
- Chronological leakage checks and target-label/future invariance tests: PASS.
- DB: READ_ONLY; invariant equality checked.
- Scientific/numerical gate: recorded per model and period; no failed subset ranked.
- Full-DEV learned-weight fits: DIAGNOSTIC ONLY.
- Main roadmap/ledger: updated with stage status, run/job/artifact/commit lineage.

Limitations: n=33 DEV and many model comparisons: point-estimate selection, not statistical superiority; Regularized baseline occupancy gate evidence is NOT_PROVEN in its historical artifact; baselines retained without unnecessary reruns; optimizer repeat-validation dispersion is available; independent full-prediction repeat robustness is NOT_PROVEN; prequential weighting conditional on a DEV-selected frozen pool; not a nested-independent holdout; historical cross-family external protocols differ; no external tuning/acceptance or ranking authority.

RBFNN family frozen; return to governed monthly roadmap N2 Gaussian Processes; no automatic N2 execution in this task.

## Artifact provenance and independent verification

Ensemble/final run [36259902967](https://github.com/ataullahturgut/sim3-automation/actions/runs/36259902967), job **108453610546**, artifact **10911484644**, execution/pool-freeze commit `77083ec589ce6e8e9626cd20ae72ed4d95543913`. This commit froze pools before workflow evaluation. Original generated JSONs preserve artifact contents; this Markdown adds identity clarification and independent verification notes.

Independent verification: **PASS**, 41 RBF specifications (2 historical baselines audited, 39 new specifications), 54 ensemble-period metric/prediction checks (18 variants × 3 periods), pool and DEV hashes intact. Verification script and result: `tools/rbfnn_independent_final_verification.py`, `GOLD_MONTHLY_RBFNN_FINAL_VERIFICATION_2026-09-26.json`. Full-DEV simplex 1402.2173 is not a promotable forecast score; prequential unshrunk FULL simplex is 1450.5469.

| Frozen FULL component | Maximum DEV design condition |
|---|---:|
| Vanilla | 24.3670 |
| DE-ABC | 312.8473 |
| Salp | 241.0406 |
| Adaptive Crow | 316.4414 |

All are well below the new optimizer gate of 1e10. Complete numerical diagnostics for all 41 specifications are in the verification JSON; unavailable historical diagnostics are explicitly NOT_PROVEN.

DE-ABC year blocks: 2022 Apr–Dec ΣAE 356.0929 / 8 of 9 directions; 2023 367.8248 / 8 of 12; 2024 691.9194 / 9 of 12. RW-relative MAE is below one in all three. Its aggregate price gap against ChHHO is only +2.80735; removing one origin changes this gap to a range of -62.1361 to +49.5453, with 15 of 33 omissions reversing the price ranking. This is sensitivity evidence, not statistically proven superiority.
