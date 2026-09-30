# GOLD MONTHLY — ChHHO Error Severity Revision V2 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING SEVERITY LABEL
**Scope:** alarm research only; model selection/economic evaluation unchanged.

## 1. Fixed normalized severity bands

Use absolute Gold log-return forecast error in percentage points:

- **NORMAL:** error < 2.50 pp
- **MEDIUM:** 2.50 pp <= error < 3.00 pp
- **HIGH:** error >= 3.00 pp

These are fixed human-readable thresholds requested for alarm interpretation. They supersede the DEV-Q3 return-error cutoff as the primary alarm severity definition.

The model-selection objective remains unchanged:
- cumulative absolute USD error (ΣAE)
- direction accuracy
- supporting MAE/MAPE/WAPE/RMSE.

AE remains an economic-impact metric, not the alarm severity label.

## 2. Required audit

Reclassify all scientifically usable ChHHO targets:
- valid pre-DEV 2021-11..2022-03
- canonical DEV 2022-04..2024-12
- 2025 transport
- 2026 Jan-Aug

Report:
1. exact target lists for NORMAL / MEDIUM / HIGH;
2. counts by period;
3. A/B/C/D/H performance for HIGH only;
4. A/B/C/D/H coverage for MEDIUM+HIGH ("elevated error");
5. E/G/GVZ/CFTC descriptor behavior;
6. HIGH misses after A/B/C/D/H;
7. MEDIUM misses separately;
8. comparison with the superseded DEV-Q3 classification.

## 3. Governance

- No alarm-rule threshold may be retuned from these labels.
- No 2025/2026 tuning.
- No routing/fallback testing.
- Severity thresholds are fixed at exactly 2.50 and 3.00 percentage points.
