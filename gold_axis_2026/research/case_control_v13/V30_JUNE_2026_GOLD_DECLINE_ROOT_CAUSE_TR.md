# V30 — 4–11 Haziran 2026 altın düşüşü: neden BASE14/CFTC21/V22 önceden yakalayamadı?

**Araştırma tarihi:** 27 Ekim 2026  
**Durum:** Kaynağa dayalı geriye dönük kök-neden denetimi; tahmin modeli, eşikler, alarm kodu, Neon ve ham fiyatlar değiştirilmedi. İlk yayın bütün sayısal fiyat/makro vintageleri sertifikalı değil. Nedensel sonuçlar piyasa haberlerinin açıklamasıyla tutarlı *hipotez*; ekonometrik/karşıolgusal nedensellik ispatı değil.

## 1. Kesin saptamalar

V24 sabit olay defterine göre **4 Haziran 2026 zirve fiyatı 4474.68**, **11 Haziran 2026 dip 4113.23 USD/ons**, **-%8.077673** (mevcut retrospektif StakTrakr günlük araştırma takvimi). Reuters'in bazı intraday/futures fiyatlarıyla birebir aynı tanım/saat değil. İlk aşağı kapanış 5 Haziran, ikinci dalga 10 Haziran.

- Zirveden önceki **son 10 işlem gününde** V22 `ACTIVE_REVIEW` ya da `FRAGILITY_WATCH` **0 gün**. Eski raporda Haziran'a bağlanan Nisan 17 uyarısı **35 fiyat oturumu** uzaklıkta, uygun lead uyarısı değil.
- Ama **zayıf uyarılar tümüyle sıfır DEĞİLDİ**: BASE14 21, 22 ve 28 Mayıs'ta `YELLOW`; orijinal `RED` değil. V22'de YELLOW yalnız hemen önceki güçlü RED'in bir gün devamını oluşturabildiği için bu üç YELLOW öncelikli uyarıya dönüşmedi. Başarısızlık tam olarak **risk seviyesinin ve öncelik filtresinin düşük kalmasıdır**, verinin hiç olmadığı Mart 2026 durumu değil.
- 4 Haziran BASE14 skoru `0.471381`, RED eşiği `0.524746`; CFTC21 `0.446291`, RED eşiği `0.520981`. Her ikisi **NORMAL**. 4 Haziran `AU_ret20=-%5.3` (20 işlem günlük log değişim), `RSI14=0.402`, `GVZ=23.87`, `GVZ_z252=-0.089`, `US nominal 10Y (lagged)=4.49%`. Ocak ve Ağustos'taki yüksek fiyat momentumu / sıra dışı aşırı ısınmadan farklı.
- 5 Haziran fiyat örneklemi `4403.77`, model BASE14 `RED` (skor `0.560899`), CFTC21 `YELLOW` (`0.514082`), V22 `ACTIVE_REVIEW`; GVZ `28.89` ve `GVZ_z252=+0.615`. **Hareket başladıktan sonra** uyarı; zirve öncesi değil.
- 8 Haziran BASE14/CFTC21 ikisi RED olsa da V22 `ORIGINAL_RED_REVIEW_ONLY` çünkü P1–P7 yolu yok; 9–10 Haziran V22 `ACTIVE_REVIEW`, ancak düşüş zaten başlamış.
- 4 Haziran `GC_net=0.2757` (CFTC raporuna göre gecikmeli), 9 Haziran `0.3443`; değişim ilk düşüşten sonra gözlemlendi. Bu, piyasanın 5 Haziran öncesi durumunu 9 Haziran CFTC raporuyla önceden bilmemiz anlamına gelmez.

Ayrıntılı satırlar: `outputs/v30_june2026_daily_feature_and_risk_audit_COMMITTED.csv` (20 Mayıs–26 Haziran **28 gün**, model eşikleri, fiyat, momentum, GVZ, USD, ABD 10Y, CFTC, V22 sebep).

## 2. 5 Haziran'ın asıl şoku: beklentiden güçlü istihdam ve Fed politika yeniden fiyatlaması

