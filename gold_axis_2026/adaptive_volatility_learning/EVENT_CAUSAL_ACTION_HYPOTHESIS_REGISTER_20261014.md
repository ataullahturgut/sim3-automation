# ÖĞREN-03 — ÇIKARIM VE OLAY KARAKTERİ MANİFESTİ
**ALTIN XAU/USD • Sürüm 2 • 14 Ekim 2026 • ARAŞTIRMA / EX-POST KARAKTER ANALİZİ**

**KİM NEYİ YÖNETİR:** [ANA-01](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) proje yöntem/strateji sözleşmesidir; [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) olay–haber–piyasa veri ve kararların **tek kanıt otoritesidir**. **ÖĞREN-03 (bu dosya) artık ÇIKARIM MANİFESTİDİR:** olayları karakter ailelerine ayırır, her ailenin **önkoşul–başlangıç–gelişim–bitiş–ters vaka** profilini tutar ve neden/karar hipotezlerini burada araştırır. [DURUM-04](months/2023-01/STATE.json) aylık çalışma durumudur. **Mevcut üç hipotez bu dosyada aşağıda korunmuştur; yeni müstakil bir çıkarım dosyası oluşturulmadı.**

## 0. Çıkarım sonucu: kaç tür olayımız var?

- **7 aday ekonomik aile:** **6 ana mekanizma ailesi + 1 KARMA/BELİRSİZ**. Bunlar eski araştırmacıların haber bağlamına dayalı retrospektif sınıflandırmasıdır; öğrenilmiş, ilk yayımları doğrulanmış veya ekonometrik nedenselliği ispatlanmış cluster değildir.
- **5 ölçülmüş uzun fiyat yaşam-döngüsü tipi:** 42 NY17 V1 uzun fiyat bacağının **41'i** 06:00 UTC günlük XAU M15 örnekli ve en az 4 gün gözlemlenmiş; **1'i çok kısa**. Bunlar ekonomik neden gruplarıyla kesişir ama aynı şey değildir.
- **5 kısa-ufuk kontrol sonucu tipi:** 54 V2 kümesinin 09:15 TRT kontrol noktasından 4 saat / 12 saat / 3 seans **gerçekleşen** hareket karakteri; **bu V2 fiyat şokunun gerçek başlangıç dakikası olduğu iddiası yoktur.**
- **96 kayıt ≠ 96 bağımsız ekonomik şok:** 42 uzun V1 + 54 örtüşebilen kısa/orta V2; kontrol düzeyinde **84 farklı 09:15 TRT gözlem**, 12'si iki kayıt tarafından etiketlenmiş. [84 tekil kontrol ve overlap sicili](../OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv). **84 de istatistiksel olarak tamamen bağımsız olay sayısı değildir**; komşu günler ve aynı üst dalga örtüşebilir.

**Bağlayıcı 96 olayın tamamı:** [G01–G07 ekonomik sınıfı, ikinci aktarım kanalı ve fiyat yaşam döngüsü bağlantıları CSV](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv) · [42 V1 fiyat başlangıç–orta–son ve sonrasındaki ters hareket sayısal CSV](../OLAY_02_42_UZUN_HAREKET_YASAM_DONGUSU_V1_20261014.csv) · [96 özgün tarihli haber/vaka fişi](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md).

### G01–G07: sınıf ve gözlenen fiyat yolunun özeti

| Ekonomik aile | Etiket /96 | Ölçülen uzun V1 /42 | V1 ortanca uzunluk | İlk 3 seans / orta / son 3 seans: yön-işaretli ortancalar |
|---|---:|---:|---:|---|
| **G01** ABD makro – faiz/dolar/Fed beklentisi | 30 | 12 | 26 gün | +0.38% / +2.78% / +1.96% |
| **G02** Tarife, ticaret ve ekonomi politikası | 20 | 11 | 9 gün | +1.91% / +1.26% / +2.50% |
| **G03** Jeopolitik risk ve güvenli liman | 13 | 7 | 14 gün | +0.78% / +2.17% / +0.80% |
| **G04** Merkez bankası / rezerv / fiziki altın ve fon akışı | 11 | 6 | 16.5 gün | +1.48% / +2.85% / +1.32% |
| **G05** Finansal stres / fonlama / zorunlu tasfiye | 4 | 3 | 9 gün | +0.83% / +0.54% / +1.90% |
| **G06** İçsel pozisyon dönüşü / kâr alma / momentum | 4 | 0 | — | **veri yok** / **veri yok** / **veri yok** |
| **G07** Karma / baskın ekonomik neden henüz ayrıştırılmadı | 14 | 3 | 30 gün | -0.20% / +2.29% / +0.91% |

*Tablodaki +% değerler **o olayın sonradan bilinen ana V1 yönüne göre işaretlidir**; hem UP hem DOWN bacaklarında + rakam yönünde hareket anlamına gelir. İlk 3/orta/son 3 ölçümü 06:00 UTC'deki günlük M15 fiyat örneklerinden üretilmiştir; resmî NY17 fiyat getirisiyle aynı zaman sözleşmesi değildir. Farklı gruplardaki ‘ortalama karakter’ bir yatırım sinyali veya açıklamanın nedensel kanıtı değildir.*

