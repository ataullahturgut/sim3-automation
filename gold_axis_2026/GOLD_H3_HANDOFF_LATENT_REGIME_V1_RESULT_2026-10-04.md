# GOLD H3 — Handoff Latent Regime V1 Result

**Status:** NO_TRUSTED_REGIME

## Unsupervised 2023-2024 regime discovery

- development origins: **460**
- selected K: **2**

| K | Silhouette |
|---:|---:|
| 2 | 0.1723 |
| 3 | 0.1567 |
| 4 | 0.1477 |
| 5 | 0.1517 |

## 2025 Handoff reliability by latent regime

| Regime | Actions | Rescue | Broken | Net | Precision | Trusted |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 12 | 4 | 8 | -4 | 33.3% | False |
| 1 | 1 | 0 | 1 | -1 | 0.0% | False |

Trusted regimes frozen from 2025: **none**

## Decision

No latent regime met the frozen 2025 Handoff trust gate. V1 closes without a 2026 assisted claim.

## Interpretation discipline

- Regime labels were learned without Handoff outcomes or reversal labels.
- 2025 alone determined which regimes, if any, were trusted.
- 2026 did not choose K, centroids, preprocessing, thresholds, or trusted regimes.
- Because the Handoff hypothesis itself originated from retrospective 2026 research, this remains a strict retrospective stress rather than pristine prospective OOS validation.
