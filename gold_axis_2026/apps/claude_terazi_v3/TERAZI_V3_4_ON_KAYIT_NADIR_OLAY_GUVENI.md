# TERAZİ v3.4: nadir olay için kural güveni | Ön kayıt eki 5

2026-10-17. Dal: `research-gold-claude-pusula-v1-20261016`.
**Bu dosya v3.4 kodundan ve sonuçlarından ÖNCE commit edilmiştir.**

## 0. Teşhis (v3.3, 2023 Şubat incelemesi, ölçüldü)

v3.3 2023'te 2 Şubat tepesinden sonra satmadı; 27 Şubat'ta, altın ~%7 düştükten sonra sattı.
Kırılma kanalı 3 ve 6 Şubat'ta **görüşsüz** kaldı (toplam ağırlık W < 0,5), diğer günlerde
Q ≈ 0,07 ≈ taban oran 0,066 dedi.

Neden: kural güveni günlük **işaret uyumuyla** ölçülüyor:
`agree = (μ_önce ≥ p₀) == (y ≥ 0,5)`. Kırılma nadir (%6,6) olduğu için, kırılma riskini
doğru biçimde 4 kat yüksek söyleyen bir kural (μ ≈ 0,25) bile tetiklendiği günlerin ~%75'inde
"yanılmış" sayılıyor; güveni negatife düşüyor, ağırlığı 0'a iniyor ya da kural ölüyor.
Ocak 2023 sonunda: μ 0,23–0,28 olan 8 kuralın ağırlığı 0; hayatta kalan güçlü kuralların
hepsi "kırılma yok" (μ ≈ 0,05) kuralları. Sert düşüş günü bu kurallar tetiklenmediği için
kanal susuyor.

Bilgi veride var (2020–2022, 2023'e bakmadan): altının günlük getirisi < −1,5σ olan 27 günün
%29,6'sı kırılma günü (taban %6,6).

## 1. Tek değişiklik: güven = kalibrasyon becerisi

Yalnız **kırılma kanalının** kurallarında (RuleB). Her gözlemde (doğumdan sonra), kuralın o
anki μ'sünün taban orana göre log-olabilirlik kazancı:

    g = y·ln(μ/p₀) + (1−y)·ln((1−μ)/(1−p₀))
    κ = μ·ln(μ/p₀) + (1−μ)·ln((1−μ)/(1−p₀))      (kural kalibre olsaydı beklenen kazanç, KL)
    G ← ρG + w·g,   Kκ ← ρKκ + w·κ
    beceri = clip(G / Kκ, −1, 1)                   (Kκ ≈ 0 ise 0)
    güven = (k·beceri + TRUST_SHRINK·c₀) / (k + TRUST_SHRINK)

Eski formül `(2h − k + TS·c₀)/(k + TS)` = `(k·(2·uyum−1) + TS·c₀)/(k+TS)` idi; yalnız
`2·uyum−1` terimi `beceri` ile değiştirilir. Kalibre kural ≈ +1, taban orandan farksız ≈ 0,
yanlış yönde kural < 0. **Yeni parametre yok.**

Değişmeyenler: giriş kanalı (v2, dokunulmaz), alış kuralı, satış kuralı (birleşik sonsal,
Pe + λ·Ue < 0,5, makro onayı), kapılar, doğum/ölüm eşikleri, λ = 0,5, M_BREAK = 5, veri,
özellikler, koşu dönemi 2023-01-03→2025-12-31, ısıtma 2020→2022. 2026 verisi yüklenmez.

## 2. Ölçütler (sonuçlara bakmadan)

| | ölçüt |
|---|---|
| S1 | 2023'te 2 Şubat tepesinden sonra **10 Şubat dahil** satış |
| S2 | 2023–2025 net NAV ≥ 213,49 (v3.3'ten kötü değil) |
| S3 | işlem sayısı ≤ 20 |
| S4 | maksimum düşüş ≤ %11,67 |
| S5 | v3 nedensellik testlerinin tamamı geçer (mutlak) |

Ayrıca raporlanır: 3 ve 6 Şubat 2023'te kırılma kanalının Q'su ve en güçlü kuralları;
satışların her biri için geri alım fiyatı; al-tut 230,82 ile kıyas.

## 3. Dürüstlük

- Teşhis 2023 Şubat'ına bakılarak yapıldı (kullanıcının v3'ü 2023–2025'e göre ayarlama
  izni kapsamında). 2023–2025 sonuçları **geliştirme kaydıdır**, kanıt değildir.
- Sonuç kötü çıksa da ayar taraması yapılmaz; ek değişiklik gerekirse yeni ön kayıtla.
