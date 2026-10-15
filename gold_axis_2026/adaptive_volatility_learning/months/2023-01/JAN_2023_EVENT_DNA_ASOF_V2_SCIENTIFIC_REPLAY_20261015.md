# OCAK 2023 — OLAY-ÖĞRENME SORULARIYLA 15 DAKİKALIK PORTFÖY KORUMA V2
**Araştırma tamamlandı:** 15 Ekim 2026 | **Statü:** `EX_POST_DISCOVERY / NOT_VALIDATED / BANK_NOT_EXECUTABLE`
**İlişkili otoriteler:** ANA-01, OLAY-02, ÖĞREN-03. Bu ek dosya otoritelerin yerini almaz.

## 1. Tek cümlede sonuç
**Ocak başı $100 nakit → 4 Ocak 2023 10.30 TSİ 1.852,848 XAU MID'den alış → Ocak sonu portföyü 0,0535392001934 ons ALTIN.**
Son fiyat **1.928,385 XAU MID** (31 Ocak 21:00 UTC = 1 Şubat 00:00 Türkiye ay sınırı).
- **Altın olarak taşınan mark-to-market portföy:** **$103,24419**. Bu gerçek satış yapılmış nakit değil.
- Sırf net karşılaştırma için ayrıca %0,8 *varsayımsal* satış komisyonu düşülürse **$102,41824 = +%2,41824**.
- Gerçek satış **yapılmadı**. Şubat başına **0,0535392001934 XAU + $0,00 nakit** devredildi.
- Altını ayın ilk tam M15 barından (03 Ocak 02:15 TSİ, **1826,197** ilk open) alsaydık ve aynı son fiyattan varsayımsal satsaydık **$103,91290 = +%3,91290**.
- Aynı MID + komisyon sözleşmesinde model al-ve-tutun **$1,49466** gerisinde.
- Başka kaynak ve farklı BID/ASK ile yazılmış önceki Ocak 2023 V1 baselinesi `$101,991366` ile **doğrudan aynı deney** gibi sunulmaz.

## 2. Saat, veri ve gerçekleşebilirlik
- Türkiye takvimi **1–31 Ocak 2023 dahil 31 × 96 = 2.976** tane M15 karar slotu değerlendirildi. İşlem yapılmayan günlerde en son durum taşındı.
- M15 kaynak **Neon `gold_research_histdata_xau15m_candidate`, `HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1`**.
- **1.763** geçerli 15 dakikalık, en son kapanmış fiyatı ve önceden bilinen yeterli fiyat geçmişi olan slot; **1.213** piyasada veri yok / kaynak geçerli değil / lookback yetersiz. Ayın sonundaki 1 Şubat 00:00 TSİ fiyatı yalnız ay-sınırı değerlemesi.
- **1.666** karar slotunda H1 Nasdaq (`NQ.c.0`) ve H1 tahvil vadeli (`ZN.c.0`) birlikte tam ve kullanılabilir.
- CME kaynağı `gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c`.
- H1 `ts_event` **bar başlangıcıdır**. Yalnız karar saatinden `en az 1 saat önce başlayan` ve karar öncesinde bitmiş H1 kullanıldı; daha yeni açık H1 alınmadı.
- İşlemler en son tamamlanmış M15 sonrası **bir sonraki M15 open MID** ile varsayımsal eşleştirildi.
- **%0,8 alış**, ayrıca yalnız teorik satışta **%0,8 satış** komisyonu; gerçek banka ASK/BID makası, kur dönüşümü, gece kotasyonu, stopaj, kayma **yok**.
- Tarihsel barlar 2026'da erişilen arşivdir, gerçek 2023 otomatik canlı kayıt değildir. Bu nedenle finansal sonuç **gerçek işlem vaadi** değildir.

