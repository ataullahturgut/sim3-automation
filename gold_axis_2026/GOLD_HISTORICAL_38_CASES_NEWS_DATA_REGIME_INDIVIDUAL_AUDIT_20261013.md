# 2023–2025 ALTIN: ÖNCEKİ 38 EKSİK OLAYIN TEK TEK HABER + VERİ + REJİM İNCELEMESİ

**Oluşturma tarihi:** 14 Ekim 2026 · **Kapsam:** 18 uzun ZigZag fiyat bacağı + 20 sabit-ufuk hareket kümesi. **Statü:** Retrospektif sayısal çapraz veri eşleştirmesi yapıldı; haber kaynakları ve ekonomi etkenleri değerlendirildi, **nedensel ispat / PIT canlı tahmin doğrulaması YOK**.

**Asıl satır delili:** [GOLD_HISTORICAL_38_MISSING_CASES_CAUSAL_DATA_EVIDENCE_V1_20261013.csv](GOLD_HISTORICAL_38_MISSING_CASES_CAUSAL_DATA_EVIDENCE_V1_20261013.csv). Özgün V1/V2/V3, 774-günlük altın arşivi, CFTC ve makro veriler değiştirilmedi. Bu araştırma ana manifestte genel tarihsel araştırmalara aittir; Ocak 2026 ayrı son vakadır.

## Bilimsel ölçüm sözleşmesi

- Altın fiyat yüzdesi **özgün V1 veya V2 tanımıyla** korunur; V2'nin yüzdesi etiketin *en yüksek mutlak kısa-ufuk hareket büyüklüğüdür*, olay başlangıcı/sonu getirisi değildir. İki etiketin getiri yüzdeleri veya banka işlemleri kıyaslanmaz.
- Beş varlık (gümüş, platin, paladyum, S&P500, Nasdaq100) için **aynı tarihli günlük veride** `100 × (P_bitiş/P_başlangıç − 1)` hesaplandı. 2023–25 serileri Neon observations Gold Control veri tabanından alındı; gümüş/platin/paladyum StakTrakr kaynaklı; hisse endeksleri FRED kaynaklı. **Günlük kapanış saatleri NY17 altın saatleriyle özdeş değildir.**
- Seriler geçmiş tarihli olmakla birlikte sisteme **2026 Ağustos/Eylül** döneminde geri yüklenmiş: bunlar 2023–25 günü canlı olarak elde edilebilir olduğunun kanıtı değil. Gerçek zamanlı işleme neden-sonuç kurulacaksa resmi yayın ilk saati, sağlayıcı ilk-vintage, karar UTC, 15m kaynak ve banka BID/ASK ayrı doğrulanmalı.
- İlk makro defteri 155 **gösterge** yayın satırıdır; NFP/ücret/işsizlik aynı açıklama saatine ait olabilir. FOMC 2025 ilk sürümü eksiktir; sonradan düzeltilmiş resmî Fed takvimi önceliklidir. Makro sürpriz rakamı duyurudan **önce** bilinen özellik sayılamaz.
- **38/38** kayda ilişkin tarih/altın/ekonomik hipotez kaynakları saklandı; beş gösterge açısından **35/38** tam takvim-ucu karşılaştırma, **3/38** en az bir eksik uç. Ayrıca *C035* aynı gün başlayıp bittiği için 5 adet yüzde sıfır **matematiksel olarak zorunlu** ve kısa-ufuk fiyat tepkisini açıklayamaz: **34/38 gerçek iki-farklı-tarihli beşli karşılaştırma** elde edildi.
- **Kaynak açıklaması ve ekonomi nedeni ayrı:** tarihli Reuters/WGC/Kitco/AP metni ekonomik bağlamdır; tarihli ay sonu WGC makalesi olaydan sonraysa ön uyarı olmaz. Çapraz korelasyon yalnız **mekanizma ile tutarlılık** sağlar; nedensel etki katsayısı, tahmin doğruluğu, istatistiksel hata payı değildir.

## Kısa araştırma bulgusu

İncelenen kayıtlarda ortak tek bir neden yoktur. ABD makro/faiz/dolar kaynaklı fiyatlama, banka-finansman stresi, jeopolitik güvenli liman, ETF/COMEX/opsiyon kaynaklı altın-özgü sermaye akışı, fiziki/EFP arbitrajı, zorunlu likidite pozisyon kapanışı ve düzeltme/kar alımı **birbirinden farklı** mekanizmalardır. Bir ayın fiyat yükselişi ile aynı ayın kısa düşüşü farklı kaynak-zaman ufuklarıyla üst üste gelebilir.

## 38 olaylık ayrıntılı sicil

## 2023 / UZUN TREND

### 01. SWING_V1_001 · 2023-01-03 → 2023-02-01 · UP

**Gerçek altın fiyat kaydı:** +6.07%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -3.29%, platin -7.27%, paladyum -9.20%; S&P500 +7.72%, Nasdaq100 +13.81%.

**Gözlenen rejim ayrımı:** Çapraz piyasalar tek yönlü değil; tek-faktör makro açıklaması yetersiz.

**Temel ekonomik etken hipotezi:** USD and US Treasury yields ↓; gold demand/positioning. **Karşıt kanıt / alternatif mekanizma:** Other white metals ↓ while stocks ↑: not broad precious-metal rally.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-01-06 AHE surprise=-0.10; 2023-01-06 NFP surprise=23.00; 2023-01-06 UNEMP surprise=-0.20; 2023-01-12 CPI surprise=-0.10; 2023-02-01 FOMC. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-january-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 02. SWING_V1_002 · 2023-02-01 → 2023-02-24 · DOWN

