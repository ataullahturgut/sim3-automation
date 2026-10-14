# CLAUDE_INDEPENDENT — Bulgular, yanlışlanan varsayımlar, belirsizlikler ve ChatGPT karşılaştırması

**Tarih:** 2026-10-14 · **Statü:** RESEARCH ONLY · 2023 vakaları hindsight'a açık · L4 kanıt yok.

## 0. Dosya dizini

| Dosya | İçerik |
|---|---|
| [CLAUDE_RESEARCH_PROTOCOL.md](CLAUDE_RESEARCH_PROTOCOL.md) | Ön kayıt, v1 dev başarısızlığı, v2 ön kaydı ve seçimi (hepsi 2023 koşusundan önce commit) |
| [CLAUDE_2023_JAN_UP_CASE_AUDIT.md](CLAUDE_2023_JAN_UP_CASE_AUDIT.md) | Sınav A (A1 bağımsız, A2 ortak pozisyon) |
| [CLAUDE_2023_JAN_CORRECTION_CONTROL.md](CLAUDE_2023_JAN_CORRECTION_CONTROL.md) | Sınav C |
| [CLAUDE_2023_FEB_DOWN_CASE_AUDIT.md](CLAUDE_2023_FEB_DOWN_CASE_AUDIT.md) | Sınav B |
| [CLAUDE_EVENT_DECISION_LEDGER.csv](CLAUDE_EVENT_DECISION_LEDGER.csv) | Kullanıcının 18 alanlı karşılaştırma şeması + varyant/kip/TRT |
| [CLAUDE_COSTED_BACKTEST_RESULTS.json](CLAUDE_COSTED_BACKTEST_RESULTS.json) | Dev 2020–22, taban oranları, 2023 portföyleri |
| [CLAUDE_15M_STATE_TRANSITION_LOG_2023.csv](CLAUDE_15M_STATE_TRANSITION_LOG_2023.csv) | 185 satır: 15dk aşama/rejim değişimleri ve tüm sinyaller (yalnız türetilmiş alanlar) |
| [CLAUDE_2023_KEY_RELEASES_CME_N0_H1_REACTIONS.csv](CLAUDE_2023_KEY_RELEASES_CME_N0_H1_REACTIONS.csv) | 18 açıklamada GC/SI/ZN/NQ/CL 1s/4s getirileri |
| [CLAUDE_R71_NEON_REPRODUCTION.sql](CLAUDE_R71_NEON_REPRODUCTION.sql) | Neon araştırma tablolarını ve simülatörü yeniden kuran SQL |

Tam 15dk kontrol kaydı (3.102 satır vaka penceresi) ham fiyat içerdiği için depoda değil; Neon `gold_research_r71_claude_indep_15m_check_log_v1`.

## 1. Ana bulgular (kısa)

1. **Maliyet yapısı belirleyici.** %0,8+%0,8 ile 2020–22'de önceden kaydedilmiş üç olay/rejim varyantının hepsi 100 $'ı 59–73 $'a indirdi (37–50 $ ücret). Pasif altın 118 $. Bu maliyette 15dk/20 seans ölçeğinde sık pozisyon değiştirmek yapısal olarak kaybettiriyor.
2. **2023 Ocak–Şubat, geliştirme döneminden çok daha “trend sürekli” bir rejimdi.** Aynı başarısız varyantlar 2023'te pasifi geçti (V-A 102,35 vs pasif 97,55). Bu bir **rejim tesadüfü** olarak kaydedilmelidir; üstünlük kanıtı değildir.
3. **Dev'de seçilen tek yapılandırma (v2 L50_H2) 2023'te en kötü varyant:** Ocak yükselişini kaçırdı (nakit), Şubat düşüşünü 3 hafta geç gördü ve 1dk kapısı yüzünden hiç icra edemedi. **Dev seçimi 2023'e taşınmadı.**
4. **Pozitif ex-ante beklentisi olan tek sınıf `MACRO_UP`** (dovish bileşenli NFP/CPI/FOMC + 60dk içinde XAU ≥ +%0,40): dev n=16, 20 seansta ort. +%2,54. 6 Ocak bunun örneği. Örneklem küçük.
5. **Sınav C'de sistem doğru biçimde hiçbir şey yapmadı.** Kâhin bile +0,74 $'dan fazla kazanamazdı.

## 2. Yanlışlanan / zayıflatılan varsayımlar

