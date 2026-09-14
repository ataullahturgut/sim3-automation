# Gold Control — 2025 Research Model Revival Audit

**Status:** research evidence only; no production/runtime promotion.  
**Authority:** subordinate to `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`.  
**Audit date:** 2026-09-14.  

## Governance

The revived/recovered channels below are historical research channels. Fixed-horizon 1D/3D/H20 direction is not the current GC-BREAK primary target. No model was promoted, flat-voted, or post-score tuned. Where original identity could not be proven, a separately named `*_RECONSTRUCTION_V1` identity was used. 2025 is retrospective challenge evidence, not fresh blind OOS.

## Revival status

| Channel | Identity status | 2025 status | Key 2025 diagnostic | Evidence |
|---|---|---|---|---|
| GOLD_RIDGE | Reconstruction V1 | PASS | accuracy ~0.5085; balanced accuracy ~0.5044; Brier ~0.2516 | separately named reconstruction |
| SESSION_RM_RIDGE | Reconstruction V1 | PASS | n=195; accuracy=0.553846; BA=0.535176; Brier=0.260397; log-loss=0.728318 | workflow run 34886955836; artifact 10364844586 |
| PRICE_DISCOVERY_HGB | Reconstruction V1 | PASS | n=203; accuracy=0.536946; BA=0.515106; Brier=0.255334; log-loss=0.705305 | workflow run 34887295177; artifact 10365830531 |
| MACRO_CROSS_RIDGE | Reconstruction V1 | PASS | n=203; accuracy=0.571429; BA=0.506510; Brier=0.248965; log-loss=0.693080; 189/204 UP | workflow run 34887740879; artifact 10366130731 |
| FULL_HGB | Reconstruction V1 recovered blocks | PASS | n=203; accuracy=0.581281; BA=0.551173; Brier=0.245565; log-loss=0.684441; 173/204 UP | workflow run 34889055032; artifact 10369002310 |
| LOCAL_ERRMEM | **Original historical V1.64 identity recovered** | EXECUTED / FROZEN GATES FAILED | all 1D/3D parent combinations failed frozen success gates; LOCAL_ERRMEM generally worsened Brier versus STATIC | historical run 34834883769; artifact 10316352769 |
| H20 / LEGACY_RTQ_R126 | **Original historical V1.56 RTQ_R126 / STRATEGIC_H20 identity recovered** | EXECUTED | 2025 H20 median: n=241, accuracy=0.742739, BA=0.499433; selective: n=142, coverage=0.589212, accuracy=0.774648, BA=0.500000, all 142 signals UP | historical run 34706090252; artifact 10302375334 |

## LOCAL_ERRMEM conclusion

The exact V1.64 contract and run evidence were recovered. `LOCAL_ERRMEM` is an adaptive residual/error-memory overlay over five parent channels, with frozen causal maturity rules. On 2025 it failed every frozen success gate. It must not be rescued by changing thresholds, memory length, residual scale, or parent selection after seeing 2025.

## H20 / LEGACY_RTQ_R126 identity conclusion

The mapping is evidence-backed, not inferred from the name alone. The canonical manifest lists research-only `H20 / LEGACY_RTQ_R126`. The exact V1.56 frozen contract defines horizon `STRATEGIC_H20 = 20` and model `RTQ_R126` as the primary real-time rolling quantile model with window 126. Therefore the historical source identity underlying the manifest label is recovered as **V1.56 `STRATEGIC_H20` + `RTQ_R126`**.

Frozen RTQ_R126 configuration: rolling 126 mature targets; q25/q50/q75 HistGradientBoostingRegressor; depth 2; 80 iterations; learning rate 0.05; L2=1; seed 20260912. Quantiles are rearranged monotonically. Selective direction is UP only when q25>0, DOWN only when q75<0, otherwise NO_SIGNAL.

The 2025 H20 headline selective accuracy of 77.46% is not sufficient evidence of symmetric direction skill: every selective 2025 signal was UP and selective balanced accuracy was exactly 0.50. The validation period itself had an H20 actual-UP rate of 81.33%. The frozen selective research-interest gate nevertheless passed because that historical gate checked selective accuracy and coverage rather than balanced accuracy. This must be carried forward as a limitation, not reinterpreted as a production winner.

## Next research use

The next step is not model retuning or ensemble construction. Each recovered/reconstructed channel should be evaluated separately against the frozen 2025 economic-opportunity swing inventory using its native role/clock. Outputs should retain `availability`, response date/state, lag, remaining move, role-specific outcome, evidence age, and missing reason. H20 must be treated as a 20-governed-origin strategic quantile context, not as a daily early-turn trigger.