**Gerçek altın fiyat kaydı:** -7.19%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -10.24%, platin -6.65%, paladyum -11.84%; S&P500 -3.62%, Nasdaq100 -3.18%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu.

**Temel ekonomik etken hipotezi:** Stronger US employment and yields/USD ↑. **Karşıt kanıt / alternatif mekanizma:** Gold, white metals and shares ↓; do not claim one NFP covers entire February leg.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-02-01 FOMC; 2023-02-03 AHE surprise=0.00; 2023-02-03 NFP surprise=332.00; 2023-02-03 UNEMP surprise=-0.20; 2023-02-14 CPI surprise=0.00. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-february-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 03. SWING_V1_003 · 2023-02-24 → 2023-05-04 · UP

**Gerçek altın fiyat kaydı:** +13.20%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +21.50%, platin +11.60%, paladyum -0.76%; S&P500 +2.30%, Nasdaq100 +8.46%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı.

**Temel ekonomik etken hipotezi:** SVB bank failure and broader bank funding stress; March gold ETFs +32t (published April 6). **Karşıt kanıt / alternatif mekanizma:** Leg also spans April and May: SVB cannot be sole explanation for whole return.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-03-10 AHE surprise=-0.10; 2023-03-10 NFP surprise=106.00; 2023-03-10 UNEMP surprise=0.20; 2023-03-14 CPI surprise=0.00; 2023-03-22 FOMC; 2023-04-07 AHE surprise=0.00; 2023-04-07 NFP surprise=-3.00; [daha fazlası CSV'de]. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-march-2023; ek literatür: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2023/04. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 04. SWING_V1_004 · 2023-05-04 → 2023-06-28 · DOWN

**Gerçek altın fiyat kaydı:** -6.93%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -11.77%, platin -12.87%, paladyum -11.86%; S&P500 +7.77%, Nasdaq100 +15.27%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı.

**Temel ekonomik etken hipotezi:** US real yield/2y TIPS ↑, dollar opportunity cost and futures positioning. **Karşıt kanıt / alternatif mekanizma:** Equities ↑ while gold/metals ↓: gold opportunity-cost channel candidate.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-05-05 AHE surprise=0.20; 2023-05-05 NFP surprise=73.00; 2023-05-05 UNEMP surprise=-0.20; 2023-05-10 CPI surprise=0.00; 2023-06-02 AHE surprise=-0.10; 2023-06-02 NFP surprise=159.00; 2023-06-02 UNEMP surprise=0.20; [daha fazlası CSV'de]. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-may-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 05. SWING_V1_005 · 2023-06-28 → 2023-07-18 · UP

**Gerçek altın fiyat kaydı:** +3.68%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +10.06%, platin +7.99%, paladyum +3.25%; S&P500 +4.07%, Nasdaq100 +5.86%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı.

**Temel ekonomik etken hipotezi:** July weaker dollar, breakeven inflation ↑; futures net longs +93t in July WGC. **Karşıt kanıt / alternatif mekanizma:** ETF holdings still declined: do not attribute all rally to ETF inflows.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-07-07 AHE surprise=0.10; 2023-07-07 NFP surprise=-16.00; 2023-07-07 UNEMP surprise=0.00; 2023-07-12 CPI surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-july-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 06. SWING_V1_006 · 2023-07-18 → 2023-10-05 · DOWN

**Gerçek altın fiyat kaydı:** -8.00%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -15.09%, platin -12.06%, paladyum -10.43%; S&P500 -6.52%, Nasdaq100 -7.06%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu.

**Temel ekonomik etken hipotezi:** Real yield/USD surge plus ETF and futures outflows; Sep 10Y +~50bp, DXY +2.5%, gold ETF -59t, COMEX netlong -70t. **Karşıt kanıt / alternatif mekanizma:** Price correction straddles August and September; monthly indicators are not daily first-prints.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-07-26 FOMC; 2023-08-04 AHE surprise=0.10; 2023-08-04 NFP surprise=-13.00; 2023-08-04 UNEMP surprise=-0.10; 2023-08-10 CPI surprise=0.00; 2023-09-01 AHE surprise=-0.10; 2023-09-01 NFP surprise=17.00; [daha fazlası CSV'de]. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-august-2023; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-september-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


## 2024 / UZUN TREND

### 07. SWING_V1_013 · 2024-02-14 → 2024-04-19 · UP

**Gerçek altın fiyat kaydı:** +19.99%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +27.87%, platin +6.81%, paladyum +16.23%; S&P500 -0.67%, Nasdaq100 -4.32%.

**Gözlenen rejim ayrımı:** Altın yukarı, ABD hisse endeksleri aşağı: güvenli-liman ayrışması ile uyumlu; kesin kriz nedeni değil.

**Temel ekonomik etken hipotezi:** March gold options/implied vol and OTC/Asian/central-bank demand, plus weaker ISM. **Karşıt kanıt / alternatif mekanizma:** Gold +19.989% NY17 leg despite equities ↓: not ordinary equity risk-on; RSI overbought alone insufficient.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2024-03-08 AHE surprise=-0.10; 2024-03-08 NFP surprise=77.00; 2024-03-08 UNEMP surprise=0.20; 2024-03-12 CPI surprise=0.00; 2024-03-20 FOMC; 2024-04-05 AHE surprise=0.00; 2024-04-05 NFP surprise=91.00; [daha fazlası CSV'de]. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-february-2024; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-march-2024. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 08. SWING_V1_014 · 2024-04-19 → 2024-04-30 · DOWN

**Gerçek altın fiyat kaydı:** -4.29%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -5.61%, platin -0.21%, paladyum -6.29%; S&P500 +1.38%, Nasdaq100 +2.37%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı.

**Temel ekonomik etken hipotezi:** April profit taking/Chinese premium and COMEX position slowing. **Karşıt kanıt / alternatif mekanizma:** Other metals ↓ while equities ↑: differentiation vs general liquidation.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-april-2024. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 09. SWING_V1_015 · 2024-04-30 → 2024-05-20 · UP

**Gerçek altın fiyat kaydı:** +6.00%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +19.28%, platin +15.23%, paladyum +6.93%; S&P500 +5.41%, Nasdaq100 +7.07%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı.

**Temel ekonomik etken hipotezi:** May gold ETF flows +USD529m and COMEX managed money longs four-year high. **Karşıt kanıt / alternatif mekanizma:** Gold leg +6.003%, but month-end GRAM residual large; no sole factor.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2024-05-01 FOMC; 2024-05-03 AHE surprise=-0.10; 2024-05-03 NFP surprise=-63.00; 2024-05-03 UNEMP surprise=0.10; 2024-05-15 CPI surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-may-2024. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 10. SWING_V1_016 · 2024-05-20 → 2024-06-07 · DOWN

**Gerçek altın fiyat kaydı:** -5.50%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -4.81%, platin -7.95%, paladyum -10.01%; S&P500 +0.73%, Nasdaq100 +1.75%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı.

**Temel ekonomik etken hipotezi:** May 22 hawkish Fed minutes, June 7 China PBoC pause plus US NFP 272k vs 185k. **Karşıt kanıt / alternatif mekanizma:** NFP and PBoC June 7 are endpoint releases, not known since May 20.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2024-06-07 AHE surprise=0.10; 2024-06-07 NFP surprise=90.00; 2024-06-07 UNEMP surprise=0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.bloomberg.com/news/articles/2024-06-07/china-s-pboc-halts-gold-purchases-after-price-hits-record-in-may; ek literatür: https://www.kitco.com/news/off-the-wire/2024-05-23/gold-falls-one-week-low-hawkish-fed-minutes. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 11. SWING_V1_017 · 2024-06-07 → 2024-07-16 · UP

**Gerçek altın fiyat kaydı:** +7.74%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +1.98%, platin -0.70%, paladyum +3.16%; S&P500 +5.99%, Nasdaq100 +7.36%.

**Gözlenen rejim ayrımı:** Çapraz piyasalar tek yönlü değil; tek-faktör makro açıklaması yetersiz.

**Temel ekonomik etken hipotezi:** Falling Treasury yields and US dollar with July rate-cut repricing. **Karşıt kanıt / alternatif mekanizma:** Pt -0.70% while silver +1.98%; no unanimous metal rally.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2024-06-07 AHE surprise=0.10; 2024-06-07 NFP surprise=90.00; 2024-06-07 UNEMP surprise=0.10; 2024-06-12 CPI surprise=-0.10; 2024-06-12 FOMC; 2024-07-05 AHE surprise=0.00; 2024-07-05 NFP surprise=15.00; [daha fazlası CSV'de]. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-july-2024. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 12. SWING_V1_018 · 2024-07-16 → 2024-07-25 · DOWN

**Gerçek altın fiyat kaydı:** -4.25%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -9.31%, platin -4.55%, paladyum -2.85%; S&P500 -4.73%, Nasdaq100 -7.69%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu.

**Temel ekonomik etken hipotezi:** Profit taking after July 16 high and correction in tech/risk appetite. **Karşıt kanıt / alternatif mekanizma:** Nasdaq ↓ materially; multiple possible sources, event-specific ex ante cause unresolved.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-july-2024. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


## 2025 / UZUN TREND

### 13. SWING_V1_031 · 2025-05-01 → 2025-05-06 · UP

**Gerçek altın fiyat kaydı:** +5.83%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +2.80%, platin +1.55%, paladyum +0.85%; S&P500 +0.05%, Nasdaq100 +0.02%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı.

**Temel ekonomik etken hipotezi:** Tariff/policy uncertainty and interest-rate outlook drove short gold rebound. **Karşıt kanıt / alternatif mekanizma:** US equities nearly flat on date-to-date; no broad flight-to-quality inference.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-05-02 AHE surprise=-0.10; 2025-05-02 NFP surprise=39.00; 2025-05-02 UNEMP surprise=0.00. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-may-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 14. SWING_V1_032 · 2025-05-06 → 2025-05-14 · DOWN

**Gerçek altın fiyat kaydı:** -7.21%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -0.42%, platin +1.94%, paladyum +0.73%; S&P500 +5.09%, Nasdaq100 +7.72%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı.

**Temel ekonomik etken hipotezi:** May 12 US-China 90-day tariff reduction and safer risk sentiment; USD stronger. **Karşıt kanıt / alternatif mekanizma:** S&P/Nasdaq ↑ yet gold leg ↓, industrial metals ↑; safe-haven unwind plausible, opposite equity-riskoff.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-05-13 CPI surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Bağlamsal kaynak: https://www.kitco.com/news/off-the-wire/2025-05-12/gold-slides-3-us-china-agree-slash-reciprocal-tariffs. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 15. SWING_V1_033 · 2025-05-14 → 2025-06-13 · UP

**Gerçek altın fiyat kaydı:** +7.96%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +9.70%, platin +27.63%, paladyum +10.30%; S&P500 +1.43%, Nasdaq100 +1.46%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı.

**Temel ekonomik etken hipotezi:** Trade and fiscal uncertainty; June 13 Israel-Iran attack adds last-day haven bid. **Karşıt kanıt / alternatif mekanizma:** Precious metals ↑ sharply, including platinum; June 13 shock not known May 14.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-06-06 AHE surprise=0.10; 2025-06-06 NFP surprise=13.00; 2025-06-06 UNEMP surprise=0.00; 2025-06-11 CPI surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.kitco.com/news/off-the-wire/2025-06-13/gold-advances-israel-iran-escalation-fuels-safe-haven-bids; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-may-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 16. SWING_V1_034 · 2025-06-13 → 2025-06-27 · DOWN

**Gerçek altın fiyat kaydı:** -4.67%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -0.26%, platin +7.22%, paladyum +6.70%; S&P500 +3.28%, Nasdaq100 +4.18%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı.

**Temel ekonomik etken hipotezi:** Diminishing Middle East acute risk premium and changing risk appetite. **Karşıt kanıt / alternatif mekanizma:** Pt/Pd and equities ↑ as gold falls: gold haven-premium unwind plausible, not global metal selloff.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.gold.org/goldhub/gold-focus/2025/06/weekly-markets-monitor-safe-haven-elevated; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-july-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 17. SWING_V1_035 · 2025-06-27 → 2025-07-22 · UP

**Gerçek altın fiyat kaydı:** +4.74%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +7.95%, platin +5.85%, paladyum +11.58%; S&P500 +2.21%, Nasdaq100 +2.35%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı.

**Temel ekonomik etken hipotezi:** Tariff/Fed uncertainty plus gold fund/investor demand; weaker-dollar case. **Karşıt kanıt / alternatif mekanizma:** All metals/equities ↑; broad asset inflation/risk regime; original trigger not proven.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-07-03 AHE surprise=-0.10; 2025-07-03 NFP surprise=36.00; 2025-07-03 UNEMP surprise=-0.20; 2025-07-15 CPI surprise=0.00. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-july-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 18. SWING_V1_036 · 2025-07-22 → 2025-07-30 · DOWN

**Gerçek altın fiyat kaydı:** -4.50%; ölçüm: EV/Dukascopy NY17 ZigZag retrospektif fiyat bacağı.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -2.37%, platin -4.08%, paladyum -0.48%; S&P500 +0.84%, Nasdaq100 +1.22%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı.

**Temel ekonomik etken hipotezi:** Late-July US dollar/interest-rate opportunity-cost repricing. **Karşıt kanıt / alternatif mekanizma:** Metals ↓ while equities ↑; gold/metal-specific policy/rates more plausible than broad stock crisis.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-july-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


## 2023 / KISA-VADELİ EŞİK KÜMESİ

### 19. MOVE_V2_C001 · 2023-01-05 → 2023-01-12 · UP

**Gerçek altın fiyat kaydı:** +3.48%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-01-12).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +1.24%, platin -0.74%, paladyum -1.33%; S&P500 +4.60%, Nasdaq100 +6.69%.

**Gözlenen rejim ayrımı:** Çapraz piyasalar tek yönlü değil; tek-faktör makro açıklaması yetersiz. İşaretli fiyat günlerinde maksimum high-low farkı: +1.49% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** January weaker USD/yields context; Jan 12 CPI release on calendar. **Karşıt kanıt / alternatif mekanizma:** Silver + but Pt/Pd -; no cluster-specific dated catalyst identified.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-01-06 AHE surprise=-0.10; 2023-01-06 NFP surprise=23.00; 2023-01-06 UNEMP surprise=-0.20; 2023-01-12 CPI surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-january-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 20. MOVE_V2_C002 · 2023-01-27 → 2023-02-08 · DOWN

**Gerçek altın fiyat kaydı:** +4.30%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-02-03).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -5.37%, platin -2.27%, paladyum +0.18%; S&P500 +1.16%, Nasdaq100 +2.70%.

**Gözlenen rejim ayrımı:** Altın aşağı, hisseler yukarı: altın-özgü pozisyon çözülmesi veya faiz/fırsat maliyeti adayı. İşaretli fiyat günlerinde maksimum high-low farkı: +3.08% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Feb 3 NFP 517k and stronger dollar/yields. **Karşıt kanıt / alternatif mekanizma:** Silver/platinum ↓ while palladium near flat; jobs surprise cannot be pre-release factor.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-02-01 FOMC; 2023-02-03 AHE surprise=0.00; 2023-02-03 NFP surprise=332.00; 2023-02-03 UNEMP surprise=-0.20. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.aa.com.tr/en/americas/us-stocks-open-lower-after-jobs-figures/2805598; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-february-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 21. MOVE_V2_C003 · 2023-03-06 → 2023-03-23 · UP

**Gerçek altın fiyat kaydı:** +6.25%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-03-13).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +8.61%, platin +1.75%, paladyum +1.61%; S&P500 -2.46%, Nasdaq100 +3.47%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı. İşaretli fiyat günlerinde maksimum high-low farkı: +3.62% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** SVB Mar 10 and March bank contagion; gold ETF March inflow +32t. **Karşıt kanıt / alternatif mekanizma:** Nasdaq ↑ but S&P ↓; bank haven + rate relief, not universal risk-off.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-03-10 AHE surprise=-0.10; 2023-03-10 NFP surprise=106.00; 2023-03-10 UNEMP surprise=0.20; 2023-03-14 CPI surprise=0.00; 2023-03-22 FOMC. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Özgün haber: https://www.gold.org/goldhub/gold-focus/2023/03/what-next-gold-volatile-bond-market; ek literatür: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2023/04. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 22. MOVE_V2_C004 · 2023-04-27 → 2023-05-04 · UP

**Gerçek altın fiyat kaydı:** +3.45%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-05-04).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +1.91%, platin -4.46%, paladyum -5.66%; S&P500 -1.79%, Nasdaq100 -1.35%.

**Gözlenen rejim ayrımı:** Altın yukarı, ABD hisse endeksleri aşağı: güvenli-liman ayrışması ile uyumlu; kesin kriz nedeni değil. İşaretli fiyat günlerinde maksimum high-low farkı: +2.47% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Fed May 3 policy/financial instability and debt-ceiling fear candidates. **Karşıt kanıt / alternatif mekanizma:** XAG ↑ but Pt/Pd ↓, equities ↓; no curated 2023 May 4 direct first-print.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-05-03 FOMC. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-march-2023; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-april-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 23. MOVE_V2_C005 · 2023-09-22 → 2023-10-03 · DOWN

**Gerçek altın fiyat kaydı:** +4.59%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-09-29).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -10.97%, platin -5.46%, paladyum -4.96%; S&P500 -2.10%, Nasdaq100 -0.92%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu. İşaretli fiyat günlerinde maksimum high-low farkı: +1.82% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** US higher real yields, dollar increase and Sept ETF -59t/COMEX -70t. **Karşıt kanıt / alternatif mekanizma:** WGC Oct10 retrospective; late-Sep technical break, not proof all from one news item.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-october-2023; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-september-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 24. MOVE_V2_C006 · 2023-10-06 → 2023-10-19 · UP

