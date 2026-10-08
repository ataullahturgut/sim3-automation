# GOLD EXECUTION CONTINUATION EXPANSION — EMPIRICAL AUDIT — 2026-10-08

**Status:** COMPLETE / EXPANSION CHALLENGERS REJECTED / NEW SOURCE-GATED HYPOTHESIS DEFINED  
**Scope:** OVERNIGHT-HOLD 17:00 Europe/Istanbul -> next eligible 09:00 Europe/Istanbul.  
**Freeze:** PRAMV V1 unchanged; no 2026 target labels opened.  
**Input snapshot:** `e2ddcab0535bbda52173b04a456b687d9461b14a` (all input prediction/data CSVs already frozen at prior HEAD).  
**Reconstruction/script:** `tools/gold_execution_continuation_expansion_audit_20261008.py`  
**Recorded common-row results:** `GOLD_EXECUTION_CONTINUATION_EXPANSION_METRICS_2026-10-08.csv`

## 1. Problem and population

A year has >250 eligible price dates, but PRAMV V1 produces only ~82–89 signals. We must distinguish inability to predict from missing data. Analyze the two completed late half-hour signs:

- `10` = first UP, second DOWN => *reversal*, PRAMV's first impulse points UP.
- `01` = first DOWN, second UP => *reversal*, PRAMV's first impulse points DOWN.
- `11` = both UP => *same-sign continuation candidate*, not proof that overnight will be UP.
- `00` = both DOWN => *same-sign continuation candidate*, not proof that overnight will be DOWN.

The exact overlap of the pre-existing FSMR4, PSF-M4, PAIR_ALL and single-interval BASE predictors has 255, 259 and 253 complete dates in 2023, 2024 and 2025. The original eligible dates were 256, 259, 254; the 1-date gap in 2023 and 2025 comes from *join/availability*, not a user-selected exclusion. In this common intersection:

| Year | Common days | Reversal days | Same-sign days | PRAMV V1 decisions |
|---|---:|---:|---:|---:|
| 2023 | 255 | 129 | 126 | 89 |
| 2024 | 259 | 129 | 130 | 86 |
| 2025 | 253 | 129 | 124 | 82 |

PRAMV V1 is reconstructed on these rows with its **exact original signal count and correct count** (2023 54/89; 2024 52/86; 2025 52/82). The original freeze is unchanged.

## 2. Falsify the intuitive continuation hypothesis

`CONT_SIGN`: on `11` predict UP, on `00` predict DOWN.

| Year | Correct/N | Accuracy | BA | Same-row PAIR Accuracy / BA | Same-row M4 Accuracy / BA |
|---|---|---|---|---|---|
| 2023 | 65/126 | 51.59% | 51.54% | 52.38% / 52.27% | 56.35% / 56.35% |
| 2024 | 62/130 | 47.69% | 46.42% | 53.85% / 49.58% | 48.46% / 49.03% |
| 2025 retrospective | 66/124 | 53.23% | 52.24% | 55.65% / 48.18% | 55.65% / 54.06% |

The same-sign rule is **NOT** a usable independent overnight mechanism. In particular the negative `00` state has 30/59=50.85% correct DOWN in 2023, 21/55=38.18% in 2024, 24/54=44.44% in 2025. The `11` state UP successes were 35/67=52.24%, 41/75=54.67%, 42/70=60.00%, but these are *one-class* state predictions, not balanced two-way skills; 2024 and 2025 market direction base rates are not controlled by quoting that UP hit rate alone.

**Base-rate check:** On all continuation dates 2024, 75/130 = 57.69% of targets were UP; on 2025, 72/124 = 58.06%. A strategy predicting UP regardless of features matches these accuracies and has BA 50%. PAIR's 2025 continuation accuracy 55.65% hides a DOWN recall of only 1.9% (119/124 predictions UP).

## 3. Empirical challenge: complement PRAMV with available experts

Every policy below leaves *every original PRAMV signal unchanged* and only decides on disjoint `11` or `00` dates, respecting the same historical macro-veto flag. Compare against PRAMV on same outer universe (255/259/253). Values are retrospective exploration after 2025 data was accessible; they are **not** an untouched test or selection-approved ensemble.

| Policy | 2023 N / Accuracy / BA | 2024 N / Accuracy / BA | 2025 N / Accuracy / BA |
|---|---|---|---|
| Frozen PRAMV V1 | 89 / 60.67% / 60.59% | 86 / 60.47% / 60.05% | 82 / 63.41% / 63.41% |
| + all same-sign first impulse | 203 / 56.65% / 56.53% | 208 / 52.88% / 51.94% | 204 / 56.86% / 56.15% |
| + same-sign M4 head | 203 / 57.64% / 57.55% | 208 / 54.33% / 54.07% | 204 / 58.82% / 57.84% |
| + same-sign PAIR head | 203 / 57.64% / 57.45% | 208 / 55.29% / 53.19% | 204 / 58.82% / 55.80% |
| + same-sign M4/PAIR agreement | 157 / 59.87% / 59.54% | 154 / 56.49% / 54.74% | 162 / 61.11% / 57.96% |
| + same-sign M4/BASE agreement | 148 / 57.43% / 57.13% | 145 / 58.62% / 56.51% | 161 / 61.49% / 59.82% |
| + same-sign BASE alone | 203 / 53.20% / 52.72% | 208 / 57.69% / 55.77% | 204 / 59.31% / 57.12% |

