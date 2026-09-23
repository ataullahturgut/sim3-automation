# GOLD CONTROL — DIRECTION MECHANISM-GAP AUDIT V1 RESULT

**Status:** `AUDIT_COMPLETE`

Pre-2025 counts: `{"CAPTURED_UP": 8, "FALSE_UP_ACTUAL_DOWN": 3, "MISSED_UP": 5, "REJECTED_DOWN": 10}`  
Locked-2025 counts: `{"CAPTURED_UP": 13, "FALSE_UP_ACTUAL_DOWN": 12, "MISSED_UP": 22, "REJECTED_DOWN": 27}`

## CAPTURED_UP_vs_MISSED_UP
- **late_downside_intensity** — MODERATE_STABLE; pre delta=0.450, 2025 delta=0.336, pre median diff=0.0192263, 2025 median diff=0.0453931, pre BH q=0.9414335664335665
- **last_hour_trend_r2** — PRE2025_ONLY; pre delta=-0.700, 2025 delta=-0.126, pre median diff=-0.639665, 2025 median diff=-0.24896, pre BH q=0.937062937062937
- **late_downside_rv_share** — PRE2025_ONLY; pre delta=0.500, 2025 delta=0.077, pre median diff=0.0371127, 2025 median diff=0.0215183, pre BH q=0.9414335664335665
- **last_hour_slope_norm** — PRE2025_ONLY; pre delta=0.500, 2025 delta=-0.252, pre median diff=2.62341, 2025 median diff=-0.797984, pre BH q=0.9414335664335665
- **terminal_negative_run_frac** — PRE2025_ONLY; pre delta=0.450, 2025 delta=-0.007, pre median diff=0.00181818, 2025 median diff=0, pre BH q=0.9414335664335665

## CAPTURED_UP_vs_FALSE_UP_ACTUAL_DOWN
- **last_hour_trend_r2** — MODERATE_STABLE; pre delta=-0.667, 2025 delta=-0.231, pre median diff=-0.579173, 2025 median diff=-0.44095, pre BH q=1.0
- **last_hour_slope_norm** — PRE2025_ONLY; pre delta=0.583, 2025 delta=0.038, pre median diff=2.07776, 2025 median diff=0.382601, pre BH q=1.0
- **last_hour_return_norm** — PRE2025_ONLY; pre delta=0.500, 2025 delta=0.103, pre median diff=0.05467, 2025 median diff=0.0377423, pre BH q=1.0
- **terminal_negative_run_frac** — PRE2025_ONLY; pre delta=0.417, 2025 delta=-0.385, pre median diff=0.00545455, 2025 median diff=-0.0037594, pre BH q=1.0
- **time_near_low_last_quarter** — PRE2025_ONLY; pre delta=0.333, 2025 delta=0.038, pre median diff=0.253623, 2025 median diff=0.0408375, pre BH q=1.0
- **late_acceleration_norm** — PRE2025_ONLY; pre delta=-0.333, 2025 delta=0.244, pre median diff=-0.0221867, 2025 median diff=0.0695351, pre BH q=1.0

## MISSED_UP_vs_REJECTED_DOWN
- **last_hour_trend_r2** — PRE2025_ONLY; pre delta=0.680, 2025 delta=-0.212, pre median diff=0.500043, 2025 median diff=-0.146014, pre BH q=0.4635364635364636
- **near_trough_revisit_rate** — PRE2025_ONLY; pre delta=0.520, 2025 delta=0.162, pre median diff=0.203907, 2025 median diff=0.0320167, pre BH q=0.4635364635364636
- **last_hour_return_norm** — PRE2025_ONLY; pre delta=-0.440, 2025 delta=-0.091, pre median diff=-0.140055, 2025 median diff=-0.00651029, pre BH q=0.4635364635364636
- **last_hour_slope_norm** — PRE2025_ONLY; pre delta=-0.400, 2025 delta=-0.081, pre median diff=-2.94771, 2025 median diff=0.185589, pre BH q=0.516983016983017
- **time_near_low_last_quarter** — PRE2025_ONLY; pre delta=0.340, 2025 delta=0.007, pre median diff=0, 2025 median diff=0, pre BH q=1.0

No classifier was trained. Stable patterns may motivate a separately preregistered future model only.