## 1. Olay karakteri için BİRLEŞİK ONTOLOJİ (başlangıç–gelişim–bitiş)

**Bir ekonomik olay bir fiyat dalgası değildir:** bir uzun fiyat dalgası farklı NFP/CPI/jeopolitik/rezerv haberlerini kapsayabilir. Bir makro ilk fiyat şoku (EVENT_ID) sonradan V1/V2 dalgalara katkıda bulunabilir. `EPISODE_ID` (fiyat dalgası) → `EVENT_ID` (gerçek ilk haber) → `CHECKPOINT_ID` (karar kontrolü) → `RESPONSE_PHASE` (o andan sonra fiyat durumu) ayrı kayıtlar olmalıdır.

| Safha | Ekonomik olay için araştırılacak kanıt | Şimdi elimizdeki güvenilir durum |
|---|---|---|
| **P0 Önkoşul (haber öncesi)** | As-of altın trendi ve volatilitesi, gümüş/platin/paladyum, dolar, 2Y/10Y nominal/reel, petrol, risk endeksleri, pozisyon, saat ve yayın lag'i | XAU M15 ve kısmen ZN/NQ/CL var; 2023–24 gümüş **SI.n.0 arşivde var fakat 55 olayın H1 değeri henüz çıkarılmadı**; DXY/gerçek faiz eksik |
| **P1 İlk katalizör** | Orijinal haber firstprint UTC, açıklama öncesi consensus-vintage, actual sürprizi, aynı andaki rakip haber | 96 fiyat kaydında hareketi *başlatan* tek ilk haberin nedensel doğrulaması **0/96**; belli NFP/CPI saatleri ayrıca doğrulanmış |
| **P2 İlk tepki / ONSET** | Firstprint öncesi ve sonrası M1/M15 altın, XAG/ZN/FX/faiz, bid-ask ve olay öncesi 1/4/12h | 85 zamanlı ABD makro release alt çalışması var; tamamını V1 başlangıcına bağlama |
| **P3 Yayılma ve devam** | 1/4/12s + 1/3/5 uygun seans yönü, güçlü/ters metal-akış ve faiz, ikinci haberler | 42 uzun ve 54 kısa kaydın gözlemlenmiş fiyat yolu ayrıştırıldı; fiyat rejiminin gerçek nedeni henüz çoğu olayda belirsiz |
| **P4 Yorulma / baskınlık değişimi** | Kalan beklenen hareket düşer, çapraz varlık ayrışır, haber akışı tersine döner, likidite/pozisyon zorlanır | Fiyat dönüm noktası **geriye dönük etiketli**; aynı noktayı canlı haber sonu olarak sunma |
| **P5 Bitiş / sonrası** | Gerçek trendin kırılması, maliyet sonrası yeniden AL/SAT/TUT karşı-olguları, takip eden 3 seans | 42 V1 için sonraki üç seansın ters işaretli değişimi ayrıca hesaplandı. **ZigZag döngü sınırı sonradan seçildiğinden dönüş sıklığı yapısal olarak yükselebilir; erken çıkış başarısı olarak kullanma.** |

**Karakter vektörü:** `group_primary`, `secondary_transmission`, `known_news_firstprint`, `precondition`, `stage`, `gold_price_1/4/12h`, `silver_spot/futures_PIT`, `USD/2Y/10Y`, `oil`, `market_risk`, `morphology`, `rival_evidence`, `end_phase_flag`, `expected_remaining`, `costed_decision`, `evidence_level`. **EKSİK** alan modele sıfır olarak kodlanmaz; ayrı eksiklik bayrağı taşınır.

## 2. Yedi ekonomik olay ailesinin karakter analizi

### G01 — ABD makro – faiz/dolar/Fed beklentisi

**Kapsam:** 96 fiyat kaydında **30 etiket**, ölçülebilir uzun V1 bacağında **12 örnek** (9 UP / 3 DOWN). **Yaygın fiyat süresi:** V1 etiketli bacaklarda ortanca **26 takvim günü**. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul: ücret/enflasyon/istihdam beklentileri, DXY ve nominal/reel faiz patikası. Katalizör adayı: zaman damgalı CPI, NFP, AHE, Fed/FOMC veya ISM açıklaması; sürprizin işareti tek başına altın yönünü belirlemez.

**Gelişim karakteri / aktarım → güçlendirici:** Makro bilginin Fed beklentisine, dolara ve faize aktarılması; zaman içinde gelen yeni verilerle güçlenme veya işaret değiştirme. 12 uzun V1'de **5 geç hızlanan** tip var; fiyatın ilk seanslarda yavaş gitmesi zayıf haber anlamına gelmez.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Karşı veri, yeni Fed konuşması, faiz/dolar hareketinin sönmesi veya uzun pozisyonların çözülmesiyle dönüş adayı. Haber değişimi ve 15m trend dönüşü gözlenmedikçe kesin ‘bitti’ sinyali yok.

**Yanlışlayan veya ayırıcı vaka:** 10 Mart 2023: güçlü NFP sürprizi olsa da altın +%0,540 ilk 15m UP; SVB güvenli liman kanalı rakip. 6 Ocak NFP ve 3 Şubat NFP ters örnekleri.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans **+0.38%**, bacak ortasında başlangıca göre **+2.78%**, son 3 seansta **+1.96%**; etiket sonunu izleyen 3 seansta **+1.31% ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [SWING_V1_001](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_001) · [SWING_V1_002](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_002) · [SWING_V1_003](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_003). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).

