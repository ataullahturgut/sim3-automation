# V15 — MEVCUT RİSK MODELLERİNE İŞ ZEKÂSI EKİ (TAHMİN DEĞİL)

Eski BASE14 / CFTC21 değiştirilmedi. Yeni regresyon, GBM, risk olasılığı
ve hedef etiketlerinden öğrenilmiş eşik yok. Yalnızca orijinal 14/21 özelliğin,
RobustScaler + IsolationForest (200 ağaç) skorunun ve eğitim dönemi %90/%95
sınırlarının **neden alarm verdiğini** gösteren tarihsel analiz katmanı var.

## Denetlenmiş sonuç
- 2026 BASE14: 50 kırmızı, 40 yanlış gün (sonraki 5 gün %5 kriteri).
- 2026 CFTC21: 32 kırmızı, 25 yanlış gün.
- 2025 BASE14: 32 kırmızı, 27 yanlış gün; CFTC21: 21 / 17.
- 2010–2022: 27 olay ve 81 kontrol gününün göstergeleri betimsel kıyaslandı.

## Dosyalar
- outputs/v15_daily_intelligence.csv: orijinal alarm, skor, eğitim eşiği,
  kırmızıya uzaklık, eğitim skor yüzdeliği, bugünkü fiyat hareketi, CFTC
  geçerli tarihleri, gösterge grubu duyarlılıkları.
- outputs/v15_parameter_trace.csv: her girdinin gerçek değeri, eğitim
  medyanı ve medyana uzaklığı (IQR).
- outputs/v15_example_dates.csv: Ocak/Haziran/Ağustos ve yanlış-alarm günleri.
- outputs/v15_historical_cases_and_controls.csv: tarihsel olay defteri.
- outputs/v15_case_control_descriptive_statistics.csv: geçmiş dağılımlar.
- outputs/v15_retrospective_alarm_driver_audit.csv: sonuç etiketleriyle
  yalnız SONRADAN yapılan yanlış/doğru alarm gruplaması.
- outputs/v15_historical_parameter_analogues.csv: her kırmızı alarm için
  mevcut 14/21 parametre uzayında en benzer tarihsel düşüş ve düşüşsüz
  dönem. Bu yalnız kayıt/kanıt aramasıdır; alarm ya da düşüş tahmini DEĞİLDİR.
- outputs/v15_audit.json: bütün koruma kontrolleri.

## Yorum sınırları
Gösterge grubu duyarlılığı: o gruptaki girdiler eğitim medyanıyla
değiştirilse mevcut IsolationForest skoru nasıl değişirdi? Bu, katkı
yüzdesi ya da nedensellik değildir; gruplar toplamı skoru vermez.
Yükseliş/düşüş bilgisi ilgili karar gününün tarihsel fiyatına aittir.
Gelecek beş günlük gerçekleşme SADECE retrospektif denetimde kullanılır,
alarm skoruna/eşiğine/kararına girmez. Günlük veriden kesin intraday
erkenlik sonucu çıkarılamaz. Geçmiş resmî ilk yayın numerik vintage
tam sertifikalı değildir. Canlı alarm, Neon ve orijinal kod dokunulmadı.
