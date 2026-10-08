# PRAMV V1 error-decomposition audit and orthogonal reliability-gate challenger — 2026-10-08

**Status:** EXPLORATORY DIAGNOSTIC COMPLETE / V2 HYPOTHESIS ONLY / NOT PROMOTED / V1 FREEZE UNCHANGED  
**Execution target:** 17:00 Europe/Istanbul -> next eligible 09:00 Europe/Istanbul  
**Research snapshot:** `ac312546d29d77ad156a40016d3f032041147967`  
**Binding authority:** `GOLD_EXECUTION_PRAMV_V1_PROSPECTIVE_FREEZE_2026-10-07.md`

## 1. Inputs and reconstruction

Read-only source files at the above snapshot:
- `GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv` (RFR reversal candidates and source-veto eligibility);
- `GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv` (M0–M4 direction scores/predictions);
- `GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv` (PAIR_ALL);
- `GOLD_EXECUTION_PRAMV_GATE_ROWS_2026-10-07.csv` (accepted signals only);
- `GOLD_EXECUTION_PRAMV_GATE_SUMMARY_2026-10-07.json`.

Join on exact date; select `eligible_nomacro=True` before checking M4 agreement. Important: the saved PRAMV_GATE_ROWS file is post-filtered by agreement, so its `agree` column is necessarily always True. Using that file alone to measure rejection is invalid.

Among 387 RFR reversal candidates (129/year), 342 pass the historical no-macro eligibility filter (2023=118, 2024=113, 2025=111). This is **not** the full decision-date denominator; PRAMV original full-date coverage remains 34.77%, 33.20%, 32.28% for 2023, 2024, 2025.

## 2. Empirical discrimination of the M4 agreement filter

Accuracy means correctness of the unchanged first-impulse RFR call (also the PRAMV call when M4 agrees). Counts are historical diagnostics, not untouched confirmatory evidence.

| Period | RFR no-macro all: correct / N | M4 agrees: correct / N | M4 disagrees: correct / N | Accuracy gap agree - disagree |
|---|---|---|---|---|
| 2023 | 68/118 = 57.63% | 54/89 = 60.67% | 14/29 = 48.28% | +12.39 pp |
| 2024 | 64/113 = 56.64% | 52/86 = 60.47% | 12/27 = 44.44% | +16.02 pp |
| 2023–2024 | 132/231 = 57.14% | 106/175 = 60.57% | 26/56 = 46.43% | +14.14 pp |
| 2025 retrospective | 65/111 = 58.56% | 52/82 = 63.41% | 13/29 = 44.83% | +18.59 pp |
| 2023–2025 exploratory | 197/342 = 57.60% | 158/257 = 61.48% | 39/85 = 45.88% | +15.60 pp |

The M4 veto accepts 257/342 = 75.15% of RFR/no-macro candidates. Its ~one-third full-date action coverage is the product of RFR/no-macro eligibility and the agreement filter.

**Two-sided Fisher exact test** on correct/wrong counts across M4-agree versus M4-disagree groups:
- 2023–2024: p ~= 0.0874;
- 2025: p ~= 0.1239;
- pooled 2023–2025: nominal p ~= 0.0159, **NOT confirmatory** because synthesis used previously observed archive and multiple models were explored.

An exploratory **within-year circular-shift negative control** rotates the observed M4 approval sequence relative to fixed RFR outcomes, keeping year-specific approval counts and serial clustering. With 30,000 seeded pseudo-random nonzero rotations per year (LCG seed 20261008), one-sided exceedance probabilities for the approval gap are approximately 0.0445 (2023–2024), 0.0562 (2025), and 0.0099 (all three). These are *diagnostic pseudo-null probabilities*, NOT independent OOS p-values or corrections for discovery/data snooping.

Within-half-year diagnostics caution against an overstrong regime claim. Rejected-call accuracies are not below 50% in every semester: 2023 H2 and 2024 H2 are each 7/12 = 58.33%. The 2025 H2 rejected slice is 8/15 = 53.33%. Small samples and time-variation remain plausible.

The original common-row comparison against PAIR remains 15 rescues / 6 breaks in 2023–2024, exact **two-sided** McNemar p=0.0784. The previously reported one-sided binomial p=0.0032 vs 50% for the selected policy does NOT adjust for model/combination discovery. Do not confuse within-policy success with proven incremental superiority over PAIR.

## 3. Ablation: does macro-augmented M4 materially improve over M3?

M3 and M4 share the same first two half-hour inputs, scalar path, signatures and FPCA. M4 adds macro state. On the same no-macro RFR candidates:

| Period | M3 agrees (correct / N) | M4 agrees (correct / N) | Overlap |
|---|---|---|---|
| 2023–2024 | 106/177 = 59.89% | 106/175 = 60.57% | 172 common accepted |
| 2025 retrospective | 53/84 = 63.10% | 52/82 = 63.41% | 82 common accepted |
| 2023–2025 exploratory | 159/261 = 60.92% | 158/257 = 61.48% | 254 common accepted |

