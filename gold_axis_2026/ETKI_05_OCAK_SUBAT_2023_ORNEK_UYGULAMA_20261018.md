# ETKİ-05 — Ocak–Şubat 2023 ekonomik K etiketi gölge örneği

**18 Ekim 2026 · Kaynak gerçek veriler + tarihli mevcut CORE raporu · YENİ ALGORİTMA / GERÇEK SİNYAL / GPT YORUMU / AL-SAT DEĞİLDİR**

Amaç: `Kxx` ekonomik koşul etiketleri o tarihte *ilk haber gerçekten yayımlandığında* görünseydi hangi maddeleri ve karşıt koşulları göstereceğini, özgün S1/S2/S3 modelinin **var olan gün-sonu kararından ayrı** sunmak. **2023–2025 sonradan derlenmiş olay sonuçları 2023-01/02 için geriye bakıştır; kör simülasyon olamaz.** Konsensüs/ilk-baskı tarihçesi onaylı değildir. S1 gün-sonu dört saatlik tahminini yayın-anı tahmini diye gösterme.

## 2023 kronolojik olay şeridi

| Tarih (Türkiye saatinde yayın) | Yayında bilinebilir K maddeleri (tarihsel arşiv vekili) | 2023–2025 benzer kombinasyon | Sonradan XAU 15dk / 4s | Mevcut S3 |
|---|---|---|---|---|
| **6 Ocak 16:30 NFP** | **K03:** istihdam güçlü (+23 bin); **K18:** ücret zayıf (−0,1 puan); **K19:** işsizlik düşük (−0,2 puan); K14: öncesi altın az yükseliyor | **K03 tek başına karışık**: UP 10 / DOWN 13 (23 vaka). Ücretin düşüklüğü tek şahin yorumu kırıyor | **+%0,644 / +%1,391** | KEEP CASH, işlem yok |
| **12 Ocak 16:30 CPI** | **K02:** manşet CPI beklentiden düşük (−0,1 puan); çekirdek CPI **beklentiyle aynı**, K16/17 değil; önceki K03 | K02 + önceki K03: **UP 5 / DOWN 2** (7 vaka); yükseliş adayı, kesin kural değil | **+%0,250 / +%0,451** | KEEP CASH, işlem yok |
| **1 Şubat 22:00 FOMC** | K01–K19'da **FOMC açıklaması/söylem sürprizi için madde yok**; fiyatın önceki 4 saatte düşmesi K15 olabilir | Ekonomik K sonucu **BİLİNMİYOR** | 4s için OLAY-02'nın 85 kayıt dosyasında veri **eksik**; eski ayrı R72 tahmini karara karıştırılmaz | KEEP CASH |
| **2 Şubat** | Bu K sözlüğünde yeni CPI/NFP yayını yok; ECB/BoE/Fed yeniden fiyatlama ekonomik madde olarak henüz kanıtlı değil | Etiket yönü **BİLİNMİYOR**. **S2 gün sonunda CONTINUE/DOWN** | Seans **−%2,222** (15dk ve 4s makro yayınına bağlanamaz) | KEEP CASH |
| **3 Şubat 16:30 NFP** | **K03:** istihdam çok güçlü (+332 bin); **K19:** işsizlik düşük (−0,2 puan); ücret beklentiyle aynı; **önceki K02:** 12 Ocak CPI düşük. K14 açıklama öncesi hafif UP | K03 + önceki K02: **DOWN 9 / UP 1** (10 vaka), bunların 4'ü dört saatte ≤−%1. **Geriye bakınca düşüş eğilimli hipotez** | **−%1,349 / −%2,611** | KEEP CASH, işlem yok |
| **14 Şubat 16:30 CPI** | **K05:** manşet CPI beklentiyle aynı; çekirdek CPI de beklentiyle aynı; önceki K03 istihdam güçlü; K15 altın öncesi düşüyor | K05 + önceki K03: **DOWN 6 / UP 2** (8 vaka), ancak güçlü büyüklük bilgisi yok | **+%0,063 / −%0,693** (ilk yön tersine dönüyor) | KEEP CASH, işlem yok |

**Yukarıdaki UP/DOWN adayları 2023–2025'ta sonuçları bilinen kütüphaneden EX-POST eşleşmelerdir, 2023 tarihinde verilmiş gerçek fiyat tahmini değildir.** Örneklem sonuçları ilgili tarihin kendisini içerir. 2023-01 ilk günlerde benzer koşul veri geçmişi olmadan karar verirken sonradan 2024–2025'te görülmüş dağılımın otomatik bilindiğini iddia etme.

