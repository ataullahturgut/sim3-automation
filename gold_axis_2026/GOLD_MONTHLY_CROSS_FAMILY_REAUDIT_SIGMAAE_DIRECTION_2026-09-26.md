# GOLD MONTHLY FORECAST — CORRECTED CROSS-FAMILY RE-AUDIT
## Active metrics: DEV ΣAE + direction

**Date:** 2026-09-26  
**Status:** CROSS-FAMILY RE-AUDIT COMPLETE

## 1. Purpose

The prior ELM-vs-ANN family-freeze document was MAPE-centered and is SUPERSEDED for active model-selection purposes.

This audit recomputes the relevant family champions directly from original monthly prediction artifacts using the binding active criteria:

1. DEV cumulative absolute error, ΣAE, lower is better.
2. DEV monthly direction accuracy, higher is better.

DEV = 2022-04..2024-12, n=33.
2025 and 2026 remain reporting-only.

No model was retrained for this audit.

## 2. Audited family champions

### ANN
Original Stage-4 prediction artifacts:
- FULL7 equal-weight ANN ensemble.
- REDUCED4 equal-weight ANN ensemble.

| Model | DEV ΣAE USD | Direction | MAE | RMSE |
|---|---:|---:|---:|---:|
| **FULL7 ANN** | **1,428.86** | 22/33 = 66.67% | 43.30 | 55.63 |
| **REDUCED4 ANN** | 1,431.46 | **24/33 = 72.73%** | 43.38 | **54.97** |

### ELM
Original broad-screen prediction artifacts were recomputed under the active metrics.

Price leaders:
- AOA-ELM: **1,474.10 USD / 20/33**.
- SCA-ELM: **1,508.71 USD / 21/33**.

Direction leader:
- TLBO-ELM: **1,758.75 USD / 23/33 = 69.70%**.

Targeted PSO-TLBO Hybrid ELM:
- 1,487.55 USD / 20/33.

ELM therefore remains a strong single-model price family, but its active-metric candidates are dominated by the ANN ensembles.

### ELMFIS
Current validated frontier:
- ABC-ELMFIS: **1,524.89 USD / 21/33**.
- SMA-ELMFIS: **1,651.45 USD / 25/33 = 75.76%**.
- CQCSA-ELMFIS: 1,731.94 USD / 20/33.

Stage 3A and Stage 3B produced no new Pareto point.

## 3. Global DEV Pareto frontier

Across the audited ELM, ANN and ELMFIS candidates, the active two-objective nondominated set is:

| Global Pareto model | Family | DEV ΣAE USD | Direction |
|---|---|---:|---:|
| **FULL7 ANN** | ANN ensemble | **1,428.86** | 22/33 |
| **REDUCED4 ANN** | ANN ensemble | 1,431.46 | **24/33** |
| **SMA-ELMFIS** | ELMFIS single | 1,651.45 | **25/33** |

Interpretation:
- FULL7 ANN is the active price-error extreme.
- REDUCED4 ANN provides a very small price-error sacrifice for substantially stronger direction.
- SMA-ELMFIS is the global pure-direction extreme, adding one additional correct direction month over REDUCED4 but at materially higher price error.

ABC-ELMFIS is globally dominated by FULL7 ANN.
The best ELM candidates are also globally dominated by ANN ensemble candidates.

## 4. Directional value of SMA-ELMFIS

SMA-ELMFIS is the strongest audited DEV direction model:
- 25/33 = 75.76%.

Comparison:
- FULL7 ANN: 22/33.
- REDUCED4 ANN: 24/33.
- best audited ELM direction model TLBO-ELM: 23/33.

### Complementarity vs FULL7 ANN
Signed forecast-error correlation:
- **0.6493**.

Direction disagreement:
- SMA rescues **6** FULL7 direction misses.
- SMA loses **3** FULL7 direction hits.
- Net directional gain if SMA is always followed on disagreement: +3 months.

### Complementarity vs REDUCED4 ANN
Signed forecast-error correlation:
- **0.6773**.

Direction disagreement:
- SMA rescues **4** REDUCED4 misses.
- SMA loses **3** REDUCED4 hits.
- Net directional gain if SMA is always followed on disagreement: +1 month.

This establishes real DEV complementarity, not merely duplicate signal.

