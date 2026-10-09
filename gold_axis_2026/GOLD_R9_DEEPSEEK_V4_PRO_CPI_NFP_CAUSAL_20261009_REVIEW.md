# Independent DeepSeek V4-Pro R9 original-response referee — hypothesis only

Model text is NOT verified empirical model improvement. 2025/26 already inspected.

**FINAL ANSWER**

**(1) Proposed signal.** A signed pre‑08:45 information channel for the 09:00–17:00 Istanbul gold directional target, defined only on CPI/NFP release dates, based on the *difference between a pre‑release true point‑in‑time nowcast of the US macro surprise and the pre‑release Bloomberg consensus vintage*. Specifically:

\[
S_t = \operatorname{sign}\left(\hat{\varepsilon}_{t|t-h} - \bar{\varepsilon}^{cons}_{t|t-h}\right)
\]

where \(t\) is an 08:30 ET CPI/NFP release date, \(h\) is the lag such that the forecast is formed no later than 08:45 Istanbul (00:45 ET), \(\hat{\varepsilon}_{t|t-h}\) is a nowcast of the actual‑minus‑consensus surprise using only data available at \(t-h\), and \(\bar{\varepsilon}^{cons}_{t|t-h}\) is the consensus expectation as published at \(t-h\). The tradeable implication is:

\[
\operatorname{sign}\left(R^{09:00-17:00}_{XAU,t}\right)
=
-\operatorname{sign}\left(S_t\right)
\]

for non‑zero nowcast‑minus‑consensus gaps, using the well‑documented inverse relation between US macro surprises and gold.

The signal is **not** a pre‑release gold momentum indicator, not a generic classifier, not a calendar volatility dummy, and not a post‑release actual surprise. It is a PIT forecast of the *surprise differential* itself.

**(2) Equation, timestamp, source authority.**

Equation for the core CPI nowcast:

\[
\hat{\pi}^{CPI}_{t|t-h}
=
\hat{\pi}^{CPI}_{t-h|t-h-1}
+
\sum_{j=1}^{J} \beta_j \left[x_{j,t-h} - \hat{x}_{j,t-h|t-h-1}\right]
\]

where \(x_j\) are the currently available high‑frequency PIT components (Cleveland Fed inflation‑nowcast subcomponents, oil price changes, used car wholesale, employment‑cost subindices, etc.). For NFP:

\[
\hat{N}_{t|t-h}
=
\hat{N}_{t-h|t-h-1}
+
\gamma_1 \Delta \text{claims}_{t-h}
+
\gamma_2 \Delta \text{ADP vintage}_{t-h}
+
\gamma_3 \Delta \text{continuing claims}_{t-h}
\]

Exact publication timestamp for the nowcast source: **Cleveland Fed Inflation Nowcasting page updates daily at approximately 16:00 ET on the prior business day before the CPI release**, i.e., by 00:00 Istanbul on the release morning, satisfying the 08:45 Istanbul cutoff with wide margin. For NFP, the nowcast‑style components (initial claims, ADP national employment report) are available no later than 08:15 ET Wednesday for a Friday 08:30 release, i.e., 15:15 Istanbul Wednesday, but the final combination must be formed no later than 08:45 Istanbul Friday.

Consensus vintage: **Bloomberg ECOS consensus as of 08:00 ET on release morning**, accessed via Bloomberg terminal or a licensed vendor providing historical consensus snapshots with first‑publication timestamps.

Source authority: Cleveland Fed (inflation nowcasting methodology as described in Knotek and Zaman, Federal Reserve Bank of Cleveland Working Paper 14‑07, updated methodology), U.S. Bureau of Labor Statistics for actual CPI, U.S. Bureau of Labor Statistics for NFP actual, Bloomberg LP for consensus vintages.

**(3) Actual backtestability today.** The signal **cannot** be fully backtested today with the required scientific rigor. The Cleveland Fed current website provides revised historical nowcast values only, not the exact original first‑print daily time series. The BLS actuals are available, but the *original published vintages* of the Bloomberg consensus are not freely archived and are not proven to be retrievable at the timestamp stated. Bloomberg terminal archives do store historical ECOS prints, but a researcher must currently hold a terminal license and verify that ECOS vintage data are accessible for 2023–2026.

**Minimum low‑cost data and gating feasibility test:**

- Acquire **daily Cleveland Fed inflation nowcast PIT estimates** directly from the Cleveland Fed website once daily at 16:00 ET, starting immediately, for a prospective run. Store the raw page values with exact timestamps. Cost: zero (public page); labor: one automated scraper.
- For NFP, manually record ADP, initial claims, continuing claims as published at their own release times. Cost: zero; labor: one person, one hour per release week.
- For consensus, if no Bloomberg license, use **Trading Economics historical calendar entries** saved once daily at 08:00 ET before release. Cost: free tier limited; full API approximately USD 50–100/month.

**Gating test:** Collect 12 consecutive release dates prospectively (approximately 6 CPI and 6 NFP). Require that the nowcast‑minus‑consensus gap is non‑zero before 08:45 Istanbul in at least 10 of 12 cases. If the gap is zero or data are missing in more than 2 of 12, the channel is rejected.

**(4) Minimalist model and controls on 2023–24 development, 2025–26 inspected.**

**Model:** No regression. On each CPI/NFP release date, if \(S_t eq 0\), forecast:

\[
\hat{Y}_t = -S_t
\]

where \(Y_t = \operatorname{sign}(R^{09:00-17:00}_{XAU,t})\). If \(S_t=0\), issue no forecast for that date.

