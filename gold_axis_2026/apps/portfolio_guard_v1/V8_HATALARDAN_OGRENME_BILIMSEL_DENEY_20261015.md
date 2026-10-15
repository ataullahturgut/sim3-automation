# V8 — Hatalardan öğrenme geliştirme deneyinin bilimsel sonucu
**Tarih:** 15 Ekim 2026
**Durum:** REJECT_PROMOTION / NO_LIVE_TRADING / EXPERIMENTAL / ALREADY_SEEN_2026

## 1. Kullanıcı hedefi

Altın ile nakit arasında as-of ekonomik ve piyasa kanıtlarından yararlanarak gidip gelmek, her AL için %0,8 ve her SAT için %0,8 kesinti sonrasında getiriyi büyütmek, geçmiş karar hatalarından öğrenmek.

Önceki 2026 Şubat–Eylül hindsight optimum fiyat-yolu çalışması:
- Her ay en çok bir tamamlanmış AL/SAT turuyla teorik **189,74 USD**.
- Her ay en çok iki tamamlanmış turla teorik **211,26 USD**.
- Bunlar bir ayın bütün fiyatlarını önceden bildiği için **ulaşılabilir ve elde edilmesi beklenen hedefler değildir.** Başarı bir gölge algoritmanın bunlara ne kadar yaklaştığıyla değil, gerçek zamanda bilinebilir bilgilerle nakde ve altını taşımaya göre elde ettiği net fazladan getirinin sağlamlığıyla ölçülür.

## 2. Kod olarak hangi geliştirme yapıldı?

