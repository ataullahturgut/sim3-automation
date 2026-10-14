# GOLD — Test Aşaması Yapay Zekâ İkinci Görüş Protokolü
**Sürüm:** `ai-review-v0.1` · **Durum:** PROTOCOL_ONLY / NO_COMPLETED_MONTHLY_AI_RUN

## Bugün nasıl kullanılacak?

**Aşama 1, doğrudan bu sohbet:** Algoritmanın/analistin ürettiği kaynak kimlikli **sayısal kanıt paketi** ChatGPT tarafından ayrı ikinci değerlendirmeye alınır. Bu, otomatik çalışan başka bir model entegrasyonu ya da algoritmadan bağımsız kör araştırmacı değildir. ChatGPT'nin cevabı `months/YYYY-MM/STATE.json` içindeki `ai_reviews` alanına, **model/tarih/prompt sürümü, kullanılan kanıt kimlikleri ve düz metin/rapor yolu** ile kaydedilir. Sohbet hafızasına güvenerek aylar arası aktarım yapılmaz.

**Aşama 2, isteğe bağlı bağımsız model:** Depoda daha önce kullanılan DeepSeek/Gemini GitHub Actions araştırma köprüleri mevcuttur; bunlar **bu aylık değerlendirme iş akışına henüz bağlı değildir**. DeepSeek önceki deneylerde tam yanıt üretebildi, Gemini deneyinde tam bilimsel yanıt alınamadı. Kullanıcı onayı ve kaynak güvenlik kontrolünden sonra **yalnız açık/sanitize edilmiş anonim toplu özet** ile sınırlı, bütçesi kontrollü manuel GitHub workflow deneyi olabilir. Mevcut API anahtarı veya servis çalışırlığı, bugün bu yeni protokole otomatik erişim sağlıyor demek değildir.

## Modelden istenen standart cevap

Girdi: `review_id, month_id, mode, algorithm_version_id, evidence_ids, numeric_features, dated_events, candidate_mechanisms, matched_case_ids, non_event_controls, numeric_baseline, missing_sources, outcome_visibility`.

Çıktı:
- `observed_facts`: Kaynağa bağlı gözlem, ölçüm zamanı, yayımlanma tarihi ve sayısal dayanak
- `plausible_mechanisms`: Başlatıcı / aktarım / güçlendirici ayrı ve neden-sonuç **iddia derecesi**
- `competing_explanations`: En az iki rakip görüş; her biri için destekleyen/çürüten kanıt
- `historical_analogues_and_differences`: Benzer ve **olaysız/ters** örnek ID'leri, benzerliğin nedenleri
- `algorithmic_verdict_check`: Sayısal algoritmanın kararıyla aynı mı, karşı mı, hangi veri yüzünden?
- `recommended_research_risk_verdict`: Kalibre edilmiş nicel risk varsa onu koru; yoksa `UNDETERMINED`, uydurma olasılık üretme
- `tests_that_could_falsify`: Sonraki aylar için sınanabilir somut iddialar ve eksik veriler
- `uncertainty / claim_status`: `SUPPORTED_BY_SOURCES`, `PLAUSIBLE_NOT_IDENTIFIED`, `CONTRADICTED`, `UNKNOWN`
- `model_id, prompt_version, reviewed_at, evidence_hash, original_algorithm_output_ref`: Daha sonra aynı paketi yeniden denetlemek için kayıt

**Yanlışlık denetimi:** Kaynağı olmayan haber veya tarih uydurma; veri sonucunu modele gizlice yazdırma; modelin akıcı metnini olasılık sayma; bir haberden tek zorunlu neden çıkarma; tek modelle bağımsız ikinci deney yapılmış gibi sunma YASAK.

## AI gerçekten değer katıyor mu?

Aynı vaka evreninde ve aynı veri izinleriyle **(A) sadece sayısal algoritma**, **(B) yalnız kanıt-temelli AI yorumu**, **(C) algoritma + AI eleştirisi** birlikte kaydedilip kıyaslanır. Olayların yorum kalitesi için kanıt doğruluğu ve yanlış nedensellik/çelişki; volatilite açısından ancak sabit olasılıksal hedef/kalibrasyon/yanlış alarm ölçütleri kullanılır. AI hükmü karşıt kanıt üretebilse bile sayısal modelin parametresi ayrı yeniden hesaplanmadan kendiliğinden 'öğrenildi' sayılmaz. Kip A tamamen hindsight içerir; kalibrasyon üstünlüğü için daha sonra Kip B/uygun kilitli test gerekir.

**Sağlayıcı ve gizlilik:** Açık repo veya haricî API'ye ham özel Neon tick, banka işlem kayıtları, kimlik, API anahtarı, model bağlantı bilgisi veya lisanslı ham piyasa verisi aktarılmaz. Yeni API anahtarı istemeden önce mevcut güvenli entegrasyonun gerçek çalışırlığı ayrıca doğrulanır.
