# GOLD — Küresel HABER → OLAY-02 → ÖĞREN-03 → ETKİ-05 Kural Sözleşmesi v1

**18 Ekim 2026 | GOLD-ADAPTIVE-MODEL-APP-01 | Kapsam: haberden kanıtlı ekonomik koşul etiketine geçiş | İŞLEM İZNİ: YOK | S1/S2/S3 kodu DEĞİŞMEDİ.**

## 1. Kullanıcı amacı

Var olan adaptif algoritmayı değiştirmek veya yeni algoritma kurmak yerine; **haber nereden çıktı, tam olarak ne değişti, hangi tarihsiz ekonomik mekanizmaya uyuyor, hangi koşul birleşimleri aktif, karşıt mekanizma nedir ve gerçekten altının ne kadarını açıklayabiliyor?** sorularını aynı haber kaydından sıralı ve zaman-doğru yanıtlayan altyapı. ABD merkezli tek başlık sisteminden **küresel haber akışına geçiş**; **altın UP/DOWN yönünü haberin menşei veya tek anahtar sözcükten uydurma**.

## 2. Aynı haberin dört ayrı otoritesi

1. **HABER KAYNAK KATALOĞU:** Haber kaynağı (`publisher`), kurumsal alan adı (`sourceUrl`), **haber menşei** (`jurisdiction`), **etkilenen olay coğrafyası** (gerekirse ayrı `eventLocation`) ve tür (`eventKind`). Dünyada ABD, AB, Birleşik Krallık, Çin, Hindistan, Japonya, İsviçre, Türkiye ve küresel kuruluşlar. 32 referans kaynak. **Resmî yayıncı** birincil haber otoritesi; Reuters/AP ikinci kaynak; CFTC/WGC/IMF gecikmeli araştırma/akım; LBMA/CME/SGE piyasa referanslarıdır. Bunların rollerini birbirine dönüştürmeyiz.
2. **OLAY-02 (tarihli):** `event_id,source,original_article_url,event_time,published_at,available_at,detected_at,firstprint_evidence_id,original_consensus_vintage,underlying_event_type,economic_numbers,actual_vs_consensus,contradictions`. OLAY-02 ekonomik ilk haberin kanıt adresidir. İlk haber ile fiyat bacağının aynı anda olması nedensellik değildir.
3. **ETKİ-05 (tarihsiz K maddeleri):** `K01–K48` basit koşullar. **K01/K02 US CPI**; **K03/K04 US NFP**; **K06/18 ücret**, **K07/19 işsizlik**, **K16/17 çekirdek CPI**. **K20/21/22** merkez bankası kararı piyasa beklentisi üstü/altı/eşit; **K23/24** beklentiye göre şahin/güvercin iletişim; **K25–26** rezerv alış/satış; **K27–28** tarife/sanction artırma/gevşeme; **K29–30** jeopolitik risk; **K31–32** fonlama; **K33–34** fizikî altın talebi; **K35–36** ETF fon akışı; **K37–38** enerji arzı; **K39** merkez bankası faiz kararı var ama sürpriz bilinmiyor; **K40** basın toplantısı açıldı ama içeriğin yeni sürprizi bilinmiyor; **K41–44** ABD dışı enflasyon/istihdam sürprizi; **K45–46** ABD PCE; **K47–48** GSYH sürprizi. USD/faiz K08–11 ve stres K12/pozisyon K13 bağımsız veri yokken otomatik gerçek sayılmaz.
4. **ÖĞREN-03 (tarihsiz örgü):** K maddeleri ÖĞREN-03'teki `ORG01–ORG12` için **aday tetikleyici/aktarım/kuvvetlendirici** üretir; **kanıtlı neden veya doğrudan fiyat komutu değildir**. `TRIGGER_DNA / TRANSMISSION_DNA / AMPLIFIER_DNA / RESPONSE_MORPHOLOGY` ayrı roller; fiyat sonucu asla ekonomik şart yerine kullanılmaz.

## 3. Kodlanmış kural kümesi

**Kod:** [event_news_condition_router_v1.js](adaptive_trading_core/event_news_condition_router_v1.js) · **Dünya kaynak listesi:** [OLAY_02_KURESEL_HABER_KAYNAK_KURALLARI_V1_20261018.json](OLAY_02_KURESEL_HABER_KAYNAK_KURALLARI_V1_20261018.json) · **Tüm K kodları:** [ETKI_05_KOSUL_ETIKETLERI_V1_20261018.json](ETKI_05_KOSUL_ETIKETLERI_V1_20261018.json).

