# GOLD-ADAPTIVE-MODEL-APP-01 — 2023 tam yıl S3 başarısızlık performans denetimi (16 Ekim 2026)

**WORKSTREAM=MODEL | PURPOSE=USER_REQUESTED_ANNUAL_DIAGNOSTIC | RUN MODE=DISCOVERY_FULL_ARCHIVE | S5=NOT_AUTHORIZED_AS_SCIENTIFIC_PASS | MARKET_SOURCE=RECONSTRUCTED_NOT_PIT | M4_GATE=FAIL | U1=UNCHANGED.**

## Deney sözleşmesi
- Gerçek read-only Neon `gold_research_evduka_xau15m_bidask_candidate`, `2023-01-01 <= bar_start_utc < 2024-01-01`, **23.544** sıralı M15 XAU BID/ASK MID araştırma fiyatı, **tek sürekli kaynak**, vendor karıştırma yok.
- Mevcut tek CORE kodu `adaptive_market_core_s1_s2.js` sıfırdan oluşturuldu, **2023 Ocak → 2023 Aralık** boyunca **bir defa kronolojik**, model S1/S2/S3 state sıfırlanmadan yürüdü. Başlangıç **100 USD CASH**; iki konfigürasyonla bağımsız aynı fiyat replay: `LEGACY_M15` ve `MULTI_SESSION_RESEARCH`. 2024–2025 gelecek fiyat sonuçları 2023 kararına yüklenmedi; **ekonomik macro feature girişi yok**, tüm S1 çıktıları price-feature-only. Bu araştırma **resmî S4/S5 bilimsel kabulü değildir** ve gerçek firstprint PIT banka yürüyüşü değildir.
- Her tamamlanan fiyat barı `priceAvailableAt=asof`; S2 slow tamamlanmış quote-only seans olayları yalnız 22:00 UTC veya sonrasında modele katıldı. Son 2023 Aralık 29 slow seansı **tam 22:00 UTC'de**, veri serisinin son barı kapandıktan sonra hazır hale gelir; karar replay'inde **bir sonraki fiyat barı yoktur**, bu yüzden 2023 karar CORE'u **248 kabul edilmiş + 8 reddedilmiş = 256 processed** slow seans bildirir. Tamamlanmış S2 yıl sonu arşivini ayrı değerlendirdiğimizde **257 aday / 249 kabul edilmiş / 8 reddedilmiş / 6 tamamlanmış epizot**; en son 29 Aralık slow kapanışı son M15 kararından sonra olgunlaşmıştır. Bu fark işlem performansını değiştirmez.
- İşlem izni gölge çalışma dışında daima `action:null`, `tradeAllowed:false`. Tek ücret `0.008` BUY + `0.008` SELL; `Europe/Istanbul 09:00–17:00` bandı shadow trade ve pasif GOLD kıyasında kullanıldı. 2023 bütün yıl Türkiye UTC+03. Bunlar **reconstructed BID/ASK MID fiyatları**; gerçek banka kotasyonu/execution/slippage değildir.
- 2023 altın al/tut kıyası: ilk izinli gözlenen tamamlanmış M15 kapanışı **03 Ocak 2023 09:00 TRT**, MID **1840,52 USD/oz**; yıl sonu **29 Aralık 2023 17:00 TRT**, MID **2059,265 USD/oz**. `100 × (1−0.008)^2 × 2059.265 / 1840.52 = 110.10195776 USD`; yıllık **+%10,10195776**. Pasif cash 100 USD. Alternatif tüm-quote Jan2→Dec29 kapanış bazında pasif GOLD yaklaşık **111,1046 USD** çıkar; bu bank-time karşılaştırmasının yerine geçirilemez.

## Gerçek kronolojik CORE 2023 sonucu
| Karar sürümü | Başlangıç | Son net shadow CASH/GOLD USD | Yıl net % | BUY | SELL | Pozisyon |
|---|---:|---:|---:|---:|---:|---|
| LEGACY_M15 | 100,00 | **100,00** | **0,00** | 0 | 0 | CASH |
| MULTI_SESSION_RESEARCH | 100,00 | **100,00** | **0,00** | 0 | 0 | CASH |
| Pasif nakit | 100,00 | **100,00** | **0,00** | — | — | CASH |
| Pasif altın (TR banka penceresi, iki ücret) | 100,00 | **110,10** | **+10,10** | 1 | 1 varsayımsal tasfiye | GOLD |

