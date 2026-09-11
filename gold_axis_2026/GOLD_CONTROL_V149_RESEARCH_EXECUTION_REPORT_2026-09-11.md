# Gold Control V1.49 Research Execution Report

**Run date:** 2026-09-11

**Starting canonical HEAD:** `e4bd899c3ee3e23e12ceb469e6e2e378da0e57f9`

**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.49, SHA-256 `442a975f8c9ddb2a658aba8bbe961d371e0007119821cf294e3de747c27da613`

**Evidence class:** `RETROSPECTIVE_RESEARCH_DIAGNOSTIC_NOT_PROSPECTIVE`

**Production writes:** `NONE`

## 1. Executive conclusion

The V1.49 programme was executed fail-closed. It did not establish a promotable monthly integration rule or a promotable 1D/3D probability model.

For monthly H=1, the four available frozen PIT-compatible views cover 43 common targets (2023-01 through 2026-07). The requested seven-view VW/DMA/DMS/IDMA/Patch/Momentum/RW panel has zero valid common PIT origins because the available CORE5 material is explicitly registered as `APPROVED_RESEARCH_ONLY_NOT_PIT`; no frozen executable DMA/DMS/IDMA forecast identity or canonical historical forecast artifact was found. DMA/DMS/IDMA diagnostic values were retained as `BLOCKED_PIT` and never entered candidate selection.

Within the legitimate four-view outer comparison (2025-01 through 2026-07, N=19), VW supplied the best point estimates: MAE 132.561 and RMSE 176.076, versus RW MAE 176.053 and RMSE 216.326. VW's squared-loss HAC comparison against RW did not reach 5% significance (`p=0.0917`). The simple equal four-view combination improved materially on RW but was weaker than VW and was not statistically superior to either (`p=0.2091` versus RW; `p=0.1980` for VW versus simple). Formal Hansen-Lunde-Nason MCS is `BLOCKED_INSUFFICIENT_SAMPLE`.

For short horizon, Block 4 context improved development Brier relative to Block 0 by 0.00215 (1D) and 0.00627 (3D), so it was retained before outer scoring. That gain did not survive the frozen outer replay. V1.49 Brier was 0.26183 for 1D (N=159) and 0.27674 for 3D (N=157), both worse than the mandatory 0.25 constant-probability benchmark. Calibration failed. The richer V1.49 candidate was also marginally worse than the matched retained HS-SDL-DMA benchmark at both horizons. No short-horizon probability may be promoted or displayed as calibrated authority.

## 2. Binding sequence and gate outcomes

| # | Gate | Status | Evidence |
|---:|---|---|---|
| 1 | Current canonical state reverify | PASS | canonical HEAD, v1.49 and Section 19 verified; Neon authority tables empty |
| 2 | Monthly same-origin panel reconstruction | PARTIAL / BLOCKED_PIT | four legitimate views N=43; seven-view common PIT N=0 |
| 3 | Complementarity/encompassing/error dependence | PASS for four-view diagnostic; NOT_PROVEN for seven views | high forecast/error correlation; partial redundancy |
| 4 | DM/CPA/MCS | PARTIAL | HAC DM and CPA computed; formal MCS blocked by sample size |
| 5 | Monthly integration-family diagnosis | PASS | complex integration NOT_PROVEN |
| 6 | Limited monthly candidate freeze | PASS | RW and SIMPLE_EQUAL_4 frozen before outer scoring |
| 7 | Short PIT/source/clock inventory | PASS | Block 0/4 usable; Blocks 1/2/3/5 fail-closed |
| 8 | Information-block definitions | PASS | field, source, clock and missing semantics frozen |
| 9 | Incremental predictive-content audit | PASS | development-only Block 0 then Block 4 |
| 10 | Limited short-model freeze | PASS | logistic + GBRT + HistGB candidates frozen |
| 11 | Nested expanding pseudo-real-time replay | PASS | 1D N=159; overlapping 3D N=157 |
| 12 | Calibration/stability/statistical comparison | PASS run / NOT_PROVEN promotion | both horizons fail skill/calibration gates |
| 13 | Architecture review | PASS | classifications recorded; no winner manufactured |
| 14 | Dashboard evidence contract | PASS | probability and production authority closed |
| 15 | Genuine prospective shadow | BLOCKED | PIT gaps and promotion evidence unresolved |

## 3. Current-state and authority verification

