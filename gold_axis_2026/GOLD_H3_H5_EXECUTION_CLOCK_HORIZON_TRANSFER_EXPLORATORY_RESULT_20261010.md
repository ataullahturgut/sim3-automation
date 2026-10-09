# XAU/USD 3- ve 5-işlem-günlük Ufuk Transferi — GERÇEK, KEŞİFSEL BACKTEST (2026-10-10)

**Durum:** NEON READ-ONLY TEST GERÇEKTEN ÇALIŞTIRILDI. **YENİ ŞAMPİYON YOK / NO PROMOTION**. Araştırma 2026-10-10 tarihinde GitHub'ın o anki `5d1d0fa426853ed55052725260126618a61d3cac` branch HEAD'i, aynı source-governed hesap ile yapıldı. Açık 2025–2026 yılları *independent lockbox değildir*. Bu belge eski kısa vadeli sonuçları değiştirmez.

## Testin anlamı ve ufuklar
- **Origin 09:00 TR**, üç işlem günü sonrası **09:00 TR** (H3), beş işlem günü sonrası **09:00 TR** (H5 = bir işlem haftası).
- **Origin 17:00 TR**, üç işlem günü sonrası **17:00 TR** (H3), beş işlem günü sonrası **17:00 TR** (H5).
- Kullanıcı 09–17 banka işlem saatlerine uygun olarak iki origin ayrı; H3 ve H5 **3/5 takvim günü değildir**. Tatil veya eksik kaynak günü, 'sıradaki gözlenmiş gün' diye atlanmadı: T+3 / T+5 kesin **hafta içi** tarihi hesaplandı ve ancak o tarihte original provider quote varsa etiket oluşturuldu. Hafta sonu doğal şekilde arada bulunabilir; borsa tatil günlerini atlayan resmi takvim modeli **henüz kurulu değil**, o dönemler kaynak yoksa kapsam dışında.
- Etiket BID origin open -> BID hedef open, ASK origin open -> ASK hedef open **aynı sign** değilse çıkarıldı; sıfır ret ve eksik origin/target da çıkarıldı. BID/ASK yalnızca veri sağlayıcının kotasyonudur, Türk banka alış/satış fiyatı değildir.
- Origin feature'ları için kesintisiz **origin öncesi 16 M15 BID open/close** (09 origin:05–09; 17 origin:13–17) gerçek kaynak barları zorunlu.
- 2020–2025: Neon `gold_research_evduka_xau15m_bidask_candidate` (Dukascopy-derived private accepted historical research quote candidate); 2026: `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`, **m1_matched=15**, yalnızca kaynakça tamam gözlemler, mevcut son tarih **2026-10-07**. 1.695 günün iki origin için tam 16 bar + 09/17 quote'u görüldü; H3/H5 rapor yıl-kohortları ayrıca belirtilir. Neon salt SELECT, kaynak mutasyonu yok.
- GPR/13D HMM'nin tam özgün ChHHO-ANFIS çıkışını buraya yeniden eğittik **DENİLMİYOR**. Aşağıda gerçek hesaplanan, *orijinal CBR'nin matematiksel çekirdeği* yeniden hedeflenmiş ve aylık işaret kontrolü de ayrı verilmiştir.

