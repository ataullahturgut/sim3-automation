# GOLD GUARD V3 — İlk çalışan motorun tarihsel denetimi

**Sürüm:** RECOVERY_HOLD_V3_FINITE_STATE_SHADOW_20261015. **DURUM:** Araştırma/gölge deney, doğrulanmış yatırım algoritması değil.

## 1) Kod ve öğrenme mimarisi
- `recovery_v3.js` yürütülebilir olay/evre/maliyet/portföy kodudur; sadece rapor taslağı değildir.
- Gerçek HistData XAUUSD M15 kaynaklarından önceden tamamlanmış karar kesitleri türetilmiştir, 3 saatlik UTC 00,03,...,21 kontrol zamanları: 2020=1889, 2021=1916, 2022=1920, 2023=1299, 2024=1914, 2025=1912; **toplam 10.850 kayıt**. 2023 kapsamı dikkat çekecek ölçüde eksiktir, yıllar doğrudan tüm-yıl başarı diye genellenemez.
- 2020–2025 geçmişinde aralarında en az 96 saat olan **65 tarihli ve ileri etiketi olgunlaşmış** stres başlangıcı ayrıldı. Bu sayı istatistiksel olarak bağımsız ekonomik neden kanıtı değildir; 96h gelecek düşük/yüksek, yalnız o vaka geçmişte tamamlandıktan sonra olay defterine alınır. OHLC ekstremi değil, 3h örnek kapanışlarından yaklaşık ekstremdir.
- G05-C (finansal stres/likidite) ve G06-B (pozisyon çözülmesi) yalnız **ÖĞREN-03 ekonomik hipotez adayıdır**; hangi olayın nedenselliği oldukları bilinmiyor. Bu çalışma yalnız XAU'nun fiyat-evre durum makinesidir, gerçek ilk haber/fed/faiz/dolar çapraz teyitli ekonomik DNA motoru değildir. Ekonomik neden her satırda `UNRESOLVED`.
- Fiyat evreleri: `CAPITULATION_CANDIDATE`, `FALLING_FAST`, `STABILIZING`, `RECOVERY_CANDIDATE`, `UP_TREND`, `FAILED_REBOUND`, `UNKNOWN`. Giriş için iki üst üste teyit, toparlanmada başlangıçta %50 kademeli pozisyon (%25 eğer yeterli tarihsel kötü vaka örtüşmesi varsa). Trendde tamamlayıcı giriş. Koruyucu çıkış için ayrı düşüş/maliyet/histerezis kapıları.
- **Sadece Türkiye 09.00/12.00/15.00 emir proxy'si** (09.00–17.00 banka işlemi kısıtı) ve alış/satış ayrı ayrı %0,8 komisyon kullanıldı. Gerçek banka ASK/BID ve kayma bilinmediğinden gerçek uygulanabilir kâr değildir.
- `recovery_v3.test.js` geçmiş etiket ambargosunu, durumu, kararı, kaynak kimliğini, 09–17 işlemlerini ve V1 sonucunun korunmasını denetler. GitHub CI Windows/Ubuntu üzerinde çalışır.

## 2) Tarih sıralı yıllık test — 100 dolar ile her yıl bağımsız başlangıç

| Yıl | Eğitim yalnız önceki yıl(lar) | V3 yıl sonu | Aynı kaynakta AL ve TUT | İşlemler | Yorum |
|---|---|---:|---:|---:|---|
| 2023 | 2020–2022 / 38 vaka | **110,57 $** | 110,32 $ | 1 | Kapsam eksik (1299 üç saatlik gözlem); adil tam-yıl zaferi değil |
| 2024 | 2020–2023 / 40 vaka | **119,39 $** | **124,43 $** | 6 | Pasif altının gerisinde |
| 2025 | 2020–2024 / 53 vaka | **141,89 $** | **161,15 $** | 8 | Pasif altının belirgin gerisinde |

**2025 kritik sonuç:** V3 +%41,89 yaparken koşu içi sürekli altın +%61,15 oldu. Artan varlıkta aşırı temkinli kalma ve pozisyon devri maliyeti ciddi darboğazdır. Bu sayılar retrospektif ve parametreleri ileride değiştirmek için kullanıldığından bağımsız kör OOS diye sunulmaz.

## 3) Ocak–Şubat 2026 bulguları
- V3 Ocak (ayrı 100$ nakit başlangıç) **110,981208 USD** buldu; V1 Ocak 119,753917 USD. **V3 Ocak başarısız.** V1 orijinal referansı asla değiştirilmedi.
- V3 Şubat **Ocak V1'den devredilen tam 119,75391720039644 USD nakit** başlangıcıyla ayrıca çalıştı; V3 Ocak 110,98 USD buraya devredilmedi. Şubat sonunda **120,442259686 USD**, pozisyon **GOLD**. Elde altın olduğundan net değer ayın son gözlemi üzerinden teorik çıkış masrafı düşülerek hesaplandı.
- V1 Şubat 15m **114,274468 USD**; hiç işlem yapmadan nakit **119,753917 USD**; Şubat ilk fiyatıyla AL/TUT karşılaştırması **132,906170 USD**. V3 ilk ciddi toparlanmayı 4 Şubat 09.00 TSİ **5079,185 USD/ons** alım ile gördü, fakat **5 Şubat 09.00 TSİ 4895,625 USD/ons** koruyucu satışı yaptı; hata/yanlış toparlanma örneği. 19 Şubat 12.00 TSİ 5016,925 üzerinden yeniden altına girdi.
- V3 Şubat, V1 Şubat'tan yaklaşık **+6,17 USD** yüksek ama nakit beklemeye üstünlüğü yalnız **+0,69 USD**. Bu, yeni modelin 132,91 dolarlık erken-tam-giriş hedefine erişmediğini gösterir.
- **ÖNEMLİ:** Şubat örneği V3 tasarlanmadan önce görülmüştü; üstünlük geriye dönük stres karşılaştırmasıdır, gerçek bağımsız OOS kanıtı değildir.