Production Neon snapshot `2026-09-11T09:55:00.411610Z` contained exactly 12 governed engine registrations. `monthly_forecast_contracts`, `decision_signal_snapshots`, `decision_runs`, and `decision_events` each contained zero rows. Non-OFF selector and ensemble registrations were both zero. Canonical-authority true rows were zero. No production database write was performed by V1.49.

The exact current-state record is `data_pipeline/audits/v149_research/current_state_reverify_v149.json`.

## 4. Monthly same-origin panel and PIT disposition

The panel has one record per model, forecast origin and target. Each target is exactly one calendar month after its origin. The four governed frozen forecasts (VW, Patch, Momentum, RW) have 43 aligned targets. Every record stores signed/absolute/squared error, origin cutoff, lineage, evidence class, model/version and Git identity.

DMA/DMS/IDMA reconstructions use the CORE5 research snapshot only for transparent diagnostic inspection. They are labelled `RETROSPECTIVE_DIAGNOSTIC_NOT_PIT`, `BLOCKED_PIT`, and excluded from selection, combination and promotion. Therefore:

- VW versus macro-dynamic family complementarity: `BLOCKED_PIT / NOT_PROVEN`;
- whether DMA/DMS/IDMA are independent or redundant: `BLOCKED_PIT / NOT_PROVEN`;
- seven-model ensemble, selector or regime weighting: ineligible.

## 5. Four-view complementarity and dependence audit

The preregistration/development window is 2023-01 through 2024-12 (N=24). Forecast correlations range from 0.9914 to 0.9971; error correlations range from 0.8592 to 0.9239. All four views are classified `PARTIALLY_REDUNDANT`. No squared-loss HAC DM comparison reaches 5%; the smallest p-values are Patch versus Momentum 0.0569, VW versus Momentum 0.0610, and VW versus RW 0.0885. All conditional-predictive-ability p-values exceed 0.05. Forecast dispersion's correlation with subsequent mean absolute error is 0.2264.

These results support neither forecast encompassing nor a predictable state-dependent winner. They justify only the mandatory RW and simple-equal benchmarks in the frozen outer comparison. Factor-adjusted, iterated, regularized, selector and regime-adaptive integration remain `NOT_PROVEN`.

## 6. Monthly outer results

### Combined outer window: 2025-01 through 2026-07 (N=19)

| Candidate | MAE | RMSE | Relative MAE vs RW | Relative MSFE vs RW | Median AE | Bias | Worst AE | Direction accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| VW | 132.561 | 176.076 | 0.753 | 0.662 | 85.673 | -10.982 | 373.385 | 73.7% |
| SIMPLE_EQUAL_4 | 148.782 | 188.003 | 0.845 | 0.755 | 117.409 | -12.332 | 351.882 | 78.9% |
| Momentum | 158.320 | 205.632 | 0.899 | 0.904 | 127.241 | 39.685 | 521.313 | 84.2% |
| Patch | 169.458 | 209.487 | 0.963 | 0.938 | 157.338 | -3.030 | 419.373 | 68.4% |
| RW | 176.053 | 216.326 | 1.000 | 1.000 | 155.000 | -75.000 | 444.000 | 0.0% |

Monthly win concentration is Momentum 8, VW 6, RW 2, simple 2, Patch 1. This explains why a lower aggregate MAE is not a universal winner claim. VW-versus-RW HAC squared-loss p-value is 0.0917. Simple-versus-RW p-value is 0.2091. Patch is significantly worse than simple in this small sample (`p=0.0147`), but the multiple-comparison superior-set claim remains blocked.

### Retrospective subwindows

| Window | N | VW MAE | Simple MAE | Momentum MAE | Patch MAE | RW MAE |
|---|---:|---:|---:|---:|---:|---:|
| 2025 | 12 | 90.634 | 107.502 | 129.392 | 119.067 | 140.583 |
| 2026 Jan-Jul | 7 | 204.435 | 219.549 | 207.909 | 255.843 | 236.857 |

Errors rose sharply in 2026 for all candidates. This is retrospective evidence, not a pristine V1.49 future test. No model or threshold was changed in response.

Monthly architecture finding: VW is the strongest point-estimate core in the available outer data, RW remains the defensive benchmark, and the simple combination remains a useful benchmark. Promotion of any new integration is `NOT_PROVEN`.

## 7. Short-horizon inventory and information blocks

