# ÖĞREN-03 — EKONOMİK OLAY DNA KÜTÜPHANESİ

**KİMLİK: ÖĞREN-03 | KAPSAM: Zamandan bağımsız ekonomik mekanizmalar, davranış yolları ve karakter ayrıştırması | DURUM: ARAŞTIRMA HİPOTEZLERİ**

> **Temel ilke: Burada tarih yok, ekonomik DNA var.** Bir olayın hangi gün gerçekleştiği, haberin yayın saati, fiyatı, yüzdesi, hangi tarihte alınıp satıldığı ve vaka bazlı sonuçları **ÖĞREN-03'e yazılmaz**. Burada yalnızca **tekrar kullanılabilir mekanizma**, bunun **önkoşulu → tetikleyicisi → aktarımı → gelişimi → yorulması → sonlanması/dönüşümü**, ayırıcı özellikleri, karşıt mekanizmaları ve yanlışlama ölçütleri bulunur.
>
> **Otorite ayrımı:** [ANA-01](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) araştırma yöntemi ve karar protokolü; [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) **tarihli olay, haber, fiyat, çoklu varlık ve karşıt vaka kanıtının tek otoritesi**; **ÖĞREN-03** tarihsiz ekonomik DNA/örgü kütüphanesi; **DURUM-04** aylık ilerleme kaydı. Eski olay sonuçları ve karar hipotezleri OLAY-02 kanıtları, bağlı raporlar ve mevcut makine-okunur hipotez sicilinde saklanır. Git geçmişindeki önceki ÖĞREN-03 içerikleri geri alınabilir; bu sürüm silme değil **sorumluluk ayrıştırmasıdır**.

## 1. DNA'nın tanımı: OLAY ≠ FİYAT ≠ MEKANİZMA

**Ekonomik DNA**, belli tarihteki bir fiyat dalgası veya haber başlığı değil, benzer koşullarda tekrar oluşabilecek **koşullu neden–aktarim–tepki örgüsü hipotezidir**. Altın yönü tek başına DNA değildir; aynı DNA farklı koşullarda farklı fiyat yönleri ve hareket karakterleri gösterebilir.

Bir DNA, ayrı ve zorunlu alanlardan oluşur:

| Alan | DNA'daki anlamı |
|---|---|
| `DNA_ID` / `variant_id` | Kararlı aile ve alt mekanizma kimliği; tarih içermez |
| `preconditions` | Haber/şok öncesi ekonomik ortam, trend, pozisyon, likidite, belirsizlik |
| `catalyst_class` | Tekil tarih değil: hangi tür bilgi veya şok tetikleyebilir? |
| `transmission_graph` | Fed/faiz, dolar, reel getiri, riskten kaçış, fonlama, fizikî talep, pozisyon gibi olası ara kanallar |
| `observable_fingerprint` | Hangi eşzamanlı piyasa verileri kanalı destekler, hangileri ayırır? |
| `branches` | Aynı tetikleyicinin ayrı koşullardaki birbirine zıt gelişim yolları |
| `phase_path` | P0–P5 başlangıç, yayılma, yorulma ve dönüş koşulları |
| `interaction_rules` | Başka DNA'nın baskınlaşması, birlikte etkisi veya çelişmesi |
| `falsifiers` | Bu mekanizmanın açıklama gücünü zayıflatan/rakibini güçlendiren gözlemler |
| `observable_limits` | Gecikmeli veri, eşzamanlı haber, eksik kaynak, ex-post seçilim sınırları |
| `evidence_status` | Hipotez / zamansal teyit / rakip-kontrol testli / bağımsız doğrulama; gerekçesi OLAY-02'dedir |

**Kanıt birimi OLAY-02'deki olaydır; kavram birimi ÖĞREN-03'teki DNA'dır.** OLAY-02 bir ekonomik olayı birden fazla `DNA_ID` adayıyla ilişkilendirebilir. ÖĞREN-03'e tekil `EVENT_ID`, vaka tarihleri, performans, fiyat başlangıç–bitiş değerleri veya geriye dönük işlem getirisi kopyalanmaz. DNA ile olayı birbirine bağlayan örnek tablosu OLAY-02'de tutulur.

**Mevcut kanıt seviyesi:** Aşağıdaki aileler kanıtlanmış nedensel kümeler değil, **test edilecek açıklama sınıflarıdır**. Bazı alt varyantların örneklem desteği daha da sınırlıdır. `UNKNOWN`, gerektiğinde geçerli nihai araştırma çıktısıdır.

## 2. Ekonomik DNA aileleri — altı mekanizma ve bir belirsizlik yönlendiricisi

