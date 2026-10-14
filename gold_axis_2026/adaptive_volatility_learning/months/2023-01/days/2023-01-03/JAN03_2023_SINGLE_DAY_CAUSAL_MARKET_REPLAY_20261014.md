# 3 Ocak 2023 — TRT 96 × M15 küresel olay nedenselliği ve maliyetli pozisyon kararı
**Statü:** `DAY_REPLAY_COMPLETED / CAUSAL_NEWS_TIME_GATED / GPT_NOT_HINDSIGHT_FREE / NO_ACTUAL_BANK_ORDERS` · **Tek gün:** 3 Ocak 2023. Önceki 2 Ocak başlangıç **100 USD CASH**. **BIST dahil HİÇBİR Türkiye iç piyasası XAU/USD yön girdisi değil.** `FULL_HISTORY_DISCOVERY` ile as-of olay delili asla karıştırılmadı.

## 1. Sayısal denetim ve gerçek zaman hizası
- Her 15 dakika **00:00–23:45 TRT toplam 96 karar noktası**: 00:00–01:45 arasında 8 nokta henüz spot fiyat yok; **02:00'de M15 açılıyor ancak bar tamamlanmamış**; 02:15'te ilk tamamlanmış bar gözlenir. **88 M15 bar BAŞLANGICI**, **23:45 itibarıyla 87 tamamlanmış M15 bar**, **9 henüz veri olmayan kontrol**. 23:45–00:00 son barın kapanışını yanlışlıkla 23:45'te kullanma. Bilinen son tam XAU 23:30–23:45.
- Önceki tam 2022-12-30 seans BID **1823,46**, ASK **1824,25**, MID **1823,855**; başlangıçtaki 47–70+ saatlik bayat referans 3 Ocak emir fiyatı sayılmadı. İlk yeni M15 02:00–02:15 TRT **BID 1826,22 / ASK 1828,04**, açılış spreadi 1,82 USD, daha geniş.
- 23:45 TRT'de son tamamlanmış M15 BID **1836.84**, ASK **1837.19**, MID **1837.015**; önceki tam seans MID'ine göre **+0.722%**. Günün en yüksek ASK **1850,18** (başlangıcı 3 Ocak 07:30 UTC, **10:30–10:45 TRT barı**). Bu zirve **EX_POST**, öncesinde işlem fiyatı olarak kullanılamaz.
- XAU gizli Neon `gold_research_evduka_xau15m_bidask_candidate`: bu gün **88/88** temel bar. Histdata M15 aynı periyotta 88 kaynak çubuğu var (bağımsız birebir fiyat kontrolünden daha zayıf *kapsama* kontrolü). **Gizli vendor raw fiyat serisi GitHub'a kopyalanmadı**. Türetilmiş 15 dk hareket, spread baz puanı, UTC as-of olay bilgisi, periyot bazlı karar CSV'de.
- CME türev 1H tablo `gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c`: **ZN 22**, **NQ 22**, **CL 22**; **SI 8, GC 2** ve çok düşük hacim = teyit vermeye uygun değil. Güvenli ihtiyat: H1 `ts_event` bar BAŞLANGICI kabul edildi ve ancak **+1 saat sonra** kontrol notuna girdi. ZN 10Y tahvil vadeli fiyatıdır; doğrudan 10Y getiri seviyesi değildir (fiyat artışı çoğu zaman faiz düşüşüyle uyumlu).
- USD/DXY fiyatı, US 2Y cash, fon günlük ETF firstprint ve bankanın gerçek uygulanabilir metal kotasyonu **o dakikalara hizalı yok**. Bu delillere `MISSING` denildi; hiçbir şey sıfır/düşüş olarak doldurulmadı.
- %0,8 AL, %0,8 SAT komisyonu sonrası, makas yoksa tam tur başabaş **+%1.6194**. Gerçek BID/ASK bunu yükseltir. **Günün geçmiş seans MID'den görülen en yüksek ASK hareketi bile +%1.443**; bu tek başına aynı gün maliyetli tam-tur fırsatı anlamına gelmez. Gelecekte daha büyük hareketin olamayacağını göstermez.

