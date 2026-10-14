# CFTC COT raporlarının içerik denetimi: 2023–2025 altın hareketlerinde opsiyon eşdeğeri / vadeli pozisyon ayrışması ve ETF kanalı
**14 Ekim 2026 | Geçmiş olayların ekonomik mekanizması araştırması | Tarihsel gözlemsel veri, tahmin modeli değil**

## 1. Yeni somut bulgu ve sınırı
**COT 'managed money options-only' sanılan değişken gerçekte CFTC'nin doğrudan bir sütunu değildir; iki Disaggregated raporun net farkından OPEN INTEREST'e oranlanan araştırma göstergesidir.** 2025'te düzeltilmiş COT yayım takvimine göre seçilmiş 51 haftadan bu gösterge artan 15 haftanın 12'sinde ilk V2 küme bayrağı, diğer 36 haftanın 11'inde ilk bayrak var (**80,0% / 30,6%**, iki taraflı Fisher p≈**0,00183**, posthoc). Ancak fiyat yolu bağımsız ölçüldüğünde sonraki beş NY17 seansta herhangi bir noktada altının kökene göre +%3 / −%3 eşiğine ulaşması **9/15 (%60,0) vs 9/36 (%25,0)**, Fisher p≈**0,02553**. Beşinci seans kapanışının mutlak %3'ü geçmesi **7/15 vs 7/36**, p≈**0,0826**. Dolayısıyla görünen örüntü özellikle **hareket olasılığı/büyüklüğü** ile ilgilidir; yön ve nihai getiri ispatı değildir.

**2023–2024 tekrar testi:** Aynı işaret kuralında V2 yeni bayrak **15/46 vs 12/57**, fiyat yoldaki %3 sınır **8/46 vs 8/57**. 2025 etkisi önceki dönemde aynı kuvvette görünmüyor; bilinen tarihsel 2025 şoklarına çoklu testle bakıldı. 2023–24 kaynak geçmişi 103 haftalık, 2025 testi 51 haftalık; bunlar birbirinden bağımsız 154 ekonomik şok değildir.

## 2. CFTC raporu doğru nasıl okunur?
CFTC **Disaggregated Futures Only** (`72hh-3qpy`) ve **Disaggregated Futures & Options Combined** (`kh3c-gbw2`) pozisyon sınıfları: Producer/Merchant/Processor/User, Swap Dealer, Managed Money, Other Reportables. Opsiyonlar birleşik raporda **delta esaslı futures-equivalent** hesaplanır; sözleşme sayısı, opsiyon gamma'sı ya da gerçek bir trader'ın opsiyon işlem hacmi değildir. CFTC resmî tanım: https://www.cftc.gov/MarketReports/CommitmentsofTraders/DisaggregatedExplanatoryNotes/index.htm ve https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm .

Kaynak algoritma [`tools/gold_cot_pit_reaudit_20261006.py`](tools/gold_cot_pit_reaudit_20261006.py), satır 71–113, tam olarak şunu hesaplar:

```text
F_t^MM = (Long_Futures_MM - Short_Futures_MM) / OI_Futures
O_t^MM = [(Long_Combined_MM - Short_Combined_MM)
          - (Long_Futures_MM - Short_Futures_MM)] / OI_Combined
D_t^MM = O_t^MM - O_{t-1}^MM
```

**ÖNEMLİ ERRATA:** Eski ETF–COT raporu ve önceki söylemde `d_opt_mm_net` 'birleşik futures+options managed money haftalık artışı' şeklinde kısaltıldı. Bu **yanlış**: alan **(combined net − futures-only net)/combined open interest farkının haftalık değişimidir**. 'Options-equivalent residual' daha uygun araştırma adıdır. Open interest paydasının değişmesi dahi pozitif/negatif işareti etkileyebilir; ham long/short net lotu, gamma, delta, futures/options ham ayrışması ayrıca gerek. Güncel açıklamada eşdeğer açık pozisyon fiyat yönünü mekanik biçimde oluşturur denmez.

**Saat ve bilgi sınırı:** Pozisyonlar salı kapanışında ölçülür, normalde cuma 15:30 ET açıklanır. 2023 ION ve 2025 CFTC yayın kesintisi için resmî özel takvim korunur. 154 origin'in 123'ünde as-of seçimi değişti; kontrol edilmiş yeni panelde `cot_age_calendar_days` alanı da yeniden hesaplandı (önceki yanlış yaş değeri `legacy_cot_age_calendar_days_before_release_clock_repair` adında korundu). Kaynak [resmî yayın saatleri raporu](GOLD_COT_PUBLICATION_CLOCK_OFFICIAL_AUDIT_AND_RETROSPECTIVE_154_ORIGIN_RETEST_20261014.md).

