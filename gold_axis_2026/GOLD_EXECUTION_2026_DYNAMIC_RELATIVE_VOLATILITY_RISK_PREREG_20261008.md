# Pre-registration: causal 63-night dynamic-volatility reference and bounded correction
Date 2026-10-08. Before running this addendum after fixed historical risk forecast experiment.

Prior (frozen) log-MAE absolute return Ridge from historical 2020–25 DID have apparent 2025 +2.30% / 2026 +8.3-9.6% overall absolute MAE improvement versus constant historical median. Yet 2026 fixed 2025 risk alarm marked 100% of 2026 nights (no discrimination). Do not promote old alarm.

No feature selection or fitting on future observations. Predeclare **ONE** as-of adaptive calibration, no optimization based on 2025/2026:
- each Turkey OVN prediction has frozen Ridge forecast F_t of |next session log-return| generated at 17:00, realized absolute return A_t only after the following 09:00.
- For each issue t, compute lagged last **63 matured** pairs (F_i,A_i) with date_i<date_t. Estimate normalized log residual median m=median(log((A_i+1e-5)/(F_i+1e-5))). Set shrunk log adjustment w*m, w=63/(63+32) where 63 is maximum lookback, or n/(n+32) for fewer matured records; clip adjustment within log(0.5)..log(2); calibrated forecast C_t=F_t*exp(clipped adjustment). This is one-sided in time.
- as-of warning threshold is **75th percentile of prior 63 calibrated forecast magnitudes**, provided >=20 preceding qualified cases; else ABSTAIN risk alarm. Alert C_t>=quantile. This is *relative high volatility*, not a guarantee of DOWN price direction.
- evaluate 2025 and 2026 real-year MAE of C_t against F_t and constant median, 2023/24 retrospective DEV, the fraction warned, severe negative tail capture and precision vs prevalences, and paired same-date absolute-error wins/losses. If warning has capture no better than coverage in 2026, reject. Source mirror (97 OVN) and native first-party 2026 (72 OVN) distinct. Report no investment PnL or certainty claims; 2026 already inspected.

No risk model newly fitted to 2026 outcomes. Lagged 2026 matured past-session outcomes MAY adjust risk scale in future 2026 sessions exactly as prospective online operation would. Do not label this frozen 2026 study; it is a retrospective causal prequential correction. Implementation creates aggregate-only artifacts; private date-level forecasts remain private.