| DNA | Aile | Ekonomik çekirdek | Kısa ayrıştırıcı soru |
|---|---|---|---|
| **G01** | Makro / Fed / faiz / dolar | Beklenti yeniden fiyatlaması | Altına etki faiz ve dolar üzerinden mi, başka kanal mı baskın? |
| **G02** | Ticaret / tarife / ekonomi politikası | Ticaret politikası şoku ve belirsizlik | Güvenli liman mı, maliyet/enflasyon mu, nakit ihtiyacı mı? |
| **G03** | Jeopolitik / güvenlik | Güvenlik risk primi | Güvenli liman akışı mı, enerji/faiz kanalı mı? |
| **G04** | Rezerv / fizikî altın / fon akışı | Talep-arz ve portföy tahsisi | Gerçek zamanlı ölçülebilen akış mı, gecikmeli rapor mu? |
| **G05** | Finansal stres / fonlama | Güvenli liman ile zorunlu satışın rekabeti | Altın sığınılan varlık mı, nakde çevrilen teminat mı? |
| **G06** | Pozisyon / içsel fiyat dönüşü | Pozisyon, kaldıraç, stop ve momentum çözülmesi | Dış haber olmadan fiyat/emir akışı mekanizması destekleniyor mu? |
| **G07** | **Ayrıştırılamamış / karma** | **Yeni bir neden DNA'sı değildir** | Birden fazla olası mekanizma arasında kanıtla tercih yapılabiliyor mu? |

### G01 — Makro, Fed, faiz ve dolar yeniden fiyatlaması

**Çekirdek:** Beklenti–gerçekleşme farkı ve açıklamanın alt bileşenleri → beklenen para politikası patikası → nominal/reel faiz ve doların fiyatlanması → altının fırsat maliyeti, yatırım talebi ve pozisyonlar. Makro veri tek yönde etki etmek zorunda değildir.

- **P0 / önkoşul:** Faiz beklentisinin mevcut düzeyi; enflasyon ve büyüme beklentileri; USD trendi; reel getiri; altın risk primi ve önceden alınmış pozisyonlar.
- **P1 / tetikleyici:** Enflasyon, ücret, istihdam, faaliyet verisi; merkez bankası kararı, tutanak veya söylem. Sürprizin **bileşenleri ve piyasanın beklediği** etki önemlidir.
- **P2–P3 / aktarım ve yayılma:** Beklenen Fed patikasının değişimi faiz ve USD üzerinden altına aktarılabilir; ardışık veriler aynı yönü güçlendirebilir veya rakip haberlerle mekanizma yön değiştirir.
- **P4–P5 / yorulma-bitiş:** Faiz/USD hareketinin sönmesi, beklenene dönmesi, yeni ters sürpriz veya güvenli liman/likidite mekanizmasının baskınlaşması.
- **Alt yollar:** `G01-A` gevşek para politikası beklentisi / fırsat maliyeti düşüşü; `G01-B` sıkılaşma beklentisi / fırsat maliyeti artışı; `G01-C` makro verinin etkisinin finansal stres veya güvenli limanla bastırılması.
- **Ayırıcı iz:** Gerçek zamanlı beklenti-vintage + açıklama sonrası faiz/reel getiri ve USD + aynı-UTC XAU ve mümkünse diğer metaller.
- **Yanlışlayıcı:** Makro açıklamanın saatinde baskın hareket yok; faiz/dolar farklı yöne tepki veriyor; daha erken eşzamanlı başka katalizör hareketi açıklıyor. Tek başına fiyat UP/DOWN etiketi G01'i doğrulamaz.

### G02 — Ticaret, tarife ve ekonomi politikası

**Çekirdek:** Ticaret veya politika rejimi değişimi → büyüme, enflasyon, belirsizlik ve sınır ötesi sermaye beklentileri → altın üzerinde birbirine rakip kanallar.

- **P0:** Tarife müzakeresi ve olası uygulama beklentisi, dış ticaret maruziyeti, büyüme kırılganlığı, enflasyon beklentisi, piyasa kaldıraç/likidite durumu.
- **P1:** Vergi/tarife oranı veya kapsam değişikliği; yaptırım, erteleme, anlaşma, yargı veya uygulama kararı.
- **P2–P3:** `G02-A` belirsizlik → güvenli liman talebi; `G02-B` maliyet/enflasyon → faiz/USD baskısı; `G02-C` ani risk ve nakit ihtiyacı → altının diğer varlıklarla beraber satılması. Açıklamaların sıralaması birden fazla dalga doğurabilir.
- **P4–P5:** Müzakere/erteleme/anlaşma; tarifenin fiyatlara yerleşmesi; likidite ihtiyacının bitmesi; başka mekanizmaya geçiş.
- **Ayırıcı iz:** Politika ilk kaynağı ve yürürlük bilgisi; reel/nominal faiz, USD, hisse, altın ve gümüşün ortak ya da ayrışan tepki işaretleri.
- **Yanlışlayıcı:** Fiyat yolu tarife haberinden önce başlıyor; ekonomik aktarım değişkenleri uyumsuz; aynı anda daha kuvvetli faiz/likidite haberi bulunuyor.

### G03 — Jeopolitik ve güvenlik riski

**Çekirdek:** Çatışma/gerilim/ateşkes/arz riski → güvenlik primi, enerji, büyüme ve fonlama kanallarının rekabeti.