### G02 — Tarife, ticaret ve ekonomi politikası

**Kapsam:** 96 fiyat kaydında **20 etiket**, ölçülebilir uzun V1 bacağında **11 örnek** (5 UP / 6 DOWN). **Yaygın fiyat süresi:** V1 etiketli bacaklarda ortanca **9 takvim günü**. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul: tarife müzakeresi, uygulama takvimi, küresel ticaret kırılganlığı. Katalizör adayı: oran, yürürlük tarihi, mahkeme/erteleme veya müzakere açıklaması; ilk kaynak saatini ayır.

**Gelişim karakteri / aktarım → güçlendirici:** İki rakip kanal: riskten kaçış/altına talep **veya** nakde sıkışıp teminat satışı. Tarife açıklaması daha sonraki karşı-haberlerle birkaç ayrı fiyat dalgasına dönüşebilir.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Erteleme/anlaşma, pozisyonların yeniden kurulması ya da satışın likidite ihtiyacının bitmesi. Son 3 seansta işaretli medyan +%2,50: bu örneklemde hareketler bazı bacaklarda **geç bölümde de devam etmiş**.

**Yanlışlayan veya ayırıcı vaka:** 2025 Nisan’da tarife/likidite stresi altında altın da düştü; ‘tarife = altın kesin yükselir’ yanlıştır.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans **+1.91%**, bacak ortasında başlangıca göre **+1.26%**, son 3 seansta **+2.50%**; etiket sonunu izleyen 3 seansta **+1.49% ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [SWING_V1_025](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_025) · [SWING_V1_027](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_027) · [SWING_V1_028](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_028). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).

### G03 — Jeopolitik risk ve güvenli liman

**Kapsam:** 96 fiyat kaydında **13 etiket**, ölçülebilir uzun V1 bacağında **7 örnek** (3 UP / 4 DOWN). **Yaygın fiyat süresi:** V1 etiketli bacaklarda ortanca **14 takvim günü**. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul: çatışma/enerji arzı/diplomatik gerilim, piyasadaki mevcut korku primi. Katalizör adayı: doğrulanmış ilk çatışma veya ateşkes haberi.

**Gelişim karakteri / aktarım → güçlendirici:** Güvenli liman talebi XAU UP doğurabilir; fakat enerji fiyatı/enflasyon/faiz veya likidite kanalı ters yönde olabilir. Haber akışı art arda değiştikçe çoklu dalga ve yön dönüşü görülebilir.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Risk priminin sönmesi, ateşkes ve diplomasi veya enflasyon-faiz kanalının baskın hâle gelmesi. Fiyatın zirvesini geçmişten bilerek bitiş saati tahmin edildiği iddia edilemez.

**Yanlışlayan veya ayırıcı vaka:** Aynı jeopolitik aile içinde 3 UP ve 4 DOWN uzun bacak: haber başlığı yön için yeterli değil.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans **+0.78%**, bacak ortasında başlangıca göre **+2.17%**, son 3 seansta **+0.80%**; etiket sonunu izleyen 3 seansta **+0.53% ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [SWING_V1_007](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_007) · [SWING_V1_008](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_008) · [SWING_V1_021](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_021). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).

### G04 — Merkez bankası / rezerv / fiziki altın ve fon akışı

**Kapsam:** 96 fiyat kaydında **11 etiket**, ölçülebilir uzun V1 bacağında **6 örnek** (3 UP / 3 DOWN). **Yaygın fiyat süresi:** V1 etiketli bacaklarda ortanca **16.5 takvim günü**. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul: merkez bankası alım eğilimi, fiziki/ETF/OTC ve vadeli piyasa stok/akış dengesi. Katalizör adayı: PBoC altın alım raporu, WGC/ETF/CFTC ilk açıklaması; **verinin ait olduğu ay ile yayımlandığı gün ayrılır**.

**Gelişim karakteri / aktarım → güçlendirici:** Talep ve arz/pozisyon kanalı metaller arasında ayrışma doğurabilir; bankacılık/rezerv bilgisi bazen fiyat hareketini izler ve gecikmeli yayımlanır. Başka makro haberler rakip olabilir.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Alımın durması, ETF/COMEX çözülmesi, aşırı momentum veya ABD faiz baskısı. Bu altı V1'de bitiş sonrası 3 seans medyan yön terslemesi **−%0,05**; ‘hemen hep geri döner’ kanıtı yok.

**Yanlışlayan veya ayırıcı vaka:** Ocak 2023 altında UP varken ETF ay sonu eksi; 7 Haziran 2024 PBoC haberi ve NFP ayrı tetikler.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans **+1.48%**, bacak ortasında başlangıca göre **+2.85%**, son 3 seansta **+1.32%**; etiket sonunu izleyen 3 seansta **-0.05% ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [SWING_V1_011](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_011) · [SWING_V1_013](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_013) · [SWING_V1_016](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_016). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).

### G05 — Finansal stres / fonlama / zorunlu tasfiye

