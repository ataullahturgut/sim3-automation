# R39 — September 2026: ORIGINAL H3 models INDIVIDUALLY, no D1 / no consensus

> **CORRECTED / SUPERSEDED FOR ALL-H3-HYBRID CONCLUSIONS:** The original R39 selection omitted DPTC-Q95/Q99 H3 hybrids. R40 independently reconstructed 2026 Jan–Sep **DPTC-Q95 135/191 = 70.68%**, and **Sep 14/19 = 73.68%**, 4 Sep H3 rescues, versus V5 10/19. Therefore any global claim below that September's existing H3 models were only 47–53% is false. The three narrow base-expert raw figures remain valid, but R40 is the complete authoritative H3-hybrid result. Read `GOLD_R40_20261011_FULL_2026_H3_HYBRID_SOURCE_ACCURACY_AND_MONTHLY_CORRECTION.md` first. All DPTC results are retrospective posthoc, not independently OOS.


**Audit date:** 2026-10-11. **User's precise requested test:** Score the four experts behind CIG **one-by-one on their ORIGINAL H3 direction outcome for September 2026**; only after this, consider adapting to a shorter interval. **NO D1 labels and NO consensus accuracy calculated or treated as model results.** Every score below was recomputed from the immutable original H3 CSV `forecast_issue_date`, `target_end_date_h3`, `y_up`, and frozen expert probability with threshold p >= 0.5.

## Source files / endpoint contract

- `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv` -> `p_helios_v5_dce`.
- `GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv` -> `p_rift`.
- `GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv` -> `p_vega`.
- `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_DIAGNOSTIC_2026-10-04.md` and `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv` -> no SAGE V2 / RuleFlow V3-TG directional exceptions in September; therefore **same vote as V5 on all 19** (not a new separately generated September full expert CSV). The SAGE V1 selective dataset `GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv` is **not** SAGE V2; 14/19 September rows available, none of its `ocs_candidate` flips.
- Original H3 **target definition**: log return from **`feature_cutoff_date`** (prior observed Gold date) to **`target_end_date_h3`**, the 3rd next observed Gold daily date in original StakTrakr historical reference. **Important:** For issue date Sep01, feature-cutoff Aug31 and H3 terminal Sep03, NOT Sep04 (which would incorrectly start 3 steps on issue date). Reported H3 y_up is same-research daily source defined in original CSV, not a Turkish bank spot H3 return.

## 2026 September VALID historical sample

- **N=19** common original H3 prediction/realization records: issue dates **Sep01 to Sep25 2026**, end dates **Sep03 to Sep29**.
- September business dates Sep28–30 are **not represented by the original V5/RIFT/VEGA 931-row frozen H3 artifacts** (those end at Sep25 with target Sep29). A separate D1 `GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.csv` contains post-snapshot model direction fields, but has **D1 outcomes only**, not a verified same-H3-target matured `y_up` on the original 2026 historical source. **Do not append those three as incorrect, correct, or a replacement H3 denominator.** An honest full-month 22/22 H3 result is not verified.

### Original three-day H3 per-model results: no consensus

| Frozen H3 direction expert | Correct / 19 | Accuracy | UP calls | DOWN calls | Correct of 7 real UP | Correct of 12 real DOWN | Balanced Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| HELIOS V5-DCE | **10/19** | **52.63%** | 14 | 5 | 6 | 4 | 59.52% |
| RIFT | **9/19** | **47.37%** | 11 | 8 | 4 | 5 | 49.40% |
| VEGA | **10/19** | **52.63%** | 12 | 7 | 5 | 5 | 56.55% |
| SAGE V2 + RuleFlow V3-TG (no Sep overrides; inherits V5) | **10/19** | **52.63%** | 14 | 5 | 6 | 4 | 59.52% |
| Always DOWN comparator, *not a model* | **12/19** | **63.16%** | 0 | 19 | 0 | 12 | 50.00% |
| Always UP comparator, *not a model* | **7/19** | **36.84%** | 19 | 0 | 7 | 0 | 50.00% |

All three original numeric model artifacts agree on **the exact same 19 realised H3 rows**, and `y_up=1` on 7, `y_up=0` on 12. H3 measurements were derived from previously reconstructed historical forecasts; results were measured in a retrospective / development-open year, **NOT clean unseen prospective test**.

### Original H3 notable individual examples

| Forecast issue date | Original H3 terminal date | H3 actual | V5 | RIFT | VEGA | Finding |
|---|---|---|---|---|---|---|
| Sep01 | Sep03 | UP | UP | UP | UP | all correct |
| Sep02 | Sep04 | UP | DOWN | DOWN | DOWN | all wrong |
| Sep04 | Sep08 | DOWN | UP | UP | UP | all wrong |
| Sep07 | Sep09 | DOWN | UP | DOWN | DOWN | V5 wrong, RIFT/VEGA correct |
| Sep15 | Sep17 | UP | UP | DOWN | UP | RIFT wrong, V5/VEGA correct |
| Sep17 | Sep21 | UP | UP | DOWN | DOWN | V5 correct, RIFT/VEGA wrong |
| Sep24 | Sep28 | DOWN | DOWN | DOWN | DOWN | all correct |
| Sep25 | Sep29 | DOWN | UP | UP | UP | all wrong |

**Concrete conclusion for user:** The old consensus members as independent original 3-day H3 forecasters in September 2026 did **NOT** deliver 70–80% accuracy. They were around **47–53% raw** on **19 actually archived and matured H3 dates**, underperforming the 63% naive always-DOWN due to a DOWN-heavy month (balanced accuracy also reported to control this skew). There is no validated "good September H3" claim to carry into D1 without new frozen, origin-safe tests.

**Next experiment logic:** Stop analyzing D1 consensus as proxy for H3. First freeze actual H3 source labels and issue time on 22 September business origins, replicate individual H3 evaluation with post Sep25 eligible matured terminal prices and identical frozen model outputs. Then for Turkish 09–17 strategy investigate each model's 3-day path and price barriers directly, not assign the same H3 vote to an unrelated same-day label. Do not report future returns/P&L without BID/ASK source and issue/entry time verified.
