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
| 2 | FULL7 ANN | 7 orijinal ANN bileşeni, `tools/vw_midas_ann_stage4_batch41_v1.py` toplama kuralı | 7/7 SMOKE PASS; 54 AY ÇALIŞIYOR | [Actions 39980863604](https://github.com/ataullahturgut/sim3-automation/actions/runs/39980863604): 7 orijinal bileşen 3 ay smoke → 54 ay replay → eşit ağırlık kontrolü |
| 3 | REDUCED4 ANN | Aynı ANN havuzunun frozen 4 bileşeni | 4/4 SMOKE PASS; 54 AY ÇALIŞIYOR | Aynı Actions 39980863604; 4 özgün ANN bileşeninin eşit fiyat ağırlığı ile hesaplanır |
| 4 | SMA-ELMFIS (yön uzmanı) | `tools/vw_midas_elmfis_meta_batch_5_v1.py` | BEKLİYOR | 0/54 |
| 5 | AOA-ELM | `tools/vw_midas_elm_meta_batch_21_25_v1.py` | BEKLİYOR | 0/54 |
| 6 | LMC2_RBF_M32 | `tools/gpr_lmc_experiment_v1.py`, `tools/gpr_lmc_core_v1.py` | BEKLİYOR; frozen external-parameter modeli ayrıca korunmalı | 0/54 |
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
