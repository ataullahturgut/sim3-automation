# FLOW-H3 CME PUBLIC SOURCE PROBE — 2026-10-03

Purpose: test whether CME public archives can supply official historical GC daily Volume/Open Interest without DataMine entitlement.

## Public daily_volume XLSX archive

| Date | HTTP | Bytes | OI text hits | Gold rows |
|---|---:|---:|---:|---:|
| 20220103 | 403 | 602 | 0 | 0 |
| 20240102 | 403 | 602 | 0 | 0 |
| 20250930 | 403 | 602 | 0 | 0 |
| 20260930 | 403 | 602 | 0 | 0 |

### Workbook evidence

#### 20220103
- sheets: None
- contains explicit Open Interest text: False

#### 20240102
- sheets: None
- contains explicit Open Interest text: False

#### 20250930
- sheets: None
- contains explicit Open Interest text: False

#### 20260930
- sheets: None
- contains explicit Open Interest text: False

## CME product JSON endpoint (Gold product id 437)

| Date | Flag | HTTP | Bytes | monthData_n | totals present |
|---|---|---:|---:|---:|---|
| 20220103 | F | 403 | 602 | None | False |
| 20220103 | P | 403 | 602 | None | False |
| 20240102 | F | 403 | 602 | None | False |
| 20240102 | P | 403 | 602 | None | False |
| 20250930 | F | 403 | 602 | None | False |
| 20250930 | P | 403 | 602 | None | False |
| 20260930 | F | 403 | 602 | None | False |
| 20260930 | P | 403 | 602 | None | False |

## Interpretation

- A public path is acceptable for FLOW only if it contains required GC daily Volume and Open Interest with stable historical coverage and an auditable final/preliminary clock.
- If the XLSX archive is volume-only, it may support a volume-only diagnostic but cannot satisfy frozen FLOW-H3 V1 as preregistered.
- If the JSON endpoint is short-retention only, it cannot backfill 2023-2026 and remains prospective/supporting only.
- No model fitting or threshold selection is performed by this probe.
