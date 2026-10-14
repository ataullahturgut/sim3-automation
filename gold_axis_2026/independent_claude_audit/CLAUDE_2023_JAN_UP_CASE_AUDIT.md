# SINAV A — 5–13 Ocak 2023 büyük UP · CLAUDE_INDEPENDENT denetimi

**Kip:** sayısal kararlar `AS_OF_DECISION_EVALUATION`; mekanizma yorumu ayrıca `FULL_HISTORY_DISCOVERY` olarak etiketli. **Statü:** 2023 vakası hindsight'a açık, kör test DEĞİL. Protokol: [CLAUDE_RESEARCH_PROTOCOL.md](CLAUDE_RESEARCH_PROTOCOL.md) (kurallar 2023 koşusundan önce commit `01d6282`, `8c2cea9`, `5ec53a5`).

## 1. Fiyat olayı (EX-POST etiket)

| Ölçü | Değer |
|---|---|
| M15 MID dip | 2023-01-05 15:45Z barı, 1826,90 |
| M15 MID tepe (atlas tanımı) | 2023-01-13 18:45Z, 1921,715 → **+%5,19** |
| Pencere azamisi (16 Ocak'a kadar) | 2023-01-16 02:45Z, 1928,43 → +%5,56 |
| Öncesi | 4 Ocak 08:30Z → 5 Ocak dip: −%1,98 (yükselişin içindeki geçici DOWN) |

## 2. Haber → beklenti → aktarım → fiyat kronolojisi

Saatler UTC (TRT = +3). XAU = EV/Dukascopy M15 MID, release öncesi son tamamlanmış bara göre. CME = depo `.n.0` saatlik, release öncesi tamamlanmış saat → ilk ≥1s sonra biten saat (XAU penceresiyle birebir aynı değil). ZN **fiyattır**; ZN↑ ≈ 10Y getiri↓.

| Zaman | Yeni bilgi (ilk yayın) | XAU 15dk / 1s / 4s / 5 seans | GC / SI / ZN / NQ 1s | Okuma |
|---|---|---|---|---|
| 01-04 15:00 | ISM imalat Ara 48,4; JOLTS (değerler ChatGPT kanıt kaydından; bağımsız yeniden çekilmedi) | −0,37 / +0,04 / −0,35 / +1,07 | +0,04 / −0,64 / −0,15 / −0,14 | Gürültü; yön yok |
| 01-04 19:00 | FOMC tutanakları: 2023'te indirim yok | — | +0,09 / +0,25 / −0,06 / −0,18 | Altında tepki küçük |
| 01-05 13:15 | **ADP Ara +235k** (konsensüs bu çalışmada kaynakla doğrulanmadı); işsizlik başvuruları 204k | −0,09 / −0,54 / −0,79 / **+1,60** | **−0,60 / −0,28 / −0,52 / −1,27** | Faiz kanalıyla teyitli hawkish şok — yine de 1 gün içinde tersine döndü |
| 01-06 13:30 | **NFP 223k vs 200k; AHE 0,3 vs 0,4 (yıllık %4,6 vs %5,0 bkl.); İşsizlik 3,5 vs 3,7** | **+0,65 / +0,54 / +1,40 / +3,33** | +0,40 / +0,74 / +0,31 / +0,18 | Karışık rapor; piyasa ücret yavaşlamasını baskın okudu |
| 01-06 15:00 | **ISM hizmet Ara 49,6 vs 55,0** (30 ay sonra ilk daralma) | +0,82 / +1,01 / +1,36 / +2,90 | **+1,01 / +1,08 / +0,83 / +1,59** | İkinci dalga: getiriler↓, hisse↑, altın↑ — geniş “daha az sıkılaştırma” yeniden fiyatlaması |
| 01-12 13:30 | CPI Ara −0,1 vs 0,0 (çekirdek 0,3 beklentiyle aynı) | +0,25 / +0,26 / +0,45 / +0,89 (3s: +1,41) | −0,28 / −0,36 / −0,06 / −1,21 | Küçük dovish sürpriz; devam ama şok değil |

Kaynaklar (yayın günü): BLS ilk yayımları ve Investing konsensüsleri Neon `observations` (NFP/AHE/UNEMP/CPI); ISM hizmet 49,6/55 — First Trust 2023-01-06 ve Kitco 2023-01-06; ADP 235k — ADP basın bülteni 2023-01-05; FedWatch 6 Ocak sonrası Şubat'ta 25bp olasılığı %74,2 — Kitco 2023-01-06. DXY / 2Y / 10Y düzey ve değişimleri **MISSING** (FRED erişilemedi).

**Ön koşul (3–5 Ocak):** Rejim 29 Aralık kapanışından beri `UP` (trend20 +%1,47, mom10 +%2,64; 3 Ocak'ta +%2,22/+%2,58). Aralık'taki zayıf CPI ve Fed'in 50bp'ye inmesiyle başlamış dolar/getiri gevşemesi altını taşıyordu; 2 Ocak tatil.

## 3. Soruların yanıtları

**5 Ocak düşüşü neden oldu, büyük DOWN mıydı?** ADP ve başvurular sıkı işgücü piyasası → daha uzun yüksek faiz beklentisi; aynı saatte ZN −%0,52, NQ −%1,27, GC −%0,60: faiz kanalı **teyitli**. Ancak yükseliş rejiminin içinde, trend20 hâlâ +%1,44'tü. Ertesi gün gelen iki yeni bilgi (AHE ve ISM) bu yorumu bozdu. **Ex-ante ayırt edici yoktu:** 5 Ocak'taki şok ile 3 Şubat'taki şok aynı imzayı taşıyordu (ZN düşüşü + altın düşüşü). Fark, *sonra* gelen veride ve rejimin olgunluğunda (bkz. Sınav B, H-STALL). Sistem burada SAT vermedi çünkü `ONSET_DOWN` (z12 −2,13, 14:00Z) `REG=UP` iken bastırılıyordu. Bu doğru sonuç verdi, ancak 2020–22 geliştirme verisinde `ONSET_DOWN` sonrası fiyat ortalama +%0,95 **ters** yöne gitti (n=58); yani bastırmanın genel bir mantığı var, Ocak'a özel ayar değil.

**6 Ocak NFP ve ISM nasıl yansıdı?** Başlık NFP ve işsizlik hawkish, AHE dovish. İlk 15 dakikada altın +%0,65 ve ZN +%0,31 → piyasa ücret yavaşlamasını baskın okudu. ISM hizmet 49,6 (beklenti 55) ikinci ve daha büyük dalgayı açtı: ZN +%0,83, NQ +%1,59, GC +%1,01. Bu, “güvenli liman” değil **dolar/getiri gevşemesi** imzası (hisseler de yükseldi).

**9–11 Ocak'ta devam?** Bu günlerde yeni bir birinci derece ABD verisi yok (10 Ocak Powell'ın merkez bankası bağımsızlığı konuşması takvimdeydi; içeriği bu çalışmada kaynaktan doğrulanmadı). Rejim yükselişi taşıdı; z12 9 Ocak 02:30Z'de +3,50'ye çıktı, sonra 9–11 Ocak'ta `PRE_ONSET`'e döndü — **haber yoksa devam da yok** (konsolidasyon). Bu, “devamı açıklayan yeni veri” iddiasını desteklemez.

**12 Ocak CPI ne kadar sürpriz?** Başlık −0,1 vs 0,0, çekirdek beklentide. Altın ilk 15dk +%0,25, 3 seans +%1,41; GC saatlik −%0,28 (pencere farkı). Orta büyüklükte dovish teyit; tek başına yeni şok değil.

## 4. Kararlar (AS_OF, 15dk durum + 1dk icra)

| Varyant | Karar | Zaman (TRT) | Gerekçe | Fill (PROXY) |
|---|---|---|---|---|
| **V-A FULL** | **AL** | 03 Oca 09:01 | `ONSET_UP` z12=+2,38 (04:15Z), REG=UP; banka açılışına kuyruk; 1dk kapısı geçti (M1 05:59 1840,46 vs tetik 1841,92) | ASK 1841,37 |
| V-A | TUT (SAT bastırıldı) | 05 Oca 17:00 | `ONSET_DOWN` z12=−2,13, REG=UP | — |
| **V-B MACRO+REGIME** | **AL** | 06 Oca 16:46 | `MACRO_NFP_UP`: AHE dovish + XAU +%0,646 / 15dk | ASK 1848,87 |
| V-A/V-B | TUT | 12 Oca 17:00 | `MACRO_CPI_UP` (zaten altında) | — |
| V-C REGIME | NAKİT TUT | — | Rejim zaten UP, yeni geçiş yok | — |
| **v2 L50_H2 (dev seçimi)** | **NAKİT TUT** | — | Bant durumu 8 Kasım 2022'den beri UP; yalnız geçişte işlem → giremez | — |

Tüm satırların zaman/kanıt/maliyet alanları: [CLAUDE_EVENT_DECISION_LEDGER.csv](CLAUDE_EVENT_DECISION_LEDGER.csv). 15dk durum geçişleri: [CLAUDE_15M_STATE_TRANSITION_LOG_2023.csv](CLAUDE_15M_STATE_TRANSITION_LOG_2023.csv); tam 15dk kayıt Neon `gold_research_r71_claude_indep_15m_check_log_v1`.

## 5. 100 $ maliyetli portföy (16 Ocak sonu; işaret BID 1917,85)

| Hesap | Açık poz. BID değeri | Şimdi satılsa net | Ücret |
|---|---:|---:|---:|
| **A1 V-A** (3 Oca AL) | 103,32 | **102,49** | 0,80 |
| A1 V-B (6 Oca AL) | 102,90 | 102,08 | 0,80 |
| A1 V-C / **v2 L50_H2 seçilen** | 100,00 | **100,00** | 0 |
| A1 pasif altın (3 Oca 09:01 TRT) | 103,32 | 102,49 | 0,80 |
| A1 nakit | 100,00 | 100,00 | 0 |
| **A2 devralınan 0,05358252 ons** (tüm varyantlar TUT) | 102,76 | **101,94** | 0 ek |

**Giriş anında hareketin ne kadarı gerideydi?** V-A dipten *önce* girdi: %0,77 ters gidişi (MAE) taşıdı, dip→tepe bacağının %85'ini yakaladı. V-B dipten sonra +%1,15 gerçekleşmişken girdi, kalan +%3,95 ile bacağın %77'sini yakaladı. ChatGPT'nin 4 Ocak 07:21Z girişi (MID ~1851,19) bacağın %74'ünü yakalar.

## 6. Bilimsel değerlendirme

* **Ne gerçekten bilgi taşıdı?** 6 Ocak 13:45Z `MACRO_UP` sınıfı: geliştirme döneminde **pozitif beklentiye sahip tek sınıf** (n=16; 10 seans ort. +%0,92, 20 seans +%2,54; 20 seansta %56 maliyeti aşıyor). 2023'te gerçekleşen 5/10/20 seans +%2,62/+%4,51/+%3,45 — beklentinin üstünde ama aynı işaret.
* **Ne yanıltıcıydı?** 3 Ocak `ONSET_UP` tek başına: geliştirme ortalaması ~0 (n=69). 2023'te kazandırdı (5/10/20 seans +%1,65/+%3,95/+%4,44) ama bu **şans/rejim** olarak okunmalı. Ayrıca 5 Ocak'taki faiz-teyitli hawkish şok, “bağımsız ikinci piyasa teyidi = güvenilir sinyal” fikrini yanlışlıyor.
* **Seçilen v2 neden başarısız?** “Yalnız geçişte işlem” kuralı, zaten süren bir trende nakitle başlayan hesabı dışarıda bırakıyor. İkincil “state-follow” yorumu pasif altınla aynı sonucu verir (102,49). Bu, protokolün metninden kaynaklanan bir tasarım hatası; sonradan değiştirilmedi.
* **Kanıt seviyesi:** Haber saati + eşsaatli XAU/ZN/GC/SI/NQ tepkisi → **L2**; MACRO_UP için dev taban oranı ile karşılaştırma → **L3'e yakın**, fakat n=16 ve 2023 hindsight. **L4 yok.**
