# GOLD INTRAMONTH — Tarihsel Olay Sicili, Çapraz Eşleme ve Zaman Nedenselliği Sözleşmesi
**Tarih:** 2026-10-13 · **Durum:** RESEARCH / belgelendirme + deterministik tarih-kesişimi; tahmin modeli, doğrulanmış nedensellik veya gerçek banka işlemi DEĞİLDİR. · **Depo dalı:** `research-gold-jan26-two-factor-confirmation-v4-20261013` · **PR:** #128 açık/henüz merge edilmemiş. · **Üst otorite:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`.

## 1. Amaç ve değiştirilemeyen kaynaklar

Eski altın olaylarını yeniden keşfetmek, ayrı defterleri toplamak veya kendiliğinden aynı haber kabul etmek yerine **kaynak satırlarını kimliği korunmuş şekilde gelecekte birleştirilebilir hâle getirmek**. Sayısal/öyküsel eski kayıtlar yerinde kalır; yeni indeks onların yerine geçmez. En önemli koruma, olayın **fiyat gözlem zamanı**, **güncel bilinen kaynak yayımlanma zamanı**, **model bilgi kesimi**, **gelecekteki fiyat hedefi** ve **gerçek işlem zamanı** kavramlarını ayırmaktır.

**Oluşturulan salt-bağlantı verisi:** `GOLD_HISTORICAL_EVENT_MASTER_CROSSWALK_V1_20261013.csv`; 291 kayıt, 39 alan; kaynak satırı tamamlayıcısı, modelin eğitilmiş girdisi DEĞİL. Aşağıdaki kaynakların mevcut araştırma dalındaki dosya blob SHA'ları hesap dökümü için sabitlenmiştir:

| Korunan özgün kaynak | Kayıt | Blob SHA | Nesne |
|---|---:|---|---|
| `GOLD_MAJOR_MOVE_EVENT_ATLAS_2023_2025_V1_20261013.csv` | 42 | `735fb169f11d0cf5bfad71c2545c45c556a39634` | ZigZag tamamlanmış + yıl sonu açık trend bacakları |
| `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_53_CLUSTER_NEWS_RESEARCH_20261013.csv` | 53 | `f1036a6f8ebd00b1bfb202c1d4d02d7a5bd492a1` | Farklı 1/4/12 saat ve 1/3/5 NY17 seans etiketli fiyat kümesi |
| `GOLD_EVENT_CHAIN_2023_2025_V4_CASE_STUDIES_20261013.csv` | 9 | `0ce27d727b13230519bbcfd4072321520dedffc6` | Ön koşul / yeni olay / kuvvetlendirici / karşıt kanıt vaka incelemeleri |
| `GOLD_H3_REMAINING53_SIGNAL_AUDIT_EPISODES_2026-10-04.csv` | **22** | `10fd4bd79ffece391c1c3ec7d1b53bd9693a1b68` | 2026 H3 model sinyal epizodu, `53` dosya adı **satır veya bağımsız olay sayısı değil** |
| `GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv` | 155 | `b243218d323ab3f9e7559266076a4bf60456e7e2` | CPI/NFP/UNEMP/AHE/FOMC yayın **gösterge** satırları; tek tarih/saatte birden çok veri olabilir |
| `GOLD_MONTHLY_CHHHO_MISSED_ALARM_ROOT_CAUSE_2026-09-29.md` | 10 | `de0a57c68067a78fd47ed1fe63e8b5017190335d` | 2025–26 aylık yüksek tahmin hatası **tanı** ayı; bağımsız intraday fiyat şoku değil |

**Tarih düzeltme yardımcısı**: `GOLD_EVENT_CHAIN_2023_2025_V3_CORRECTED_V2_NEWS_TIMING_20261013.csv` 53 id ve SHA `f7e43c0224a65146e3690986eb2ccf850bb46d1c`. `earliest_qualifying_window_baseline` Claude **açık PR #118** kaynaklı hakem hesaplamasıdır; buradaki aktarım **bağımsız yeniden hesaplanmış gerçek şok başlangıcı** veya haberin dakika damgalı first-print kanıtı değildir.

