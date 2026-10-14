# OLAY-02 — ENTEGRE OLAY VE VAKA KÜTÜPHANESİ
**2026-10-14 · Tek olay kimliği, tek bütün kayıt.** VAKA-03 isimlendirmesi kaldırılmıştır: vaka, OLAY-02'nin ayrı bir ana belgesi değil, aynı olayın kanıt ve işlem değerlendirme katmanıdır.

## Olayın tek kayıt kontratı
Her `EVENT_ID` altında olayın **(1) takvimi ve haber akışı**, **(2) sürpriz ve mevcut piyasa rejimi**, **(3) XAU/USD 15m ve olay-tetikli 1m fiyat akışı**, **(4) USD/faiz/değerli metaller/risk çapraz verileri ve eksikleri**, **(5) geçmiş benzer/karşıt olaylar**, **(6) neden-sonuç hipotezleri ve kanıt seviyesi**, **(7) NAKİT/GOLD pozisyonuna göre AL/SAT/TUT/BEKLE kararı**, **(8) banka ASK/BID %0,8 alış+%0,8 satış maliyetli sonuç ve kıyas**, **(9) sonradan gözlenen olay sonucu ile karar anında bilinebilir bilginin ayrımı**, **(10) ÖĞREN-03 hipotez kayıtlarına ID bağlantısı** görünmelidir.

Büyük çok-günlü epizot `EPISODE_ID` altındaki NFP, CPI, ISM vb. haberlerin her biri kendi `EVENT_ID` ile bağlıdır. Bir haberin birden çok gün süren altın hareketinin tamamını açıkladığı otomatik varsayılmaz. Güncel olmayan gelecekteki veri geçmiş AL/SAT gerekçesine taşınamaz.

Ham M15/M1 fiyatları özel Neon veritabanında kalabilir; rapor/CSV/JSON kaynakları olay kaydının içinde doğrudan linklenir. Böylece haber, fiyat ve karar ayrı dosyalarda teknik olarak saklansa da **kullanıcı tek olay sayfasından hepsine ulaşır**. Aynı fiyat/haber iki yerde birbirinden farklı doğrulukla tekrar yazılmaz.

## Denetim hükmü: kapsam ve kalite statüsü (2026-10-14)
**[OLAY-02 ayrıntılı haber–veri kalite kontrol raporu](OLAY_02_ICERIK_KALITE_DENETIMI_20261014.md)** üç ana vaka üzerinden resmî ilk yayımları, 15m/1m uygulama saatlerini, portföy sonuçlarını ve veri eksiklerini denetledi.

- İndekste bugün **3 üst olay kimliği** bulunuyor; bağlı **13/13 GitHub dosya bağlantısı açılıyor**. Üç üst olayın altındaki başka makro haberler henüz tek tek tam olay kimliğine ve bağımsız eşsaatli piyasa vektörüne sahip değil.
- Tarihsel arşivdeki **96 fiyat kaydının tamamında** `first_original_news_UTC_verified_for_initiation=NO` ve `causal_contribution_measured=NO`. Bu, NFP/ADP/ISM/CPI'nin **resmî duyuru saatlerinin** aşağıda ayrıca teyit edilmesine aykırı değil: duyurunun saati ve *altın hareketinin ilk nedeni olma ispatı* farklıdır.
- **DXY/2Y/10Y/reel faiz/gümüş/platin/paladyum gibi göstergelerin tam aynı-UTC onaylı 15m fiyat paneli** üç raporda yeterli değil. Bazı ZN/NQ/CL **saatlik tamamlanmış** fiyatlar bulunuyor; banka ASK/BID yok.
- Olayların `HABER/VERİ/AKSİYON` bağları **kısmen**, eski 96 vakanın tamamının entegre olduğu iddiası **HAYIR**. Tüm geçmiş olaylara otomatik doğrulandı etiketi verme.

