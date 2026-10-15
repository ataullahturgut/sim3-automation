# Gold Portfolio Guard — V6 Ekonomik Örgü Kanıtı ve Çapraz Piyasa Karar Filtresi

**15 Ekim 2026 · Gerçek tarihsel denetim, canlı işlem yetkisi yok.**

## Soru ve sonuç
OLAY-02 / ÖĞREN-03 ekonomik hipotezleri altın için maliyet-sonrası ekstra karar faydası sağlıyor mu? **Cevap henüz kanıtlanmadı.** 96 OLAY-02 kaydında ilk yayın zamanı doğrulanmış kayıt **0**, ekonomik nedenselliği kanıtlanmış kayıt **0**, as-of işlem kararı onaylı kayıt **0**. Bu yüzden G05-C/G06-B veya G01/ORG01 gibi tarihsiz hipotezler **asla doğrudan canlı AL/SAT sebebi** olarak kullanılmadı. Araştırma tablosunun Git blob'u `4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527`.

## 1. Verinin gerçekte ne olduğu
- CME geçmiş NQ, ZN, SI, CL vadeli fiyatları: as-of altın karar saatlerine eşlendi. H1 çubuğunun başlangıcından en az bir saat sonraki karar, en geç dört saatlik veri yaşına sahip olabilir. 6 H1 gözlemle altı saatlik fiyat değişimi türetildi, altı çubuğun zaman açıklığı 9 saati aşarsa sahte altı saatlik ölçüm üretilmez.
- Pinned yeni as-of eşleme panelleri: `data/CROSSMARKET_ASOF_2023_2024_3H_V1.csv` (Git blob `20f237093d8f073664baeab2f61bcca4c00a6d16`, **2193** karar slotu); `data/CROSSMARKET_ASOF_2025_2026_3H_V1.csv` (Git blob `392a505456355cb39485253c601760dc0f09b6e6`, **1914** slot). Toplam **4107** karar slotu.
- NQ + ZN ikisi birlikte geçerli: 2023 **640/1095**, 2024 **655/1098**, 2025 **648/1095**, 2026 Ocak–Eylül **491/819**. Silver SI geçerli: sırayla yalnız **22, 25, 48, 48** slot. Bu kadar seyrek SI'yi zorunlu gerekçe yapma. NaN/bayat durumda `UNKNOWN_DATA`, kesin risk rahatlaması değil.
- Alternatif makro-olay/sürpriz veri kaynağı R71 için 2024–2026 kapsaması yok; ekonomik ilk yayımlı haber olarak sunulamaz.

## 2. V4 sabit modeline eklenen tek değişiklik
`crossmarket_v6.js` yalnız V4'ün 09/12/15 Türkiye karar saatlerini izler. İki gözlem birlikte sağlanırsa `NQ6 <= -%0,8` VE `ZN6 <= -%0,12`, bu **ekonomi nedeni değil çapraz piyasa birlikte satış fiyat vekili** diye etiketlenir.

- V4 AL yapacakken iki piyasa aynı anda böyle düşüyorsa alımı ertelemeyi dene.
- V4'te beklemeye devam edilen riskli GOLD pozisyonunda aynı anda XAU `r92 <= -%1,3` ve `r4 <= -%0,5` olursa riskli satışın erkene alınmasını deneysel olarak değerlendir. Değilse orijinal V4 SAT kuralını uygula.
- Acil fiyat şoku, komisyonda alış ve satış için ayrı **%0,8** gibi V4 temel kuralları saklı kalır. `overlay=false` V4 ile birebir aynı işlem saat ve sonuçları üretmek zorundadır; testler bunu kontrol eder.
- Gerçek Türkiye banka ASK/BID, slip, makro ilk haber sürümü bu çalışmada YOK. V6 geçmiş getirileri görülerek kurulmuş; 2026 sonucu **kör OOS değil**.

## 3. Getiri ve işlem sayısı (tam karşılaştırma)

