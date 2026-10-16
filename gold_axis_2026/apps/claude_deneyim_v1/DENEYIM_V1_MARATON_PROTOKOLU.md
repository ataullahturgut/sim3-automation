# DENEYİM v1 — Claude özgün deneyim modeli | Maraton protokolü

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`. Bu dosya maraton kodu ve aylık sonuçlardan ÖNCE commit edilmiştir.

## Amaç
Model 2023 Ocak'tan 2025 Aralık'a kadar ay ay ilerleyerek altının **neden** yükseldiğini ve düştüğünü öğrenir. Her ay o ayın **en uygun al/sat** hamleleri hesaplanır, bu hamlelerden önce piyasanın durumu ölçülür ve deneyim hafızasına yazılır. Model tarihleri değil, **tarihsiz durum örüntülerini** öğrenir. 2025 sonunda 36 ayın deneyimi tek algoritmada birleştirilir ve dondurulur. 2026 testi daha sonra ayrı yapılır.

## Aşamalar ve 2026 yasağı
1. **Deneyim maratonu:** 2023-01 → 2025-12. Kod, geliştirme modunda 2025-12-31'den sonraki hiçbir satırı yüklemez (kodda kontrol).
2. **Birleştirme ve dondurma:** 2025-12 sonu durumundan nihai algoritma, parametreleri ve belgeleri commit edilir.
3. **Test (sonra):** 2026 olay verisi aynı formatta toplanır, dondurulmuş algoritma değiştirilmeden çalıştırılır. 2026'nın bir kısmı önceki projelerde görüldüğü ve Claude 2026 ortasına kadar bilgi sahibi olduğu için test "yarı-kör" etiketlenir; gerçek kanıt 2026-10 sonrası ileri kâğıt testidir.

## Yürütme (PUSULA v1 ile aynı)
Karar 06:00Z (09:00 TSİ), dolum aynı gün 09:00Z; AL = ASK, SAT = BID; banka maliyeti varsayımı %0,8 / yön; NAV = tasfiye değeri. Dukascopy BID/ASK, Türk bankası kotasyonu değildir.

## En uygun strateji (ideal al/sat) — matematiksel tanım
İki durumlu (NAKİT/ALTIN) dinamik programlama: 2023-01-03'ten ayın son karar gününe kadar, gerçek dolum fiyatları ve maliyetle **son servetin logaritmasını en büyükleyen** al/sat dizisi. Sabit tutma süresi yoktur; gereksiz işlemleri maliyet kendiliğinden eler. Her ay sonunda o güne kadarki veriyle yeniden hesaplanır (son günlerin etiketi sonraki ay değişebilir; hafıza her ay güncel etiketlerle yenilenir). Bu tanım yalnızca **etiket** üretir; geriye bakış yalnız etikette serbesttir.

## Durum değişkenleri (tarihsiz, karar anında bilinen)
- **Altın:** 1/5/20/60 günlük log getiri, 20 günlük oynaklık, 60 günlük zirveye uzaklık, 200 günlük ortalamaya uzaklık.
- **Faiz:** 10Y reel faiz (DFII10) ve 2Y faiz (DGS2) 5/20 günlük değişim. Erişim: değer tarihinden 2 karar günü sonra.
- **Dolar:** FRED geniş dolar endeksi 20 günlük değişim (indirilebilirse). Erişim: değer tarihi + 10 takvim günü (H.10 haftalık yayın).
- **Oynaklık:** GVZ düzeyi ve 5 günlük değişim. Erişim: ertesi karar günü.
- **Pozisyon:** COT managed money net vadeli (düzey ve 4 haftalık değişim). Erişim: `cot_available_at_utc` < karar anı.
- **Makro sürprizler:** Son CPI ve NFP sürprizi (geçmiş sürprizlerin s.sapmasıyla ölçeklenmiş), son yayından bu yana gün, son yayın sonrası 240 dk altın tepkisi. FOMC: son ve sonraki planlı toplantıya gün. Erişim: yayın zamanı + 240 dk < karar anı.
- **Piyasalar arası:** Nasdaq (NQ), 10Y tahvil vadeli (ZN), petrol (CL) ve gümüş (SI) 5/20 günlük getiri; altın/gümüş oranı 20 günlük değişim.
- **Olayların matematiksel izi:** Hisse şoku (NQ 5g < −2σ), kaçış-güvenli liman (ZN ↑ ve NQ ↓), petrol şoku (CL 5g > 2σ), oynaklık sıçraması (GVZ 5g > 2σ).
Standardizasyon: genişleyen pencere, yalnız önceki günlerden; ±4 kırpma.
96 olaylık neden kaydı (tarife, jeopolitik, merkez bankası talebi vb.) ilk yayın zamanı doğrulanmadığı için **model girdisi değildir**; yalnız aylık raporda geriye dönük bağlam olarak gösterilir.

## Aylık döngü (her ay sonu, yalnız o güne kadarki veriyle)
1. İdeal al/sat yolunu yeniden hesapla.
2. Modelin o ay **kendi** verdiği kararları (önceki ay sonu durumuyla, ay içinde gerçek zamanlı gibi) kaydet: işlemler, NAV, ideal yolun yakalanan oranı.
3. Hata analizi: kaçırılan giriş, geç çıkış, yanlış giriş, gereksiz işlem.
4. "Neden" analizi: her ideal bacakta durum değişkenlerinin standart değişimi (hangi değişken ne kadar hareket etti), aydaki makro yayınlar ve sürprizleri, COT değişimi, çakışan olay kaydı hipotezleri.
5. Deneyimi güncelle ve modeli yeniden öğren (aşağıda).
6. Aylık matematiksel model raporunu `reports/AYLIK_YYYY_MM.md` ve `.json` olarak kaydet.

## Model (özgün): deneyim hafızası + ayırt edici metrik + histerezis
- **Hafıza:** Her gün için (durum vektörü, ideal pozisyon) çifti.
- **Ayırt edici metrik:** Her değişkenin ağırlığı, ideal ALTIN ve ideal NAKİT günlerini ne kadar ayırdığıyla belirlenir (son aylara daha fazla önem veren, küçültülmüş standart ortalama farkı).
- **Benzer deneyim skoru:** Bu metrikle bugüne en yakın geçmiş durumların ideal pozisyonlarının çekirdek ağırlıklı ortalaması.
- **Doğrusal skor:** Hafızaya güçlü düzenlemeli lojistik model.
- **Birleşim:** İki skorun ağırlığı, son 6 ayda modelin gerçek zamanlı ürettiği skorların ideal pozisyonu ne kadar iyi tahmin ettiğine göre ayarlanır (hatalardan öğrenme).
- **Karar:** p ≥ θ_giriş ise AL, p ≤ θ_çıkış ise SAT (θ_giriş > θ_çıkış, histerezis). θ'lar her ay, o güne kadarki gerçek zamanlı skorlarla oynatılan net servet en büyük olacak şekilde küçük bir ızgarada seçilir.
Tüm öğrenme yalnız ilgili ay sonuna kadarki veriyle yapılır.

## Dürüstlük
- Maraton sonuçları geliştirme dönemi sonucudur, test değildir. Claude'un 2023–2025 bilgisi etiket ve analizde kullanılır; model girdileri as-of'tur.
- Haber metinleri ve ilk yayın zamanı doğrulanmış haber akışı yoktur; olaylar piyasa izi ve planlı makro yayınlar üzerinden temsil edilir.
- Banka alış/satış kotasyonu olmadan kârlılık iddiası yapılmaz.
