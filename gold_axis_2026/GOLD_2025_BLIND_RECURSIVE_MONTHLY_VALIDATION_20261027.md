# 2025 Altın: 2024 sonunda kapanan gerçek kör 12-ay ileri simülasyon
Araştırma tarihi 2026-10-27. **2025 gerçek fiyatlarını görmeden 12 ardışık koşullu tahmin; sonuçlar SONRA ayrı karşılaştırıldı.**

## Veri sızıntısı denetimi
- ChHHO-ANFIS ve ANN: tam olarak 2027 için kullanılan **deneysel, 4 metal log-getiri** mimarileri; orijinal sekiz-girdili GPR ChHHO ve REDUCED4 ANN değildir.
- Tahmin modeline girişte **yalnız 2010-01–2024-12** aralığındaki 180 ay gönderildi. 2025–2026 satırları model fonksiyonuna verilmedi. Eğitim ve doğrulama: 2010-03–2021-12 (142 satır), 2022-01–2024-12 (36 satır). Son model fit 2024-12.
- 2025 Ocak tahmininden sonra Şubat için Ocak tahmini, Mart için Şubat tahmini vb. kullanıldı. 12 ayda gerçek 2025 fiyatı, GPR, metal fiyatı veya hedefi modele girilmedi.
- Tahminler önce ayrı salt-tahmin JSON dosyasına işlendi (Git blob `878387713d1296c5c008b84d317dfb6febe073e8`), daha sonra başka bir araç çağrısında gerçek 2025 12 ayı açılıp tahminler karşılaştırıldı (puan dosyası blob `e7a890d836c057cbbf7d5445cc143ca7171ef0e2`).
- **Sınır:** Bu, 2026'da geliştirilen mimariyle sonradan yapılan veri-izole kör simülasyondur; 2024 sonunda gerçekten yayımlanmış önceden tescilli model tahmini olduğu iddia edilmez. 2010–2024 fiyatları sonradan alınmış StakTrakr araştırma anlık görüntüsü; ilk yayımlandıkları fiyat kanıtlanmış değildir.

## Kör aylık tahmin ve gerçekleşen (XAU/USD aylık ortalama)
| Ay | ChHHO-ANFIS | ANN | 2025 gerçek |
|---|---:|---:|---:|
| 2025-01 | 2645.95 | 2648.46 | 2707.58 |
| 2025-02 | 2654.15 | 2660.21 | 2896.67 |
| 2025-03 | 2664.98 | 2675.79 | 2981.74 |
| 2025-04 | 2676.84 | 2693.38 | 3212.13 |
| 2025-05 | 2689.04 | 2712.04 | 3280.50 |
| 2025-06 | 2701.33 | 2731.27 | 3351.70 |
| 2025-07 | 2713.65 | 2750.84 | 3342.40 |
| 2025-08 | 2725.98 | 2770.65 | 3358.18 |
| 2025-09 | 2738.34 | 2790.65 | 3658.09 |
| 2025-10 | 2750.73 | 2810.81 | 4058.28 |
| 2025-11 | 2763.18 | 2831.12 | 4084.62 |
| 2025-12 | 2775.68 | 2851.58 | 4299.97 |

## 12 aylık doğrulama
| Ölçüt | ChHHO-ANFIS | ANN |
|---|---:|---:|
| MAPE | 19.848% | 18.885% |
| MAE USD/oz | 727.67 | 692.09 |
| Toplam AE USD/oz | 8732.01 | 8305.05 |
| 2025 yön başarısı | 11/12 | 11/12 |
| Aralık 2025 öngörülen | 2775.68 | 2851.58 |
| Aralık 2025 gerçekleşen | 4299.97 | 4299.97 |
| Mutlak hata avantajlı ay | 0/12 | 12/12 |

Kör 2025 simülasyonunda altın her iki modelde de yavaş yükseldi; gerçek fiyat hızlı yükseldi. Yönün 11/12 doğru görülmesi fiyat seviyesindeki başarısızlığı maskelememeli (iki model de 2025'te 12 ayın 12'sine yükseliş tahmin etti, gerçek Temmuz geriledi).
Karşılaştırma için düz Aralık 2024 fiyatını tüm 2025'e sabitleme kuralının MAPE'si 21.598%; ChHHO %19.85, ANN %18.88. Uyum sağlanmış bir 12-adımlı horizon backtest olmadan 2027 12-ay fiyat eğrisi güvenilir öngörü olarak tanıtılamaz.

## Metodolojik ayrım
- **Tek aylık model / H=1**: her yeni ayın gerçek verisi geldikçe yeniden tahmin yapılır; 2025 ayları gerçek önceki aylarla hesaplandığında uyarlanmış ANN yaklaşık %3.10, ChHHO %3.71 MAPE göstermişti.
- **Kör 12-adımlı recursive**: 2024-12'den sonra hiç gerçek fiyat almayan aynı uyarlanmış aileler. ANN %18.88, ANFIS %19.85.
- Bu iki deney aynı hedef ufkunda değildir ve geçmiş aylık orijinal ChHHO / REDUCED4 kıyasının yerine geçmez.
- Aynı nedenle 2027 projeksiyonlarını kesin fiyat hedefi, güven aralığı veya yatırım kararı kabul etmeyin.

## Sonuç dosyaları
- `research/gold_2025_blind_recursive_forecasts_ONLY_20261027.json` (önce kaydedilen tahminler).
- `research/gold_2025_blind_recursive_12month_score_20261027.json` (sonradan açılan gerçekleşenler).
- `tools/gold_2025_blind_recursive_replay_v1.js` (kaynakta 2024-12 katı kesimi).
- Neon orijinal veritabanına yazım yok, live uygulama değiştirilmedi.