## Gerçek sınanan tahmin sınıfları
1. **CBR_PATH**: Mevcut `gold_execution_2026_full_trajectory_cbr_20261008.py` matematiksel çekirdeğindeki 16 M15 getiri -> sekiz yarım saat toplamı -> 8 normalize kümülatif path, RV=`sqrt(sum(r_bar²))`. En yakın 41 geçmiş yol, `distance=sqrt(sum((path_now - path_hist)²)/8)`, sıcaklık=komşu 41'in medyan uzaklığı, ağırlık=`exp(-d/temp)`, eğitimdeki genel UP oranı ile **5 eşdeğer ağırlık** shrunk posterior; 0.5 sabit yön kararı. Bu bir **H3/H5 için YENİ RETRAIN**, eski gece etiketi yeniden adlandırılmadı.
2. **CBR_REGIME_PATH**: Aynı k41 CBR fakat uzaklığa `0.30 * [((log_RV_i-log_RV_j)/train_SD_RV)² + ((log_GVZ_i-log_GVZ_j)/train_SD_GVZ)²]` ekleniyor. GVZ dosyası repo içindeki `GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv`; **yalnızca origin tarihinden ÖNCEKİ son kapanış**, en fazla 7 gün önce, PIT erişim ve kaynak-vintage kesinliği geçmiş backfill için bağımsız olarak kanıtlanmış değildir. Bu sürüm eski CBR'nin feature formüllerini korur, son 3/5 günlük yeni hedefi öğrenir; tam eski DAY/OVN score'u değildir.
3. **PRIOR_MONTH**: Önceki **tamamlanmış** takvim ayının 09/17 kaynak BID fiyatının ilk -> son yönü. En az 10 kaynak günü olan önceki ay gerekir; **özgün CURRENT8 veya ChHHO tahmini değil**, düşük frekanslı işaret vekilidir. Tarihler arası risk ve eksik 2026 kaynak ayları ayrıca kontrol edilmelidir.
4. **UP baseline**: Her zaman UP; her yıl BA=50%, raw ACC yükseliş prevalansına eşit. VIX+GVZ DAY Logistic, tam sekiz-metalli özgün aylık ChHHO-ANFIS ve eski 3-gün H3 experts **BU koşuda yeniden eğitilmedi**, dolayısıyla bunların ufuk transferi başarı iddiası yok. İzleyen ayrı source/PIT çalışmaları gerektirir.

**Chronology:** Eğitim 2020–22 (2023 skoru), 2020–23 (2024), 2020–24 **frozen** (2025 ve 2026); örnek hedefinin olgunlaştığı *end date < sonraki test yılının 1 Ocak'ı* zorunlu. 2025 ve 2026 etiketleri fit edilmedi. Parametreler H3/H5 için ayrı öğrenildi, 2025/26'ya göre k/0.30/cutoff optimizasyonu yapılmadı. Önceki sonuçları gördükten sonra yapılan bu test keşifseldir. Art arda tahminlerin H3/H5 gerçekleşme aralıkları birbiriyle çakışır, satır N bağımsız örnek sayısı değildir.

## Gerçek BA (%) sonuçları

| Origin | Ufuk | Model | DEV 2023 | DEV 2024 | Açılmış 2025 | Açılmış 2026 |
|---|---|---|---:|---:|---:|---:|
| 09 TR | H3 | CBR_PATH | 48.41 | 47.98 | 54.33 | 48.31 |
| 09 TR | H3 | CBR_REGIME_PATH | 51.59 | 47.84 | 53.97 | 50.62 |
| 09 TR | H3 | PRIOR_MONTH | 48.02 | 49.59 | 48.88 | **64.34**¹ |
| 09 TR | H5 | CBR_PATH | 50.66 | 51.76 | 44.28 | 53.24 |
| 09 TR | H5 | CBR_REGIME_PATH | 50.48 | 50.21 | **55.93** | **44.20** |
| 09 TR | H5 | PRIOR_MONTH | 48.38 | 48.90 | 46.68 | 55.22¹ |
| 17 TR | H3 | CBR_PATH | **55.21** | 50.69 | 54.02 | 53.14 |
| 17 TR | H3 | CBR_REGIME_PATH | 45.75 | 50.09 | 48.19 | 51.92 |
| 17 TR | H3 | PRIOR_MONTH | 47.86 | 47.74 | 49.97 | 52.63¹ |
| 17 TR | H5 | CBR_PATH | 54.45 | 50.15 | 47.59 | 50.25 |
| 17 TR | H5 | CBR_REGIME_PATH | 50.44 | 50.85 | 52.11 | 47.55 |
| 17 TR | H5 | PRIOR_MONTH | 49.49 | 48.51 | 47.68 | 44.80¹ |

¹2026 MONTHLY PRIOR kohortu H3 **n=99**, H5 **n=95**; diğer modellerde H3 09/17 **n=124**, H5 09 **n=120**, 17 **n=119**. Sütunlar farklı katılımlıysa asla paired model superiority sayılmasın.

**N:** 2023 H3 09/17 252; H5 09 253/17 252. 2024 H3 09/17 256; H5 09 257/17 256. 2025 H3 09/17 255; H5 09 255/17 254. 2026 CBR üst satırdaki 124/120/119; PRIOR_MONTH 2023–25 hemen hemen tüm aynı tarihleri kapsar. 2026 ham direkt kaynak tüm iş günlerinin tam kapsamı değildir.

