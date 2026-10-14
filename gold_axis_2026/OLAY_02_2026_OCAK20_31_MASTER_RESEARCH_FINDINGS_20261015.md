# OLAY-02 — Ocak 2026 20–31 As-of Ekonomik DNA Araştırma Merkezi

**Araştırma hattı:** ANA-01 metodolojisi, OLAY-02 tarihli haber/fiyat/karar kanıtları, ÖĞREN-03 G01–G06 ve ORG ekonomi-mekanizma hipotezleri. Bu dosya yeni dördüncü manifest değildir; OLAY-02'deki tarihli 20–31 Ocak 2026 araştırma eki ve bulgu indeksidir.

**Dal:** `research-gold-jan2026-asof-restart-20261015`, 43 eski Ocak 2026 deney/artifact dosyası silinmiş `c2d1ab4` commitinden ayrılmıştır. **Eski deney sonuçları/kararları yeniden kullanılmamıştır.** Üç manifest değiştirilmedi.

## Veri-kapsama ve çalışmanın dürüst niteliği

20–31 Ocak 2026 arasında Türkiye saatiyle **12 gün × 96 = 1152 takvim kontrolü** araştırma defterlerine işlendi. **826 tam HistData M15 bar-kontrolü, 326 boş / eksik / kapalı kontrol.** 20 Ocak 86/96, 21 Ocak 92/96, kalan 22–31 Ocak 648/960. **1152 bağımsız haber incelemesi, 1152 GPT ekonomist kararı veya tam banka backtesti yapılmış değildir.** 20 ve 21 Ocak ayrıca bağlamsal karar günü analizi, 29–30 Ocak ise ayrıntılı negatif/karşıt mekanizma vakası olarak araştırılmış; diğer günler için öncelikle saat/ham fiyat/çapraz piyasa ve seçili haber takvimi taraması tamamlanmıştır.

As-of zaman damgası kuralı: fiyatın tam M15 **başlangıcı+15 dakika** <= kontrol; CME H1 `ts_event+1h<=kontrol` fakat gerçek vendor gecikmesi henüz bağımsız kanıtlı değil; borsa tatilinde yoklama hâlâ yapılır ama hayalî emir olmaz. Reuters **modified** yazılarının ancak güncellenme zamanından sonraki kontrollerde tam içeriği kullanılabilir. **Tek bir 2026-10-08 tarihli tarihsel fiyat vintage** 2026 Ocak orijinal veri erişimini kanıtlamaz.

### Kanıt kayıtları
- [20 Ocak 96-slot karar/delil CSV](OLAY_02_2026_OCAK20_96_ASOF_RESEARCH_LEDGER_20261015.csv), [20 Ocak derin ekonomik araştırması](OLAY_02_2026_OCAK20_DEEP_CAUSAL_DECISION_AUDIT_20261015.md)
- [21 Ocak 96-slot CSV](OLAY_02_2026_OCAK21_96_ASOF_EVIDENCE_LEDGER_20261015.csv), [21 Ocak diplomatik ters mekanizma raporu](OLAY_02_2026_OCAK21_CAUSAL_REVERSAL_RESEARCH_20261015.md)
- [22–31 Ocak 960-slot veri ve olay-zaman taraması](OLAY_02_2026_OCAK22_31_960_ASOF_DATA_EVIDENCE_20261015.csv), [10 günlük kaynak ve fiyat kapsama denetimi](OLAY_02_2026_OCAK22_31_CHRONOLOGY_DATA_QA_20261015.md)
- [29–30 Ocak büyük satışın ilk kırılması / Warsh öncesi ve sonrası mekanizmaları](OLAY_02_2026_OCAK29_30_FIRST_BREAK_VS_WARSH_CAUSAL_AUDIT_20261015.md)

## 12 gün: gözlenen değişim ve yatırım yetkisi

| Türkiye günü | Tam fiyat kontrolü / 96 | Günün son bilinen tam araştırma fiyatı, USD | O ana kadar yorumlanabilir ekonomik durum | BANKA AL/SAT yetkisi |
|---|---:|---:|---|---|
| 20 Ocak | 86 | 4.749,525 | Grönland tarife/politika riski G02/G03 ve fiyat ivmesi G06; haber ilk sebep doğrulaması yok | YOK |
| 21 Ocak | 92 | 4.819,865 | Davos askeri güç kullanılmayacak, sonra NATO çerçeve/tarife geri çekilmesi; sırası önemlidir | YOK |
| 22 Ocak | 92 | 4.922,675 | Gerilimin azalmasına karşın altın UP; salt G02→altın UP tek açıklama değil | YOK |
| 23 Ocak | 92 | 4.982,245 | Altın yeni zirvelere yakın; G04/G06 rakip kanallar | YOK |
| 24 Ocak | 5 | 4.983,785 | Cumartesi erken seans sonrası veri büyük ölçüde yok | YOK |
| 25 Ocak | 0 | — | Pazar araştırma verisi yok, 1m cache'i işlem fiyatı sayılmadı | YOK |
| 26 Ocak | 87 | 5.046,435 | 5.100 üstü haber ve ani dalgalanma; şokun kapsamı fiyat sinyalinden çıkarılamaz | YOK |
| 27 Ocak | 92 | 5.142,095 | Fiyat trendi sürüyor; haber/fiyat nedenselliği belirsiz | YOK |
| 28 Ocak | 92 | 5.383,265 | Fed FOMC 22:00 TRT itibarıyla bilinebilir; 22:00 öncesine taşınmaz | YOK |
| 29 Ocak | 92 | 5.354,145 | Gün içi 5.585,555 görüldükten sonra 18:15'te −%3,619 peak drawdown; ilk G06/G05 çalkantı alarmı | YOK; `SELL_REVIEW` only |
| 30 Ocak | 92 | 4.861,105 | Satış Warsh adayı resmî 14:48 TRT duyurusundan **önce** çoktan başladı; haber sonrası G01 katkısı ayrı | YOK |
| 31 Ocak | 4 | 4.860,485 | Cumartesi erken seans dışında geçerli fiyat yok; 31 Ocak kapanış varsayımı değildir | YOK |

