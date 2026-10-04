# GOLD H3 — SAGE V2 + RuleFlow V3-TG Combined Diagnostic

**Date:** 2026-10-04  
**Status:** RETROSPECTIVE DIAGNOSTIC ONLY — NOT INDEPENDENT OOS VALIDATION  
**Baseline:** HELIOS V5-DCE  
**Layer 1:** SAGE-H3 V2 exception-only  
**Layer 2:** RuleFlow V3-TG topology-gated reversal exception

## 2026 full mature universe

- N = **191**
- HELIOS V5-DCE: **121/191 = 63.35%**
- SAGE-H3 V2 exception-only: **125/191 = 65.45%**
- SAGE V2 + RuleFlow V3-TG union: **126/191 = 65.97%**

### Balanced accuracy
- V5-DCE: **63.76%**
- SAGE V2: **65.81%**
- Combined: **66.31%**

### Confusion counts
| System | TP | TN | FP | FN |
|---|---:|---:|---:|---:|
| V5-DCE | 66 | 55 | 45 | 25 |
| SAGE V2 | 67 | 58 | 42 | 24 |
| Combined | 67 | 59 | 41 | 24 |

## Exception chronology

SAGE V2 2026 exception dates:
- 2026-02-03 — rescue
- 2026-05-26 — rescue
- 2026-07-10 — rescue
- 2026-07-15 — rescue

RuleFlow V3-TG surviving 2026 exception:
- 2026-02-11 — rescue

There is **no overlap** between the four SAGE V2 exceptions and the surviving RuleFlow V3-TG exception. Therefore the combined union adds one additional correct call to SAGE V2: **125 -> 126**.

The four RuleFlow V2 broken calls in 2026 Q2-Q3 (2026-06-17, 2026-06-25, 2026-07-29, 2026-08-04) are vetoed by V3-TG and therefore do not damage the SAGE baseline.

## Interpretation

The topology-gated RuleFlow mechanism is complementary to SAGE V2 in the 2026 retrospective replay: it contributes one additional DOWN rescue on 2026-02-11 without removing any SAGE rescue.

**Important scientific caveat:** RuleFlow V3-TG was designed after observing 2026 Q2-Q3 RuleFlow failures. Therefore the 2026 combined result is a post-hoc diagnostic and cannot be labeled independent validation or clean OOS evidence. SAGE V2 also remains retrospective development evidence for 2026. The frozen identities must be tested on unseen prospective origins and separately replayed on earlier untouched years.
