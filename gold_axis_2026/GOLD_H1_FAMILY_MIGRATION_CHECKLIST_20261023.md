# GOLD H=1 — Ortak Aylık Model Grubu / Taşıma Kontrol Listesi

**Konum:** `ataullahturgut/sim3-automation` → `gold-midas-headswap-v1-20260925` → `gold_axis_2026/`.
**İşlem:** Eski başarıları yeniden icat etmek değil; mevcut dondurulmuş model sınıflarını, mevcut NEON_STAKTRAKR_GPR_V2 salt-okunur kaynağıyla teknik doğrulamadan geçirip sırayla yeniden çalıştırmak.
**Kayıt zamanı:** 2026-10-23.

## Başarılı model havuzu, yürütme sırası

| Sıra | Model | Orijinal uygulama / dayanak | Kapı | Çalıştırma |
|---|---|---|---|---|
| 0 | ChHHO-ANFIS | `tools/vw_midas_anfis_stage3c_literature_v1.py` | PASS | 54/54 geçmiş araştırma replays tamam, ayrı kaydedildi |
| 0 | DE-ABC-RBFNN | `tools/vw_midas_rbfnn_stage1_v1.py` | PASS | 54/54 geçmiş araştırma replays tamam, ayrı kaydedildi |
| 1 | PLS1 V1 All-4 | `tools/gold_monthly_challenger_b_pls1_v1.py` | 3/3 smoke PASS; 54/54 full PASS | [Actions 39979925070](https://github.com/ataullahturgut/sim3-automation/actions/runs/39979925070); DEV ΣAE 1390.83, 2025 ΣAE 1098.01, 2026 Ocak–Eylül ΣAE 1996.05 |
| 2 | FULL7 ANN | 7 orijinal ANN bileşeni, `tools/vw_midas_ann_stage4_batch41_v1.py` toplama kuralı | **54/54 PASS + 7/7 ACTIVE LEAK TEST PASS** | [Kaynak-snapshot 39986747259](https://github.com/ataullahturgut/sim3-automation/actions/runs/39986747259), [aktif sızıntı testi 39987397390](https://github.com/ataullahturgut/sim3-automation/actions/runs/39987397390); DEV ΣAE 1390.3694, 2025 1036.1148, 2026 1604.0026 ve 8/9 yön |
| 3 | REDUCED4 ANN | Aynı ANN havuzunun dondurulmuş dört bileşeni | **54/54 PASS + 4/4 ACTIVE LEAK TEST PASS** | Aynı kaynak snapshot ve test; DEV ΣAE 1392.9719, 2025 1034.6766, 2026 1680.6234 ve 8/9 yön |
| 4 | SMA-ELMFIS (yön uzmanı) | `tools/vw_midas_elmfis_meta_batch_5_v1.py` | BEKLİYOR | 0/54 |
| 5 | AOA-ELM | `tools/vw_midas_elm_meta_batch_21_25_v1.py` | BEKLİYOR | 0/54 |
| 6 | LMC2_RBF_M32 | `tools/gpr_lmc_experiment_v1.py`, `tools/gpr_lmc_core_v1.py` | **3/3 bilimsel ön denetim PASS, Nisan 2022 gerçek model pilotu PASS, 54 ay model koşusu başlatıldı** | [Actions 39990355055](https://github.com/ataullahturgut/sim3-automation/actions/runs/39990355055) tam tarihsel koşu DEV33 + 2025 12 + 2026 9; nihai performans ancak workflow tam başarılıysa onaylanır |
| 7 | RBF epsilon-SVR DAILY12 | `tools/gold_monthly_svr_dwt_stage2b_representation_v1.py` ve Stage3 özgün yöntem | BEKLİYOR; CURRENT8 yerine özgün DAILY12 gerekiyorsa muhafaza | 0/54 |
| 8 | CatBoost PRICE | `tools/gold_monthly_boosting_stage6b_catboost_full_dev_v1.py` ve Stage6 frozen model | BEKLİYOR; ekstra model paketi | 0/54 |

## Her modelin zorunlu kapısı

1. **Kimlik / dondurma:** Algoritmayı veya optimizasyon hiperparametrelerini yeniden arama yok; orijinal dosya ve model seçimi bozulmaz.
2. **Kaynak sözleşmesi:** `NEON_STAKTRAKR_GPR_V2`, eski CORE5 fiyat/GPR yok. Var olan araştırma verilerine dokunulmaz.
3. **Öngörü ufku:** Bir sonraki takvim ayı ortalama XAU/USD; hedef ay fiyatı veya hedef etiketi model eğitimine / yeni tahmin X girdisine girmez.
4. **Geçmiş:** Her tahmin anında yalnız tamamlanmış önceki ay etiketleri. Orijinal modelin tanımladığı eğitim başlangıcı ve kronolojik iç doğrulama mantığı sabittir. Yalnızca bir modelin girdisi için farklı özellik gerekliyse ayrı ve işaretlenmiş dondurulmuş temsil korunur.
5. **Bilimsel kapı:** NaN, sonsuz, aşırı fiyat/return ekstrapolasyonu, köken metal/GPR sürümü, matris durum bozukluğu, eksik ay veya optimizer çakışması başarısız sayılır. Başarısız koşu başarı gibi sunulmaz; ham kanıt saklanır.
6. **Aşamalı test:** DEV içinden bir ay + 2025'ten bir ay + 2026'dan bir ay: önce smoke. PASS olunca 33 DEV + 12 TEST + 9 STRESS = toplam 54 ay. Sonuçlar kaynak hash, gerçek fiyat, tahmin ve yön ile ayrı dosyalara gider.
7. **Sıralama:** Aynı kaynak/same-month gerçekleşenleriyle ΣAE, MAPE, Direction Accuracy ve 2,5%/3,0% eşiği değerlendirilir. 2025/2026 sonuçlarıyla hiperparametre optimize edilmez.
8. **Ekim:** Henüz bu taşıma havuzunun toplu karşılaştırmasına eklenmez. Etiketsiz ileri tahmin koşusu ayrı kapıdan geçmelidir; açık ayın fiyatı kullanılmaz.
9. **Uygulama ve DB:** Bu test aşamasında üretim uygulamasına model seçimi aktarılmaz, Neon mevcut forecast kayıtları değiştirilmez.

## İlk gerçekleştirilen işlem

- PLS1 kaynak dosyası zaten bu dalda mevcut; yeniden kopyalanmadı.
- `tools/gold_monthly_h1_family_replay_pls1_v1.py` özgün PLS1 `forecast_one` fonksiyonunu değiştirmeden çağıran kontrol katmanı oluşturuldu.
- `.github/workflows/gold-monthly-h1-family-migration-pls1-v1.yml`: 3 hedef smoke → 54 hedef sıralı koşu. Her ikisi de SUCCESS ve aynı NEON V2 verisini kullanıyor.
- Kanıt: [GitHub Actions PLS1](https://github.com/ataullahturgut/sim3-automation/actions/runs/39979925070); orijinal ANFIS/RBFNN 54x2 [kanıtı](https://github.com/ataullahturgut/sim3-automation/actions/runs/39969094669).

## ANN ortak havuz — 23 Ekim ek yürütme

- Uygulama adaptörü: `tools/gold_monthly_h1_family_replay_ann_component_v1.py`.
- Kaynak: `tools/gold_monthly_2026_aug_sep_topmodels_v1.py` içindeki aynı 7 orijinal `pred_component` yolu; ANN komponent kodlarına müdahale yok.
- Her bileşenin girdi özellikleri düzeltilmiş V2 sözleşmesiyle karşılaştırılır; hedef ay etiketleri öğrenici çağrısından önce `None` yapılır. Başarısız bireysel bileşen yerine sessiz başka tahmin kullanılmaz.
- 7 bileşenli FULL7 ve ilk dört bileşenli REDUCED4, **log-getiri ortalaması değil, fiyat tahminlerinin aritmetik eşit-ağırlıklı ortalaması** olarak elde edilir; eski havuz dondurması korunur.
- GitHub Actions: `.github/workflows/gold-monthly-h1-family-ann-ensemble-v1.yml`. 7 bilimsel smoke işi PASS olmadan, 7 komponent×54 geçmiş ay işi başlamaz; bütün komponentler PASS olmadan iki ensemble karşılaştırması oluşmaz.
- Uzun ANN tam koşusu, PLS1 başarılı tamamlandıktan sonra ayrı bir iş akışı olarak başlatıldı; sonuç işlerinin PASS durumu doğrulanmadan başarılı sayılmamalıdır.

## 16:02Z nihai ANN koşu doğrulaması — AÇIK BLOKAJ

- [Actions 39980863604](https://github.com/ataullahturgut/sim3-automation/actions/runs/39980863604): **FAILURE** overall, despite **7/7 smoke SUCCESS and 7/7 separate full 54-month component SUCCESS**. Thus the full seven-component predictions **378/378 rows** exist as seven separately retained artifacts.
- The sole failed job is `Assemble frozen equal-weight FULL7 and REDUCED4` (job 120509681486): assert on monthly per-origin feature SHA identical across 7 component artifacts. This scientific gate was not bypassed.
- Independent downloaded artifact comparison: VANILLA/SCA/DE_ABC/TLBO_TUNED_PSO/MPA_SCA feature provenance hashes agree for all 54 months. **MPA and ADAPTIVE_TLBO disagree with those five for 51 of the 54 months**; those two mutually agree. Their origin price, target actual and official GPR source commit agree with the five across 54 months. Hash mismatch reason remains **not yet established**. Do not claim exact feature-byte equality, model-pool scientific pass or frozen-ensemble validated success.
- Resolve provenance discrepancy before final FULL7 and REDUCED4 54-month numeric performance is declared. Existing components remain archived, source database and legacy model code unchanged. **Other families SMA-ELMFIS / AOA-ELM / LMC2 / SVR / CatBoost have NOT been rerun in the new source contract.**

## 23 Ekim 2026 — FINAL FULL7/REDUCED4 kaynak eşliği ve sızıntı kapısı PASS

Eski hata kaydı silinmedi: [39980863604](https://github.com/ataullahturgut/sim3-automation/actions/runs/39980863604) bileşenleri 7×54 PASS, fakat tam seti birleştirirken iki süreç grubu arasında hash uyumsuzluğu nedeniyle son aşama FAIL. Bu kaydın düzeltilmesi için yeni işlem geçerli ve bağımsız bir veri snapshot'ı üretir; orijinal algoritma kodlarına dokunulmadı.

Yeni doğrulanmış işlem: [39986747259](https://github.com/ataullahturgut/sim3-automation/actions/runs/39986747259), **tüm işler SUCCESS**. Veri 54 hedef için tek salt-okunur `NEON_STAKTRAKR_GPR_V2` yüklemesinde oluşturulan sabit girdilerden gelir: snapshot SHA-256 `576efa5033975559e1a963e06a9dc5b2b2b47d87e046390100605bd132f4d15b`. ANN'nin yedi orijinal bileşeninin tamamı ve FULL7/REDUCED4 toplama aşaması **tamamen aynı snapshot_sha256 ve per-origin model_input_sha256** izini doğruladı. Her bileşen 54/54; topluluklar da 54/54 ay.

Bağımsız aktif nedensel sızıntı testi: [39987397390](https://github.com/ataullahturgut/sim3-automation/actions/runs/39987397390), **8/8 GitHub Actions job SUCCESS**. Her yedi bileşenin 2022-04, 2025-01, 2026-09 aylarında hedef ay tüm metal getirileri aşırı sahte değerlere çevrildi ve 2099 ayından uydurma kayıt eklendi. Orijinal algoritma yeniden çağrıldığında dört çıktının tamamı aynı kaldı (maksimum mutlak değişim `<=1e-10`); geçmiş eğitim satırları da değişmedi. Bu **algoritmanın hedef etiket veya ileriki ay örneği sızdırmadığı** mekanik kanıttır. Veri kaynağı yeni StakTrakr retrospektif fiyat snapshot'ları olduğundan **orijinal tahmin anında o fiyat revizyonlarının aynen mevcut olduğu kanıtlanmış değildir**; prospektif PIT veya firstprint iddiası yok.

| Dönem | FULL7 ANN ΣAE USD | FULL7 MAPE | FULL7 doğru yön | REDUCED4 ANN ΣAE USD | REDUCED4 MAPE | REDUCED4 doğru yön |
|---|---:|---:|---:|---:|---:|---:|
| DEV 2022-04..2024-12 | 1390.369428 | 2.046950% | 23/33 | 1392.971904 | 2.061535% | 25/33 |
| TEST 2025-01..2025-12 | 1036.114849 | 2.470360% | 11/12 | 1034.676569 | 2.459699% | 11/12 |
| STRESS 2026-01..2026-09 | 1604.002602 | 3.989352% | 8/9 | 1680.623431 | 4.163872% | 8/9 |

**2026:** Her iki model de yalnız Eylül ayında yönü kaçırdı; diğer sekiz ayda doğru yön. FULL7 tahminleri 2026 Eylül için 4576.51 USD/oz, gerçek 4327.88; REDUCED4 4577.46 USD/oz. Karşılaştırma ve model seçimi DEV yetkisine bağlı, bu 2026 raporu yeni hiperparametre optimizasyon yetkisi değildir. **Sıradaki model:** LMC2_RBF_M32 GPR/MOGP; ardından RBF-SVR, CatBoost, AOA-ELM, SMA-ELMFIS.

## LMC2 — 23 Ekim 2026, **algoritma kontrolü tamamlandı / eğitime geçilmedi**

- [Preflight GitHub Actions 39989531757](https://github.com/ataullahturgut/sim3-automation/actions/runs/39989531757): 3/3 işler **SUCCESS**. Eski matematiksel testler `tools/test_gpr_lmc_core_v1.py` orijinal iki çekirdek, bağımsız matris kovaryansı, posterior ortalama ve varyans, matris kondisyonu, 40 türevin sonlu fark farkları, sentetik veriyle hedef/gelecek etiket değişmezliğini sınadı. Orijinal çözücü koduna müdahale edilmedi.
- Yeni test `tools/gold_monthly_h1_lmc2_scientific_preflight_v1.py`: `NEON_STAKTRAKR_GPR_V2` salt-okunur kaynağı için 54/54 ayın tüm örneklerini 2010-03'ten önceki tamamlanan aya dek kontrol etti, 54/54 ön-test hedefine yapay Y+2099 örneği eklendiğinde GP eğitim/doğrulama matrisleri ve scaler değişmedi, resmi GPR sürüm/lag kaynak izleri uygun bulundu.
- Korumalı eğitim seçimi: 2022–2024 DEV'de her ay kronolojik eğitim/son %20 doğrulama, üç L-BFGS-B tekrarından en iyi doğrulama sonucu, dış dönemler için parametrelerin ve scaler'in 2024-12 sonunda sabitlenmesi; 2025–2026 sırasında yalnız GP posterior geçmiş gözlemlerle genişler. Bu mimari orijinal dondurulmuş çalışmanın şartıdır, tarihsel dış dönem performansını bakıp hiperparametre değiştirme yetkisi değildir.
- **Yeni LMC2 fiyat tahmini henüz 0/54**; tam koşuya başlamadan önceki matematik ve veri engelleri temizlendi. `gpr_lmc_experiment_v1.py` eski 2026-07 bitişli dönem tanımlarını körlemesine çalıştırmak yerine, V2 veri kontratı ve 2026-09'a genişletilmiş ayrı salt-okunur yürütme adaptörü gerekir. Resmi as-of GPR ile kaynak izinin doğrulanması StakTrakr retrospective GOLD price **firstprint/PIT ispatı değildir**.

## 23 Ekim 2026 LMC2 gerçek deney başlatılması

[Actions 39990355055](https://github.com/ataullahturgut/sim3-automation/actions/runs/39990355055): `pilot` işinin tamamı **SUCCESS**: 2022-04 gerçek veri, orijinal 3 tekrar × 40-parametre bounded L-BFGS-B, exact Gaussian Process posterior, 2010-03…2022-03 eğitim kontrolü, maksimum covariance condition bound ve finite tahmin doğrulandı. Yalnız pilot koşusu için başarı var; daha geniş dönem bitmeden onu tamamlandı sayma.

Tek V2 tarihsel frozen ANN kaynak snapshot'ı SHA256 `576efa5033975559e1a963e06a9dc5b2b2b47d87e046390100605bd132f4d15b` LMC2 için de kullanıldı. Orijinal `gpr_lmc_experiment_v1.tune` / `forecast` ve kovaryans çekirdeği hiç değişmedi. Yeniden yürütme adaptörü `tools/gold_monthly_h1_lmc2_frozen_replay_v1.py`. İlk 33 DEV tarihi per-origin optimize, yalnız 2025-01'de bir kez theta/scaler freeze, sonrası Ocak 2025–Eylül 2026 arası 21 ay ek veriyle Gaussian posterior. Onaylı preflight [39989531757](https://github.com/ataullahturgut/sim3-automation/actions/runs/39989531757) daha önce 54/54 kronolojik eğitim ve sentetik hedef-gelecek zehirleme kontrolünü geçti.

**İlk kayıt sırasında 54/54 koşusunun son durumu henüz onaylanmadı**; 54 ayın tamamı ve kontrol işleri PASS olmadan yeni model performans rakamı yazılmamalı. DB değişiklikleri yok, frozen old models korunur.
