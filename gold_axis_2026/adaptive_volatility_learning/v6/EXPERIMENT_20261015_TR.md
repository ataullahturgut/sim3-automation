# GOLD V6: Çift ufuklu adaptif öğrenme araştırması — 15 Ekim 2026

**Durum:** EX_POST_RESEARCH / NOT_BLIND / NO_LIVE_EXECUTION / ECONOMIC_ALPHA_UNVERIFIED.

## Hedef ve gerçek uygulama

Yeni araştırma dosyası: v6_adaptive_replay.js. Başka projeler, V4/V5 kodu, ANA-01 / OLAY-02 / ÖĞREN-03 manifestleri veya silinmiş eski Ocak 2026 deneyleri değiştirilmez.

- 14 günlük (336 saat) uzun ufuk: CASH konumunda altın almanın kalan beklenen getirisi iki yönlü maliyeti karşılayabilecek mi?
- 96 saatlik kısa ufuk: GOLD pozisyonunu savunmak için kalan düşüş beklenen maliyeti aşacak mı?
- Her ufukta fiyat, NQ/ZN çapraz piyasa ve geçmiş sonuçların çevrimiçi ortalaması ayrı uzman; ek olarak yalnız doğrulanmış olay haberlerinde ORG01–ORG12 kanıtı için aday ekonomi uzmanı.
- Bir önceki tahminin 96 saat/14 günlük gerçek sonucu bitmeden etiket, model güncellemesi veya karşı-olgusal pişmanlık yazılmaz. Öğrenme ankrajı UTC 06:00 / TSİ 09:00; işlemler TSİ 09:00/12:00/15:00 checkpointlerinde.
- Tahmin uzmanları gecikmeyle gelen gerçekleşmelere göre online Ridge güncellemesi ve geçmiş MSE'den üstel ağırlıklandırma yapar. Karar eşikleri işlem maliyeti ve belirsizliğe göre kapılanır.
- Uygulama modeli MID araştırma fiyatı ve her AL/SAT bacağında %0,8; ilave gerçek banka ASK/BID makası, kayma ve kur farkı yok. Canlı emir yok.
- Ekonomik kaynakta firstprint, erişim saati, doğrulanmış durum ve kaynak linki olmadan ekonomi uzmanı **aktifleşmez**. V6 testinde uygun ekonomik vaka sayısı **0**.

## Şubat–Eylül 2026, 119,753917 USD nakitten başlayan ön deney

| Konfigürasyon | Son tasfiye USD | Başlangıca göre |
|---|---:|---:|
| V6 çift ufuk + online hata güncelleme + XAU/NQ stres satışı | **123,529545** | **+%3,153** |
| Aynı model, öğrenme 1 Ocak 2026 öncesinde dondurulmuş | 105,181771 | −%12,168 |
| Aynı model, XAU/NQ stres satışı devre dışı | 108,444342 | −%9,444 |
| Fiyat uzmanı + genel oran (stres satışı açık) | 123,529545 | +%3,153 |
| Başlangıçtan sona nakitte kalma | 119,753917 | %0 |
| İlk Şubat 09 TSİ alıp Eylül sonuna kadar pasif GOLD taşıma | 108,444342 | −%9,444 |

**Dört işlem, Türkiye saati:** 2 Şubat 09:00 AL (MID 4547,265); 3 Mart 12:00 SAT (5295,235, XAU/NQ stres); 6 Mart 12:00 AL (5108,048); 2 Nisan 09:00 SAT (4672,555, XAU/NQ stres). Daha sonra Eylül'e dek CASH.

**Ablasyon:** 2026 öğrenmesini dondurmak daha kötü; XAU/NQ satışını silmek de daha kötü. Fakat bu özdeş 2026 örnekleminde fiyat+NQ/ZN tahmin uzmanları, yalnız fiyat uzmanına göre yeni AL/SAT kararı kazandırmadı. Pozitif portföy sonucu, bir ekonominin doğru nedensel teşhisi değildir.

