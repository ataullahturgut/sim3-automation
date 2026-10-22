# GOLD MONTHLY — GPR Ağırlığının Bağımsız Katkısı: ChHHO DEV Test Sonucu

**22 Ekim 2026 — COMPLETE / GITHUB_ACTIONS_PASS / DEV_ONLY / NO_AUTOMATIC_PROMOTION**

## Karar özeti

Aynı ChHHO-ANFIS mimarisinde ve aynı dört metalin **8 girdisi** korunarak yalnız VW günlük getiri ağırlıkları değiştirildi. 2022-04…2024-12'de 33 hedef ay, aynı kronolojik eğitim ve HHO optimizasyonu ile hesaplandı.

| Arm | DEV ΣAE USD ↓ | DEV direction ↑ | ΣAE farkı (GPR lehine) |
|---|---:|---:|---:|
| **GPR_PIT_CURRENT8 (yetkili mevcut model)** | **1413.0298545** | **23/33** | referans |
| **NO_GPR_FIXED_RECENCY** (λ=0.05, GPR yok) | 1780.9258274 | 18/33 | **367.8959729 USD** |
| **NO_GPR_EQUAL** (günlük getiriler eşit) | 7002988067.453009 | 19/33 | **7.0 milyar USD üzeri: SAYISAL PATOLOJİ** |

### 1. GPR vs sabit zaman ağırlığı (en anlamlı kıyas)

- GPR'nin toplam mutlak hata avantajı **367.90 USD** = sabit ağırlıklı yönteme göre **%20.66** daha az toplam hata.
- 33 ayda GPR **20 ay daha az hatalı, 13 ay daha fazla hatalı**.
- Eşli aylık AE medyan avantajı: **+6.1591 USD**.
- GPR yön doğru sayısı **23/33**; sabit yöntemde **18/33** (**+5 ay**).
- Yıllara göre GPR hata avantajı: **2022 +90.6239 USD** (9 hedef ay); **2023 +46.6318 USD**; **2024 +230.6403 USD**. Üç yılın üçünde de işareti GPR lehine.
- Önceden kayıtlı DEV istikrar kapısı: **PASS**; ancak bu bir dış dönem/prospektif istatistiksel üstünlük kanıtı değildir.
- Ay kazanımının 20/33 olması için basit iki taraflı binom işaret testi **p≈0.296**; aylar bağımsız olmayabilir ve yalnız bu test güçlü nüfus-genellemesi vermez.

### 2. GPR vs eşit günlük ağırlık (kararsızlık uyarısı zorunlu)

Eşit günlük ağırlık kolunda **2022-06** tahmini **7,002,988,024.68 USD/ons** olarak patolojik biçimde yükseldi. O ay gerçekleşen **1,837 USD/ons**, referans origin fiyatı **1,849 USD/ons**, elde edilen tahmin log getirisi **+15.1472** ve consequent tasarım condition number ≈ **2.236×10^18**.

**Bu 7 milyarlık ΣAE, GPR'nin fiyat tahminine milyarlarca dolar fayda sağladığı anlamına gelmez.** GPR'siz bu temsil ve optimizer eşleşmesinin ciddi sayısal kararsızlık yaşadığını gösterir. Uç ay **teşhis amacıyla** dışarıda bırakıldığında:
- Eşit ağırlık alternatifinin diğer **32 ay** ΣAE ≈ **1879.77 USD**;
- Aynı 32 ayda GPR aktif ≈ **1402.14 USD**;
- Bu yalnız **post-hoc duyarlılık teşhisidir**, yeni resmi hata metriği değildir; rapor edilen asıl 33 aylık sonuç değişmez.

### 3. Bilimsel yorum ve sınırlar

- **Bu deneyin özgün sorusuna yanıt:** GPR kontrollü VW, özellikle GPR'siz sabit λ=0.05 alternatifine karşı **DEV döneminde hem fiyat hatasında hem yönde olumlu** görünür.
- **Kanıt sınırı:** GPR ağırlıklarının bu **tek model ve tek geliştirme döneminde** faydası var; tüm piyasa rejimlerinde veya gelecekte mutlaka daha iyi olduğuna dair kanıt yok. Dahası, farklı sabit λ katsayılarının tümü test edilmemiştir; λ=0.05 **önceden** sabitlenmiştir ve sonuçlar görüldükten sonra değiştirilmemiştir.
- Geçmiş F1 “MR-only vs VW-only” deneyi GPR etkisini izole etmediğinden burada **kanıt olarak kullanılmadı**.
- Bu çalışmada 2025 ve 2026 sonuçları **NOT_RUN**, dış dönem doğrulama **NOT_PROVEN**; 2025/2026 açılmış başarı sonuçlarından GPR deneyinin parametresi seçilmedi.
- Yetkili CURRENT8 modeli **aynen korundu**. GPR ON/OFF seçici, ensemble switching, dinamik yeniden ağırlık veya yatırım aksiyonu bu çalışmayla **aktif edilmedi**.

## Kontrol ve üretim koşulu

- Veri: `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`; payload SHA256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`.
- Her hedef ayda aynı 8 input / 4 metal target, aynı HHO kodu (24 pop × 45 gen × 3 tekrar), aynı inner holdout, aynı deterministic seed, yalnız ağırlıklandırma farkı. `train_month < target_month`.
- GPR kolundaki gerçek X/Y özellikleri orijinal `vw_midas_msvr_successor_v1.py` hesaplamasıyla `np.array_equal` sınandı. Yetkili DEV fiyat ΣAE `1413.0297794085` ve `23/33` parite testi **PASS**: yeni koşu `1413.0298545`, mutlak yeniden çalışma farkı **0.0000751 USD**.
- Neon veritabanı bağlantısı: **yok**; snapshot hash/parite zorunlu. 2025 ve 2026 eğitim/seçim kullanılmadı.
- Ana model optimizer kodları ve uygulamanın canlı tahmin ekranı **değişmedi**.

## Doğrulanabilir asıl kanıtlar

- [Github Actions RUN 39766658131 — SUCCESS](https://github.com/ataullahturgut/sim3-automation/actions/runs/39766658131)
- Paired summary artifact ID **12420935911**: `GOLD_MONTHLY_CHHHO_GPR_WEIGHT_PAIRED_V1.json`.
- GPR aktif arm artifact **12421055562**, SHA-256 `e09d1c2032d92a3dc7c2be6a2cf8c5f8a6161c36a9b6155fd7b88af88b3e981b`.
- No-GPR equal arm artifact **12419959549**, SHA-256 `8c59989e3376b046dc6b4a3e2cb155b1561807d44f6571345f4e936781c2d4c7`.
- No-GPR fixed recency arm artifact **12420218301**, SHA-256 `901863db4613ed192b6e213035b176d06dbef166c30234e5e1d0ad4398904102`.
- [Experiment method](https://github.com/ataullahturgut/sim3-automation/blob/07997510fc113abf1b55465489bbabaa028bf67d/gold_axis_2026/tools/gold_monthly_chhho_gpr_weight_ablation_v1.py), [paired recomputation](https://github.com/ataullahturgut/sim3-automation/blob/07997510fc113abf1b55465489bbabaa028bf67d/gold_axis_2026/tools/gold_monthly_chhho_gpr_weight_summarize_v1.py).
