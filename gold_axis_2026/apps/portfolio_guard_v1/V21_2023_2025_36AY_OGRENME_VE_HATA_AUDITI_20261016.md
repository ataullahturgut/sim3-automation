# V21 — 2023 Ocak–2025 Aralık Kesintisiz Öğrenme: 36 Aylık Bilimsel Durum

Research date: 2026-10-16. Branch: research-gold-2023-forward-monthly-online-learning-20261016. PR #142.

## 100 USD CASH başlangıç, bankanın her AL ve SAT bacağı için %0,8
- 36 ay, 2203 banka-penceresi kontrol noktası. 2197 olgunlaşmış 3h Double-Q fiyat-aralığı güncellemesi. Ay kapanışında Q ağırlıkları, adaptif optimizasyon istatistikleri, CASH/ALTIN, zirve NAV ve işlem giderleri sonraki aya aynen taşındı. Gizli aylık sıfırlama yok.
- V18 price only: final 202.571891 USD; toplam 3 işlem (3'ü de 2023), 2024 ve 2025 boyunca hiç AL/SAT yok; maxDD 13.700768%. Total işlem masrafı 2.321368 USD.
- V18 + as-of NQ: final 176.154622 USD; toplam 7 işlem; maxDD 15.018297%. Toplam işlem masrafı 5.62189 USD.
- Altını ilk uygun kontrol noktasında al, Aralık 2025 sonunda satış varsayımıyla pasif net 231.044201 USD; nakitte kal 100 USD. Her iki dinamik varyant pasif altına yenildi.
- 2025 başarıları esasen pozisyonu elde tutmaktan kaynaklandı. Matematiksel katsayılar her ay güncellense de 2024–2025 fiyat-only modelinde tek bir pozisyon değişikliği gerçekleşmedi.

## Yıllık sonuçlar
| Yıl | Fiyat-only NAV başlangıç→bitiş USD | NQ ekli NAV başlangıç→bitiş USD | İşlem fiyat-only | İşlem NQ |
|---|---|---|---:|---:|
| 2023 | 100.00 → 97.16 | 100.00 → 92.77 | 3 | 5 |
| 2024 | 97.16 → 122.69 | 92.77 → 114.57 | 0 | 1 |
| 2025 | 122.69 → 202.57 | 114.57 → 176.15 | 0 | 1 |

## Aylık kesintisiz öğrenme defteri
| Ay | Fiyat-only NAV USD | NQ ekli NAV USD | Fiyat-only ay işlem | NQ ay işlem |
|---|---:|---:|---:|---:|
| 2023-01 | 98.02 | 99.47 | 1 | 1 |
| 2023-02 | 93.20 | 95.31 | 0 | 1 |
| 2023-03 | 101.68 | 93.45 | 0 | 1 |
| 2023-04 | 102.04 | 93.79 | 0 | 0 |
| 2023-05 | 100.69 | 92.54 | 0 | 0 |
| 2023-06 | 98.07 | 90.28 | 0 | 1 |
| 2023-07 | 100.81 | 90.28 | 0 | 0 |
| 2023-08 | 100.08 | 90.28 | 0 | 0 |
| 2023-09 | 96.38 | 90.28 | 0 | 0 |
| 2023-10 | 93.98 | 89.73 | 2 | 1 |
| 2023-11 | 95.73 | 91.40 | 0 | 0 |
| 2023-12 | 97.16 | 92.77 | 0 | 0 |
| 2024-01 | 95.73 | 91.40 | 0 | 0 |
| 2024-02 | 95.41 | 91.09 | 0 | 0 |
| 2024-03 | 103.87 | 99.17 | 0 | 0 |
| 2024-04 | 108.80 | 103.88 | 0 | 0 |
| 2024-05 | 110.14 | 105.16 | 0 | 0 |
| 2024-06 | 109.76 | 104.80 | 0 | 0 |
| 2024-07 | 113.65 | 108.50 | 0 | 0 |
| 2024-08 | 118.20 | 112.85 | 0 | 0 |
| 2024-09 | 123.91 | 118.31 | 0 | 0 |
| 2024-10 | 130.61 | 124.70 | 0 | 0 |
| 2024-11 | 124.98 | 114.57 | 0 | 1 |
| 2024-12 | 122.69 | 114.57 | 0 | 0 |
| 2025-01 | 131.58 | 114.42 | 0 | 1 |
| 2025-02 | 134.49 | 116.95 | 0 | 0 |
| 2025-03 | 146.53 | 127.42 | 0 | 0 |
| 2025-04 | 153.78 | 133.72 | 0 | 0 |
| 2025-05 | 154.84 | 134.65 | 0 | 0 |
| 2025-06 | 154.29 | 134.17 | 0 | 0 |
| 2025-07 | 154.89 | 134.69 | 0 | 0 |
| 2025-08 | 160.03 | 139.16 | 0 | 0 |
| 2025-09 | 179.13 | 155.77 | 0 | 0 |
| 2025-10 | 188.45 | 163.87 | 0 | 0 |
| 2025-11 | 196.00 | 170.44 | 0 | 0 |
| 2025-12 | 202.57 | 176.15 | 0 | 0 |

## Dürüst öğrenme denetimi
1. Q-learning gerçekten her yeni fiyat olgunlaşmasında Double Q değerlerini güncelliyor ve aylar arasında saklıyor. Ancak ay sonu analizinden sonra ödül fonksiyonu veya öğrenme mimarisini geliştiren ayrı bir üst-model bu sürümde henüz yok. Bu aşama yalnız kesintisiz matematiksel öğrenmenin doğrulanmış başlangıcıdır.
2. 2023 ilk ay fiyat-only NAV 98.018774, NQ NAV 99.468259; Şubat sırasıyla 93.203558 ve 95.313181. Fiyat-only 2023 boyunca yalnız 3 gerçek sanal işlem yaptı. 2024 ve 2025 boyunca TUT davranışı esas kaldı.
3. NQ her zaman fayda sağlamadı: 2023 Mart fiyat-only 101.68 USD iken NQ 93.45 USD. Çapraz piyasaları eklemek ayrı doğrulama gerektirir.
4. Bu arşivde gerçek 2023 XAU gözlemleri ve diğer piyasalar var; ancak bu koşuda sadece altın fiyatı ve öncesinden kullanılabilirliği etiketlenmiş NQ sinyali matematiksel girdi olarak işlendi. ETF, hisse senedi, SI/Pt/Pd, Fed ve haber/olay ilk yayın kanıtları tamamlanmadıkça kullanılmış gibi sunulmaz.
5. Üç saatlik spot price proxy, kullanıcının bankasının BID/ASK kotasyonu DEĞİLDİR. %0,8 maliyet, bu kaynağın üstünde modellenmiştir. 2023–25 geçmişi önceden araştırıldığından model performansı blind/OOS değildir.
6. Ocak 2026 için ayrı gerçek piyasa saati testinde olduğu gibi fiyat zamanlaması, gerçek banka emri ve 15dk olay yakalama becerisi halen ayrıca doğrulanmalıdır.

## Sonraki matematiksel araştırma hipotezi
- Sabit tek aralık gelir hedefi yerine yeniden giriş maliyetini de taşıyan çok ufuklu AL/SAT/TUT karar fonksiyonu: +3h/+12h/+1g/+3g beklenen net Q değerini öğren, baştan belirlenmiş maliyet farkıyla karar ver.
- Ay sonunda kalibreli hata kayıtlarından yalnız bir sonraki ayı etkileyen, önceden kayıtlı meta-öğrenme ve sabit esneklik sınırı; daha önce gözlenen aynı ayı tekrar optimize etme yok.
- ETF, hisse senedi, altın/gümüş/platin/paladyum, COT ve haber verileri için kaynak as-of/ilk yayın etiketleri tamamlandığında eklenir, eksik veri sıfır gibi uydurulmaz.
- 2023–25 sonuçları artık tanı/development; yeni değerlendirme dönemi için ön kayıt + maliyet sonrası pasif altın kıyaslaması gerekir.

## Kanıt
PREREG ilk commit 806290ec293db4345203bc8355363c1a6568c0a5. GitHub Actions run https://github.com/ataullahturgut/sim3-automation/actions/runs/38903393134 .
Detaylı 36 aylık JSON, gerçekleşen işlemler ve final öğrenilmiş Q-state checkpoint workflow artefaktında kayıtlıdır. Önceki Ocak 2026 dosyaları değiştirilmedi, gerçek bankaya emir verilmedi.
