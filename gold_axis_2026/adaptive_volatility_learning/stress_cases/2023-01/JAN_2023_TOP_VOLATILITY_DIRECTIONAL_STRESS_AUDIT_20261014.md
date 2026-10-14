# Ocak 2023 — En yüksek oynaklık günleri: 5 Ocak DOWN, 6 Ocak UP, 15dk×2 gün stres testi
**Çalıştırıldı 2026-10-14** · **İki ayırt edici tarih**: 2023-01-05 en kuvvetli DOWN, 2023-01-06 en yüksek volatilite ve en büyük UP. **Ana rejim:** `STRESS_DAYS_CHOSEN_USING_EX_POST_PRICE_RANGE`; gün içi replay `AS_OF_RECORDED_PRICE_AND_SCHEDULED_RELEASE` ama GPT politikası/kontratlar 2026'da bilinen sonuçlardan etkilenmiş olabilir; OOS veya canlı gerçek işlem değil.

## 1. Ayın zor günlerini seçmenin SAYISAL KURALI
En yüksek tarihsel ASK ile en düşük tarihsel BID arasındaki fark / günün ilk MID'i; ve günün ilk–son MID değişimi ayrı. **Range tüm günü gördükten sonra yalnız zor örnek seçer, emir sinyalinde KULLANILMAZ.** BID/ASK farkı range içine dahildir. Türkiye 00:00–24:00 günleri, Pazar/tatil ve kısmi günler dışarıda tutuldu. Tüm ayın [ranking CSV](JAN_2023_VOLATILITY_RANKING_20261014.csv).

| Rang | Gün (TRT) | Fiyat aralığı | İlk–son MID |
|---|---|---:|---:|
| 1 | 2023-01-06 | 2.187% | +1.834% |
| 2 | 2023-01-05 | 1.842% | -1.257% |
| 3 | 2023-01-19 | 1.814% | +1.585% |
| 4 | 2023-01-31 | 1.594% | +0.284% |
| 5 | 2023-01-04 | 1.594% | +0.915% |
| 6 | 2023-01-26 | 1.587% | -0.812% |
| 7 | 2023-01-13 | 1.569% | +1.136% |
| 8 | 2023-01-18 | 1.554% | -0.254% |
| 9 | 2023-01-12 | 1.551% | +1.162% |
**Birincil stres çifti:** 5 Ocak DOWN (**%1.842**; ilk–son **-1.257%**) ve hemen ertesi gün 6 Ocak UP (**%2.187**; net **+1.834%**). Bu iki gün ardışık olduğu için yeni 4 Ocak denemesinin GOLD pozisyonu **doğrudan** devredilebilir; arada incelenmemiş gün kalmaz. Diğer adaylar 19 Ocak UP, 26 Ocak DOWN, 31 Ocak iki-yönlü/kapanış yanıltıcı volatilite olup bu **iki günlük testte çalışılmadı**.

## 2. Devreden portföy ve maliyetler
4 Ocak 10:21 TRT tarihsel tepkiden kurulmuş GPT+minute AL vekili **ASK 1851.34994**, %0.8 AL ücreti, **0.0535825226 oz GOLD**. 4 Ocak BID-mark 99.230545 USD (realize edilmemiş, erken çıkılırsa bir %0.8 de SAT kesilecek). Bankanın tarihsel kotasyonları henüz yok.

## 3. Olay -> veri -> 1 dakika teyit -> maliyetli karar
M1 tetik koşulu yalnız **haberden sonra**: haber anından önceki son tamamlanan M1 MID'e göre **DOWN -%0.4**, **UP +%0.4** hareketin en az **5 ardışık tamamlanmış M1 bar** ile korunması. Bu araştırma için olay teyit *açıklayıcı gate*; **BUY/SELL otomatik kuralı değildir**. Tetikten sonraki gerçek banka fiyatı yok; fiyat vekili sadece *bir sonraki M1 MID* ± önceki kapanmış M15 makasının yarısı. "En ideal dakika" seçilmez, sonraki fiyat/olay karar nedeni değildir.

| Haber | İlk yayımlanma (UTC) | Yön adayı | 5 ardışık M1 teyidinin ilk anı | Sonraki dakika yaklaşık fiyat | 2 saat sonra fiyat farkı, yalnız EX POST |
|---|---|---|---|---|---|
| ADP | 2023-01-05 13:15 UTC | DOWN | 13:58 UTC | 1834.38 BID / 1834.75 ASK vekili | -0.702% |
| CLAIMS | 2023-01-05 13:30 UTC | DOWN | 13:58 UTC | 1834.38 BID / 1834.75 ASK vekili | -0.833% |
| NFP | 2023-01-06 13:30 UTC | UP | 13:48 UTC | 1849.12 BID / 1849.48 ASK vekili | 1.185% |
| ISM_SERVICES | 2023-01-06 15:00 UTC | UP | 15:07 UTC | 1857.37 BID / 1858.00 ASK vekili | 1.071% |

