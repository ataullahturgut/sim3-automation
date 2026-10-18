# ETKİ-05 — Ekonomik koşullardan fiyat etkisinin yön, şiddet, süre ve dönüşünü öğrenme: ilk grup denetimi

**Tarih:** 2026-10-18 · **Proje:** GOLD-ADAPTIVE-MODEL-APP-01 · **Durum:** ARAŞTIRMA / TAKSONOMİ TASLAĞI · **Karar yetkisi:** YOK  
**Kaynak otoriteleri:** OLAY-02 tarihli kanıt, ÖĞREN-03 tarihsiz ekonomik DNA. Bu dosya ayrı bir ETKİ çalışma alanıdır; iki kaynağın içeriğini değiştirmez. Matematiksel CORE, işlem motoru, geçmiş sonuçlar ve gerçek ekonomik kural sicili bu araştırma sırasında değiştirilmedi.

## Sorun ve sonuç

Hedef, küçük XAU hareketlerini alıp satmak değil: **aynı ekonomik örgünün hangi koşullarda küçük, orta veya büyük UP/DOWN; hangi koşullarda gecikmeli, kalıcı, sönümlenen ya da terslenen tepki üretebileceğini öğrenmek.** Gün/tarih bir öğrenilen ekonomik kuralın kimliği değildir. OLAY-02'deki ex-post fiyat yönü olayın ekonomik nedeninin kanıtı değildir.

**İlk kavramsal karar: 5 ana ekonomik ETKİ grubu + 1 karma/kanıtsız yönlendirme durumu.**  
Aşağıdaki örnek adetleri, 38 derin vaka arşivinin **primary_plot_candidate_id** alanını *birincil taslak grup* olarak bir kez saymaktan ibarettir; nedensel doğrulanmış örnek veya birbirinden bağımsız 38 şok anlamına gelmez. Bu 38'in bir bölümünün eski `MOVE_V2_C...` kimlikleri, yeni `C_CORR_...` fiyat etiketleriyle **numara sırasından eşlenemez**; bu nedenle 38 sayıları 96 güncel sayısal fiyat sonuçlarıyla vaka bazında birleştirilmedi.

| Birincil etki sınıfı | ÖĞREN-03 örgüleri | Derin arşiv birincil aday adedi (38) | Ayırt edici ekonomik soru | Statü |
|---|---|---:|---|---|
| **E01 — Faiz, reel getiri ve USD fırsat maliyeti** | ORG01 + ORG02 | **15** | Makro sürpriz, beklentiye göre faiz/USD yeniden fiyatlamasını ne kadar kuvvetlendiriyor; karşıt risk primi baskın mı? | **En geniş araştırma ailesi; kesin nedensellik yok** |
| **E02 — Risk primi oluşumu ve çözülmesi** | ORG03 + ORG04 + ORG05 + ORG06 + ORG07 | **13** | Bankacılık, güvenlik veya ticaret haberleri risk primini oluşturuyor mu, söndürüyor mu? Fonlama kaynaklı nakit ihtiyacı ters baskı yaratıyor mu? | **Heterojen; oluşum/sönme ayrı alt yol olmalı** |
| **E03 — Rezerv, fizikî ve finansal talep birikimi** | ORG09 | **3** | Fizikî talep, rezerv ve pozisyon akımları anlık tepkinin ötesinde birikerek gecikmeli fiyat etkisi yaratıyor mu? | **Az destekli araştırma adayı** |
| **E04 — Likidite / teminat kaynaklı zorunlu tasfiye ve dönüş** | ORG08 + ORG12 | **3** | İlk haber riskli varlıklardan toplu nakit çıkışına dönüşüyor mu; satış sonrası sığınak alımı geri geliyor mu? | **Az destekli araştırma adayı** |
| **E05 — Doygunluk, kâr alma ve pozisyon çözülmesi** | ORG10 | **3** | Önceki trendin yorgunluğu ve pozisyon yoğunluğu, küçük ters tepkiyi büyütebiliyor mu? | **Az destekli araştırma adayı** |
| **EX — Rakip ekonomik aktarım / belirsizlik** | ORG11 | **1** | Rezerv/merkez bankası bilgisi ile makro/faiz açıklaması rakip kanallar oluşturuyor mu? | **Altıncı kanıtlı mekanizma sayılmaz, belirsizlik/fallback sınıfı** |
| **Toplam** | ORG01–ORG12 | **38** | | |

Aynı vaka hem tetik (E02), hem aktarım (E01), hem kuvvetlendirici (E04/E05) taşıyabilir. Birincil atama, çoklu mekanizmanın gerçek hayattaki tek etkene indirgenmesi değildir. E02'de ticaret politikası enflasyon/faiz kanalına kayarsa E01 aktarımı ayrıca değerlendirilir.