**Gerçek altın fiyat kaydı:** +5.63%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-10-13).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +8.38%, platin +2.68%, paladyum -3.67%; S&P500 -0.71%, Nasdaq100 -1.27%.

**Gözlenen rejim ayrımı:** Altın yukarı, ABD hisse endeksleri aşağı: güvenli-liman ayrışması ile uyumlu; kesin kriz nedeni değil. İşaretli fiyat günlerinde maksimum high-low farkı: +3.32% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Israel/Gaza Oct 7 shock, gold haven bid; COMEX short-covering reported retrospectively. **Karşıt kanıt / alternatif mekanizma:** Pd ↓ as silver ↑, US stocks ↓; war cannot be priced before Oct7.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2023-10-06 AHE surprise=-0.10; 2023-10-06 NFP surprise=166.00; 2023-10-06 UNEMP surprise=0.10; 2023-10-12 CPI surprise=0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-october-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 25. MOVE_V2_C007 · 2023-11-24 → 2023-12-01 · UP

**Gerçek altın fiyat kaydı:** +3.55%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2023-12-01).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +6.14%, platin +1.74%, paladyum -3.88%; S&P500 +0.77%, Nasdaq100 +0.10%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı. İşaretli fiyat günlerinde maksimum high-low farkı: +2.04% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Late-Nov softer rates/USD, Fed pivot expectations, gold futures technical momentum. **Karşıt kanıt / alternatif mekanizma:** Silver ↑, Pd ↓: gold/silver-specific; no curated cluster-source contemporaneous.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-october-2023; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-december-2023. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


