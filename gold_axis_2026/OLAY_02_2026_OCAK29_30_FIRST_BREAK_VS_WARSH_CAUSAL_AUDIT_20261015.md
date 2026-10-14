# OLAY-02 — 29–30 Ocak 2026: gözlenen pozisyon kırılması ile sonraki Warsh duyurusunu ayrıştırma

**Kapsam:** 20 Ocak 00:00'dan ileri koşunun 29–30 Ocak ilk ciddi yanlışlama vakası. Kapsamlı 22–31 Ocak 960 zaman-slot ham kontrolü: [veri cetveli](OLAY_02_2026_OCAK22_31_960_ASOF_DATA_EVIDENCE_20261015.csv), [10 günlük veri/haber-kapsama raporu](OLAY_02_2026_OCAK22_31_CHRONOLOGY_DATA_QA_20261015.md). 20 ve 21 Ocak kararları geri dönük değiştirilmedi.

**Araştırma kanıt türü:** RETROSPECTIVE_NOT_BLIND_OOS / RESEARCH_ONLY. Belirtilen fiyatlar NEON'daki HistData araştırma kapanışlarıdır; kaynak ilk yayın (firstprint), gerçek banka TRY/ONS makası ve tam zamanlı haber terminali doğrulanmadı. Gerçek işlem YOK. Ocak 2026 eski sonuç/karar defterleri yeniden kullanılmadı.

## 1. 29 Ocak: ana olayın ilk büyük kırılması, henüz Warsh haberi yok
29 Ocak 28 Ocak 22:00 TRT sonrası bilinen Fed FOMC kararı %3,50–3,75 oranını sabit tuttu: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm. Olay kronolojisini bu kaynakla aç; 30 Ocak'taki Fed başkanı haberini daha önceki saatlere ekleme.

| TRT | Tamamlanmış XAU M15 araştırma kapanışı | Yalnız o anda görülebilir kırılma | Hüküm |
|---|---:|---|---|
| 29 Ocak 08:00 | 5557.86 | Çok büyük yükseliş, aşırı pozisyon/kar realizasyonu G06 riski incelenir; kesin düşüş haberi yok | HOLD_GOLD / HOLD_CASH, olay izleme |
| 29 Ocak 10:00 | 5561.07 | Öncesinde gözlenmiş $5.585,56 zirvesine göre çok sınırlı çekilme | Otomatik SAT yok |
| 29 Ocak 18:00 | 5496.05 | Görülmüş zirveden −%1,60. G06 yorulma ADAY | Kesin yön kanıtı yok |
| **29 Ocak 18:15** | **5383.42** | **Görülmüş $5.585,56 zirvesinden −%3,619 ilk büyük kırılma.** Önceki M15 yaklaşık −%2,05 | **SELL_RISK_REVIEW (araştırma alarmı), gerçek emir değil** |
| **29 Ocak 18:30** | **5188.80** | Gözlenmiş tepeye göre −%7,10; son 15 dk −%3,62. G06 likidite/stop zinciri ya da G05 zorunlu satım olası, kanıtlanmış değil | Risk artık ciddi; fiyat hızı ve bankada gecikme özellikle önemli |
| 29 Ocak 18:45 | 5120.72 | −%8,32 tepeye göre. Ex-post düşüşü 18:15 fiyatına geri yazma | Acil çalkantı, yürütülebilir ASK/BID yok |
| 29 Ocak 19:15 | 5272.84 | Önceki dipten hızlı geri sıçrama. Kolay SELL kuralının ters riski | Yalnız tepe-dip tetikleyicisi henüz doğrulanmadı |
| 29 Ocak 23:45 | 5354.15 | Fiyat toparlanmış ama zirve altında | G06 aday devam/yorulma ayrımı açık |

**Haber zaman güvenliği:** Reuters'ın 29 Ocak kâr realizasyonu hakkındaki yayımlanmış güncellenmiş raporu 29 Ocak 13:36 EST = **21:36 TRT** erişilebilir sürümdür. Haber kullanımı ihtiyatla **21:45 TRT** sonrasıdır. 18:15 veya 18:30'da bu metni 'yeni ilk haber' diye göstermek yasaktır. https://www.investing.com/news/economy-news/gold-extends-record-run-races-past-5400oz-4471579

