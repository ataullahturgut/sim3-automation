# ALTIN AYLIK MODEL — 2010–23 EKİM 2026 BEŞ SERİ VERİ DOĞRULAMA TUTANAĞI

**23 Ekim 2026 / Yalnız veri denetimi / Yol haritası ve eğitim bu raporun kapsamında değil**

## Nihai sonuç — doğrulandı ve veri tabanına işlendi

Araştırma veritabanı: Neon project `winter-art-94880101`, database `neondb`. Kaynaklar, *her serinin ilk kullanıldığı kaynak* üzerinden doğrulandı; eski fiyatlar ve orijinal tahminler silinmedi veya yeniden yazılmadı.

| Aile | Tarih / kapsam | Kaynak dosya doğrulaması | Veritabanı durumu |
|---|---|---|---|
| Gold XAU, Silver XAG, Platinum XPT, Palladium XPD | 2010-01-04..2026-07-31 | **16.918 gözlem**, **68/68 metal-yıl tam tarih-fiyat digest eşleşmesi**, orijinal `lbruton/StakTrakr` @ `ed2e549f82ba0d1cd3ca32842b82d3888d301e01` | Aynı orijinal `public.observations` serileri, **değiştirilmedi** |
| Aynı dört metal — sonraki dosya sürümü | 2026-08-01..2026-09-30 | **244 gözlem** aynı StakTrakr `02964d0324dde362099976c867f5077a369acaa5` Git blob'undan, 31+30 tam takvim günü | Salt araştırma `gold_monthly_h1.original_source_shadow_daily_v1` |
| Aynı dört metal — içinde bulunulan ay | 2026-10-01..2026-10-16 | **64 gözlem** (16 gün × 4 metal), aynı yeni sürüm | Aynı `shadow` tablosunda; **Ekim ayı tamamlanmış aylık hedef DEĞİLDİR** |
| GPR/GPRT/GPRA | 2022-03..2026-08 arşiv sürümleri, her birinde 1985'ten itibaren tarihsel endeks | **54 resmî tarihsel `.xls` dosyası × 3 endeks = 162/162 tam sürüm hash'i doğru** | Mevcut `GPR/GPRA/GPRT_OFFICIAL_GIT_PIT` sürümleri, **değiştirilmedi** |
| GPR/GPRT/GPRA — yeni resmî yayınlar | 2026-09 vintage: Jan2010–Aug2026; 2026-10 vintage: Jan2010–Sep2026 | **1.203 aylık endeks değeri** resmî `iacoviel` arşivindeki ilgili ilk-yayın Git commit'inden okundu | `gold_monthly_h1.original_source_shadow_monthly_v1` içine **1.188 yeni** + önceden doğrulanan 15 mevcut = **1.203**, revizyonlar ayrı saklandı |
| Birim / ölçek sözleşmesi | 4 metal + 3 GPR bileşeni | Metaller kaynak doğal fiyat seviyesi **USD/troy ounce**; GPR **endeks**, ne yüzde ne 0–1 olasılık | `gold_monthly_h1.five_series_verified_units_v1`: **7/7** kayıt, hepsi `research_only=true` |

## Teknik test kanıtları