| Dönem | V4 (yalnız fiyat) | V6 (fiyat+NQ/ZN) | Delta / sonucu |
|---|---:|---:|---|
| 2023* (100 $ ile bağımsız) | 110,5740 $ | 110,5740 $ | 0 $; sıfır işlem farkı |
| 2024 (100 $ ile bağımsız) | 125,5188 $ | 125,5188 $ | 0 $; sıfır işlem farkı |
| 2025 (100 $ ile bağımsız) | 141,1253 $ | 141,1253 $ | 0 $; sıfır işlem farkı |
| 2026 Şubat–Eylül (Ocak V1 nakit 119,753917 $ başlangıç) | **96,706968 $** | **98,285174 $** | **+1,578206 $**, fakat 7 yerine **13 işlem** |

*2023 fiyat evreni eksik; sağlam yıllık OOS iddiası değil. 2026 Şubat–Eylül maksimum gerileme V4 **%26,68** / V6 **%24,77**. NQ/ZN eşlemesi 2026 toplam 513 banka risk kontrol noktasında 422 defa kullanılabilir, 91 defa geçersiz/yok; 11 beraber satış riski, 4 ek koruyucu satış, **0 engellenmiş alış**.

Bu örneklemde **yeni filtrenin getiriyi kalıcı artırdığına ilişkin kanıt yok**: önceki üç yıl hiçbir alım/satımı değiştirmedi; 2026'da işlem sayısını artırıp nakitte kalmaktan ve ilk Şubat AL/TUT kontrolünden kötü net verdi. Otomatik yükseltme yetkisi yok.

## 4. Diğer eşzamanlı V6 hipotezleriyle tutarlılık
- `macro_v6.js` sert -%2 intraday/24h risk sınıflandırıcısı: ilk fiyat+makro çalışma setinde yalnız **506 tam günlük örnek / 963 aday günlük saat**. 2024 testinde 148 günlük 5 sert aşağı vaka; 2025 testinde 155 gün 8 vaka; 2026 örneğinde 114 gün 14 vaka. Olay desteği seyrek, olasılık kesinliği iddia edilemez.
- `macro_v6_portfolio.js` adlı bağımsız V5 tabanlı çapraz-varlık alternatifi Şubat–Eylül sonunu **107,740399 $** hesapladı; salt V5 aynı dönem **107,832861 $**. Bu ikinci V6 örneği V5'e göre de üstün değil. Başlangıç/strateji farklı olduğu için bu rakamı V4-tabanlı V6 98,285174 ile aynı tek model gibi birleştirme.
- `event_evidence_gate_v6.js` 2023-02-01 06:15 UTC olay sınıfına aynı günün 19:00 UTC Fed açıklamasını geçmiş haber diye bağlamayı engeller. Bu yalnız tek kanıtsız nedeni engeller; başka olası önceki nedenleri reddetmez.

## 5. Araştırmada doğru devam yolu
Önce as-of ekonomik ilk yayın, GPR, faiz/dolar, fiziksel talep/ETF veri zaman damgasını topla ve doğrudan piyasa davranışından ekonomik sebep üretme. Etiketleri geçmişten bilen seçilmiş 96 olaya güvenmek yerine olaysız negatif kontrol ve bağımsız epizotlar kullan. Kısmi kayıtta gerekçe `UNRESOLVED` ve karar `ABSTAIN` kabul edilsin. Gerçek banka makası ve bağımsız daha sonraki veriler olmadan kalibrasyon/otomatik AL-SAT onayı verilmesin.

**Son bilimsel karar:** Fiyat+ekonomik örgü henüz fiyat modeline kanıtlanmış marjinal karar avantajı sağlamıyor. Testler Windows/Linux üzerinde çalıştırıldı; önceki V1–V5 karar dosyaları değiştirilmedi. Finansal tavsiye veya canlı ticaret sinyali değildir.
