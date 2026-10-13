# ALTIN OCAK 2026 — YENİ HATADAN ÖĞRENME TURU, EVENT-HAZARD + DISTRESS-STATE TESTİ
**Tarih:** 2026-10-13. **Denetim statüsü:** araştırma, deneysel, 2026 Ocak geçmişte zaten görüldü ve **BAĞIMSIZ / DOKUNULMAMIŞ TEST DEĞİLDİR**. Önceden hazırlanmış 2026 olay manifestlerini bu turda okuyup sinyal çıkarmadık. PR #123 orijinal gün-gün AL/SAT/TUT ve PR #125 geçmiş model sonuçları değişmedi. Bu dal PR#125 üstüne yığılı (stacked research).
**İlk okuma:** `GOLD_JAN2026_RISK_HAZARD_V2_FROZEN_PROTOCOL_20261013.md`, `GOLD_JAN2026_RISK_V2_STAGE_D_FROZEN_ANOMALY_PROTOCOL_20261013.md`.
**Sabit temel S4:** önceki 60 tamamlanmış NY17 seans getirisi >=+2% ise AL, <=−2% ise SAT; sonraki ilk gözlenmiş M15 quote üzerinden işlem, tek yön %0,8 ücret, 5 seans reentry cooldown. 2023–25 EV Dukascopy BID/ASK midpoint, Jan2026 HistData close (farklı sağlayıcı); tüm kotasyonlar retro-elde edildi; banka ASK/BID değil. Ocak için Türkiye 09–17 işlem uygulanabilirliği ayrıca *spot-quote* duyarlılığıyla denetlendi.

## A. Önceki başarısızlıklardan öğrenilen gerçek kısıtlar
1. PR#123 Ocak: 29 Ocak NY17 kapanışı yalnız −%0,66 önceki güne göre; aynı NY17 seansında kronolojik zirve→sonraki dip −%8,90; 30 Ocak kapanışı −%9,07. B0 ve S4 gibi günlük kapanış trend kuralları erken SAT diyemedi.
2. PR#125 Stage A/C: sırf gün içi -%3/%4/%5 şok görüldüğünde otomatik satmak, Jan2026'da +%18–22 görünse de 2024 DEV'de kazancı düşürdü; yanlış alarmların %0,8 her çıkış/%0,8 yeniden giriş maliyeti var. Yalnızca Ocak sonuçlarına dönük bir eşik güvenilir değil.
3. 2023–25 için altınla aynı 15 dakikalık saatlerde doğrulanmış XAG/XPT/XPD paneli mevcut Neon şemasında bulunamadı. Günlük metal/risk verileri ayrıca 2026 sonradan yüklenmiş olduğu için gerçek Jan PIT girdi gibi kullanılmadı. Çapraz-metal senkronizasyon modeli **gerçekte denenmedi**. Veri olmadan varsayım yapma.
4. Farklı yıllarda %3 şokun ender olması: 2022–23 eğitim kümesinde ileri 3 seans içinde en az -%3 LOW ilk-geçiş y3 toplam 13/454. Bu, nadir olay sınıflandırması için oldukça düşük destek ve 2024/2025'te rejim dağılım kayması anlamına gelebilir.

## B. Stage V2: 2022–23'te eğitilmiş ileri 3-seans downside hazard logistic
Modelin **sekiz** tamamen t anında bilinebilen altın fiyat özelliği: r5/r20/r60, bugünün en yüksekten sonraki en düşük değerine gerilemesi, kapanışın gün içi en yüksekten uzaklığı, kapanışın gün içi aralıktaki konumu, şokun önceki 60 gün medyanına oranı, son 20 seans volatilitesi. Sadece **2022–23 eğitim**, %1/%99 kırpma ve ölçekleme de yalnız eğitim, L2=2 ridge-logit, önceden dondurulmuş satış eşiği `p>=max(.35,2×train prevalence)`. Model ileri 3 seans içinde bugünkü close'a göre low<=−3% ilk-geçişi tahmin etmeyi hedefledi.
- Eğitim **454 örnek**, pozitif oran **%2,8634**; eşik **0,35**.
- 2024 doğrulama: 259 örnekte 17 ileri-3seans ağır düşüş kaydı; **0 alarm**. Brier 0.06384, sabit train oranıyla 0.06270 (daha kötü).
- 2025 transfer: 255 etiketli örnekte 24 ağır düşüş; **0 alarm**. Brier 0.09007, sabit train oranı 0.08955 (daha kötü).
- 2026 Ocak önce görülmüş stres: 18 adet tam ufukla etiketlenebilir gün (Ocak28–30 3-gün sonrası Ocak içinde kalmadığından censored); **0 alarm**, 29 Ocak puanı **0,00207**, 30 Ocak puanı **0,00610**.
- **Bilimsel hüküm: REJECT otomatik SAT.** Daha önce seçilmiş modelden ileri risk tahmininde kanıtlanmış iyileşme değil. Tüm 2026 puanları hiçbir yeniden eğitim yapmadan raporlandı.

