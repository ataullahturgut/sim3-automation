# BAĞIMSIZ HAKEM DEĞERLENDİRMESİ #2 — GOLD EVENT CHAIN V3/V4 (2023–2025)

**Tarih:** 2026-10-13 · **Hakem:** Claude · **Temel:** `gold-execution-channel-audit-20261006` @ `4ecdf81` (PR #118 sonrası güncel HEAD)
**Okunan:** V3 bulguları + analiz sözleşmesi + JSON özet + günlük panel + 24 küme + düzeltilmiş zamanlama; V4 nedensel denetim, 13 başlangıç/13 kontrol CSV'si, vaka CSV'si; manifest kayıtları.
**Tür:** Tarihsel neden araştırması. **Model, alarm, al-sat kuralı veya kârlılık iddiası yoktur.** Mevcut hiçbir dosya değiştirilmedi; PR #118 birleştirilmedi.

| Ek dosya | İçerik |
|---|---|
| `..._V4_REFEREE_REPRODUCE_20261013.py` | Bu rapordaki fiyat türevli tüm sayıları commit edilmiş V2/V3/V4 CSV'lerinden yeniden üretir |
| `..._V4_REFEREE_RATIOS_20261013.sql` | Neon'dan gümüş/platin/madenci/S&P oran paneli (çıktı **commit edilmedi**: tedarikçi hakları yeniden dağıtıma kapalı) |
| `..._V4_REFEREE_MATCHING_SENSITIVITY_20261013.csv` | V4 eşleştirmesinin üç kuralla yeniden çalıştırılması |
| `..._V4_REFEREE_TENSION_EPISODES_20261013.csv` | Gerginlik günlerinin epizod düzeyinde özeti |
| `..._V4_REFEREE_DIRECTION_SEPARATORS_20261013.csv` | Yön ayrımı için denenen **tüm** 17 özellik (seçilmiş değil) |
| `..._V4_REFEREE_HYPOTHESIS_LEDGER_20261013.csv` | 17 hipotezin durumu, kanıtı, kaynağı, bilgi zamanı |
| `..._V4_REFEREE_CASE_DEEPDIVE_20261013.csv` | Dört vaka: ÖNCE / SIRASINDA / SONRA katmanları |

---

## 0. En önemli sorunun cevabı

**Soru:** Büyük bir altın hareketinden önce birden fazla koşulun birleştiği ve bunu diğer günlerden ayıran tekrar edilebilir bir olaylar örgüsü var mı?

**Cevap: Kısmen — ama "hareketin olacağını" değil, "hareket olursa yönünü ve büyüklüğünü" açıklayan bir örgü var. Bunun dışında genel geçer bir öncü örgü bulunamadı.**

1. **Büyük hareketin zamanlamasını önceden ayıran tekrar edilebilir bir koşul bulunamadı.** Gerginlik, büyük hareket olasılığını 2024–25'te artırıyor ama 2023'te azaltıyor (§3.1). En büyük şoklardan biri (5 Ağustos 2024) hiç gerginlik yokken, dışsal bir fonlama şokuyla geldi.
2. **Bulunan örgü iki katmanlı:**
   - **(a) Durum:** Önceki 20 seanslık getiri. Büyük bir hareket gerçekleştiğinde, önceki yükseliş hareketin **düşüş** yönünde olma olasılığını üç yılın her birinde aynı ölçüde artırıyor (AUC 0.74 / 0.73 / 0.74).
   - **(b) Tetikleyici türü:** Gergin fiyatta, rallinin baskın anlatısını tersine çeviren haber sert düşüşle; anlatıyı pekiştiren haber yükselişle çakışıyor. Aynı haber fiyat gergin değilken küçük kalıyor.
   - Bu ikinci katman **yeni bir hipotezdir**; geriye dönük ve kör olmayan kodlamaya dayanıyor (§5).
3. **V4'ün eşleştirilmiş kontrol tasarımı bu soruyu cevaplayacak güce sahip değil ve sızıntı içeriyor.** Kontrol sonuçları kurala göre "UP 8/13"ten "DOWN 5/13"e kadar değişiyor (§1).

---

## 1. V4: 13 gerginlik başlangıcı ve 13 kontrol — metodoloji denetimi

**Yeniden üretim:**
- 13 ilk geçiş birebir üretildi.
- 13 kontrolün 12'si birebir aynı. Bir kontrolde (2025-04-11 → V4: 2025-08-06, benimki: 2025-08-07) σ eşitliğinde farklı seçim var; sonuç değişmiyor.
- Sonuçlar doğru: risk DOWN 2/13, UP 4/13; kontrol DOWN 1/13, UP 8/13.

**Bulunan sorunlar**

1. **Bağımlılık.** 13 başlangıç yalnız **6 ralli epizoduna** ait (birbirine ≤20 seans olanlar birleştirildiğinde). 7 başlangıç çiftinin 10 seanslık gelecek pencereleri örtüşüyor; örneğin 2023-03-23 / 03-28 / 04-04 ve 2024-03-28 / 04-03 / 04-10. CSV'deki `NO_FUTURE_WINDOWS_OVERLAP` etiketi yalnız risk–kontrol çifti için doğru; riskli günlerin kendi aralarında doğru değil.

2. **Kontrol sızıntısı (en ciddi sorun).** 13 kontrolün **8'inin** 10 seanslık gelecek penceresi, bir risk başlangıcını *oluşturan* 20 seanslık rallinin içine düşüyor:
   - 2024-02-23, 02-27, 02-28, 03-01 → Mart 2024 rallisi;
   - 2025-03-05 → Nisan 2025;
   - 2025-08-05, 08-06, 08-20 → Eylül 2025.

   Kontrollerin "UP" sonuçlarının 6'sı bu sızan günlerden geliyor. Yani "kontrollerde UP 8/13", büyük ölçüde riskli başlangıçları yaratan aynı rallileri sayıyor. Bu dairesel bir karşılaştırma.

3. **Eşleştirme kuralına aşırı duyarlılık** (`MATCHING_SENSITIVITY.csv`):

   | Kural | Kontrol DOWN | Kontrol UP | Risk DOWN | Risk UP |
   |---|---:|---:|---:|---:|
   | V4 (yeniden üretim) | 1/13 | 8/13 | 2/13 | 4/13 |
   | Sızıntısız (kontrolden sonraki 30 seansta gerginlik yok) | 5/13 | 3/13 | 2/13 | 4/13 |
   | Sızıntısız + ±60 seans | 1/13 | 3/13 | 2/13 | 4/13 |

   Kontrol grubunun yönü tasarım tercihine bağlı olarak tersine dönüyor. Sızıntısız kuralda 2024 kontrolleri Kasım 2024 seçim düşüşüne kayıyor; bu da başka bir rejim karışıklığı.

4. **Güç yetersizliği.** 13'e 13 karşılaştırmada kontrol oranı %10 iken gücün %80'e ulaşması için risk oranının ~%60 olması gerekir. %30'luk gerçek bir fark ancak %22 olasılıkla görülür. V4'ün 2/13 – 1/13 farkı için Fisher p = 1.0.

5. **Seçim ve pencere yanlılığı.**
   - Tasarım yalnız *ilk geçişi* ölçüyor ve sonucu ilk geçişten sonraki 10 seansla sınırlıyor. Oysa en önemli düşüşler gerginlik **uzun sürdükten sonra** geldi: 35 seanslık Eylül–Ekim 2025 epizodu 21 Ekim düşüşünü içeriyor ama 8 Eylül başlangıcının 10 seanslık penceresi bunu görmüyor.
   - Aralık 2025'teki iki ilk geçiş, sonucu tamamlanmadığı için dışarıda kalmış; 29 Aralık düşüşü de bu yüzden görünmüyor.
   - Kontroller aynı yıl içinde σ'ya göre eşleştirilmiş ama mevsim ve rejim ayrı: 2025 riskleri Nisan–Mayıs, kontrolleri Ağustos–Kasım.
   - Sabit %3 sonuç eşiği 2023'te ~1.1σ√10, 2025'te ~0.9σ√10'a denk geliyor (yıllık medyan σ'ya göre); sonuç ölçütü de rejime bağımlı.

