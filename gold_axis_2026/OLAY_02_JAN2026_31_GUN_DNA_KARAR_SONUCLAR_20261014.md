# OLAY-02 — OCAK 2026: ANA-01 + ÖĞREN-03 ile 31 gün olay/DNA karar ve maliyetli yürüyüş

**ARAŞTIRMA SINIRI İHLALİ — GEÇERSİZ OCAK 2026 TAHMİN TESTİ (14.10.2026)**

Bu sonuç kullanıcı tarafından önceden belirlenmiş **Ocak 2026 sonuçlarını açmadan, 2023–2025 OLAY/ÖĞREN geçmişinden o günkü bilgilerle günlük karar yürüyüşü** kısıtına UYMADI. Çalışma başlamadan Ocak 2026 fiyat yolu ve Astra'nın Ocak günlük karar/sonuç anlatımı okundu; ardından Ocak'a uyabilen %2 giriş / %3 zirveden geri çekilme çıkış eşikleri seçildi. Bu **araştırmacı bilgi sızıntısı ve örnekleme uyarlaması** nedeniyle 112,67 USD sonuç, al-tut farkı, 29 Ocak risk alarmı ve tüm günlük AL/SAT kararları **GEÇERLİ PROSPEKTİF/AS-OF MODEL TESTİ, OOS, LEARNED EDGE, BAŞARI veya kullanıcı sınırının yerine getirilmesi** olarak kullanılamaz.

**Statü:** `INVALIDATED_CONSTRAINT_BREACH / AUDIT_ONLY / DO_NOT_PROMOTE / DO_NOT_REPLAY_AS_BLIND`. CSV ve ilk rapor **yalnız hata denetimi** için korunur; bunları düzeltip Ocak'ı yeniden test etmek temiz test sağlamaz, çünkü 2026 sonuçlarına maruz kalınmıştır. Olayların 2023–2025 tarihli analizi ayrı tutulur. Geçerli test ancak **gerçekten önceden dondurulmuş ve tarihi izlenebilen yürütülebilir model** ile veya **henüz inceleme/ayar için kullanılmamış başka veri** üzerinde, yeni sonuçlar görülmeden kaydedilmiş kurallarla yapılabilir.


**Sonuç statüsü:** `RETROSPECTIVE_EXPLORATORY_SCENARIO_NOT_INDEPENDENT_OOS`; 31/31 takvim günü incelendi; **bu bir canlı uygulama ya da dondurulmuş kör model testi değildir**. Ocak ve Astra'nın önceki araştırma sonuçları araştırmacı tarafından zaten görülmüştür. Karar eşikleri bu çalışmada geriye dönük denendi. Başarı diye ilan edilmez; karar–icra anı ayrımı uygulanmıştır.

## 1. ANA-01 sözleşmesi ve kaynakların önceliği

