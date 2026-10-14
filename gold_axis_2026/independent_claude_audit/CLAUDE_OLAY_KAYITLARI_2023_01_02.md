# CLAUDE — Olay kayıtları, Ocak–Şubat 2023 (OLAY-02 şablonuyla, Claude'un bağımsız kaydı)

**Temel belgeler (yalnız okunur, değiştirilmez):** [ANA-01](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) · [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md). Bu dosya OLAY-02'ye **yazmaz**; aynı olay için OLAY-02'de kimlik varsa **aynı `EVENT_ID`** kullanılır, yoksa aynı biçimde yeni kimlik verilir.
**Bağlı Claude belgeleri:** [CLAUDE ÖĞREN sicili](CLAUDE_OGREN_03_OGRENME_SICILI.md) · [CLAUDE DURUM](CLAUDE_DURUM_04_CALISMA_DURUMU.md) · [Karar günlüğü](CLAUDE_ANALYST_DECISION_JOURNAL_JAN_FEB_2023.md).
**Kip:** kararlar `AS_OF` (yalnız o an bilinen), benzer olay yorumu `FULL_HISTORY_DISCOVERY` olarak ayrı işaretli. **Hindsight:** Sonuçları bilerek yazıldı; kör test değildir.

**Ortak veri kaynakları:** XAU 15dk BID/ASK ve 1dk MID (Neon, vendor; banka fiyatı değil) · CME `.n.0` saatlik GC/SI/ZN/NQ/CL ve 1dk gümüş (depo) · GVZ günlük (depo) · ilk yayım + konsensüs (Neon `observations`; ISM/ADP/GDP/PCE/perakende için yayın günü haber kaynakları). **Eksik:** gün içi DXY, 2Y/10Y getiri düzeyi, gerçek banka BID/ASK.
**Tepki sütunları:** altın değişimi, açıklamadan önceki son tamamlanmış 15dk MID'e göre: 15dk / 1s / 4s / 1, 3, 5 seans kapanışı. CME 1s = açıklamadan önce biten saat → açıklamadan ≥1 saat sonra biten saat (pencere XAU ile aynı değil). ZN fiyattır (ZN↑ ≈ faiz↓).

---

## Olay dizini

| EVENT_ID | OLAY-02'de var mı? | Claude kararı | Bağlı hipotez |
|---|---|---|---|
| `MACRO_2023_01_05_ADP` | Var | A2: ALTINDA KAL · A1: BEKLE | C-H01 |
| `MACRO_2023_01_06_NFP` + `US_ISM_SERVICES_2023_01_06` | NFP var, ISM sayfası yok | **AL** 16:46 TRT | C-H02 |
| `US_CPI_2023_01_12` | Sayfa yok | KAL | C-H02 |
| `EPISODE_2023_01_26_31_CORRECTION` (`US_GDP_2023_01_26`, `US_PCE_2023_01_27`) | Yok | KAL | C-H05 |
| `US_FOMC_2023_02_01` | Sayfa yok | KAL | — |
| `EU_BOE_ECB_2023_02_02` + `REGIME_FLIP_2023_02_02` | Yok | 2 Şub: KAL · **3 Şub 09:00 SAT** | C-H03 |
| `MACRO_2023_02_03_NFP` + `US_ISM_SERVICES_2023_02_03` | NFP var | NAKİTTE KAL (zaten satılmış) | C-H04 |
| `EPISODE_2023_02_06_28_HAWKISH_SEQUENCE` (`US_CPI_2023_02_14`, `US_RETAIL_2023_02_15`, `US_PPI_2023_02_16`, `US_PCE_2023_02_24`) | Yok | NAKİTTE KAL | C-H06 |

---

## `MACRO_2023_01_05_ADP` — ikincil istihdam verisiyle kısa düşüş

