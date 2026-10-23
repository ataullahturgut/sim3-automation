# GOLD MONTHLY — 2010–2026 Dört Metal ve GPR Veri Temizliği / Eksik Kayıt Defteri
**Denetim: 23 Ekim 2026 | Kaynak: Neon salt-okunur SQL + resmi veri sağlayıcılarının yayın sözleşmeleri**  
**Durum: DATA_GOVERNANCE_IMPLEMENTED / RESEARCH_REPLAY_PASS / LIVE_POINT_IN_TIME_NOT_CERTIFIED / MISSING_SOURCE_NOT_BACKFILLED**

## Kapsam ve dosyalar
- **Gerçek Neon aylık kaynak denetimi:** [GOLD_MONTHLY_FOUR_METAL_NEON_DATA_AUDIT_20261023.json](data_audits/GOLD_MONTHLY_FOUR_METAL_NEON_DATA_AUDIT_20261023.json), **201 ay** ve **54 resmi GPR Git sürümü**; ham lisanslı fiyatları repo'ya kopyalamaz.
- **Kaynak kalite motoru:** [tools/gold_monthly_four_metal_governance_v1.py](tools/gold_monthly_four_metal_governance_v1.py), 2010–2026 4 metalin eşleşen iş günü satırlarını güvenli biçimde seçer; eksik veriyi **uydurmaz**, hafta sonunu **sessizce içermez**, sağlayıcı kaymasını **ayırır**, GPR'nin eski sürümlerini kanıtsız PIT ilan etmez.
- **Dondurulmuş DEV kaynak kapısı:** [tools/gold_monthly_governance_dev_snapshot_gate_v1.py](tools/gold_monthly_governance_dev_snapshot_gate_v1.py), immutable kaynak hash'i ile **2010–2024 180 aylık araştırma kapsamını** doğrular.
- **Kaynak yönetişimi testleri:** [tools/tests/test_monthly_four_metal_governance_v1.py](tools/tests/test_monthly_four_metal_governance_v1.py). Kaynak kalite sonuçları otomatik olarak modelin CANLI veri kapısına terfi etmez.

## Gerçek Neon taramasından çıkan sayılar

| Kontrol | Sonuç | Hüküm |
|---|---|---|
| 2010-01..2026-09 toplam takvim ayı | **201** | Kapsam envanteri |
| Kaynağı `LBMA` / `seed` diye etiketlenmiş ve 4-metal eş iş günü >=15 olan aylar | **193** | Araştırma geçmişi, *PIT değil*: 2010-01..2026-01 |
| Sağlayıcı karışıklığı / hafta sonu / belirsiz sağlayıcı ayları | **6** | **2026-02..2026-07 karantina** |
| Tüm dört metal serisinde hiç fiyat olmayan aylar | **2** | **2026-08, 2026-09 mevcut arşivde yok** |
| Eksik fiziksel metal günü | **1** | **2021-12-24: Gold+Silver var; Platinum+Palladium yok**; ortak günden çıkarılır |
| Geçersiz / <=0 fiyat | **0** | Toplu değer kontrolleri |
| 2010–2025 tam yıllar | **16 yıl ×12=192 ay**, her ay dört-metal yeterli | Eğitim/replay mümkün, ilk yayım kanıtı değil |
| 2026 Jan | 21 gözlem/metal | Homojen kaynak etiketli araştırma verisi |
| GPR resmî `GPR_OFFICIAL_GIT_PIT` aylık vintage sayısı | **54**: 2022-03..2026-08 | Resmî Git commit-based historical vintage reconstruction |
| GPR tarihsel veri değerleri | 1985..2026 ve CORE5 1994..2026 | Eski tarihler için *güncel veya daha yeni vintage* değerleri kullanılabilir; eski ay origin'i PIT sertifikası yok |

### 2026 sağlayıcı kalitesi (Neon kaynağı `XAU/XAG/XPT/XPD_STAKTRAKR_RESEARCH_DAILY_R1`)

- 2010..2025 tüm fiyatlarda sağlayıcı metaverisi `LBMA`, payload türü `seed` (bunlar **kanıtlı orijinal LBMA firstprint / lisans anlamına GELMEZ**; 2026-09-05 retrospective upload).
- **2026-02:** `LBMA`, `MetalPriceAPI`, `StakTrakr` birlikte; **4 hafta sonu tarihi**.
- **2026-03:** `MetalPriceAPI` ve kaynağı belirsiz `sqld`; **6 hafta sonu**.
- **2026-04:** sağlayıcı `UNKNOWN/sqld`; **8 hafta sonu**.
- **2026-05:** sağlayıcı `UNKNOWN/sqld`; **10 hafta sonu**.
- **2026-06:** sağlayıcı `UNKNOWN/sqld`; **8 hafta sonu**.
- **2026-07:** sağlayıcı `UNKNOWN/sqld`; **8 hafta sonu**.
- **Toplam 44 hafta sonu tarihi**, altın serisindeki 2026-02..07 dönemi; 2026-04..07 her takvim günü mevcuttur ama **borsa iş günü/fixing serisiyle eşdeğer değildir**.
- **2026-08 / 2026-09:** aynı dört-metal kaynak ailesinde **sıfır** veri. Başka bir **yalnız altın** serisini 4 metal yerine doldurmak yasak.