G06-B (kâr alımı), G06-C (ardışık likidite boşluğu), G05-A (zorunlu fonlama satışı) ve ORG10/ORG12 ayırımı: kayıtlardaki hız ve metal eş hareketi **davranış imzası** olabilir; gerçek teminat çağrısı, emir defteri, COT/ETF anlık veri ve yayım saati yokken mekanizmayı nedensel olarak doğrulama. Özellikle 18:30 hızlı düşüşün ardından kısa saatler içinde tepki alımı gerçekleşti: basit %-3 stop/sat sinyali beklenen gelecekteki net düşüşü garanti etmez.

## 2. 30 Ocak: Warsh haberi gelmeden altın zaten çok gerilemişti
| TRT | Tamamlanmış XAU M15 araştırma kapanışı | As-of değerlendirme |
|---|---:|---|
| 30 Ocak 03:00 | 5438.00 | Önceki günün çalkantısı sonrası toparlanma, dalganın bittiği ispatlanmadı |
| 30 Ocak 05:00 | 5300.13 | Yeni düşüş; 29 Ocak zirvesine göre −%5,11, G06/G05 yeniden açılır |
| 30 Ocak 06:00 | 5223.89 | 29 Ocak zirvesinden −%6,48; Warsh duyurusu **henüz yapılmadı** |
| 30 Ocak 09:00 | 5184.04 | 29 Ocak zirvesinden −%7,19; satışın öncesinde fiyat adım adım ilerliyor |
| 30 Ocak 12:00 | 5116.46 | Tepeden −%8,40; tek 14:48 haberiyle açıklanamaz |
| 30 Ocak 14:45 | 5120.64 | Fed başkanlığı ilanından **önceki son tamamlanmış fiyat** |
| **30 Ocak 14:48** | **HABER (fiyat değil)** | Trump'ın Warsh Fed başkan adayı duyurusu **03:48 PST = 14:48 TRT**. Resmî ilk paylaşım arşivi: https://www.presidency.ucsb.edu/documents/truth-social-posts-january-30-2026 |
| 30 Ocak 15:00 | 5135.29 | Haberden sonraki ilk tamamlanmış M15 gözlem; kapanış otomatik SAT fill'i değildir |
| 30 Ocak 20:00 | 4984.47 | Haber sonrası da satım baskısı sürüyor |
| 30 Ocak 21:00 | 4848.90 | Eski zirveden −%13,19; işlem yapılmadı |
| 30 Ocak 23:45 | 4861.11 | Gün sonu, hâlâ 29 Ocak zirvesinin oldukça altında |

**Kırılma yönü ile zaman ayrımı:** Warsh Fed başkanlığı duyurusu 30 Ocak 14:48 TRT'de yapılmıştır. 29 Ocak 18:15 M15'ten başlayan çok büyük düşüş ve 30 Ocak sabahındaki düşüş **bu açıklamadan önce olmuştur**. Bu nedenle tüm Ocak düşüşünü Warsh tek başına 'başlattı' biçiminde kodlamak nedensel hata olur. En az iki durum tanımla: `pre-announcement G06/G05? liquidation hypothesis` ve `post-announcement G01 USD/rates candidate amplifier`. Reuters 30 Ocak 08:14 EST'de (16:14 TRT) yayımlanıp 08:19 EST'de güncellenen altın-gümüş-bakır haberinin değişmiş tam metni ancak 16:30 TRT'den sonra karara girebilir: https://www.investing.com/news/economy-news/gold-silver-and-copper-tumble-as-nervous-investors-discover-gravity-4476024

## 3. Portföy kararı, maliyet ve gerçekleşen kayıp
ANA-01'e göre %0,8 alış + %0,8 satış; fiyat açısından işlem tam döngü eşiği yaklaşık %1,6194 + gerçek spread + gecikme. **Haber olmadan sadece gerçekleşen düşüşü fark ederek SAT yapıldığı iddia edilemez.** RİSK ALARMI (18:15 ilk geçiş) ile işlem emri ayrıdır. Bağımsız kaynağa, gerçek bankaya ve kalan düşüşün kalibre edilen olasılığına dayalı SELL onayı **yoktur**. Resmî Warsh haberinin gelişinden sonra G01/G06 yorumunun gücü artsa da bu, önceki satışın nedeni yapılamaz. Ayrıca çok kısa sürede $5383→$5188 kayışında kaynak kapanış fiyatının bankadan uygulanabilirliği doğrulanamaz.