## 2024 / KISA-VADELİ EŞİK KÜMESİ

### 26. MOVE_V2_C016 · 2024-05-17 → 2024-05-27 · DOWN

**Gerçek altın fiyat kaydı:** +3.98%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2024-05-23).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş veri yok, platin veri yok, paladyum veri yok; S&P500 veri yok, Nasdaq100 veri yok. **GÜNLÜK KAYNAK UÇ TARİHİ EKSİK; bu aralıkta dolgu yapılmadı.**

**Gözlenen rejim ayrımı:** En az bir karşılaştırmalı günlük uç fiyat eksik; rejim sonucu veriyle tamamlanmadı. İşaretli fiyat günlerinde maksimum high-low farkı: +2.44% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** May 22 hawkish Fed minutes and profit-taking after May20 high. **Karşıt kanıt / alternatif mekanizma:** May27 holiday source endpoint missing for 5 daily series; no fabricated 27-May close.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Bağlamsal kaynak: https://www.kitco.com/news/off-the-wire/2024-05-23/gold-falls-one-week-low-hawkish-fed-minutes. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi PARTIAL_OR_HOLIDAY_MISSING_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 27. MOVE_V2_C029 · 2024-12-11 → 2024-12-19 · DOWN

**Gerçek altın fiyat kaydı:** +4.80%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2024-12-18).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -6.97%, platin -0.54%, paladyum -4.56%; S&P500 -3.57%, Nasdaq100 -3.00%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu. İşaretli fiyat günlerinde maksimum high-low farkı: +2.51% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Dec18 2024 Fed cut with hawkish future dot guidance, USD/yields rise. **Karşıt kanıt / alternatif mekanizma:** Silver/palladium/stocks ↓; WGC Jan8 2025 retrospective, not first-print.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2024-12-11 CPI surprise=0.00; 2024-12-18 FOMC. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-december-2024. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


