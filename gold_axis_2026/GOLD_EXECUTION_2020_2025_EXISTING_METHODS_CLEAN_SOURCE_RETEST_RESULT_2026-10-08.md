# GOLD EXECUTION — Existing Forecast Methods Re-tested on Audited 2020–2025 XAU/USD Source — 2026-10-08

**Repository:** `ataullahturgut/sim3-automation`, branch `gold-execution-channel-audit-20261006`. **Verdict:** `PARTIAL FAMILY REPLAY COMPLETE — NO PROMOTED CHAMPION; SESSION TARGETS AND MACRO-PIT PRAMV NOT YET FULLY RE-RUN`.

## 1. What was actually executed (not copied from old metrics)

**Actual new-source re-training** for **19 named original architecture/policy identities** across two successful GitHub Actions workflows:

- LIT Stage1 **six** frozen original feature specifications: three individual prior-17:00 half-hours, OVN paired half-hours, DAY 09:00, separate delayed DAY 09:30; each with original `StandardScaler+LogisticRegression(C=1)` and OLS sign.
- LIT Stage2 **three** original price-only specs: single 16:00–16:30, paired path, continuous pre-17:00 volatility/jump state; logit and OLS sign.
- PSF-OVN **four** original price-only `M0_SCALAR`, `M1_SIGNATURE`, `M2_FPCA`, `M3_SIG_FPCA` models with original expanding-history PCA/PIT feature training, no macro model.
- FSMR **two** original finite-state shrunk probability models `FSMR4`, `FSMR8`, updated by their original prequential matured-history algorithm.
- LIT Stage3 **four** original price-based policies: `PAIR_ALL`, `PAIR_CONF60`, `SNR_Q67`, `SNR_Q67_PAIR_SAME`; `PAIR_CONF60` produced **no qualifying cases** and is therefore not a numerical score.

**Original identity caveat:** `LIT_OVN0_1600_1630` and `BASE_1600_1630` are redundant, as are `LIT_OVN1_PAIR` and `PAIR_1600_1700`. Therefore 19 names are NOT 19 independent pieces of evidence.

**Price/target source:** One single audited 2020–2025 Dukascopy-derived XAUUSD BID source in private Neon, from 141,890 accepted M15 BID/ASK observations and 1,549 source-maturity controlled issue dates. The 09:00 versus 17:00 execution labels were independently verified in `GOLD_EXECUTION_2020_2025_PRICE_LABEL_FORENSIC_AUDIT_20261008.json`. Previous legacy vendor results and forecasts were not overwritten. All models trained on **BID** returns only; separate ASK quotes remain execution uncertainty evidence and are NOT presumed Turkish-bank quotes.

**Time method and samples:** `2020–2022 = warmup/historical training`, `2023–2024 = chronological expanding-origin development scoring`, `2025 = fixed 2024-trained parameters for PSF and LIT; FSMR intentionally uses its prequential-state update`. Each archived 2025 result was previously inspected as part of research and is **retrospective transport**, NOT untouched future OOS. All eligible matured source labels were included without ex-post filtering by realization or post-hoc class balancing.

- Original 09:00 features known by exactly 09:00, original 17:00 pre-decision features ending exactly 17:00; SOURCE delivery lag and Turkish bank execution readiness remain a blocker to live claims.
- Friday 17:00→Monday 09:00 **64h** is evaluated as a **separate** population from normal **16h** weekday OVN.
- The delayed `DAYD` model forecast issued at 09:30 is **not** a 09:00 DAY forecast, and its 09:30→17:00 label is kept distinct.
- Accuracy, balanced accuracy **BA=(UP recall+DOWN recall)/2**, individual recalls, Brier, count and confusion matrix computed identically by year/source and horizon; original model C=1 and fixed selectivity retained, no 2025-inferred tuning.

## 2. Actual new-source BALANCED ACCURACY (BA) — complete DAY 09:00→17:00

| Original model | 2023 BA (N=256) | 2024 BA (N=259) | 2025 BA (N=258) | 2025 DOWN recall |
|---|---:|---:|---:|---:|
| LIT DAY0 OLS-sign | 53.08% | **47.15%** | **54.79%** | 50.00% |
| LIT DAY0 Logistic | 49.88% | 50.17% | 52.96% | **10.71%** |
| Delayed 09:30 DAYD OLS *(different horizon)* | 51.05% | 47.83% | 47.62% | 17.76% |

2025 DAY always-UP trivial benchmark **56.59% raw accuracy but BA=50%**, versus LIT DAY0 logistic 58.53% raw accuracy with only 10.71% DOWN recall. Accuracy must not be interpreted as reliable two-sided direction prediction. The 09:30 variant is not a valid same-horizon DAY comparison.

