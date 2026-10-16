# DENEYİM v1.1 — Karar katmanı iyileştirmesi | Ön kayıt

2026-10-16. Bu dosya v1.1 aday kodları ve sonuçlarından ÖNCE commit edilmiştir. Hâlâ geliştirme dönemidir (2023-01 → 2025-12); 2026 verisi yüklenmez.

## Teşhis (v1 maratonundan)
v1'in durum skorları ideal ALTIN/NAKİT günlerini giderek daha iyi ayırdı (gerçek zamanlı AUC 0,53 → 0,61 → 0,63), ama eşik seçimi modelin kendi geçmişindeki net servete göre yapıldığı için çıkış eşiği 0,10'a indi ve model 2023-12'den sonra hiç satmadı. Sorun skorun "ideal pozisyon olasılığı" olması: bu olasılık, bir çıkışın maliyeti (%1,6 tam tur) karşılayıp karşılamayacağını doğrudan söylemiyor.

## v1.1 fikri: sonuç belleği
Deneyim hafızasındaki her gün için, o günden sonra **gerçekte ne olduğu** da saklanır (yalnız olgunlaşmış olanlar: gün i'nin sonucu i+H gününde bilinir ve yalnız ay sonuna kadar olgunlaşanlar hafızaya girer):
- r_H = 100·ln(mid09[i+H] / mid09[i]), H = 10 karar günü;
- d_H = 1[sonraki H gün içinde mid09 yolu, i'deki değerin %c_rt kadar altına iner], c_rt = −200·ln(1−0,008) ≈ %1,606.
Bugünün durumuna benzeyen geçmiş durumlardan (v1'in öğrendiği ayırt edici metrik ve bant genişliğiyle, çekirdek ağırlıklı) şunlar tahmin edilir:
- E[r_H] (öncül: 0, 5 sözde gözlem ağırlığı),
- P(düşüş) = P(d_H = 1) (öncül: hafızadaki taban oran, 5 sözde gözlem ağırlığı).
Bu tahminler maliyetle aynı birimde (%) olduğundan karar kuralı **ayarlanmadan**, maliyetten türetilir.

## Adaylar (yalnız bu üçü; sonradan aday eklenmez)
- **C0:** v1 (değişiklik yok).
- **C1 (beklenen getiri, maliyet bandı):** NAKİT iken E[r_H] > c_rt/2 ise AL; ALTIN iken E[r_H] < −c_rt/2 ise SAT.
- **C2 (düşüş riski çıkışı):** NAKİT iken E[r_H] > 0 ve P(düşüş) < 0,30 ise AL; ALTIN iken P(düşüş) > 0,50 ise SAT.
Durum değişkenleri, metrik, bant genişliği ve aylık öğrenme döngüsü v1 ile aynıdır. Kararlar her ay yalnız önceki ay sonu bilgisiyle verilir.

## Seçim kuralı
1. Üç adayın 2023-01-03 → 2024-12-31 gerçek zamanlı son NAV'ları karşılaştırılır; en yüksek olan seçilir (eşitlikte düşük maks. düşüş).
2. **2025 iç doğrulama:** Seçilen aday C0 değilse ve 2025 yılı getirisi C0'ın 2025 getirisinden 5 puandan fazla düşükse, C0'a dönülür.
3. Sonuç ne olursa olsun üç adayın tüm sonuçları raporlanır.
Not: Claude 2025'te altının güçlü yükseldiğini bilir; bu yüzden 2025 iç doğrulaması zayıf bir kontroldür ve öyle raporlanır.

## Dondurma
Seçilen aday `DENEYIM_V1_1_DONDURULMUS_MODEL.json` olarak, sonuç belleğiyle birlikte dondurulur. 2026 testi bu dosyayla, kod değiştirilmeden yapılır.
