# Actual DeepSeek Pro source feasibility rebuttal (R14B)

Dear Author,

Thank you for the chance to review the revision. The data feasibility objection stands: the proposed 15-minute Ag/Pt/Pd panel and the 2023–2026 live-vintage daily four-metal screen cannot be certified from the cited sources. I therefore require the following minimal, source-certified design as the **only** acceptable R14 test. All statements below are falsifiable from the original Neon DataFrame and Dukascopy M15 gold archives, with availability restrictions stated explicitly.

**Data and vintages**

- Daily Au/Ag/Pt/Pd closes from StakTrakr for 2010-01-04 through **2022-12-30 only**, used strictly as published in the original Neon extraction. No 2023–2026 daily rows are admitted.
- GPR monthly index, **as-of monthly vintage**, i.e., for any trade date \(t\) use the last GPR value whose observation month ended on or before \(t-2\) completed trading days. This is the only certified PIT GPR stream.
- Dukascopy M15 gold bars for H3 (09:00 Turkey, Europe/Istanbul) targets, requiring 16 prior completed M15 bars (04:00–08:45 Turkey, i.e., 01:00–05:45 UTC in winter; state DST handling explicitly).

**Sample and chronology**

- Warmup: 2022-03-01 through 2022-12-30, chronological, used only to initialize expanding-window ridge scaling; no performance reported.
- Training: expanding windows with origins from 2023-01-02 through 2024-12-30; each window uses all daily data up to \(t-2\) and all available GPR monthly vintages up to \(t-2\).
- Freeze: all coefficients fixed on the model estimated with data through 2024-12-30. Apply the frozen model to 2025-01-02 through 2026-12-30 daily, using only pre-2023 daily metal closes and the as-of monthly GPR vintage. No re-estimation in 2025–2026.
- For every trade date, require at least 300 daily training observations after warmup; state the first eligible origin explicitly.

**Features (fixed, continuous, no hindsight thresholds)**

1. Au5 = 5-day log return of Au daily close.
2. Ind5 = equal-weight average 5-day log return of Ag, Pt, Pd daily closes.
3. Divergence = Au5 − Ind5.
4. GPRz×Divergence, where GPRz is the z-score of the as-of monthly GPR level relative to its expanding mean and standard deviation through \(t-2\).

Ridge penalty fixed at \(\lambda=1\) per standardized feature; no hyperparameter search.

**GPR interaction decision**

GPRz multiplies **direction**, not magnitude, of Divergence: the feature is \(GPRz \times \text{sign}(Divergence)\). This avoids overweighting large divergence moves when GPR is merely high. One-line falsification: if this feature’s out-of-sample sign agrees with the in-sample sign in fewer than 50% of 2025–2026 trading days, the mechanism is rejected.

**Targets and forecast comparison**

- H3 09:00 Turkey return = log(H3 09:00 close / 08:45 close) from Dukascopy M15 gold, using 16 completed prior M15 bars.
- Strong null: identical trade dates between (a) the four-feature metal-GPR forecast and (b) a one-feature Au-only daily forecast (Au5) with the same ridge, expanding/freeze chronology, and 09:00 target. Both must use the same 2025–2026 dates and same direction convention.

**Negative controls**

- Permute GPRz × sign(Divergence) across dates within each month 1,000 times; report whether the true out-of-sample direction agreement exceeds the 95th percentile.
- Replace H3 09:00 target with the 04:00–08:45 overnight return; expect no significant direction agreement.

**Required outputs**

- Table of eligible origins after 300-sample constraint, first trade date, number of 2025–2026 trades.
- For the strong null, report sign agreement, mean signed return, and a binomial test; no Sharpe or p-hacking across thresholds.
- State explicitly: “No 2027 out-of-sample promotional claim is made. All 2023–2026 daily metal rows are excluded because source certification ends 2022-12-30 in the Neon archive available as of Sep2026.”

If you cannot produce gold M15 bars for 16 bars before 09:00 Turkey for both 2025 and 2026, say so; the test then collapses to daily-close targets and the GPR mechanism must be reframed accordingly. I cannot accept the prior four-metal 15-minute PCA or the 2023–2026 daily-metal screen as valid.
