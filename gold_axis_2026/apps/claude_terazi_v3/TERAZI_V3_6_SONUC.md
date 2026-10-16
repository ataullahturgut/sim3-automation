# TERAZİ v3.6: birikimli kanıt (CUSUM) | Sonuç — BAŞARISIZ

Ön kayıt `12e050b`. Kod `karar_v36.py`, çıktı `KOSU_v3_6.txt`, `TERAZI_V3_6_SONUC.json`.
Net NAV **182,30**, 29 işlem, düşüş %20,49. S0, S2, S3, S4 geçmedi; S1 geçti (9 Şub).

Neden: kırılma kanalının Q'su yükselen piyasada sakin günlerde de taban oranın (0,066) üstünde
(Ocak 2023'te 0,06–0,13); birikim neredeyse her gün artıyor ve Ocak'ta iki kez eşiği geçiyor.
Daha önemlisi Q, Ocak geri çekilmelerini 3 Şubat'tan ayırmıyor:

| gün | altın günlük | Q |
|---|---:|---:|
| 18 Oca | −%0,7 | 0,120 |
| 27 Oca | −%1,2 | 0,128 |
| 31 Oca | −%0,7 | 0,117 |
| **3 Şub** | **−%1,9** | **0,131** |

Hangi karar kuralı kurulursa kurulsun, bu girdiyle Ocak'ta satmayıp 3 Şubat'ta satmak mümkün
değil: sorun karar katmanında değil, kırılma kanalının ürettiği sinyalde.
