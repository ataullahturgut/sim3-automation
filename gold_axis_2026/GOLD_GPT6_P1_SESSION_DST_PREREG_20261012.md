# GPT-6 P1 — session/DST conditional XAU/USD forward-return baseline — PRE-REGISTERED
Timestamp: 2026-10-12. Created **before** P1 target returns fetched/calculated. Independent of Claude's research. Governance from open PR #93; not modifying canonical.

## Hypothesis and clock
US exchange DST calendar may shift directional base rates on fixed Istanbul DAY09:00→16:45 (issue08:45 TRT), and OVN16:45→next09:00 Mon–Thu (issue16:30 TRT). Compare **pure calendar-conditioned sign probabilities** against non-DST unconditional, **separately per window type**. Calendar attributes are known before each issue. Do not introduce feature search or fitted daily H3 model.

Daily M15 source: Neon `gold_research_evduka_xau15m_bidask_candidate`, 2020–25 archive. Keep vendor separate; historical receipt timestamps not proven. Decision price is future 09:00 or 16:45 mid *open* (never a feature at 08:45/16:30), target mid *close* of last bar ending at 16:45/09:00, respectively. DAY: 31 contiguous 15m bars; OVN: 61 observed bars with one 75min maintenance gap. Invalid BID/ASK, DST crossovers, date gaps: exclude, never interpolate. `r=ln(mid_exit/mid_entry)`; y=1 if r>0; no unduly convenient prior-day native-average label. US DST based on `America/New_York` at window **issue** timestamp.
Warm-up 2020–2022, sequential DEV 2023–2024. 2025 transported prediction uses coefficients/priors **frozen at 2024-12**, and is already-opened retrospective. 2026 different vendor/m1 matching not established => BLOCKED.

## Fixed challenger + references
- `BASE`: smoothed all-prior same-session UP rate `(nUP+2)/(n+4)`; `DST`: same window-type + US DST-state rate with same Beta(2,2) pseudo-counts. One (binary) feature, no weekday/rules/threshold scan.
- Corresponding level-return predictions: historical all-prior mean log-return BASE, DST-state conditional mean log-return DST (known prior only).
- Probabilistic primary: per-row Brier and logloss; secondary accuracy (threshold .5), BA, recall up/down, absolute price forecast error, RMSE log-return. Always-UP and RW zero return reported without Brier overconfidence.
- Success: DST beats BASE in Brier and logloss **in BOTH 2023 and 2024**, and beats in already-viewed 2025 without parameter reoptimization. Paired 3-month bootstrap 95% CI of Brier(BASE minus DST) excludes 0 on 2023–24. Correct multiple tests for DAY/OVN (Holm), no spurious annual small-N cut. Otherwise BASELINE_ONLY.
- This P1 investigates calendar base rates, **not** event reaction, HAR RV or opening source lead-lag. Existence of some conditional effect is not a verified live edge.
- Save source rows, SQL, deterministic replay and scientific result separately. Do not alter original manifests, vintage data or buy trading products.
