# Gold H1 R1 — 2023 Pre-2023 Rule Test

## Contract
- No 2023 outcome was used to define the candidate rule.
- Candidate source: NEW TACTICAL R1 historical audit.
- Frozen development period: 2010–2020.
- Monthly prior: exact canonical 3M momentum direction.
- Slow Tactical: sign(completed weekly close - SMA4), requiring the same state for 2 consecutive completed weeks.
- Candidate challenger: if Tactical is CONFLICT with the monthly 3M prior, flip the direction; otherwise retain 3M.
- Production baseline remains 3M direction + Tactical CONFIRM/CONFLICT confidence state; automatic flip is not approved.

## Why this candidate existed before 2023
Historical audit on DEV 2010–2020:
- CONFIRM: N=53, 3M hit=83.02%
- CONFLICT: N=36, 3M hit=25.00%
- NEUTRAL: N=40, 3M hit=37.50%
- Base 3M accuracy=52.70%
- Flip-on-CONFLICT challenger accuracy=66.67%
- Base balanced accuracy=52.40%
- Flip balanced accuracy=66.41%

Thus the candidate had a real pre-2023 statistical rationale; it was not invented from 2023 errors.

## One-shot 2023 test
Using the reconstructed 2023 month-end origin states:

| Month | Actual dir | 3M | Tactical relation | Frozen flip result | Effect vs 3M |
|---|---|---|---|---|---|
| Jan | UP | UP | NEUTRAL | UP | unchanged correct |
| Feb | DOWN | UP | CONFIRM | UP | unchanged wrong |
| Mar | UP | UP | CONFLICT | DOWN | damages correct call |
| Apr | UP | UP | CONFIRM | UP | unchanged correct |
| May | DOWN | UP | CONFLICT | DOWN | fixes error |
| Jun | DOWN | UP | CONFLICT | DOWN | fixes error |
| Jul | UP | UP | CONFLICT | DOWN | damages correct call |
| Aug | DOWN | DOWN | CONFLICT | UP | damages correct call |
| Sep | DOWN | DOWN | CONFIRM | DOWN | unchanged correct |
| Oct | FLAT | DOWN | CONFIRM | DOWN | score remains miss/flat artifact |
| Nov | UP | DOWN | CONFLICT | UP | fixes error |
| Dec | UP | UP | CONFIRM | UP | unchanged correct |

### Score
- Base 3M: 7/12 = 58.33% under archived scoring (flat October counted as miss).
- Frozen flip-on-CONFLICT: 7/12 = 58.33%.
- Excluding exactly-flat October as economically directionless: base 7/11 = 63.64%; flip 7/11 = 63.64%.
- Errors fixed: May, Jun, Nov = 3.
- Previously correct calls damaged: Mar, Jul, Aug = 3.
- Net directional gain: 0 months.

## Decision
`SIMPLE_CONFLICT_FLIP = REJECT_FOR_2023_CORRECTION`

The 2010–2020 relationship is real, but it is not sufficiently specific to identify the 2023 turning points. Tactical conflict is useful as a confidence warning, not as an automatic reversal command.

The remaining research question is narrower: distinguish **true reversal conflicts** (Jun, Nov; May weakly) from **temporary counter-trend conflicts** (Mar, Jul, Aug) using only information available before the target month. Any new discriminator must be learned before 2023 and must not use 2023/2024/2025/2026 outcomes for threshold tuning.