### 5 Ocak: DOWN stres
- Sabah: [4 Ocak FOMC tutanakları](https://www.federalreserve.gov/monetarypolicy/fomcminutes20221214.htm) bir gece önce biliniyordu, 5 Ocak 13:15Z ADP sonucu **henüz bilinmiyordu**; spekülatif SAT yasak.
- **16:15 TRT (13:15Z):** [ADP](https://mediacenter.adp.com/2023-01-05-ADP-National-Employment-Report-Private-Sector-Employment-Increased-by-235%2C000-Jobs-in-December-Annual-Pay-was-Up-7-3) Aralık özel istihdam **235 bin**; Reuters anket beklentisi **150 bin** ([Reuters USD haberi](https://za.investing.com/news/hawkish-fed-rhetoric-fails-to-lift-dollar-aussie-jumps-2675093)); dolar/faiz şahin kanalı DOWN riskini artırdı.
- **16:30 TRT (13:30Z):** [ABD ilk işsizlik başvuruları](https://www.dol.gov/newsroom/releases?agency=All&page=9&state=All&topic=132&year=all) **204 bin** (önceki revize 223 bin), istihdam dirençli ve Fed sıkı kalabilir. Geçmişte Fed/işgücü sıkılığıyla altına baskı arasında ilişki gözlemlendi; **bu haber çıkmadan ona bağlı işlem yazmadık**.
- **16:58 TRT (13:58Z):** Gerçek XAU M1 bazlı ilk DOWN teyidi: her biri ADP öncesi MID'den **-%0.4** altında kalan beş 1m. Ancak düşüşün ciddi kısmı **zaten yaşanmış** ve önümüzdeki NFP ertesi güne saklı, geriye kalan sürekli DOWN'un %1.62 komisyon+spread üzerinde olacağına dayalı sayısal kanıt yok. **Karar: SATMA, GOLD koru**. Olabilecek satışın 16:59 TRT BID vekili **1834.38 USD**. Bir sonraki gün NFP ne olacağını **5 Ocak'ta bilmiyoruz.**
- [Reuters altın günü](https://www.marketscreener.com/news/latest/Gold-slips-as-caution-sets-in-before-key-U-S-jobs-data-42662891/) fiyatın düşüşünü ve NFP öncesi kar realizasyonunu anlatıyor; haberin sonradan güncellenmiş fiyat paragrafı, sabah emrinin nedeni değildir. [S&P final hizmet PMI](https://forex.tradingcharts.com/economic_calendar/2023-01-05.html?code=USD) 44.7 = büyüme zayıflığı, ADP şahinliğiyle karşıt.
- **23:45 TRT** fiyat BID **1833.87**, GOLD BID-mark **98.2634 USD**. Satış yok. Karşıt DOWN teyidi güçlü ama **maliyetli golddan-nakde geçiş fırsatı teyidi değil**.

### 6 Ocak: UP stres
- **16:30 TRT (13:30Z)** [BLS NFP](https://www.bls.gov/news.release/archives/empsit_01062023.htm): **223 bin** net iş, işsizlik **%3.5** (güçlü), fakat saatlik ücret artışı **%0.3** (beklenti %0.4); tek yönde olumlu/olumsuz dememek gerekir. Büyüme korundu ama ücret baskısının hafiflemesi Fed faiz politikasının gevşeyebileceği hipotezini güçlendirdi. 2022 Kasım daha serin CPI→USD/faiz gerilemesi örneği **benzer nedensel kanal, aynı şok değil**. <BLS firstprint> 13:30Z itibarıyla geçerli; 15:00 ISM henüz yok.
- **16:48 TRT (13:48Z)** +%0.4 üstü M1 beş kapanış teyidi var, ara artış sonrası geriye çekilme olabiliyor. İşlemci zaten GOLD; ikinci AL yok, pozisyon korunur.
- **18:00 TRT (15:00Z)** [ISM hizmet PMI](https://www.prnewswire.com/news-releases/services-pmi-at-49-6-december-2022-services-ism-report-on-business-301715010.html) **49.6** vs önceki **56.5**, ilk daralma 2020'den beri. Faiz beklentisi, USD, ZN fiyatı ve NQ risk iştahı aktarım kanallarını birlikte izliyoruz; aynı zamanlı DXY/US2y serisi **eksik**. Daha güçlü UP şoku asıl bu haber sonrasında görüldü, **NFP anında bilinmez**.
- **18:07 TRT (15:07Z)** ISM sonrası beş ardışık M1 ile ilk +%0.4 kalıcı yükseliş teyidi. GOLD→GOLD pozisyon; yeni giriş maliyeti yok. Duyulan fiyatlar [6 Ocak Reuters altın gözlemi](https://theprint.in/business/gold-jumps-as-u-s-jobs-data-suggests-less-hawkish-fed-path/1302106/) ile uyumlu, haberin kendi yayımlanma saati kadar ilk yayımda farklı gözlem olabileceği ihtiyatla saklanır.
- **23:45 TRT** BID 1867.65 → altın miktarı değişmeden **100.0734 USD BID-mark**. Şimdi nakde dönülse ek %0.8 SAT komisyonu sonrası **99.2728 USD**. Fiilen SAT yapılmadı.

## 4. En zor test: yanlış DOWN SAT ve ertesi gün geri AL alternatifleri
Kullanıcı maliyeti **alırken %0.8, satarken %0.8**, spot vendor BID/ASK ayrıca. Aşağıdaki **karşıt olasılıklar ex-post sonuç kıyasıdır, sistem tarafından gerçekleştirilmedi**. Süreklilik: 4 Ocak devreden GOLD 0.0535825226 oz, 5 Ocak 13:58Z açıklanmış veri sonrası DOWN ilk M1 teyidi; en erken sonraki 1m yaklaşık BID'den satış, 6 Ocak ilk UP teyitlerinden biri sonrasında en erken sonraki 1m yaklaşık ASK'den geri alım.

| Karar çizgisi | 6 Ocak 23:45 teorik GOLD BID-mark NAV | Aradaki ilave işlemler | Altında kalmaya göre USD |
|---|---:|---|---:|
| **Olay yorumuna göre GOLD'u hiç satmadan koru** | **100.0734** | **YOK** | Referans |
| DOWN sonrası SAT, NFP UP sonrası AL | 97.6749 | 1 SAT + 1 AL | -2.3985 |
| DOWN sonrası SAT, ISM UP sonrası AL | 97.2267 | 1 SAT + 1 AL | -2.8467 |

**Net maliyet dersi:** 5 Ocak fiyatı en yüksekten en düşüğe %1.84 aralık yapmış olsa da **duyurudan sonra teyit edilmiş DOWN hareketini satmak** ve 6 Ocak toparlanmasını gördükten sonra altına geri dönmek, bu örnekte komisyonla erozyon yaratır. Ancak bu **her büyük DOWN'da SATMA** diye evrensel kuralı ispatlamaz. 2026 Ocak V4'ün 2024 retrospektifte 12 önemli DOWN olayından sıfırını yakalaması, güvenli göründüğü için aşırı HOLD etmenin de gerçek risk olduğunu hatırlatır. Daha güçlü DOWN olaylarında alternatif SAT'ların gerekliliği ayrıca sınanmalıdır.

## 5. Veri ve araştırma sınırları
- **Gün seçimi sonradan**: iki gün tüm Ocak en uç fiyat aralıklarına bakılarak seçildi, NFP/ADP oynaklığı önceden biliniyormuş gibi pozisyon kurulamaz. Bu **challenge/diagnostic** setidir, kör/OOS değil. M15 tüm gün **92 bar**, Türkiye günü 96×15 kontrol noktasından 91'ine 23:45'e kadar tamamlanmış bar vardır; 1 kontrol 00:00'da yeni kapanış yok, 4 kontrol 22:00 civarında veri molası taşıyabilir.
- **6 Ocak 1m kapsama** 1319 bar, **121 dakika eksik** (çoğu gün sonu 20:00–21:00 UTC aralığı ve günlük rollover); bu saatlerde hayali dakikalık takip YOK, yeni 15m çubuğu varsa **M15 yedek**. 5 Ocak 1380 M1 (60 eksik, olağan rollover). M1 fiyat `MID` vekili; 15m kaynağı ayrı BID/ASK, 1m gerçek banka kotasyonu değil.
- **ZN 10Y Treasury futures fiyatını**, doğrudan getiri seviyesi sanmayız. GC/SI 1H çok düşük hacimli, aşırı teyit sayılmaz; DXY/US2Y tam eş-saatli bu testte yok; küresel veri bağları bazı yerlerde hipotez düzeyinde.
- **As-of konuşlandırma:** planlı ABD haberleri ancak ilk saatinde bilinir; koşulların önceden görüldüğü iddia edilmez. Karar kuralı tek fiyat eşiği değil; olay nedeni + karşıt kanıt + kalan hareket olasılığı + maliyet + M1 teyittir. Bunun gerçek ileri başarıya dönüştüğü gösterilmedi.
- **Doğrulama sınırı:** 4 Ocak M1 teorik alış zaten ex-post GPT ile belirlenmişti; bu iki günü seçmek de ex-post. $100 başlangıçtan bu varlık döngüsü kıyası 4–6 Ocak örnek zinciridir, Ocak 2023 tamamı değildir. **Oynaklık başarı metriği değildir; yanlış alarm ve kaçan büyük hareket de ölçülmeli.**

**Kanıt dosyaları:** [15m×192 kontrol](JAN05_JAN06_2023_192X15M_ASOF_EVENT_DECISION_LEDGER_20261014.csv) · [kural/olay/alternatif NAV JSON](JAN05_JAN06_2023_STRESS_RESULTS_AND_COUNTERFACTUAL_20261014.json) · [tüm ay volatilite tablosu](JAN_2023_VOLATILITY_RANKING_20261014.csv). Gizli Neon ham 15m ve 1m fiyat satırları kamusal GitHub'a aktarılmadı.