## Hangi tür ekonomik yorum model ekranına eklenir?

- **6 Ocak**: `NFP_STRONG` ama `WAGE_SOFT` → **iki rakip Fed kanalı**. "Güçlü istihdam" otomatik altın SAT değildir. **İlk 15dk sonrası** gözlenen kuvvetli XAU pozitif tepki ayrıca eklenirse koşullu pozitif aktarım adayı; bunun için eşzamanlı USD/faiz teyidi hâlâ gereklidir.
- **12 Ocak**: `CPI_SOFT`, çekirdek `NEUTRAL` → manşet gevşeme hipotezi; fakat tek sürpriz yüksek kârlı işlem değil.
- **2 Şubat**: ekonomik etiket boşluğunda **S2 fiyat düşüş evresini** görebilir. Bu, ekonomik nedenin doğru sınıflandığı veya 3 Şubat NFP'nin önceden bilindiği anlamına gelmez.
- **3 Şubat**: `NFP_STRONG`+ `UNEMP_LOW` + geçmiş `CPI_SOFT` → şahin ücret dışı bileşenler ve karşıt durum. Gerçek USD/faiz/pozisyon teyidi yoksa **ekonomik baskı adayı**; ilk 15dk negatif veri ancak 16:45'ten sonra as-of özellik olabilir. Sonraki 4s kaybı açıklama anında bilinemez.
- **14 Şubat**: her iki CPI sürprizi `NEUTRAL`; haber başlığından kesin fiyat yönü çıkmaz. **İlk 15dk hafif UP, sonra DOWN** → tepki süre/terslenme ayrı öğrenilmelidir.

## CORE'la ayrım ve bilim kapısı

- Gölge CORE çalışması **Ocak ve Şubat'ın her gününde S3=KEEP**, `tradeAllowed=false`, **gerçek GPT = 0**, **AL/SAT = 0**, banka CASH portföyü $100 sonlandırılmış. Etiketleri veri dosyasına eklemek bu modeli yeniden eğitmek veya ona ekonomik işlem çıkartmak değildir.
- S1/S2 alanları mevcut arşivde **gün sonu snapshot** olarak tutuluyor, olay saati anlık S1/S2 kararları değil. 2 Şubat S2 gün-sonu DOWN; 3 Şubat gün-sonu NEUTRAL. "S1 pUp ~%52,9" ve aynı gün düşen altın, farklı ufukları olduğu için çelişki gibi yorumlanamaz.
- 2023–2025 tüm fiyat sonuçlarını kullanarak 2023 tarihli "AL 6 Ocak, SAT 2 Şubat" kuralını doğruymuş gibi kurmak **lookahead** olur. 2 Şubat'ta bu K sözlüğünde yeni makro veri bulunmadığı için alış/satış anını etiket tek başına bilemez.
- Eksikler: ilk yayımlanmış konsensüs ve haber erişim zaman damgaları, veri saati USD/DXY, ABD reel ve nominal faiz, gümüş, haberin koşullu etki ömrü, beklenen kalan hareketin %1,6194 civarı roundtrip asgari maliyet üstünlüğü, gerçek banka BID/ASK.
- `ETKI05_OUTCOME` ayrı etikettir; açıklamadan sonraki 15dk/4s yüzdesi açıklama öncesi/şu an verilmiş makro karar şartı olamaz. **AL/SAT/EKONOMİK_KÂR_BAŞARISI=NOT_PROVEN**.

**Makine okunur bu çalışma:** [ETKI_05_JAN_FEB_2023_K_ETIKET_GOLGE_ORNEGI_20261018.json](ETKI_05_JAN_FEB_2023_K_ETIKET_GOLGE_ORNEGI_20261018.json).

**Kaynaklar:** [2023 Ocak–Şubat geçmiş CORE ve GPT olmayan gölge](apps/portfolio_guard_v1/data/JAN_FEB_2023_AI_SHADOW_CHRONOLOGICAL_20261017.json), [makro duyuru gözlem](OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv), [K etiketi eşleştirmeleri](ETKI_05_KOSUL_ETIKETLERI_V1_20261018.json), Neon R72 2023 makro sürprizleri ve EVTradingLabs 15dk pre-release XAU.
