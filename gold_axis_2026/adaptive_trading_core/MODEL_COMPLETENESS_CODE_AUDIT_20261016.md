# İstenen matematiksel model — Kod temelli TAMLIK DENETİMİ
**Tarih:** 16 Ekim 2026  
**Proje otoritesi:** [GOLD-ADAPTIVE-MODEL-APP-01](../GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md)  
**İncelenen mevcut dal:** `research-gold-core-timeless-selective-learning-20261016`  
**Denetim türü:** statik kod incelemesi + GitHub Actions tarihsel 8/8 sözleşme testi + 3 çalıştırılan adversarial test; fiyat getiri iddiası YOK.  
**Karar:** `MODEL_GATE=FAIL; APP_GATE=NOT_APPLICABLE; TRAINED_CORE_2023_2025=FALSE`.

## Gereksinim → kod kanıtı → durum

| Model sözleşmesi | Kod kanıtı / gerçek durum | Karar |
|---|---|---|
| S0 kaynak/vintage, maliyet, eksik veri | S1 zaman doğruluyor fakat kaynak sertifikasyonu, as-of normalizer, 2023 gerçek ekonomi çoklu seri loader'ı yok; banka spread proxy | KISMEN |
| S1 tarih bağımsız örüntü/kural oluşturma | [S1 JS](adaptive_rule_discovery_s1.js) `newRule`, `updateCenter`, `scored`, `maybeMerge`: artan prototip merkezleri, gözlem sayıları ve destek sonuçları var | KISMEN; yalnız çevrimiçi küme prototipi |
| S1 kuralları çürüterek bölme/zayıflatma/silme/uyarlama | Kod kural bölme, geçersizleşme ve rejim değişiminde yeniden adaptasyon yapmıyor; `maxRules` aşılınca en yakın kümeye zorla atıyor | EKSİK |
| OLAY-02 ve ÖĞREN-03 okunup kurala bağlanıyor mu | S1'de bu dosyaları açan bir loader, DNA→sayılsal ekonomik durum eşlemesi, ORG evresi ve ilk-haber kaynak bağlayıcısı yok | EKSİK |
| Ekonomik neden/haber/yayılım, rakip hipotez ve olaysız kontrol | S1 numerik özellik merkezlerine dayanıyor; ekonomik sebep, ters-vaka, P0–P5 lifecycle ve olaysız kontrolün kanıt sınıflandırması yok | EKSİK |
| S2 başlangıç/devam/yorulma/bitme/yeni giriş | S1 `horizon` getiri/downside betimsel istatistiklerini öğreniyor, faz/survival/hazard/reversal motoru yok | EKSİK |
| S3 net `V_gold - V_cash`, öğrenilmiş uzun pozisyon stratejisi | S1 `observe` her zaman `action:null`, `policyStatus:"NOT_IMPLEMENTED_NO_BUY_SELL"`; nakit/altın state veya risk/ücret policy yok | EKSİK |
| Geçmiş V15/V18/V20, eski V0 | Ayrı kodda linear/fuzzy/MLP ve/veya Double-Q prototipleri var; **S1 tarafından import edilmemiş, S1 ekonomik rule->portfolio policy bağlantısı kurulmuyor**; sentetik veya başka araştırma sonuçları yeni CORE sonucu değildir | AYRI PROTOTİPLER |
| Kalıcı ay ay matematiksel hafıza | S1 `checkpoint/restore` var, ama Jan2023 aylık gerçek S1 checkpoint, 36 ay zinciri ve 2025 dondurulmuş CORE yok | KISMEN |
| Ocak2023 gerçek veri öğrenme/doğrulama | S1 sentetik 8/8 teknik testten geçti. Eski V0 Jan2023 `0 trades / 100 USD` farklı motor, yalnız XAU ve 4 makro girdili | YAPILMADI |
| Uygulamayla CORE bağlantısı | `apps/portfolio_guard_v1/server.js` S1 modülünü yüklemiyor; araştırma dashboard'u ayrı | YAPILMADI |

## Denetlenen test kanıtı

