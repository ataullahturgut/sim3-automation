# GLOBAL XAU R2 — Regime / Distribution Shift Diagnostic

**Status:** DIAGNOSTIC ONLY — NO RETUNING

## Probability / outcome state

| Period | N | Mean P(UP) | P SD | Actual UP | Accuracy |
|---|---:|---:|---:|---:|---:|
| 2025 | 253 | 0.500 | 0.058 | 61.7% | 50.2% |
| 2026 | 191 | 0.553 | 0.104 | 47.6% | 44.0% |
| 2026-07 | 23 | 0.546 | 0.042 | 34.8% | 30.4% |
| 2026-08 | 21 | 0.475 | 0.044 | 66.7% | 47.6% |
| 2026-09 | 19 | 0.536 | 0.027 | 36.8% | 47.4% |

## Largest feature-distribution shifts
### TRANSPORT_2025
- silver_r21: mean shift +0.70 SD, std ratio 1.10, PSI 1.385.
- gold_r21: mean shift +0.75 SD, std ratio 1.06, PSI 0.746.
- sigma20: mean shift +0.89 SD, std ratio 1.67, PSI 0.514.
- platinum_r21: mean shift +0.92 SD, std ratio 1.52, PSI 0.486.
- silver_r5: mean shift +0.40 SD, std ratio 1.05, PSI 0.310.
### OPENED_2026
- sigma20: mean shift +7.88 SD, std ratio 14.93, PSI 7.768.
- gold_r21: mean shift -0.22 SD, std ratio 2.15, PSI 0.663.
- gold_r5: mean shift -0.16 SD, std ratio 2.78, PSI 0.571.
- silver_r21: mean shift -0.06 SD, std ratio 2.36, PSI 0.558.
- silver_r5: mean shift -0.10 SD, std ratio 2.35, PSI 0.536.
### 2026_JUL_SEP
- sigma20: mean shift +1.25 SD, std ratio 0.80, PSI 7.765.
- gold_r21: mean shift -0.02 SD, std ratio 1.69, PSI 0.645.
- gold_r10: mean shift +0.05 SD, std ratio 1.44, PSI 0.538.
- silver_r21: mean shift -0.18 SD, std ratio 1.55, PSI 0.499.
- platinum_r5: mean shift +0.24 SD, std ratio 0.97, PSI 0.373.

These diagnostics describe failure anatomy only. They do not authorize a post-hoc regime gate or threshold change.