## 3. Dondurulmuş araştırma V2 karar soruları
1. Son **400** tamamlanmış M15 kapanışındaki en düşük değerden itibaren yükseliş **≥%3** mü? (400 bar beş tam takvim günü DEĞİLDİR.)
2. Son 16, 92 ve 276 tam M15 barı altın getirilerinin yönü birbirini destekliyor mu? Başlangıç için `r16>=+%0,25`, `r92>=0`, `r276>=0`.
3. Gerçekten tamamlanmış Nasdaq son H1 `>=-%0,25` ve ZN son H1 `>=-%0,10` ile fiyat onayı var mı? Bunlar **ABD getirisi** ya da 2Y faiz tahmini değildir, vadeli fiyat hareketi.
4. Onaylı yayımlanmış G01 tipi takvim bilgisi son 6 saatte yeni mi? Açıklama sonrası XAU başlangıca göre `>=+%0,45`, r16 `>=+%0,30`, NQ H1 `>=-%0,25`, ZN H1 `>=+%0,02` ile alternatif **AL** hipotezi desteklenebilir mi?
5. Altındaysak ağır koruma alarmı: r16 `<=-%1,5` **VE** Nasdaq 6 tamamlanmış H1 `<=-%1`; ya da tepe geri çekilmesi `<=-%3`, r16 `<=-%0,8`, ek piyasa kırılımı; ya da yayımlanmış makro sonrasında daha güçlü ters fiyat/varlık teyidi mi?
6. Yukarıdakiler yoksa **HOLD_GOLD / HOLD_CASH**. Küçük düşüşte komisyon ödeyip gereksiz işlem yapma.
7. Koruma satışı sonrası geri dönüş için en az 72 saat + 92 ve 276 barlık toparlanma teyidi araştırması; bu Ocak'ta hiç tetiklenmedi.
Bu eşikler gerçek öğrenilmiş kalibre edilmiş olasılıklar değildir; 2022–2026 araştırmasında oluşan **test edilecek V2 hipotezi** olarak dondurulmuştur.

## 4. İşlem ve kararın gerekçesi
| Tarih Türkiye | Aksiyon | Gerçekleşme vekili | Gerekçe |
|---|---|---:|---|
| 1–3 Ocak | BEKLE | — | İlk günler tatil / yeterli teyit ve likidite yok |
| **4 Ocak 10.30** | **ALTIN AL** | **$1.852,848** | 400 bar dipten +%3,059; 4h +%0,395; 92-bar +%0,312; 276-bar +%2,466; NQ H1 +%0,043; ZN H1 +%0,097 |
| 5–31 Ocak | ALTIN TUT | — | Teyitli ağır DOWN koruma kapısı açılmadı; ekonomik haber görüldükçe G01 adayı veya G07 belirsizlik kaydedildi |
| **1 Şubat 00.00 TSİ ay sınırı** | **DEVRET (SATMA)** | **$1.928,385 MID** | **0,05353920 ons GOLD** Şubat'a taşınır |

Yalnız fiyat göstergelerine göre **4 Ocak 10.30** erken BUY oluşmuştur. JOLTS aynı gün **18.00 TSİ**, Fed tutanağı **22.00 TSİ** olduğundan o alıma neden olarak gösterilemez.

## 5. OLAY-02 / ÖĞREN-03 entegrasyonunun gerçekte kapsamı
- Her uygun kontrol slotunda yayımlanmış G01 makro takvimini ve tamamlanmış XAU+NQ+ZN fiyat göstergelerini değerlendiren bir **P0/P2 ve G01/G07 aday hipotez mekanizması** çalıştı.
- **26 uygun M15 kontrolde** `P2_G01A_CANDIDATE`, **153 kontrolde** `P2_G07_UNRESOLVED`, **1.584 kontrolde** `P0_OR_NO_VERIFIED_RELEASE` etiketi oluştu. Bunlar **bağımsız olay sayısı değildir**; aynı haber sonrası art arda 15m kontrolleridir.
- Jan12 CPI ve Jan31 ECI sonrasında kısa vadeli G01A **aday** teyitleri; Jan6 NFP güçlü XAU tepki verdi fakat çapraz işaretler aynı anda kesin teyit olmadığından `G07_UNRESOLVED` bırakıldı.
- Jan18 PPI+perakende eşzamanlıydı ve ilk tepki ile birkaç saat sonraki fiyat birbirinden farklıydı; tek sebep teşhisi veya erken SAT yok.
- OLAY-02'nin **`SWING_V1_001` / `ORG01`** geçmiş kaydı Jan3'e denk gelir, fakat tarihsel uzun dalganın sonucu ve sonradan atanmış DNA kimliği Ocak kararına **as-of giriş olamaz**.
- 2023-2025 tarihli 93 vakalık arşiv, **Ocak 2023 anında gelecekteki sonuçları biliniyormuş gibi kullanılmadı**. Buradaki V2, önceden doğrulanmış istatistiksel ekonomik olasılık sistemi değildir.