- [GitHub Actions 39927995174 — tam beş-seri doğrulama SUCCESS](https://github.com/ataullahturgut/sim3-automation/actions/runs/39927995174): 2010–2026 Temmuz dahil dört metalin **16.918 tarih+fiyat eşleşmesi** (tarih|fiyat, ondalık 4); 54 eski GPR vintages × GPR/GPRT/GPRA (ay|değer, ondalık 6) **162/162**. Bu değerler salt basit grup ortalaması değil, orijinal dosyaya karşı sıralı içerik hash karşılaştırmasıdır.
- [GitHub Actions 39928442844 — 2026-09/10 resmî GPR tam 1.203 değer SUCCESS](https://github.com/ataullahturgut/sim3-automation/actions/runs/39928442844).
- Kaynak denetim manifestleri: `data_audits/FOUR_METAL_2010_2026_NEON_DAILY_CHECKSUMS_20261023.json` (68 orijinal DB digest referansı), `data_audits/GPR_OFFICIAL_54_VINTAGE_NEON_AGGREGATE_CHECKSUMS_20261023.json` (162 orijinal vintage hash/commit referansı). Scriptler: `tools/audit_full_2010_2026_stak_exact_v1.py` ve `tools/audit_full_2010_2026_gpr_vintages_v1.py`. Her ikisi de orijinal Git commit'ten yeniden indirip hesaplar.
- Kaynak geçmişi için [resmî GPR internet sitesi](https://www.matteoiacoviello.com/gpr.htm); veri normalizasyonu **1985–2019 ortalama = 100**, araştırma veritabanından doğrudan kontrol edildi: GPR, GPRT, GPRA'nın her biri **420 ayda ortalama 100.00000**. Bu, GPR sütununda yüzde veya yanlış ×100/÷100 uygulanmadığını doğrular.
- `CORE5_GPR_ROUNDED_RESEARCH_R1` ile `GPR_OFFICIAL_GIT_PIT` son eski resmi sürümünde **390 ortak ay**, ortalama mutlak fark **0.0024 endeks puanı**: iki ondalığa yuvarlanmış eski CORE5 değeriyle ölçek tutarlı; canlı ilk-yayın vintage statüleri aynı DEĞİLDİR.

## Kayıt ve kaynak sürümleri

### Dört metal

- StakTrakr eski pin `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, 2010..2025 yıllık spot-history Git blob'ları ve 2026 Ocak–Temmuz günlük fiyatlarıyla tam içerik eşleştirme.
- StakTrakr yeni pin `02964d0324dde362099976c867f5077a369acaa5`, `data/spot-history-2026.json` blob `ce0775767fad3d9d56431b5ca57c3e47a3c3a70b`. **2026 Ağustos 124, Eylül 120, Ekim 1–16 64** `shadow` gözlem, toplam **308**; **77 benzersiz tarih**, **88 hafta sonu metal kaydı** işaretli. `firstprint_verified=true` olan **sıfır** kayıt. Eski `public.observations` dört-metal serilerine Ağustos/Eylül/Ekim eklenmedi; araştırma modeli kendiliğinden kaynak değiştirmez.
- Orijinal StakTrakr 2010–2025 yıllık dosyaları `provider=LBMA,source=seed` **etiketi** taşıyor; orijinal LBMA ticari fixing yayın kaydını tek başına ispatlamaz.
- 2026 `source=sqld` satırları farklı biçimde hesaplanmış: StakTrakr kaynak kodu `AVG(spot)`u **tamamlanmış UTC takvim günü boyunca**, MetalPriceAPI beslemeli kendi `sqld` veritabanında hesaplıyor; JSON'daki `12:00:00` **sentetik timestamp**, fiyatın veya ortalamanın saat 12:00'de bilindiği delili değil.
- 2021-12-24 Platinum+Palladium fiziksel kaydı orijinal dosyada yok, Gold+Silver var; buna **uydurma fiyat yazılmadı**. Ortak dört-metal hesapta gün elenecek. Eksik kabulü veri fiziken kaydedilmemesi anlamına gelir; ilgili piyasa tatilinin resmî doğrulaması yapılmış sayılamaz.
- 2026 eski ve yeni Stak dosyası arasında **224 çakışan fiyatın revizyonu** gözlendi; iki sürüm ayrı korunmuştur.

### GPR

- Resmî site [Caldara-Iacoviello GPR](https://www.matteoiacoviello.com/gpr.htm): aylık **GPR**, tehditler **GPRT** ve eylemler **GPRA**. Bunların değerleri ham **endeks seviyesi**, normalize referansı **1985–2019 ortalama 100**; üç farklı kolon karıştırılmadı. 2021 yöntem revizyonu ve eski sürümlerin revize olabilmesi ayrıca kaydedildi.
- Eski 54 resmî aylık Git arşiv sürümü: 2022-03'ten 2026-08'e, üç metrik tam aylık değer hash eşleşmesi.
- Yeni 2026-09 tarihli resmî dosya `data_gpr_export_202609.xls`, original commit `21449bec606bc5a5b1bf58d08ce526dc35d66c94`, yayımlanma Git commit saati **2026-09-01 14:27:55Z**: **2010-01..2026-08 = 200 ay ×3=600 değer**.
- Yeni 2026-10 dosyası `data_gpr_export_202610.xls`, original commit `8b903073ea4ce9caf9b2f238e792685ca17270f4`, yayımlanma Git commit saati **2026-10-01 14:19:21Z**: **2010-01..2026-09 = 201 ay ×3=603 değer**.
- Veritabanında iki ayrı `source_version` ile **1.203 gözlem** var; hiçbiri mevcut 54 farklı sürümün yerine geçirilmedi. Örnek GPR Aug2026: Eylül 2026 sürümünde **117.918846**, Ekim 2026 sürümünde **125.621384**; sonraki sürümdeki revizyon eski tahmin anına taşınmaz.
- `GPR_OFFICIAL` cari-vintage serisi ile vintage kayıtları **farklı amaçlı**; hangisinin hangi forecast-origin saatinde elde edilebileceği ayrıca kaynak commit tarihiyle tanımlanır.

## Kalan DÜRÜST veri/sürüm sınırlamaları

**Aşağıdakiler doğrulanmış diye raporlanamaz:**

1. **23 Ekim 2026 itibarıyla StakTrakr yıl JSON dosyasındaki son tarih 16 Ekim 2026**. Ekim 17–23 için aynı yıllık kaynaktan gözlem mevcut değil; hiçbir sayı üretilmedi. Ayrıca 16 Ekim'e kadarki mevcut Ekim ayı tamamlanmış aylık hedef sayılamaz.
2. **Ekim 2026'nın aylık GPR endeksi henüz yayımlanmış resmî sonraki-vintage kapsamında değil.** Ekim 1 Git dosyası Eylül sonuna kadarki endeksi içeriyor; Ekim GPR'yi Ekim ayında olmuş gibi yazmak geleceği görme olur.
3. **2010–Şubat 2022 GPR özgün aylık ilk-yayın vintage arşivimizde yok.** Bu yılların **değerleri mevcut** (2022 ve 2026 resmî sürümlerin tarihsel geçmişinde), fakat bunları 2010 tarihinde erişilen orijinal sürüm diye sunmak mümkün değil. 2022+ origin için arşivdeki eski değerlerle geçmiş eğitim yapma olanağı bundan farklıdır.
4. **StakTrakr günlük arşivin orijinal tarihte halka açıldığı ilk saat kanıtlanmamıştır.** 2010..2025 `LBMA` kaynak etiketi tek başına bağımsız resmî LBMA fiyatı lisansı veya fixing doğrulaması değildir; 2026 `sqld` günlük UTC ortalama ayrı metottur. Bu **kaynak yöntemi değişimi** çözülecek kalite konusu; rakamsal checksum eşleşmesi yayın saati sertifikası değildir.
5. Orijinal `public.source_registry` metal serilerinde `unit` alanları daha önce **NULL**'dı. Eski metadata UPDATE edilmedi; denetlenmiş `USD/troy_oz`/GPR INDEX ölçekleri ve kaynak değişimi yeni **`five_series_verified_units_v1`** 7 satırlık sözleşmede ayrı, sürümlü şekilde kayda alındı. Bu kanıt yalnız araştırma derecesindedir.
6. Dünya Bankası karşılaştırmaları yalnız bağımsız fiyat ölçek kontrolüdür, ana ChHHO model için GEREKLİ kaynak kapısı değildir.

## Son yazma/readback denetimi

- DB `original_source_shadow_daily_v1`: **308 satır**, 77 gün, 4 metal, hiç false firstprint TRUE yok.
- DB `original_source_shadow_monthly_v1`: resmî GPR **1203 satır**, iki vintage, her birinde GPR GPRT GPRA; geçersiz firstprint TRUE yok.
- DB `five_series_verified_units_v1`: **7 satır**, 4 metal `USD/troy_oz`, 3 risk endeksi `INDEX_1985_2019_MEAN_100`.
- Modelin kanonik `XAU_STAKTRAKR_RESEARCH_DAILY_R1` Ağustos sonrası kayıt sayısı **0** (bilinçli karantina); archived ChHHO `forecast_records` sayısı **53**, **değiştirilmedi**.

**Son karar: FIVE_SERIES_SOURCE_AND_VALUE_AUDIT_PASS_WITH_DISCLOSED_HISTORICAL_PIT_AND_OCT_2026_GAPS.** Veri denetimi tamamlandı, sınırlamalar belgeye işlendi. Bu rapor bir eğitim/test önerisi veya algoritma yol haritası içermez.
