# E2/E3 OVN V0 fixed-parameter mechanism pilot — research pre-commit

Created 2026-10-12 **before querying this pilot's forecast-loss outcomes**, but AFTER the 2023–2026 gold data and earlier research outcomes have been repeatedly inspected; therefore this is a **retrospective** mechanistic diagnostic, not a virgin test. The frozen original E2/E3 broad protocol is in PR #87. This is its narrowly scoped *overnight-only* smoke test, not the complete planned DAY+OVN HAR-RV/GVZ/calendar study.

## Dataset and clock
Read-only Neon `gold_research_r73b_ovn1645_xmkt_exactbar_panel_v2`, **only** decision `isodow<=4` with non-null `ovn_mid`, label = sign of log price mid entry 16:45 Turkey → next calendar day 09:00 Turkey. CME factor rows are not used here. 2023–25 EV/Dukascopy and 2026 direct-Dukascopy must be **partitioned as separate source streams**; no training on target-date result and no joining 2025 source to 2026 source. Dates must be chronological; only 60 **prior completed** overnight outcomes (their next-day exits precede the current 16:45 decision) allowed for feature estimation. Zero overnight move omitted for direction.

Historical quote issuance and live bank BID/ASK not independently proven. Quoted execution profit is **not** inferable. DEV 2023–24, opened 2025/26 descriptive only.

## Fixed competing probabilities — no fitting, search or new threshold
Use prior 60 eligible completed OVN returns: `mu60=avg(r)`, `sigma60=stddev_samp(r)`, `up_rate60=avg(r>0)`. Dynamic sigma is `sigma20=stddev_samp(last20 prior OVN returns)`, a proxy for clustering, **not** the as-of M15 HAR-RV model. Minimum 60 prior rows per source. Fail closed on missing/zero sigma. Exactly **one window**.

Use fixed logistic approximation `Phi(z) ≈ 1/(1+exp(-1.702z))` rather than re-tuning. E2:
- `p_dyn = Phi(mu60/sigma20)`
- `p_const = Phi(mu60/sigma60)`
- `p_freq = up_rate60`
- score paired Brier and cross-entropy; DOWN accuracy/BA descriptive. If mu does not change sign, volatility alone cannot change binary direction; improvement must be in **calibration**, not claimed directional switching.

E3 (absolute OVN log-return):
- primary cutoff `c=0.002` (0.20% absolute movement); secondary `c=0.001,0.003` purely sensitivity.
- `q_dyn(c)=2/(1+exp(1.702*c/sigma20))`
- `q_const(c)=2/(1+exp(1.702*c/sigma60))`
- `q_freq(c)=mean(abs(last60 r)>c)`
- Compare Brier/log loss for `I(|r|>c)`. The cost cutoffs are **illustrative hypothetical movement levels**, not bank net-profit claims or execution-feasible no-trade policies.

## Gate and interpretation
E2 must outperform both `p_const` and `p_freq` in DEV mean Brier loss, with **month-block resampling CI for paired loss reduction excluding 0**, and not reverse in 2023 vs 2024. E3 primary 0.2% event must outperform both `q_const` and `q_freq` in DEV Brier with same uncertainty criterion and 2023/24 consistency; secondary cutoffs cannot rescue failed primary. 2025/26 never rescue DEV. Otherwise REJECT / NO PROMOTION. Negative is a valid result.

The 60/20 choice, logistic link, event thresholds, and metric definitions are frozen now. The experiment must not be presented as the full macro-calendar/HAR-RV E2/E3; if positive, proper next study still requires PIT M15 RV, macro schedules, distinct daily window, and true prospective lockbox. Do not modify Neon, current manifests, champions or production code.
