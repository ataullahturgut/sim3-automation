# Macro Reversal Audit R1

Frozen pre-2023 rule: mode=OR, real-yield 1M change >= 0.1, USD 1M return >= 0.0%.

- DEV: (130, np.float64(0.5230769230769231), np.float64(0.6153846153846154), 23, 11, 34)
- VAL: (24, np.float64(0.4166666666666667), np.float64(0.5833333333333334), 5, 1, 6)
- TEST2023: (11, np.float64(0.6363636363636364), np.float64(0.5454545454545454), 2, 3, 5)
- LOCK: (30, np.float64(0.7666666666666667), np.float64(0.6333333333333333), 4, 8, 12)

## 2026 Jan-Jul
- 2026-01: actual=+1 3M=+1 ry1=+0.140 usd1=-1.080% alarm=True pred=-1
- 2026-02: actual=+1 3M=+1 ry1=-0.030 usd1=-1.542% alarm=False pred=+1
- 2026-03: actual=-1 3M=+1 ry1=-0.180 usd1=-0.066% alarm=False pred=+1
- 2026-04: actual=-1 3M=+1 ry1=+0.280 usd1=+2.727% alarm=True pred=-1
- 2026-05: actual=-1 3M=-1 ry1=-0.060 usd1=-1.953% alarm=False pred=-1
- 2026-06: actual=-1 3M=-1 ry1=+0.130 usd1=+0.175% alarm=False pred=-1
- 2026-07: actual=-1 3M=-1 ry1=+0.130 usd1=+1.722% alarm=False pred=-1