## 3. Actual new-source BA — **REGULAR 16-HOUR OVN ONLY** (17:00→next 09:00)

| Original model / original variant | 2023 BA | 2024 BA | 2025 BA | 2025 N | 2025 DOWN recall |
|---|---:|---:|---:|---:|---:|
| LIT first impulse 16:00–16:30 OLS-sign | 48.96% | 50.72% | **54.35%** | 198 | 22.09% |
| LIT 16:00–17:00 paired OLS-sign | 47.72% | 51.86% | 50.39% | 198 | 41.86% |
| LIT 3h volatility state OLS-sign | 48.52% | 46.36% | 50.57% | 198 | 39.53% |
| PSF `M0_SCALAR` | **51.13%** | **50.41%** | **51.81%** | 198 | 23.26% |
| PSF `M1_SIGNATURE` | 55.16% | **46.42%** | 50.16% | 198 | 24.42% |
| PSF `M2_FPCA` | 52.53% | 49.96% | 49.17% | 198 | 19.77% |
| PSF `M3_SIG_FPCA` | 54.95% | 49.65% | 49.40% | 198 | 25.58% |
| **FSMR4** | **50.99%** | **53.12%** | **54.29%** | 198 | **52.33%** |
| FSMR8 | 45.93% | 55.18% | 52.50% | 198 | 52.33% |
| LIT3 PAIR_ALL price model | 49.22% | 49.56% | 50.00% | 198 | **0.00%** |
| LIT3 SNR_Q67 *(selective)* | 52.99% (N=70) | **46.35%** (N=67) | **55.72%** | **60** | 48.48% |
| LIT3 SNR_Q67+PAIR_SAME *(selective)* | 56.00% (N=35) | **47.06%** (N=34) | 54.76% | **26** | 42.86% |

**Interpretation:** FSMR4 is the most consistent of the listed 16h standalone directional challengers by annual BA, and its 2025 DOWN recall is less one-sided than the near-always-UP logistic heads. However **50.99–54.29% BA is modest**, and these years have already been used throughout model development. It is **not statistically established or authorized as a production winner**.

LIT3 SNR's best-looking 2025 BA (55.72%) occurs on only 60/198 accepted regular nights and degraded below chance in 2024. No new cutoff, gate, expert weight or champion was selected on 2025.

## 4. Actual new-source BA — **FRIDAY→MONDAY 64-HOUR OVN HOLD** (different target)

| Existing method | 2023 BA | 2024 BA | 2025 BA | 2025 N |
|---|---:|---:|---:|---:|
| FSMR4 | 44.05% | 51.71% | 53.57% | 51 |
| FSMR8 | 42.86% | 47.13% | **60.00%** | 51 |
| LIT paired OLS-sign | — | — | 53.10% | 51 |

`FSMR8` apparent 2025 weekend strength **does not replicate in 2023–2024**. It must NOT be pooled with weekday 16h to manufacture an attractive headline.

## 5. Frozen existing PRAMV V1 / RFR / macro PSF — what was actually checked

Separate **source-retargeted replay of prior archived binary predictions against the NEW source's labels on identical available dates** was executed. **This is not a retraining or re-running of the original feature pipeline.** Historical saved predictions can use a different historical vendor and do not become new-source-model outputs merely by changing their truth labels.

| Original archived (unchanged) policy | 2023 new-label BA / N | 2024 new-label BA / N | 2025 new-label BA / N | exact evidence class |
|---|---:|---:|---:|---|
| Frozen **PRAMV V1** | **60.38% / 86** | **58.97% / 84** | **61.39% / 77** | OLD forecasts vs independently verified new labels only |
| RFR-NOMACRO V1 | 57.59% / 115 | 55.87% / 105 | 56.42% / 104 | OLD forecasts vs new labels only |
| PSF M4_SIGNATURE+FPCA+MACRO | 56.89% / 246 | 53.02% / 249 | 54.96% / 244 | OLD forecasts vs new labels only |

Original PRAMV 2025 historical frozen report was 63.41% BA on 82 accepted dates. New independent BID-label comparison gives **61.39% BA on 77 matched dates**; **not** a matched-sample causal deterioration claim, because denominators changed and legacy features/predictions were NOT rebuilt.

**Blocking problem is genuinely material:** `GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv` is PIT incomplete for 2025: archived event audit found FOMC **0**, NFP **11**, CPI **10** instead of complete event counts. Treating missing events as `macro_released=0` would create fabricated "no announcement" features and incorrectly activate PRAMV macro veto. Therefore frozen M4 and exact PRAMV cannot ethically be called **fully rerun on 2020–2025** until the historic FOMC/NFP/CPI actual/consensus/release-readiness ledger is verified for each origin. The existing frozen PRAMV V1 is unmodified; don't silently substitute M3 for M4 or call a macro-free rule PRAMV V1.