## C. Stage D: 2022–23 kaynaklı unsupervised distress-state / olağanüstü *halihazırdaki* fiyat kırılması algılayıcısı
Nedensel veya ileri risk tahmin modeli değildir. Tamamlanmış NY17 seansında:
`D=abs(ordered session high→subsequent low drop %)`,
`W=max(0,100×(session high-close)/session high)`,
`d0=median(previous 60 sessions D)`,
`w0=median(previous 60 sessions W)`; payda en az 0,1 yüzde puanı.
`A=sqrt((D/d0)^2+(W/w0)^2)`.
**Tek dondurulmuş alarm eşik** 2022–23 EV'nin gözlenen A skorlarının %99 persentili **5,737212**; 2024/25/Jan eşik seçiminde hiç kullanılmadı. Bu deney metodolojisinin kendisi zaten bilinen Jan başarısızlığından sonra önerildiği için Jan asla OOS sayılmaz.

**Sadece EV sağlayıcısından doğru yıl evreni (veri dosyasında önceden 2025 EV+HIST aynı yıla karışmış bir sayaç ayrıldı ve düzeltildi):**
| Yıl | Seans | Anomali alarmı | 3 seanslık y3 etkisi tam bilinen alarm | Sonraki ≥3% düşüşle eşleşen |
|---|---:|---:|---:|---:|
| 2022 eğitim | 198 | 2 | 2 | 0 |
| 2023 eğitim | 257 | 3 | 3 | 0 |
| 2024 transfer | 259 | 10 | 10 | 1 |
| 2025 transfer | 258 | 14 | 13 | 4 |
| Ocak 2026 HIST | 21 | 2 (29 ve 30 Ocak) | 0 (tam 3 gün Ocak içinde yok) | Y3 doğrulanamaz |
2024'te 9/10, 2025'te tam etiketli 9/13 alarmın ardından **≥3% sonraki üç-seans düşük fiyat şartı gerçekleşmedi**. Bu alarm **olağandışı fiyat bozulmasını tanır**, ileride düşüşün devam edeceğini güvenilir biçimde öngörmez.

**Jan29 gün içi gerçek ilk-eşik zamanı (ek süreklilik analizi, dondurulmuş Stage D end-session kararından FARKLI, yeni bir online kural olarak test edilmedi):**
- 2026-01-29 15:00 UTC bar başlangıcı / **15:15 UTC bar bitişi = 18:15 Türkiye**, model skor **7,855**, ordered high→subsequent low **−%4,132**; bu noktada 29 Ocak yakın tarihli yükselişi henüz bitmemişti ve 30 Ocak geleceği bilinmiyordu.
- 2026-01-29 15:15 UTC başlayan bar bitişinde **18:30 Türkiye**, ordered DD **−%8,899**.
- 29 Ocak 17:00 Türkiye banka alış/satış uygun penceresinin **ARDINDA** oluşan alarmdır. `NY17` gün sonu modelinin asıl kararı 30 Ocak 01:00 Türkiye civarına denk gelir. Bu yüzden 'bankadan 29 Ocak 16:45'te SAT'ı gördük' şeklinde iddia **YANLIŞTIR**.
- Haberi doğrulamadan şoku tek bir Fed/Warsh haberine atfetmek yanlış; Warsh açıklaması 30 Ocak tarihli ve 29 Ocak ilk uyarısının önceki sebebi sayılamaz.

## D. Bir risk alarmı otomatik SAT olunca ekonomik test
**S4 taban** vs **S4+StageD şokta SAT** (aynı gün NY17 sonunda, sonraki seansın ilk mid QUOTE kapanışından teorik icra, bankanın o saatlerde açık olduğu iddia edilmez):
| Yıl | S4 | S4+anomali | Kazanç etkisi |
|---|---:|---:|---:|
| 2023 | +%6.00 | +%7.85 | +1.86 puan |
| 2024 | +%15.09 | +%4.87 | **−10.22 puan** |
| 2025 | +%41.17 | +%26.34 | **−14.83 puan** |
| Ocak2026 daha önce görülmüş | +%10.15 | +%22.09 | +11.94 puan |
2024 StageD 16 ücretli emirle ≤12 işlem kabul sınırını da aştı; maksimum kapanış-bazlı portföy drawdown -%8.05→**-%10.96** kötüleşti. 2025 18 ücretli emirle maliyet şişti. Böylece iki yıllık kabul ölçütleri de **kesinlikle FAIL**. **RİSK İNCELEME etiketi bilimsel olarak savunulabilir; SAT yetkisi bilimsel olarak savunulamaz.** 2026 Jan +%22.09, kötü tarihsel sonuçları geçersiz kılmaz.

