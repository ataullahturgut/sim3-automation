# TERAZİ v3.4: nadir olay güveni | Sonuç

2026-10-17. Ön kayıt `5a7884c`, kod `78a96e2`. Çıktılar: `KOSU_v3_4.txt`, `KOSU_v3_3_kontrol.txt`,
`TERAZI_V3_4_SONUC.json`, `TERAZI_V3_4_GUNLUK.json`, `TERAZI_V3_3_KONTROL_*.json`.
Kontrol: varsayılan mod v3.3'ü birebir üretti (213,49, 5 işlem). **Geliştirme kaydı, kanıt değil.**
Nedensellik testleri (S5) bu koşuda çalıştırılmadı.

| | v3.3 | v3.4 | ölçüt |
|---|---:|---:|---|
| 2 Şubat sonrası satış | 27 Şub | **10 Şub** | S1 geçti |
| net NAV | 213,49 | **178,99** | S2 (≥ 213,49) geçmedi |
| işlem | 5 | 19 | S3 (≤ 20) geçti |
| maks düşüş | %11,27 | %14,60 | S4 (≤ %11,67) geçmedi |

3 Şubat 2023: kırılma kanalı artık konuştu (Q 0,168, taban 0,066); Pe + 0,5·Ue = 0,399 < 0,5,
yani satış koşulu sağlandı. Satışı **makro onayı** engelledi (o gün reel faiz ve 2Y faiz
5 günde yükselmemişti). 6 Şubat'ta kanal yine sustu; satış 10 Şubat'ta geldi.

Ancak aynı değişiklik tüm dönemde 9 satış üretti; 9'unun 9'u daha pahalıya geri alındı
(−%0,85 ile −%5,86). Mayıs 2024'ten sonra işlem yok. **v3.4 başarısız (S2, S4).**

## v3.5 (ön kayıt eki 6, `59451bf`): COT kırılma kanalından çıkarıldı
`KOSU_v3_5.txt`, `TERAZI_V3_5_*.json`. Net NAV **205,54**, 13 işlem, düşüş %11,47.
S0 (3 Oca–2 Şub satış yok) **GEÇMEDİ**: Ocak'ta 4 satış (6, 18, 27, 31 Ocak), hepsi 1–3 gün
içinde daha pahalıya geri alındı. S1 geçti (6 Şubat'ta 1.878'den satış), S2 geçmedi, S3, S4 geçti.
2024'te satış yok. COT'u çıkarmak 2024 kayıplarını giderdi ama Ocak 2023 dalgalanmasını artırdı:
kırılma kanalı Ocak'taki küçük geri çekilmeleri (−0,5σ…−1σ) ve 3 Şubat düşüşünü (−1,97σ)
mevcut değişkenlerle ayırt edemiyor. Ayar taraması yapılmadı.
