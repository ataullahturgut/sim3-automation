# GOLD MONTHLY — Ücretsiz dört metal API gerçek erişim testi (23.10.2026)

## Kullanıcı hedefi
- 2010'dan başlayarak **4 metal** (XAU/XAG/XPT/XPD), **günlük** USD/oz, tek homojen kaynak.
- Geçmişi bir defa yüklemek ve bundan sonra **ücretsiz sürekli günlük** güncellemek.
- Altın tahmin girdilerini **LBMA fixing / farklı spot veya vadeli** veri gibi yanlış etiketlememek.

## Gerçek uzak API testi
- GitHub Actions **39943413253**: https://github.com/ataullahturgut/sim3-automation/actions/runs/39943413253 — SUCCESS.
- Test kodu: `tools/gold_monthly_free_api_coverage_probe_v1.py`.
- **Gold API** `https://api.gold-api.com/price/{XAU,XAG,XPT,XPD}`: 4/4 HTTP 200 ve geçerli pozitif USD canlı spot verisi; API anahtarı gerekmedi. Bu **ücretsiz günlük/tetiklemeli geleceğe dönük örneklem** olabilir; **resmî sabit LBMA benchmark**, kapanış veya tarihsel 2010 kapsamı değildir. Gold API sağlayıcı arasında otomatik failover yaptığını açıklıyor.
- **Gold API tarihsel veri**: kamuya açık tarihsel uç nokta **ücretsiz hesap API anahtarı gerektiriyor**. Kullanıcının Gold API tarihsel API anahtarı mevcut/erişilebilir olarak doğrulanmadığı için 2010/2015/2020/2026 XAU/XAG/XPT/XPD tarihsel geri yükleme **TEST EDİLMEDİ**. Gold API ücretsiz planı için resmî fiyat sayfası **saatte 10 tarih sorgusu** yazıyor: https://gold-api.com/pricing
- **Standard Bullion**, resmî ücretsiz veri belgesi: 4 metal, keyless tarihsel endpoint ve günlük seri başlangıcı **2011**: https://standardbullion.com/market-data ve https://standardbullion.com/gold-price-api
- **Standard Bullion gerçek 16 tarih aralığı isteği**, 2010-06-14..18, 2015-06-15..19, 2020-06-15..19 ve 2026-10-12..16 × 4 metal: **16/16 HTTP 200**, her birinde `grain=daily`, `points=49` ama **0/16 istenen aralıktaki gerçek günlük nokta**. Sağlayıcı `range` alanında istenen tarihleri geri yansıtırken `points` içindeki ilk/son tarih **2026-10-19..2026-10-23**. Bu nedenle **tarih aralığı parametrelerine fiilen uymuyor**; `200 OK` sağlam veri kanıtı değildir. Özellikle **2010 geçmiş veri kullanımı reddedildi**.
- **2010..2026 tek kaynak tamamlandı mı?** **HAYIR.** `can_certify_2010_to_2026_one_provider=false`. Güvenli tek kaynak araştırma görünümü 2010–2026 Ocak için hâlâ geçerlidir; Şubat–Eylül 2026 tek-kaynak fiyatları **tamamlanmadı**.
- **Mevcut eski anahtarlar:** Kodda `TWELVE_DATA_API_KEY` (Twelve Data XAU kullanım), `FRED_API_KEY`/ALFRED makro serileri; Gold API kamuya açık spot keyless. Twelve Data'nın XPT/USD ve XPD/USD seri kontratları açıkça `PAID_GROW_REQUIRED` diye işaretli. MetalPriceAPI kaydı StakTrakr arşivindeki provider *etiketi*, bu Neon aylık dört metal research serisinde **MetalPriceAPI kişisel anahtarımızın mevcut olduğunun kanıtı değil**.
- **Ücretsiz başka adaylar:** MetalpriceAPI resmî ücretsiz planı 100 istek/ay ve günlük güncelleme yazıyor: https://metalpriceapi.com/pricing ; ancak tam 2010–2026 dört metal günlük geçmişi ve eldeki etkin anahtar **doğrulanmadı**. MetalCharts 200 istek/ay ücretsiz başlangıç iddiası mevcut, ama 2010–2026 tarihsel limit ve data lisansı test edilmedi.
- **Gereken sonraki kontrol:** Varsa Gold API veya MetalpriceAPI geçmiş veri anahtarı için **güvenli GitHub Actions Secrets** yoluyla yetkili canlı sorgu: 4 metal × 2010/2015/2020/2026 tarihleri, gerçek data tarihi ve tarihler arası süreklilik, 4-metal USD/troy_oz ve kaynak sözleşmesi; sağlayıcı ücretsiz kotasıyla 2010–2026 backfill yapılabiliyorsa otomatik Neon branch/staging ingest kodu kurulmalı.
- **Güvenlik:** Testlerde fiyatlar, erişim anahtarları, özel Neon URL'leri loglanmadı; Neon'da hiçbir gözlem, fiyat, karar veya model kaydı değiştirilmedi.
- **Prensip:** Güncel Gold API spot verisini tarihsel StakTrakr/LBMA olarak etiketlemek veya 2010 eksiğini başka fiyat türü ile örtmek yasaktır.
