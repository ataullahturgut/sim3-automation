# GOLD H3 — Topology Competence Gate V1 — 2026-10-05

**Status:** POSTHOC_TOPOLOGY_GATE_CHALLENGER — not prospectively validated.

## Frozen primary rule

**TCG-V1 = allow a DPTC flip only when strong_pro_risk is TRUE.**
This is the already-defined label-free topology: Gold–Nasdaq positive and Gold–VIX negative, with the frozen significance condition. No RESCUE/BROKEN label is used to set a numeric threshold.

## Primary gate results

| Year | Ungated R/B/net | TCG actions | TCG R/B/net | TCG precision |
|---:|---:|---:|---:|---:|
| 2023 | 6/5/+1 | 0 | 0/0/+0 | — |
| 2024 | 2/4/-2 | 0 | 0/0/+0 | — |
| 2025 | 4/5/-1 | 3 | 2/1/+1 | 66.7% |
| 2026 | 11/2/+9 | 11 | 9/2/+7 | 81.8% |

- Across the harmonized 2023–2026 action sample: ungated **23/16 = net +7** on 39 actions; TCG-V1 **11/3 = net +8** on 14 actions.
- Primary-gate odds ratio for RESCUE vs rejected actions: **3.97**, Fisher exact **p=0.0930**.
- Pre-2026 only: **2/3 rescue**, 1 broken, net **+1**.

## Exact Yahoo-lineage accuracy projection

| Period | Baseline | TCG-V1 | Accuracy |
|---|---:|---:|---:|
| 2025 | 171/248 | 172/248 | 69.35% |
| 2026 | 126/191 | 133/191 | 69.63% |
| combined | 297/439 | 305/439 | 69.48% |

## Sensitivity family

| Gate | 2023 net | 2024 net | 2025 net | 2026 net | All R/B/net | Actions |
|---|---:|---:|---:|---:|---:|---:|
| TCG_V1_STRONG_PRO_RISK | +0 | +0 | +1 | +7 | 11/3/+8 | 14 |
| TCG_V1_PHASE | +0 | +0 | +1 | +7 | 11/3/+8 | 14 |
| TCG_P3 | +0 | +0 | +0 | +5 | 8/3/+5 | 11 |
| TCG_OIL_NEG | +0 | +0 | +1 | +7 | 10/2/+8 | 12 |
| TCG_P3_OIL_NEG | +0 | +0 | +0 | +5 | 7/2/+5 | 9 |
| TCG_TRIAD | +0 | +0 | +0 | +7 | 9/2/+7 | 11 |

## Scientific reading

- The primary gate is intentionally simple. It asks whether the cross-asset topology associated with competence is present; it does not ask whether the market is generally volatile or structurally anomalous.
- 2023–2024 are source-robust historical reconstructions, not exact Yahoo lineage.
- 2025–2026 projections use the exact frozen Yahoo-lineage action outcomes.
- Because the topology hypothesis was diagnosed using consumed 2026 evidence, TCG-V1 cannot be called independently validated. It is a challenger for prospective shadow evaluation.
- Sensitivity gates are reported to show how persistence and oil-decoupling restrictions affect selectivity; they are not selected by best historical performance.