- **P0:** Önceden fiyatlanmış risk primi, enerji arzı kırılganlığı, faiz/enflasyon duyarlılığı, risk iştahı ve kaldıraç.
- **P1:** Kaynağı doğrulanmış yeni güvenlik/çatışma/diplomasi gelişmesi; söylenti ile teyit edilmiş ilk bilgiyi ayır.
- **P2–P3:** `G03-A` güvenli limana geçiş; `G03-B` enerji fiyatı → enflasyon/faiz yeniden fiyatlama; `G03-C` riskli pozisyon ve fonlama baskısı → likidite amaçlı satış.
- **P4–P5:** Diplomasi/ateşkes, korku priminin sönmesi, olayın uzamasıyla fiyatlanmış riskin normalleşmesi veya faiz/likidite kanalının baskınlaşması.
- **Ayırıcı iz:** İlk güvenlik haberi, enerji ve risk varlığı hareketi, USD/faiz ile altın/gümüş tepkisinin senkron sırası.
- **Yanlışlayıcı:** Ekonomik bağlantı yok, haber fiyat değişiminden sonra yayımlanmış veya piyasa tepkisini farklı makro açıklama açıklıyor.

### G04 — Merkez bankası, rezerv, fizikî altın ve fon akışı

**Çekirdek:** Portföy/rezerv tercihi veya fizikî-finansal altın talebi → arz-talep ve pozisyon dengesinin değişmesi. **Ait olunan dönem ile bilginin yayımlanma zamanı ayrıdır.**

- **P0:** Rezerv tercihi, ETF/OTC/fizikî talep eğilimi, vade piyasası stokları ve pozisyon yoğunlaşması; metal bazlı talep/arz ayrışması.
- **P1:** Yeni erişilebilir akış verisi, politika açıklaması veya gerçek piyasa emir/likidite değişimi. Sonradan yayımlanan aylık rapor ilk tetik sayılmaz.
- **P2–P3:** `G04-A` kalıcı alım/arz darlığı; `G04-B` ETF/CTA/pozisyon kaynaklı momentum; `G04-C` birbiriyle ayrışan fizikî ve finansal piyasa kanalları.
- **P4–P5:** Alımların yavaşlaması, akışın tersine dönmesi, aşırı pozisyon veya faiz/USD baskısının yeniden üstün gelmesi.
- **Ayırıcı iz:** Veri yayım gecikmesi, ETF/CFTC vintage, fizikî prim ve vadeli yapı; XAU–XAG–Pt–Pd birlikte/ayrışık tepki.
- **Yanlışlayıcı:** “Talep vardı” kanıtı ancak fiyat hareketi bittikten sonra erişilebilir; gözlenen akış yetersiz ve eşzamanlı makro haber daha güçlü.

### G05 — Finansal stres, fonlama ve zorunlu tasfiye

**Çekirdek:** Kredi/teminat/fonlama şoku altını **iki zıt yoldan** etkileyebilir: kaçış talebi veya nakit sağlamak için altın satışı.

- **P0:** Kaldıraç, teminat baskısı, kredi spreadleri, kısa vadeli finansman ve piyasa derinliği.
- **P1:** Kredi olayı, marjin gereği, piyasa derinliği daralması veya fonlama erişiminin şoklanması.
- **P2–P3:** `G05-A` zorunlu satış: altın ve başka likit varlıklarda birlikte düşüş; `G05-B` güvenli liman: altına talep artışı; `G05-C` ilk satış sonrası fonlama rahatlayınca ters hareket.
- **P4–P5:** Nakit ve teminat ihtiyacının karşılanması, kredi riskinin çözülmesi veya korkunun yeni kanala geçmesi.
- **Ayırıcı iz:** Kredi/fonlama göstergeleri, hisse/emtia/metal eş hareketi, hacim ve makas, USD/faiz tepkisi.
- **Yanlışlayıcı:** Altına özel düşüşe rağmen genel risk varlıkları güçlü; zorunlu teminat olgusuna dair gösterge yok; gözlem yalnız fiyat düşüşünden çıkarılmış.

### G06 — Pozisyon, momentum, stop zinciri ve içsel dönüş

**Çekirdek:** Önceki fiyat hareketi ve piyasa mikro-yapısı → pozisyon yoğunlaşması, emir/stop zinciri, kaldıraç çözülmesi veya kısa pozisyon sıkışması → haberden bağımsız ya da haberle güçlenmiş fiyat sapması.

- **P0:** Tek yönlü uzun trend, aşırı pozisyonlanma, oynaklık, finansman/marjin, dar piyasa derinliği.
- **P1:** Destek/direnç kırılması, emir dengesizliği, zorunlu risk azaltma veya küçük bir katalizörün stopları tetiklemesi; yalnız teknik kırılım **neden kanıtı değildir**.
- **P2–P3:** `G06-A` trend yönünde sıkışma/stop devamı; `G06-B` kâr alma veya aşırı uzama sonrası tersine dönüş; `G06-C` ardışık likidite boşluklarıyla çalkantı.
- **P4–P5:** Emir baskısının tükenmesi, derinliğin toparlanması, pozisyonların dengelenmesi veya dış makro/jeopolitik DNA'nın devralması.
- **Ayırıcı iz:** Gerçek hacim/emir akışı veya bunun sınırlı vekilleri, vade ve opsiyon pozisyonu, metal ayrışması, aynı-UTC genel risk doğrulaması.
- **Yanlışlayıcı:** Ayrışmayı güçlü ve önceden yayımlanmış dış haber açıklıyor; emir/pozisyon verisi bulunmuyor. Bu durumda G06 yalnız olasılıktır.
- **Sınır:** Bu ailenin uzun fiyat-bacağı karakteri için bağımsız yeterli uzun örnek desteği henüz yoktur; sırf dönüş yaşandı diye otomatik G06 ataması yapılamaz.