**Kapsam:** 96 fiyat kaydında **4 etiket**, ölçülebilir uzun V1 bacağında **3 örnek** (0 UP / 3 DOWN). **Yaygın fiyat süresi:** V1 etiketli bacaklarda ortanca **9 takvim günü**. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul: marjin, kredi, fonlama veya nakit teminat ihtiyacı. Katalizör adayı: banka/kredi haberi, teminat gereksinimi veya piyasa likidite boşluğu.

**Gelişim karakteri / aktarım → güçlendirici:** Teminatlı pozisyonlar çözüldüğünde altın ve hisseler/beyaz metaller birlikte satılabilir. Fiyatın ilk düşüşünden sonra başka emir dalgaları gelebilir; 3 uzun bacağın tamamı DOWN ama **örnek çok küçüktür**.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Marjin/nakit ihtiyacının bitmesi, piyasanın likiditesinin toparlanması veya yeni risk/varlık haberinin baskınlaşması. Medyan son 3 seans +%1,90 yönlü, çıkışın son anı ex-post saptanmıştır.

**Yanlışlayan veya ayırıcı vaka:** SVB Mart 2023 bankacılık stresi altına güvenli liman UP yaratabildi; bankacılık riski = her zaman altın DOWN değil.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans **+0.83%**, bacak ortasında başlangıca göre **+0.54%**, son 3 seansta **+1.90%**; etiket sonunu izleyen 3 seansta **+1.45% ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [SWING_V1_010](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_010) · [SWING_V1_018](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_018) · [SWING_V1_042](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_042). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).

### G06 — İçsel pozisyon dönüşü / kâr alma / momentum

**Kapsam:** 96 fiyat kaydında **4 etiket**, ölçülebilir uzun V1 bacağında **0 örnek** (uzun V1 örneği yok). **Yaygın fiyat süresi:** hesaplanamaz. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul: birikmiş trend, yoğun long/short pozisyonu, fiyatın önceki volatilitesi ve marjin. Bu sınıftaki dört kayıt **V2 kısa-ufuk**, 42 V1 uzun bacak sınıflarında ayrı birincil etiket yok.

**Gelişim karakteri / aktarım → güçlendirici:** Tetikleyici net makro haber olmayabilir; likidite, stop zinciri, teknik kırılma veya pozisyon tasfiyesi birlikte gelir. Bugün için yalnız 4/12h ve 1/3/5seans kontrol akışındaki fiyat morfolojisi incelenebilir.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Satıcı/alıcı baskısı tükenmesi, ters fiyat teyidi veya yeni haberin yönü değiştirmesi. **Uzun bacak başlangıç–orta–son sayısal medyanı hesaplanmadı**; başka ailenin dönüşünü yanlış biçimde bunun uzun örneği sayma.

**Yanlışlayan veya ayırıcı vaka:** Ekim 2025 altında/metallerde düşüşe karşın hisse/petrol yükselişi; genel likidite paniği diye otomatik sınıflandırma yanlış olabilir.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans ****veri yok****, bacak ortasında başlangıca göre ****veri yok****, son 3 seansta ****veri yok****; etiket sonunu izleyen 3 seansta ****veri yok** ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [C_CORR_008](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_008) · [C_CORR_013](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_013) · [C_CORR_022](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_022) · [C_CORR_049](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_049). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).

### G07 — Karma / baskın ekonomik neden henüz ayrıştırılmadı

**Kapsam:** 96 fiyat kaydında **14 etiket**, ölçülebilir uzun V1 bacağında **3 örnek** (1 UP / 2 DOWN). **Yaygın fiyat süresi:** V1 etiketli bacaklarda ortanca **30 takvim günü**. Bu sınıf **ekonomik neden ispatı değil, ilk sürüm aday mekanizma**.

**Başlangıç karakteri / önkoşul → tetikleyici:** Önkoşul ve ilk kaynak çelişkili, gecikmeli ya da belirsiz. Tek haberle açıklanamayan üst üste NFP, CPI, Fed, tarife ve jeopolitik bilginin rekabet ettiği vakalar.

**Gelişim karakteri / aktarım → güçlendirici:** Birden fazla nedenin üst üste binmesi, başlangıçta ters yönde hareket sonra yeni bilgilerle asıl trendin oluşması mümkün. Üç uzun kayıtla genel tip tanımlanamaz.

**Bitiş karakteri / tükenme → karşı-haber → dönüş:** Baskın mekanizma çözümlenene kadar `UNKNOWN`; fiyatın son bulması nedensel mekanizmanın bittiğini göstermez.

**Yanlışlayan veya ayırıcı vaka:** Haber bulunamadı ≠ haber gerçekleşmedi. Bu sınıf model başarısızlığı değil, gerekçeli ‘bilmiyoruz’ kaydıdır.

**Gerçek gözlemsel üç evre (42 uzun V1 örnekleme esaslı):** İlk 3 uygun seans **-0.20%**, bacak ortasında başlangıca göre **+2.29%**, son 3 seansta **+0.91%**; etiket sonunu izleyen 3 seansta **+1.11% ters yönlü** hareketin grup ortancası. *İşaret, her bacağın sonradan etiketlenmiş UP/DOWN yönüne çevrilmiştir; bunlar gerçek haber başlangıcı/saatli banka getirisi veya karar anında bilinebilir bitiş tahmini değildir.*

