# R40 — CORRECTION: All 2026 original H3 hybrids, monthly performance, and September's omitted DPTC result

**Date:** 2026-10-11. **Supersedes the incomplete model selection and false overarching verdict of `GOLD_R39_20261011_SEPTEMBER_2026_ORIGINAL_H3_INDIVIDUAL_EXPERT_RESULT.md`.** This audit explicitly follows the user's stated request: assess **original three-day H3 model directions and other H3 HYBRIDS over all months of 2026**, not D1 consensus labels. The older R39 correctly counted three selected base experts but omitted **DPTC-Q95/Q99**, a genuinely stronger 2026 H3 hybrid. No training, retuning or relabeling; deterministic joined replay of existing frozen CSVs, exact available H3 dates.

## Model and outcome identity

Standardized original H3 target on the CLEAN H3 2026 panel: `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`, `feature_cutoff_date`, `forecast_issue_date`, `target_end_date_h3`, `y_up`. At each issue date, terminal return is Gold price **three observed Gold dates after the PRIOR feature_cutoff_date**. The historic original source target uses STAK dated daily Gold, **NOT executable 3-day Turkey 09→09 spot**. Full mature issue-date 2026 span: **Jan 02–Sep 25, N=191**; Sept **Sep01–Sep25 N=19** (Sept28–30 original H3 model CSV incomplete; never fake 22 days).

Existing H3 model sources:
- HELIOS V5: `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`, threshold `p_helios_v5_dce >= 0.5`.
- RIFT: `GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv`, `p_rift >= 0.5`.
- VEGA: `GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv`, `p_vega >= 0.5`.
- SAGE-H3 V2 + RuleFlow V3-TG H3 hybrid: V5 direction with **5** previously recorded `RESCUE` toggles at `feature_cutoff_date` in `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv`; no Sept exception.
- **DPTC-Q95** and **Q99** (crucially omitted in prior response): using EXACT **feature_cutoff_date** on `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`, apply Q95 or Q99 `acted=True` as **FLIP of the SAGE+RuleFlow combined H3 baseline**, not a direct modification of RIFT/VEGA and not date-shifted to `forecast_issue_date`. Against the original cleaned y_up this exactly reproduces original `GOLD_H3_DPTC_V1_SUMMARY_2026-10-05.json`.
- AURORA/OPAL/HERA for separate historical context exist; HERA (original pre-clean probabilities and y_up) has a different 2026 target vintage, so don't silently substitute its published 122/191=63.87% into the same CLEAN target comparison. Scoring those old HERA frozen probabilities on CLEAN target gives **120/191=62.83%**, and September **11/19=57.89%**, with **two target labels different** between HERA's original vintage and clean V5. AURORA_CLEAN **112/191=58.64%**; OPAL_CLEAN **121/191=63.35%**. Separate direct clean RIFT/VEGA 113/191=59.16%.

## 2026 FULL H3 (191 comparable original H3 predictions)

| Three-business-date H3 direction strategy | Correct/N | Accuracy | Development status |
|---|---:|---:|---|
| **DPTC-Q95 + SAGE V2/RuleFlow V3-TG hybrid** | **135/191** | **70.68%** | Strong retrospective, **NOT prospective/OOS**; DPTC architecture designed after seeing 2026 history |
| **DPTC-Q99 + SAGE V2/RuleFlow V3-TG hybrid** | **134/191** | **70.16%** | Sensitivity challenger, NOT independently OOS |
| **SAGE V2 + RuleFlow V3-TG** | **126/191** | **65.97%** | 2026 retrospective posthoc diagnostics |
| HELIOS V5-DCE | 121/191 | 63.35% | Clean H3 reconstructed probabilities |
| OPAL_CLEAN | 121/191 | 63.35% | Clean H3 alternative, not in CIG D1 four-expert vote |
| HERA original probabilities scored on clean target | 120/191 | 62.83% | Cross-vintage sensitivity; original HERA preclean report 122/191=63.87% is different target |
| RIFT_CLEAN | 113/191 | 59.16% | H3 specialist |
| VEGA_CLEAN | 113/191 | 59.16% | H3 specialist |
| AURORA_CLEAN | 112/191 | 58.64% | H3 parent |
| Always DOWN fixed base-rate check | 100/191 | 52.36% | Not an algorithm |
| Always UP fixed base-rate check | 91/191 | 47.64% | Not an algorithm |

Q95 over the whole 2026 had **13 actions: 11 RESCUE and 2 BROKEN**; combined prior base 126/191, **net +9 => 135/191**. Q99 12 actions 10 rescue 2 broken: 126+8=134/191. Reproduced from archived original dates without any posthoc correction of votes.

## All 2026 monthly H3 forecast-issue cohorts, ORIGINAL H3 exact same target dates