## 4) Kalan eksikler ve V4 adayları
1. İlk 2 gün yoğun çöküş ve yeniden yükselişte *piyasa kapanış saatine bağlı* üç saatlik karar gecikmesi ölçülmeli; kısa pencere sinyali daha sık izlenebilir ama kullanıcı 09–17 dışında gerçek alım-satım yapılamaz.
2. 4 Şubat AL→5 Şubat SAT, eksik dalga güvenini ve yanlış dönüşü gösteriyor. Pozisyon boyutunu azaltan, maliyet-sonrası beklenen avantajı kullanabilen model kalibre edilmeli; katı zorunlu bekleme, yeni crash ile mücadelede yanlış olabilir.
3. 2024–2025'te pasif altının gerisinde kalma, GOLD'da HOLD süresinin çok kısa kaldığı dönemlerin epizot bazında incelenmesini gerektiriyor. Her yılı yalnız final USD ile seçme.
4. G05-C/G06-B gibi ekonomik mekanizma için as-of haber firstprint ve çapraz teyit gerekli. `UNRESOLVED` olan nedenle sahte güven üretme.
5. 2023 veri eksikliği araştırılmalı; gerçek BID/ASK/piyasa makası (bankanın %0,8 ücretinden ayrı) yoksa işlem maliyeti sadece alt sınırdır.
6. V3'ün konum ve durum karar günlüğündeki tüm işlemleri/fiyatları okunabilir; sonraki aylarda ve birden çok bağımsız rejimde sürüm kilitlemeden `VALIDATED` unvanı verilmez.

## 5) Program kullanım
- Uygulamada sol menü **Yeni V3 toparlanma modeli** → **V3 sonuçlarını hesapla ve karşılaştır**.
- V3 ayrı `/api/algorithm/v3` GET ile çalışır; V1 ana panodaki Ocak ve Şubat performansını değiştirmez.
- Komut isteyen araştırmacı için: `npm run verify-v3`, `npm test`; normal kullanıcı yalnız `BASLAT.bat`.
- Kaynak dosyalarının Git blob SHA denetimi aktiftir: 2020–22 `e19d69fbbf4a825420a07d7e5f678899d1e0f805`, 2023–25 `a588b6745f893fcafc935fa486328a6349caa658`.

**SONUÇ:** Çalışan V3 algoritması kuruldu, veriler ve gerçek simülasyon sonuçları üretildi; ancak maliyetli AL/SAT stratejisinin bağımsız ve kalıcı biçimde pasif altın veya nakitten üstün olduğu gösterilemedi. İlerleme “çalışan araştırma motoru” düzeyindedir, “uygulanabilir sürekli öğrenen yatırım sistemi” düzeyinde değil.

## Veri kapanışı düzeltmesi
Model ikinci doğrulamada piyasa kapalıyken geçen süreyi iki bağımsız toparlanma teyidi saymamayı garanti etti: son uygun 3h kesit ile yeni kesit arasında 12 saatten fazla boşluk olduğunda evre teyit sayacı sıfırlanır. Şubat 1'de veri yokken nakit ilk durum $119,753917 olarak korunur. Bu düzeltmeden sonra Şubat sonucu aynı $120,442260 kalmış, 2024 yıllık sonuç $119,389706 olarak düzelmiştir. İzinsiz ticaret saati veya hayalî piyasa verisi üretilmez.

## İlk banka saatindeki pasif alternatifin doğru hesabı
Şubat ilk tam M15 gözlemi 2 Şubat **06.45 Türkiye** saati (p=4665,628), banka 09–17 işlem penceresinin **dışında**. Bu fiyatla ay sonuna dek AL/TUT sonucu 132,906170 USD'dir ama işlem saati kullanıcı kısıtına uymaz. **2 Şubat 09.00 Türkiye** saatinde (06:00 UTC) ilk banka zamanlı karar p=4547,265, aynı altın son fiyatı 5261,895 ve %0,8+%0,8 proxy komisyonla ay sonu pasif karşılaştırma **136,365650 USD**. 09.00 as-of sinyali XAU 4 saatlik getiri -%3,974, 92-bar getirisi -%12,946, downside varyans payı 0,905 ile çok sert düşüş rejimidir. Bu yüksek pasif kâr **yalnız geriye dönük fırsat maliyeti üst sınırı**: gelecekteki Şubat yükselişi o saatte bilinmiyordu. V3'ün %50 kademeli girişi 4 Şubat 09.00 TSİ'dedir. Mevcut V1 frozen grafik/benchmark rakamlarını bu açıklama için geriye dönük değiştirmiyoruz.