Dosya: \`v8_regret_engine.js\`, rapor adaptörü: \`v8_regret_audit.js\`, as-of regresyon ve güvenlik: \`v8_regret_engine.test.js\`.

- Ocak 2023–Aralık 2024 tarihsel altın göstergeleri, CME NQ geçmişi ve Ocak 2025–Eylül 2026 üç saatlik kesitler kullanıldı. 2025 örtüşen 1.892 kesitin altın fiyatı aynı olduğu doğrulandı.
- Fiyat dinamiği: 4 saatlik, yaklaşık 92 saatlik ve 276 saatlik XAU değişimleri; gerçekleşen oynaklık, downside variance share, intrabar verimlilik, bar kapanış konumu, tepe düşüş; erişilebilir dönemde CME Nasdaq ve ZN futures dönüşleri.
- Hedef: 96 saatlik zarar/koruma ve 336 saatlik (14 günlük) beklenen fırsat getirisi. Eğitim ankrajı Türkiye saati 09:00. Bir tahminin **gerçek sonucu 96/336 saat dolmadan** ağırlıklar güncellenmez.
- Fiyat ve çapraz piyasa için çevrimiçi, sınırlı ağırlıklı regresyon. Tahminin başlangıç rejimi (UP/DOWN/SHOCK/RANGE) için ayrı olgunlaşmış gözlem ortalamaları.
- Gecikmeli hata defteri: \`MISSED_UP\`, \`MISSED_DOWN\`, \`AVOIDED_DOWN\`, \`HOLD_WIN\`; ayrıca \`badBuy\`, \`recentSell followed by profitable rebound\` durumlarından koşullu hata belleği.
- Hata belleği yalnız olgunlaşmış etiketlerden gelen giriş/satış sapmasını küçük adımlarla güncelliyor. Son fiyatı *aynı günün model girdi verisi* olarak kullanmak veya ayın ideal zirve/dibini zamandan önce öğrenmek yasak.
- Banka için yalnız fiyat vekili ve %0,8 alış / %0,8 satış giderleri dahil. Gerçek banka BID/ASK, emrin uygulanma süresi, ilave spread/slippage bilinmiyor.
- Çelişkili AL kararı güvenlik freni: doğrulanmış NQ/altın stres SAT sinyali veya yavaş trend kırılma SAT sinyali varken aynı kesitte yeni AL **yasak**.
- Eski V1–V7 sürümleri ve OLAY-02/ÖĞREN-03 manifestleri değiştirilmedi.

## 3. Gerçek sonuçlar

2024 ve 2025 bağımsız 100 $ başlangıç; 2026 Şubat–Eylül ayrı bir 119,753917 $ nakit devri.

| Dönem | V8 / online adaptif | Karşılaştırma | Değerlendirme |
|---|---:|---:|---|
| 2024 | 117,9761 USD | Pasif altın 123,8497 USD | Pasif altının gerisinde |
| 2025 | 145,6746 USD | Pasif altın 160,4153 USD | Pasif altının gerisinde |
| Şubat–Eylül 2026 | **117,3323 USD** | Nakit 119,7539 USD; V7 123,5295 USD | **Başarısız** |

Şubat–Eylül 2026 aynı V8 kapıları:
- Adaptif çevrimiçi öğrenme + hata belleği: **117,3323 USD**.
- \`no_regret\`: yalnız fırsat-hatası tabanlı dinamik karar ayarlaması kapalı: **117,3323 USD** (aynı işlemler).
- 2026 başlangıcında bütün çevrimiçi model güncellemeleri dondurulmuş: **103,6427 USD**.
- XAU/NQ stres ve yavaş trend koruyucu satışları kapalı: **102,2103 USD**.
- Sabit eski V7 aynı panelde: **123,5295 USD**.

**Önemli nedensel sınır:** V8'in bütün öğrenmesini dondurmanın zararı, "özel hata-regret politikası kâr kazandırdı" anlamına gelmez. Çünkü yalnızca regret politikasını dondurunca 2026 işlemleri ve sonuçları **değişmedi**. Bu, gerçek başarı elde edemediğimiz açık bir olumsuz ablation testidir.

### 2026 V8 işlemleri (Türkiye saati)

- 3 Şubat 09:00 AL.
- 3 Mart 12:00 SAT (XAU/NQ ortak stres).
- 6 Mart 12:00 AL.
- 19 Mart 12:00 SAT (yavaş düşüş teyidi).
- 19 Mart sonrası nakit; Ağustos yükselişine geri giriş yapamadı.

V8 2026 Şubat sonunda 126,6603 USD iken Mart sonunda 117,3323 USD'ye geriledi. 2026'nın kapanmış 96 saatlik 168 ankrajında 87, 14 günlük 162 ankrajında 65 doğru yön; gözlemler örtüşebilir. **66 MISSED_UP** ve **34 MISSED_DOWN** kayıtları, 2026 başlangıç tarihli fakat birbirine zaman bakımından örtüşen olgunlaşmış örneklerdir. Bunların kâr/zarar yüzdeleri toplanarak para hesabı yapılmaz.

## 4. 2026 üzerinden ayrıca denenen yeni denemeler ve neden reddedildi?

- İlk V8'deki birbirini bozan sat/al davranışı ve bankanın %1,6 üzerindeki işlem maliyeti yüzünden \`risk_veto\` adında tutarlılık kapısı eklendi. Bu, Şubat–Eylül 2026 net teorik sonucu yaklaşık **112,3362→117,3323 USD** düzeltti; hâlâ V7'nin altında.
- Hızlı trend tekrar girişini güçlü bir r1/r3 hareketiyle zorlayan iki keşif varyantı 2026'da yaklaşık **92,88** ve **98,97 USD**'ye geriledi. Bu parametreler 2026 gözlemlerine bakıldıktan sonra sınandı, bu nedenle geleceği bilmeden geliştirilen kanıt veya güvenilir alternatif sayılmaz.
- 2026 çalışmasına devam etmek için bu varyantları geriye dönük fit etmek uygun değildir.

## 5. Hata teşhisi

1. **Missed UP / Ağustos 2026:** Mart'ta satıp nakitte kalmak risk yönetimini korusa da, yeni pozitif ekonomik rejimin farkına varabilecek bir mekanizma henüz oluşmadı. 336 saatlik tahmin belirsizliği bu kez gereksiz pasifliğe yol açtı.
2. **Missed DOWN / Mart:** Şubat sonundaki açık GOLD pozisyonunda, düşüş başlamadan önce riskin yükselmesini yakalayabilecek bağımsız ekonomik veri vardı mı sorusu hâlâ doğrulanmadı. SAT kararını Mart başında vermesi NQ/altın teyidinden geldi; ekonominin nedensel kaynağını tanıdığımız anlamına gelmez.
3. **Bad REENTRY:** 6 Mart yeniden AL sonrasında 19 Mart SAT etmesi, kısa fiyat sıçramasını yeni trend sanma sorununu gösteriyor. Benzerlik güvencesi henüz olay tarihli ve kaynaklı değil.
4. **Unverified macro:** 96 OLAY-02 vakasının gerçek habere ilk erişim/ilk yayın zamanı ve nedensellik kanıtı halen sıfır. OLAY-02 DNA sınıf isimleri, fiyat hareketini açıklayan ekonomik kanıta dönüşmeden modele katılamaz.
5. **Regret gate useless in 2026:** Hata defterine kaydedilen fırsat kayıpları, aktif kararlara yetecek seviyede ayırt edici bilgi sağlamadı; \`no_regret\` aynı 4 emri verdi.

## 6. Bilimsel sonraki işlem

- Bilgi taşıyan makro vakaların firstprint, sürpriz vintageleri, karşıt haberleri, günün NQ/ZN/DXY/reel getiri koşullarını tarih-saat düzeyinde eşleştirmek.
- Her aylık 'en iyi 1 tur' karşı-olgusal fiyat yolu defterinden yalnız *eğitim etiketleri* ve karar öncesi ulaşılabilir özelliklerle \`recovery/reversal\` olasılıklarını sınıflandırmak.
- Aynı tarih döneminde tekrar tekrar eşik değiştirip kazanan model seçmek yerine, yıl/olay bazında **bloklu walk-forward**, model kaydı ve daha sonra tamamen yeni dönemde fiyat ve işlem doğrulaması.
- Nakit, pasif altın, V4/V5/V7 ve olay katmanı ayrıştırılmış V8'i aynı veri, aynı banka fiyatı/kadans ve komisyonlarla test etmeden otomatik terfi **YOK**.
- Ürün mimarisi: gölge araştırma API'si \`GET /api/algorithm/v8/regret\`, sol menüde \`V8 hata öğrenmesi denetimi\`. Eski V7 kullanımdan kaldırılmaz. Canlı işlem de yok.

Bu çalışma bir **gerçek kod ve yürütülmüş negatif deney** kaydıdır; başarılı yeni getiri stratejisi bulunmuş değildir.
