# R39 — September 2026: individual ORIGINAL H3 model directions on their ORIGINAL 3-observation target (not CIG-D1)

**Study date:** 2026-10-11. **Research status:** historical frozen H3 retrospective, not prospective/OOS and not investment return. **Strict user question:** first assess the constituent existing THREE-DAY H3 models on September 2026; only thereafter research conversion into daily/session windows. Therefore NO daily consensus, no intraday rescore, no clock optimization, and NO model retraining in this test.

## Source and coverage

Authoritative forecast rows from `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv` and `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_SUMMARY_2026-10-04.json`. Back-check direction labels explicitly against `GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv`. **All 19/19 label signs checked and agree**, 0 mismatches.

- September **issue dates with matured existing exact H3 model output: Sep01–Sep25 = 19**. These models' **last original H3 target end = 2026-09-29**. Sep28–30 **are NOT contained in the original four-model frozen H3 prediction files**; do not fill them using D1 Sep28–Oct02 expansion because that would silently change both label horizon and source.
- Original H3 contract: from `feature_cutoff_date` at D to 3rd NEXT SOURCE OBSERVATION after D, `target_end_date_h3` (for issue Sep01, cutoff Aug31 and end Sep03). Thus **three source-observation jumps from cutoff; after the next-day issue typically two remaining jumps**. This is the original actual H3 label, not issue+3 full new days and not any one-day D1 conversion.
- Source: StakTrakr frozen historical date-indexed daily Gold reference. It is **mixed-source during September 2026 (`sqld`, UTC calendar-day mean)** and **not** a fixed Turkish price print at 09TR/17TR. Do not make investability claims or silently substitute Dukascopy.
- Model direction: threshold `p_helios_v5_dce, p_rift, p_vega >= 0.5`. SAGE V2+RuleFlow V3-TG changes V5 only on frozen verified exception dates. The original combined 2026 diagnostic listed only exceptions Feb03, Feb11, May26, Jul10, Jul15; **NO Sept 2026 exception**. Hence SAGE+RuleFlow output equals frozen V5 direction for each of the 19 September rows. (SAGE selective V1 abstention is **not** the SAGE V2 exception-only direction; don't mix versions.)

## Original three-observation H3 directional accuracy, Sep 2026 same 19 rows

| Original H3 directional family | Correct / 19 | Accuracy | Balanced accuracy | Calls UP | Correct UP / correct DOWN |
|---|---:|---:|---:|---:|---|
| **HELIOS H3 V5-DCE** | **10/19** | **52.63%** | 59.52% | 14 | 6 / 4 |
| **RIFT H3** | **9/19** | **47.37%** | 49.4% | 11 | 4 / 5 |
| **VEGA H3** | **10/19** | **52.63%** | 56.55% | 12 | 5 / 5 |
| **SAGE V2 + RuleFlow V3-TG H3** | **10/19** | **52.63%** | 59.52% | 14 | 6 / 4 |
| **ALWAYS DOWN** simple comparator | **12/19** | **63.16%** | 50% | 0 | 0 / 12 |
| ALWAYS UP comparator | 7/19 | 36.84% | 50% | 19 | 7 / 0 |

Correct H3 target labels: 7 UP / 12 DOWN. On matched rows, RIFT and V5 differ Sep07, Sep15, Sep17; VEGA and V5 differ Sep07, Sep17. On Sep07 RIFT/VEGA DOWN is correct and V5 UP incorrect; on Sep17 V5 UP correct and RIFT/VEGA DOWN incorrect. On Sep15 VEGA matches V5 UP and RIFT DOWN is incorrect. The final SAGE V2+RuleFlow V3-TG has **no actual September FLIP events**; it is *not* an independent fourth September direction stream.

## Per issued date — actual original H3 labels, unchanged models

| Issue (2026-09) | H3 end (2026-09) | Realized cutoff→H3 label | HELIOS V5 | RIFT | VEGA | SAGE V2+RuleFlow |
|---|---|---|---|---|---|---|
| 09-01 | 09-03 | UP (+0.25%) | UP ✓ | UP ✓ | UP ✓ | UP ✓ |
| 09-02 | 09-04 | UP (+1.57%) | DOWN ✗ | DOWN ✗ | DOWN ✗ | DOWN ✗ |
| 09-03 | 09-07 | UP (+1.45%) | UP ✓ | UP ✓ | UP ✓ | UP ✓ |
| 09-04 | 09-08 | DOWN (-1.17%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |
| 09-07 | 09-09 | DOWN (-1.25%) | UP ✗ | DOWN ✓ | DOWN ✓ | UP ✗ |
| 09-08 | 09-10 | DOWN (-0.72%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |
| 09-09 | 09-11 | DOWN (-1.16%) | DOWN ✓ | DOWN ✓ | DOWN ✓ | DOWN ✓ |
| 09-10 | 09-14 | DOWN (-2.01%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |
| 09-11 | 09-15 | DOWN (-1.91%) | DOWN ✓ | DOWN ✓ | DOWN ✓ | DOWN ✓ |
| 09-14 | 09-16 | DOWN (-0.72%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |
| 09-15 | 09-17 | UP (+0.51%) | UP ✓ | DOWN ✗ | UP ✓ | UP ✓ |
| 09-16 | 09-18 | UP (+1.89%) | UP ✓ | UP ✓ | UP ✓ | UP ✓ |
| 09-17 | 09-21 | UP (+0.88%) | UP ✓ | DOWN ✗ | DOWN ✗ | UP ✓ |
| 09-18 | 09-22 | UP (+0.23%) | UP ✓ | UP ✓ | UP ✓ | UP ✓ |
| 09-21 | 09-23 | DOWN (-1.39%) | DOWN ✓ | DOWN ✓ | DOWN ✓ | DOWN ✓ |
| 09-22 | 09-24 | DOWN (-1.84%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |
| 09-23 | 09-25 | DOWN (-1.26%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |
| 09-24 | 09-28 | DOWN (-3.55%) | DOWN ✓ | DOWN ✓ | DOWN ✓ | DOWN ✓ |
| 09-25 | 09-29 | DOWN (-2.86%) | UP ✗ | UP ✗ | UP ✗ | UP ✗ |

Rows with "✓" use **original H3 target**, not a same-day label. 2026 Sep28, Sep29, Sep30 remain NOT SCORED because original 4-model H3 ledger lacks those issue dates and corresponding consistent matured source target data; count must not be reported as a complete full-month 22-session test.

## Decision

**No model demonstrates credible September 2026 H3 outperforming even a trivial constant DOWN in this 19-observation sample.** HELIOS/SAGE 10/19 =52.63%, VEGA 10/19=52.63%, RIFT 9/19=47.37%; constant DOWN 12/19=63.16%. Sample small and overlapping H3 horizons; no model independence implied. This is a **real original H3 model comparison** before any proposed daily conversion. The 2026 Oct04 SAGE/RuleFlow formulas were developed after inspecting prior 2026, so in no way can this September historical replay be called independent prospective validation.

If future research aims to convert to session direction, FIRST freeze actual H3 source-availability and feature-cutoff/issue clock for each original expert, THEN define distinct prospective future-only target; this report itself neither creates nor tests a new one-day model.
