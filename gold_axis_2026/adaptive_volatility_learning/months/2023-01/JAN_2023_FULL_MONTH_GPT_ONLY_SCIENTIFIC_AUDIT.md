# Ocak 2023 — ARŞİV: 31 günlük V0 altın/nakit mekanik deney ve GPT bilimsel gözden geçirmesi

> **14 Ekim 2026 AMAÇ UYUMSUZLUĞU DÜZELTMESİ:** Bu rapordaki `$101,9695` ve tüm günlük işlemler **5-seans momentum V0** deneyidir. Kullanıcının hedeflediği **orta/büyük şiddetli UP/DOWN olaylarını, başlamadan önce veya başladıktan sonra tespit edip yalnız maliyet-sonrası değer taşıyan hareketlerde işlem yapma stratejisi** bu raporda uygulanmamıştır. Bu sonuç **asıl stratejinin performansı** veya Ocak 2023 çalışmasının tamamlanması değildir. Sayılar değiştirilmeden tarihsel baz olarak korunur. [Yeni hedef ve Ocak yeniden çalışma sözleşmesi](../../EVENT_DRIVEN_MEDIUM_LARGE_MOVE_RESTART_CONTRACT_20261014.md).
**Durum (2026-10-14): COMPLETED_NUMERIC_REPLAY / COMPLETED_GPT_SOURCE_CRITIQUE / EX_POST_DISCOVERY / NO_BLIND_TEST / NOT_REAL_BANK.**

## I. Gerçek 100 USD sonucu

| Aynı vendor BID/ASK ve %0,8 her yön masraf | 31 Ocak net nakit | Toplam ücret | İşlem |
|---|---:|---:|---|
| **Risk-aware 5 seans trend V0** | **$101,9695** | $3,2910 | 2 AL, 2 SAT |
| Sadece 5 seans trend | **$101,9695** | $3,2910 | 2 AL, 2 SAT |
| **Altın al ve ay boyunca tut** | **$103,7589** | $1,6368 | 1 AL, 1 SAT |
| Nakit | $100,0000 | $0 | 0 |

**Karar:** Mekanik V0 %1,97 kazandı fakat altın pasif al-tuttan **$1,7894** geride kaldı. **Adaptif volatilite filtresi 20 tam seansın hiçbirinde işlemi değiştirmedi.** Dolayısıyla ilk ay yeni bir volatilite tahmin başarısı sağlamıyor.

## II. Her takvim günü hesaplanan karar ve 100 USD portföy değeri

**Saat uyarısı:** Aşağıdaki **tarih UTC takvim günüdür**; XAU günlük getiri o tarihle adlandırılan **NY17 seansının** kapanış getirisidir ve 00:00–24:00 UTC getirisi değildir. 3 Ocak NY17 seansına ait ilk işlem **2 Ocak 23:15 UTC**'de, 27 Ocak seansı satışı 26 Ocak 23:15'te, 30 Ocak seansı alışı 29 Ocak 23:15'te, 31 Ocak seansı satışı 30 Ocak 23:15'te gerçekleşmiş sayılır. Gün sonu NAV gerçek UTC işlemlerine göre işaretlenir. 16 Ocak MLK gününde 76 bar olsa da tamamlanmış NY17 kapanışı olmadığından sinyal/işlem yok.

| Ocak günü (UTC) | XAU NY17 değişimi | Gerçek UTC-günü eylem / tutulan varlık | Gün sonu $ |
|---|---:|---|---:|
| 01 | — | Tam seans yok / mevcut varlığı tut | 100.00 |
| 02 | — | **ALTIN AL** (sonraki NY17) | 99.10 |
| 03 | +0.850% | Altın tut | 99.80 |
| 04 | +0.829% | Altın tut | 100.60 |
| 05 | -1.169% | Altın tut | 99.45 |
| 06 | +1.800% | Altın tut | 101.24 |
| 07 | — | Tam seans yok / mevcut varlığı tut | 101.24 |
| 08 | — | Tam seans yok / mevcut varlığı tut | 101.24 |
| 09 | +0.302% | Altın tut | 101.53 |
| 10 | +0.293% | Altın tut | 101.82 |
| 11 | -0.077% | Altın tut | 101.74 |
| 12 | +1.149% | Altın tut | 102.90 |
| 13 | +1.223% | Altın tut | 104.16 |
| 14 | — | Tam seans yok / mevcut varlığı tut | 104.16 |
| 15 | — | Tam seans yok / mevcut varlığı tut | 104.16 |
| 16 | — | Tatil / NY17 kapanışı yok | 104.16 |
| 17 | -0.599% | Altın tut | 103.55 |
| 18 | -0.246% | Altın tut | 103.28 |
| 19 | +1.470% | Altın tut | 104.80 |
| 20 | -0.313% | Altın tut | 104.48 |
| 21 | — | Tam seans yok / mevcut varlığı tut | 104.48 |
| 22 | — | Tam seans yok / mevcut varlığı tut | 104.48 |
| 23 | +0.258% | Altın tut | 104.78 |
| 24 | +0.325% | Altın tut | 105.10 |
| 25 | +0.459% | Altın tut | 105.58 |
| 26 | -0.877% | **ALTIN SAT** (sonraki NY17) | 103.87 |
| 27 | -0.054% | Nakit tut | 103.87 |
| 28 | — | Tam seans yok / mevcut varlığı tut | 103.87 |
| 29 | — | **ALTIN AL** (sonraki NY17) | 103.02 |
| 30 | -0.268% | **ALTIN SAT** (sonraki NY17) | 101.97 |
| 31 | +0.283% | Nakit tut | 101.97 |

