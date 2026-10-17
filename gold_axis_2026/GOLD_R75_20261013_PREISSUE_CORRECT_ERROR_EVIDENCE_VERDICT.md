# R75 — Measured ex-ante discriminability of correct and incorrect gold direction signals (2026-10-13)

**Status: COMPLETED, RESEARCH NEGATIVE, NO NEW ROUTER PROMOTED.**
Evidence: strictly original R67 same-clock `GOLD_R67_20261012_H3_AS_DAY_AND_OVN_CONDITIONER_2023_2026_ROWS.csv`, prereg commit `e218e9ca`, script `tools/gold_r75_preissue_correctness_mechanisms.py`, [CI completed run 38379993507](https://github.com/ataullahturgut/sim3-automation/actions/runs/38379993507), artifact `r75-preissue-direction-gates` (ID 11803202216, summary JSON, full 72-row gate table CSV, markdown). Original R67 and other authority remain unchanged.

## Research question and cohort
Can pre-issue **confidence, expert agreement, or momentum context** distinguish R67 *future post-origin* direction hits from errors? Two target identities: DAY 09→16:45 Türkiye, OVN16:45→next-calendar09; no Friday weekend relabel. DEV feature cut thresholds frozen on 2023–24, retrospective 2025 and2026 untouched by thresholds, but the years have already been broadly inspected and are not new holdouts. The original R67 logistic is unchanged.

## Baselines matched on yearly native coverage
| target | 2023 |2024 | 2025 opened |2026 opened |
|---|---:|---:|---:|---:|
| DAY original R67 | 65/123 =52.8% |140/240=58.3%|110/248=44.4%|100/190=52.6%|
| OVN original R67 |52/91=57.1%|104/189=55.0%|92/196=46.9%|74/150=49.3%|
Note 2023 HistData vendor source has incomplete 09/OVN coverage; older 3d H3 daily-average label and CIG 74.4% are not these executable-clock outcome targets.

## Strongest *apparent* DEV mechanism: original forecast confidence margin
Use only preorigin `abs(prob-.5)` with top DEV quartile threshold: DAY `>=0.0607582`, OVN `>=0.0739008`.
| target | 2023 | 2024 | 2025 opened |2026 opened|
|---|---:|---:|---:|---:|
| DAY top-quarter confident |18/30=60.0%|39/61=63.9%|38/84=45.2%|50/93=53.8%|
| OVN top-quarter confident |13/17=76.5%|34/53=64.2%|33/67=49.3%|39/84=46.4%|

OVN top-confidence DEV=47/70=67.1%, opened=72/151=47.7%; drop ≈19.5pp. DAY confident opened falls short of same-selected-row always-UP (2025 51/84=60.7%, 2026 54/93=58.1%). So no economically useful exante selective-direction superiority.

Other eight predeclared confidence half, H3 agreement, prior DAY/OVN sign agreement/reversal, calm prior OVN and combination gates were executed in both target clocks, exact metric table in CI artifact. **0 of 9 gates** meets predeclared cross-year standards in either clock. A few subset results are above one weak frozen class benchmark but fall below the on-row UP base rate and/or fail one of 2023/24 years.

## Regime / calibration diagnostic — NOT sufficient causal proof
|Target|Year|Correctness confidence AUROC (higher is better)|Median absolute prior overnight return|Median absolute actual next-window return (OUTCOME ONLY)|
|---|---:|---:|---:|---:|
|OVN|2023|0.627|0.292%|0.331%|
|OVN|2024|0.583|0.343%|0.285%|
|OVN|2025|0.532|0.510%|0.527%|
|OVN|2026|0.475|0.720%|0.774%|
|DAY|2023|0.542|0.323%|0.237%|
|DAY|2024|0.527|0.340%|0.330%|
|DAY|2025|0.508|0.517%|0.311%|
|DAY|2026|0.478|0.709%|0.409%|

Observed historical high-confidence association collapses as prior overnight movement/realized night risk grows. AUROC below .5 in 2026 must NOT be sold as a profitable inverse rule or proof of a causal volatility gate. Already opened 2025/26 cannot retune thresholds.

## Separate strongest old CIG-D1 historical-label diagnostic
From pinned `GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv` exact 125 consensus rows:
- 93/125 correct on OLD DAILY-REFERENCE date label, but only 59/125 correct on exact post-08:15 NY→16:00 NY direction.
- Contingency old-correct/post-correct **51**, old-correct/post-wrong **42**, old-wrong/post-correct **8**, old-wrong/post-wrong **24**. Only **51 of original 93** nominal successes remain post-issue correct. This validates target mismatch, not a hidden still-executable 74% direction edge.
- CIG clock differs from R67 TR session and is not pooled in R75.

## Data / protocol caveats
Source R67 uses HistData and 2023 sparsity; historical exact H3 issuance timestamps, provider first-print PIT and actual user bank bid/ask unavailable. R67 model may have DEV fitted-score optimism; DEV is NOT pristine test. 2025–26 repeatedly inspected, no new untouched test. Realized return magnitude is permitted only for DIAGNOSTIC classification, never as a predecision selection criterion. Moving-block paired intervals vs frozen DEV majority class included in CI artifact; class-switching and year heterogeneity prevent any robust promotion.

**Verdict:** found a plausible source of unstable apparent past successes (confidence calibration and volatility/regime shift), **not a stable prospective discriminator of winning trades**. Do not launch a new confidence gate or daily sign flip. Next materially distinct test would require independently timestamped information-arrival predictors and a new forward lockbox, not post-hoc threshold search.
