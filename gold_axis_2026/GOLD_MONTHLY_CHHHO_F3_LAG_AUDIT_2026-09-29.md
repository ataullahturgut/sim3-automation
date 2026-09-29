# GOLD MONTHLY — ChHHO-ANFIS F3 Lag Architecture Audit

**Date:** 2026-09-29  
**Status:** COMPLETE / DEV-ONLY / ZERO NEON  
**Decision:** RETAIN L1 CURRENT-ORIGIN LAG CONTRACT

## 1. Scientific question

F0/F1 retained the eight CURRENT8 channels.
F2 retained the MR1 + GPR-conditioned VW representation.

F3 therefore changed only the temporal lag architecture.

Baseline:
- L1 = CURRENT8 from the most recent completed origin month.

Predeclared challengers:
- L1+L2
- L1+L2+L3
- L1/L3/L6
- DL3 equal weighted
- DL3 decay weighted (0.6/0.3/0.1)
- fixed six-lag Beta(1,3)-like monotone weights (36/25/16/9/4/1 normalized)

No external variables and no representation reopening.

## 2. Authority

Main workflow:
- run **36544008921**
- head commit **8d61f80997ddf42328c35027a0013638fdff6121**
- result role: six valid artifacts + one technical serialization failure
- Neon reads: **0**

Targeted L1+L2 recovery:
- run **36545472948**
- head commit **b91f281a99c3553e97bdafe3c47c935ea395e85a**
- artifact **11021484607**
- digest `sha256:f239ad5315a5157abf596cb35fca479dc18ab0c417e0e661bd436dc8702aec07`

The original L1+L2 job completed model computation but failed artifact serialization because a diagnostic condition number was `inf`. Recovery reran the identical deterministic model and mapped only non-finite diagnostic fields to null. Forecasts/metrics were not altered.

Baseline artifact:
- L1 artifact **11021516711**
- digest `sha256:bca2cc369bc9c6d9673970e0d8b322a18ca272dc764555325cc0358928882311`

## 3. F3 results

| Lag architecture | Input dimension | DEV ΣAE | Direction | ΔΣAE vs L1 |
|---|---:|---:|---:|---:|
| **L1 CURRENT8** | 8 | **1413.0299** | **23/33** | — |
| DL3 decay | 8 | 1727.8880 | 17/33 | -314.8581 |
| DL3 equal | 8 | 1912.0261 | 14/33 | -498.9963 |
| L1+L2+L3 | 24 | 1971.3237 | 16/33 | -558.2938 |
| L1/L3/L6 | 24 | 7587.4515 | 16/33 | -6174.4217 |
| L1+L2 | 16 | 9109.1640 | 19/33 | -7696.1341 |
| DL6 Beta13 fixed | 8 | 34407.8023 | 19/33 | -32994.7724 |

L1 parity:
- reference ΣAE: **1413.029779**
- observed: **1413.029855**
- absolute difference: **0.000075**
- direction: **23/33**
- parity: **PASS**

L1+L2 recovery paired statistics:
- months improved: **16**
- months worsened: **17**
- median paired AE improvement: **-1.2175**
- mean paired AE improvement: **-233.2162**
- yearly ΔΣAE vs L1:
  - 2022: **-7564.5403**
  - 2023: **-99.4379**
  - 2024: **-32.1559**

## 4. Interpretation

### 4.1 Direct lag stacking is not useful for ChHHO under the frozen architecture
Increasing CURRENT8 from 8 dimensions to 16 or 24 dimensions materially worsens DEV performance.

This is not interpreted as proof that historical information is economically irrelevant. It shows that raw lag stacking under the current ChHHO-ANFIS capacity/optimizer geometry does not improve forecast performance.

### 4.2 Simple distributed lag smoothing also fails
Equal 3-month smoothing and recency-decay smoothing both worsen ΣAE and direction.

The six-lag fixed Beta-like smoother is highly unstable.

### 4.3 Most recent completed month carries the strongest usable signal
Within this model/representation contract, preserving the most recent completed-origin CURRENT8 block alone is superior to the tested lag extensions.

### 4.4 Do not infer causal irrelevance of older lags
F3 is a predictive architecture test, not a causal test.
Older information may still enter indirectly through:
- GPR-conditioned VW construction;
- external macro/FX/risk variables in F4;
- future architectures specifically designed for sequences.

## 5. Binding decision

**Retain F3 baseline lag architecture: L1 only.**

Frozen ChHHO internal contract entering F4:
- metals: Gold, Silver, Platinum, Palladium;
- representations: MR1 + GPR-conditioned VW;
- temporal lag: current completed origin month only (L1);
- feature count: 8.

No F3 lag challenger is promoted.

Next active stage:
**F4 native external-family integration / feature-value audit.**

Predeclared first external families:
1. inflation / realized CPI;
2. nominal + real rates;
3. FX;
4. Nasdaq / equity risk;
5. VIX;
6. commodity/oil.

Each family must be tested separately before combination.

## 6. Kontrol ve Uyum Özeti

- F3 baseline parity: **PASS**
- tested lag architectures: **7**
- robust promoted challenger: **NONE**
- CURRENT8 L1 retained: **YES**
- representation changed: **NO**
- external features: **NONE**
- 2025 selection/tuning: **NONE**
- 2026 selection/tuning: **NONE**
- random split: **NONE**
- Neon reads: **0**
- next stage: **F4 native external-family integration**