1. **Takvim/haber:** ADP Aralık +235k (ADP bülteni 2023-01-05; konsensüs bu çalışmada kaynaktan doğrulanmadı). İşsizlik başvuruları 13:30Z 204k. NFP ertesi gün (saati biliniyor, sonucu bilinmiyor).
2. **Sürpriz/rejim:** Hawkish. Rejim UP: trend20 +%2,82, mom10 +%3,75.
3. **XAU:** 15dk −%0,09 · 1s −%0,54 · 4s −%0,79 · 1 seans −%0,72 · 3 seans **+%1,38** · 5 seans +%1,60. 15dk z12 −2,13 (14:00Z).
4. **Çapraz veri:** Açıklama saatinde GC −0,60 · SI −0,28 · ZN **−0,52** · NQ **−1,27** · CL −1,43. Karar anında (16:45 TRT) 24 saatlik: altın −1,04, gümüş −3,16, ZN −0,04, NQ +0,15. Faiz kanalı **teyitli**.
5. **Benzer olaylar (Kip B, 2020–22):** Yükseliş rejiminde hawkish veriyle altın düşüşü, n=8. İlk 4 saatten sonra ortalama −%0,85 ek düşüş; yalnız 1'i %1,62 maliyeti aştı. **Karşıt/Kip A:** 2023-12-08 NFP (UP rejimi, −%1,06/60dk) → 10 seansta +%2,44 toparlanma.
6. **Hipotez:** Tek seferlik ikincil veri şoku; kalan düşüş maliyeti karşılamaz. **Kanıt:** L2 (resmî saat + eşsaatli çoklu piyasa). Nedensel pay ölçülmedi.
7. **Karar:** A2 (altında) **KAL**. A1 (nakitte) **BEKLE**, NFP'yi bekle.
8. **Maliyetli sonuç:** Satıp ertesi gün geri almak ~%1,6 + makas. ChatGPT kaydı (OLAY-02) aynı yönde: SAT→AL alternatifi ≈ 97,2–97,7 $ vs tutma 100,07 $.
9. **Karar anı / sonradan:** 6 Ocak'taki dovish ücret verisi 5 Ocak'ta bilinmiyordu; karar yalnız taban oranına ve maliyete dayanıyor.
10. **Öğrenme bağı:** C-H01 (destek). ChatGPT karşılığı: H-HOLD01.

## `MACRO_2023_01_06_NFP` + `US_ISM_SERVICES_2023_01_06` — yumuşak ücret, UP başlangıcı

1. **Takvim/haber:** 13:30Z BLS: NFP 223k (bkl. 200k), AHE +0,3 (bkl. 0,4; yıllık %4,6 vs %5,0), işsizlik 3,5 (bkl. 3,7). **15:00Z** ISM hizmet 49,6 (bkl. 55,0), 30 ayın ilk daralması (First Trust, Kitco 2023-01-06). ISM, 13:46Z kararından **sonra** geldi.
2. **Sürpriz/rejim:** Karışık; ücret bileşeni dovish. Rejim UP (trend20 +%1,44).
3. **XAU:** NFP 15dk **+%0,65** · 1s +%0,54 · 4s +%1,40 · 1 seans +%1,63 · 3s +%2,24 · 5s **+%3,33**. ISM 15dk +%0,82, 1s +%1,01.
4. **Çapraz veri:** NFP saatinde GC +0,40 · SI +0,74 · ZN +0,31 · NQ +0,18. ISM saatinde GC +1,01 · SI +1,08 · ZN **+0,83** · NQ **+1,59**: geniş “daha az sıkılaştırma” yeniden fiyatlaması. 13:45Z'de NFP saatlik barları henüz tamamlanmamıştı; karar yalnız XAU tepkisi ve gümüşle verildi.
5. **Benzer olaylar (Kip B):** 2022-11-10 CPI (dovish, UP rejimi, +%1,66/60dk, 20 seans +%2,1 devam) · 2022-12-13 CPI (+%1,56, 20s +%3,8). Sınıf (n=11): 10 seans ortalama +%0,33 devam; 3/11 maliyeti aşan ters dönüş. **Karşıt:** 2023-03-10 güçlü NFP'de altın yükseldi (SVB) — güçlü NFP her zaman düşüş değil.
6. **Hipotez:** Ücret yavaşlaması → Fed yolu yumuşar → dolar/faiz ↓ → altın ↑. **Kanıt:** L2.
7. **Karar:** **AL**, 16:45 TRT karar, 16:46 TRT icra.
8. **Maliyetli sonuç:** ASK vekili 1848,87 (M1 1848,69 + 0,18); 0,05365439 ons; ücret 0,80 $. 16 Ocak BID 1917,85 → değer 102,90 $ / satılsa 102,08 $. Bacağın %77'si yakalandı (giriş dipten +%1,15 sonra).
9. **Karar anı / sonradan:** ISM dalgası ve 12 Ocak CPI karar gerekçesinde **yok**.
10. **Öğrenme bağı:** C-H02. ChatGPT karşılığı: H-UP01 (aynı dakika, ASK 1849,30).

## `US_CPI_2023_01_12` — küçük dovish teyit

