# GOLD SHORT-HORIZON GLOBAL XAU — Stage 2 H3 Direction Robustness Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / ROBUST_PASS**  
**Workflow:** Gold Short Horizon Global XAU Stage2 Robustness  
**Run:** **36911524415**  
**Artifact:** **11186831488**  
**Artifact digest:** `sha256:829cda0755c1bcada9ea7a1f6ba661fee3aa6a37018d0d8a066f923920720297`  
**Authority:** `GOLD_SHORT_HORIZON_GLOBAL_XAU_STAGE2_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

The only Stage-1 global-XAU pass survives the frozen robustness audit.

Frozen H3 direction engine:

- target: global XAU/USD daily spot-average research series
- horizon: **H3**
- features: **CORE3**
- model: **Logistic L2**.

CORE3:
- Gold
- Silver
- Platinum.

No external macro block replaces CORE3.

H5 remains secondary only and does not clear the 1% direction gate.

2025 remains unopened.

## 2. Aggregate H3 result

Binding baseline:
- **EXPAND_PREV** historical UP prevalence.

CORE3 / Logistic L2:
- Brier: **0.246731**
- baseline Brier: **0.249712**
- relative Brier improvement: **+1.194%**
- log loss: **0.686634**
- baseline log loss: **0.692572**
- accuracy: **55.23%**
- balanced accuracy: **54.78%**
- prediction SD: **0.04422**
- DEV n: **755**.

Frozen robustness gate:
**PASS**.

## 3. Annual robustness

| Year | N | Brier | Baseline Brier | Relative improvement |
|---|---:|---:|---:|---:|
| 2022 | 250 | 0.245598 | 0.250574 | **+1.99%** |
| 2023 | 251 | 0.249529 | 0.249916 | **+0.15%** |
| 2024 | 254 | 0.245081 | 0.248664 | **+1.44%** |

Annual evidence:
- positive Brier improvement: **3/3 years**
- worst year: **+0.15%**
- no annual deterioration
- every year n >= 200.

The weakest year is 2023, but it remains slightly positive versus the frozen baseline.

## 4. Representation comparison

| Representation | Brier | Relative improvement | Log loss | Prediction SD |
|---|---:|---:|---:|---:|
| GOLD_ONLY | 0.250081 | **-0.15%** | 0.693313 | 0.0177 |
| **CORE3** | **0.246731** | **+1.19%** | **0.686634** | 0.0442 |
| CORE4 | 0.247975 | +0.70% | 0.689301 | 0.0492 |
| CORE3_SAFE_EXTERNAL_RAW | 0.250550 | -0.34% | 0.694460 | 0.0653 |
| CORE3_SAFE_EXTERNAL_CHG | 0.250581 | -0.35% | 0.694485 | 0.0629 |

Binding decision:
**retain CORE3**.

Interpretation:
- Gold alone is insufficient;
- Silver + Platinum add the useful direction information;
- Palladium weakens the edge somewhat;
- the current rates / FX / VIX / Nasdaq external block does not improve H3 direction under this Logistic contract.

## 5. H5 secondary diagnostic

H5 does not clear the frozen >=1% relative Brier gate.

Therefore:
- H5 remains documented as suggestive secondary evidence only;
- it cannot override H3;
- no multi-horizon action rule is authorized from H5.

## 6. Model-family implication

The robust global-XAU direction signal is low-capacity:

> **CORE3 / Logistic L2**

The project does not currently justify replacing it with:
- boosting
- deeper sequence models
- broader external feature stacks.

This is evidence that the useful short-horizon information is primarily in the joint recent path of:
- Gold
- Silver
- Platinum.

## 7. Scope of the conclusion

Supported:

> There is a small but robust pre-2025 probabilistic edge in forecasting whether global XAU will be UP or DOWN over the next three daily observations.

Not supported yet:
- reliable return magnitude
- reliable Q10/Q50/Q90 distribution
- a profitable trading rule
- an executable live instrument mapping.

## 8. 2025

2025 remains:
**FROZEN / UNOPENED FOR SELECTION**

No Stage-2 result uses 2025 to choose:
- representation
- model
- probability threshold
- economic rule.

## 9. Artifact hashes

- `global_xau_stage2_h3_core3_coefficients.csv`: `291f0b5a3a15331a9cf1400930ba232f0eba6fbd15f59dc1428a1d4a96307a49`
- `global_xau_stage2_h3_aggregate.csv`: `fce81ab7583972e31aef00152e46c7e6cd1f82466562361e7329141a480a0b10`
- `STAGE2_RESULT.md`: `7cc7afebed0cdf1e97b8a964705ca47bdc8a46be46d05155ba4533b7b00139c5`
- `global_xau_stage2_h5_secondary.csv`: `b9f232a59e1aa44a7b1bf12d294082ebb2c4aaf4abc5d1b70ea68c7b0602a40d`
- `global_xau_stage2_h3_baselines.csv`: `cc95d4b02139ae3033771920f9684f3cebdb9b068422a4f77eb385895f8024e4`
- `global_xau_stage2_h3_coefficient_stability.csv`: `d464be9081590d3aa8d9e7d74cd8807401201b215c197149000d2837c4c5ac35`
- `global_xau_stage2_h3_volatility.csv`: `609a52ea223a5cc7aaf7080b2ac40ca91d757430dc9c00487a04330b2e03aa4b`
- `global_xau_stage2_h3_predictions.csv`: `4b2f62fb229e47f0a119f6d61090f0ca0b0660bde0b15e6cfdb8b2615723d257`
- `global_xau_stage2_h3_years.csv`: `2bfa0e450008eeb3b1e4cfa42c3c072c545ab890d50f3c0d78be0f72639b7917`
- `global_xau_stage2_representation_decisions.csv`: `d3dce894af24b1b8c611b25a433b1edc57353f34eb70178f3ba6319ea3c8a7a1`.

## 10. Decision

**Stage 2 = COMPLETE / ROBUST_PASS.**

Frozen current direction engine:
**H3 / CORE3 / Logistic L2**

## 11. Exact next stage

**Stage 3 — Probability Calibration / Conviction Audit**

Purpose:
determine whether the robust H3 probability contains economically usable confidence information without inventing a return-magnitude model.

Required:
1. calibration intercept / slope
2. ECE / reliability bins
3. raw versus Platt / isotonic calibration under chronological fit-only rules
4. frozen probability bands:
   - <=0.40
   - 0.40–0.45
   - 0.45–0.50
   - 0.50–0.55
   - 0.55–0.60
   - >=0.60
5. realized H3 UP rate by band
6. sample support / annual stability by band
7. no P&L threshold optimization
8. 2025 remains unopened.

Only if confidence bands separate realized direction reliably should a direction-only economic architecture be designed.
