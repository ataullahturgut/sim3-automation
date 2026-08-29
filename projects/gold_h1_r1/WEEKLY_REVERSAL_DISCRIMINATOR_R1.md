# GOLD H1 R1 — Weekly Event-Level Reversal Discriminator R1

- D1→W1 exhaustive 2010–2022: **FAIL** (678 bars, exact=579)
- Tactical count DEV reconciliation: **FAIL** reconstructed={'CONFIRM': 54, 'NEUTRAL': 40, 'CONFLICT': 38} expected={'CONFIRM': 53, 'CONFLICT': 36, 'NEUTRAL': 40}
- Tactical count VAL 2021–2023 reconciliation: **FAIL** reconstructed={'CONFIRM': 15, 'CONFLICT': 14, 'NEUTRAL': 7} expected={'CONFIRM': 14, 'CONFLICT': 14, 'NEUTRAL': 7}

- Baseline DEV acc=0.5231, BA=0.5203
- Baseline VAL 2021–22 acc=0.4167, BA=0.4056
- Baseline 2023 acc=0.6364, BA=0.6167
- Pre-2023 qualified rules=17
- Frozen rule: single raw_persistence>=2
- DEV acc=0.6769, BA=0.6752, corrected=29, damaged=9
- VAL acc=0.7500, BA=0.7483, corrected=8, damaged=0
- 2023 acc=0.6364, BA=0.6333, corrected=3, damaged=3
- Final model status: **FAIL_2023_GENERALIZATION**

- DATA_GATE=FAIL
- Target leakage: NONE
- 2023+ tuning: NONE
- Random split: NONE
- False flips counted: YES
