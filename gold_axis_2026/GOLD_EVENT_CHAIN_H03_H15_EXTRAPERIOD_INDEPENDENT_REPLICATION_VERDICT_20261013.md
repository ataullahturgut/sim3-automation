# ALTIN OLAY ZİNCİRİ: H03 TARİHSEL TRANSFER SINAMASI VE H15 HABER-KÖRLÜĞÜ DENETİMİ
**13 Ekim 2026** · Bağımsız araştırma dalı: `research-gold-event-chain-h15-2016-2026-test-20261013`
Dayanak: Claude hakem PR #119, açık PR #118, ana `gold-execution-channel-audit-20261006` HEAD `4ecdf810`. **Her iki PR hâlâ birleştirilmedi.** Bu araştırma hiçbir tahmin modeli, banka işlemi veya erken uyarı sistemi üretmemiştir.

## 1. Asıl sonuç: H03 farklı döneme taşınamıyor
Claude'un 2023–25 bulgusu: Önceki 20 seans altın getirisi, sonraki 10 tamamlanmış NY17 işlem seansından birinde ilk görülen >=3% DOWN hareketini >=3% UP hareketinden ayırmakta 0.683 pooled ROC AUC, her yılda ~0.74 AUC veriyordu. Bu, sadece **hareket gerçekleştiğine koşullu** ve işlem doğruluğu değildir.
Bu hipotez H03, kaynak/ufuk/eşik tanımı hesaplama öncesi `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_TEST_PROTOCOL_20261013.md` dosyasına yazılarak ilk kez diğer dönemlerde sorgulandı. Fakat 2026 olaylarını daha önce başka projelerde gördük; bu çalışma hiçbir anlamda 'tam dokunulmamış OOS' değildir.

### Period AUC results
| Study | Eligible decision days | DOWN-first | UP-first | NONE | AUC r20 -> DOWN-first | 20-session moving-block bootstrap descriptive 95% interval |
|---|---:|---:|---:|---:|---:|---|
| 2016–2019 reconstructed LBMA-labelled London daily fixing | 941 | 108 | 148 | 685 | **0.580** | 0.441–0.721 |
| **2020–2022 EV 15m NY17 (primary era-transfer)** | **705** | **145** | **144** | **416** | **0.473** | **0.347–0.633** |
| 2020–2022 HistData 15m NY17, source sensitivity | 703 | 141 | 151 | 411 | **0.474** | 0.344–0.621 |
| 2023–2025 EV 15m NY17 (referee baseline replication) | 764 | 85 | 286 | 393 | **0.683** | 0.553–0.815 |
| **2026 Jan–Sep 30 HistData 15m NY17** | **182** | **79** | **77** | **26** | **0.517** | 0.411–0.778 |

NOTE: The interval is **block-bootstrap sensitivity**, not a proven stationary sampling confidence interval; 550 random contiguous 20-session block resamples, many overlapping 10-day outcomes. All periods have estimated uncertainty. Each annual 2023–25 AUC (~0.739/0.733/0.743) is independently reproduced. 2020–22 yearly AUC **0.468/0.444/0.529**; hence the year-by-year replication *fails*. AUC below 0.5 does **not** establish reliable reverse sign. Ten disjoint-stride offset sensitivities vary widely.

Same-source reproducibility:
- EV vs HistData matched dates in 2020–22: **773**, close-return correlation **0.9917**, sign agreement **96.9%**. Two independent 2020–22 AUC 0.4728 and 0.4740, agreeing closely.
- 2026 alternate Twelve Data NY17 hourly-derived reconstructed daily price: through August, with weekend placeholders removed, 2026 **162** eligible dated origins, **71 UP, 66 DOWN**, AUC **0.497**. HistData using 2026 period through Aug14 has AUC **0.501** (160 eligible decision days). The Twelve series uses fixed 21UTC timestamps that differ from actual 17 ET in winter and include synthetic nontrading dates; this is a supplementary source check, not PIT authority.
- 2016–19 StakTrakr 'LBMA' source is an entirely different 12:00 London fixing, retro-available 2026, no direct contemporaneous proof. In 2020–22 overlap its daily returns correlate only **0.334** with EV NY17 closes, and average sign agreement 58.7%. **Do not combine 2016–19 value with comparable NY17 AUC to assert time-generalization.**

Interpretation: H03 is a **sample/re-gime dependent descriptive association**, not a transportable directional early warning. This overturns the strong wording of the PR #119 recommendation to promote the three yearly AUCs as a reliable regularity, though differences across subperiods need larger/outcome-blind samples for strong hypothesis tests.