## 6. What "ALL models" actually means — machine-audited inventory

The `...INVENTORY.csv` checks the archived original output filenames and records explicit status:

- **19 exact existing research identities actually reconstructed/refit** across source-repaired LIT Stage1/2, PSF price-only, FSMR, LIT3. Around 2 original architecture definitions are duplicated/nested (not independent).
- **23 original archived method identities** were additionally scored as **legacy prediction transfer**, not newly trained. Some duplicate those actually re-run, so do not add counts naively.
- **28 archived WGC/Sobti multi-session model prediction files** were **BLOCKED_DIFFERENT_TARGET**. Their ASIA/EU/US/WGC/Sobti labels are NOT the 09:00–17:00 and 17:00–next 09:00 execution labels. This includes the old SESSION model-01..09 family, shallow CART, SAGE, Structural IRIS, RIFT, VEGА, OPAL, SENTRY, DART, AURORA, HELIOS, BOCPD and related nested routers. Translating architectures to execution target requires their originally required 1h metals/session/PIT features and exact-origin retransmission, not target renaming.
- **12 unrefit original authority identities** retained on the explicit TODO register, including PRAMV V1, M4 macro, raw GVZ hazard and old SENTRY/AURORA/HELIOS architectures; these overlap the blocked archival session files.
- **2 archived prediction files** have noncomparable schema / prediction semantics; also delayed 09:30 is handled as an explicitly distinct horizon.
- No new consensus, weighted voting, hybrid router or oracle-on-2025 was performed or selected in this work.

**Scientific test contracts:** exact 2020–25 price-source identifier; chronological prequential labels with matured overnight gate; fixed original feature definitions/hyperparameters; regular versus weekend split; no target-period feature leakage, under the exact 09:00/17:00 idealized timestamp; source uncertainty flagged in V2 separately; 2025 is retrospective only; output metrics by year include full confusion matrices, balanced accuracy, DOWN/UP recall, Brier and coverage. No transaction profit claims.

## 7. Evidence files & reproducibility

- `GOLD_EXECUTION_2020_2025_SINGLE_MODELS_CLEAN_SOURCE_REPLAY_20261008_SUMMARY.json`
- `GOLD_EXECUTION_2020_2025_SINGLE_MODELS_CLEAN_SOURCE_REPLAY_20261008_METRICS.csv` — exact re-trained Stage1/2 and constant UP/DOWN controls; 16h vs 64h independent.
- `GOLD_EXECUTION_2020_2025_SINGLE_MODELS_CLEAN_SOURCE_REPLAY_20261008_SOURCE_TRANSPORT_METRICS.csv` — **69** source-retargeted archive metric rows, not model retraining.
- `GOLD_EXECUTION_2020_2025_SINGLE_MODELS_CLEAN_SOURCE_REPLAY_20261008_INVENTORY.csv` — `ACTUAL_REFIT`/source-label-transfer/different target/blocked authority.
- `GOLD_EXECUTION_2020_2025_EXISTING_PSF_FSMR_LIT3_SOURCE_REPLAY_20261008_SUMMARY.json`
- `GOLD_EXECUTION_2020_2025_EXISTING_PSF_FSMR_LIT3_SOURCE_REPLAY_20261008_METRICS.csv`
- Date-level exact forecasts only as access-controlled GitHub Actions **run artifacts**; raw BID/ASK OHLC remains in private Neon tables; prior originals unchanged.
- Scripts: `tools/gold_execution_2020_2025_all_existing_model_replay_20261008.py`, `tools/gold_execution_2020_2025_psf_fsmr_lit3_clean_replay_20261008.py`.
- Successful jobs: `Gold Execution Existing Models Clean Price Retest 2020-2025` and `Gold Existing PSF FSMR LIT3 Source Corrected Replay 2020-2025` (completed on this date).

## 8. Unambiguous verdict and next research gate

**No source-clean original full-coverage standalone model has yet demonstrated strong replicated two-sided direction edge across 2023, 2024 and 2025.** New-source training does not rescue near-always-UP models or eliminate their low DOWN recall. FSMR4 merits **scientific examination** as a relatively class-balanced modest baseline, but is not a final system. The legacy PRAMV selective archive remains **promising but not newly trained**, source-dependent and not fully verified.

**Next required if all original model families are to be fully evaluated:** (A) obtain event-by-event PIT-complete macro ledger and identical current source inputs to faithfully retrain M4/PRAMV V1; (B) port only historically defined WGC/Sobti SESSION architectures to execution labels with their actual source-safe features, rather than claim SESSION scores represent DAY/OVN; (C) use genuinely future as-of-2026-10-08+ prospective origins for model promotion. No new confidence threshold or 2025-selected champion authorized.