### G07 — Belirsiz, çoklu nedenli veya henüz ayrıştırılamamış

**G07 başlı başına ekonomik DNA değildir; sınıflandırma ve kanıt yönlendiricisidir.** Şu durumlardan biri varsa seçilir: birden fazla rakip mekanizma aynı anda geçerli; ilk haber bilinmiyor; veri erişim gecikmesi var; fiyat ve haber zamansal sırası ters; hiçbir adayın ayırıcı izi yeterli değil.

**Çözüm yolu:** Aday alt kanalları ayrı `candidate_DNA_ID` olarak kaydet, hangisinin neyi açıklayamadığını yaz, farklı zaman/varlık penceresi ve şoksuz/ters kontrol iste. Kanıt yeterli olana kadar `UNRESOLVED` bırak. G07'yi zorla yeni bir nedene dönüştürme.

## 3. DNA'nın görünümü: fiyat karakteri ayrı bir eksendir

Ekonomik DNA'nın kimliği (**G ailesi**) ile gerçekleşen fiyat yolunun **M/S morfolojisi** birbirine karıştırılmaz. Aynı G01 farklı bağlamlarda M1, M3 veya M4 üretebilir; M4 ise farklı G ailelerinden gelebilir.

| Morfoloji | Tarafsız karakter tarifi | Genellenebilir yorum sınırı |
|---|---|---|
| **M1 — Erken impuls** | Toplam gözlenen bacak hareketinin büyük bölümü başlarda gerçekleşir | Gerçek ilk haber saati veya önceden görülebilen bitiş değildir |
| **M2 — Düzenli sürme** | Fiyat yolu az karşı dalga ile net yönde ilerler | Sürmenin ekonomik nedeni ayrıca doğrulanır |
| **M3 — Gecikmeli hızlanma** | İlk bölüm görece küçük; sonra hareket ivmelenir | Geç gelen haber/aktarımı ayrıca araştır |
| **M4 — Dalgalı / sık dönüş** | Yol boyunca tekrarlı ters hareketler ve düşük net yol etkinliği vardır | Ücret ve makas, geriye dönük her dönüşte işlem yapılmasını cazip göstermez |
| **M5 — Çok dalgalı / geçiş** | Birden fazla evre veya rekabet eden gelişim yolu vardır | Alt olaylar ayrıştırılır; bir habere tüm dalga atfedilmez |
| **M0 — Ölçüm yetersiz** | Uzun bacak için yeterli örnekleme yok | Uzun morfoloji zorlanmaz |
| **S1–S4 / S0** | Kısa pencerede ilk impulsun sürmesi, ters dönmesi, gecikmeli büyüme, ücret-altı net hareket veya veri yetersizliği | Gelecek ufuk gerçekleşmeleri **ex-post etiket**; olay tetik saati veya canlı öngörü değildir |

**Sınıflandırma eşikleri, örnek adedi, performans oranları, gözlenen tarihli yollar ve fiyat ölçüm sözleşmeleri burada değil OLAY-02 sayısal kanıtlarında yaşar.** Buradaki M/S adları bilimsel olarak keşfedilip bağımsız doğrulanmış doğal kümeler değildir.

## 4. Olay örgüsünün evre grameri

| Evre | Ekonomik DNA'da aranacak değişim | Aynı-UTC ayırıcı kanıt |
|---|---|---|
| **P0 / latent önkoşul** | Kırılganlık, beklenti, varlık ilişkileri ve pozisyon birikimi | Haber öncesi as-of veri, mevcut piyasa rejimi |
| **P1 / katalizör** | Beklenen yapıya yeni bilgi/şok girer | Özgün kaynak ve erişilebilirlik; aynı anda rakip bilgi |
| **P2 / ilk fiyat aktarımı** | Bir veya daha fazla ekonomik kanal işlemeye başlar | XAU ve aktarım değişkenlerinde gerçek zaman sırası |
| **P3 / yayılma** | Mekanizma güçlenir, sönümlenir veya yeni dalga yaratır | Ardışık bilgi ve çoklu varlıkta teyit/ayrışma |
| **P4 / doygunluk/çatallanma** | Beklenti kalabalıklaşır, kanal değişir, karşıt haber baskınlaşır | Alternatif kanal, yeni fiyat/likidite koşulları |
| **P5 / çözülme/geçiş** | Aynı mekanizma azalır, başka DNA devralır veya neden belirsizleşir | Yapısal değişimin kanıtı; sonradan seçilmiş tepe/dip tek başına değil |

Her aile ve alt varyant bu gramer üzerinden tanımlanır. **P0→P1→P2→P3→P4→P5 zorunlu doğrusal sıra değildir**: bazı gözlemler P2'de kesilir; P3 yeniden tetiklenebilir; P4 ile P3 iç içe geçebilir; ayrı mekanizmalar aynı anda etkindir. Her faz ataması ayrıca `KNOWN_AS_OF`, `RETROSPECTIVE_ONLY` veya `UNKNOWN` taşır. Geriye dönük fiyat dönüşü bir ekonomik şokun sona erdiğinin kanıtı değildir.

