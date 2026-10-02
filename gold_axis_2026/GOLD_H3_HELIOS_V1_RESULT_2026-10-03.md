# HELIOS-H3 V1 — REGIME-GATED REVERSAL ROUTER RESULT

**Status:** **POSTHOC_STRENGTHENING_RESULT**  
**Evidence class:** retrospective strengthening evidence; future freeze required for prospective proof.  

## Candidate reversal anatomy

| Year | Candidate | Success | Failure | Precision | Mean OPAL P(reversal) |
|---:|---:|---:|---:|---:|---:|
| 2022 | 1 | 1 | 0 | 100.0% | 91.7% |
| 2023 | 3 | 1 | 2 | 33.3% | 78.1% |
| 2024 | 7 | 5 | 2 | 71.4% | 75.8% |
| 2025 | 6 | 5 | 1 | 83.3% | 74.8% |
| 2026 | 4 | 3 | 1 | 75.0% | 78.9% |

## Gate switches

- **2024-07-16** -> **ACTIVE**; recent 8 = 10101011 (5W/3L).

## Period metrics

| Period | AURORA Acc | HELIOS Soft Acc | Hard Acc | Raw OPAL Acc | AURORA BA | HELIOS BA | AURORA Brier | HELIOS Brier | Routed | Rescue | Broken |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022_COMMON_NOV_DEC | 57.58% | 57.58% | 57.58% | 57.58% | 58.27% | 58.27% | 0.2567 | 0.2567 | 0 | 0 | 0 |
| 2023 | 71.23% | 71.23% | 71.23% | 67.12% | 71.83% | 71.83% | 0.2118 | 0.2118 | 0 | 0 | 0 |
| 2024 | 70.83% | 71.25% | 71.25% | 70.00% | 69.97% | 70.22% | 0.2006 | 0.1989 | 3 | 2 | 1 |
| 2025 | 64.52% | 66.13% | 66.13% | 64.92% | 62.93% | 64.26% | 0.2276 | 0.2253 | 6 | 5 | 1 |
| 2026 | 60.73% | 61.78% | 61.78% | 63.87% | 61.12% | 62.21% | 0.2477 | 0.2460 | 4 | 3 | 1 |
| 2023-2024 | 71.02% | 71.24% | 71.24% | 68.63% | 71.24% | 71.40% | 0.2059 | 0.2050 | 3 | 2 | 1 |
| 2025-2026 | 62.87% | 64.24% | 64.24% | 64.46% | 62.07% | 63.31% | 0.2363 | 0.2343 | 10 | 8 | 2 |

## 2026 changed calls

| Issue | H3 end | q competence | AURORA | HELIOS | Actual | H3 return | Effect |
|---|---|---:|---|---|---|---:|---|
| 2026-03-11 | 2026-03-13 | 70.0% | UP | DOWN | DOWN | -2.11% | RESCUED |
| 2026-08-03 | 2026-08-05 | 80.0% | DOWN | UP | UP | +3.09% | RESCUED |
| 2026-08-04 | 2026-08-06 | 80.0% | DOWN | UP | UP | +4.98% | RESCUED |
| 2026-08-28 | 2026-09-01 | 80.0% | DOWN | UP | DOWN | -4.95% | BROKEN |

## Dependence-aware bootstrap