**Tahmin performansının zayıflığı:** 2026 Şubat–Eylül'de tamamlanmış 96 saatlik tahminlerde uzman karışımı yalnız 39/98 doğru yön, 14 günlük tahminlerde 64/160 doğru yön. Ufukların örtüşmesi nedeniyle 98/160 bağımsız olay sayısı değildir.

## Negatif doğrulama

2025 Ocak–Aralık ayrı başlangıç 100 USD CASH deneyinde V6 **104,275734 USD**, pasif GOLD **160,415265 USD**. Büyük ve uzun süren UP rejimini büyük ölçüde kaçırdı.

2026 Ocak ayrı 100 USD CASH deneyinde V6 **115,202011 USD**, aynı panelde pasif GOLD **115,366463 USD**. Bu Ocak sonucu eski 119,75 $ modelinin yerine geçmez.

Bu V6 paneli 3 saatlik Neon MID araştırma kesitlerinden oluşur. V4/V5'in 96,71 / 107,83 USD rakamlarıyla aynı saat, veri ve emir sözleşmesi doğrulanmadan doğrudan üstünlük çıkarımı yapılamaz. 2026 dönemi daha önce defalarca incelendiği ve bu ufuklar araştırma esnasında seçildiği için **kör test değildir**.

## Bilimsel geliştirme yol haritası

1. **Gerçek olay kanıtları:** OLAY-02'deki 96 olay için haber ilk yayımlanma + kullanıcıya teknik erişim saatini, dönemsel consensus vintage, DXY/USD, ABD 2Y/10Y/reel getiri, SI/PL, NQ/ZN ve karşıt haberleri kronolojik doğrula. Sahte nedensellik etiketi verme. İstatistikte olaysız ve karşıt olay kontrol günleri oluştur.
2. **Ekonomik olay durumları:** onset / continuation / exhaustion / reversal; 24, 96 ve 336 saat kalan UP/DOWN büyüklüğü ve OOD mesafesi. Yalnız olay sonrası gerçek zamanlı bilinebilen değişkenlerden eğitim yap.
3. **Adaptif hata defteri:** missed_UP, false_SELL, missed_DOWN, premature_BUY, bad_REENTRY. Kaçırılan fırsat analizini tek tek yap; üst üste binen 14 günlük etiketlerin yüzde değerlerini dolar kâr gibi toplama. Farklı maliyet hassasiyetleri ve eşik güncellemesi yalnız geçmiş geliştirme bölümlerinde.
4. **Aylık yürüyüş:** Her ayın başında dondurulmuş sürüm; ay boyunca as-of veri ve yalnız olgunlaşmış etiketle kontrollü güncelleme. Eski sürüme dokunmadan yanlışlanan eşikleri yeni sürüm olarak kaydet.
5. **Gerçekçi icra:** Kaynaklanan 15m ve tetik sonrası 1m emir saati, TR 09–17 banka gerçek BID/ASK + %0,8'lik iki işlem bacağı, varsa gerçek ek spread/kayma, posizyon devri.
6. **Bağımsız test kapısı:** Karşılaştırma nakit, aynı kaynak GOLD buy-hold, V4/V5, ekonomik katman kapalı/açık ablation, 2023–2025 ve daha sonra tamamen dokunulmamış ileri dönemler. Önce maliyet sonrası pozitif ek kazanç kanıtı, sonra ürün entegrasyonu.

## Yeniden çalıştırma

Node 22 veya üstü ile depo kökünden komut:

    node gold_axis_2026/adaptive_volatility_learning/v6/v6_adaptive_replay.js --data gold_axis_2026/adaptive_volatility_learning/portfolio_protection/verified_3h_asof_features_2025_2026_v0.csv --out v6_research_results.json

Test:

    node --test gold_axis_2026/adaptive_volatility_learning/v6/test_v6.js

**Sınır:** araştırma, gerçek işlem önerisi veya banka ile doğrulanmış kâr değildir. Makro-firstprint ve olaysız kontrol henüz tamamlanmamıştır; ekonomik katmanın marjinal faydası sıfır vaka nedeniyle test edilmemiştir.
