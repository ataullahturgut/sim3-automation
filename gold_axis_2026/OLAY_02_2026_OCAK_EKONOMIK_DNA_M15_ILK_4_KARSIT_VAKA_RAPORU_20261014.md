# OLAY-02 — 15 dakikalık ekonomik DNA araştırması: İlk dört haber vakasının karşılaştırması

**Statü:** FIRST_4_CASES_REVIEWED / 2976_SLOT_TIME_SPINE_BUILT / NOT_FULL_DECISION_REPLAY / NO_PNL. Araştırmacı Ocak sonuçlarını daha önce gördüğü için bağımsız kör test değildir. Bu belge tarihli vaka kanıtıdır, yeni ana manifest değildir.

**Saat sözleşmesi:** Haber anı t'deki XAU fiyatı, t-15 → t arasında TAMAMLANAN M15 barının kapanışıdır. +15dk ilk tam haber-sonrası bar, +60dk sonraki ilk saat gözlemidir. ZN/NQ/SI/CL futures H1 barları başlangıçta değil **tamamlanınca** görünür. **Yeni bir H1 barı gelmediyse önceki fiyatın tekrar görünmesi yüzde sıfır piyasa tepkisi değildir; tabloda — ile gösterilir.** Haber-sonrası t+60/t+240 sonucu t anındaki karar için kullanılamaz.

| Haber / ilk yayın | Türkiye saati | XAU +15dk | XAU +60dk | ZN future +60dk | SI future +60dk | Sınıflandırma |
|---|---|---:|---:|---:|---:|---|
| Venezuela olayını anlatan Reuters **ilk piyasa raporu** (ilk siyasi haber değil) | 5 Ocak 07:00 | +%0,004 | +%0,097 | +%0,028 | — | ORG04 ADAY |
| BLS Aralık NFP / işsizlik | 9 Ocak 16:30 | +%0,320 | +%0,486 | +%0,056 | +%0,206 | G01-A ve G01-B rekabeti; desteklenen tepki |
| BLS Aralık CPI | 13 Ocak 16:30 | +%0,380 | +%0,390 | +%0,084 | +%2,033 | G01-A desteklenen tepki |
| Fed FOMC statement | 28 Ocak 22:00 | +%0,336 | +%0,869 | +%0,056 | — | G01-X / ORG09 ADAY; sürpriz belirsiz |