**Hakem önerisi:** Gün düzeyinde eşleştirme yerine **epizod düzeyi** analiz ve **epizod-blok bootstrap** kullanılmalı. Sonuç, sabit 10 seans yerine "epizod sonu + 20 seans"ta ölçülmeli. Kontroller sızıntısız kurala göre önceden kaydedilmeli (PREREG).

---

## 2. Epizod düzeyinde gerginlik: ne oluyor?

20 seanslık getiri ≥%8 olan 76 gün, ≤10 seans boşlukla birleştirildiğinde **8 epizod** veriyor (`TENSION_EPISODES.csv`).

| Başlangıç | Seans | Zirveye kadar kazanç | Zirve sonrası 20 seanslık maks. düşüş | 10 seansta ≥%3 düşüş gelen gün |
|---|---:|---:|---:|---:|
| 2023-03-23 | 11 | %10.9 | −%1.9 | 0/11 |
| 2023-10-27 | 6 | %8.5 | −%3.4 | 1/6 |
| 2024-03-11 | 3 | %8.1 | −%1.2 | 0/3 |
| 2024-03-28 | 16 | %17.0 | −%4.3 | 4/16 |
| 2025-02-10 | 2 | %9.2 | −%1.7 | 0/2 |
| 2025-04-11 | 18 | %14.7 | −%7.2 | 8/18 |
| 2025-09-08 | 35 | %30.2 | −%9.8 | 9/35 |
| 2025-12-23 | 3 | %9.7 | −%4.8 | 3/3 |

