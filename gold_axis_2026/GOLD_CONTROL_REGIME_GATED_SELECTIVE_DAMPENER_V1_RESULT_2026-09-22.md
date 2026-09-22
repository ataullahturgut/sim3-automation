# GOLD CONTROL — REGIME-GATED SELECTIVE DAMPENER V1 RESULT

Status: BLOCKED_INTEGRITY_MISMATCH

## Integrity

- Errors: ['LEGACY_2023_SLOW_UP:80!=79', 'LEGACY_2024_SLOW_UP:110!=111', 'FROZEN_2021_router_up:32!=33', 'FROZEN_2023_router_up:25!=19', 'FROZEN_2024_router_up:47!=42', 'FROZEN_2024_overlap:5!=4', 'FROZEN_2024_good:4!=3']
- Frozen reproduction: {2020: {'alarms': 212, 'router_up': 185, 'overlap': 140, 'good': 80, 'bad': 60}, 2021: {'alarms': 28, 'router_up': 32, 'overlap': 2, 'good': 1, 'bad': 1}, 2022: {'alarms': 11, 'router_up': 22, 'overlap': 0, 'good': 0, 'bad': 0}, 2023: {'alarms': 2, 'router_up': 25, 'overlap': 0, 'good': 0, 'bad': 0}, 2024: {'alarms': 17, 'router_up': 47, 'overlap': 5, 'good': 4, 'bad': 1}}

## Year-by-year

| Year | alarms | suppress | watch | good | bad | FA reduction | DOWN retention | remaining precision |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | 51 | 89 | 26 | 25 | 0.22608695652173913 | 0.7422680412371134 | 0.4472049689440994 |
| 2021 | 28 | 2 | 0 | 1 | 1 | 0.08333333333333333 | 0.9375 | 0.5769230769230769 |
| 2022 | 11 | 0 | 0 | 0 | 0 | 0.0 | 1.0 | 0.5454545454545454 |
| 2023 | 2 | 0 | 0 | 0 | 0 | 0.0 | 1.0 | 0.5 |
| 2024 | 17 | 5 | 0 | 4 | 1 | 0.4 | 0.8571428571428571 | 0.5 |

## Pooled 2020–2024

- Alarms: 270
- SUPPRESS: 58; WATCH: 89; RETAIN: 123
- Good suppressions: 31; bad suppressions: 27
- Suppression precision: 0.5344827586206896
- False-alarm reduction: 0.21678321678321677
- True-DOWN retention: 0.7874015748031497
- Remaining forced-DOWN precision: 0.4716981132075472
- Precision gain pp: 0.1327742837176793
- Exact alpha/delta: 0.2/0.1; p=0.6854538844229463
- Exact 90% upper bad-suppression bound: 0.2663684826455538

Retrospective hypothesis stress only; not prospective certification.
