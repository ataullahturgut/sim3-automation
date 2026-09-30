# GOLD MONTHLY — Market Regime Discovery V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Scope:** market-state only; no alarm labels, forecast errors, model forecasts, routing or fallback inputs.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_DISCOVERY_V1_AUTHORITY_2026-09-30.md`
- authority commit: `f30e7a3b70bee75cc194eb6980f11a38c8d121bf`

Execution:
- workflow: **Gold Monthly Market Regime Discovery V1**
- run: **36716979693**
- artifact: **11097041821**
- code commit: `5e4a3e32ce1bb1ad718e9e0049fe0ac8e7e093ad`
- workflow commit: `86917fea4cebaf6ad25623279e96370bcf6b2438`
- artifact digest: `sha256:6bf8455e93ece5dc42f06dc58930a79be2a94ea70f5f3f9da82bff8da752338e`
- scientific gate: **PASS**

## 2. Data and governance

Requested panel:
- 2010-01..2026-08

Effective complete panel:
- **2010-07..2026-08**
- first six requested months are unavailable only because prior-window volatility/level normalization requires warm-up history.

Regime development:
- 2010-07..2024-12
- **174 complete monthly observations**

Frozen transport:
- 2025-01..2026-08
- **20 complete monthly observations**

Market-state features:
- Gold 1m return
- Gold 3m return
- Gold level gap vs prior-12m mean
- Gold realized-volatility ratio
- cross-metal return dispersion
- GVZ ratio
- CFTC Managed Money net/OI
- CFTC OI ratio
- broad USD monthly change
- nominal 10Y change
- real 10Y change
- GLD/IAU combined flow proxy
- ETF outflow breadth

Forbidden from the regime model:
- ChHHO errors
- A/B/C/D/E/G/H/I1/I2/T1
- HIGH/MEDIUM/NORMAL labels
- model forecasts

## 3. Primary HMM evidence

Gaussian HMM BIC:

| K | BIC |
|---:|---:|
| 1 | 3405.30 |
| 2 | 3342.75 |
| **3** | **3334.20** |
| 4 | 3353.59 |
| 5 | 3380.92 |

Primary selected K:
- **3 states**

BIC improvement vs K=1:
- **71.09**

Persistence:
- weighted self-transition probability: **89.20%**
- simple mean self-transition: **89.23%**
- all three states have >=12 development months.

Primary regime-evidence gate:
- **STRONG**

Interpretation:
The 2010-2024 market-state process is not well described as one homogeneous state. A persistent multi-state process is strongly supported.

## 4. Independent GMM robustness

Static Gaussian-mixture BIC:

| K | BIC | Silhouette |
|---:|---:|---:|
| 1 | 3482.68 | — |
| **2** | **3471.36** | **0.258** |
| 3 | 3513.28 | 0.243 |
| 4 | 3574.07 | 0.164 |
| 5 | 3632.00 | 0.123 |

GMM supports:
- **2 coarse clusters**

Therefore the exact count is not uniquely identified across methods:
- static clustering supports **2 broad regimes**;
- persistence-aware HMM supports **3 regimes**.

Binding interpretation:
**at least two distinct market regimes are strongly supported; the primary time-series model favors three persistent states.**

## 5. HMM state profiles

State names below are descriptive labels only.

### R0 — drawdown / macro-pressure / stress state

Development occupancy:
- 45 months
- 25.9%

Typical state means:
- Gold 1m return: **-0.59%**
- Gold 3m return: **-3.42%**
- Gold level gap vs prior-12m mean: **-5.77%**
- Gold RV ratio: **1.223**
- GVZ ratio: **1.122**
- CFTC Managed Money net/OI: **0.087**
- combined ETF flow proxy: **-0.65%**
- broad USD change: **+0.75%**

Dominant deviations:
- low Gold level/trend
- low speculative positioning
- higher volatility/GVZ
- stronger USD / higher real-rate pressure

### R1 — quiet / neutral / low-volatility state

Development occupancy:
- 82 months
- 47.1%

Typical state means:
- Gold 1m return: **+0.14%**
- Gold 3m return: **+0.87%**
- Gold level gap: **+1.67%**
- Gold RV ratio: **0.866**
- GVZ ratio: **0.866**
- CFTC Managed Money net/OI: **0.185**
- combined ETF flow: **-0.12%**

Dominant deviations:
- low realized volatility
- low GVZ
- low cross-metal dispersion
- near-neutral Gold trend.

### R2 — bullish / accumulation / elevated-state regime

Development occupancy:
- 47 months
- 27.0%

Typical state means:
- Gold 1m return: **+1.95%**
- Gold 3m return: **+6.88%**
- Gold level gap: **+12.91%**
- Gold RV ratio: **1.257**
- GVZ ratio: **1.212**
- CFTC Managed Money net/OI: **0.314**
- combined ETF flow proxy: **+2.26%**
- ETF outflow breadth: materially below other states
- nominal and real yields tend to decline.

