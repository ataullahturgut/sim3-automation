# GPT-6 R74 follow-up — cross-target HAR-CAL vs EWMA (actual computation, 2026-10-13)

## Distinct clocks: DO NOT MIX
- R74 Claude #110: 16:45 Türkiye -> +1/+3/+5 trading-day close-to-close, and daily STAKTRAKR 1/5/10/21 trading days. Uses EWMA daily risk.
- HAR-CAL supplied ZIP: **08:45 -> 16:45 Türkiye same-day** realized intraday RV forecast. Do not directly use this *completed-same-day* RV forecast as 16:45 -> next09 or 16:45 -> future 16:45 variance; they require different targets.
- Test here: identical **08:45 -> 16:45** target and dates, 950 complete positive-RV HAR-CAL preissue forecasts over 2023–26, EV/Duka 2020–25 and direct Duka 2026. Published 2025–26 opened retrospective, not clean OOS.

## Original HAR-CAL re-executed
ZIP's `run_all.py` execution PASS: PR107 1724 target matching, prefix stability, calibration future-perturbation, full daily RV interval. Input M15 08:45 initial quote receipt unproven.

## Forecast QLIKE (smaller better)
| period | N | EWMA lambda .94 (strict prior DAY RV) | HAR-CAL | EWMA minus HAR 95% paired 20-day bootstrap |
|---|---:|---:|---:|---|
| 2023 |256|.237693|.230526|[-.005404,+.020648]|
| 2024 |259|.234096|.241417|[-.024321,+.010986]|
| 2023–24 DEV |515|.235884|.236003|[-.011260,+.011397]|
| 2025 |258|.279735|.243375|[+.005146,+.076392]|
| 2026 |177|.354439|.279200|[-.013856,+.224978]|

2026 QLIKE improvement 21.2% but CI crosses 0; DEV tie. No proven universal superiority. This is prediction of variance **not gold UP/DOWN**.

## Matched 08:45->16:45 DAY mean-risk portfolio
Both variants use precisely same past60 matured DAY log-return mean; prior DAY RV forecast differs (EWMA vs HAR-CAL). Long/cash weight = clip(mu/(3*variance),0,1). Each day enter and EXIT 16:45, pay 5bp each direction (10bp/day for full weight), **NOT** R74 close-to-close rebalancing/turnover cost. Hypothetical mids, not Turkish bank profit.
| Period | EWMA CER pp | HAR-CAL CER pp | HAR minus EWMA 95% paired-block CER CI |
|---|---:|---:|---|
| 2023 | -17.416 | -17.326 | [-.184,+.423] |
| 2024 | -14.709 | -14.790 | [-.297,+.070] |
| DEV 2023–24 | -16.055 | -16.051 | [-.191,+.194] |
| 2025 | -14.308 | -14.497 | [-.492,+.109] |
| 2026 | -18.507 | -20.922 | [-6.071,+.167] |

2026 weighting clipped at 0/1 on 153/177 (108 long, 45 cash), mean abs HAR-EWMA weight difference only **1.72 percentage points**, 17/177 days exceed 5 pp weight difference. Hence more precise conditional RV rarely changes actual exposure, while high daily round-trip costs dominate. Net strategy benefit NOT established.

## Direct DAY future price (USD/oz mean absolute error)
2026 N177: RW (08:45 known price) **31.0331**, EWMA lognormal-drift mean-price **31.8190**, HAR-CAL lognormal-drift **31.8175**. Price mean uses past60 DAY mean logreturn plus 0.5 forecast variance, an *untested* lognormal approximation. HAR does not beat RW; sign uses same μ for both; mean-signal correctness 78/177 =44.1%, always-up 95/177=53.7%. HAR variance can't magically yield better direction.

## Cohort B weekend correction
2010–25 daily metal source **0** weekend rows; 2026 has **44 Saturday/Sunday rows** of 189 (Jan–Jul). Original Claude R74 B 2026 5/10/21 *trading*-day h erroneously counted these as days. The original opened 21 day 2025–26 result 20 scored entries (2025 n12/2026 n8), 2026 six of eight origin dates weekend. Fixed original R74 script in `tools/gold_gpt6_r74_weekday_corrected_replay.py` drops weekend metal source rows BEFORE returns, MODWT, labels, and training. CI is `.github/workflows/gpt6-r74-weekday-replay.yml`; original Claude R74 #110 unchanged. **Do not claim corrected R74 performance until CI output exists.**

## Files
User ZIP's true daily data + HAR-CAL archived / source script re-run locally, own Python + full 950-row ledger in generated sandbox artifact `R74_HARCAL_EWMA_research_audit_20261013.zip` in associated conversation. Repo PR carries no raw or financial secrets; no existing canonical files changed.
