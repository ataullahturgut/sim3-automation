# GOLD H3 — Databento ↔ Frozen Yahoo Source Bridge V2 — 2026-10-05

**Status:** **SOURCE_BRIDGE_V2_REQUIRES_REVIEW**  
V2 estimated additional Databento cost: **USD 1.3926** (ceiling USD 1.60).  
V2 fixes V1 alias-deduplication by requesting each roll family separately.

## Full and non-roll source agreement

| Root | Roll | Cov | Full r1 corr | Full sign | Full MAE bps | Non-roll exact px | NR r1 corr | NR sign | NR MAE bps | NR r3 | NR r6 | NR vol corr | Score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CL | c | 99.23% | 0.979186 | 98.271% | 1.9296 | 90.036% | 0.986419 | 98.546% | 1.3934 | 0.989910 | 0.990897 | — | 0.978837 |
| CL | v | 99.88% | 0.976447 | 98.059% | 1.9089 | 90.826% | 0.983270 | 98.495% | 1.4993 | 0.988109 | 0.989483 | — | 0.978246 |
| CL | n | 99.86% | 0.763911 | 95.904% | 5.2777 | 65.004% | 0.975970 | 96.297% | 3.1694 | 0.982850 | 0.984494 | — | 0.866051 |
| GC | v | 99.86% | 0.975849 | 99.085% | 0.8586 | 93.814% | 0.981859 | 99.290% | 0.6529 | 0.991830 | 0.994642 | 0.93272 | 1.020604 |
| GC | n | 99.88% | 0.976150 | 99.065% | 0.8534 | 90.058% | 0.979982 | 99.142% | 0.7490 | 0.989371 | 0.992594 | 0.89826 | 1.016926 |
| GC | c | 40.88% | 0.875806 | 80.507% | 16.2494 | 0.143% | 0.857247 | 79.621% | 17.0634 | 0.951524 | 0.975530 | 0.17945 | 0.784935 |
| NQ | v | 99.88% | 0.977567 | 98.923% | 0.6782 | 84.843% | 0.986221 | 99.047% | 0.5136 | 0.994148 | 0.996262 | — | 0.980119 |
| NQ | n | 99.88% | 0.976628 | 98.913% | 0.7030 | 84.335% | 0.983540 | 99.025% | 0.5680 | 0.993245 | 0.995145 | — | 0.979243 |
| NQ | c | 99.48% | 0.978711 | 98.939% | 0.6742 | 81.932% | 0.980821 | 98.948% | 0.6350 | 0.992879 | 0.995336 | — | 0.978198 |
| SI | v | 99.82% | 0.969684 | 98.861% | 1.5639 | 94.540% | 0.971357 | 99.057% | 1.2989 | 0.989536 | 0.994294 | 0.93310 | 1.018123 |
| SI | n | 99.88% | 0.970458 | 98.537% | 1.7532 | 86.076% | 0.970811 | 98.695% | 1.6157 | 0.989150 | 0.993909 | 0.86858 | 1.010556 |
| SI | c | 26.63% | 0.852622 | 79.756% | 41.2082 | 0.321% | 0.842787 | 78.164% | 44.6054 | 0.946465 | 0.976414 | 0.19289 | 0.748665 |
| ZN | n | 99.88% | 0.992141 | 98.049% | 0.1347 | 97.282% | 0.994687 | 98.303% | 0.1108 | 0.998189 | 0.999052 | — | 0.990460 |
| ZN | v | 99.88% | 0.991576 | 97.998% | 0.1426 | 97.199% | 0.993737 | 98.362% | 0.1074 | 0.996953 | 0.997771 | — | 0.990103 |
| ZN | c | 90.12% | 0.951106 | 94.166% | 0.6541 | 80.854% | 0.957941 | 94.152% | 0.6272 | 0.984906 | 0.991575 | — | 0.945729 |

## Frozen mapping candidate

| Root | Winner | Gate | Coverage | NR exact px | NR r1 corr | NR sign | NR MAE bps |
|---|---|---|---:|---:|---:|---:|---:|
| GC | **GC.v.0** | **False** | 99.86% | 93.814% | 0.981859 | 99.290% | 0.6529 |
| SI | **SI.v.0** | **False** | 99.82% | 94.540% | 0.971357 | 99.057% | 1.2989 |
| NQ | **NQ.v.0** | **False** | 99.88% | 84.843% | 0.986221 | 99.047% | 0.5136 |
| ZN | **ZN.n.0** | **False** | 99.88% | 97.282% | 0.994687 | 98.303% | 0.1108 |
| CL | **CL.c.0** | **False** | 99.23% | 90.036% | 0.986419 | 98.546% | 1.3934 |

## Governance

- V1 is not used for roll selection because one combined request caused alias attribution/deduplication.
- V2 selection uses only frozen Yahoo vs Databento source agreement.
- ±30 hours around Databento contract switches are excluded only for the non-roll identity diagnostic; full-window metrics remain reported.
- No RESCUE/BROKEN labels, forecast correctness, Q95/Q99 outcomes or threshold tuning enter this bridge.
- Raw Databento observations are processed in-memory and are not committed.