The frozen NY17 reconstruction contains 400 unique chronological origins from 2025-01-03 through 2026-08-30; 399 1D and 397 3D targets are mature.

| Block | Disposition | Reason |
|---|---|---|
| 0 gold own-history | READY / retained baseline | exact chronological NY17 values |
| 1 cross precious metals | BLOCKED_CONTRACT | exact session/timestamp parity not frozen |
| 2 FX + rates | BLOCKED_PIT | only monthly/PIT material; no daily-origin join |
| 3 equities + risk + commodities | BLOCKED_PIT | daily historical origin availability not proven |
| 4 Gold Control states | READY / retained after development | categorical chronological state joins |
| 5 positioning/flow/news | BLOCKED_PIT | historical release/timestamp lineage not proven |

Block 4 uses FAST, SLOW, MONTHLY_DIRECTION and emergency state categories as context, never as numeric votes. BOCPD, GVZ and Macro Event lacked a valid exact daily-origin join for this run and were not silently filled.

## 8. Short-horizon development and frozen candidates

The development-only incremental audit used the earlier origins. Block 0+4 versus Block 0 produced:

| Horizon | Development N | Block 0 Brier | Block 0+4 Brier | Gain |
|---|---:|---:|---:|---:|
| 1D | 100 | 0.270384 | 0.268236 | 0.002148 |
| 3D | 96 | 0.258134 | 0.251866 | 0.006268 |

Before viewing the final outer results, the code froze logistic C values 0.1/1/10, depth-1/2 GBRT, depth-2/3 histogram GBRT, prior-only hyperparameter selection, prior-only Platt calibration, Block 0+4, outer start index 240, P=0.50 and expanding-frequency baselines, and HS-SDL-DMA where origin parity existed.

## 9. Short-horizon outer results

| Horizon/model | N | Brier | Log loss | Accuracy | Balanced accuracy |
|---|---:|---:|---:|---:|---:|
| 1D V1.49 | 159 | 0.261830 | 0.717042 | 43.4% | 50.0% |
| 1D HS-SDL-DMA matched | 159 | 0.261729 | 0.716855 | 45.3% | 46.3% |
| 1D expanding UP frequency | 159 | 0.259109 | 0.711465 | 43.4% | 50.0% |
| 1D P=0.50 | 159 | 0.250000 | 0.693147 | 43.4% | 50.0% |
| 3D V1.49 | 157 | 0.276739 | 0.749213 | 48.4% | 50.0% |
| 3D HS-SDL-DMA matched | 157 | 0.271097 | 0.736920 | 48.4% | 50.0% |
| 3D expanding UP frequency | 157 | 0.267289 | 0.728736 | 48.4% | 50.0% |
| 3D P=0.50 | 157 | 0.250000 | 0.693147 | 48.4% | 50.0% |

The 1D calibration intercept/slope are -0.284/0.081; the 3D values are -0.444/0.613. Both fail the frozen calibration gate. Expected-return forecasts also fail to establish useful direction skill: 1D return MAE 0.011685, RMSE 0.016891, direction accuracy 42.8%; 3D return MAE 0.020502, RMSE 0.027878, direction accuracy 41.4%.

All frozen estimator families were scored. The best family-level Brier was logistic C=10 for 1D (0.261667) and histogram GBRT depth 3 for 3D (0.274025); neither beats 0.25. These family results are diagnostics and were not used to invent a post-outer candidate.

Because 3D targets overlap, comparisons use dependence-aware block/HAC logic. The approximate superior-set diagnostic retains P=0.50 as best and excludes V1.49 at the 5% level for 3D (`p=0.0395`). Formal MCS remains `NOT_PROVEN`.

## 10. Architecture and dashboard decision

- VW + DMA/DMS/IDMA complementarity: `BLOCKED_PIT / NOT_PROVEN`.
- DMA/DMS/IDMA separate-vote justification: `NOT_PROVEN`.
- Patch/Momentum incremental information: `NOT_PROVEN`; both are retained research views, not removed.
- Simple combination versus complex: no complex family was eligible; simple improved on RW pointwise but did not beat VW.
- RW anchoring: retained as mandatory defensive benchmark; adaptive anchoring benefit `NOT_PROVEN`.
- Origin-state prediction of relative model loss: CPA did not establish it.
- Strongest monthly point architecture: VW alone among valid candidates, without statistical promotion claim.
- Short-horizon real predictive gain: none established in outer replay.
- FAST/SLOW/Gold Control states: development gain, outer incremental gain `NOT_PROVEN`.
- 1D and 3D baseline beaten: no.
- Probability calibration acceptable: no.
- Statistical superiority: not established for the promoted architecture; short 3D evidence is adverse.
- Prospective shadow readiness: blocked.
- Production readiness: no.

