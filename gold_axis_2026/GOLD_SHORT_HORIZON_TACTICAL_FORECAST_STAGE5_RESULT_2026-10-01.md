# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 5 Forecast-Head Reconciliation Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / NO_RECONCILIATION_PASS**  
**Workflow:** Gold Short Horizon Stage5 Head Reconciliation  
**Run:** **36892132569**  
**Artifact:** **11177455544**  
**Artifact digest:** `sha256:6363c1687cb6ced34b3119f58fa03261ac7c9c733728d5991fdb96d86b1229b5`  
**Authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE5_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

The preregistered categorical reconciliation architecture does **not** earn promotion.

Therefore:

- do **not** collapse the three frozen H3 heads into ALIGNED_UP / ALIGNED_DOWN / HIGH_DOWNSIDE categorical states;
- retain the raw continuous forecast object:
  - H3 `P_UP`
  - H3 point-return estimate
  - H3 Q10 / Q50 / Q90;
- Stage 6 tactical allocation / utility research must use those raw head outputs directly.

No Stage-5 threshold is retuned.

2025 remains frozen.

## 2. Frozen inputs

From corrected Stage-2 OOS predictions:

- Direction: CORE3 / XGB_CLASS
- Point return: GOLD_ONLY / LGBM_REG
- Distribution: GOLD_ONLY / LGBM_QUANT.

DEV:
- 2022-2024
- **749 origins**.

No model was refit in Stage 5.

## 3. Unconditional DEV context

- H3 UP rate: **53.81%**
- H3 DOWN rate: **46.06%**
- mean H3 return: **+0.154%**
- median H3 return: **+0.153%**
- mean absolute H3 return: **1.355%**
- severe-downside frequency: **13.08%**
- strong-upside frequency: **16.02%**.

Tail definitions use origin-known:
`hvol = sigma20 * sqrt(3)`.

## 4. Preregistered head-vote rules

Direction vote:
- UP if P_UP >= 0.55
- DOWN if P_UP <= 0.45
- else NEUTRAL.

Return / Q50 vote:
- dead-band = 0.25 × hvol
- UP above +dead-band
- DOWN below -dead-band
- else NEUTRAL.

Directional states:
- ALIGNED_UP
- ALIGNED_DOWN
- LOW_CONVICTION
- MIXED.

Risk flag:
- HIGH_DOWNSIDE if Q10 <= -1.0 × hvol.

No threshold search followed.

## 5. Usefulness gate result

| Component | N | Realized key rate | Unconditional | Lift | Mean realized H3 return | Gate |
|---|---:|---:|---:|---:|---:|---|
| **ALIGNED_UP** | **9** | UP **66.67%** | 53.81% | **+12.86 pp** | **+0.655%** | **FAIL** |
| **ALIGNED_DOWN** | **4** | DOWN **50.00%** | 46.06% | +3.94 pp | **+0.351%** | **FAIL** |
| **HIGH_DOWNSIDE** | **472** | severe downside **16.95%** | 13.08% | +3.87 pp | +0.124% | **FAIL** |

Why ALIGNED_UP fails despite attractive realized statistics:
- only **9** DEV origins;
- frozen minimum was 30;
- yearly support was:
  - 2022: 6
  - 2023: 2
  - 2024: 1
- it fails the minimum per-year support requirement.

Why ALIGNED_DOWN fails:
- only **4** origins;
- realized mean return is actually positive;
- downside lift is too small.

Why HIGH_DOWNSIDE fails:
- 472 / 749 origins are flagged;
- tail-risk lift is only **+3.87 percentage points**;
- frozen requirement was +5 pp.

## 6. Directional-state frequencies

| State | N | Frequency | Realized UP | Mean H3 return | Severe-downside |
|---|---:|---:|---:|---:|---:|
| ALIGNED_UP | 9 | **1.2%** | **66.7%** | **+0.655%** | 11.1% |
| ALIGNED_DOWN | 4 | **0.5%** | 50.0% | **+0.351%** | 25.0% |
| LOW_CONVICTION | 699 | **93.3%** | 53.8% | +0.156% | 12.9% |
| MIXED | 37 | **4.9%** | 51.4% | -0.035% | 16.2% |

