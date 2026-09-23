# GOLD CONTROL — UP-2 REGIME-CONDITIONED R2 ANATOMY V1

**Status:** `REGIME_CONDITIONED_DIAGNOSTIC_SIGNAL_EXISTS`

Fixed R2 veto threshold: 0.5.

Pre-2025 useful rules: `['sqrt_score:HIGH', 'rv60_ratio:HIGH', 'downside_share:LOW', 'late_downside_intensity:HIGH', 'lag1_close_return:HIGH']`  
Transport-consistent rules: `['sqrt_score:HIGH', 'downside_share:LOW', 'late_downside_intensity:HIGH', 'lag1_close_return:HIGH']`

| Axis | Side | Pre cut | Pre false removed | Pre true retained | 2025 false removed | 2025 true retained | Transport |
|---|---|---:|---:|---:|---:|---:|---|
| sqrt_score | HIGH | 1.29989 | 3/3 | 7/8 | 5/12 | 10/13 | True |
| sqrt_score | LOW | 1.29989 | 0/3 | 7/8 | 3/12 | 12/13 | False |
| rv60_ratio | HIGH | 4.03411 | 2/3 | 6/8 | 2/12 | 12/13 | False |
| rv60_ratio | LOW | 4.03411 | 1/3 | 8/8 | 6/12 | 10/13 | False |
| downside_share | HIGH | 0.618005 | 1/3 | 7/8 | 3/12 | 12/13 | False |
| downside_share | LOW | 0.618005 | 2/3 | 7/8 | 5/12 | 10/13 | True |
| late_downside_intensity | HIGH | 0.0540692 | 2/3 | 7/8 | 7/12 | 10/13 | True |
| late_downside_intensity | LOW | 0.0540692 | 1/3 | 7/8 | 1/12 | 12/13 | False |
| lag1_close_return | HIGH | -0.0122661 | 2/3 | 6/8 | 4/12 | 11/13 | True |
| lag1_close_return | LOW | -0.0122661 | 1/3 | 8/8 | 4/12 | 11/13 | False |

Diagnostic only. No regime-conditioned veto is authorized.
