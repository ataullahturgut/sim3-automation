# GOLD H3 FROZEN STAKTRAKR UPSTREAM AUDIT — 2026-10-03

- pinned ref: `54fdf1c8d39b7b6c7b874d0f30f784296e886044`
- overlap with independent NY17-derived XAU: **1072** dates
- >=3% cross-source deviations: **4**
- >=5% deviations: **1**
- robust |z|>=8 deviations: **1**

## Cross-source flags

| Date | Stak | NY17 | Source | Deviation | z |
|---|---:|---:|---|---:|---:|
| 2026-02-27 | 3516.0200 | 5278.6362 | sqld | 33.38% | -62.3 |
| 2026-01-30 | 5063.4500 | 4866.2554 | seed | 4.07% | 6.1 |
| 2025-10-21 | 4275.1000 | 4130.3300 | seed | 3.53% | 5.3 |
| 2025-10-16 | 4225.5500 | 4362.2900 | seed | 3.12% | -4.9 |

## Source-type diagnostics

| Source | n | Median dev | Max dev | >3% | >5% | |z|>=8 |
|---|---:|---:|---:|---:|---:|---:|
| sqld | 131 | 0.43% | 33.38% | 1 | 1 | 1 |
| seed | 941 | 0.44% | 4.07% | 3 | 0 | 0 |
