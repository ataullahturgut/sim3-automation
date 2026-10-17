# 6 Ocak AL / 2 Şubat SAT — OLAY–ÖĞREN gerekçe denetimi (17 Ekim 2026)

**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 · **WORKSTREAM=MODEL / retrospective forensic only**.  
**Bilimsel statü:** `RETROSPECTIVE_HYPOTHESIS_ONLY; LEARNED_ORG_SIGNAL=NOT_PROVEN; LIVE_OR_BLIND_TEST=NO; S3_EXECUTION=0`.  
**Amaç:** Önceki sohbetteki yaklaşık +%2,81 araştırma senaryosunun hangi parçaları gerçek zamanlı ekonomiye uyuyor, hangileri sonradan seçilmiş, ayırmak. Mevcut CORE, ÖĞREN-03 ve OLAY-02 değiştirilmez.

## 1. İki farklı eski karar izi — birbirine karıştırılmamalı

1. **14 Ekim GPT bağımsız vaka deneyi**, [asıl rapor](../independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md): 6 Ocak 2023 **16:46 TRT** makro+ilk altın tepkisi, üç M1 tamamlanmış teyidi, M1 ASK proxy **1849,30** ile AL hipotezi. 13 Ocak'a kadar GOLD tutuldu, SAT gerçekleşmedi. 6 Ocak'ta ücret sürprizi ve ilk fiyat tepkisi **tutarlı ekonomik senaryo**, ancak eşik 0,6% ve 3M1 bu örnek gözlendikten sonra geliştirildi ve DXY/getiri teyidi eksik; dolayısıyla kör/öğrenilmiş olay kuralı değil.
2. **Daha sonraki sohbetin +%2,81 senaryosu**, 6 Ocak 17:00 UTC **bar başlangıcı** (tamamlanma 17:15 UTC / 20:15 TRT) MID **1863,26** al ve 2 Şubat 14:00 UTC **bar başlangıcı** (tamamlanma 14:15 UTC / 17:15 TRT) MID **1946,56** sat. Bunlar **ayrı, geriye dönük seçilmiş araştırma fiyat çıpalarıdır**; birinci testteki 16:46 TRT AL ile aynı değildir. İlgili as-of karara ayrılmış dondurulmuş GPT prompt/yanıt/zaman damgası veya teyitli S3 BUY/SELL kaydı bulunmadı. Eski konuşma açıklamalarından bu iki noktanın tarihsiz ORG kuralı tarafından bağımsız olarak üretildiğini çıkaramayız.

**Salt-okunur Neon kontrolü (17 Ekim 2026):** Tek EVTradingLabs/Dukascopy-türevi `gold_research_evduka_xau15m_bidask_candidate` source_id `EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1`; 2023-01-06 17:00Z M15 bar `BID=1863.08, ASK=1863.44, MID=1863.26`; 2023-02-02 14:00Z M15 bar `BID=1946.40, ASK=1946.72, MID=1946.56`. `100*(.992^2)*(1946.56/1863.26)=102.8058` USD; vendor ASK/BID üzerine **ayrıca** aynı varsayımsal %0,8/ayak gider eklenirse 102.7874 USD. **Banka fiyatı, banka spread'i, karar sonrası emir icra fiyatı ve karar üretim kanıtı değildir**. Fiyat barı ancak **bar kapanışında** bilinebilir. MID fiyat kapanışında sinyal verip aynı kapanış MID'inden emir gerçekleştirmek de gerçek bir execution testi değildir.

## 2. Ekonomik DNA uygunluğu

**AL tarafı — G01-A / ORG01 adayı, açıklanabilir fakat kural olarak henüz ispatlanmamış.**

