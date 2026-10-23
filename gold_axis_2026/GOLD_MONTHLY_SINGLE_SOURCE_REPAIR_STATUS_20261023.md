# GOLD MONTHLY — Dört metal için tek kaynak politikasına geçiş (23.10.2026)

## Kapsam / yapılan gerçek değişiklik
- `tools/vw_midas_msvr_successor_v1.py` veri yükleyicisi artık tarihsel **dört metalin** (Au/Ag/Pt/Pd) birbirleriyle hizalanmış, hafta içi tarihli ve **tek dondurulmuş kaynak soyuna** ait günlük kayıtlarını kabul eder.
- Geçici araştırma kaynağı: DB içindeki `lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01` arşivi, **yalnızca** `metadata.payload_provider_label=LBMA` ve `metadata.payload_source_label=seed`. Bu etiketler **resmi, lisanslı orijinal LBMA firstprint kanıtı değildir**; StakTrakr bir farklı kaynakları kullanan toplayıcıdır.
- 2010-01..2026-01: **193** kaynak-etiketi tutarlı araştırma ayı; modelin dört metal girdilerinde ortak iş günleri kullanılır.
- 2026-02..2026-07: **6 karışık/belirsiz sağlayıcılı ay**, bütün ay karantinaya alınır; farklı sağlayıcıları aralarında harmanlayan seri modeli besleyemez.
- 2026-08..2026-09: dört metalin güncel araştırma serisinde **2 eksik ay**, otomatik interpolasyon veya başka sağlayıcıdan sessiz ekleme yapılmaz.
- Tarihsel model `core_gold` fiyat hedefi artık ayrı `CORE5_GOLD_USD_OZ_RESEARCH_R1` değerinden **üretilmez**: dört metal ile aynı kaynak/gün takviminden hesaplanan aylık altın ortalaması kullanılır. Dolayısıyla **önceki tahmin performansı sonuçları bu yeni fiyat tanımı için geçerli değildir**; model yeniden eğitilip test edilmelidir.
- Kaynak-göreli denetimler modelin DB üzerinden `load_data()` işlevine bağlandı; tek-saf kaynak araştırma aşaması, as-of ve lisanslı canlı fiyat onayı değildir.
- Eski gözlem satırları, üretim sonuçları, model parametreleri ve Neon kayıtları **silinmedi, değiştirilmedi**. Yalnızca **araştırma dalındaki model giriş/etiket seçimi** değiştirildi; PR henüz merge edilmedi.
- CI: `.github/workflows/gold-monthly-source-governance-v1.yml` testleri, 2010–2024 frozen data kanıtını ve modelin karışık-ay / kaynak soyunu reddetmesini kontrol eder; online Neon üretim yeniden değerlendirmesi değildir.

## Gerçek veri tamamlama için gereken aynı-kaynak kanıtı
Tek kaynak 2010–2026/10 tarih aralığının **tüm dört metali** için aynı fiyat tanımı, para birimi (`USD/troy oz`), günlük saat kapanışı, belge/abonelik, API kimlik doğrulaması ve fiyat dizisi sağlanmalıdır. Yeni veri dosyası/sağlayıcıya karar verilmeden mevcut arşivde geriye dönük fiyatların **yanlış olduğu** varsayılıp sayı değiştirilmez.

### Araştırılan erişim seçenekleri
1. **LBMA / ICE (IBA)**: dört resmi günlük kıymetli maden benchmark'ı, fakat tarihsel fiyatların tam erişimi için IBA lisansı gerekir: https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices
2. **MetalCharts Ultimate**: XAU/XAG/XPT/XPD USD/oz günlük spot geçmişi dördü için en az 2005 yılına kadar ve 2026 güncele kadar; sağlayıcı 18.10.2026'da her metal için tek tarihsel feed yayımladığını açıklıyor. 2010 tarihine kadar erişim **Ultimate tam geçmiş planı** gerektirir; yayınlanan liste fiyatı **249 USD/ay**, bir kullanıcı hesabı/API erişimi olmadan veriler alınamaz: https://metalcharts.org/metals-api
3. **Stooq**: dört metal spot sembolü bulunuyor ancak CSV indirmeleri için API anahtarı/CAPTCHA gerekir; bu oturumda erişim sağlanıp 2010–2026 dört metal tüm tarihsel kapsamı doğrulanamadı. Ayrıca Stooq farklı referans serilerini toplayabilen bir sağlayıcıdır.
4. **Standard Bullion**: kimlik doğrulamasız 4-metal daily geçmişi **2011'den** başlar; tek başına 2010'u kapsamaz: https://standardbullion.com/market-data

## Kapanış kabul kriterleri
- Seçilen tek sağlayıcıdan **2010 Ocak–2026 Eylül** dört metalin günlük orijinal satırları gerçekten alınır, bütün aylara uygun kapsama ve hafta içi senkronizasyon testi yapılır.
- Eski DB kayıtları önce güvenli yedeklenir, fiyat farkları ve kimlikli kaynak kayıtları karşılaştırılır, ayrı **versioned canonical** seriye aktarılır; bozuk kaynak satırları geriye dönük gerçek veri diye değiştirilmez.
- Tüm tahmin modellerinde girdi ve fiyat hedefi yeni seriyle yeniden kurulup 2010–2024 DEV, 2025 test, 2026 stress ayrı ayrı yeniden yürütülür.
- **Bu rapor sonuç: MODEL_VERI_KARISIMI_DURDURULDU / GERCEK_TEK_KAYNAK_2010_2026_BACKFILL_TAMAMLANMADI.**
