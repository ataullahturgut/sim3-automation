# REHBER — 2023 başından tek portföy, neden öğrenmeye rağmen geç alıyor?

**16 Ekim 2026 — araştırma kaydı, hiçbir banka emri verilmedi.**

## Veri ve test sözleşmesi

- İlk veri ve karar: 3 Ocak 2023, Türkiye 09.00; son kontrol: 30 Eylül 2026, Türkiye 15.00.
- 6.724 kronolojik üç saatlik veri ve 947 tamamlanan 14 günlük etiket. Bu etiketlerin tamamı istatistiksel açıdan bağımsız değildir.
- İlk 14 günlük vaka sonucu 17 Ocak 2023'te tamamlandı. Altı ayrı 14 günlük bloktan örnek oluşunca ilk model-hazır tahmin: 17 Mart 2023, Türkiye 09.00.
- 100 USD NAKİT ile tek portföy başladı. Yıl başında sıfırlama ve yeni para ekleme yok. Sinyal Türkiye 09.00, işlem sonraki 12.00 kesitinde; alış ve satışta %0,8'er maliyet.

## Kesintisiz REHBER gerçek replay sonucu

| Tarih | Bakiye (USD) | İşlem adedi |
|---|---:|---:|
| 2023 Aralık sonu | 100,000000 | 0 |
| 2024 Aralık sonu | 100,000000 | 0 |
| 2025 Aralık sonu | 100,000000 | 0 |
| 2026 Eylül sonu | **100,076881** | 6 (3 AL / 3 SAT) |

İlk AL 30 Ocak 2026 Türkiye 12.00, ilk SAT 2 Şubat 2026 Türkiye 12.00: bu turda büyük düşüş gerçekleşti. Şubat 2026'da 119,753917 USD nakitle başlayan eski ve farklı deney 135,663808 USD'ye ulaşıyordu; 30 Ocak pozisyonunu içermez. Bu nedenle 2026 Şubat başlangıçlı rakamı, 2023'ten kesintisiz hesap olarak sunmak yanlıştır.

Karşı kontrol: 3 Ocak 2023'te uygun sonraki bankanın fiyat vekilinden 100 USD ile ALTIN AL ve 30 Eylül 2026'da SAT senaryosu, %0,8 alış ve %0,8 satış bedeliyle **224,272004 USD**. Bu da gerçek banka BID/ASK fiyatı değil, geçmiş MID vekili varsayımıdır.

## Neden 2024 ve 2025'te altın almadı?

- **2024:** 258 model-hazır karar gününün hiçbirinde REHBER'in beklenen komisyon-sonrası 14 günlük getiri tahmini giriş marjını geçmedi. Hatta her 258 gün için net beklenen 14 günlük getiri sıfırın altında kaldı.
- **2025:** 255 model-hazır karar gününün hiçbirinde geçmiş benzeyen örneklerden türetilen kâr olasılığı gerekli **%58'i** geçmedi. Yalnızca 13 gün pozitif net getiri bekliyordu ama yeterli güven vermiyordu.
- Diğer AL şartları: kötü %20 getiri kuantili -%6'nın üzerinde olmalı ve XAU/NQ stres teyidi bulunmamalı.

Bu durum bir veri-başlangıç yetersizliği değil; 14 günlük AL-SAT fırsatını öğrenen hafızanın yıllarca süren yükseliş rejimini tanımaması, benzer geçmiş durumları yanlış değerlendirmesi veya aşırı temkinli davranması sorunudur.

## REHBER'in mevcut çalışma çevrimi

1. 09.00'da 14 as-of piyasa metriği okunur.
2. Trend, stres ve piyasa yapısı mercekleriyle daha önce tamamlanmış benzer epizotlar bulunur. Her 14 günlük bloktan en fazla bir komşu ve mercek başına en çok 32 komşu değerlendirilir.
3. Komisyon sonrası 4 ve 14 günlük beklenen getiri, kâr olasılığı, kötü yüzde 20 sonuç ve belirsizlik çıkarılır.
4. AL / SAT / BEKLE kararı kurallardan üretilir. Sinyal aynı anda doldurulmaz; sonraki banka kontrol noktasında komisyonlu fiyat vekiliyle işleme dönüşür.
5. 14 günlük sonuç tamamlanınca örnek hafızaya eklenir; uzmanların geçmiş tahmin hataları ve karar marjı güncellenir.

**Öğrenme var, kanıtlanan başarılı politika öğrenmesi yok:** 2026'daki hafıza güncellemelerini durdurmak 135,663808 USD'lik ayrı 2026 deneyini 130,591594 USD'ye düşürdü. Ancak karar marjı ve uzman güven ağırlıklarını dondurmak aynı 2026 işlemlerini değiştirmedi. Tam dönem kesintisiz portföyde performans ise yalnız 100,076881 USD.

## Bilimsel karar ve sonraki değişken

REHBER'in şimdi öğrenmesi gereken şey yalnız 14 günlük AL-SAT fırsatı değil; **rejim sürekliliği, yükselişe ilk katılım, elde tutma süresi, riskin yayılımı, trendin bozulması ve olayı yanlış sınıflandırma maliyeti**. Bunu yeni vadeler ve haberlerin doğrulanmış ilk erişim saatleriyle ölçmek gerekir. Başarıyı aynı incelenmiş 2023–2026 verilerine uydurarak ilan etmek yasak. Gerçek banka BID/ASK ve ileri tarihli bağımsız dönem bulunmuyor.

Denetim modülü: v12_earliest_origin_audit.js. Testler: v12_earliest_origin_audit.test.js. Salt okunur API: GET /api/algorithm/v12/earliest. V12 arayüzünde 2023 başından kesintisiz yürüyüş düğmesi eklendi. Eski modeller değiştirilmedi; otomatik işlem ve terfi yok.