- [BLS'nin 6 Ocak 2023 tarihli ilk bülteni](https://www.bls.gov/news.release/archives/empsit_01062023.htm): istihdam +223 bin, işsizlik %3,5, ücret artışı aylık %0,3; eski GPT raporunun derlediği ex-ante piyasa ücret beklentisi yaklaşık %0,4. Yumuşak ücret ve daha az Fed sıkılaşması beklentisi → düşük USD/getiri → GOLD-UP, ÖĞREN-03 [ORG01 P0–P3 hipotezi](../adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md#org01--fırsat-maliyeti-gevşemesi-ve-çokkanallı-altın-talebi) ile uyumlu. Aynı pakette kuvvetli istihdam **karşıt ORG02 şahin kanalını** açık tutar.
- 6 Ocak 13:30Z'den sonra ilk tamamlanmış M15: öncesi MID 1835,97 → sonrası 1847,83, +%0,646; eski GPT 16:46 TRT M1 teyidi vardı. 15:00Z ISM zayıf hizmet raporu **16:46 TRT kararının gerekçesi olamaz**, ancak 20:15 TRT fiyat senaryosunda daha önce yayımlanmış olabilir.
- ÖĞREN-03 gerçek karar için aynı-saniye faiz/USD, açıklama öncesi beklentinin vintage'ı, rakip mekanizmalar, beklenen kalan hareketin ücret üstü getirisi ister. Eski vaka araştırması bu kanıtların **tam olmadığını** açıkça kabul eder.
- 6 Ocak ve 12 Ocak'taki seçilmiş aynı-saat olaysız kontrollerin sonraki 4 saat fiyat hareketleri de pozitif; olayın tüm yükselişe **neden olduğuna** veya sonraki haftaların devamını tahmin ettiğine karar verilemez.
- [S1 57 olay deneyi](S1_ARCHIVE_INDEPENDENT_EVENT_DISCOVERY_AUDIT_20261016.md) değerlendirmesindeki 2024–25 **41 bağımsız yayında** ekonomik açık yön **20/41**, market-only **19/41**; Brier ekonomi **0,295443**, market-only **0,281137**, basit yayın-aile oranı **0,257885**. Daha düşük Brier daha iyi; **ekonomik bağlantının genellenebilir üstünlüğü bulunmadı**. Retrospektif erişim ve güncel taraflılık sınırları devam eder.

**SAT tarafı — Şubat 2 ORG01 sönümü / ORG10 kâr alma / ORG02 baskı hipotezi, fakat somut 17:15 TRT anı için sertifika yok.**

- [Fed 1 Şubat 2023 resmî açıklaması](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm): +25 baz puan (4,50–4,75%) ve ilave artış beklentisi; 2 Şubat'a kadar biliniyordu.
- [2 Şubat ECB açıklaması](https://www.ecb.europa.eu/press/pr/date/2023/html/ecb.mp230202~08a972ac76.en.html): +50bp; aynı gün [BoE](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2023/february-2023) de +50bp. **Tek yönlü gold-DOWN etkisi bu başlıklardan otomatik çıkmaz**; USD/ABD reel faiz ve değerli metallerin gerçek zamanlı ayrışması gerekiyor.
- Neon'da 2 Şubat **07:00Z'de başlayan M15 kapanışı** MID **1959,615**, 14:00Z'de başlayan M15 kapanışı MID **1946,56**: o ana kadar yaklaşık **-%0,666** zirveden düzeltme görülebiliyordu. Fiyat zayıflaması olası **yorulma adayı**, tek başına ekonomik ORG10 veya güçlü satış kanıtı değil. Aynı gün daha sonra (20:15Z M15 barı) MID 1911,785'e kadar iniş **17:15 TRT SAT'ın gerekçesi olarak ileri taşınamaz**.
- **3 Şubat 2023 NFP 517 bin** verisi satış anında bilinmiyordu; fiyatın sonraki gün daha çok düşmesi 2 Şubat çıkışını otomatik doğru tahmin olarak doğrulamaz. [BLS Şubat 3 ilk bülten](https://www.bls.gov/news.release/archives/empsit_02032023.htm). Eski bağımsız **Şubat 3 SAT** vakası ise [ayrı rapor](../independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md); Şubat 2 exit ile aynı değildir.

## 3. CORE ne dedi?

[Ocak–Şubat mevcut CORE deneyinde](JAN_FEB_2023_MATURED_OPPORTUNITY_REPLAY_AUDIT_20261016.md) **6 Ocak 17:00 UTC** `START UP` ve `S3=KEEP CASH`; **1 Şubat 20:45 UTC** `START UP` ve `KEEP CASH`. Aynı CORE araştırmada **0 AL, 0 SAT**, Nakit 100 USD. Yeni [gün gün Ocak](../apps/portfolio_guard_v1/data/JAN_2023_SELECTIVE_CADENCE_REAL_CORE_AGGREGATES_20261017.json) ve [Şubat raporu](FEB_2023_INTEGRATED_S1_S2_S3_REAL_DAILY_RESULTS_20261017.md) de kanıtlı OLAY-ÖĞREN ekonomik S1 tahminini veya başarılı S3 kararı göstermiyor. **+%2,81 S3 model başarısı değil, ayrı retrospektif fiyat senaryosudur.**

## 4. Yeniden üretilebilir bilimsel test için eksik zincir

1. İlk yayın öncesi **özgün actual + consensus**; `event_time, first_available_at, vintage` ve verinin o dakikada erişildiğinin belgesi.
2. Olay öncesi ve hemen sonrası **XAU/FX/ABD nominal-reel faiz, gümüş ve likidite** eşzamanlı durum; seçilmiş habersiz ve rakip olay kontrolleri. Bu kanıtlar olmadan G01-A/ORG01 adayını S1'de eğitimli kural sanma.
3. Kuralın P0→P1→P2/P3→P4/P5 **geçersizleşme ve kalma** mekaniğini geçmiş bağımsız olaylarda, önceden dondurulmuş algoritma/parametrelerle öğren; önceki yıllardan gelecek dönem bilgisi as-of protokolüne göre ayrılmalı.
4. `2023-01-06T17:15Z` ve `2023-02-02T14:15Z` gibi seçilmiş karar anlarını hedef olarak koyma. **Karar üretilen ilk timestamp**, **o ana kadar bilinen veri**, **dondurulan ORG koşulu + karşıt hipotez**, **P(UP/DOWN)/kalan hareket**, **maliyet-net Q(CASH/GOLD)**, **sonraki ilk yürütülebilir fiyat**, **sonuç olgunlaşma zamanı** ayrı immutably yazılsın.
5. 6 Ocak 2023 olayı, aynı türden **başarısız/yanıltıcı başlıklarla** ve 2 Şubat Şubat 3 negatif kontrolleriyle sınanmadan `RULE_CONFIRMED` olamaz.

**Denetim kararı:**
- `ECONOMIC_NARRATIVE_COMPATIBLE_WITH_ORG01=YES` (6 Ocak araştırma hipotezi)
- `ECONOMIC_CAUSAL_MECHANISM_INDEPENDENTLY_PROVEN=NO`
- `PRIOR_GPT_EVENT_REACTION_BUY_HYPOTHESIS=YES_2026_ARCHIVE_EX_POST`
- `ORIGINAL_6JAN_2FEB_PAIR_WAS_LEARNED_SIGNAL=NOT_ESTABLISHED`
- `FEB02_CONCURRENT_SELL_RULE_PROVEN=NO`
- `CORE_REAL_BUY_SELL=0`
- `DECISION_PROTOCOL_FREEZE_BEFORE_NEXT_REPLAY=REQUIRED`.
