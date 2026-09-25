# GOLD MONTHLY FORECAST — 2026 AUGUST / SEPTEMBER LIVE AUDIT

**Date:** 2026-09-26

## Scope
Current top-family check for 2026-08 and 2026-09.

Active top roles:
- FULL7 ANN ensemble
- REDUCED4 ANN ensemble
- SMA-ELMFIS direction specialist
- AOA-ELM single-model benchmark

## August 2026 governed forecasts

Origin monthly Gold level used by the project: **4073.00 USD/oz (July 2026)**.

Component forecasts generated from the frozen governed protocol:
- Vanilla ANN: 4067.58
- MPA-ANN: 4079.91
- SCA-ANN: 4092.29
- DE-ABC-ANN: 4067.74
- Adaptive TLBO-ANN: 4136.60
- TLBO-tuned PSO-ANN: 4135.33
- MPA+SCA ANN: 4151.79
- SMA-ELMFIS: 4107.60
- AOA-ELM: 4108.39

Frozen ensemble calculations:
- **FULL7 ANN = 4104.46 USD/oz**
- **REDUCED4 ANN = 4076.88 USD/oz**

## August realization

Project DB daily metal series currently end at 2026-07-31, so August actual is not yet present in the internal governed daily-metal table.

External project-aligned monthly benchmark:
- World Bank / Commodity Markets Review London PM fixing monthly average for **August 2026 = 4411.00 USD/oz**.
- July 2026 = 4073.00 USD/oz.

Forecast errors against 4411.00:
- FULL7 ANN: |4104.46 - 4411.00| = **306.54 USD** (6.95%)
- REDUCED4 ANN: **334.12 USD** (7.57%)
- SMA-ELMFIS: **303.40 USD** (6.88%)
- AOA-ELM: **302.61 USD** (6.86%)

All four top-role models forecast UP relative to July 4073 and therefore got the August direction correct, but materially underestimated the magnitude.

## September 2026

**Canonical project forecast: BLOCKED.**

Reason:
- The frozen VW-MIDAS feature contract requires August daily Gold/Silver/Platinum/Palladium inputs at the August month-end origin.
- Governed daily-metal data currently stop at **2026-07-31**.
- Therefore no leakage-safe canonical September forecast can be produced from the project DB.

No fabricated or externally substituted September model forecast is recorded.

September 2026 is also not complete as of this audit. Any current observed average is MTD only, not a final monthly realization.

## Control and compliance summary
- August forecast uses origin-safe frozen protocol: PASS.
- Target-month actual used in August forecast: NO.
- DB READ_ONLY: PASS.
- September required origin inputs present: NO / BLOCKED.
- External data substituted into canonical September model: NO.
