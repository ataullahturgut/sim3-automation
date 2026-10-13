# OCAK 2026 — 31 GÜNLÜK İLERLEYEN AS-OF ALTIN KARAR DENEYİ (YENİ 2026 OLAY MANİFESTLERİ KULLANILMADI)
**Çalışma tarihi:** 13 Ekim 2026. **Dönem:** 1–31 Ocak 2026. **Oluşturma yaklaşımı:** 2026 olay/katalizör manifesti veya 2026 model sonucunu **okumadan** bir kaynak taraması. 2023–25 mekanizma öğrenimleri ve 2025 ham fiyat geçmişi kullanılabildi. 2026'nın Ocak ayına ait olaylar yalnız kendi gününün veya daha önceki günlerin tarihli Reuters/Kitco haberlerinden ayrıca incelendi. Haberleri o gün sonradan revize edilmiş olabilecek kaynaklardan çektiğimiz ve ilk-baskı saatlerini bütünüyle doğrulayamadığımız için geriye dönük **günlük sıralı araştırma**, dokunulmamış canlı tahmin değildir.

## 1. Kronoloji ve önceden kilitlenen karar politikası
OCAK fiyat sonuçları çekilmeden önce `GOLD_JAN2026_ASOF_DAILY_DECISION_PROTOCOL_LOCKED_20261013.md` dosyasında açıkça kilitlendi. NY17 en son tamamlanmış 15dk HistData XAUUSD spot quote, geçmiş 5/20 seans getirileri ve SMA10:
- Önce CASH: beş seans r5 ≥+1.20%, r20>0, close>=SMA10 ise **AL**, aksi **TUT nakit**.
- Önce GOLD: üç seans r3 ≤−1.50%, veya 10-seans kapanış zirvesinden düşüş ≥2%, veya SMA10 altına iniş ve r5 ≤−0.50 ise **SAT**, aksi **TUT altın**.
- 31 Ocak takvim günü, 21 geçerli HistData altın seansı, 10 gün ana sağlayıcıda yok; 19 Ocak **erken kapanış** ve ayrı kaydedildi. 1 Ocak HistData'da yok ama Dukascopy alternatifinde alıntı var, bu nedenle mutlak piyasa tatili olarak tüm platformlara genellenemez.
- Başlangıç 100% nakit; 0.8% her alım ve satış bankacılık komisyonu, bid-ask banka makası ve kayma bilinmiyor. Alım/satım **karar anındaki kapanıştan değil**, bir sonraki yeni seanstaki ilk alıntıdan yapılmak üzere tanımlandı. Pozisyon tek altın veya nakit, açığa satış yok.
- Kilitli model HABER KULLANMAZ: bağımsız bir zamansal haber analisti yorumunu fiyat sonucunu gördükten sonra sırf başarılı görünsün diye karara eklemek yasaktı. Diğer metal/Nasdaq/ABD faiz/dolar panelleri yıllar sonra `available_as_of` tarihli geri yüklemelerdir, as-of doğrulanmış girdi olarak **kullanılmadılar**; ayrı `GOLD_JAN2026_ALL_31_DAYS_METALS_RISK_LAGGED_CONTEXT_20261013.csv` dosyasında şeffafça günlük önceki tarihli araştırma göstergeleri olarak incelendi.

