# TRES-H3 V1 — STAGE 1 COMPETING-RISK RESULT

**Status:** **TRES_EVENT_SIGNAL_PASS**  
- predictions: **679**
- scored origins: **2024-01-02 .. 2026-09-24**
- cumulative-incidence identity failures: **0**
- training-maturity leakage failures: **0**
- multiclass event log loss: **1.0519**
- first-passage reversal Brier: **0.1630**

## Aggregate top-vs-bottom F_reversal quintile

- first-passage reversal: **4.41% -> 34.56%**, separation **+30.15 pp**
- terminal H3 reversal: **20.59% -> 52.94%**, separation **+32.35 pp**

## Half-year stability

| Block | N | FP low | FP high | FP sep | Terminal low | Terminal high | Terminal sep | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024_H1 | 116 | 4.2% | 20.8% | +16.7pp | 16.7% | 66.7% | +50.0pp | 0.1181 |
| 2024_H2 | 124 | 8.0% | 40.0% | +32.0pp | 16.0% | 56.0% | +40.0pp | 0.1532 |
| 2025_H1 | 119 | 8.3% | 41.7% | +33.3pp | 29.2% | 75.0% | +45.8pp | 0.1763 |
| 2025_H2 | 129 | 3.8% | 26.9% | +23.1pp | 15.4% | 34.6% | +19.2pp | 0.1337 |
| 2026_H1 | 128 | 3.8% | 42.3% | +38.5pp | 30.8% | 53.8% | +23.1pp | 0.1913 |
| 2026_H2 | 63 | 15.4% | 30.8% | +15.4pp | 30.8% | 46.2% | +15.4pp | 0.2429 |

## Gate

- positive first-passage blocks: **6/6** (required 5)
- non-negative terminal-transfer blocks: **6/6** (required 5)
- Stage 1 passed. Stage 2 V5 error-risk modeling is authorized.
- No FLIP/DAMP threshold has been selected in Stage 1.
