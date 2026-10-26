# WORK HANDOFF — ALTIN BÜYÜK DÜŞÜŞ ERKEN RİSK TESPİTİ
**Tarih:** 26 Ekim 2026 | **Dil:** Türkçe | **Durum:** Araştırma / uygulama, fiyat tahmini veya canlı işlem değil.

## 0) Görev: açıklamayla yetinme, gerçekten uygula
Bağlı GitHub ve Neon uygulamalarını aç, orijinal kodları, veri sözleşmelerini ve eski raporları oku. Büyük altın düşüşlerinin ilk başlangıcından önce risk göstergelerinin ne söylediğini 2000–2022 döneminin erişilebilir tarihsel veri örnekleriyle öğren; aynı özellikleri gösterip düşmeyen negatif kontrol dönemleriyle karşılaştır; mevcut BASE14 ve CFTC21 risk modellerinin 2025 doğrulaması ve 2026 geriye dönük stres testi üzerinde erken uyarı/yanlış alarm değişimini deneysel olarak ölç. **Modeli yeniden etiketleyip aynı 2026 vakalarını optimize ederek “kazandık” deme.** Sonuç kötü ise bunu açıkça söyle. Yalnızca plan, pseudo-code veya veri indirici bırakıp durma. Engellenen kaynaklar varsa hata ve alternatifini kanıtla, izin verilen veriyle deneyi gerçekten yürüt, eksik kapsamı işaretle. Kullanıcının amacı altın fiyatını tahmin etmek değil, özellikle büyük düşüş başlamadan uyarı üretmek ve gereksiz alarmı azaltmak.

## 1) Bağlı uygulamalar / güvenli çalışma
- GitHub repo: `ataullahturgut/sim3-automation`.
- MEVCUT kaynak ve raporları inceleme dalı: `gold-risk-official-download-retry-v4-20261026`.
- YENİ araştırma dalı yarat, örn. `research/gold-risk-2000-2026-case-control-v13`; bu dalda yalnız araştırma/test/rapor dosyalarını geliştir. Mevcut ana algoritma ve canlı uygulama üzerine doğrudan yazma; deploy/merge yapma.
- Neon: proje **Gold Control**, project_id **`winter-art-94880101`**. Neon'a yalnız **SELECT** sorguları; şema değişikliği, insert, update, delete, drop, migration, prod-data repair, reset YASAK. Sorguları küçük ve kaynak seçici yap; canlı deney tablolarından modele farkında olmadan veri sızdırma. Veritabanı parolası/connection string isteme veya raporlama; bağlı uygulamayı kullan.
- GitHub'daki diğer proje dallarına, ANN/ANFIS aylık fiyat tahminine, günlük AL/SAT sistemine dokunma.
- Çalıştırma sırasında GitHub Actions kullanmak mümkünse artifaktları indir, hash doğrula, çalışmanın id/run bağlantılarını ver. Workflow'un tetiklendiğini ya da dosyanın indiğini **sadece kod commit edildi diye iddia etme**.

## 2) Başlamadan önce gerçekten oku — teyitli GitHub dosyaları
*Risk modeli & veri girdisi*
1. `gold_axis_2026/tools/gold_forecast_risk_overlay_2023_2026_v1.py` — BASE14 kaynak oluşturma ve unsupervised risk.
2. `gold_axis_2026/tools/gold_risk_cftc_independent_overlay_v2.py` — CFTC21 özellikleri, GC+SI kalite ve rapor tarihlerinin birleşmesi.
3. `gold_axis_2026/tools/gold_risk_release_clock_v8.py` — Fed H.10 tatil/dönem yayın saati düzeltmesi.
4. `gold_axis_2026/tools/gold_risk_asof_audit_20261026.py` — kaynak vintage kontrol kapısı.
5. `gold_axis_2026/tools/gold_risk_source_features_v6_20261026.py` — 2Y/TIPS/SLV araştırma özellikleri; PIT onaysızlar üretim için yasak.
6. `gold_axis_2026/tools/gold_monthly_h1_neon_source_v2.py` — **PRICE_SQL** kaynak sözleşmesini esas al; aylık fiyat-tahmin algoritmasını değiştirme.

