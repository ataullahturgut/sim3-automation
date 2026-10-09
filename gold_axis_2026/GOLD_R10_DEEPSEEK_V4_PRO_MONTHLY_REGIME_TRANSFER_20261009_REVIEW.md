# DeepSeek V4 Pro R10 monthly-to-session expert referee

UNTRUSTED hypotheses, no actual market experiment by DeepSeek.

**1. Empirical and mechanistic explanation for monthly price-model success**

The ChHHO monthly XAU level model exploits three mutually reinforcing statistical properties of *monthly average* gold prices, none of which transfers directly to signed intraday bank-window direction.

First, monthly averaging acts as a low-pass filter that suppresses high-frequency shock noise (CPI, geopolitics, order-flow bursts). The resulting series is dominated by slow-moving log-price level inertia — a near-unit-root process where the previous month's average is an extremely strong predictor of the next month's average. The relative MAE of 0.804 versus a prior-month random walk confirms that most apparent "skill" is trend persistence, not causal discovery. Second, the eight Au/Ag/Pt/Pd features with MR (momentum/return) and GPR-conditioned VW (volatility-weighted) summaries capture cross-metal *co-movement* — a common-factor structure where all four precious metals share a slow common trend plus idiosyncratic deviations. This adds modest complementary information beyond gold alone, but the 0.72% improvement over the four-input gold-silver ablation is marginal relative to N=33 sampling error. Third, the 13-variable HMM identifies persistent *market states* (drawdown/stress, quiet, accumulation) with 89–93% self-persistence. However, the 88.9% walk-forward "agreement" is reference-label matching, not gold directional accuracy — and the state for month *t* is unknown until month *t* ends. No monthly regime label is available mid-month, so no intramonth trade can condition on it without leakage.

Critically, 69.7% monthly direction (23/33) has a binomial two-sided p ≈ 0.08 against 50%, and with only N=33 the 95% confidence interval spans roughly 51–84%. The DEV success does not imply signed 09:00→17:00 or overnight bank-window hit rates above 60%; intraday signed returns have near-zero autocorrelation with monthly drift, and the same-method H1 2013–2021 test (relative MAE 1.90) plus 2025/26 volatile episodes demonstrates regime fragility and optimizer ill-conditioning. The monthly model is a smoothed-level persistence engine with cross-metal covariation — not a signed short-horizon predictor.

**2. Strongest testable hierarchical month-prior/session-residual mechanism**

Propose ONE mechanism: **Hierarchical signed drift-residual decomposition** using only *last-completed-month* slow drift as a prior, with session innovations orthogonalized.

Clock cuts (TR time):  
- Monthly prior computation: at 08:45 on first trading day after a completed calendar month *M*, compute the signed monthly log-return from month *M−1* end to month *M* end using exact bid-ask midpoints:  
  \(s_M = \text{sign}(p_{\text{end},M}/p_{\text{end},M-1} - 1)\).  
- Session residual: at the same 08:45, compute gold's previous two completed sessions' (09→17) signed returns \(r_{t-1}, r_{t-2}\). The prior is active for all sessions within month *M+1*.

Model (minimal degrees of freedom: 2 coefficients, sign-only rule):  
Directional signal for session *t* in month *M+1*:  
\[
\text{signal}_t = \text{sign}\left(\beta_1 s_M + \beta_2 (r_{t-1} - \bar{r}_{\text{month}})\right)
\]
where \(\bar{r}_{\text{month}}\) is the mean 09→17 return over the last completed month. Only \(\beta_1 \in \{0,1\}\) (month-prior on/off) and \(\beta_2 \in \{0,1\}\) (session residual on/off) are evaluated — not fit continuously. This prevents the "adapted to 2026" trap. Data required: metal daily bid-ask midpoints at 08:45 and 17:00 TR, already available; no 15-minute intraday VW-MIDAS needed. This mechanism is falsifiable: if the monthly drift truly carries a persistent directional bias into the next month's bank sessions, signal should outperform price-only B4/DIR4 in 2023/24 DEV and survive the pre-registered 2025/26 stress. If it fails in 2023/24, the hierarchy is wrong.

**3. Ablation and negative control**

