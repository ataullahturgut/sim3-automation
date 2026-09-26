# GPR Stage2 DEV filtering and parent freeze

Status FROZEN_BEFORE_STAGE3; 2025/2026 never used.

Roles: {"price_leader": "MULTISWARM", "direction_leader": "FA_FPA", "stability_parent": "ICM_M32", "architecture_anchor": "VANILLA_ICM_RBF", "optimizer_hybrid_parent": "MPA"}.

Conditional hybrid opening: [{"pair": ["MPA", "SCA"], "correlation": 0.8756565779738953, "combined_sae": 3415.418114376115}].

| Model | DEV ΣAE | Direction | RW-relative MAE | Max condition bound | Retained |
|---|---:|---:|---:|---:|---|
| MULTISWARM | 1606.7414 | 23/33 | 0.91396 | 1.84e+07 | True |
| AOA | 1611.8839 | 22/33 | 0.91689 | 6.457e+04 | True |
| ICM_M32 | 1640.0091 | 17/33 | 0.93288 | 4.899e+08 | True |
| GWO | 1650.2596 | 21/33 | 0.93871 | 1.913e+08 | True |
| ABC | 1672.2945 | 22/33 | 0.95125 | 1.136e+05 | True |
| HGSO | 1677.9024 | 19/33 | 0.95444 | 4.804e+05 | True |
| SMA | 1701.0740 | 22/33 | 0.96762 | 6.457e+04 | True |
| MPA | 1701.5802 | 23/33 | 0.96791 | 1.408e+07 | True |
| MFO | 1702.0152 | 19/33 | 0.96815 | 8.677e+08 | True |
| ALO | 1704.0561 | 21/33 | 0.96932 | 4.989e+06 | True |
| DE_ABC | 1709.2591 | 23/33 | 0.97227 | 4.606e+06 | True |
| FPA | 1711.7090 | 20/33 | 0.97367 | 2.744e+07 | True |
| SCA | 1713.8379 | 23/33 | 0.97488 | 4.182e+08 | True |
| GA | 1723.5877 | 21/33 | 0.98043 | 9.282e+04 | True |
| FA_FPA | 1724.6532 | 25/33 | 0.98103 | 9.282e+04 | True |
| VANILLA_ICM_RBF | 1726.6205 | 15/33 | 0.98215 | 1.107e+08 | True |
| TLBO | 1736.5717 | 19/33 | 0.98781 | 2.046e+08 | True |
| CROW | 1736.9995 | 22/33 | 0.98805 | 6.385e+08 | True |
| BAT | 1746.6720 | 21/33 | 0.99356 | 1.571e+06 | True |
| JAYA | 1760.9248 | 22/33 | 1.00166 | 8.793e+08 | False |
| KRILL | 1769.3329 | 22/33 | 1.00645 | 5.116e+06 | False |
| CPA | 1778.4226 | 22/33 | 1.01162 | 5.512e+07 | False |
| PSO | 1780.2169 | 19/33 | 1.01264 | 1.682e+06 | False |
| SSA | 1798.1173 | 21/33 | 1.02282 | 1.816e+05 | False |
| HGS | 1814.9260 | 20/33 | 1.03238 | 1.953e+08 | False |
| ACO | 1815.8271 | 19/33 | 1.03289 | 3.268e+05 | False |
| CHOA | 1822.1087 | 17/33 | 1.03647 | 1.031e+09 | False |
| HHO | 1823.3648 | 21/33 | 1.03718 | 1.353e+06 | False |
| CS | 1835.2043 | 22/33 | 1.04392 | 1.589e+05 | False |
| WOA | 1836.8353 | 21/33 | 1.04484 | 1.589e+05 | False |
| SALP | 1841.6043 | 20/33 | 1.04756 | 1.753e+05 | False |
| REGULARIZED_ICM_RBF | 1842.2361 | 16/33 | 1.04792 | 6538 | False |
| GOA | 1850.3608 | 22/33 | 1.05254 | 6.457e+04 | False |
| FA | 1861.6613 | 19/33 | 1.05897 | 1.562e+05 | False |
| DE | 1924.6270 | 21/33 | 1.09478 | 6.502e+07 | False |

Full pairwise signed/absolute-error correlations, direction rescue/loss and price-win counts, years, repeat-validation dispersion and source DEV hashes in JSON. Auxiliary SO_RBF is not a four-output parent. Independent predictive-repeat robustness remains NOT_PROVEN.

## Kontrol ve Uyum Özeti

DEV-only PASS; external exclusion PASS; no random split; audited chronology/scientific gates; DB invariants equal. Freeze must be committed before Stage3.