## 2025 / KISA-VADELİ EŞİK KÜMESİ

### 28. MOVE_V2_C030 · 2025-01-29 → 2025-02-10 · UP

**Gerçek altın fiyat kaydı:** +3.91%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-02-05).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +6.00%, platin +4.34%, paladyum +2.09%; S&P500 +0.45%, Nasdaq100 +1.61%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı. İşaretli fiyat günlerinde maksimum high-low farkı: +1.99% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Early-Feb 2025 tariff fears; COMEX gold stock inflows and EFP basis dislocation. **Karşıt kanıt / alternatif mekanizma:** All three metals ↑, equities slightly ↑; Feb27 WGC COMEX quantitative retrospective.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-02-07 AHE surprise=0.20; 2025-02-07 NFP surprise=-26.00; 2025-02-07 UNEMP surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.kitco.com/news/off-the-wire/2025-02-04/gold-steadies-after-record-rally-tariff-concerns-loom-large; ek literatür: https://www.gold.org/goldhub/gold-focus/2025/02/you-asked-we-answered-threat-us-tariffs-moving-gold-market. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 29. MOVE_V2_C031 · 2025-03-10 → 2025-03-19 · UP

**Gerçek altın fiyat kaydı:** +4.02%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-03-13).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +4.35%, platin +1.54%, paladyum +0.73%; S&P500 +1.08%, Nasdaq100 +1.57%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı. İşaretli fiyat günlerinde maksimum high-low farkı: +1.87% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** March tariff and geoeconomic concern, weaker USD; March gold ETF inflows. **Karşıt kanıt / alternatif mekanizma:** ETF monthly summary published April; no exact March 13 firstprint from original.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-03-12 CPI surprise=-0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-march-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 30. MOVE_V2_C032 · 2025-03-24 → 2025-04-02 · UP

