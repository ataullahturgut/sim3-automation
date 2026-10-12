# GPT-6 P6 — exact RBF Gaussian Process price prediction at preissue XAU/USD spot
**Reject / NO PROMOTION**; prereg `de2b6636`. Original goal direct numerical forecast of **future spot XAU/USD price after issue**, not gold investment in TRY. Correct issue-known pricing anchor: archived EV/Dukascopy 15-minute MID close at 08:30TR (before DAY issue08:45) and16:15TR (before OVN issue16:30), **not the future 09:00 or16:45 spot entry price**. Complete DAY09→16:45, OVN16:45→next09 Mon–Thu, exact source source 2020–25, 2740 windows; 2023–2025 chronological eval1366. Historic source first receipt not proven; 2025 already inspected many times.

Exact GP implementation: RBF kernel fixed unit length, unit diagonal noise after empirical y scale, 4 standardized prior-session features [last1 logret, last5, last22, last RV log], most recent 40 eligible completed historical rows; GP prior local mean; no optimized kernel, no hyperparam search. Controls same-history MEAN40 and RIDGE alpha10, plus strong random-walk last **KNOWN ISSUE price**. Prediction `P_future=P_issue_asof*exp(expected_log_return)`. This is an as-of-aligned **numerical future price forecast**, unlike a return score conditioned on future origin/open prices.

**Absolute future price error per year, USD/oz (smaller better):**
| Window | Year, n | RW known issue spot | Exact GPR | GPR excess error |
|---|---|---:|---:|---:|
| DAY | 2023,256 | **6.8143** | 7.6080 | +0.7937 |
| DAY | 2024,259 | **9.8392** | 10.1289 | +0.2897 |
| DAY | 2025,258 | **17.1523** | 18.1034 | +0.9511 |
| OVN | 2023,198 | **9.1501** | 10.0219 | +0.8718 |
| OVN | 2024,197 | **12.0207** | 13.1436 | +1.1229 |
| OVN | 2025,198 | **24.1284** | 25.5577 | +1.4294 |

2023–24 DEV three-month blocked bootstrap 95% interval of **RW MAE minus GP MAE**:
- DAY [-0.8646,-0.2102] USD per forecast
- OVN [-1.2280,-0.5681] USD per forecast.
Both negative, showing GP **worse** on sampled DEV months. 2025 also worse. Same conclusion for signed log-return RMSE; directional BA 2025 DAY 0.531, OVN 0.467, insufficient and no level skill. The GP prior and kernel are **one fixed tested specification**, not a conclusive rejection of all GPR or nonlinear information channels. **No actual future price model beats RW in this stage.**

### Crucial correction vs P1/P5 conditional price metric
P1 and P5 predict return from future **09:00/16:45 origin** and may reconstruct `P_exit` using realized future origin price; their MAE fields are retrospective **conditional reconstruction metrics, NOT forecasts of a numerical future price as of 08:45/16:30**. Their return classification experiments remain valid causal-window comparisons subject to historical firstprint limits. P6 remedies this by anchoring on issue-15m known price, and is the proper as-of spot PRICE forecast comparator.

All inputs, issues and outputs saved, `tools/gold_gpt6_p6_replay.py` recreates 1366 exact matrix GP probabilities/prices from `GOLD_GPT6_P6_ASOF_PRICE_TARGET_SOURCE.csv`. No original PRs or Neon tables overwritten.
