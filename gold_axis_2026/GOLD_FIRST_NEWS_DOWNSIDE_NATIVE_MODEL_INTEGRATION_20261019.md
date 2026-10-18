# GOLD — Büyük düşüşü ilk haber ile yakalama: ORİJİNAL MODELE ENTEGRASYON V1

**19 Ekim 2026 · research-gold-core-timeless-selective-learning-20261016 · S1/S2/S3 aynı çekirdek · AL/SAT yetkisi YOK**

## 1. Amaç ve yeni temel prensip

**Amaç:** 2023–2025'teki büyük en az %4 DOWN bacaklarından öğrenilen **haber/fiyat kronolojisini modelin günlük online çalışma mantığına eklemek**. Büyük olayın başlangıcı hakkında "ilk haber geldi, altın düşecek" gibi tek yönlü elle yazılmış bir tahmin değil, **fiyat zayıflaması ne zaman başlamıştı, haber bundan önce mi sonra mı ilk erişilebilirdi, fiyat tepkisi daha sonra hızlandı mı?** sorularını as-of yanıtlamak.

[Çalışan yeni saatli çekirdek](adaptive_trading_core/downside_news_onset_v1.js) doğrudan [native S1/S2/S3 model](adaptive_trading_core/adaptive_market_core_s1_s2.js) içine entegre edildi. Ayrıca [S3 eleştirmeni](adaptive_trading_core/adaptive_position_value_s3.js) risk durumu gördüğünde yalnız \`REVIEW_EXISTING_GOLD_EXPOSURE_NO_ORDER\` üretir; yeni BUY/SELL emri ve otomatik banka işlemi üretmez.

## 2. G ve N — iki as-of saat

**G/fiyat saati:** tamamlanmış M15 barından geçmiş en çok 96 **bitişik** M15 kapanışında önceki fiyat tepesine göre yüzde geri çekilme, dört saatlik yön, negatif bar payı, önceki yükselişin doygunluğu. \`0,5%\` geri çekilmede **EARLY_WEAKNESS**, \`1,0%\` ve olumsuz dörtsaat yönü varsa **CONFIRMED_FALL**. Bunlar başlangıç için **araştırma eşikleri**, kesin önceden %4 düşüş sinyali değil. Seans boşluğunda fiyat bir sonraki geçerli gözlemle >%0,5 boşluk düşmüşse \`GAP_OPEN_DOWN_DISLOCATION\` ve **kesintili gözlem** olarak işaretlenir; hiç görülmemiş hafta sonu M15'leri doldurulmaz. Son 72s'lik önceki zayıflama bilgisi ayrı korunur: sonra gelen bir haber, yeni seansta o ana kadar düşüş görülmese bile **sıfırdan ilk haber** muamelesi görmez.

**N/haber saati:** \`eventTime/publishedAt/availableAt/detectedAt\` haberi [küresel kaynak sicili](OLAY_02_KURESEL_HABER_KAYNAK_KURALLARI_V1_20261018.json) ve [K/ORG yönlendirici](adaptive_trading_core/event_news_condition_router_v1.js) üzerinden doğrular. \`originalFirstprintVerified=true\` ancak birincil kaynak ve ilgili ilk-baskı kanıtı varsa ara **ilk-haber adayı**na girebilir; sadece URL / haberin varlığı yeterli değildir.

**N'nin rol durumları:**
- \`BEFORE_FIRST_OBSERVED_WEAKNESS\`: henüz fiyat saati zayıflamamışken, birincil ilk-baskı kontrolü geçen haber. Daha sonraki geri çekilmede ancak önceki kapanmış barda zaten erişilebilmiş haber bağlanır. Aynı M15 barında gelen haberin aynı bardaki düşüşten önce mi sonra mı olduğu **SAME_BAR_UNRESOLVED**.
- \`AFTER_PRICE_WEAKNESS_ACCELERANT_CANDIDATE\`: haber **önceden gözlenmiş** zayıflamanın ardından.
- \`AFTER_PREVIOUS_PRICE_WEAKNESS_ACCELERANT_CANDIDATE\`: önceki seansın düşüşü çoktan bilinmişken yeni bir seansta haber.
- \`UNVERIFIED_OR_LATE_CONTEXT\`: geçmiş makale/ilk yayın sertifikası bulunmayan veya canlı feed'e sonradan katılan haber; ayrı \`chronologyRole\` betimleyici zaman ilişkisini gösterebilir ama ekonomik tetikleyici diye kanıtlanmaz.
- \`POSTHOC_OR_SECONDARY_REPORT\`: WGC/medya aylık veya gerçekleşmiş fiyat hareketinin yorumu; erken ilk-haber sinyali olamaz.

**ÖNEMLİ:** İlk haberin fiyat kırılmasından önce olması nedensellik kanıtı değildir. Düşüş yeni habersiz başladığında \`priceOnlyStarts\` artar, sonra gelen makro gelişme kendi ayrı E olay saatiyle izlenir. Haberler birden fazla ve çakışıyor olabilir.

## 3. S1 / S2 / S3 bağlama ve koruma kapıları

- S1 için dört **MARKET** özelliği geliştirildi: \`down_pressure_z\`, \`down_drawdown_norm\`, \`down_negative_share\`, \`down_rally_exhaustion\`. Bu özellikler güncel bitmiş bara kadar fiyat geçmişinden hesaplanır, S1'in **tarihsiz** sayısal prototip öğrenmesine girilebilir. Ekonomik haber etiketi K39, tarihsiz ORG adayı veya haber metni otomatik **güvenilir S1 olasılığı**na dönüşmez.
- **Kritik güvenlik varsayılanı:** \`downsideEnabled=false\` — çünkü gerçek Ocak–Şubat 2023 karşılaştırmasında bu dört özelliğin S1 tahmin kalitesine katkısı **ispatlanmadı, yön doğruluğu kötüleşti**. Ancak \`downsideEnabled=true\` ile kontrollü shadow araştırmasında sayısal S1'e eklenebilir; sistemdeki fiyat düşüş gözlemcisi **her durumda çalışır**.
- S2 FAST/SLOW **mevcut global yaşam döngüsü** matematiğini bozmaz; \`observe().downsideResearch\` ayrı fiyat/haber saati durumudur. Seans kesintisinde eski S2'nin sansürleme kuralı korunur.
- S3 aynı Q critic / kondisyonel model yolunda, \`downsideEvidence\` tip ve zaman doğrulamasından sonra **yalnız risk/pozisyon gözden geçir** notunu üretebilir. Yalnız gözlenmiş \`CONFIRMED_FALL\` veya gap-down → \`REVIEW_EXISTING_GOLD_EXPOSURE_NO_ORDER\`; **satış üretmez**. %0,8 alış + %0,8 satış maliyeti modeline dokunulmadı.
- Eski CORE checkpoint'i S1 featureNames değiştirmeden geri açılır; geçmişte görülmemiş düşüş uyarıları sonradan oluşturulmaz; yeni gözlemci ilk yeni bardan öğrenmeye başlar.

## 4. GERÇEK veriyle 2023–2025 (fiyat-bazlı, tek merkezli haber evreni olmadan)

[Kayıt: bütün 70.915 M15 fiyat ile 17 ana DOWN bacağına karşı mekanizma metrikleri](adaptive_trading_core/GOLD_DOWN_FALL_ONSET_REAL_2023_2025_REPLAY_V1_20261019.json).

| Ölçüm | Sonuç |
|---|---:|
| XAU/USD tamamlanmış M15 BID/ASK orta fiyat, 2023–2025 | **70.915 bar** |
| Geçmiş 96 ardışık M15'e göre −%0,5 erken fiyat-zayıflama uyarısı | **744** |
| Gerçek M15 boşluğu sonrası ≥%0,5 gap-down uyarısı (ayrı) | **6** |
| Seçilmiş 17 uzun ≥%4 DOWN bacağının pivotunun −24 / +48 saati içindeki alarmı | **17/17**, ancak **sonuçtan sonra seçilmiş pivot çevresi** ölçümü |
| Uyarının ardından sıradaki 5×96 gözlenmiş bar içinde yeni −%4 fiyat düşüşü | **57/737 = %7,73** |
| Aynı kabaca gözlem ufkundaki sabit dört saatlik çıpalar | **199/4397 = %4,53** |
| Uyarının ardından sıradaki 20×96 gözlenmiş bar içinde yeni −%4 düşüş | **121/717 = %16,88** |
| Aynı kabaca gözlem ufkundaki sabit dört saatlik çıpalar | **674/4307 = %15,65** |

**Bulguyu doğru okumak:** 17/17 *fiyat zaten değişmeye başlamış olan dönemlerde* alarm var demektir; **gelecekteki büyük düşüşü önceden yakalama oranı değildir**. 744 alarmın çoğu başka bir ≥%4 düşüşe yol açmıyor. 5×96 ve 20×96 pencere, tatil/seans kesintilerini içeren **gözlenmiş M15 bar sayısıdır**, takvimde kesintisiz 5/20 gün değil. Sabit dört saatlik çıpalar istatistiksel eşleşmiş kontrol grubu değil; örnekler örtüşür. Bu oranlardan doğru/yanlış alarm için istatistiksel güven veya önceden alım/satım başarısı çıkarılamaz. Gerçek haberlerin ilk yayın vintage bağlantısı olmadan bu koşu **sadece fiyat uyarısını** değerlendirdi.

## 5. Aynı S1 modeli için adil kontrol: Ocak–Şubat 2023, 2022 eğitim SIFIR

[155 aynı dört-saatlik olgunlaşmış ileri-getiri penceresinde BASELINE vs DOWN ÖZELLİKLERİ](adaptive_trading_core/GOLD_DOWNSIDE_S1_VS_BASELINE_JANFEB2023_20261019.json). Hem temel hem yeni model aynı kaynakla **2023 Ocak ilk barından** ileri yürüdü; fiyat-dışı olayların sertifikasız K etiketleri S1'e sokulmadı.

| S1 240 dakika ileri yön/olasılık | Orijinal fiyat S1 | Düşüş özellikli S1 |
|---|---:|---:|
| Ortak geçerli geçmişten verilen değerlendirme | **155** | **155** |
| İşaret yön doğruluğu | **%54,194** | **%50,323** |
| Brier olasılık kaybı (küçük daha iyi) | **0,263567** | **0,260198** |

**Karar:** **−3,871 yüzde puan yön kötüleşmesi**, küçük Brier iyileşmesi; başarının objektif olarak arttığına karar verilemez. Özellikle **3 Şubat 2023 13:45Z ilk sert istihdam düşüşünde** risk katmanı \`CONFIRMED_FALL\` dese de S1 henüz \`P(UP)≈%56\` üretiyor. Bu, risk takibi ve gerçek ileriyi öğrenen yön tahmininin **farklı görevler** olduğunun güçlü karşı örneğidir. Yeni dört S1 özelliğini **default-off, opt-in araştırma** yapmamızın nedeni budur. S3 bankadan işlem sonuçlarını iyileştirdiğine dair kanıt yok.

## 6. As-of gerçek olay: 1–3 Şubat 2023

[Native model içinde Fed, BoE, ECB, Lagarde, NFP haberinin fiyat başlangıcına göre nerede geldiğinin replay'i](adaptive_trading_core/GOLD_DOWN_NEWS_FEB2023_CORE_SHADOW_REPLAY_20261019.json).

- 1 Şubat **17:15Z** erken fiyat zayıflaması; Fed haberi **19:00Z** → \`AFTER_PRICE_WEAKNESS\`, ilave faize yönelik yeni olasılık. **Haber önce değil**.
- 2 Şubat BoE 12:00Z, ECB 13:15Z ve ECB konuşması 13:45Z ayrı kaynak ve koşullar olarak işaretlendi. Altın 13:45Z'de yerel **EARLY_WEAKNESS** oluştu; aynı M15 barındaki konuşmanın kesin ilk rolü belirsiz.
- 3 Şubat NFP 13:30Z mevcut önceki seans zayıflama bilgisinden sonra → fiyat-kronoloji düzeyinde \`AFTER_PREVIOUS_PRICE_WEAKNESS_PRIOR_SESSION\`; aynı gün 13:45Z sert yeni DOWN şoku \`CONFIRMED_FALL\`. Bu istihdamın yeni bir **ikincil DOWN hareketi başlatmasına engel değildir**; sadece uzun seçilmiş bacağın Şubat 1 başlangıcına neden olarak geriye taşınamaz.

Bu beş tarihli resmî yayın kaydının **özgün 2023 firstprint** ve o anda bilinen konsensüs-vintage delilleri yeterli olmadığı için model \`firstprintVerified=false\` ve \`tradeAllowed=false\` tutar. Bu replay **gerçek haberi canlı çekmedi**, arşiv adresi ve planlanan ilan saatini kullandı.

## 7. Doğrulama / sınırlar

[Test modülü](adaptive_trading_core/test_downside_news_onset_v1.js) **13/13 PASS**: haber → ertesi fiyat kırılması, haber düşüşten sonra, aynı M15 belirsiz, birincil ilk-baskı yoksa early statü yok, gelecekteki haber reddi ve state rollback, tekrar ID, boşluk ve gap-down, eski checkpoint, aynı CORE S1/S3 beslemesi. Modülün \`tradeAllowed=false\` durumunu S3 bile değiştiremez.

**Mevcut bilim kapısı:** \`PRICE_FALL_CLOCK_IN_CORE=YES\`, \`FIRST_NEWS_CLOCK_IN_CORE=YES\`, \`ORG_K_ROUTING_PRESENT=YES\`, \`S1_DOWN_FEATURES_AVAILABLE_OPT_IN=YES\`, \`S3_REVIEW_PRESENT=YES\`, \`LARGE_DROP_FORWARD_ALPHA_PROVEN=NO\`, \`REAL_FIRSTPRINT_CATALOG=NOT_COMPLETE\`, \`OOS_2024_2025_S1_FEATURE_WIN=NOT_TESTED\`, \`S3_COST_NET_WIN=NOT_PROVEN\`, \`LIVE_BUY_SELL=NO\`.

**Bir sonraki bilimsel hedef:** Tarihi haberlerin **ilk yayımlanma ve erişim saatleriyle** 2023–2025 öğrenmeyi besleyip; A faiz/USD, B pozisyon çözülmesi, C risk primi, D nakit/teminat, E rezerv-makro gruplarında **haber önce gelen düşüşleri** önceki fiyat sinyaliyle eşleştirerek *ileriye kalan 1/5/10 seanslık düşüş olasılığını* normal S1/S2'ye karşı bağımsız yılda test etmek. Ek fayda kanıtlanırsa S1 feature-gate açılabilir; başarısızsa mevcut iyi CORE korunur.
