# GOLD H3 — REVERSAL RESEARCH PROGRAM CLOSURE AFTER 2026 CONCEPT-DRIFT AUDIT

**Date:** 2026-10-04  
**Binding decision:** **NO REVERSAL OVERRIDE PROMOTION — HELIOS V5-DCE REMAINS BINDING**

## 1. Objective

The reversal program attempted to solve HELIOS V5-DCE's dominant residual failure mode without copying another generic forecasting model.

The target problem was:
- V5 follows prevailing 12h momentum;
- the true H3 direction reverses;
- OPAL usually provides no reversal candidate.

The program therefore built purpose-designed reversal specialists around:
- matched continuation twins;
- path/exhaustion state;
- CME Gold futures volume;
- CME Gold CALL/PUT volume asymmetry;
- sequential transition memory;
- regime permission;
- online shadow credibility;
- live prior correction;
- long-horizon trend context.

## 2. Strongest pre-2026 mechanism

OAR-RTE, requiring:
- pRTE >= 0.60
- pInst >= 0.50
- signed Gold options pressure against momentum > 0
- signed change in that pressure > 0

produced on 2024-2025:
- 34 candidates
- 22 rescues
- 12 broken
- net +10
- precision 64.71%.

APT-RTE added fading futures participation:
- GC dlog volume < 0
- GC volume acceleration < 0.

APT passed the preregistered pre-2026 robustness gate:
- 15 candidates
- 10 rescues
- 5 broken
- net +5
- precision 66.67%
- half-year nets +1 / +1 / +4 / -1.

## 3. Independent 2026 holdout failure

APT was opened exactly once on 2026 after the pre-2026 gate passed.

Result:
- 12 candidates
- 2 rescues
- 10 broken
- net -8
- precision 16.67%.

Whole clean 2026:
- V5-DCE: 121/191 = 63.35%
- hypothetical APT-assisted: 113/191 = 59.16%.

APT was rejected.

This consumed 2026 Jan-Sep as the independent reversal holdout for successor research.

## 4. Post-holdout attempts to explain the failure

### 4.1 Historical rescue-prototype similarity

PGR compared OAR candidates with historical RESCUE vs BROKEN prototypes.

Leave-one-year-out:
- 2024 guard: 2 rescue / 3 broken = -1
- 2025 guard: 9 / 4 = +5
- 2026 guard: 1 / 11 = -10.

Local similarity could not identify the 2026 failure state.

### 4.2 20/60-day secular rejoin state

OAR candidates were partitioned by whether 12h momentum aligned with or opposed 20/60-day trend.

2026:
- REJOIN_BOTH: 0 rescue / 3 broken
- MIXED: 1 / 4
- ALIGN_BOTH: 2 / 9.

Thus long-trend sign alone does not rescue the mechanism.

### 4.3 5/20/60-day multi-scale phase cube

All natural multi-scale sign families remained unstable in 2026.

Examples:
- long-60 countertrend family: 2024 net +4, 2025 +1, 2026 -5
- long-60 aligned family: 2025 +5, 2026 -8.

No invariant sign-phase filter was found.

### 4.4 Concept-drift audit

Within OAR candidates:

2024-2025:
- N=34
- rescue rate 64.71%.

2026:
- N=19
- rescue rate 15.79%.

Conditional rescue-vs-broken feature effects:
- sign retention: 62.5%
- SMD correlation 2024-25 vs 2026: **-0.155**.

Major effect reversals:
- opposite_semivar_share: +0.151 -> -1.355
- counterfactual opposite-semivariance gap: +0.141 -> -1.398
- path_consistency: +0.461 -> -0.519
- RTE tension: +0.217 -> -0.464
- V5 confidence: -0.107 -> +0.499.

This is not adequately described as simple covariate shift. The conditional relationship between the available state variables and reversal success changed materially.

### 4.5 Dual-transition attempt

DTR attempted to model:
- EXHAUSTION reversal in ordinary persistence states;
- PREEMPTIVE reversal in high V5-confidence + high trend-strength states.

Result:
- 2024: +3, 100% precision
- 2025: +4, 64.29%
- 2026: -9, 9.09%.

Status:
`DTR_DEVELOPMENT_NOT_VIABLE`.

No prospective DTR freeze was permitted.

## 5. Scientific conclusion

The current reversal problem is **not solved by further threshold/routing work on the existing information set**.

The evidence now shows:

1. price-path/exhaustion state is non-invariant;
2. aggregate GC futures Volume/OI is non-selective;
3. aggregate Gold CALL/PUT volume pressure is useful in some regimes but not invariant;
4. matched-continuation similarity does not protect against 2026 concept drift;
5. 5/20/60-day trend context does not explain the break;
6. even low-capacity state-conditional and online-credibility controllers cannot make the current signal family robust.

Therefore continuing to search more combinations of the same variables would be retrospective overfitting rather than research progress.

## 6. Missing information implied by the failure

The most important diagnostic inversion is in **directional adverse-risk state**:
- opposite-side realized semivariance was positively associated with historical rescue but strongly negatively associated with 2026 rescue.

This suggests the missing signal may need to be **forward-looking**, not another realized-price transformation.

Priority new information channels:

### A. Directional Gold option-implied state — highest priority
- CME Gold CVOL UpVar / DownVar / Skew (GCUP / GCDN / GCSK), or equivalent entitled directional volatility-surface data;
- changes in skew, downside/upside implied variance, and term structure.

This directly targets the pre-emptive-vs-exhaustion ambiguity that realized semivariance cannot resolve.

### B. Strike/moneyness-aware Gold options activity
Aggregate CALL/PUT volume is insufficient.
Needed if obtainable:
- OTM put vs OTM call activity;
- delta-bucketed volume/OI;
- strike concentration around spot;
- short-dated vs longer-dated positioning.

### C. Higher-frequency futures/options participation
If available:
- intraday GC volume/price imbalance around the NY reference;
- open-interest or trade-flow state at finer granularity;
- cross-market lead/lag around reversal onset.

## 7. Binding production / prospective policy

Until genuinely new reversal information is available:

- **HELIOS V5-DCE remains the binding direction model.**
- No RTE/OAR/APT/PGR/DTR signal may override V5.
- CLEAN_H3_PROSPECTIVE_V1 remains untouched.
- Existing reversal candidates may be logged in **research shadow mode only**.
- No retrospective 2026 result may be relabeled as independent validation for a successor designed after the APT holdout.
- The next independent evidence begins on prospective origins from **2026-10-05 onward**.

## 8. Research stop rule

Do not run another retrospective threshold/grid search over the current RTE/OAR feature family.

Reopen the reversal promotion program only when at least one genuinely new information channel is available or a prospectively accumulated shadow sample establishes a new invariant mechanism.

## 9. Primary evidence

- `GOLD_H3_APT_RTE_HOLDOUT_CLOSURE_2026-10-04.md`
- `GOLD_H3_PGR_V1_RESULT_2026-10-04.md`
- `GOLD_H3_SECULAR_REJOIN_DIAGNOSTIC_2026-10-04.md`
- `GOLD_H3_MULTISCALE_PHASE_CUBE_2024_2026_2026-10-04.md`
- `GOLD_H3_REVERSAL_CONCEPT_DRIFT_AUDIT_2026-10-04.md`
- `GOLD_H3_DTR_V1_RESULT_2026-10-04.md`
