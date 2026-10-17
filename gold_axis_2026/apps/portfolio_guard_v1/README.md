# GOLD Portfolio Guard V1 — sabit tarihsel koşu uygulaması

> **PROJE AYRIMI — 16 EKİM 2026:** Bu klasör mevcut **UYGULAMA (U)** araştırma arayüzünün tarihsel kodudur; içinde eski model deneylerinin bulunması yeni matematiksel CORE'un uygulamada geliştirileceği anlamına GELMEZ. **Tek aktif model+uygulama proje sözleşmesi:** [GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md](../../GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md). Uygulama yalnız onaylı MODEL çekirdeğini sürüm/checkpoint kimliğiyle çağırır; ekonomik kuralları ve AL/SAT matematiğini kendi başına seçmez. Bu README'deki eski V1/V2/V3 raporları tarihsel referanstır, yeni MODEL'in kabulü değildir.\n\n
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


## V4 — Adaptif TUT algoritması (15 Ekim 2026)

Programda sol menüden **V4 adaptif strateji** > **V4 algoritmasını çalıştır ve karşılaştır**. Eski Ocak/Şubat V1 ve V3 sonuçları aynı kalır.

V4 geçmiş dönem oynaklık yüzdeliklerinden (2020–2025) eşik öğrenir; RECOVERY_CANDIDATE durumunda kademeli giriş, UP_TREND'de kalan nakdi altına geçirme, riskte iki farklı onayla satış, aşırı şokta erken risk azaltma mekanizmasına sahiptir. Ekonomik G05-C ve G06-B DNA hipotezlerini nedensel olarak doğrulamaz, tüm ekonomik mekanizma adayları UNRESOLVED. Türkiye 09:00,12:00,15:00 işlem saatlerini kullanır.

- Şubat 2026: 119,753917 USD nakit devrinden **V4 122,867909 USD** (GOLD, varsayımsal SAT ücreti düşülmüş); V1 114,274468 USD; V3 120,442260 USD; CASH 119,753917 USD. V4 **4 Şubat 09:00 AL** ve **19 Şubat 12:00 AL**, satış yok.
- Ocak V4 100 dolardan **109,534460 USD**, Ocak V1 **119,753917 USD**: V4 Ocak'ta kötü. 2024 V4 **125,518805** vs V3 119,389706 / altın al-tut 124,430292. 2025 V4 **141,125260 USD** vs altın al-tut **161,151041 USD**: önemli fırsat kaybı.
- 2023 fiyat kapsamı eksik. Şubat 2026 strateji geliştirmeden önce bilinmiş olduğundan kör ileri test değildir. Gerçek banka alış/satış makası ve slip fiyatı yok, komisyon her yönde %0,8.

Uygulama kaynağı: recovery_v4.js; test recovery_v4.test.js; analiz RECOVERY_V4_SCIENTIFIC_EXECUTION_REPORT_20261015.md. npm test ve npm run verify-v4 çalışır; GET /api/algorithm/v4 salt okunur ve gerçek banka emri vermez.


## 15 Ekim 2026 — Şubat–Eylül kesintisiz bilimsel yürüyüş ve V5 reddi

Normal kullanıcı: GitHub Desktop'ta **Fetch origin → Pull origin**, eski siyah sunucu penceresini kapat, `BASLAT.bat` ile aç. Sol menüde **Uzun dönem bilimsel test** bölümüne gir, **8 aylık V4 / V5 bilimsel testini çalıştır** düğmesini kullan.

Bu ekran mevcut Ocak–Şubat V1, V2, V3, V4 modellerini değiştirmez. V4 ve V5 çalışmaları ve bunların başarısızlıkları yalnız ayrı, salt okunur araştırma panosunda gösterilir. Şubat V1 kapanış nakdi 119,753917 USD ile başlayan kesintisiz 2026 Şubat–Eylül değerlendirmesi, Türkiye'deki her ay sonunda:

| Gösterge | V4 | V5 | Alternatifler |
|---|---:|---:|---|
| Eylül sonu USD | **96,706968** | **107,832861** | NAKİT 119,753917; Şubat TR09 AL/TUT 107,741250 |
| Maksimum gerileme | %26,68 | %17,28 | NAKİT 0 varsayımı |

V5, yükselişi kaçırma ve aşırı koruyucu satış sorununu çözmedi: 2024'te V4 125,52 vs V5 111,23; 2025'te V4 141,13 vs V5 135,04 (her yıl ayrı 100 USD). V5'te her iki yılda daha çok alım/satım oluştu. Kodun bilimsel kabul kapısı `REJECT_PROMOTION`, otomatik model değişimi YOK.

