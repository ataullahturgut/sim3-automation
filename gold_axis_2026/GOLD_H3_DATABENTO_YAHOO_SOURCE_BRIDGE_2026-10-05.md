# GOLD H3 — Databento ↔ Frozen Yahoo Source Bridge — 2026-10-05

**Status:** **SOURCE_BRIDGE_REQUIRES_REVIEW**  
Pre-download estimated Databento cost: **USD 1.3926** (approved ceiling USD 1.60).  
**No raw Databento prices are committed. Roll selection uses source agreement only; no DPTC outcome labels.**

## Per-channel roll comparison

| Root | Roll | Coverage | r1 corr | r1 sign | r1 MAE bps | r3 corr | r6 corr | Vol log corr | Score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CL | c | 92.40% | 0.980829 | 98.286% | 1.8498 | 0.983810 | 0.985290 | — | 0.977391 |
| CL | v | 10.96% | 0.994083 | 92.400% | 6.2903 | 0.997383 | 0.998298 | — | 0.886023 |
| CL | n | 35.26% | 0.679180 | 92.283% | 12.0560 | 0.685281 | 0.682924 | — | 0.734069 |
| GC | v | 98.01% | 0.980572 | 99.254% | 0.7198 | 0.989891 | 0.993151 | 0.94277 | 1.035305 |
| GC | n | 9.14% | 0.991891 | 97.111% | 3.4070 | 0.993076 | 0.993503 | 0.43600 | 0.914077 |
| GC | c | 40.88% | 0.875806 | 80.507% | 16.2494 | 0.954898 | 0.975657 | 0.11194 | 0.851049 |
| NQ | c | 99.48% | 0.978711 | 98.939% | 0.6742 | 0.990503 | 0.992899 | — | 0.988970 |
| NQ | n | 3.07% | 0.997373 | 96.678% | 2.0177 | 0.998942 | 0.999198 | — | 0.894115 |
| NQ | v | 0.70% | 0.996946 | 95.588% | 2.9148 | 0.998989 | 0.999467 | — | 0.887619 |
| SI | v | 98.02% | 0.971563 | 99.047% | 1.3339 | 0.989354 | 0.994091 | 0.95713 | 1.033456 |
| SI | n | 13.93% | 0.996090 | 95.408% | 4.9121 | 0.997338 | 0.997652 | 0.55751 | 0.923004 |
| SI | c | 26.63% | 0.852622 | 79.756% | 41.2082 | 0.948940 | 0.976797 | 0.08142 | 0.817442 |
| ZN | c | 79.24% | 0.951667 | 94.095% | 0.6234 | 0.982301 | 0.988932 | — | 0.948192 |
| ZN | v | 24.27% | 0.997723 | 98.285% | 0.1083 | 0.999196 | 0.999622 | — | 0.919362 |
| ZN | n | 11.67% | 0.995862 | 95.909% | 0.3121 | 0.997060 | 0.997258 | — | 0.898540 |

## Frozen source mapping

| Root | Winner | Strict gate | r1 corr | r1 sign | MAE bps | Coverage |
|---|---|---|---:|---:|---:|---:|
| GC | **GC.v.0** | **False** | 0.980572 | 99.254% | 0.7198 | 98.01% |
| SI | **SI.v.0** | **False** | 0.971563 | 99.047% | 1.3339 | 98.02% |
| NQ | **NQ.c.0** | **False** | 0.978711 | 98.939% | 0.6742 | 99.48% |
| ZN | **ZN.c.0** | **False** | 0.951667 | 94.095% | 0.6234 | 79.24% |
| CL | **CL.c.0** | **False** | 0.980829 | 98.286% | 1.8498 | 92.40% |

## Governance

- This bridge is source-only and does not inspect RESCUE/BROKEN, DPTC Q95/Q99, or forecast correctness.
- The selected roll rule may differ by product.
- 2023–2024 replay is allowed only if the bridge quality is scientifically adequate; otherwise it remains a proxy reconstruction.
- No LLRS/IFBC/DPTC thresholds or architecture were changed.
