# Olay sonrası çift saatli S1/S2/S3 ölçüm tasarımı — inceleme sözleşmesi

**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 · **Durum:** TASARIM / HENÜZ KODLANMADI / AL-SAT YOK
**Kullanıcı teşhisi (18 Ekim 2026):** OLAY–ÖĞREN–ETKİ mekanizması tetiklenirse S1/S2/S3, ekonomik haberden **önceki** fiyat değişimini olay **sonrasındaki** hareketle tek bir global 4s pencerede ortalamasın. Olay yoksa normal piyasa hesabı korunsun. **Önemli cevap:** Bu teşhis güçlü; fakat bütün geçmişi unutup S1/S2/S3'ü sıfırdan 15 dakikalık veriyle eğitmek hatalı olur. Öneri aynı model içinde **GLOBAL + EVENT** paralel metrik katmanıdır.

## Gerçek kod denetim bulgusu

- `adaptive_phase_lifecycle_s2.js`, `signal(window)`: son 17 fiyat/16 tam M15 adımının log değişimi ve sqrt(sum squared log returns) üzerinden `trendZ`; **ekonomik olay zamanı bağımsız bir anchored price window yok**. S2 fiyat epizodları (`START/CONTINUE/PULLBACK/END`) olay mekanizması epizodları değildir.
- `adaptive_market_core_s1_s2.js`, `features()`: S2 fast `trendZ,retracement,phase_direction,phase_age` + slow session; `bar.economicFeatures` yalnız kaynak/vintage gate'i geçmiş olan ayrı sayısal sürprizlerden gelebilir. S1 `horizons:[240],anchorMinutes:240`; olay anına özgü t0 origin/yenileme yok.
- `adaptive_rule_discovery_s1.js`: mature label 4h origin'leri her 240 dk, fakat yeni makro release event-driven S1 anchor kurmuyor. S1 geçmiş kazanımlarını sırf olay başladı diye boşaltma.
- `adaptive_conditional_position_s3.js`: koşullu S3 `MKT:phase:direction|ECO:EMP/CPI:dominant:sign` ile birleştiriyor; ücret/işsizlik/CPI maddelerinden **yalnız en baskın tek sayısal özellik** kalıyor. S3 tarihi result maturity, 5/10/20 seans ve gerçek spread sınırları var. **Olay t0 fiyatı, event elapsed age, ilk tepki, rakip ekonomik mekanizma beraber tutulmuyor.**
- `chronological_ai_portfolio_v1.js` olay `eventTime` ve `availableAt` tutabiliyor; ancak makro ilk-baskı/PIT olayları halen karantinada. Bu tasarım, canlı GPT hesaplandığını iddia etmez.

## Çift saat

**G — Global market saat:** Mevcut 4s/slow geçmiş pencereleri ile trend, düzeltme, uzun konum ve normal oynaklık. Olay yokken CORE'un mevcut matematik/çalışma hali **değişmemeli**.

**E — Olay saati:** Bir veya birden fazla `Kxx` ekonomik koşulu doğrulanıp ÖĞREN-03 mekanizma adayına bağlandığında ayrı **eventEpisode**:

- `event_time`: yayının / gelişmenin gerçekleştiği gerçek UTC.
- `first_available_at`: veri kaynağının o içeriği yayınladığı / kullanıcıya fiilen erişilebilir olduğu ilk UTC.
- `detected_at`: mekanizmanın **sistem tarafından ilk defa** doğru şartlarla tanındığı UTC (bu andan önce ekonomik karar üretilemez).
- `pre_event_price`: `first_available_at` öncesinde tamamlanmış son geçerli M15 barın fiyati (fiyat veri kaynağı ve kesin `asof` ile). İlk fiyat hareketi sonrası geçmişteki en iyi fiyatı çapa seçmek yasak.
- `event_price_first_closed`: olayın ilk bilinebilir ve tamamlanmış fiyat barı (ör. TRT 16:30 NFP sonrası TRT 16:45 M15). **Event-relative fiyat metriği burada olgunlaşmaya başlar, ama başlangıç referansı pre-event bar olabilir.**
- `decision_asof`: gözlemin gerçekten hesaplanabildiği an. `decision_asof>=detected_at` ve fiyatın kapanışı; gecikmiş ilk yayın veya tarihi etiket gelirse geçmişe AL/SAT yazma.
- `active_conditions=[K03,K18,...]`, `ORG hypothesis`, `opposing_conditions`, `evidence`, `unknowns`, `decay_state` her biri ayrı.
- `E` sinyali çıkması **otomatik ilk işaretin büyük hareket olduğunu** veya yönü doğruladığını göstermez. `UNKNOWN/ABSTAIN` temel sonuçtur.

