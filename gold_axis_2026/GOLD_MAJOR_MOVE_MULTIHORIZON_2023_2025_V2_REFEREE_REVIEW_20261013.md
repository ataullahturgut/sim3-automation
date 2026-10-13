# BAĞIMSIZ HAKEM DEĞERLENDİRMESİ — XAU/USD 2023–2025 ÇOK UFUKLU HAREKET VE OLAY ATLASI V2

**Tarih:** 2026-10-13 · **Hakem:** Claude (bağımsız inceleme; mevcut V2 dosyalarının hiçbiri değiştirilmedi)
**İncelenen:** `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_SCIENTIFIC_FINDINGS_20261013.md`, dört V2 CSV'si, V1 atlas + verdict, `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` içindeki V2 kaydı.
**Tür:** Tarihsel olay/neden denetimi. Model, sinyal veya al-sat kuralı **yoktur**.

**Bu incelemenin ekleri**
| Dosya | İçerik |
|---|---|
| `..._V2_REFEREE_53_CLUSTER_AUDIT_20261013.csv` | 53 kümenin her biri için: gerçek pencere başlangıcı, düzeltilmiş kaynak zamanlaması, volatiliteye göre büyüklük, GC/SI/ZN/NQ/CL hareketi, hazırlık koşulu, tetikleyici, büyütücü, karşıt kanıt, tarihli kaynaklar, hakem kararı |
| `..._V2_REFEREE_MISSED_AND_NONEVENT_CONTROLS_20261013.csv` | Atlanan hareketler ve "aynı işaret vardı, büyük hareket olmadı" kontrol olayları |
| `..._V2_REFEREE_RECOMPUTED_CLUSTER_TIMING_20261013.csv` | Betikten üretilen zamanlama/volatilite tablosu |
| `..._V2_REFEREE_REPRODUCE_20261013.py` | Bu rapordaki fiyat türevli tüm sayıları yalnız commit edilmiş V2 CSV'lerinden yeniden üretir |
| `..._V2_REFEREE_CROSSMARKET_20261013.sql` | Neon CME saatlik verisinden çapraz piyasa hesaplaması (salt okuma) |

---

## 0. Hakem hükmü (özet)

