# RBFNN Stage 1 — artifact audit and cumulative results

Selection authority: DEV 2022-04..2024-12 only. 2025/2026 reporting only. No parent frozen.
Exact optimizer equations/constants: source file, function and SHA256 in each artifact. Population 24, generations 45, repeats 3.
Script `gold_axis_2026/tools/vw_midas_rbfnn_stage1_v1.py`; workflow `.github/workflows/gold-monthly-rbfnn-stage1-v1.yml`.
Numerical audit checks all available rows, chronology, full-period coverage, invariant equality, DEV freeze hash and recomputed metrics.

| Model | DEV ΣAE | Direction | MAE | RMSE | RW relative MAE | RW wins | Worst AE | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| SALP | 1426.6878 | 23/33 | 43.2330 | 56.3283 | 0.81154 | 21/33 | 148.0859 | PASS |
| MFO | 1449.1065 | 20/33 | 43.9123 | 60.2160 | 0.82429 | 18/33 | 147.8087 | PASS |
| JAYA | 1460.7401 | 21/33 | 44.2649 | 59.1096 | 0.83091 | 19/33 | 149.8114 | PASS |
| HGS | 1461.9334 | 20/33 | 44.3010 | 59.1341 | 0.83159 | 19/33 | 163.4165 | PASS |
| ACO | 1481.9468 | 19/33 | 44.9075 | 57.7832 | 0.84297 | 18/33 | 152.5209 | PASS |
| GOA | 1492.8771 | 20/33 | 45.2387 | 57.4806 | 0.84919 | 17/33 | 153.0539 | PASS |
| WOA | 1499.2639 | 19/33 | 45.4322 | 60.5691 | 0.85282 | 18/33 | 157.4068 | PASS |
| AOA | 1501.0998 | 19/33 | 45.4879 | 59.6291 | 0.85387 | 18/33 | 146.8618 | PASS |
| BAT | 1501.6410 | 21/33 | 45.5043 | 58.1928 | 0.85418 | 16/33 | 152.4168 | PASS |
| MPA | 1510.5118 | 20/33 | 45.7731 | 61.0286 | 0.85922 | 18/33 | 153.0577 | PASS |
| GWO | 1511.6245 | 22/33 | 45.8068 | 62.1607 | 0.85985 | 19/33 | 158.3893 | PASS |
| GA | 1523.4710 | 19/33 | 46.1658 | 59.2889 | 0.86659 | 16/33 | 157.9942 | PASS |
| FA_FPA | 1524.5325 | 20/33 | 46.1980 | 60.0151 | 0.86720 | 18/33 | 158.5392 | PASS |
| FPA | 1525.4420 | 21/33 | 46.2255 | 61.6968 | 0.86771 | 19/33 | 170.3735 | PASS |
| CS | 1525.6645 | 20/33 | 46.2323 | 59.3562 | 0.86784 | 17/33 | 148.7565 | PASS |
| TLBO | 1525.7861 | 19/33 | 46.2359 | 60.7834 | 0.86791 | 17/33 | 151.7869 | PASS |
| FA | 1530.4171 | 20/33 | 46.3763 | 61.6788 | 0.87054 | 18/33 | 150.5364 | PASS |
| CROW | 1538.2158 | 19/33 | 46.6126 | 60.9653 | 0.87498 | 17/33 | 166.4605 | PASS |
| SCA | 1541.6271 | 21/33 | 46.7160 | 61.7928 | 0.87692 | 18/33 | 160.7054 | PASS |
| DE | 1550.2583 | 18/33 | 46.9775 | 60.5498 | 0.88183 | 17/33 | 146.9444 | PASS |
| ABC | 1558.8168 | 18/33 | 47.2369 | 60.9410 | 0.88670 | 17/33 | 150.7081 | PASS |
| SSA | 1559.8246 | 18/33 | 47.2674 | 59.4641 | 0.88727 | 15/33 | 153.1977 | PASS |
| KRILL | 1560.4829 | 17/33 | 47.2874 | 60.2197 | 0.88765 | 14/33 | 157.6193 | PASS |
| HGSO | 1564.9802 | 20/33 | 47.4236 | 61.0783 | 0.89020 | 19/33 | 154.1318 | PASS |
| SMA | 1568.1653 | 19/33 | 47.5202 | 59.9730 | 0.89202 | 16/33 | 144.6313 | PASS |
| CHOA | 1571.0927 | 20/33 | 47.6089 | 61.2654 | 0.89368 | 18/33 | 148.6535 | PASS |
| HHO | 1586.1569 | 20/33 | 48.0654 | 60.9390 | 0.90225 | 18/33 | 141.8358 | PASS |
| ALO | 1597.3649 | 19/33 | 48.4050 | 63.5329 | 0.90863 | 17/33 | 153.4569 | PASS |
| PSO | 1598.5085 | 20/33 | 48.4397 | 65.2068 | 0.90928 | 18/33 | 167.8131 | PASS |
| CPA | 1608.6437 | 17/33 | 48.7468 | 60.9102 | 0.91504 | 14/33 | 158.4264 | PASS |