## 2025–2026 kontrol: raw ACC ve sınıf hassasiyeti
- **09 H3 CBR_REGIME_PATH 2025:** 141/255 = 55.29% raw, BA53.97, UP59.01 / DOWN48.94. **2026:** 67/124 = 54.03% raw, BA50.62, UP31.37 / DOWN69.86.
- **09 H5 CBR_REGIME_PATH 2025:** 154/255 = 60.39% raw, BA55.93, UP69.01 / DOWN42.86. **2026:** 55/120 = 45.83% raw, BA44.20, UP33.33 / DOWN55.07. **Aynı tarihler 2025 always UP=171/255=67.06% raw; BA=50.**
- **17 H3 CBR_PATH 2025:** 156/255=61.18% raw, BA54.02, UP77.71 / DOWN30.34. **2026:** 64/124=51.61% raw, BA53.14, UP84.75 / DOWN21.54; DOWN kurtarma düşük.
- **09 H3 PRIOR_MONTH 2026:** 65/99=65.66% raw, BA64.34, UP57.50 / DOWN71.19. **2023, 2024 ve 2025 aynı strateji BA48.02,49.59,48.88**. Geçmiş yıllara taşınmayan, 2026 gözlenmiş ay rejimiyle ilişkili aday; normalde 2026 sonuçları seçilmemesi gerekir.
- **09 H5 CBR_PATH 2025:** 139/255=54.51% raw, BA44.28, DOWN14.29. **2026:** 59/120=49.17% raw, BA53.24, DOWN26.09.
- **17 H5 CBR_PATH 2025:** 152/254=59.84% raw, BA47.59, DOWN15.19. **2026:** 54/119=45.38% raw, BA50.25, DOWN16.18.

## Sonuç ve araştırma sınırları
- **Yeni üç günlük/haftalık ufuk, mevcut CBR yol ve GVZ-rejim modelinin yıllar arasında güvenilir şekilde >55% BA sağlamasını başaramadı.** Haftalık 09:00 rejim-CBR 2025 BA55.93 ise 2026 BA44.20; 17:00 H3 CBR_PATH daha kararlı ama ancak BA~50–55 aralığı.
- **2026 09:00 H3 önceki-ay yönü 64.34 BA** dikkat çekicidir fakat 2023–25 düşük BA ve yalnızca ~8 kaynakça uygun 2026 ay grubu nedeniyle yüksek araştırma yanlılığı vardır. Bu veri dilimiyle modele/politikaya PROMOTE edilmemeli.
- Farklı amaçlar: H3/H5 **endpoint sign** sonuçları *2026 DAY09–17 veya OVN17–next09 sign* başarılarıyla doğrudan karşılaştırılamaz. Üç/beş gün içinde tersine hareket, maximum adverse excursion ve 17 sonrasındaki banka makası ayrıca ölçülmedi.
- Kaynak/cause gate: gerçek broker fill, 09/17 banka makası ve masraf yok; quote provider PIT/tick ilk baskı ayrıntıları ayrıca gereklidir. 2026 dahil farklı sağlayıcı boru hatları kontrollü ama tam cross-vendor exact target parity çalıştırılmadı. Bağımsız bekleyen 2027 forward holdout yok.
- **Sonraki tek kapsamlı deney:** Tüm 3D/5D horizon'ları aynı 2020–2026 source-eligible origin üzerinde *as-of* orijinal DAY VIX+GVZ Logistic, aylık CURRENT8 GPR-VW/gerçek ChHHO tahmininin sayısal çıktısı, RTE ve CBR yolunu ayrı ayrı yeniden etiketleyerek **H3/H5 için sıfırdan retrain** etmek; soft-handoff/risk filter yalnızca geliştirme yılına dayalı. 2026'yı seçici rejim olarak eşik optimize etme. En güçlü gösterge uzun ve kısa periyot arasındaki ölçek farkı olabilir, ancak mevcut sonuç yeni yön tahmin kanıtı değildir.

**Not:** Bu çalışma GitHub Actions workflow çalıştırması değildir; bağlı Neon DB'den canlı SQL SELECT ve GitHub sabit-kod formüllerinden Javascript ile sayısal test yapıldı. Çekirdek CBR yöntemine uygundur, ancak eski modelin tam Python uçtan-uça `shape.features` / frozen prediction artefaktı değildir. Aynı şekilde gerçek VIX ve aylık optimizer bu raporda koşulmadı; dolayısıyla eski H3 bütün-model transferi yapılmış gibi sunulamaz.
