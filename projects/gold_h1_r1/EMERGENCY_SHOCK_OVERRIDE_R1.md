# Emergency Shock Override R1

Frozen pre-2023 rule: MTD drawdown <= -3.0%, 5D return <= -4.0%, below SMA50, stress=NONE, stress_thr=20%.

Role: intramonth emergency downside override only when monthly 3M prior is UP. It does not alter the start-of-month forecast.

- DEV: eligible/needs/triggers/corrected/damaged/precision/recall = (77, 36, 12, 8, 4, 0.6666666666666666, 0.2222222222222222)
- VAL: eligible/needs/triggers/corrected/damaged/precision/recall = (9, 6, 3, 3, 0, 1.0, 0.5)
- TEST2023: eligible/needs/triggers/corrected/damaged/precision/recall = (8, 3, 0, 0, 0, nan, 0.0)
- LOCK: eligible/needs/triggers/corrected/damaged/precision/recall = (27, 7, 3, 3, 0, 1.0, 0.42857142857142855)

## 2026 Jan-Jul UP-prior months
- 2026-01: actual=+1 need_override=0 trigger=False date=- dd=nan% ret5=nan% VIX5=nan% USD5=nan% RY5=+nan
- 2026-02: actual=+1 need_override=0 trigger=False date=- dd=nan% ret5=nan% VIX5=nan% USD5=nan% RY5=+nan
- 2026-03: actual=-1 need_override=1 trigger=True date=2026-03-18 dd=-9.46% ret5=-6.93% VIX5=3.55% USD5=0.54% RY5=+0.010
- 2026-04: actual=-1 need_override=1 trigger=False date=- dd=nan% ret5=nan% VIX5=nan% USD5=nan% RY5=+nan
