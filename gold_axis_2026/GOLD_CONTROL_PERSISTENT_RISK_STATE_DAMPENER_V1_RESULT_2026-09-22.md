# GOLD CONTROL — PERSISTENT RISK-STATE DAMPENER V1 RESULT

Status: RETROSPECTIVELY_PROMISING_NOT_CERTIFIED

## Frozen state definition

- Lookback: 20 completed trading days ending at origin
- Q80 exceedance count cutoff: >= 9
- Binomial(20,0.20) tail at K=9: 0.009981786320724306
- K minimal at 0.01 level: True

## Integrity

- Errors: none
- Frozen reproduction: {2020: {'alarms': 212, 'router_up': 185, 'overlap': 140, 'good': 80, 'bad': 60}, 2021: {'alarms': 28, 'router_up': 33, 'overlap': 2, 'good': 1, 'bad': 1}, 2022: {'alarms': 11, 'router_up': 22, 'overlap': 0, 'good': 0, 'bad': 0}, 2023: {'alarms': 2, 'router_up': 19, 'overlap': 0, 'good': 0, 'bad': 0}, 2024: {'alarms': 17, 'router_up': 42, 'overlap': 4, 'good': 3, 'bad': 1}}

## Year-by-year

| Year | alarms | persistent | suppress | watch | good | bad | FA reduction | DOWN retention | remaining precision |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 199 | 3 | 137 | 3 | 0 | 0.02608695652173913 | 1.0 | 0.46411483253588515 |
| 2021 | 28 | 18 | 1 | 1 | 0 | 1 | 0.0 | 0.9375 | 0.5555555555555556 |
| 2022 | 11 | 4 | 0 | 0 | 0 | 0 | 0.0 | 1.0 | 0.5454545454545454 |
| 2023 | 2 | 0 | 0 | 0 | 0 | 0 | 0.0 | 1.0 | 0.5 |
| 2024 | 17 | 8 | 4 | 0 | 3 | 1 | 0.3 | 0.8571428571428571 | 0.46153846153846156 |

## Pooled 2020–2024

- Alarms: 270
- Persistent alarms: 229; non-persistent: 41
- SUPPRESS: 8; WATCH: 138; RETAIN: 124
- Good suppressions: 6; bad suppressions: 2
- Bad-suppression rate among actual DOWN alarms: 0.015748031496062992
- Suppression precision: 0.75
- False-alarm reduction: 0.04195804195804196
- True-DOWN retention: 0.984251968503937
- Remaining forced-DOWN precision: 0.4770992366412214
- Precision gain pp: 0.6728866270851008
- Exact alpha/delta: 0.2/0.1; p=2.624235178314573e-10
- Exact 90% upper bad-suppression bound: 0.04136291339317107

## Frozen comparators

- Universal Router veto: {'alarms': 270, 'actual_down': 127, 'actual_up': 143, 'retain': 124, 'watch': 0, 'suppress': 146, 'good_suppressions': 84, 'bad_suppressions': 62, 'bad_suppression_rate': 0.4881889763779528, 'suppression_precision': 0.5753424657534246, 'false_alarm_reduction': 0.5874125874125874, 'true_down_retention': 0.5118110236220472, 'baseline_forced_down_precision': 0.4703703703703704, 'remaining_forced_down_precision': 0.5241935483870968, 'precision_gain_pp': 5.382317801672637, 'persistent_alarm_count': 229, 'nonpersistent_alarm_count': 41, 'insufficient_history_alarm_count': 0, 'router_up_persistent': 138, 'router_up_nonpersistent': 8, 'router_up_insufficient': 0, 'recent20_high_count_histogram': {'1': 2, '2': 2, '3': 3, '4': 8, '5': 7, '6': 5, '7': 5, '8': 9, '9': 5, '10': 12, '11': 12, '12': 15, '13': 13, '14': 5, '15': 13, '16': 19, '17': 37, '18': 27, '19': 12, '20': 59}, 'exact_ltt_alpha': 0.2, 'exact_ltt_delta': 0.1, 'exact_lower_tail_p_value': 0.9999999999999079, 'exact_90pct_cp_upper_bad_suppression_rate': 0.5487724275558232, 'retrospective_safety_diagnostic_pass': False}
- Q80-Q90 instantaneous gate: {'alarms': 270, 'actual_down': 127, 'actual_up': 143, 'retain': 124, 'watch': 89, 'suppress': 57, 'good_suppressions': 30, 'bad_suppressions': 27, 'bad_suppression_rate': 0.2125984251968504, 'suppression_precision': 0.5263157894736842, 'false_alarm_reduction': 0.2097902097902098, 'true_down_retention': 0.7874015748031497, 'baseline_forced_down_precision': 0.4703703703703704, 'remaining_forced_down_precision': 0.4694835680751174, 'precision_gain_pp': -0.08868022952530086, 'persistent_alarm_count': 229, 'nonpersistent_alarm_count': 41, 'insufficient_history_alarm_count': 0, 'router_up_persistent': 138, 'router_up_nonpersistent': 8, 'router_up_insufficient': 0, 'recent20_high_count_histogram': {'1': 2, '2': 2, '3': 3, '4': 8, '5': 7, '6': 5, '7': 5, '8': 9, '9': 5, '10': 12, '11': 12, '12': 15, '13': 13, '14': 5, '15': 13, '16': 19, '17': 37, '18': 27, '19': 12, '20': 59}, 'exact_ltt_alpha': 0.2, 'exact_ltt_delta': 0.1, 'exact_lower_tail_p_value': 0.6854538844229463, 'exact_90pct_cp_upper_bad_suppression_rate': 0.2663684826455538, 'retrospective_safety_diagnostic_pass': False}

Retrospective hypothesis stress only; not prospective certification.