*Karşılaştırma ve yanlış sonuç düzeltmeleri*
7. `gold_axis_2026/GOLD_RISK_V8_CORRECTED_ACTUAL_REPLAY_20261026.md` — **otoritatif V8 karşılaştırması**.
8. `gold_axis_2026/GOLD_RISK_CORRECTION_BASE14_VS_CFTC21_MATCHED_20261025.md` — beş günlük 4/4 ile ertesi gün 4/4'ü karıştırma.
9. `gold_axis_2026/GOLD_RISK_CFTC_V2_2023_2026_REPLAY_RESULT_20261024.md` — özgün farklı yayın-saati sonuçlarının tarihi, artık nihai kıyas değil.
10. `gold_axis_2026/GOLD_RISK_V9_13_FEATURE_ABLATIONS_ACTUAL_RESULT_20261026.md` — 13 ablation: daha fazla özellik otomatik ilerleme değil.
11. `gold_axis_2026/GOLD_RISK_V10_EVENT_FIRST_CONFIRMATION_REPLAY_20261026.md` — geçmiş sonuç görülerek geliştirilmiş çift-teyit adayı: bağımsız başarı sayma.
12. `gold_axis_2026/GOLD_RISK_SOURCE_PIT_VERIFICATION_V5_20261026.md`, `gold_axis_2026/GOLD_RISK_V6_SOURCE_REPLAY_AND_MODEL_GATE_20261026.md`, `gold_axis_2026/GOLD_RISK_V7_DATE_RELEASE_ASOF_AUDIT_20261026.md`.
13. `gold_axis_2026/GOLD_RISK_V12_LEGACY_MACRO_PROVENANCE_AND_CASE_COMPARISON_20261026.md` ve `gold_axis_2026/research/V12_LEGACY_OFFICIAL_DOWNLOAD_TRIGGER_20261026.md`. Bu eski V12 kapsamı 2010–2019 ile sınırlıydı; **yeni kullanıcı kararı 2000–2022** araştırmasına genişletildi.
14. `gold_axis_2026/tools/gold_risk_legacy_macro_acquisition_v12.py` ile `.github/workflows/gold-risk-legacy-2010-2019-official-v12.yml`. Mevcut indiricileri kontrol et, 2000–2022 için ayrı uyarlanmış araştırma akışı oluştur.
- Önceden söylenmiş V11 kod ve raporunun dalda var olduğunu **varsayma**; gerçekten bulursan kullan, yoksa V11 arşivini bulamadığını belirt.
- Önceki V8/V9/V10 araştırma ZIP/CSV'leri GitHub Actions artifacts veya konuşma dosyalarında olabilir; gerçekten al, asıl tarihlerle yeniden çalıştır ve checksum ile karşılaştır.

