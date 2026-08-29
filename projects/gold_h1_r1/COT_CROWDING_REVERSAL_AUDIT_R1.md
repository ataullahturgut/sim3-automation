# COT Crowding Reversal Audit R1

Frozen pre-2023 rule: crowd_pct >= 0.90; unwind_required=False; unwind_pct >= 0.80.

CFTC rows: 1055; span 2006-06-13 to 2026-08-25.
- DEV: n/base/rule/corrected/damaged/alarms = (130, np.float64(0.5230769230769231), np.float64(0.5307692307692308), 5, 4, 9)
- VAL: n/base/rule/corrected/damaged/alarms = (24, np.float64(0.4166666666666667), np.float64(0.4166666666666667), 0, 0, 0)
- TEST2023: n/base/rule/corrected/damaged/alarms = (11, np.float64(0.6363636363636364), np.float64(0.5454545454545454), 0, 1, 1)
- LOCK: n/base/rule/corrected/damaged/alarms = (30, np.float64(0.7666666666666667), np.float64(0.6), 3, 8, 11)

## 2026 Jan-Jul
- 2026-01: actual=+1 3M=+1 crowd=0.506 unwind=0.686 alarm=False pred=+1
- 2026-02: actual=+1 3M=+1 crowd=0.442 unwind=0.628 alarm=False pred=+1
- 2026-03: actual=-1 3M=+1 crowd=0.378 unwind=0.558 alarm=False pred=+1
- 2026-04: actual=-1 3M=+1 crowd=0.474 unwind=0.321 alarm=False pred=+1
- 2026-05: actual=-1 3M=-1 crowd=0.410 unwind=0.590 alarm=False pred=-1
- 2026-06: actual=-1 3M=-1 crowd=0.545 unwind=0.256 alarm=False pred=-1
- 2026-07: actual=-1 3M=-1 crowd=0.724 unwind=0.654 alarm=False pred=-1
