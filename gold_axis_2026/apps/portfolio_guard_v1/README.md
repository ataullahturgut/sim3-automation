# GOLD Portfolio Guard V1 — sabit tarihsel koşu uygulaması

**Statü: RESEARCH_ONLY · READ_ONLY · LOCALHOST_ONLY · BANKAYA EMİR YOK**

Bu uygulama, Ocak 2026 altın koruma deneyinin aynı veri, aynı parametreler ve aynı motorla her seferinde **aynı sonucu vermesini** sağlar. Canlı tavsiye veya alım-satım emri üretmez.

## Başlatma — Windows PowerShell

GitHub dalı: gold-portfolio-guard-app-v1-20261015

Repo klasöründe:

    cd gold_axis_2026\apps\portfolio_guard_v1
    node --version
    npm test
    npm run verify
    npm start

Tarayıcıdan: http://127.0.0.1:8787

Kapatmak için ilgili PowerShell penceresinde Ctrl+C. Node.js 18+ gerektirir; harici NPM paketi veya internet bağlantısı gerekmez. Yerel sunucu yalnızca 127.0.0.1 adresinde çalışır.

## Sabit API
- GET /api/health — model ve veri kontrolü
- GET /api/summary — üç dondurulmuş modelin kıyaslaması ve kaynak imzaları
- GET /api/replay?mode=event15m — tam 2.976 slot karar defteri
- GET /api/replay?mode=price15m — yalnız fiyat
- GET /api/replay?mode=legacy3h — eski 3 saatlik karşılaştırma

İşlem türü yalnız GET; kullanıcı arayüzü hesaplama formülü çalıştırmaz, motordan gelen verileri görüntüler.

## Ocak 2026 başlıca referans sonuçlar

| Senaryo | 100 $ net son değer | Koruma satışı |
|---|---:|---|
| Olay benzerliği ve fiyat · 15 dk | **119,753917 $** | 29 Ocak 18.15 TSİ |
| Yalnız fiyat · 15 dk | **119,753917 $** | 29 Ocak 18.15 TSİ |
| Eski fiyat · 3 saat | **118,337853 $** | 29 Ocak 21.00 TSİ |

İlk 15 dakikalık alış 5 Ocak 2026 09.30 TSİ, 4.424,055 XAU MID; satış 29 Ocak 2026 18.15 TSİ, 5.383,775 XAU MID. Net sonuç 119,753917 dolar nakit; ay sonuna kadar nakitte.

Maliyetler %0,8 alım + %0,8 satım; **gerçek banka ASK/BID spreadi, slippage, stopaj yok**. Al-ve-tutun aynı 15 dakikalık veri sonuyla teorik tasfiye karşılığı yaklaşık 111,195133 dolar.

Ocak içinde olay öğrenme katmanı, fiyat modelinin işlem kararlarını **değiştirmedi**. Olay bazlı ek net getiri **0 $**. Yakın olaylara verilen skor **kalibre edilmiş olasılık değil**; ekonomik nedensellik ve ilk yayımlı haber verisi henüz kanıtlanmış değil. Ocak 2026 bağımsız ileri test DEĞİLDİR.

## Sürüm ve veri güvenliği
1. Veri ve kaynak vaka dosyalarının **Git blob SHA-1** kimlikleri engine.js içinde sabittir. Bir bayt değişiklikte uygulama hata vererek durur.
2. Komisyonlar ve koşullar engine.js içinde donduruldu. Yeni mantık yeni model VERSION ile ayrı kaydedilmeli.
3. Türkiye saat dilimi Europe/Istanbul. 2.976 Ocak takvim slotunun 1.804'ünde yeni, yeterli M15 veri var. Eksik zamanlarda yeni işlem verilmez.
4. Sadece tamamlanmış CME H1 geçmişi kullanıldı; XAU alım-satımı bir sonraki M15 open MID vekil fiyatından modellendi.
5. 2023–2025 arşivindeki yalnız ilk Ocak 2026'dan önce 96 saatlik ileri fiyat sonucu olgunlaşmış 92 vaka eğitim benzerliği için kullanılabildi. Arşiv, gerçek ilk haber zamanı / nedensellik doğrulaması yerine geçmez.
6. npm test, referans gelir, işlem saatleri, tam slot sayısı, kadans karşılaştırması ve kaynak kimliklerini kontrol eder.
7. Ocak sonu portföy durumu: 119,753917 $ **NAKİT**, altın 0 ons. Şubat'a nakit ve öğrenme notları birlikte devredilmeli.
8. Repo'nun var olan altın tahmin uygulamalarına müdahale edilmedi. Bu uygulama yeni dalda ve ayrı klasördedir.

