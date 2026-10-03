# FRS-H3 V1 — DAMPING / CALIBRATION DIAGNOSTIC

**Status:** retrospective development diagnostic only.

This diagnostic does not change the fuzzy evidence layer. It asks whether fuzzy uncertainty should be used to shrink V5 confidence rather than reverse its direction.

## Same-universe V5 baseline

- n: **452**
- accuracy: **65.93%**
- Brier: **0.2279**
- Log loss: **0.6612**

## Fuzzy DAMP-only comparison

| Representation | Native flips | Damps | Abstain | DAMP-only Brier | Δ Brier | DAMP-only logloss | Δ logloss |
|---|---:|---:|---:|---:|---:|---:|---:|
| HESITANT | 177 | 72 | 0 | 0.2240 | -0.0039 | 0.6515 | -0.0097 |
| IFS | 175 | 74 | 0 | 0.2240 | -0.0039 | 0.6515 | -0.0097 |
| NEUTROSOPHIC | 115 | 134 | 0 | 0.2240 | -0.0039 | 0.6515 | -0.0097 |
| IT2 | 116 | 120 | 102 | 0.2314 | +0.0035 | 0.6645 | +0.0034 |
| PYTHAGOREAN | 0 | 65 | 300 | 0.2373 | +0.0094 | 0.6754 | +0.0142 |
| PICTURE | 84 | 46 | 194 | 0.2375 | +0.0096 | 0.6795 | +0.0183 |
| T1 | 22 | 67 | 301 | 0.2456 | +0.0177 | 0.6945 | +0.0333 |
| QRUNG3 | 0 | 0 | 447 | 0.2493 | +0.0214 | 0.6928 | +0.0316 |