## 5. DNA–DNA etkileşimleri ve dönüşüm kuralları

**Amaç yalnız tekil olay ailesi değil, birbirini etkileyen mekanizma ağını tanımlamaktır.** Aşağıdakiler **olasılık yollarıdır, tarihsel olarak doğrulanmış zincirler değildir**.

| Olası etkileşim | Bileşen grafiği | Gerçekten ayırt etmek için |
|---|---|---|
| Makro sürpriz + risk stresi | `G01 ↔ G05` | Faiz/USD ilk tepkisi, kredi stresi ve güvenli liman eşzamanlılığı |
| Tarife ve güvenlik endişesi | `G02 ↔ G03` | Fiyat hareketine önce hangi doğrulanmış bilgi ve enerji/risk kanalı girdi? |
| Jeopolitik risk → maliyet/faiz baskısı | `G03 → G01` adayı | Enerji/enflasyon beklentisi ile faiz patikasının ara bağlantısı |
| Politik şok → fonlama zorlanması | `G02 → G05` adayı | Kredi/marjin/liquidation teyidi ve haber sırası |
| Talep artışı → aşırı pozisyon → düzeltme | `G04 → G06` adayı | Gecikmesiz akış ile gerçek pozisyon/likidite birikimi |
| Fonlama şoku → nakit satışı → güvenli liman | `G05-A → G05-B` adayı | Fonlama rahatlaması ve risk varlıkları/altın işaret değişimi |

**Bağ türü zorunlu:** `CO_OCCURRENCE` (yalnız birlikte gözlem), `TEMPORALLY_ORDERED`, `TRANSMISSION_CONSISTENT`, `RIVAL_TESTED`, `INDEPENDENTLY_VALIDATED`. Birlikte hareket `CAUSES` bağlantısı değildir. Her aday grafiğin test edilebilir ayırıcı değişkenleri vardır; **grafiğin olay bazlı kenarları ve kaynakları OLAY-02'dedir**, burada yalnız jenerik mekanizma vardır.

## 6. Çapraz vaka araştırmasından çıkan tarihsiz yapı dersi — rol ayrıştırması

**Farklı araştırmacılar aynı fiyat örgüsünü bazen haber başlığıyla, bazen faiz/likidite aktarımıyla, bazen de pozisyon çözülmesiyle adlandırabilir.** Bu yüzden `G01–G06`'yı tek bir `primary_family` olarak zorlamak yerine şu **dört farklı rol** açıkça araştırılmalıdır:

- `TRIGGER_DNA`: Yeni ekonomik bilgi/şok hangi tür? (Makro sürpriz, tarife, güvenlik, rezerv politikası, kredi şoku; gerçekten ilk açıklanan mı?)
- `TRANSMISSION_DNA`: Fiyat etkisi hangi aracılarla taşındı? (Faiz/USD, güvenli liman, enflasyon, fonlama/teminat, fiziki talep)
- `AMPLIFIER_DNA`: Önceden birikmiş hangi yapı etkiyi büyüttü veya tersine çevirdi? (Kaldıraç, ETF/CTA/COMEX pozisyonu, likidite ve emir akışı)
- `RESPONSE_MORPHOLOGY`: Fiyat yolunun şekli nedir? (M/S sınıfları; sadece fiyat sonucudur, ekonomik kökenin kimliği değildir)

**Örnek tarihsiz koşullu örgüler; şu anda hipotez:**

1. `G05 kredi/fonlama şoku → güvenli liman talebi ↔ G01 faiz indirim beklentisi`: güvenli liman alımı ve faiz kanalını ayrıştır; biri diğerinin yerine tek aile seçilmez.
2. `G02 tarife/politika katalizörü → G05 fonlama baskısı → G06 pozisyon tasfiyesi`: aynı fiyat düşüşünü üç ayrı tarihli neden gibi sayma; biri tetik, biri aktarım, biri kuvvetlendirici olabilir.
3. `G04 rezerv/ETF/fizikî bilgi + G01 makro açıklama`: önce/sonra gelen ayrı bilgi şoklarının etkilerini karşılaştır; geç yayınlanan talep raporu ilk katalizör değildir.
4. `G01 reel faiz/USD kanalı + G04 fon akışı`: aynı yönlü veya ters etkiler olabilir; zaman ve yayın/vintage ayrılmadan ortak yön kuralı çıkarma.
5. `G06 pozisyon sönümlenmesi ↔ G05 kredi/fonlama şoku`: geri çekilme tek başına genel fonlama krizi değildir; bağımsız fonlama göstergesi olmadan G05 doğrulama.

**Yöntemsel sonuç:** DNA sınıflandırması `tek etiket` değil, `rol × mekanizma × evre` olarak çalışır. Her mekanizma bağlantısının `SOURCE`, `RIVAL`, `TIMING`, `INDEPENDENT_ASSET_EVIDENCE`, `STATUS` kayıtları tarihli kanıt manifestinde tutulur. Bu bölümde örnek tarih, fiyat seviyesi ve olay kimliği kullanılmaz. **Tarihsel birden fazla yorumun bulunması yeni kanıt oluşturmaz; yalnız sınanacak rakip hipotezleri gösterir.**

