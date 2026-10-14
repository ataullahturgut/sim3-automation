# CLAUDE_INDEPENDENT — Haber/veri → olay örgüsü eşleştirmesi → KAL / ÇIK / GİR kararları (Ocak–Şubat 2023)

**Tarih:** 2026-10-14 · **Bu dosya birincil karar raporudur.** Önceki mekanik kural backtest'i ([CLAUDE_RESEARCH_PROTOCOL.md](CLAUDE_RESEARCH_PROTOCOL.md), V-A/V-B/V-C, L50_H2) kullanıcının istediği yöntem değildi; yalnız yan bulgu olarak saklanır.

**Yöntem (her karar anında):**
1. O dakikaya kadar yayımlanmış veri/haber (ilk yayın, sürpriz) ve fiyat durumu.
2. Zincir: ön koşul → tetikleyici → beklenti sürprizi → aktarım (faiz/dolar/pozisyon) → teyit / karşıt kanıt.
3. **Olay örgüsü eşleştirmesi** iki katmanda:
   * **Kip B (karara girdi):** yalnız karar tarihinden ÖNCE gerçekleşmiş analoglar — 2020–2022 makro olayları ([eşleştirme tablosu SQL'i](CLAUDE_R72_ANALOG_TABLES.sql), Neon `gold_research_r72_claude_macro_analogs_v1`).
   * **Kip A (yalnız yorum/öğrenme):** manifest atlası 2023–2025 kayıtları (SWING/C_CORR, E01–E10). Bunlar 2023 kararına **gerekçe yapılmadı**; yalnız “sonradan bakınca bu örüntü nerede tekrarladı” sütununda.
4. KAL / ÇIK / GİR / BEKLE kararı, %0,8+%0,8 maliyet ve 09:00–17:00 TRT banka penceresiyle. Fill = karar dakikasından sonraki M1 MID ± son M15 yarım makas (PROXY_FILL).

**Hindsight uyarısı:** Bu üç vakanın sonucunu biliyorum. Kararları yalnız o an bilinenle gerekçelendirdim ve her kararda karşıt kanıtı ve alternatif yolu sayısal gösterdim; yine de bu bir kör test değildir.

---

## 1. Eşleştirme kütüphanesinin özeti (2020–2025 NFP/CPI/FOMC, 60dk ≥%0,4 tepki, n=89)

“Devam” = ilk 4 saatten sonra, **ilk tepkinin yönünde** kalan hareket (pozitif = aynı yönde sürdü, negatif = geri alındı).

| Durum | Dönem | n | Kalan hareket ort. 10s | 20s | Maliyeti aşan devam / maliyeti aşan ters |
|---|---|---:|---:|---:|---|
| Hawkish veri, altın ↓, rejim **UP** | **2020–22 (Kip B)** | 8 | **+0,85 (hafif devam)** | −0,01 | 1 / 0 |
| aynı | 2023–25 (Kip A) | 8 | −1,96 (geri alındı) | −2,85 | 1 / 4 |
| Hawkish veri, altın ↓, rejim **DOWN** | **2020–22** | 7 | +0,07 (yatay) | −2,37 (geri alındı) | 2 / 2 |
| Dovish veri, altın ↑, rejim **UP** | **2020–22** | 11 | +0,33 | +0,19 | 5 / 3 |
| aynı | 2023–25 | 14 | +1,02 | +1,80 | 6 / 2 |

**Okuma:** 2020–22'de hawkish düşüşler ilk 4 saatten sonra ortalama biraz daha sürdü ama yalnız nadiren %1,62'lik tur maliyetini aştı; 2023–25'te aynı düşüşler çoğunlukla geri alındı. Ortalama kal/çık kararını tek başına vermiyor. Bu yüzden her kararda **adı konmuş analoglara** ve şokun türüne (tek seferlik veri mi, Fed yolu yeniden fiyatlaması mı) bakıldı.

---

## 2. Karar kayıtları

### K1 — 3–5 Ocak: NAKİTTE BEKLE (A1)
* **Biliniyor:** Ara CPI zayıf (13 Ara), Fed 50bp'ye indi (14 Ara); rejim UP (trend20 +%2,2). 4 Ocak ISM imalat 48,4, FOMC tutanakları “2023'te indirim yok”. Önümüzde 6 Ocak NFP.
* **Analog (Kip B):** UP rejiminde **hawkish NFP**: 2022-08-05 (altın −%1,02/60dk, sonra 20 seansta −%4,2 daha), 2022-10-07 (−%0,53, sonra −%4,4), 2022-12-02 (−%0,70, sonra 10s −%1,1). UP rejiminde **dovish CPI**: 2022-11-10 (+%1,66, 20s +%2,1), 2022-12-13 (+%1,56, 20s +%3,8).
* **Karar:** Yükseliş rejimi var ama sonraki büyük katalizör NFP iki yönlü ve 2022'de UP rejimdeki üç hawkish NFP'de altın 60dk'da −%0,5 ile −%1,0 düştü, ikisinde düşüş sonraki haftalarda da sürdü. %1,6 maliyetle katalizörden önce girmek yerine **teyit beklenir**.
* **Alternatif:** ChatGPT 4 Ocak 10:21 TRT'de girdi (1851,35) ve 5 Ocak düşüşünü taşıdı. Bu karar 6 Ocak'ta %0,13 daha ucuza (1848,87) girdi; bekleme bu sefer maliyetsizdi, ama NFP güçlü gelseydi yükselişin devamı kaçırılabilirdi.

### K2 — 5 Ocak 16:15–17:00 TRT (ADP 235k): A2 için ALTINDA KAL
* **Biliniyor:** ADP 235k, başvurular 204k → sıkı işgücü; altın −%0,54/60dk, ertesi gün NFP.
* **Analog (Kip B):** UP rejiminde hawkish veriyle altın düşüşlerinden sonra (n=8) 10 seansta ortalama yalnız −%0,85 ek düşüş oldu; 8'inden yalnız 1'i %1,62 tur maliyetini aştı. Beklenen ek düşüş maliyetin altında. ADP ikincil veri; asıl karar verisi NFP 24 saat sonra.
* **Karar:** Satmak + NFP sonrası geri almak ~%1,6 maliyet. Tek seferlik, ikincil veri şoku → **KAL**.
* **Kip A notu:** 2023-12-08 NFP (UP rejimi, −%1,06/60dk) sonrası 10s +%2,4 toparlandı — aynı örüntü.

### K3 — 6 Ocak 16:45 TRT (NFP 223k, **AHE 0,3 vs 0,4**, işsizlik 3,5): A1 **AL**
* **Biliniyor:** Başlık güçlü ama ücret artışı beklentinin altında; altın +%0,65/15dk. Piyasa ücret yavaşlamasını Fed için baskın okuyor.
* **Analog (Kip B):** UP rejiminde dovish tepki: 2022-11-10 CPI, 2022-12-13 CPI — ikisinde de “dezenflasyon → faiz/dolar ↓ → altın ↑” devam etti. Sınıf ortalaması küçük (+%0,33 / 10s), ama **aynı anlatının aynı rejimdeki son iki örneği** devam etti.
* **Karşıt kanıt:** NFP ve işsizlik hawkish; sınıfın %27'si ters döndü (3/11).
* **Karar:** **AL**, 16:46 TRT, ASK vekili **1848,87** (M1 1848,69 + 0,18). Saat 18:00 TRT'deki ISM hizmet 49,6 (bkl. 55) ikinci dalgayı açtı ama karar ondan önce verildi.
* **Kalan hareket (ex-post):** 13 Ocak tepesine +%3,95; bacağın %77'si.

### K4 — 12 Ocak CPI (−0,1 vs 0,0): KAL
Dovish ama küçük sürpriz; anlatıyı teyit ediyor. Satma gerekçesi yok.

### K5 — 26–31 Ocak düzeltmesi (−%2,35): KAL
* **Biliniyor:** GDP 2,9 vs ~2,6 (hafif hawkish), PCE çekirdek beklentide, ECI; büyük sürpriz yok. 9 ayın zirvesinde yatay seyir; FOMC 1 Şubat'ta.
* **Analog:** Kip B — UP rejiminde sürprizsiz veri günleri anlamlı devam üretmedi. Kip A (yorum) — manifest atlasında güçlü yükseliş içindeki kâr realizasyonu bacakları: SWING_V1_010 (Ara 2023, −%4,4), SWING_V1_014 (Nis 2024, −%4,3), SWING_V1_026 (Şub 2025, −%3,2) hepsi sonra yukarı devam etti.
* **Karar:** **KAL.** Kusursuz zamanlamayla bile sat-geri al en fazla +0,74 $ kazandırırdı ([Sınav C](CLAUDE_2023_JAN_CORRECTION_CONTROL.md)).

### K6 — 1 Şubat FOMC (+25bp, Powell “dezenflasyon başladı”): KAL
Dovish okuma, dolar −%0,9, 10Y −10bp, altın 9 ayın zirvesine. Anlatı sürüyor.

### K7 — 2 Şubat (BoE/ECB +50bp) ve 3 Şubat 09:00 TRT: KAL — **bu kararın maliyeti oldu**
* **Biliniyor (2 Şub banka kapanışına kadar, 14:00Z):** BoE/ECB kararları; dolar toparlanıyor. Büyük düşüş 14:30–15:00Z'de, **banka kapandıktan sonra** geldi. 3 Şub 09:00 TRT: altın zirveden −%2,3 (1915), 2 Şub NY17 kapanışı 20 seans ortalamasının %0,08 altında; NFP 7,5 saat sonra.
* **Analog (Kip B):** Bu ABD verisi değil; dolar kaynaklı tek günlük geri verme. 2020–22'de UP rejimindeki hawkish düşüşlerin devamı ortalama maliyetin altında kaldı. NFP'den önce satıp NFP'den sonra geri almak çift maliyet.
* **Karar:** **KAL**, NFP'yi bekle.
* **Alternatif (sayısal):** 3 Şub 09:01 TRT'de satış (BID 1915,22) → B hesabı **97,57 $** olurdu; bu karar NFP sonrası satışla **96,15 $**'da kaldı. **Fark −1,42 $.** Bu, 2 Şubat sinyalini “dolar gürültüsü” diye okumanın bedeli.

### K8 — 3 Şubat 16:45 TRT (NFP 517k vs 185k, işsizlik 3,4 — 1969'dan beri en düşük): **ÇIK (SAT)**
* **Biliniyor (13:45Z):** Konsensüsün 332k üstünde istihdam, en düşük işsizlik; altın −%1,34/15dk. Önceki günden beri rejim zayıf (DOWN sınırında). ISM henüz yok (15:00Z, banka kapalı).
* **Asıl soru:** Bu tek seferlik bir veri şoku mu, yoksa Fed yolunun yeniden fiyatlanması mı?
  * **Tek seferlik lehine (Kip B):** DOWN rejimindeki hawkish düşüşler 2020–22'de 10 seansta ortalama devam etmedi (+%0,07), 20 seansta geri döndü. 2022-02-04 NFP +317k: altın −%0,74, sonra 10s +%5 (ancak Ukrayna savaşı araya girdi).
  * **Fed yolu yeniden fiyatlaması lehine (Kip B):** 2022-09-13 CPI (−%1,70/60dk, sonra 10s −%4,7 daha) ve 2021-06-16 FOMC (−%1,44, sonra −%2,8 daha) — **beklenti çapasını değiştiren** şoklar devam etti. 3 Şubat'ın sürprizi (332k) yakın tarihin en büyüğü ve 1 Şubat'taki “Fed duruyor” anlatısını doğrudan yalanlıyor; bir önceki gün dolar zaten dönmüştü.
* **Karar:** **SAT**, 16:46 TRT, BID vekili **1887,31** (M1 1887,51 − 0,21). Güven: orta-düşük; taban oranı satışı desteklemiyor, analog türü destekliyor.
* **Teyit (karardan sonra gelen, karar girdisi değil):** 15:00Z ISM hizmet 55,2 (bkl. 50,4); Reuters 15:26Z: 2Y +~16–18bp, 10Y +~13bp. ZN.n.0 1s −%0,68, gümüş −%3,31.
* **Kalan hareket (ex-post):** 24 Şub kapanışına −%4,05, 28 Şub dibine −%4,22. 1 Şub kapanışından satışa kadar −%3,23 kaçırıldı.
* **Kip A notu:** 7 Haziran 2024 NFP 272k (C017/E02) — aynı tür sürpriz, sonra +%7,7 yükseliş: aynı haberin farklı rejimde ters sonuç verdiği karşı örnek. Fark: 2024'te Fed indirim döngüsü yaklaşıyordu ve merkez bankası talebi vardı; Şubat 2023'te piyasa indirim fiyatlıyordu ve veri onu yalanladı.

### K9 — 14–28 Şubat: NAKİTTE KAL
CPI 0,5 (beklentide ama yüksek), perakende +%3,0 vs +%1,8, PPI, PCE çekirdek 0,6 vs 0,4: **ardışık hawkish veri dizisi**. Geri giriş için dovish katalizör yok → **KAL (NAKİT)**. Yeniden giriş tetikleyicisi bu pencerede yok (SVB, 10 Mart, pencere dışı).

---

## 3. 100 $ sonuçları

| Hesap | Kararlar | Sonuç |
|---|---|---:|
| **A1** (3 Oca nakit) | Bekle → 6 Oca AL 1848,87 → 3 Şub SAT 1887,31 → nakit | 16 Oca: BID 102,90 / net 102,08 · **28 Şub: 100,45 $ nakit** (ücret 0,80+0,81) |
| **A2** (devralınan 0,05358252 ons) | Kal → 3 Şub SAT 1887,31 | **28 Şub: 100,32 $** (16 Oca: 102,76 / net 101,94) |
| **C** (26 Oca altın) | Kal | 31 Oca: 98,16 / net 97,37 (kâhin üst sınır 98,11) |
| **B** (30 Oca altın, ASK 1931,64) | Kal (2 Şub) → 3 Şub SAT | **96,15 $** · tut 92,99 · 3 Şub sabah satışı 97,57 |
| Pasif altın (3 Oca → 28 Şub) | — | net **97,55 $** |
| Nakit | — | 100,00 $ |
| (Yan bulgu) mekanik rejim kuralı V-A | 3 Oca AL / 3 Şub 09:01 SAT | 102,35 $ |

## 4. Değerlendirme

* **İşe yarayan:** Ocak'ta katalizör teyidiyle giriş (K3), sürprizsiz düzeltmede ve ikincil veri şokunda kalma (K2, K5) ve Şubat'ta “Fed yolu yalanlandı” analoğuyla çıkış (K8). Pasife göre +2,90 $, nakde göre +0,45 $.
* **Yanlış giden:** 2 Şubat'taki dolar kaynaklı dönüşü “gürültü” saydım (K7). Ocak kazancının çoğu geri verildi; mekanik rejim kuralı burada daha iyiydi (−1,42 $ fark). Ders: **Fed sonrası rallinin 24 saatte tamamen geri verilmesi** kendi başına bir olay örgüsüdür; bir sonraki sürümde bunu atlas/analog kütüphanesine ayrı bir sınıf olarak eklemeliyim (Kip A adayları: SWING_V1_024 Ara 2024, E10 Eki 2025 Fed sonrası ters yön).
* **Kanıt seviyesi:** K3 ve K8'de resmî saat + eşsaat XAU tepkisi + adlandırılmış Kip B analogları → **L2**. Taban oranları K8 kararını desteklemiyor → güven orta-düşük. **L3/L4 yok.**
* **Eksik veri:** Gün içi DXY ve 2Y/10Y getirileri yok. K7 ve K8 kararlarındaki dolar/faiz kanıtı yalnız haber metinlerinden.

## 5. Sıradaki iş (önerim)

1. Bu yöntemi **Mart 2023 (SVB)** ile sürdürmek: banka stresi + NFP aynı gün, analogsuz yeni aile — gerçek bir test.
2. Analog kütüphanesine ISM, PCE, PPI, perakende ve ADP ilk yayımlarını eklemek. 6 Ocak ve 3 Şubat'taki ISM dalgaları şu an kütüphanede yok.
3. “Fed sonrası ralli 24 saatte geri verildi” ve “ardışık hawkish veri dizisi” örgülerini sınıf olarak tanımlayıp 2023–2025 atlasında saymak.