## Olay-bağıl metrikler — baseline'ı kaybetmeden

| Alt sistem | G (global, korunur) | E (olay başlatmalı, yeni yalnızca aday) |
|---|---|---|
| **S1** | Mevcut fiyat fazı/SLOW ve 4s ileri koşullu forecast. | `elapsed_after_first_event_bar`, `log(P_t/P_pre_event)`, ilk M15 tepki (yalnız olgunlaştıktan sonra), haber K birleşimi, asof-USD/faiz/gümüş teyidi, rakip ORG. `P(direction,size,duration | event+pre_state)` **yalnız geçmişte olgunlaşmış olaylardan**; event karar origin'i, mevcut 4s periyodik anchor'dan bağımsız olabilir. |
| **S2 FAST** | Mevcut 16 M15 trend/phase devam. | Olay-sonrası fiyat yolu: yeni tepki, hızlanma/yavaşlama, erken fade, reverse, continuation; `event_window_bars`, `event_age`. **İlk 15dk verisi 4s trend z diye raporlanmaz.** Normal ön-olay oynaklığı ile ufka uygun normalize edilir; veri seyrekse `NOT_READY`. |
| **S2 SLOW** | Önceki uzun trend/slow yönetilir. | Ekonomik olay uzun trende karşı mı, onu güçlendiriyor mu? Uzun dönem trend belleği resetlenmez. |
| **S3** | Var olan CASH/GOLD, beklenen net fark ve banka maliyeti. | Global+event kanıtlarıyla `net_Q(CASH/GOLD | context,elapsed,holding)` karşılaştır; event-only etkisi baseline'a karşı **artımlı** ve tekrarlı bağımsız örneklerde doğrulanmış olmalı. %0,8 alış + %0,8 satış, banka gerçek kotasyonu yoksa shadow-only. |
| **OLAY/ÖĞREN/ETKİ** | Geçmiş OLAY-02 vaka ve mekanizma ORG hipotezleri. | Yeni olay sadece doğru zamanda gözlenen K etiketleriyle açılır; uygun gerçek takvim/ilk baskı yoksa EVENT_UNVERIFIED; aynı ekonomik haber birden fazla ORG kanalını tetikleyebilir. |

Metrik örneği: `r_event(t)=100*log(P(t)/P_pre_event)`; `r_global_4h(t)=100*log(P(t)/P(t-4h))`. Bu iki ölçüm birbiri yerine geçmez. `sigma_pre_event(h)` yalnız olay-öncesi tamamlanmış karşılaştırılabilir dönemden belirlenir; `event_z=r_event/sigma_pre_event(matched_elapsed_horizon)`. İlk olay barında yeterli normlandırma desteği yoksa uç değerlere aşırı güvenilmez. `first_15m_ret` ancak **ilk M15 tamamlandığında** oluşur.

## Kritik yanlış kullanım yasakları