**Kayıt örnekleri:** [SWING_V1_006](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_006) · [SWING_V1_014](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_014) · [SWING_V1_033](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_033). Tüm kayıtlar [96'lık karakter atlasında](../OGREN_03_96_OLAY_AILE_KARAKTER_ATLASI_20261014.csv).


## 3. Ekonomik nedenden bağımsız 5 ana uzun-fiyat karakteri (42 V1)

**Yöntem:** V1 NY17 düzeltilmiş fiyat bacağının tarih başlangıcı/bitişi alınarak her uygun işlem günü 06:00 UTC M15 kapanış fiyatı örneklendi. İlgili güne ait M15 kapanışı ancak **06:15 UTC** sonrasında bilinebilir. İlk 3 uygun seans, bacak orta günü, son 3 uygun seans ve etiket bitiminden sonraki ilk 3 uygun seans karşılaştırıldı. Ölçümde kullanılan **`path_efficiency = |net toplam yönlü getiri| / toplam mutlak günlük yüzde hareketleri`**; etiketli bacak ve örneklenmiş 06:00 fiyat ölçümü ayrı sözleşmedir. Kıstaslar bilimsel doğrulanmış doğal cluster değil, **test edilmek üzere tasarlanmış sayısal profil eşikleridir**.

| Fiyat hareketi karakteri | Uzun V1 olay sayısı | Ölçüm tanımı | Karar araştırmasında neyi değiştirir? |
|---|---:|---|---|
| **M1 Erken impuls** | **8** | İlk 3 uygun seansta bacak yönünde ölçülen net hareketin ≥%50'si; çıkış veya ilk açıklama saati değildir. | Erken ivmenin 12s/3seansta sönmesi, karşıt haber ve kalıcılık işaretleri |
| **M2 Düzenli devam** | **4** | İşaretli toplam hareket / mutlak günlük dalgalanma toplamı ≥0,70; erken impuls şartını karşılamamış. | Şiddetli yavaşlama, etrafında yeniden fiyatlama, risk ve spread yükselişi |
| **M3 Gecikmeli hızlanma** | **7** | İlk 3 uygun seansta toplamın <%15'i, bacak orta noktasında <%40'ı ortaya çıkar. | Sonraki haberle mi tetiklendi? İlk makroyu hareketin tümüne atfetme |
| **M4 Dalgalı / sık ters hareket** | **16** | Net yönlü ilerleme / mutlak günlük fiyat yolu <0,40; pek çok karşı dalga var. | Her küçük geri çekilmede SAT/AL değişimi çift %0,8 maliyete takılır |
| **M5 Çok dalgalı / geçiş** | **6** | Yukarıdaki katı beşli kuralların diğer dört tipine girmeyen, birden çok evreli fiyat yolu. | Farklı haberler ve aşamalar ayrı alt-olaya bölünmeli |
| **M0 Çok kısa** | **1** | 4'ten az 06:00 UTC günlük M15 örneği; uzun-fiyat profilinde güvenilir oran yok. | Günlük yerine gerçek M15/M1 pencereyle ayrı profil gerek |

**Yorum:** **16/42** uzun V1 kaydı dalgalı karakter aldı; burada sürekli AL/SAT değiştirmenin toplam komisyonu ciddi engeldir. **7 geç hızlanan** vaka vardır; olayın başındaki yavaşlık, geriye kalan hareketin küçük olduğunu kanıtlamaz. **8 erken impuls**, **4 düzenli devam**, **6 çok dalgalı geçiş** görüldü. **1 kısa vaka** uzun-fiyat morfolojisine zorlanmadı. Sadece geçmiş fiyat yolundan ekonomik neden çıkmaz.

## 4. Kısa/orta ufuk V2 kontrol karakterleri (54 kısa fiyat kaydı)

| 09:15 TRT kontrol noktasına göre SONRADAN gerçekleşen tip | Kayıt | Ölçüm ve sınırı |
|---|---:|---|
| S1 İlk impuls üç seansa taşındı | **12** | 09:15 kontrol sonrası 4s MID ≥%0,35 ve 3 seans MID ≥%0,50, işaret aynı |
| S2 İlk impuls üç seansta tersine döndü | **6** | İlk 4s |getiri| ≥%0,35, 3 seans |getiri| ≥%0,50 ama işaret ters |
| S3 Gecikmeli büyük hareket | **10** | İlk 4s |getiri| <%0,35, sonraki 3 seans |getiri| ≥%1,62 |
| S4 3 seans hareketi ücret eşiğinden küçük | **25** | 3 seans |MID getiri| <%1,62; tam bir işlemin maliyetini tek başına karşılamayabilir (spread hariç) |
| S0 Ölçülemeyen | **1** | 3 seans sonucu yok veya uygun ileri M15 veri eksik |

**Önemli:** 4 saat/12 saat sonuçları ve 3/5 seans ölçümleri, önceden bilinmeyen hedeflerdir. V2 olayının ‘gerçek ilk haber saati’ bu 09:15 kontrolünden önce/sonra olabilir. Sınıflandırma **in-sample ex-post** gözlemdir; otomatik erken uyarı değildir.

## 5. Gruplar arası ayrım — aynı sonuç nasıl zıt ekonomi üretebilir?

| Birbirine benzeyen XAU sonucu | Rekabet eden karakterler | Karşıt durum, sınanacak fark |
|---|---|---|
| **UP** | G01 güvercin Fed / G03 kredi-jeopolitik haven / G04 fiziki/rezerv talep | Gerçek USD/faiz etkisi, gümüş-altın ayrışması, haber yayın/vintage, kredi ve petrol |
| **DOWN** | G01 şahin Fed / G02 tarife-likidite / G05 zorunlu fonlama / G06 pozisyon sönümlenmesi | Hisse+petrol+gümüş birlikte mi düştü, yoksa yalnız kıymetli metal mi? Same-UTC teyit gerekir |
| **İlk yükseliş sonra satış** | NFP+ISM aynı gün, ilk haber yanlış yorum / G06 aşırı pozisyon | İlk 15dk/60dk, sonraki 4/12h, 3 seans; negatif kontrol |
| **Büyük uzun trend** | M2 düzgün devam / M3 geç ivme / M4 dalgalı çok haber | İlk haberin katkısını uzun dalganın tamamıyla eşitleme; ara haberleri EVENT_ID olarak böl |
| **Düşüş sonunda hızlı toparlanma** | G05 likidite zorunluluğu bitti / G02 tarife karşı-haber / G01 Fed beklentisi değişimi | Sonradan seçilmiş ZigZag diplerini sinyal saymadan likidite/yeniden fiyatlama ilk gözlemi |

**Benzerlik/öğrenme sırası:** `same unique checkpoint` mükerrerliği kaldır → aynı üst fiyat bacağı ve 14 günlük embargo ile yakın komşuları ayır → as-of haber ailesi *ilk yayımla*, altın geçmiş trend/oynaklık, gümüş, faiz/dolar, petrol, rejim ve evreyle karşılaştır → **aynı koşullarda ters sonuç veren kontrolleri** zorunlu bul → gelecekteki sonucu yalnız değerlendirmede aç. Şu anda 84 kontrolün yalnız 3'ünde sınırlı NFP/CPI/FOMC takvim türü+altın fiyat rejimi eşleşmesi vardır, **bu gerçek haber neden eşleşmesi değildir**. 2023–24 SI.n.0 saatlik gümüş kaynak arşivi henüz tüm 55 olaya sayısal aktarılmadı. **‘En yakın fiyat’ eşlemesi ile AL/SAT izni yok.**

## 6. Bir çıkarım hangi şartta kalıcı öğrenmeye dönüşecek?

1. **Aile hipotezi:** Haber ilk yayımlanma saati, ön koşul ve rakip nedenleriyle birlikte kaydedilmeden `G01–G07` etiketi yalnızca `CANDIDATE` kalır.
2. **Karakter testi:** En az bir aynı-grup ters sonuç ve bir şoksuz kontrol eşleştir; fiyat deseninin farklı makro rejimde bozulup bozulmadığını ölç.
3. **Safha tahmini:** Gerçek alarm anında `P(ONSET/CONTINUE/EXHAUST/REVERSE)` kalibre edilecek; sonradan seçilmiş V1/V2 bitişini doğru tahmin sayma.
4. **Fırsat–maliyet testi:** %0,8 alış + %0,8 satış + bankanın BID/ASK makası ile **karar sonrasında kalan beklenen hareketi** karşılaştır. `GOLD/CASH` başlangıç hâli ve geri-giriş ihtiyacı ayrı ele alınmalı.
5. **Bilimsel geçiş:** `DESCRIPTION_ONLY → TIMED_SOURCE_QA → CONTRADICTION_TESTED → FROZEN_ASOF_OOS → COSTED_VALIDATED`. Bugün G01–G07 ve M1–M5 **DESCRIPTION_ONLY**; ilk üç mevcut `MECH_...` karar hipotezi de `RESEARCH_ONLY`.
6. **Bilgi arşivi:** OLAY-02 araştırmasının `EVENT_ID`si ve özgün dosya bağlantısı kaybolmadan, aile karakteri veya yanlışlanan kuralın yeni sürümü bu ÖĞREN-03'e eklenir. Aile değiştirildiğinde eski etiket tarihçesi `superseded_by` ile saklanır.

## 7. Geliştirilmesi gereken eksik kanıtlar — açık öncelik

**P1:** 2023–24 55 olay için SI.n.0 / SI 15m/1h gümüş verisini doğru kapanış saatinde gerçekten hesaplamak (arşiv mevcut, çıkarım henüz değil). **P2:** DXY / gerçek 2Y–10Y nominal/reel faiz, Brent ve haber/vintage; günlük ETF/CFTC yayım gecikmesi. **P3:** 84 tekil kontrolün şoksuz normal günlerle genişletilmesi; 96 olayın yalnız büyük gerçekleşmiş dalgalardan seçilme yanlılığı. **P4:** Ekonomik ilk haberin mevcut fiyat bacağını başlatıp başlatmadığının ilk UTC M1/M15 testi; retrospektif WGC haberleri canlı özellik olamaz. **P5:** 2026 Ocak–Eylül günlük Astra araştırma mekanizmalarının farklı saat/etiket ve maliyet varsayımları korunarak ayrı doğrulanması.

**Çıkarım manifesti DURUMU:** `7_CANDIDATE_ECONOMIC_FAMILIES / 5_MEASURED_LONG_LEG_MORPHOLOGIES / 1_SHORT_V1_INSUFFICIENT / 54_SHORT_HORIZON_PROFILES / 96_PRICE_RECORDS_AND_84_CHECKPOINTS / NO_VERIFIED_PRICE_INITIATION_CAUSALITY / NO_MODEL_PROMOTION`.

---

## TARİHSEL EK — İlk üç olay–karar hipotezi (ilk sürüm, aynen korunan kanıt zinciri)

**SABİT KOD: ÖĞREN-03 · TEK merkezi hipotez sicili.** Kaynaklar [OLAY-02'deki 96 haber/veri fişi](../OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md) ve [OLAY-02 ana sayfasında](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) birlikte okunur. Buradaki **üç mekanizma henüz doğrulanmamış hipotezdir**. Yeni vaka kanıtı ve negatif kontrol önce OLAY-02'de, genel sonuç burada hipotez-ID ile; kopya vaka manifesti yoktur.

> **Belge kodu: ÖĞREN-03 — Ortak Öğrenme ve Karar Mekanizmaları.** Bu sicil **OLAY-02** içindeki haber/fiyat/karar kanıtları üzerinden türeyen, şimdilik test edilmekte olan hipotezleri tutar. Önceden kullanılan **ÖĞREN-04** adı artık geçersizdir. Olayın sayısal verileri, haber ve testleri tek [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) kimliği altından açılır. [Belge haritası](../BELGE_HARITASI_V1.md).

**Sicil ID:** `GPT_CAUSAL_ACTION_REGISTER_V1_20261014` · **Durum:** `RESEARCH_ONLY / HINDSIGHT_EXPOSED / NO_MODEL_PROMOTION`.
**Kapsam:** 2023 Ocak UP, 2023 Şubat DOWN ve 5 Ocak kısa DOWN düzeltme karşıt vakalarının **olay-aksiyon mekanizma adayları**, **onaylı otomatik AL/SAT kuralları değildir**.
**Olay araştırmasının değişmeden korunan tarihsel otoritesi:** [5.190 satırlık 0.1A–0.1G manifest arşivi](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md). Bu dosyaya append yapmayın; tarihsel snapshot donuktur. [Aktif amaç/karar manifesti](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) buraya yönlendirir.
**Kanıt otoritesi:** Sayısal as-of ve ücret hesaplarında orijinal rapor/CSV/JSON özet cümleden üstündür. Hiçbir hesap gerçek banka emri değildir; USD/DXY ve faiz tam M15 kaynağı, banka icra fiyatı, dağılımsal kalan yön avantajı ve ayrı OOS kontrolü eksiktir.

## 1. Bilgiden aksiyona: üç hipotez
| ID | Gözlemlenen olay zinciri (karar sırasına dikkat) | Aksiyon adayı | Örnek olay sonucu ve karşıt örnek | Durum |
|---|---|---|---|---|
| **H-UP01 / MECH_FED_DOVISH_REPRICING_UP_V1** | NFP: ücret artışı beklentiden yumuşak *ama* istihdam güçlü → Fed'in gelecekte daha yumuşak davranması olasılığı → fiyat M15 UP → adayda M1 devamlılık → **banka maliyeti sonrası KALAN UP potansiyeli için ek kanıt** | Nakitken AL *adayı*, altında TUT; şüphe veya yetersiz kalan hareket varsa BEKLE | 6 Ocak NFP 13:30Z; 13:46Z hipotez AL, 13:47Z tahmini ASK 1849.30; 13 Ocak **yalnız teorik kapatılmış** $100 → ~$102.19. İlk AL'dan **SONRA 15:00Z** ISM geldi: sabah kararında kullanılamaz. **10 Mart 2023 güçlü NFP sürprizi + XAU ilk 15dk +%0.54 karşı-vaka**, güçlü NFP daima altını düşürmez. | Tek vaka, KANITLANMADI |
| **H-DN01 / MECH_FED_HAWKISH_REPRICING_DOWN_V1** | NFP çok güçlü/sürpriz → daha sıkı Fed ihtimali → ilk tamamlanmış M15 altın DOWN → M1 devamlılık → altından çıkıp nakitte kalmanın beklenen maliyet sonrası faydası > altında kalmanın riski | Altındayken SAT *adayı*, nakitteyken TUT | 3 Şubat 517K NFP, M15 -%1.34, 13:45Z SAT kararı, 13:46Z BID vekili 1887.305; koşullu $100 altınla başlarsak $96.384 nakit, 24 Şubat pasif altın net $92.531. **3 Şubat öncesinde USD/UST saatlik veri ve 517K as-of bilinmiyor**. Satıştan sonra yeniden giriş programı test edilmedi. | Tek vaka, KANITLANMADI |
| **H-HOLD01 / MECH_SHORT_DOWN_WHIPSAW_HOLD_V1** | Güçlü ADP/claims → DOWN M1 teyit *ama* hareketin çoğu oldu → kalan DOWN'un **SAT + tekrar AL** ve makası karşılayacağı belirsiz → emir vermeden pozisyonu koru | Altındayken TUT; şüpheli DOWN'da otomatik SAT değil | 5 Ocak DOWN ilk M1 teyidi 13:58Z, 6 Ocak NFP/ISM sonrası UP 13:48/15:07Z (5 Ocak'ta bu **bilinmiyordu**). 6 Ocak tutulan altın BID-mark $100.073; SAT→geri AL alternatifleri yaklaşık $97.67 veya $97.23. **3 Şubat gerçek büyük DOWN'da ise kör TUT yanlış olabilir.** | Tek vaka, KANITLANMADI |

**Not:** 5 Ocak vakasında gelecekteki 6 Ocak olumlu olayının bilinmediği şartta ilk gün TUT nedeninin kanıtlanmış yön avantajı değil **yüksek çift-taraf komisyonu ve kalan düşüş belirsizliği** olduğu açıkça saklanır. UP ve DOWN kararı **önce haber sürprizi, sonra fiyat/doğrulama, sonra kalan hareket/maliyet** koşuluyla değerlendirilmeli; haber olmadan sabit %0.6 ya da %3 fiyat kırılması emir değildir.

## 2. İlk aday işlem örnekleri — model kanıtı değil
- [5–13 Ocak GPT bağımsız ilk UP çalışma raporu](../independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md). İlk AL 6 Ocak 16:46 TRT, bir sonraki dakika ASK vekili; banka %0.8/%0.8 sonrası 13 Ocak *varsayımsal* $102.19, pasif/NAKİT kıyasları.
- [1–24 Şubat büyük DOWN GPT bağımsız raporu](../independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md). 3 Şubat 16:45 TRT SAT, sonraki dakika BID vekili; 24 Şubat şartlı kıyası $96.384 nakit vs $92.531 pasif altın tasfiye. Şubat başındaki ALTIN koşulu bağımsız başlangıçtır, aradaki Ocak14–31 otomatik doldurulmadı.
- [5–6 Ocak küçük DOWN/UP günleri stres ve whipsaw kıyası](../adaptive_volatility_learning/stress_cases/2023-01/JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md). Bu tek-gün aralığı stresidir, asıl %3+ çok gün yönlü atlası değil.

## 3. Sıkı karar araştırma sözleşmesi (otomatik ticaret değildir)
1. **As-of**: Haber `event_time_utc` ve `available_at_utc` ayrı; yalnız **tamamlanmış** M15/H1/M1 bar, emirde en erken takip eden 1m/m15 fiyat. Reuters yayın revizyonları da kontrol edilir.
2. **Neden**: `event_surprise_vector` (NFP/ücret, CPI çekirdek, ISM gibi alt bileşenler); `candidate_transmission` (USD, Treasury yield/real yield, safe-haven, likidite) ve **karşı hipotezler**. ZN H1 tahvil vadeli fiyatı, doğrudan nakit tahvil faizi değildir.
3. **Evre ve kalıcılık**: `PRE_ONSET/ONSET/CONTINUATION/EXHAUSTION/REVERSAL/UNCERTAIN` puanlaması; trendin toplam eski hareketi ile **sinyalden sonraki** olası hareket ayrılır.
4. **Banka faydası**: `E[V(ALTIN)|available]` ile `E[V(NAKİT)|available]` farkı **0.8% her emir yönü + gerçek BID/ASK + tekrar giriş/çıkış olasılığı** düşüldükten sonra anlamlı olmalı. Sadece gerçekleşmiş altın yüzde getiri veya haber geçmiş analoğu bu beklentinin sayısal ölçüsü değildir.
5. **Eşiklerin statüsü**: +/−%0.6 ve 3×M1 kapanışlar **bugünkü örneklerde geçmişe bakılarak seçilmiş taktik teşhis**; kalibrasyon ve başka yıla transfer doğrulanmadan üretime alınamaz. `≥%3` ve hızlı `≥%2` **olay seçim kategorileri**, otomatik al/sat yüzdesi değil.
6. **Yanlışlama**: 10 Mart 2023 NFP karşıt örneği, 2024/25 değişen rejimler, büyük DOWN'da HOLD maliyeti, geç SAT sonrası geri alım ve aynı sürprizde şoksuz günler birlikte test edilecek.
7. **İki mod**: Tüm yıllardan analog topla `FULL_HISTORY_DISCOVERY` fakat o tarihte gerçekten bilinebilecek bilgiden sinyal üret `AS_OF_REPLAY`; araştırmacı geçmiş sonuçları gördüğünden bu raporda karar skorları **ne kör ne bağımsız OOS**.
8. **Yönetim**: Gerekli veri ve model/karar doğrulama eksikse `ABSTAIN`. Yeni hipotez/test sonucu bilimsel sicile eklenebilir ama ana manifestte tek paragraf ve kanıt linki dışında binlerce satırlık döküm tutulmaz.

## 4. Eksik ve net geliştirme kapısı
**Bugünkü en büyük boşluk:** `P(remaining_4h/12h/1d/3eligible/5eligible returns | precondition, surprise, markets, stage)` dağılımı ve işlem maliyeti sonrası aksiyon faydası **kalibre edilmiş değil**. Güçlü büyük olayların başarısını ölçmek için geçmiş kazançları anlatmak değil aynı kuralı daha önce model geliştirmede kullanılmayan pozitif, ters ve şoksuz olaylarda körlemesine denemek gerekiyor. Örneklerin birinde $102.19, diğerinde $96.38 çıkması **genel strateji getirisi değildir**.