**Gerçek altın fiyat kaydı:** +3.70%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-03-31).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +2.37%, platin 0.00%, paladyum +2.70%; S&P500 -1.67%, Nasdaq100 -2.97%.

**Gözlenen rejim ayrımı:** Altın yukarı, ABD hisse endeksleri aşağı: güvenli-liman ayrışması ile uyumlu; kesin kriz nedeni değil. İşaretli fiyat günlerinde maksimum high-low farkı: +1.67% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Tariff deadline April2, physical gold and ETF demand, dollar weakness. **Karşıt kanıt / alternatif mekanizma:** US equities ↓ while gold rises; March31 Reuters article dated during, not proven first-minute.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Özgün haber: https://www.reuters.com/markets/commodities/gold-sails-above-3100-uncharted-territory-us-tariffs-approach-2025-03-31/; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-march-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 31. MOVE_V2_C033 · 2025-03-31 → 2025-04-08 · DOWN

**Gerçek altın fiyat kaydı:** +4.65%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-04-04).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -10.98%, platin -7.04%, paladyum -6.12%; S&P500 -11.21%, Nasdaq100 -11.35%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu. İşaretli fiyat günlerinde maksimum high-low farkı: +4.02% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** April reciprocal tariffs, liquidity deleveraging and EFP/physical spread compression. **Karşıt kanıt / alternatif mekanizma:** Metals and US equities ↓ >~6-11%; May8 WGC retrospective cannot be pre-April input.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-04-04 AHE surprise=0.00; 2025-04-04 NFP surprise=91.00; 2025-04-04 UNEMP surprise=0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-april-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 32. MOVE_V2_C034 · 2025-04-04 → 2025-04-22 · UP

**Gerçek altın fiyat kaydı:** +8.57%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-04-09).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +4.05%, platin +3.08%, paladyum +1.83%; S&P500 +4.21%, Nasdaq100 +5.05%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı. İşaretli fiyat günlerinde maksimum high-low farkı: +4.37% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** US dollar plunge and renewed safe-haven inflow amid tariff escalation, ETF demand. **Karşıt kanıt / alternatif mekanizma:** Apr4-Apr22 window includes both crisis sell-off then rebound; net endpoint cannot prove one monotonic regime.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-04-04 AHE surprise=0.00; 2025-04-04 NFP surprise=91.00; 2025-04-04 UNEMP surprise=0.10; 2025-04-10 CPI surprise=-0.20. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-april-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 33. MOVE_V2_C035 · 2025-04-23 → 2025-04-23 · DOWN

**Gerçek altın fiyat kaydı:** +3.04%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil.

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş 0.00%, platin 0.00%, paladyum 0.00%; S&P500 0.00%, Nasdaq100 0.00%. **TEK-GÜN BAZ HATASI:** beş varlıkta 0% aynı gözlemin kendisine oranıdır; piyasa etkisi/gerçek kısa ufuk reaksiyonu değildir.

**Gözlenen rejim ayrımı:** Çapraz piyasalar tek yönlü değil; tek-faktör makro açıklaması yetersiz. İşaretli fiyat günlerinde maksimum high-low farkı: +3.88% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Sharp one-day drop after April records; profit-taking/USD/risk appetite candidate. **Karşıt kanıt / alternatif mekanizma:** V3 source baseline same calendar date April23 => cross-market endpoint returns 0 by construction, NOT evidence of no reaction.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Bağlamsal kaynak: https://www.gold.org/goldhub/research/gold-market-commentary-april-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi SAME_DAY_REFERENCE_INVALID_ZERO_INFORMATION; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 34. MOVE_V2_C040 · 2025-05-14 → 2025-05-26 · UP

