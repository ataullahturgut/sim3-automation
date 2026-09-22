# GOLD CONTROL — HIGH-RISK HURDLE RESOLUTION V1 RESULT

Status: BLOCKED_INTEGRITY_MISMATCH

Integrity errors: ['ALARM_COUNT_2020:215!=212', 'ALARM_COUNT_2023:3!=2', 'CLASS_HIT_DOWN:116!=115', 'CLASS_MISS:55!=52', 'POOLED_N:274!=270']

## Year-by-year

| Year | n | HIT_DOWN | HIT_UP | MISS | coverage | selective acc | argmax acc | dir AUC on risk hits |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 215 | 90 | 91 | 34 | 0.5348837209302325 | 0.4608695652173913 | 0.3767441860465116 | 0.5335775335775336 |
| 2021 | 28 | 15 | 5 | 8 | 0.2857142857142857 | 0.375 | 0.4642857142857143 | 0.5733333333333333 |
| 2022 | 11 | 4 | 5 | 2 | 0.6363636363636364 | 0.42857142857142855 | 0.45454545454545453 | 0.35 |
| 2023 | 3 | 1 | 0 | 2 | 0.6666666666666666 | 1.0 | 0.6666666666666666 | None |
| 2024 | 17 | 6 | 2 | 9 | 0.35294117647058826 | 0.8333333333333334 | 0.47058823529411764 | 0.41666666666666663 |

## Pooled 2020–2024

- N: 274
- Observed: {'HIT_DOWN': 116, 'HIT_UP': 103, 'MISS': 55}
- Emitted: {'HIT_DOWN': 11, 'HIT_UP': 69, 'MISS': 58, 'UNCERTAIN': 136}
- Coverage: 0.5036496350364964
- Selective accuracy: 0.4782608695652174
- Non-selective argmax accuracy: 0.3978102189781022
- Largest observed class share: 0.4233576642335766
- Multiclass Brier: 0.6436512132263249
- Multiclass log loss: 1.0247901891904003
- Direction AUC on realized-risk-hit alarms: 0.556662202879143
- Direction accuracy @0.5 on realized-risk-hit alarms: 0.5114155251141552

Router/context features are intentionally excluded from V1.