Key discovery: **coverage is technically expandable, but every examined no-new-data addition deteriorates PRAMV's yearwise BA**. The agreement policies supply more decisions than PRAMV but lose a large portion of DOWN recall (e.g. M4/PAIR continuation extension makes the *combined* 2025 DOWN recall 32.39%, compared with V1 53.66%). On 2025 continuation-only dates, M4/PAIR agreement has 47/80 = 58.75% accuracy yet BA 47.67% because most selected predictions are UP.

No candidate passes the conservative design gate of **BA >= frozen V1 BA on both 2023 and 2024 while increasing coverage**, and 2025 cannot be used to retune it. Thus NONE is promoted. The user should not receive a fabricated 60%+ full-year accuracy.

The directional metric also does NOT imply tradability: the historic PRAMV 2025 *sum of idealized signed overnight log returns* on 82 selected days is approximately **0.006710**, gross **before** all bank spreads, issue-delay, slippage and buy-only constraints. This is not a historical real-money return, and neither long/short nor spot prices may be silently treated as executable bank quotes.

## 4. Negative experiment: continuation-only logistic meta-learner

Exploratory chronological low-capacity meta-learner using ONLY historical matured continuation labels, same-day frozen base expert probabilities and same-sign state, L2 shrinkage, earliest 40 continuation-origin warm-up rows, no 2025 outcomes in the 2025 frozen fit:

- STATE + M4 logistic: 2023 (N=86) BA 42.69%; 2024 (N=130) BA 47.15%; 2025 (N=124) BA 50.00%, 100% predicted UP.
- STATE + M4 + PAIR logistic: 2023 BA 40.42%; 2024 BA 44.61%; 2025 BA 50.00%, 100% predicted UP.
- STATE + M4 + PAIR-agreement logistic: 2023 BA 47.84%; 2024 BA 50.24%; 2025 BA 53.85% with DOWN recall just 7.7%.

This exploratory fit did **not** improve balanced skill; do not treat a 2025 accuracy over 60% as substantive when UP dominance drives most of it. Meta-learner diagnostics were computed interactively, not included in the deterministic CSV/script above, so treat the table as research diagnostic, not the primary audited evidence.

## 5. Next new hypothesis — CAVS (Causal Absorption vs Venue Synchronization)

The problem is not 'the second half-hour repeats the first'; it is *why* similar late spot paths sometimes persist overnight and sometimes revert. Test whether a separate **external price-discovery channel** can distinguish these cases. Literature analogue: Ma et al. (2025), Global Finance Journal 64 101084, shows that gold/silver intraday continuation/reversal can depend on night-session information arrival, COMEX volatility and liquidity. This is not direct proof for 17:00 Istanbul -> 09:00 Istanbul.

Proposed, not yet fitted:
- First branch: keep frozen PRAMV for `01` / `10`; do NOT route same-sign dates to PRAMV.
- Second branch: on `00` / `11`, build only origin-ready, earlier/event-safe features: (1) signed late-impulse persistence/imbalance of the two completed half-hours; (2) COMEX GC futures return relative to simultaneous spot return; (3) GC price-volume confirmation or divergence *if actual historical volume is available*; (4) strictly lagged and source-ready gold-volatility state (GVZ or a documented substitute, never falsely direct flow).
- Define independent information gate: GC-minus-spot *incremental* predictive value, tested relative to **XAU-only continuation expert** on exact same source-ready dates. Use source timestamps including vendor delivery, avoid post-17:00 data, holiday gaps, DST mapping and zero/inactive GC candles.
- Test one sparse L2 regularized continuation-specific logistic model and one low-capacity decision state `confirm / diverge / unknown`. Train with expanding matured eligible labels and a firm minimum prior history; evaluate probability Brier, calibration, UP/DOWN recall, McNemar rescues/breaks, rolling half-year BA and risk–coverage. Do not select confidence thresholds by looking at 2025.
- Adopt a **shadow policy**: V1 signal output remains immutable. A CAVS continuation head can be promoted only if 2023 and 2024 each improve paired source-ready baseline and retain both class recalls (>=35% suggested study minimum), then transport unchanged to 2025 retrospective and score prospectively newly unseen origins in 2026+ if genuinely sealed. No 2026 labels for feature/threshold selection.
- Revisit bank-executable first post-17:00 quotes and 09:00 quotes before *any* P&L promotion. The 16:45–17:00 completed bar cannot be treated as an executable 17:00 open if the signal calculation and quote receipt happen afterward.

**Source gate:** The current manifest confirms native XAU15 data for 2023–2025 but not a complete governed GC 15m price-and-volume paired panel for this continuation study. Treat CAVS as **data-gated**; no synthetic GC or unverified venue-flow surrogate allowed.

## 6. Decision

**REJECT** naive same-sign continuation routing, reusing M4 / PAIR as broad same-sign heads, and easy apparent wins from UP-heavy meta-models. **PRESERVE** PRAMV V1 freeze and its selective, approximately one-third coverage. **ALLOW** a separate explicitly preregistered, source-ready cross-venue CAVS challenge with unchanged PRAMV and protection against data-snooping. The present research legitimately explains *why* the coverage gap persists; it does **not** claim to have solved it yet.

## 7. External research basis

- Ma, G., Bouri, E., Xu, Y., Zhou, Z. I. (2025), *The "night effect" of intraday trading: Evidence from Chinese gold and silver futures markets*, Global Finance Journal 64, 101084. DOI 10.1016/j.gfj.2025.101084.
- Hansen, P. R. (2005), *A Test for Superior Predictive Ability*, Journal of Business & Economic Statistics 23(4), 365–380. DOI 10.1198/073500105000000063.
- White, H. (2000), *A Reality Check for Data Snooping*, Econometrica 68(5), 1097–1126. DOI 10.1111/1468-0262.00152.