## 2. Tam saklama ve hata kontrolü

- **Toplam 291 satır** = 42 + 53 + 9 + 22 + 155 + 10. **291 ekonomik olay değildir**: kapsam, kimlik, dönem, metrik ve kimi zaman aynı ekonomik gelişme farklıdır. 2023–25 M15 hareketlerinin **774 işlem günü, 151 ana >=3% ve 23 ikincil hızlı >=2% işaretli günü**, 53 yönlü kümeye indirgenmiştir; 174 farklı fiyat günü, 53 ayrı makro haber değildir.
- İlk ZigZag'daki 42 hareketin başlangıç/tepe/dip noktaları **ileride oluşan dönüşle** belirlenir; `confirmed` geriye dönük doğrulama tarihidir. Günlük model o tarihte gelecekteki fiyat ekstremesini biliyormuş gibi işlem yapamaz. Yıl sonundaki 42. bacak açık kalmıştır.
- V2'nin `start` alanı **ilk threshold bayrağı**, V3 `earliest_qualifying_window_baseline` ise geriye dönük ölçülen getiri penceresinin **en erken kaynak günü**dür; her ikisi de fiyat hareketinin nedeninin ilk ortaya çıkma anını garanti etmez.
- V1/V2 arasındaki eşleme **YYYY-MM-DD dahil başlangıç/bitiş aralıklarının kesişimi** ile yapılmıştır; **53/53 V2 fiyat kümesi en az bir V1 bacağıyla kesişir**. Ancak **26/53**, en az bir **karşıt yönlü V1 bacağıyla da kesişir**. Bunun sebebi geniş ZigZag bacağı ile ara dönem hızlı karşı hareketlerin aynı tarih aralığına düşebilmesidir. **Tarih kesişimi = potansiyel bakılacak vaka**, **aynı olay / aynı ekonomik neden / aynı işlem / bağımsız onay** DEĞİLDİR.
- `overlap_v1_same_direction_date_only`, `overlap_v1_opposite_direction_date_only`, `overlap_v2_date_only`, `overlap_v4_case_date_only` **analitik navigasyon** alanlarıdır. V1 özgün `legacy_swings_overlap_count` sayısı saklıdır; yeni tarih-kesişimiyle birebir uyuşmak zorunda değil, çünkü tanımlar/fiyat pencereleri farklı.
- V4 vaka yüzdesi hücresinde `+3.979 (20-session trailing return on Jan28 +6.001)` bulundu; **ilk sayısal ana hareket `+3.979` olarak tutuldu ve hücrenin tamamı `data_lineage_notes.original_move_cell` olarak korundu**. Sonraki model bu açıklama içindeki ikinci sayıyı yanlışlıkla olay getirisi diye kullanamaz.
- V2'nin 25 dosyasında özel tarihlenmiş haber derlemesi yok (`NO_CURATED_DATE_SOURCE`); 42 eski epizoda bağlanan kaynak linki bulunabilir. **Bu 25 vaka nedensiz veya habersizdir denemez**; teyitli ilgili yayın eksik demektir.
- V4 9 kaynaklı vaka `antecedent`, `new_event`, `amplifier`, `contrary` ayrı alanlarda tutulur; **ön uyarı** (vulnerability) ile sürpriz (catalyst) ve anlık fiyat çözülmesi (reaction) birbirine karıştırılamaz.
- H3 2026'daki 22 epizot ve ayrıca 2025 için H3 reversal root cause raporunda geçen yaklaşık 24 epizot, farklı model hedefleri ve örneklemlerdir; 42/53 ve 2026 dosya adındaki `53` ile kesinlikle toplanmaz.
- Aylık 10 hatanın `forecast_error_usd` ve `forecast_ape_pct` alanı vardır; `movement_pct` **BOŞ**. Bu aylara fiyat şoku yüzdesi uydurulmadı; aylık tahmin hatası, piyasadaki fiyat hareketinin yüzdesi değildir.