- HELIOS_vs_AURORA / 2023-2024 / accuracy / block5: diff=+0.2179 pp; 95%=[-0.4357,+0.8769] pp; P(improve)=61.0%.
- HELIOS_vs_AURORA / 2023-2024 / accuracy / block10: diff=+0.2179 pp; 95%=[-0.4357,+0.8715] pp; P(improve)=61.0%.
- HELIOS_vs_AURORA / 2023-2024 / brier / block5: diff=-0.0009; 95%=[-0.0029,+0.0002]; P(improve)=76.0%.
- HELIOS_vs_AURORA / 2023-2024 / brier / block10: diff=-0.0009; 95%=[-0.0029,+0.0002]; P(improve)=78.4%.
- HELIOS_vs_AURORA / 2023-2024 / logloss / block5: diff=-0.0020; 95%=[-0.0065,+0.0006]; P(improve)=75.8%.
- HELIOS_vs_AURORA / 2023-2024 / logloss / block10: diff=-0.0020; 95%=[-0.0065,+0.0005]; P(improve)=78.7%.
- HELIOS_vs_AURORA / 2025-2026 / accuracy / block5: diff=+1.3667 pp; 95%=[+0.0000,+2.9613] pp; P(improve)=95.7%.
- HELIOS_vs_AURORA / 2025-2026 / accuracy / block10: diff=+1.3667 pp; 95%=[+0.0000,+2.9613] pp; P(improve)=95.9%.
- HELIOS_vs_AURORA / 2025-2026 / brier / block5: diff=-0.0020; 95%=[-0.0047,-0.0001]; P(improve)=98.1%.
- HELIOS_vs_AURORA / 2025-2026 / brier / block10: diff=-0.0020; 95%=[-0.0046,-0.0001]; P(improve)=98.3%.
- HELIOS_vs_AURORA / 2025-2026 / logloss / block5: diff=-0.0043; 95%=[-0.0101,-0.0002]; P(improve)=98.3%.
- HELIOS_vs_AURORA / 2025-2026 / logloss / block10: diff=-0.0043; 95%=[-0.0099,-0.0002]; P(improve)=98.3%.
- HELIOS_vs_AURORA / 2026 / accuracy / block5: diff=+1.0471 pp; 95%=[-1.0471,+3.6649] pp; P(improve)=72.6%.
- HELIOS_vs_AURORA / 2026 / accuracy / block10: diff=+1.0471 pp; 95%=[-1.0471,+3.6649] pp; P(improve)=73.2%.
- HELIOS_vs_AURORA / 2026 / brier / block5: diff=-0.0017; 95%=[-0.0047,+0.0005]; P(improve)=87.7%.
- HELIOS_vs_AURORA / 2026 / brier / block10: diff=-0.0017; 95%=[-0.0047,+0.0005]; P(improve)=87.9%.
- HELIOS_vs_AURORA / 2026 / logloss / block5: diff=-0.0034; 95%=[-0.0096,+0.0009]; P(improve)=87.4%.
- HELIOS_vs_AURORA / 2026 / logloss / block10: diff=-0.0034; 95%=[-0.0096,+0.0009]; P(improve)=87.8%.
- HELIOS_vs_OPAL_RAW / 2023-2024 / accuracy / block5: diff=+2.6144 pp; 95%=[-0.8715,+6.1002] pp; P(improve)=92.4%.
- HELIOS_vs_OPAL_RAW / 2023-2024 / accuracy / block10: diff=+2.6144 pp; 95%=[-0.8715,+6.5359] pp; P(improve)=91.9%.
- HELIOS_vs_OPAL_RAW / 2023-2024 / brier / block5: diff=-0.0130; 95%=[-0.0261,-0.0006]; P(improve)=98.1%.
- HELIOS_vs_OPAL_RAW / 2023-2024 / brier / block10: diff=-0.0130; 95%=[-0.0277,-0.0005]; P(improve)=97.9%.
- HELIOS_vs_OPAL_RAW / 2023-2024 / logloss / block5: diff=-0.0293; 95%=[-0.0589,-0.0027]; P(improve)=98.6%.
- HELIOS_vs_OPAL_RAW / 2023-2024 / logloss / block10: diff=-0.0293; 95%=[-0.0622,-0.0015]; P(improve)=98.2%.
- HELIOS_vs_OPAL_RAW / 2025-2026 / accuracy / block5: diff=-0.2278 pp; 95%=[-2.7335,+2.2779] pp; P(improve)=38.0%.
- HELIOS_vs_OPAL_RAW / 2025-2026 / accuracy / block10: diff=-0.2278 pp; 95%=[-2.5057,+2.0501] pp; P(improve)=38.0%.
- HELIOS_vs_OPAL_RAW / 2025-2026 / brier / block5: diff=-0.0040; 95%=[-0.0142,+0.0055]; P(improve)=79.1%.
- HELIOS_vs_OPAL_RAW / 2025-2026 / brier / block10: diff=-0.0040; 95%=[-0.0144,+0.0053]; P(improve)=77.9%.
- HELIOS_vs_OPAL_RAW / 2025-2026 / logloss / block5: diff=-0.0111; 95%=[-0.0349,+0.0103]; P(improve)=83.1%.
- HELIOS_vs_OPAL_RAW / 2025-2026 / logloss / block10: diff=-0.0111; 95%=[-0.0356,+0.0100]; P(improve)=83.6%.
- HELIOS_vs_OPAL_RAW / 2026 / accuracy / block5: diff=-2.0942 pp; 95%=[-6.2827,+1.5707] pp; P(improve)=12.1%.
- HELIOS_vs_OPAL_RAW / 2026 / accuracy / block10: diff=-2.0942 pp; 95%=[-5.2356,+1.0471] pp; P(improve)=7.9%.
- HELIOS_vs_OPAL_RAW / 2026 / brier / block5: diff=+0.0008; 95%=[-0.0168,+0.0163]; P(improve)=44.8%.
- HELIOS_vs_OPAL_RAW / 2026 / brier / block10: diff=+0.0008; 95%=[-0.0167,+0.0148]; P(improve)=42.7%.
- HELIOS_vs_OPAL_RAW / 2026 / logloss / block5: diff=-0.0020; 95%=[-0.0426,+0.0335]; P(improve)=52.4%.
- HELIOS_vs_OPAL_RAW / 2026 / logloss / block10: diff=-0.0020; 95%=[-0.0436,+0.0305]; P(improve)=50.8%.

## Governance

HELIOS routes only a residual reversal correction. The base AURORA probability is untouched outside active consensus events. All competence evidence is target-matured before use. Because HELIOS was designed after historical error analysis, these results cannot be called pristine confirmation. Any operational challenge to AURORA requires a new prospective HELIOS freeze.