## 7. Yeni DNA keşfetme, güncelleme ve yanlışlama sözleşmesi

1. **Aday oluştur:** Mevcut G ailesinin içine sığmayan tekrar edilebilir yeni aktarım yolu varsa `Gxx-ALTn` taslağı oluştur; yalnız farklı fiyat grafiğine bakıp yeni DNA yaratma.
2. **Önkoşul + tetik + aracı + sonuç:** Adayın haber/şokun ilk erişim anında bilinen önkoşullarını, beklenen ara piyasa tepkisini, farklı gelişim dallarını ve yanlışlayıcılarını önceden tarif et.
3. **Karşıt örgüleri zorunlu ara:** Aynı haber ailesinde ters yön, farklı morfoloji, benzer piyasa koşullarında olaysız kontrol; kayıtlarda bu yoksa `INSUFFICIENT_COMPARATORS`.
4. **Eksik değer bilinmezdir:** USD/faiz veya SI gibi kaynağı bulunmayan kanalları sıfır veya geriye dönük uydurulmuş fiyat olarak kullanma. Gecikmeli fon/rezerv raporu olay anına taşınmaz.
5. **Gerçek nedensellik iddiasını kısıtla:** İlk haber kaynağı, piyasa zaman sırası, bağımsız aktarım doğrulaması ve rakip mekanizma kontrolü olmadan `CAUSAL` yazma. Fiyat bacağına geriden seçilmiş bitiş ekonomik evre bitişi sayılmaz.
6. **Genellemenin sınırını koru:** Tüm tarihsel arşiv keşif için kullanılabilir; bununla oluşan DNA aynı arşivde “kör tahmin başarısı” olarak puanlanamaz. Ayrı donmuş zaman-as-of sınavı ve maliyetli karar çalışması ANA-01 yöntem sözleşmesindedir.
7. **Kanıt yükseltme:** `DNA_CANDIDATE → SOURCES_TIMED → TRANSMISSION_CONSISTENT → RIVAL_CONTROL_TESTED → INDEPENDENTLY_VALIDATED`. DNA bazında kanıt bağlantıları, gerekçeler ve eksikler OLAY-02 altında değerlendirilir; kanıt düzeyi kayıtsız yükseltilmez.
8. **Sürüm yönetimi:** Ekonomik çekirdeği değişmeyen DNA'nın varyantını güncelle; çekirdek değişiyorsa yeni alt varyant aç ve eskisine `superseded_by` kaydı bırak. Tarihli değişiklik günlüğü ve eski tanımın tam sürümü Git geçmişindedir; DNA metnine olay tarihi eklenmez.

**Başlangıçtaki bilgi sınırı:** Bu katalog, ekonomik mekanizmaların **test edilecek koşullu tanımlarıdır**. G01–G06 tanımlanmış, G07 bilinmezlik yönlendiricisidir. Bunların hiçbirine kanıtlanmış fiyat başlatıcısı, iyi kalibre edilmiş sonraki yön tahmini veya otomatik banka al/sat izni atanmamıştır.

## 8. DNA ile koşullu karar bilgisinin bağlantısı

**Bu kütüphanede tarih veya vaka getirisi değil, yalnızca koşullu karar mekanizması bulunur.** Karar hipotezleri ekonomik DNA, gözlenmiş evre, portföydeki başlangıç varlığı (`GOLD/CASH`), beklenen **kalan** getiri dağılımı ve toplam işlem maliyetiyle birlikte tanımlanır. Aşağıdaki ilk üç kod önceki öğrenme sicilinden **genel ilke düzeyinde korunmuştur**; hiçbiri kalibre edilmiş, bağımsız doğrulanmış veya otomatik AL/SAT izni değildir.

| Hipotez ID | DNA + gözlemlenmesi gereken evre ve koşul | Araştırılacak karar ve yanlışlama |
|---|---|---|
| `H-UP01` | `G01-A` adayı, P1 sonrası P2/P3; önceden bilinen ücret/enflasyon/faiz beklentileri ve XAU tepkisi tutarlı; rakip güvenli liman/likidite kanalı dışlanmış olmalı | `CASH → GOLD` alım adayı / zaten GOLD ise koruma adayı **yalnız beklenen kalan UP getirisi alım + olası çıkış maliyeti ve makası aşıyorsa**. Aksi durumda nakitte beklemek de geçerli. Güçlü başlık tek başına AL değildir. |
| `H-DN01` | `G01-B` adayı, P1 sonrası P2/P3; faiz/USD kanalı ve düşüşün kalıcılığı as-of destekleniyor; tek M15 düşüşü yeterli değil | `GOLD → CASH` çıkış adayı **yalnız beklenen kalan korunabilir DOWN hareketi satış ve muhtemel yeniden giriş maliyetini aşıyorsa**. Düşüş zaten tamamlandıysa geç SAT yanlışlanır. |
| `H-HOLD01` | İlk güçlü görünen fakat kısa/terslenebilir tepki; `G01/G05/G06` olasılıkları ayrıştırılmamış veya `P2 → P4` ihtimali yüksek; kalan hareket maliyete kıyasla belirsiz | `GOLD TUT` / `CASH BEKLE` adayı: sırf tek fiyat şoku yüzünden ücret ödeyerek gidip gelmeme. Büyük ve devam eden gerçek DOWN olasılığı kontrol edilmezse kör TUT de yanlış olabilir. |

