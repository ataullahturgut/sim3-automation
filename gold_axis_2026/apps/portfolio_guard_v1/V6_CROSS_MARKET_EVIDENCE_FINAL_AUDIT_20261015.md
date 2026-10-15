# V6 bilimsel sonuç — olay öğrenme ile çapraz piyasa aktarım doğrulaması

**2026-10-15.** Kod `macro_v6.js`; kaynaklar orijinal Git blob SHA ile sabit. 2024, 2025 ve 2026 geçmiş yılların tamamı veya bölümü daha önce araştırma bağlamında görülmüş olduğundan bu çalışma *bağımsız kör ileri doğrulama değildir*. Bu rapor alım-satım getirisi veya canlı risk alarmı sunmaz.

## Hipotez ve veri güvenliği
- Soru: Altın fiyatından gelen beş geriye dönük özellik yerine bunlara Nasdaq NQ, ZN tahvil vadeli ve CL petrol vadeli **saatlik kapanmış** getirilerini eklemek, ertesi 24 saatte XAU kapanışında görülecek >=%2 düşüşün riskini daha iyi sıralar mı?
- **Karar saati:** her uygun takvim işlem gününde Türkiye 09:00 (06:00 UTC), bir günde tek örnek. Başka varlık için saatlik OHLC barının açılışı bu karardan bir saat önce olup kapanışı karar saatidir. Böylece o karar sonrasının 1h barı kullanılmaz. Gelecek 24 saat altın fiyatları yalnız sonuç etiketidir.
- 2023-2026 için 2.904 saat etiketi, NQ/ZN/CL 1h+6h değişim verileri kaydedildi. Sadece eksiksiz eşleşen ve 21–24 saat sonra sonuç etiketi bulunabilen **506 günlük örnek** kaldı; 963 fiyat günü içinden 237 örnek makro veri eksikliği, 220 örnek ileri 24 saat etiket penceresi eksikliği nedeniyle dışlandı. Eksik veri sıfır doldurulmadı.
- Si gümüş vadeli 6h getirisi karar saatlerinin azında bulunduğundan hariç. Daha önce çalışılan Claude R71/R72 makro sürpriz tablolarının NFP/CPI/FOMC gözlemlerinde **ilk yayın vintage teyidi yok**, predictor yapılmadı. G01/G05/G06 nedensel ekonomik DNA doğrulanmadı; OLAY-02'de as-of fiyat etiketleri bu yüzden G05-C ya da G06-B olarak kesin atanamaz.
- **Tahmin hedefi:** gözlemden sonra 24 saat içinde, gelecekteki en az 5 tamamlanmış 3 saatlik altın kapanışının en düşüğü mevcut fiyatın %2 altında veya daha düşükse `DOWN_2PCT_24H`. Piyasa hafta sonu kapanırsa ileri 21 saate kadar veri yoksa bu hedef eksik sayılır.
- **Model:** önceki yıllarda eğitilmiş L2 lojistik regresyon; günlük veri bağımsızlık beklentisi için 09:00 tek örnek, yıl sınırında 96 saat etiket ambargosu, yüzde 2 olay sınıflaması. 2024 eğitim 2023, 2025 eğitim 2023–24, 2026 eğitim 2023–25. Aynı yılın ileri sonuçları fit'e sokulmaz.

## Ana sonuç: daha düşük Brier daha iyi

| İncelenen yıl | Tam eşleşen günlük örnek | 24 saatte -%2 altın vakası | Eğitimde pozitif | XAU-only Brier | XAU+NQ/ZN/CL Brier | Ek piyasa katkısı |
|---|---:|---:|---:|---:|---:|---|
| **2024** | 148 | **5** | 2 | 0,033162 | **0,031546** | Evet ama örnek çok az |
| **2025** | 155 | **8** | 7 | **0,047953** | 0,050139 | Hayır |
| **2026 (Ocak–Eylül)** | 114 | **14** | 13 | **0,112185** | 0,112769 | Hayır |

2024 5 pozitif olay ile makro katkısı üstüne güvenilir sonuç çıkarmak uygun değil. 2025'te hem Brier hem logloss kötüleşti; 2026'daki 14 olayla risk modeli de daha iyi olmadı. Bu nedenle **ek veri katmanı V6 karar mekanizmasına otomatik eklenmeyecek**.

| Yıl | Basit geçmiş olay sıklığı Brier | XAU-only log loss | Çapraz piyasa log loss |
|---|---:|---:|---:|
| 2024 | 0,032642 | 0,153599 | 0,136349 |
| 2025 | 0,049273 | **0,191256** | 0,207826 |
| 2026 | 0,115311 | **0,401925** | 0,405419 |

**Kontrol:** `acceptance.incrementalEvidenceOn2024And2025=false`, `tradeAuthorized=false`, `verdict=REJECT_UNPROVEN_CROSS_ASSET_IMPROVEMENT`. Tek bir sene görünür fayda yeni canlı emir izni değildir. Olay başına sonuç oranları nadir ve tekrar eden piyasa durumları nedeniyle kalibre edilmiş kriz olasılığı sayılamaz.

## Öğrenilen şey ve deneyi sonlandırma kararı
1. Fiyat evrelerini hesaplamak ve 2023–2026 arasında en az 24 saatlik düşüş etiketleri üretmek **başarıyla çalışıyor**. Ancak ekonomik *neden* açıklaması için ilk haber-vintage ve ekonomide gerçek aktarım belgeleri yoktur.
2. NQ/ZN/CL çarpanları geliştirme sürecine kontrol değişkeni olarak eklendi ama 2025/2026'da riski daha iyi öngörmediler; **modelin trading motoruna taşınmaları bilimsel olarak reddedildi**. V1–V5 kodları değişmedi.
3. Şubat 2026 132,91 USD alış/taşıma fırsatı veya V5 2026'da daha az zarar ettiği diye parametreleri yeniden düzenleyip aynı aylarda 'başarı' sunulmaz.
4. **Araştırma aşaması için nihai karar:** Şu an elimizde birden çok çalışan fakat bağımsız ve gerçek banka koşullarında kanıtlanmış hiçbir üstün AL/SAT politikası yok. Kullanıcı işlemi beklese bile geçmişe dönük yazılan modelin canlı sinyal üretmesi onaylanmadı.
5. Bundan sonraki araştırmanın öncelikli ve somut veri kapıları: R72 macro surprise yayın ilk-print doğrulaması, 2023'teki eksik altın saatlerinin gerçek kaynakla tamamlanması, bankanın gerçek BID/ASK fiyat kotasyonları, görülmemiş sonraki takvim döneminde parametresi sabit öngörü deneyi. Bunlar olmadan 6. veya 7. modelin eski yıllarda eşiklerle kâr yükseltmesi ekonomik geçerlilik göstermez.

## Tek tıkla uygulama
Windows'ta GitHub Desktop Fetch origin→Pull origin, `BASLAT.bat`, sol menü **V6 piyasa aktarım denetimi** > **V6 ekonomik aktarım testini çalıştır**. API `GET /api/algorithm/v6`; `npm test`, `npm run verify-macro-v6`; salt okunur, gerçek banka bağlantısı ve emir işleme yok.
