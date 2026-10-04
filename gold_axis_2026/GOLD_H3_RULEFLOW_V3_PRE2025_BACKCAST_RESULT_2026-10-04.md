# GOLD H3 — RULEFLOW V3-TG PRE-2025 BACKCAST RESULT

**Status:** FIXED-RULE HISTORICAL BACKCAST — not prospective validation.

No RuleFlow threshold, topology sign, p-value threshold, or action rule was changed after the preregistration commit.

## 2023

- event rows scored: **47**
- V2 hotspots / gated hotspots: **8 / 3**
- V2 actions: **1**, rescue/broken/net = **0 / 1 / -1**
- V3-TG actions: **1**, rescue/broken/net = **0 / 1 / -1**
- V3-TG action precision: **0.00%**
- V5 baseline: **156/219 = 71.23%**, BA **71.83%**
- V5 + V3-TG: **155/219 = 70.78%**, BA **71.35%**
- V3 action dates: **2023-10-03**

## 2024

- event rows scored: **56**
- V2 hotspots / gated hotspots: **9 / 2**
- V2 actions: **1**, rescue/broken/net = **0 / 1 / -1**
- V3-TG actions: **1**, rescue/broken/net = **0 / 1 / -1**
- V3-TG action precision: **0.00%**
- V5 baseline: **172/241 = 71.37%**, BA **70.30%**
- V5 + V3-TG: **171/241 = 70.95%**, BA **69.94%**
- V3 action dates: **2024-06-12**

## Combined 2023-2024 event accounting

- V2 actions: **2**, rescue/broken/net = **0 / 2 / -2**
- V3-TG actions: **2**, rescue/broken/net = **0 / 2 / -2**
- V3-TG precision: **0.00%**

## V3 action detail

| Date | Event | V5 | Momentum | Actual | Rescue | Broken | NDX r60 | VIX r60 | Strong pro-risk |
|---|---|---:|---:|---:|---|---|---:|---:|---|
| 2023-10-03 | JOLTS | 0 | 0 | 0 | False | True | 0.053 | -0.012 | False |
| 2024-06-12 | CPI+FOMC | 1 | 1 | 1 | False | True | -0.049 | 0.073 | False |

## V2 calls vetoed by topology

| Date | Event | V2 rescue | V2 broken | NDX r60 | VIX r60 |
|---|---|---|---|---:|---:|

## Data note

- DGS2 carry-forward was required on **1** event dates: 2024-03-29.
- SAGE V2 cannot be backcast to 2023-2024 with the frozen source contract because IFBC begins 2025-05-09 and LLRS begins 2025-02-07. No synthetic SAGE result is reported.
- This backcast is historically earlier than the topology discovery period, but it remains retrospective evidence rather than prospective OOS validation.
