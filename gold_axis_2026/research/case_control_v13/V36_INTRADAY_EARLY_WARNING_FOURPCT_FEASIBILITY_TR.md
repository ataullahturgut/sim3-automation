# V36 — %4 altın düşüşleri öncesinde saatlik ve dört saatlik XAU anomali araştırması

**30 Ekim 2026, retrospektif araştırma.** Orijinal BASE14/CFTC21/V22 **değişmedi**. Yeni AL/SAT, canlı uyarı, üretim veri yazımı **yok**.

## Kaynaklar ve gerçek kapsam

Neon Gold Control / public:
- \`gold_research_histdata_xau15m_candidate\` — 156.366 satır, 2020–2026-10-01; 2024–2025 eşik eğitimi ve 2026 bağımsız yıl sonucu için **aynı upstream HistData**. 2024 kaynak blob ailesi ayrı, 2025–2026 kaynak blob ailesi ayrıdır; \`EST_FIXED_UTC_MINUS_05\` saat tanımı, \`HISTORICAL_INDEPENDENT_SOURCE_CANDIDATE_NOT_CANONICAL\`; 2026 Eylül barları **8 Ekim 2026'da geriye dönük alınmıştır**.
- \`gold_research_dukascopy_2026_direct_m1_m15_bidask_v2\` — 17.184 XAU/USD 15dk BID/ASK bar, Ocak–7 Ekim 2026; \`2026-10-08_RETRIEVED_HISTORICAL_NOT_PIT\`; Mayıs-Haziran-Eylül teyidi için **ayrı bağımsız fiyat kontrolü**, eşik eğitimi için karıştırılmadı.
- \`xau_intraday_research_cache_1m\` — 1.330.943, son Haziran 2026; \`xau_intraday_research_cache_5m\` — 482.734, son Ağustos 2026. Twelve Data cache indirmeleri **8 Eylül 2026**, Eylül 1dk/5dk için ileri sürülemez. 1dk Haziran kısmen kota nedeniyle eksik.
- Neon'da karşılaştırılabilir eşzamanlı XAG/XPT/XPD dakika/15dk tablosu **henüz doğrulanmadı**. StakTrakr dört metal günlük verisi, bu 15dk XAU tek-metal testinin yerini tutmaz.

**Önemli:** Aynı gerçek piyasa hareketini HistData ve Dukascopy yakın büyüklükte doğruluyor; ancak gün içi fiyat barlarının raporlanan saatinde **yaklaşık 1 saatlik kaynak ofseti farkı** görüldü. Herhangi bir canlı dakika bazlı alarm zamanı iddia edilmeden önce timestamp normalizasyonu ve bar-available semantics ayrı doğrulanmalıdır.

## Araştırma sorusu ve hesap yöntemi

- **Hedef:** Bir tarihteki son XAU fiyatından sonraki *beş fiyat işlem günü* içindeki en düşük gün sonu fiyatına kadar **≤-%4**.
- 15dk veriyle, mevcut/past kapanışları kullanarak **1 saatlik (4 bar)** ve **4 saatlik (16 bar)** yüzde değişim hesaplanır. Gecelik/hafta sonu kesintileri 4/16 bar sanılmaz: tam zaman farkı zorunlu.
- Günlük özet \`min(1h return)\`, \`min(4h return)\` yalnız o günün sonuna kadar bilinebilecek değerlerdir. Sonraki fiyatlar **yalnız sonuç ölçümü** içindir.
- **Eşikler yalnızca 2024–2025 HistData** günlük minimum dönüşlerinin en alt %5'inden alındı: 1h ≤ **-%1,174**, 4h ≤ **-%1,7952**. 2026'ya özel eşik optimize edilmedi. Historik fiyat PIT olmadığı için yine de gerçek prospektif sertifikasyon yok.
- Bu eşikler karar tavsiyesi değil; \`RESEARCH_SHADOW\` olarak araştırma amaçlı anomalilerin sınıflanmasıdır. Özellikle anomali tespitinin \`warning\` diye görülmesi, sonradan %4 düşüşü *önceden bildiğini* kanıtlamaz.
- V22 ile ortak araştırmada \`BASE14 RED/YELLOW\` ve V22 öncelikli uyarı iki ayrı katman olarak korunmalıdır; **aynı günün tamamlanmış BASE14 kaydı gün içi geçmiş barlara geriye dönük taşınamaz**.

## Önce kaçırılmış 3 düşüşte asıl bulgu

| Düşüş dönemi | Önceki 10 işlem günündeki önemli XAU intraday fiyat anomalisi | Eşik durumu |
|---|---|---|
| **13–20 Mayıs, -%4,11** | Öncesinde 1h/4h aşırı düşüş bulunmadı | İki eşikle de **erken işaret yok** |
| **4–11 Haziran, -%8,08** | **27 Mayıs: 4h -%1,897; 28 Mayıs: 4h -%1,883** | 4h alt %5 eşiği aşıldı, Haziran 4 zirvesinden **6 ve 5 fiyat günü önce** |
| **21–28 Eylül, -%4,49** | **16 Eylül: 1h -%2,208; 4h -%2,309** | İki eşik de aşıldı; 21 Eylül başlangıcından **3 fiyat günü önce** |

Dukascopy bağımsız kontrol: 16 Eylül worst1h **-%2,252**; HistData **-%2,208**. 5 Haziran worst1h yaklaşık **-%1,429/-1,430** fakat **4 Haziran sonrası**; Haziran ilk düşüşün öncü başarısı sayılamaz. 27 Mayıs bağımsız veri worst1h yaklaşık **-%1,118**, dört saatlik olağandışı hareket daha belirgindir.

**Sinyal türü ayrımı:** Mayıs ve Haziran öncesinde BASE14 zaman zaman YELLOW olsa da V22 ACTIVE doğmamıştı. Eylül'de 11/14/15/17 Eylül BASE14 RED olup V22 \`ORIGINAL_RED_REVIEW_ONLY\` yapmıştı. 16 Eylül 1h/4h fiyat anomalisi, Eylül'de bu orijinal riskin ek bağlamı olarak anlamlı bir **araştırma adayıdır**.

## False alarm ve veri sızıntısı denetimi

**Yalnızca HistData 2026 test, 2024–2025 eşik öğrenme.** Takvimde fiyat kapsaması tam ve beş sonraki fiyat günü bulunan **187** 2026 araştırma gününde **35** gün %4/5g hedefi taşıyor. Bunlar bağımsız 35 büyük çöküş **değildir**.

| Sabit intraday araştırma koşulu | Uyarı günü | Sonraki 5g %4 ile eşleşen | Sonraki 5g %4 görülmeyen |
|---|---:|---:|---:|
| 1h anomali | 37 | 9 | **28** |
| 4h anomali | 29 | 9 | **20** |
| 1h veya 4h | 42 | 11 | **31** |

**Karar:** Bu sonuçlar tek başına bir intraday-anomali sisteminin V22'den daha iyi olduğunu **göstermiyor**. Büyük hareket başladıktan sonra oluşan anomaliler de eşleşebilir. Sonuçsuz uyarı oranı yüksek. Geleceğin 2026 sonuçlarına bakarak yeni parametre belirlemek bilimsel olmaz.

## Düşüş sinyali güçlendirme kararı — üretim değişikliği yok

1. **Günlük V22 dursun.** Ayrı araştırma şeridinde \`XAU_INTRADAY_WATCH_RESEARCH\` üret: ilk kez fiyat 1h/4h olağandışı eşik altına düştüğünde, kapanan barın kendi zamanından +15dk olası kullanıma hazır zamanı belirtilsin.
2. **Üç aşama:** \`erken kırılganlık\` (günlük BASE14/CFTC21, yalnız gerçekten önce mevcutsa), \`15dk/1h/4h intraday WATCH\`, \`V22 öncelikli teyit\`. Birini diğeri yerine geçirme.
3. **Ek özellik hipotezleri:** birkaç güne yayılmış baskı, yükseliş sırasındaki volatilite sıçraması, tekrarlanan sert 4 saatlik dönüşler, XAU–XAG/XPT/XPD ayrışması, XAU/GVZ stres çaprazlaması. **Diğer metal 15dk kaynak ve PIT gecikmeleri bulunmadan dört metal alarmı iddia etme.**
4. Aynı seans ve saat standartlarında 2024 eğitim, 2025 doğrulama, 2026 **donmuş** değerlendirme; alarm-düşüş **zirve öncesi gün/saat**, yanlış alarm epizodu ve 5-gün %4 kapsaması ayrı raporlanmalı. 2026 zaten incelendiği için sonuç katı prospektif kör test değildir; canlı ilk-baskı gölge kayıtlarının ileri dönem boyunca toplanması gerekir.
5. Bu sürüm Neon veritabanına **yazmaz**, canlı REST API'ye sinyal **yayınlamaz**, portföy pozisyonu **üretmez**. Orijinal V22/BASE14 ve mevcut üretim kanalı değişmez.

**Araştırma kodu:** \`risk_v36_intraday_anomaly_shadow_v1.py\`, \`test_risk_v36_intraday_anomaly_shadow_v1.py\` ve \`gold-v36-intraday-fourpct-shadow.yml\` araştırma dalında. Kodun çalıştırma sonucu, CI koşusu doğrulanmadan \`SUCCESS\` ilan edilmez.