Dashboard rules are fail-closed: retrospective monthly metrics may be displayed only with their evidence label. Raw short scores, vote percentages and V1.49 probabilities must not be presented as calibrated forecast authority. BUY/SELL/HOLD/EXIT/REDUCE, selector weights and production forecast authority remain prohibited.

## 11. Reproducibility and implementation tests

Three full outer runs returned identical frame hashes:

- monthly `91ab3fd7a56411572d626e09f74d01467b3fb61becd1d9bffdb30ec2a4eebdf5`;
- 1D `00a0e8130ebf2db72a364a715fad8572774d913cf532433b9516ed65961b50b5`;
- 3D `ec0729a57c10e4738083e929b1f2297c5218613dfe26e8c2bab1877051c4ebc9`.

Tests cover PIT fail-closed handling, exact common-origin alignment, prefix invariance, deterministic rerun, no-future-target logic, 3D maturity, calibration isolation, candidate-freeze enforcement and closed authority. No leakage or PIT violation was accepted; missing PIT proof remains a blocker rather than an imputed input.

The V1.49 suite passed 9/9 tests. The wider repository suite initially exposed a pre-existing v1.45 auditor compatibility defect: it required the project manifest to equal v1.45 even though the sole canonical manifest is now v1.49, causing the frozen 2025-10 Macro contractual exclusion test to fail closed. The auditor was corrected to accept an observed project manifest version at or above its v1.45 minimum only when the binding v1.45 contract remains referenced. After correction, 76/76 collectable wider tests passed. One legacy component-role test requires PyTorch, which was not installed in the execution environment and was therefore not represented as a passing test.

## 12. Remaining blockers before genuine prospective shadow

1. Reconstruct or generate frozen, origin-valid DMA/DMS/IDMA forecasts with executable identity and verifiable vintage lineage; otherwise the central seven-model complementarity question remains blocked.
2. Freeze exact daily PIT source/session contracts for cross metals, FX/rates and risk/commodity inputs before any new short-horizon scoring.
3. Accumulate genuinely prospective issued forecasts after architecture freeze; 2025/2026 outcomes are researcher-visible and cannot be pristine evidence.
4. Demonstrate short-horizon Brier/log-loss skill over P=0.50 and acceptable calibration on prospective or otherwise legitimate new outer origins.
5. Keep `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, and production authority closed until these gates are satisfied.

## 13. Authority and method limitations

The design follows Manifest Section 19.14 and the cited primary literature: Diebold-Mariano for predictive-accuracy comparison, Giacomini-White for conditional predictive ability, Hansen-Lunde-Nason for superior-set discipline, Tashman for rolling OOS, Hewamalage et al. for leakage controls, and Gneiting et al. for calibration/proper scoring. Given the small monthly sample, the stored HAC and block-resampling results are assumption-aware diagnostics; they are not relabelled as a fully powered formal MCS.

Machine-readable results are under `data_pipeline/audits/v149_research/`. The architecture/dashboard decision is `architecture_dashboard_review_v149.json`; deterministic evidence is `determinism_evidence_v149.json`.

## 14. GitHub and final authority closeout

- Feature branch: `gold-v149-research`.
- Research PR: `#35`.
- PR head: `bdcd5dd8cdb9698168965a3a5b5c87272e20afd8`.
- GitHub Actions governance job: PASS.
- Research merge/canonical checkpoint: `f02c49457992b4952e5b79c930c14e7dbf947130`.
- Post-merge Neon snapshot: `2026-09-11T10:52:24.036Z`.
- Post-merge engine inventory: 12.
- Post-merge authority counts (`monthly_forecast_contracts`, `decision_signal_snapshots`, `decision_runs`, `decision_events`): `0/0/0/0`.
- Post-merge non-OFF selector/ensemble counts: `0/0`.
- Historical or production rows inserted by V1.49: 0.

The closeout-only report commit is delivered through a second narrow PR. Its merge SHA becomes the final canonical HEAD and supersedes the research merge SHA only as repository bookkeeping; it does not alter any result, model, threshold, feature or authority state.
