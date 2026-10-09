# ZN-VPT2 source-constrained nested volume ablation — ACTUALLY EXECUTED 2026-10-09
**Evidence class:** SQL-derived read-only governed Neon data + in-memory JS deterministic logistic chronological fit. No market rows exported to GitHub or to DeepSeek; aggregate-only output below. **NO PROMOTED MODEL.**

## Scientific chain (author first, external criticism second, manifest novelty check, data test last)
1. Original GPT-6 independent hypothesis in `GOLD_ZN_VOLUME_CONDITIONED_NIGHT_SIGN_HYPOTHESIS_PREREG_20261009.md` before hypothesis-specific labels were queried.
2. DeepSeek Flash single targeted hostile referee `GOLD_DEEPSEEK_ZN_VOLUME_FOCUSED_REFEREE_20261009_REVIEW.md` (3,393 provider tokens). It was asked to REFUTE THE SPECIFIC proposal, not invent models. Emphasized volume is not signed aggressor flow, macro vol confounding, contract rolls, sparse conditional cells; requested REVISE.
3. Manifest checked **again**: CME3-K25 previously scored six NQ/ZN/CL *returns* not volume, CAVS proposed GC price/volume but **untrained**, BSC8 own XAU quote-spread, PRAMV M4 macro-veto. ZN volume interaction **not previously run** but is a close cross-market descendant, not novel universal architecture.
4. Original high-volume disagreement cohort after prior20 seasonal median: 2023 14, 2024 18, 2025 27 eligible, **STOPPED BEFORE LABEL SCORING** for 2023–24 sample insufficiency.
5. A revised, separate continuous-volume test was re-preregistered **before revised-label outcomes** in `GOLD_ZN_CONTINUOUS_VOLUME_INCREMENTAL_TEST_PREREG_20261009.md`. The selection change was justified ONLY by observed unconditional sample counts; no 2025 outcome selected a parameter.

## Fixed causal target / one-vendor price data
XAU/USD regular weekday OVERNIGHT **17:00 Europe/Istanbul → next eligible09:00** signed endpoint, original source `gold_research_evduka_xau_session_target_candidate_v1` (`overnight_y=0` means DOWN); source-matched BID/ASK M15 from `gold_research_evduka_xau15m_bidask_candidate`. Two pre-origin spot mids at 15:00 and16:00, M15 start14:45/15:45. Databento separate CME native c.0 ZN futures H1 close from hour-start local14:00 and15:00, same `instrument_id`, positive volumes, both bars closed by16:00 (assume conservative published by16:15). H1 model as-of proof not separately certified from vendor. Rolling prior20 same-local-15h positive-volume ZN hour series forms baseline; no current/future observations contribute.

### Exact sample populations
| Year | Normal eligible base | ZN+spot price source-ready | Strict prior20 source-ready | Actual model scored |
|---|---:|---:|---:|---:|
| 2023 | 198 | 173 | 158 | 72 (calendar-month expanding evaluation with ≥80 previous origins) |
| 2024 | 198 | 175 | 175 | 175 |
| 2025 retrospectively inspected | 198 | 178 | 178 | 178 |
Total data in revised regression product = **511 origin rows**; 425 evaluated. Dates have one upstream spot source. NO Friday64h, 2026 scores, bank prices, transaction commission or short-sale constraints.