1. 13:30Z CPI aylık −0,1 (bkl. 0,0), çekirdek 0,3 (beklentide).
2. Hafif dovish; rejim UP (trend20 +%2,85).
3. XAU 15dk +%0,25 · 1s +%0,26 · 4s +%0,45 · 3s +%1,41.
4. 16:45 TRT 24 saatlik: altın +0,64, gümüş +0,67, ZN +0,36 (teyit). CME 1s: GC −0,28 (pencere farkı), NQ −1,21.
5. Benzer: 2022-11 ve 2022-12 CPI.
6. Mevcut UP hipotezini teyit; L2.
7. **KAL** (zaten altında).
8. İşlem yok.
9. —
10. C-H02.

## `EPISODE_2023_01_26_31_CORRECTION` — sürprizsiz veri günlerinde düzeltme (−%2,35)

1. 26 Oca 13:30Z GDP Q4 öncü %2,9 (bkl. ~%2,6), GDP fiyat endeksi %3,5 vs %3,2 (Kitco). 27 Oca PCE Aralık çekirdek +%0,3, yıllık %4,4 — beklentide (Kitco). 31 Oca ECI. FOMC 1 Şubat.
2. Hafif hawkish / sürprizsiz. Rejim UP ama zayıflıyor: mom10 %3,8 → %0,5, trend20 %3,3 → %1,2.
3. M15 MID tepe 26 Oca 06:00Z barı 1948,705 → dip 31 Oca 12:15Z barı 1902,92 (−%2,35). GDP 15dk −%0,23, 4s −%0,56. 15dk z12 en düşük −1,14 (silahlı DOWN başlangıcı yok).
4. 27 Oca 09:00: altın 24s −1,15, ZN −0,53 (faiz ↑). 31 Oca 09:00: altın −0,73, gümüş −1,13, NQ −1,98.
5. Kip A (yorum): atlas SWING_V1_010 (Ara 2023 −%4,4), SWING_V1_014 (Nis 2024 −%4,3), SWING_V1_026 (Şub 2025 −%3,2) — güçlü yükselişin içindeki kâr satışı bacakları sonra devam etti.
6. FOMC öncesi kâr realizasyonu / konsolidasyon; L1–L2.
7. **KAL.**
8. 26 Oca altın kurulumu: 31 Oca net 97,37 $. **Kâhin üst sınırı** (tepede sat, dipte al) 98,11 $ → en iyi durumda +0,74 $.
9. —
10. C-H05; ayrıca **C-H03 ön koşulu (duraklama) bu dönemde gözlendi ve not edildi.**

## `US_FOMC_2023_02_01` — dovish okunan Fed

1. 19:00Z +25bp; Powell 19:30Z “dezenflasyon süreci başladı” (Kitco/Reuters 2023-02-01: DXY −%0,90, 10Y −10,5bp).
2. Dovish okuma; rejim UP (trend20 +%1,22).
3. XAU 15dk −%0,01 · 1s +%0,80 · 4s +%1,46 · 3 seans **−%3,25**.
4. CME 1s: GC +0,84, SI +1,70, ZN +0,54, NQ +1,65. 2 Şub 09:00 TRT: altın 24s +1,38, gümüş +2,06, NQ +3,47.
5. —
6. Ralli dovish yeniden fiyatlama; L2. **24 saat içinde geri verildi** (sonradan bilinen).
7. **KAL.**
8. İşlem yok.
9. Karar anında yalnız rallinin kendisi biliniyordu.
10. C-H03 (geri verilen Fed rallisi bileşeni).

## `EU_BOE_ECB_2023_02_02` + `REGIME_FLIP_2023_02_02` — dolar toparlanması ve rejim dönüşü