1. **Fiyat taraması teknik olarak doğru ve yeniden üretilebilir.** 151 birincil gün, 23 ikincil gün, 53 küme, 152 işaretli yön satırı ve 1 saatlik ufukta sıfır bayrak birebir yeniden üretildi; bayrak dizelerinde 0 uyumsuzluk var. Eksik 9 hafta içi gün yalnızca tatiller (1 Oca, Kutsal Cuma, 25 Ara).
2. **Ancak "151 önemli hareket günü" ve "53 olay" bilimsel olarak *olay sayısı* değildir.** 152 yön-bayrağının 124'ünü 5 seanslık, 63'ünü 3 seanslık **örtüşen** pencereler üretiyor; yalnız 9'u 1 günlük, 17'si gün içi (4h/12h). Tek bir sert gün, sonraki 4 seansı da bayraklıyor.
3. **Yıllar arası artış (24 → 48 → 79) büyük ölçüde sabit %3 eşiğinin volatilite ve fiyat rejimi değişimine duyarlılığından kaynaklanıyor.** %3, 2023'te 3.6σ, 2025'te 2.5σ günlük hareket demek. Volatiliteye göre ölçeklenmiş 5 seanslık ölçüt (|z5|≥2) ile sayılar 19 / 21 / 24 — neredeyse sabit. 53 kümenin **24'ü** volatiliteye göre ölçeklenince büyük değil ("eşik artefaktı adayı").
4. **Kaynak zamanlaması (PRE/DURING/POST) sistematik olarak yanlı.** Etiketler "ilk bayrak günü"ne göre verilmiş; oysa bayrak, hareketin *bitiş* ucunda oluşur. 53 kümenin 46'sında gerçek pencere başlangıcı ilk bayraktan ≥3 takvim günü önce (medyan 7 gün). V2'deki **3 "PRE" etiketinin 2'si (C023, C030) gerçekte DURING**. Yalnız C048 (WGC 13 Eki 2025 notu) gerçekten hareketten öncedir.
5. **Makro takvim analizi yanlış ölçütle yapılmış.** Yayın günü karşılaştırması örtüşen 3/5 seanslık bayraklara dayanıyor ve FOMC'yi dışarıda bırakıyor. Aynı gün |z| ile ölçülünce: **FOMC günlerinde |z|≥2 olasılığı %26.7 (4/15), diğer günlerde %6.9 (Fisher p=0.019, çoklu test düzeltmesi öncesi)**; NFP %12.5 (anlamsız), TÜFE %3.1. Çekirdek TÜFE sürprizi ile aynı gün altın getirisi korelasyonu −0.61 (n=34; 19 sıfırdan farklı sürpriz).
6. **V2'nin "kaynaksız" bıraktığı 25 kümenin 22'si için tarihli, eşzamanlı haber kaynağı bulundu** (ayrıntı denetim CSV'sinde). Bunların hiçbiri nedensellik kanıtı değildir; hepsi eşzamanlı anlatıdır.
7. **Önemli atlanmış olaylar var:** 2–5 Ağustos 2024 küresel carry çözülmesi (5 Ağu gün içi %4.0 aralık, hiçbir kümede değil) ve Ocak 2025'teki +%6'lık tarife/EFP kaynaklı fiziki altın kayması (20 seanslık pencerede hiçbir kümeyle örtüşmüyor).
8. **En güçlü yeni bulgu (hipotez):** Düşüş kümelerinden önce fiyat belirgin şekilde gergin — önceki ~4 haftadaki altın getirisinin medyanı DOWN kümelerde **+%5.6**, UP kümelerde **+%0.85**. Ama aynı gerginlik, sonraki 10 seansta ≥%3 *yükselişle* de eşit veya daha sık sonuçlanıyor. **Gerginlik yönü değil, iki yönlü kırılganlığı işaret ediyor.**

---

## 1. Yöntem ve veri kapsamı

**Yeniden üretim:** V2'nin `ALL_774_DAYS` CSV'sindeki ham alanlardan bayraklar, kümeleme (≤3 uygun seans boşluk, yön bazında) ve yıl sayıları bağımsız kodla yeniden hesaplandı (`REPRODUCE.py` §1–2).

**Bağımsız çapraz piyasa verisi:** Neon `gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c` içinde GC (altın), SI (gümüş), ZN (10Y T-note, fiyat ↑ = faiz ↓), NQ (Nasdaq-100), CL (ham petrol) saatlik barları. Günlük kapanış = NY17 seans etiketinin son saatlik barı. **Sınırlamalar:** `.c.0` takvim rulolu sürekli kontrat, rulo boşlukları düzeltilmedi; son bar çoğunlukla ~15:00–16:00 ET, XAU'nun 17:00 kapanışıyla birebir hizalı değil. GC'nin küme penceresindeki işareti 53/53 kümede XAU yönüyle aynı — fiyat kaynağı yön açısından sağlam.

**Makro sürprizler:** Neon `observations` içindeki `MACRO_*_ACTUAL_FIRST_PRINT` (BLS/ALFRED ilk açıklama) ve `MACRO_*_CONSENSUS_PIT` (Investing.com, araştırma amaçlı). FOMC sürpriz serileri (USMPD) 2023–25 için `available_as_of` alanında dönmedi; FOMC yalnız tarih olarak kullanıldı ve V2 defterinde **yalnız 16 FOMC günü** var (3 yılda 24 toplantı olmalı) — defter eksik.

**Erişilemeyen veriler (bu oturumda):** Dolar endeksi/DXY, reel faiz (TIPS), günlük ETF akımları, CFTC COT ham verisi, FedWatch arşivi. Kabuk ağ erişimi FRED/CFTC/Yahoo'ya kapalı. Bu kanallar için yalnız tarihli ikincil kaynaklar (WGC, Reuters/Kitco) kullanıldı ve **nicel test yapılmadı**. Bunu bir eksik olarak kayda geçiriyorum, sonuç uydurmuyorum.

**Haber kaynakları:** Her küme için tarihli eşzamanlı haber (çoğunlukla Reuters'ın Kitco "off-the-wire" kopyaları, URL'de yayın tarihi var) ve WGC raporları. Kaynak tarihi, gerçek pencere başlangıcına göre PRE/DURING/POST olarak yeniden sınıflandı.

---

## 2. Veri ve tanım denetimi — somut bulgular

### 2.1 Doğrulanan noktalar
- 774 geçerli gün (257/259/258), 151 birincil + 23 ikincil = 174, 53 küme (33 UP, 20 DOWN), 1h ufkunda 0 bayrak: **doğru**.
- Birleştirme boşluğu duyarlılığı: boşluk 1 → 66 küme, 2 → 59, 3 → 53, 5 → 50. Yani "53" sayısı keyfi bir parametreye ±%25 duyarlı; raporda belirtilmeli.

### 2.2 Bayrak ufku dağılımı (yön-bayrak sayısı, UP/DOWN)
| Ufuk | 1h | 4h | 12h | 1 seans | 3 seans | 5 seans |
|---|---:|---:|---:|---:|---:|---:|
| UP | 0 | 0 | 3 | 4 | 43 | 94 |
| DOWN | 0 | 4 | 10 | 5 | 20 | 30 |

**Sonuç:** Atlas esas olarak bir "5 günlük trend" atlasıdır, "şok" atlası değildir. UP/DOWN dengesizliği (33/20) üç yılda fiyatın 1,839.7$'dan 4,315.0$'a (+%134.5) çıkmasıyla uyumlu; sabit eşik trend yönündeki sürüklenmeyi aşırı sayar.

### 2.3 Volatilite rejimi
| Yıl | Günlük σ | %3 kaç σ | 5 seans |getiri|≥%3 | |z5|≥2 (ölçekli) |
|---|---:|---:|---:|---:|
| 2023 | 0.822% | 3.6 | 22 | 19 |
| 2024 | 0.942% | 3.2 | 40 | 21 |
| 2025 | 1.190% | 2.5 | 62 | 24 |

Ölçekli tanımla yıllık "olay" sayısı neredeyse sabit. "2025'te daha çok önemli olay oldu" iddiası, **aynı mutlak eşikle** ölçülünce doğru, **göreli şok** olarak ölçülünce büyük ölçüde yanlış. İki tanım da meşrudur ama raporda ikisi ayrıştırılmalı.

### 2.4 Başlangıç tarihi yanlılığı
"İlk bayrak günü" (V2'de `start`) 3/5 seans geriye bakan bir pencerenin **son** günüdür. Gerçek hareket, en geç pencere başlangıcında (t−3 veya t−5) başlamıştır. 46/53 kümede bu fark ≥3 takvim günü. Somut sonuçlar:
- **C023:** V2 "PRE" (kaynak 19 Eyl 2024). Pencere 17 Eyl'de başlıyor → **DURING**. Fed'in 18 Eyl kararı hareketin içinde.
- **C030:** V2 "PRE" (kaynak 4 Şub 2025). Pencere 29 Oca'da başlıyor → **DURING**. Üstelik asıl öncül (tarife/EFP kaynaklı fiziki akış) 17 Ocak'tan beri haberdeydi.
- **C045:** Pencere 25 Ağu 2025'te başlıyor; bu, Trump'ın Fed Guvernörü Cook'u görevden alma girişiminin duyurulduğu gece ([Kitco, 26 Ağu 2025](https://www.kitco.com/news/article/2025-08-26/trumps-firing-fed-governor-cook-roils-markets-and-capitol-hill-boosts-gold)). V2 bu tetikleyiciyi hiç anmıyor.
- **C003:** Pencere 6 Mar 2023'te başlıyor; 7–8 Mart'taki şahin Powell ifadesi ve ardından 10 Mart SVB, 15–19 Mart Credit Suisse — iki ayrı bankacılık tetikleyicisi tek kümede.

### 2.5 Kaynak–küme yön uyumsuzluğu
- **C013 (12 Nis 2024, DOWN):** V2 kaynağı "rekor zirve, güvenli liman talebi" başlıklı. Küme ise rekor sonrası gün içi ~%3.6 düşüş. Mekanizma "patlama ve geri dönüş"; kaynak yükselişi açıklıyor. Etiket düzeltilmeli.
- **C005:** V2'nin eşleştirdiği kaynak Ağustos ve Ekim WGC yorumları. Asıl eşzamanlı mekanizma 20 Eyl 2023 FOMC "uzun süre yüksek" mesajı ve 10Y faizin 16 yılın zirvesine çıkması; ZN penceresi −%2.0 ile tutarlı.

### 2.6 Makro takvim analizi
V2 §4'teki "68 yayın günü / %22.1 vs %19.3" karşılaştırması, örtüşen 3/5 seanslık bayrakları kullandığı için yayın gününü değil **önceki haftayı** ölçüyor. Aynı gün |z| (önceki 60 günlük σ'ya göre) ile:

| Gün tipi | n | ort. |z| | P(|z|≥2) | P(gün içi aralık≥%2.5) |
|---|---:|---:|---:|---:|
| TÜFE | 32 | 0.77 | 0.031 | 0.029 |
| NFP | 32 | 0.97 | 0.125 | 0.176 |
| **FOMC** | 15 | 1.07 | **0.267** | 0.188 |
| Yayınsız | 655 | 0.80 | 0.069 | 0.074 |

**Sürprizlerin yönü tutarlı, büyüklüğü küçük:** Çekirdek TÜFE sürprizi ile aynı gün altın getirisi korelasyonu −0.61, sıfırdan farklı sürprizlerin %79'unda altın ters yönde hareket etti. NFP için korelasyon −0.36 ve yıla göre kararsız (2024'te ters işaret payı yalnız %33). Sıfırdan farklı sürpriz günlerinde ortalama |z| ≈ 0.95–0.97 — yani tipik bir veri sürprizi **1σ civarında** hareket yaratıyor, tek başına %3 için yetersiz.

