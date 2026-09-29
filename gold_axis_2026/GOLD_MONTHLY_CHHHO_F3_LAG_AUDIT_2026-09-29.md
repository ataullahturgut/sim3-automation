# GOLD MONTHLY — ChHHO-ANFIS F3 Lag Architecture Audit

**Date:** 2026-09-29  
**Status:** COMPLETE / DEV-ONLY / ZERO NEON  
**Decision:** RETAIN L1 CURRENT8; NO LAG CHALLENGER PROMOTED

## 1. Scientific question

After F0-F2 retained CURRENT8 with MR1 + GPR-conditioned VW, F3 tested whether adding or distributing older completed-month information improves the same ChHHO-ANFIS architecture.

Tested lag structures:
- L1 = current completed origin month (baseline)
- L1+L2
- L1+L2+L3
- L1/L3/L6
- DL3_EQUAL
- DL3_DECAY
- DL6_BETA13_FIXED

No external variables. No representation re-opening. 2025/2026 excluded from selection.

## 2. Authority

Primary run:
- run **36544008921**
- head commit **8d61f80997ddf42328c35027a0013638fdff6121**
- valid artifacts:
  - L1: **11021516711**
  - DL3_EQUAL: **11022068014**
  - DL3_DECAY: **11021554496**
  - DL6_BETA13_FIXED: **11022033826**
  - L1_L2_L3: **11021739503**
  - L1_L3_L6: **11021849520**

L1+L2 first serialization attempts:
- **TECHNICAL_FAILURE / NOT MODEL EVIDENCE**
- reason: non-finite diagnostic field could not be serialized to strict JSON.

Authoritative L1+L2 recovery:
- run **36545472948**
- artifact **11021484607**
- digest `sha256:f239ad5315a5157abf596cb35fca479dc18ab0c417e0e661bd436dc8702aec07`
- gate: **PASS**

Neon reads: **0**

## 3. Results

| Lag architecture | Input dim | DEV ΣAE | Direction | ΔΣAE vs L1 |
|---|---:|---:|---:|---:|
| **L1 CURRENT8** | 8 | **1413.0299** | **23/33** | — |
| DL3_DECAY | 8 | 1727.8880 | 17/33 | -314.8581 |
| DL3_EQUAL | 8 | 1912.0261 | 14/33 | -498.9963 |
| L1+L2+L3 | 24 | 1971.3237 | 16/33 | -558.2938 |
| L1/L3/L6 | 24 | 7587.4515 | 16/33 | -6174.4217 |
| L1+L2 | 16 | 9109.1640 | 19/33 | -7696.1341 |
| DL6_BETA13_FIXED | 8 | 34407.8023 | 19/33 | -32994.7724 |

L1 parity:
- observed ΣAE **1413.0298545**
- direction **23/33**
- parity gate: **PASS**

L1+L2 paired recovery diagnostics:
- months improved: **16**
- months worsened: **17**
- median paired AE improvement: **-1.2175**
- mean paired AE improvement: **-233.2162**
- yearly ΔΣAE vs L1:
  - 2022: **-7564.54**
  - 2023: **-99.44**
  - 2024: **-32.16**

## 4. Interpretation

### 4.1 Extra monthly lags do not help
Every tested lag challenger worsens aggregate DEV error relative to L1.

### 4.2 Concatenated lag expansion is unstable
The 16D and 24D variants materially deteriorate, indicating that simply adding older CURRENT8 blocks increases dimensionality without reliable predictive gain under the frozen ChHHO-ANFIS capacity/optimizer contract.

### 4.3 Fixed distributed-lag compression also fails
Equal, decayed and 6-month fixed beta-like weighting all underperform L1. The model appears to benefit from the most recent completed-month state more than from fixed smoothing across older months.

### 4.4 No lag challenger satisfies promotion criteria
There is no candidate with lower aggregate ΣAE than L1, so the robustness gate necessarily fails before considering secondary conditions.

## 5. Binding decision

**Retain L1 CURRENT8 as the lag architecture.**

Frozen internal contract after F3:
- feature set: CURRENT8
- representation: MR1 + GPR-conditioned VW
- lag architecture: L1 only

No extra monthly lags and no fixed distributed-lag compression are promoted.

The next active stage is **F4 external-family native integration**, beginning with single-family tests while keeping the internal CURRENT8/MR1+VW/L1 contract frozen.

Recommended F4 order:
1. rates
2. FX
3. Nasdaq monthly
4. VIX
5. realized CPI
6. oil/commodity

Each family must be tested independently first; combinations only after independent evidence.

## 6. Kontrol ve Uyum Özeti

- F3 lag variants: **7/7 scientifically resolved**
- L1 parity: **PASS**
- promoted lag challenger: **NONE**
- CURRENT8 retained: **YES**
- MR1+VW retained: **YES**
- L1 retained: **YES**
- external features: **NONE**
- 2025 selection/tuning: **NONE**
- 2026 selection/tuning: **NONE**
- random split: **NONE**
- Neon reads: **0**
- next stage: **F4 external-family native integration**
