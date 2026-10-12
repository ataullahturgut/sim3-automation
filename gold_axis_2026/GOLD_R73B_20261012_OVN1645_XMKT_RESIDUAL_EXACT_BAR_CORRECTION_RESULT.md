# R73B RESULT — exact-bar CME time-alignment correction of R73 (model frozen)

**Verdict after correction: still REJECT** for the primary pre-registered W7 test. The original R73 report (`GOLD_R73_20261012_OVN1645_CROSSMARKET_RESIDUAL_REVERSAL_RESULT.md`) and its numbers are preserved unchanged; this file is an additive correction.

Files:
- Prereg: `GOLD_R73B_20261012_OVN1645_XMKT_RESIDUAL_EXACT_BAR_CORRECTION_PREREG.md`, commit `a6f716ed`, written before any corrected output.
- Code: `tools/gold_r73b_exactbar_correction.py`. It imports the unchanged R73 model code; the v1 rerun reproduces every committed R73 metric exactly.
- SQL: `sql/gold_r73b_ovn1645_xmkt_exactbar_panel_v2.sql`.
- Panel: `GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_PANEL_LOGRET_E5.csv`.
- Ledger: `..._EXACTBAR_ROWS.csv`. Summary: `..._EXACTBAR_SUMMARY.json`.
- New Neon table `gold_research_r73b_ovn1645_xmkt_exactbar_panel_v2`; the v1 table and view are untouched.

## 1. Defect confirmed

- **Cause.** The v1 SQL picked CME prices with `BETWEEN … ORDER BY ts_event DESC LIMIT 1`. When an exact bar was missing, it silently used an earlier bar.
- **Check.** An independent single-pass exact-hour query (bars `ts_event` = D 05:00, 09:00, 12:00 UTC, i.e. bar starts) reproduces the external audit exactly.
- **W7 scope.** Among the 624 W7 nights scored in R73, **41** lacked an exact start or end bar for at least one root: 2023 8, 2024 14, 2025 11, 2026 8.
- **W3 scope.** 43 of 652 scored nights are affected: 9, 13, 13 and 8 by year.
- **Roots involved.** Almost all cases are ZN in quarterly roll weeks, where calendar-front `c.0` does not trade at 05:00 or 12:00 UTC. A few are CL 05:00 UTC gaps.
- **Continuity.** No start/end pair spans a contract roll (`instrument_id` is identical on every retained pair).
- **Training rows.** The same rule removes 52 complete-W7 weekdays from the pool that ridge training draws on: 873 → 821 (2023 227→216, 2024 230→214, 2025 235→221, 2026 181→170).
- **Values unchanged.** SQL identity check: wherever v2 has a value it equals v1 exactly (0 mismatches). The correction therefore removes affected cells and changes no value.

## 2. Original vs corrected — W7 (09–16 TR, primary), rule sign(−residual)

| Year | v1 N (cov.) | v2 N (cov.) | removed | v1 acc / BA | **v2 acc / BA** (Wilson 95%) | v2 UP / DOWN recall | v2 raw-reversal BA | v2 RESID vs REV |
|---|---|---|---|---|---|---|---|---|
| 2023 | 134 (65.4%) | 124 (60.5%) | 10 = 8 alignment + 2 warm-up shift | 56.72 / 55.93 | **57.26 / 57.07** (48.5–65.6) | 57.9 / 56.2 | 55.10 | 16 / 13 |
| 2024 | 182 (88.8%) | 168 (82.0%) | 14 | 53.85 / 54.64 | **54.76 / 55.14** (47.2–62.1) | 50.5 / 59.7 | 57.79 | 8 / 13 |
| **DEV 23–24** | 316 (77.1%) | **292 (71.2%)** | 24 | 55.06 / 55.38 | **55.82 / 56.15** (50.1–61.4) | 53.9 / 58.4 | 56.64 | **24 / 26 (p=0.66)** |
| 2025 (retro.) | 187 (91.7%) | 176 (86.3%) | 11 | 45.99 / 46.37 | **46.02 / 46.54** (38.8–53.4) | 40.0 / 53.1 | 48.40 | 7 / 10 |
| 2026 (retro., direct Dukascopy) | 121 (91.0%) | 113 (85.0%) | 8 | 51.24 / 51.23 | **52.21 / 52.14** (43.1–61.2) | 50.9 / 53.3 | 49.42 | 6 / 3 |

**The warm-up shift.** Removing training rows delayed the 60-row ridge warm-up, so the first 2023 prediction moved from 2023-04-05 to 2023-04-11.

