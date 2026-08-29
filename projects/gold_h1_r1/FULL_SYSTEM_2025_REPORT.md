# GOLD H1 R1 — Full System 2025 Replay

Role separation is preserved: level forecast, model selection, monthly direction, Tactical confirmation/conflict, BOCPD regime risk, and Emergency intramonth override are reported separately. No 2025 outcome is used for tuning.

## Headline metrics

- MOM3_direction_accuracy: 0.916667
- MOM1_direction_accuracy: 0.750000
- VW_direction_accuracy: 0.833333
- selector_implied_direction_accuracy: 0.833333
- VW_MAPE: 2.385942
- selector_MAPE: 3.043933
- equal_ensemble_MAPE: 2.933212
- selector_oracle_pick_rate: 0.500000
- tactical_confirm_months: 6
- tactical_conflict_months: 1
- tactical_neutral_months: 5
- bocpd_alarm_months: 0
- emergency_trigger_months: 0
- reversal_warning_months: 3

## Monthly replay

|Target|Actual|MOM3|MOM1|VW dir|Tactical|Selector|VW APE|Selector APE|BOCPD|Emergency|Action|
|---|---:|---:|---:|---:|---|---|---:|---:|---|---|---|
|2025-01|+1|+1|-1|-1|CONFLICT|momentum|2.938%|1.289%|-|-|LOW_CONFIDENCE_KEEP_PRIOR|
|2025-02|+1|+1|+1|+1|CONFIRM|momentum|2.823%|6.147%|-|-|KEEP_PRIOR|
|2025-03|+1|+1|+1|+1|NEUTRAL|vw|2.926%|2.926%|-|-|KEEP_PRIOR|
|2025-04|+1|+1|+1|+1|CONFIRM|vw|2.401%|2.401%|-|-|KEEP_PRIOR|
|2025-05|+1|+1|+1|+1|CONFIRM|vw|1.191%|1.191%|-|-|KEEP_PRIOR|
|2025-06|+1|+1|+1|+1|NEUTRAL|patch|0.029%|1.804%|-|-|KEEP_PRIOR|
|2025-07|-1|+1|+1|-1|NEUTRAL|vw|0.143%|0.143%|-|-|KEEP_PRIOR|
|2025-08|+1|+1|-1|-1|NEUTRAL|momentum|0.998%|0.415%|-|-|KEEP_PRIOR|
|2025-09|+1|+1|+1|+1|CONFIRM|vw|6.282%|6.282%|-|-|KEEP_PRIOR|
|2025-10|+1|+1|+1|+1|CONFIRM|patch|6.516%|8.641%|-|-|KEEP_PRIOR|
|2025-11|+1|+1|+1|+1|NEUTRAL|patch|0.338%|0.136%|-|-|KEEP_PRIOR|
|2025-12|+1|+1|+1|+1|CONFIRM|rw|2.048%|5.152%|-|-|KEEP_PRIOR|

## Decision

- The archived VW path is the stronger 2025 price-level reference than the exploratory selector if its mean MAPE is lower.
- The selector remains diagnostic/challenger; gate_hit is ex-post oracle-model selection agreement, not direction accuracy.
- Tactical conflict is a confidence warning, not an approved automatic flip.
- BOCPD-return is structural risk context only.
- Emergency Shock Override is intramonth risk-off only and does not rewrite the start-of-month forecast.
- Any oracle_pick/oracle_ape column is diagnostic hindsight only.