[Aynı olayların -60, 0, +15, +30, +60, +120, +240 dakika karşılaştırma CSV'si](OLAY_02_2026_OCAK_DORT_ILK_HABER_M15_KARSIT_AKTARIM_DENETIMI_20261014.csv).

## OLAY A — Venezuela: farklı haberin ilk yayınını asıl olayın başlangıcı sanma

Müdahale hafta sonunda yaşanmıştı; Reuters piyasa haberi sendikasyonunun **5 Ocak 04:00 UTC** timestamp'i müdahalenin orijinal ilk haberi değildir. 04:00 XAU 4.399,615, 04:15 XAU 4.399,785 ve 05:00 XAU 4.403,865. H1'de ZN +%0,028, NQ +%0,092, CL -%0,070; tam bir küresel risk-off kanıtı değil. Güvenlik primi ORG04 araştırma adayıdır, ilk tetikleyici ve kalan ekonomik hareket kanıtı bulunmamıştır.

Kaynak: https://www.marketscreener.com/news/gold-surges-as-us-capture-of-venezuela-president-spurs-safe-haven-demand-ce7e59d9d08df026

## OLAY B — İstihdam: açıklamanın alt bileşenleri zıt

BLS açıklama saati **9 Ocak 13:30 UTC**. NFP +50 bin, Reuters erken piyasa beklentisi +60 bin (güvercin yönde); işsizlik %4,4, beklenti %4,5 (şahin yönde). G01-A ve G01-B tek taraflı seçilmez. Ön haber XAU 4.472,235, ilk +15dk 4.486,548, +60dk 4.493,955. ZN futures +%0,056, SI +%0,206, NQ +%0,217: mekanizma adayının P2 piyasalar arası aktarım yönüyle tutarlıdır; gerçek ABD 2Y/DXY yok, kesin neden değildir.

**As-of karar çizgisi:** 16:30 TRT'de +15dk bar henüz yoktur; ilk M15 teyidi 16:45, ilk haber-sonrası tam H1 çapraz gösterim 17:00 TRT. DESTEKLENEN as-of tepki hipotezi olabilir, ama beklenen **kalan** hareketin ücret + BID/ASK'ı aşacağı bağımsız kaynakla kalibre edilmeden yürütülebilir AL sonucu çıkarılamaz.

Kaynak: https://www.bls.gov/news.release/archives/empsit_01092026.htm

## OLAY C — CPI: yumuşak çekirdek veri, farklı güçte metal kanalları

BLS özgün **13 Ocak 13:30 UTC** CPI raporunda çekirdek aylık %0,2; önceki gün Reuters anketinde %0,3 beklenmişti. Manşet aylık %0,3, yıllık %2,7. 13:30 XAU 4.600,155 → 13:45 4.617,615 (+%0,380), 14:30 4.618,118 (+%0,390). ZN H1 +%0,084; SI H1 +%2,033; NQ H1 +%0,293. G01-A fırsat maliyeti gevşemesi **DESTEKLENEN ekonomik tepki adayı**, fakat aynı anda gümüşün çok güçlü tepki vermesi genel metal/pozisyon hareketini rakip bırakır. USD ve piyasa-implied Fed faiz patikası eksik; P3/P4/P5 onaylanmaz. Kalan getiri maliyet kıyasından önce AL yok.

Kaynaklar: https://www.bls.gov/news.release/archives/cpi_01132026.htm ve https://www.reuters.com/world/us/us-consumer-prices-likely-snapped-back-after-being-restrained-by-government-2026-01-13/

## OLAY D — Fed: ilan saatinde altın yükseldi ama Fed şoku ölçülmedi

FOMC **28 Ocak 19:00 UTC** faiz aralığını %3,50–%3,75'te tuttu. Gerçek patika sürprizi ölçülmedi. Açıklamadan önceki XAU 5.279,248 → 19:15 5.296,988 (+%0,336), 20:00 5.325,105 (+%0,869), ZN futures +%0,056, NQ -%0,041; **SI için +60dk öncesinde yeni H1 barı tamamlanmadığından yön ölçülemedi**. Daha geniş altın talep/pozisyon trendi ayrı rakip ORG09'dur. Bu dalganın tamamını Fed'in beklenmeyen parasal sıkılaştırması/gevşemesi diye tanımlamak hatalı. Canlı kararın gerekçesi için politika yolunun **beklentiden farkı**, önceki evre ve gerçek USD/faiz kanalının zaman sırası gerekir.

Kaynak: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm

## Kritik kaynak bağımsızlık ve 1 dakikalık teyit uyarısı

Neon SQL'de **1.642/1.642** HistData OHLC çubuğunun dört OHLC değeri de Duka BID OHLC ile **tamamen eşit**. İki bağımsız fiyat kaynağı diye double-count yasaktır; veri türetme kökü henüz doğrulanmamıştır. Spot MID/BID farkını farklı sağlayıcı uyumu sayma. Duka ASK/BID yalnız teorik quote vekilidir. Twelve Data 1m cache'i üç resmi haberden sonraki ilk 16 dakikada 16 gözlem taşıyor, ama cache ilk-bar zamanı/fiyatı spot M15 sağlayıcıyla aynı değildir; 1m canlı emir kaynağı olmadığı ve hafta sonu kayıtları görüldüğü için bağımsız QA olmadan işlem fill'i üretme.

[Ana 2.976 adet Türkiye saati kontrol noktası](OLAY_02_2026_OCAK_2976_M15_ASOF_ZAMAN_OMURGASI_20261014.csv). Buradaki **position_decision = NO_DECISION_EVIDENCE_SPINE**; bu, bütün günlerde ekonomik AL/SAT/TUT deneyi tamamlandı demek **DEĞİLDİR**.

## Araştırmanın mevcut sınırı

İlk dört vakada haber saatleri, altın ilk M15 tepkisi, mevcut H1 diğer varlıklar ve karşıt nedenler denetlendi. İlgili yılın diğer bütün saatli olayları, gerçek haber firstprint'i ve karar altında beklenen kalan % hareketin 2023–2025 kaynaklı kalibrasyonu **tamamlanmadı**. Bu aşamada 100 USD'lik portföy performansı sunmak metodolojik olarak yanlış; olay sonucu / ekonomik çıkarım / karar / gerçekleşebilir işlem **ayrı kayıtlardır**. ANA-01 önce 15m kronolojiyi zorunlu tutuyor; OLAY-02 tarihli kanıt, ÖĞREN-03 tarihsiz DNA kaynağı olmaya devam ediyor.
