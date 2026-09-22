# GOLD CONTROL — SQRT ALARM SEMANTIC AUDIT V1 RESULT

Semantic conclusion: DIRECTION_FALSE_ALARM_LABEL_CONFOUNDS_RISK_AND_DIRECTION

## Integrity

- Errors: none
- Alarm counts: {2020: 212, 2021: 28, 2022: 11, 2023: 2, 2024: 17}
- Pooled alarm direction: DOWN=127, UP=143

## Alarm anatomy by year

| Year | alarms | hit+DOWN | hit+UP | miss+DOWN | miss+UP | alarm risk-hit rate | UP-close that are risk hits |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 89 | 91 | 8 | 24 | 0.8490566037735849 | 0.7913043478260869 |
| 2021 | 28 | 15 | 5 | 1 | 7 | 0.7142857142857143 | 0.4166666666666667 |
| 2022 | 11 | 4 | 5 | 2 | 0 | 0.8181818181818182 | 1.0 |
| 2023 | 2 | 1 | 0 | 0 | 1 | 0.5 | 0.0 |
| 2024 | 17 | 6 | 2 | 1 | 8 | 0.47058823529411764 | 0.2 |

## Pooled 2020–2024 alarm semantics

- Alarms: 270
- RISK_HIT_DOWN_CLOSE: 115
- RISK_HIT_UP_CLOSE: 103
- RISK_MISS_DOWN_CLOSE: 12
- RISK_MISS_UP_CLOSE: 40
- Risk-hit rate among alarms: 0.8074074074074075
- UP-close alarms: 143
- UP-close alarms that were nevertheless realized high risk: 103
- Share of UP-close alarms that were realized high risk: 0.7202797202797203

## Full-parent risk-state diagnostics

- Rows: 1131
- Risk precision: 0.8074074074074075
- Risk recall: 0.6833855799373041
- Risk specificity: 0.9359605911330049

Do not equate UP-close with SQRT risk false alarm. Intraday rebound timing is not proven by this audit.