- BLS, 5 Haziran 2026 saat **08:30 EDT (15:30 Türkiye saati)** Mayıs istihdam verisini **+172,000** açıkladı. Reuters'ın aynı gün öncesi anket beklentisi yaklaşık **+85,000**: ilk açıklanan veriye göre **+87,000 kişi sürpriz**. +4.3% işsizlik oranı. BLS ilk yayın: https://www.bls.gov/news.release/archives/empsit_06052026.htm; Reuters: https://www.reuters.com/world/india/gold-slips-set-weekly-loss-mideast-tensions-rate-hike-fears-2026-06-05/
- Reuters 5 Haziran: dolar ve ABD tahvil getirileri artarken Fed'in yıl içinde **faiz artırabileceği** beklentisi güçlendi; Irak/İran/Middle East savaşının petrol ve enflasyon baskısı altının güvenli liman niteliğini bu defa bastırıyordu. 5 Haziran haberinde Aralık faiz artışı ihtimali ~%50'den **%72**'ye çıktı (piyasa algısı, birebir tarihli anlık fiyat). Aynı gün gümüş, platin, paladyum da sert düştü: **metaller arası ortak şok**, yalnız altın pozisyon çözülmesi değil.
- **2 Haziran JOLTS** (BLS resmî ilk yayın): açık iş sayısı 7.6 milyon, +731k artış; Reuters beklentisi ~6.88 milyon, ilk değer ~7.62 milyon. İlk yayımlanma 2 Haziran **10:00 EDT**: https://www.bls.gov/news.release/archives/jolts_06022026.htm ve https://www.investing.com/news/economy-news/us-job-openings-jump-to-near-twoyear-high-in-april-4722392
- **3 Haziran ADP** özel istihdam +122k, Reuters ekonomist beklentisi +117k (**+5k sürpriz, küçük**), 08:15 EDT civarı; ilk yayın: https://mediacenter.adp.com/2026-06-03-ADP-National-Employment-Report-Private-Sector-Employment-Increased-by-122%2C000-Jobs-in-May-Annual-Pay-was-Up-4-4 ; Reuters https://www.investing.com/news/economy-news/us-private-payrolls-increase-in-may-adp-says-4724242 . JOLTS daha belirgin ilk sinyal; ADP, NFP sürprizinin kesin ya da büyük olacağını göstermez.

## 3. 9–11 Haziran devamı: neden yeni bir düşüş geldi?

- 9–10 Haziran dolara ve petrole destek veren ABD–İran çatışma tırmanışı, faiz/enflasyon korkuları ve pozisyon azaltma devam etti. Reuters 10 Haziran erken haber: https://www.marketscreener.com/news/gold-drops-as-oil-and-dollar-rise-on-renewed-us-iran-hostilities-ce7f5cdade88f526
- 10 Haziran **Mayıs CPI** BLS ilk yayın: `+0.5%` aylık ve `+4.2%` yıllık, 08:30 EDT. **İkisi de konsensüsle AYNI**, çekirdek +0.2% aylık (konsensüs +0.3%, nispeten daha ılımlı). Bu nedenle **10 Haziran düşüşünün nedeni "beklenmedik CPI sürprizi" değildir.** Beklentiler dahilinde yüksek yıllık manşet enflasyon/fed faiz riskinin sürmesi ile gün öncesi fiyat baskısı ayrılmalıdır. Kaynak: https://www.bls.gov/news.release/archives/cpi_06102026.htm ; https://www.cmegroup.com/education/events/econoday/666990 ; Reuters https://www.reuters.com/business/view-cpi-rises-fastest-rate-three-years-meets-market-expectations-2026-06-10/
- World Gold Council, Ağustos 2026 tarihli Q2 2026 ETF analizinde **Martı ağırlıkla zorunlu risk azaltma/pozisyon çözülmesi**, **Haziranı faizlerin, reel getirilerin, doların temel yeniden fiyatlanması** olarak açıkça ayırıyor: https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-us-focus-q2-2026
- Pozisyon ve ETF çıkışları satışları **kuvvetlendirmiş olabilir**. Ancak altının 5 Haziran hareketinin ne kadarının her nedenden geldiği mevcut verilerle yüzde olarak bölüştürülemez.

## 4. MODEL MEKANİZMASI: neden piyasa bilgisini işlemeye başlamadı?

**A. Daha önceki bazı düşüşlerin ayırt edici aşırı ısınma kalıbı yoktu.** 4 Haziran RSI `0.402`, AU_ret20 `-5.3%`, GVZ `23.87`; BASE14 ve CFTC21 anomali skorları kırmızı eşiklerinin belirgin altında. V21 NORMAL/WATCH `RSI>=0.74 and AU_ret20 in +4–6%` koşulu başarısız.

**B. Orijinal 14/21 model aileleri NFP'yi, ADP'yi, JOLTS sürprizini ve *beklentiden sapmayı* girdi olarak hiç kullanmıyor.** Gösterge listesi AU trend / oynaklık, metaller arası dağılım, GVZ, USD (H10 **~10 takvim günü gözlem-gecikmesi**), nominal 10Y (H15 günlük gecikme), 7 CFTC özellik; 2Y/10Y reel faiz, FedWatch fiyatlama, petrol, yayınlanacak olay takvimi, ADP/JOLTS/NFP/CPI konsensüsü ve ETF akımı yok.

