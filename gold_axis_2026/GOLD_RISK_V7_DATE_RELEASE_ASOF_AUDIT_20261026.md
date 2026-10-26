# ALTIN BÜYÜK DÜŞÜŞ MODELİ — TARİHSEL VERİ ERİŞİM DENETİMİ V7
**Tarih:** 26 Ekim 2026  
**Kapsam:** GitHub'dan indirilen resmî dosyaların doğrudan SHA-256 doğrulaması + 2023–2026 kayıt tarihleri + yayın saatleri + eski BASE14/CFTC tarih mantığının statik kod denetimi. **Model performansını yeniden hesaplayan koşu değildir.**

## Kesin olarak doğrulananlar
- Orijinal SLV, Fed H.15, ABD Hazine 2023–26 gerçek faiz dosyalarının SHA-256 parmak izleri önceki kayda eşit; toplam **958 SLV**, **994 H.15** hafta içi tarih kaydı, **953** reel faiz kaydı. Kayıt tarihleri tekil.
- SLV iki pay-sayısı eksik tarihi: **29 Mart 2024** (Good Friday, normal NYSE işlem günü değil) ve **31 Mart 2024** (Pazar); özellikle Pazar kaydı günlük işlem verisi sayılamaz, beş *işlem* günlük değişim penceresine gün olarak katılmamalı. Eksikler sıfır değil, boş tutulmalı.
- H.15 2 yıl ve 10 yıl serilerinde ayrı ayrı **42 boş/ND**; Hazine 10 yıllık reel par faizde 953 dosya satırında boş değer görülmedi.
- H.15 resmî yayımlanma saati **16.15 New York**. Karar saati bundan önceyse aynı günün faiz değeri yasak; tatil/ND ise son yayımlanmış **geçerli** değer ancak yaş/güncellik kontrolüyle değerlendirilebilir.
- CFTC normalde **Salı pozisyonu / Cuma New York 15.30 yayını**, istisnalar için gerçek takvim gerekir. 2025 hükümet kapanması sonrası CFTC 9147-25 **13 ayrı** günün güncellenmiş gerçek yayın tarihlerini verir.
- CFTC 2026 örneği: **20 Ocak pozisyonu 23 Ocak 15.30 NY**, **27 Ocak pozisyonu 30 Ocak 15.30 NY** yayımlandı. **30 Ocak Türkiye 09.00** kararında yeni 27 Ocak raporu henüz bilinmez; **30 Ocak NY 17.30** kararında bilinir. Tarih-saat kontrolleri bağımsız kodla çalıştırıldı.

## Eski risk algoritmasında bulunan risk
- `gold_forecast_risk_overlay_2023_2026_v1.py` içindeki `next_monday_after_obs` fonksiyonu, H.10 dolar endeksi için **her pazartesi** varsayıyor ve resmî tatili hesaba katmıyor.
- Örneğin 16 Ocak 2026 Cuma gözlem haftası için eski kod **19 Ocak Pazartesi** kullanılabilir varsayabilir; Fed H.10 gerçekte **20 Ocak Salı 16.15 NY** yayımlandı. 2026'nın **16 Şubat, 25 Mayıs, 7 Eylül** pazartesi tatillerinde aynı risk var.
- ABD federal tatil listesi ile 2023–26 arasında **24 olası takvim istisnası** belirlendi. Bu sayı 24 hatalı model sinyali demek değildir; tam giriş paneli ile hangi tahminlerin etkilendiği yeniden çalıştırılmadan bilinemez.
- H.10 resmi yayınında ilave düzeltme/özel takvim istisnaları olabilir. Genel tatil hesaplaması tek başına tam tarihsel ilk yayın belgesi değildir.

## Tamamlanmamış ve karantinada
- GLD/SLV tarihsel arşivin **ilk yayın saatleri ve ilk açıklanan değerleri** kanıtlı değil.
- Hazine reel faizlerin işlem günündeki **15.30 NY ölçüm/alıntı saati**, web yayını ve değer sürümünün o saatte bilinmesi anlamına gelmez. Önceki T+1 09.00 NY kuralı **yalnız araştırma vekili**, kesin yayın belgesi değil.
- Fed H.15/H.10'un **geçmiş dönemde yayımlanan ilk değerleri ve revizyonları** ayrıca incelenmeli.
- CFTC tüm 2023–2026 haftaların gerçek yayın saatlerinin sıralı arşiv kontrolü tamam değil (2025 özel ve seçili 2026 tarihler onaylı).
- Dört metal referans fiyatının gün içi/ilk-baskı kaynak zamanları da tam sertifikalı değil; modeli sırf makro tarihler doğru diye canlı kullanmak hatalı olabilir.
- CME teminat arşivi henüz edinilemedi.
- BASE14 ve CFTC21 eski skorları **tatil/kaynağa-özel tarih kuralları düzeltilip yeniden eşleştirilmeden** kesin onaylı başarı sayılmamalı. 4/4 ve 2/4 önceki **araştırma** sonuçlarıdır; bu V7 koşusunda yeniden üretilmedi.

## Uygulama kararı
**Kırmızı değil, henüz ONAYSIZ:** Kaynak dosyaları doğrulandı; eksikler işaretlendi; tarih/saat kontrolü test edildi. Ancak *tüm* geçmiş veri sürümleri ve yayın zamanları doğrulanmadan yeni veriler ve eski modeller canlıya alınmayacak. Ana BASE14 geçmiş sonuçları silinmedi; ayrı V7 hata listesi oluşturuldu. Neon, canlı model ve otomasyonlara **yazım yapılmadı**.

## Resmî kaynaklar
- Fed H.15: https://www.federalreserve.gov/releases/h15/default.htm
- Fed H.10: https://www.federalreserve.gov/Releases/H10/
- CFTC 2026 takvim: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
- CFTC kapanma sonrası 2025 revizyon: https://www.cftc.gov/PressRoom/PressReleases/9147-25
- ABD Hazinesi reel getiri tanımı: https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics
- GLD yayın pencereleri: https://www.spdrgoldshares.com/usa/gld/