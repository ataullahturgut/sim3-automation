# GOLD H3 — Latent-Regime Handoff V1 Result

**Status:** NO_ELIGIBLE_2025_REGIME

## Unsupervised regime fit — 2023-2024 only

- training rows: **460**
- selected K by BIC: **2**
- BIC: K=2: 9933.4, K=3: 9995.9, K=4: 10205.9

## 2025 Handoff reliability by frozen regime

| Regime | Alarms | Rescue | Broken | Raw precision | Posterior mean | P(precision>50%) | Eligible |
|---|---:|---:|---:|---:|---:|---:|---|
| R1_risk+0.32_trend-0.26_topo+0.14 | 13 | 4 | 9 | 30.8% | 32.1% | 8.2% | False |

## Decision

No frozen latent regime passed the 2025 Bayesian reliability gate. V1 closes without using 2026 to manufacture a rule.

## Governance

Regimes were fit without 2025/2026 labels. 2025 was used only for Bayesian regime reliability. 2026 did not choose K, features, scaling, confidence threshold, or reliability threshold. Because the Handoff hypothesis itself arose from 2026 diagnostics, this remains strict retrospective stress evidence rather than pristine prospective OOS validation.