**Gates (v2, DEV):**
- **H1 FAIL.** 163/292 correct, exact binomial p = 0.0266, **Holm across W7/W3 = 0.053**.
- **H2 FAIL.** McNemar against raw reversal is 24 vs 26, p = 0.66. The month-block bootstrap BA difference is −0.50 pp, 95% CI [−4.45, +3.40].
- **H3 FAIL.** In the OLS (HC3) of the overnight return, the residual coefficient is −0.035 (t = −0.43, p = 0.33); the fitted factor part has t = −0.27.
- **Verdict: REJECT, unchanged.**

**W3 (13–16 TR), v2:**
- DEV: 168/310 = 54.19%, BA 54.52%, Holm p = 0.078. RESID vs REV 23/21.
- By year: 2023 BA 60.40%, 2024 49.94%, 2025 48.75%, 2026 53.23%.
- v1 DEV was 52.08% / 52.28%.

**R67 matched (W7, v2).** R67 is in-sample on DEV.

| Rows | N | R_RESID BA | R_REV BA | R67 new_pred BA | R_RESID vs R67 (rescue/break) |
|---|---|---|---|---|---|
| DEV | 213 | 55.12% | 55.82% | 51.71% | 41 / 34, p = 0.24 |
| 2025 | 168 | 47.33% | — | 47.95% | 30 / 32 |
| 2026 | 109 | 51.35% | — | 51.59% | 16 / 16 |

## 3. Was the change caused by predictions or by the sample? (common-date decomposition, W7)

| Period | Common dates | v1 correct on common | v2 correct on common | Predictions changed (v2 right / v1 right) | v1 correct on removed nights |
|---|---|---|---|---|---|
| 2023 | 124 | 71 | 71 | 6 (3 / 3) | 5 / 10 |
| 2024 | 168 | 92 | 92 | 2 (1 / 1) | 6 / 14 |
| DEV | 292 | **163** | **163** | 8 (4 / 4) | **11 / 24 = 45.8%** |
| 2025 | 176 | 81 | 81 | 6 (3 / 3) | 5 / 11 |
| 2026 | 113 | 60 | 59 | 1 (0 / 1) | 2 / 8 |

**Conclusion.** On identical dates the corrected model is exactly as accurate as v1. The small DEV accuracy rise (55.06% → 55.82%) is **entirely a sample effect**: the removed misaligned nights happened to be below 50%. It is not a better model.

W3 common dates: DEV v1 165 vs v2 168 correct (5 vs 2 among 7 changed predictions); 2025 88 → 86; 2026 63 → 63.

## 4. Pre-declared sensitivities (reported, not used for selection)

**S-FULL7 (all seven 06–12 UTC bars present for all three roots), W7:**

| Period | N | Accuracy | BA |
|---|---|---|---|
| DEV | 276 | 56.52% | 57.00% |
| 2025 | 163 | — | 47.81% |
| 2026 | 108 | — | 55.59% |

- H1 Holm p = 0.035 passes, but H2 fails (22/23, p = 0.62) and H3 fails (t = −0.21). The mapped label is "INCONCLUSIVE".
- What remains is the raw-gold reversal already known from earlier work. Raw-reversal BA on the same rows is 57.02% in DEV, against 57.00% for the residual rule. It fails in 2025 (49.84%).
- This is a non-primary filter chosen after v1 results were known, so it cannot overturn the primary REJECT.

**S-SRC (2026 source mixing):**
- **Every one of the 113 v2 W7 2026 predictions** was trained on a window that mixes 2025 EV/Dukascopy rows with 2026 direct-Dukascopy rows. The first prediction (2026-01-05) has 249 of its 250 training rows from 2025 EV/Dukascopy. Across all 2026 predictions, 19,884 of the 28,250 training-row slots (70.4%) are EV/Dukascopy rows.
- **Same-source re-score.** Training restricted to 2026 direct-Dukascopy rows only, with the frozen model, alpha 10, window 250 and minimum 60. Only 68 dates qualify, from late spring 2026.
- **Effect on those 68 common dates.**
  - Mixed training: 38/68, BA 55.54%.
  - Same-source training: 41/68, BA 60.89%.
  - 5 predictions changed (4 / 1), McNemar p = 0.19.
  - Residual rank correlation between the two trainings is 0.937.
- **Interpretation.** The source mix has a small, non-significant effect. It does not change any conclusion. 2026 remains retrospective, already-inspected data, and this sensitivity is **not** used to claim or tune 2026 performance.

## 5. Answers

- The external audit is confirmed exactly: 41 W7 nights (8/14/11/8).
- W7 removed 43 scored nights (41 alignment + 2 warm-up) and 52 training weekdays. W3 removed 47 scored nights (43 alignment + 4 warm-up).
- No CME value was altered.
- The primary scientific decision is unchanged: **REJECT**. The residual adds nothing beyond raw reversal; H2 fails in every variant.
