# TERAZİ v3 — Ön kayıt eki: saha güveninin referans noktası

2026-10-16. **Bu ek, v3 maratonu koşulmadan ve herhangi bir NAV/işlem sonucu görülmeden önce
commit edilmiştir.** Ana ön kayıt: `TERAZI_V3_IKI_KANAL_ON_KAYIT.md` (commit `1fcdcaf`).

## Neden gerekli

Ana ön kayıt 2.5'te "güven formülü değişmez" yazıyor:

```
güven = (2h − k + 10·c₀) / (k + 10)
```

`h`, kuralın **sahada doğru tarafı tuttuğu** indirimli ağırlıktır. v2'de doğru taraf şöyle ölçülür:

```
agree = 1  ⇔  (μ_R ≥ 0,5) == (y ≥ 0,5)
```

Bu, v2'nin dengeli hedefi için doğrudur: evre etiketinin oranı ≈ 0,54, yani 0,5 anlamlı bir
ayırıcıdır.

v3'ün çıkış hedefi **dengesizdir**: ısıtma döneminde ölçülen taban oran **p₀ = 0,0677**
(739 onaylanmış etiket). 0,5 referansı burada formülü bozar: hiçbir kuralın μ'sü 0,5'e
yaklaşmaz, dolayısıyla her kural daima "kırılma yok" demiş sayılır ve günlerin %93'ünde
bedava doğru çıkar. Güven, ayırt etme gücünden bağımsız olarak yükselir; ölüm kuralı
(`saha ≥ 15 ve güven < 0`) hiçbir zaman tetiklenmez ve işe yaramaz kurallar tabanda kalır.

## Yapılan uyarlama

Çıkış kanalında **yalnız referans noktası** taban orana taşınır:

```
agree = 1  ⇔  (μ_R ≥ p₀) == (y ≥ 0,5)
```

Okunuşu: *"Bu kural, kırılmanın koşulsuz orandan daha olası olduğunu söylediğinde gerçekten
kırılma oldu mu?"* Formülün geri kalanı (h, k, c₀, ρ, TRUST_SHRINK=10) aynıdır. Giriş kanalı
hiç değişmez; v2 nesnesi aynen kullanılır.

## Bu bir ayar değildir

- p₀ **yalnız 2020-01→2022-12 ısıtma döneminden** hesaplanır ve dondurulur. 2023–2025'ten
  hiçbir bilgi girmez.
- Alternatif bir referans değeri taranmamıştır ve taranmayacaktır. 0,5 → p₀ değişikliği,
  dengesiz hedefte formülün anlamını koruyan tek seçimdir; serbest bir parametre değildir.
- Bu ek, sonuçlara bakılarak yazılmamıştır: koşu henüz yapılmadı.

## Ayrıca kayda geçen uygulama ayrıntıları

Ana ön kayıtta ima edilen ama açıkça yazılmayan iki nokta:

1. **Kırılma penceresi onay gününde kesilir.** `brk[q] = 1` yalnız `top < q ≤ min(top+m, onay)`
   için verilir. Böylece etiketin tamamı onay gününde bilinebilir olur ve nedensellik testi
   (etiket, onay gününe kadarki fiyatlarla belirlenir) geçerli kalır.
2. **İki kanal sırayla sınanır.** Pozisyondayken önce hızlı kanal (kırılma + makro onayı),
   sonra v2'nin yavaş kanalı denenir. İkisi de "SAT" demezse pozisyon korunur. Nakitteyken
   yalnız yavaş kanal çalışır — hızlı kanalın alım yetkisi yoktur.
