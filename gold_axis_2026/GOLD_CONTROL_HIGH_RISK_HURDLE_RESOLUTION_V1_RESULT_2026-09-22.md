# GOLD CONTROL — HIGH-RISK HURDLE RESOLUTION V1 RESULT

Status: SELECTIVE_SIGNAL_PRESENT_NOT_CERTIFIED

Integrity errors: none

## Year-by-year

| Year | n | HIT_DOWN | HIT_UP | MISS | coverage | selective acc | argmax acc | dir AUC on risk hits |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 89 | 91 | 32 | 0.5377358490566038 | 0.45614035087719296 | 0.37264150943396224 | 0.5333991850845784 |
| 2021 | 28 | 15 | 5 | 8 | 0.2857142857142857 | 0.375 | 0.4642857142857143 | 0.5733333333333333 |
| 2022 | 11 | 4 | 5 | 2 | 0.6363636363636364 | 0.42857142857142855 | 0.45454545454545453 | 0.35 |
| 2023 | 2 | 1 | 0 | 1 | 0.5 | 1.0 | 0.5 | None |
| 2024 | 17 | 6 | 2 | 9 | 0.35294117647058826 | 0.8333333333333334 | 0.47058823529411764 | 0.41666666666666663 |

## Pooled 2020–2024

- N: 270
- Observed: {'HIT_DOWN': 115, 'HIT_UP': 103, 'MISS': 52}
- Emitted: {'HIT_DOWN': 11, 'HIT_UP': 68, 'MISS': 57, 'UNCERTAIN': 134}
- Coverage: 0.5037037037037037
- Selective accuracy: 0.47058823529411764
- Non-selective argmax accuracy: 0.3925925925925926
- Largest observed class share: 0.42592592592592593
- Multiclass Brier: 0.6486898730300662
- Multiclass log loss: 1.0315994500456505
- Direction AUC on realized-risk-hit alarms: 0.5557619248628112
- Direction accuracy @0.5 on realized-risk-hit alarms: 0.5091743119266054

Router/context features are intentionally excluded from V1.