**Kaynak ve ücret:** Neon `gold_research_evduka_xau15m_bidask_candidate`, tarihsel EVTradingLabs/Dukascopy M15 BID/ASK; kapanış gerçek bar, NY17 DST doğru. Yeni NY17 seansının **ilk kapanmış M15 fiyatı** ve **önceki tamamlanmış beş seans** kullanılmakta; 20 seanslık referans abs log getirisi ile karşılaştırılan `a5/a20 <= 2` risk filtresi. Her AL'da **%0,8**, her SAT'ta **%0,8**; ayrıca vendor BID/ASK alış-satış farkı. Faiz, banka spread'i, vergi ve slippage yok. **Gerçek bankada uygulanmış işlem değildir**; kullanıcıya bankada tahsil edilmiş getiri olarak sunulamaz.

**Sayısal delil:** [31 UTC takvim günü ve NAV](JAN_2023_31_UTC_CALENDAR_DAYS_ACTIONS_NAV.csv), [21 NY17 seans, momentum, vol oranı ve kararlar](JAN_2023_21_NY17_SESSIONS_VOL_AND_DECISIONS.csv), [4 senaryo sonuç JSON](JAN_2023_100USD_RESULTS.json), [işlem/masraf ve durum dondurma](FROZEN_RESEARCH_CONTRACT.md), [tekrar oynatma için girişleri özel tutan Python referans kodu](../../../tools/gold_adaptive_monthly_v0_replay_20261014.py).

## III. GPT-only kanıt/olay örgüsü

| Ekonomik ilk yayın, UTC | Kaynakta gerçek bilgi | Fiyat ve bilimsel yorum |
|---|---|---|
| **6 Oca 13:30** NFP | BLS Aralık22 payroll **+223.000**, işsizlik **%3,5** | NY17 altın **+%1,800**; Fed beklentisi/ücret kanalları aday; ilk15m USD/yield kontrolü olmadan NFP bütün yükselişe neden oldu denemez |
| **12 Oca 13:30** CPI | BLS Aralık22 aylık **−%0,1**, yıllık **%6,5** | XAU **+%1,146**; dezenflasyon ve daha yavaş Fed hipoteziyle uyumlu, tam nedensel pay ölçülmedi |
| **18 Oca 13:30** PPI | BLS Aralık22 **−%0,5** | XAU **−%0,25**. **Karşıt örnek:** yumuşak enflasyon ölçümü ALTIN UP'ı zorunlu kılmıyor |
| **26 Oca 13:30** GDP | BEA 2022Q4 ilk tahmin **+%2,9** yıllıklandırılmış | XAU **−%0,877**; büyüme/iskonto/Fed kanalları ayırt edilemedi; V0 satışı 27 NY17 ilk barında **yalnız momentum işaretiyle** |
| **27 Oca 13:30** PCE | BEA Aralık22 aylık manşet **+%0,1**, çekirdek **+%0,3** | XAU **−%0,054**. V0 satış **26 Oca 23:15 UTC**; bu satışın nedeni 27 Oca PCE olamaz |
| **31 Oca** Fed beklentisi | Reuters: zayıf USD ve **1 Şubat** 25bp faiz artırımı beklentisi | 1 Şubat gerçek FOMC **Ocak'ta açıklanmadı**; yalnız toplantı/beklenti olay örgüsünün parçası |

