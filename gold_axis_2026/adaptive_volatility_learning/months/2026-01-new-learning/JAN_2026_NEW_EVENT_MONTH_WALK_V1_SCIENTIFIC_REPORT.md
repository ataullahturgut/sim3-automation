# OCAK 2026 — YENİ OLAY-ÖĞRENME İLE AYLIK KORUMA YÜRÜYÜŞÜ (V1)
**15 Ekim 2026** | **Gerçek test ayı: OCAK 2026** | `RESEARCH / RETROSPECTIVE / NOT_BLIND / NOT_LIVE`
**Amaç:** 100 USD nakit başlangıç, büyük UP ve DOWN şoklarına odaklanan seyrek işlemli altın koruma.
**Önceki silinmiş Ocak 2026 deneyi yeniden oluşturulmadı.** Tüm yeni veriler `2026-01-new-learning/` altındadır. **Ocak 2023 değil.**

## 1. Nihai denetlenen sonuç
| 2026 Ocak 100 USD | Net sonuç |
|---|---:|
| Önceki 3h fiyat kontrolü (aynı komisyon, başka sıklık) | **$118.337853 (+%18.337853)** |
| Yeni 15m fiyat kontrolü | **$119.753917 (+%19.753917)** |
| Yeni 15m + 2023–25 OLAY-02 benzerlik/şok aday katmanı | **$119.753917 (+%19.753917)** |
| Aynı 15m kaynakta Ocak ilk uygun open–son mevcut close altın pasifi | **$111.195133 (+%11.195133)** |
| Maksimum varsayımsal tasfiye portföy geri çekilmesi | **%3.61253** |

- Alış komisyonu %0,8, satış komisyonu %0,8; gerçek Türk bankası BID/ASK makası, kur, stopaj, emir uygulama ve slippage **yok**.
- V1 iyileşmesinin **$1.416064** kısmı kontrollerin 3 saatten 15 dakikaya düşmesiyle daha erken giriş/çıkışa denk geldi, **olay DNA katmanının işlem ve net P&L marjinal katkısı $0**.
- Pasif altın benchmark'ı ilk 2026-01-01 00:00 TSİ M15 next OPEN **4313.305** ve son eldeki M15 close **4873.855** ile ölçüldü. Son gözlem **2026-01-31 00:30 TSİ**; 31 Ocak 23:45'e kadar piyasa veri yok. Eski 3h koşusunun daha erken son kontrolünde pasif benchmark **$110.57807** olduğu için iki pasif benchmark doğrudan aynı son fiyatla değildir.
- Portföy **29 Ocak'tan sonra NAKİT** kaldı, Ocak sonu fiilî nakit **$119.753917**, Şubat'a devredilir; hiçbir teorik ay sonu ilave satışı yapılmadı.

## 2. Gerçek iki işlem
| Türkiye saati | Eylem | Sonraki tamamlanmış 15m/open MID vekili | Karar kanıtı |
|---|---|---:|---|
| **5 Ocak 2026 09:30** | **AL** | **$4,424.055 / ons** | 92 M15 +%1.00534, 276 M15 +%1.16125, 16 M15 +%0.49730, zirve mesafesi >=-%3.5, son 92 M15 range %2.69994 |
| **29 Ocak 2026 18:15** | **SAT** | **$5,383.775 / ons** | 16 M15 -%2.2366; son 6 tamamlanmış NQ H1 -%1.46388; RV4 anormal; 2023–25 olay profili en yakın uzaklığı 1.27992 (OOD/bilinmeyen şok); aynı anda eski fiyat trailing koşulu da satış derdi |

Alımdan sonra hesap: `100*0.992/4424.055=0.02242286770847 XAU`.
Satımdan sonra hesap: `0.02242286770847*5383.775*0.992=119.7539172 USD`.

