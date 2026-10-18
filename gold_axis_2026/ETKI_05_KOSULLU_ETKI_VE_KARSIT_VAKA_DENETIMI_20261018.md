# ETKİ-05 — Koşullu fiyat etkisi ve karşıt-vaka araştırması (Aşama B)

**18 Ekim 2026 | GOLD-ADAPTIVE-MODEL-APP-01 | RESEARCH_ONLY | SCIENCE_GATE=FAIL | LIVE_TRADE=false**

ÖĞREN-03, OLAY-02 ve matematiksel CORE **değiştirilmedi**. Bu bağımsız ETKİ-05 çalışma alanında, "neden aynı ekonomik olay bir seferinde küçük UP, başka bir seferinde büyük DOWN yaratıyor?" sorusu için veri ve karşıt örnek incelemesi yapıldı. **Etki grupları bilimsel tahmin kanıtı değil, sınanabilir hipotezlerdir.** Sonradan gerçekleşen dalga boyunu önceden biliyormuş gibi kullanma.

## 1. Kapsam, veri doğruluğu ve yöntem

- ÖĞREN-03'teki 12 olay örgüsü, 38 derin vaka arşivindeki **birincil araştırma hipotezine göre** 5 ekonomik etki ailesi + 1 çatışma/belirsizlik durumuna bağlandı: E01 15, E02 13, E03 3, E04 3, E05 3, EX 1. Bunlar birbiriyle ilişkisiz 38 bağımsız şok anlamına gelmez; bir vakada ikincil ORG mekanizmaları mevcuttur.
- 96 sayısal olay kaydının **84 farklı karar kontrol noktası** vardır; 12 çift kontrolü bağımsız örnek diye iki kez sayma. 96 içindeki alt-tipler: **34 G01** (4 G01-A + 5 G01-B + 25 G01-X), **20 G02/G03/G05**, **9 G04**, **5 G06**, **28 belirsiz G07**. Belge dayanağı 18 D2, 56 D1, 22 D0. **İlk haberin fiyat dalgasını başlatması 0/96 doğrulanmış.**
- 38 eski vaka arşivindeki `MOVE_V2_C...` ile 96 yeni `C_CORR_...` kimlikleri sayısal sıradan eşlenemiyor. **E03/E04/E05'in seyrek kanıtını artırmak için sahte eşleme yapılmadı.** Yalnız birebir `SWING_V1_...` vakaları tarihli ZigZag bacağı sonuçlarıyla ayrıca betimlendi; ZigZag bacakları büyük hareket seçilerek oluştuğu için küçük/büyük etki olasılığı hesaplamakta temsili örneklem değildir.
- Doğrudan saatli olay incelemesi için ayrı **85 makro açıklama** kaydı kullanıldı: 34 CPI, 35 NFP, 16 FOMC. İlk 15 ve ilk 60 dakika pencere sonuçları, dört önceki haftanın aynı saatli kontrol ortalamasıyla karşılaştırıldı. Sonraki 4s sonuçları **34 CPI + 34 NFP** için var; **FOMC 4s tüm 16 kayıtta EKSİK**.
- Ek kontrol olarak Neon `gold_research_evduka_xau15m_bidask_candidate` üzerinde her açıklama için **olay zamanından kesinlikle önce tamamlanmış en son 17 M15 barın** ilk/son orta fiyatından 4s önceki altın eğilimi yeniden ölçüldü. **84/85** olayda kesintisiz 17 bar (240 dakika) bulundu; 1 olayda fiyat verisi yok. **Bu özellik geçmişte bilinebilir fiyat geçmişidir; makro actual+consensus'un özgün ilk yayımlanma vintage'ı hâlen onaylı değil.**
- Örnek koşullu sınama için, **yalnız betimleyici** 4s `abs(XAU_return) >= %1` büyük eşik kullanıldı. Bu ufka özgü sabit eşik gerçek ETKİ sınıfı değildir; sonradan rejim oynaklığı, aynı-saat plasebo ve veriye sızmayan dış dönem kalibrasyonuyla düzeltilmesi gerekir.

## 2. E01 — Gerçek karşılaştırma: sürpriz yönü ve önceki altın eğilimi