## 2. Gerçek tarihli olay kimlikleri, karşı deliller ve geçmiş vaka analojisi
| İlk erişilebilir zaman (TRT) | As-of olay | Yön kanalı / geçmiş olayla bağlantı | Verilecek tepki |
|---|---|---|---|
| **Önceki yıl** | [14 Aralık 2022 FOMC %4,25–4,50](https://www.federalreserve.gov/newsevents/pressreleases/monetary20221214a.htm); [Nov 10 2022 beklenenden serin CPI ve USD/faiz düşüşü](https://www.marketscreener.com/news/latest/Wall-St-ends-sharply-higher-as-cooling-inflation-fuels-hope-of-easing-Fed-42276308/) | **Gerçek vaka analojisi:** Nov 2022 CPI sürprizi+faiz/USD beraber yumuşayınca risk ve altın lehine mekanizma doğabilir. 3 Ocak 2023'te **CPI sürprizi yok**; analojiyi otomatik UP emir kuralına çevirme. 2022 Fed sıkılaşması karşı risk. | Nötr ön bilinen arka plan; yeni delil gerektirir |
| **07:30 TRT** | [3 Ocak Reuters Caixin PMI](https://www.reuters.com/markets/asia/china-dec-factory-activity-extends-declines-covid-infections-caixin-pmi-2023-01-03/): Aralık imalat **49,0**, önceki 49,4, **Reuters anketine göre beklenti 48,8**. Yayım Reuters **04:19 UTC**. | Çin yeniden açılma orta-vade talep desteği; **bugünkü üretim daralması** ters risk, fakat veri tahminden iyi. **Kötü haber = altın kesin düşer** çıkarımı yapılmaz. | XAU ve ZN çapraz akışı takip; otomatik AL yok |
| **Gün ortası, en erken 15:15 TRT** | [Reuters altının altı ayın zirvesini görmesi ve ABD tahvil getirilerinin gevşemesi](https://www.marketscreener.com/news/latest/Gold-touches-six-month-high-in-positive-start-to-2023-42648130/). Sayfa yayın etiketinde **10:22 UTC**, metinde **12:05 UTC fiyatı** var; bu çelişkiden dolayı **12:05 UTC'den önce içeriği kullandırmadık**. | Faiz/altın pozitif bağlantısı, Nov2022 geçmiş neden şablonuyla uyumlu; fakat zirve sonrası fiyat çözülmesi ve **$1850 civarı direnç**. | Fiyat yükseldi diye geriden büyük işlem açma |
| **17:30 TRT** | [AP Almanya 2022 Aralık CPI %8,6](https://apnews.com/article/2ba565a72a327c22671d73da785b12f2), **14:26:36 UTC AP yayımlama**. | EUR/USD ve ECB beklentisi kanalları; ABD ons altın için **doğrudan belirsiz**, dolar içsel veri eksik | Yeni tek yönlü emir yok |
| **18:00 TRT** | [ABD imalat PMI final 46,2, 09:45 EST](https://forex.tradingcharts.com/economic_calendar/2023-01-03.html?code=USD) | ABD büyüme zayıflığı Fed beklentisini yumuşatabilir ama tek başına altın için kesin değildir; Jan4 ISM başka bir veridir ve **bugün açıklanmadı** | ZN/NQ/XAU aynı saatli tepki test et, kararı koru |
| **18:15 TRT** | [ABD Kasım inşaat harcaması +%0,2, 10:00 EST](https://www.census.gov/economic-indicators/calendar-listview-2023.html) | Büyümede kısmi direnç, önemli sürpriz büyüklüğü teyit edilmedi | Kararı koru |
| **21:45 TRT'den sonra** | [Reuters gün sonuna doğru altın +%, DXY yaklaşık +%1 ve paladyum keskin düşüş](https://www.marketscreener.com/news/latest/Gold-rises-to-near-six-month-highs-while-investors-await-Fed-minutes-42651251/). Reuters içindeki fiyat zamanı **18:42 UTC**, ilk metin yayım etiketi farklı; temkinli erişilebilirlik 18:42 UTC olarak alındı. | **Karşı delil:** Altın yükselirken dolar da güçlenebilir. Basit "dolar düştü o yüzden altın çıktı" açıklaması yanlış olur. SI/GC yerel 1H vadeli kayıtları hacimsiz. | Net kalan UP fırsatı için güçlü teyit yok |

**Sonradan bilinen açıklama**: ABD hisse piyasalarının zayıflaması ve doların güçlenmesi 3 Ocak dünya piyasası Reuters gün sonu özetinde yer alır ([3 Ocak 22:18 GMT Reuters](https://www.lse.co.uk/news/dollar-jumps-us-stocks-buck-global-rally-uf7bip16n4v6qjo.html)); bu metin **Türkiye saatiyle 4 Ocak 01:18 sonrasında**, 3 Ocak karar defterine alınmadı.

## 3. Olay→gerekçe→karar, günün tam takibi
| TRT | MID XAU | Önceki 30 Aralık kapanışına göre | Tamamlanmış 1H ZN / NQ / CL seviyesi* | Bilinen son delil | Olay evresi / karar |
|---|---:|---:|---|---|---|
| 00:00 | — | — | — / — / — | CHINA_REOPENING_DEC2022 | NO_FRESH_XAU_MARKET · **NAKİT TUT** |
| 01:45 | — | — | — / — / — | CHINA_REOPENING_DEC2022 | NO_FRESH_XAU_MARKET · **NAKİT TUT** |
| 02:00 | — | — | — / — / — | CHINA_REOPENING_DEC2022 | NO_FRESH_XAU_MARKET · **NAKİT TUT** |
| 04:45 | 1827.840 | 0.218% | 112.563 / 10997.25 / 80.25 | CHINA_REOPENING_DEC2022 | UNDECIDED · **NAKİT TUT** |
| 05:30 | 1830.610 | 0.370% | 112.594 / 10985.50 / 79.59 | CHINA_REOPENING_DEC2022 | UP_EARLY · **NAKİT TUT** |
| 07:30 | 1841.195 | 0.951% | 112.641 / 11032.75 / 80.04 | CHINA_CAIXIN_DEC_MANUFACTURING_49_0 | UP_ACTIVE_UNCONFIRMED_CAUSAL · **NAKİT TUT** |
| 08:45 | 1840.120 | 0.892% | 112.656 / 11022.00 / 79.89 | CHINA_CAIXIN_DEC_MANUFACTURING_49_0 | UP_ACTIVE_UNCONFIRMED_CAUSAL · **NAKİT TUT** |
| 10:00 | 1842.020 | 0.996% | 112.656 / 11051.00 / 80.54 | CHINA_CAIXIN_DEC_MANUFACTURING_49_0 | UP_ACTIVE_UNCONFIRMED_CAUSAL · **NAKİT TUT** |
| 10:45 | 1848.875 | 1.372% | 112.656 / 11051.00 / 80.54 | CHINA_CAIXIN_DEC_MANUFACTURING_49_0 | UP_CONFIRMED_PRICE_ONLY · **NAKİT TUT** |
| 12:45 | 1840.805 | 0.929% | 112.828 / 11126.75 / 80.73 | CHINA_CAIXIN_DEC_MANUFACTURING_49_0 | UP_ACTIVE_UNCONFIRMED_CAUSAL · **NAKİT TUT** |
| 15:00 | 1833.235 | 0.514% | 112.891 / 11078.25 / 79.14 | CHINA_CAIXIN_DEC_MANUFACTURING_49_0 | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 15:15 | 1833.670 | 0.538% | 112.891 / 11078.25 / 79.14 | REUTERS_GOLD_HIGHEST_6M_AND_FALLING_YIELDS | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 15:30 | 1835.445 | 0.635% | 112.891 / 11078.25 / 79.14 | REUTERS_GOLD_HIGHEST_6M_AND_FALLING_YIELDS | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 15:45 | 1835.560 | 0.642% | 112.891 / 11078.25 / 79.14 | REUTERS_GOLD_HIGHEST_6M_AND_FALLING_YIELDS | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 17:15 | 1838.925 | 0.826% | 112.969 / 11116.50 / 79.48 | REUTERS_GOLD_HIGHEST_6M_AND_FALLING_YIELDS | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 17:30 | 1841.245 | 0.953% | 112.969 / 11116.50 / 79.48 | GERMANY_DEC_CPI_PRELIM_8_6 | UP_ACTIVE_UNCONFIRMED_CAUSAL · **NAKİT TUT** |
| 17:45 | 1847.790 | 1.312% | 112.969 / 11116.50 / 79.48 | US_DEC_SP_GLOBAL_MFG_FINAL_46_2 | UP_CONFIRMED_PRICE_ONLY · **NAKİT TUT** |
| 18:00 | 1844.950 | 1.157% | 113.078 / 10993.75 / 79.24 | US_NOV_CONSTRUCTION_SPENDING_PLUS_0_2 | UP_CONFIRMED_PRICE_ONLY · **NAKİT TUT** |
| 18:45 | 1828.870 | 0.275% | 113.078 / 10993.75 / 79.24 | US_NOV_CONSTRUCTION_SPENDING_PLUS_0_2 | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 19:00 | 1833.315 | 0.519% | 112.766 / 10974.50 / 78.99 | US_NOV_CONSTRUCTION_SPENDING_PLUS_0_2 | UP_FADING_OR_REVERSAL · **NAKİT TUT** |
| 23:45 | 1837.015 | 0.722% | 112.641 / 10938.00 / 76.91 | REUTERS_LATE_GOLD_DXY_UP1PCT_AND_MIXED_METALS | UP_FADING_OR_REVERSAL · **NAKİT TUT** |

**Önemli nedensellik farkı:** Fiziki ons altının yönüne BIST yerel hisse endeksi bağlamı katılmıyor. 3 Ocak'ta fiyatın 6 aylık yüksek düzeyi görmesi **OBSERVED MEDIUM UP CANDIDATE**; fakat haber/ZN/CL/NQ/DXY kombinasyonu kalan **+%1,62 üstü işlem kârını** yeterli güvenle tahmin etmiyor. Saatli DXY ve banka kotasyonu eksik; makro aktarımlarda karşıt örnek var. Bu yüzden gün içinde erken yükselişte **TAKİP / CASH**, geri çekilişte de **WAIT / CASH**, sonraki günün fiyatları 3 Ocak kararına sızdırılmadı. **Her slotta cevap üretildi; işlem yokluğunu sıfır takip diye sunma.**

## 4. İlk gün açılışından itibaren başlatılan 100 USD pozisyon muhasebesi
| 3 Ocak 2023 TRT kapanışı (en son 23:45 kontrol) | Sonuç |
|---|---:|
| Başlangıç durumu | 2 Ocak'tan **100,00 USD CASH** |
| Satın alma / Satış adedi | **0 / 0** |
| Masraf | **0,00 USD** |
| Gün sonu net NAV | **100,00 USD** |
| Getiri | **%0,00** |
| Aynı gün 02:15 ilk ASK'dan AL → 23:45 BID'a zorunlu tasfiye örneği | **98.8801 USD** (her iki %0,8 dahil; **gerçekte uygulanmadı**) |

**Bu yalnızca bir günlük likidasyon kıyasıdır.** Nakit kararının gelecekteki aylık altın-al-tutdan daha iyi olacağını iddia etmiyoruz; sonraki günler fiyat sonucu **3 Ocak karar girdisi değildir**.

## 5. Keskin risk/öğrenme kaydı ve sonraki güne sınırlar
1. **Zaman/gün etiketleme:** 00:00–01:45 TRT XAU veri yok. 02:00 başlayan bar ancak 02:15'te tamam; 23:45 başlayan son bar 4 Ocak 00:00'da tamam. **88 başlangıç / 87 tamamlanan** farkını hep koru.
2. **Olay karşıtları:** Nov2022 disinflasyon/yield/USD düşüş analoğu ile Jan2023 Caixin PMI sürpriz yönü ve Fed sıkılaşması aynı mekanizma değildir. 3 Ocak altın+USD beraber yükselebildiğinden tek mekanizma açıklaması zayıf. Çin talep olgusu çok aylı; olay üzerinden 15 dakika ileri garantili ticaret değildir.
3. **As-of haber derlemesi:** Reuters metinlerinin 10:22Z sayfa etiketi ve metindeki 12:05Z, diğerinde 16:03Z ve 18:42Z farkları olabilir. **Makale revizyonu ihtimaline karşı daha geç zaman** kullanıldı. Haber portföy girişinde bir sinyal olarak kullanılmadı, dolayısıyla bu belirsizlik sonuç NAV'ını değiştirmez.
4. **Kritik veri boşlukları:** NQ/ZN/CL yüksek frekans proxy; 1H `ts_event` varsayımı source audit yapılmadan bağımsız zaman ispatı değil. GC/SI çok ince; USD/DXY ve gerçek banka kotasyonu yok. Bu gün sistemin **büyük olay ileri alarm gücü test edilemedi**; yalnız temkinli karar muhasebesi ve mekanizma açıklaması elde edildi.
5. **Pozisyon:** 100 USD CASH. **4 Ocak henüz bu günlük as-of protokolünde işlenmedi**; dosyada 4 Ocak için yeni veri veya işlem ileri sürülmüyor.

**Kaynaklar:** Yukarıdaki 2022–2023 ilk gün haber/araştırmalar. Her M15 bar düzeyi için ham veri: kullanıcı Neon Gold Control private proje; public GitHub yalnız türetilmiş feature ve sınırlı örnek. Ayrıntılı CSV: `JAN03_2023_TRT_96X15M_CAUSAL_DECISION_LEDGER_20261014.csv`; yapılandırılmış mekanizma/ilk erişim saatleri: `JAN03_2023_EVENT_GPT_DECISION_RESULTS_20261014.json`.
