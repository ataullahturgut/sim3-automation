# R44 — original H3 to forecast-eligible real-time clock: May 2026 diagnostic and mixed-frequency bridge

Date: 2026-10-12. Status: RETROSPECTIVE_TIME_ALIGNMENT_ONLY; NO LIVE/ISSUED_AT/PROSPECTIVE CERTIFICATION. This does not overwrite R40/R42/R43, and does not relabel the original H3 source.

## Original forecast and timing
- Historical model origin: source Gold (2026 May StakTrakr `sqld`) average of raw spot polls during a complete **UTC day**; **03TR on source date to 03TR the next date**. `12:00:00` is a synthetic date tag, not observation at 15TR. Source producer MetalPriceAPI through StakTrakr. Source mean is unweighted arithmetic poll mean, not close or a bank executable BID/ASK.
- Old H3 label: `sign(log(A_D3/A_D0))` where D0 is prior `feature_cutoff_date`, D3 third subsequent available source-date record. Issue-date D1 falls AFTER D0; old H3 target D3 is only *two more available source dates after the issue*, not three future sessions. Do not deceptively call original 17/21 an issue→3-forward-day issued score.
- Some inputs: previous-date 16NY Twelve Data hourly cutoff (May = previous-day 23TR). D0 source average completes after May issue-date 03TR, but actual provider publication latency is unknown. Governed H3 08NY deadline = May 15TR, NOT an archived actual `issued_at`, and each as-of input's firstprint/release is not certified. No 09TR first-availability claim. 

## Clock-coherent paired retrospective May results
The unchanged 21 issue-date H3 votes are compared against HistData 15-minute `open_price` on the same vendor at exact 09TR = 06UTC and 15TR =12UTC. For each forecast (i) start = issue-date clock, (ii-a) terminal = **original D3 H3 target-date** same clock OR (ii-b) terminal = **third subsequent Mon-Fri weekday after issue** same clock (new horizon). The second horizon is a different task, not the originally learned label. HistData M15 source is reconstructed historical candidate, NOT a 2026 real-time accessible bank quote.

| Evaluation contract | N | Q95 correct | Q99 correct | SAGE/RuleFlow correct | Always DOWN |
|---|---:|---:|---:|---:|---:|
| old_target_stak_direction | 21 | 17 | 16 | 13 | 13 |
| old_target_09_direction | 21 | 13 | 12 | 9 | 11 |
| old_target_15_direction | 21 | 13 | 12 | 11 | 11 |
| future3_09_direction | 21 | 12 | 13 | 10 | 12 |
| future3_15_direction | 21 | 12 | 13 | 10 | 12 |

On true three-future-weekday horizon at 15TR Q95 12/21=57.14%, Q99 13/21=61.90%, always-DOWN 12/21=57.14%. On issue 15TR→old D3 15TR Q95 13/21=61.90%, versus always-DOWN 11/21=52.38%. These are direct fixed-forecast tests, NOT a successful normalization model, not OOS, not proof of signal availability at either clock. Hour/target comparisons are exploratory, do not select the highest May number as the production hour.

Exact 21-row prices, directions and new target dates: `GOLD_R44_20261012_H3_CLOCK_ALIGNMENT_MAY_2026_ROWS.csv`. Price rows are from Neon `public.gold_research_histdata_xau15m_candidate`, exact 06/12UTC 15-min `open_price` with May summer 3h timezone offset. Original mean/label/votes from `GOLD_R42_20261012_ORIGINAL_H3_SOURCE_TIME_MAY_UTC_AVERAGE_RECONSTRUCTION.csv`; Q99 flips from frozen `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv` by `feature_cutoff_date`, Q95 as recorded. No model refit or new vote created.

## Scientific bridge (NOT YET MODEL-FITTED)
Same-source/same-clock fixed terminal day D3 identity, in logs:

`R_{issue h -> D3 h} = R_{A_D0 -> A_D3} - log(P_issue,h/A_D0) + log(P_D3,h/A_D3)`.

- Term 1: unknown numeric old H3 average-to-average return; the old models give only **its sign**; no single-bit normalization can reconstruct it.
- Term 2: observed origin-average to issued-at/intraday entry, conditionally measurable only if A_D0 was actually published by the issue. No future leakage permitted.
- Term 3: unknown future within-target-day clock offset from daily average; cannot fill from future intraday bars at issue time. Must forecast distribution, not retrospectively substitute actual offset.
- For issue to third future trading day D4, add unknown extension `log(P_D4,h/P_D3,h)`, or explicitly train direct forecast to D4. H3 learned D3 sign does not automatically predict D4.

**Recommended disciplined mechanism**: source-consistent mixed-frequency MIDAS or state-space/Kalman multi-horizon model using strictly as-of H3 frozen votes/probabilities, release-certified source daily aggregates and lagged M15 returns/volatility/session profile to generate a *conditional distribution* (quantiles 10/50/90%) of coherent future clock return. Forecast-eligibility gate `t_eligible=max(all required feature published_at, completed origin-average published_at, model run available_at)`; first available complete M15 bar AFTER t_eligible, not fixed arbitrary 09/15. Include source regime keys (2026 sqld vs 2023-25 LBMA AM) and never conflate. Calibrate on preyear matured labels only; expanding-year walk-forward, purging target-interval overlaps, issuer's as-of/external data firstprints, reject a posteriori threshold/hour selection and unregistered sample exclusions; validate direction & balanced accuracy, Brier for probabilistic, distribution coverage and bid/ask feasible net returns vs fixed baselines on independent untouched period.

Literature: Guay and Maurin (2015) MIDAS temporal disaggregation, https://doi.org/10.1016/j.econmod.2015.05.013 ; Bai, Ghysels and Wright (2013) MIDAS vs Kalman state-space, https://doi.org/10.1080/07474938.2012.690675 ; Sax and Steiner (2013) temporal disaggregation, https://journal.r-project.org/articles/RJ-2013-028/ ; leakage-aware CV methodology https://pmc.ncbi.nlm.nih.gov/articles/PMC9521884/ .

**Handoff:** As of R44, only label clock alignment + May empirical comparison are COMPLETE. Numerical PIT quantile bridge model NOT FITTED; no validated future 3-date alpha; historical issued_at/release gate outstanding. Do not insert future data into any signal, and do not overwrite original retrospective 17/21 H3 score.