## Entegre vaka ve olay dizini (ilk indeks)
| Olay kimliği | Olay/epizot | Haber ve piyasa mekanizması | Zaman damgalı veri + karar + maliyetli sonuç | Öğrenme bağlantısı |
|---|---|---|---|---|
| `MACRO_2023_01_06_NFP` | [5–13 Ocak büyük UP epizodu](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md) | ABD NFP, ücret artışı beklentisi, Fed yeniden fiyatlama; ISM 6 Ocak **daha sonra** | [864×15m denetim](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_864X15M_DECISION_LEDGER_20261014.csv) · [M1](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_EVENT_M1_GATES_20261014.csv) · [USD100 sonuç](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_REPLAY_RESULTS_20261014.json) | `MECH_FED_DOVISH_REPRICING_UP_V1` |
| `MACRO_2023_02_03_NFP` | [1–24 Şubat büyük DOWN](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md) | ABD güçlü NFP, olası Fed şahin beklentisi | [2304×15m](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_2304X15M_STATE_LEDGER_20261014.csv) · [USD100 sonuç](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_RESULTS_20261014.json) | `MECH_FED_HAWKISH_REPRICING_DOWN_V1` |
| `MACRO_2023_01_05_ADP` | [5 Ocak DOWN / 6 Ocak UP](adaptive_volatility_learning/stress_cases/2023-01/JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md) | ADP+claims düşüşü ve ertesi gün başka katalizörlerle geri dönüş | [192×15m](adaptive_volatility_learning/stress_cases/2023-01/JAN05_JAN06_2023_192X15M_ASOF_EVENT_DECISION_LEDGER_20261014.csv) · [karşı-olgular](adaptive_volatility_learning/stress_cases/2023-01/JAN05_JAN06_2023_STRESS_RESULTS_AND_COUNTERFACTUAL_20261014.json) | `MECH_SHORT_DOWN_WHIPSAW_HOLD_V1` |


## Olayın haber ve veri tarafı — ayrı ayrı okunabilir ilk üç örnek

