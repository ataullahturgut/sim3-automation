# 2 Ocak 2023 | İlk gün: Türkiye saatiyle 96 × 15 dakika olay–fiyat–karar taraması
**Araştırma yapıldı:** 14 Ekim 2026 | **Çalışılan tek gün:** Pazartesi **02.01.2023** | **Kontrol saati:** Europe/Istanbul, 00:00–23:45, 15 dakika; 96 slot. **Sonraki güne geçilmedi.**
**Araştırma kipi:** geçmiş fiyat/olay keşfi + geçmiş tarihte erişilebilirlik sınırlı karar yeniden oynatması; gerçek banka kotasyonu ve canlı işlem DEĞİLDİR. İlk portföy $100 **CASH**.
**Durum:** `DAY_COMPLETE_NO_EXECUTABLE_PRICE_QUOTE`. İşlem fırsatının gerçekten bulunmadığı **kanıtlanmadı**; kayıtlı spot referans fiyat akışı içinde **gözlenemedi**.

## Tatil günü / işlem saati neden önemli?
- **1 Ocak 2023 Pazar:** Türkiye'de yılbaşı resmi tatili. [Borsa İstanbul 2023 tatil listesi](https://www.borsaistanbul.com/resmi-tatil-gunleri). Kullanıcı talimatıyla **2 Ocak'a geçildi**.
- **2 Ocak Pazartesi:** Türkiye'de Borsa İstanbul işlem gördü; BIST100'ün +%2,76 olduğu gün sonu haberinin yayın zamanı **18:49 TRT** ([Bloomberg HT, 2 Ocak 2023](https://www.bloomberght.com/borsa-yeni-yila-rekorlarla-girdi-2322406)). Yani "Türkiye'de tüm piyasalar tatil" ifadesi **YANLIŞ** olur.
- Ancak ABD'de **2 Ocak yılbaşı gözlenen tatili** ([CME official 2023 memo](https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-advisory.pdf), [Fed January release calendar](https://www.federalreserve.gov/newsevents/2023-january.htm), [BLS January calendar](https://www.bls.gov/schedule/2023/01_sched_list.htm)). **Şanghay Altın Borsası** 31 Aralık–2 Ocak kapalı, 3 Ocak açılıyor ([SGE notice, published December 2022](https://en.sge.com.cn/eng_news_Announcement/10001252)).
- CME'nin ürün bazında kesin bütün XAU/USD kotasyonlarıyla özdeş olmaması önemlidir. Bu araştırmadaki spot fiyat erişimi *özel Neon BID/ASK vendor serisiyle* ölçülmüştür.

## 15 dakikalık gerçek veri taraması
Özel Neon tablosu `public.gold_research_evduka_xau15m_bidask_candidate`, EV Trading Labs/Dukascopy-derived XAUUSD **BID/ASK M15**. Bağımsız `public.gold_research_histdata_xau15m_candidate` verisinin aynı zaman sınırında fiyat çubuğu yok; üstteki kaynakla beraber asgari çapraz kapsama denetimi. Türk günü **[2023-01-01 21:00Z, 2023-01-02 21:00Z)**; böylece 96 adet farklı dakika slotu **0 yeni fiyat çubuğu** ile sonuçlandı.

- **Eldeki son geçerli eski bar:** 30 Aralık 2022 **21:45–22:00Z** = 31 Aralık **00:45–01:00 TRT**. Bu bar kapanışı **BID $1.823,46 / ASK $1.824,25 / MID $1.823,855**, spread **$0,79**. Ocak 2 için fiyat **değil**; tek başına emir fiyatı diye kullanmak lookahead/stale-quote hatası olur.
- **Gün başında bayatlık:** 47 saat. **Son slot 23:45 TRT:** 70 saat 45 dakika bayatlık. İzleme yapılır ama elde yeni yön ölçümü yoktur; **NO DATA** bulgusu teknik olarak **NO EVENT** etiketiyle değiştirilmez.
- **İlk bir sonraki gözlenen bar:** Pazartesi **2 Ocak 23:00Z**, yani Türkiye saatiyle **Salı 3 Ocak 02:00**. Pazartesi TRT veri veya AL/SAT hesabına **KESİNLİKLE dahil edilmez**. NY17 "3 Ocak seansı" tarih etiketi, takvim gününe göre işlem zamanından ayrılır.
- Eski benzer yılbaşı takvimi: **3 Ocak 2022 Pazartesi**, aynı özel XAU BID/ASK kaynağı TRT gününde **88 fiyat çubuğu** var. **2 Ocak 2023 Pazartesi** 0. İki günün aynı haftanın günü olması seansın açık olacağı anlamına gelmiyor; *observed-holiday* takvimi ayrı girdidir. Bu bir fiyat-yön analoğu değil, **likidite/veri erişilebilirliği analoğu**.

## O güne gelmeden zaten bilinen somut neden/sonuç olayları
| Olay ve tarih | Karar anında biliniyor muydu? | XAU etkisi değerlendirmesi | Karar üzerindeki etkisi |
|---|---|---|---|
| [Fed 14 Aralık 2022 FOMC](https://www.federalreserve.gov/newsevents/pressreleases/monetary20221214a.htm): hedef faiz %4,25–4,50 | Evet (önceden açıklanmış) | Yüksek faiz altının fırsat maliyeti için risk hipotezi; **bugün ABD faizi/dolar tepkisi yok** | Otomatik SAT veya AL yok; önce canlı ortak piyasa doğrulaması gerekli |
| [Çin 26 Aralık 2022 sınır/karantina gevşetmesi](https://finance.yahoo.com/news/1-china-scrap-covid-quarantine-161240216.html) | Evet | Metal talebi/ülke büyümesi lehine ihtimal; o gün SGE kapalı, yön ve şiddet henüz gözlenebilir değil | Büyük UP beklentisini teyit etmez |
| [SGE Aralık 2022 ön duyurusu](https://en.sge.com.cn/eng_news_Announcement/10001252): 2 Ocak 2023 kapalı | Evet | Likidite ve zaman riskinin doğrudan koşulu | **Mevcut pozisyon nakit ise yeni altın emri yok** |
| [ABD Fed/BLS 2 Ocak 2023 tatil takvimi](https://www.federalreserve.gov/newsevents/2023-january.htm) | Evet | 2 Ocak'ta normal ABD makro firstprint yok, USD/UST doğrulaması eksik | WAIT |
| [BIST 100 kapanış haberi 18:49 TRT](https://www.bloomberght.com/borsa-yeni-yila-rekorlarla-girdi-2322406): +%2,76 | **Sadece 18:49 sonrası**, CSV'de 19:00 kontrolünden itibaren | Yerel hisse piyasası risk iştahı **olumlu**; XAU yönünü ve global risk kanalını tek başına kanıtlamaz | 19:00–23:45 arası hipotez güncellenir, ancak altın fiyatı yok → karar **korunur** |

**Analojik mekanizma çözümü:** (a) Önceden bilinen Fed sıkılığı ile Çin açılımının yönleri birbirini dengeleyebilir, (b) global XAU spot/vendor ve ilgili CME/SGE tatil takvimi price-discovery mekanizmasını sınırlar, (c) Türkiye hisse piyasası pozitif kapanır fakat yalnız yerel BIST'ten USD/ons altına AL emri çıkarılamaz. Açılış boşluğu/şoku **3 Ocak'ta oluşabilir**, fakat o fiyatı 2 Ocak'ta biliyormuş gibi davranılmaz. *Dönüş/şok oldu veya olmayacak demek için 2 Ocak verisi yok.*

## Gün boyu tarama ve her slotun karar muhafazası
96 kontrol noktasının tamamı **[CSV karar denetimi](JAN02_2023_TRT_96X15M_ASOF_CHECKS_20261014.csv)** içindedir. Her satırda yerel kontrol saati, UTC saat, yeni iki-source XAU veri adedi, eskimiş son gerçek BID/ASK ve yaşı, karar anında bilinen olay kimliği, BIST haberinin ilk bilinebilir zamanı, olayın gözlemlenebilirliği, önce/sonra pozisyon, emir ve portföy değeri tutulur.

| Türkiye zamanı | 15 dk kontrol sayısı | Gün içinde yeni XAU fiyatı | Bilinen olay/ek bağlam | Karar |
|---|---:|---:|---|---|
| 00:00–05:45 | 24 | 0 | Fed + Çin açıklamaları **önceden**; ABD/Çin yeni yıl piyasa tatili | CASH koru |
| 06:00–11:45 | 24 | 0 | Türkiye iş günü; banka altın kotasyonu tarihsel kaydı mevcut değil | CASH koru |
| 12:00–17:45 | 24 | 0 | Seçili ABD Fed/BLS takviminde yeni açıklama yok; XAU M15 yok | CASH koru |
| 18:00–18:45 | 4 | 0 | BIST kapanış haberi 18:49'da yayımlanıyor, 18:45 kontrolü için **henüz bilinmiyor** | CASH koru |
| 19:00–23:45 | 20 | 0 | BIST risk iştahı +%2,76 olarak gözlendi; XAU BID/ASK yok | CASH koru |

**Her bir 15 dakikada denetlenen koşullar:** 1. Yeni tamamlanmış XAU BID/ASK var mı? **Yok**. 2. Önceki sinyal teknik açıdan geçerli mi? **Yeni sinyal üretilemez; bayat fiyat**. 3. As-of haber takvimi ve olay kimlikleri güncellendi mi? **BIST akşam ilk erişilebilir haberinden sonra bağlam güncellendi**. 4. Diğer piyasa kanıtı maliyeti karşılayacak güçlü yeni UP/DOWN *emir fiyatıyla* eşleşiyor mu? **Eşleşmiyor**. 5. Uygulanabilir banka ASK/BID var mı? **Doğrulanmış kayıt yok**. 6. Aksiyon? **HOLD CASH / WAIT**.

## İlk gün sonu $100 komisyonlu muhasebe
| Alan | 2 Ocak 2023 sonucu |
|---|---:|
| Başlangıç / Bitiş | $100,0000 / **$100,0000** |
| AL / SAT | 0 / 0 |
| Gerçekleşen işlem komisyonu | $0,0000 |
| Maliyetli net getiri | **%0,0000** |
| Araştırma verisinde güvenilir XAU emir fiyatı | **0** |
| Orta/büyük yönlü olay tespiti | **VERİ YOK, YÖNÜ DEĞERLENDİRİLEMEZ** |

**Net sonuç:** 96 kontrolde pozisyon aynı kaldı çünkü hiçbirinde 2 Ocak Türkiye gününe ait kullanılabilir yeni XAU/USD BID/ASK verisi veya tarihsel banka icra kotasyonu doğrulanamadı. **Bu, 2 Ocak'ta altın fiyatı dünyanın hiçbir yerinde oynayamazdı iddiası DEĞİL.** Zorunlu banka işlemi icat etmek ve ertesi günün fiyatıyla dün AL yazmak yasak. Sonraki gün (**3 Ocak**) için ilk fiyat 02:00 TRT'de başlıyor; ancak **bu araştırma 3 Ocak kararlarını çalıştırmadı**.

**Sınırlamalar:** Bu gün için her-slot hafızalı fiyat algoritmasının asıl performansı ölçülemez; olayların nicel şiddeti/direction/MFE/MAE hesaplanamaz. Haberlerin *ilk yayın tarihi* desteklenmeyenler geçmişten geriye kesin as-of takvimle atfedilemez. Yalnız tarihli ilk kaynaklar kullanıldı, 2023 Ocak daha sonraki sonuçları karar girdisine girmedi. Aylık tahmin kararı başlangıçta doğrulanmış bulunmadığından otomatik GOLD diye varsayılmadı. **Çalışılan gün: yalnız 2023-01-02.**
