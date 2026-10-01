# GOLD SHORT-HORIZON GLOBAL XAU — Data Readiness Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN

Target:
- global XAU daily spot-average research series
- not BIST Metal Price.

Chronology:
- history <=2021
- DEV 2022-2024
- 2025 frozen.

PASS if:
- DEV >=700 eligible origins at H1/H3/H5
- pre-DEV Gold history >=2000
- 2025 transport >=200 per horizon
- CORE3 and safe external joins do not materially collapse DEV.

Feature timing:
- H.15 <= signal_date -2 calendar days
- H.10 <= signal_date -7 days
- VIX/NDX <= signal_date -1 day.

No WTI/Brent in first batch.
No 2025 selection.
