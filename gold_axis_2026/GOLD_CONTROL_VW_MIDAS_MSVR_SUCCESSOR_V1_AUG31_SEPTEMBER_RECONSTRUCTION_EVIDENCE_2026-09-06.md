# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 AUG31 → SEPTEMBER RECONSTRUCTION EVIDENCE

Date calculated: 2026-09-06
Model: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Evidence class: `ORIGIN_RECONSTRUCTION_HISTORICAL_REPLAY`
Forecast origin: `2026-08-31`
Target month: `2026-09`
Prospective claim: `false`

## 1. Result

September 2026 monthly-average XAU/USD forecast:

`4565.115907930242 USD/oz`

Same-origin Random Walk / August reconstruction anchor:

`4404.829230769231 USD/oz`

Predicted Gold log return:

`0.03574241278838995`

Equivalent predicted return from the August anchor:

`+3.6388851590739124%`

Selected MSVR configuration under the frozen nested rule:

- `C = 1.0`
- `epsilon = 0.05`
- `gamma_scale = 0.5`

Inner eligible forecasts used for configuration selection: `53`
Inner mean absolute Gold log-return error: `0.027648725225022503`
Final training rows: `198`

## 2. August 2026 four-metal reconstruction panel

Source identity:

`MYFXBOOK_FOUR_METAL_AUG31_RECONSTRUCTION_V1`

Frozen local source snapshot:

`gold_axis_2026/data_pipeline/myfxbook_four_metal_august_2026_reconstruction_snapshot.csv`

Common four-metal August dates:

- count: `26`
- first: `2026-08-02`
- last: `2026-08-31`

August common-date arithmetic means:

- Gold: `4404.829230769231`
- Silver: `65.10876923076923`
- Platinum: `1775.5576923076926`
- Palladium: `1345.8165384615384`

No September observations were used in model fitting, hyperparameter selection, scaling, or feature construction.

## 3. Myfxbook ↔ StakTrakr source-continuity bridge

Reference StakTrakr commit:

`ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

Direct overlap window: `2026-08-02 .. 2026-08-19`
Exact common four-metal dates: `16`

All preregistered bridge gates passed.

| Metal | Median daily APE | P95 daily APE | Mean APE | Gate |
|---|---:|---:|---:|---|
| Gold | `0.7473732740932566%` | `2.387937262084888%` | `0.9084237140301106%` | PASS |
| Silver | `0.7433434112300541%` | `3.1653426082517013%` | `1.1899834073697315%` | PASS |
| Platinum | `0.910806788620025%` | `3.181575342128517%` | `1.2990685808825306%` | PASS |
| Palladium | `0.7058320418587598%` | `2.981909560467102%` | `1.076692916413218%` | PASS |

The bridge was frozen before any successful forecast output. Earlier engineering runs failed before producing a forecast because Myfxbook denied direct GitHub Actions HTML requests with HTTP 403. The successful run used the already frozen August reconstruction snapshot and the exact commit-pinned StakTrakr overlap only.

## 4. GPR/PIT input

GPR identity:

`GPR_OFFICIAL_GIT_PIT`

Origin vintage:

`2026-08`

Frozen publication-lag observation used for the August-origin feature:

`2026-07`

No final/current GPR substitution was made.

## 5. Execution evidence

Successful workflow run:

`34025082641`

Workflow head SHA:

`4df61bced54207f8fe13149139065a22365d7120`

Conclusion:

`SUCCESS`

Artifact ID:

`9986790210`

Artifact digest:

`sha256:ad0b687be0395e4acdc492bf37fde08be12345c838bebbb5429c309687722201`

## 6. Production safety verification after reconstruction

Independent production Neon verification after the successful run:

- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`
- current governed runtime: `ACTIVE 6 / WAITING 5 / BLOCKED 1`

No production database write, forecast-authority write, decision write, runtime mutation, selector activation, or ensemble activation occurred.

## 7. Interpretation

This is the September 2026 current-month H=1 reference produced from the completed 31-August information boundary using the separately governed `VW_MIDAS_MSVR_SUCCESSOR_V1` reconstruction lane.

It is valid as:

`EYLÜL 2026 · 31 AĞUSTOS ORIGIN`

with secondary audit wording equivalent to:

`31 Ağustos bilgi setiyle 6 Eylül'de yeniden hesaplandı`

It is NOT evidence that the forecast was actually issued on 31 August and must not be backdated as a prospective issuance.