Ablate the proposal against three controls on identical dates:
- **Price-only B4/DIR4** (existing frozen model): no monthly prior, no residual term.
- **MONTHLY_PRIOR_ONLY**: \(\beta_1=1, \beta_2=0\) — sign of last completed month's return only.
- **SESSION_RESIDUAL_ONLY**: \(\beta_1=0, \beta_2=1\) — fast session reversal/momentum only.

Negative controls:
- **Month-shuffle null**: randomly permute the monthly prior signs relative to sessions, recompute BA/DOWN recall 1000 times to get null distribution. The real prior must exceed 95th percentile to reject.
- **Time-frozen qualification**: fit nothing; pre-register 2023/24 as DEV (N≈24 months), open 2025 (N≈12) as first stress, inspect 2026 only after completion as second stress. The proposed signal must improve 2023/24 DEV BA and recall versus price-only, then retain ≥50% of DEV improvement in 2025 — otherwise REJECT. 2026 inspection cannot be used to modify \(\beta_1,\beta_2\).
- **Rescue/break paired test**: on sessions where B4 predicts one direction but the hierarchical signal disagrees, measure whether following the proposed signal rescues losing days or breaks winning days. Report calibrated BA, UP/DOWN recall separately for each cohort.

If the monthly prior provides real slow-drift information, MONTHLY_PRIOR_ONLY should beat price-only in 2023/24 and 2025; if only 2026, it is leakage/fitting.

**4. Precise source gate for each metal/GPR/HMM original monthly vintage**

- **ChHHO 8-feature monthly inputs (Au, Ag, Pt, Pd; MR and GPR-VW)**: origin — broker daily bid-ask midpoints aggregated to monthly averages at month-end. First-print vintage: available only after month *M* closes. No postissue month-end revisions — each month's value is fixed on first business day of *M+1*. Source feasibility TODAY: YES, provided broker daily midpoint series is archived without adjustment.
- **13-variable HMM monthly features**: gold 1m/3m momentum, level gap, vol; other-metals dispersion; GVZ; CFTC MM net/OI; USD; nominal/real 10Y Treasury; GLD/IAU ETF flows. CFTC COT is published weekly with T+3 lag; for completed month *M*, final weekly COT of that month is available by day 3–4 of *M+1*. HMM state for *M* is therefore available approximately day 4 of *M+1*, NOT day 1. All other series are month-end vintages. Source feasibility TODAY: PARTIAL — CFTC timing gap means HMM state cannot be used at the 08:45 day-1 cut; only monthly slow-price prior from metal midpoints is immediately available.
- **GPR-conditioned VW summaries**: derived from daily GPR index (Caldara-Iacoviello) and daily returns; monthly summary available after month-end. Source feasibility TODAY: YES for historical monthly summary via public GPR download, but real-time monthly aggregation requires daily GPR access.

No postissue month-end values are used; all features are frozen as-of month-end. The proposed mechanism uses only metal midpoints and session returns — fully available at 08:45 day 1.

**5. Strongest objection, hard stop, and independent prospective qualification**

**Strongest objection**: The monthly model's apparent skill is dominated by level persistence, not signed forecast. The proposed month-prior/session-residual hierarchy assumes slow drift persists into next-month *signed* bank windows — but the monthly drift itself is the same persistence that failed in H1 2013–2021 (relative MAE 1.90) and deteriorated in 2025/26. If slow drift does not survive as a signed prior at session horizon, the hierarchical decomposition is empty.

**Hard stop rule**: If MONTHLY_PRIOR_ONLY does not exceed price-only B4/DIR4 BA or UP recall in 2023/24 (pre-registered DEV) OR does not retain ≥50% of that improvement in 2025 (first stress), the mechanism is REJECTED and no further monthly-prior transfer is attempted. No coefficient re-fitting after 2026 inspection; no additional features; no ensemble substitution.

**Independent prospective qualification**: PASS_TO_TEST only if the model is evaluated on 2027 sessions with no parameter changes and no look-ahead, using the exact clock cuts and sign rule stated. Both original bank windows (09→17 issued 08:45, OVN issued 16:45) must be reported separately. If 2026 inspection shows improvement but 2027 prospective fails, the result is NO_PROMOTION.

**Verdict**: **DATA_GATE_FIRST** — immediately executable with approved metal midpoint data only for the month-prior/session-residual component; HMM state cannot enter day-1 timing due CFTC lag. The proposed mechanism is minimal (2 binary coefficients), source-safe, and falsifiable. No invented test metrics. No claim of >70% direction is warranted.
