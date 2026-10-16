# KAVİS CORE — TARİHTEN BAĞIMSIZ EKONOMİK DENEYİM ÖĞRENME MİMARİSİ

> **YETKİ SINIRI / 16 EKİM 2026:** Bu dosya, 16 Ekim tarihli **araştırma amaçlı teknik KAVİS V0 taslağıdır**; matematiksel çekirdeğin tam olarak öğrenildiği veya onaylandığı anlamına gelmez. Yeni MODEL ve UYGULAMA iş paketlerinin **tek bağlayıcı proje manifesti** [GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md](../../GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md) dosyasıdır. Uygulama ayrıdır; OLAY-02/ÖĞREN-03 yalnız bilgi kaynağıdır; Ocak 2023 MODEL_GATE geçilmeden başka aya/model mimarisine/UI geliştirmesine geçilmez.\n\n**Dondurulmuş tasarım ve araştırma protokolü (2026-10-16)**

## 0. Kullanıcının bağlayıcı amacı
- **Model kurallarının içinde takvim tarihi, yıl veya olay ID'si AL/SAT etkisi yaratan özellik OLMAYACAK.** Tarihler yalnız veri erişilebilirlik damgası, yürüyüş saati, aylık rapor dosyası ve dönem sınırıdır. Tüm öğrenilmiş bilgilerin asıl biçimi tarih içermeyen genel ekonomik DURUM→TETİK→AKTARIM→TEPKİ→BİTİŞ / yeniden giriş bilgisidir.
- Eğitim yürüyüşü **Ocak 2023 CASH 100 USD** ile başlar; o ay tüm kayıtları incelenir, matematiksel çekirdek kaydedilir, **ancak Ocak araştırması bilimsel olarak doğrulanmadan Şubat'a geçilmez**. Daha sonra ay ay Aralık 2025'e kadar ilerler. **Aralık 2025 bitiminde öğrenilmiş CORE durumu derlenip kilitlenir; 2026 Ocak sınaması daha sonra, bu CORE kilidinden sonra yapılır.** Bu repoda 2026 Ocak daha önce görülmüştür: test kör/bağımsız diye sunulamaz.
- Amaç her küçük yükselişi ve düşüşü işlem fırsatı saymak DEĞİL; kullanıcı banka maliyeti ve risk bütçesiyle **az ama ekonomik açıdan anlamlı AL, TUT, SAT, yeniden AL** olaylarını seçebilmek. Maliyet tek yönlü **%0,8 AL + %0,8 SAT**; yaklaşık gidiş-dönüş %1,6. Sık işlem CEZALIDIR; sıfır işlem fırsatı kaçırma maliyeti taşıyabilir. "Hiç işlem yapmayan kapı" başarı kabul edilmez.
- Kâr garantisi, her ay pozitif sermaye ve her ay tekdüze iyileşme garanti edilmez. Net sermaye, en kötü düşüş, işlem masrafı ve kaçırılan ana hareketler birlikte ölçülür. Pasif altın, nakit, V18, V22 kıyasları şarttır.
- Makine gerçek banka emri GÖNDERMEZ; geçmiş XAU fiyatı bankanın asıl BID/ASK kaydı değildir.

## 1. Ortak epistemik saat: gözlemler
Her gelen veri için `source`, `event_time`, `first_available_at`, `retrieved_at`, `revision/vintage`, `quality`, `observation` kaydı bulunur. `first_available_at <= decision_time` ise girdi kullanılabilir; yayın zamanı bilinmiyorsa geriye dönük bilgi üretimi iddia edilmez ve ana modele giriş bilinmeyen olarak işaretlenir.
- Fiyat: XAU, XAG, XPT, XPD; örnek zamanına göre BTC/ETF/hisse/dolar/faiz/petrol/GVZ/VIX / GPR, CME SI/GC/NQ/ZN/CL, COT/ETF akışı.
- Haber: ilk baskı UTC, beklenen/değişim sürprizi, tekilleştirme, ilk kaynak güveni, kesinleşmiş ilk-yayın saati, sonraki düzeltmeler. Haber yorumları bu zaman damgalarının yerine geçemez.
- 2023 koşusuna 2024–2026 atlasındaki sonradan öğrenilmiş fiyat sonucu, hareketin bitişi veya bu sonuçtan çıkarılmış "kim kazandı" ağırlıkları GERİYE TAŞINAMAZ. ÖĞREN ve OLAY araştırması ekonomik ontoloji önerisi olabilir ama gelecek yılların sonuçlarından türeyen kalibrasyon 2023'e aktarılmaz. Önceden belirlenmiş taksonomi varsa etiketsiz yeniden kullanılır; olayın fiyat etkisi Ocak 2023 itibarıyla öğrenilir.
- Ham fiyat yalnız **o an işlem görmekte olan son tamamlanmış bar**; karar için yayımlanmamış yeni bar kullanılmaz. Bugünkü gerçekleşme ancak sonraki karar güncellemesinde sonuç/label olur.
- Eksik veri nedeni ve payı kaydedilir; uydurma "nötr 0" ile güncel gözlem gibi gösterilemez. Fiyat vekilinin banka makası olup olmadığı şeffaf olur.