**Sistemin zayıflığı gizlenemez:** 20 Ocak'tan beri GOLD taşımak kararı 29–30 Ocak büyük zarar/görülen kâr erimesini önleyemedi. 29 Ocak 18:15 `-3%` risk alarmı daha önce geliştirilmiş, bağımsız olarak doğrulanmış satış politikası değildir. 18:30'da 5188,798'e hızlı düşüş, 19:15'te 5272,835'e hızlı geri sıçrama; bu riskli olayın mekanizması sırf teknik eşikle doğrulanmaz. Nakit başlangıç portföyü 20–28 Ocak yükselişini kaçırdı.

**İlk katalizörü yanlış atfetmeyin:** 29 Ocak 18:15 TRT görülen düşüşte 29 Ocak tepesine göre −%3,619 (XAU kapanış 5383,415). 18:30'da kapanış 5188,798 (tepeye −%7,103). Trump'ın Kevin Warsh adayını resmen ilanı **30 Ocak 14:48 TRT** ve ilan öncesi son 14:45 XAU araştırma fiyatı 5120,64; bu nedenle Warsh gün önceki düşüşün birincil ilk tetikleyicisi olamaz. Jan30 sonrası hareketin kuvvetlendiricisi olabilir, ancak eş zamanlı fiyat+USD/faiz+gerçek teminat verisi olmadan kesin ispat da değildir. [Fed arşivi](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm) · [Kevin Warsh resmî Trump paylaşım arşivi](https://www.presidency.ucsb.edu/documents/truth-social-posts-january-30-2026).

## Portföy karşılaştırması — gerçek emir değil

Mevcut portföy kesin bilinmediği için **GOLD veya CASH** şartlı olarak izlenir. 20 Ocak ilk güvenilir 02:15 HistData araştırma kapanışı **4670,348**, 31 Ocak son geçerli araştırma 15m kapanışı **4860,485**: brüt **+%4,071**. Yalnız *zorunlu satış varsayımıyla* 100$ başlangıç, alımda ve satımda ayrı ayrı %0,8 teorik komisyon ardından **$102,413** eder. Bu banka ASK/BID veya USDTRY ve piyasa saati garantili emir sonucu **DEĞİLDİR**, ilk giriş as-of politikayla onaylanmış da değildir. Zirveden yapılan hayalî SAT yoktur.

## Risk/engeller ve bir sonraki bilimsel deneyde tamamlanması gerekenler

1. `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` aynı saatte HistData kapanışına **1.643/1.644** eşit bid fiyatı (ocak), `m1_matched=1` **0**; iki bağımsız veri kaynağı veya orijinal Türk bankası ASK/BID onayı sayılmaz. HistData native-minute bar<15 kullanılamaz.
2. `SI.c.0` çok seyrek ve aşırı düşük işlem hacmi; `ZN.c.0` tahvil futures fiyatı, doğrudan ABD tahvil faizi değil. USD, nominal/reel faiz, orijinal haber firstprint, ETF/CFTC and source-vintage yayın saatleriyle bağımsız aynı-UTC doğrulama yetersiz.
3. Gerçek banka iki yön %0,8 komisyon teorik fiyat-eşiği **%1,6194** + spread/slippage/kur; mevcut veriyle `BANK_EXECUTABLE=FALSE`. Hiç BUY veya SELL doldurulmadı; her GOLD/CASH kontrolü kaydedildi fakat 22–31 için derin ve kapsamlı ekonomik gerekçe doğrulanmış değildir.
4. Yeni algoritma kriteri, `SELL_RISK_REVIEW`, ilk olay ve karşıt mekanizma G01/G02/G03/G04/G05/G06, ORG10/ORG12 **önce 2023–2025 ve bağımsız ileri dönemlerde maliyetli OOS sınanmalı**; 29–30 başarılıymış gibi tarihsel kural seçilmemeli.

**Statü:** FİYAT/SAAT/DNA ÖN TARAMASI 20–31 TAM, DERİN EKONOMİK/KAYNAK İLKPRINT ÇALIŞMASI KISMİ, BANKA YATIRIM STRATEJİSİ DOĞRULAMA YOK. ANA-01/OLAY-02/ÖĞREN-03 korunur; yeni tarihli deliller OLAY-02 altında eklenmiştir.