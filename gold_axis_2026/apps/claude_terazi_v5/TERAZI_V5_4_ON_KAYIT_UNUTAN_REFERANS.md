# TERAZİ v5.4: unutan referans | Ön kayıt eki 4

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`.
**Bu dosya v5.4 kodundan ve sonuçlarından ÖNCE commit edilmiştir.**

## 0. Teşhis (v5.3 sonrası, ölçüldü)

v5.3 (R=6) 2023–2025'te 3 Ocak 2023'te aldı ve hiç satmadı (230,82 = al-tut). İnceleme bir
**ölçü tutarsızlığı** buldu:

- Kuralların olasılığı μ, RHO = 0,995 ile **unutarak** güncelleniyor (yakın geçmiş ağır basar).
- Karar referansı p₀ ise 2020'den bu yana öğrenilmiş bütün etiketlerin **düz ortalaması**.

Yükselen piyasada P ile p₀ arasındaki fark yapısal olarak açıldı:

| ay | p₀ (düz) | 0,995 ağırlıklı etiket oranı | modelin ort. P |
|---|---:|---:|---:|
| 2024-01 | 0,458 | 0,433 | 0,422 |
| 2025-01 | 0,522 | 0,697 | 0,700 |
| 2025-12 | 0,578 | 0,793 | 0,800 |

z = (P − p₀)/U yukarı kaydı: yıllık ortalama z 2022 −0,88 → 2025 +1,66. 2025'te z'nin negatif
olduğu gün oranı %6; z hiç −0,6'nın altına inmedi. Bu nedenle hiçbir satış eşiği 2025'te
tetiklenemezdi. v5.3'ün "hiç satma" seçimi bu kaymanın sonucudur.

## 1. Tek değişiklik

p₀, kurallarla **aynı unutma hızıyla** hesaplanır. Öğrenilmiş etiket günleri kronolojik sırada
q₁ < … < q_N iken:

    p₀ = Σ RHO^(N−t) · y_t / Σ RHO^(N−t),   RHO = 0,995 (T2.RHO, yeni parametre yok)

p₀ kullanılan her yerde (karar referansı, kural saha güveni, yeniden kurma, doğum artıkları)
bu değer kullanılır. Hedef, K = 2, yeniden etiketleme (ek-1), kural makinesi, λ = 0,5: değişmez.
Isıtma 2020-01→2022-12, koşu 2023-01-03→2025-12-31. 2026 verisi yüklenmez.

## 2. Koşular

- **v5.4**: v5.1 (aylık, K=2, relabel) + unutan p₀. Sabit eşikler al z > +0,5, sat z < −0,5.
- **v5.4 + eşik öğrenme**: v5.3'ün `esik_ogrenme_v53.py` mantığı birebir (aynı ızgara, aynı
  12 aylık geçmiş, R = 3/6/12, birincil R = 6), sinyal v5.4'ün z serisi (2021-01-04'ten).
  Eşitlik bozma kuralı değişmez; ayrıca seçimin beraberlikten mi geldiği raporlanır.
- 2022 kontrolü (v5.3 ile aynı yöntem) raporlanır.

## 3. Ölçütler (sonuçlara bakmadan)

v5.4 için ana ön kayıttaki G1–G6 aynen (G1 ≥ 230,82; G2 10–60 işlem; G3 uyum ≥ %65;
G4 nedensellik testleri; G5 Ocak 2023 ≥ %50; G6 düşüş ≤ %11,67).

Teşhis ölçütü **D**: 2023, 2024, 2025'in her birinde z < 0 olan gün oranı ≥ %20
(sinyal satış bölgesine girebiliyor mu). D geçmezse düzeltme amacına ulaşmamıştır.

## 4. Dürüstlük

- Teşhis 2023–2025'e bakılarak yapıldı; bu dönemdeki sonuçlar **geliştirme kaydıdır**, kanıt değil.
- Düzeltme ilkesel (iki tarafın aynı pencereyi ölçmesi), sonucu iyileştirmek için seçilmiş bir
  parametre değildir; RHO zaten modelde var. Sonuç kötü çıksa da geri alınmaz, raporlanır.
- Tek sınav 2026.
