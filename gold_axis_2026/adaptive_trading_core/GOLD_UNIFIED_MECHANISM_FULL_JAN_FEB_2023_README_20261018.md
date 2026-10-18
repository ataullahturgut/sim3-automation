# Ocak–Şubat 2023 — BİRLEŞİK ekonomik mekanizma + orijinal S1/S2/S3 GERÇEK fiyat koşusu

**2026-10-18 · Reproduced native CORE · S1/S2/S3 kodları değiştirilmedi · 2022 ön eğitimi yapılmadı · 2024–25 fiyat/olay sonuçları öğrenmeye verilmedi**

## Gerçek deney kapsamı

- Neon `gold_research_evduka_xau15m_bidask_candidate`: **3.750** gerçek XAU/USD 15 dakikalık BID/ASK kaydı, tamamlanmış bar MID fiyatları. 2023-01-02 23:15Z → 2023-03-01 00:00Z; 39 kabul edilmiş 22:00 UTC araştırma seansı.
- GitHub orijinal `adaptive_market_core_s1_s2.js`: S1 kural keşfi, FAST S2 fazı, SLOW S2 tamamlanmış 39 seansın girişi, S3 koşullu ekonomik araştırma modu **sadece fiyatla ve kronolojik** gerçek işletildi.
- **Sıfır ön eğitim:** Önceki [2023 Jan–Feb AI gölge raporunda](../apps/portfolio_guard_v1/data/JAN_FEB_2023_AI_SHADOW_CHRONOLOGICAL_20261017.json) kullanılan **2022-10..12 = 5865 bar** bu yeni koşuda **KULLANILMADI**. Ocak 2023'ün ilk gözleminde S1 kural belleği boş, önceki sonuçlar yoktur. `learningMode=DISCOVERY_FULL_ARCHIVE` ismi ile olayın geçmişe bilgi taşıdığı sonucu çıkarılamaz: Kod yeni barları artan zamanda besliyor ve olgunlaşmamış etiketleri hiç kullanmıyor. Ancak veri PIT sertifikalı değil; ticari kör test değil.
- 8 tarihli haber: **6 Ocak NFP; 12 Ocak CPI; 1 Şubat Fed; 2 Şubat BoE, ECB kararı, ECB basın konuşması; 3 Şubat NFP; 14 Şubat CPI**. Bütün önemli haberler listesi olduğu veya bunlardan başka ABD/EU/Çin haberleri bulunmadığı İDDİA EDİLMEZ.
- `event_news_condition_router_v1` ve `economic_mechanism_integrator_v1` üzerinden ETKİ koşulları (K/CR), ORG adayları ve olay saati; **2023 actual vs consensus ilk-baskı vintage kanıtı yetersizse K03 vb yalnız `researchProxyTagsNotCertified` alanında** tutulur, orijinal CORE tahminine gizlice eklenmez.
- Her haber için açıklamadan sonraki **15dk/60dk/240dk** kapanmış bar, global S2 faz/yön/z, orijinal S1 4s forecast, S3 araştırma kararı ve geçmiş olay başlangıcından beri gerçekleşen fiyat değişimi. +60/+240 dakika ileri fiyat etiketleri **yalnız daha sonra sonuç denetimi için**, geçmiş karara girdi değil. Tam pencerede tek eksik M15 varsa 4s sonucu `null`.

## 1. Sekiz haberin gözlenen etkisi

Rakam `100×ln(P_t/P_{release-pre})`, yüzde log-getiri. Kaynak vendor MID. İşlem kârı değildir. Türkiye saati UTC+3.

| İlk açıklama | Sadece araştırma koşulları | +15dk | +60dk | +240dk | +60dk'da orijinal S2 |
|---|---|---:|---:|---:|---|
| **06.01 16:30 NFP** | K03 güçlü istihdam + K18 ücret beklentiden düşük + K19 işsizlik düşük; ORG01/02 çatışma adayı | +%0,644 | +%0,542 | +%1,391 | **NEUTRAL** |
| **12.01 16:30 CPI** | K02 manşet CPI beklentiden düşük | +%0,250 | +%0,257 | +%0,451 | **REENTRY UP** |
| **01.02 22:00 Fed** | K39 faiz kararı, doğrulanmış konsensüs/iletişim sürprizi yok; ORG01/02 aday | −%0,013 | +%0,793 | **NULL: fiyat barı boşluğu** | **NEUTRAL** |
| **02.02 15:00 BoE** | K39, beklenti ve söylem bilinmiyor, ORG01/02 | +%0,008 | −%0,066 | −%1,473 | **NEUTRAL** |
| **02.02 16:15 ECB** | K39; karar var, şahin sürpriz ispatlanmamış; ORG01/02 | −%0,044 | −%0,340 | −%1,798 | **CONTINUE DOWN** |
| **02.02 16:45 ECB konuşması** | K40, henüz tam konuşma içeriği bilinmez; ORG01/02 | −%0,219 | −%0,545 | −%1,745 | **CONTINUE DOWN** |
| **03.02 16:30 NFP** | K03 güçlü istihdam + K19 düşük işsizlik (RETROSPEKTİF, strict motorda UNKNOWN) | −%1,349 | −%1,731 | −%2,611 | **NEUTRAL** |
| **14.02 16:30 CPI** | K05 sürpriz yok | +%0,063 | −%0,600 | −%0,693 | **NEUTRAL** |