## Bilerek ertelenen işlevler
- Mart ve sonraki aylara genelleştirilmiş ay-ay motor / veri ithalatı
- Geçmişe bakmayan model güncelleme/değişiklik kaydı ve aylık run-id defteri
- Zaman doğrulanmış haberlerin ekonomik DNA P0–P5 evreleriyle gerçek entegre öğrenilmesi
- Olaysız negatif kontroller, şok kalibrasyonu ve bağımsız performans testleri
- Gerçek banka ASK/BID / likidite / işlemin verilebilme saatleri

**Ocak ve Şubat 2026 çalıştırılabilir.** Mart ve sonraki aylar henüz eklenmedi. Şubat için V1 karar kuralları Ocak'tan değiştirilmeden devredildi.

Kaynak: gold_axis_2026/adaptive_volatility_learning/months/2026-01-new-learning/JAN_2026_NEW_EVENT_MONTH_WALK_V1_SCIENTIFIC_REPORT.md


## 15 Ekim 2026 — V2 bilimsel algoritma denetimi eklendi
**Algoritma V2 denetimi** sol menüde ayrı bir bölüm. Ocak 2026'nın V1 işlem sonuçlarını değiştirmez.

Düzeltmeler: OLAY-02 aynı checkpoint kopyalarının tekilleştirilmesi; **163** takvimle seçilmiş geçmiş kontrolünün karşılaştırılması; tarihsel risk oranının gerçek olasılık olmadığının açık işaretlenmesi; **%1,6194** tam tur asgari komisyon eşiği; ekonomik ilk haber ve nedensellikte **UNRESOLVED**; 96 saat ileri etiketin olgunlaşma kontrolü; sonraki aya yalnız olgun bilgi aktarımı.

Özellikle 2025 tarihle sıralı kontrol örneklerinde V2 basit yakın-komşu tahmininin Brier hatası **0,115535**, sabit tarihsel taban **0,115346**: Henüz daha iyi tahmin göstermedi. Bu nedenle yeni olay skoru otomatik işlem açamaz. V1 Ocak getirisi **119,753917 USD** olarak korunur.

Kaynak:
- `event_audit_v2.js` — kaynaklı cevaplar, olay deduplikasyonu ve takvim kontrol riski.
- `data/CALENDAR_CONTROLS_2023_2025_M15_96H_V1.csv` — 163 bağımsız takvim örnek noktası, 96 saat ileri etiketleri yalnız eğitim sonuç alanıdır.
- `monthly_learning_v2.js` — 29 Ocak satışının ileri etiketini 2 Şubat'a kadar bekletir.
- `V2_ALGORITHM_SCIENTIFIC_AUDIT_20261015.md` — sonuç, yanlışlama ve henüz eksik bilimsel doğrulamalar.
- `npm.cmd test` ve `npm.cmd run audit` — Windows doğrulaması.

**Önemli:** V2 bir onaylı ekonomik tahmin sistemi veya banka emir motoru değildir. Şubat ayı stratejisi için henüz V2 yürürlüğe alınmadı; önce kontrol validasyonu ve gerçek banka maliyeti gerekir.

## Şubat 2026 — Gerçek "Ayı Çalıştır" özelliği (15 Ekim 2026)

**Bilgisayarda açma:** GitHub Desktop > Fetch origin > Pull origin; çalışan eski siyah sunucu penceresini kapat, `BASLAT.bat` dosyasına çift tıkla. Üstte **Çalışılacak ay: Şubat 2026** seç > **Ayı Çalıştır** düğmesine bas. Komut yazmak gerekmiyor.

Bu düğme `GET /api/months/2026-02/run` yoluyla **1723** tamamlanmış 15m fiyat özellik satırını Git SHA doğrulamasıyla okur; 1–28 Şubat takvimindeki 2688 adet 15 dakikalık slotun her birinde fiyat yoksa BEKLE/TUT olarak taşır. **Ocak 2026 119,75391720039644 dolar NAKİT** durumundan başlatır, Ocak V1 AL/SAT kurallarını *hiç değiştirmez*, Ocak 2026 sonrasındaki haber veya sonuçları ekonomik nedensel açıklama olarak uydurmaz.

Aynı 0,8% / 0,8% maliyetle (banka makası hariç):

| Şubat 2026 sabit koşu | Başlangıç USD | Ay sonu net (varsayımsal satılırsa) | Portföy |
|---|---:|---:|---|
| Fiyat V1 · 15 dk | 119,753917 | **114,274468** | GOLD |
| Olay benzerliği V1 · 15 dk | 119,753917 | **114,274468** | GOLD |
| Fiyat V1 · 3 saat aralık | 119,753917 | **119,895812** | GOLD |