## 2. Öğrenilecek tarih-bağımsız ekonomik durum
`z_t = Encoder_θ(available_market_prefix, available_event_prefix, learned_memory)`.
Olay kodlayıcısı `e_t`: `[mechanism_family, signed_surprise, surprise_z, release_confidence, pre_market_state, spread_liquidity, metal_divergence, crossasset_confirmation, elapsed_since_firstprint, missing_flags]`. Burada **olay türü kural değil; eğitilebilir açıklayıcı değişkendir**.
- Ön durum: trend / volatilite / likidite / dolar-faiz-metal ilişkileri; belirsizlik.
- Tetik: yayımlanmış haber/makro sürprizi ya da haber olmadan fiyat-şok başlangıcı; "belirsiz haber" de geçerli sınıf.
- Aktarım: XAU↔XAG/XPT/XPD, USD–rates, NQ/ETF/COT/likidite; gelişen etkinin gecikme, kuvvet, yön ve çözülmesi.
- Tepki: horizon bazında koşullu **getiri dağılımı**, uç kuyruk/düşüş olasılığı ve hareketin ömrü (survival/hazard).
- Bitme / karşı-örnek: fiyat hareketinin bitmesi, düzeltme, yeniden alım olasılığı, haber uyumsuzluğu. Sadece yükselen günleri değil hiçbir şey olmayan **kontrol günlerini** de öğren.
- Tarih/olay numarası yalnız provenance ve günlük araştırma defterinde bulunur, hiçbir model katsayısı doğrudan bu kimliğe indekslenmez.

## 3. Matematiksel CORE'un modülleri
**(A) Temsil/olay modülü:** parametreli bağlamsal embedding; fiyat + haber için ayrı kalite maskeli encoder. Geçmiş olayların gerçek zamanlı *ön durum* ve *sonradan olgunlaşmış* sonucu ile online contrastive / representation loss. Kategori seviyesi değişmez; olayın etkisi parametre olarak öğrenilir. Nedensellik iddiası ancak negatif kontrol, yanlışlama ve kaynak ilk-baskı denetiminden sonra makul açıklama olarak raporlanır.

**(B) Çok ufuklu dağılım modülü:** kısa işlem gürültüsüne odaklanmak yerine ufuklar **[4 saat, 1 işlem günü, 3 işlem günü, 1 hafta, 2 hafta]**; kayıp `L_forecast = Σ_h w_h * proper_scoring_rule(P_θ(R_h|z_t), R_h)` (örn. quantile pinball/CRPS), gerçekleşme etiketi ancak gerçek ufuk geçtikten sonra olgunlaşır. `w_h` olgunlaşmış prospektif tahmin kaybından online değişir. *Ufukların takvim günü farklı model tarihi olmadığına dikkat*: bunlar hareket ömrü/büyük işlem arama penceresidir.

**(C) Ekonomik deneyim / hata hafızası:** her gözlemden sonra `[ön durum embedding, olay temsili, tahmin vektörü, realized outcome, residual, karşıt mekanizma, net işlem farkı, sonraki altın/cash fırsat maliyeti]` kaydı. Benzerlik tarih üzerinden değil `metric(z_i,z_t)` ile hesaplanır. Sürekli adaptif kalibrasyon ve kavram kayması takip edilir. Yeni örnek hafızaya ancak etiketi olgunlaşınca girer; "kaçırılan hareket" yalnız geçmişteki tamamlanmış veriden değerlendirilir.