The frozen thresholds create an overwhelmingly LOW_CONVICTION state.

That makes the categorical architecture operationally uninformative.

## 7. Low-conviction diagnostic

LOW_CONVICTION:
- n = **699**
- mean absolute H3 return = **1.342%**.

Unconditional:
- mean absolute H3 return = **1.355%**.

Relative change:
- about **-1.0%**.

Thus LOW_CONVICTION does not isolate a materially quieter market.

## 8. Mixed-state diagnostic

MIXED:
- n = 37
- UP rate = **51.35%**
- mean H3 return = **-0.035%**
- mean absolute H3 return ≈ **1.497%**
- severe-downside frequency = **16.2%**.

MIXED is directionally close to random but somewhat higher-magnitude than the unconditional sample.

This is descriptive only and does not create a new gate.

## 9. Scientific interpretation

The failure is informative.

The three frozen H3 heads contain modest predictive information individually, but strict vote alignment discards too much information:

- direction probability often remains near the middle;
- point-return magnitudes are small relative to realized H3 volatility;
- Q50 frequently sits inside the preregistered volatility dead-band.

Therefore forcing all heads into one hard categorical label loses useful continuous information.

The correct next architecture is not a looser post-hoc state threshold.

It is:

> preserve `P_UP`, point return, Q10, Q50 and Q90 as a **continuous forecast vector**, then define investment utility / action rules transparently from that vector.

## 10. What is explicitly rejected

Do not:
- lower 0.55/0.45 thresholds after seeing the result;
- shrink the 0.25×hvol dead-band;
- redefine HIGH_DOWNSIDE to force a PASS;
- create a volatility-specific alignment rule from DEV hindsight;
- inspect 2025 to choose reconciliation thresholds.

The categorical reconciliation hypothesis is closed under the current preregistered design.

## 11. Artifact hashes

- `stage5_reconciled_forecasts.csv`: `39e2fe83f75f1df777550a265903c06ddb4c6515f6cd4e63e92256e4a4152f91`
- `stage5_state_summary.csv`: `9916aa15a30279e500f49626a3c1d5db61f89523359d95887a8455148d02ec97`
- `stage5_state_year_summary.csv`: `88647ca35e9e10a44e5806bd10c17af1ace81925bd97f97ea3fe651c5f6e163a`
- `stage5_state_volatility_summary.csv`: `2b7b92445e987ab8094508d2ad8473963e84a03557152cad46b258a9601d8c0c`
- `stage5_risk_flag_summary.csv`: `4c93b1ce8e8eda6b8c5f6ce06c85d72490071b90204177449fd6d75271475c59`
- `stage5_usefulness_decisions.csv`: `8e96eae79d6b72ff23931c5ffa27217dcef2c7367f38846533e885485561cd6f`
- `stage5_component_robustness.csv`: `8bc052c2f0eb13c728dc7d8db15a0ce84355ff3861f35ca1492246f7e5fd341f`
- `STAGE5_RESULT.md`: `2ec7896a43de4fde951acb1804b0004878ed4cc8221228462adf54691953e049`.

## 12. Decision

**Stage 5 = COMPLETE / NO_RECONCILIATION_PASS.**

Frozen forecast object going forward:

`F_t = [P_UP3, RET_HAT3, Q10_3, Q50_3, Q90_3]`

with:
- H3 as core horizon
- H1/H5 as supporting horizon context only.

## 13. Exact next stage

**Stage 6 — Tactical Allocation / Utility Contract**

Purpose:

Translate the continuous frozen forecast vector into a decision framework that can answer:

> Given current short-horizon forecast and downside distribution, when is expected risk-adjusted reward sufficiently attractive to allocate capital to Gold?

Before any backtest, Stage 6 must preregister:

1. tradable instrument / price convention
2. decision timing
3. holding horizon
4. entry/exit rule
5. transaction cost / spread assumptions
6. no-position / cash state
7. risk penalty
8. position-size policy
9. benchmark:
   - cash
   - always-long H3-roll / buy-and-hold-compatible benchmark
10. utility and drawdown metrics.

No P&L threshold may be selected from 2025.

2025 remains frozen until the full Stage-6 rule is selected and frozen on DEV.