## 2. H02 timing: price tension still not a reliable alarm
Under the frozen definition, all origin days:
- 2020–22 EV: prior r20 >=8% in 31 valid origins, any ±3% first passage 17/31; r20 <5% 244/613 had any passage.
- 2023–25 EV: 52/74 vs 260/571.
- 2026 HistData: 31/32 vs 100/125.
This raw association increases markedly with volatility (especially 2026); days are highly overlapping exposures, NOT independent forecasts or calibrated hit rates. Subperiod 2020–22 conditional sign AUC below 0.5 and 2026 0.517; therefore being 'stretched' is not a robust SELL or 'event arrives now' rule. Statistical adjustment by origin-volatility and no-news non-event cases is still needed.

## 3. H15 narrative-reversal conjecture: a genuinely blinded test is not yet possible
The original proposed H15 was 'pre-existing gold price tension × an independently first-published news item that **reverses the previously dominant explanatory narrative** -> unusually large downshock'. PR #119 coded examples with future gold outcome already known, **not blinded**; reusing those as test cases would constitute label leakage/selection.
We constructed an **outcome-hidden study base**, not an H15 validation:
- **249** dated macro release rows (67 FOMC, 91 CPI, 91 NFP) covering 2016–22 and 2026, selected without looking at subsequent gold price movements: `GOLD_EVENT_CHAIN_H15_NEWS_BLIND_CODING_UNIVERSE_249_MACRO_RELEASES_20261013.csv`.
- **1,429** weekday candidate comparison dates with no CPI/NFP/FOMC release within ±1 calendar day, selected by calendar alone: `GOLD_EVENT_CHAIN_H15_NEWS_BLIND_NONEVENT_CALENDAR_20261013.csv`. These are ***not guaranteed no-news or no-shock dates***, nor matched based on regime/volatility.
- **13** dated source links and pre/during/post publication labels: `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_DATED_NEWS_AUDIT_20261013.csv`. Famous cases selectively chosen for illustrating pitfalls, NOT blind samples.
- `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_BLIND_NEWS_CODEBOOK_20261013.md` freezes first-published-source, prior narrative, evidence against, genuinely independent gold-masked coder, uncertainty/firstprint and causal window rules. The blinded narrative labels have **NOT BEEN FILLED**. Original first-publication time of most historical WGC/Reuters updated articles is unknown; publishing time must precede first-price reaction or can explain only ongoing continuation. Therefore **NO H15 AUC, odds ratio or causal significance** is claimed.

### Event chronologies — evidence tests, not favorable-example predictions
**2016 Brexit**: Reuters article published 24 June after the UK referendum Leave result reported gold safe-haven rally. WGC webpage dated *23 June* contains explicit discussion of the referendum result and June 24 price: a clear metadata/date trap; impossible to use its page date as advance warning without original snapshots. https://www.foxbusiness.com/markets/gold-races-to-highest-in-over-2-years ; https://www.gold.org/goldhub/research/market-update/market-update-gold-surges-after-brexit-becomes-reality

**March 2020 liquidity — genuine dated vulnerability example**: WGC **2 March 2020** already warned that record COMEX long positions and margin-call liquidation could cause gold to be sold alongside shares, while also presenting contrary bullish ETF inflow evidence. EV quote NY17 March9 $1,676.945 -> March16 $1,505.935 = ~**-10.20%**; daily high-low span 12/13/16 March **5.74/6.20/8.57%**. WGC **19 March** explains liquidation after it occurred, not a foresight claim. The date prewarning was non-deterministic; the COVID/credit panic was catalyst. https://www.gold.org/goldhub/gold-focus/2020/03/despite-last-weeks-selloff-market-shifts-could-bode-well-gold-prices ; https://www.gold.org/goldhub/research/gold-prices-swing-as-markets-sell-off

**23 March 2020 QE**: Official Fed statement at **08:00 EDT** described open-ended Treasury/MBS buying to restore functioning. That was publicly observable only after 08:00; market reaction cannot be predicted using its text before the release. https://www.federalreserve.gov/newsevents/pressreleases/monetary20200323a.htm

**24 February 2022 invasion**: On the same trading day, Reuters at **04:10 EST** reported bullion up >2% after the Russian attack; another Reuters update around **17:11 EST** reported gold had **erased the safe-haven rally** as global risk appetite recovered. Our same-provider NY17 gold session: **high 1,974.525, low 1,878.195, 5.129% high/low range** yet Feb23 NY17 close 1,907.535 -> Feb24 close **1,903.270 (−0.22%)**. This is a rigorous COUNTERCASE to inferring closing direction from a single shock headline. https://www.marketscreener.com/news/latest/Gold-jumps-over-2-as-Russia-attacks-Ukraine-39562653/ ; https://www.marketscreener.com/news/latest/Investors-regain-risk-appetite-dollar-oil-pare-gains-after-Ukraine-invasion-39577470/