**Fed 1 Şubat'ta** haberden 4 saat sonraki 23:00Z hedef fiyatının 15dk tam yolunda piyasa boşluğu olduğundan `NULL` tutulmuştur. Eski başka bir 4s archivenin raporladığı artış, eksik 15dk yolu interpolasyonla doldurmak için kullanılmadı.

**2 Şubat'taki BoE/ECB/ECB-press 4 saatlik tepkileri tamamen bağımsız değildir**; aynı düşüşü üç defa toplamak yasak.

## 2. Orijinal modelin tüm dönem sonuçları

| Bileşen | Gerçek yeniden yürütme |
|---|---|
| **S1** | 3.750 gözlem, **219 origin**, **210 olgunlaşmış etiket**, **3 fiyat özelliği prototip kuralı** (Ocak'ta öğrenmeye sıfırdan başladı) |
| **S2 FAST** | **1.579 NEUTRAL**, **1.141 CONTINUE**, **89 START**, **174 PULLBACK**, **72 END**, **35 REENTRY**, **660 WARMUP** 15dk bar |
| **S2 SLOW** | **39/39** araştırma seansı alındı (UTC 22:00 çıpası, gerçek resmi settlement değildir) |
| **S3** | **0** ekonomik kural yayın-vintage sertifikalı; gerçek **0** işlem; ekonomik bilim kapısı kapalı |
| **S3 araştırma önerileri** | **3.090 KEEP**, **618 faz bilgisi yetersiz ABSTAIN**, **42 bar-boşluğu ABSTAIN** |
| **Nakitte 100 USD** | **100 USD** kaldı — koşullu modelin AL/SAT emri çıkarmaması; kâr kanıtı değil |
| **Başta altın alıp sonda bozdurma referansı** | **≈98,323 USD**, vendor MID ve %0,8 alım + %0,8 satım indirimi varsayımı, gerçek banka kotasyonu değil |

**Dikkat:** Önceki 2022 ön-eğitimli shadow sonucuyla PUP yüzdeleri karşılaştırılırken o farklı öğrenme tasarımı göz önünde bulundurulmalı. Bu yeni koşu daha dürüst kronolojiyi kullanır, fakat geçmiş olay/ekonomik etiketler **S1 tahmin ağırlığına eklenmiş değildir.**

## 3. Çift saat gerçekten hangi bilgiyi ekliyor?

- 3 Şubat **ilk 15dk**: eski S2 `NEUTRAL`; olay E `−%1,349` düşüşü ayrı ölçer. +60dk E `−%1,731`; o anda S1 fiyat-only `P(UP 4s)=0,547`, yaklaşık beklenen +%0,025 ve S2 `NEUTRAL`. **Farklı ölçüm pencereleri çelişebilir**. E geçmiş şoku kaydeder; kalan −%0,934 dört saatlik hareket sadece daha sonra bilinir.
- 2 Şubat ECB +60dk: G S2 `CONTINUE DOWN`, E `−%0,340`; S1 4s fiyat-only `P(UP)=0,598`, beklenen +%0,057. Sonraki 4s gözlenen **−%1,702**. Haber kanıtlı ORG02 değildi; K39/ORG01/ORG02 açılabilir, ancak USD/reel-faiz ve özgün beklenme verisi yok.
- 14 Şubat: ilk 15dk E `+%0,063`, +60dk `−%0,600`, ondan sonraki 60dk `+%0,508` → *kümülatif olay yönü sonraki yönün garantisi değildir*. S2 hâlâ `NEUTRAL`.
- Ocak 6: ilk M15 E pozitif ama 15dk sonrasından sonraki 60dk **−%0,333**; erken tepkiyi ilk anda trade kuralı yapmak gerçek risk taşır.

## 4. Küçük örnekli karşılaştırma, ALFA değil

**Haber+60dk anından sonraki dört saat**, önceden seçilmiş altı ayrık haber dönemi: 6 Ocak, 12 Ocak, 1 Şubat, 2 Şubat ECB, 3 Şubat, 14 Şubat. Fed veri yolu koptuğu için **5 değerlendirilebilir olay** vardır. Diğer iki Şubat 2 açıklaması (BoE/ECB konuşması) bağımsız örnek sayılmadı.

| Sinyal (haber+60dk'da) | Sonraki 4s yönü doğru | Yanlış | Çekimser |
|---|---:|---:|---:|
| S1 4s beklenen getiri işareti | **1** | **4** | 0 |
| Orijinal S2 fiyat evresinin yönü | **2** | 0 | **3** |
| Olaydan beri gerçekleşen ilk saat E yönü (naif devam varsayımı) | **4** | **1** | 0 |

`E` geriye dönük gerçekleşmiş hareket işaretidir, **eğitilmiş tahmin değil**; bu karşılaştırma 5 seçilmiş olaydan nedensel tahmin gücü genellemesi kuramaz. S1 tahminleri çoğu +/−%0,001 ila 0,07 düzeyinde küçük, işaret karşılaştırması ekonomik önem göstergesi değildir.

**Bankadaki long/cash modelinin maliyet kontrolü:** Haber+60dk'dan sonraki dört saatte **bu 5 örneğin hiçbirinde altın yükselişi %1,594'ü aşmadı**. ECB'nin +60dk'dan sonraki büyük düşüşü nakitte yeni BUY için kâr fırsatı değildir; hâlihazırda GOLD tutuluyorsa önlenebilecek riski araştırmak ayrı bir S3 switching çalışmasıdır. Bu karşılaştırma AL/SAT simülasyonu veya strateji getirisi değildir.

## 5. Bilimsel eksikler

1. 2023 Ocak–Şubat **bütün haber takvimi değil**: PCE, GDP, PPI, ISM, Avrupa/Çin/jeopolitik/fizikî talep eksik. 8 resmî odak noktası yeterli genel performans evreni değil.
2. Orijinal `actual/consensus` PIT, saatlik USD endeksi, **gerçek ABD reel getirileri**, piyasa OI/fonlama ve aynı-UTC kaynaklar eksik. Orijinal `event_news_condition_router` bu nedenle ekonomi içeriğinde UNKNOWN tutabilir. `K03/K02/K19` geriye dönük araştırma proxy'si canlı girişe dönüştürülmedi.
3. `H1` ilk haber ve `H2` ara kanal doğrulanmadan gerçek nedensellik atfedilemez; örneğin 2 Şubat üç merkez bankası gelişmesinin getiri payları ayrı bilinmiyor.
4. Olay odaklı S1 koşullu ileri yön, kalan getiri, hızlanma ve süre **henüz eğitilmedi**; mevcut S1 ve S3'e ekonomik K/ORG dahil edilmedi. İlk gözlemsel uyum S3 ticari alfa değildir.
5. 2023 sadece **kronolojik ilk öğrenme ayları**; bu ayda ölçüp bu aya kural fit ederek aynı ay getiriyi "out-of-sample" raporlamak yanlış. 2024/2025 bağımsız ileri yıl ve olaysız karşıt testleri şart.

**Raporun tam ham çıktısı:** [GOLD_UNIFIED_MECHANISM_FULL_JAN_FEB_2023_RESULTS_20261018.json](GOLD_UNIFIED_MECHANISM_FULL_JAN_FEB_2023_RESULTS_20261018.json)

**Tekrar çalıştırma kodu:** [replay_janfeb_2023_unified_mechanism_full_v1.js](replay_janfeb_2023_unified_mechanism_full_v1.js)

**Son durum:** `CORE_REAL_PRICE_REPLAY=EXECUTED`; `NO_2022_PRETRAIN=PASS`; `ALL_39_QUALIFIED_SESSIONS=PASS`; `8_EVENTS_SHADOW=EXECUTED`; `MACRO_MECHANISM_ASOF_VERIFIED=FAIL`; `S1_EVENT_CONDITIONED_TRAINING=NOT_DONE`; `S3_NET_TRADE_ALPHA=NOT_PROVEN`; `REAL_BANK_ORDERS=NONE`.