## Farklı bağımsız arşivlerde gözlenen kapsama

**96 OLAY-02 fiyat kaydı / ekonomik alt-tip belge taraması:** G01-A/B/X **34**, G02/G03/G05 **20**, G04 **9**, G06 **5**, belirsiz G07 **28**. E04 zorunlu satışın ayrı ilk-etiketi **0**; E04'ü 96 kayıttan kalibre edilmiş güçlü sınıf gibi gösterme. Bu 96 etiketin **43'ü spesifik alt-tip adayı, 25'i genel makro, 28'i belirsiz**; kanıt seviyesi D2 **18**, D1 **56**, D0 **22**. İlk neden/ilk fiyat başlatma teyidi **0/96**. Ayrıca **96 kimlik = 84 tekil 09:15 kontrolü**; 12 mükerrer checkpoint iki bağımsız örnek değildir. Bu alt-tip taraması ve 38 örgü eşlemesi farklı şemalardır, yüzdeleri ve adetleri toplanamaz.

**85 CPI/NFP/FOMC tarihli makro duyurusu:** İlk 15 dakika mutlak XAU tepkisi dört önceki haftanın aynı saatindeki kontrol ortalamasını **66/85** yayında aşmış. İlk 15dk ile ilk 60dk tepki yönü **64 SAME**, **20 REVERSE**, **1 MISSING**. Bu, aynı haber ailesinde ilk reaksiyonun devam veya tersine dönüşünün ayrı öğrenme hedefleri olması gerektiğini gösterir; makro haberin hareketin birincil nedeni olduğunu ve gelecekte bu tepkinin tahmin edilebildiğini kanıtlamaz.

**İlk 60 dakika ex-post gelişim alt etiketleri (84 tam kayıt):** Farklı ETKİ ailesi değildir, bütün ailelere uygulanacak bir `path_shape` boyutudur. İlk15 ve kümülatif ilk60 getirilerinin işaretine ve mutlak oranına göre: işaret değiştiren **20**, aynı işarette fakat büyüklüğü yarıdan aza sönen **13**, aynı işarette 1,5 kattan fazla büyüyen **19**, aynı işarette oranı 0,5 ile 1,5 arasında kalan **32**. **Bir kayıt eksik.** 0,5 ve 1,5 oranları *ilk araştırma tarifidir*, öğrenilmiş optimum eşik veya fiyat sebebi değildir; ilk15 hareketi sıfıra yakınsa oran gürültüye aşırı hassas olur. Bu sebeple modelde asgari ilk etki, oynaklık ve kontrol sınamaları olmadan kullanılamaz. Mevcut 85 seride 4s sonucu FOMC için eksik olduğundan dört saat süre sonuçları bütün 85'e genellenemez.

## Örnekler — aynı haber adının farklı tepki yönü ve şiddeti

Bunlar **resmî duyuru sonrası ex-post pencere getirileri**, as-of GPT tahmini, doğrulanmış ekonomik neden veya AL/SAT sinyali değildir.

| Makro pencere | İlk 15dk | İlk 60dk | İlk 4saat | Ayırıcı araştırma sorusu |
|---|---:|---:|---:|---|
| 6 Ocak 2023 NFP | +%0,644 | +%0,542 | +%1,391 | Ücret/fırsat maliyeti kanalı, güçlü istihdam karşı kanalını hangi göstergelerle bastırdı? |
| 3 Şubat 2023 NFP | −%1,349 | −%1,731 | −%2,611 | Faiz/USD şahin kanalı ve önceki piyasa konumu düşüşü nasıl büyüttü? |
| 10 Mart 2023 NFP | +%0,540 | +%0,841 | +%1,551 | Güçlü istihdama rağmen bankacılık riski/güvenli liman baskın mıydı? |
| 14 Şubat 2023 CPI | +%0,063 | −%0,600 | −%0,693 | İlk tepki neden bir saat içinde yön değiştirdi? |

**Bu örneklerden hareketle otomatik E01/E02 sınıfı atanmaz**; olay öncesi makro konsensüs-vintage, ilk yayın zamanı ve as-of eşzamanlı USD/faiz/diğer varlıklarla doğrulama gerekir.

## ETKİ-05 veri sözleşmesi — ekonomik aile ≠ hareket sonucu

Her araştırma gözlemi için ayrı alanlar:

1. `economic_roles`: `TRIGGER`, `TRANSMISSION`, `AMPLIFIER`, rakipler ve ORG kodları; her biri zaman/kaynak/kanıt derecesiyle.
2. `prior_state`: sürpriz beklentisi, DXY, nominal/reel faiz, diğer metaller, piyasa riski, likidite, mevcut altın trendi, pozisyon / doğrulanmış availability-as-of.
3. `response_direction`: UP / DOWN / MIXED / UNRESOLVED; tek ekonomik ailenin sabit yönü yok.
4. `response_scale`: **SMALL / MEDIUM / LARGE / UNKNOWN**, fakat yalnız fiyatın çıplak yüzde değeriyle değil; ilgili 15m/60m/4h/1/3/5 seans ufku, eşsaat kontrol ve rejim oynaklığı/quantile standardı ile. Mutlak yüzde ayrıca tutulur.
5. `path_shape`: başlangıçta sınırlı, sönümlenen, tutunan, hızlanan, tersine dönen, çok-dalgalı / unknown. Zamansal sınıf, sonradan bilinen sonuç etiketidir.
6. `duration_and_invalidation`: fark edilme gecikmesi, tepe zamanı, geri dönüş, nedenin sönmesi, yanlışlayıcı kontrol.
7. `evidence`: özgün tarihli kaynak, tespit anı, first-print, olaysız/karşıt vaka, kontrol, örnek tekrarı, konusuz fiyat şoku, bilinmeyenler. Veri yokken otomatik fill yok.
8. `decision_authority`: NONE. Etki sınıfı sonucu tek başına AL/SAT değildir; maliyet ve eylem değeri S3'ün ayrı görevidir.

**Etkili ayrım şeması:** 5 birincil ekonomik aile **×** 3 büyüklük sınıfı **×** UP/DOWN/MIXED yönü **×** süreç biçimi. Bunlar 5×3×3×... bağımsız ve istatistiksel olarak güvenilir alt-grup demek değildir. Veri seyrekse hücreler birleştirilmeli veya UNKNOWN kalmalı; salt örnek sayısı tamamlamak için uydurma kayıt eklenmemeli.

## Bilimsel kabul ve sonraki doğrulama

- **Aşama A — Grup denetimi:** Tek bir vakayı iki kez saymadan, önce `38 legacy-V2 → C_CORR` güncel kimlik/aile eşlemesini kaynak kanıtıyla açıkça çöz; çözülmeyenleri 96 sayısal sonuca katma. 84 tekil checkpoint için bağlı olay/etiket ve ilk haber zamanını ayrı belgele.
- **Aşama B — Ekonomik etki ayrıştırması:** 85 tarihli makro duyuruda ilk-yayın actual/consensus eski vintage; ilk 15/60/240dk eşzamanlı XAU-USD-faiz-metaller; olaysız eşsaat ve karşıt haber kontrolü. Retrospektif fiyat biçimini ekonomik sebep diye sunma.
- **Aşama C — Şiddet dağılımı:** Farklı ufuklarda matched placebo koşullu `P(SMALL/MEDIUM/LARGE,UP/DOWN,patika | asof ekonomik durum)` ölç; minimum destek ve kalibrasyon kontrollerini raporla. Gizli lookahead yasak. 96 seçilmiş ZigZag/çok-ufuk fiyat bacağı evreni rastgele olay evreni değildir; koşullu olasılık için taban oran kabul edilemez.
- **Aşama D — Kör/ileri sınav:** Kuralları ve eşikleri testten önce dondur, izlenmeyen yeni olaylarda ve farklı rejimlerde Brier/log-loss, etki büyüklüğü hatası, kapsama, yanlış alarm, sessiz kalma oranı ile ekonomik bağlamı olmayan baz modeli kıyasla. Neden zinciri / büyüklük üstünlüğü kanıtlanmadan `MODEL_SCIENCE_GATE=FAIL`.
- **S3 veya uygulama bağlama:** Yalnız bilim kapısından sonra adapter ile; sırf ETKİ-05 oluşturuldu diye CORE işlem veya canlı GPT varmış gibi gösterme.

## Bağlı kanıt dosyaları

- [ÖĞREN-03 — Tarihsiz ekonomik DNA](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md)
- [OLAY-02 — tek olay otoritesi](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md)
- [38 derin vaka ve ORG birincil/ikincil aday eşlemesi](OLAY_02_38_DERIN_VAKA_OLAY_ORGUSU_ARSIV_ESLESMESI_20261014.csv)
- [96 kaynak — alt-tipler ve roller](OLAY_02_96_KAYIT_DNA_ALT_TIP_ROL_TARAMA_20261014.csv)
- [96 sayısal fiyat kontrolleri ve farklı ufuklar](OLAY_02_96_VAKA_FILITRELENEBILIR_KARAR_KATALOGU_20261014.csv)
- [85 makro olay, matched-placebo ve zamanlı yanıt](OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv)
- [96 olay çoklu çıkarım, kanıt düzeyleri ve sınırlar](OLAY_02_COKLU_EKONOMIK_DNA_CIKARIM_SONUCLARI_20261014.md)
