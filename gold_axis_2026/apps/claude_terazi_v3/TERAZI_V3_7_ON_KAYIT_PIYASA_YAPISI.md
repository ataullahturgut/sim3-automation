# TERAZİ v3.7: piyasa yapısı onayı | Ön kayıt eki 8

2026-10-17. **Karar kodundan ve koşudan ÖNCE commit edilmiştir.** Kullanıcının talimatıyla
ayrı bir 2020–2022 kontrolü yapılmaz; 2023–2025 koşusuna bakılır.

## Teşhis
v3.6: kırılma kanalı Ocak 2023 geri çekilmelerine ve 3 Şubat'a aynı Q'yu veriyor (0,117–0,131).
Kanal günleri tek tek değerlendiriyor; yükselen tepe/dip yapısının bozulup bozulmadığına bakmıyor.

## Tanım: yapı kırılması (yalnız p06 fiyatından, nedensel)
- Salınım dibi: t günü, kendinden önceki 2 ve sonraki 2 işlem gününün kapanışından düşükse
  (kesin). Bu dip ancak t+2 gününde bilinir.
- Yapı kırıldı(t) ⇔ p06(t) < karar anında bilinen **son** salınım dibinin fiyatı.

**k = 2 seçimi 2023 Ocak–Şubat fiyatlarına elle bakılarak yapılmıştır:** k = 1 ile 27 ve 31 Ocak
da "kırılma" sayılıyordu; k = 2 ile Ocak'ta kırılma yok, ilk kırılma 3 Şubat (1.915 < 31 Oca dibi
1.917). Bu nedenle S0/S1 sonuçları bu tanımla örneklem içidir.

## Karar (v3.5 öğrenme kanalları değişmez)
- ALIŞ: v2 kuralı (değişmez).
- SATIŞ: pozisyondayken **yapı kırıldı VE Pe + λ·Ue < 0,5 VE makro onayı**. Yapı kırılması
  olmadan satış yok.

## Ölçütler
S0: 3 Oca – 2 Şub 2023 satış yok · S1: 3–10 Şub 2023 arası satış · S2: NAV ≥ 213,49 ·
S3: işlem ≤ 20 · S4: düşüş ≤ %11,67. Geliştirme kaydıdır, kanıt değildir.