**Veri boşluğu:** 2025 Ekim NFP ve TÜFE iptal edildi ([BLS kararı, Bloomberg Law](https://news.bloomberglaw.com/us-law-week/bls-axes-us-october-cpi-report-sets-dec-18-for-november-data)). C047–C049 dönemi "resmi veri karartması" altında geçti; bu kendi başına incelenmesi gereken bir koşul.

### 2.7 Kaynak vintajı sorunu
WGC 2024 merkez bankası alımını 5 Şub 2025'te **1,044.6t** olarak yayımladı ([WGC GDT FY2024](https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2024)); 29 Oca 2026 raporunda aynı yıl **1,092.4t** olarak revize edildi ([WGC GDT FY2025](https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025)). Atlas "o gün bilinen" ile "sonradan bilinen"i ayırmak istiyorsa, MB/ETF rakamları da yayın vintajıyla tutulmalı.

### 2.8 Pozisyon verisi gerçek zamanlı yoktu
CFTC COT yayını 2025 kapanması nedeniyle 3 Ekim'den itibaren durdu; 30 Eyl tarihli rapor 19 Kas'ta, 21 Eki tarihli rapor 2 Ara'da yayınlandı ([CFTC takvimi, Mondo Visione 18 Kas 2025](https://mondovisione.com/media-and-resources/news/cftc-to-resume-publishing-cot-reports-wednesday-the-agency-also-announced-a-c-20251118/)). **Ekim 2025 düşüşünden önceki spekülatif pozisyon, düşüş anında piyasaya görünmüyordu.** Bu dönem için COT'a dayanan her "öncü işaret" iddiası ex-post'tur.

### 2.9 WGC 13 Ekim 2025 notunun eksik aktarımı
V2 notu yalnız uyarı yönüyle aktarıyor. Asıl metin ([WGC, 13 Eki 2025](https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point)) RSI>90 ve 200 günlük ortalamanın %20+ üstünü kısa vadeli kırılganlık olarak işaretliyor. Ama **aynı not ETF ve COMEX pozisyon birikiminin önceki dalgaların yalnız %30–40'ı olduğunu, yani pozisyonun aşırı olmadığını** da söylüyor ve düzeltme öngörmüyor. Ayrıca bu notta kullanılan COMEX pozisyon rakamları, CFTC yayınının durduğu dönemde veriliyor; kaynağı doğrulanmalı.

---

## 3. Atlanan veya yanlış birleştirilen hareketler

**Atlanan (ayrıntı: `MISSED_AND_NONEVENT_CONTROLS` CSV):**
- **2–5 Ağu 2024 küresel carry çözülmesi:** 2 Ağu aralık %2.77, 5 Ağu aralık %4.00, hiçbir küme penceresinde değil ([Kitco, 2 Ağu 2024](https://www.kitco.com/news/article/2024-08-02/gold-price-drops-below-unchanged-heavy-profit-taking-weak-long-liquidation)). Likidite mekanizmasının en temiz örneklerinden biri atlasta yok.
- **Ocak 2025 tarife/EFP rallisi:** 28 Oca'da biten 20 seanslık +%6.0 hareket hiçbir kümeyle örtüşmüyor; CME depo stoklarındaki sıçrama 17 Ocak'tan itibaren raporlandı ([Kitco/Reuters, 17 Oca 2025](https://www.kitco.com/news/off-the-wire/2025-01-17/cme-precious-metals-stocks-soar-trump-tariff-threat)).
- Küme dışında kalan gün içi büyük aralık günleri: 2023-04-14, 2023-05-05 (rekor sonrası NFP geri dönüşü), 2024-03-21, 2024-04-15 (İran saldırısı sonrası ilk seans), 2025-05-29, 2025-06-02, 2025-10-30.
- **Ufuk kör noktası:** Mayıs–Ekim 2023'teki ~%12'lik yavaş düşüşün yalnız son ayağı (C005) yakalandı. ≤5 seans pencereleri yavaş rejim değişimlerini göremez; 10/20 seanslık ufuk ve volatiliteye göre ölçeklenmiş eşik eklenmeli.
- Volatiliteye göre büyük olup bayraklanmayan günler: 2023-09-27 (z −2.5), 2023-10-09 (z +3.0, saldırı sonrası ilk seans), 2023-12-13 (z +2.7, FOMC), 2024-03-01 (z +3.0), **2024-04-22 (z −3.4, iki yılın en büyük günlük düşüşü — yalnız C014'ün 3 seanslık penceresine dolaylı giriyor)**, 2024-04-30 (z −2.6).

**Yanlış veya sorunlu birleştirmeler:**
- **C003:** SVB (10 Mar) ve Credit Suisse (15–19 Mar) iki ayrı tetikleyici.
- **C034 (9–22 Nis 2025):** Erteleme sonrası toparlanma, ABD–Çin tırmanması ve Fed bağımsızlığı saldırıları üç ayrı alt olay.
- **C047 (1–20 Eki 2025, 13 bayraklı gün):** Fed indirimi devamı, kapanma, ETF/gümüş köpüğü.
- **C038/C039 ve C047/C048:** Zıt yönlü kümeler aynı günleri paylaşıyor; C039 bağımsız olay olarak sayılmamalı.
- **C007/C008/C009 (1–8 Ara 2023):** Aynı "rekor–spike–geri dönüş" fiyat yolu üç kümeye bölünmüş.

---

## 4. Olay zincirleri: önceden bilinebilen ile sonradan açıklanan

Her küme için ayrıntı denetim CSV'sindedir. Aşağıda tekrar eden zincirler, her biri için **ex-ante** (hareketten önce yayımlanmış/bilinebilir) ve **ex-post** (hareket sırasında/sonrasında ortaya çıkan) ayrımıyla özetlendi.

### Zincir A — Faiz/Fed yeniden fiyatlaması (klasik kanal)
*Örnekler:* C001, C002, C005, C010, C016, C022–C023, C029, C043, C050.
- **Ex-ante:** Toplantı ve veri tarihleri; bazen beklenti kayması önceden haberde (C029: "slower cuts" beklentisi 17 Ara 2024'te yazıldı, [Kitco](https://www.kitco.com/news/off-the-wire/2024-12-17/gold-retreats-traders-see-slower-fed-rate-cuts-2025); C022: 13 Eyl 2024 50bp tartışması).
- **Ex-post:** Kararın/verinin büyüklüğü (C029'daki 2025 için 2 indirim nokta grafiği, [Kitco, 19 Ara 2024](https://www.kitco.com/news/article/2024-12-19/gold-silver-pounded-feds-hawkish-pivot)).
- **Kanıt:** ZN penceresi 53 kümenin yalnız 35'inde altınla "beklenen" yönde. Faiz kanalı tekrar eden ama **baskın olmayan** bir zincir.

### Zincir B — Gerginlik + tetikleyicinin geri alınması/yumuşama → sert düşüş
*Örnekler:* C014 (19 Nis 2024 İsrail sınırlı misillemesi), C027 (Bessent + ateşkes), C035 (22 Nis 2025 Trump'ın Powell'ı görevden almayacağını söylemesi), C038 (12 May 2025 Cenevre ateşkesi), 24 Haz 2025 İran ateşkesi.
- **Ex-ante:** Fiyatın gerginliği (önceki 4 haftada C014 +%10.9, C035 +%11.3, C038 +%14.9 GC).
- **Ex-post:** Yumuşamanın kendisi.
- **Gözlem:** Tırmanma haberleri çoğu zaman 1σ civarında yükseliş üretirken (1 Eki 2024 +%1.0; 13 Haz 2025 +%1.4; 23 Haz 2025 +%0.1), **yumuşama haberleri daha büyük düşüşler** üretti (22 Nis 2024 z −3.4). *Hipotez:* Jeopolitik prim kademeli birikiyor, tek seferde çıkıyor.

### Zincir C — Jeopolitik şok × kalabalık kısa pozisyon
*Örnek:* C006 (Ekim 2023). WGC, yönetilen fonların net kısasının 10 Eki itibarıyla z=−2 olduğunu ve Ekim'de −87t kısa kapama yaşandığını raporladı; ETF'lerden ise çıkış sürdü ([WGC, 7 Kas 2023](https://gold.org/goldhub/research/gold-market-commentary-october-2023)).
- **Ex-ante:** Kısa pozisyonun aşırılığı (CFTC ~3 gün gecikmeli, kısmen bilinebilir).
- **Ex-post:** 7 Ekim saldırısı (öngörülemez), kısa kapamanın büyüklüğü.
- **Karşıt:** Diğer büyük jeopolitik şoklar kalabalık kısa olmadan küçük kaldı (bkz. §5). *Hipotez:* Jeopolitik etki pozisyona koşullu.

### Zincir D — Likidite / teminat şoku: altın riskli varlıklarla birlikte düşer
*Örnekler:* C019 (Tem 2024, NQ −%4.5, CL −%4.9), atlanmış 5 Ağu 2024, C033 (3–8 Nis 2025: CL −%18, NQ −%11.4, SI −%13.7), C053 (Ara 2025 CME teminat artışları, gümüş −%9).
- **Ex-ante:** Çoğunlukla önceki gerginlik (C033 önceki 4 hafta +%8.4; C053'te RSI≥75 ve 200g ortalamanın %20+ üstü). Teminat artışları duyuru ile yürürlük arasında kısa süre bilinir ([Kitco, 29 Ara 2025](https://www.kitco.com/opinion/2025-12-29/precious-metals-retreat-record-highs-amid-profit-taking-and-margin-increases)).
- **Ex-post:** Likidasyonun boyutu.
- **Sonuç:** "Güvenli liman" işareti likidite rejimine göre tersine dönüyor; V2'nin tarife örneğindeki tespiti genelleşiyor.

### Zincir E — Kurumsal/mali güven kanalı (2025'e özgü)
*Örnekler:* C034 (17–22 Nis 2025 Powell'a saldırılar, [FXStreet, 21 Nis 2025](https://www.fxstreet.com/news/gold-price-explores-past-3-400-as-trump-powell-clash-sparks-fed-independence-fears-202504211649)), C045 (25 Ağu 2025 Cook), C047 (1 Eki kapanma, [AA](https://www.aa.com.tr/en/economy/gold-prices-hit-new-record-level-amid-us-government-shutdown/3704020)).
- **Kritik gözlem:** C034'te ZN −%1.9 (faiz **yükseldi**) iken altın +%10.9. Bu, reel faiz kanalının tersi; tahvil ve dolar birlikte zayıflarken altın yükseliyor.
- **Ex-ante:** Siyasi açıklamalar hareketle eşzamanlı; önceden bilinebilir olan yalnız kurumsal gerilimin varlığı.
- **Durum:** Güçlü *hipotez*; dolar endeksi, vade primi ve CDS verisiyle test edilmeli.

### Zincir F — Fiziki arbitraj / tarife kaynaklı lokasyon kayması
*Örnekler:* Atlanmış Ocak 2025 rallisi → C030, C032 (31 Mar 2025 COMEX stok rekorları, [Kitco/Reuters](https://www.kitco.com/news/off-the-wire/2025-03-31/gold-stocks-comex-warehouses-track-hit-new-records-over-coming-days)), muhtemelen C044 (Ağustos 2025 İsviçre külçesi tarife yorumu — *doğrulanmalı*).
- **Ex-ante:** Tarife tehditleri ve COMEX/Londra primleri gerçek zamanlı görülebilirdi.
- **Not:** Bu mekanizma V2'de neredeyse tamamen yok.

### Zincir G — Resmi talep (merkez bankası) bilgisi
*Örnekler:* C017 (15 May 2024 WGC: PBoC Nisan alımı 2t'ye düştü → 7 Haz durdurma), C028 (7 Ara 2024 PBoC alımlara dönüş, [Kitco/Reuters, 9 Ara 2024](https://www.kitco.com/news/off-the-wire/2024-12-09/chinas-central-bank-resumes-gold-purchases-after-six-month-hiatus)).
- **Yapısal arka plan:** MB alımları 2023'te 1,050.8t, 2024'te 1,044.6t (Şub 2025 vintajı); aynı yıllarda ETF akımları −244.2t ve −6.8t. 2025'te ETF'ler +801.2t, MB 863.3t ([WGC FY2025](https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025)). *Hipotez:* 2023–24 yükselişlerinin marjinal alıcısı resmi/Asya talebi, 2025'inki ise Batı yatırım akımıydı; bu kayma 2025'teki iki yönlü volatilite artışıyla tutarlı.

### Zincir H — Gümüş liderliği ve köpük
- Gümüş 53 kümenin 46'sında altınla aynı yönde, medyan büyüklük oranı UP'ta 1.14, DOWN'da 1.55.
- C048 öncesi gümüş önceki 4 haftada +%27.3, C053 öncesi +%38.2. *Hipotez:* Gümüşün altından çok daha hızlı yükselmesi, değerli metal kompleksindeki kaldıraçlı köpüğün öncül işareti olabilir. n çok küçük.

---

## 5. Aynı işaretler vardı, büyük hareket olmadı (karşı-olgular)

**Gerginlik ölçütlerinin taban oranlarına etkisi** (2023–25, 744 gün; "runs" = bağımsız dönem sayısı):

| Koşul (karar gününde bilinir) | gün | dönem | P(10 seansta ≥%3 düşüş) | P(10 seansta ≥%3 yükseliş) |
|---|---:|---:|---:|---:|
| Taban | 744 | — | 0.109 | 0.382 |
| 20 seans getirisi ≥%5 | 180 | 21 | 0.189 | 0.428 |
| 20 seans getirisi ≥%8 | 74 | 13 | 0.284 | 0.446 |
| RSI14 ≥70 | 114 | 21 | 0.211 | 0.430 |
| 50g ortalamanın ≥%8 üstü | 52 | 7 | 0.365 | 0.500 |
| 20 seans getirisi ≤−%3 | 60 | 15 | 0.017 | 0.467 |

**Yorum:** Gerginlik düşüş riskini 2–3 katına çıkarıyor ama gergin günlerin %64–81'inde ≥%3 düşüş gelmiyor ve yükseliş olasılığı da en az aynı kalıyor. Bağımsız dönem sayısı 7–21; güven aralıkları geniş.

**"Aşırı gerginlik" (RSI≥75 ve 200g ortalamanın %20+ üstü):** 2023–25'te yalnız **üç dönemde** görüldü (Nis 2025, 29 Eyl–20 Eki 2025, 22–26 Ara 2025). Üçünün ardından da 0–15 seans içinde ≥%3 düşüş geldi (C035/C036, C048, C053). Ancak 30 Eyl–8 Eki 2025 arasında koşul her gün sağlandığı halde fiyat 20 Ekim'e kadar **%13 daha yükseldi**. **3/3 isabet, n=3 ve belirsiz zamanlama — bu bir sinyal değil, kırılganlık durumudur.** Bizim RSI hesabımız 90'a hiç ulaşmadı; WGC'nin RSI>90 ifadesi farklı veri/hesaplama kullanıyor olabilir.

**Büyük veri sürprizi, küçük tepki:** 6 Eki 2023 NFP +166k sürpriz → altın +%0.65; 2 Şub 2024 +166k → −%0.83; 4 Eki 2024 +107k → −%0.18. 2024'teki üç sıcak çekirdek TÜFE (+0.1) yalnız −%0.9 ile −%1.35 arası düşüş üretti ve Mart–Nisan 2024 rallisi devam etti.

**Büyük jeopolitik şok, küçük tepki:** 1 Eki 2024 İran füze saldırısı +%1.04 ([Kitco](https://www.kitco.com/news/article/2024-10-01/gold-silver-rally-reports-iran-poised-attack-israel)); 13 Haz 2025 İsrail'in İran'a saldırısı günü +%1.40 (C041 ancak 3/5 seans birikimiyle bayraklandı); 22 Haz 2025 ABD saldırısına "sönük tepki" ([Kitco, 23 Haz 2025](https://www.kitco.com/news/article/2025-06-23/gold-price-modestly-muted-reaction-us-strikes-iran)).

---

## 6. Eksikler, hatalı varsayımlar, gözden kaçmış mekanizmalar

**Hatalı veya sorunlu varsayımlar**
1. "Bayraklı gün = önemli olay" varsayımı: Örtüşen pencereler nedeniyle günler bağımsız değil; olay sayısı tanım parametrelerine (eşik, boşluk, ufuk) güçlü biçimde bağlı.
2. Sabit %3 eşiğinin yıllar arası karşılaştırılabilir olduğu varsayımı: Volatilite rejimi değiştiği için değil.
3. "İlk bayrak = başlangıç" varsayımı (V2 bunu kabul ediyor ama PRE/DURING/POST etiketlemesini yine de buna dayandırıyor).
4. Makro takvimin CPI+NFP ile temsil edilebileceği varsayımı: FOMC, PCE, ISM, JOLTS ve Fed konuşmaları yok; FOMC aynı gün etkisi en güçlü olan.
5. "Güvenli liman" yönünün sabit olduğu örtük varsayımı: Likidite rejiminde altın riskli varlıklarla birlikte satılıyor.

**Gözden kaçmış olası mekanizmalar**
- Yen carry ve küresel kaldıraç çözülmesi (Ağustos 2024).
- Fiziki lokasyon arbitrajı (EFP, COMEX stokları, tarife sınıflandırması).
- Fed bağımsızlığı / ABD kurumsal riski (2025).
- Resmi veri karartması (Ekim–Kasım 2025) ve pozisyon verisinin yokluğu.
- Teminat (margin) değişiklikleri ve borsa kesintileri (28 Kas 2025 CME kesintisi, Aralık teminat artışları).
- Gümüş ve platin köpüğünün altına taşınması.
- Opsiyon vadeleri ve gamma etkisi (WGC Ekim 2023 ve Eylül 2025 notlarında opsiyon aktivitesine değiniliyor — *test edilmedi*).
- Hindistan/Çin yerel prim/iskonto ve mevsimsel fiziki talep (Diwali, Çin Yeni Yılı) — *test edilmedi*.

**Veri eksikleri (öncelik sırasıyla)**
1. Yayın vintajlı DXY ve 10Y reel faiz (DFII10) günlük serisi.
2. Yayın tarihli CFTC COT (rapor tarihi ≠ yayın tarihi; kapanma boşluğu işaretli).
3. Günlük ETF akımları (GLD/IAU ve WGC bölgesel), vintajlı.
4. FOMC sürpriz serisinin (USMPD) 2023–25 için doğru `available_as_of` ile yüklenmesi ve eksik 8 FOMC gününün tamamlanması.
5. FedWatch/vadeli fon olasılık arşivi (beklenti kayması ex-ante ölçümü).
6. Eşzamanlı ilk yayın zaman damgalı haber (GDELT/Reuters) — şu anki kaynakların çoğu yeniden yayın.

---

## 7. Bilimsel çıkarımlar

Bütün kümeler, karşı-olgular ve çapraz piyasa verileri birlikte değerlendirildiğinde aşağıdaki çıkarımlar en iyi desteklenenlerdir. Hiçbiri nedensellik kanıtı değildir; kanıt düzeyi parantez içinde.

1. **Büyük hareketler tipik olarak "hazırlık + tetikleyici + büyütücü" yapısında ve tek bir haber tipiyle açıklanamıyor.** Tek başına veri sürprizi ~1σ, tek başına jeopolitik şok ~1–1.5σ hareket üretiyor; ≥%3 hareketler çoğunlukla iki unsurun çakışmasında görülüyor: 7 Haz 2024 (PBoC + NFP), 3–8 Nis 2025 (tarife + likidasyon), Ekim 2023 (savaş + kalabalık kısa), 29 Ara 2025 (gerginlik + teminat). *(Orta: tutarlı örnekler, sistematik test yok.)*
2. **Düşüşlerin en güçlü ex-ante işareti fiyatın kendisinin gerginliğidir, ama bu yön değil kırılganlık bilgisidir.** DOWN kümeleri önce medyan +%5.6, UP kümeleri +%0.85 dört haftalık getiri. Gerginlik, ≥%3 düşüş olasılığını ~%11'den %19–37'ye çıkarıyor; yükseliş olasılığını düşürmüyor. *(Orta: n küçük, dönemler bağımlı.)*
3. **Jeopolitik etki asimetrik ve pozisyona koşullu görünüyor.** Tırmanmalar küçük, yumuşamalar (gergin fiyatta) büyük tepki üretti; büyük yükseliş yalnız kalabalık kısa pozisyonla birleşince görüldü. *(Zayıf–orta: 6–8 örnek.)*
4. **Faiz kanalı 2023'te güçlü, 2024–25'te kısmen kopuk.** ZN (10Y vadeli fiyatı) küme penceresinde altınla "beklenen" yönde: 2023'te 9/10, 2024'te 12/19, 2025'te 14/24; Mart–Nisan 2024 ve Nisan 2025'te altın faiz yükselirken çok güçlü yükseldi. Bu, yaygın "reel faiz–altın ayrışması" tartışmasıyla uyumlu ama burada reel faiz verisiyle test edilmedi. *(Orta, nicel doğrulama gerekli.)*
5. **Makro takvimde en ayırt edici gün FOMC'dir, TÜFE değil.** FOMC günlerinde ≥2σ hareket olasılığı ~4 kat (p=0.019, düzeltme öncesi, n=15). *(Zayıf–orta: defter eksik, tek dönem.)*
6. **"Güvenli liman" işareti likidite rejimine bağlı olarak tersine dönüyor.** Çapraz varlık satışlarında (Tem 2024, Ağu 2024, Nis 2025, Ara 2025) altın hisse ve petrolle birlikte düştü, sonra ayrıştı. *(Orta.)*
7. **2025'te yeni bir kanal belirdi: kurumsal/mali güven riski.** Fed bağımsızlığı ve kapanma olayları dolar ve tahvil zayıflığıyla birlikte altını yükseltti. *(Hipotez; DXY/vade primi testi gerekli.)*
8. **Marjinal alıcının değişimi volatilite rejimini açıklayabilir.** 2023–24'te ETF çıkışına rağmen yükseliş (resmi/Asya talebi), 2025'te güçlü ETF girişi ve iki yönlü sert hareketler. *(Hipotez.)*

**Sayım düzeyinde düzeltilmiş sonuç:** V2'nin 53 kümesinden 22'si için tarihli eşzamanlı kaynak eklendi (toplam kaynaklı küme 50/53). 2 zamanlama etiketi düzeltildi, 1 yön/mekanizma etiketi hatası bulundu, 5 birleştirme sorunu ve 2 önemli atlanmış olay kaydedildi. Hiçbir küme için ex-ante *tetikleyici* kanıtı yok; ex-ante bilinebilen yalnız **hazırlık koşulları** (gerginlik, kalabalık pozisyon, önceden ilan edilmiş tarihler, yavaşlayan MB alımı).

---

## 8. Önerilen sonraki adımlar (model kurmadan)

1. **Olay tanımını önceden kaydet (PREREG):** Volatiliteye göre ölçekli eşik (ör. |z1|≥2.5 veya |z5|≥2), 1/5/20 seans ufukları, pencere başlangıcı = olay başlangıcı, birleştirme boşluğu duyarlılık tablosu. Sonuçlara bakmadan sabitle.
2. **Kaynak zamanlamasını gerçek başlangıca göre yeniden etiketle** ve "ex-ante hazırlık", "tetikleyici", "büyütücü" alanlarını ayrı sütunlar olarak tut (bu incelemenin CSV şablonu kullanılabilir).
3. **Eşleştirilmiş kontrol günleri:** Aynı gerginlik/sürpriz/şok koşulunu taşıyan ama büyük hareket olmayan günleri sistematik seç (bu incelemedeki kontrol listesi başlangıç olarak kullanılabilir).
4. **Eksik veri katmanlarını vintajlı ekle:** DXY, DFII10, COT (yayın tarihli), ETF akımları, FedWatch, FOMC sürprizleri.
5. **Dış geçerlilik:** Aynı tanımı 2016–2022'ye ve 2026'nın görülmemiş kısmına uygula; burada "3/3" görünen aşırı gerginlik bulgusu ancak böyle sınanabilir.
6. Manifest kaydını (bu dosyaları değiştirmemek talebi nedeniyle) eklemedim; kabul edilirse kullanıcı veya ayrı bir commit `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` içine kısa bir kayıt ekleyebilir.

---

## 9. Temel kaynaklar (tarihli)
- WGC, *October 2023 in review* (7 Kas 2023): https://gold.org/goldhub/research/gold-market-commentary-october-2023
- WGC, *Gold Demand Trends FY2024* (5 Şub 2025): https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2024
- WGC, *Gold Demand Trends FY2025* (29 Oca 2026): https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025
- WGC, *Gold hits US$4,000/oz: trend or turning point?* (13 Eki 2025): https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point
- CFTC COT yeniden yayın takvimi (18 Kas 2025): https://mondovisione.com/media-and-resources/news/cftc-to-resume-publishing-cot-reports-wednesday-the-agency-also-announced-a-c-20251118/
- BLS Ekim 2025 TÜFE iptali: https://news.bloomberglaw.com/us-law-week/bls-axes-us-october-cpi-report-sets-dec-18-for-november-data
- Kitco/Reuters tarihli haberleri (her küme için URL'ler denetim CSV'sinde; URL içinde yayın tarihi bulunur).
- Neon `Gold Control`: CME GLBX saatlik GC/SI/ZN/NQ/CL; `observations` NFP/çekirdek TÜFE ilk açıklama ve PIT konsensüs.
