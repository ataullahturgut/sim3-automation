# S2 — 4 saat / 1 gün / 3 gün / 1 hafta / 2 hafta yaşam döngüsü denetimi
**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 | **WORKSTREAM=MODEL** | **S2_DEV=MULTIHORIZON_IMPLEMENTED** | **S2_SCIENCE_GATE=NOT_PROVEN** | **S1_SCIENCE=FAIL** | **S3/TRADING=NOT_IMPLEMENTED**
**Tarih:** 16 Ekim 2026 · **GitHub:** aynı research-gold-core-timeless-selective-learning-20261016 dalı · Ham fiyatlar depoya yazılmadı.

## Ne gerçekten yapıldı
Mevcut [adaptive_phase_lifecycle_s2.js](adaptive_phase_lifecycle_s2.js) **aynı S1+S2 model zincirinde** uzatıldı; ayrı model/strateji/proje açılmadı. Her dört saatlik karar çıpasında beş belirlenmiş takvim ufku [240, 1440, 4320, 10080, 20160] dakika için **epizot bitiş olasılığı P(END≤H)** ve devam olasılığı **1−P(END≤H)** hesaplanır; destek yetersizse çekimser. Sonuçlar yalnız yayınlandıktan/gerçekleşip **olgunlaştıktan** sonra öğrenmeye/puanlamaya girer.

* Tamamlanmış epizotlar karar zamanından önce kapanmışsa tarihi eğitim örneğidir. Veri aralığı veya kaynak değişimi nedeniyle sağ-sansürlü epizotlar **bitiş örneği değildir**; sadece **yaş+H kadar gerçekten izlenmişse** doğrulanmış devam olarak süre-risk havuzuna alınabilir.
* Dört saat dolmadan gerçek hareketin sona erdiği gözlendiyse, iki haftalık END etiketi **erken ama gerçekten bilinebilir** ve puanlanabilir. Henüz bitmemiş epizotta END=0 ancak tüm ufuk boyunca **kesintisiz ve aynı kaynak kalitesiyle** izlendiyse doğrulanır. Kesintide veya örneklem sonunda devam hakkında bilgi uydurulmaz.
* Her ufuk için ayrı `issued/ready/scored/knownEnd/verifiedSurvival/censored`, Brier, geçmiş tamamlanmış sürelere göre baz çizgi, epizot-kümeli bootstrap ve **iki sınıf yeterliliği** tutulur.
* Eski 4s sonucu ile tam olarak karşılaştırılamayan yeni skorun nedeni: önceden ufuk bitmeden araya boşluk girdiği için sansürlenen **zaten gözlenmiş END** sonuçları artık erken olgunlaşıp doğru pozitif sayılır. Bu doğru sonuç-denetimi düzeltmesidir, kârlılık veya model iyileşmesi kanıtı değildir.
* S2 checkpoint şeması `KAVIS_S2_CAUSAL_EPISODE_MULTIHORIZON_20261016` sürümüne yükseltildi; eski tek-ufuk state'i sessizce uyarlanmaz. Dışsal haber firstprint, S1 başarısız ekonomi sinyali ve S3 işlem yetkisi **eklenmedi**.

## Gerçek veri deneyi — retrospektif 2023–2025
Neon read-only `gold_research_histdata_xau15m_candidate`: **67.919** orijinal bar, **67.653** tam 15-dk bar, **266** eksik; 2023–24 / 2025 farklı XAU kaynak kimliği ve tüm hafta sonu/boşluklarda epizot sağ-sansürü. **1.223 tamamlanmış**, **341 sansürlü** kısa epizot; medyan süre **3 saat 45 dakika**. Bu tanımların hepsi önceden belirlenmiş **4s-trend/oynaklık eşiğine** dayanır; 1–2 haftalık gerçek trend tanımı değildir.

| Ufuk | Hazırdan üretilen tahmin | Gerçekten skorlanan | END sonucu | Doğrulanmış devam | Model Brier | Basit süre Brier | Bilimsel sonuç |
|---|---:|---:|---:|---:|---:|---:|---|
| **4 saat** | 2.057 | **1.763** | 1.137 | 626 | **0,218717** | 0,219215 | Çok küçük, kanıtlanmamış fark |
| **1 gün** | 2.047 | **1.632** | 1.632 | **0** | 0,000433 | 0,000063 | **Ölçülemez: tek sınıf** |
| **3 gün** | 2.047 | **1.632** | 1.632 | **0** | 0,000433 | 0,000063 | **Ölçülemez: tek sınıf** |
| **1 hafta** | 2.047 | **1.632** | 1.632 | **0** | 0,000433 | 0,000063 | **Ölçülemez: tek sınıf** |
| **2 hafta** | 2.047 | **1.632** | 1.632 | **0** | 0,000433 | 0,000063 | **Ölçülemez: tek sınıf** |

**4s iyileşmesi:** baz çizgi−model Brier=+0,000499, **1.280 epizot-kümesi** bootstrap %95 **[−0,001493; +0,002431]**. Sıfırı içeriyor; model üstünlüğü kanıtlanmadı. Yıllık 4s skorlar: 2023 n=374 Brier 0,225380 / base 0,222920 (**kötü**), 2024 n=691 0,211966 / base 0,214112, 2025 n=698 0,221829 / base 0,222283. Bu yıllar test dönemi olarak optimize edilmedi; araştırmada defalarca incelenmiş arşiv olduğu için kör OOS deneyi **değildir**.

**1gün–2hafta metrikleri kesinlikle yorumlanamaz:** Skorlanabilen tüm kayıtlar END=1. Hiçbir doğrulanmış devam etiketi yok; çünkü başlangıç detektörü *birkaç saat süren mikro-epizotları* tanımlıyor ve uzun ufuk negatifleri için hafta sonu/boşluklara rağmen tam market devamı kanıtı gerekiyor. 100% doğru yön gibi görülebilecek değerler **tamamen tek-sınıf trivial** durumudur. Brier değerleri tabloya denetim için yazıldı; başarı göstergesi değildir. `estimable=false` güvenlik işareti bu dört ufukta zorunlu.

## S2 bilim kapısının asıl açık işi
Gerçek **günlük ve haftalık trend yaşam döngüleri**, dört saatlik mikro epizodun sonucu büyütülerek üretilemez. Aynı S2 zincirinin **ayrı zaman ölçekli rejim/epizot katmanını**, pazarın planlı kapanışı ile veri kaybını ayırabilen takvim ve oturum kanıtıyla, gerçek farklı sürelerdeki START/CONTINUE/PULLBACK/END/REENTRY'yi tarihsel as-of gözlemlerle öğrenmesi gerekir. O aşama yapılmadan S2 multi-horizon science PASS ilan edilemez. Eşiklerle 2023–25 hindsight optimizasyonu yapılmadı.

**Teknik test:** Eski 46 S1 + S2 önceki 9 + yeni 3 çoklu-ufuk regresyon testi = **58/58** izole JS harness PASS. GitHub Actions workflow ilgili S2 test dosyasını zaten çalıştıracak şekilde tanımlı; Actions sunucu koşusunun tamamlandığı ayrıca teyit edilmedi.

**Kısa karar:** `S2_MULTIHORIZON_MECHANICS=PASS`, `4H_HAZARD_ALPHA=NOT_PROVEN`, `1D_3D_1W_2W=UNESTIMABLE_CURRENT_SHORT_EPISODE`, `S2_SCIENTIFIC_GATE=PENDING`, `S1_SCIENCE_GATE=FAIL`, `NO_TRADE_POLICY`, `APP_UNCHANGED`.
