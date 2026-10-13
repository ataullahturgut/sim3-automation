# R79 2026-10-13 — Started move after-observation continuation/reversal, pilot run

Status: COMPLETED historical pilot / ALL PREDECLARED GATES FAIL / no short gold-cash strategy endorsed. Research PR #116, pre-data prereg commit `f8fed601`, data commit `327926fb`, code commit `59ef2208`, [CI success](https://github.com/ataullahturgut/sim3-automation/actions/runs/38385519497), artifact `r79-confirmed-start-continuation-reversal` (ID11805441715, 2023–26 row probabilities and summary JSON). No writes to Neon, user bank trades or main authority.

**Core insight:** Already moving gold can trigger a new forecast origin. Do **NOT** have to forecast before first movement. But *movement started* is not an empirical proof that it will persist, so naive "sell after first red candle" and "buy after first green candle" are disallowed.

## Locked trigger and target
XAU 2020–25 EV Dukascopy derived 15m BID+ASK midpoint, 2026 native Dukascopy M1 matched15. Daily 09:00 midpoint OPEN. The FIRST *completed 15m bar* (not bar high, not future intrabar preview) crossing fixed abs(log(close/09open))>=0.0075 (75bp) and completing between10:00 and16:00 Turkey. Require full 31 bar 09:00–16:30 daily sequence, 16 pre09 completed bars, past4 complete trigger bars, no early (<10TR) threshold-touch included, no weekend. One event maximum/day. Entry/reference quote at completed signal bar **CLOSE**, future target 16:30 same-day bar **OPEN**. Outcome is sign of log(future price / trigger close) aligned to triggering move. Other binary outcomes: residual same-direction >=50bp, reversal >=50bp.
No bank contemporaneous ASK/BID or actual first receipt: midprice signal is retrospective research, not actual trade. Training 2023 from2020–22, 2024 from2020–23, 2025+26 both fixed from2020–24. Logistic regularized C0.2 uses preissue sign/magnitude, minutes remaining, prior four bars and early05→09 volatility and directional return; rolling60 previous matured conditional probability baseline.

## Actual first 75bp crossing and remaining same-day path
| Year | N first movement starts | Still in onset direction at16:30 | Reversed by16:30 | Model continuation AUC |
|---|---:|---:|---:|---:|
|2023|29|16|13|.447|
|2024|37|15|22|.642|
|2025|63|37|26|.612|
|2026 Jan–Oct07|73|34|39|**.438**|

2026 by onset sign: first DOWN n31, still dropping n14 and rebounded n17; first UP n42, still rising n20 and gave back n22. **At least 0.5% *additional residual* movement** after first crossing: DOWN first continued >=.5% n8, DOWN first rebounded >=.5% n3, UP first further rise >=.5% n5, UP first fell back >=.5% n3. These are counterfactual end16:30 labels; not model forecasts.

## Predictive test vs matured rolling60
|Year|Continuation logistic Brier|matured rolling60 Brier|gain baseline minus model|continuation AUC|
|---|---:|---:|---:|---:|
|2023|.27055|.25570|-.01486|.447|
|2024|.24574|.25240|+.00665|.642|
|2025|.23751|.25869|+.02118|.612|
|2026|.27778|.25964|-.01814|.438|
Reversal >=50bp AUC 2023 .384 /2024 .744 /2025 .636 /2026 **.403**; large-onset-continued >=50bp AUC 2023 .107 (1 event only) /2024 .629 /2025 .662 /2026 .617 (13 events). All three predeclared paired DEV 5day block CI include zero: CONT [-.03144,+.02322], REV50 [-.01419,+.01774], CONT50 [-.00511,+.00831]. **0/3 targets satisfy all-year gain + confidence CI gate.** Do not reverse signal or chase 2026 threshold changes.

## Next research direction
A monthly-gold/cash core with two conditional event states: 1) starts DOWN while monthly UP -> compute conditional probability of further adverse drop AFTER observed onset before 16:30/next09; do not auto sell on onset. 2) starts UP while monthly DOWN -> compute conditional probability of further rally AFTER onset; do not auto buy on onset. Need 3) independent risk-of-stabilization for reentry and 4) bank ASK/BID spread and response times. Avoid treating future up/down after signal as origin-known features. Retrospective monthly-trend predictions for 2023–26 have not been verified as recorded at prior month end, so cannot run a valid combined monthly/core overlay PnL today.

**Especially relevant to user's Fed question:** R78 had ONLY prior-hours NQ,ZN,CL and public Fed meeting date, missing the actual *post-release first reaction* in live EUR/US trading sessions. A different event-trigger model should use verified realtime 15m changes **after** actual CPI/NFP release (roughly US 08:30 ET) in NQ, bond and USD, plus spot confirmation, and judge continuation from a valid **post-release** bank quote. The FOMC statement usually arrives after user's 17TR normal-spread window, so route FOMC to next-day09 decision rather than assumed pre-release reaction. This requires source availability/reception timestamps; current UTC01-05 CME data cannot provide release aftermath, and R78 negative morning result does not prove these news reaction features are useless.

No proof of time-aligned market order execution, no automatic trading, no release-channel insertion into canonical authority. Save R79 as negative baseline for future genuinely forward post-onset observation study.