**İşlem kuralı geçiş kapısı:** `DNA_GROUNDED` + `PHASE_ASOF_OBSERVABLE` + `EXPECTED_REMAINING_RETURN_CALIBRATED` + `ALTERNATIVE_STATE_COMPARED` + `COSTED_OOS_VALIDATED`. Bu beş koşul tamamlanmazsa öneri `RESEARCH_ONLY / NO_AUTOMATED_ACTION` olarak kalır. Bunlar araştırmanın hedef fonksiyonudur; geçmişte ex-post elde edilen kazançları bağımsız model kanıtı yapmaz.

**Açık bilgi açığı:** Şu anda olayların çoğunda ilk haberin ekonomik yayılma zinciri ve P0–P5 evresi doğrulanmamıştır; bunlara yukarıdaki karar hipotezlerini atanmış ve çalışırmış gibi göstermeyin. Ayrıntılı zamanlı olay ve karar kanıtı yalnız [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) içindedir.

## 9. Öğrenmenin saklandığı yer — DNA ile anıyı ayır

- **ÖĞREN-03:** Yalnız aile ve alt varyant şemaları, ayırıcı DNA izleri, olası geçiş grafikleri, yanlışlama koşulları, kanıt düzeyinin tanımı ve jenerik mekanizma sürümleri.
- **OLAY-02:** Tek tek tarihli olaylar, ilk kaynaklar, vaka ID'leri, haber/veri saatleri, XAU–metaller/faiz/USD tepkileri, aşama etiketlerinin gözlemsel gerekçeleri, rakip mekanizma ve sonuç.
- **ANA-01:** Hangi deneyin nasıl yürütüleceği, saat güvenliği, keşif/denetim ayrımı, maliyet ve karar protokolü; eski tarihli araştırma günlüğü.
- **DURUM-04:** Aylık inceleme, eksik veri, yeniden test, araştırma durumu.

**Yalnız DNA'yı bilmek olayın fiilen gerçekleştiğini ispatlamaz.** Bir vakayı incelemek için OLAY-02'daki kanıt zinciri açılır; bu dosyaya sadece farklı olaylarda tekrar kullanılabilecek, koşullu ve yanlışlanabilir öz aktarılır.

## 10. Kanıta dayalı DNA çözümleme — sistematik sınıflandırma ilkeleri

**Öğrenme bulgusu:** Bir önceki fiyat hareketine G ailesi yapıştırılması ile ekonomik DNA **keşfedilmiş olmaz**. Ekonomik DNA'nın kimliğine ilişkin kanıt, **(i) şok/bilgi içeriği, (ii) aracılık kanalı, (iii) pozisyon ve likidite kuvvetlendiricileri, (iv) fiyatın ayrı ex-post davranışı** olarak dörde ayrılmalıdır. Bütün bu roller aynı aileden olmayabilir.

### 10.1 Birincil DNA'nın yanında türev alt yollar

| Ana DNA | Tarihsiz alt-yol adayları |
|---|---|
| **G01** | `G01-A` gevşeme/fırsat maliyeti azalışı; `G01-B` sıkılaşma/fırsat maliyeti artışı; `G01-C` baskın karşı mekanizma; `G01-X` makro var ama alt yön ayrışmamış |
| **G02** | `G02-A` ticaret belirsizliği; `G02-B` politika/ticaret geriliminde rahatlama; `G02-C` tarife kaynaklı likidite/teminat baskısı |
| **G03** | `G03-A` risk tırmanışı ve güvenli liman; `G03-B` tırmanışın çözülmesi; `G03-C` enerji-enflasyon-faiz baskısına dönüş |
| **G04** | `G04-A` rezerv/merkez bankası; `G04-B` ETF/CTA/COMEX finansal akış; `G04-C` EFP/teslimat ve fizikî-vadeli sürtünme |
| **G05** | `G05-A` teminat/likidite amaçlı satış; `G05-B` finansal stres altında güvenli liman; `G05-C` fonlamanın toparlanması |
| **G06** | `G06-A` momentum/sıkışma; `G06-B` kâr alma/pozisyon çözülmesi; `G06-C` stop/emir akışı zinciri |
| **G07** | Nedensel belirsizlik **yönlendiricisidir**, ekonomik şok DNA'sı değildir |

**Sınıf ile rol ayrı olmalı:** `TRIGGER_DNA` yeni haber şokunun kaynağı, `TRANSMISSION_DNA` ekonomik aktarım, `AMPLIFIER_DNA` kaldıraç/pozisyon/likidite şiddetlendirici, `RESPONSE_MORPHOLOGY` yalnız gerçekleşmiş fiyat yolu. Farklı retroaktif hikâyelerin aynı fiyat dalgasını farklı G koduyla açıklaması bu roller karıştırıldığında beklenebilir; bir nedeni bağımsız doğrulamaz.