| Öncesinde/anında tanımlanan makro koşulu | 4saat tam gözlem | Gerçekleşen yön | 4saat >= %1 mutlak tepki |
|---|---:|---|---|
| **CPI beklentiden düşük** (dovish aday) | 13 | **11 UP**, 2 DOWN | **5 büyük UP** |
| **CPI beklentiden yüksek** (hawkish aday) | 8 | **5 DOWN**, 3 UP | **2 büyük DOWN** |
| **CPI sürprizi sıfır** | 13 | **10 DOWN**, 3 UP | **2 büyük DOWN** |
| **NFP istihdam beklentiden güçlü** | 23 | **13 DOWN**, **10 UP** | **5 büyük DOWN + 4 büyük UP** |
| **NFP istihdam beklentiden zayıf** | 11 kullanılabilir / 12 kayıt | **6 UP**, 5 DOWN | **2 büyük UP** |

**Olası E01 ayrıştırması:** CPI yön sürprizi altının ilk fiyat yönüne ilişkin farklı geçmiş dağılımlar oluşturuyor. Fakat NFP yalnız toplam istihdam sürpriziyle ekonomik etkiyi açıklamıyor; ücret, işsizlik, önceden fiyatlanmış Fed patikası, USD/nominal-reel faiz ve finansal stresin rakip kanalları gerekli. Bu ilişkiler önceden geçerli ekonomik kural/işlem kararı kabul edilemez.

**Önceki piyasa koşulu için ilk somut test:** Neon M15 `pre4h` fiyat değişimi yalnız açıklamadan **önce tamamlanmış** barlardan hesaplandı.
- **Pozitif CPI sürprizi + öncesinde altın 4s UP:** **4/4** sonrasında DOWN, bunların **2/4**'ü <=−%1 (4s). Aynı pozitif CPI sürprizi + önceki 4s DOWN: **3/4** sonrasında UP, **hiçbiri >=|%1| değil**. Bu ilgi çekici bir *karşıt koşul*, ama **n=4** hücrelerinden genellenebilir kural çıkmaz; öngörü doğrulaması yapılmadan kullanılmaz.
- **Negatif CPI sürprizi + öncesinde 4s UP:** **4/4** sonraki 4s UP (2 büyük). Öncesinde 4s DOWN ise **7/9** UP (3 büyük), **2/9** DOWN. Dolayısıyla yön sürprizinin etkisi önceki fiyat eğiliminden bütünüyle bağımsız veya mutlak değil.
- **Pozitif NFP sürprizi + öncesinde 4s UP:** **8/13** sonraki 4s DOWN, **5/13** UP; **4/13** büyük DOWN, **2/13** büyük UP. Öncesinde 4s DOWN ise **5/10** DOWN, **5/10** UP. Etkiyi fiyat rejimi tek başına ayrıştırmıyor.

**Ekonomik karşıt vakalar:**
- **NFP 6 Ocak 2023:** istihdam +23k sürpriz; XAU ilk 15dk **+%0,644**, 4s **+%1,391**. Güçlü istihdamın basit "şahin → DOWN" kuralı ters.
- **NFP 3 Şubat 2023:** istihdam +332k sürpriz; XAU ilk 15dk **−%1,349**, 4s **−%2,611**. İstihdam şahin baskısı hipoteziyle tutarlı fakat tek başına gerçek USD/faiz aracılık kanıtı değil.
- **NFP 10 Mart 2023:** istihdam +106k sürpriz; XAU ilk 15dk **+%0,540**, 4s **+%1,551**. Bankacılık güven riski/alternatif kanal adayı; doğrulanmış olay nedeni değil.
- **CPI 13 Haziran 2023:** düşük sürprize rağmen 4s **−%0,712**; **CPI 11 Haziran 2025:** düşük sürprize rağmen 4s **−%0,250**.
- **CPI 10 Ekim 2024:** yüksek sürprize rağmen 4s **+%0,529**; **CPI 12 Şubat 2025:** yüksek sürprize rağmen 4s **+%0,992**.

**İlk hipotez:** E01'de "küçük/büyük" sonuç, haber başlığı ile değil **surprise bileşenleri × öncesi piyasa × bağımsız faiz/USD teyidi × rakip E02/E04 etkisi** ile araştırılmalı. Gerçek-time USD/reel getiri birikmiş ve kanıtlı değilse bilinmiyor olarak bırak.

## 3. Birinci saat — Büyüme, sönme ve tersine dönme aynı olay ailesinde farklı

85 makro açıklamada ilk 15dk mutlak tepki, dört hafta önceki aynı saat kontrol ortalamasından **66/85** kez büyük; bu **yön tahmini veya nedensellik kanıtı değil**.

İlk 15dk ile kümülatif ilk 60dk arasındaki işaret/büyüklük (84 tam vaka):