| Kural | Açık mantık | Hata engeli |
|---|---|---|
| **R01 Kaynak menşei** | Bir resmî haber `sourceId`, gerçek HTTPS yayıncı host'u, ülke/bölge, haber türüyle eşleşmeli. | Reuters/gazete yorumu resmî ilk-baskı gibi işaretlenmez; taklit alan adı reddedilir. |
| **R02 Bilgi zamanı** | `eventTime ≤ publishedAt ≤ availableAt ≤ detectedAt ≤ asof`. | Daha sonra duyulmuş haber geçmişteki AL/SAT'e sokulmaz; kayıt gecikiyorsa `PENDING_FIRST_ACCESS`. |
| **R03 Sürpriz** | Faiz/ücret/istihdam/CPI/PCE/GSYH için **gerçekleşme − açıklama öncesi piyasa konsensüsü**, birimi ve ilan duyarlığı korunur. | Faiz +50bp geldi diye K20 veya gold-DOWN etiketi otomatik YOK. Beklenti yayımlanma zamanı bilgi anından sonra ise `UNKNOWN`. |
| **R04 Konuşma metni** | CB basın toplantısı başladığı an sadece **K40**, gerçek söylenen cümle ilk duyulduktan ve önceki beklenti farkı belgelenirse **K23/K24**. | Konuşmanın başlangıcında henüz söylenmemiş son cümleleri kullanamaz. |
| **R05 Coğrafi şok** | Çin rezerv alımı, Hindistan vergi değişimi, Japonya faiz, Orta Doğu güvenlik, Avrupa bankası haberleri ülke ve kurumuna özgü tanınır. | Avrupa'nın ECB/BoE faizi NFP/CPI ABD haberine dönüştürülmez. Haberin çıktığı yer ile XAU fiyat aktarımı ayrı. |
| **R06 Gecikmeli kaynak** | WGC/IMF rezerv ve CFTC/ETF raporlarında *referans ayı/haftası* ile *yayımlanma anı* ayrı. | Bir ay sonra çıkan rezerv raporu önceki ayın 15dk haber tetikleyicisi sayılamaz. |
| **R07 Tekli ekonomik madde** | Uygun bilgi varsa K kodu üretilir, yoksa `UNKNOWN` tutulur. | `UNKNOWN` = `FALSE` değildir. |
| **R08 Çoklu madde** | Birden çok K aynı açıklamada veya yakın zamanda bağımsız kaynaklardan geldiyse eşleştirici **AND** kalıpları kurulur (14 `CRxx`). | 2+ koşulun birlikte bulunması garanti altın yükseliş/düşüşü değildir. |
| **R09 Mekanizma rekabeti** | Şahin + güvercin bileşen varsa `ORG01` ve `ORG02` rakip adayları birlikte korunur. | Bir baskın etiket diğer kanalı ve olumsuz örnekleri silmez. |
| **R10 Haber kümelenmesi** | Dört saat içinde çakışan haberler ayrı `event_id`, aynı `overlappingEpisode` grubu. | BoE+ECB+Lagarde üç bağımsız %1,7'lik düşüş sayılmaz. Bu pencere yalnız çakışma kontrolü için seçilmiştir; ekonomik etki ömrü değildir. |
| **R11 Olay saati** | İlk kaynak kanıtı doğrulanırsa event t0, son tamamlanmış pre-event fiyat ve ilk post-event bar ayrıca ölçülebilir. | Global S1/S2/S3 sıfırlanmaz; etki ölçümü fiyatın geçmiş global trendi ile karıştırılmaz. **Olay saati S1/S2/S3'e henüz kod olarak bağlanmadı.** |
| **R12 Bilimsel kapı** | Öğrenilmiş yön, büyüklük ve süre tahmininden önce yeterli bağımsız örnek, plasebo, piyasa rejimi ve ileri dönem kıyası gerekir. | İlk fiyat tepkisi veya tek başlık otomatik AL/SAT değildir. `action=null,tradeAllowed=false`. |

## 4. Kodlanmış 14 ekonomik AND birleşimi

Bu **olasılığı öğrenilmiş kurallar değil; araştırma sorgularıdır**:

| Kural | Gerçekleştirilecek şart | ÖĞREN-03 mekanizması adayı |
|---|---|---|
| CR01 | **K02+K17**: manşet ve çekirdek CPI beklentiden düşük | ORG01 |
| CR02 | **K03+K06**: güçlü istihdam + güçlü ücret | ORG02 |
| CR03 | **K03+K18**: güçlü istihdam + zayıf ücret | ORG01 + ORG02 çatışması |
| CR04 | **K03+K07**: güçlü istihdam + yüksek işsizlik | ORG01 + ORG02 çatışması |
| CR05 | **K03+K06+K19**: istihdam/ücret güçlü, işsizlik düşük | ORG02 |
| CR06 | K20+K08: beklentiden şahin faiz + doğrulanmış USD güçlü | ORG02 |
| CR07 | K21+K09: beklentiden güvercin faiz + USD zayıf | ORG01 |
| CR08 | K29+K37: güvenlik gerilimi + enerji arzı aksaması | ORG04 + ORG02 |
| CR09 | K31+K13: likidite şoku + bağımsız tasfiye delili | ORG12 |
| CR10 | K27+K31: ticaret şoku + fonlama krizi | ORG06 + ORG08 |
| CR11 | K25+K03: rezerv alımı bilgisi ve kuvvetli istihdam | ORG11 çoklu haber rekabeti |
| CR12 | K36+K13: ETF çıkışı + bağımsız pozisyon çözülmesi | ORG10 |
| CR13 | K23+K10: beklenenden şahin iletişim + doğrulanmış reel faiz artışı | ORG02 |
| **CR14** | **K39+K40**: faiz kararı ve basın toplantısı var fakat sürpriz ayrıştırılmadı | ORG01 + ORG02, yön **BİLİNMİYOR** |