## 5. Predeclared directional-overlay diagnostic

Following the user hypothesis that ELMFIS may be useful primarily for direction, a simple no-fit overlay was tested:

- price-magnitude source = frozen ANN ensemble distance from RW;
- direction-sign source = SMA-ELMFIS;
- no learned weight;
- no parameter fitting.

### DEV
| Overlay | ΣAE USD | Direction |
|---|---:|---:|
| FULL7 magnitude + SMA sign | **1,391.88** | **25/33 = 75.76%** |
| REDUCED4 magnitude + SMA sign | 1,402.84 | **25/33 = 75.76%** |

On DEV, the FULL7-magnitude/SMA-sign overlay improves both active objectives relative to FULL7 and REDUCED4.

### Reporting-only transport/stress
However, this gain does not transport consistently:

| Overlay | 2025 Direction | 2026 Direction | 2025 ΣAE | 2026 ΣAE |
|---|---:|---:|---:|---:|
| FULL7 magnitude + SMA sign | 10/12 = 83.33% | 3/7 = 42.86% | 1,040.52 | 1,813.23 |
| REDUCED4 magnitude + SMA sign | 10/12 = 83.33% | 3/7 = 42.86% | 1,058.14 | 1,763.81 |

For comparison, the frozen ANN ensembles themselves had 91.67% direction in 2025 and 71.43% in 2026 reporting.

Therefore the hard SMA direction override is **not promoted** despite its strong DEV result.

## 6. Agreement / confirmation role

A safer use is as a confirmation signal rather than a forced override.

### FULL7 + SMA direction agreement
- DEV: agreement on 24/33 months (72.73% coverage); accuracy within agreement = **19/24 = 79.17%**.
- 2025: agreement on 11/12; accuracy = **10/11 = 90.91%**.
- 2026: agreement on 5/7; accuracy = **3/5 = 60.00%**.

### REDUCED4 + SMA direction agreement
- DEV: agreement on 26/33 (78.79% coverage); accuracy = **21/26 = 80.77%**.
- 2025: agreement on 11/12; accuracy = **10/11 = 90.91%**.
- 2026: agreement on 5/7; accuracy = **3/5 = 60.00%**.

The confirmation behavior is promising but not uniformly stable, especially in the 2026 stress period.

## 7. Corrected family decision

### Primary price forecasting role
Retain ANN ensembles as the primary family:
- FULL7 = price-error anchor.
- REDUCED4 = balanced price/direction challenger.

### ELM role
Retain as strong single-model benchmark:
- AOA-ELM price benchmark.
- TLBO-ELM direction benchmark within ELM.

### ELMFIS role
Do not promote ELMFIS as the primary price family.

Retain:
- **SMA-ELMFIS = AUXILIARY DIRECTION SPECIALIST**.
- ABC-ELMFIS = internal ELMFIS price benchmark.
- CQCSA = rejected for promotion.

SMA must not hard-override ANN direction by default based on current evidence.
Its scientifically defensible current role is:
- confirmation signal;
- disagreement flag;
- candidate component for a future abstention/router layer;
- secondary direction evidence.

A future router must be trained/validated with a predeclared protocol and must not use 2025/2026 outcomes to tune its rule.

## 8. Control and compliance summary

- Original prediction artifacts used: PASS.
- Model retraining for re-audit: NO.
- DEV-only selection authority: PASS.
- 2025 selection exclusion: PASS.
- 2026 selection exclusion: PASS.
- Active metric contract ΣAE + direction: PASS.
- Global Pareto recomputed: PASS.
- Post-hoc hard SMA override promoted: NO.
- SMA directional specialist role retained: YES.

## 9. Current project state

- ELM: completed.
- ANN: completed.
- ELMFIS Stage 0: completed.
- ELMFIS Stage 1: completed 33/33.
- ELMFIS Stage 2: completed.
- ELMFIS Stage 3A: completed 6/6.
- ELMFIS Stage 3B: completed 3/3.
- ELMFIS Stage 3C CQCSA: completed.
- Cross-family active-metric re-audit: completed.

**Current working hierarchy:**
1. ANN ensembles for primary monthly price forecasting.
2. SMA-ELMFIS retained as auxiliary direction specialist.
3. ELM retained as single-model benchmark family.