**2023'te potansiyel fırsat farkı:** Aynı banka araştırma fiyatlarında model vs baştan sona altın tutmak = **10,10195776 USD / 100 USD başlangıç**. Bu fark yalnız al/tut referansıyla geriye dönük farktır; fiyatın önceki ayki düşüşlerini zamanında satabilen üstün strateji kanıtı değildir.

- LEGACY_M15: **23.544 bar, 23.286 olgun tek-M15 Q güncellemesi, 257 bar gap, 18.216 değerlendirilen KEEP, 5.328 abstain, 0 BUY**.
- MULTI_SESSION_RESEARCH: **23.544 bar, 7.858 araştırma oturum değeri değerlendirmesi, 5.503 uygun KEEP, 0 BUY**, BANK_WINDOW_CLOSED 15.066, MATURED_SESSION_SUPPORT_INSUFFICIENT 2.355, ACTION_VALUE_SUPPORT_INSUFFICIENT 608. Bazı durum açıklamaları birbirini dışlamayan karar-aşaması sayıları olabilir; karar `audit.proposed/abstained` ayrı toplamdır.
- S1 aynı CORE'da **1.438 anchor, 1.384 mature 4h label, 4 öğrenilmiş prototip**, ama 2023 bu replay'de makro/OLAY-ÖĞREN feature **0** ve S1 yön başarısının kârlılığa katkı test edilmedi. S2 fast **463** tamamlanmış mikro hareket; slow **6** tamamlanmış uzun epizot (yıl sonunda ayrı S2 son gününü sayarak), karar modelinde **248** geçerli slow seans gözlemi. S3 multi-horizon memory yıllık karar replay'inde **812** olgun etiket, **170** sansür; kapanış sonrası 29 Aralık slow'u yalnız arşiv denetimine işlendiğinde **814** olgun etiket olur.

## Ay sonu, aynı 100 USD yıl başlangıcından itibaren kümülatif tasfiye değeri
Pasif altın sütununda **Ocak başındaki tek AL** ve ilgili ay sonunda **bir varsayımsal SAT** için %0,8+%0,8 ücret düşülmüştür. Her ay yeniden altın alıp satıldığı anlamına gelmez. Model her ay CASH'de kaldı.

| 2023 | M15 bar | Legacy model $ | Multi-session model $ | Yıl başından GOLD al/tut $ |
|---|---:|---:|---:|---:|
| Ocak | 1,920 | 100,00 | 100,00 | 102,64 |
| Şubat | 1,830 | 100,00 | 100,00 | 96,99 |
| Mart | 2,112 | 100,00 | 100,00 | 105,85 |
| Nisan | 1,756 | 100,00 | 100,00 | 106,22 |
| Mayıs | 2,106 | 100,00 | 100,00 | 105,32 |
| Haziran | 2,006 | 100,00 | 100,00 | 102,22 |
| Temmuz | 1,930 | 100,00 | 100,00 | 105,41 |
| Ağustos | 2,116 | 100,00 | 100,00 | 103,93 |
| Eylül | 1,911 | 100,00 | 100,00 | 100,02 |
| Ekim | 2,032 | 100,00 | 100,00 | 107,07 |
| Kasım | 1,989 | 100,00 | 100,00 | 108,91 |
| Aralık | 1,836 | 100,00 | 100,00 | 110,10 |
    
## Neden hiç almadı ve bilimsellik sınırı
- Mevcut M15 TD `Q(CASH,SWITCH)` değerlemesi 15dk artışa %0,8 BUY maliyetini yüklemekte; günlerce/haftalarca GOLD TUT'un toplam gelecekteki net politika avantajını yeterince öğrenmemektedir. Yıl boyunca **18.216** kıyas KEEP çıkması bu yöndeki mühendislik başarısızlığının kanıtıdır.
- Beş gün sonu **zorunlu GOLD→CASH** etiketinin çoğu durumda negatif çıkması, Ocak–Aralık uzun yükselişte GOLD tutmanın kârını temsil etmez. `MULTI_SESSION_RESEARCH` modu ayrıca geçmiş seanslardan muhafazakâr düşük sınır uygular, alfa/economic conditional üstünlük kanıtı yoktur.
- Kullanıcının istediği ekonomik davranış M2, S2 uzun epizot ve M4 öz-finansmanlı **politikaya bağlı uzun tutma değerinin** birlikte öğrenilmesi tamamlanmadı; gerçek 2023 ilk erişimli makro olay sinyali bu 2023 model yürüyüşünde bağlanmadı. S4/FIRSTPRINT ve bağımsız banka icra testleri PENDING/FAIL. 2023 tam yıl araştırma teşhisi, manifest 2023 Ocak bilim kapısını veya 2023 Şubat→Aralık eğitim devir kabulünü aşmış sayılmaz.