**Sonuçlar**
- **8 epizodun hepsi** zirveden sonra geri çekildi, ama yalnız **5'inde** ≥%3. Gerginlik tek başına "düşüş" demek değil; her rally bir yerde bitiyor.
- **Ralli ne kadar büyükse, zirve sonrası düşüş o kadar derin** (Spearman −0.79, p = 0.021, n = 8). Bu tutarlı ama zirve günü önceden bilinemez; gerçek zamanlı kullanılabilir bir işaret değil.
- Volatiliteye ölçeklenmiş tanımla (zr20 ≥ 2) epizod sayısı 6'ya iniyor ve aynı tablo korunuyor.

---

## 3. Kırılganlık tek başına yön vermiyor — hangi ilave koşullar yönü ayırıyor?

Her özellik gün kapanışında bilinebilir: önceki 60 günlük σ, 5/20 seanslık getiri, gün içi aralık (V2), sd20/sd60, önceki gün NQ/CL/ZN (V3 kapsam kapılı). Gümüş/altın, platin/altın, NEM/altın ve S&P 500 serileri Neon `observations`'tan alındı. Bunlar "LBMA" etiketli **yeniden yapılandırma** veya NYSE/FRED kapanışlarıdır; yayın zamanı kanıtlanmamış.

**17 özelliğin tamamı raporlandı; yalnız tutanlar seçilmedi.**

### 3.1 Büyük hareket olur mu? (gerginlik → herhangi bir ≥%3 hareket, 10 seans)

| Yıl | Gerginlikte (zr20≥2) | Gerginlik dışı |
|---|---:|---:|
| 2023 | 1/12 (%8) | %36 |
| 2024 | %58 (n=31) | %43 |
| 2025 | %91 (n=46) | %61 |

**Tutarsız:** 2023'te gerginlik büyük hareketi azaltmış. "Kırılganlık hareketin olacağını gösterir" hipotezi de genel geçer değil.

### 3.2 Büyük hareket olduğunda yön (DOWN-ilk 85 gün / UP-ilk 286 gün, blok-bootstrap %95 güven aralığı)

| Özellik | AUC (DOWN-ilk) | %95 GA | 2023 | 2024 | 2025 |
|---|---:|---|---:|---:|---:|
| **r20 (önceki 20 seans getirisi)** | **0.683** | 0.559–0.802 | 0.739 | 0.733 | 0.743 |
| **zr20 (volatiliteye ölçekli)** | **0.678** | 0.551–0.795 | 0.753 | 0.731 | 0.681 |
| r5 | 0.604 | 0.507–0.740 | 0.493 | 0.660 | 0.681 |
| gümüş/altın 5 gün | 0.377 | 0.284–0.480 | 0.548 | 0.377 | 0.282 |
| gün içi aralık (5 gün) | 0.575 | 0.460–0.714 | 0.432 | 0.663 | 0.705 |
| NEM/altın, S&P, NQ, CL, ZN, platin | 0.44–0.53 | 0.5'i içeriyor | işaret değişiyor | | |