**Same‑date price‑only control:** Pre‑release 15‑minute gold momentum:

\[
\hat{Y}^{price}_t = \operatorname{sign}\left(R^{07:45-08:00 ET}_{XAU,t}\right)
\]

measured from exchange or high‑quality spot 15‑minute BID/ASK data, using the exact same dates as the nowcast model.

**Constant direction control:** Always forecast DOWN on CPI/NFP dates only:

\[
\hat{Y}^{const}_t = -1
\]

**Scoring.** For each model, compute **balanced accuracy (BA)**, **false DOWN rate**, **Brier score**, and **effect size** (Cohen's \(g\) against 0.5 probability). The 2023–24 development set is used only to verify that the nowcast gap is computable; no parameter is fitted. The 2025 and 2026 dates are used as inspected evaluation. Future issue‑frozen outcomes are required for final scientific validation.

Expected performance under the null (no information): BA near 50%, false DOWN near 50%, Brier near 0.25, effect size near zero. The model is rejected if BA < 55% on either year, or false DOWN > 55%, or Brier improvement over the constant DOWN control is negative.

**(5) 2026 apparent B4 success, class imbalance, after‑1‑minute 50% failure.**

The 2026 source‑native B4/DIR4 apparent success (11/14 whole‑day, 12/14 news→17, 11/14 first‑15) is not evidence of a pre‑release signed predictor. It is consistent with a **class‑imbalance artifact**: on high‑volatility CPI/NFP dates, the unconditional direction is not 50/50. The observed first‑15 gold direction matching the inverse actual surprise 40/50 across 2023–2025 is a *post‑release* relation, not a pre‑release forecast. The B4 first‑15 scores 12/23, 12/24, 12/22 for 2023/24/25 were retrospectively inspected and are not separable from the known calendar volatility effect.

The **after‑1‑minute 50% failure** (surprise sign predicts remaining minute 1→15 only 25/50; first‑minute momentum 26/52) indicates that the surprise information is fully incorporated into price within the first completed minute. Therefore, any model that uses the actual surprise after 08:31 ET has no predictive content for the remaining 14 minutes, let alone for the full 09:00–17:00 Istanbul window. This is the strongest evidence against any trading strategy based on post‑release surprise signs.

The B4 whole‑day 09:00–17:00 apparent success is dominated by the 17:00 close relative to the 09:00 open, not by the first‑minute shock. The pre‑08:45 signal must therefore forecast both the immediate response and the subsequent drift. The nowcast‑minus‑consensus gap is the only defensible pre‑decision candidate.

**(6) Strongest two failure mechanisms and definite reject gate.**

**Failure mechanism 1: Efficient surprise consensus.** The Bloomberg consensus already incorporates the same nowcast inputs that the Cleveland Fed uses; therefore, the gap \(\hat{\varepsilon}_{t|t-h} - \bar{\varepsilon}^{cons}_{t|t-h}\) is near zero in expectation and has no incremental information. If the gap is non‑zero but the market has already priced it into gold before 08:45 Istanbul, the 09:00–17:00 return is noise.

**Failure mechanism 2: Gold reaction is state‑dependent.** The inverse CPI/NFP surprise relation is conditional on monetary policy regime, risk sentiment, and real‑yield curvature. A fixed sign rule \(-\operatorname{sign}(S_t)\) fails when the surprise is small, when the market is pricing a Fed reaction function shift, or when the gold market is dominated by safe‑haven flows on the same day. This is not capturable by a signed gap alone.

**Definite reject gate.** Collect 24 fully prospective CPI/NFP dates using the daily Cleveland Fed nowcast and the Trading Economics consensus, where the gap \(S_t\) is non‑zero and the forecast is issued before 08:45 Istanbul. Compute BA on the full 09:00–17:00 window and on the first‑15 minutes separately. Reject permanently if:

1. BA on full 09:00–17:00 < 55% with a one‑sided binomial \(p>0.10\);
2. OR false DOWN rate > 55%;
3. OR Brier score improvement over the constant DOWN control ≤ 0 on either subperiod;
4. OR first‑15 BA ≤ 52% after excluding zero‑gap dates.

This gate is not threshold‑fitted; it is a fixed pre‑registered criterion.

**Alternative if original macro vintages are irretrievable.** If the Cleveland Fed daily nowcast history cannot be reconstructed as PIT, the only remaining low‑cost pre‑08:45 signed gold predictor is **cross‑market pre‑news positioning in CME GC futures using Commitment of Traders (COT) disaggregated noncommercial net positions as of the last Tuesday before release**, combined with the sign of the prior 30‑day gold trend. The signal is:

\[
S^{COT}_t =
\operatorname{sign}\left(\Delta \text{NonComm Net}_{t-5}
-
\Delta \text{NonComm Net}_{t-30}\right)
\]

and the forecast is \(-\operatorname{sign}(S^{COT}_t)\) if the prior 30‑day gold return is negative, else \(\operatorname{sign}(S^{COT}_t)\). This is a genuinely pre‑decision signal (COT is released Friday 15:30 ET, covering positions through Tuesday, so it is available before the following release), it is implementable with free CFTC data, it is falsifiable, and it does not require any post‑release surprise or PIT consensus. It is distinct from price momentum because it uses positioning flow, not price change. It is the only alternative that meets the challenge's source‑availability and no‑lookahead requirements. All other previously tested alternatives (NQ, ZN, CL, SI, H1, B4 first‑15) are explicitly rejected as failed variants and are not repeated.
