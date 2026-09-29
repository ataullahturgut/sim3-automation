# GOLD MONTHLY — F4 HIERARCHICAL EXTERNAL INFORMATION INTEGRATION CHARTER

**Freeze date:** 2026-09-29  
**Status:** BINDING BEFORE F4 OUTCOME REVIEW  
**Scope:** ChHHO-ANFIS native external integration only  
**Internal baseline frozen:** CURRENT8 + MR1 + GPR-conditioned VW + L1

## 1. Purpose

F4 does **not** add external variables one by one and select on outer DEV outcomes.

Each economic family is treated as a small expert module:
1. freeze a compact economically motivated candidate set;
2. fit each candidate natively inside ChHHO using only pre-target history;
3. choose BASE or one candidate for each outer origin using only chronological inner-validation fitness;
4. evaluate the resulting family module on the 33 untouched DEV origins;
5. promote a family only if the family-level outer robustness gate passes;
6. combine only independently promoted families in a later compact-combination stage.

No bad-month-driven feature invention is allowed after F4 results are observed.

## 2. Authority and chronology

- Target: next-calendar-month average Gold price via Gold log-return.
- DEV outer origins: 2022-04..2024-12, n=33.
- 2025: locked transport/reporting only after F4 specification freeze.
- 2026: reporting/quarantine only.
- Random split: NONE.
- Inner selection: chronological validation tail inside each outer-origin training sample.
- Baseline architecture/optimizer/rule count: frozen ChHHO-ANFIS.
- Baseline internal inputs: CURRENT8 MR1+VW L1.
- External block size: maximum **2 native external features** per candidate, except explicitly documented 1-feature controls.
- BASE is always a candidate in the inner family selector.
- Family promotion is judged on outer DEV only; no 2025 feedback.

## 3. Data authority

### Internal
- frozen DEV snapshot artifact 10985453248
- canonical payload SHA256 2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb

### External
Direct external store:
- run 36533719167
- artifact 11018030682
- artifact digest sha256:9181d4a8a346d9594ec5105ae23ed9c7251b463cfd60064a55fbda0fc819af48
- payload SHA256 c52670ccf7bccc75e7c92e6d8261fe25d2d8c62b986300d45d5f264a26142353
- Neon reads: 0

Availability rules:
- Fed H.15 rates: use observations available no later than origin month-end minus **2 calendar days**.
- Fed H.10 FX: use observations available no later than origin month-end minus **7 calendar days**.
- Cboe VIX: origin month-end market observations allowed.
- Nasdaq monthly CORE5: completed origin-month monthly value allowed; daily Nasdaq is NOT_PROVEN and prohibited.
- BLS CPI: at an origin month-end, use at most **previous calendar month's CPI observation**; same-month CPI is not allowed.
- World Bank commodity: use at most **previous calendar month's published monthly observation** as a conservative release rule.
- CPI survey-consensus surprise long history: NOT_PROVEN / prohibited in native F4.

## 4. Family candidate freeze

### F4-RATES

Raw authority:
- 10Y nominal Treasury constant maturity (H.15)
- 10Y real Treasury yield (H.15)
- breakeven proxy = nominal10 - real10
- Fed Funds monthly CORE5, lagged one extra month for publication safety

Origin-safe transforms:
- `nom10_chg`: last-known nominal10 at origin cutoff minus last-known previous-month cutoff
- `real10_chg`
- `be10_chg`
- `ff_lagged_chg`: FedFunds[p-1] - FedFunds[p-2]

Predeclared native candidates:
- R_NOM10 = [nom10_chg]
- R_REAL10 = [real10_chg]
- R_BE10 = [be10_chg]
- R_NOM_REAL = [nom10_chg, real10_chg]
- R_REAL_BE = [real10_chg, be10_chg]

No other rates combination may be added after results without reopening F4A.

### F4-FX

Raw authority:
- broad USD index
- EUR, GBP, JPY, CHF, CNY H.10 series

Origin-safe transforms:
- broad_usd_ret
- cny_usdstrength_ret
- safehaven_rotation
- usd_breadth
- fx_dispersion

Predeclared candidates:
- FX_BROAD = [broad_usd_ret]
- FX_CNY = [cny_usdstrength_ret]
- FX_SAFEHAVEN = [safehaven_rotation]
- FX_BROAD_CNY = [broad_usd_ret, cny_usdstrength_ret]
- FX_BROAD_SAFE = [broad_usd_ret, safehaven_rotation]
- FX_BREADTH_DISP = [usd_breadth, fx_dispersion]

### F4-NASDAQ

Authority:
- locked CORE5 monthly Nasdaq series only
- long-history daily Nasdaq remains NOT_PROVEN

Origin-safe transforms:
- ndx_ret1 = log(NDX[p]/NDX[p-1])
- ndx_mom3 = log(NDX[p]/NDX[p-3])
- ndx_mom6 = log(NDX[p]/NDX[p-6])
- ndx_vol6 = standard deviation of the six most recent monthly log returns ending at p

Predeclared candidates:
- NDX_RET1
- NDX_MOM3
- NDX_MOM6
- NDX_RET1_MOM3
- NDX_MOM3_VOL6

Daily realized volatility, daily drawdown and daily MIDAS are prohibited until daily authority is proven.

### F4-VIX