## E. Kritik fark: 24 saat spot fiyatı ile gerçek banka işlem saati
StageD/S4 +%22.09 Ocak sonucu M15 spot **2:00 Türkiye** civarındaki ilk yeni seans alım/satım fiyatlarını varsayıyor (bankada uygulanabilir olduğu ispatlı değil). Jan29 akşam 18:15TR alarmı bankanın normal 09–17 düşük-makas zamanından sonra geldi. İlk sonraki banka saatini taklit etmek için bağımsız HistData M15 spot kotasyonları:
- 5 Ocak 09:15TR 'AL' end15m quote **4417.869** USD/ons (ilk S4 sinyali Jan2 gece; bu eşdeğer bank BUY fiyatı değildir).
- 30 Ocak 09:15TR 'SAT' end15m quote **5190.295** USD/ons (Jan29 akşam risk sonrası; aynı gerçek banka BID fiyatı değildir).
- 30 Ocak 17:00TR end15m quote **5018.965** USD/ons (hiç satış yapmayıp son saatte teorik tasfiye karşılaştırması).
- **Her alım/satış %0.8 sabit maliyet** (gerçek banka makası, likidite ve kotasyon farkı bilinmiyor): Ocak başı hipotetik 09:15 alıp 30 Ocak 09:15 satarak yaklaşık **+%15.612**; aynı alımı 30 Ocak 17:00'ye dek altın tutup o saatte satarsak **+%11.796**. Bunlar yalnızca altın spot quote farkı ve sabit %0.8 iki yön maliyetli **örneklem-içi karşı-olgusal işlem saatleri**, gerçek banka hesabındaki fill değildir. Alarmın gerçekten 17:00TR'den ÖNCE verilmiş olduğu varsayılamaz; değildi. Ocak dışı yıllarda bu maliyetli zaman rejiminin başarısı ayrıca sınanmadan pozisyon kararı **onaylanmaz**.

## F. Literatür ve tekrar üretilebilirlik
- Üç-seans outcome etiketleri örtüşür; bağımsız Bernoulli işlemleri gibi %95 güvene abartılı çıkarım yapılmadı. Sabit tarihli yıl/kontrol blokları kullanıldı, fakat tam aylık blok bootstrap henüz çalıştırılmadı. Gerekirse purging/embargo ve event-cluster dependence uygulanmalı. https://python.financial/concepts/purged-cross-validation/
- David Bailey vd., *The Probability of Backtest Overfitting*, J Computational Finance (2017), DOI 10.21314/JCF.2016.322; tekrar tekrar Jan geçmişi üzerinden model uydurma bilimsel alfanın aşırı tahminidir. https://escholarship.org/uc/item/4w1110bb
- Data/artefaktlar `GOLD_JAN2026_RISK_HAZARD_V2_HISTORICAL_VENDOR_SAFE_PANEL_20261013.csv` (1,160 origin-safe ratios, no raw vendor spot values), `GOLD_JAN2026_RISK_HAZARD_V2_TRAINED_LOGIT_AND_RESULTS_20261013.json` (train mean, clipped ranges, 8 coefficient, event results), `GOLD_JAN2026_RISK_V2_STAGE_D_CALIBRATION_ALERTS_AND_BACKTEST_20261013.json` (FIXED EV-only year rates, alert episode controls, 4-year strategy full actions, first Jan29 time), `GOLD_JAN2026_RISK_V2_BANK_0915TR_EXECUTION_SENSITIVITY_20261013.json` (TR clock falsification).
- Independent third-party PIT original source timestamps, 2023–25 synchronous 15m multi-metal, bank bid/ask quote logs, and original 2026 news firstprint NOT provided. No trader should use these candidate outputs as an investment recommendation.

## G. Status & next scientific research gate
- **S4**: a less frequently trading exploratory trend comparator, NOT validated positive excess return vs passive buyhold. Jan29/30 crisis weakness remains.
- **Logistic future-risk**: rejected (2024/2025 Brier worse than simple training-rate, zero alerts).
- **Anomaly-state detector**: candidate **risk WATCH / REVIEW**, not directional forecast; identified Jan29 unusual conditions after Turkish bank low-spread hours; because huge false alarm burden, *no automatic liquidation*.
- **S4+anomaly auto SELL**: explicitly rejected by 2024 and 2025 false alarms and bank clock.
- **Next valid development**: obtain 2020–25 PIT-correct synchronous XAU/XAG and futures order book, intraday dollar/US10Y risk and firstprint UTC catalyst records; compare real 09:00–17:00TR available intraday state and no-shock control; use cross-year nonoverlap episodes, realistic bank spread. No reason to scan further Jan2026 parameter grids; we have documented failure and a testable data-acquisition hypothesis.