Dominant deviations:
- elevated Gold level
- strong multi-month Gold momentum
- high speculative positioning
- positive ETF accumulation
- above-normal volatility.

## 6. Persistence and spell lengths

Transition matrix, ordered R0/R1/R2:

- R0 -> R0: **85.6%**
- R1 -> R1: **88.9%**
- R2 -> R2: **93.2%**

Historical development spell statistics:

- R0 median spell: **6 months**, max **9**
- R1 median spell: **4 months**, max **18**
- R2 median spell: **12 months**, max **16**

This persistence is central evidence that the states are regimes rather than month-to-month clusters.

## 7. Historical timeline

Notable R2 spells before transport:
- 2010-11..2012-02 — **16 months**
- 2016-03..2016-09 — 7 months
- 2019-07..2020-09 — **15 months**
- 2024-04..2024-12 — 9 months entering the transport boundary.

R0 dominated much of:
- 2013
- 2015
- much of 2022.

R1 dominated:
- 2017-2018
- 2021
- 2023 through 2024-03.

## 8. 2025 transport

Every month of 2025 is classified:
- **R2 = 12/12**
- R0 = 0
- R1 = 0

Historical 2010-2024 occupancy:
- R0 25.9%
- R1 47.1%
- R2 27.0%

2025 occupancy:
- **R2 100%**

Jensen-Shannon distance versus 2010-2024 occupancy:
- **0.604**

This is a large descriptive shift in regime mix.

However:
2025 is not a newly invented fourth state. It is a continuation of the already-known R2 regime that began in **2024-04**.

The R2 spell continues through **2026-04**, yielding a continuous **25-month R2 spell** from 2024-04 through 2026-04.

This is materially longer than the maximum **16-month** R2 spell observed inside 2010-2024 development.

Binding interpretation:
**2025 represents unusually persistent occupation of an existing bullish/accumulation regime, not clear evidence of a brand-new categorical regime.**

## 9. 2026 Jan-Aug transport

Assignments:

| Month | State | Filtered probability | Historical OOD? |
|---|---|---:|---|
| 2026-01 | R2 | ~1.000 | **YES** |
| 2026-02 | R2 | ~1.000 | **YES** |
| 2026-03 | R2 | ~1.000 | **YES** |
| 2026-04 | R2 | 0.983 | No |
| 2026-05 | R1 | 0.527 | No |
| 2026-06 | R2 | 0.363 | No |
| 2026-07 | R1 | 0.701 | No |
| 2026-08 | R1 | 0.986 | No |

2026 Jan-Aug occupancy:
- R2 **62.5%**
- R1 **37.5%**
- R0 0%

Jensen-Shannon distance versus 2010-2024:
- **0.359**

### OOD result

Months below the 5th percentile of the 2010-2024 fitted-state emission distribution:
- **2026-01**
- **2026-02**
- **2026-03**

Interpretation:
The HMM still recognizes them as R2, but their feature combination is unusually extreme relative to historical R2 observations.

The evidence supports the phrase:
**“extreme R2 / historically unusual state intensity”**

It does **not** yet justify declaring a new R3/fourth regime.

2026-05 onward shows weakening R2 dominance and increasing R1 occupation.
2026-06 is particularly state-ambiguous with only 36.3% posterior on R2.

## 10. Change-point robustness

Multivariate PELT/RBF with fixed penalties:
- 2 log(n)
- 4 log(n)
- 6 log(n)

found no robust discrete break date under these penalties.

Therefore:
- the HMM evidence supports **persistent latent regimes**;
- the data do **not** support a single sharp deterministic structural-break date such as “January 2025”.

This distinction is important.

## 11. Binding conclusion

1. **Yes — statistically persistent Gold market regimes are strongly supported.**
2. Static clustering says at least **2 broad regimes**; the persistence-aware HMM favors **3 states**.
3. The three HMM states are interpretable as:
   - R0 drawdown/macro-pressure/stress,
   - R1 quiet/neutral/low-vol,
   - R2 bullish/accumulation/elevated-state.
4. **2025 is genuinely unusual in regime composition:** 12/12 months were R2 versus only 27% historical R2 occupancy.
5. 2025 appears to be an unusually long continuation of an existing R2 regime, **not a clean new fourth regime**.
6. The R2 spell from 2024-04 through 2026-04 lasts **25 months**, longer than any R2 spell inside 2010-2024 development.
7. **2026-01..03 are historically out-of-distribution even within R2**, indicating unusually extreme state intensity.
8. 2026-05 onward begins moving back toward R1; 2026-06 is state-ambiguous.
9. No alarm selection, alarm weighting or alarm scoring is authorized from this study.
10. The next stage, if opened, may examine alarm behavior conditional on these independently discovered regimes.