**30 January 2026 Warsh nomination**: NY17 HistData gold close Jan29 $5,382.90 -> Jan30 $4,860.49 = approx **−9.71%**, consistent with Reuters contemporaneous ~-9.5% spot report. But Reuters at early-morning publication already describes gold tumbling amid candidate speculation and profit taking, so the article is NOT reliable evidence of a *lead signal before* the price move. https://www.reuters.com/world/india/gold-slips-firmer-dollar-set-best-month-since-1980-2026-01-30/ ; https://www.marketscreener.com/news/stocks-steady-gold-tumbles-as-kevin-warsh-emerges-as-likely-fed-pick-ce7e5bdcdb8df720

**March 2026 sell-off**: WGC's **8 April** analysis attributes March's historically large liquidation in substantial part to ETF/CTA flows, bond stress, liquidity and de-risking, despite geopolitics. But April report CANNOT backdate into March. https://www.gold.org/goldhub/research/gold-market-commentary-march-2026

## 4. Limitations and decisions
- The narrow H03 quantitative hypothesis is **tested and fails transportability**. AUC only describes ordering of future UP vs DOWN *conditional on an event known after the fact*, and says NOTHING directly about live timing, 09:00–17:00 Türkiye execution, 0.8% one-way bank cost, or profitability.
- Observed historical price quotes are research-reconstructed from vendor archives; no proof they were all obtained in real time.
- 2016–19 reconstructed London fixing has incomparable valuation timestamp and missing origin-safe archival vintage; treat AUC=0.58 as separate exploratory evidence.
- News originals are not gold-outcome blinded; selecting well-known stories cannot be treated as statistical validation, and *two time-labelled Reuters reports on the same day may describe opposite intraday states*. WGC 2020/2026 backcast analyses are informative mechanisms, not predictive evidence.
- True H15 test needs independent coder(s), time-verified primary-firstprint news corpus for ALL macro-news and unscheduled-event candidates, gold outcome hidden, independently sampled negative controls, episode-cluster analysis and chronological publication lags. The 249+1,429 event-calendar packets make that design feasible but do not supply the missing narrative labels.
- 2026 explicitly prior-exposed and not fully untouched; source B quote and daily label mismatches mean interpret cautiously.
- No event-time classifier or strategy optimized. No GitHub main-branch manifest edited; PR #118 and #119 remain unmerged.

## 5. Files
1. `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_TEST_PROTOCOL_20261013.md` — frozen BEFORE H03 testing, not external preregistration.
2. `GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_2016_2026_DAILY_OUTCOMES_20261013.csv` — derived per-session features and labels, **raw vendor price column scrubbed**, with separate vendor scopes.
3. `GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_2016_2026_RESULTS_20261013.json` — AUC, N, years, source concordance, ten-phase sensitivity.
4. `GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_BLOCK_UNCERTAINTY_20261013.json` — block resampling descriptive uncertainty.
5. `GOLD_EVENT_CHAIN_H03_2026_TWELVE_ALTERNATE_SOURCE_QC_20261013.json` — 2026 alternate (daily converted) NY17 source result.
6. `GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_REPRODUCE_20261013.py` — stdlib reproducer for the AUC from derived CSV.
7. `GOLD_EVENT_CHAIN_H03_H15_EXTRAPERIOD_SOURCE_QUERIES_20261013.sql` — upstream Neon read-only source regeneration SQL.
8. `GOLD_EVENT_CHAIN_H15_NEWS_BLIND_CODING_UNIVERSE_249_MACRO_RELEASES_20261013.csv`
9. `GOLD_EVENT_CHAIN_H15_NEWS_BLIND_NONEVENT_CALENDAR_20261013.csv`
10. `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_DATED_NEWS_AUDIT_20261013.csv`
11. `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_BLIND_NEWS_CODEBOOK_20261013.md`

**Scientific verdict:** A three-year-invariant AUC around 0.74 **is NOT** reliable temporal-generalization. Narrative reversal remains a plausible *mechanistic description*, not an advance warning, pending fully time-validated and gold-masked blind coding. Historical examples indicate that liquidity and same-day repricing can completely reverse the headline-driven gold move.
