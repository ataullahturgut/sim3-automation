# GOLD MONTHLY — Unified Alarm Matrix V1 Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Rows:** 58
**Scope:** consolidation only; no new thresholds, no forecast correction, no routing/model switching.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V1_AUTHORITY_2026-09-30.md`
- authority commit: `195a9e13ae8144ad839c58660b23a22f981a7fce`

Execution:
- workflow: **Gold Monthly Unified Alarm Matrix V1**
- run: **36710435526**
- artifact: **11094306282**
- code commit: `e09338ba31b68a55f7509dbef920963678cfac07`
- workflow commit: `e6208e2039080ad36de1350361e3855ed0517265`
- artifact digest: `sha256:58fe779f3a564073697c109717949170c23ce772342f32ae20f9aff8eea6dac8`
- scientific gate: **PASS**

Inputs:
- APE severity V3 artifact 11090497943
- ETF dynamic V2 artifact 11090919621
- WGC T1 V4 artifact 11093192454

Outputs:
- JSON full matrix
- CSV full matrix
- Markdown full matrix

## 2. Binding severity

APE:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

## 3. Signal statuses retained

- A — selective T0 alarm candidate
- B — warning-only
- C — medium-error / low-event warning
- D — rare HIGH hit
- E — discovery-period / unvalidated
- G — high-movement regime warning
- H — CFTC positioning warning
- I1 — ETF transition warning candidate
- I2 — historically supported regime warning
- T1_WGC — early-month report warning

No signal is deleted merely because it is not a hard alarm.

## 4. HIGH-error map

There are **17 HIGH APE targets**.

| Target | APE | Active signals |
|---|---:|---|
| 2021-12 | 4.783% | H |
| 2022-05 | 4.324% | I1 |
| 2022-07 | 3.748% | I2, T1_WGC |
| 2022-09 | 3.509% | I2, T1_WGC |
| 2022-11 | 5.925% | A, I2, T1_WGC |
| 2023-01 | 5.308% | B, T1_WGC |
| 2023-08 | 4.040% | A, I2, T1_WGC |
| 2024-03 | 6.098% | I2, T1_WGC |
| 2024-11 | 4.494% | D |
| 2025-02 | 3.947% | H |
| 2025-03 | 3.991% | B |
| 2025-09 | 7.864% | A |
| 2025-10 | 5.079% | H |
| 2025-11 | 4.011% | E |
| 2026-01 | 9.647% | E |
| 2026-06 | 8.566% | **NONE** |
| 2026-08 | 7.889% | G |

Key consolidation result:
- **16/17 HIGH months have at least one visible A..I2 or T1_WGC signal.**
- **Only 2026-06 is completely signal-free in the currently frozen matrix.**

This 16/17 figure is descriptive visibility, not validated hard-alarm recall, because E/G/I carry different evidence statuses.

## 5. Blind spots by evidence layer

### Standard T0 A/B/C/D/H only

No standard T0 signal:
- 2022-05
- 2022-07
- 2022-09
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

=> standard T0 covers 9/17 HIGH = 52.9%.

### All visible T0 A/B/C/D/E/G/H/I1/I2

No visible T0 signal:
- **2026-06 only**

=> descriptive visibility 16/17 HIGH = **94.1%**.

This is not a hard-alarm performance number because E/G/I are not equally validated.

### All visible T0 + T1

Still no signal:
- **2026-06 only**

T1 does not reduce the final all-visible blind spot further because the T1 incremental hits 2022-07, 2022-09, and 2024-03 are already visible through I2 at T0.

Operationally, however, T1 is useful as an official early-month confirmation channel.

## 6. Signal-by-signal HIGH statistics

| Signal | Events | HIGH hits | MEDIUM hits | Normal false alarms | HIGH precision |
|---|---:|---:|---:|---:|---:|
| A | 5 | 3 | 0 | 2 | 60.0% |
| B | 4 | 2 | 0 | 2 | 50.0% |
| C | 1 | 0 | 1 | 0 | 0.0% |
| D | 1 | 1 | 0 | 0 | 100.0% |
| E | 4 | 2 | 2 | 0 | 50.0% |
| G | 3 | 1 | 0 | 2 | 33.3% |
| H | 9 | 3 | 3 | 3 | 33.3% |
| I1 | 2 | 1 | 0 | 1 | 50.0% |
| I2 | 12 | 5 | 0 | 7 | 41.7% |
| T1_WGC | 23 | 6 | 2 | 15 | 26.1% |

Interpretation:
- A is selective but low-coverage.
- D is a single-event perfect hit and cannot be generalized.
- E looks clean descriptively but is discovery-period/unvalidated.
- I2 has the strongest historical external-regime support among ETF alarms but carries false alarms.
- T1_WGC is noisy standalone but useful as an official first-week confirmation channel.
- H catches a distinct positioning mechanism.
- G remains regime warning, not ChHHO error alarm.
- I1 specifically surfaces 2022-05 but lacks broad historical support.

## 7. Medium-error rows

MEDIUM:
- 2022-01 — no signal
- 2022-02 — T1_WGC
- 2024-04 — H + T1_WGC
- 2024-07 — C + H
- 2025-01 — no signal
- 2025-05 — E
- 2026-03 — E + H

This confirms C belongs naturally in medium-error/risk-warning space under APE severity.

## 8. Binding conclusion

1. A/B/C/D/E/G/H/I1/I2/T1_WGC all remain in the research architecture.
2. They do **not** have equal validation status.
3. Standard T0 hard/standardized coverage remains 9/17 HIGH.
4. When all visible warning/regime signals are retained, 16/17 HIGH months show at least one origin/early-month signal.
5. The single fully blind HIGH month is **2026-06 (APE 8.566%)**.
6. The next alarm-research priority is therefore 2026-06, without weakening existing thresholds merely to catch it.
7. No forecast correction or router/model switching is authorized.