### GPR: neden 2010–2022 günlük fiyat var ama ilk tarihli vintage yok?

Resmi Caldara–Iacoviello [GPR site](https://www.matteoiacoviello.com/gpr.htm) GPR aylık sürümlerinin başında yayımlandığını, bazı geriye dönük revizyonların olabildiğini ve arama metodunun 2021'de değiştiğini açıkça belirtiyor. Veritabanındaki `GPR_OFFICIAL_GIT_PIT` **54 archived monthly release** içeriyor, ilk `2022-03`. Tarihsel 2010 aylık GPR değeri **YOK değildir**; 2022 vintage içindeki tarihten geriye uzanan seriyle 2022+ model eğitiminde kullanılabilir. Ancak `2010 origin tarihinde elimde bu bugün gördüğüm GPR vardı` diye iddia edilemez. Önceki metodolojide üretilmiş eski veri, 2021 sonrası metotla birebir aynı değişken olarak eklenmez.

## Dış kaynak araştırması ve lisans engeli

- [LBMA Precious Metal Prices](https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices): resmi dört benchmark'ın tarihsel tablosu MyLBMA portalına taşınmış, **IBA lisans gerektiriyor**. LBMA fiyatı ve StakTrakr `LBMA` metadata etiketini **eşdeğer / aynı yayın anı** kabul etmek yasak.
- [London Platinum and Palladium Market](https://www.lppm.com/data): 1 Temmuz 2026 itibarıyla tarihsel Pt/Pd tablosu artık herkese açık değil; IBA lisans hattı. Bu durum **2026 Ağustos–Eylül 4-metal aynı fixing** hedefinin doğrulanmasını engelliyor.
- [Borsa İstanbul Kıymetli Madenler](https://www.borsaistanbul.com/en/data/precious-metals-and-diamond-market): dört metal için USD/ONS fiyat ve seans bilgisi sağlayabilen **alternatif piyasa/işlem ağırlıklı ortalama** tanımı; **LBMA fiyatı değildir**. Yeni alternatif model kaynak sözleşmesi tanımlanmadan mevcut seriye karıştırılmayacak.
- [Perth Mint historical](https://www.perthmint.com/invest/information-for-investors/metal-prices/historical-metal-prices/) geçmiş fiyatları başka bir bağımsız referans; metodolojik farklılık nedeniyle yine source-swap ile backfill yapılamaz.

## Aktif araştırma veri kapısı

`require_research_eligible_month(ym,ledger)`:
- `RESEARCH_ELIGIBLE_NOT_ORIGINAL_PIT` / `RESEARCH_ELIGIBLE_NOT_LIVE_PIT`: PASS — sadece araştırma.
- **2026-02..2026-07**: FAIL — sağlayıcı değişimi, weekend/unknown.
- **2026-08..2026-09**: FAIL — hiç 4-metal veri yok.
- geçersiz fiyat, asgari 15 gün altında, non-unique date-metal: FAIL.
- `require_real_time_firstprint(ym,ledger)`: her durumda FAIL — orijinal yayın/saatli kaynak kanıtlanana kadar geçmiş araştırma kaydı canlının yerine geçemez.
- 2021-12-24 Gold+Silver kalır, Pt/Pd olmadığı için ortak takvimden **yalnız o gün çıkar**, önceki gün fiyatı taşıma / interpolasyon **yasak**. Arşivin aslında devamlılığını bozmaz.

**Veritabanındaki kanonik gözlemler, eski aylık tahmin kayıtları, original model veya ana branch DEĞİŞTİRİLMEDİ.** Eklenen script salt-okunur kaynak kalite raporu ve ayrı temiz dört-metal *araştırma* paneli üretmeye uygun; bunun üretim modeline bağlanması için **kullanılabilir 4 metal original timestamp verisinin sağlanması ve ayrı onay** gerekir. GPR'nin 2022 öncesi özgün vintage kanıtı ve 2026 Aug/Sep lisanslı tutarlı dört-metal kaynak bulunmadığından **“tüm veri eksikleri kapandı” raporu verilmez.**

## Sıradaki bağımlılık / hangi durumda kapanır?
- 2026-08 ve 2026-09 için **aynı dört metalin tutarlı USD/troy ounce benchmark/fixing** günlük kayıtları, kaynak lisansı, saat/timezone, revizyon politikası.
- 2026-02..07 için yeniden homojen kaynak serisi veya ayrı model-split kaynak değişimi ve istatistiksel kalibrasyon kanıtı; hafta sonu fiyatlarını tek başına çıkarmak sorunu çözmez.
- Historical firstprint: veri sağlayıcısından actual data release timestamps yahut immutable archived time, eksik GPR gerçek tarihe uygun eski metodolojisi.
- Bunlar olmadan canlı aylık H=1 tahminin prospektif veri-zamanı ispatı tamamlanmış sayılamaz.
