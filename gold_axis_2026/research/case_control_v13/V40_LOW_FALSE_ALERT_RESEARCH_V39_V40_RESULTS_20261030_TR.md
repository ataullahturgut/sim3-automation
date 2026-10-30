# V39–V40 | %4 altın düşüşlerinde düşük yanlış alarm araştırması — doğrulanmış deneme kaydı

**30 Ekim 2026 | Durum: RESEARCH-ONLY, CANLI KULLANIMA ONAY YOK**

## Problem, seçilen değerlendirme

- Hedef: altın fiyatında bir gün sonunda sonraki **beş işlem gününde %4+ düşüş** olasılığı için ön uyarı. Başlangıç tarihinden sonraki fiyatlar yalnızca skorlamak için kullanılır.
- Farklı hedefler ayrıldı: **(a)** günlük uyarı isabeti ve sonuçsuz uyarı günleri; **(b)** tekrarları **8 işlem günü** susturarak tek alarm epizodunda sonraki 10 işlem gününde gerçek %4 düşüş olup olmaması; **(c)** büyük düşüşten önceki 10 işlem gününde ilk uyarı. Bu üçü birbirinin yerine geçemez.
- Dört metal saatlik gerçek StakTrakr arşivi **25 Mart 2026** itibarıyla mevcut; 2024–2025 aynı kaynak saatlik geçmişi yok. 2024–2025 için StakTrakr **günlük metal** ve GVZ/FRB H.15 fiyatlarıyla yavaş risk öncülü kuruldu; 2026 için dört metalin **aynı saat** 4 saatlik stres ölçüsüyle karşılaştırıldı.
- 2026 araştırma kayıtları daha önce incelendi; dört-metal -%1 eşiği de 2026 olaylarını görerek tasarlandı. **Hiçbir 2026 testi kör veya sertifikalı PIT değildir**.

## Bilimsel tasarım

- **V39:** Ridge-cezalı, dengeli lojistik regresyon; 15 gecikmeli günlük özellik (XAU, XAG, XPT, XPD 1 ve 5g, altın tepeye uzaklık, metallerin birlikte düşme oranı, metal dağılımı, GVZ, 10 yıllık ABD tahvil faizi). Özelliklerde metal günü **en az D−1**, GVZ/faiz **en az D−2**. **2024** yalnız model eğitimi, **2025** yalnız skor kalibrasyonu / epizot başına sonuçsuz uyarı bütçesi, **2026** geriye dönük test. Orijinal V22 hiçbir noktada yeniden eğitilmedi.
- **V40:** Aynı modelin mutlak risk puanını 2025 rejiminden 2026 rejimine doğrudan aktarmak yerine **son 60 geçmiş işlem gününe göre ampirik sıralama**. Alarm kesimi sadece 2025 verisinden donduruldu (**%97,5 sıra eşiği**). 2026 etiketiyle bu eşik iyileştirilmedi.
- **Kapanan bar / uyarı zamanı:** Günlük model skoru tamamlanan önceki günler üzerinden. 4-metal 4s anomali tamamlanan saatlik barlardan; ancak raporda gün sonu karar şeklinde karşılaştırıldı. Kaynağın ilk yayım zamanı (**firstprint**) doğrulanmadı; gerçek üretim başarısı iddia edilmez.

## V39 — 2026 aynı 148 fiyat gününde

2024 eğitim 249 gün, 7 pozitif köken gün; 2025 kalibrasyon 248 gün. 2026 ortak dört metal saatlik takvim: **153 gün**, sonraki 5g sonucu olgunlaşmış **148 gün**, StakTrakr günlük fiyat hedefinde **18 adet ≥%4 etiketli başlangıç günü**.

| Sinyal | Uyarı günü | 5g≥%4 ile eşleşen | 5g sonucu olmayan | Eşleşme oranı |
|---|---:|---:|---:|---:|
| V22 | **23** | **7** | **16** | **%30,43** |
| V22 veya ham 4-metal eşzamanlı -%1 | 42 | 9 | **33** | %21,43 |
| Yalnız V39 lojistik risk puanı | 103 | 15 | **88** | %14,56 |
| V22 veya (4-metal -%1 ve V39 yüksek risk) | 36 | 8 | **28** | %22,22 |
| **V22 ve V39 yüksek risk** (yüksek öncelik alt sınıfı) | **17** | **6** | **11** | **%35,29** |

Sonuç: **V22 + katı teyit** (mantıksal AND), sonuçsuz uyarı günlerini 16'dan 11'e indirdi; ancak 7 doğru eşleşmeden **1'i** elendi. **Yeni büyük düşüşleri yakalamayı başaramadı**; yalnız öncelik sınıflaması adayıdır.

