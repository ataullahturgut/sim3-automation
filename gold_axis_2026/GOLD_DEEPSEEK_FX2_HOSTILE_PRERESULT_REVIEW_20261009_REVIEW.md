# DeepSeek independent pre-result critique of original EURUSD/USDJPY dual confirmation

**External LLM text, not market evidence.**

**Referee report — EURUSD+USDJPY USD-pressure overlay (pre-score). Verdict: BLOCK for promotion; GO_FOR_EXPLORATION only as a labelled cross-asset ablation.**

**1. Confounding is intrinsic, not incidental.** USDJPY embeds (i) risk-off yen funding demand and (ii) the US-JPY rate differential plus Treasury term premium — the same JGB-UST/yield channel that mechanically drives XAU through real rates. So `-sign(Δlog USDJPY)` is *not* a clean "USD pressure" instrument; it is a composite of dollar and rates/risk-aversion. EURUSD is also rates-mediated (ECB-Fed differential). Consequently the two legs are **not independent information**: both are largely the same broad USD factor, plus shared macro news. The "double agreement" filter therefore selects high-|USD-factor| hours, i.e. a *volatility/regime* conditioning, not two orthogonal confirmations. Author's own corpus already contains a broad USD/FX channel (PRAMV/CAVS proposal), so the marginal novelty claim is weak. Soybilgen & Sobti-type regime findings do not license exact Istanbul clock returns.

**2. Clock/publication audit.** H1 start-labels: pre-DAY features are bar starts local 06:00 and 07:00 (UTC 03:00/04:00 given TRT=UTC+3); closes 07:00/08:00 local, i.e. last FX close 08:00 = 45 min before 08:45 issue and 60 min before 09:00 target. Pre-OVN: starts local 14:00/15:00, closes 16:00, 45 min before 16:45 issue. This is sound *only* if the provider's "start-labelled" H1 bar truly closes at start+1h and is not revised. Twelve Data retrieved *today* is NOT PIT vintage; do not claim 2023 archival authenticity. Add explicit assert `parse_utc(open_time)` and reject bars not exactly 1h apart across the pair window. The 15/45-min buffer is conservative and acceptable, but gaps/holidays and missing-bar substitution must hard-abstain, not fill.

**3. Source/target vintage.** Legacy LIT vs governed EV DUKA: 5/589 sign disagreements (0.849%) with >0.9% abs-return divergence is **material at the sign boundary**, exactly where FX2 acts. Any "rescue/break" near ±0.9% will be misattributed. Treat all LIT-scored FX results as *related-but-non-canonical*; no promotion without canonical join.

**4. Selection vs coverage.** FX2 selective coverage will overstate BA. Mandatory reporting must separate (a) paired selective N/coverage/DOWN recall/DOWN precision among acted and (b) FX-OVERLAY full-coverage BA. A paired full-coverage **Brier** is admissible **only** if calibrated probabilities exist for both heads under the same target vintage — otherwise report Brier as *unavailable*, not fabricated. DOWN false-alarm count and FP-rate among acted DOWN calls are mandatory, not optional.

**5. Novelty vs prior.** CME3-K25, ZN-VPT2, PRAMV, CAVS all invoke cross-asset/rates/USD structure. FX2 adds *intraday FX-signed hours*; the genuinely new element is the exact-clock pair-agreement filter, not a new market channel. State this explicitly to avoid over-claiming.

**6. Negative control (exact).** Same-date, same clock, same abstention rule using **lag-shifted FX**: substitute `sign(Δlog FX at T-1h−T-2h)` for the FX2 decision. If FX2's selective BA does not exceed this shifted control by a small pre-set margin with paired McNemar, the "leadership" narrative is dead (coincident common-shock).

**7. Falsifiable sign-stability test.** Freeze per-half-year `sign(HitRate_FX2 − 0.5)` for 2023H*, 2024H*, and inspected-2025 halves. Require **identical sign across all three vintages** and monotone non-degradation in 2025; any single sign flip ⇒ FAIL, regardless of pooled 2025 lift.

**Verdict: BLOCK** the promotion pathway (no champion, no calibration claim, no canonical-vintage score). **GO_FOR_EXPLORATION** strictly as an ablation with the shifted-FX control, both selective and full-coverage reporting, DOWN false-alarm accounting, and explicit "same broad USD factor / rates-confounded" caveat in the preregistration. No score given.