## 2. TÜM 31 GÜN — FİYAT / KARAR / EŞZAMANLI BAĞLAM
| Tarih | NY17 altın kapanışı, US$/ons | O gün bitiminde kilitli karar | O tarihte yayımlanmış olabileceği belgelenen haber veya durum (kesin ilk dakika değil) | Gözlenen en kötü gün içi tepe→dip |
|---|---:|---|---|---:|
| 2026-01-01 | — | TUT (nakit) | Ana fiyat kaynağında seans yok | — |
| 2026-01-02 | 4,332 | TUT (nakit) | Bu tarih için doğrulanmış bağımsız yeni haber kaydı yok | -2.1% |
| 2026-01-03 | — | TUT (nakit) | Ana fiyat kaynağında seans yok | — |
| 2026-01-04 | — | TUT (nakit) | Ana fiyat kaynağında seans yok | — |
| 2026-01-05 | 4,448 | TUT (nakit) | [Venezuela müdahalesi sonrası güvenli liman talebi](https://www.reuters.com/business/energy/market-analysts-react-trumps-venezuela-gambit-2026-01-05/) | -1.0% |
| 2026-01-06 | 4,493 | AL | [Venezuela ve faiz indirimi beklentileri](https://www.kitco.com/news/off-the-wire/2026-01-06/gold-inches-closer-record-high-geopolitical-risks-fed-cut-bets-boost) | -0.7% |
| 2026-01-07 | 4,456 | TUT (altın) | [Altın ve gümüşte kâr satışı uyarısı](https://www.kitco.com/news/article/2026-01-07/profit-taking-price-pressure-gold-silver) | -1.7% |
| 2026-01-08 | 4,478 | TUT (altın) | [Gümüşte uzun pozisyon çözülmesi](https://www.kitco.com/news/article/2026-01-08/gold-price-down-amid-sharp-losses-silver) | -1.3% |
| 2026-01-09 | 4,509 | TUT (altın) | [ABD tarım dışı istihdam sürprizi: 50 bin](https://www.kitco.com/news/off-the-wire/2026-01-09/gold-set-weekly-gain-us-payrolls-miss-broader-uncertainty) | -0.8% |
| 2026-01-10 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |
| 2026-01-11 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |
| 2026-01-12 | 4,599 | TUT (altın) | [Powell soruşturması ve Fed bağımsızlığı tartışması](https://www.kitco.com/news/off-the-wire/2026-01-12/londons-ftse-100-dips-sterling-strengthens-amid-trump-powell-tensions) | -0.9% |
| 2026-01-13 | 4,586 | TUT (altın) | [TÜFE ve değerli metal teminat düzenlemesi](https://www.kitco.com/news/off-the-wire/2026-01-13/us-consumer-inflation-increases-steadily-households-paying-more-food) | -1.4% |
| 2026-01-14 | 4,626 | TUT (altın) | [İran gerilimi ve Fed özerklik kaygısı](https://www.kitco.com/news/off-the-wire/2026-01-14/gold-silver-hit-historic-highs-amid-geopolitical-strains-fed) | -0.9% |
| 2026-01-15 | 4,615 | TUT (altın) | [İran geriliminde yumuşama ve Grönland riski](https://www.kitco.com/news/off-the-wire/2026-01-15/gold-steadies-investors-keep-wary-eye-greenland-iran) | -1.1% |
| 2026-01-16 | 4,596 | TUT (altın) | Bu tarih için doğrulanmış bağımsız yeni haber kaydı yok | -1.8% |
| 2026-01-17 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |
| 2026-01-18 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |
| 2026-01-19 | 4,670 | TUT (altın) | [Grönland tarife tehdidi ve küresel riskten kaçış](https://www.kitco.com/news/off-the-wire/2026-01-19/stocks-fall-after-trumps-tariff-threats-gold-receives-safety-bid) | -0.9% |
| 2026-01-20 | 4,763 | TUT (altın) | [Grönland tarife riski; hisseler düşüyor altın yükseliyor](https://www.kitco.com/news/off-the-wire/2026-01-20/wall-street-slides-near-three-week-low-greenland-dispute-triggers) | -0.6% |
| 2026-01-21 | 4,832 | TUT (altın) | [Davos; güç kullanılmayacağı açıklaması ve altın zirvesi](https://www.kitco.com/news/article/2026-01-21/gold-early-record-high-trump-wont-forcibly-take-greenland) | -2.7% |
| 2026-01-22 | 4,936 | TUT (altın) | [Grönland tarifelerinden geri adım; risk iştahı değişimi](https://www.kitco.com/news/article/2026-01-22/gold-price-slightly-down-risk-appetite-improves) | -1.3% |
| 2026-01-23 | 4,984 | TUT (altın) | [Altın gümüş rekorlar; teknik ve güvenli liman alımı](https://www.kitco.com/news/article/2026-01-23/gold-silver-hit-new-record-highs-safe-haven-demand-bullish-charts) | -1.4% |
| 2026-01-24 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |
| 2026-01-25 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |
| 2026-01-26 | 5,010 | TUT (altın) | [Altın 5100 dolar; dolar zayıflığı ve siyasi belirsizlik](https://www.kitco.com/news/off-the-wire/2026-01-26/gold-hits-record-above-5100-geopolitics-drive-safe-haven-rush) | -2.4% |
| 2026-01-27 | 5,179 | TUT (altın) | [Altında yükseliş ve kalıcı jeopolitik risk anlatısı](https://www.kitco.com/news/off-the-wire/2026-01-27/gold-holds-momentum-uncertainty-fuels-safe-haven-bids) | -1.1% |
| 2026-01-28 | 5,415 | TUT (altın) | [Fed faizi sabit bıraktı; altında güçlü momentum](https://www.kitco.com/news/off-the-wire/2026-01-28/gold-nears-5400oz-rally-gains-momentum-uncertainties-mount) | -1.4% |
| 2026-01-29 | 5,379 | TUT (altın) | [Zirveden kâr satışları; risk işaretleri](https://www.kitco.com/news/article/2026-01-29/gold-silver-back-down-record-highs-profit-taking) | -8.9% |
| 2026-01-30 | 4,891 | SAT | [Warsh Fed adaylığı; altın gümüşte sert satış](https://www.kitco.com/news/article/2026-01-30/price-meltdowns-gold-silver-after-trumps-fed-chair-pick) | -14.1% |
| 2026-01-31 | — | TUT (altın) | Ana fiyat kaynağında seans yok | — |

Önemli: Gün içi diplerin bir kısmı sonraki fiyatların görülmesiyle teyit edilir; bu sütun yalnız gün bitiminde geçmişe ilişkin **gözlenebilir risk** niteliğindedir, en kötü dipten satış garantisi değildir. Haber sütunu yalnız tarihli bağlamdır, sonradan okunduğu için karar motorunu beslemez. Bazı Reuters/Kitco metinleri kaynak olarak gün içinde yayımlanmış, fakat orijinal ilk UTC dakika bağımsız arşivden tam doğrulanmamıştır.


### Kaynaklarda işlemsiz hafta sonları: haberler kaybolmamalı

Ana HistData altın kaynağında fiyat seansı olmaması, o gün önemli olay olmadığı anlamına **GELMEZ**. Aşağıdakiler yalnızca 2026 Ocak tarihli bağımsız Reuters ve Fed yayınlarından bulundu; projedeki önceden yazılmış 2026 olay manifesti okunmadı:

- **3 Ocak Cumartesi:** Venezuela'da ABD operasyonu ve Maduro'nun yakalanması; Reuters'ın 3 Ocak tarihli haberi. https://www.reuters.com/world/americas/shocked-venezuelans-hunker-down-unsure-what-comes-next-2026-01-03/
- **4 Ocak Pazar:** Bir sonraki açılış için Venezuela olayının güvenli liman ve petrol kanallarına etkisi gündemde; 4 Ocak tarihli piyasa katılımcısı Reuters derlemesi. https://www.investing.com/news/stock-market-news/market-analysts-react-to-trumps-venezuela-gambit-4428658
- **11 Ocak Pazar 19:30 EST:** Fed Başkanı Jerome Powell resmî açıklamayla kendisine gönderilen büyük jüri celplerini ve Fed bağımsızlığı üzerindeki baskıyı kamuoyuyla paylaştı. Bu bilgi **12 Ocak Pazartesi'den önce** biliniyordu; 12 Ocak haberlerinden geriye uydurulmadı. https://www.federalreserve.gov/newsevents/speech/powell20260111a.htm
- **17 Ocak Cumartesi:** Trump, Grönland konusunda sekiz Avrupa ülkesini ithalat tarifesiyle tehdit etti. https://www.reuters.com/world/europe/trump-vows-tariffs-eight-european-nations-over-greenland-2026-01-17/
- **18 Ocak Pazar:** Tarifelerin AB/ABD ilişkileri üzerindeki karşılıklı etkileri tartışıldı; ilk işlem tepkisi 19/20 Ocak tarihlerinde değerlendirilebilir. https://www.reuters.com/world/europe/world-markets-face-fresh-jolt-trump-vows-tariffs-europe-over-greenland-2026-01-18/
- **31 Ocak Cumartesi:** 30 Ocak Fed/Warsh ve metal likidasyon olaylarının bilgisi vardı, fakat yeni tam ana kaynak seansı yoktu. Bu gün için yeni yön kararı **yok**.

Tam tarih sıralı belge: `GOLD_JAN2026_WEEKEND_NEWS_CHRONOLOGY_20261013.csv`. Hafta sonu açıklamaları bir sonraki işlem günü başlangıcında erişilebilir olabilir, fakat kilitlenmiş fiyat kararına sonradan takdirî override eklenmedi.

## 3. İşlem kaydı ve sonucu
- 06 Ocak 17:00 NY kapanışı: AL kararı. Gerçekleşti varsayılan ilk SONRAKİ HistData M15 kotasyonu **07 Ocak 2026, 4,497.265 US$/ons**. Sermayenin %0.8'i alım komisyonu.
- 07–29 Ocak: TUT altın. Günlük trend sinyali güçlü olduğu için satış kararı veremedi.
- 28 Ocak kapanışında 1 birim başlangıç sermayesi portföyün değeri **1.194339** (alım maliyeti dahil, satış maliyeti hariç). Dönemin zirvesi.
- 29 Ocak kapanışı **5,378.815**; önceki 28 Ocak kapanışına göre yalnız **−0.660%**. Buna rağmen NY17 seansı içinde intraday high **5,596.805**, low **5,098.765**, kronolojik high→sonraki low **−8.899%**; en kötü dip 29 Ocak **15:15 UTC**, yani NY **10:15 EST** bar başlangıcı civarında. Çok büyük düşüş **30 Ocak gelmeden önce** gözlemlenebilirdi. Kilitli günlük kapanış-kuralı bu olayı **TUT** işledi; hata izlenebilir.
- 30 Ocak kapanışı **4,891.195**, bir önceki güne **−9.065%**. 30 Ocak sonunda SAT kararı çıktı. Ancak SAT **OCAK içinde icra edilmedi**, bir sonraki işlem fiyatı Şubat'a kalır; sonrasında ne olacağını Ocak performansına karıştırma.
- 31 Ocak itibarıyla altın portföyü açık ve **1.078892** birim (alış komisyonu düşmüş, varsayımsal açık pozisyon mark-to-mid); yani **+%7.889**. 30 Ocak kapanışında aynı fiyattan satılabildiğini sadece **varsayarsak** ek %0.8 ücret sonrası **+%7.026**; bu gerçek uygulanabilir satış değil, farkı gösterme amaçlı.
- Adil olmayan fakat kıyas için düz Jan02 kapanışından Jan30 kapanışına altın fiyat değişimi **+%12.920**; aynı fiyat noktalarında %0.8 alım ve %0.8 varsayımsal satışla **+%11.120**. Stratejinin pahalı maliyetli alternatiften düşük kalmasının nedenleri geç AL, geç SAT.
- 28 Ocak zirvesinden 30 Ocak sonuna açık portföydeki zirveye göre kapanış bazlı düşüş **−%9.666**. Gün içindeki düşüşler daha da büyük.
- 19 Ocak 82 bar, 19:15 UTC son bar (NY 14:30 EST'de bitiyor); 17NY tam seans kapanışı yoktu. Bu gün erken işlem kapanışı olarak işlendi; piyasa açılışı normal sanılmamalı.

## 4. Hangi mekanizmalar gerçekte incelendi?
- **05–09 Ocak:** Venezuela şoku + Fed faiz indirim beklentisi, 09 Ocak ABD istihdam 50 bin / zayıf; altın/diğer metallerde risk primi.
- **12–16 Ocak:** Powell'ın soruşturulması kaygısı, Fed bağımsızlığı, İran jeopolitiği, 13 Ocak TÜFE ve CME teminat rejimi; altın yükselişi ve gümüşte zaman zaman kar realizasyonu.
- **19–23 Ocak:** Grönland ve ticaret tarifeleri, ABD hisselerindeki riskten kaçış ve 21/22 Ocak kısmi uzlaşma; buna rağmen altın yükseldi. Bu, düz 'risk-on haberi altın satar' anlatısının tek başına çalışmadığına örnek.
- **26–28 Ocak:** Dolar zayıflığı, jeopolitik çekince, teknik/metallerde hızlanma; Fed'in beklenen faizi sabit tutma kararı altın patlamasının tamamını açıklamıyor.
- **29 Ocak:** büyük gün içi altın tepe→dip likidite şoku (−8.90%) ve kâr realizasyonu kaynağı; altının kapanıştan görünen -0.66%'si tehlikeyi sakladı.
- **30 Ocak:** Warsh'ın Fed başkan adayı olarak açıklanması, dolar yeniden fiyatlaması, yoğun altın/gümüş satışları; Reuters/Kitco **o gün** yayımlandı, önceki güne geri taşınamaz. Warsh haberi 29 Ocak riskinin as-of nedenini açıklayamaz.
- Aynı takvimde gümüş/platin/paladyum/Nasdaq/SP500/dolar/faiz değerleri geçmiş günle sınırlı gösterildi ama `available_as_of` Eylül/Ağustos 2026 olduğundan bunların orijinal fiyat bülteninin o gün yayımlandığı iddia edilmedi. Nedenselliği kanıtlamak için gerçek ilk yayın/haber UTC saatleri ve konum/ETF/CFTC pozisyonları gerekir.

## 5. Başka yıllarla kritik yanlışlama
2023–25 EV 15m altın aynı tepe→sonraki dip kuralında:
- Gün içi geri çekilmesi en az %3 olan **21 gün**; %4 olan 7 gün; %5 olan **3 gün**.
- Bu 21 günün **hiçbirinin hemen bir sonraki NY17 seans kapanışı** en az %3 düşmedi.
- Dolayısıyla 29 Ocak 2026'daki %8.9 'ön risk' kaydı, sonraki gün büyük satışın gerçekten yaşandığı ilginç **tek vaka** olsa da, sonradan belirlediğimiz tepe→dip eşiğinin başka yıllarda **güvenilir bir sonraki gün satış alarmı** olmadığı ayrıca saptandı.
- Örneklem küçük ve rejim farklı; test yönü posthoc seçildi. 'Biz artık düşüşü yakalayabiliyoruz' diye sunmak bilimsel olarak hatalıdır.

## 6. Kaynak ve politika kayıtları
- `GOLD_JAN2026_ASOF_DAILY_DECISION_PROTOCOL_LOCKED_20261013.md`: 2026-01 fiyat sonuçları görülmeden GitHub'a commit edilmiş sözleşme.
- `GOLD_JAN2026_ALL_31_DAYS_LOCKED_DECISIONS_PRE_OUTCOME_20261013.csv`: 31 karar ve as-of fiyat features, herhangi bir sonradan haberle değiştirilmedi.
- `GOLD_JAN2026_CONTEMPORANEOUS_NEWS_BY_DATE_20261013.csv`: 19 tarihli özgün Reuters/Kitco haber kaydı; nedeni kanıtlamaz.
- `GOLD_JAN2026_ALL_31_DAYS_METALS_RISK_LAGGED_CONTEXT_20261013.csv`: önceki tarihlere ait Ag/Pt/Pd/NQ/S&P/10Y/USD değişimleri, tamamı PIT olarak **doğrulanmamış**.
- `GOLD_JAN2026_INTRADAY_RISK_31DAY_FACTS_POSTHOC_20261013.csv`: 15dk yüksek/düşük dizisinin kronolojik olay analizi.
- `GOLD_JAN2026_PRICE_SOURCE_COVERAGE_20261013.json`: Jan 18 ortak tam seans iki farklı sağlayıcının aynı gün kapanışı farkı ort. mutlak **%0.0218**, max **%0.0908**. Jan01 DUK'ta tam-ish quote olmasına rağmen HIST yok, başka günlerde de boşluklar var; sağlayıcı ikamesi/gerçek işlem varsayımı yapma.
- `GOLD_JAN2026_LOCKED_REPLAY_POSTHOC_PERFORMANCE_20261013.json`: gecikmeli emir ve net maliyet ayrımı, 31 Ocak itibarıyla açık pozisyon.
- `GOLD_JAN2026_INTRADAY_SHOCK_2023_2025_FALSIFICATION_20261013.json`: önceden ayrı kronolojik altın seanslarında intraday drawdown eşik yanlışlama.

## Bilimsel karar
Kilitli fiyat kuralı, Ocak 2026 hızlı yükselişine 7 Ocak'tan katıldı; 29 Ocak gün içi şoku ve 30 Ocak likidasyonunu **erken SAT ile öngöremedi**. Bu olaylar 2026 olay manifesti okunmadan, yalnız 2026 ham fiyat ve bağımsız tarihli haberlerle bulunmuştur. 2026 tek ayından güvenilir model çıkmaz. Geliştirilecek sonraki hipotez, tek başına 'kapanış trendi' yerine **anlık altın→gümüş senkron düşüşü + intraday geçici likidite kaybı + saat damgalı bir haber yön/değişim şoku** örüntüsünü ve bu kombinasyon olmadığında sert satış yaşanmayan günleri incelemeli. Bunu aynı Ocak'ta optimize edip skor vermek geçersiz; geçmiş ve ileriki ayrı dönemlerde kilitlenmiş test gerekir.

**No future-as-of claims, no actual bank fills, no use of 2026 event manifest or previously written 2026 shock narrative files.**
