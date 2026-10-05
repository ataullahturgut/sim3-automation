# GOLD H3 — Hourly History Depth Probe

Purpose: test whether the original Yahoo hourly futures source can reproduce the missing historical IFBC/LLRS windows without source substitution.

| Target window | Channel | HTTP | Rows | First UTC | Last UTC | Error |
|---|---|---:|---:|---|---|---|
| 2023 | GC | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1664582400 and endTime=1705276800. The requested range must be within the last 730 days."}}} |
| 2023 | SI | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1664582400 and endTime=1705276800. The requested range must be within the last 730 days."}}} |
| 2023 | ZN | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1664582400 and endTime=1705276800. The requested range must be within the last 730 days."}}} |
| 2023 | NQ | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1664582400 and endTime=1705276800. The requested range must be within the last 730 days."}}} |
| 2023 | CL | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1664582400 and endTime=1705276800. The requested range must be within the last 730 days."}}} |
| 2024 | GC | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1696118400 and endTime=1736899200. The requested range must be within the last 730 days."}}} |
| 2024 | SI | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1696118400 and endTime=1736899200. The requested range must be within the last 730 days."}}} |
| 2024 | ZN | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1696118400 and endTime=1736899200. The requested range must be within the last 730 days."}}} |
| 2024 | NQ | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1696118400 and endTime=1736899200. The requested range must be within the last 730 days."}}} |
| 2024 | CL | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1696118400 and endTime=1736899200. The requested range must be within the last 730 days."}}} |
| 2025 | GC | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1719792000 and endTime=1768435200. The requested range must be within the last 730 days."}}} |
| 2025 | SI | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1719792000 and endTime=1768435200. The requested range must be within the last 730 days."}}} |
| 2025 | ZN | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1719792000 and endTime=1768435200. The requested range must be within the last 730 days."}}} |
| 2025 | NQ | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1719792000 and endTime=1768435200. The requested range must be within the last 730 days."}}} |
| 2025 | CL | 422 |  |  |  | {"chart":{"result":null,"error":{"code":"Unprocessable Entity","description":"1h data not available for startTime=1719792000 and endTime=1768435200. The requested range must be within the last 730 days."}}} |
