# TERAZİ v3.6: birikimli kırılma kanıtı (CUSUM) | Ön kayıt eki 7

2026-10-17. **Karar kodundan ve sonuçlardan ÖNCE commit edilmiştir.**

## Teşhis (yapısal)
v3.3–v3.5'te satış her gün yalnız o günün sonsalıyla verilir (`Pe + λ·Ue < 0,5`). Alış ve satış
aynı 0,5 çizgisine bakar; 2023 Ocak'ında P 0,54–0,56'da, yani çizginin dibinde gezdi. Tek
günlük kırılma alarmı satışa yetiyor, toparlanan ve devam eden düşüş ayırt edilmiyor.
"Düşüş devam ediyor" ölçüsü karar mekanizmasında yok.

## Değişiklik: satış kararı birikimli kanıtla (Page CUSUM)
Kırılma kanalının günlük kanıtı, taban orana göre log-olabilirlik oranıdır:

    ℓ_t = ln[ odds(Q_t) / odds(p₀) ]        (kanal görüşsüzse ℓ_t = 0)
    S_t = max(0, S_{t−1} + ℓ_t)              (pozisyon altındayken; alışta S = 0)
    SAT  ⇔  S_t > h  VE makro onayı (v3 ile aynı)

h, Wald eşiği: h = ln((1−β)/α), α = β = 0,10 ⇒ **h = ln 9 ≈ 2,197**. α, β sonuçlara bakmadan
genel kabul gören %10 seçildi; ayar taraması yapılmaz.

Alış kuralı v2 (değişmez). Kırılma kanalı v3.5 (beceri güveni, COT hariç). Karar konumdan
bağımsız öğrenildiği için koşu v3.5'in günlük serisinden birebir yeniden üretilebilir; ayrıca
tam koşuyla doğrulanır.

## Ölçütler
S0: 3 Oca – 2 Şub 2023 satış yok · S1: 3–10 Şub 2023 arası satış · S2: NAV ≥ 213,49 ·
S3: işlem ≤ 20 · S4: düşüş ≤ %11,67. Geliştirme kaydıdır, kanıt değildir.
