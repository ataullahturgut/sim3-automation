# OCAK 2026 — 3. Bilimsel yineleme: Türkiye banka saati, şok-alarmı ve yanlış alarmlar
**Araştırma tarihi:** 13 Ekim 2026. **Statü:** deneysel / Ocak sonucu önceden bilinen geriye dönük araştırma. Bu turda 2026 olay manifesti okunmadı. Tüm Ocak 2026 önceki sohbetlerde araştırıldığı için 2026 Ocak verisine bakılmadan kural yayımlanmış olsa bile *bağımsız gelecek doğrulaması değildir*.

**Ana manifest:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`. İlgili PR #123 günlük eski replay; PR #125 yavaş S4, reddedilen günlük çöküş çıkışları; PR #126 2022/23 logit ve gün sonu yanlış alarm testleri. Bu araştırma yeni stacked branch `research-gold-jan26-bank-hour-sequential-v3-20261013` içinde; önceki çalışmaları veya işlem sistemini değiştirmez.

## I. Önce ne öğrendik, hangi hatayı değiştirdik?
- PR#123/B0 NY17 gün sonu SAT = Türkiye ertesi gün yaklaşık 01:00: **bankanın 09–17 düşük makas penceresiyle uyumsuz**.
- PR#126 29 Ocak NY17 anomali ilk net 18:15 Türkiye; 17:00 sonrası, bankada kullanılır ileri-satış iddiası doğru değil.
- Altın günlük kapanış getirisindeki güçlü yükseliş 29 Ocak'taki gün içi fiyat bozulmasını maskeleyebilir. Ancak tek bir çöküş örneğinden otomatik satış üretmek 2024/25'te maliyetli yanlış alarm yaratmıştır.
- As-of olmayan tarihli metal/haber verisi tahmin girdisi değildir; 2023–25 senkron XAG/Pt/Pd 15m veri yok; bu döneme ilişkin ilişkileri uydurmadık.

## II. Yeni gerçek zaman sözleşmesi (ilk hesaplamadan önce donduruldu)
`GOLD_JAN2026_BANK_HOURS_V3_FROZEN_EXPERIMENT_PROTOCOL_20261013.md`: **16:30 Türkiye** itibarıyla yalnızca 09:00–16:30 arası tamamlanmış 15 dakikalık altın fiyat ve önceki günler. Aynı gün sonraki 16:30–16:45 barın ilk OPEN spot kotasyonundan *teorik* emir. İkinci ve daha temkinli deneyde **16:45 Türkiye'de tamamlanan barın son fiyatıyla** teorik icra. Yerel banka BID/ASK ve fiili işlem/komisyon tahsilatı yok. Alış/satış için kullanıcıdan alınan %0,8 her bir yönde komisyon; banka makası ve ek fiyat kayması 0/0,15/0,30% ayrı denendi.
- 2022/23 EV 15m bank-saatli şok eğitim eşikleri; 2024 ve 2025 EV kaynaklı yıl bazlı kabul; 2026 Ocak HIST fiyatla daha önce görülmüş stres.
- B0_BANK: orijinal kısa dönem 3/5/20 seans + SMA10 AL/SAT, sabit.
- S4_BANK: 60 bank-seans getirisi >=2% AL / <=-2% SAT, 5 bank-günlük yeniden giriş ertelemesi.
- **A (anomali):** o gün 09–16:30 altın high→sonraki low ve kapanışın gün içi yüksekten uzaklığı, tamamen geçmiş 60 bank günündeki medyanlara bölünüp birleştirildi; yalnız 2022/23 **99. persentil = 5,62713** kesimi.
- **T (aşırı yükseliş):** son 5 bank seansının yükseliş getirisi / önceki 60 seans günlük volatilitesi ve √5; yalnız 2022/23 pozitif değerlerinin **99. persentil = 2,98059** kesimi.
- Her biri ayrı WATCH; yalnız iki rakip deney, WATCH iken GOLD pozisyonunda bile **SAT** varsayımı; ne yıllık ne aylık geleceğe bakışla eşik değiştirilmedi.
- Her iki WATCH'tan gelecek 1 bank seansında saat09–16:30 tamamlanmış XAU LOW <= bugünkü16:30 cutoff spot -2% hedefi ayrıca ayrı değerlendirildi. End-of-period açık altın pozisyonuna varsayımsal tasfiye maliyeti uygulanır, gerçek satıldı denmez.

## III. 2023–2025 gerçekten ne oldu? (16:30 karar / teorik anlık sonraki spot OPEN, iki yön .8% ücret)
| Yıl | B0 BANK | S4 BANK | S4+A SAT | S4+T SAT | Sürekli altın tut |
|---|---:|---:|---:|---:|---:|
| 2023 | -13.73% | 7.38% | 5.22% | 3.11% | 10.53% |
| 2024 | -8.42% | 23.91% | 11.31% | 21.80% | 24.44% |
| 2025 | 13.61% | 41.73% | 30.08% | 40.55% | 61.31% |
| Jan2026 önce görülmüş | 11.47% | 13.05% | 24.17% | 24.17% | 13.05% |

**Yıl bazlı sıkı kabul testi FAIL (iki deney için de)**. 2024 A: 5 sinyal ve ileri 1 banka seansı -2% hedefine *0 eşleşme*; 2025 A: 14 sinyal, 7 eşleşme ama çok yanlış alarm ve geri alım. 2024 S4 + A autoSAT S4'e göre **−12,60 getiri puanı**; 2025 **−11,65 puan**; emir 2024 12 adet, 2025 22 adet. 2024 T: 2 sinyal/0 eşleşme; 2025 T 4 sinyal/2 eşleşme. T autoSAT yıllık sırasıyla S4'e göre **−2,10** ve **−1,18** puan. Yanlış çıkışın fırsat maliyeti ile %0,8 satış+geri alış komisyonu, riski tanımanın kârlı satış olduğunu kanıtlamadığını gösterir.

S4 düşük işlemli referans, fakat 2023–25 aynı bank16:30 evrende sürekli altın tutmanın getirisini geçmedi. Gerçek banka makası dahil değil.

## IV. Ocak 2026, her gün aynı kurallarla kayıt
`S4_BANK` sütununda karar, diğer iki uyarı sütununda hangi gün risk WATCH oluştuğu gösterilir. Banka saati cutoff **16:30 TRT**. Hesap kayıtları `GOLD_JAN2026_BANK_HOURS_V3_CROSSYEAR_RESULTS_20261013.json`.

| Tarih | 16:30 XAU/USD mid ($) | S4 kararı | A anomali | T aşırı yükseliş | Olası birleşik davranış |
|---|---:|---|---|---|---|
| 2026-01-01 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-02 | 4.374,3 | AL | — | — | S4 AL |
| 2026-01-03 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-04 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-05 | 4.399,4 | TUT altın | — | — | Değişiklik yok |
| 2026-01-06 | 4.458,8 | TUT altın | — | — | Değişiklik yok |
| 2026-01-07 | 4.441,9 | TUT altın | — | — | Değişiklik yok |
| 2026-01-08 | 4.434,0 | TUT altın | — | — | Değişiklik yok |
| 2026-01-09 | 4.472,2 | TUT altın | — | — | Değişiklik yok |
| 2026-01-10 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-11 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-12 | 4.604,6 | TUT altın | — | — | Değişiklik yok |
| 2026-01-13 | 4.600,2 | TUT altın | — | — | Değişiklik yok |
| 2026-01-14 | 4.631,2 | TUT altın | — | — | Değişiklik yok |
| 2026-01-15 | 4.605,2 | TUT altın | — | — | Değişiklik yok |
| 2026-01-16 | 4.586,6 | TUT altın | — | — | Değişiklik yok |
| 2026-01-17 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-18 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-19 | 4.671,6 | TUT altın | — | — | Değişiklik yok |
| 2026-01-20 | 4.719,1 | TUT altın | — | — | Değişiklik yok |
| 2026-01-21 | 4.867,8 | TUT altın | — | — | Değişiklik yok |
| 2026-01-22 | 4.827,0 | TUT altın | — | — | Değişiklik yok |
| 2026-01-23 | 4.931,1 | TUT altın | — | — | Değişiklik yok |
| 2026-01-24 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-25 | — | TUT / seans yok | — | — | İşlem yok |
| 2026-01-26 | 5.071,3 | TUT altın | — | — | Değişiklik yok |
| 2026-01-27 | 5.080,7 | TUT altın | — | — | Değişiklik yok |
| 2026-01-28 | 5.281,1 | TUT altın | — | — | Değişiklik yok |
| 2026-01-29 | 5.519,5 | TUT altın | UYARI | UYARI | SAT (anomali) |
| 2026-01-30 | 5.024,9 | TUT altın | UYARI | — | Eski model SAT |
| 2026-01-31 | — | TUT / seans yok | — | — | İşlem yok |

**29 Ocak 16:30 veri örneği:** gün içi 09–16:30 fiyat düşüşü **-2.229%**, bank16:30 tamamlanmış 5 seans trend **+14.346%**, 20 seans trend **+27.529%**, 60 seans trend **+38.555%**. A skoru **6.8373** >5.6271; T skoru **4.5966** >2.9806. Buna rağmen S4 BANK tek başına **TUT ALTIN**; anomali veya aşırılık gözlemiyle otomatik SAT deneyleri **29 Ocak16:30 sonrası** teorik spot kotasyonundan altını boşaltır. 30 Ocak olay/satış sonrası bilinen veri, 29 Ocak model girdisine konulmadı.

30 Ocak **16:30 XAU spot $5024.908**; 29 Ocak 16:30 XAU spot $5519.485; fark sonraki gün ağır kayıp. Ertesi günkü Warsh vb. 30 Ocak haberleri 29 Ocak risk skorunu üretmekte kullanılmadı.

## V. Daha temkinli 16:45 teorik icra ve ek maliyet
Denetim `GOLD_JAN2026_BANK_HOURS_V3_DELAYED_FILL_SENSITIVITY_PROTOCOL_20261013.md` hesaplanmadan önce donduruldu. Gerçek spot 16:45 kapanışında işlem varsayımı; maliyet her AL/SAT %0,8 + ek 0,15% veya 0,30% her işlem yönüne.
| Jan2026 deney | 0 ek kayma | +%0,15 her yön | +%0,30 her yön |
|---|---:|---:|---:|
| B0 Bank | +11.82% | +11.49% | +11.15% |
| S4 Bank | +13.37% | +13.04% | +12.70% |
| S4 + A | +24.36% | +23.99% | +23.62% |
| S4 + T | +24.36% | +23.99% | +23.62% |

**2024/25 kabul testi 16:45 gecikmeli senaryoda da FAIL.** 20 model/yıl üzerinden normalize fiyatlardan alternatif hesap ile orijinal 16:30 spot OPEN getiri hesaplarını yeniden ürettim; en büyük mutlak fark 0, yani portföy aritmetiği bu girdi seti için teyit edildi. Ancak bağımsız banka BID/ASK ve tarihsel kotasyon saatleri doğrulanmadı; burada "16:45 spot" kullanımı bir emir uygulandığını ispatlamaz.

## VI. Ek yöntem denetimi: OHLC içi sıra kanıtlanamaz
İlk yöntemde aynı 15 dakikalık barın HIGH ve LOW fiyatlarını kronolojik varsayma sakıncası vardı. Önceden kayıtlı QC protokolü uyarınca muhafazakâr alternatifte ancak bir **önceki tamamlanmış bardaki HIGH** takip eden LOW ile eşleşir. 2022–25 EV 1.032 bank gününün 97'sinde orijinal orderedDD ile fark oluştu, azami **0,9605 yüzde puan**. 2026 Jan HIST 108 bank gününün 5'inde, azami **0,0552 yüzde puan**. 2022–23'ten yeniden eğitilmiş strict-q99 eşiği **5.67682** ve 29 Ocak skoru **6.83729**, hala üstünde: **29 Ocak 16:30 risk WATCH tanısı bar sıralaması varsayımıyla ortadan kalkmadı**. QC, bu uyarıya yetki kazandırmaz; geçmiş yanlış alarmlar sürdü.

## VII. Açık bilimsel sınırlılıklar ve karar
- **Ocak özelinde olumlu sonuç, 2024/25 negatif zaman-karşılaştırmasını geçersiz kılamaz**. Otomatik SAT çıkış stratejisi TERFİ EDİLMEYECEK.
- Değerlendirme 2026 fiyatlarının 2026 ekiminde önceden görülmüş olmasına dayanır; en basit iki alarm ailesi bile Ocak yüzünden hipotez seçimi sapması taşıyabilir. Giriş/çıkış kuralını canlıya alabilmek için *gerçek görülmemiş ayrı dönem* gerekir.
- Aynı bar 16:30 close -> 16:30 next bar OPEN emir yerleştirme sıfıra yakın uygulama gecikmesi farz ediyor. 16:45 gecikmeli duyarlılık bunu azaltıyor ama gerçek banka quote ve broker saatlerini doğrulamıyor.
- Sabit %0,8 kullanıcı bankasından öğrenilmiş varsayım, gerçek XAU/USD/gram/sertifika dönüşümlerinin spread ve kur maliyeti eksik; tüm getiri rakamları *spot XAU teorik USD indeks getirisi*, TL sonuç değildir.
- 2023–25 senkron gümüş/platin/paladyum M15 olmadığı için çapraz metaller bu deneyde yer almadı; 2026 ilk yayın UTC'leri denetlenmemiş haber PIT kolonu da yok. Bir olay zinciri keşfedilmiş/kanıtlanmış değildir.
- **Olumlu araştırma:** 29 Ocak 16:30 Türkiye'de, büyük akşam çöküşünden ÖNCE bağımsız 2022/23 fiyat eşiğiyle risk durumunun iki farklı ölçümü yükseldi. Bu yalnızca bir sonraki bilimsel araştırma için *olay adayı / risk review*; otomatik SAT teyidi yok.
- **Bilimsel nihai karar:** mevcut S4 düşük işlemli deneysel karşılaştırma modeline devam; hiçbir yeni uyarıya otomatik SAT hakkı verme; önce PIT cross-metal ve banka BID/ASK + likidite spread ve gerçek out-of-time eksenini tamamla.

## VIII. Dosyalar
- `GOLD_JAN2026_BANK_HOURS_V3_FROZEN_EXPERIMENT_PROTOCOL_20261013.md`
- `GOLD_JAN2026_BANK_HOURS_V3_NORMALIZED_1630TR_ASOF_PANEL_20261013.csv` (1.140 araştırma banka günü)
- `GOLD_JAN2026_BANK_HOURS_V3_CROSSYEAR_RESULTS_20261013.json` (train eşikleri, 2022–2025 false-alarm kontrolü, 2026 Ocak gün gün kararlar)
- `GOLD_JAN2026_BANK_HOURS_V3_DELAYED_FILL_SENSITIVITY_PROTOCOL_20261013.md`
- `GOLD_JAN2026_BANK_HOURS_V3_1645_FILL_RATIO_20261013.csv`
- `GOLD_JAN2026_BANK_HOURS_V3_DELAYED_1645_FILL_AND_SLIPPAGE_RESULTS_20261013.json`
- `GOLD_JAN2026_BANK_HOURS_V3_INTRABAR_ORDER_QC_PROTOCOL_20261013.md`
- `GOLD_JAN2026_BANK_HOURS_V3_STRICT_PRIORBAR_DD_QC_20261013.csv`
- `GOLD_JAN2026_BANK_HOURS_V3_STRICT_PRIORBAR_ANOMALY_QC_RESULTS_20261013.json`.
