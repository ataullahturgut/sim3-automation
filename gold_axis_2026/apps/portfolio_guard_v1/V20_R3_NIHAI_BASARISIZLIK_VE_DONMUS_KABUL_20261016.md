# V20 KAVİS–ATLAS R3 — SONUÇ: ÖN KAYIT KABULÜNDEN RED / FAIL

**Tarih:** 16 Ekim 2026. **Dal:** research-gold-v20-r3-gate-calibration-20261016. **Draft PR:** #140.
**İlk commit:** 3c04badbf14c8aede2a5e4b3d1e1bc866af88134 — YALNIZ `V20_R3_PREREG.md`, koddan önce.
**Eşik kalibrasyonu lock commit:** aa70eff508ae01fea5f498d3ce38c884b0e67b74.
**Asıl kabul testi:** GitHub Actions run 38897049697; bilimsel kabul step FAIL kasıtlıdır. Teknik/sözleşme step PASS.

## Ön kayıt parametreleri ve metodoloji
riskMode=alert only (constrained R4 için ayrı prereg), shadowGate=off/gated risk modundan bağımsız, lambda=eta=0.
16 kabul edilmiş banka kontrol noktasından bir tamamlanmış blok, 8 blok minimum kanıt, iki başarılı blok üst üste açılma, t<0 veya son iki blok toplamı negatifse kapanma. `T_OPEN=1.9` 500 ayrı drift-sıfır kalibrasyon tohumundan, 2 ücret katmanından (0.8%,2.5%) seçildi: 24/500 (%4.8) kalibrasyon yanlış açılma. Eşik, testten önce JSON lock'a donduruldu. Sonraki sonuçlar eşik seçimini değiştirmedi.

## Teknik kabul — BAŞARILI
- Yeni R3 testleri 11/11, R2 12/12, V15–V20 139/139. Toplam 162/162 PASS.
- Eski 128 kurgusal dünyada shadowGate=off, V18 ile sayısal NAV parity denetimi PASS.
- R3 iki ayrı ücreti ödenmiş tam gölge sanal portföyü tutar. Kapı, 16'lık tamamlanmış blokların yalnız SONRAKİ sinyali etkiler.
- Kabul edilmiş kotasyondan sonra aktif kapıda gerçek CASH/GOLD pozisyonunun gölge uzmanın hedef pozisyonuna eşlenmesi 0 hata.
- Restore sahte `lastEvidence`/`confirmedStreak`/`gateOpen` değerlerini şeffaf geçiş geçmişinden yeniden türetir ve bozuk tescil edilmiş karşı-olgusal fiyat getirisi/sayaçları reddeder.
- Her tür canlı banka emri yoktur, tarihsel gerçek altın fiyatına bağlanmaz.

## Yeni 200 sıfır-drift yolunun ön kayıtlı kabul testi — BAŞARISIZ
Her tohum (200000+53*i; i=0..199), her iki banka maliyetiyle 300 kontrol noktası; yanlış alarm, her iki ücret yolundan herhangi birinde bir kez kapının açılmasıdır.
- **15/200 = %7.5** yanlış açılma; sınır <=%5. Wilson %95 interval [4.597%,12.004%]. Bu CI 5%'i kapsasa da önceden belirlenen *gözlenen hata oranı* kriteri başarısızdır.
- Null ortalama aday−V18 sermaye farkı **−0.152824 USD**; sınır >=−0.10 USD. BAŞARISIZ.

## Önceden kayıtlı altı senaryo ailesi (32 tohum aile başına x 2 ücret)
| Aile | R3 − V18 ortalama farkı USD |
|---|---:|
| Sıfır drift | −0.304213 |
| Ortalamaya dönüş | +0.092202 |
| Kalıcı trend (UP/DOWN dengeli) | **−1.134769** |
| Trend ↔ yatay rejim | −0.013915 |
| Fat-tail/gap sıçramaları | −0.247326 |
| Volatilite değişimi | +0.671551 |

En kötü aile kalıcı trend: −1.134769 USD; kabul >=−1 USD olduğu için BAŞARISIZ.
En büyük üç pozitif kazancın, tüm pozitif kazanca katkısı **%96.8919**; sınır <=%40: BAŞARISIZ. Toplam pozitif katkı 50.1018 USD; sonuç birkaç kazanca aşırı duyarlı.
384 aile/ücret senaryosu toplam ortalama son NAV: V18 **169.812663 USD**, R3 **169.656584 USD**. R3 **113 gerçek uzman müdahalesi** yaptı; ortalama üstünlük üretemedi.
En kötü R3 final **43.74699 USD**, ortalama maksimum drawdown %21.0221, nakdi yenebilen senaryo sayısı 205/384, pasif altını geçen 141/384. Bunların hiçbiri gerçek yatırım kârlılık kanıtı değildir.

## Ön kayıt kabul vektörü
- Yanlış açılma <=5%: FAIL.
- Null ortalama fark >=−0.10: FAIL.
- Mean-reversion ortalama fark >=−0.10: PASS.
- Her aile ortalama >=−1 USD: FAIL (persistent_trend).
- Top3 pozitif kazanç payı <=40%: FAIL.
- Aynı bankanın kabul ettiği gölge/gerçek pozisyonların uyumu: PASS.
- Özgün V18 korunmuş default ve 128 eski dünyada parity: PASS.
- R3 riskMode alert-only ve hard DD garantisi yok: PASS.

## Nihai bilimsel karar ve korunacak sınırlar
**R3 KABUL EDİLMEDİ, ÜRETİME/LIVE TRADING'E TERFİ EDİLEMEZ.** R2 ve V18 bozulmadı. Kalibrasyon eşikleri, z, blok uzunluğu, seed veya karar katsayıları sonuçtan sonra yeniden taranmadı. R3 başarısız olduğu halde araştırma dalı/prereg/test/artifact saklandı.
Kalibrasyon modelini düzeltmek için ileride yeni hipotez gerekiyorsa ayrı isimli R4 ön kayıt ve önceden kararlaştırılmış yeni dönem/seed gerekir. Yeniden ayarladığımız aynı 200 ve 384 set kör test sayılmaz.
Bu model gerçek XAU/USD ilk yayın zamanı, gerçek banka bid/ask, fon-transfer süresi, işlem penceresi ve bağımsız tarihsel ileri dönemden yoksundur.