| Ex-post ilk saat davranışı | Sayı | Tanım (araştırma amaçlı) |
|---|---:|---|
| Aynı yönde benzer büyüklük | **32** | Kümülatif 60dk / mutlak ilk15 oranı **0,5–1,5** ve işaret aynı |
| Aynı yönde büyüme | **19** | İşaret aynı; 60dk büyüklüğü ilk15'in **>=1,5 katı** |
| Aynı yönde sönme | **13** | İşaret aynı; 60dk büyüklüğü ilk15'in **<0,5 katı** |
| İşaret tersine dönme | **20** | İlk15 ve 60dk kümülatif tepki ters |
| Eksik | **1** | Veri yok |

**Yöntem uyarısı:** İlk15 sıfıra yakınsa oran çok büyük ve anlamsız olabilir; bu sınıflar şiddet tahmini değil gerçekleşmiş patika tasnifidir. İleri modelde normal oynaklığa göre asgari ekonomik tepki, başlangıç zamanı ve plasebo şartı aranmalı.

**Kritik örnek:** 14 Şubat 2023 CPI ilk15 **+%0,063** iken ilk60 **−%0,600**, ilk4s **−%0,693**: *ilk tepkiyi nihai olay etkisi gibi etiketlemek yanlış olur.*

## 4. E02–E05: Her grubun ayrı koşulu ve mevcut bilimsel sınır

| ETKİ | İlk karşılaştırılmış örgüler | V1'daki tarihli uzun bacak gözlemi | Ayırmak için zorunlu eksik veri / koşul | Bilimsel değerlendirme |
|---|---|---|---|---|
| **E02: Risk primi** | ORG03–07 | 6 seçilmiş uzun bacak: **4 UP / 2 DOWN** | Olayın **yeni mi zaten fiyatlanmış mı** olduğu; ilk güvenlik/banka/ticaret haberinin zamanı; likidite ve USD/faiz kanalı; gevşeme/de-eskalasyon karşı olayı | Aynı ailede zıt yön var, **etki büyüklüğü kalibrasyonu yok** |
| **E03: Talep birikimi** | ORG09 | 2 seçilmiş uzun V1 UP; bir üçüncü eski V2 vaka | ETF, COMEX, rezerv/OTC/fizikî akımın özgün yayın gecikmesi; talep artışı ile faiz/dolar ayrıştırması | **EKSİK / seyrek**; zamanlı akış olmadan küçük/büyük dağılımı yok |
| **E04: Zorunlu tasfiye** | ORG08, ORG12 | Yalnız 3 eski V2 adayı; birebir doğrulanmış V1 **0** | Marjin/fonlama/derinlik göstergesi; birlikte satılan varlıklar; likidite normalleşmesi sonrası sığınak talebi; eski V2 ID doğrulaması | **EKSİK / en yüksek öncelikli kanıt açığı** |
| **E05: Doygunluk ve kâr alma** | ORG10 | 2 seçilmiş uzun V1 DOWN; ayrıca 1 eski V2 | Önceki fiyat/pozisyon aşırılığı, yüklenme yaşı, gerçekleşmiş kâr alma akımı, yeniden giriş/uzama karşı-vaka | **EKSİK**; seçilmiş düşüşler büyük olasılık anlamına gelmez |
| **EX: Çatışma** | ORG11 | 1 seçilmiş uzun V1 DOWN | Aynı gün ayrı ilk haberlerin rol ve saatleri (örn. rezerv alım haberi ve ABD NFP) | **UNKNOWN yönlendirmesi**, ayrı kanıtlı olay DNA'sı değil |

**Birincil uzun V1 karşıt örnek kimlikleri:** E02 için SWING_V1_003 (UP, bankacılık stresi ve faiz indirimi beklentisi) vs SWING_V1_032 (DOWN, ticaret rahatlaması), SWING_V1_034 (DOWN, gerilim çözülmesi); E03 için SWING_V1_013/015 (UP); E05 için SWING_V1_014/018 (DOWN). Bunlar geriye dönük seçilen geniş ZigZag bacaklarıdır; ekonomi aynı anda birden fazla haber içerebilir.

**E04 ve E05 fiyatın DOWN işaretinden doğrulanmış "zorunlu satış" veya "kâr alma" sonucu çıkarma.** Nedeni açıklayan yayın/akım/fonlama saatini ve aksi sonuçlu vaka ailesini bulmadan ciddi şiddet öğrenimi yapılamaz.

## 5. Zaman dışı öngörü denetimi — gerçekten daha iyi mi?

