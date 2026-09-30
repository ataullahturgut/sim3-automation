# GOLD MONTHLY — Alarm Fine-Tuning V1 + Untouched 2025/2026 Transport Result

**Date:** 2026-09-30  
**Status:** COMPLETE / FINE-TUNED RED REJECTED ON TRANSPORT  
**Scope:** alarm detection only; no forecast correction, no routing/model switching.

## 1. Design

Fine-tune authority:
- DEV only: 2022-04..2024-12, 33 rows.
- 2025 and 2026 outcomes were not used in selection.

Authority:
- `gold_axis_2026/GOLD_MONTHLY_ALARM_FINE_TUNING_V1_AUTHORITY_2026-09-30.md`
- authority commit: `c7bc33ed6956d6a7af7943d5929aadbe794129de`

DEV fine-tune:
- workflow: **Gold Monthly Alarm Fine Tuning V1**
- run: **36714696050**
- artifact: **11095407918**
- code commit: `484fc5db9e3564fca0092e53e192d82a63cf4716`
- workflow commit: `0e403d766668ccd87007d3f508d85adba3783c21`
- scientific gate: **PASS**

Untouched transport:
- workflow: **Gold Monthly Alarm Fine Tuning V1 Transport 2025 2026**
- run: **36714849672**
- artifact: **11095058554**
- code commit: `c59f27c635e3473b923fd12bb894ced5039ca4b9`
- workflow commit: `5ce20054c79468f4f7f761c289c8014652aa7201`
- artifact digest: `sha256:a890471a6174fedb29dbafe52e2c03cbab832d12c0f66b6e7631bd75f1a70604`
- scientific gate: **PASS**

## 2. Frozen DEV-selected configuration

T0 RED:
- **A OR D OR I1 OR I2**

T1 RED confirmation:
- **T1_WGC AND (B OR I2)**

FINAL RED:
- **T0_RED OR T1_RED_CONFIRM**

Non-RED channels retained:
- AMBER_T0 = B OR C OR H
- SHADOW_T0 = E OR G

No underlying alarm definition was changed.

## 3. DEV fine-tune performance

### T0 RED
- events: 13
- HIGH hits: 7/8
- HIGH recall: **87.5%**
- MEDIUM hits: 0
- false calls: 6
- false-call rate: **46.2%**

Missed HIGH:
- 2023-01

### T1 RED confirmation
- events: 13
- HIGH hits: 6/8
- false calls: 7
- false-call rate: **53.8%**

### FINAL RED
- events: 15
- HIGH hits: **8/8**
- HIGH recall: **100%**
- false calls: **7**
- false-call rate: **46.7%**

DEV false calls:
- 2022-08 — APE 2.031%
- 2022-10 — 0.193%
- 2022-12 — 1.755%
- 2023-02 — 1.566%
- 2023-09 — 0.281%
- 2023-10 — 1.853%
- 2023-11 — 0.624%

On DEV the sparse tuned rule looked substantially cleaner than the raw ANY_VISIBLE map while retaining all HIGH errors.

## 4. Untouched 2025 result

2025 has 5 HIGH APE months.

FINAL RED:
- events: **2**
- HIGH hits: **1/5**
- HIGH recall: **20.0%**
- MEDIUM hits: 0
- false calls: **1**
- false-call rate: **50.0%**

True RED hit:
- **2025-09 — A — APE 7.864%**

False RED call:
- **2025-12 — A — APE 2.166%**

Missed HIGH by tuned RED:
- **2025-02 — H — APE 3.947%**
- **2025-03 — B — APE 3.991%**
- **2025-10 — H — APE 5.079%**
- **2025-11 — E — APE 4.011%**

T1_RED_CONFIRM:
- no events
- no incremental HIGH hit.

Raw comparison, 2025:
- RAW_T0_STANDARD: 4/5 HIGH, 1 false call.
- RAW_ANY_VISIBLE: **5/5 HIGH**, 1 MEDIUM, 1 false call.

Therefore DEV fine-tuning materially worsened 2025 performance.

## 5. Untouched 2026 Jan-Aug result

2026 Jan-Aug has 3 HIGH APE months.

FINAL RED:
- events: **2**
- HIGH hits: **0/3**
- HIGH recall: **0%**
- MEDIUM hits: 0
- false calls: **2**
- false-call rate: **100%**

False RED calls:
- **2026-04 — I1 — APE 0.608%**
- **2026-07 — I2 + T1_WGC (plus G shadow) — APE 2.030%**

