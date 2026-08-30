# GVZ + Macro Event Reversal Audit R1

Sources: pinned XAUUSD D1; official Cboe GVZ_History.csv; FRED release/actual enriched with Investing.com consensus from superpilot69/fred-us-macro-open-data.
2023 is untouched test. Approximate release timestamps are excluded. Event decisions are close-of-release-day and apply to the next D1 bar.

Frozen DOWN event rule: (1, 0.005)
Frozen UP event rule: (1, 0.0)

## NFP around 3-Feb-2023
- 2023-02-03: actual=517.0, forecast=185.0, surprise=332.0, gold_sign=-1, source=investing-economic-calendar

## 2023 event triggers
- 2023-01: prior=+1, actual=+1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-02: prior=+1, actual=-1, trigger=True, date=2023-02-03, macro_score=-2.0, GVZ=15.06, GVZ_stress=False
- 2023-03: prior=+1, actual=+1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-04: prior=+1, actual=+1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-05: prior=+1, actual=-1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-06: prior=+1, actual=-1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-07: prior=+1, actual=+1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-08: prior=-1, actual=-1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False
- 2023-09: prior=-1, actual=-1, trigger=True, date=2023-09-01, macro_score=1.0, GVZ=11.28, GVZ_stress=False
- 2023-11: prior=-1, actual=+1, trigger=True, date=2023-11-03, macro_score=3.0, GVZ=14.04, GVZ_stress=False
- 2023-12: prior=+1, actual=+1, trigger=False, date=-, macro_score=nan, GVZ=nan, GVZ_stress=False

## Interpretation
- GVZ is non-directional risk/intensity context and never creates UP/DOWN by itself.
- Macro Event is execution-authorized only if a pre-2023 rule is selected and 2023 is then replayed untouched.
- If no pre-2023 eligible rule exists, EVENT_EXECUTION=REJECT and the layer remains context-only.