## 3. İleride olayları modellere bağlama — zorunlu çapraz eşleştirme sırası

1. **Önce araştırma nesnesini seç:** `PRICE_ZIGZAG_V1`, `MULTIHORIZON_FIXED_THRESHOLD_V2`, `EXPLANATORY_CASE_STUDY_V4`, `H3_MODEL_SIGNAL_EPISODE_2026`, `MACRO_PUBLICATION_RAW_V1` veya `MONTHLY_CHHHO_FORECAST_ERROR_CASE`. Model hedefinin D0→D3 günlük ortalaması mı, NY17 kapanışı mı, 09→16:45 BANK DAY mi, 16:45→next09 OVN mi olduğu anahtarın parçasıdır.
2. **Özgün satır kimliğini ve kaynak SHA'sını sabitle:** `event_key` salt kayıt ve versiyon kimliğidir; `source_row_id`, `source_path`, `source_blob_sha` ve orijinal `start_date/end_date` değiştirilmez. Büyük makro sürpriz veya haber olayına `C001` gibi keyfi fiyat-ID atanamaz.
3. **Tarih kesişimi başlangıç aday listesi üretir, otomat eşitlik değil:** farklı yönlü, farklı saatli, farklı fiyat sağlayıcılı veya iç içe olan fiyat hareketlerinde aynı olay sayılabilmesi için ayrı `event_link_evidence` dosyasında bağımsız kabul gerekçesi ve provenance tanımlanmalıdır. `UNRESOLVED` geçerli nihai statüdür.
4. **Saatleri bilimsel sıraya koy:** `article_first_publication_utc` ve `market_data_available_utc` ancak güvenilir dakika/vintage kanıtıyla doldurulabilir; mevcut CSV'de böyle kanıt yok, otomatik gece yarısı atama yasak. Tüm source `pub_date` hücreleri gün etiketi; bazılarında birden çok tarih noktalı virgülle ayrılmıştır.
5. **Makro haber yeni bilgi saatine göre katılır:** ham `release_timestamp_utc` ile `surprise_available_after_utc` ayrı tutulur; `actual-consensus` sadece ilgili resmî açıklama ve orijinal konsensus vintage elde edildikten sonra kullanılabilir. İlk RAW V1 2025 FOMC kapsaması 2026-10-08 resmi takvim düzeltmesinden önceki **eski sürümdür**. Birden fazla NFP/UNEMP/AHE satırı aynı istihdam olayının göstergeleridir, üç ayrı şok olamaz. PCE/ADP/JOLTS bu RAW V1'de kaynak-kısmi/eksiktir.
6. **Sızıntısız birleştirme:** `decision_origin_utc` biliniyorsa sadece `first_available_utc <= decision_origin_utc` kanıtlı bağımsız değişken kullan. Sonradan görülen ZigZag dönüşü, V2 future window eşiği, model `anymax` veya gelecekte açıklanan makro surprise **öncü gösterge değildir**. Yalnızca hedef ve geriye dönük analiz alanında yer alabilir.
7. **Çelişkili kanıtı atma:** ör. 2024 Mart aşırı yükseliş sonrası da yükseliş sürdü; 2025 Ekim WGC aşırılık uyarısından sonra artış sürdü ve sonra keskin döndü; 2024 Ağustos 4% high-low aralığına rağmen NY17 close önceki referansa göre ~−1.275%; 2025 Nisan tarife haberleri hem UP hem DOWN rejiminde rol aldı. Tek faktör `NEWS=SENTIMENT=SAT` veya `OVERBOUGHT=SELL` etiketi üretmek YASAK.
8. **Tahmin kabiliyeti için gözlem/kontrol/sıfır noktası:** false-alarm ve missed-shock için tarih/saat/ürün bazlı negatif kontrol günleri, bağımsız 2023/24 development, incelenmiş 2025 ve 2026'yı **retrospektif** etiketleme, araştırmadan hiç görülmemiş ileri dönem; event inception seçimini outcome üzerinden optimize etme.
9. **Banka icrası ayrı katman:** %0.8 alış + %0.8 satış kullanıcı masrafı; gerçek teklif BID/ASK, spread, emir kabul saati, gecikme ve kısmi gerçekleştirmeler bilinmiyorsa hipotetik spot getiri **bankada kazanılan net getiri değildir**. R70'nin 25bp total roundtrip proxy'si V4'ün %0.8+%0.15 her-işlem varsayımıyla aynı değildir.
10. **Yeni çalışma kabul kriteri:** zorunlu `study_id`, `target_id`, `source_vintage`, `event_registry_version`, `origin_utc`, `feature_available_at_utc`, `event_window_start/end_utc`, `prediction_issue_at_utc`, `fill_source`, `cost_contract`, `matched_control_design`, `outcome`, `known_at_validation`, `reproduction_status`. Eksikse ilgili alan `UNKNOWN`; model/AL-SAT PROMOTION otomatik **FAIL CLOSED**.
11. **Sürüm ve düzeltme protokolü:** Eski atlası silmeyin veya orijinal satırlarını üzerine yazmayın. Doğrulanmış yeni haber first-print veya çift kontrol geldiğinde `CROSSWALK_V2` ve ayrı `EVIDENCE_RELATION_V2` oluşturun; hangi raw SHA ve satırı neden supersede ettiğini belirtin. GitHub PR incelemesi ve kullanıcı onayı olmadan LIVE yok.