**Gerçek altın fiyat kaydı:** +4.97%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-05-21).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş veri yok, platin veri yok, paladyum veri yok; S&P500 veri yok, Nasdaq100 veri yok. **GÜNLÜK KAYNAK UÇ TARİHİ EKSİK; bu aralıkta dolgu yapılmadı.**

**Gözlenen rejim ayrımı:** En az bir karşılaştırmalı günlük uç fiyat eksik; rejim sonucu veriyle tamamlanmadı. İşaretli fiyat günlerinde maksimum high-low farkı: +2.40% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** US Treasury auction debt/deficit concern, policy/tariff risk and interest-rate volatility. **Karşıt kanıt / alternatif mekanizma:** May26 holiday missing daily endpoint; cannot infer direction of all metals from absent quotes.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak olay penceresinden sonra yayımlanmış; olay öncesi bilgi sayılmaz. Özgün haber: https://www.gold.org/goldhub/research/gold-market-commentary-may-2025; ek literatür: https://www.reuters.com/business/tepid-demand-us-treasury-auction-shows-investor-jitters-about-tax-bill-deficit-2025-05-21/. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi PARTIAL_OR_HOLIDAY_MISSING_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 35. MOVE_V2_C050 · 2025-11-12 → 2025-11-17 · DOWN

**Gerçek altın fiyat kaydı:** +3.67%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-11-14).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş -0.93%, platin -2.02%, paladyum -4.42%; S&P500 -2.61%, Nasdaq100 -2.81%.

**Gözlenen rejim ayrımı:** Altın ve bazı diğer piyasalarda eş yönlü satış: risk azaltma veya ortak finansal koşullar ile uyumlu. İşaretli fiyat günlerinde maksimum high-low farkı: +4.44% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Nov 2025 Fed-rate repricing and positioning/profit-taking candidates. **Karşıt kanıt / alternatif mekanizma:** Stocks and metals ↓ concurrently, but no verified cluster-specific event catalyst.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Bağlamsal kaynak: https://www.reuters.com/world/india/gold-holds-steady-focus-turns-us-data-more-fed-cues-2025-11-17/. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 36. MOVE_V2_C051 · 2025-11-21 → 2025-11-28 · UP

**Gerçek altın fiyat kaydı:** +3.79%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-11-28).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +10.23%, platin +9.07%, paladyum +4.92%; S&P500 +3.73%, Nasdaq100 +4.93%.

**Gözlenen rejim ayrımı:** Gümüş/platin/altın hareketi destekliyor; hisse rejimi karışık veya yukarı. İşaretli fiyat günlerinde maksimum high-low farkı: +1.75% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Late-Nov policy easing and precious metal momentum candidates. **Karşıt kanıt / alternatif mekanizma:** Ag/Pt/Pd plus equity ↑; original legacy ETF report published Dec, no dated catalyst for Nov28.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/12; ek literatür: https://www.gold.org/goldhub/research/gold-market-commentary-december-2025. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 37. MOVE_V2_C052 · 2025-12-15 → 2025-12-26 · UP

**Gerçek altın fiyat kaydı:** +4.65%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-12-22).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş veri yok, platin veri yok, paladyum veri yok; S&P500 +1.66%, Nasdaq100 +2.30%. **GÜNLÜK KAYNAK UÇ TARİHİ EKSİK; bu aralıkta dolgu yapılmadı.**

**Gözlenen rejim ayrımı:** En az bir karşılaştırmalı günlük uç fiyat eksik; rejim sonucu veriyle tamamlanmadı. İşaretli fiyat günlerinde maksimum high-low farkı: +2.57% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** Year-end rate-cut hopes and geopolitical uncertainty, option flows, precious metal rally. **Karşıt kanıt / alternatif mekanizma:** Dec26 daily metal endpoints unavailable; Dec22 Reuters during, Jan8 WGC postevent.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** 2025-12-16 AHE surprise=-0.20; 2025-12-16 NFP surprise=13.00; 2025-12-16 UNEMP surprise=0.10. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Tarihli özgün vaka-haberi doğrulanmadı. Özgün haber: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/12; ek literatür: https://www.reuters.com/business/gold-silver-soar-year-end-rally-2025-12-22/. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi PARTIAL_OR_HOLIDAY_MISSING_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


### 38. MOVE_V2_C053 · 2025-12-23 → 2025-12-31 · DOWN

**Gerçek altın fiyat kaydı:** +4.80%; ölçüm: farklı saat/seans ufuklarının işaretlenmiş fiyat hareketindeki maksimum mutlak büyüklüğü; pencere net getirisi değil (ilk tespit edilen eşik gün etiketi: 2025-12-29).

**Ayrı kaynaklardan tarih sonu–başı sayısal veri:** Gümüş +3.23%, platin -6.93%, paladyum -13.09%; S&P500 -0.93%, Nasdaq100 -1.32%.

**Gözlenen rejim ayrımı:** Çapraz piyasalar tek yönlü değil; tek-faktör makro açıklaması yetersiz. İşaretli fiyat günlerinde maksimum high-low farkı: +5.78% (uygulanabilir yön/getiri değildir).

**Temel ekonomik etken hipotezi:** CME futures margin increase after strong rally, leveraged metal deleveraging and thin year-end liquidity. **Karşıt kanıt / alternatif mekanizma:** Whole Dec23-Dec31 silver +3.23% while platinum/palladium ↓: window net differs Dec29 one-day plunge.

