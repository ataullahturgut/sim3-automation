# GOLD CONTROL — CBR CASCADE-ROUTE-CONSISTENT EXTENSION V1 RESULT

**Status:** `CASCADE_ROUTE_CONSISTENT_NOT_SUPPORTED`  
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
| 2022 | 11 | 98 | 10 | 6 | 4 | 0.6 | 1.0 | 0.8 |
| 2023 | 2 | 109 | 1 | 1 | 0 | 1.0 | 1.0 | 0.0 |
| 2024 | 13 | 111 | 5 | 2 | 3 | 0.4 | 0.3333333333333333 | 0.42857142857142855 |

Pooled 2022–2024: n=26, DOWN calls=16, correct=9, false=7, precision=0.5625, recall=0.6923076923076923, FPR=0.5384615384615384.

## Locked 2025 transport

n=74; DOWN calls=36; correct=20; false=16; precision=0.5555555555555556; recall=0.5128205128205128; FPR=0.45714285714285713; baseline=0.527027027027027; precision lift=0.028528528528528607; supportive=True.

No threshold, K, DTW band or representation was changed. 2025 remained locked transport only; 2026 was not used.