**C. Çok değişkenli anomali modeli olay sürprizi tahmincisi değildir.** 200 ağaçlık IsolationForest geçmiş *gözlenmiş* şartların sıra dışılığını sınıflıyor. Beklenmedik +87k NFP açıklaması daha önce bilinemez; önceden yalnız takvim ve öncül göstergeler bilinebilir. 5 Haziran GVZ sıçraması ancak piyasa tepki verdikten sonra 2026 modeline girmiştir.

**D. V22 mantığı kriz oluştuğunda iyi ama "şok öncesi" yüzdesel momentum koşuluna bağımlı.** V22 P1 pozitif altın momentumunda hızlanma, P3 aynı gün düşüş+GVZ, P6 güçlü RED'in YELLOW'a bir günlük geçişi, P7 aşırı RSI/pozitif 20 günlük ralli -> öncesindeki hafif zayıflığı otomatik risk uyarısına dönüştürmüyor. 21/22/28 Mayıs YELLOW değerlerini şimdi kırmızı sayarsak geriye dönük kolay ama yanlış alarm oranı gözardı edilmiş olur.

**E. Zaman uyumu önemli.** 5 Haziran ABD NFP **15:30 TR** saatinde yayımlandı; kullanıcı açısından 17:00 işlem erişim süresinden önceydi. Fakat bugünkü modelin 5 Haziran GVZ ve ABD seans-sonu/günlük girdi bileşenleri **15:30 TR'de hepsi yayımlanmış değil**. Dolayısıyla o günün kapanış temelli `RED` sonucunu "15:30'da alınabilir uyarıydı" diye iddia etmeyin. Gereken ayrı bir **yayın-saati uyumlu hızlı haber/ekonomi katmanı**.

## 5. Denetlenebilir, geriye dönük aşırı uyum üretmeyen yol

1. Orijinal BASE14/CFTC21/V22 parametrelerine ve geçmiş orijinal alarmlara dokunma.
2. Önceden bilinen resmî `NFP/CPI/FOMC` yayın saatlerini ayrı `EVENT_PENDING` (takvim risk uyarısı, SAT sinyali değil) olarak işaretle; JOLTS ve ADP ilk yayımlanan gerçek/consensus farklarını `EVENT_PRIOR_CONTEXT` içinde tut.
3. Açıklama geldiğinde ilk-baskı gerçekleşen - yayın öncesi konsensüs farkı, 2Y/10Y **yayın-sonrası** getiriler, DXY, petrol, altın/gümüş kısa fiyat hareketi ve konvansiyonel "en son gözlenen" girdi timestamp'iyle ayrı `EVENT_REPRICING` durumu hesapla. Olayın kesin yönünü önceden bilemez; ancak piyasa şokunu 15:30–17:00 TR penceresinde izleme imkanı modelden ayrı doğrulanabilir.
4. Yalnız olay saatinden **ÖNCE** yayımlanan faktörlerle 2010–2025 tarihsel walk-forward / orijin vintage karşılaştırması, **tüm haber günleri ve açıklamasız kontrol günleri** dahil; yalnız 5 Haziran üzerine optimizasyon yasak. 2026 bu keşiften sonra kör test olarak gösterilemez.
5. İlk fiyat yayımlanma tanımı (LBMA fixing vs spot) ve CFTC/H10/H15/GVZ ilk sayı vintageleri onaylanmadan `PIT_CERTIFIED` veya canlı bir AL/SAT sistemi ilan etme.

## Kontrollü sonuç

**Haziran kaçırılması bir fiyat-hatası karantinasından kaynaklanmıyor.** Model 4 Haziran'da çalışıyordu, ama **faiz artışı beklentisi ve sürpriz işgücü verisiyle öne çıkan makro veri-takvimi şokunu temsil edecek girdileri yoktu**. 5 Haziran hemen sonrasında reaksiyon gösterdi. Bu, yüksek güvenle bir **girdi kapsamı ve karar frekansı** eksiği olarak tanımlanabilir; sürpriz NFP'yi önceden kesin bilmek mümkündü iddiası değildir. Haziran 2026'nın makro nedeni, enerji kaynaklı enflasyon beklentileri ile Fed faiz yeniden fiyatlaması; 10 Haziran'ın gerçek CPI değerleri beklentiyle aynı olduğundan "CPI beklenenden yüksek" anlatısı hatalı. Mart 2026 daha fazla tasfiye/likidite ağırlıklıydı (WGC).

**Ayrı yeni alarm başlatılmadı; kod, veri, parametreler ve üretim orijinal kaldı.**
