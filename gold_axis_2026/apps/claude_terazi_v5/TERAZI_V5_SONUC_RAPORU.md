# TERAZİ v5 — Sonuç: BAŞARISIZ, nedeni etiket olgunlaşma kuralı

2026-10-16. Ön kayıt `14c7e3b`. 2023–2025 sayıları geliştirme kaydıdır, kanıt değildir.

| | aylık K=2 (birincil) | haftalık K=2 | aylık K=3 | ölçüt |
|---|---:|---:|---:|---|
| net NAV | **87,04** | 102,37 | 107,98 | G1 ≥ 230,82 → geçmedi |
| işlem | 34 | 22 | 10 | G2 → geçti |
| hedefle uyum | %48,4 | %52,2 | %35,7 | G3 ≥ %65 → geçmedi |
| Ocak 2023 içeride | **%100** | %76 | %100 | G5 → **geçti** |
| maks düşüş | %24,81 | %12,66 | %13,32 | G6 → geçmedi |

Referans: hedefin 2 gün gecikmeli tavanı 310,15; al-tut 230,82. **v5 başarısızdır.**
(G4 nedensellik testleri bu turda koşulmadı; başarısız sürüm için ertelendi.)

2023 iyi: Ocak ve 8 Mar → 5 May hareketlerinin %100'ünde içeride. 2024–2025 kötü: model günler
içinde alıp satıyor (ör. 2024-05-20 al @2440, 05-23 sat @2360).

## Neden — ölçüldü

Yuvarlanan hedefte bir günün etiketi **ilk olgunlaştığı değerle kesinleşiyor** (ön kayıt §1).
v5 hedefi uzun hareketleri sonradan birleştirdiği için bu kural bozuluyor: uzun bir yükseliş
sürerken, ilk parçaları o anki kısa ufukta "kârsız kısa hareket" sayılıp **0** etiketleniyor;
hareket tamamlanınca nihai hedef onları **1** yapıyor ama model düzeltilmiyor.

| | tümü | 2023–2025 |
|---|---:|---:|
| ilk etiket ≠ nihai etiket | **%23,2** (358 gün) | **%35,9** (277 gün) |
| yön | hepsi 0→1 | hepsi 0→1 |
| ilk etiketlerin taban oranı | %35,8 | %35,0 |
| nihai etiketlerin taban oranı | %58,9 | %70,9 |

(v4'te bu oran %4,8 idi.) Yani model 2023–2025'te, sonunda "altında ol" çıkan günlerin üçte
birini "nakitte kal" diye öğrendi. Örnek: 14 Şub → 17 Nis 2024 hareketinin 44 gününden 11'i
ilk olgunlaşmada 0 etiketlendi.

## Önerilen düzeltme (yapılmadı)

Her öğrenme anında geçmiş günler **o ana kadarki en güncel hedefle yeniden etiketlenmeli** ve
kural sonuçları (μ) bu etiketlerle yeniden hesaplanmalı. Bu hâlâ nedenseldir (yalnız o ana
kadarki fiyatlar kullanılır); değişen, ilk olgunlaşmanın kesin sayılmaması. Ön kayıt eki gerekir.