| Issue month | Common N | HELIOS V5 | SAGE+RuleFlow | **DPTC-Q95** | **DPTC-Q99** | RIFT | VEGA |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan | 21 | 16/21=76.19% | 16/21=76.19% | **16/21=76.19%** | 16/21=76.19% | 16/21=76.19% | 16/21=76.19% |
| Feb | 20 | 11/20=55.00% | 13/20=65.00% | **13/20=65.00%** | 13/20=65.00% | 12/20=60.00% | 12/20=60.00% |
| Mar | 22 | 17/22=77.27% | 17/22=77.27% | **17/22=77.27%** | 17/22=77.27% | 16/22=72.73% | 16/22=72.73% |
| Apr | 22 | 15/22=68.18% | 15/22=68.18% | **15/22=68.18%** | 15/22=68.18% | 15/22=68.18% | 13/22=59.09% |
| May | 21 | 12/21=57.14% | 13/21=61.90% | **17/21=80.95%** | 16/21=76.19% | 11/21=52.38% | 11/21=52.38% |
| Jun | 22 | 13/22=59.09% | 13/22=59.09% | **14/22=63.64%** | 14/22=63.64% | 11/22=50.00% | 11/22=50.00% |
| Jul | 23 | 11/23=47.83% | 13/23=56.52% | **13/23=56.52%** | 13/23=56.52% | 10/23=43.48% | 10/23=43.48% |
| Aug | 21 | 16/21=76.19% | 16/21=76.19% | **16/21=76.19%** | 16/21=76.19% | 13/21=61.90% | 14/21=66.67% |
| Sep, Sep01–25 | 19 | 10/19=52.63% | 10/19=52.63% | **14/19=73.68%** | 14/19=73.68% | 9/19=47.37% | 10/19=52.63% |
| **Jan–Sep** | **191** | **121/191=63.35%** | **126/191=65.97%** | **135/191=70.68%** | **134/191=70.16%** | **113/191=59.16%** | **113/191=59.16%** |

Sep H3 true UP 7/19, DOWN 12/19; always-DOWN benchmark **12/19=63.16%**, so DPTC-Q95 **14/19=73.68%**, beating the naive September imbalance benchmark. This is observed **after model was developed with some 2026 data**, NOT proof it would generalize. The original D1 four-expert CIG membership does not automatically include DPTC. But the user asks us to examine every valuable H3 HYBRID **BEFORE** choosing a D1 transformation, so omitting it was a factual research oversight.

## Exactly how September DPTC-Q95 added four H3 rescues (no imagined daily conversion)

DPTC action CSV dates are **FEATURE CUTOFF dates**; translating to actually reported forecast issue dates:

| Q95 action on feature cutoff | Forecast issue date | Original H3 end date | SAGE+RuleFlow H3 call | DPTC H3 call | H3 outcome | Correct? |
|---|---|---|---|---|---|---|
| **Sep 03** | **Sep 04** | **Sep 08** | UP | **DOWN** | DOWN | **RESCUE** |
| **Sep 09** | **Sep 10** | **Sep 14** | UP | **DOWN** | DOWN | **RESCUE** |
| **Sep 11** | **Sep 14** | **Sep 16** | UP | **DOWN** | DOWN | **RESCUE** |
| **Sep 24** | **Sep 25** | **Sep 29** | UP | **DOWN** | DOWN | **RESCUE** |

Thus **V5 and SAGE+RuleFlow 10/19 + 4 correct H3 rescues = DPTC 14/19**. Previous R39's statement that "**September H3 3-day systems were all 47–53% and clearly poor**" was FALSE as a statement about the full existing H3 research family. Some individual base experts were weak, while the already-existing DPTC hybrid was materially stronger.

## What these successes mean and do NOT mean

1. They are on original H3 DAILY SOURCE **feature cutoff date→third subsequent available daily source date**, not on an independently tradable 09TR→09TR three-day spot entry/exit. They contain historical source-clock/mixed-provider risks documented R36–R38. Don't infer 70.68% realized post-issue bank trade alpha.
2. The DPTC synthesis was explicitly created after analyzing 2026 errors; its 2026 135/191=70.68% is **posthoc development accuracy, NOT untouched independent forecast validation**. Q95 was not chosen over Q99 based on future results; both reported.
3. Source-data completeness: 19/19 original Sept H3 matured dates as of Sep25 freeze, **not Sep28–Sep30**. Neither percentage should be called a full 22-day September validation.
4. H3 alternatives include HERA, OPAL, multiple HELIOS generations, RC-RTE, ANFIS and classical models. They have different source vintages, training dates and status; they must not be deceptively described as all four D1 experts or as equally trusted.
5. **Next research correct order:** accurately assemble ALL 2026 September and Jan–Sep original 3-day H3 experts and hybrids, rank 2023–26 by both accuracy and balanced accuracy plus coverage and PIT. Only **THEN** test whether original H3 votes provide future intraday segment-specific actions. In particular, retrospectively stronger DPTC should be treated as a 2026 regime-specialist hypothesis, not a 2026 chosen production model.

## Evidence

Original frozen prediction and action files plus original model authority:

`GOLD_H3_DPTC_V1_RESULT_2026-10-05.md`, `GOLD_H3_DPTC_V1_SUMMARY_2026-10-05.json`, `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`, `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv`, `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_DIAGNOSTIC_2026-10-04.md`, `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_CLEAN_REVERSAL_CHAIN_RESULT_2026-10-03.md`, `GOLD_H3_HERA_V1_PREDICTIONS_2026-10-03.csv`. No new external model data or invented results.