### `MACRO_2023_01_05_ADP` — Şahin istihdam, kısa DOWN, TUT hipotezi
**Haber akışı (karar zamanı itibarıyla):** 5 Ocak **13:15 UTC/16:15 TRT** ABD [ADP ilk yayımlanmış 235.000 özel sektör istihdamı](https://mediacenter.adp.com/2023-01-05-ADP-National-Employment-Report-Private-Sector-Employment-Increased-by-235%2C000-Jobs-in-December-Annual-Pay-was-Up-7-3). Eski araştırma yaklaşık 150.000 beklenti yazıyor; *bağımsız as-of consensus-vintage* henüz teyit edilmemiş. **13:30Z/16:30 TRT** [DOL işsizlik başvuruları 204.000](https://www.dol.gov/newsroom/releases?agency=All&page=9&state=All&topic=132&year=all) (revize önceki 223.000). **6 Ocak NFP/ISM sonuçları henüz bilinmiyor.**

**Altın veri akışı:** İki gün **192×15m düzenli kontrol**, gerçek **184 M15 fiyat barı**; ADP sonrasında **13:58Z** civarında beş kapalı M1 düşüş teyidi. Bir sonraki dakika tahmini BID banka değil vendor/MID-makas vekili. Altın yönü DOWN ve şahin Fed kanalı **plausible**, **kalan >%1.62 işlem maliyeti sonrası düşüş** kanıtlanmış değil. Tam onaylı same-UTC DXY/US2Y yok, ZN saatlik kontrolle sınırlı.

**Karar/test:** Önceden Jan4'te alınmış GOLD altını **TUT** (SAT ve ertesi gün AL yapmak ilave ücret). 6 Ocak açık BID-mark **$100,0734**, 5 Ocak SAT→6 Ocak geri AL alternatifi yaklaşık **$97,67–$97,23**; gelecekteki 6 Ocak yükselişi 5 Ocak karar nedeni OLAMAZ. [İki günlük olay ve stres raporu](adaptive_volatility_learning/stress_cases/2023-01/JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md). **STATÜ: açıklanan haber actual + XAU fiyat kontrolü mevcut, ekonomik nedensellik ve kârlı sinyal avantajı kanıtlanmadı.**

### `MACRO_2023_01_06_NFP` — Karma istihdam/ücret, UP hipotezi
**Haber akışı:** **6 Ocak 13:30Z/16:30 TRT** [BLS NFP +223.000, işsizlik %3,5, saatlik ücret +%0,3](https://www.bls.gov/news.release/archives/empsit_01062023.htm). Ücretin yaklaşık +%0,4 beklentiye göre yumuşak gelmesi Fed-yavaşlama mekanizması ADAYI, ancak +223k istihdam ters şahin kanaldır. **15:00Z/18:00 TRT** [ISM Services 49,6, önceki 56,5](https://www.prnewswire.com/news-releases/services-pmi-at-49-6-december-2022-services-ism-report-on-business-301715010.html) açıklanır: **NFP'den 90 dakika sonra**, 13:46Z AL'a giremez. Sonraki **12 Ocak [CPI -%0,1 aylık/+%6,5 yıllık](https://www.bls.gov/news.release/archives/cpi_01122023.htm)** ve 13 Ocak Michigan bilgileri de sonradandır.

**Altın veri akışı:** **864×15m kontrol / 644 kayıtlı M15** (5–13 Ocak, hafta sonu dâhil), NFP öncesi M15 MID **$1.835,97**, ilk 15m UP yaklaşık **+%0,646**. İlk 13:45Z tamamlanan M15 UP + ardından 13:46Z üç tamamlanmış M1 tutunması AL adayı. **13:47Z** sonraki dakika M1 MID + son bilinen M15 makas = **$1.849,30 yaklaşık ASK**; gerçek banka emri değil. 13:46Z'de post-NFP ZN H1 henüz kapanmadığından NFP-sonrası tahvil teyidi kurulmadı.

**Karar/test:** Başlangıç CASH $100 → teorik BUY (0,8% alış); 13 Ocak 23:45 TRT **BID-mark $103,0123**, *ancak o tarihte varsayımsal SAT komisyonu ayrıca ödenirse* **$102,1882**. Bu tarihte algoritmik SAT kararı yok. [Makro vaka raporu](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md) · [864 kayıt](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_864X15M_DECISION_LEDGER_20261014.csv). **STATÜ: belirli NFP/ISM/CPI actual + ilk yayımlar doğrulandı, kural geçmiş vakaya maruz, L4/OOS yok.**

### `MACRO_2023_02_03_NFP` — Çok güçlü işgücü, büyük DOWN hipotezi
**Haber akışı:** **3 Şubat 13:30Z/16:30 TRT** [BLS orijinal NFP +517.000, işsizlik %3,4](https://www.bls.gov/news.release/archives/empsit_02032023.htm). Aynı yayın sonraki revizyonlarla değiştirilmez. İstihdam sürprizi Fed'in daha uzun sıkı kalabileceği kanalı; ancak gelecekteki 14 Şubat CPI, 16 Şubat PPI, 24 Şubat PCE haberlerini **3 Şubat'taki SAT gerekçesine ekleme**.

**Altın veri akışı:** 1–24 Şubat **2304×15m kontrol / 1646 gerçek M15**, NFP sonrası ilk kapalı 15m altın fiyat tepkisi yaklaşık **−%1,34**. Ardından **13:45Z**'de üç M1 kapanışıyla fiyat sürekliliği SAT adayı; **13:46Z** sonraki M1 MID − en son M15 yarım makas yaklaşık **$1.887,3050 BID** fiyat vekili. 13:45Z'de son NFP-post 1H ZN fiyatı henüz tamamlanmamış; aynı-UTC DXY/UST faiz verisi ve gerçek banka BID yok.

**Karar/test:** Yalnız ayrı bir **1 Şubat $100 GOLD başlangıç benchmark** varsayımıyla, 3 Şubat SAT sonrası **$96,3843 nakit**, 24 Şubat altını hiç satmama ve o tarihte %0,8 satış masrafıyla kıyas **$92,5313**. Satıştan sonra yeniden AL protokolü test edilmedi. [Şubat olay raporu](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md) · [2304 kayıt](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_2304X15M_STATE_LEDGER_20261014.csv). **STATÜ: haber actual + altın fiyat tepkisi doğrulandı, karar ve kâr tahmini genellenemez.**

### Üst vakaların içinde şimdilik ayrı olay sayfası OLMAYAN duyurular
`US_CLAIMS_2023_01_05`, `US_ISM_SERVICES_2023_01_06`, `US_CPI_2023_01_12`, `US_UMICH_2023_01_13`, `US_FOMC_2023_02_01`, `US_CPI_2023_02_14`, `US_PPI_2023_02_16`, `US_PCE_2023_02_24` ve önceki/yayın zamanı belirsiz haberler üst vaka anlatısı içinde **kaynaklı anılmış** olabilir; bağımsız ilk yayın, konsensus sürümü, bütün fiyat/çapraz veriler ve negatif kontrol olmadan **tamamlandı** işaretlenmez. Üç entegre üst vaka dışındaki **96 düzeltilmiş fiyat kaydını** [tarihsel kanıt sicilinden](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv) aşama aşama ve olay-ID ile taşı.

**Eski kapsamlı olay araştırmasının değiştirilmeyen orijinali:** [TARİHSEL OLAY ARŞİVİ (OLAY-02 kaynak arşivi)](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md). Orijinal 0.1A–0.1G çalışması eksiksiz korunur; tüm tarihsel olayların yeni indekse bir seferde geçirildiği iddia edilmez. Diğer vakalar çalışıldıkça veya aktarım doğrulanınca aynı `EVENT_ID` dizinine bağlanır.

**Ana yönetim:** [ANA-01](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md). **Ortak hipotezler:** [ÖĞREN-03 (eski dosya adı korunur)](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md). **Aylık ilerleme:** ilgili `months/YYYY-MM/STATE.json`.

**Güven sınırı:** Üç olayın karar kuralları ve %0,6/3M1 örnek teyidi geçmiş görüldükten sonra seçildi; gerçek banka kotasyonu ve bağımsız ileri performansı yok. Buradaki bağlantılar araştırma vakasıdır, otomatik banka emri değildir.
