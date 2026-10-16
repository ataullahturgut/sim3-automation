# TERAZİ v3 — Ön kayıt eki 2: çıkış testindeki ölçek hatası ve düzeltmesi

2026-10-16. Ana ön kayıt `1fcdcaf`, kod ve ek-1 `278066b`. **v3.0 koşusu yapıldı ve sonucu
aşağıda olduğu gibi kaydedildi; bu ek, v3.1 koşulmadan önce commit edilmiştir.**

## v3.0 sonucu (ön kayıttaki haliyle) — BAŞARISIZ

`TERAZI_V3_0_ONKAYIT_HALI_SONUC.json`, `reports_v3_0/`

| | v3.0 | v2 |
|---|---:|---:|
| net NAV | 202,82 | 202,82 |
| brüt NAV | 215,31 | 215,31 |
| işlem | 7 | 7 |
| maks düşüş | %11,67 | %11,67 |
| hızlı kanaldan gelen satış | **0** | — |

Hızlı kanal 774 günün tamamında görüş üretti ama **hiç ateşlemedi**; 7 işlemin tümü yavaş
kanaldan geldi. Sonuç v2 ile birebir aynı. Geçme ölçütlerinden G1 teknik olarak sağlanıyor
(eşitlik), G3 sağlanmıyor.

## H1 ise güçlü biçimde TUTTU

Çıkış tabanı (60 kural, 163 kapı) kapı payları:

| | v2 evre tabanı | v3 kırılma tabanı |
|---|---:|---:|
| `g_r1` (altın 1g getiri) | %0,60 | **%33,74** |
| `g_r1 + g_r5` | %16,17 | **%34,36** |

Hedef H1a ≥ %5 ve H1b ≥ %30 idi; ikisi de tuttu. Günlük getiri, çıkış tabanının **en çok
kullanılan değişkeni** oldu. Yani teşhisin mekanizma iddiası doğrulandı: hedefi hızlandırmak,
yeni veri eklemeden, hızlı değişkenlerin kural doğumunu kazanmasına yetiyor.

## Ölçek hatası

Ön kayıt 2.3'te çıkış testini şöyle yazdım:

```
Q − λ·U_Q  >  EXIT_MULT · p₀        (EXIT_MULT = 2)
```

Bu, v2'nin kuralının doğru çevirisi **değil**. v2'nin kuralı cebirsel olarak bir z-testidir:

```
v2:   P − λ·U > 0,5   ⟺   (P − 0,5) / U > λ
```

Yani v2 şunu sorar: *"olasılık, referansını en az λ belirsizlik kadar aşıyor mu?"* Referans 0,5'tir
ve dağılımın ortasındadır; orada U ≈ 0,07, 0,5'e göre küçük bir toplamsal düzeltmedir.

Referansı p₀ = 0,0677 kuyruğuna taşıdığımda aynı yazım artık aynı testi yapmıyor. Ölçülen:
`U_Q ≈ 0,85 · Q`, çünkü nadir olayda kurallar arası çelişki terimi (μ_R − Q)² sinyalin kendisiyle
mertebe olarak eşit. Dolayısıyla `Q − 0,5·U_Q ≈ 0,57·Q` ve eşiğe ulaşmak için Q > 0,237 gerekiyor;
tüm koşudaki en yüksek Q 0,157. Test matematiksel olarak ulaşılamaz hale gelmiş.

Ayrıca `2·p₀` çarpanı v2'de **karşılığı olmayan, tarafımdan uydurulmuş fazladan bir parametredir.**

## Düzeltme (v3.1)

v2'nin kuralının referansı değiştirilmiş hali, tek biçimde:

```
ALTIN iken:  ( Q − p₀ ) / U_Q  >  λ   VE   makro onayı   →  SAT       (λ = 0,5, v2'den devralındı)
```

- Yeni parametre **eklenmiyor**; `EXIT_MULT` parametresi **kaldırılıyor**. Düzeltme serbestlik
  derecesini azaltır, artırmaz.
- λ = 0,5 v2'den gelir, v3 için seçilmemiştir.
- p₀ yine yalnız 2020–2022 ısıtmasından (0,0677, 739 etiket).
- Giriş kanalı ve `U_Q`'nun formülü değişmez.

## Dürüstlük kaydı

- Bu hatayı **v3.0'ın sıfır ateşleme vermesi üzerine** aradım. Keşif yolu buydu ve saklamıyorum.
- Ancak düzeltmenin gerekçesi "daha iyi sonuç vermesi" değil, yukarıdaki cebirdir: ön kayıttaki
  yazım, ön kaydın kendisinin "v2'nin güven mantığı korunur" ifadesiyle çelişiyordu.
- Düzeltmenin Şubat 2023'ü yakalayacağının **garantisi yok**: düzeltilmiş test v3.0'ın yolu
  üzerinde ölçüldüğünde 774 günün 10'unu geçiyor ve Şubat 2023 kırılma günleri z = +0,44…+0,47
  ile λ = 0,5 barajının altında kalıyor. Bu ek, sonucu bilerek değil, ölçeği düzeltmek için yazıldı.
- **λ ateşleme görene kadar düşürülmeyecektir.** λ ∈ {0,5; 1,0; 2,0} duyarlılığı raporlanır,
  seçim için kullanılmaz. v3.1 de G3'ü sağlamazsa v3 başarısız olarak raporlanır ve bu,
  "kırılma anı bu 35 değişkenden güvenilir biçimde kestirilemiyor" bulgusu olarak kayda geçer.
- Geçme ölçütleri G1–G5 değişmez.