Authority:
- Cboe daily VIX

Origin-safe transforms:
- vix_ret = log(last[p]/last[p-1])
- vix_avg_chg = log(mean[p]/mean[p-1])
- vix_spike = log(max[p]/median[p])

Predeclared candidates:
- VIX_RET
- VIX_AVG
- VIX_SPIKE
- VIX_RET_SPIKE
- VIX_AVG_SPIKE

### F4-CPI

Authority:
- BLS headline CPI NSA
- BLS core CPI NSA

At origin p, latest eligible CPI month = p-1.

Transforms:
- cpi_yoy
- core_yoy
- cpi_accel = cpi_yoy - lag1(cpi_yoy)
- core_accel = core_yoy - lag1(core_yoy)

Predeclared candidates:
- CPI_HEADLINE = [cpi_yoy]
- CPI_CORE = [core_yoy]
- CPI_HEAD_CORE = [cpi_yoy, core_yoy]
- CPI_ACCEL = [cpi_accel]
- CPI_CORE_ACCEL = [core_accel]
- CPI_ACCEL_PAIR = [cpi_accel, core_accel]

Survey-consensus CPI surprise is excluded from native F4 because long-history consensus provenance is NOT_PROVEN.

### F4-COMMODITY

Authority:
- World Bank Pink Sheet monthly
- Brent, WTI, crude average, copper

At origin p, latest eligible World Bank month = p-1.

Transforms:
- brent_ret
- wti_ret
- crude_avg_ret
- copper_ret

Predeclared candidates:
- CMD_BRENT = [brent_ret]
- CMD_WTI = [wti_ret]
- CMD_CRUDE = [crude_avg_ret]
- CMD_COPPER = [copper_ret]
- CMD_BRENT_COPPER = [brent_ret, copper_ret]
- CMD_CRUDE_COPPER = [crude_avg_ret, copper_ret]

## 5. Inner family selector

For each outer DEV target T:

1. Construct only samples strictly before T.
2. For BASE and every predeclared candidate in the family:
   - use identical chronological inner-train / inner-validation boundaries;
   - fit/reoptimize native ChHHO-ANFIS;
   - record inner validation fitness from the frozen ChHHO selection procedure.
3. Select the candidate with the lowest inner validation fitness.
4. If BASE is best, the family contributes no external feature at this origin.
5. Refit the selected structure on all pre-T history and forecast T.
6. Never use T actual or any later outcome for candidate choice.

This produces one adaptive but fully causal **FamilyBlock forecast sequence** over the 33 outer origins.

## 6. Outer family promotion gate

A family is promotion-eligible only if its routed 33-origin sequence satisfies all of:

1. lower DEV ΣAE than BASE;
2. months improved >= months worsened;
3. positive median paired AE improvement;
4. improvement in at least 2 of 3 DEV calendar-year slices;
5. direction loss no worse than 1 month versus BASE;
6. leave-one-origin total improvement remains positive;
7. no pathological forecast explosion / finite-output gate passes.

Supporting diagnostics:
- MAE/RMSE/MAPE
- worst-month AE
- signed bias
- Clark-West-style nested forecast comparison where applicable
- paired bootstrap as small-n support

Statistical tests are supporting evidence, not sole promotion rules.

## 7. Combination stage

Only independently promoted families enter combinations.

No exhaustive powerset search.

Allowed first combination layer:
- all promoted pairs;
- if >3 families promote, retain at most the best three pair-supported families for one compact three-family challenge.

Final combination must undergo:
- leave-one-block-out;
- year stability;
- paired month stability;
- tail/worst-month diagnostics.

## 8. Freeze rule

After the first F4 family outcome is observed:
- no new transform;
- no new lag;
- no new candidate subset;
- no candidate deletion based on bad performance;
unless F4A is explicitly reopened and all prior F4 outcomes are marked exploratory/superseded.

## 9. Prior residual-screen boundary

Earlier residual screens are prior evidence only. They showed recoverable external information but **do not select native F4 winners**.

Native F4 starts from this charter with the long-history direct external store.

## 10. Active execution order

Family challenges will run:
1. Rates
2. FX
3. Nasdaq
4. VIX
5. CPI
6. Commodity

This order is operational only; cross-family promotion is based on the same frozen protocol, not on sequence.

## F4A revision note — baseline parity correction

The first Rates implementation run **36549022859** is **SUPERSEDED_METHODOLOGY / NOT SCIENTIFIC RESULT** because its BASE training window began at 2010-04 instead of the canonical 2010-03 and therefore failed baseline parity (2511.48 vs canonical 1413.03).

Correction:
- canonical training start restored to **2010-03**;
- BASE parity is now a hard fail-closed gate;
- `R_REAL_FF` was removed from the frozen Rates candidate set because the governed external store does not contain the 2009-12 Fed Funds observation required to preserve the canonical 2010-03 common history. No imputation or shortened-history comparison is allowed.

This revision occurred before any valid F4 Rates result was accepted.

## Kontrol ve Uyum Özeti

- F4A candidate universe: FROZEN
- BASE candidate included in every family selector: YES
- Inner selection: chronological only
- Outer DEV: 33 origins
- 2025 selection/tuning: NONE
- 2026 selection/tuning: NONE
- random split: NONE
- native integration: YES
- residual correction: NO
- Neon reads: 0