## 3. Futures / options-equivalent yön ayrışımı: 2025'te yeni sınıflar
| Seçilmiş rapordaki oran değişimi | 2023–24 yeni V2 bayrağı | 2025 yeni V2 bayrağı |
|---|---:|---:|
| `D_t>0`, `ΔF_t<=0` | **6/16** | **7/7** |
| `D_t>0`, `ΔF_t>0` | **9/30** | **5/8** |
| `D_t<=0`, `ΔF_t<=0` | **7/36** | **11/28** |
| `D_t<=0`, `ΔF_t>0` | **5/21** | **0/8** |

**İlişki özgüllüğü:** 2025'te futures-only managed money normalize net değişimi pozitifse bir sonraki V2 bayrağı **5/16**, negatif veya sıfırsa **18/35** (Fisher p≈0,232). Producers pozisyon değişimi veya Swap Dealer türetilmiş proxy'leri de aynı derecede güçlü ve istikrarlı değildi. Bu, COT net uzun hacminden çok **pozisyon formatı ayrışımı** adayını araştırmaya değer kılar. Ancak bu dört kategori **veriye baktıktan sonra** oluşturuldu, örnekler çok küçük; `D>0, ΔF<=0` hiçbir şekilde 7/7 kesin kural değildir.

**7 olayın gerçek başlangıç originleri:** 3 Şubat (COT 28 Ocak), 10 Mart (4 Mart), 31 Mart (25 Mart), 7 Nisan (1 Nisan), 21 Nisan (15 Nisan), 5 Mayıs (29 Nisan), 22 Aralık (9 Aralık) 2025. İlk V2 bayrakları sırasıyla UP, UP, DOWN, UP, DOWN, UP+DOWN, DOWN. İlişkinin **yön kararsızlığı** burada da açık. Eski COT yayım saatiyle elde edilen sonuç bu değil.

## 4. Cluster artefaktı ve doğrudan fiyat kontrolü
- **14 Nisan 2025:** `D<=0,ΔF>0`, yeni V2 bayrağı **yok**, fakat kökenden sonraki beş NY17 seansta altın **+%5,291** yükseliyor. Sebep yeni küme oluşturma eşik/cluster suppression semantiği, 'hiç hareket yok' değil.
- Bağımsız fiyat yolu: **2025 2023–24 eşleşmesi** önceki bölüm. COT ters oranının dışa dönük hareket büyüklüğüne olan ham ilişkisi %60 vs %25; 2025 birinci çeyreğini çıkarınca **5/11 vs 8/27** (%45,5 vs %29,6; Fisher p≈0,4573), yani farkın kanıtı **Q1 ağırlıklı**. Aynı işlemden sonra beşinci seans mutlak %3 kapanış oranı **3/11 vs 7/27** (Fisher p=1). Mutlak COT mevkiini genel yıllara uygulamak için yeterli değil.
- Nisan ve Mayıs 2025 tarihlerinin ikisini birlikte çıkardığımızda kalan haftalarda fiyat bariyeri **6/10 vs 7/33** (Fisher p≈0,0441; çoklu seçim). Ancak Q1'i de çıkarınca sonuç kuvvetli değil. Bu çelişki özel çeyrek / rejim koşulunu göstermektedir.

## 5. Negatif kontroller ve istatistiksel dürüstlük
- **2025 51 haftalık çeyrek koşullu hipergeometrik exact üst-kuyruk (aynı çeyrekte pozitif COT sayısını sabit tutar):** V2 ilk bayrak p≈**0,00152**; fiyat +3/−3 bariyeri p≈**0,03464**. Bu önceden sabitlenmiş doğrulayıcı test değildir.
- **51 haftalık dairesel yer değiştirme kontrolü:** sıfır-kayma gerçek hafta eşleştirmesi V2 ilk bayrak ve fiyat bariyeri farkında **51 kaymanın en üstünde (1/51)**; 5-seans son kapanış büyüklüğünde en üstte üç kayma var (**3/51**). Haftalar ve şok rejimleri bağımsız olmadığından bu doğrudan p-değeri sayılmaz.
- **Çeyrek + önceki beş seans altın hareketi ≥%3 sınıfı korunursa** 2025 fiyat bariyeri için exact üst kuyruk p≈**0,08464**. **Q1 hariç fiyat bariyeri p≈0,4573**. Çoklu test, geçmişten keşif, küçük `n` ve fiyat serisi provenance sınırlamaları baskındır.
- **2025 CPI/NFP/FOMC kalenderi konfounderi:** sonradan olay tarihleri değil, seçilen kökenden sonraki beş NY17 seansta günleri düşen **93 tarihli makro yayımdan** uygun olanları sınıflandırdık. 2025 options-equivalent residual UP olan **9/15**, olmayan **19/36** haftada en az bir CPI/NFP/FOMC var (makro haftaları sadece pozitif değişime özgü değil). Makro haftalarında gerçek %3 fiyat bariyeri: UP **6/9** vs NONPOS **3/19**; makro olmayanlarda UP **3/6** vs NONPOS **6/17**. Bunlar küçük, gözlemsel, aylara göre değişen karşılaştırmalar. CPI/NFP açıklamasının şoka neden olduğu gün dakika bazında ayrıca kontrol edilmelidir.
- **Kontrol edilen diğer COT kanalları:** futures-only managed-money net oran değişimi, futures producer değişimi, reconstructed producer/swap/other positions değişimi. 2025 options-equivalent residual haftalık artışın %80 oranı kadar güçlü *aynı yönlü* başka basit rapor alanı görülmedi. Birden çok aday denenmiştir; nominal p<0,05 mekanizma keşfi için yeterli değildir.