1. 12:00Z BoE +50bp, 13:15Z ECB +50bp; ABD başvuruları 183k (bkl. 200k). FXStreet 15:18Z: DXY +%0,44, 10Y −6bp, altın 1959,7 zirveden 1920'ye.
2. ABD dışı; dolar kanalı. **Banka kapanışı 14:00Z (17:00 TRT); büyük düşüş 14:30–15:00Z'de, banka kapandıktan sonra.**
3. 12:00Z'den XAU: 4s −%1,46 · 12s −%2,03 · 3 seans −%4,47. 15dk z12 −2,54 (15:00Z). NY17 kapanış 1912,46 → trend20 **−%0,08**, mom10 −%1,02 → **rejim DOWN**.
4. 1s: GC −0,55, ZN **+0,42** (faiz ↓), NQ +0,75. Altın faiz düşerken düştü → **faiz kanalı değil**. 3 Şub 09:00 TRT pano: altın 24s −1,93, gümüş **−2,94**, ZN +0,22, NQ +1,05. DXY yalnız haber metninden.
5. Kip B: Rejim dönüşü sinyalinin koşulsuz taban oranı ~0 (n=56). Kip A: SWING_V1_024 (Ara 2024 güçlü dolar), E10 (Eki 2025 Fed sonrası ters yön).
6. **Duraklama (Ocak sonu) + şok + rejim dönüşü + gümüş teyidi + faizle açıklanmayan düşüş** → pozisyon çözülmesi, tek seferlik veri tepkisi değil. L1–L2.
7. 2 Şub 16:45: **KAL** (banka saatinde sinyal yok). **3 Şub 09:00 TRT: SAT.**
8. BID vekili 1915,22 (M1 1915,37 − 0,15), 06:01Z. A1 nakit 101,94 $; A2 101,80 $; B (30 Oca altın) 97,57 $ vs tutma 92,99 $. Satıştan 24 Şub kapanışına −%5,44 daha düşüş atlatıldı; 1 Şub kapanışından satışa −%1,80 kaçırıldı.
9. NFP sonucu bu kararda **bilinmiyordu**. Koşulsuz taban oranı satışı desteklemiyor; karar koşullu C-H03 kuralına dayanıyor.
10. **C-H03 (yeni hipotez).** ChatGPT siciline karşılığı yok.

## `MACRO_2023_02_03_NFP` + `US_ISM_SERVICES_2023_02_03` — Fed yolunu değiştiren şok

1. 13:30Z NFP 517k (bkl. 185k), işsizlik 3,4 (bkl. 3,6), AHE beklentide. 15:00Z ISM hizmet 55,2 (bkl. 50,4). Reuters 15:26Z: 2Y +~16–18bp, 10Y +~13bp.
2. Çok hawkish; rejim DOWN (önceki kapanıştan).
3. XAU 15dk **−%1,34** · 1s −%1,72 · 4s −%2,58 · 3s −%2,11 · 5s −%2,72. NFP sonrası hareketin çoğu ilk 4 saatte.
4. 1s: GC −1,73 · SI **−3,31** · ZN **−0,68** · NQ −0,11 · CL +1,71 → faiz/dolar kanalı teyitli, genel likidite tasfiyesi değil.
5. Kip B: DOWN rejiminde hawkish düşüş (n=7) 10 seansta yatay, 20 seansta geri alındı. Ama Fed yolunu değiştiren şoklar sürdü: 2022-09-13 CPI (−%1,70, sonra 10s −%4,7), 2021-06-16 FOMC (−%1,44, sonra −%2,8). Kip A karşıt: 2024-06-07 NFP 272k (C017/E02) sonra +%7,7.
6. Fed yolu yeniden fiyatlaması; L2–L3.
7. **NAKİTTE KAL** (sabah satılmıştı).
8. Yalnız NFP'ye bağlı satış (ChatGPT H-DN01 yolu, BID 1887,31) → B hesabı 96,15 $; sabah satışı 97,57 $.
9. ISM ve Reuters getiri rakamları 16:45 TRT'den sonra.
10. C-H04. ChatGPT karşılığı: H-DN01.

## `EPISODE_2023_02_06_28_HAWKISH_SEQUENCE` — ardışık hawkish veri

1. 14 Şub CPI 0,5 (beklentide) · 15 Şub perakende +%3,0 (bkl. +%1,8; Kitco) · 16 Şub PPI (rakamlar bu çalışmada kaynaktan doğrulanmadı) · 24 Şub PCE çekirdek +%0,6 (bkl. +%0,4), yıllık %4,7 (bkl. %4,3; Kitco).
2. Hawkish dizi; rejim sürekli DOWN (trend20 −%2 ile −%3,4).
3. CPI 1s −%0,60, 3s −%1,32 · perakende 1s −%0,06 · PPI 1s −%0,26 · PCE 1s −%0,30. Ay dibi 28 Şub 08:00Z barı 1807,95.
4. CPI saatinde ZN −0,47; PPI saatinde NQ −0,97; PCE saatinde SI −0,80, NQ −1,00.
5. —
6. “Uzun süre yüksek faiz” anlatısının yerleşmesi; L1–L2.
7. **NAKİTTE KAL.** Geri giriş için ne dovish katalizör ne rejim düzelmesi var.
8. İşlem yok; 28 Şub A1 101,94 $ nakit.
9. —
10. C-H06.