*Araştırma durumundaki iki başlangıç portföyü*:
- GOLD zaten tutuluyorsa H3/P3 geçişiyle beraber korunması 29–30'ta **çok büyük gerçekleşmemiş kâr erimesi** doğurmuştur; mevcut kapıların yetersizliği bilimsel negatif bulgudur. Bunu yanlışlıkla başarılı SELL olarak skorlamayın.
- CASH tutuluyorsa 20–28 günleri yükseliş fırsatı kaçırılmıştır; 29–30'da sakınılan zarar tesadüfen olumlu olabilir, fakat nihai model başarısı değildir.
- Yalnız **karşılaştırma amacıyla** 20 Ocak 02:15'te 4670.348 (gerçek banka kotasyonu değil) fiyatından satın alıp elde tutmak ve 31 Ocak son geçerli araştırma fiyatı 4860.485 ile zorunlu varsayımsal satmak yaklaşık **%4.071 brüt; 100 başlangıç ve iki kez %0,8 teorik ücret sonrası $102.413** değer verir. Bu, gerçek AL/SAT kararı ya da protokolde baştan ilan edilmiş çıkış değildir, yalnız karşı-olgusal endeks.
- 29 Ocak **$5585.555** gözlenen zirvesinden 30 Ocak 23:45'teki **$4861.11** değerine gerileme **%-12.970**. Zirveden satıldığını varsayarak kâr yazmak yasaktır. Bu aralıkta modelin GERÇEK performansı, verilen emir olmadığı için 'sözde kurtarılan kâr' değildir.

## 4. Hangi bilgi eksik olduğu için güvenilir AL/SAT doğmadı
1. Gerçek zaman damgalı BID/ASK Türk banka kotasyonları ve emri takip eden ilk uygulanabilir fiyata ait kanıt yok.
2. HistData kapanışlarıyla 'Dukascopy direct' serisi 1.643/1.644 ortak Ocak kayıtlarında aynı BID olduğundan birbirini bağımsız doğrulamıyor; m1_match=1 sayısı 0.
3. Gümüş, platin, paladyum, USD, nominal/reel ABD faizi, güvenli liman/teminat mekanizmalarını ayıran aynı-UTC yüksek kaliteli kaynaklar ve resmî firstprint haberi 29 Ocak olayının ilk 15 dakikasında eksik.
4. Var olan ORG10/ORG12/P0–P5 hipotezleri bir **güvenilir bankadan çıkış kuralı** olarak daha önce dev/OOS maliyetli testten geçirilmedi.
5. Alım/satım zamanı geçmişte en iyi tepe-dipten seçilemez. %-3 gözlenmiş düşüş bir **olay araştırma alarmıdır**, otomatik stop veya onaylı satış eşiği değildir.

## 5. Öğrenilecek yanlışlama, fakat ÖĞREN-03'e 'kanıtlandı' yükseltme yok
Olay-02'ye iki tarihli soruyu ekledik: (a) 'önce düşüş sonra Fed adayı haberi' ile (b) 'haber sonrası hızlanma' nasıl ayrılır? ÖĞREN-03'teki ORG10 pozisyon doygunluğu ve ORG12 teminat zinciri birbirinden ayrılmadan tek G06 nedeni ilan edilmez. Ancak kullanıcı hedefi açısından yeni hipotez açık: **hızlı eksi %3 tepe-drawdown + gerçek piyasa çapraz teyidi + maliyeti aşacak kalan zarar analizi** varsayımsal risk denetçisi olarak önceden kaydedilmeli, 2023–2025 ve ayrı test döneminde sınanmalı. Bu koşul sonraki ay sonuçlarına bakılarak başarıya seçilmiş kural olarak 29 Ocak'a uygulanmaz.

**Sonuç:** 29–30 Ocak büyük harekettir; hareketin başlangıcı 30 Ocak 14:48 Warsh haberinden önceydi. Mevcut kanıt standardıyla somut banka SAT kararı doğrulanamadı; araştırmanın önemli başarısızlık modunu açık kaydediyoruz. ANA-01/OLAY-02/ÖĞREN-03 dosyaları değiştirilmedi; bağlantılı tarihli rapor yeni deneme dalına eklendi.
