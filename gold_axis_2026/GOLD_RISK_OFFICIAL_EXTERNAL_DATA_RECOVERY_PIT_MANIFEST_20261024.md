# GOLD RISK — EXOGENOUS SOURCE RECOVERY / PIT CONTRACT — 2026-10-24

**İş durumu:** Resmî dış kaynakların adresleri ve manuel kaynak-indirme denemesi için kod yazıldı; **indirmenin GitHub koşusu henüz başlatılmadı**. Dolayısıyla eksik veriler henüz Neon'a yazılmadı, tamlık denetimi yapılmadı, model yeniden kurulmadı.

**Kod:** `gold_axis_2026/tools/gold_exogenous_official_archive_capture_v1.py`
**Çalıştırma:** GitHub Actions, default `main` üzerinde `Gold Official Exogenous Archives — MANUAL Only` -> `Run workflow`. Çalışma doğrudan araştırma dalındaki kodu checkout eder. Schedule, push, workflow_run TETİKLEYİCİLERİ YOK.
**Çıktı:** Her kaynağın başarı/engel ve SHA256 kaydı `source_inventory.json`, yalnız 30 günlük Actions artifact; hiç bir veritabanı/tablo/model etkilenmez.

## Source families and precisely verified public endpoints

1. **CFTC Disaggregated Futures Only, COMEX gold/silver, managed money/open interest.** Resmî 2023-2026 yıllık ZIP kaynakları:
   `https://www.cftc.gov/files/dea/history/fut_disagg_txt_{YEAR}.zip`
   Resmî dizin: https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm
   Haftalık pozisyon tarihi ile yayımlanma zamanı aynı değildir: normal rapor haftada bir cuma 15:30 NY, salı kapanış verisidir. 2023-24 ve normal 2025 haftaları için modelde sadece konservatif **salı +7 gün** kullanma adayı — resmî istisnai gecikme günleri ayrıca denetlenmedikçe as-of kesin sertifikası değildir.
   **2025 hükümet kapanması:** 30 Eylül–23 Aralık raporlarının gecikmiş günleri CFTC 9 Aralık 2025 düzeltmesine göre eşlenmiştir; örn. 30 Eylül raporu 19 Kasım'da yayımlandı. Orijinal planı as-of diye saklamak veri sızıntısıdır.
   https://www.cftc.gov/PressRoom/PressReleases/9147-25

2. **CME COMEX Gold (GC) + Silver (SI) historical performance bonds, date by contract maturity.**
   - GC https://www.cmegroup.com/clearing/risk-management/files/GC-2020-to-present.pdf
   - SI https://www.cmegroup.com/clearing/risk-management/files/SI-2020-to-present.pdf
   - Index https://www.cmegroup.com/solutions/risk-management/margin-services/historical-margins.html
   Bu PDF'ler sözleşme/roll tarihlerine göre tarihsel *uygulanan* marjı içerir; **marj değişim duyurusunun ilk yayımlanma zamanı** ile bire bir aynı değildir. PDF yalnız arşivlenir; olay modeli için tarihli CME clearing advisory ile bağımsız yayın doğrulaması ve vade eşleştirme şart.

3. **GLD SPDR fund historical archive XLSX** https://www.spdrgoldshares.com/usa/gld/ 'Historical Archive (XLSX)' publisher direct link on page. Arşiv URL'si kaynak HTML'den doğrulanarak çözümlenir; dosya kimliği/hash, tarih/kolon denetimi olmadan modelde kullanılmaz.

4. **SLV iShares publisher Data Download Excel** https://www.ishares.com/us/products/239855/ishares-silver-trust-fund . "Data Download Excel" link exists. Daily tonnes/trade-date coverage *henüz doğrulanmadı*. Silver bar list -> settlement basis; ETF flow diye karıştırma. Hangi alanlar geçmişte mevcutsa kayıt altına alınacak.

5. **Federal Reserve 10y real rates + 2y,10y nominal + Broad USD** (FRED current history snapshot, firstprint not proven):
`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10` and `DGS2,DGS10,DTWEXBGS`.
Real faiz DFII10 as-of release rule separate; H.10 Broad USD haftanın izleyen pazartesi yayımlanır, future-dated Fed historical observation same day use forbidden. Later ALFRED vintage source where necessary.

## Integration contract

- Valid source has original URL; retrieval SHA-256; original observation date; date/time of first PUBLIC release or conservative *audited* eligibility; quality flags; missingness; and model-relevant definition.
- Distinguish holdings stock (GLD/SLV tonnes) vs net asset flows; a change in holdings may correlate with flow but is NOT bank-reported actual cash flow.
- CPI/FOMC and daily intraday gold are separate source families, not silently asserted as complete.
- TRAIN 2023-2024, VALID 2025, **2026 entirely out-of-sample** for calendar-year-level onset; threshold discovery on 2026 absolutely prohibited.
- Three independent test objectives: risk of 1-day loss >=3%, risk of future 5 trading-day drawdown >=5%, and error inflation of locked ANN daily/weekly/monthly predictions. False-alarm count + count of *independent crash episodes*, lead time and number of missed episodes required.
- Final layer annotations are **uncertainty warnings** until error uplift vs locked ANN observed; never a free-standing BUY/SELL signal.

## Status scope

| Family | Verified official source | Download run | Numeric parse | PIT ready | In model |
|---|---|---|---|---|---|
| CFTC 2023-26 | yes | **not executed** | scripted; not verified | no | no |
| CME GC/SI 2020-present PDFs | yes | **not executed** | not implemented (raw only) | no | no |
| GLD historical XLSX | yes | **not executed** | not implemented (raw only) | no | no |
| SLV official data excel | link exists | **not executed** | history not verified | no | no |
| FRED DFII10 DGS2 DGS10 BroadUSD | yes | **not executed** | script CSV validation | no | BroadUSD and DGS10 used in prior separate overlay |

No automatic schedule was restored. No Neon insertion or model retraining was performed in this stage.
