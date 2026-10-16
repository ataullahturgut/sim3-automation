# TERAZİ v4 — Ön kayıt eki 1: karar referansı taban orandır

2026-10-16. Ana ön kayıt `f3811ff`. **Bu ek, v4.1 koşulmadan önce commit edilmiştir.**
v4.0 koşusu yapıldı ve sonucu aşağıda olduğu gibi kaydedildi.

## v4.0 sonucu (ön kayıttaki haliyle) — BAŞARISIZ

| | v4.0 | ölçüt |
|---|---:|---|
| net NAV | **83,26** | G1 ≥ 230,82 → geçmedi |
| işlem | 28 | G2 20–60 → geçti |
| hedefle uyum | %53,6 | G3 ≥ %65 → geçmedi |
| ilk çıkış | 2024-11-04 | G5 < 2023-02-02 → geçmedi |
| maks düşüş | %22,79 | G6 ≤ %11,67 → geçmedi |
| pozisyonda geçen gün | **%15,0** | hedef %51 |

İlk işlem **2024-10-22**'de; model 2023-01'den 2024-10'a kadar (22 ay) hiç almadı.

## Teşhis: referans noktası hedefin taban oranıyla uyuşmuyor

Ana ön kayıt §1'de şunu yazmıştım:

> Taban oranın ~%40–50 olması v4'ün can alıcı avantajı: **0,5 artık doğal karar sınırıdır.**

Ölçüm bunu yanlışlıyor. Yuvarlanan idealin ürettiği etiketlerin taban oranı:

| tarih itibarıyla | etiketli gün | taban oran |
|---|---:|---:|
| 2022-12-30 (ısıtma sonu) | 770 | **%37,9** |
| 2023-06-30 | 883 | %38,5 |
| 2023-12-29 | 1031 | %38,5 |
| 2024-12-31 | 1279 | %40,0 |
| 2025-12-31 | 1546 | %45,0 |

Karar anında geçerli taban oran **%38**, 0,5 değil. v2'nin kuralı
`P − λU > 0,5`, cebirsel olarak `(P − 0,5)/U > λ` biçiminde bir z-testidir; referansı 0,5'tir.
Ortalama P ≈ 0,38 iken alım için P > 0,5 + 0,5U ≈ 0,55 gerekiyor — model yapısal olarak alamaz.
v2'de bu kural çalıştı çünkü **evre etiketinin taban oranı 0,539'du**, yani tesadüfen 0,5'e yakındı.

## Düzeltme (v4.1)

Referans, öğrenilmiş etiketlerin **taban oranına** taşınır:

```
p₀ = öğrenilmiş etiketlerin ortalaması (her ay sonunda güncellenir)

NAKİT iken:  (P − p₀) / U > λ   →  AL        (λ = 0,5)
ALTIN iken:  (p₀ − P) / U > λ   →  SAT
aksi halde pozisyon korunur
```

Okunuşu: *"Kanıt, koşulsuz orandan en az λ belirsizlik kadar yukarıda mı (aşağıda mı)?"*

- **Yeni parametre yok.** λ = 0,5 v2'den gelir. p₀ veriden okunur, seçilmez.
- **Nedensellik korunur:** p₀ yalnız o ay sonuna kadar **öğrenilmiş** etiketlerden hesaplanır;
  gelecekten bilgi girmez. Testle doğrulanır.
- `2λU` genişliğindeki tutma bandı korunur, yalnız merkezi kayar.
- Bu, yeni bir fikir değil: **v3 ek-2'de (`aa5ab2c`) türetilip commit edilmiş ilkenin
  uygulanmasıdır** — *"v2'nin kuralı bir z-testidir; referansı taban orana taşımak tek
  doğru çeviridir."* v4.0'da bu ilkeyi kendi ön kaydımda atladım.

## Dürüstlük

- Hata, v4.0'ın 22 ay hiç işlem yapmaması üzerine arandı. Keşif yolu buydu, saklanmıyor.
- Düzeltmenin gerekçesi "daha iyi sonuç" değil, ölçülen taban oran (%37,9) ile varsayılan
  referans (0,5) arasındaki uyuşmazlıktır.
- Geçme ölçütleri G1–G6 **değişmez.**
- v4.1 de geçmezse v4 başarısız raporlanır ve **beşinci mimari denenmez** (ana ön kayıt §5).
- 2023–2025 sayıları hâlâ geliştirme kaydıdır; eşik kullanıcının bu döneme bakarak yaptığı
  seçimden türetildi. Tek sınav 2026'dır.