Teknik: `v4_forward_review.js`, `recovery_v5.js`, `scientific_promotion_gate.js`, veri `data/RECOVERY_HOLDOUT_2026_MAR_SEP_3H_ASOF_V1.csv` (Git blob SHA 860917258c84a86a210d8c7f44655d46d878470e). Tam ayrıntılar `SCIENTIFIC_V4_V5_CONTINUOUS_REVIEW_20261015.md`; V4 ve V5 hipotez kayıtları da aynı klasörde. Yalnız veri kaynağı bitişinde 2026 Sep30 21UTC satırı Türkiye 1 Ekim olduğu için Eylül sonu hesaplanmaz.

Bu deneyler geçmiş dönemler görülerek geliştirildiğinden **kör ileri validasyon değildir**. Gerçek banka alış/satış makası, slippage, doğrulanmış ilk haber ve ekonomik G05-C/G06-B nedenselliği yoktur. V5 bir önerilen canlı işlem algoritması değildir.


## V6 — Ekonomik olay/diğer piyasa kanıtlarının araştırma sonucu

**Kullanım:** GitHub Desktop'tan Fetch origin / Pull origin, önceki siyah Node konsolunu kapat ve `BASLAT.bat` aç. Sol menü **V6 piyasa aktarım denetimi**, **V6 ekonomik aktarım testini çalıştır**. Bu menü yalnız bilgi ve karşılaştırma sunar; mevcut V1/V3/V4/V5 modelini otomatik değiştirmez, banka emri vermez.

2023–2026 için gerçek NQ, ZN ve CL saatlik kapanmış vadeli verilerinin son 1h ve 6h fiyat değişimleriyle altın 09:00 Türkiye karar noktasını eşleştirip 24 saat içinde XAU'nun en az %2 düşüp düşmediğini test ettik. 506 tam-veri gün elde edildi (2024:148, 2025:155, 2026:114; 2023:89). XAU fiyat modeline ek piyasa verisi 2024 Brier hatasını **0,033162→0,031546** düşürdü ama 2025 **0,047953→0,050139**, 2026 **0,112185→0,112769** yükseltti (kötü). 2024–25 negatif olay sayıları sadece 5 ve 8; güçlü genelleme iddiası yok.

Ekonomik OLAY-02: 96 vaka, 84 farklı kontrol noktası; kaynakta **ilk haber UTC doğrulaması 0/96, nedensellik kanıtı 0/96, as-of işlem onayı 0/96**. 1 Şubat 2023 06:15 UTC SWING_V1_002'ye, o gün 19:00 UTC yayımlanan Fed kararını açıklayıcı sebep olarak atamak **tarih sırasını ihlal eder**; kod bunu engelliyor.

**Karar: V6 bilimsel üstünlük ve ekonomik nedensel öğrenme eşiğini GEÇMEDİ.** V6 ekonomik olayları kullanarak otomatik alım/satım işlemine yükseltilmedi. Araştırma sonucu: `V6_CROSS_MARKET_EVIDENCE_FINAL_AUDIT_20261015.md`. Kod `macro_v6.js`, `event_evidence_gate_v6.js`, testler aynı adlarda `.test.js`. `npm run verify-macro-v6` ve `npm run audit-event-evidence-v6`, ayrıca `npm test`. API `GET /api/algorithm/v6`. Tam banka ask/bid ve slippage ile bağımsız ileri test olmadan geçmiş fiyat kârları gerçek al-sat avantajı olarak sunulmaz.


## V6 – Ekonomik as-of AL/SAT araştırması ve nihai sınama

GitHub Desktop'ta **Fetch origin → Pull origin** yap, eski sunucuyu kapatıp `BASLAT.bat` ile aç. Sol menüde **V6 ekonomik AL/SAT deneyi** bölümünde **Ekonomik V6 AL/SAT testini çalıştır** düğmesine bas. Bu ekran V6 fiyat/ekonomik gözlem tutarlılığı, Şubat–Eylül kesintisiz portföy devri ve eski yıl testlerini ayrı görüntüler. Ayrıca **V6 piyasa aktarım denetimi** bölümünde risk tahmin Brier testleri yer alır.

2023–2026 CME NQ/ZN/SI fiyat serisi, yalnız tamamlanmış H1 kesitlerinden türetilmiş 7.682 3h gözlem. 96 OLAY-02 vakasının hiçbiri kanıtlanmış ilk haber yayımlanma ve ekonomik neden taşımıyor; V6 bunları doğrudan işlem sinyali saymıyor. Olaylar ve fiyat verisi dondurulmuş SHA kaynaklarıyla okunuyor.