| Varsayım | Test | Sonuç |
|---|---|---|
| “Bağımsız faiz piyasası (ZN) teyidi, haber şokunu güvenilir kılar” | 5 Ocak ADP: ZN −%0,52 + altın −%0,60 → 3 seansta altın +%1,38 | **Yanlışlandı** (teyitli şok tersine döndü) |
| “Altının düşüşü faiz kanalıyla gelir” | 2 Şub: altın −%1,46/4s, ZN **+%0,42**, NQ +%1,74 | **Yanlışlandı** (USD/pozisyon kanalı; DXY verisi eksik) |
| “Güçlü NFP ⇒ altın düşer” | 6 Ocak NFP 223k>200k ama altın +%0,65/15dk; depo kaydı: 10 Mar 2023 NFP +106k sürpriz, altın +%0,54 (SVB) | **Deterministik kural reddedildi**; bileşen (AHE) ve eşzamanlı başka şok belirleyici |
| “Şok sonrası ilk dalgadan sonra büyük kalan hareket vardır” | 3 Şub NFP: 4s −%2,58 vs 5 seans −%2,72; 6 Ocak: 4s +%1,40 vs 5 seans +%3,33 | **Karışık**: biri bitmiş, diğeri devam etmiş; ilk 4 saatten ayırt edilemedi |
| “15dk z-şok onset'i yön bilgisi taşır” | Dev 2020–22: ONSET_UP 10 seans ort. −%0,01 (n=69); ONSET_DOWN +%0,95 **ters** (n=58) | **Yanlışlandı** (DOWN onset'ler ortalamada geri dönüyor) |
| “Günlük rejim dönüşü maliyeti karşılar” | Dev: REG_FLIP 10 seans ±%0,4 civarı, %32–34'ü maliyeti aşar | **Desteklenmedi** (2023 hariç) |
| “Kovalamama 1dk kapısı her sinyalde faydalı” | 23 Şub v2 satışını 4 denemede reddetti, sinyal düştü | **Yavaş sinyallerle uyumsuz** (tasarım hatası) |

## 3. Kip A — keşif notları (geriye dönük, karar girdisi DEĞİL)

* **H-STALL (yeni hipotez):** Uzun bir yükselişin ardından 2+ hafta yatay seyir (trend20'nin SMA20 yetiştikçe erimesi) varken gelen hawkish şok rejimi döndürür; trend genç ve SMA'dan uzakken (5 Ocak: trend20 +%1,44, rejim tutuldu) aynı şok emilir. 2 Şub dönüşü SMA20'nin yalnız **%0,08** altında gerçekleşti → kenar durumu; eşik %0,1 farklı olsaydı sonuç değişirdi. **Sınama önerisi:** 2023-03 → 2025 arasındaki 42 V1 dönüm noktasında “dönüş öncesi 10 seanslık yatay/aralık oranı” ile sonraki 10 seans yönü (dokunulmamış 2024–25 ile, kural 2023'te dondurularak).
* **Depo atlasıyla tutarlı karşı örnekler:** 7 Haz 2024 (PBoC alım duruşu 09:42Z + NFP 272k 12:30Z — çift katalizör), 18 Ara 2024 FOMC (altın −%0,76/15dk, hisse ve tahvil birlikte düştü), Nisan 2025 (önce likidite satışı, sonra güvenli liman). Bunlar “aynı haber türü, rejime göre farklı sonuç” örüntüsünü destekler; 2023 kararlarına girdi olarak **kullanılmadı**.

## 4. Belirsizlikler ve veri boşlukları

* **USD/DXY ve 2Y/10Y/TIPS gün içi ve günlük veri yok** (FRED proxy politikası; WebFetch 429). Faiz kanalı yalnız ZN vadeli fiyatıyla; USD kanalı yalnız haber metinlerindeki rakamlarla (L1).
* XAU fiyatı EV/Dukascopy türevi, non-PIT; **banka BID/ASK değil**. 2023 fill'leri M1 MID ± son M15 yarım makas (PROXY_FILL). Gerçek Türk bankası makası muhtemelen daha geniş → tüm net sonuçlar **iyimser**.
* Banka penceresi 09:00–17:00 TRT varsayımdır; NFP/CPI 16:30 TRT'de, FOMC 22:00 TRT'de (pencere dışı). Pencere farklıysa Şubat çıkış fiyatı değişir.
* FOMC path faktörünün “+30dk'da biliniyor” varsayımı yaklaşık; 2023-02-01'de makro sinyal üretmediği için bu vakalarda sonuç etkilemedi.
* Makro sınıfı ISM/ADP/PCE/GDP/perakende/PPI'yi kapsamıyor (dev'de ilk-yayın serisi yok). 6 Ocak ve 3 Şubat ISM hizmet dalgaları sınıf dışında kaldı.
* 2020–22 dev döneminde NFP Eylül 2020 satırı eksik; COVID 2020 aşırı oynaklığı σ15'i şişiriyor.
* Ex-post anchorlar (1826,90 / 1921,715 / 1948,705 / 1902,92 / 1959,615 / 1807,95) M15 **bar kapanış MID**; bar içi uçlar değil.