### Etki/ablasyon — çok önemli
Aynı M15 panelinde **makro karar katmanı kaldırıldığında** yine **4 Ocak 10.30 AL, 0 SAT, $102,41824**.
Hatta bu ay özelinde tüm çapraz varlık koşulları çıkarılıp yalnız aynı fiyat koşullarıyla kontrol edildiğinde de aynı işlem oluştu.

**Dolayısıyla Ocak 2023'te ekonomik DNA ve çapraz piyasa katmanlarının _net ek ticari katkısı sıfır_ ölçüldü.**
Şimdiye kadar modelin örnek olay mekanizması bilgi olarak entegredir, fakat portföy avantajı gösterilememiştir. Aksini yazmak bilimsel olarak doğru olmaz.

## 6. Ayın tamamı — 31 takvim günü
Tablodaki portföy USD, varsa **varsayımsal son satış komisyonu düşülmüş anlık tasfiye değeri**dir. Fiilî SAT yalnızca işlem defterindeki koşullarla tetiklenir, bu ay **0**.
| Ocak günü | Durum | Teorik tasfiye NAV | Tamamlanmış karar slotu | İşlem | Kaydedilen makro |
|---|---|---:|---:|---|---|
| 01 | NAKİT | $100.00 | 0 | — | — |
| 02 | NAKİT | $100.00 | 0 | — | — |
| 03 | NAKİT | $100.00 | 70 | — | — |
| 04 | ALTIN | $98.36 | 91 | BUY_GOLD 10:30 | JOLTS|FOMC_MINUTES |
| 05 | ALTIN | $97.40 | 91 | — | FOMC_MINUTES |
| 06 | ALTIN | $99.19 | 91 | — | NFP |
| 07 | ALTIN | $99.12 | 4 | — | — |
| 08 | ALTIN | $99.12 | 0 | — | — |
| 09 | ALTIN | $99.34 | 71 | — | — |
| 10 | ALTIN | $99.70 | 91 | — | — |
| 11 | ALTIN | $99.70 | 91 | — | — |
| 12 | ALTIN | $100.74 | 91 | — | CPI |
| 13 | ALTIN | $101.99 | 91 | — | — |
| 14 | ALTIN | $101.96 | 4 | — | — |
| 15 | ALTIN | $101.96 | 0 | — | — |
| 16 | ALTIN | $101.59 | 58 | — | — |
| 17 | ALTIN | $101.37 | 71 | — | — |
| 18 | ALTIN | $101.10 | 89 | — | PPI_RETAIL |
| 19 | ALTIN | $102.60 | 91 | — | — |
| 20 | ALTIN | $102.43 | 91 | — | — |
| 21 | ALTIN | $102.32 | 4 | — | — |
| 22 | ALTIN | $102.32 | 0 | — | — |
| 23 | ALTIN | $102.58 | 66 | — | — |
| 24 | ALTIN | $102.89 | 80 | — | — |
| 25 | ALTIN | $103.34 | 91 | — | — |
| 26 | ALTIN | $102.47 | 89 | — | GDP |
| 27 | ALTIN | $102.43 | 91 | — | PCE |
| 28 | ALTIN | $102.42 | 4 | — | — |
| 29 | ALTIN | $102.42 | 0 | — | — |
| 30 | ALTIN | $102.11 | 61 | — | — |
| 31 | ALTIN | $102.38 | 91 | — | ECI |

**Ay sonu sınır fiyat farkı:** 31 Ocak son 23.45 TSİ son tam bar tasfiye NAV'si yaklaşık **$102,3791**; 1 Şubat 00.00 TSİ tam ay kapanış sınırında **$102,41824**. 00.00 fiyatı 31 Ocak kararına geri verilmedi; yalnız muhasebe sınırında kullanıldı.

