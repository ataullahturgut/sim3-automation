# H1 — Monthly future-information audit, prespecified scope (2026-10-12)

**Pre-registration created before the H1 feature-versus-future-return computation.** This is a chronological *retrospective diagnostic*, NOT an untouched out-of-sample test: prior monthly models have been trained/selected on historical years and opened 2025/26. Never claim H1 historical superiority certifies live predictive performance.

## Source, target and timing
- Read-only Neon `observations`: World Bank CORE5 monthly gold mean; StakTrakr Au/Ag/Pt/Pd daily prices (2010 onward). These archival daily rows and WB monthly rows were ingested in 2026; **origin-time first print and WB origin-average publication are NOT proven**. Any experiment using `WB_avg[p]` in K is an **oracle-alignment retrospective decomposition**, not a deployable contemporaneous signal.
- Canonical monthly target remains next calendar month mean XAU/USD, not price at a trading timestamp.
- `K[p]=WB_avg[p]*(STAK_XAU_last[p]/STAK_XAU_mean[p])`; target `Y*[p+1]=ln(WB_avg[p+1]/K[p])`. Historical diagnostic only.
- All features use **completed origin month or earlier** Stak daily observations. Never use target month features.
- Development/estimation uses dates 2012–2015 for warmup; causal expanding chronological one-month-ahead replay in 2016–2024. 2025/26 shown only as already-inspected descriptive transport if desired; **not** parameter selection.
- No daily model or H3 labels are modified.

## Single frozen, low-capacity screen and controls
- Benchmark: expanding prior residual `Y*` mean (intercept only), minimum **36 prior eligible monthly records** (2012 onward). The historical residual itself depends on lagged WB price availability and is not proven PIT, hence **diagnostic**.
- Gold block B1: completed origin gold monthly last-to-last **log return** `AuMR1_last`.
- Cross-metal block B2: mean of completed origin `Ag/Pt/Pd` monthly last-to-last **log returns** minus AuMR1_last. This is one precommitted relative-strength predictor.
- Joint B12: B1 and B2, no other candidates. For each, expanding `ridge(alpha=10)` with predictors standardized **using only prior fitting months**; intercept unpenalized. No feature lags beyond listed; no CV, tuning, model-family scan, regime selection or calendar slicing.
- **GPR B3** requires a point-in-time comparable methodological vintage for early period; insufficient or changing historical index methodology => **BLOCKED** for primary 2016–2024 screen.
- **Regime B4** requires origin-frozen HMM state vintages. No supplied provenance => **BLOCKED**, never synthesize using a HMM trained on later observations.

## Outcomes and preregistered decision
- Primary: one-step rolling **squared-error** on Y* and improvement against intercept-only; show R2_OS. Secondary: absolute-error and predicted sign correctness.
- Also evaluate **WB actual next-month price** reconstructed as K*exp(predicted Y*), against K*exp(baseline drift); this is retrospective target-price error, not certified operational price.
- Require (1) pooled 2016–2024 R2_OS>0, (2) 3-year block 2016–18 / 2019–21 / 2022–24 positive improvement each, (3) a paired **3-month block bootstrap** 95% CI of squared-loss improvement excluding 0, and (4) multiplicity correction across B1/B2/B12 (Holm) for improvement p-values. If any requirement fails, **NO PROMOTION**. Historical training overlap and source vintage caveats remain regardless of positive score.
- Optional ChHHO 2022–24 residual-score decomposition: separately compare original frozen predictions from PR #86 by exact month and source; **never pool** ChHHO selection-sample improvement as OOS evidence.
- Negative outcome cannot be rescued by altering alpha, time windows, candidate predictors, or testing 2025/26.

## Deliverables
Source-monthly CSV with formula and availability warning, deterministic replay code, machine-readable monthly predictions, per-cohort metrics/uncertainty, result report. Do not alter Neon tables or original monthly forecast/manifest.
