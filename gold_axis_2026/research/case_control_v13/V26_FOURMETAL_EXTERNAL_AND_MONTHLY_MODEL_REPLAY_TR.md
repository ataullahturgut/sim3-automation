# V26 — 2010–2026 DÖRT METAL VERİ SAĞLIĞI VE GERÇEK AYLIK MODEL TEKRARLARI

**26 Ekim 2026 · Gold Control · salt-okuma araştırma dalı**

## Karar

**Dört metalin tarihli dış fiyat karşılaştırması tamamlandı; fiyat sağlık sertifikası henüz verilemez.** 27 Şubat 2026'nın dört metal ham fiyatı ciddi biçimde bozuk. Aynı veriyle eğitilmiş/gösterilmiş aylık model sonuçlarının Mart 2026 bölümünü önemli ölçüde etkiliyor. İç tabloları olduğu gibi bıraktık; yeni, bir günü dışlayan **araştırma veri sürümü** ve alternatif dış kapanış senaryosu oluşturduk. **Neon ham veri, ana algoritma, üretim alarm sistemi, eski tahmin kayıtları değiştirilmedi.**

### Sabit kaynak sözleşmesi

- 2010–2025 dört metal: `lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, Neon `public.observations` LBMA/seed/research filtreleri.
- 2026 dört metal: `gold_monthly_h1.staktrakr_2026_git_snapshot_daily_v1` commit `02964d0324dde362099976c867f5077a369acaa5`.
- **4.234** ortak hafta içi tarih, toplam **16.936** metal-tarih fiyat kaydı; kaynaklar ve fiyat değerleri olduğu gibi saklanan iki immutabl araştırma CSV'sinde.
- İki orijinal CSV: `outputs/v26_internal_fourmetal_2010_2018_NOT_PIT.csv` ve `outputs/v26_internal_fourmetal_2019_2026_NOT_PIT.csv`.
- Kısa dönem GPR veri vintageları Neon'un resmî arşiv satırlarından **2026-01..04** için **1.974 satır** olarak sabit: `outputs/v26_gpr_official_origin_vintages_Jan_Apr_2026_RESEARCH.csv`. Veri deposu GPR'yi değiştirmedik.

## Dört metalde tarihli bağımsız fiyat karşılaştırması

**Dış seri:** https://goldprice.com/ üzerindeki yıllık geçmiş sayfalarının ücretsiz indirilebilir tarih/günlük USD/ons kapanış CSV'leri. Kaynak GoldPrice.com; atıf korunmalıdır. Dış seri **aynı Londra AM/PM benchmarkını garanti etmez**, ayrıca günlük kapanışlar ve ilk yayın sürümleri (PIT) karıştırılmamalıdır. Tam dış CSV'ler repoya yeniden yayımlanmadı; yalnız yıllık toplulaştırmalar ve istisna özetleri elde tutuldu.

| Metal | Kaynağın 4.234 gününden dış seriyle karşılaştırılan | Mutlak farkı %5'i aşan gün |
|---|---:|---:|
| AU Altın | 4.201 | 1 |
| AG Gümüş | 4.232 | 1 |
| PT Platin | 4.201 | 5 |
| PD Paladyum | 4.203 | 23 |
| **Toplam** | **16.837** | **30** |

Bunlar 30 kesin hatalı fiyat değil; önemli piyasa günlerinde PM kapanış/London fixing saat farkları olabilir. 2010–2025 gümüş alt seri dış arşivle birebir örtüşüyor, fakat kaynakların ortak temel benchmark kullanması gerçek bağımsız ilk-yayın doğrulaması demek değildir. 2010–2025 AU/PT/PD'deki büyük sapmalar ayrıca gözden geçirilecek.

2010–2025 **16.162** ham metal gözlemi vardı; bir takvim günü (24 Aralık 2021) yalnız altın/gümüşle temsil edildiğinden dört-metal ortak günleri hesabında hariç. Kaynak tablosunda sıfır, negatif veya yinelenen fiyat-tarih bulunmadı. Metal fiyatlarının tarihsel ilk baskıları ve gün içi seans saati henüz tüm yıllar için kanıtlanmadı.

### 27 Şubat 2026 — kesin bilinen dört metal anomalisi

| Metal | StakTrakr iç kaynak | Dış günlük kapanış | Uyuşmazlık, dış kaynağa göre |
|---|---:|---:|---:|
| AU | 3.516,02 | 5.222,30 | -%32,67 |
| AG | 62,15 | 89,975 | -%30,93 |
| PT | 1.585,39 | 2.366,00 | -%32,99 |
| PD | 1.201,26 | 1.793,00 | -%33,00 |

Dört metal birlikte 26→27 Şubat'ta ~%28–32 düşüp 2 Mart'ta ~%48–52 artıyor. Londra benchmark kontrolleri bu seviyeleri desteklemiyor. **İç kaynaktaki 27 Şubat geçerli fiyat değildir.**

## V26 karantinalı fiyat versiyonu

**Araştırma amaçlı yeni sürüm:** `outputs/v26_censored_monthly_fourmetal_research_NOT_CERTIFIED.csv` — 2010-01..2026-09 **201 ay × 4 metal = 804 aylık satır**, tek kaynak aynı, gün silme dışındaki bütün günlük orijinal fiyatlar sabit.

- 27 Şubat 2026 dört metalde atlandı; **sahte/interpolasyon fiyatı üretilmedi**.
- Şubat 2026 fiyat ortalaması 20 değil **19 ortak gün** üzerinde; bu bir **duyarlılık senaryosudur**, tamamlanmış Şubat ayı gerçekleşen hedefi veya ilk yayın sertifikalı fiyatı değildir.
- Diğer 200 ayda fiyat ve günlük tarih sırası değişmedi.
- `EXTERNAL_CLOSE_ONLY_SENSITIVITY` ayrı dal içinde sadece 27 Şubat tarihine **GoldPrice.com günlük kapanışlarını** geçici olarak koyar; fiyat tanımı uyumlu diye onay verilmedi, Neon'a yazılmadı.
- Orijinal `RAW_UNTOUCHED` da korunuyor. Her hesapta yöntem etiketi var.

| Metal | Ham Şubat 2026 ort. | Şüpheli gün çıkarılmış ort. | Fark |
|---|---:|---:|---:|
| Altın | 4.934,0445 | 5.008,6774 | +74,6329 $ |
| Gümüş | 81,1008 | 82,0982 | +0,9974 $ |
| Platin | 2.099,5890 | 2.126,6521 | +27,0631 $ |
| Paladyum | 1.706,3385 | 1.732,9216 | +26,5831 $ |

İkinci sütundaki fiyatlar *doğrulanmış nihai fixing* değildir.

## Gerçek H=1 ANN/ANFIS/ELM karşılaştırması

Kod; orijinal `vw_midas_msvr_successor_v1.py` dosyasının **8 adet Au/Ag/Pt/Pd MR ve GPR-ağırlıklı VW** özellik denklemini, gerçek resmî orijin-vintage GPR ve asıl model fonksiyonlarını kullanarak üç fiyat koşulunda yeniden çalıştırıldı. Hedef ayın gerçekleşen `Y` girdisi estimatöre **None** verildi. Mart'a ait gerçekleşen altın fiyatı her koşulda aynı **4.879,69682 USD/ons** (araştırma serisinin Mart ortalaması).

### Araştırmada kullanılan seçilmiş algoritmalar — Mart 2026

| Model (kodun asıl sürümü) | Hatalı ham fiyat | 27 Şubat hariç | Dış günlük kapanış senaryosu | Hamdan dış senaryoya fark |
|---|---:|---:|---:|---:|
| MPA-ANN (orijinal) | 4.854,82 | 5.125,52 | 5.155,05 | **+300,22** |
| ChHHO-ANFIS (orijinal) | 4.470,05 | 4.631,06 | 4.762,54 | **+292,48** |
| AOA-ELM (hata düzeltilmiş V2) | 4.880,44 | 5.302,35 | 5.356,55 | **+476,11** |
| SMA-ELMFIS (inner scaler güvenli V2) | 4.246,95 | 5.243,69 | 5.234,27 | **+987,32** |

**Önemli:** AOA-ELM'in eski V1 kodunda optimizasyonu bozan sıfır katsayılı AOA problemi, SMA-ELMFIS V1'de inner-train/validation scaler sızıntısı vardı. Bu nedenle güvenilir karşılaştırmada eski kusurlu uygulamalar değil açıkça ayrı V2 sürümleri kullanılmıştır; orijinal V1 başarıları bu rakamlarla karıştırılmamalıdır.

Alternatif olarak ANN VANILLA, ANFIS V3 ve ELM VANILLA üçlü çalışması **Şubat, Mart, Nisan 2026** için her üç senaryoda toplam **27 gerçek model tahmini** üretti. Şubat için üç senaryonun tahminleri aynı kaldı (çıktığı gün itibarıyla henüz 27 Şubat bilgisi yok); farklı olan Şubat gerçekleşme etiketi. Mart modellerinde yaklaşık +267…+594 USD/ons farklar var. Nisan'daki farklar daha küçük fakat eğitim geçmişinde önceki ayın kirlenmiş `Y` etkisi sürüyor. GitHub Actions kaynak ve parametre kilidini kaydetti.

**Tahmin başarısı bütün modellerde iyileşmiş değildir!** Bazı modellerin ham/kirli girdilerle elde ettiği tesadüfen düşük Mart hatası yeni senaryoda artıyor; bazıları azalıyor. Yeni sonuçları tek başına model üstünlüğü olarak sunmak veri sızıntısı veya sonuç seçme yanlılığı olur.

## Açık kalan sağlıklı veri sertifikası kapıları

1. **Aynı fiyat tanımı:** AU AM/PM, AG öğle, PT/PD sabah/öğleden sonra fixing ve dış kapanışların hangisinin aylık modelin asıl StakTrakr verisiyle tam aynı olduğunu seans/time-zone/para birimi bazında sözleşmeye bağlama. Dış seri ile fiyat karışımı yapma.
2. **Lisans/PIT:** Resmî LBMA/LPPM tarihsel günlük benchmark tablolarının tam erişimi, yetkili lisans / provider vintage ve tüm 2010–2026 ilk baskı as-of kontrolü *yok*. Özel lisans gerekebilir. LBMA: https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices ve LPPM: https://www.lppm.com/charts .
3. **Şubat tam gerçekleşen hedef:** 27 Şubat'ın dört metalde *tam ve aynı seans tanımlı* doğru fiyatı kaynaktan belgelenmeden 19 günlük ortalama tam ay sayılmaz.
4. **Model başarı kararı:** Bu hesaplar 2026 olayları önceden bilinerek yapılan **geriye dönük fiyat duyarlılık sınaması**. Tüm DEV/2025/2026 yeniden eğitim, karşılaştırma ve canlı model yükseltme kararı için henüz yeterli değil; fiyat sağlığı kapısı sertifikası başarısız olmaya devam eder.

## Reprodüksiyon

```bash
cd gold_axis_2026/research/case_control_v13
python risk_v26_fourmetal_external_comparison.py
python risk_v26_monthly_models_sensitivity.py
python risk_v26_curated_models_stress.py
python -m unittest -v test_risk_v26_fourmetal_and_monthly.py test_risk_v25_price_health_gate.py
```

Bu kodlar **Neon bağlantı dizesi istemez**; girişler Neon SELECT'ten sabitlenmiş araştırma CSV'leri ve resmî kaynak-origin GPR CSV'sidir.

Güvenilir linkler:
- `outputs/v26_independent_all_fourmetals_annual_checks.csv` — 68 yıl×metal karşılaştırma özeti.
- `outputs/v26_curated_mar2026_models_COMMITTED.csv` — algoritmaların 12 adet gerçek Mart tahmin sonucu.
- `outputs/v26_censored_monthly_fourmetal_research_NOT_CERTIFIED.csv` — 804 satırlık karantinalı aylık fiyat karşılaştırma sürümü.
- `outputs/v26_gpr_official_origin_vintages_Jan_Apr_2026_RESEARCH.csv` — 1.974 GPR kaynak gözlemi.
- GitHub Actions `gold-v26-independent-fourmetal-comparison`, `gold-v26-monthly-ANN-ANFIS-ELM-source-sensitivity`, `gold-v26-curated-monthly-model-replays` çıktıları; kaynak ve model tanımlarıyla birlikte indirilebilir.

**Operasyonel hüküm:** Neon'daki yanlış 27 Şubat 2026 fiyatını başka bir seriyle otomatik değiştirme. Aylık tahminleri yeniden yayınlama veya model sıralamasını değiştirme. Araştırma kolundaki **V25 fail-closed sağlık kapısı** temiz veri onayını bloke ediyor, ama üretim aylık H1 veri yükleyicisine henüz zorunlu bağlanmış değil. Tam veri sağlık onayı **VERİLMEDİ**.
