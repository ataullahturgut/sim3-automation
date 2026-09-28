# GOLD MONTHLY FORECAST — CHALLENGER B / B5 PLS1 METAL ABLATION RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / ALL-4 RETAINED FOR PRIMARY PRICE OBJECTIVE  
**Workflow run:** 36437087929  
**Commit:** 5cbf2b777f028a73f1296ae679eb45d8a124e892  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_B5_PLS1_METAL_ABLATION_FREEZE_2026-09-28.md`

## Reproduction gate
PASS.

The frozen All-4 PLS1 reference was reproduced:
- Expected DEV SigmaAE: 1420.0291314697745
- Observed DEV SigmaAE: **1420.0291314697738**
- Absolute difference: **6.82e-13**
- Expected direction: 20/33
- Observed direction: **20/33**

Therefore the subset comparisons are methodologically aligned with the previously frozen PLS1 V1.

## DEV metal-set ranking
| Rank | Variant | Metals | Features | DEV SigmaAE | Direction | Delta SigmaAE vs All-4 | Delta direction |
|---:|---|---|---:|---:|---:|---:|---:|
| **1** | **M2_ALL4_REFERENCE** | Au+Ag+Pt+Pd | 8 | **1420.0291** | 20/33 | 0.00 | 0 |
| 2 | M3_NO_SILVER | Au+Pt+Pd | 6 | 1454.3225 | **22/33** | +34.29 | +2 |
| 3 | M5_NO_PALLADIUM | Au+Ag+Pt | 6 | 1461.6772 | 19/33 | +41.65 | -1 |
| 4 | M1_GOLD_SILVER | Au+Ag | 4 | 1491.2346 | 20/33 | +71.21 | 0 |
| 5 | M0_GOLD_ONLY | Au | 2 | 1519.4727 | 21/33 | +99.44 | +1 |
| 6 | M4_NO_PLATINUM | Au+Ag+Pd | 6 | 1519.6757 | 20/33 | +99.65 | 0 |

## Interpretation
### Primary price-error objective
**All four metals remain justified.** No frozen removal improves DEV SigmaAE.

### Silver
Removing Silver:
- worsens SigmaAE by **34.29**
- improves direction by **+2 correct months** to 22/33.

Thus Silver is useful for the primary price-error objective under PLS1, while its inclusion is associated with a price-vs-direction trade-off. This is predictive ablation evidence, not a causal statement.

### Platinum
Removing Platinum is the most damaging single-metal removal:
- SigmaAE worsens by **99.65**
- direction stays 20/33.

Within this frozen experiment, Platinum carries the strongest unique incremental price-accuracy evidence among the three non-Gold metals.

### Palladium
Removing Palladium:
- SigmaAE worsens by **41.65**
- direction falls by 1 month.

Palladium therefore adds useful predictive information under the frozen PLS1 setup, although less strongly than Platinum by the primary error metric.

### Gold + Silver only
Keeping only Gold and Silver worsens SigmaAE by **71.21** with no direction gain. Platinum/Palladium jointly therefore add material price-accuracy information beyond Au+Ag.

### Gold only
Gold-only worsens SigmaAE by **99.44** but improves direction by one month. Cross-metal information materially improves the primary price-error objective.

## DEV Pareto view among ablation variants
The only nondominated metal subsets are:
- **M2_ALL4_REFERENCE:** 1420.03 / 20 directions
- **M3_NO_SILVER:** 1454.32 / 22 directions

All-4 is the primary price-error winner. No-Silver is a direction-heavier trade-off variant, not a replacement.

## Cross-family position
Because All-4 remains the DEV winner, the original PLS1 cross-family placement is unchanged:
- **Price-error rank: 3rd** in the frozen main comparison pool.
- It remains dominated by ChHHO-ANFIS and RBFNN DE-ABC on the two-objective DEV view.

No metal-subset variant creates a new cross-family leader.

## 2025 — LOCKED REPORT ONLY
Selected report-only SigmaAE / direction:
- Gold only: 1131.27 / 9
- Gold+Silver: 1023.95 / 10
- All-4: 1058.90 / 10
- No Silver: 1020.34 / 10
- No Platinum: 1025.39 / 10
- No Palladium: 1042.70 / 10

Several subsets retrospectively outperform All-4 on 2025 price error, but **this cannot be used to change the DEV-selected metal set**.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
SigmaAE / direction:
- Gold only: 1416.85 / 5
- Gold+Silver: 1381.03 / 5
- All-4: 1392.69 / 6
- No Silver: 1415.89 / 6
- No Platinum: 1400.52 / 5
- No Palladium: 1405.20 / 5

Again, this period has no selection authority.

## Decision
For PLS1:
- **Primary frozen metal set remains All-4: Gold + Silver + Platinum + Palladium.**
- **No-Silver is retained only as a DEV Pareto trade-off reference** because it gains 2 correct directions at the cost of +34.29 SigmaAE.
- No post-hoc subset expansion is authorized from these results.

## Governance
- DB READ_ONLY.
- Random split: NONE.
- CURRENT8 definitions unchanged.
- PLS internal scaling: training-fold only.
- 2025 locked.
- 2026 quarantined.
- Existing Challenger-A/main Gold path unchanged.

Result payload SHA256:
`2655511d973f59b2a82580ab893d72a9f6e422895297dd40e4252c6bc21bd21f`