### 10.2 Fiyatın ekonomik nedene tanık olduğu durumlar — ayrı morfoloji kontrolü

Fiyat hareketi altının başka piyasalara göre davranışıyla da **tarif** edilmelidir. Ekonomik mekanizmalarla otomatik eşleştirilmeyecek beş **gözlemsel** kategori:

1. `BROAD_COSELL`: Altın, gümüş, hisse ve petrol birlikte geriler. Fonlama/tasfiye **adayı** olabilir; gerçek marjin-kredi teyidi olmadan G05 kanıtı değildir.
2. `METAL_EQUITY_CODIRECTIONAL`: Altın, beyaz metaller ve hisse birlikte ilerler. Makro/risk-on/daha geniş likidite kanalının ayırt edici incelemesini gerektirir.
3. `METAL_COHERENT_EQUITY_DIVERGENT`: En az iki beyaz metal altınla aynı, hisseler ters yönde; altın fiyatı yalnız riskli hisse talebinin karşıtı olarak açıklanamaz.
4. `GOLD_WHITE_METAL_DECOUPLING`: Altın diğer beyaz metallerden en az ikisine karşıt hareket eder; altına özgü güvenli liman/fizikî/rezerv veya göreli emtia talebi ayrı araştırılır.
5. `HAVEN_LIKE_DIVERGENCE`: Altın yükselir, hisse düşer ve en az bir beyaz metal ters gider; güvenli liman **benzerliği**, nedensel ispatı değildir.
6. `DATA_INSUFFICIENT`: İmza güvenilir çıkarılamaz.

Bu kategoriler geçmiş günlük veya çok-günlü fiyat serileriyle **ex-post** oluşur. İntraday kaynakların eşzamanlılığı doğrulanmadan canlı karakter ve P0–P5 evre tanıması yapılamaz.

### 10.3 Makro şokun birbirinden ayrı üç hedefi

- `SURPRISE_CONTENT`: İlk duyurunun gerçek zamanlı beklentiden sapması ve alt bileşenler.
- `IMMEDIATE_RESPONSE`: İlk tamamlanmış XAU barı ve aynı anda faiz/dolar/metal tepkisi.
- `PERSISTENCE_AND_STAGE`: Ayrı ufuktaki devam, tersleme ve ekonomik baskınlık değişimi.

Tek sürpriz işareti altın yönünü evrensel belirlemez; ilk tepkinin yönü, sonra ölçülen uzun fiyat epizodu yönüyle aynı olmak zorunda değildir. **Makro takvimini ve açıklama öncesi bilinen beklentiyi, sonraki fiyat sonucuyla karıştırma.** Bir makro açıklama başka bir ilk haberin yarattığı şokun ortasına düşebilir.

### 10.4 Belge anlatısından DNA çıkarmanın kanıt katmanları

- `D0`: Olay penceresinde zamanlı kaynak açıklaması yok; genel tema/sonradan rapor yalnız araştırma ipucudur.
- `D1`: Olay penceresinde tarihli haber bağlamı var fakat `firstprint UTC`, ilk fiyat başlangıcı ve aracılık henüz doğrulanmadı.
- `D2`: Ayrıntılı vaka araştırması, rakip mekanizmalar ve ek çapraz varlık bağlamı var; **bunlar yine nedensel doğrulama değildir**.
- `D3` (*henüz atanmadı*): İlk kaynak ve piyasa eşzamanlılığı doğrulanmış, rakip/negatif kontrolleri sınanmış ekonomi aktarımı.
- `D4` (*henüz atanmadı*): Önceden dondurulmuş sınıflama bağımsız yeni olaylarda tekrar doğrulanmış.

**Güncel araştırma modelinde yalnız D0–D2 belgelerden öneri çıkarılmıştır.** Belgede yazan mekanizma alt tipi `CANDIDATE` kalır; geçmiş bacağın yönü veya geri dönük yüksek getirisi kanıt düzeyini yükseltmez. Makine-veri sınıflandırmasındaki sayımlar, olay kimlikleri, tarihler, haber bağlantıları ve nicel bulgular yalnız OLAY-02'dedir.

### 10.5 Gümüş ve sürekli vadeli kontrat ayrımı

`SI.c.0` (takvim-roll) ile `SI.n.0` (önceki gün açık pozisyonuna dayalı open-interest-roll) farklı kaynak serileridir. Mevcut bir gümüş saatlik arşivinin **varlığı**, her kontrol anında tamamlanmış ve taze gümüş verisi bulunduğu anlamına gelmez. Barın başlangıç/bitiş etiketi, kontrat değiştirme sırası, olay anında erişilebilirlik ve piyasa saati kontrolünden geçmeyen gümüş teyidi `MISSING_OR_STALE`dır, sıfır getiri değildir.

**Araştırma otoritesi:** Tarihli çoklu-DNA öneri tablosu, makro kontroller, çapraz-varlık fenotipleri, gerçek veri kullanılabilirliği ve bunların dayanağı [OLAY-02'de](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md). Bu ÖĞREN-03 yalnız tarihsiz **öğrenilmiş ayrım ilkelerini** saklar. Nedensel olarak kesinleşmiş DNA veya otomatik AL/SAT iddia edilmez.

