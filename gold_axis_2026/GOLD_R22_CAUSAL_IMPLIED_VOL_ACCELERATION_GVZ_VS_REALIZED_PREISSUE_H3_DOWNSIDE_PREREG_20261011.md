# R22 / pre-outcome experimental authority — external-option GVZ implied-vol acceleration vs recent realized XAU 09TR downside risk
Objective: Improve R20 2026 three-day severe drawdown event R_H3<=-0.015 **risk ranking** without sacrificing annual probabilistic scoring. Inspired by Engle-Manganelli CAViaR 2004 and realized semivariance gold research, new causal information = historical GVZ change and implied-vs-realized gap, in addition to 2025–26 prior gold 5day negative trend. All combinations declared before outcome SQL. 2025/26 already OPENED in R15–R21, no untested validation.
Strict source R20: M15 XAU BID latest completed bar08:30–08:45TR, issue08:45TR, entry09TR spot source BID and ASK, outcome third following Mon–Fri09TR, exclude missing exact target and BIDASK sign mismatch. Use R20 exact same 5 prior complete09TR returns, their gap<=7calendar days, last day's NY GVZ strictly prior date not stale>7. Additional window of 5 and 20 prior available GVZ dates, consecutive gvz trade dates gaps<=7, no same day index. To retain matched equality among 5 compared heads, require all these on all test points. Historical 2020–25 EV vs native2026 Dukascopy M1 complete, no Stak metals.
Risk features:
- `RV = ln(sqrt(sum16 15min BID logreturns^2))`, `GVZ = ln(last prior available GVZ close)`; R18 frozen TWO-var.
- `GVZ5=ln(last GVZ / 5 prior available GVZ close)`, `GVZ20=ln(last GVZ / 20 prior available GVZ close)`, both purely PRE origin and market-GVZ dated.
- `Trend5=sum five prior complete09to09 source logreturns`, `MaxDown5=min past five 09 logreturns`, `Realized5=ln(sqrt(sum last5 09ret²))`, `NegSemi5=(sum negative last5 09ret²)/(sum all last5 09ret²)`.
- `RV_IMPLIED_GAP=GVZ−Realized5`; log scales GVZ annualized implied percentage versus daily realized fraction not directly commensurate; this difference is mathematically unit-sensitive and should be treated as nuisance, REJECT if no improvement, no arbitrarily annualizing after observing scores.
Fixed models all ridge logistic standardized only earlier training rows λ30, intercept unpenalized, 16 Newton iteration:
 BASE=RV,GVZ;
 GVZ_ACCEL=BASE+GVZ5+GVZ20;
 TREND_ACCEL=BASE+Trend5+MaxDown5+GVZ5;
 SEMI_ACCEL=BASE+Trend5+MaxDown5+NegSemi5+GVZ5;
 FULL_ACCEL=BASE+Trend5+MaxDown5+NegSemi5+GVZ5+GVZ20+Realized5.
No up/down direction inference. Compare same test dates/overlaps N, Brier and top/bottom 20% large DOWN event counts, per year2023/24/25/26. Freeze through pre-year H3 maturity: 2023 train 2020–22, 2024 train2020–23, 2025 and 2026 BOTH train2020–24. No training/tune on opened years; any 2026-only improved ranking not enough to promote; 2023 inversion must be reported. No claims independent significance due overlapping H3 and 2025/26 inspected. Strict pre-source checks and 2027 as prospective criterion.