## 7. Şubat'a devredilecek öğrenme ve yanlışlama listesi
1. **İlk UP bacağının gecikmesi:** 3 Ocak yükselişinin bir kısmı nakitte geçti. Aynı masraflarla pasif altına kıyasla **$1,49466** fark var. 3% geçici momentum kuralını yeni aylarda **karar öncesinde** değerlendir; Jan sonucu görülerek Jan'a özel ayar yapma.
2. **Gereksiz satış yok:** Önceki fiyat temelli modellerin küçük düzeltmelerde aşırı işleme gitme hatası Ocak'ta gözlenmedi. Ancak büyük DOWN koruma yeteneği **sınanamadı**.
3. **Haber etkisi sorusu:** Makro aday etiketleri işlem akışını değiştirmedi; NFP ve CPI için yayın öncesi consensus/vintage, XAU+USD/yield firstprint ve birbirine rakip açıklamaların **bağımsız** kıyaslaması yapılmalı.
4. **Ekonomik DNA = tarihsel mekanizma sözlüğü:** G01, G05, G06 ve ORG01/ORG10 arası rol/geçiş ihtimalleri dışarıdan sonuç bilindi diye kanıtlanmış olarak atanmaz.
5. **Maliyet ve marka hassasiyeti:** MID ile gerçek bankanın spreadi ve işlem penceresi aynı değildir. M15 intraday satışı ekonomi açısından anlamlı kılmak için kaçınılabilir hareketin iki yönlü ücret ve makası aşması gerekir.
6. **Deney disiplininde sıfır geri besleme:** Jan 2023 ara fiyatıyla sınırlı Şubat başlangıç bilgisi; 2026 olay arşivi, Jan 2023 simülasyon kararlarına geri beslenemez.

## 8. Şubat'a canlı portföy durumu
```json
{
  "month_end_utc": "2023-01-31T21:00:00Z",
  "asset": "GOLD",
  "gold_oz": 0.05353920019343195,
  "cash_usd": 0,
  "last_xau_mid": 1928.385,
  "mark_to_market_usd": 103.24419056501128,
  "sell_now_net_usd_scenario_only": 102.41823704049119,
  "strategy_status": "HYPOTHESIS_EX_POST_NO_BANK_VERIFICATION"
}
```
Şubat araştırması bu GOLD miktarıyla başlar; Ocak sonunda kurgusal satış yapıp **$102,42 nakit**e dönüşmez.

## 9. Kaynaklar, dosyalar, tekrar çalıştırma
- **BLS release calendar:** https://www.bls.gov/schedule/2023/01_sched_list.htm
- **CPI original:** https://www.bls.gov/news.release/archives/cpi_01122023.htm
- **NFP original:** https://www.bls.gov/news.release/archives/empsit_01062023.htm
- **Fed minutes calendar:** https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- Neon HistData XAU M15, CME NQ/ZN completed H1 (spot USD faiz ve gerçek banka BID/ASK değildir).
- `JAN_2023_EVENT_DNA_ASOF_V2_PANEL_20261015.csv` — kaynak karar özellikleri; 1.764 satır, son 1 satır ay muhasebe sınırı.
- `JAN_2023_EVENT_DNA_ASOF_V2_15M_LEDGER_20261015.csv` — **2.976** 15m takvim kontrolleri.
- `JAN_2023_EVENT_DNA_ASOF_V2_DAILY_SUMMARY_20261015.csv` — 31 gün.
- `JAN_2023_EVENT_DNA_ASOF_V2_STATE_20261015.json` — Şubat'a devir.
- `JAN_2023_EVENT_DNA_ASOF_V2_REPLAY_20261015.js` — deterministik replay.
  Çalıştırma: `node JAN_2023_EVENT_DNA_ASOF_V2_REPLAY_20261015.js JAN_2023_EVENT_DNA_ASOF_V2_PANEL_20261015.csv`
- Mevcut önceki Ocak 2023 V0/V1 belgeleri korunur; **silinmiş Ocak 2026 strateji deneyi dosyaları geri getirilmedi**.
