# TR09 H3 — Trailing five-session maximum drawdown as a downside-tail indicator (2026-10-23)

Status: PRE-RESULT FROZEN EXPLORATORY PROTOCOL. No trading/model promotion.

## Single new hypothesis
At 09:00 Europe/Istanbul, the **maximum peak-to-subsequent-trough decline** across the latest six eligible daily 09:00 prices (five completed 09→09 session returns) may predict a >=2% XAU/USD loss by the 09:00 quote three eligible sessions later, beyond unconditional rate, two-consecutive-UP streak and prior five-session realized-volatility gate. Directional UP/DOWN is a mandatory secondary metric.

This is a *new 09:00 three-session-tail experiment*; it does not claim novelty of drawdown as a financial concept. No interaction or regime choice selected using 2025/26 outcomes.

## Data, as-of and sample
- Neon project `winter-art-94880101`, read-only `public.gold_research_histdata_xau15m_candidate`, HistData fixed-EST M1→M15. Require `native_minute_bars=15` and the M15 bar starting **08:45 Türkiye**, closing **09:00 Türkiye**. Six eligible 09:00 anchors ending on origin t; exact third future eligible date for label. Source metadata inspected BEFORE results: three disjoint source_id spans 2020–21, 2022–24, 2025–26; all retrieved on 2026-10-08. Historical first publication/vintage **NOT verified**, and the 09:00 closing bar cannot be assumed executable at exactly 09:00 with zero feed latency. This is historical clock-aligned research, NOT certified live PIT or bank-executable inference.
- Eligible calendar: Mon–Fri excluding 2023-01-02, 2023-04-07, 2023-12-25, 2024-01-01, 2024-03-29, 2024-12-25, 2025-01-01, 2025-04-18, 2025-12-25, 2026-01-01, 2026-04-03. **2026-09-25 missing 09:00 is an outage, NOT a holiday.** Any missing current, prior five or third-target exact 09:00 bar excludes that row; never jump over a missing quote. Strict date-based third eligible session, not native H3 D0→D3 daily mean.
- Six prices in chronological order `P0...P5` ending at current origin `P5`. `mdd5=max(0,max_{0<=i<j<=5}(1-Pj/Pi))`. Only current and earlier prices are used. `v5=sqrt(mean((ln(Pj/P(j-1)))^2))` for j=1..5; `two_up=(P5>P4 AND P4>P3)`.
- Target labels `y_up=1[Ptarget>P5]` and `y_tail=1[Ptarget/P5<=0.98]`.
- Train: origin 2023-01-01..2024-12-31 AND target<=2024-12-31 (purge boundary); 2025 full eligible and 2026 Jan–Sep separately score. No training on 2025/26, no 2025/26 feature selection.
- Candidate: `high_mdd=(mdd5>Q75_train(mdd5))`; Q75 from training using PostgreSQL `percentile_cont(0.75)`. For every model separately fit Laplace rates `(events+1)/(N+2)` for UP and tail by gate group. Comparator A unconditional Laplace; B two_up; C high_v5=(v5>Q75_train(v5)) same definition as 2026-10-22. Same complete-row population for ALL arms, and same training cohort for rate estimates. UP decision iff `p_up>=0.5`.
- Mandatory metrics on 2025 and 2026 separately: N, actual UP/DOWN and >=2% tail counts, balanced accuracy (UP and DOWN recall average), UP recall, DOWN recall, UP Brier, tail Brier; tail rates in high vs low mdd, plus comparisons on same rows. Check train sample, thresholds, missing-bar counts, and chronology.
- Reject if the candidate does not improve both years' tail Brier against unconditional and vol comparator **without** a material direction-calibration deterioration; treat small apparent gains as exploratory, not statistical significance. No selection or promotion from repeatedly inspected 2025/2026. 2027 prospective timestamped issue-before-outcome, verified vendor firstprints and real bank bid/ask required.
- Do not change existing project manifest, native H3, production, or 2026-10-21/22 experiments.
