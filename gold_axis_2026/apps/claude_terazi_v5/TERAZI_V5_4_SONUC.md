# TERAZİ v5.4: unutan referans | Sonuç

2026-10-17. Ön kayıt: `TERAZI_V5_4_ON_KAYIT_UNUTAN_REFERANS.md` (834d4eb).
Çıktılar: `KOSU_v54.txt`, `KOSU_v54_esik.txt`, `KOSU_v54_test.txt`, `V54_TESHIS.txt`,
`TERAZI_V5_SONUC_month_K2_relabel_v54.json`, `TERAZI_V5_4_ESIK_SONUC.json`, `V54_Z_SERISI_2021_2025.json`.
**2023–2025 geliştirme kaydıdır, kanıt değildir.**

## 1. Düzeltme amacına ulaştı (D geçti)

| yıl | v5.3 ort. z | v5.3 z<0 | **v5.4 ort. z** | **v5.4 z<0** |
|---|---:|---:|---:|---:|
| 2022 | −0,88 | %75 | +0,24 | %45 |
| 2023 | +0,22 | %43 | +0,42 | %40 |
| 2024 | +0,80 | %25 | +0,10 | %51 |
| 2025 | +1,66 | %6 | −0,20 | %58 |

Sinyal artık yukarı kaymıyor; her yıl satış bölgesine giriyor. Nedensellik testleri (V54=1): **8/8 OK**.

## 2. Ama satışlar zarar ettiriyor

**v5.4, sabit eşik (al > +0,5, sat < −0,5):** net NAV **109,29**, 30 işlem, düşüş %16,91,
uyum %47,9. G1, G3, G6 geçmedi; G2, G4, G5 geçti. **Başarısız.**

14 satıştan sonra geri alım (masraf dahil): **13 zarar, 1 başa baş, 0 kazanç.**
En pahalısı: 2025-04-07 sat 3.031 → 2025-09-01 al 3.477 (−%14,2).

**v5.4 + eşik öğrenme:** R = 3 ve R = 6 → 230,82 (1 işlem, hiç satmadı), R = 12 → 201,93.

Bu kez "hiç satma" artefakt değil, beraberlikten de gelmiyor. Her pencerede, en az bir kez
satan en iyi eşik hiç satmamaktan geride kaldı:

| kalibrasyon | hiç satma | gerçekten satan en iyi | fark |
|---|---:|---:|---:|
| 2023-07 | 108,9 | 103,9 | +5,0 |
| 2024-01 | 110,9 | 105,4 | +5,5 |
| 2024-07 | 119,8 | 110,2 | +9,6 |
| 2025-01 | 126,1 | 120,7 | +5,4 |
| 2025-07 | 137,2 | 124,9 | +12,3 |

## 3. 2022 kontrolü kötüleşti

| | 2022 NAV | işlem | maks düşüş |
|---|---:|---:|---:|
| v5.3 | 95,67 | 4 | %5,3 |
| **v5.4** | **98,07** | 1 | **%20,7** |
| al-tut | 98,07 | – | %20,7 |

v5.4, 2021'e göre kalibre olunca 2022'de de hiç satmadı. v5.3'ün 2022'deki iyi görünen
satışı kısmen kayan ölçünün yan etkisiydi (2022'de z %75 negatifti).

## 4. Sonuç

1. v5.3'teki "hiç satmama" **ölçü hatasından** geliyordu. Hata düzeltildi; D geçti.
2. Düzeltme, altta yatan gerçeği ortaya çıkardı: **bu modelin satış sinyali 2023–2025'te
   para kazandırmıyor.** Satış bölgesine girdiği 14 seferin hiçbirinde, sonraki geri alımdan
   daha pahalıya satmadı.
3. Dolayısıyla 230,82 sonucu (v5.3 ve v5.4 eşik öğrenme) modelin başarısı değildir; al-tut'tur.
4. v5.4 düzeltmesi geri alınmaz (ilkesel olarak doğru). v5.3 **dondurulmaz**.