Kaynaklar: [6 Ocak BLS NFP](https://www.bls.gov/news.release/archives/empsit_01062023.htm), [12 Ocak BLS CPI](https://www.bls.gov/news.release/archives/cpi_01122023.htm), [18 Ocak BLS PPI](https://www.bls.gov/news.release/archives/ppi_01182023.htm), [26 Ocak BEA GDP](https://www.bea.gov/news/2023/gross-domestic-product-fourth-quarter-and-year-2022-advance-estimate), [27 Ocak BEA PCE](https://www.bea.gov/news/2023/personal-income-and-outlays-december-2022), [31 Ocak Reuters](https://wealthinsights.metrobank.com.ph/reuters/precious-gold-set-for-third-monthly-rise-on-softer-dollar-fed-slowdown-bets).

**Olay araştırmasından asıl yeni ve karşıt kanıt:** [9 Şubat 2023'te ilk yayımlanan WGC Ocak ETF raporu](https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2023/02): Küresel ETF **−US$1,6bn / −26 ton çıkış**, altın **+%6,1 aylık**. [WGC Ocak altın yorumunda](https://www.gold.org/goldhub/research/gold-market-commentary-january-2023) zayıf dolar ve düşen ABD faizleri ana açıklama adayları; ayrıca COMEX managed-money vadeli net long genişlemesi var. Ocak aylık ETF raporu **9 Şubat'tan önce bilinmiyordu**, bu nedenle 2023 Ocak işlemlerine girdi yapılmadı; sadece **FULL_HISTORY_DISCOVERY/GPT** karşı-örneği oldu. Altının mutlaka pozitif global ETF girişiyle yükseldiği mekanik iddiası yanlışlanıyor.

**Diğer metaller (yalnız geriye dönük bağlam):** StakTrakr 3–31 Ocak günlük serilerinde XAG **−%5,35**, XPT **−%8,10**, XPD **−%11,14**. Veri `available_as_of=2026-09-05` ve kapanış NY17 ile aynı UTC değildir; altınla aynı-saat nedensel katsayı oluşturma. Gold strong vs 3 metals weak **altına özgü talep / USD–faiz–pozisyonlanma** olası; her metalin farklı beta ve sanayi talebi de rakip nedendir.

**İzin verilen sonraki yıl analojisi:** 2025 ilk çeyrekte güçlü ETF girişi + azalan futures managed-money net long görülmesi ile 2023 Ocak'taki ETF çıkışı + genişleyen futures net long örüntüsü **farklıdır**. Sonraki yılları 2023'ü anlamak için kullanabiliyoruz; fakat bu örnekler 2023'teki işlemleri önceden haber veren bilgi değildi. 2025/26 krizlerini 2023'in normal yükseliş rejimine zorla eşitleme.

## IV. V0'dan alınan sınırlı dersler — olay stratejisine otomatik devredilemez

1. **Volatilite katmanı bu ay başarısız katkı:** `a5/a20 >2` uyarısı **0/20**; trend5 ve vol-gated strateji **tam eşit**. Riski o ay ölçen diagnostik oran bir **kalibre edilmiş gelecekteki volatilite tahmini değildir**.
2. **Sadece kâr etmek yeterli değil:** V0 +%1,97, aynı ücretle BUY/HOLD +%3,76. Ocak 25 NAV **$105,58** iken 31 Ocak $101,97; 27/30/31 NY17 kararlarında **işlem sürtünmesi** önemli.
3. **Makro nedenler çoklu:** NFP/CPI/PPI/GDP/PCE farklı reaksiyonlar; kaynakların tarihi belli, yine de eşzamanlı DXY/UST2/10Y/QE beklentileri eksik. Haberin sonrasında fiyatın aynı yönde gitmesi tek-neden ispatı değil.
4. **Ücret duyarlı hysteresis, minimum bekleme, daha iyi vol risk eşiği** ayrı **POST_JAN_UNTESTED_IDEAS**. Bu öneriler Jan sonuçlarına baktıktan sonra ortaya çıktı; Ocak'taki işlem geri dönük **değiştirilmez**. Şubat testine önce kayıt edilmeli; 2023 Şubat'ın bilinmiş olduğu da gizlenmez.
5. **AI rolü burada niteliksel ve GPT-only:** GPT belge temelli karşıt kanıtları ortaya koydu, otomatik emir/gold direction düzeltmesi **yapmadı**. Algoritma tek başına vs algoritma+GPT **sayısal üstünlük testi yapılmadı**, aksi iddia edilmez.

**Hüküm:** `JAN2023_V0_ONLY_ARCHIVED; 31_UTC_DAYS_CHECKED; NY17_FULL_20_PARTIAL_1; MECHANICAL_V0_COSTED; GPT_CAUSAL_AUDIT_COMPLETED_BUT_NONEXHAUSTIVE; PRIMARY_EVENT_DRIVEN_MEDIUM_LARGE_UP_DOWN_NOT_RUN; FEB_HANDOFF_PENDING; NO_PREDICTIVE_PROMOTION`. **Önemli:** 'küçük hareketlerde işlem yapmayalım' bu projenin yeni icadı değildir; kullanıcı tarafından en baştan belirtilen temel iş kuralıdır. Bu V0 kullanıcı amacına göre yanlış seçilmiş testtir.
