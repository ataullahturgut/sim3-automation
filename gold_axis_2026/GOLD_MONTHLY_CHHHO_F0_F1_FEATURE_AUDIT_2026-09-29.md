# GOLD MONTHLY — ChHHO-ANFIS F0/F1 Feature Necessity Audit

**Date:** 2026-09-29  
**Status:** COMPLETE / ZERO NEON / DEV-ONLY  
**Decision:** RETAIN CURRENT8 FOR F2

## 1. Scientific question

Before adding external drivers or changing lags/representations, test whether the current eight ChHHO inputs are necessary.

CURRENT8:
1. Gold MR
2. Gold VW
3. Silver MR
4. Silver VW
5. Platinum MR
6. Platinum VW
7. Palladium MR
8. Palladium VW

DEV authority: **2022-04..2024-12, 33 origins**.  
2025 used for selection: **NO**.  
2026 used for selection: **NO**.  
Random split: **NONE**.  
Neon reads: **0**.

The ChHHO optimizer, rule count, chronological inner validation and target contract were held fixed. Reduced-input ablations truly removed columns from the input space; omitted columns were not zero-filled.

## 2. F0 parity

Authoritative reduced-input workflow:
- run **36534691218**
- runner commit **cf44dc1925b28132590d254db098382d7442fe67**
- summary artifact **11018091595**
- artifact digest: `sha256:f3211269487ecf4730d35bcef1ee424efd851f492bd52dae8817c8d069924734`

CURRENT8 reproduced:
- DEV ΣAE: **1413.0297794085**
- direction: **23/33**

F0 parity: **PASS**.

An earlier mean-masking attempt, run **36534304610**, is **SUPERSEDED_TECHNICAL / NOT MODEL EVIDENCE** because constant masked inputs produced singular design-condition diagnostics and JSON fail-closed behavior.

## 3. F1 broad necessity audit

| Variant | DEV ΣAE | Direction | ΔΣAE vs CURRENT8 | Months improved / worsened | Median paired AE improvement |
|---|---:|---:|---:|---:|---:|
| **Gold + Silver** | **1402.8244** | **23/33** | **+10.2054** | 15 / 18 | **-0.7379** |
| **CURRENT8** | **1413.0298** | **23/33** | 0 | — | 0 |
| Gold only | 1583.7389 | 22/33 | -170.7091 | 15 / 18 | -2.6637 |
| No Silver | 1589.9368 | 20/33 | -176.9070 | 15 / 18 | -1.7386 |
| Gold+Silver+Platinum | 1736.2615 | 21/33 | -323.2317 | 18 / 15 | +3.1978 |
| No Palladium | 1736.2615 | 21/33 | -323.2317 | 18 / 15 | +3.1978 |
| No Gold | 1795.9566 | 18/33 | -382.9268 | 14 / 19 | -11.8867 |
| MR only | 2187.2832 | 15/33 | -774.2534 | 11 / 22 | -20.1025 |
| VW only | 2304.5555 | 20/33 | -891.5258 | 13 / 20 | -9.3667 |
| No Platinum | 2680.1790 | 21/33 | -1267.1492 | 12 / 21 | -4.4531 |

Notes:
- Gold+Silver lowers total ΣAE by only **0.72%**.
- It improves only **15/33** origins and worsens **18/33**.
- Median paired AE effect is negative; therefore its aggregate gain is concentrated in a minority of months.
- Gold+Silver+Platinum and No-Palladium are mathematically the same retained feature set and reproduce essentially the same result, providing a useful determinism cross-check.
- MR-only and VW-only both fail badly; MR and VW carry complementary information.

## 4. F1 single-feature leave-one-out

Authority:
- run **36535476553**
- runner commit **023ffef8567ae309e5ca83cff8a812808d2f6e9b**
- summary artifact **11018880667**
- artifact digest: `sha256:d38466479f29cec3c24f64ad2ce4b50f71dacd8c1bc98f53d1bbe529df4f10b6`

| Removed feature | DEV ΣAE | Direction | ΔΣAE vs CURRENT8 | Months improved / worsened | Median paired AE improvement |
|---|---:|---:|---:|---:|---:|
| Palladium MR | 1582.1095 | 21/33 | -169.0797 | 15 / 18 | -6.3030 |
| Gold VW | 1764.6486 | 19/33 | -351.6188 | 11 / 22 | -12.0332 |
| Silver VW | 1808.1832 | 22/33 | -395.1534 | 13 / 20 | -4.6374 |
| Palladium VW | 1920.7006 | 17/33 | -507.6708 | 17 / 16 | +0.0759 |
| Gold MR | 4017.9842 | 21/33 | -2604.9544 | 14 / 19 | -5.8331 |
| Silver MR | 4337.6786 | 24/33 | -2924.6488 | 13 / 20 | -8.5420 |
| Platinum MR | 10723.7857 | 18/33 | -9310.7559 | 9 / 24 | -7.7285 |
| Platinum VW | 30823.7420 | 19/33 | -29410.7122 | 15 / 18 | -5.7596 |

## 5. Interpretation

### 5.1 No safe deletion
Every single-feature removal worsens DEV ΣAE. Therefore there is **no evidence for deleting an individual CURRENT8 feature** at F1.

### 5.2 MR and VW are complementary
Both global MR-only and VW-only models deteriorate sharply. The existing two-representation structure is not redundant.

### 5.3 Direction alone can be misleading
Example: removing Silver MR yields **24/33 direction**, higher than CURRENT8's 23/33, but ΣAE explodes to **4337.68**. Direction and price-error objectives must remain jointly visible.

### 5.4 Pathological reduced-input responses are stability evidence
Very large errors after removing Platinum MR/VW or Gold/Silver MR are not interpreted as a literal causal importance score. They show that the current ChHHO-ANFIS optimization/representation is highly sensitive to some reduced-input geometries.

Therefore:
- do not rank feature importance by raw ΣAE explosion magnitude;
- do not infer that Platinum VW is “20× more important” than Palladium MR;
- treat these as **architectural stability diagnostics**.

### 5.5 Gold+Silver is an exploratory compact challenger, not a replacement
Gold+Silver has the lowest aggregate ΣAE in the broad screen (**1402.82**) but:
- improvement is only **0.72%**;
- it worsens more months than it improves;
- median paired benefit is negative.

Status: **INTERESTING_COMPACT_CHALLENGER / NOT_PROMOTED**.

## 6. Binding F1 decision

**CURRENT8 remains the retained feature contract for the next stage.**

No feature is deleted.

The next scientific stage is **F2 representation audit**, not additional combinatorial subset mining.

F2 should ask, within the retained information families:
- whether 1M MR can be improved by 3M/6M momentum or other stationary representations;
- whether VW can be improved/replaced by realized volatility, range, absolute-return activity or causal distributed/MIDAS summaries;
- whether representation improvements can reduce the instability seen in reduced-input ablations.

Gold+Silver may remain a compact control/challenger in F2 but must not replace CURRENT8 based on F1.

## 7. Control and compliance

- F0 parity: **PASS**
- F1 broad ablation: **COMPLETE**
- F1 single-feature ablation: **COMPLETE**
- CURRENT8 retained: **YES**
- 2025 selection/tuning: **NONE**
- 2026 selection/tuning: **NONE**
- External variables: **NONE**
- Lag changes: **NONE**
- Representation changes: **NONE**
- Random split: **NONE**
- Neon reads: **0**
- Next stage: **F2 representation audit**
