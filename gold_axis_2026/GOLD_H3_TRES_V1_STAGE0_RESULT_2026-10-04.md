# TRES-H3 V1 — STAGE 0 EVENT-TIME AUDIT RESULT

**Status:** **PASS**  
- panel rows: **1029**
- audited rows: **1029**
- failures: **0**
- max |recomputed target_r3 - panel target_r3|: **9.975e-17**

## Primary 1.00×sigma20 event counts

| Year | N | Continuation | Reversal | Censored | Terminal reversal |
|---:|---:|---:|---:|---:|---:|
| 2022 | 131 | 71 | 23 | 37 | 47 |
| 2023 | 219 | 134 | 35 | 50 | 74 |
| 2024 | 240 | 134 | 41 | 65 | 86 |
| 2025 | 248 | 134 | 52 | 62 | 90 |
| 2026 | 191 | 77 | 54 | 60 | 84 |

## Terminal H3 reversal rate conditional on first-passage state

### Barrier 0.75× sigma20
- CENSORED: n=177, terminal reversal **46.33%**, mean |H3| **0.41%**
- CONTINUATION: n=624, terminal reversal **13.14%**, mean |H3| **1.68%**
- REVERSAL: n=228, terminal reversal **95.18%**, mean |H3| **1.69%**

### Barrier 1.00× sigma20
- CENSORED: n=274, terminal reversal **46.35%**, mean |H3| **0.53%**
- CONTINUATION: n=550, terminal reversal **10.18%**, mean |H3| **1.81%**
- REVERSAL: n=205, terminal reversal **96.59%**, mean |H3| **1.80%**

### Barrier 1.25× sigma20
- CENSORED: n=403, terminal reversal **46.15%**, mean |H3| **0.65%**
- CONTINUATION: n=461, terminal reversal **7.38%**, mean |H3| **1.99%**
- REVERSAL: n=165, terminal reversal **97.58%**, mean |H3| **1.99%**

## Integrity interpretation

- origin / H1 / H2 / H3 date mapping is internally consistent with the frozen H3 target.
- primary and robustness first-passage labels were constructed without future information entering the origin barrier.
- Stage 1 competing-risk modeling is authorized.