Hedefler: CPI/NFP **olay sonrası 4s UP** ve **mutlak 4s değişimin %1'i aşması**. 68 tam kayıt. Sadece `event kind` taban oranına karşı `kind + actual-consensus surprise sign` koşulunu kıyaslayan **Laplace (1/1) öncüllü olasılık** araştırması yapıldı; en eski yıllar önceki eğitimden alınarak sırayla 2024, 2025 sonuçları değerlendirildi. Bu bir **keşif sonrası kronolojik kıyas**, dondurulmuş bağımsız kör test değil.

| Yalnız 2025 ileri yıl değerlendirme: 21 kayıt | Yalnız makro türü (baseline) | Tür + sürpriz işareti |
|---|---:|---:|
| Sonraki 4s **UP** Brier (düşük iyi) | **0,29237** | **0,29067** |
| Sonraki 4s `abs(return)>=1%` Brier | **0,20392** | **0,23232** |

**Kesin sonuç:** Sürpriz bilgisi yön için **çok sınırlı** avantaj verdi; ancak **büyük hareketi tahmin etme kalitesini kötüleştirdi**. 2024 yön kıyasında bile baseline **0,24904** iken surprise **0,25213**. Dolayısıyla "**büyük hareketin koşullarını öğrendik**" sonucu **YOK**. Bu tablo, ETKİ-05'in gerçek hedefini doğrulamanın henüz erken olduğunu gösterir. İkinci teyitli kaynak gerçek as-of USD ve faiz kanalları olmadan sinyal üretme.

**Eksik kanıt**: tam 85 release için özgün actual+consensus ilk-baskı yayın provenance (FOMC sürpriz alt bileşenleri yok), FOMC 4s fiyat hedefleri, faiz/USD/Gümüş eşzamanlı as-of panel, E02–E05 ailelere ait açıklama saati bağımsız örnekler, 38 eski V2 güncel kayıt eşlemesi, büyük hareket için volatilite normalize edilmiş hedef tanımı.

## 6. ETKİ-05 modeline önerilen öğrenim kaydı (veri doldurulmadan kural değildir)

`event_source_id, asof, org_roles, prior_state, verified_macro_actual_consensus, signed_surprise, independent_cross_asset_reaction, competing_mechanisms, negative_controls, response_direction, response_magnitude_horizon, persistence_reversal_path, invalidation, uncertainty, mechanism_evidence_status, outcome_available_at`.

- **As-of kuralları**: ileri getiri ve gerçekleşmiş olay şekli sadece label; ilk haber erişimi kanıtlanmadıysa model özelliği `UNVERIFIED`; haber sonrası 15dk tepkisi yayın öncesi kararın girdisi olamaz.
- **Örnekleme**: 96 şok-seçilmiş ZigZag/V2 sonuçları, tüm saatlerin fiyat dağılımı gibi kullanılmaz; 84 tekil checkpoint korunur. 85 makro release duyuru örneklemi farklıdır; evrenler birleştirilirken olay ve kontrol kimliği eşleşmesi gerekir.
- **Büyüklük**: SMALL/MEDIUM/LARGE, 15m,60m,4h,1/3/5 seans ayrı; gelecekte baz alınacak normal oynaklık/aynı-saat plasebo dağılımıyla yurt dışı yıl testinde kalibre et. Veri bulunmadığında `UNKNOWN`.
- **Yetki**: `TRADE_ALLOWED=false`; ETKİ-05 analizi CORE S3'ün gerçek banka AL/SAT kararını değiştirmez.

## 7. Kaynaklar

- [ÖĞREN-03 ekonomik mekanizmalar](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md)
- [OLAY-02 tarihlenmiş olay otoritesi](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md)
- [38 birincil/ikincil örgü eşleştirmesi](OLAY_02_38_DERIN_VAKA_OLAY_ORGUSU_ARSIV_ESLESMESI_20261014.csv)
- [96 G aile/alt-tip kayıtları](OLAY_02_96_KAYIT_DNA_ALT_TIP_ROL_TARAMA_20261014.csv)
- [96 tarihli ölçüm/84 benzersiz kontrol](OLAY_02_96_VAKA_FILITRELENEBILIR_KARAR_KATALOGU_20261014.csv)
- [85 makro açıklama ve 4 karşı hafta kontrolü](OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv)
- [ETKİ-05 makine-okunur sözleşme](ETKI_05_MECHANISM_IMPACT_HYPOTHESES_V1_20261018.json)

**Kabul durumu:** Etki aileleri oluşturuldu, karşıt etki yönleri ve sürpriz/öncü fiyat ilişkileri nicelleştirildi. **Güvenilir büyüklük öngörüsü, ekonomik neden doğrulaması ve işlem değeri başarı eşiğini geçmedi.** İşlem modeline taşınmaz.