**(D) Karar / optimal pozisyon değiştirme:** portföy durumu CASH veya GOLD; yanlılık yerine `Q_φ(z_t,position,choice)` ve `V_cash,V_gold` durum değerleri **net işlem ücreti** ile öğrenilir. Temel araştırma hedefi:

`maximize E[ log(W_T/W_0) - λ * drawdown_tail_risk - κ * avoidable_turnover ]`

- Önceden bankanın %0,8 leg masrafı `log(1-0.008)` ödüle uygulanır. Aynı makas ikinci kez işleme alınmaz. Realized NAV ve teorik likidasyon ayrı tutulur.
- `Δ_t = E[U(policy_after_switch)] - E[U(policy_hold)]` beklenen net risk-düzeltilmiş **tamamlanmış tutma/yeniden giriş yolu** değeri. `BUY/SELL` yalnız `lower_confidence_bound(Δ_t)>0` ise; aksi halde mevcut pozisyonu TUT. **Yatırım eşiği sabit "fiyat %3 yükselirse" değil, ödeme maliyeti + model belirsizliğiyle dinamik hesaplanan ekonomik üstünlüktür.**
- Seyrek davranış `L_trade_cost`, geçmiş işlemden sonra elde tutma opsiyonu ve switching-value hysteresis ile doğal oluşur. Gelişigüzel haftada X işlem kotası, tarihe özgü alarm, "16 bar sonra izin" temel alfa öğreniminin yerine geçmez. Banka penceresi/eksik kotasyon yasağı sadece icra kısıtıdır.
- Çok ufuklu ve kuyruk farkı önemlidir: olası küçük %0,2 artış için %1,6 gidiş-dönüş makas ödenmez. %5–%10 anlamlı rally/crash olasılığı, evresel süreklilik ve dönüş olasılığı daha değerlidir. Sabit %5 fiyat hareketini işlem emri yapan kural da kullanılmaz.
- Artı getirili yanlış işlemleri ve alım fırsatını kaçıran CASH günlerini aynı net modelde sorgula. Ay sonu servet, net pişmanlık, peak-to-trough DD, risk, işlem sayısı ve tekrar giriş maliyeti her ay ayrı raporlanır.

**(E) Meta-öğrenme / uzman bileşimi:** ayrı ufuk ve rejim tahminleyicilerini geçmişteki olgunlaşmış skorlamaya göre online değerle, başarısız uzman azaltılabilir. Ancak kapı takvim, `if(newsCategory===...)`, `month===2023-01` gibi el yapımı alpha kuralı OLMAYACAK. Banka emir geçerliliği ve veri as-of gibi işlemsel `if` koşulları elbette gerekir. Kullanılan ANN/ANFIS/LSTM/MoE/DQ vb. mimariler **önce bağımsız kıyaslamadan sonra** uzman olarak kabul edilir; isim seçmek başarı kanıtı değildir.