**Makro yayınları (eski kısmî defterde tarih içine düşen açıklamalar):** takvim defterinde olay penceresine denk gelen doğrulanmış satır yok. Takvim çakışması otomatik fiyat nedeni veya önce-bilinir alarm değildir.

**Haberin kullanılabilirlik sınırı:** Kaynak dönem içinde tarihlenmiş; ilk yayın dakika-saat ve karar saatine uygunluğu kanıtlanmadı. Bağlamsal kaynak: https://apnews.com/article/c49577dedd4c799005de5b7af552ce81. İlk haber baskısı UTC ve piyasanın kaynağı gerçekten ne zaman işlediği bağımsız kanıtlanmadı.

**Vaka sonucu:** Fiyat etiketi arşivde mevcut; çapraz varlık gözlemi DATA_CO_MOVE_PLUS_DATE_SOURCE_CAUSE_UNPROVEN; ekonomik etkenin nedensel etkisi **DOĞRULANMADI**, işlem öncesi model girdisi **ONAYLANMADI**.


## Bilerek kesinleştirmediğimiz hususlar ve ileri eşleştirme kapısı

- **Holiday/date mismatch:** C016 (2024-05-27 ABD tatili), C040 (2025-05-26 ABD tatili) ve C052 (2025-12-26 eksik metaller) başka günün fiyatına sessizce taşınmadı. Sonraki aşamada kaynak-takvim uyumlu önceki son işlem günü ve gerçek saat kesimi ayrı bir kaynak-düzeltme dosyasında hesaplanmalı.
- **C035:** 2025-04-23'te V3 hakem baseline ile olay son günü aynıdır; 0'lar ancak aynı gözlemi böldüğümüzü söyler. Fiyat tepkisi için son geçerli **önceki** 15m/NY17 baseline saatini gerçek kaynaktan yeniden bağlamak gerekir. Mevcut fiyat cluster yönünü 0'lar reddetmez.
- **2023'te altın 2023-01-03→02-01 +%6.065 iken gümüş −%3.29/platin −%7.27/paladyum −%9.20.** Bu, aynı dönem altın pozitif ≠ tüm değerli metal talebi pozitif farkını gösterir. Yorum: dolara/faize altın-özgü duyarlılık adayı; altının sebebini ispatlamaz.
- **2025 Mayıs tarife anlaşması:** 6–14 Mayıs altın ZigZag −%7.208 iken karşılaştırılabilir S&P +%5.09 / Nasdaq +%7.72 ve Pt +%1.94: genel hisse satışı değil, güvenli liman primi çözülmesiyle uyumlu. Bu ekonomik haberin Mayıs 12 ilk günü öncesi bilinmesi mümkün değil.
- **2024 Mart–Nisan altın yükselişinde V1 +%19.989, Stak silver +%27.87, platinum +%6.81, palladium +%16.23; ABD hisseleri düşmüş:** tek USD ve hisse risk-on faktörü açıklamada yetersiz. WGC Mart/April raporları opsiyon/implied vol, Çin/OTC ve merkez-bankası talebi üzerinde duruyor; bazı raporlar söz konusu olayın **sonrasında** yayımlandı.
- **2025 Nisan 4–22 kümesinde** altın hem önce riskten kaçışla düşüş hem sonra zayıf dolar/ETF ile yükseliş yaşadı; kümülatif uç-fark yönü ile ana kısa-ufuk UP bayrağı aynı matematiksel nesne değildir.
- ETF, CFTC, GC/SI/ZN/NQ/CL futures, USD, 2Y/10Y reel/nominal faiz, GVZ/VIX, FED sürprizi ve EFP/fiziki altın akışı **her 38 olay için saatli geçmiş kaynak-vintage ortak tabloda tamamlanmadı**. İşaretli haber/otorite yorumundan gözlenmemiş intraday feature **üretilmedi**. Retrospektif regime tanısı ileriye dönük predictability ispat etmez.
- Kaynaklar korunacak, özgün olay satırları overwrite edilmeyecek. Olay metrikleri (NY17 long leg / short max move / bank ask-bid / next-hours) otomatik toplanmayacak. Ocak2026 özel V4 tekrar testleri en son ayrı araştırma olup geçmiş olay katalogu üzerinde yeni model seçimine sızıntı yaratamaz.

**Hüküm:** `38/38_SOURCE_ROW_PRESERVED | 35_EXACT_DAILY_ASSET_MATCH | 3_CALENDAR_GAPS | 1_SAME_DAY_UNINFORMATIVE | 38_EVENT_HYPOTHESIS_EVALUATED | ZERO_CAUSALITY_PROMOTIONS | ZERO_NEW_BANK_SIGNALS`.

**Özgün kaynak:** [Olaylar CSV](GOLD_HISTORICAL_38_MISSING_CASES_CAUSAL_DATA_EVIDENCE_V1_20261013.csv) · [Özgün 42 uzun bacak](GOLD_MAJOR_MOVE_EVENT_ATLAS_2023_2025_V1_20261013.csv) · [53 kümenin orijinal araştırması](GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_53_CLUSTER_NEWS_RESEARCH_20261013.csv) · [V4 nedensellik eleştirisi](GOLD_EVENT_CHAIN_2023_2025_V4_FACT_CHECKED_CAUSAL_AUDIT_20261013.md).
