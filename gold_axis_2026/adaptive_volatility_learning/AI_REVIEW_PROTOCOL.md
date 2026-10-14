> **Amaç düzeltmesi (2026-10-14):** Yalnız GPT ile yapılan olay incelemesi **orta/büyük yönlü UP/DOWN olayları**, olayın başlaması/devam etmesi/tersine dönmesi, beklenen **kalan hareket**, maliyetli olası `BUY/SELL/HOLD_GOLD/HOLD_CASH/WAIT` kararına ilişkin **kaynaklı, karşı-kanıtlı nitel eleştiri** sunmalıdır. GPT otomatik banka emri vermez; sadece vol riski/tekil haber açıklamasıyla görev tamamlandı sayılamaz. Bu proje küçük günlük momentum dalgalanmalarında al-sat yapan sistem değildir. [Yeni protokol](EVENT_DRIVEN_MEDIUM_LARGE_MOVE_RESTART_CONTRACT_20261014.md).

# GOLD — Test Aşaması Yapay Zekâ İkinci Görüş Protokolü
**Sürüm:** `ai-review-v0.1` · **Durum:** JAN2023_GPT_QUALITATIVE_REVIEW_RECORDED / NO_EXTERNAL_AI

## Bugün nasıl kullanılacak?

**Aşama 1, doğrudan bu sohbet:** Algoritmanın/analistin ürettiği kaynak kimlikli **sayısal kanıt paketi** ChatGPT tarafından ayrı ikinci değerlendirmeye alınır. Bu, otomatik çalışan başka bir model entegrasyonu ya da algoritmadan bağımsız kör araştırmacı değildir. ChatGPT'nin cevabı `months/YYYY-MM/STATE.json` içindeki `ai_reviews` alanına, **model/tarih/prompt sürümü, kullanılan kanıt kimlikleri ve düz metin/rapor yolu** ile kaydedilir. Sohbet hafızasına güvenerek aylar arası aktarım yapılmaz.

**Bu projenin şu anki kesin kullanıcı kararı: YORUMLAMA GPT-ONLY.** DeepSeek, Gemini veya başka harici LLM **çağrılmayacak**, araştırma sonucu onlara gönderilmeyecek. Önceki başka projelerde bulunan bağlantılar burada kullanılmaz. Bu politika ancak kullanıcı açıkça değiştirirse güncellenebilir.

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

**İlk uygulama:** [Ocak 2023 GPT niteliksel olay raporu](months/2023-01/JAN_2023_FULL_MONTH_GPT_ONLY_SCIENTIFIC_AUDIT.md) ve [Ocak GPT review metadata](months/2023-01/STATE.json) kaydedildi. Sayısal politikayı GPT geriye dönük değiştirmedi; AI katmanının **NAV artış katkısı hesaplanmadı**.

**Yanlışlık denetimi:** Kaynağı olmayan haber veya tarih uydurma; veri sonucunu modele gizlice yazdırma; modelin akıcı metnini olasılık sayma; bir haberden tek zorunlu neden çıkarma; tek modelle bağımsız ikinci deney yapılmış gibi sunma YASAK.

## AI gerçekten değer katıyor mu?

Aynı vaka evreninde ve aynı veri izinleriyle **(A) sadece sayısal algoritma**, **(B) yalnız kanıt-temelli AI yorumu**, **(C) algoritma + AI eleştirisi** birlikte kaydedilip kıyaslanır. Olayların yorum kalitesi için kanıt doğruluğu ve yanlış nedensellik/çelişki; volatilite açısından ancak sabit olasılıksal hedef/kalibrasyon/yanlış alarm ölçütleri kullanılır. AI hükmü karşıt kanıt üretebilse bile sayısal modelin parametresi ayrı yeniden hesaplanmadan kendiliğinden 'öğrenildi' sayılmaz. Kip A tamamen hindsight içerir; kalibrasyon üstünlüğü için daha sonra Kip B/uygun kilitli test gerekir.

**Sağlayıcı ve gizlilik:** Açık repo veya haricî API'ye ham özel Neon tick, banka işlem kayıtları, kimlik, API anahtarı, model bağlantı bilgisi veya lisanslı ham piyasa verisi aktarılmaz. Yeni API anahtarı istemeden önce mevcut güvenli entegrasyonun gerçek çalışırlığı ayrıca doğrulanır.