## 4. Kapsam dışı ama korunması zorunlu diğer araştırmalar

- `GOLD_H3_REVERSAL_ROOTCAUSE_ATLAS_V1_2026-10-04.md` — 2025 83 V5 direction error, 68 momentum-reversal kaçışı, yaklaşık 24 grup; model mekanizma tanısı, nedensellik ispatı değil.
- `GOLD_H3_MACRO_RELEASE_SAMPLE_DIAGNOSTIC_V1_2026-10-04.md` — 2025 Mart–Haziran 22 benzersiz scheduled event tarihi ve önce/sonra H3 reversal kıyasları.
- `GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_ALL_774_DAYS_20261013.csv` ve `..._174_FLAGGED_DAYS_20261013.csv` — olay/sakin gün kontrol evreni. **Sadece bayraklı 174 günü kullanmak seleksiyon bias yaratır.**
- `GOLD_EVENT_CHAIN_2023_2025_V4_13_TENSION_ONSETS_MATCHED_CONTROLS_20261013.csv` — ilk yüksek-gerilim eşiği aşımı ile 13 matched control; doğal şok özdeşliği kanıtı değil.
- `GOLD_MONTHLY_PROJECT_MANIFEST.md` — aylık H1 ayrı gerçek otorite, 2010–2024 ay örüntüleri ve alarmlar bağımsız kayıtlardır. 10 case sadece `GOLD_MONTHLY_CHHHO_MISSED_ALARM_ROOT_CAUSE_2026-09-29.md` dosyasından alınmıştır; tüm aylık model alarm matrisi burada sınıflandırılmamıştır.

## 5. Bilimsel hüküm

**PASS — kaynakların kaybını önleyen id/lineage tablosu, deterministik tarihsel örtüşme haritası ve kategori ayrımı.** 291/291 satırda benzersiz `event_key`, özgün `source_path + blob_sha`; 42/53/9/22/155/10 aile sayıları kontrol edildi. V2 53 satırın tamamına tarihli V3 düzeltme referansı vardır. **WARN — 53 fiyat kümesinin 26'sında en az bir karşıt yönlü uzun epizot kesişmesi:** eşleme otomatik olay-birleştirmesi değildir. **BLOCKED — dakika düzeyinde haber first-print, ekonomik etkene nedensel atıf, onaylı feature-vintage, tüm model tahmin/karar/işlem saatleri, gerçek banka BID/ASK, bağımsız aynı-kaynak teyit ve untouched prospective başarı.**

**Bu dosya, önceden yapılmış araştırmayı koruyup yeniden kullanım standardı sağlar; yeni fiyat modelinin test edildiği veya alarm kalitesinin yükseldiği iddiası içermez.**