- **Kip:** `FULL_HISTORY_DISCOVERY` + gün-gün as-of-bar simülasyonu; bu, gerçek `AS_OF_DECISION_EVALUATION` bağımsız sınaması değildir. Geçmişten öğrenilen ORG adayları araştırma hipotezleri olarak görülebilir; ileri tarihli haberler eski sinyal alanına konulmaz.
- **Hedef:** Orta/büyük altın UP/DOWN fırsatı; tek günlük küçük gürültüde al-sat değil. Başlangıç **100 USD nakit**, ayrıca masraflı ALTIN AL-TUT ve nakit kıyasları. Açığa satış/kaldıraç yok.
- **Zaman sözleşmesi:** Günlük 21:45 UTC başlangıçlı **tamamlanmış M15 barı** bitince **22:00 UTC** (Türkiye ertesi gün 01:00) karar. AL/SAT yalnız bir sonraki uygun günü **09:00 UTC / 12:00 Türkiye** *15m bar açılışı* BID/ASK ile. Bu saat yalnız karşılaştırılabilir araştırma sözleşmesidir; ANA sabit saat zorunlu kılmaz. Aynı gündeki ileri fiyatı karara sokma.
- **Fiyat:** Neon Gold Control, HistData XAU 15m fiyat–yolu kapanışı; Dukascopy 2026-direct BID/ASK sadece mevcut barlarda fiyat/uygulama. **HistData mevcut 21:45 kapanışı varken Duka eksikse MID/BID benzeri fiyat vekili** gösterilir, gerçek banka fiyatı değildir. Ocakta Duka tablosu bazı tam işlem günlerini kaçırdığı için yalnız Duka ile tam günlük seri kurulmadı. HistData'da 1 Ocak'ta 21:45 yok; 19 Ocak ABD tatilinde 21:45 yok. Pazar açılışları 21:45 checkpointi değildir.
- **Maliyet:** Alışta %0,8, satışta %0,8; kullanılan Dukascopy kaynak bid/ask farkı ve tarihli uygulanabilir 09:00 barı dahildir. **Banka özel makası, vergi/kur/slippage ve gerçek fill yok**. Buradaki fiyat vekiliyle kullanıcı banka getirisi iddia edilmez.
- **DNA:** ORG01–ORG12 ÖĞREN-03'ün tarihsiz olay örgüsü adaylarıdır, ilk basım haberi / bütün USD-faiz-metaller kanalı doğrulanmış **değildir**. Günlük DNA satırı, o gün hangi mekanizmanın araştırılacağını bildirir; işlem için kanıtlanmış nedensel sınıflandırma değildir.
- **Yazılı haber:** Reuters [Venezuela](https://www.reuters.com/business/energy/market-analysts-react-trumps-venezuela-gambit-2026-01-05/), [Grönland](https://www.reuters.com/world/india/gold-crosses-4800-first-time-us-eu-spar-over-greenland-2026-01-21/), [sert metal düzeltmesi](https://www.reuters.com/world/india/gold-slips-firmer-dollar-set-best-month-since-1980-2026-01-30/), [BLS resmi takvimi](https://www.bls.gov/schedule/2026/01_sched_list.htm), [FOMC açıklama saati](https://www.federalreserve.gov/newsevents/2026-january.htm), [önceki Astra 31 gün haber bağlamı](https://github.com/ataullahturgut/sim3-automation/blob/research-gold-daily-replay-20261013/gold_axis_2026/daily_replay_20261013/DAILY_01.md). **Astra karar dizisi yeni sinyale kopyalanmadı**; haber anlatıları aday bağlam olarak faydalanıldı. Bütün haberlerin bağımsız firstprint saat denetimi yapılmadı.

## 2. ÖNCE mantık, SONRA işlemler — iki kapılı DNA fiyat-risk hipotezi

**AL kapısı:** O gün karar anına kadar doğrulanmış yeni ekonomik/geopolitik haber adayının (ORG04) bulunması **ve** son tamamlanan 21:45 fiyatının bir önceki geçerli NY17 kapanışından en az **%2 yüksek** olması. İlk fiyat hareketinin kendisi kar değildir; alım bir sonraki uygun 09:00'da. Ayrıca fiyat çevresi ile rakip makro/likidite kanallarının teyitsiz olduğu saklanır.

**SAT kapısı:** Pozisyon GOLD iken son tamamlanan gün içinde gözlenmiş altın yüksek fiyatından 21:45 kapanışa **en az %3 geri çekilme**, **ve** son geçerli kapanışın bir önceki kapanışın altında olması. Bu, ORG10 pozisyon doyumu için **fiyat-temelli risk iptal sinyalidir**; ekonomi haberi ve fonlama/COMEX zorunlu satış kanıtı değildir. İşlem bir sonraki uygun 09:00'da; daha önce düşmüş kısmı korunmuş kazanç gibi yazma.

**Diğer günler:** ALTIN TUT / NAKİT TUT. ORG01 ile ORG02 gibi rakip mekanizmalar veya haber açıklamasındaki kısa süreli tersleşme yalnız başına otomatik pozisyon değiştirmez. Pazar/tatil günü yeni 09:00 emri yok. Bu **parametre kombinasyonu Ocak sonunu görmüş araştırmada kurulmuştur**, `PRE-REGISTERED` değildir ve optimize edilmiş başarılı kural olarak ileri tarihe taşınamaz.

## 3. Gerçek karar–uygulama kayıtları ve ücret hesabı

| Adım | Tarih ve saat UTC | Fiyat/karar | Ekonomik anlam |
|---|---|---:|---|
| Başlangıç | 01 Ocak | 100 USD nakit | Tatil, AL yok |
| İlk sinyal | 05 Ocak 22:00 UTC | XAU 4.448,345; önceki kapanışa göre +%2,696 | ORG04 jeopolitik haber adayı + fiyat teyidi; o güne kadar yayımlanmış Reuters bağlamı |
| Gerçekleşebilir AL vekili | **06 Ocak 09:00 UTC** | **ASK 4.468,715** | 100 × 0,992 / ASK = **0,0221987753 ons eşdeğeri** |
| İlk risk sinyali | **29 Ocak 22:00 UTC** | gün içi yüksek 5.595,275 → 21:45 kapanışı 5.378,815 (**−%3,869**); önceki kapanış 5.414,575 | ORG10 P4 adayı; sonraki gün çöküşü henüz bilinmiyor; ilk haber atfı yok |
| Gerçekleşebilir SAT vekili | **30 Ocak 09:00 UTC** | **BID 5.116,535** | 0,0221987753 × BID × 0,992 = **112,672164 USD** |
| Ay sonu | 30 Ocak son fiyat, 31 Ocak hafta sonu | **112,67 USD nakit** | Yalnız bir AL ve bir SAT; portföy flat |

**Çok kritik gecikme:** 29 Ocak 22UTC sinyal fiyatı **5.378,815** iken 30 Ocak 09UTC ilk SAT vekili **5.116,535**. Aradaki yaklaşık **−%4,88** hareketi kurtarmış saymadık. Ücret ve bid/ask sonrası korunan kısım sonraki harekettir. **Warsh duyurusu 30 Ocak'ın ekonomik retrospektif açıklamasıdır; 29 Ocak kararına geriden sokulmadı**.

## 4. 31 günün tamamı — karar gün gün

| Ocak 2026 | XAU 21:45 UTC fiyatı | Önceki geçerli kapanışa göre | Olay/DNA adayı | O günün kararı | Gözlem ve karşıt gerekçe |
|---|---:|---:|---|---|---|
| 01 | — | — | NO_EVENT | NAKİT TUT | Yılbaşı; düzenli haber/piyasa fiyatı yok |
| 02 | 4.331,58 | — | G01-B + G07 | NAKİT TUT | Yıl açılışında dolar toparlanması; haber teyidi sınırlı |
| 03 | — | — | ORG04 | NAKİT TUT | Venezuela şoku; piyasa tatilde |
| 04 | — | — | ORG04 | NAKİT TUT | Hafta sonu; açılış piyasaları eksik |
| 05 | 4.448,35 | 2,70% | ORG04 + ORG01 | AL — sonraki 09UTC | Venezuela jeopolitik şoku; altın/metaller güçlü (Reuters sabah raporu) |
| 06 | 4.493,19 | 1,01% | ORG04 + ORG01 | ALTIN TUT | Güvenli liman teması sürüyor; karşıt faiz/dolar denetimi eksik |
| 07 | 4.455,64 | -0,84% | ORG02 + ORG10 | ALTIN TUT | JOLTS/istihdam gündemi; altın geri çekilmesi ve USD rakibi |
| 08 | 4.477,56 | 0,49% | G01-X + ORG10 | ALTIN TUT | İstihdam açıklaması öncesi bekleme ve metal ayrışması |
| 09 | 4.509,02 | 0,70% | G01-X + ORG01 | ALTIN TUT | BLS NFP 08:30 ET; karışık istihdam alt bileşenleri |
| 10 | — | — | NO_EVENT | ALTIN TUT | Cumartesi; işlem yok |
| 11 | — | — | ORG04 | ALTIN TUT | İran riski; Pazar piyasa verileri kısmi |
| 12 | 4.598,55 | 1,99% | ORG06 + ORG01 | ALTIN TUT | Fed bağımsızlığı/Powell hukuki gündemi ve dolar hassasiyeti |
| 13 | 4.585,66 | -0,28% | G01-X + ORG01 | ALTIN TUT | BLS CPI 08:30 ET; haberin alt bileşenleri önemli |
| 14 | 4.626,07 | 0,88% | ORG01 + ORG05 | ALTIN TUT | PPI/veri sonrası yumuşama beklentisi; İran gerilimi karşıt |
| 15 | 4.614,82 | -0,24% | ORG05 + ORG02 | ALTIN TUT | Jeopolitik rahatlama, başvuru/Fed söylemi: karşıt kanallar |
| 16 | 4.595,52 | -0,42% | ORG02 + ORG10 | ALTIN TUT | Dolar/faiz baskısı anlatısı; düşüş teyidi sınırlı |
| 17 | — | — | ORG06 | ALTIN TUT | Cumartesi, Grönland gerginliği |
| 18 | — | — | ORG06 | ALTIN TUT | Pazar, Grönland bağlantılı tarife tehdidi |
| 19 | — | — | ORG06 | ALTIN TUT | ABD MLK tatili; bazı spot fiyatlar olsa da NY17 eksik |
| 20 | 4.762,95 | 3,64% | ORG06 + ORG01 | ALTIN TUT | Tarife/Grönland gerilimi, USD ve hisselerden ayrışma adayı |
| 21 | 4.831,69 | 1,44% | ORG07 + ORG06 | ALTIN TUT | Grönland tehdidi kısmen geri alındı; ilk fiyat dalgası tamamen sönmedi |
| 22 | 4.935,69 | 2,15% | ORG06 + ORG09 | ALTIN TUT | Rahatlamaya rağmen altın güçlenmesi; rakip talep kanalı |
| 23 | 4.983,79 | 0,98% | ORG01 + ORG09 | ALTIN TUT | Yen/USD, faiz ve risk tema; pozisyon/metal aşırılık uyarısı |
| 24 | — | — | NO_EVENT | ALTIN TUT | Cumartesi, yeni uygulanabilir piyasa fiyatı yok |
| 25 | — | — | ORG06 | ALTIN TUT | Pazar, Fed haftası ve tarife belirsizliği |
| 26 | 5.009,54 | 0,52% | ORG09 + ORG10 | ALTIN TUT | Geniş altın yükselişi; fiyat ivmesi artıyor |
| 27 | 5.178,68 | 3,38% | ORG09 + ORG10 | ALTIN TUT | FOMC öncesi güçlü yükseliş, oynaklık riski |
| 28 | 5.414,58 | 4,56% | G01-X + ORG09 | ALTIN TUT | FOMC kararı 19:00 UTC; parabolik yükseliş, ilk satış teyidi yok |
| 29 | 5.378,82 | -0,66% | ORG10 + ORG12 | SAT — sonraki 09UTC | Gün içi zirveden belirgin geri alma, önceki kapanış altı; pozisyon riski |
| 30 | 4.891,20 | -9,07% | ORG02 + ORG10 + ORG12 | NAKİT TUT | Warsh Fed başkanı adaylığı, USD güçlenmesi, genel metal tasfiyesi; 29'una taşınmaz |
| 31 | — | — | NO_EVENT | NAKİT TUT | Cumartesi; yeni işlem fiyatı yok |

**Tablo okuma:** 09:00 AL ve SAT uygulamaları sırasıyla 06 ve 30 Ocak'ta yapıldı; sinyaller 05 ve 29 Ocak 22:00 UTC'de oluşturuldu. Tatil ve hafta sonunda fiyat çizgisi boş, ekonomik haber gözlemi varsa satırın kendisi duruyor. Fiyat yüzdeleri **önceki mevcut 21:45 kapanışına göre** hesaplanır; arada tatil varsa tek günlük getiri demek doğru değildir. İşlem durumu ve veri kalite alanlarının tamamı [31 satırlık sayısal günlük sicilindedir](OLAY_02_JAN2026_31_GUN_DNA_KARAR_MALIYET_DENETIMI_20261014.csv).

## 5. 100 USD net portföy ve değiştirilmeyen bazlar

| Karşılaştırma | Ay sonu 100 USD karşılığı | Net değişim |
|---|---:|---:|
| **Bu iki-işlemli, olay/risk-geçiş keşif hipotezi** | **112,67 USD** | **+%12,67** |
| Aynı fiyat kontratında baştan altın al-tut (02 Ocak 09:00 ASK 4.387,435, 30 Ocak 21:45 BID 4.895,118, %0,8 alış ve satış) | **109,79 USD** | **+%9,79** |
| 06 Ocak aynı AL, **29 Ocak risk kapısını uygulamadan** ay sonuna kadar altın tut | **107,80 USD** | **+%7,80** |
| Nakit tut | **100,00 USD** | **%0,00** |

**Asıl sınırlama:** Bu tek ayın **+2,88 USD al-tut farkını** ileri dönük üstünlük veya istatistiksel anlamlı sonuç olarak kullanmak geçersiz: Ocak 2026 sonuçları ve önceki Astra analizi kural belirlenmeden önce görülmüştür. Ay içindeki risk kapısı özellikle bu ayın sonu için seçilim/overfit taşıyabilir. Aynı kural kör ve sabit şekilde başka tarihlerde test edilmeden performans iddiası yok.

**Fiyat QA:** 30 Ocak 21:45 HistData kapanış proxy'si 4.891,195, eşsaat Dukascopy BID 4.895,118: **farklı kaynak/symbol/bidask tanımları aynı diye birleştirilmedi**. Buy-hold benchmark mark'ı tutarlı Dukascopy BID 4.895,118; portföy zaten 30 Ocak 09:00'da nakde geçmişti. HistData'nın bazı kayıtlarında 15 native dakikadan az kapsama bulunur, fakat işlem yapılan 09:00 Dukascopy barları kaynak BID/ASK olarak mevcuttur. 1 Ocak'ta Duka tablosunda 96 sentetik benzeri satır olmasına karşı HistData'da yalnız 23:00 sonrası dört bar vardır; tatil günü 21:45 kararı uygulamaya dönüştürülmez.

## 6. Öğrenme: DNA karakterlerinin Ocak içindeki davranış karşılaştırması

- **ORG04/ORG01:** Jeopolitik haberin altında maliyet sonrasında araştırılabilir UP fırsatı, haberin yayımlanması ile sonraki fiyat teyidi birlikte oldu. Ancak haber ve getiri karşılaştırması gerçek nedensel ilk başlatıcıyı kanıtlamaz.
- **ORG06/ORG07 rekabeti:** Tarife/Grönland tehdidinin geri çekildiği dönemde altın kapanışının güçlenmesi sürüyorsa yalnız haber etiketinden SAT kararı üretme. Eski Astra kararlarında haber değişimine sık reaksiyon maliyet doğurdu; bu örnek yanlışlamayı akılda tutuyor.
- **ORG09→ORG10 aday geçişi:** Birikmiş yükseliş ve büyük gün-içi geri alma fiyat-risk karakterini değiştirebilir; fakat P4 gerçekten başlangıç anında biliniyor ve ORG12 zorunlu tasfiye nedenini önceden biliyorduk iddiası **yok**. Fiyat riski, ekonomik nedensellik ve uygulanabilir işlem **üç ayrı kayıt**.
- **Öğrenme statüsü:** OLAY-02 tarihi 31 günlük karar/sonuç/kanıt saklar. ÖĞREN-03'te yeni sayısal kuralı kesin DNA yapma; yalnız genel karakter dersi tarihsiz olarak eklenebilir. %2/%3 eşikleri Ocak görülerek oluşturulduğundan bağımsız testte **kural sürümü sabitlenmeden** tekrar kullanılmamalı.

## 7. Bağımsız eleştiri ve Astra karşılaştırması

**Astra önceki Ocak–Eylül yürüyüşünün Ocak net sonucu ayrı fiyat kaynağı ve farklı hedef işlem sırasıyla +%5,07 idi** (bk. [Astra özgün rapor](https://github.com/ataullahturgut/sim3-automation/blob/research-gold-daily-replay-20261013/gold_axis_2026/daily_replay_20261013/REPORT_JAN_SEP_TR.md)). Bu tutarı **bu simülasyonun fiyat bazına doğrudan üstünlük testi** olarak kullanma: evren, çıkış tarihi ve işlem etkisi farklı. Astra'nın 29 Ocak TUT, 30 Ocak SAT kararı 02 Şubat'a taşındı; bu sonuç Jan29 fiyat-risk çıkış fikrinin niçin ayrıca araştırılabileceğini gösterir, fakat geçmiş sonuç görülerek oluşturulan yeni kuralın öngörü geçerliliğini sağlamaz.

**Bilimsel nihai statü:** 31/31 takvim günü ve 2/2 hipotetik fiyat fill kaydı tamamlandı; tarihli 21:45 as-of fiyatı, sinyal sonrası 09:00 ASK/BID, %0,8 iki yön maliyet hesabı yapıldı. **Giriş/çıkış kuralları sonradan belirlendi, gerçek banka fiyatı / birebir ilk haber saati / bağımsız OOS yok.** Bu yüzden `EXPLORATORY_REPLAY_COMPLETE`, fakat `LIVE_TRADING_READY=NO` ve `COSTED_OOS_VALIDATED=NO`.

## 8. Kritik duyarlılık — bu başarı hangi varsayıma bağlı?

- Aynı alış yapılıp **29 Ocak'taki risk çıkışı tamamen kaldırılırsa**, 30 Ocak ay sonundaki komisyonlu likidasyon vekili **107,80 USD**. Bu yüzden sonuçtaki yaklaşık **4,88 USD fark**, risk kapısının geçerli olduğu varsayımına bağlıdır.
- 29 Ocak sinyalinde 21:45 fiyatının gün içi zirveye göre geri çekilmesi **%3,869**. Bu örnekte **%3** eşiği SAT adayı üretir; aynı koşulun **%4** yapılması o günü atlar. Dolayısıyla bu tek ayda sonuç eşik seçimine duyarlıdır; eşik çoktan görülmüş fiyatlardan türetildiği için bağımsız başarı sayılmaz.
- 05 Ocak'ta önceki geçerli kapanıştan yükseliş **%2,696**. %2 fiyat koşulu geçilirken %3 geçilmez. Bu da giriş kararının eşik hassasiyetini gösterir; 05 Ocak dışında daha sonraki olayların bu farklı kuralla ne olacağı bu testin konusu değildir.
- 29 Ocak kararındaki XAU 5.378,815'ten 30 Ocak 09UTC'deki BID 5.116,535'e **−%4,876** hareket önceden kurtarılmamıştır. 30 Ocak 09UTC BID 5.116,535'ten 21:45 BID 4.895,118'e **−%4,327** sonraki hareketten kaçınılmıştır; yüzde hesabı karara *sonradan* bağlanmaz.

**Hüküm:** Yeni DNA riski uyarısı *araştırmaya değer*; ama %2 giriş ve %3 çıkış sayıları, farklı rejimlerde freeze/paper test öncesi kullanılırsa **hindsight optimisation** taşır. Bu nedenle bu ayda pozitif sonuç bulunmuş olması ekonomik DNA'nın karar gücünü doğrulamaz.