**Sonuçlar**
- **Güçlenen:** Önceki trend, büyük hareketin yönünü üç yılın her birinde aynı derecede eğiyor. Bu, V3/V4'ün "gerginlik yön vermez" bulgusuyla çelişmiyor, onu **düzeltiyor**: gerginlik hareketin *olmasını* tutarlı biçimde ayırmıyor, ama hareket olduğunda *yönünü* tutarlı biçimde eğiyor.
- **Uyarı:** Bu analiz geleceğe koşullanıyor ("büyük hareket olduysa"); alarm değildir. 17 özellik denendi; çoklu test riski var.
- **Karışık:** Gümüşün son 5 günde altından zayıf kalması DOWN ile ilişkili (GA 0.5'i dışlıyor) ama 2023'te ilişki yok.
- **Desteklenmedi:** Madenci, hisse, petrol ve faiz göstergeleri.

### 3.3 Gerginliğin içinde: düşüşten önce ne değişiyor?

74 gerginlik günü, 21'i ≥%3 düşüşle izlendi, 7 epizod.
- 5 günlük gün içi aralık: AUC 0.892; epizod içi sıralamada 0.791.
- sd20/sd60 (volatilite genişlemesi): 0.821 / 0.770.
- Süre: 0.759 / 0.871.
- Ham r20 0.784, **ama volatiliteye ölçekli zr20 yalnız 0.498.** Ham etki rejimden (2025) kaynaklanıyor.

**Yorum:** "Fiyat yükselirken volatilitenin de yükselmesi" düşüşten önce görülüyor. Ekim 2025'te 16–20 Ekim arası gün içi aralık 2.6σ'dan 3.2σ'ya, sd20/sd60 1.15'ten 1.28'e çıktı. Ancak:
- iki sonucu da içeren yalnız **4 epizod** var;
- etkinin önemli bir kısmı "epizodun sonuna yakınlık".

Bu yüzden durum: **düşündürücü, kanıtlanmadı.**

---

## 4. Alternatif mekanizmalar

Ayrıntı `HYPOTHESIS_LEDGER.csv` dosyasında.

| Mekanizma | Durum | En güçlü kanıt | Bilgi zamanı |
|---|---|---|---|
| **Zorunlu likidasyon / fonlama şoku** | GÜÇLENDİ | [BIS Bülten 90, 27 Ağu 2024](https://www.bis.org/publ/bisbull90.htm): ~¥40 trilyon carry, prosiklik kaldıraç azaltma ve teminat artışları. XAU 5 Ağu gün içi %4.0 aralık; **r20 yalnız %2.2 (gerginlik yok)**. Nis 2025'te CL −%18, NQ −%11; Ara 2025 CME teminatları | Tetikleyici eşzamanlı, açıklama sonradan |
| **Faiz beklentisi** | Klasik kanal sürüyor ama sınırlı | Çekirdek TÜFE sürprizi–altın korelasyonu −0.61 (PR #118). [RBC, 26 Haz 2025](https://www.rbcwealthmanagement.com/en-us/insights/golds-regime-change): altın–TIPS korelasyonu 2005–21 %84, 2022–23 %3, 2024+ %7. ZN önceki gün AUC ~0.50 | Veri günü eşzamanlı |
| **Fed bağımsızlığı** | GÜÇLENDİ | Nis 2025 Powell saldırıları → 3,500$; 22 Nis geri adım → düşüş; 25 Ağu Cook. Örneklem dışı doğal deney: 30 Oca 2026 Warsh adaylığı → GLD gün içi −%13, SLV −%34 ([etf.com, 30 Oca 2026](https://www.etf.com/sections/features/gold-silver-etfs-suffer-historic-collapse-trump-fed-pick)). Mekanizma: siyasi baskı enflasyon beklentisini yükseltir ([Drechsel, NBER w32461, May 2024](https://www.nber.org/papers/w32461)) | Olaylar eşzamanlı; 2026 örneklem dışı |
| **Jeopolitik** | Tehdit–eylem asimetrisi GÜÇLENDİ | Metaller eylemlerden çok tehditlere tepki verir ([Baur & Smales 2020, JBF](https://ideas.repec.org/a/eee/jbfina/v117y2020ics037842662030090x.html)). 1 Eki 2024 İran füzeleri +%1.0; 23 Haz 2025 ABD saldırısı +%0.1; 19–22 Nis 2024 yumuşama −%2.6 (z −3.4) | Eşzamanlı |
| **ETF / CFTC kalabalığı** | ZAYIFLADI | 20 Ağu 2024 haftası net uzun 193,305 kontrat, Mart 2020'den beri en yüksek ([Kitco, 26 Ağu 2024](https://www.kitco.com/news/article/2024-08-26/gold-still-has-plenty-room-run-hedge-funds-bullish-bets-hit-4-year-high)); ardından ralli Ekim sonuna kadar sürdü. Ekim 2025'te pozisyon "aşırı değil" (WGC) ve COT görünmezdi | COT ~3 gün gecikmeli |
| **COMEX–Londra EFP** | GÜÇLENDİ (ayrı mekanizma) | 17 Oca 2025 COMEX stokları 23.62m oz; Hindistan ve Londra kiralama oranları rekor ([Reuters/Kitco, 11 Şub 2025](https://www.kitco.com/news/off-the-wire/2025-02-11/us-demand-squeezes-indias-gold-supply-leasing-rates-rise-record)); 3 Nis muafiyet sonrası prim ~$43→~$20. ECB (19 May 2025) fiziki sıkışma ve teminat riskini işaret etti ([Kitco](https://www.kitco.com/news/article/2025-05-20/ecb-highlights-golds-increasing-risks-analysts-say-threat-overstated)) | EFP/stok verisi gerçek zamanlı yayımlanır ama repoda vintajlı seri yok |
| **Opsiyon gamma** | TEST EDİLEMEDİ | [WGC 7 Eki 2025](https://www.gold.org/goldhub/research/gold-market-commentary-september-2025): Eylül'de "güçlü opsiyon aktivitesi" bir sürücü; sayı yok. OI/IV/skew verisi yok | Sonradan anlatı |
| **Gümüş/metal liderliği** | KARIŞIK | §3.2–3.3. Önceki PR #118'deki gümüş sayıları seyrek CME SI saatlik verisine dayanıyordu; V3 bu veriyi haklı olarak yetersiz buldu (12/774). Bu incelemede günlük LBMA yeniden yapılandırması kullanıldı | Yayın zamanı kanıtsız |
| **Perakende momentum / patlayıcı rejim (YENİ)** | ADAY | [BIS Üç Aylık İnceleme, Ara 2025, Kutu C](https://www.bis.org/publ/qtrpdf/r_qt2512.pdf): altın ve S&P 50 yılda ilk kez aynı anda patlayıcı; ETF'ler 2025 başından beri NAV üzerinde primli; perakende alıcı, kurumsal yatay | Yayın sonradan; test gerçek zamanlı uygulanabilir |
| **Resmi talep (MB)** | Yavaş arka plan | MB alımları 2022–24'te üç yıl üst üste >1,000t ([RBC](https://www.rbcwealthmanagement.com/en-us/insights/golds-regime-change)). Fed IFDP 1420 (Eyl 2025): birikimin ~%64'ü Çin, Rusya, Türkiye; yaptırım kaynaklı dolar terki kanıtı sınırlı ([Weiss 2025](https://www.federalreserve.gov/econres/ifdp/files/ifdp1420.pdf)) | Aylık/çeyreklik, revizyonlu |

---

## 5. Dört vaka — önce / sırasında / sonra

Tam tablo `CASE_DEEPDIVE.csv` dosyasında.

**Ağustos 2024 carry çözülmesi.**
- **Önce:** 31 Tem BoJ artışı; 2 Ağu NFP 114k vs 176k (Neon PIT konsensüs); yönetilen fon net uzunu yüksek. **Gerginlik yoktu** (r20 %2.1).
- **Sırasında:** 5 Ağu gün içi %4.0 aralık; gümüş/altın 5 günde −%5.0.
- **Sonra:** BIS 27 Ağu. Altın 16 Ağu'da 2,500$'ı geçti.
- **Ders:** Dışsal fonlama şoku gerginlik gerektirmez ve kalıcı yön üretmeyebilir.

**Ocak 2025 fiziki arbitraj.**
- **Önce:** Tarife tehditleri; günlük CME depo stokları ve vadeli-spot primi piyasada görünürdü.
- **Sırasında:** 17 Oca stoklar, 29 Oca BoE kuyruğu, 11 Şub kiralama oranları.
- **Fiyat:** 2→28 Oca +%3.98. Gerginlik 10 Şub'da başladı ve yalnız −%1.7 ile −%3.2 geri çekilmeyle bitti.
- **Ders:** Bu mekanizma bir *yükseliş birikimi* üretti; asıl çözülme 3 Nisan muafiyetiyle geldi.

**Nisan 2025 iki yönlü tarife.** Aynı konu, hangi kanalın baskın olduğuna göre iki yönde sonuç verdi:
1. **3–8 Nis:** EFP primi çöktü ve küresel likidasyon oldu → düşüş.
2. **9–11 Nis:** Çin tırmanması ve "Amerika'yı sat" (10Y %3.87→%4.47, dolar zayıf; [NAB, 16 Nis 2025](https://business.nab.com.au/behind-recent-bond-market-turbulence/)) → S&P +%9.5 ile aynı gün altın +%8.6.
3. **17–22 Nis:** Fed bağımsızlığı korkusu → 3,500$ rekor.
4. **22–23 Nis:** Trump'ın geri adımı → düşüş.

**Basit bir risk-off sınıflaması dört aşamanın üçünde yanlış yön verir.**

**Ekim 2025 düzeltmesi.**
- **Önce:**
  - 35 seanslık gerginlik;
  - WGC 7 Eki: rekor ETF girişi ve opsiyon aktivitesi;
  - WGC 13 Eki: kırılganlık uyarısı, ama pozisyon aşırı değil;
  - resmi veri ve COT karartması;
  - 16–20 Eki gün içi aralık ve volatilite genişlemesi;
  - 17 ve 20 Eki gümüşün altından zayıf kalması.
- **Sırasında:** 20 Eki ABD–Çin anlaşma beklentisi, Diwali sonu, 21 Eki spot gün içi −%6.3 ([CNN, 21 Eki 2025](https://localnews8.com/money/cnn-business-consumer/2025/10/21/golds-frenzied-rally-ends-with-largest-sell-off-in-over-a-decade/)).
- **Sonra:** COT 19 Kas'tan itibaren, BIS Aralık Kutu C, Çin KDV (1 Kas yürürlük). Bu sonuncusu **düşüşten sonra**; neden olamaz.
- **Ders:** Gerginlik 30 Eylül'den beri vardı ve fiyat **%13 daha** yükseldi. Zamanlamayı açıklayan ek unsur, gergin durumdaki **anlatı-tersine çevirici haberdir**.

**Yeni hipotez — "gerginlik × anlatı tersine dönüşü" (H15):**

| Tarih | Gerginlik (r20) | Anlatıyı tersine çeviren haber | Sonuç |
|---|---:|---|---|
| 19–22 Nis 2024 | %9.6 | İsrail-İran yumuşaması | −%2.6 (z −3.4) |
| 22 Nis 2025 | %12.2 | Trump Powell'ı görevden almayacak | düşüş |
| 12 May 2025 | önceki 4h +%14.9 | ABD-Çin tarife ateşkesi | düşüş |
| 20–21 Eki 2025 | %16.3 | ABD-Çin anlaşma beklentisi | −%5.4 |
| 30 Oca 2026 (örneklem dışı) | — | Warsh adaylığı | GLD gün içi −%13 |
| **Karşı örnek:** 24 Haz 2025 | **%0.6 (gergin değil)** | İran ateşkesi | yalnız −%1.4 |

V3'ün 12 DOWN kümesinin 5'i bu sınıfa giriyor. Kodlama geriye dönük ve kör değil; bu yüzden bulgu hipotezdir. Doğrulamak için anlatının hareketten **önceki** kaynaklardan kör kodlanması gerekir.

---

## 6. Karşı örnekler: aynı koşul var, büyük hareket yok

- **Gerginlik, düşüş yok:** Mart–Nisan 2023 (0/11 gün; zirve sonrası −%1.9), Şubat 2025 (−%1.7), Mart 2024'ün ilk ayağı (−%1.2), Mart–Nisan 2024 (fiyat %10.7 daha yükseldi, V4 vaka 2).
- **Kalabalık uzun pozisyon, çöküş yok:** Ağustos–Ekim 2024.
- **Büyük jeopolitik eylem, küçük tepki:** 1 Eki 2024, 13 Haz 2025 (+%1.4), 22 Haz 2025.
- **Büyük veri sürprizi, küçük tepki:** 6 Eki 2023 NFP +166k → +%0.65; 4 Eki 2024 +107k → −%0.18 (PR #118 kontrol listesi).
- **Gerginlik 2 hafta sürdü, büyük düşüş yok:** 30 Eyl–8 Eki 2025.

---

## 7. Somut sonuç: güçlenen, çürüyen, açıklanamayan, umut veren

**Güçlenen**
- Büyük hareket olduğunda önceki trend yönü eğer (H03; üç yılda kararlı).
- Fonlama/teminat şokunda altın riskli varlıklarla satılır (H09).
- Fed bağımsızlığı kanalı (H10; 2026 örneklem dışı doğal deneyle tutarlı).
- EFP/fiziki lokasyon ayrı bir mekanizmadır (H11).
- Jeopolitik tehdit–eylem asimetrisi (H08).

**Çürüyen veya zayıflayan**
- Gerginlik yönlü satış işaretidir (H01): **çürüdü.**
- Gerginlik büyük hareketi tutarlı biçimde öngörür (H02): **tutarsız.**
- Kalabalık CFTC/ETF pozisyonu çöküşü öngörür (H13): **zayıfladı.**
- Reel faiz kanalı ana açıklayıcıdır (H14): **zayıfladı.**
- Çin KDV değişikliği Ekim düşüşüne katkı yaptı (H17): **zamanlama nedeniyle reddedildi.**
- V4'ün "kontrollerde UP 8/13" karşılaştırması: **sızıntı nedeniyle geçersiz.**

**Açıklanamayan**
- Mart–Nisan 2024 rallisi: WGC'nin kendi modelinde artık terim; 22 Mar–11 Nis 2024 arasında ZN −%2.4 (faiz yükseldi) iken XAU +%9.8.
- 17 Ekim 2025 ilk kırılmanın kesin tetikleyicisi.
- 4 Aralık 2023 gece spike'ı.
- 15 Mayıs 2025 12h yükselişi.
- Gerginliğin neden 2023'te büyük hareketi *azalttığı*.

**Bilimsel olarak en umut verici araştırma yolları (model değil)**
1. **H15'i önceden kaydedilmiş, kör kodlamayla sına.** Her gerginlik epizodunun baskın anlatısını yalnız epizod öncesi kaynaklardan kodla; sonra anlatıyı pekiştiren/tersine çeviren haberleri tarihli olarak sınıflandır. 2016–2022 ve 2026 örneklem dışı sınama alanıdır.
2. **H03'ü taze dönemlerde dene.** 2016–2022 ve 2026'yı daha önce görülmemiş veri olarak kullan; özellik listesi bu rapordaki 17 ile sınırlı ve sabit kalmalı.
3. **Gerçek zamanlı yayımlanan piyasa yapısı verisini vintajlı topla.** EFP, CME depo stokları, Londra kiralama oranları, GLD primi/iskontosu, CME teminat bildirimleri ve opsiyon IV/skew. Bunlar hem H11/H12/H16'yı test eder hem de "zorunlu satış" kanalını ölçülebilir kılar.
4. **Volatilite-fiyat birlikte yükselişini (H05) epizod-blok tasarımla sına.** Örneklem 2023–25 dışına genişletilmeli.

---

## 8. Kendi önceki çalışmama (PR #118) yönelik düzeltme

- PR #118'deki GC/SI çapraz piyasa sayıları seyrek CME saatlik verisine dayanıyordu. Örneğin "gümüş 53 kümenin 46'sında aynı yönde" sayısı, gümüşün 774 günün yalnız 12'sinde yeterli bar kapsamına sahip olduğu bir kaynaktan geliyordu. V3'ün kapsam kapısı haklıdır. Bu sayılar **güvenilir değildir** ve bu incelemede günlük LBMA yeniden yapılandırmasıyla değiştirilmiştir.
- PR #118'deki "FOMC 4/15" sayısı eksik paydaya dayanıyordu; V3'ün 24 toplantılı 4/24 düzeltmesi doğrudur.

---

## 9. Sınırlar
- Dolar endeksi, reel faiz, günlük ETF akımları, ham COT, FedWatch, EFP, opsiyon ve kiralama oranı serileri repoda vintajlı olarak yok. Bunlar için nicel sonuç üretilmedi.
- Gümüş/platin/NEM/S&P serilerinin ilk yayın zamanı kanıtlanmamış; LBMA fixing saati kodlanmamış.
- Tüm 2023–25 dönemi daha önce incelendi; hiçbir sonuç dokunulmamış test başarısı değildir.
- 2026 Warsh olayı yalnız örneklem dışı nitel destek olarak anıldı; fiyat verisi bu çalışmada analiz edilmedi.
- Manifest değiştirilmedi (kullanıcı talebi). Kabul edilirse ayrı bir kayıt eklenebilir.
