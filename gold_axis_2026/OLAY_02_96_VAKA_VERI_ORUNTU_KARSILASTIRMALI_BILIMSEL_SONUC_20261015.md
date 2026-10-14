# OLAY-02 — 96 Vaka / 84 Karar Noktası / 38 Derin Örgü: Ortak Veri Örüntüsü Bilimsel Denetim Sonucu

**15 Ekim 2026 · Bilimsel keşif araştırması; Ocak 2026 koşusu veya emir defteri DEĞİL.**
Bu rapor OLAY-02 ve ÖĞREN-03'ten gelecekteki as-of karar destek sistemine **ortak ölçülebilir özellik sözleşmesi** devridir. ANA-01/OLAY-02/ÖĞREN-03 üç ana manifest ve tarihli 2023–2025 kaynaklar değiştirilmedi.

**Üretilmiş, makine-okunur delil:**
1. [Evrensel metrik sözlüğü: 33 ortak metrik, 9 bileşik aday indeks, ORG01–ORG12 hipotez matrisi](OLAY_02_EVRENSEL_VERI_ORUNTU_METRIK_SOZLUGU_20261015.md).
2. [84 tekil kontrol için Neon'dan yeniden hesaplanan kapalı M15/H1 metrikleri](OLAY_02_84_ASOF_FIYAT_CAPRAZ_METRIKLER_20261015.csv).
3. [96 olay kaydının 84 kontrol ve 42 tarihsel çapraz varlık imzasıyla tek matrisi](OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv).
4. [38 derin belgelenmiş vakanın 12 tarih bağımsız olay örgüsü ve doğru kimlik eşleştirme köprüsü](OLAY_02_38_DERIN_VAKA_12_ORGU_METRIK_KOPRUSU_20261015.csv).

## 1. Mevcut kanıt kapasitesi — var ve eksik
| Mevcut kaynak | Kayıt / başarı | Bilimsel durum |
|---|---:|---|
| V1 uzun net fiyat bacağı | 42 | Ex-post etiket, predecision değil |
| V2 maksimum mutlak çok-ufuk hareketi | 54 | V1 ile aynı metric değil, ex-post |
| **Tekil karar zaman damgası** | **84** | 12 tekrar aynı observation, 96 bağımsız değil |
| **En az 1 saat kesintisiz önceki XAU 15m** | **82/84** | As-of teknik geçmiş var; 2026'da backfill edilmiş |
| **4 saat kesintisiz XAU 15m** | **81/84** | r4h, RV4h, downshare, efficiency, close position, drawdown hesaplandı |
| Nasdaq 100 H1 önceki 1 saat fiyat değişimi | 83/84 | NQ.c.0, H1 kapanmış; XAU penceresiyle 15m tam eş hizalanmamış |
| 10Y tahvil futures **FİYAT** H1 değişimi | 73/84 | ZN.c.0, faiz (%) değildir |
| Gümüş SI.c.0 iki ardışık H1 fiyat değişimi | **12/84** | Seyrek ve roll/hacim uygunluğu teyitsiz; işlem onayı değildir |
| 38 derin tarihli vaka | 38 | 18 direkt düzeltilmiş V1 kimlikli, 20 eski V2 düzeltmeyle ID eşleştirmesi açık |
| İlk olay yayım saati + nedensellik doğrulaması | **0/96** | Haber/metin etiketi yetmez |
| P0–P5 bütün evre as-of nedenselliği | **0/96** | Bütün P0 alanları UNKNOWN |
| Maliyetli, bankadan yürütülebilir doğrulanmış politika | **0/96** | %0,8 + %0,8 ve banka spread farkı kapısı |

**Neon ham veri denetimi:** 2023=20.600 M15 kaynak satırı (20.436 tam); 2024=23.713 (23.657 tam); 2025=23.606 (23.560 tam). Toplam **67.919 kaynak fiyat barı, 67.653 tam**. As-of karar noktasında seçilen son tamamlanmış barlar ve ardışık 16 getiri üzerinden hesaplama yapıldı. Kaynakların indirilme vintage'ı tarihsel 2023 akış anına ait değildir, dolayısıyla **HISTORICAL_ASOF_INPUT_SIMULATION**; prospective veya BLIND OOS değil.

## 2. İlk gerçek veri örüntüsü sınaması — bütün vakalar ayrı tutuldu

**Önemli ayırt edici olgu:** 42 V1 uzun fiyat hareketinin **41'inde** ilk kontrol öncesi 4 saatlik fiyat yönü ölçülebiliyor. Bunların yalnız **17'sinde** önceki 4 saatlik fiyat işaretiyle *sonradan oluşmuş uzun V1 yön etiketi* aynı; **24'ünde farklı**. Bu sayı, 24 kesin tersine dönüşün nedensel olarak doğrulandığı veya yarınki yönü ters tahmin etmenin kârlı olduğu **anlamına gelmez**. Uzun-vade V1 uçları önceden seçilmiş ex-post episode sınırlarıdır. **Bulgumuz:** yalnız son 4 saatlik momentum, ekonomik olayın gelecekteki uzun yönünü güvenilir şekilde temsil etmiyor; evre, çapraz piyasa, olay karakteri şart.

**Ayırıcı örnekler (hepsi as-of kontrol anındaki PAST 4h ve eski ex-post uzun-vade sonuçları ayrı):**

| Vaka | Önceden gözlenen r4h | RV4h | Downside semivaryans payı | 4s yol verimi | NQ H1 önceki kapanmış getiri | Sonradan tarihli V1 uzun yön | Yorum |
|---|---:|---:|---:|---:|---:|---|---|
| SWING_V1_001, 2023 ilk bacağı | +%0,694 | %0,493 | 0,083 | 0,563 | +%0,259 | UP | Altın ile beyaz metallerin geniş retrospektif ayrışması, G01/G04 rakiplerini gerektirir |
| SWING_V1_028, Nisan 2025 tarife/panik | **−%0,501** | %0,305 | **0,778** | 0,494 | **−%0,166** | DOWN | Altın+NQ negatif; güvenli liman veya likidite satımı olasılığını ayırmak için G05 kanıtı şart |
| SWING_V1_029, Nisan toparlanma adayı | +%0,785 | **%1,522** | 0,255 | **0,170** | +%0,158 | UP | Pozitif fiyat sıçraması ama oldukça çalkantılı düşük yol verimi |
| SWING_V1_038, Ekim 2025 metal dönüşü | **+%0,147** | %0,408 | 0,365 | **0,112** | +%0,005 | DOWN | Kontrol anında yükseliş varken sonradan DOWN; label'ı t'de tahmin girdisi yapma |
| SWING_V1_042, Aralık 2025 teminat riski adayı | +%0,140 | %0,377 | 0,412 | 0,122 | −%0,010 | DOWN | ORG10/12 rekabeti; canlı marjin/OI/vintage bilgisi eksik |

**Matematik:** r4h basit yüzde `100×(P_t/P_{t−4h}−1)`; `RV4h=100×sqrt(Σ[ln(P_i/P_{i−1})]^2)`, eksiksiz 16×15m getiri; `downside_share=Σ[ln return<0](log_return²)/Σ(log_return²)`; `EFF4h=|ln(P_t/P_{t−4h})| / Σ |ln return|`. Dolayısıyla fiyat +0,78% iken RV=1,52% olabilir; değişkenler aynı şey değil.

**Zaman uyarısı:** NQ H1 verisi kontrol anına kadar kapanmış son tam saatlik bar olduğundan H1 değişimi XAU son dört saatiyle eşzamanlı *aynı aralık getirisi* değildir. İlk karşılaştırma yalnız `available_at<=t` garantili zaman-sayısı uygunluğudur; kesin eşsaatli çapraz tetik/korelasyon kanıtı değildir.

## 3. Tüm 12 ekonomik örgü için müşterek ortak ölçüm soruları

ÖĞREN-03'teki **ORG01–ORG12** (12 adet) ortak indeks sözlüğü ile karşılaştırılır; örgü/kodlar sabit:
- **Faiz ve dolar:** ORG01 (fırsat maliyeti gevşemesi), ORG02 (faiz/dolar baskısı) ve ORG11 (rezerv vs makro). Ayrıştırıcı: macro surprise/vintage, 2Y/10Y/TIPS, DXY ve XAU sıralı reaksyon. Bunlar olmadan basit XAU/NQ işareti G01 nedeni **doğrulamaz**.
- **Stres/jeopolitik:** ORG03 (banka stresinde güvenli liman/easing), ORG04 (jeopolitik tırmanma), ORG05 (rahatlama). Ayırıcı: ilk haber, kredi/finansman, NQ, petrol, metaller ve ALTIN.
- **Ticaret:** ORG06 (tarife belirsizliği, korunma), ORG07 (tarife rahatlaması), ORG08 (tarife şokunda ilkin co-sell sonra korunma). Ayrıştırıcı: haber sıralaması, P04 down semivaryans, XAU/NQ/metal eş yön ve fonlama/marjin.
- **Fon akışı/pozisyon:** ORG09 (rezerv+ETF fiyat birikimi), ORG10 (doygunluk/pozisyon dönüşü), ORG12 (marjin/likidite boşaltma). Ayırıcı: OI/hacim/ETF/CFTC vintage, fiyat patikası ve volatilite hızlanması; RSI ya da r15 tek başına neden değil.

**38 derin tarihli vaka için** aynı matris gerçekten üretildi. ORG01:6, ORG02:9, ORG03:3, ORG04:1, ORG05:1, ORG06:7, ORG07:1, ORG08:2, ORG09:3, ORG10:3, ORG11:1, ORG12:1. **18** derin eski V1 doğrudan güncel V1 fiyat kaydına bağlanabilir (bunların **17'sinde** tam as-of 4h var); eski V2 kökenli **20** derin kayıt güncel C_CORR'ye otomatik bağlanmadı. Bu 20 vakanın karakter açıklaması OLAY-02'de durur ama metrik altına yanlış ID iliştirilmez. Bu nedenle 38 anlatı ile 96 sayısal kaydın tamamı arasında nedensel etiket doğruluğu iddia edilmiyor.

## 4. Haber-anomali kanıtı: 'sıradan volatilite mi açıklama tepkisi mi?' metrik olarak

NFP/CPI/FOMC eski 85 duyurusu, özgün makro-vintage notu ve eşsaat dört önceki haftayla karşılaştırmalı:
- **NFP 35 olay:** İlk M15 mutlak hareket medyanı **%0,3344**; dört haftalık as-of eşsaat kontrolü satır medyanı **%0,1290**; **26/35** durumda ilk tepki kontrol ortalamasından büyük; +240 dakika ölçülebilir 34 olaydan 10'unda ilk M15 işareti tersine döndü.
- **CPI 34 olay:** İlk M15 mutlak hareket medyanı **%0,2927**, placebo medyanı **%0,1533**; **28/34** normalin üzerinde; +240 dakika karşılaştırmada 9/34 işaret dönmesi.
- **FOMC 16 olay:** İlk M15 mutlak hareket medyanı **%0,1895**, placebo medyanı **%0,0661**; **12/16** anormal; fakat **16/16 için 240 dakika sonucu yok**, bunu 0 dönüş diye yorumlamak yasak.

**Toplam: 66/85 ilk M15 anormal büyüklük.** Bu 66 değer, doğru al/sat yönü veya ekonomik olayın ilk nedeni değil, **oynaklığın tahmin edilebilir haber saatleriyle ilişkisini** gösteren gözlemsel testtir. Bu sebeple `ABNORMAL_REACTION15`, `FOLLOW_THROUGH_SIGN`, `REACTION_DECAY` ve `NEWS_SURPRISE_Z` ayrı indisler gerektirir.

Literatürle uyumlu savunulan yaklaşım: gün içi sezonsallığın düzeltilmesi (Cai, Cheung & Wong 2001); makro sürprizlerin hem yönü hem volatilite ve metal ayrışmasına etkisi (Elder, Miao & Ramchander 2012); açıklama öncesi beklenti dağılımı (Smales & Yang 2015); finansal futures sıçramalarının yalnız bir kısmının duyuru zamanıyla çakışması (Evans 2011). Kaynak URL ve formül bibliyografisi metrik sözlüğünde.

## 5. Neden bugünden doğrudan 0–100 skor/otomatik işlem kurulmuyor?

- **Yüksek kapsama, düşük mekanizma kimliği:** 81/84 XAU fiyat örüntüsü ölçülebilir, ancak ilk haber nedenselliği hâlâ 0/96. Fiyat tek başına haberin kimliğini göstermiyor.
- **Asimetrik veri:** NQ 83/84, ZN futures fiyatı 73/84; kesintisiz SI.c.0 iki H1 getirisi yalnız **12/84**. Gümüşü zorunlu kapı yapmak veriye aykırı; gümüş kanalını `UNAVAILABLE` olarak koruyup bağımsız spot SI.n.0 veya XAG aramak gerek.
- **Eski ex-post seçilim:** 96 vaka gelecekte bilinen fiyat uçları ile seçilmiş. Bu vakalar üzerinde metrikleri seçip aynı vakalarda isabet ölçmek sahte verim üretir. Negatif kontrollü olaysız günler ve erken bilinen haber saatiyle random/clock-matched karşıtlar gerekir.
- **Cross-asset kaynağı:** 42 V1 retrospektif günlük pencere imzası, 84 as-of H1 sinyaliyle veya ilk haber dakikasıyla aynı şey değildir.
- **Yürütme:** Banka bid/ask fiyatı, kur ve %0,8+%0,8 olmadan uygun eylem yok. Dondurulmuş model train/validation 2023–2024 ve 2025 zamansal OOS kıyas ile verim göstermedikçe `ACTION_ELIGIBLE=NO`.

## 6. Araştırmanın karar mimarisi

**HER 15 dakikada aynı tip paket**: 33 ölçüm, bunlardan hesaplanabilir olanlar; 9 bileşik *aday indeks* ve her indeksin eksik bileşeni; 12 ORG hipotezinden en çok 2–3 rakip; en az 1 açık yanlışlama; canlı veya tarihsel yayın zamanı; XAU+NQ+gerçek USD/faiz/metal durumları; önceki bilgiye göre değişen delil; GOLD ve CASH için iki ayrı maliyetli karar senaryosu.

**Kritik kabul standardı:** Haber geldi diye G02; altın düştü diye G06; NQ düştü diye zorunlu satış; 4h r4h pozitif diye AL **yasak**. Yalnız yeterli ekonomik ilk haber, bağımsız aktarıcı, yanlışlayıcılar ve ilerideki kalan-maliyet dağılımı birleştiğinde gerçek al/sat tartışılır. Veri eksikse 'ADAY' veya 'UNKNOWN' olarak belgelenir; araştırma durur değil, eksik kanalı araştırma görevi açılır.

## 7. Doğrulanan bulgu ve yeni araştırma kapısı

**Gerçek katkı:** Eski 96 olayın her biri artık en azından kendi düzeltmeli vaka kimliğiyle **ortak ölçülebilir as-of XAU/NQ/ZN ve var ise SI çekirdeğine** ve D0/D1/D2 kanıt seviyesine bağlandı; 38 tarihli derin vaka örgüsü yanlış V2 eşlemesi yapılmadan ayrıldı. Tüm 12 örgüye uygun tek gösterge sözlüğü oluşturuldu.

**Henüz yapılmadı:** 33 metrik ve 9 indeksin tüm geçmiş günlerde ve 96 vakada doldurulması; 20d same-hour robust z-score, USD/yield/metallerin gerçek as-of vintage çekilmesi, haber-öncesi/orijinal firstprint ve likidite/pozisyon kanıtı; 2025 maliyetli bağımsız işlem performansı. Bunların henüz hiçbiri 'başarı kanıtı' olarak gösterilmez.

**Sınır:** Bu araştırma **20 Ocak 2026 başlatılan koşunun yenilenmesi değildir**. Kullanıcının sildirdiği Ocak 2026 koşu dosyalarına dokunulmadı; sonraki karar tartışmasına aktarılacak tek şey metodolojik özellik sözlüğü ve 2023–2025 vaka geçmişidir.
