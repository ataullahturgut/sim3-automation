# V12 — 2010–2019 Çok-değişkenli vaka çalışmasının gerçek veri durumu ve yürütme kayıtları

Tarih: 26 Ekim 2026. İleriye dönük **risk algılama** çalışması; fiyat tahmini değil. Kapsam 2010–2019 vaka öğrenimi (2020–2022 dışarıda), 2025 seçim, 2026 stres karşılaştırması. **Bu rapor yeni CFTC/GVZ/Fed ile eğitilmiş model sonucu değildir.**

## Önceki yöntemdeki hata

V11, 2010–2019 örneklerinin riskini yalnızca altının fiyat özelliklerine göre öğrenmişti; 2011–2013 olayları için CFTC, GVZ, USD ve faiz analizini yapmamıştı. Bu önceki kabul edilmiş kapsamdan sapmadır. Yeni çalışmada V11 ana modele terfi ettirilmiyor.

## Neon read-only 2010–2019 gerçek kontrol

- AU, AG, PT, PD: her biri 2.526 aynı günlük gözlem; `XAU_STAKTRAKR_RESEARCH_DAILY_R1`, `XAG_...`, `XPT_...`, `XPD_...` ve aynı sürüm / sağlayıcı / kalite filtresiyle.
- 2010–2019 günlük CFTC GC/SI, Cboe GVZ ve H.15/H.10 broad USD/DGS10/DFII10, veritabanında bu döneme ait mevcut değil. 2016 sonrası sadece aylık DGS10 ALFRED kayıtları ve aylık diğer göstergeler var, 2011/2013 günlük first-print gibi kullanılmıyor.
- Günlük dört metal verileri tarihsel geriye dönük referans serisidir; gerçek gün sonu ilk yayımlanan spot fiyat vintajı ayrıca ispatlı değil.

### Fiyat dışındaki metallerin ilk araştırma kontrolü (bu bir model koşusu değil)

Aynı günlü altın/gümüş/platin/paladyum panelinde `t-5..t` geçmiş beş **işlem günü** getiri özellikleri alındı, değerlendirme sınıfı `min(P[t+1..t+5])/P[t]-1 <= -5%` olarak ayrı ve geriye dönük etiketlendi. Sadece 2011 ve 2013 karar tarihleri:

| Yıl ve sınıf | Karar günü | Altın önceki 5g ort. | Gümüş önceki 5g | Platin önceki 5g | Paladyum önceki 5g |
|---|---:|---:|---:|---:|---:|
| 2011 sonrası 5g sert düşüş | 15 | +0.79% | -0.23% | -0.51% | +1.00% |
| 2011 düşüş etiketi yok | 236 | +0.26% | +0.14% | -0.36% | -0.33% |
| 2013 sonrası 5g sert düşüş | 19 | -1.95% | -2.58% | -2.56% | -3.56% |
| 2013 düşüş etiketi yok | 234 | -0.48% | -0.60% | -0.03% | +0.38% |

Düşüş etiketli başlangıç günleri birbiriyle örtüşür; bağımsız kaza/çöküş sayısı değildir. Sayılar geçmiş fiyatlarla sonradan tanımlanmış etiket sınıfının **betimleyici ortalamalarıdır**; örnekleme sapması ve dönem farkı olabileceğinden hiçbir katsayı, eşik veya alarm gerekçesi çıkarmadık.

2011 ve 2013 öncesindeki metallerin davranışı farklı olabildiği için tek “altın düştüğünde öncesinde gümüş mutlaka şöyle olmalı” kuralı çıkarılamaz. Negatif kontroller aynı yılın diğer günleridir; henüz eğilim-volatilite eşleştirilmiş kontrol örneği değildir.

## Resmî makro arşivler bulundu, tam üretim indirmesi ayrı çalıştırma aşaması

- CFTC resmî **Disaggregated Futures Only** yıllık 2010–2019 ZIP: `https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm`, COMEX GC=088691, SI=084691.
- Cboe resmî GVZ 2008+ günlük arşiv: `https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv`.
- Fed H.15 nominal 2/10 yıllık, enflasyona endeksli reel 10Y: `DGS2`, `DGS10`, `DFII10`. FRED güncel retrospektif geçmiş sadece araştırma, first print/vintage değil.
- Eski H.10 `DTWEXB` eski broad USD dönemi 2011/2013; bugünkü `DTWEXBGS` ancak 2019'da ilk yayımlandı. 2011/2013'te DTWEXBGS biliniyormuş gibi kullanmak veri sızıntısıdır ve yasaktır.
- Script: `gold_axis_2026/tools/gold_risk_legacy_macro_acquisition_v12.py`; workflow `.github/workflows/gold-risk-legacy-2010-2019-official-v12.yml`.
- Bu workflow'a `V12_LEGACY_OFFICIAL_DOWNLOAD_TRIGGER_20261026.md` ile **push tetikleyicisi commit edildi**; connectorun Actions çalıştırma durumunu burada doğrulayamadığımız için **arşivlerin başarıyla indirildiği iddia edilmiyor**. Actions artifact varsa incelenip yayın saatleri denetlenmeden model eğitimi yapılmayacak.

## Sonuç / Gate

**Eski tek-altın V11 adayı reddedildi.** 2011/2013 dört metal verisi araştırıldı. CFTC/GVZ/USD/H.15 arşiv indirme ve günlük as-of kanıtı henüz tamamlanmadı; yeni çok değişkenli model henüz eğitilmedi. BASE14/CFTC21/V10 sonuçları ve Neon/üretim sistemi aynen korunuyor.