15 dakikalık model **4 AL + 3 SAT** yaptı; son AL 25 Şubat 17:15 Türkiye saati. 3 saatlik senaryo da **aynı Ocak sonu nakitten** başlatılmış yalnız Şubat için karşılaştırmadır; Ocak'taki kendi 118,34 dolar başlangıç serisini sürdürmez. Bu ayrım bilinçli olarak korunur.

Her iki model **Şubat sonunda gerçek SAT yapmadı**: sonuçlar açık GOLD pozisyonunu ayın son kullanılabilir XAU MID kapanışından **varsayımsal çıkış ücreti düşülmüş değerlemedir**. Gerçekte nakitte duran tutar 0, altın birimleri korunur. Son kullanılabilir Şubat M15 fiyatı **27 Şubat 21:30 UTC = 28 Şubat 00:30 Türkiye**; piyasanın kapalı sonraki saatlerinde yeni işlem üretilmedi.

Şubat çalışması V2'yi kanıtlanmış ekonomik yapay zekâya dönüştürmez. Olay katmanının Şubat AL/SAT saatlerine ve getiriye ek katkısı yine sıfırdır. **15 dakikalık modelin Şubat'ta daha sık satış yapıp daha kötü performans göstermesi yeni hata olarak kaydedildi; aynı Şubat verisi üzerinden ayar yapıp daha iyi sonuç iddia edilmez.** Takip eden güncellemeler yalnız daha sonraki aylarda validasyona girmelidir.

- Dondurulmuş Şubat paneli: `data/FEB_2026_V1_ASOF_PANEL.csv`, Git blob `8e3bb94acc3d38d12778439115292388b295734f`.
- Ay yürütücüsü: `monthly_runner.js`.
- Testler: `monthly_runner.test.js`, `npm.cmd test`, `npm.cmd run verify-months`.
- Yalnız izin verilen API: `GET /api/months`, `GET /api/months/2026-02/run`. Üçüncü ay kapalı.

**Not:** Bu uygulama geçmiş veri araştırmasıdır; canlı banka işlemi, otomatik öğrenmeyle strateji değiştirme veya Mart 2026'yı çalıştırma henüz desteklenmiyor.

## 15 Ekim — Çalışan toparlanma algoritması V3 (gölge araştırma)
Sol menüde **Yeni V3 toparlanma modeli** bölümünü aç ve **V3 sonuçlarını hesapla ve karşılaştır** düğmesine bas. Bu bölüm **2020–2025 tarihsel XAU 3 saatlik tamamlanmış durumları** (10.850 kontrol kesiti), **65 olgunlaşmış şok başlangıcını**, 2023→2024→2025 kronolojik karşılaştırmasını ve V3 Ocak–Şubat işlemlerini gösterir.

Şubat 2026 için Ocak V1 sonu **119,753917 USD NAKİT** başlangıcıyla V3 **120,442260 USD** net varsayımsal tasfiye değeri üretmiştir. Eski 15 dakikalık V1 **114,274468 USD** iken hiç işlem yapmadan nakit **119,753917 USD**, ay başı AL/TUT **132,906170 USD**. V3 yalnız bu ayda V1'den daha iyi; nakdi ancak 0,69 dolar aşmıştır. Ayrıca Jan V3 100 dolar başlangıçta **110,981208 USD** ile eski Ocak V1 **119,753917 USD**'nin gerisindedir. 2024 V3 **119,389706 USD** vs buy-hold **124,430292 USD**, 2025 V3 **141,894040 USD** vs buy-hold **161,151041 USD**. **V3 doğrulanmış yatırım üstünlüğü göstermez.**

İşlemler sadece Türkiye saati **09:00, 12:00, 15:00** tamamlanmış üç saatlik kesitlerde araştırma fiyatı üzerinden yapılır. Ekonomik olayın G05-C veya G06-B olması **kanıtlanmamış hipotez**: neden UNRESOLVED. Olay benzerliğinde ileri 96h etiketler yalnız kaynak tarihinde olgunlaşmışsa alınır, geleceğin bilgisi kullanılmaz. %0,8 alış ve %0,8 satış var, gerçek banka alış-satış makası ayrıca mevcut değil. Ocak/Şubat V1 dondurulmuş sonuçları değiştirilmedi.

Teknik dosyalar: `recovery_v3.js`, `recovery_v3.test.js`, `data/RECOVERY_HIST_3H_2020_2022_V1.csv`, `data/RECOVERY_HIST_3H_2023_2025_V1.csv`, `RECOVERY_V3_EXECUTION_REPORT_20261015.md`. Windows ve Linux test: `npm test`, `npm run verify-v3`. Arayüzde çalıştırma, yatırım sinyallerinin canlı onayı değil, retrospektif karşılaştırmadır.
