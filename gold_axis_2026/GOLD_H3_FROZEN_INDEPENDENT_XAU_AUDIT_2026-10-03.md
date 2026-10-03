# GOLD H3 FROZEN vs INDEPENDENT XAU AUDIT — 2026-10-03

Independent comparator: Neon `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`. The clean frozen series uses only the already-confirmed 2026-02-27 patch; no other values are changed.

## Level consistency

- overlap: **1072** dates
- deviation from normal source ratio >=1%: **193**
- >=2%: **31**
- >=3%: **3**
- >=5%: **0**
- max clean deviation: **4.07%** on **2026-01-30**

## H3 target-direction source sensitivity

- comparable H3 origins: **1003**
- direction disagreements: **206 (20.54%)**
- 2026 comparable origins: **169**
- 2026 direction disagreements: **33 (19.53%)**
- 2026 disagreements where BOTH sources imply >=0.5% absolute H3 move: **7**
- 2026 disagreements where BOTH imply >=1.0% absolute H3 move: **3**

## Yearly

| Year | N | Direction disagreements | % | Both >=0.5% | Both >=1% |
|---:|---:|---:|---:|---:|---:|
| 2022 | 175 | 36 | 20.57% | 11 | 1 |
| 2023 | 188 | 44 | 23.40% | 12 | 0 |
| 2024 | 228 | 48 | 21.05% | 14 | 3 |
| 2025 | 243 | 45 | 18.52% | 15 | 6 |
| 2026 | 169 | 33 | 19.53% | 7 | 3 |

## 2026 disagreement events

| Start | H3 end | Frozen r3 | NY17 r3 | Frozen dir | NY17 dir |
|---|---|---:|---:|---|---|
| 2026-01-05 | 2026-01-08 | -0.104% | +0.642% | DOWN | UP |
| 2026-01-30 | 2026-02-04 | -0.231% | +2.015% | DOWN | UP |
| 2026-02-03 | 2026-02-06 | -1.094% | +0.328% | DOWN | UP |
| 2026-02-04 | 2026-02-09 | -1.180% | +1.859% | DOWN | UP |
| 2026-02-09 | 2026-02-12 | +1.143% | -2.734% | UP | DOWN |
| 2026-02-10 | 2026-02-13 | -1.913% | +0.344% | DOWN | UP |
| 2026-02-13 | 2026-02-18 | +0.975% | -1.312% | UP | DOWN |
| 2026-02-26 | 2026-03-03 | +0.770% | -1.875% | UP | DOWN |
| 2026-03-03 | 2026-03-06 | -1.811% | +1.621% | DOWN | UP |
| 2026-03-09 | 2026-03-12 | +0.089% | -1.155% | UP | DOWN |
| 2026-03-20 | 2026-03-25 | -1.544% | +0.256% | DOWN | UP |
| 2026-03-23 | 2026-03-26 | +1.703% | -0.676% | UP | DOWN |
| 2026-03-25 | 2026-03-30 | -0.803% | +0.102% | DOWN | UP |
| 2026-04-08 | 2026-04-13 | -1.089% | +0.450% | DOWN | UP |
| 2026-04-14 | 2026-04-17 | +0.513% | -0.230% | UP | DOWN |
| 2026-04-15 | 2026-04-20 | -0.227% | +0.614% | DOWN | UP |
| 2026-04-28 | 2026-05-01 | -0.180% | +0.399% | DOWN | UP |
| 2026-04-29 | 2026-05-04 | +0.014% | -0.448% | UP | DOWN |
| 2026-05-07 | 2026-05-12 | -0.236% | +0.550% | DOWN | UP |
| 2026-05-15 | 2026-05-20 | -1.420% | +0.086% | DOWN | UP |
| 2026-05-19 | 2026-05-22 | -0.100% | +0.600% | DOWN | UP |
| 2026-05-28 | 2026-06-02 | +1.492% | -0.171% | UP | DOWN |
| 2026-06-25 | 2026-06-30 | +0.155% | -0.467% | UP | DOWN |
| 2026-07-02 | 2026-07-07 | +1.074% | -0.431% | UP | DOWN |
| 2026-07-07 | 2026-07-10 | -0.564% | +0.321% | DOWN | UP |
| 2026-07-24 | 2026-07-29 | -0.314% | +0.332% | DOWN | UP |
| 2026-07-27 | 2026-07-30 | -0.145% | +0.649% | DOWN | UP |
| 2026-07-29 | 2026-08-03 | +0.339% | -0.286% | UP | DOWN |
| 2026-08-10 | 2026-08-13 | +0.658% | -0.888% | UP | DOWN |
| 2026-08-11 | 2026-08-14 | -0.631% | +0.202% | DOWN | UP |
| 2026-08-12 | 2026-08-17 | -0.060% | +0.172% | DOWN | UP |
| 2026-08-13 | 2026-08-18 | +0.029% | -0.357% | UP | DOWN |
| 2026-08-21 | 2026-08-26 | +0.922% | -0.205% | UP | DOWN |

## Interpretation

Source-time differences can legitimately flip labels when the three-session move is close to zero. Disagreements where both sources show large opposite moves are materially more suspicious and require event-level verification before any model rerun.
