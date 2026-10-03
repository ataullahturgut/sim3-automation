# FLOW-PRELIM-OI-H3 V1 — CLOSURE

**Date:** 2026-10-03  
**Identity:** `FLOW_PRELIM_OI_H3_V1`  
**Branch:** `gold-h3-flow-oi-salvage-v1-20261003`  
**Binding status:** **NO_ELIGIBLE_FLOW_PRELIM_OI_THRESHOLD / NOT PROMOTED**

## 1. What was actually tested

A previously blocked FLOW hypothesis was partially reopened using an official CME source:

- host: `ftp.cmegroup.com`
- directory: `/daily_volume`
- daily workbook: `daily_volume_YYYYMMDD.xlsx`
- product row: COMEX(STATS) / GC / GOLD FUTURES / F
- fields: Total Volume + preliminary Open Interest

CME explicitly marks this Open Interest as preliminary. The original FINAL-only FLOW-H3 V1 therefore remains unchanged; this was a separately named challenger.

Origin-safe alignment:
- same-day preliminary values forbidden;
- latest source row with `trade_date < feature_cutoff_date`;
- no lag search;
- no OI imputation.

## 2. Source coverage

| Year | Listed | Valid GC Volume+OI | Coverage |
|---:|---:|---:|---:|
| 2022 | 251 | 251 | 100.00% |
| 2023 | 251 | 250 | 99.60% |
| 2024 | 252 | 252 | 100.00% |
| 2025 | 251 | 251 | 100.00% |
| 2026 through Sep-30 | 188 | 53 | 28.19% |

The 2026 source format ceases to expose the expected GC OI header after 2026-03-19 in this FTP family. This source-coverage fact was audited independently of forecast outcomes.

DEV 2023-2024 therefore has essentially complete source coverage and is adequate for the preregistered gate test.

## 3. DEV 2023-2024 result

Eligible AURORA-follows-momentum origins: **388**  
True reversals: **111**

| Threshold | Candidates | Precision | Recall | Candidate rate | F2 | Eligible |
|---:|---:|---:|---:|---:|---:|---|
| 0.35 | 343 | 28.86% | 89.19% | 88.40% | 0.6290 | NO |
| 0.40 | 302 | 28.15% | 76.58% | 77.84% | 0.5697 | NO |
| 0.45 | 239 | 26.36% | 56.76% | 61.60% | 0.4612 | NO |
| 0.50 | 176 | 26.14% | 41.44% | 45.36% | 0.3710 | NO |
| 0.55 | 109 | 28.44% | 27.93% | 28.09% | 0.2803 | NO |

Frozen eligibility required:
- precision >= 45%;
- candidate rate <= 35%.

No threshold passed.

Binding status:
`NO_ELIGIBLE_FLOW_PRELIM_OI_THRESHOLD`.

## 4. Holdout governance

Because DEV failed:
- no threshold was selected;
- 2025 confirmation was **not opened**;
- 2026 forecast outcomes were **not opened**;
- the known 55 V5-missed / OPAL-no-candidate reversals were not used for tuning or rescue analysis.

This preserves the preregistered chronology.

## 5. Scientific interpretation

The result is stronger than the prior volume-only ablation because actual official CME daily aggregate preliminary GC Open Interest was added.

Under the frozen feature/model representation, Volume+preliminary-OI still produces a broad reversal score with insufficient precision.

Adding aggregate daily preliminary OI did **not** solve the selectivity problem.

This does not prove that:
- CME FINAL OI has no value;
- contract-level OI structure has no value;
- options OI asymmetry has no value;
- nonlinear/event-conditioned OI states have no value.

It does show that the preregistered simple aggregate daily FLOW representation should **not** be promoted or tuned further using 2025/2026.

## 6. Next independent information channel

The same official CME FTP files expose:
- `OG / GOLD CALL / O`
- `OG / GOLD PUT / O`
with separate daily Total Volume and Open Interest.

This enables a separately named options-positioning asymmetry specialist without pretending it is CME CVOL implied-variance Skew.

Any such successor must be preregistered independently before outcome inspection.

## 7. Evidence

- `GOLD_H3_FLOW_PRELIM_OI_V1_PREREG_2026-10-03.md`
- `GOLD_H3_FLOW_PRELIM_OI_V1_FAST_RESULT_2026-10-03.md`
- `GOLD_H3_FLOW_PRELIM_OI_V1_FAST_SUMMARY_2026-10-03.json`
- `GOLD_H3_FLOW_PRELIM_OI_V1_FAST_SOURCE_COVERAGE_2026-10-03.csv`
- `GOLD_H3_FLOW_PRELIM_OI_V1_FAST_THRESHOLD_GRID_2026-10-03.csv`
- `GOLD_H3_FLOW_CME_FTP_OI_PROBE_RESULT_2026-10-03.md`

Transport note:
- the first parallel implementation downloaded **1193 daily files** successfully but failed afterward because interaction columns were checked before panel alignment;
- this implementation-order bug was fixed without changing source, features, lags, model, threshold grid, or evaluation rules;
- the corrected parallel run completed successfully.
