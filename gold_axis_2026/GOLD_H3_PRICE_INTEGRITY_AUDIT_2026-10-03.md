# GOLD H3 DAILY PRICE INTEGRITY AUDIT — 2026-10-03

**Scope:** frozen StakTrakr daily panel vs Twelve Data hourly closes, 2026-01-27..2026-03-25.

## Source status

- gold: `{"first": "2026-01-27 00:00:00", "last": "2026-03-25 23:00:00", "rows": 1391, "symbol": "XAU/USD"}`
- silver: `{"error": "{'code': 404, 'message': 'This symbol is available starting with the Grow or Venture plan. Consider upgrading now at https://twelvedata.com/pricing', 'status': 'error'}", "symbol": "XAG/USD"}`
- platinum: `{"error": "{'code': 404, 'message': 'This symbol is available starting with the Grow or Venture plan. Consider upgrading now at https://twelvedata.com/pricing', 'status': 'error'}", "symbol": "XPT/USD"}`
- palladium: `{"error": "{'code': 404, 'message': 'This symbol is available starting with the Grow or Venture plan. Consider upgrading now at https://twelvedata.com/pricing', 'status': 'error'}", "symbol": "XPD/USD"}`

## >=3% level discrepancies

| Date | Metal | Hour NY | Frozen | Twelve | log ratio |
|---|---|---:|---:|---:|---:|
| 2026-01-29 | gold | 12:00 | 5501.7000 | 5331.7062 | +3.14% |
| 2026-01-30 | gold | 12:00 | 5063.4500 | 4832.1308 | +4.68% |
| 2026-01-30 | gold | 16:00 | 5063.4500 | 4866.2554 | +3.97% |
| 2026-02-04 | gold | 12:00 | 5051.7500 | 4900.5574 | +3.04% |
| 2026-02-27 | gold | 12:00 | 3516.0200 | 5234.2051 | -39.79% |
| 2026-02-27 | gold | 16:00 | 3516.0200 | 5278.6362 | -40.63% |

## Feb 24–Mar 03 focus

| Date | Metal | Hour | Frozen | Twelve | log ratio |
|---|---|---:|---:|---:|---:|
| 2026-02-24 | gold | 12:00 | 5136.0600 | 5162.8671 | -0.52% |
| 2026-02-24 | gold | 16:00 | 5136.0600 | 5143.5952 | -0.15% |
| 2026-02-25 | gold | 12:00 | 5212.1000 | 5206.6447 | +0.10% |
| 2026-02-25 | gold | 16:00 | 5212.1000 | 5164.8157 | +0.91% |
| 2026-02-26 | gold | 12:00 | 5178.7000 | 5166.5110 | +0.24% |
| 2026-02-26 | gold | 16:00 | 5178.7000 | 5184.8173 | -0.12% |
| 2026-02-27 | gold | 12:00 | 3516.0200 | 5234.2051 | -39.79% |
| 2026-02-27 | gold | 16:00 | 3516.0200 | 5278.6362 | -40.63% |
| 2026-03-02 | gold | 12:00 | 5354.5900 | 5308.2020 | +0.87% |
| 2026-03-02 | gold | 16:00 | 5354.5900 | 5322.1342 | +0.61% |
| 2026-03-03 | gold | 12:00 | 5218.7100 | 5080.2675 | +2.69% |
| 2026-03-03 | gold | 16:00 | 5218.7100 | 5088.5127 | +2.53% |