## 3. Modelin gerçek karar soruları ve olay mekanizması
**ANA-01/ÖĞREN-03/OLAY-02** sözleşmelerinden:
1. **UP başladı mı?** 16/92/276 M15 ve geriye dönük tepe/dip/volatilite özelliklerinde makul devam kanıtı var mı?
2. **Görülmüş benzer olaylar hangileri?** Ocak 2026 ilk kararında 96h gelecek fiyat sonucu olgunlaşmış **92** tarihi kesit (2023–2025); `C_CORR_054` olgunlaşmadığı için dışlandı.
3. **Olay hangi evrede?** `P0_PRICE_STATE_UNKNOWN_CAUSE`, yayımlanmış G01 takviminin ardından `P2_G01_RELEASE_OBSERVED_CAUSE_UNRESOLVED`, eşzamanlı satış baskısında `P2_CROSS_MARKET_SELLING_CANDIDATE`, arşiv kapsam dışı `P2_OUT_OF_DISTRIBUTION_MOVE_UNKNOWN_CAUSE`.
4. **Büyük DOWN mu geçici düzeltme mi?** XAU 16 M15 <= -1% ve NQ 6 H1 <= -1% ile satış baskısı; ardından 9 benzer vakanın geçmiş 96h -%3 alt bacak durumu ve **novelty / OOD**.
5. **Satıştan sonra tutar mı, nakitte mi kalırız?** Karar XAU MID vekiliyle, %0.8 iki yönlü maliyeti içerir; banka spread henüz yok.
6. **G01/G05/G06/ORG10/ORG12 hangisi?** Kaynaklı haber ilk yayın saati ve faiz/USD/metal doğrulanmazsa **`UNRESOLVED`**, doğrudan olay nedeni atama yok.
7. **Yeniden giriş:** Aynı frozen 5'li giriş koşulları + 12h satış sonrası cooldown; Jan29 sonrası yeniden giriş yok.

**Tarihsel öğrenme gerçekten nasıl uygulandı?** Önceden olgunlaşan 92 vakada k=9, 8 değişkenli ağırlıklı normalize mesafe: altın 4h getiri, RV4, aşağı oynaklık payı, yol etkinliği, kapanış konumu, 4h tepe farkı, NQ H1, ZN H1. En yakın tarihsel vakaların gerçekleşen 96h -%3 fiyat uzamasının ters-mesafe-ağırlıklı payı alınır. Bu **kalibre edilmiş olasılık değil**; arşiv ex-post olay seçilmiş ve çok sayıda çakışan/ikiz vaka içerir.

### Kritik yanlışlama
- 5 Ocak **AL** noktasında olay analogu tarihsel -%3 bacak ağırlığını **0.5785** verdi; bu iyi UP hareketini engellememeliydi. Demek ki bu skorun yüzde olarak satış riski yorumu / koruması **şu an güvenilir değil**.
- 29 Ocak **SAT** noktasında aynı skor yalnızca **0.1097** verdi; ancak en yakın olay mesafesi **1.2799** ve RV anormaldi. `UNKNOWN_SHOCK` uyarısı, geçmiş olayların körlemesine iyimserliğine karşı önemlidir.
- Aynı anda **önceki 15m fiyat-only trailing kuralı** da SAT sonucunu üretti. **Olay öğrenmesinin Ocak'ta ek getiri katkısı sıfır**, alarmın bir yorumlama kanalı olması ekonomik sebebi kanıtlamaz.
- 2023–25 tarihli vakalara geriye dönük konmuş ORG ve DNA isimleri Ocak 2026 ilk yayım saatinde canlı ispatlanmış ekonomik mekanizmalar değildir.