## 5. ChatGPT ile karşılaştırma (yalnız depodaki kayıtlarla)

| Konu | ChatGPT (depo kaydı) | Claude | Fark türü (kullanıcının 1–7 listesi) |
|---|---|---|---|
| İlk AL | Takdirî: 4 Oca 07:21Z, ASK vekili 1851,35 (1850 kırılımı + 5×1dk). Kural “EVENT3”: 4 Oca 08:15Z ASK 1859,72 (4 seansa göre ≥%3) | V-A: 3 Oca 06:01Z ASK 1841,37 (z12 onset 04:15Z); V-B: 6 Oca 13:46Z ASK 1848,87 (makro) | **1** (aynı fiyatın farklı yorumu: z-ölçekli 12s vs 4 seans %3) ve **5**. Claude V-A ~10 $/ons ucuz girdi, ama V-A sınıfının dev beklentisi ~0. |
| 5 Ocak düşüşü | TUT (geçici düzeltme yorumu) | TUT (`ONSET_DOWN` REG=UP ile bastırıldı) | **Uyum** |
| A2 ortak pozisyon | TUT | Tüm varyantlar TUT → 16 Oca net 101,94 | **Uyum** |
| 26–31 Ocak | EVENT3: DOWN eşiği aşılmadı; 31 Oca 22:00Z **deneysel ay sonu tasfiyesi** (sinyal değil) → 101,99 | TUT, sinyal yok; ay sonu tasfiye yok | **4** (muhasebe: ChatGPT ayı kapatmak için sattı) |
| Şubat | Depoda Şubat kararı yok (`STATE.json`: Şubat aktarımı BLOCKED) | V-A/V-B/V-C 3 Şub 06:01Z SAT; v2 icra edemedi | Karşılaştırılamaz (ChatGPT kaydı yok) |
| Maliyet | %0,8+%0,8, M15/M1 vekil BID/ASK | Aynı | Uyumlu |
| Gelecek bilgisi | 4 Oca kaydı JOLTS/minutes'ın alımdan sonra geldiğini açıkça belirtiyor | Tüm sinyaller tamamlanmış barlar; makro yalnız açıklama sonrası | İki tarafta da tespit edilen sızıntı yok |

**Neden farklı?** Temel fark sinyal ölçeği: ChatGPT'nin EVENT3 kuralı mutlak %3 eşiği kullanıyor (geç ve pahalı giriş), takdirî kararı fiyat kırılımına dayanıyor; Claude'un V-A'sı oynaklık-ölçekli 12 saatlik şoka dayanıyor. 2023'te erken giriş kazandırdı, ama Claude'un kendi dev testi bu sınıfın ortalamada kazandırmadığını gösteriyor — **hangisinin “daha doğru” olduğu bu üç vakayla belirlenemez.**

## 6. Sonraki aşamaya ne taşınmalı?

1. **Taşınacak:** (a) maliyet-önce yaklaşım ve dev'de taban oranı ölçümü; (b) `MACRO_UP` sınıfı (dovish bileşen + 60dk fiyat teyidi), daha geniş takvimle (ISM/PCE/PPI ilk yayınları eklenerek) yeniden test; (c) rejim bastırmasının DOWN onset'lerde kullanımı (dev'de onset'ler geri dönüyor).
2. **Taşınmayacak:** 15dk onset ile tek başına işlem; ZN'yi “bağımsız teyit” sayan kurallar; yalnız-geçişte-işlem yapan yavaş rejim; yavaş sinyallerde kovalamama kapısı.
3. **Gerekli veri:** DXY/EURUSD ve 2Y/10Y gün içi (aynı UTC), gerçek banka kotasyonu ve işlem saatleri, ISM/ADP/PCE/PPI/perakende ilk-yayın + konsensüs arşivi.
4. **Doğrulama tasarımı:** Kuralları **şimdi dondur**, 2024-01 → 2025-12 (bu çalışmada hiç koşulmadı) üzerinde tek seferlik test; UP/DOWN recall, yanlış alarm, gecikme, kalan hareket, net 100 $ ve pasif fark raporlanır. 2023–2026 ile **ileri işlem başarısı iddia edilmez**.
5. **Büyük DOWN'larda yanlış satışı azaltmak için:** H-STALL ön koşulu (yatay süre + SMA yakınlığı) ile şok büyüklüğünü birleştiren, maliyet-duyarlı (beklenen kalan hareket > %2) bir çıkış kapısı; geliştirme 2020–22, test 2024–25.