**Kısıtlar:** K08/K09 ve K10/K11 dolar/ABD reel getiri kaynakları mevcut projede olay anı olarak bağlanmadı; ilgili CR06/07/13 için **şu anda gerçek altın yönü çıkarılamaz**. K13 teminat boşaltma gibi kavramlar fiyat grafiğine bakarak oluşturulamaz.

## 5. 2023 Ocak–Şubat gerçek haber örneği — düzeltme

[Çalıştırılmış tarihli örnek sonuç JSON](adaptive_trading_core/GLOBAL_NEWS_ROUTER_JANFEB2023_DEMO_20261018.json).

**8 tarihli haber kaydı** (6 Ocak NFP, 12 Ocak CPI, 1 Şubat Fed, 2 Şubat BoE, 2 Şubat ECB kararı, ECB basın toplantısı, 3 Şubat NFP, 14 Şubat CPI) sınıflandırıldı; **6 çakışma/ayrışma dönemi** oluşturuldu. **2 Şubat Avrupa grubu: `K39+K40 → CR14`**, `ORG01+ORG02` rekabeti. Fed bir gün önceki ayrı haber; 3 Şubat NFP ertesi günün ayrı haberi, 2 Şubat kararı için önceden kullanılamaz.

İlk-published fiyat 2023 haber URL'lerinin bulunması tek başına **konsensüs-vintage ve haberin tam ilk erişiminin** sertifikalandığı anlamına gelmiyor. Bu **katı/haklı güvenlik modunda** tarihsel CPI/NFP için arşivde bulunmuş `K03,K18,K19` gibi etiketler `retrospectiveArchiveLabelsNotRouted` alanında tutuldu; strict motor bunları canlı kanıt diye içeri **ALMADI**. Bunun sonucu tarihli BLS olayında `CONDITIONS_UNKNOWN` görülebilir; ekonomi olmadığından değil, kabul sözleşmesinin gerekleri sağlanmadığından. Merkez bankası kararları kaynaklı `K39` ve basın başlangıcı `K40` ayrı çıkarıldı.

Bu gösterim **gerçek haber kanıtlarını internetten canlı çekme** veya **ekonomik kuralları ilk fiyatı görünce geçmişe yazma** işlemi değildir. Girdileri tarihli resmî arşiv bağlantılarıyla araştırmacı verdi.

## 6. Çalıştırılmış test ve iş sınırları

- [35 temel + 5 çoklu madde = 40 otomatik test](adaptive_trading_core/test_event_news_condition_router_v1.js): **40/40 PASS**; kaynak ve alan adı, ülke uyumu, gelecek haber reddi, konsensüs tarihi, açıklama vs yönlendirme, Çin/Avrupa/Hindistan/Japonya/UN olayı, yanlış WGC/CFTC zaman ataması, kopya haber, çapraz-rakip ORG ve çakışma grubu.
- Kod `route(news,{asof,registry})`, `routeMany(news,{asof,registry})` dönüyor; **fiyat tahmini veya işlem üretmiyor**, ağdan haber otomatik indirmiyor. Özellik girişi dışarıdan kontrollü olay nesnesi olarak sağlanıyor.
- `FIRSTPRINT_ATTESTED_NOT_CAUSAL` yalnız önceden insan tarafından doğrulanmış kaynak ilk basım belgesiyle mümkün; programın tek başına web URL'si varsa gerçek neden bulduğu iddia edilmez.
- Gerçek kaynak elde etme/firstprint-arşivleme iş akışı, CPI/NFP 2023 beklenti sağlayıcısının tarihi, o ana kadar yayımlanan açıklama/metin parçaları, OLAY-02'nin 96 kanıt davasındaki 0/96 başlatıcı kanıt açığı hâlâ açık.
- **S1/S2/S3 ve bankanın %0,8/ayak işlem modeli** değiştirilmedi. Testten kâr, doğru tahmin veya yeni işlem sonucu üretilmedi. Altın USD/TRY/gram net değeri ayrı varlık/kur kanalı olarak modellenmelidir.

**Durum kodları:** `RULE_REGISTRY_DEFINED=YES`, `GLOBAL_PUBLISHERS=32`, `K_LABELS=48`, `CROSS_CONDITION_RULES=14`, `ORG01_12_COVERED=YES`, `INTEGRITY_TESTS=40_PASS`, `HISTORICAL_2023_NEWS_ROUTING_RUN=YES`, `LIVE_NEWS_INGESTION=NO`, `PIT_ASOF_CERTIFIED=NO`, `S1_S2_S3_INTEGRATED=NO`, `LEARNED_DIRECTION_ALPHA=NO`, `TRADE_ALLOWED=FALSE`.