## 4. Ocak 2026 tarihiyle ekonomik kanıt — geleceği bilmeme
**Gün ve yayın saatleri** BLS geçmiş takvimi ve Fed açıklaması:
- **7 Ocak 15:00 UTC**: JOLTS (Kasım 2025).
- **9 Ocak 13:30 UTC**: Aralık 2025 istihdam raporu.
- **13 Ocak 13:30 UTC**: Aralık 2025 CPI.
- **14 Ocak 13:30 UTC**: Kasım 2025 PPI.
- **28 Ocak 19:00 UTC**: Fed/FOMC karar açıklaması (2 pm EST).
- **29 Ocak 13:30 UTC**: Q3 2025 verimlilik revizyonu.
- **30 Ocak 13:30 UTC**: Aralık 2025 PPI.
Kaynaklar: [BLS Ocak 2026 takvimi](https://www.bls.gov/schedule/2026/01_sched_list.htm),
[Fed 28 Ocak açıklaması](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm).
Başlık/sonuçların daha sonra analiz edilmiş ekonomik yorumu 5 Ocak AL veya 29 Ocak SAT kararına otomatik girdi yapılmadı.
29 Ocak altın–NQ satışının ekonomik nedeni, resmi ilk haber ve bağımsız faiz/USD/metaller eksikliği nedeniyle `G05/G06/ORG10/ORG12` arasında **BELİRSİZ**.

## 5. Her günün kapanış durumunun muhasebesi
Bu tablo takvim gününün son 15m kontrolünde eldeki nakdi / GOLD teorik satılırsa elimize geçecek neti gösterir. **Bu tablo her 15m için bağımsız GPT haber/ekonomik yorum üretildiği anlamına gelmez; kontroller otomatik as-of kurallarıyla yapıldı.**

| Ocak günü | Pozisyon | USD değeri | İşlem | Bilinen veri yayını |
|---|---|---:|---|---|
| 01 | NAKİT | 100.00 $ | TUT / BEKLE | — |
| 02 | NAKİT | 100.00 $ | TUT / BEKLE | — |
| 03 | NAKİT | 100.00 $ | TUT / BEKLE | — |
| 04 | NAKİT | 100.00 $ | TUT / BEKLE | — |
| 05 | ALTIN | 98.71 $ | BUY_GOLD 09:30 | — |
| 06 | ALTIN | 99.86 $ | TUT / BEKLE | — |
| 07 | ALTIN | 99.13 $ | TUT / BEKLE | JOLTS_2025_11 |
| 08 | ALTIN | 99.50 $ | TUT / BEKLE | JOLTS_2025_11 |
| 09 | ALTIN | 100.18 $ | TUT / BEKLE | NFP_2025_12 |
| 10 | ALTIN | 100.31 $ | TUT / BEKLE | — |
| 11 | ALTIN | 100.31 $ | TUT / BEKLE | — |
| 12 | ALTIN | 102.16 $ | TUT / BEKLE | — |
| 13 | ALTIN | 101.98 $ | TUT / BEKLE | CPI_2025_12 |
| 14 | ALTIN | 102.89 $ | TUT / BEKLE | PPI_2025_11 |
| 15 | ALTIN | 102.49 $ | TUT / BEKLE | — |
| 16 | ALTIN | 101.96 $ | TUT / BEKLE | — |
| 17 | ALTIN | 102.19 $ | TUT / BEKLE | — |
| 18 | ALTIN | 102.19 $ | TUT / BEKLE | — |
| 19 | ALTIN | 104.02 $ | TUT / BEKLE | — |
| 20 | ALTIN | 105.65 $ | TUT / BEKLE | — |
| 21 | ALTIN | 107.21 $ | TUT / BEKLE | — |
| 22 | ALTIN | 109.50 $ | TUT / BEKLE | — |
| 23 | ALTIN | 110.82 $ | TUT / BEKLE | — |
| 24 | ALTIN | 110.82 $ | TUT / BEKLE | — |
| 25 | ALTIN | 110.82 $ | TUT / BEKLE | — |
| 26 | ALTIN | 112.25 $ | TUT / BEKLE | — |
| 27 | ALTIN | 114.38 $ | TUT / BEKLE | — |
| 28 | ALTIN | 119.74 $ | TUT / BEKLE | FOMC |
| 29 | NAKİT | 119.75 $ | SELL_TO_CASH 18:15 | FOMC|PRODUCTIVITY_Q3_2025 |
| 30 | NAKİT | 119.75 $ | TUT / BEKLE | PPI_2025_12 |
| 31 | NAKİT | 119.75 $ | TUT / BEKLE | — |

## 6. Zaman kapsamı ve altın fiyatı sözleşmesi
- **2976** Türkiye Ocak 2026 takvim kontrolü; yeni ve yeterli M15 bar + origin-safe lookback olan **1804** nokta; piyasa kapanışı/eksik koşul/hafta sonları toplam **1172** slot. Anlatımlı haber yorumları her bir slotta GPT ile tek tek yapılmadı.
- Tamamlanan M15 ve bir sonraki 15m open; bir H1 veri karar anında ancak önceki H1 tamamlanmışsa kullanılır.
- Kaynak Neon `gold_research_histdata_xau15m_candidate` (HistData 2025/26 candidate), `gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c` (NQ, ZN CME H1).
- Tarih saatleri UTC + **Europe/Istanbul**, 2026 Ocak TRT +3; mevsimsel NYC saat değişimi bu ay yapılmaz.
- Günlük yerel 15m son M15 alış fiyatı ve eski 3h sonucu ayrı benchmarklardır; ay sonu küçük fiyat-bitiş farklılığı açık tutuldu.

## 7. Ocak'tan **Şubat 2026'ya** kilitli öğrenme
1. 29 Ocak bilinmeyen büyük şok sürecinde geçmiş olay analogları **düşük risk** demesine rağmen piyasa kırıldı. OOD ayrı güven kapısı olmalı. Bu fikir önceden mevcut olduğu için Jan içinde çok kez değiştirilmedi.
2. 5 Ocak yukarı yön başlangıcında geçmiş olayların yüzde benzeri riski yüksek çıktı, ama trend sürdü: örnekleme yanlılığı ve "başlangıç durumu UP/DOWN" koşullu negatif kontrol eksik.
3. OLAY-02/ÖĞREN-03 mekanizma etiketlerini ekonomik ilk basım/sürüm/vintage doğrulanmadan güncel haberin kanıtı gibi verme.
4. Jan2026 modelinin `+%19.75` sonucunu **olay analogu öğrenme başarısı sayma**; marjinal işlem katkısı sıfır.
5. Şubat 2026 testi **$119.753917 nakit** ile başlayacak (Şubat bağımsız $100 senaryosu ayrıca gösterilebilir); yeni ayın sonuçlarını görmeden model eşiklerini değiştirme.
6. Hedef **marjinal olayları yakalamak ve portföyü korumak**, işlem sayısını artırmak değil.
7. İleri kalan hareket / maliyet dağılımı için ayrıca olaysız-kontrol havuzu ve gerçek banka BID/ASK şarttır.

## 8. Kalıcı çıktı ve kapsam güvenliği
- Kaynak panel: `JAN_2026_NEW_EVENT_MONTH_WALK_V1_15M_ASOF_PANEL.csv` (1804 M15).
- Karar defteri: `JAN_2026_NEW_EVENT_MONTH_WALK_V1_15M_DECISION_LEDGER.csv` (2976 takvim slotu).
- Günlük nakit/altın defteri: `JAN_2026_NEW_EVENT_MONTH_WALK_V1_DAILY.csv` (31 gün).
- Deney sonucu ve Şubat'a devredilecek öğrenme: `JAN_2026_NEW_EVENT_MONTH_WALK_V1_STATE.json`.
- Yeniden çalıştırılabilir araştırma kodu: `JAN_2026_NEW_EVENT_MONTH_WALK_V1_REPLAY.js`.
- OLAY-02 ana vaka CSV, 2023–2025 forward96h outcome CSV karar anındaki olgunluk filtresinden geçtikten sonra kullanıldı.
- Bu yeni çalışma 2026-01 `new-learning` klasöründe; daha önce sildirilen Ocak 2026 deney dosyalarının yollarına yazmadık, diğer yılların dosyalarına dokunmadık.