Missed HIGH:
- **2026-01 — E — APE 9.647%**
- **2026-06 — no frozen signal — APE 8.566%**
- **2026-08 — G — APE 7.889%**

T1_RED_CONFIRM:
- 2026-07 only
- false call
- no incremental HIGH hit.

Raw comparison, 2026:
- RAW_T0_STANDARD: 0/3 HIGH, one MEDIUM hit (2026-03), no false calls.
- RAW_ANY_VISIBLE: **2/3 HIGH**, one MEDIUM hit, two false calls.
- only remaining raw blind HIGH: 2026-06.

## 6. Combined untouched 2025 + 2026

20 targets:
- HIGH = 8

FINAL RED:
- events: **4**
- HIGH hits: **1/8**
- HIGH recall: **12.5%**
- MEDIUM hits: 0
- false calls: **3**
- false-call rate: **75.0%**
- useful-call rate: **25.0%**

False calls:
- 2025-12 — 2.166%
- 2026-04 — 0.608%
- 2026-07 — 2.030%

Missed HIGH:
- 2025-02
- 2025-03
- 2025-10
- 2025-11
- 2026-01
- 2026-06
- 2026-08

RAW_T0_STANDARD combined:
- 4/8 HIGH
- one MEDIUM
- one false
- HIGH recall 50.0%
- false-call rate 16.7%

RAW_ANY_VISIBLE combined:
- **7/8 HIGH**
- two MEDIUM
- three false
- HIGH recall **87.5%**
- false-call rate **25.0%**
- only missed HIGH: 2026-06.

## 7. Month-by-month 2025/2026 alarm tracking

| Target | APE | Severity | Active raw signal(s) | Tuned RED result |
|---|---:|---|---|---|
| 2025-01 | 2.926% | MEDIUM | — | OFF |
| 2025-02 | 3.947% | HIGH | H | MISSED |
| 2025-03 | 3.991% | HIGH | B | MISSED |
| 2025-04 | 0.896% | NORMAL | — | OFF |
| 2025-05 | 2.727% | MEDIUM | E | OFF / SHADOW |
| 2025-06 | 0.289% | NORMAL | — | OFF |
| 2025-07 | 1.290% | NORMAL | — | OFF |
| 2025-08 | 0.469% | NORMAL | — | OFF |
| 2025-09 | 7.864% | HIGH | A | **HIGH HIT** |
| 2025-10 | 5.079% | HIGH | H | MISSED |
| 2025-11 | 4.011% | HIGH | E | MISSED / SHADOW |
| 2025-12 | 2.166% | NORMAL | A | **FALSE CALL** |
| 2026-01 | 9.647% | HIGH | E | MISSED / SHADOW |
| 2026-02 | 0.904% | NORMAL | — | OFF |
| 2026-03 | 2.999% | MEDIUM | E + H | OFF / AMBER+SHADOW |
| 2026-04 | 0.608% | NORMAL | I1 | **FALSE CALL** |
| 2026-05 | 1.201% | NORMAL | — | OFF |
| 2026-06 | 8.566% | HIGH | — | **MISSED / BLIND** |
| 2026-07 | 2.030% | NORMAL | G + I2 + T1_WGC | **FALSE CALL** |
| 2026-08 | 7.889% | HIGH | G | MISSED / SHADOW |

## 8. Root cause of fine-tune failure

DEV sparse selection favored:
- I1
- I2
- A
- D

because these mechanisms covered the 2022-2024 HIGH months with fewer DEV false calls.

But the error mechanism shifted in 2025/2026:
- 2025-02 / 2025-10 -> H
- 2025-03 -> B
- 2025-11 / 2026-01 -> E
- 2026-08 -> G
- 2026-06 -> no current signal

Therefore sparse signal deletion produced severe **regime overfit**.

The test demonstrates that mechanisms that looked redundant or noisy in DEV can become the only useful warning channel later.

## 9. Binding decision

**REJECT the V1 fine-tuned sparse RED configuration for operational use.**

Do not replace the current multi-signal architecture with:
- A/D/I1/I2-only T0 RED, or
- T1 gated by B/I2.

Maintain the individual alarm channels and their evidence statuses.

Current evidence favors:
- transparent multi-signal tracking;
- false-call accounting per signal;
- confidence/status tiers;
- not sparse DEV-only signal selection.

The 2025/2026 transport set is now opened and must not be reused as an untouched test for another tuned rule.

No forecast correction.
No routing/model switching.
