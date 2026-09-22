# GOLD CONTROL — External Dukascopy / pre-2022 full method audit V2

**Date:** 2026-09-22  
**Identity:** `EXTERNAL_DUKASCOPY_SESSIONMASK_V2_METHOD_AUDIT`  
**Preregistration:** `77f6fe1856a3e2349bbf8f8f6e1dfbead7e50202`  
**Final status:** `METHOD_AND_DATA_AUDIT_PASSED_AFTER_SESSION_CORRECTION; HARD_VETO_FAILURE_CONFIRMED`

## 1. A real construction mismatch was found

The audit found that the governed internal 5-minute source has **276 recurring local-time bars/day**, not 288.

The governed source consistently omits:

**17:00–17:55 America/New_York**

The first external V1 spine had retained those twelve five-minute bins and therefore showed 288 bars on normal days.

This is a genuine loading/construction mismatch. It was corrected before further interpretation.

The correction was determined from the governed source clock, not from model outcomes.

## 2. Corrected external spine

The older source was rebuilt from the raw mirrored one-minute bid/ask files:

- exact bid/ask timestamp inner join;
- mid close;
- last close per five-minute bin;
- America/New_York conversion;
- 17:00–17:55 local maintenance hour excluded;
- weekday grouping;
- zero-variance synthetic holiday rows removed.

Corrected consolidated panel:
- 2018: 260 days
- 2019: 260
- 2020: 260
- 2021: 258
- total: **1038**
- duplicates: **0**
- unsorted rows: **0**
- bad/nonfinite rows: **0**
- zero-RV retained rows: **0**
- bars per retained day: **276 exactly**

Corrected artifact:
`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`

## 3. Source harmonization after correction

Exact overlap with the governed cache remains extremely strong:

- exact overlap: **345 / 345 = 100%**
- close-return Pearson: **0.9999746**
- return-sign agreement: **99.42%**
- RV Spearman: **0.99753**
- downside-RV Spearman: **0.99699**
- external/governed mean RV ratio: **0.99664**
- external/governed mean downside-RV ratio: **0.99608**
- top-quintile downside-risk state agreement: **99.42%**

The harmonization gate still passes.

## 4. Frozen SQRT implementation reproduction

The SQRT-HAR-DR reconstruction code was independently run on the governed source and compared with the frozen 2022–2024 parent artifact.

Across **613 rows**:
- target-date mismatch: **0**
- high-risk alert mismatch: **0**
- next-return sign mismatch: **0**
- max SQRT-DR forecast difference: **4.93e-18**
- max normalized-score difference: **7.82e-14**
- high-risk-threshold difference: **0**

Therefore the external-extension parent implementation is numerically the frozen method.

## 5. Direct-expert / Router reproduction

The previous exact reconstruction audit remains valid:

- 2023/2024 target-date mismatch: 0
- actual-direction mismatch: 0
- TTSM UP mismatch: 0
- Bonato h=1 median-UP mismatch: 0
- RM_LOGIT mismatch: 0
- AR1_RM_LOGIT mismatch: 0

Frozen 2024 Router:
- n=205
- Router UP=42
- TP=26
- FP=16
- precision=61.90%
- false-UP FPR=18.60%

reproduced exactly.

## 6. Corrected pre-2022 rerun

After the 276-bar session correction, the full 2020/2021 reconstruction was rerun.

The results are **unchanged** from the first external stress test:

| year | SQRT alarms | Router overlap | good suppress | bad suppress | true-DOWN retention |
|---|---:|---:|---:|---:|---:|
| 2020 | 212 | 140 | 80 | **60** | **38.14%** |
| 2021 | 28 | 2 | 1 | 1 | **93.75%** |

So the severe 2020 result is **not caused by the 288-vs-276 loading mismatch**.

## 7. Pooled hard-veto safety result remains

2020–2024:
- SQRT alarms=270
- actual DOWN=127
- actual UP=143
- suppressions=146
- good=84
- bad=62
- suppression precision=57.53%
- empirical BAD_SUPPRESSION rate among true DOWN alarms=**48.82%**
- true-DOWN retention=**51.18%**
- false-alarm reduction=58.74%
- remaining forced-DOWN precision=52.42%

At alpha=20%, delta=10%, the exact one-sided safety p-value is approximately **1.0000**.

The universal hard veto is therefore decisively not risk-certified.

## 8. Remaining provenance limitation

The older minute history is a public GitHub mirror whose README states that it was downloaded from Dukascopy through `dukascopy-node`.

This audit did not independently redownload every minute directly from Dukascopy.

However the 2020–2021 overlap against the governed internal source is near-exact, which provides strong empirical source validation for research use.

The external spine remains **research-only**, not production authority.

## 9. Binding conclusion

One real data-construction mismatch was found and corrected.

After correction:
- data integrity passes;
- source harmonization passes;
- SQRT method reproduction passes;
- direct-expert/Router reproduction passes;
- the 2020 crisis-regime hard-veto failure remains unchanged.

Therefore the failure is not currently attributable to a loading, clock, formula or implementation bug.

For model use, **V1 external 288-bar spine is superseded by V2 276-bar session-masked spine**.