In 2023–2024, M3-only accepted 5 days (2 correct) and M4-only accepted 3 days (2 correct). M4 is thus **not shown to add substantial standalone discrimination** relative to M3 on no-macro RFR candidates. Its narrower selection slightly increases the reported conditional accuracy while preserving the count of correct development calls. This is a retrospective ablation, NOT authorization to replace frozen M4 with M3.

**Dependence warning:** The published PRAMV description calls M4 and RFR independent mechanisms. They are independently fitted decision procedures but **not information-disjoint**: both use the 16:00–16:30 and 16:30–17:00 XAU returns. A high agreement frequency cannot be interpreted as two independent evidential votes.

## 4. V2 research hypothesis: orthogonal evidence for RFR reliability (O-RG)

**Hypothesis:** A predictor built from a NON-OVERLAPPING earlier information block and/or a separately governed external price-discovery stream can estimate whether the late first-impulse RFR rule is trustworthy, beyond a correlated M4 vote.

This is a **new, separate challenger**. PRAMV V1 coefficients, calendar veto, windows, decisions, and next unseen scoring are immutable.

### V2A — strictly earlier-path reliability score

- At 17:00, first calculate the unchanged RFR reversal candidate and unchanged no-macro veto.
- Build a separately trained *RFR-success* probability q = P(RFR direction equals the future overnight label | early-path features), rather than another redundant direction vote.
- Use only completed 14:00–16:00 Istanbul XAU 15-minute bars (8 bars): early 2h log return, realized volatility, signed semivariance balance, normalized time-price path area. No feature may contain, directly or through PCA/scaling, ANY observation from 16:00–17:00. The late-window RFR direction is used only as the final output, not a model input.
- Candidate estimator: StandardScaler + L2 LogisticRegression C=1.0; 4 named features; no threshold search or neural/boosting family sweep. Chronologically fit on matured prior eligible targets, requiring at least 80 prior eligible non-macro reversal labels and both classes; otherwise abstain in V2A. PCA is not needed for 8 bars.
- First report probabilistic reliability metrics (Brier vs expanding prior hit-rate, log loss, calibration and AUC), plus score ordering of RFR-correct vs RFR-wrong cases. A new hard action threshold is **not authorized** until reliability improvement is reproduced without post-hoc selection. V2A cannot inherit M4's original nominal significance.

### V2B — external price-discovery residual (data-gated)

- Optional independent source: governed GC/COMEX returns, volume/liquidity, and GC-versus-spot divergence observed and source-ready **before the issue origin**. Use a fixed early observation window rather than searching event minutes.
- A proxy is forbidden if direct GC series is missing; do not replace missing volume/order flow with unlabelled XAU-only information.
- Compare V2B incremental reliability Brier/calibration over V2A on EXACT common source-ready dates. A gain on different row populations is not evidence of incremental information.
- A known US macro release can remain an abstention reason; actual-consensus surprises may only enter after the PIT availability timestamp. Missing event pairs MUST NOT silently mean a verified no-event day.

### V2 evaluation hierarchy / falsification

1. Reproduce V1 before any change; preserve unchanged prospective V1 predictions.
2. Confirm no inadvertent label-feature contamination and model-maturity leakage. Specifically examine the last 16:45–17:00 close vs 17:00 issue timestamp and what the first **executable** bank quote would actually be.
3. Audit V2A source-clock feasibility and origin-safe probability estimation before evaluating accuracy; train on older matured outcomes only.
4. Evaluate chronological reliability predictions independently of any action policy and compare q_t to a historical hit-rate baseline.
5. Evaluate no-filter RFR, frozen PRAMV V1, diagnostic M3 agreement and V2A/V2B at matched date/coverage, including selective risk–coverage curves, UP/DOWN recalls, McNemar common-row rescues/breaks, year/semester splits, and event/DST states.
6. Separate trading economics: 17:00 idealized price is NOT assumed executable after reading a completed 16:45–17:00 bar. Report first obtainable post-ready bank quote, spread, next-day quote, delay-sensitive P&L, and maximum adverse excursion.
7. No best-of-many selection from the opened 2023–2025 archive. 2026 may be called untouched only if its specific outcomes and all design choices truly remained unseen before the locked forecast; otherwise mark retrospective. A genuine prospective stream must log timestamped predictions **before** their 09:00 outcomes.

**Promotion:** None today. Neither the ablation, exploratory p-values, nor the proposed V2A/V2B establish a new accuracy figure. The only confirmed project candidate continues to be frozen PRAMV V1, pending true future validation. DAY 09:00->17:00 remains separate and unsolved.

## 5. Literature crosswalk

- Ma et al. (2025), *Global Finance Journal*, DOI 10.1016/j.gfj.2025.101084: first night half-hour and momentum/reversal/market-state mechanisms; the paper does not validate Istanbul overnight returns.
- Giacomini & White (2006), *Econometrica*, DOI 10.1111/j.1468-0262.2006.00718.x: conditional predictive ability and model-comparison perspective.
- Hansen (2005), *Journal of Business & Economic Statistics*, DOI 10.1198/073500105000000063: data-snooping-aware superior predictive ability.