## Exact pre-origin covariates
Let `rx=10000ln(mid16/mid15)`, `rz=10000ln(ZNclose16/ZNclose15)`, `v=ln(ZN_15h_volume/median20_prior_same15h_volume)`.
- Baseline B0: intercept + [rx,rz,abs(rx),abs(rz),v].
- Challenger B1: **same covariates**, plus only [rz*v].
- Both are L2 logistic trained on DOWN=1, intercept unpenalized, standardized train-only mean+SD separately by feature, penalty `5/(2N) sum(beta_j^2)`. Deterministic batch gradient descent 1800 iterations, learning rate0.15, average logloss+penalty. DOWN iff probability>0.5, no historical threshold search.
- 2023: calendar-month prequential, at least 80 strictly PREVIOUS qualified origin rows; 2024: fitted ONLY 2023 qualifying rows; 2025: fitted ONLY completed 2023–24, 2025 labels never used in fit. Same source/date panel B0/B1. No shuffling or hyperparam fit driven by 2025 outcomes.
- The prereg specified learning rate 0.1 and 2000 iterations or tolerance; actual execution used 0.15 and 1800 iterations (an optimizer difference requiring independent convergence replication). Both nested models used identical realized optimizer, so the within-run comparison is still paired. **Treat this as an exploratory diagnostic, NOT a perfect preregistration-concordant confirmatory result**. No claim of scientific significance.

## Real executed paired metrics (DOWN-positive)
| Year | Score N | B0 BA | B1 BA | B0 accuracy | B1 accuracy | B0 Brier | B1 Brier | B1 DOWN recall | B1 DOWN precision | Rescues / breaks vs B0 | McNemar exact 2-sided p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2023 | 72 | 47.95% | 47.95% | 54.17% | 54.17% | 0.24920 | 0.24923 | 3.23% |25.00%| 0/0 |1.00|
| 2024 |175|48.33%|48.33%|52.57%|52.57%|0.26107|0.26104|18.67%|38.89%|0/0|1.00|
| 2025 retrospective |178|49.08%|50.72%|53.37%|55.06%|0.25570|0.25569|21.05%|44.44%|3/0|0.25|

Confusion matrices B0/B1 (TP=DOWN correct, FP=false DOWN, FN=missed DOWN, TN=UP correct):
- 2023: B0 TP1 FP3 FN30 TN38; B1 exactly same.
- 2024: B0 TP14 FP22 FN61 TN78; B1 exactly same.
- 2025: B0 TP15 FP22 FN61 TN80; B1 TP16 FP20 FN60 TN82. Only **3** corrected decisions on 178 matched retrospective dates, not replicated in 2023/24.

## Interpretation / rejection
The prespecified positive incremental 2024+2025 BA and Brier criterion is **FAILED**: 2024 BA identical, 2025 only +1.64 pp without paired significance, Brier difference ~1e-5. DOWN recall only 21.05% on 2025 B1; most overnight DOWN nights still missed. A multi-factor apparent cohort effect is **not independently signed orderflow**; H1 volume, times, DST, settlement/roll and macro-event confounding remain possible.

**REJECT ZN-VPT2 as a directional forecast breakthrough.** No next optimization of volume threshold, sign or confidence using inspected 2025. The correct enduring insight is that rare-cell signal selection looked promising as a hypothetical mechanism but lacks sample, and continuous volume adds little measurable value on same dates. No 2026 source-spliced transport and no live trading promotion.

## Reproducibility note
SQL joins are deterministic: local `t.issue_date+14h/15h` to same-contract CME ZN and XAU local14:45/15:45 M15 starts; prior20 median via source-only `LATERAL (ORDER BY ts_event DESC LIMIT 20) + percentile_cont(0.5)`; full-weekday night gates. Logistic evaluated privately in sandboxed in-memory JS, no raw user data printed. For an independent archival rerun, implement the listed exact optimizer as well as original prereg optimizer and compare convergence; freeze new code hash and generate dated forecasts with full eligible-date hashes in protected Actions artifacts before any promotion.

## Conceptual academic supports (NOT actual XAU 17->09 performance)
Hauptfleisch et al., 2016, DOI10.1002/fut.21775; Elder et al., 2012, DOI10.1016/j.jbankfin.2011.06.007; Sobti et al., 2021, DOI10.1016/j.irfa.2021.101893. The evidence here comes solely from our controlled 2023–25 Neon experiment; external LLM did not backtest market data.