## 4. Yürüyüş ve aylık kayıt sözleşmesi
İlk ay Ocak 2023: `MONTH_START` anında model parametreleri ve CASH 100 snapshot al; yalnız o anda bilinen girdiler kullan. Her yeni saat/bar:
`observe → validate_asof → encode_event+market → forecast_distribution → choose(HOLD,BUY,SELL) → hypothetical_bank_fill → update_only_matured_labels → write_experience`.
Önce karar, sonra yalnızca olgunlaşmış sonuçla geribildirim ve gecikmeli kredi ataması; aynı bara ait sonraki fiyat sinyalde YOK.
Ay kapanışında 4 bağımsız dosya:
1. `months/YYYY-MM/DECISIONS.csv`: her uygun kontrol noktası, pozisyon, hedef, confidence bound, net switching advantage, işlem masrafı, as-of data, açıklama ve referans.
2. `months/YYYY-MM/EVENT_ECONOMICS.jsonl`: olay DNA'sı ve ekonomik olay teorileri / en az iki alternatif açıklama, ilk yayın, çürütme ve confidence; ham olaya göre değil embedding ile öğrenilen temsiller.
3. `months/YYYY-MM/MATH_AUDIT.json`: CRPS/MAE, kalibrasyon, Q-regret, distribution/horizon scores, tail risk, turnover ve benchmark, en büyük kazanılan/kaçırılan hareketin kapanmış tarihsel sonuç analizi, bias/variance, expert weights, ablation, eksik veri.
4. `months/YYYY-MM/CORE_CHECKPOINT.json`: weights, optimizer moments, normalization states, prototypes, pending labels (ancak gelecekte olgunlaşacaklar *hedef sonuç içermeyecek*), cash/ounces, peak/nav/fees, schema-version, rng state, source hashes, tam konfigürasyon ve devamlılık hash.
Ayrıca `MONTH_REPORT.md` ile insan tarafından okunur ekonomik anlatı ve işlem gözden geçirme raporu.
Ocak sonunda kontrol: aynı Ocak tekrar optimize edilmez. Kullanıcı/araştırmacı Ocak raporunu onayladıktan sonra Şubat'a geçilir; aylık model değişiklikleri yalnız önceden tanımlanmış online adaptation protokolünden gelir. Hata kaynaklı çekirdek mimari değişiklik gerekiyorsa **versiyon önerisi**, test ve geçiş kuralı ayrı dokümante edilir; Ocak'ta yeniden turlayarak başarı iddia edilemez.

## 5. 2025 sonu birleşik algoritma — veri tarihine göre değil CORE olarak
Aylık raporların yan yana konması **yeterli değildir**. `CORE_CHECKPOINT` zinciri kesintisiz sürmeli, öğrenilmiş ekonomik encoder/başlık/critic ağırlıkları, olay-semantik prototipleri, belirsizlik kalibrasyonu, optimizer state ve outcome-conditioned deneyim belleği korunmalı. Son checkpoint tüm bunları kapsar.
Aralık 2025 sonunda `CORE_VFINAL_FROZEN`: yılları isimlerden öğrenmeyen `weights+semantic_memory+online_calibration+policy+portfolio_accounting` ayrı artifact; kayıtlı şema ve hash. 2026 Ocak testinde öğrenme politikası ve güncelleme takvimi **önceden seçilir**: örn. frozen-param inference veya precommitted online update. Ocak 2026 sonuçları 2023–25 CORE'a geriye sızmaz.

## 6. İlk ayın kabul kriteri (Ocak 2023 dışına çıkılmayacak)
- Data/PIT availability audit, yayın damgaları, missing source ve banka fiyatı proxy raporu dürüst olmalı.
- Tahmin ve olay mekanizma parametrelerinde gerçek **olgunlaşmış-label** güncellemesi gözlemlenmeli; tarih bazlı lookup yasak.
- CASH/GOLD ödül, çok ufuklu hareket sürme/bitme, yeniden giriş avantajı aynı ünite bazında öğrenilmeli; sadece 15 dakikalık return eşiği TUT davranışına kilitlenmemeli.
- En az 2 ekonomik karşı-mekanizma ile aylık önemli hareketler incelenmeli; fiyat oynaklığına bağlı ex-post olay seçimi eğitim tarafında leakage üretmemeli.
- 100USD net ve banka iki bacak ücretli sonuç, pasif altın ve nakit karşılaştırması raporlanmalı; hiç işlem yapmayan sonuç "başarılı risk uzmanı" diye sunulmamalı.
- Ocak 2023'te kesin sonuç iddia edilmez; kaydedilen checkpoint önce manuel denetlenir, başka aya geçilmez.
- R2/R3/V21/V22 araştırmaları tarihsel geçmiş sonuçlarıyla kıyas olabilir fakat "kanıtlanmış sistem" olarak yanlış terfi ettirilmez.

## 7. Karar
**Bu belge bir mimari/araştırma taahhüdüdür; tek başına çalışan ekonomik ana motor, Ocak 2023 ekonomik neden analizi veya 2025 sonu eğitilmiş algoritma değildir.** Bir sonraki uygulanabilir adım: olay/piyasa PIT birleştirici → öğrenen encoder/critic → Ocak 2023 karar/audit → check-point. Tarih asla modelin özelliği olmaz, yalnız walk-forward denetimidir.