## External reporting — excluded from selection

Only STRICT_FROZEN rows are authoritative. Original expanding-tuning external rows are SUPERSEDED pending strict pre-2025 tuning freeze. DEV remains unchanged.
| Model | 2025 ΣAE | 2025 direction | 2026 Jan–Jul ΣAE | 2026 direction |
|---|---:|---:|---:|---:|
| ABC | 1163.3667 | 10/12 | 1724.0050 | 3/7 |
| ACO | 1078.1735 | 9/12 | 1303.0020 | 6/7 |
| ALO | 1125.6221 | 9/12 | 1695.0873 | 6/7 |
| AOA | 1112.8490 | 10/12 | 1157.9096 | 5/7 |
| BAT | 1103.4830 | 9/12 | 1426.7382 | 6/7 |
| CHOA | 1076.1496 | 10/12 | 1578.1525 | 5/7 |
| CPA | 1006.6045 | 10/12 | 1604.2304 | 5/7 |
| CROW | 1080.5612 | 8/12 | 1486.2783 | 5/7 |
| CS | 1026.6605 | 10/12 | 1597.2074 | 5/7 |
| DE | 1027.8448 | 10/12 | 1441.2427 | 5/7 |
| FA_FPA | 1057.3122 | 10/12 | 1637.0993 | 6/7 |
| FA | 1179.5730 | 9/12 | 1926.0538 | 4/7 |
| FPA | 1097.1847 | 9/12 | 1753.2470 | 5/7 |
| GA | 1015.5576 | 9/12 | 1509.5037 | 5/7 |
| GOA | 1001.7465 | 10/12 | 1509.2009 | 5/7 |
| GWO | 1074.3216 | 10/12 | 1457.2699 | 6/7 |
| HGS | 1068.9775 | 9/12 | 1467.0408 | 5/7 |
| HGSO | 1050.0976 | 9/12 | 1427.1983 | 6/7 |
| HHO | 1037.4322 | 9/12 | 1588.5282 | 5/7 |
| JAYA | 1189.3143 | 9/12 | 1703.0444 | 5/7 |
| KRILL | 1131.2027 | 11/12 | 2052.6335 | 4/7 |
| MFO | 1045.5957 | 9/12 | 1755.3723 | 5/7 |
| MPA | 1062.0186 | 9/12 | 1463.0003 | 5/7 |
| PSO | 1085.9960 | 9/12 | 1559.0378 | 6/7 |
| SALP | 1048.4474 | 10/12 | 1481.7930 | 6/7 |
| SCA | 1070.8575 | 8/12 | 1668.9123 | 5/7 |
| SMA | 1061.1819 | 9/12 | 1741.0975 | 4/7 |
| SSA | 1195.7422 | 10/12 | 2079.8413 | 4/7 |
| TLBO | 1219.1781 | 8/12 | 1849.1663 | 3/7 |
| WOA | 1203.7105 | 10/12 | 1776.8797 | 5/7 |

## Provenance and decisions

- ABC: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `abc_phase`.
- ACO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `aco_phase`.
- ALO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_6_v1.py` / `alo_phase`.
- AOA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_7_v1.py` / `aoa_phase`.
- BAT: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `bat_phase`.
- CHOA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_7_v1.py` / `choa_phase`.
- CPA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_8_v1.py` / `cpa_phase`.
- CROW: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_8_v1.py` / `crow_phase`.
- CS: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_5_v1.py` / `cs_phase`.
- DE: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `de_phase`.
- FA_FPA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_4_v1.py` / `fa_fpa_phase`.
- FA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_4_v1.py` / `fa_phase`.
- FPA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_4_v1.py` / `fpa_phase`.
- GA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `ga_phase`.
- GOA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_6_v1.py` / `goa_phase`.
- GWO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `gwo_phase`.
- HGS: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_7_v1.py` / `hgs_phase`.
- HGSO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_7_v1.py` / `hgso_phase`.
- HHO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `hho_phase`.
- JAYA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_6_v1.py` / `jaya_phase`.
- KRILL: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_8_v1.py` / `krill_phase`.
- MFO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_4_v1.py` / `mfo_phase`.
- MPA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `mpa_phase`.
- PSO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `pso_phase`.
- SALP: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_5_v1.py` / `salp_phase`.
- SCA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_5_v1.py` / `sca_phase`.
- SMA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_5_v1.py` / `sma_phase`.
- SSA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `ssa_phase`.
- TLBO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_6_v1.py` / `tlbo_phase`.
- WOA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `woa_phase`.

Job/artifact IDs are recorded in the main ledger batch entries and evidence provenance JSON.

Completed artifacts audited: 30/32. Scientific failures retained; no missing rows silently dropped.
Next: finish remaining Stage-1 batches; only then Stage-2 filtering/parent freeze.