## 3) Neon kaynak sözleşmesi (read-only)
`public.observations` şema sütunları: `series_id`, `observation_ts`, `value`, `source`, `provider_as_of`, `available_as_of`, `first_seen_at`, `retrieved_at`, `quality_status`, `metadata`, `lineage_id`, `payload_hash`, diğerleri.
2010–2025 için dört metal serisi:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`
ZORUNLU kaynak filtreleri: `source='lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01'`, `metadata->>'payload_provider_label'='LBMA'`, `metadata->>'payload_source_label'='seed'`, `quality_status='APPROVED_HISTORICAL_RESEARCH_RECONSTRUCTION_NOT_PIT'`, weekday intersection. Bu fiyatlar tarihsel araştırma rekonstrüksiyonu; gerçek ilk-yayın PIT değildir.
Kontrol edilmiş 2010–2019: metal başına **2.526** hafta içi kayıt. 2010–2022 altın yıllık verileri Neon'da mevcut. **2000–2009 dört metal bu serilerde yok;** bağımsız güvenilir kaynak ve fiyat tanımı gerek, bilinmiyorsa kapsam katmanlandır ve ayrım yap.
2026 kaynağı **AYRI**: `gold_monthly_h1.staktrakr_2026_git_snapshot_daily_v1`, `snapshot_commit='02964d0324dde362099976c867f5077a369acaa5'`, `source_repository='lbruton/StakTrakr'`, `evidence_status='RESEARCH_GIT_SNAPSHOT_NOT_PIT'`. Rastgele son fiyat satırlarını karıştırma. **2026-02-27 XAU 3516.02 hatalı gözlem** ve etkilenen geçmiş özellik / gelecek etiket pencereleri karantina; interpolate/impute etme.
`GPR_OFFICIAL_GIT_PIT` vs GPRT/GPRA serileri mevcut, ancak **bu eski risk modeli BASE14/CFTC21 özellikleri değildir**; başka projelerden veri kaçırma; araştırmaya alınacaksa gerekçe ve PIT denetimi ayrı. Aynı isimde birden fazla revizyonu karıştırma. `DGS10_ALFRED_PIT_ME` 2016 sonrası aylık kökenli; 2011/2013 günlük H15 yerine geçmez.
Mevcut `available_as_of` alanı tek başına yayın zamanı/vintage güvencesi değildir; issuer dosyasıyla kontrol et.

## 4) 2000–2022 ekonomik tarihsel kanıt ve indirilecek en küçük veri
Önce **2000–2022 tüm tarihlerin yalnız fiyat serisinden** büyük düşüş başlangıçlarını ve bağımsız olay kümelerini çıkar. Gelecek 5 iş günü minimum / başlangıç fiyatı <= -5% ve ertesi gün <= -3% hedeflerini ayrı sakla; ayrıca 3, 5, 10 ve 20 günlük sert gerileme türlerini karşılaştır; başlama anı/ilk düşüş/yerel dip ve toparlanma ayrı etiket. Olay penceresi örn. **-30 ile +10 işlem günü**. Sadece büyük düşüşleri seçme: **aynı geçmiş trend/oynaklık/dört metal ayrışması koşullarındaki fakat düşüşsüz 2–4 eşleştirilmiş negatif kontrol penceresi**; seçimde geleceği özellik olarak kullanma; aynı yıllardan farklı piyasa rejimleri seç; yakın olayları bağımsız sayma.
Makro girdiler: yayınlanmış GC/SI CFTC (COMEX Gold `088691`, Silver `084691`), Cboe `GVZ` (yalnız tarihsel mevcut dönem), dönemin o tarihte mevcut Fed H.10 broad USD (eski DTWEXB ile 2019 sonrasının DTWEXBGS serilerini yayımlanmadan önce geriye taşımama), DGS2/DGS10 nominal, DFII10 10Y reel (var olduğu tarihten sonra), dört metalin günlük geçmiş davranışı. 2000 öncesi/2000–07 sınırlı kaynaklarda **özellik eksikliğini açıkça bildir**, farklı feature-family ve gözlem aralığı varyantlarıyla karşılaştır, imputasyonla 2000'de GVZ/CFTC disaggregated varmış gibi yapma.
Mümkünse yalnız olay/kontrol + gerekli özellik lookback aralıklarını çek; CFTC yıllık resmi ZIP gerekiyorsa bir kez indir, ilgili haftaları ayıkla. **2000–2022 tamamını global girdi paneli olarak indirmeye zorlanma**. Her dosyada kaynak URL, SHA-256, kapsama, eksik tarihler, sonradan revizyon ve gerçek ilk yayın zamanı denetimi tut. Salı tarihli CFTC pozisyonu cuma yayımlandığında kullanılabilir; 2006'ya geriye yayımlanan disaggregated veri o tarihlerde mevcut sayılmaz. Yayın tarihi sabit değilse fail-closed.
Resmî arşiv erişimi engellenirse ne kadar denendiğini, HTTP/MIME ve alternatif sağlayıcı kanıtını yaz; önce yarım veriyle başarı uydurma.

## 5) Sabit eski algoritmalar ve yeniden üretim
- BASE14: `RobustScaler + IsolationForest(n_estimators=200,random_state=1701)`; skor `-score_samples`, train-only quantile YELLOW 90%, RED 95%. Mevcut 14 özellik **yerinde**.
- CFTC21: 14 mevcut + 7 CFTC özellik, aynı öğrenme sözleşmesi. Normal rapor +7g conservative proxy, CFTC resmi 2025 kapanma/tatil sapmalarına ayrı gate, veri en fazla 21g eski olabilir; yayın-anı as-of gerçek kaynağa göre doğrulanmalı.
- Sinyal anı tarihsel test `17:30 America/New_York`, gün içi düşüşten **önce** uyarı verdiğini iddia etmek için intraday event onset fiyatı ve timestamp şart. 09:00 Türkiye karar penceresi başka bir deneydir, iki saat kuralını karıştırma.
- Orijinal eğitim 2023–24 / 2025 validation; 2023–25 fit / 2026 stress. 2026 test penceresi 21 Eylül'e kadar 161 ortak karar günü.
- **V8 2026 kaynak/saat düzeltilmiş referans (161 ortak gün)**: BASE14 46 RED, CFTC21 31 RED; ertesi gün >=3% düşüş **4/4 her ikisi**; gelecek 5g >=5% düşüş **etiket başlangıç günleri** BASE14 9/13 vs CFTC21 6/13; çakışan 5g etiket kümeleri BASE14 4/4, CFTC21 2/4; 5g hedefine göre non-event RED **37 vs 25 gün**. **4/4 ayrı fiziksel düşüş başlangıcının önceden tespiti demek DEĞİLDİR.**
- V9 refit için birkaç eğitim günü silindiğinden 45 vs 29 gibi sayılar V8 ile birebir karıştırılmamalı; karşılaştırma her zaman aynı origin/feature availability setinde **yeniden eğitilmiş kontrollerle** olsun.
- V10 çift teyit (41 RED, 32 non-event RED; 4/4 risk label group) önceden incelenmiş 2026 dönemiyle geliştirildi, kör doğrulama değil.

## 6) Yeni modelleme: çift sonuç, yüksek false-alarm maliyeti
- Genel tüm veri indisleri yerine **olay tabanlı** yaklaşım ve benzer negatif kontroller kur.
- Önce açıklanabilir geçmiş vaka profilini üret: CFTC pozisyon yoğunlaşması, hafta değişimi, GVZ değişimi, dolar, nominal/reel faizde bp, dört metalin 1/3/5/10 günlük korelasyon/ayrışma ve fiyat trend/ivme; bütün hesaplar karar anından önce erişilen veriyle.
- Alternatifleri **ayrı test et**: basit rejim koşulları; lojistik/GBM gibi düşük kompleksiteli, class imbalance ve örnek sayısına uygun denetimli meta-filtre; conditional anomaly; BASE14 + CFTC21 agreement/episode state. Her ayrı modelde feature ablation, negatif kontroller, makro family leave-one-out, kaynak/PIT kapısı yap. Çok az bağımsız büyük düşüşte ağır modelin overfit riski büyüktür.
- **Risk olasılığı ile IsolationForest anomaliliğini karıştırma.** Fiyatın beklenen seviyesi ya da günlük AL/SAT kararı üretme.
- Kör / zaman sıralı sınama: 2000–2022 yalnız kullanılabilir tarihsel eğitim örnekleri; 2023–24 base fit, 2025 seçim ve sonradan dondurma; 2026 dokunulmamış feature/parametre kaynağı olacak, fakat daha önce kullanıcı/araştırmacı 2026 sonuçlarını gördüğü için epistemik olarak kör değildir. Gerekirse 2010–2022 içindeki ek walk-forward bloklarıyla istikrar kanıtla. 2026'yı hiperparametre araması/özellik seçimi için kullanma.
- Alarmın **düşüş başlamadan** kaç gün önce ilk kez geldiğini belirle: lookahead 1/3/5/10 gün, early/onset/late; karşılaştırılabilir *ayrı olay* recall, günlük yanlış RED ve false-alert *episode* sayısı, zamanında yakalama, false-alert lead-time, alarm süresi, 2025/2026 per-year score. Red alarmı ardışık günlerde tekrarlamak tek doğru öngörü değildir.
- Düşüş onayı %100 recall için zorunlu invariant değil; risk/false alarm karşılaştırmalarında her modelin yakalayamadığı gerçek düşüşleri ayrı listele. Başarı hedefi: 2026'da ölçülmüş BASE14 4/4 risk-etiket-kümesini korumaya **çalışmak**, CFTC21 25 false 5d-RED günün altını aramak; bunları gelecek performans garantisi sayma.

## 7) Çıktılar, acceptance gates ve kullanıcıya sunulacak şey
Yalnız plan değil, araştırma dalına **gerçek çalıştırılabilir kod+unit test**, orijinal kaynak SHA/URL manifesti, tarihli as-of join QA, 2000–2022 gerçek olay ve kontrol tablosu, 2025 & 2026 aynı-gün backtest raporu, günlük BASE14 / CFTC21 / yeni aday alarm CSV, her olay için ilk uyarı-olay başlangıcı-dip zaman çizelgesi, alarm kalitesi/kaçırmalar, sonuçların birebir yeniden üretim komutu ve GitHub commit URL'leri yaz.
Tek ekran özet: kaç bağımsız olay, kaç veri eksik, ilk alarm ne zaman, hangi olayların başlangıcı öncesinde, kaç yanlış alarm günü/kümesi. İlerleme yerine **çalıştırılmış sonuç**; mümkün olmayan alt işlerin blockers'ı ve kanıtı. Strict leakage audit: no future values in feature, no post-event CFTC, no retrospective revised first-print as PIT, no target 2026 training, no bad Feb27. Tests PASS olmazsa PASS yazma.
**Canlı Neon, üretim uygulaması, mevcut BASE14/CFTC21 orijinalleri, yanlış fiyat kayıtları değişmeyecek. Yeni model ancak yeniden üretim ve as-of kanıtı sonrası adaydır.**

## 8) Çalışma yöntemi
Ek soru sormadan önce bağlantıları, kaynak dosyalarını ve kayıtları kontrol et. Uzun süreçte rapora sıkışma: sırasıyla veri arşivini al/doğrula → olay/karşı örnekleri üret → as-of özellik tablosu → 2025 seçimi → 2026 stress ve tarihler → regression tests → net karar. Her önemli aşamadan sonra gerçek ilerlemeyi kısaca göster; henüz olmadıysa gerçekleşmiş gibi anlatma. Türkçe, kısa ama sayısal nihai sonuç ver.