8 işlem gününü tekrar uyarı bakımından birleştirdiğimiz ayrı epizot skorunda:
- V22: 8 uyarı epizodu; 10 fiyat günü içinde ≥%4 düşüşle eşleşen 3, **eşleşmeyen 5**.
- V22 VE V39 yüksek risk: 7 epizot; eşleşen 3, **eşleşmeyen 4**.
- V22 VEYA ham dört-metal: 12 epizot; eşleşen 4, **eşleşmeyen 8**.

Bu yöntem mesaj tekrarlarını azaltır; yanlış ekonomik sinyalin ortadan kalktığını tek başına kanıtlamaz.

## V40 — rejim değişimi testinin olumsuz sonucu

2025 risk puanı medyanı **0,3616**; 2026 ortak günlerinde **0,9535**. Aynı V39 mutlak **0,90983** eşik puanını geçenler 2025'te 22 gün iken 2026 ortak örnekleminde **106 gün** oldu; ciddi dağılım kayması var.

2025'te dondurulmuş son-60g **%97,5** sıra eşiği:
- 2026'da **yalnız 3 uyarı günü**, sonraki 5 işlem gününde ≥%4 düşüşle **0 eşleşme**.
- V22 VEYA (dört-metal stres ve yeni sıra koşulu): **23 uyarı günü / 7 eşleşme / 16 sonuçsuz**. Yani **V22 ile tamamen aynı**.
- Yalnız yüksek sıralı V22: **2 gün / 0 eşleşme / 2 sonuçsuz**. Başarıyı öldüren aşırı seçicilik.

**V40 tercih edilmez.** Rejim farkına dayanıklılık hedeflerken gerçek uyarıları da engelledi. Değerli pozitif sonuç, **veri dağılımı değişimini sayıyla kanıtlayabilmemizdir**.

## Bilimsel karar — kesinlikle sahte üstünlük yok

- Şu aşamada **“hem 5/5 düşüşü koruyup hem çok az yanlış alarm” sağlayan doğrulanmış kural bulunmadı**.
- Üç aşamalı sistem araştırması önerisi: `EARLY_WATCH` (orijinal BASE14/CFTC21 veya dört-metal anormal hareket, kullanıcıya düşük öncelik, sınırsız kırmızı değil), `CONFIRMED_REVIEW` (orijinal V22), `STRICT_HIGH_PRIORITY_RESEARCH` (V22 ve bağımsız günlük risk); bu üç durumu aynı renk ve alarm şiddeti olarak göstermemek.
- Alternatif ileri test literatürü: ardışık değişim tespiti (CUSUM / GARCH parameter monitoring), yapısal rejim geçişi (Markov switching), sabit alarm bütçeli ampirik/konformal kalibrasyon. Bunlar **ileride denenecek adaylar**; bu aşamada gerçeğe aykırı performans sonucu uydurulamaz.
- Ek veri sorunu: 2024–2025 için **dört metal eşzamanlı saatlik veri yok**, 2026 StakTrakr saatlik arşiv retrospektif; risk sınıfları az sayıda bağımsız düşüş içeren veriyle değerlendirilmiştir. 2027/ileriki tarihli, değiştirilmeyen ileriye dönük ilk-yayın veri ve alarm günlüğü üretimi gereklidir.

## Kodlar, testler, kanıtlar

- V39: `risk_v39_ridge_prior_fourmetal_confirmation.py`, `test_risk_v39_ridge_prior_fourmetal_confirmation.py`, `.github/workflows/gold-v39-risk-budget-frozen-validation.yml`. [GitHub Actions başarı: 41112775047](https://github.com/ataullahturgut/sim3-automation/actions/runs/41112775047) — 6/6 test PASS ve gerçek Neon read-only çalışması PASS. İlk CI regresyon testindeki yanlış yıl sınırı koşulu düzeltildi, ardından başarılı tekrar çalıştırıldı.
- V40: `risk_v40_causal_rolling_risk_rank.py`, `test_risk_v40_causal_rolling_risk_rank.py`, `.github/workflows/gold-v40-causal-rolling-ranks-risk-audit.yml`. [GitHub Actions başarı: 41113338728](https://github.com/ataullahturgut/sim3-automation/actions/runs/41113338728) — 12/12 test PASS ve gerçek Neon read-only çalışması PASS.
- Sonuç dosyaları ilgili Actions çalıştırmalarında **JSON artifact** ve job step logs olarak saklandı.
- **Üretim değişikliği:** YOK. Sinyal veritabanı, orijinal V22, canlı ANN, aylık tahmin, yatırım emirleri değiştirilmedi. Geliştirme sonuçları araştırma dalında tutulmalı, geriye dönük olarak canlı model başarılı ilan edilmemeli.
