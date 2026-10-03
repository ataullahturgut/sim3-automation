# DIVERGE-PROXY-H3 V1 — RESULT

**Status:** **NO_ELIGIBLE_DIVERGE_THRESHOLD**  
**Evidence:** retrospective proxy mechanism test with strict prior-date alignment; not claimed as authority or pristine historical PIT.

## Source audit

| Source | Series | Rows | Min | Max | Status |
|---|---|---:|---|---|---|
| FROZEN_METALS | GOLD/SILVER | 4202 | 2010-02-16 | 2026-09-29 | PASS |
| YAHOO_CHART | DXY_PROXY | 1446 | 2021-01-04 | 2026-10-02 | PASS |
| YAHOO_CHART | TNX_PROXY | 1444 | 2021-01-04 | 2026-10-02 | PASS |
| YAHOO_CHART | NDX | 1444 | 2021-01-04 | 2026-10-02 | PASS |
| YAHOO_CHART | VIX | 1446 | 2021-01-04 | 2026-10-02 | PASS |

## DEV 2023-2024 threshold grid

| Th | Candidate | Precision | Recall | Rate | F2 | Eligible |
|---:|---:|---:|---:|---:|---:|---|
| 0.35 | 339 | 29.20% | 89.19% | 87.37% | 0.6322 | False |
| 0.40 | 290 | 29.66% | 77.48% | 74.74% | 0.5858 | False |
| 0.45 | 238 | 32.77% | 70.27% | 61.34% | 0.5718 | False |
| 0.50 | 177 | 30.51% | 48.65% | 45.62% | 0.4348 | False |
| 0.55 | 121 | 28.10% | 30.63% | 31.19% | 0.3009 | False |
| 0.60 | 64 | 21.88% | 12.61% | 16.49% | 0.1378 | False |

## Governance

No 2026 outcome was used for feature, lag, threshold, proxy source, or confirmation selection. 2026 was evaluated only if the preregistered 2025 confirmation gate passed. DIVERGE is not promoted to HELIOS from this result alone.
