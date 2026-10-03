# REVERSAL CONCEPT-DRIFT AUDIT — OAR CANDIDATES

**Evidence class:** post-holdout diagnostic. 2026 is development evidence here.

- OAR 2024-2025: **34**, rescue rate **64.71%**
- OAR 2026: **19**, rescue rate **15.79%**
- rescue-vs-broken feature-effect sign retention: **62.5%**
- correlation of feature SMDs (2024-25 vs 2026): **-0.155**

## Largest conditional-effect changes

| Feature | SMD 2024-25 | SMD 2026 | Same sign | |ΔSMD| |
|---|---:|---:|---|---:|
| cf_opposite_semivar_share_gap | +0.141 | -1.398 | False | 1.539 |
| opposite_semivar_share | +0.151 | -1.355 | False | 1.507 |
| p_inst | -0.368 | -1.382 | True | 1.014 |
| path_consistency | +0.461 | -0.519 | False | 0.980 |
| signed_opt_pressure | -0.140 | -1.030 | True | 0.890 |
| cf_deceleration_6h_gap | -0.087 | -0.887 | True | 0.800 |
| rte_tension | +0.217 | -0.464 | False | 0.682 |
| trend_strength | -0.078 | -0.689 | True | 0.611 |
| v5_confidence | -0.107 | +0.499 | False | 0.606 |
| cf_signed_opt_pressure_gap | +0.145 | -0.393 | False | 0.537 |
| gc_volume_accel_5 | -0.513 | -0.008 | True | 0.506 |
| opposite_extreme_recency | -0.565 | -0.100 | True | 0.465 |
| p_rte | -0.019 | -0.426 | True | 0.407 |
| gc_dlog_volume_1 | -0.417 | -0.017 | True | 0.400 |
| cf_adverse_excursion_gap | -0.055 | -0.369 | True | 0.315 |
| deceleration_6h | -0.134 | -0.416 | True | 0.282 |
| adverse_excursion | +0.135 | -0.086 | False | 0.221 |
| gc_volume_z20 | +0.145 | +0.009 | True | 0.136 |
| cf_signed_d_opt_pressure_gap | -0.232 | -0.314 | True | 0.082 |
| opt_total_z20 | -0.072 | +0.009 | False | 0.081 |
| signed_d_opt_pressure | +0.004 | -0.061 | False | 0.065 |
| cf_opt_total_z20_gap | -0.088 | -0.040 | True | 0.048 |
| cf_gc_dlog_volume_1_gap | -0.201 | -0.226 | True | 0.025 |
| trend_close_location | +0.095 | +0.086 | True | 0.010 |

## Largest unconditional OAR-state shifts into 2026

| Feature | SMD 2026 - 2024/25 |
|---|---:|
| v5_confidence | +0.667 |
| cf_opposite_semivar_share_gap | +0.604 |
| rte_tension | -0.513 |
| signed_opt_pressure | +0.463 |
| cf_gc_dlog_volume_1_gap | -0.441 |
| gc_dlog_volume_1 | -0.409 |
| cf_deceleration_6h_gap | -0.385 |
| gc_volume_accel_5 | -0.368 |
| trend_strength | +0.358 |
| p_inst | -0.328 |
| cf_adverse_excursion_gap | +0.324 |
| p_rte | -0.310 |
| opt_total_z20 | -0.275 |
| opposite_semivar_share | +0.275 |
| cf_signed_d_opt_pressure_gap | +0.247 |
| cf_opt_total_z20_gap | -0.244 |
| gc_volume_z20 | -0.241 |
| deceleration_6h | -0.229 |
| opposite_extreme_recency | +0.198 |
| adverse_excursion | -0.185 |
| signed_d_opt_pressure | -0.173 |
| path_consistency | -0.075 |
| trend_close_location | +0.049 |
| cf_signed_opt_pressure_gap | +0.016 |