Eski S1 [testleri](adaptive_rule_discovery_s1.test.js) **8/8** [GitHub Actions #38917966345](https://github.com/ataullahturgut/sim3-automation/actions/runs/38917966345) üzerinde PASS; bu başarının konusu **yapay veriyle sözleşme doğruluğudur**. Yeni denetimde S1 modülünü yükleyerek doğrudan üç adversarial vaka çalıştırıldı:

1. **P0: ESKİ ASOF'YA YENİ PARAMETREYLE FORECAST:** Önce T0 2023-01-03 09:00 UTC'de tahmin hazır DEĞİL; 15 adet 4s sentetik olgunlaşma sonrası çekirdeğin `clock` değeri 2023-01-05 21:00 UTC. Aynı çekirdeğe `forecast({asof:T0,...})` sorulunca beklenen log-% `+1.0` ve `ready:true` dönüyor. `forecast` bağımsız API'si artık öğrenilmiş sonraki model durumuyla eski zaman için rapor oluşturabiliyor. **Kronolojik `observe` farklı, eski tahmini geriye dönük üretmek için bu API kullanılmamalı; ya `asof >= checkpoint clock` gardı ya doğru snapshot sorgusu gerekir.**
2. **P1: HEDEF UFUK KAYMASI:** `horizon=240m`, ilk fiyat 1800, 13:00 UTC'ye etiket olgunlaşması gerekirken ilk sonraki kaynak bar **14:15** (+75m) olunca `mature` bu fiyatı `240 dakika` etiketi olarak işliyor. 90 dakikalık izinli gecikme fiili getirinin ufkunu büyütebilir. Kesin horizon/işlem günü kalibrasyonu gerekir. Özellikle hafta sonları `maxLateMinutes` uzun ufuk sonuçlarını yanlış `SKIPPED` işaretleyebilir.
3. **P1: KAYNAK DELİLİ:** Girdiye `source:"FAKE_UNVERIFIED_SOURCE"` verildiğinde S1 kural prototipi oluşturuyor. Kodda kaynak string'i var olması kontrol ediliyor, **vintage/source doğruluğu üst katman tarafından sertifikalanmıyor**. `f.kind` yanlış/boş verilirse haber firstprint zorunluluğu da semantik olarak denetlenemez. Bu kaynak sözleşmesi tek başına gerçek-ekonomik kanıt üretmez.

**Önemli:** Bu üç test `adaptive_rule_discovery_s1.test.js` dosyasına FAIL olarak eklenmedi, çalışma dosyaları değiştirilmedi. Denetimde doğrudan çağrılarla doğrulanan açık tasarım/arayüz sınırları ve kusurlarıdır. Bunları düzeltip regresyon testleri eklemeden as-of ekonomik öğrenmeye bilimsel onay VERİLMEZ.

## Çalışan S1'in gerçek yeteneği

Tam olarak: normalize edilmiş, doğruluğu dışarıda üstlenilen birden fazla sayısal piyasa özelliğinin benzerlik bölgelerini çevrimiçi prototiplere ayırmak; tamamlanmış ufuk sonrası getirileri bu prototiplere atayıp betimsel sonuç profilleri oluşturmak; checkpoint saklamak. **Bu bir adaptif fiyat-davranış kümeleyicisidir**, özünde kendi ekonomik nedensel kural kitaplığını ve net portföy politikası kurmuş bütünleşik yatırım modeli DEĞİLDİR.

## Model tamamlanmadan atlanamayacak tamamlama sırası

1. `S0/P0`: kaynak/vintage/normalize/missing/firstprint ve kapalı M15 bar sözleşmesi; P0 asof forecast guard + P1 gecikmiş etiket ve işlem günü semantiği, kaynak doğruluğu regresyon testleri.
2. `S1`: OLAY/ÖĞREN verisini yalnız kaynaklı ekonomik özelliklere dönüştür; çoklu varlık, karşıt/olaysız olay kontrolü; gerçek Ocak 2023 koşullu örüntü öğrenimi ve genelleme/karşıt vaka; kural bölme/söndürme/belirsizlik.
3. `S2`: hareket evresi, kalan büyüklük ve süre, zorunlu risk ve tersine dönüş öğrenimi.
4. `S3`: aynı ekonomik kuralı ve epizot state'ini kullanarak GOLD/CASH, AL/TUT/SAT/yeniden giriş **net politika** değerlendirmesi, %0.8 her bacak, DD/tail ve kaçırılmış fırsat ödülü; S1'in `action:null` çıktısı bağımsız hisse politika modülüne uydurma başarı olarak çevrilmez.
5. `S4`: Ocak 2023 açık örnek ve karşı-örnekler, full month decision audit, net 100 USD, cash/passive/oracle yalnız ex-post, checkpoint.
6. Ancak `MODEL_GATE=PASS` sonrası Şubat 2023, 36 ay ve uygulama entegrasyonu.

**Değişiklik disiplini:** Mevcut model çizgisinde kal; yeni Git branch/ANN/LSTM varyantı veya uygulama ekranı açarak gerçek S1 ekonomik kural keşfi ve policy eksiklerini perdeleme.
