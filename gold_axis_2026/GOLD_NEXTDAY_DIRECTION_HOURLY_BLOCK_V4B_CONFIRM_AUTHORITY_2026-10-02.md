# GOLD NEXT-DAY DIRECTION — HOURLY BLOCK V4B FROZEN CONFIRMATION

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN CONFIRMATION  
**Parent screen:** V4 small-block screen, workflow 37008370714

## Why this confirmation exists

The V4 2023 screen found one clear standalone block winner:

- `blk3_19_21`
- 2023 accuracy delta versus V1: **+1.34 pp**
- 2023 balanced-accuracy delta: **+1.38 pp**
- 2023 Brier delta: **-0.0061**
- 2023 log-loss delta: **-0.0186**.

The same block added on top of V3 (`V1 + lag2`) did not improve 2023 direction accuracy, but materially improved probability quality.

Therefore V4B freezes that already-selected 2023 winner **before examining its 2024 confirmation metrics** and evaluates two fixed forms:

1. `V1 + blk3_19_21` — can the block replace lag2?
2. `V1 + lag2 + blk3_19_21` — does the block improve calibration while preserving V3 direction performance?

No other block is tested in V4B. No 2024 outcome may change the candidate or specification.

## Evaluation

Report 2023, 2024, and combined 2023-2024:
- accuracy
- balanced accuracy
- Brier
- log loss
- UP recall
- DOWN recall
- false-call rate.

2024 remains confirmation evidence within an already-opened research history, not a pristine lockbox.
