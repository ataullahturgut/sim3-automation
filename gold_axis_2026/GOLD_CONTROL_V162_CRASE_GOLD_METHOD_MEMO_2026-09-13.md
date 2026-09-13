# Gold Control V1.62 — CRASE-Gold Prototype Method Memo

## Purpose

This branch tests a method-development hypothesis rather than another standalone gold classifier. CRASE-Gold means **Causal Regime-Adaptive Selective Expert Forecasting for Gold**.

The method does not directly learn UP/DOWN. At each H5 origin it estimates which frozen expert is locally reliable under a regime similar to the current one, using only already-matured H5 outcomes. It then combines only positive local reliability and abstains when the causal reliability mass or directional agreement is too weak.

## Fixed experts

- H5_BASE_QB
- H5_PD_RM_QB
- TREND20
- GC_TREND3

## Fixed regime state

Gold momentum/volatility, realized downside/jump state, lagged GC futures proxy state, broad USD, real 10Y yield, BOCPD and FAST/SLOW context.

## Core method

For each expert k and current origin t:

1. Keep only prior expert forecasts whose H5 target has matured by t.
2. Measure similarity between current regime and prior regimes using origin-local robust scaling.
3. Use the 63 nearest matured regimes and apply both similarity and recency weights.
4. Compute local weighted balanced accuracy.
5. Penalize experts whose prior local predictions collapse toward one direction.
6. Shrink reliability when effective sample size is small.
7. Combine current expert directions with the resulting positive causal reliability scores.
8. Return NO_SIGNAL when aggregate reliability or directional agreement is insufficient.

The frozen reliability score is:

`max(0, 2*local_balanced_accuracy - 1) * degeneracy_penalty * support_factor`

This explicitly targets the one-class failure repeatedly observed in 2025/2026 successor experiments.

## Evidence limitations

V1.62 is a retrospective method-development diagnostic. 2025/2026 are researcher-visible. Even if the support gate passes, prospective shadow evidence is required. The method is **not yet claimed to be novel** until a formal novelty audit establishes that the exact combination and mathematical formulation are distinct from prior dynamic model averaging, mixture-of-experts, local learning and selective prediction methods.

No production authority, action mapping, automatic selector or automatic ensemble is enabled.