## 6. ETF ve ekonomik mekanizma: 2025 Q1 dönemini okumak
- World Gold Council, 30 Nisan 2025 tarihli **Q1 2025** raporunda altın ETF'lerine **226,5 ton** net talep, yaklaşık **US$21bn** giriş ve aynı çeyrekte COMEX managed-money vadeli net long yaklaşık **75 ton azalma** bildiriyor. ETF canlanması, ABD tarife/ekonomi belirsizliği ve altın momentumunu vurguluyor. https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q1-2025/investment
- WGC 6 Mart 2025 **Şubat ETF** raporu: fiziksel ETF yaklaşık **US$9,4bn** giriş; COMEX MM net long bir ayda **%16 düşüp 605 tona** indi. Bu kaynak, **ETF ve futures farklı yatırımcı/ürün gruplarının eşzamanlı zıt yönlü akımlarını** güçlü biçimde destekler. https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/03
- WGC 8 Nisan 2025 **Mart ETF** raporu: ETF net **US$8,6bn** giriş, futures MM net long **599 ton** (Şubat 605 ton). https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/04
- **Aday olay örgüsü:** tarifsiz normal haftadan farklı olarak 2025 Q1'de değişen ABD ticaret politikası/güvenli liman talebi → altın ETF'lerinde yatırımcı fon girişi, COMEX futures net pozisyonunda kâr realizasyonu/azalma; eşzamanlı CFTC futures+options ve futures-only arasındaki türetilmiş residual oranının kimi haftalarda artması → yakındaki fiyat hareketinin büyüklüğüyle eş-hareket. **Bireysel yatırımcıların futures'tan opsiyona/ETF'ye kaydırdığı doğrudan izlenmedi; kurumsal pozisyon transferi, opsiyon gamma satın alımı ve kesin fiyat nedeni ispatlanmadı.** CFTC residual payda/open interest ve bilinmeyen gerçek opsiyon tarafı çözülmeden anlatı 'hipotez'dir. ETF raporları ay sonrasında çıktı; olay tarihindeki herkesin ETF aylık akışını bildiğini varsayma.

## 7. Kaydedilmiş denetim dosyaları ve sonraki dar test
- [154 haftalık COT options-residual/futures ve 93 makro olay adayını birleştiren, fiyat bariyerli yeni panel](GOLD_COT_OPTIONS_RESIDUAL_FUTURES_CROSSCHANNEL_154_WEEKLY_WITH_MACRO_CONTROLS_20261014.csv)
- [154 haftalık düzeltilmiş COT yayın saati, hesaplanan taze COT yaşı, eski yaşı saklanmış panel](GOLD_COT_154_WEEKLY_NY17_CORRECTED_PUBLISH_CLOCK_RETEST_20261014.csv)
- [Eski 2023–25 COT saha saat denetimi](GOLD_COT_2023_2025_OFFICIAL_PUBLISH_VS_LEGACY_CLOCK_AUDIT_20261014.csv)
- [Düzeltmeden sonraki COT alan karşılaştırmaları](GOLD_COT_FRIDAY_CLOCK_CORRECTED_HYPOTHESES_20261014.csv)

**EN KRİTİK BİLİMSEL EKSİK:** CFTC `kh3c-gbw2` vs `72hh-3qpy` **ham LONG/SHORT/OI 2023–2025** COMEX GOLD raporlarını rapor-tarihinde karşılaştırıp *residual numerator (gerçek delta eşdeğeri), delta'dan türetilen pozisyon farkı, OI-normalizasyon etkisi* ayrı çıkarılmalıdır. Bu çalışma kaynak kodun türetilmiş alanlarını doğruladı, fakat CFTC ham tam yıllık ZIP indirmesi mevcut bağlanabilir kanallardan bu oturumda gerçekleşmedi; dolayısıyla ham alanları **yeniden bağımsız hesapladık** iddiası yapılmaz. Ardından bu maruziyetin gerçekleşen oynaklığın **nedeni mi, geçmiş fiyatın yan ürünü mü** olduğunu aynı haftaların ETF (vintage-first), makro haber, DXY/US2Y/10Y ve GC/SI geçerli UTC fiyat pencereleriyle yanlışlama yöntemiyle sınamak gerekir.

**STATUS: CAUSAL_HYPOTHESIS_CANDIDATE_2025_FIRST_HALF / PREVIOUS_DOPT_SEMANTIC_ERRATA / YEAR_HOLDOUT_NOT_REPLICATED / MULTIPLE_TESTS / NO_TRADE_OR_PREDICTION_PROMOTION.**
