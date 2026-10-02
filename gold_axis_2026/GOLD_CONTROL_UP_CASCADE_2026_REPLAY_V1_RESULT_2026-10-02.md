# GOLD CONTROL — FROZEN UP CASCADE 2026 REPLAY V1 RESULT

**Period:** 2026 observed stress through 2026-08-31.  
**Rules:** frozen; no 2026 tuning.

## Primary UP Verifier V2 — standalone 2026

| Timeline | UP calls | True UP | False UP | Precision | Call-error | False-UP FPR | UP recall | Coverage |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 173 | 4 | 2 | 2 | 50.00% | 50.00% | 2.27% | 2.35% | 2.31% |

Selected experts: \`{"RM_LOGIT": 4}\`.

## Primary UP Verifier V2 inside SQRT HIGH RISK

148 alarms = 74 actual UP + 74 actual DOWN. Primary emits 3 UP calls: 2 true + 1 false; precision 66.67%.

## One-Sided UP-2 on Primary residual

| Residual n | Actual UP | Actual DOWN | UP2 calls | True UP | False UP | Precision | Call-error | Recall | FPR | AUC | Tau |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 145 | 72 | 73 | 7 | 5 | 2 | 71.43% | 28.57% | 6.94% | 2.74% | 0.5225 | 0.554700 |

## Combined positive-UP cascade inside SQRT HIGH RISK

| Calls | True UP | False UP | Precision | Call-error | False-UP FPR | Actual-UP recall | Coverage | Remaining residual | Remaining UP/DOWN |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 7 | 3 | 70.00% | 30.00% | 4.05% | 9.46% | 6.76% | 138 | 67/71 |

Historical frozen checkpoints were reproduced before the 2026 metrics were accepted.
ABSTAIN remains UNCERTAIN; no DOWN authority is inferred.