1. Olayın gerçekleştiği saat ile **tanıma/ilk bilme** saatini karıştırma; `detected_at` 17:00 ise 16:45'e ex-ante karar yazma. Aynı gün olaydan sonraki 4h sonucu 16:30 kararını beslemez.
2. Her fiyat dalgasında `K03+... oldu` diye sonradan etiket üretme. Ekonomik firstprint / consensus vintage kaynakları sertifikasızsa `RESEARCH_MACRO_UNVERIFIED` / `UNKNOWN` ve **gerçek AL/SAT yok**.
3. Etki/olay penceresini global 4h penceresine zorla eşitleme. Olay t0 yeni bilgi kaynağı; pre-trend/rejim **bağlam** olarak korunur.
4. Olay var diye eski S1 uzun hafızasını veya S2 SLOW fiyat rejimini silme; etki sönümlendiyse E kapanır, G çalışmayı sürdürür.
5. Birden çok olay: hem faiz/USD hem güvenli liman, aynı anda farklı K/ORG. Ortaya çıkan ekonomik zincirde rakip kanalları koru; `UNKNOWN` ve etki çatışması sonuç seçenekleri olmalı.
6. Gün içi ani veri sıçrayışı, veri boşluğu veya tatil ayrı kalite statüsüdür: `GAP` üzerinde eğri üretme veya gecikmiş sinyal işlemine izin verme.
7. `E` kesin yön/işlem komutu değildir; küçük hareketi al-sat fırsatı diye zorlamak yasak. Hareketin potansiyel **büyüklüğü/kalan ekonomik etkisi** ayrı öğrensin.
8. Event E ile Global G arasında eğitim örnekleri aynı fiyat sonuçlarını paylaşıyorsa iki bağımsız kanıt sayma.

## Önerilen kabul sınaması (gelecek teknik çalışma; bu dosya test çalıştırıldığı iddiası değildir)

Üç kolun aynı veri, aynı as-of ve aynı kaynak masrafıyla karşılaştırılması:

- **A — ORİJİNAL:** mevcut G-only S1/S2/S3 (kontrol, değişmez).
- **B — NAİF RESET:** ekonomik olayda tüm 4h fiyat belleğini sıfırlayan yöntem (istenmeyen deney karşıtı; uzun rejimi kaybetme riski).
- **C — DUAL CLOCK:** G + olay E ayrı metrik + event-aware confidence/uncertainty; olay yokken C==A olması test.
- 2023 Ocak/Şubat örnekleri: 6 Ocak 16:30 TRT K03+K18+K19, 12 Ocak 16:30 K02(+çekirdek sürpriz=0), 1 Şubat FOMC K-yoksun, **2 Şubat 16:45 S2 fiyat START/DOWN ama yeni sertifikalı makro K yok**, 3 Şubat 16:30 K03+K19+eski K02, 14 Şubat 16:30 K05. Örnek değerlendirmede 2024/2025 sonradan sonuçlarını 2023 kör eğitim kuralı gibi sunma.
- Çıktı: olay t0, veri erişim ve karar saati, G yön/z, E relatif getiri ve normalize şiddet, E READY/UNREADY, rakip ORG, S1 event koşullu posterioru, S2 fast+slow, S3 net value ve `KEEP/SWITCH/ABSTAIN`, gerçekleşmiş vs olgunlaşmamış hedefler; **hiçbiri ekonomik haberin olacağını önceden bildiğini iddia etmesin**.
- Kalite: kaynağa uygun firstprint, no-lookahead, yanlış tarih/olay, missing price, DST, faz bazlı olay sönme/terslenme, same-time karşıt mekanizma, dünya/olaysız eş-saat placebo, etkinin global baseline'dan fazladan bilgi verdiği test, küçük örnek aşırı öğrenme engeli.
- Karşılaştırma: yön Brier ve calibration, büyüklük MAE / regime-normalized error, A vs C olaylı/olaysız kıyas; banka %0,8/ayak maliyetli yalnız shadow net servet; **parametreyi örnek ay sonuçlarına bakarak ayarlamak kör performans değildir**.

**Bilimsel statü:** `EVENT_AWARE_DUAL_CLOCK_PROPOSAL=DOCUMENTED`; `IMPLEMENTED=FALSE`; `ORIGINAL_CORE_UNCHANGED=TRUE`; `REGIME_EVENT_ALPHA_NOT_PROVEN`; `GPT_LIVE=FALSE`; `TRADE_ALLOWED=FALSE`.