**Reproduction lineages:** Aynı branch GitHub kodu `adaptive_market_core_s1_s2.js` / `adaptive_position_value_s3.js` / `adaptive_position_memory_s3.js` / `S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql`; read-only Neon 2023 M15 12 aylık sıralı blokta JS CORE'a uygulandı, özel ham veri depoya commitlenmedi. GitHub Actions sözleşme testleri ayrı koşar; bu özel fiyat replay'ini kendiliğinden CI'de çalıştırmaz.


---

## 16 Ekim 2026 kullanıcı düzeltmesi sonrasında saat-kısıtsız yeniden üretim

**BU BÖLÜM AYNI RAPORDAKİ ESKİ 09:00–17:00 İŞLEM PENCERESİ İDDİASININ YERİNE GEÇER.** Kullanıcı altın/nakit algoritmasında banka işlem saati şartı olmadığını teyit etti; S3 `BANK_WINDOW_CLOSED_RESEARCH` kod engeli ve shadowTrade saat kontrolü kaldırıldı (commit `55f20d641cc33a43151a6cdfdcebf221833f85cf`, her iki GitHub Actions sözleşme testi PASS). Alım ve satış için ayrı ayrı %0,8 maliyet korunur, bankada fiyat/işlem imkânı kanıtlanmış değildir.

Kodu değiştirdikten sonra yeni tek-süreklilik replay aynı read-only Neon **2023 Ocak–Aralık 23.544** M15 BID/ASK araştırma kaydı üzerinde gerçekten TEKRAR çalıştırıldı: 12 ay boyunca tek S1/S2/S3 state devam ettirildi; model baştan 100 USD CASH.

| Yeni saat bağımsız yıllık araştırma kıyası | Bakiye 2023 sonu | Altın AL | Altın SAT |
|---|---:|---:|---:|
| S3 LEGACY_M15 | **100,000000 USD** | **0** | **0** |
| S3 MULTI_SESSION_RESEARCH | **100,000000 USD** | **0** | **0** |
| Tüm gözlenen fiyatlardan pasif GOLD | **111,104608 USD** | 1 varsayımsal giriş | 1 varsayımsal tasfiye |
| Nakit | **100,000000 USD** | — | — |

- İlk tamamlanmış M15 kapanışı `2023-01-02T23:15:00Z` MID **1827,13**; son `2023-12-29T22:00:00Z` MID **2062,90**. `100×0.992²×2062.9/1827.13=111.1046080793`. **Önceden belirtilen 110,101958 USD benchmark eski TR 09–17 penceresine bağlıdır, artık güncel deney benchmarkı değildir.** İki deneyin başlangıç/bitiş saatleri aynı olmadığından rakamlar karıştırılmaz.
- LEGACY_M15: 18216 durum için `LEARNED_KEEP_GREATER_OR_EQUAL`; 0 alım. MULTI_SESSION_RESEARCH: 18216 araştırma kıyası; 5571 `MATURED_SESSION_SUPPORT_INSUFFICIENT` + 12645 `MATURED_5_SESSION_NOT_CONVINCING`; 0 alım. `BANK_WINDOW_CLOSED_RESEARCH` artık sıfır/yok. 2023 oturum hafızasında 812 olgun etiket, 170 sansür. Kapanmış son günün henüz sonraki M15 kararına aktarılamaması kronolojik olarak korunuyor.
- **Sonuç:** Eski `0 işlem / 100 USD` negatif araştırma bulgusu bağımsız saat-kısıtsız replay ile teyit edildi; değişen kıyas **pasif GOLD 111,10 USD**. Bu, modelin sinyali neden vermediği konusunda daha güçlü başarısızlık kanıtıdır ama ekonomik M2 firstprint, uzun HOLD değeri ve bilimsel AL/SAT policy hâlâ eksik. **MODEL_GATE=FAIL, FIRSTPRINT_PIT=false, USER_BANK_EXECUTION=false, U1=UNCHANGED.**