2024 bağımsız 100 USD başlangıcı: V6=111,227607 USD, V5=111,227607 USD. 2025: V6=135,040312 USD, V5=135,040312 USD. 2026 Şubat başı 119,753917 USD nakit ile kesintisiz Eylül: V6 **107,740399 USD**, V5 **107,832861 USD**, hep nakitte **119,753917 USD**.

**Yatırım algoritması olarak KABUL EDİLMEDİ**. Ekonomik değişkenlerin uzun dönemde gerçek ek karar getirisi yok; 2026 sonuçları geliştirme öncesi görülmüştü (kör doğrulama değil). Gerçek banka alış-satış kotasyonu/spreadi bulunmuyor. Yalnız alış %0,8 ve satış %0,8 komisyon proxy olarak kullanıldı.

Kaynak: `macro_v6_portfolio.js`, `macro_v6_portfolio.test.js`, `V6_CROSS_ASSET_EVIDENCE_PROTOCOL_20261015.md`, `V6_ECONOMIC_MACRO_PORTFOLIO_FINAL_AUDIT_20261015.md`, `data/CME_3H_ASOF_2023_2024_V6.csv`, `data/CME_3H_ASOF_2025_2026_V6.csv`. Komut isteyen denetçiler için: `npm test`, `npm run verify-macro-v6-portfolio`; sunucuda salt okunur `GET /api/algorithm/v6/portfolio`.


## 17 Ekim 2026 — 2023 ekonomik kural + S1 / S2 / S3 günlük inceleme ekranı

**Uygulamada kullanma:** Bu özellik `research-gold-core-timeless-selective-learning-20261016` GitHub dalında geliştirildi. Yerel bilgisayarda bu dalın son sürümünü çekip uygulamayı yeniden açın (Windows'ta `BASLAT.bat` veya `npm start`). Tarayıcıda `http://127.0.0.1:8787` adresinde sol menüden **2023 · Ekonomik kural / S1 / S2** bölümünü açın. Üstteki **2026 Ayı Çalıştır** kutusu farklı, eski deneyindir; bu araştırma ekranında onu kullanmayın. Menü küçük ekranda kaydırılabilir; bölüm sayfanın başına da eklendi.

**Eklenenler:** Ocak / Şubat 2023 ay seçimi, tüm gün / kural adayı / işlem seansı filtresi, gün gün araştırma aday ORG etiketi, S1 +4 saatlik UP olasılığı ve beklenen log hareket, S2 hızlı evre/yön/trend z, Şubat uzun S2 evresi, mevcut CORE S3 KEEP CASH araştırma kararı, aynı gün gerçekleşmiş altın seans hareketi, tıklanan günün ayrıntıları, 6/12 Ocak ve 3/14 Şubat için **ilk ekonomik araştırma gözlemi**. Önceki ayın öğrenmesi korunarak yapılan iki **başarılı matematiksel CORE** koşusunun raporları aynen kullanılır.

**Kaynak ve yöntem:** `../../adaptive_trading_core/JAN_2023_INTEGRATED_S1_S2_S3_REAL_DAILY_RESULTS_20261017.md` ve `FEB_2023_INTEGRATED_S1_S2_S3_REAL_DAILY_RESULTS_20261017.md`. Uygulama `model_2023_daily_view.js` üzerinden yalnız bu iki raporu okur ve doğrular; yeni fiyat, işlem, ORG kuralı veya simüle performans üretmez. Salt okunur API `GET /api/model/2023/daily?month=2023-01` veya `2023-02`. Desteklenmeyen aylar 400, eksik/bozuk kaynak 503 döner. Ham lisanslı 15 dakika fiyatlar uygulamaya veya GitHub'a kopyalanmadı.

**Güvenilirlik sınırı:** ORG etiketleri araştırmacı hipotezidir, doğrulanmış ekonomiden öğrenilmiş sinyal değildir. S1 UP gün sonu +4 saat, gerçek fiyat aynı gün seans ilk-son olduğundan isabet karşılaştırması yapılamaz. Olaydan sonra araştırma koşullu S1 henüz UNREADY; ekonomik ilk yayın erişimi PIT doğrulanmadı. S2 uzun bitiş olasılıkları güvenilir hazır değil. S3 KEEP, **canlı AL/SAT veya gerçek banka hesap sonucu değildir**. Eski 2026 V1/V2/V3 ve diğer deneyler değiştirilmedi.

**Teknik kontrol:** `node --test model_2023_daily_view.test.js`; ayrıca [2023 uygulama uçtan-uca GitHub CI](https://github.com/ataullahturgut/sim3-automation/actions/workflows/gold-2023-core-daily-app-tests.yml) kaynak ve ekran bağlantılarını, localhost GET yanıtlarını ve eski V1 regresyonunu denetler.
