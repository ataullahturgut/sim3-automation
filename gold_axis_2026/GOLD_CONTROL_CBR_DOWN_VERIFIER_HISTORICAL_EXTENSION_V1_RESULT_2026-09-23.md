# GOLD CONTROL — CBR DOWN VERIFIER HISTORICAL EXTENSION V1 RESULT

**Status:** `HISTORICAL_EXTENSION_NOT_SUPPORTED`  
**Integrity errors:** none

## External/path integrity

- external reconstruction pass: True
- overlap path harmonization n: 345
- median same-date path correlation: 0.9999137678740709
- median same/shifted DTW ratio: 0.013228373983626128
- fraction same-date DTW below shifted median: 1.0

## Historical extension results

| Year | n | Train n | DOWN calls | Correct | False | Precision | Recall | FPR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 11 | 240 | 6 | 3 | 3 | 0.5 | 0.5 | 0.6 |
| 2023 | 2 | 251 | 1 | 0 | 1 | 0.0 | 0.0 | 1.0 |
| 2024 | 13 | 253 | 5 | 3 | 2 | 0.6 | 0.5 | 0.2857142857142857 |

Pooled 2022–2024: n=26, DOWN calls=12, correct=6, false=6, precision=0.5, recall=0.46153846153846156, FPR=0.46153846153846156.

## Locked 2025 transport

n=74; DOWN calls=33; correct=18; false=15; precision=0.5454545454545454; recall=0.46153846153846156; FPR=0.42857142857142855; baseline=0.527027027027027; precision lift=0.01842751842751844; supportive=True.

No threshold, K, DTW band or representation was changed. 2025 remained locked transport only; 2026 was not used.
